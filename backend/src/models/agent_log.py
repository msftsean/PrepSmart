"""Agent Activity Log data model."""

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AgentActivityLog(BaseModel):
    """Real-time agent status for UI display."""

    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = Field(..., description="Associated crisis plan task ID")

    agent_name: str = Field(
        ...,
        description="e.g., 'Coordinator', 'Risk Assessment', 'Supply Planning'"
    )
    agent_type: Literal[
        "coordinator",
        "risk_assessment",
        "supply_planning",
        "financial_advisor",
        "resource_locator",
        "video_curator",
        "documentation"
    ]

    status: Literal["waiting", "active", "complete", "error"]

    current_task_description: str = Field(
        ...,
        description="Human-readable description of what agent is doing right now"
    )

    progress_percentage: int = Field(
        default=0,
        ge=0,
        le=100,
        description="0-100% completion"
    )

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None

    error_message: Optional[str] = None

    # Inter-agent Communication
    messages: list[dict] = Field(
        default_factory=list,
        description="Messages sent/received from other agents"
    )

    # Metadata
    tokens_used: Optional[int] = Field(None, description="Claude API tokens consumed")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost in USD")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "log_id": "log-a1b2c3-001",
                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "agent_name": "Risk Assessment Agent",
                "agent_type": "risk_assessment",
                "status": "active",
                "current_task_description": "Analyzing historical hurricane data and current weather patterns for Miami Beach, FL...",
                "progress_percentage": 65,
                "started_at": "2025-10-28T14:32:10Z",
                "completed_at": None,
                "execution_time_seconds": None,
                "error_message": None,
                "messages": [
                    {
                        "from": "coordinator",
                        "to": "risk_assessment",
                        "content": "Analyze hurricane risk for Miami Beach, FL",
                        "timestamp": "2025-10-28T14:32:10Z"
                    }
                ],
                "tokens_used": 1523,
                "cost_estimate": 0.0152
            }
        }
