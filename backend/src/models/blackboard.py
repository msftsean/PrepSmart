"""
Blackboard: Central coordination entity for multi-agent orchestration.

The blackboard pattern is used for multi-agent coordination in PrepSmart.
All agents read from and write to this shared state atomically.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class Blackboard(BaseModel):
    """
    Shared state for multi-agent coordination using the blackboard pattern.

    The blackboard contains all input data, intermediate agent results, and final output.
    Agents read from and write to the blackboard atomically.
    The Coordinator Agent monitors the blackboard to determine agent execution order.
    """

    # Identifiers
    task_id: str = Field(..., description="Unique UUID linking all agent outputs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Input Data
    crisis_profile: Optional[dict[str, Any]] = Field(
        None,
        description="User's crisis scenario (CrisisProfile model as dict)"
    )

    # Intermediate Agent Results
    risk_assessment: Optional[dict[str, Any]] = Field(
        None,
        description="From Risk Assessment Agent - risk level, severity, threats"
    )
    supply_plan: Optional[dict[str, Any]] = Field(
        None,
        description="From Supply Planning Agent - items, costs, tiers"
    )
    emergency_plan: Optional[dict[str, Any]] = Field(
        None,
        description="From Emergency Plan Generator (natural disaster mode only)"
    )
    economic_plan: Optional[dict[str, Any]] = Field(
        None,
        description="From Financial Advisor Agent (economic crisis mode only)"
    )
    resource_locations: Optional[list[dict[str, Any]]] = Field(
        None,
        description="From Resource Locator Agent - shelters, food banks, etc."
    )
    video_recommendations: Optional[list[dict[str, Any]]] = Field(
        None,
        description="From Video Curator Agent - educational videos"
    )

    # Final Output
    complete_plan: Optional[dict[str, Any]] = Field(
        None,
        description="From Documentation Agent - consolidated plan"
    )
    pdf_path: Optional[str] = Field(
        None,
        description="Filesystem path to generated PDF"
    )

    # Coordination State
    status: str = Field(
        default="initialized",
        description="Lifecycle status: initialized, processing, completed, failed"
    )
    agents_completed: list[str] = Field(
        default_factory=list,
        description="List of agent names that have successfully written to blackboard"
    )
    agents_failed: list[str] = Field(
        default_factory=list,
        description="List of agent names that encountered errors"
    )

    # Execution Tracking
    execution_start: Optional[datetime] = Field(
        None,
        description="When agent orchestration began"
    )
    execution_end: Optional[datetime] = Field(
        None,
        description="When all agents completed or failed"
    )
    total_execution_seconds: Optional[float] = Field(
        None,
        description="Total time from start to completion"
    )

    # Cost Tracking
    total_tokens_used: int = Field(
        default=0,
        description="Sum of all agent token usage (Claude API)"
    )
    total_cost_estimate: float = Field(
        default=0.0,
        description="Estimated total cost in USD for Claude API calls"
    )

    # Error Tracking
    errors: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of errors encountered during execution"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "status": "processing",
                "crisis_profile": {
                    "crisis_mode": "natural_disaster",
                    "specific_threat": "hurricane"
                },
                "risk_assessment": {
                    "overall_risk_level": "EXTREME",
                    "severity_score": 95
                },
                "agents_completed": ["RiskAssessmentAgent", "SupplyPlanningAgent"],
                "agents_failed": [],
                "total_tokens_used": 3500,
                "total_cost_estimate": 0.042
            }
        }

    def mark_agent_complete(self, agent_name: str, tokens_used: int = 0, cost: float = 0.0) -> None:
        """
        Mark an agent as completed and update tracking metrics.

        Args:
            agent_name: Name of the agent that completed
            tokens_used: Number of tokens consumed by this agent
            cost: Estimated cost in USD for this agent's API calls
        """
        if agent_name not in self.agents_completed:
            self.agents_completed.append(agent_name)

        self.total_tokens_used += tokens_used
        self.total_cost_estimate += cost
        self.updated_at = datetime.utcnow()

    def mark_agent_failed(self, agent_name: str, error_message: str) -> None:
        """
        Mark an agent as failed and log the error.

        Args:
            agent_name: Name of the agent that failed
            error_message: Description of the error
        """
        if agent_name not in self.agents_failed:
            self.agents_failed.append(agent_name)

        self.errors.append({
            "agent_name": agent_name,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.updated_at = datetime.utcnow()

    def calculate_execution_time(self) -> Optional[float]:
        """
        Calculate total execution time if start and end are set.

        Returns:
            Execution time in seconds, or None if not yet started/completed
        """
        if self.execution_start and self.execution_end:
            delta = self.execution_end - self.execution_start
            self.total_execution_seconds = delta.total_seconds()
            return self.total_execution_seconds
        return None

    def is_complete(self) -> bool:
        """
        Check if all required agents have completed.

        For natural disaster: Need RiskAssessment, SupplyPlan, ResourceLocations, Videos, Documentation
        For economic crisis: Need RiskAssessment, SupplyPlan, EconomicPlan, ResourceLocations, Videos, Documentation

        Returns:
            True if plan generation is complete
        """
        if not self.crisis_profile:
            return False

        crisis_mode = self.crisis_profile.get("crisis_mode")

        # Required agents for all modes
        required = [
            "RiskAssessmentAgent",
            "SupplyPlanningAgent",
            "ResourceLocatorAgent",
            "VideoCuratorAgent",
            "DocumentationAgent"
        ]

        # Mode-specific requirements
        if crisis_mode == "natural_disaster":
            # Emergency plan is optional but nice to have
            pass
        elif crisis_mode == "economic_crisis":
            required.append("FinancialAdvisorAgent")

        # Check if all required agents completed
        completed_set = set(self.agents_completed)
        required_set = set(required)

        return required_set.issubset(completed_set)

    def get_pending_agents(self) -> list[str]:
        """
        Get list of agents that haven't completed yet.

        Returns:
            List of agent names that haven't run or are still running
        """
        if not self.crisis_profile:
            return []

        crisis_mode = self.crisis_profile.get("crisis_mode")

        all_agents = [
            "RiskAssessmentAgent",
            "SupplyPlanningAgent",
            "ResourceLocatorAgent",
            "VideoCuratorAgent",
            "DocumentationAgent"
        ]

        if crisis_mode == "economic_crisis":
            all_agents.append("FinancialAdvisorAgent")

        completed_set = set(self.agents_completed)
        failed_set = set(self.agents_failed)

        return [
            agent for agent in all_agents
            if agent not in completed_set and agent not in failed_set
        ]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert blackboard to dictionary for JSON serialization.

        Returns:
            Dictionary representation of blackboard
        """
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Blackboard":
        """
        Create blackboard from dictionary.

        Args:
            data: Dictionary with blackboard fields

        Returns:
            Blackboard instance
        """
        return cls(**data)
