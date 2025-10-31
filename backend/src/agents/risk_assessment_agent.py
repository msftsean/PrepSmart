"""Risk Assessment Agent for disaster threat analysis (natural + economic)."""

from datetime import datetime
from typing import Any, Dict

from .base_agent import BaseAgent
from ..models.blackboard import Blackboard
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class RiskAssessmentAgent(BaseAgent):
    """
    Agent that analyzes disaster risk for a given location.

    Supports dual-mode operation:
    - Natural disaster: Analyzes environmental/physical risks (hurricanes, earthquakes, etc.)
    - Economic crisis: Analyzes financial risk based on user's situation
    """

    def __init__(self, claude_client, timeout: int = 30):
        """Initialize Risk Assessment Agent."""
        super().__init__(claude_client, timeout)
        self.agent_type = "risk_assessment"

    async def process(self, blackboard: Blackboard) -> Blackboard:
        """
        Analyze disaster risk using blackboard pattern.

        Reads: crisis_profile from blackboard
        Writes: risk_assessment to blackboard

        Args:
            blackboard: Shared blackboard state

        Returns:
            Updated blackboard with risk_assessment
        """
        self.start_time = datetime.utcnow()

        try:
            # Read from blackboard
            crisis_profile = blackboard.crisis_profile
            if not crisis_profile:
                raise ValueError("Blackboard missing crisis_profile")

            crisis_mode = crisis_profile.get('crisis_mode')
            location = crisis_profile.get('location')
            threat = crisis_profile.get('specific_threat')
            task_id = crisis_profile.get('task_id', 'unknown')

            # Get mode-specific label and emoji
            agent_label = self.get_agent_label(crisis_mode)
            agent_emoji = self.get_agent_emoji(crisis_mode)

            logger.info(f"{agent_emoji} {agent_label} starting for task_id={task_id}")

            self.log_activity(
                task_id,
                "active",
                f"Analyzing {threat} risk for {location.get('city') if location else 'location'}",
                25
            )

            # Mode-specific processing
            if crisis_mode == "natural_disaster":
                risk_assessment = await self._process_natural_disaster(crisis_profile, task_id)
            elif crisis_mode == "economic_crisis":
                risk_assessment = await self._process_economic_crisis(crisis_profile, task_id)
            else:
                raise ValueError(f"Unknown crisis_mode: {crisis_mode}")

            # Write to blackboard
            blackboard.risk_assessment = risk_assessment
            blackboard.mark_agent_complete(
                self.agent_class_name,
                tokens_used=self.tokens_used,
                cost=self.cost
            )

            self.end_time = datetime.utcnow()

            # Log completion for UI
            self.log_activity(
                task_id,
                "completed",
                f"Risk assessment complete: {risk_assessment.get('overall_risk_level')} risk",
                100
            )

            logger.info(
                f"{agent_emoji} {agent_label} completed: "
                f"risk={risk_assessment.get('overall_risk_level')}, "
                f"tokens={self.tokens_used}, cost=${self.cost:.4f}"
            )

            # Log comprehensive debug output
            self.log_agent_output(task_id, risk_assessment, agent_emoji)

            return blackboard

        except Exception as e:
            self.end_time = datetime.utcnow()
            logger.error(f"Risk Assessment Agent error: {e}")
            blackboard.mark_agent_failed(self.agent_class_name, str(e))
            raise

    async def _process_natural_disaster(
        self,
        crisis_profile: Dict[str, Any],
        task_id: str
    ) -> Dict[str, Any]:
        """Process natural disaster risk assessment."""
        location = crisis_profile['location']
        threat = crisis_profile['specific_threat']

        # Build prompt for Claude
        prompt = self._build_natural_disaster_prompt(location, threat)
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

        self.tokens_used = tokens
        self.cost = cost

        self.log_activity(task_id, "active", "Processing risk analysis data", 75)

        # Parse response
        risk_assessment = self._parse_risk_response(response, location, threat)
        risk_assessment['crisis_mode'] = 'natural_disaster'

        return risk_assessment

    async def _process_economic_crisis(
        self,
        crisis_profile: Dict[str, Any],
        task_id: str
    ) -> Dict[str, Any]:
        """Process economic crisis financial risk assessment."""
        threat = crisis_profile['specific_threat']
        runtime_questions = crisis_profile.get('runtime_questions', {})

        # For economic crisis, we need runtime questions
        # TODO: T118 will handle asking questions if not present
        # For now, use defaults if missing
        primary_concern = runtime_questions.get('primary_concern', 'Unknown')
        runway = runtime_questions.get('runway', 'Unknown')

        # Build prompt
        prompt = self._build_economic_crisis_prompt(threat, primary_concern, runway)
        system_prompt = """You are a financial crisis analyst helping people survive economic hardship.
You assess financial risk levels based on their situation (income loss, expenses, savings runway).
Provide realistic, actionable guidance focused on immediate survival (30-90 days).
Be empathetic but honest about risks. Cite resources like unemployment benefits, food assistance."""

        # Call Claude API
        response, tokens, cost = await self.claude_client.generate_async(
            prompt=prompt,
            system=system_prompt,
            max_tokens=1500
        )

        self.tokens_used = tokens
        self.cost = cost

        self.log_activity(task_id, "active", "Analyzing financial risk", 75)

        # Parse response
        risk_assessment = self._parse_economic_risk_response(response, threat, primary_concern, runway)
        risk_assessment['crisis_mode'] = 'economic_crisis'

        return risk_assessment

    def _build_natural_disaster_prompt(self, location: Dict[str, Any], threat: str) -> str:
        """Build prompt for natural disaster risk assessment."""
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


    def _build_economic_crisis_prompt(self, threat: str, primary_concern: str, runway: str) -> str:
        """Build prompt for economic crisis financial risk assessment."""
        prompt = f"""Assess the financial risk for someone facing {threat}.

Context:
- Crisis type: {threat}
- Primary concern: {primary_concern}
- Financial runway: {runway}

Provide a financial risk assessment including:

1. SEVERITY SCORE (0-100):
   - 0-25: LOW financial risk (6+ months runway, stable income)
   - 26-50: MEDIUM risk (3-6 months runway, some income)
   - 51-75: HIGH risk (1-3 months runway, minimal income)
   - 76-100: EXTREME risk (<1 month runway, no income)

2. RISK LEVEL: One of EXTREME, HIGH, MEDIUM, or LOW

3. IMMEDIATE CONCERNS: 3-5 most urgent financial issues to address

4. SURVIVAL TIMELINE: Estimated timeframe before critical situation

5. RECOMMENDATIONS: 3-5 immediate action items for financial survival

Format your response as JSON:
{{
  "severity_score": <number 0-100>,
  "risk_level": "<EXTREME|HIGH|MEDIUM|LOW>",
  "immediate_concerns": ["<concern1>", "<concern2>", ...],
  "survival_timeline": "<timeframe>",
  "recommendations": ["<action1>", "<action2>", ...],
  "source": "Financial Risk Assessment + CFPB + Labor Department guidance"
}}

Be realistic but supportive. Focus on 30-90 day survival strategies."""

        return prompt

    def _parse_economic_risk_response(
        self,
        response: str,
        threat: str,
        primary_concern: str,
        runway: str
    ) -> Dict[str, Any]:
        """Parse economic crisis risk response."""
        import json

        try:
            # Extract JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)

            # Build structured assessment
            risk_assessment = {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "crisis_type": threat,
                "primary_concern": primary_concern,
                "financial_runway": runway,
                "overall_severity_score": data.get("severity_score", 70),
                "overall_risk_level": data.get("risk_level", "HIGH"),
                "immediate_concerns": data.get("immediate_concerns", []),
                "survival_timeline": data.get("survival_timeline", "30-60 days"),
                "recommendations": data.get("recommendations", []),
                "time_sensitive": data.get("severity_score", 70) >= 75,
                "source": data.get("source", "Financial Risk Assessment Agent")
            }

            return risk_assessment

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning(f"Could not parse economic risk response: {e}. Using fallback.")

            # Fallback based on runway
            if "less than 2 weeks" in runway.lower() or "<2" in runway:
                severity = 95
                risk_level = "EXTREME"
            elif "2-4 weeks" in runway.lower():
                severity = 85
                risk_level = "EXTREME"
            elif "1-3 months" in runway.lower():
                severity = 65
                risk_level = "HIGH"
            else:
                severity = 45
                risk_level = "MEDIUM"

            return {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "crisis_type": threat,
                "primary_concern": primary_concern,
                "financial_runway": runway,
                "overall_severity_score": severity,
                "overall_risk_level": risk_level,
                "immediate_concerns": [primary_concern, "Income loss", "Expense management"],
                "survival_timeline": runway,
                "recommendations": [
                    "Apply for unemployment benefits immediately",
                    "Contact creditors about hardship programs",
                    "Find local food assistance resources",
                    "Cut non-essential expenses now"
                ],
                "time_sensitive": severity >= 75,
                "source": "Financial Risk Assessment Agent"
            }
