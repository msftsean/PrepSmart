"""
Coordinator Agent: Orchestrates multi-agent execution using blackboard pattern.

The coordinator monitors the blackboard, determines which agents can run based on
preconditions, dispatches agents in parallel when possible, and handles failures.
"""

import asyncio
from datetime import datetime
from typing import Optional

from ..models.blackboard import Blackboard
from ..services.blackboard_service import blackboard_service
from ..services.claude_client import ClaudeClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class CoordinatorAgent:
    """
    Orchestrates multi-agent crisis plan generation using blackboard pattern.

    The coordinator:
    1. Initializes blackboard with crisis profile
    2. Determines which agents can run (precondition checking)
    3. Dispatches agents in parallel when dependencies allow
    4. Monitors completion and handles failures
    5. Updates blackboard status throughout execution
    """

    def __init__(self, claude_client: ClaudeClient):
        """
        Initialize coordinator.

        Args:
            claude_client: Claude API client (passed to agents)
        """
        self.claude_client = claude_client
        self.max_retries = 2
        self.agent_timeout = 60  # seconds per agent

    def get_ready_agents(self, blackboard: Blackboard) -> list[str]:
        """
        Determine which agents can run based on preconditions.

        Agent dependencies (discovered iteratively):
        - RiskAssessmentAgent: No dependencies (always ready)
        - SupplyPlanningAgent: Needs RiskAssessment complete
        - ResourceLocatorAgent: No strict dependencies (can run anytime)
        - VideoCuratorAgent: No strict dependencies (can run anytime)
        - FinancialAdvisorAgent: Needs RiskAssessment (economic mode only)
        - DocumentationAgent: Needs ALL other agents complete

        Args:
            blackboard: Current blackboard state

        Returns:
            List of agent class names that are ready to execute
        """
        if not blackboard.crisis_profile:
            return []

        crisis_mode = blackboard.crisis_profile.get("crisis_mode")
        completed = set(blackboard.agents_completed)
        failed = set(blackboard.agents_failed)

        ready = []

        # RiskAssessmentAgent: Always ready if not done
        if "RiskAssessmentAgent" not in completed and "RiskAssessmentAgent" not in failed:
            ready.append("RiskAssessmentAgent")

        # SupplyPlanningAgent: Needs RiskAssessment
        if ("SupplyPlanningAgent" not in completed and
            "SupplyPlanningAgent" not in failed and
            blackboard.risk_assessment is not None):
            ready.append("SupplyPlanningAgent")

        # ResourceLocatorAgent: Can run anytime (no strict dependencies)
        if ("ResourceLocatorAgent" not in completed and
            "ResourceLocatorAgent" not in failed):
            ready.append("ResourceLocatorAgent")

        # VideoCuratorAgent: Can run anytime
        if ("VideoCuratorAgent" not in completed and
            "VideoCuratorAgent" not in failed):
            ready.append("VideoCuratorAgent")

        # FinancialAdvisorAgent: Only for economic crisis, needs RiskAssessment
        if crisis_mode == "economic_crisis":
            if ("FinancialAdvisorAgent" not in completed and
                "FinancialAdvisorAgent" not in failed and
                blackboard.risk_assessment is not None):
                ready.append("FinancialAdvisorAgent")

        # DocumentationAgent: Needs all others complete
        required_for_docs = ["RiskAssessmentAgent", "SupplyPlanningAgent",
                             "ResourceLocatorAgent", "VideoCuratorAgent"]
        if crisis_mode == "economic_crisis":
            required_for_docs.append("FinancialAdvisorAgent")

        if ("DocumentationAgent" not in completed and
            "DocumentationAgent" not in failed and
            all(agent in completed for agent in required_for_docs)):
            ready.append("DocumentationAgent")

        return ready

    async def dispatch_agents(
        self,
        agent_names: list[str],
        blackboard: Blackboard
    ) -> Blackboard:
        """
        Dispatch multiple agents in parallel.

        Args:
            agent_names: List of agent class names to execute
            blackboard: Current blackboard state

        Returns:
            Updated blackboard after agent execution
        """
        if not agent_names:
            return blackboard

        logger.info(f"Dispatching agents in parallel: {', '.join(agent_names)}")

        # Import agents dynamically to avoid circular imports
        from .risk_assessment_agent import RiskAssessmentAgent
        from .supply_planning_agent import SupplyPlanningAgent
        # TODO: Import other agents as they're implemented
        # from .resource_locator_agent import ResourceLocatorAgent
        # from .video_curator_agent import VideoCuratorAgent
        # from .financial_advisor_agent import FinancialAdvisorAgent
        # from .documentation_agent import DocumentationAgent

        agent_map = {
            "RiskAssessmentAgent": RiskAssessmentAgent(self.claude_client),
            "SupplyPlanningAgent": SupplyPlanningAgent(self.claude_client),
            # TODO: Add other agents as implemented
        }

        # Filter to only agents we have implementations for
        available_agents = [name for name in agent_names if name in agent_map]

        if not available_agents:
            logger.warning(f"No implementations available for agents: {agent_names}")
            return blackboard

        # Create tasks for parallel execution
        tasks = []
        for agent_name in available_agents:
            agent = agent_map[agent_name]
            task = self._execute_agent_safely(agent, blackboard, agent_name)
            tasks.append(task)

        # Execute agents in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for agent_name, result in zip(available_agents, results):
            if isinstance(result, Exception):
                logger.error(f"{agent_name} failed: {result}")
                blackboard.mark_agent_failed(agent_name, str(result))
            elif isinstance(result, Blackboard):
                # Agent succeeded, blackboard was updated
                blackboard = result
                logger.info(f"{agent_name} completed successfully")
            else:
                logger.warning(f"{agent_name} returned unexpected result: {type(result)}")

        # Persist blackboard after agent batch
        blackboard_service.update_blackboard(blackboard)

        return blackboard

    async def _execute_agent_safely(
        self,
        agent,
        blackboard: Blackboard,
        agent_name: str
    ) -> Blackboard:
        """
        Execute an agent with timeout and error handling.

        Args:
            agent: Agent instance
            blackboard: Current blackboard
            agent_name: Agent class name for logging

        Returns:
            Updated blackboard

        Raises:
            Exception: If agent fails after retries
        """
        try:
            # Execute agent with timeout
            updated_blackboard = await asyncio.wait_for(
                agent.process(blackboard),
                timeout=self.agent_timeout
            )
            return updated_blackboard

        except asyncio.TimeoutError:
            error_msg = f"{agent_name} timed out after {self.agent_timeout}s"
            logger.error(error_msg)
            raise Exception(error_msg)

        except Exception as e:
            error_msg = f"{agent_name} error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def generate_plan(self, crisis_profile: dict) -> Blackboard:
        """
        Generate complete crisis plan using multi-agent orchestration.

        This is the main entry point for plan generation.

        Args:
            crisis_profile: User's crisis scenario (CrisisProfile as dict)

        Returns:
            Completed blackboard with all agent results

        Raises:
            Exception: If plan generation fails
        """
        task_id = crisis_profile.get("task_id")
        logger.info(f"Starting plan generation for task_id={task_id}")

        # Create blackboard
        blackboard = blackboard_service.create_blackboard(crisis_profile)
        blackboard.status = "processing"
        blackboard.execution_start = datetime.utcnow()
        blackboard_service.update_blackboard(blackboard)

        try:
            # Main orchestration loop
            max_iterations = 20  # Prevent infinite loops
            iteration = 0

            while not blackboard.is_complete() and iteration < max_iterations:
                iteration += 1
                logger.info(f"Orchestration iteration {iteration}")

                # Get agents that can run
                ready_agents = self.get_ready_agents(blackboard)

                if not ready_agents:
                    # Check if we're stuck
                    pending = blackboard.get_pending_agents()
                    if pending:
                        error_msg = f"No agents ready but {len(pending)} pending: {pending}"
                        logger.error(error_msg)
                        blackboard.status = "failed"
                        blackboard.errors.append({
                            "message": error_msg,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                        break
                    else:
                        # All done
                        break

                # Dispatch ready agents in parallel
                blackboard = await self.dispatch_agents(ready_agents, blackboard)

                # Small delay between iterations
                await asyncio.sleep(0.1)

            # Check completion
            if blackboard.is_complete():
                blackboard.status = "completed"
                logger.info(f"Plan generation completed for task_id={task_id}")
            else:
                blackboard.status = "failed"
                logger.error(f"Plan generation incomplete for task_id={task_id}")

            # Finalize
            blackboard.execution_end = datetime.utcnow()
            blackboard.calculate_execution_time()
            blackboard_service.update_blackboard(blackboard)

            logger.info(
                f"Plan generation finished: status={blackboard.status}, "
                f"time={blackboard.total_execution_seconds}s, "
                f"tokens={blackboard.total_tokens_used}, "
                f"cost=${blackboard.total_cost_estimate:.4f}"
            )

            return blackboard

        except Exception as e:
            logger.error(f"Plan generation failed for task_id={task_id}: {e}")
            blackboard.status = "failed"
            blackboard.execution_end = datetime.utcnow()
            blackboard.calculate_execution_time()
            blackboard.errors.append({
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
            blackboard_service.update_blackboard(blackboard)
            raise


# Singleton instance
def create_coordinator(claude_client: Optional[ClaudeClient] = None) -> CoordinatorAgent:
    """
    Create coordinator instance.

    Args:
        claude_client: Optional Claude client (creates new if not provided)

    Returns:
        CoordinatorAgent instance
    """
    if claude_client is None:
        claude_client = ClaudeClient()

    return CoordinatorAgent(claude_client)
