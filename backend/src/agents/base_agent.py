"""Base agent interface for PrepSmart."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from ..services.claude_client import ClaudeClient
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all PrepSmart agents."""

    def __init__(self, claude_client: ClaudeClient, timeout: int = 30):
        """
        Initialize base agent.

        Args:
            claude_client: Claude API client
            timeout: Maximum execution time in seconds
        """
        self.claude_client = claude_client
        self.timeout = timeout
        self.agent_name = self.__class__.__name__.replace("Agent", " Agent")
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    @abstractmethod
    async def process(self, crisis_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process crisis profile and generate agent-specific output.

        This method must be implemented by each agent.

        Args:
            crisis_profile: User's crisis scenario data

        Returns:
            Dict containing agent's output

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
