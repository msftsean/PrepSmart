"""Claude API client for PrepSmart."""

import asyncio
from typing import Optional

from anthropic import Anthropic, AsyncAnthropic

from ..utils.config import settings
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ClaudeClient:
    """Client for interacting with Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client.

        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        self.api_key = api_key or settings.claude_api_key
        self.client = Anthropic(api_key=self.api_key)
        self.async_client = AsyncAnthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Latest Sonnet 4.5 (2025)
        self.max_tokens = 4096

    def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: Optional[int] = None,
        temperature: float = 1.0
    ) -> tuple[str, int, float]:
        """
        Generate text using Claude API (synchronous).

        Args:
            prompt: User prompt
            system: System prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Tuple of (response_text, tokens_used, cost_estimate)
        """
        try:
            logger.info(f"Generating with Claude: prompt length={len(prompt)}")

            # Build request parameters
            params = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }

            # Add system prompt if provided
            if system:
                params["system"] = system

            response = self.client.messages.create(**params)

            text = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens

            # Estimate cost (Claude Sonnet 4.5 pricing)
            # Input: $3/MTok, Output: $15/MTok
            input_cost = (response.usage.input_tokens / 1_000_000) * 3
            output_cost = (response.usage.output_tokens / 1_000_000) * 15
            cost = input_cost + output_cost

            logger.info(f"Claude response: {len(text)} chars, {tokens} tokens, ${cost:.4f}")

            return text, tokens, cost

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    async def generate_async(
        self,
        prompt: str,
        system: str = "",
        max_tokens: Optional[int] = None,
        temperature: float = 1.0
    ) -> tuple[str, int, float]:
        """
        Generate text using Claude API (asynchronous).

        Args:
            prompt: User prompt
            system: System prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Tuple of (response_text, tokens_used, cost_estimate)
        """
        try:
            logger.info(f"Generating async with Claude: prompt length={len(prompt)}")

            # Build request parameters
            params = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }

            # Add system prompt if provided
            if system:
                params["system"] = system

            response = await self.async_client.messages.create(**params)

            text = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens

            # Estimate cost
            input_cost = (response.usage.input_tokens / 1_000_000) * 3
            output_cost = (response.usage.output_tokens / 1_000_000) * 15
            cost = input_cost + output_cost

            logger.info(f"Claude async response: {len(text)} chars, {tokens} tokens, ${cost:.4f}")

            return text, tokens, cost

        except Exception as e:
            logger.error(f"Claude API async error: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test Claude API connection.

        Returns:
            True if connection successful
        """
        try:
            response, _, _ = self.generate("Hello, Claude!", max_tokens=50)
            return len(response) > 0
        except Exception as e:
            logger.error(f"Claude connection test failed: {e}")
            return False
