"""Base agent interface for PrepSmart using blackboard pattern."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from ..models.blackboard import Blackboard
from ..services.claude_client import ClaudeClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all PrepSmart agents using blackboard pattern.

    All agents read from and write to a shared blackboard for coordination.
    """

    # Agent emoji icons for UI display (mode-specific)
    AGENT_EMOJIS = {
        "natural_disaster": {
            "RiskAssessmentAgent": "🌪️",
            "SupplyPlanningAgent": "📦",
            "ResourceLocatorAgent": "🗺️",
            "VideoCuratorAgent": "🎥",
            "DocumentationAgent": "📄"
        },
        "economic_crisis": {
            "RiskAssessmentAgent": "💰",
            "SupplyPlanningAgent": "📊",
            "FinancialAdvisorAgent": "💼",
            "ResourceLocatorAgent": "🗺️",
            "VideoCuratorAgent": "🎥",
            "DocumentationAgent": "📄"
        }
    }

    # Agent UI labels (mode-specific)
    AGENT_LABELS = {
        "natural_disaster": {
            "RiskAssessmentAgent": "Risk Assessment Agent",
            "SupplyPlanningAgent": "Supply Planning Agent",
            "ResourceLocatorAgent": "Resource Locator Agent",
            "VideoCuratorAgent": "Video Curator Agent",
            "DocumentationAgent": "Documentation Agent"
        },
        "economic_crisis": {
            "RiskAssessmentAgent": "Financial Risk Agent",
            "SupplyPlanningAgent": "Budget Planning Agent",
            "FinancialAdvisorAgent": "Financial Advisor Agent",
            "ResourceLocatorAgent": "Resource Locator Agent",
            "VideoCuratorAgent": "Resource Curator Agent",
            "DocumentationAgent": "Documentation Agent"
        }
    }

    def __init__(self, claude_client: ClaudeClient, timeout: int = 30):
        """
        Initialize base agent.

        Args:
            claude_client: Claude API client
            timeout: Maximum execution time in seconds
        """
        self.claude_client = claude_client
        self.timeout = timeout
        self.agent_class_name = self.__class__.__name__
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.tokens_used: int = 0
        self.cost: float = 0.0

    def get_agent_emoji(self, crisis_mode: str) -> str:
        """
        Get agent emoji based on crisis mode.

        Args:
            crisis_mode: "natural_disaster" or "economic_crisis"

        Returns:
            Emoji string for this agent
        """
        mode_emojis = self.AGENT_EMOJIS.get(crisis_mode, {})
        return mode_emojis.get(self.agent_class_name, "🤖")

    def get_agent_label(self, crisis_mode: str) -> str:
        """
        Get agent UI label based on crisis mode.

        Args:
            crisis_mode: "natural_disaster" or "economic_crisis"

        Returns:
            UI-friendly label for this agent
        """
        mode_labels = self.AGENT_LABELS.get(crisis_mode, {})
        return mode_labels.get(self.agent_class_name, self.agent_class_name)

    @abstractmethod
    async def process(self, blackboard: Blackboard) -> Blackboard:
        """
        Process blackboard and generate agent-specific output.

        This method must be implemented by each agent.
        Agents should:
        1. Read inputs from blackboard (crisis_profile, other agent results)
        2. Perform their specialized task
        3. Write results back to blackboard
        4. Update tracking metrics (tokens, cost)

        Args:
            blackboard: Shared blackboard state

        Returns:
            Updated blackboard with agent's output

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    def log_activity(
        self,
        task_id: str,
        status: str,
        description: str,
        progress: int = 0
    ) -> None:
        """
        Log agent activity for UI display.

        Args:
            task_id: Crisis plan task ID
            status: Agent status (waiting/active/complete/error)
            description: Human-readable description
            progress: Progress percentage (0-100)
        """
        logger.info(
            f"[{self.agent_name}] Task {task_id}: {status} - {description} ({progress}%)"
        )

        # TODO: Store in database for real-time UI updates
        # For now, just log to console

    def get_execution_time(self) -> Optional[float]:
        """
        Get agent execution time in seconds.

        Returns:
            Execution time or None if not started/ended
        """
        if not self.start_time or not self.end_time:
            return None

        delta = self.end_time - self.start_time
        return delta.total_seconds()

    def format_prompt(self, template: str, **kwargs: Any) -> str:
        """
        Format prompt template with variables.

        Args:
            template: Prompt template string
            **kwargs: Variables to substitute

        Returns:
            Formatted prompt
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            raise ValueError(f"Prompt template missing variable: {e}")

    def validate_input(self, crisis_profile: Dict[str, Any], required_fields: list[str]) -> None:
        """
        Validate that required fields are present in crisis profile.

        Args:
            crisis_profile: Crisis profile dict
            required_fields: List of required field names

        Raises:
            ValueError: If required fields are missing
        """
        missing = [field for field in required_fields if field not in crisis_profile]

        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
