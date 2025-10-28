"""Risk Assessment Agent for natural disaster threat analysis."""

from datetime import datetime
from typing import Any, Dict

from .base_agent import BaseAgent
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class RiskAssessmentAgent(BaseAgent):
    """Agent that analyzes disaster risk for a given location."""

    def __init__(self, claude_client, timeout: int = 30):
        """Initialize Risk Assessment Agent."""
        super().__init__(claude_client, timeout)
        self.agent_type = "risk_assessment"

    async def process(self, crisis_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze disaster risk for the location.

        Args:
            crisis_profile: User's crisis scenario

        Returns:
            Dict with risk assessment data
        """
        self.start_time = datetime.utcnow()

        try:
            # Validate required fields
            self.validate_input(crisis_profile, ['location', 'specific_threat'])

            location = crisis_profile['location']
            threat = crisis_profile['specific_threat']
            task_id = crisis_profile.get('task_id', 'unknown')

            self.log_activity(task_id, "active", f"Analyzing {threat} risk for {location.get('city')}, {location.get('state')}", 25)

            # Build prompt for Claude
            prompt = self._build_risk_prompt(location, threat)
            system_prompt = """You are a disaster risk assessment expert working for FEMA.
You analyze natural disaster threats and provide evidence-based risk assessments.
Your assessments are used to help families prepare for emergencies.
Always cite authoritative sources (NOAA, USGS, FEMA historical data).
Be realistic but not alarmist. Focus on actionable risk levels."""

            # Call Claude API
            response, tokens, cost = await self.claude_client.generate_async(
                prompt=prompt,
                system=system_prompt,
                max_tokens=2000
            )

            self.log_activity(task_id, "active", "Processing risk analysis data", 75)

            # Parse Claude's response into structured format
            risk_assessment = self._parse_risk_response(response, location, threat)
            risk_assessment['tokens_used'] = tokens
            risk_assessment['cost_estimate'] = cost

            self.end_time = datetime.utcnow()
            self.log_activity(task_id, "complete", f"Risk level: {risk_assessment['overall_risk_level']}", 100)

            return risk_assessment

        except Exception as e:
            self.end_time = datetime.utcnow()
            logger.error(f"Risk Assessment Agent error: {e}")
            self.log_activity(task_id, "error", f"Error: {str(e)}", 0)
            raise

    def _build_risk_prompt(self, location: Dict[str, Any], threat: str) -> str:
        """Build prompt for risk assessment."""
        city = location.get('city', 'Unknown')
        state = location.get('state', 'Unknown')
        lat = location.get('latitude', 'Unknown')
        lng = location.get('longitude', 'Unknown')

        prompt = f"""Assess the {threat} risk for this location:
City: {city}, {state}
Coordinates: {lat}, {lng}

Provide a comprehensive risk assessment including:

1. SEVERITY SCORE (0-100):
   - 0-25: LOW risk
   - 26-50: MEDIUM risk
   - 51-75: HIGH risk
   - 76-100: EXTREME risk

2. RISK LEVEL: One of EXTREME, HIGH, MEDIUM, or LOW

3. DISTANCE TO THREAT: If applicable (e.g., miles to coast for hurricanes, miles to fault line for earthquakes)

4. HISTORICAL CONTEXT: Brief history of {threat}s in this area (past 30 years)

5. SPECIFIC WARNINGS: 3-5 bullet points of immediate threats or concerns

6. EVACUATION RECOMMENDATION: Yes or No, with brief rationale

7. TIME SENSITIVE: Is this an imminent threat requiring immediate action?

8. RECOMMENDATIONS: 2-4 immediate action items based on the risk level

Format your response as JSON with these fields:
{{
  "severity_score": <number 0-100>,
  "risk_level": "<EXTREME|HIGH|MEDIUM|LOW>",
  "distance_to_threat": <number or null>,
  "historical_context": "<string>",
  "specific_warnings": ["<warning1>", "<warning2>", ...],
  "evacuation_recommended": <true|false>,
  "time_sensitive": <true|false>,
  "recommendations": ["<rec1>", "<rec2>", ...],
  "source": "AI Risk Assessment + FEMA + <other sources>"
}}

Be specific to {threat} risks. Use real data when possible."""

        return prompt

    def _parse_risk_response(self, response: str, location: Dict[str, Any], threat: str) -> Dict[str, Any]:
        """Parse Claude's response into structured risk assessment."""
        import json

        try:
            # Try to extract JSON from response
            # Claude might wrap it in markdown code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)

            # Build structured risk assessment
            risk_assessment = {
                "task_id": location.get('task_id', ''),
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "location": f"{location.get('city')}, {location.get('state')}",
                "primary_threat": {
                    "threat_type": threat,
                    "severity_score": data.get("severity_score", 50),
                    "risk_level": data.get("risk_level", "MEDIUM"),
                    "distance_to_threat": data.get("distance_to_threat"),
                    "historical_context": data.get("historical_context", "No historical data available"),
                    "specific_warnings": data.get("specific_warnings", [])
                },
                "secondary_threats": [],  # Can be expanded later
                "overall_severity_score": data.get("severity_score", 50),
                "overall_risk_level": data.get("risk_level", "MEDIUM"),
                "time_sensitive": data.get("time_sensitive", False),
                "evacuation_recommended": data.get("evacuation_recommended", False),
                "recommendations": data.get("recommendations", []),
                "source": data.get("source", "AI Risk Assessment Agent")
            }

            return risk_assessment

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(f"Could not parse structured response: {e}. Using fallback.")

            # Fallback: Create basic assessment
            return {
                "task_id": location.get('task_id', ''),
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "location": f"{location.get('city')}, {location.get('state')}",
                "primary_threat": {
                    "threat_type": threat,
                    "severity_score": 50,
                    "risk_level": "MEDIUM",
                    "distance_to_threat": None,
                    "historical_context": response[:200],  # Use first part of response
                    "specific_warnings": ["Unable to parse detailed warnings. Please check with local authorities."]
                },
                "secondary_threats": [],
                "overall_severity_score": 50,
                "overall_risk_level": "MEDIUM",
                "time_sensitive": False,
                "evacuation_recommended": False,
                "recommendations": ["Consult local emergency management", "Monitor weather/alerts", "Prepare emergency supplies"],
                "source": "AI Risk Assessment Agent"
            }
