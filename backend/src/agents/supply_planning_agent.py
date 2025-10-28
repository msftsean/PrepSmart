"""Supply Planning Agent for emergency supply list generation.

Supports dual-mode operation:
- natural_disaster: Emergency supplies (water, food, batteries, first aid)
- economic_crisis: Food stockpiling within budget constraints
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .base_agent import BaseAgent
from ..models.blackboard import Blackboard
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class SupplyPlanningAgent(BaseAgent):
    """Agent that creates personalized supply lists for crisis scenarios.

    Mode-adaptive behavior:
    - Natural disaster: Emergency supplies for immediate survival
    - Economic crisis: Food stockpiling for 30-90 day runway
    """

    def __init__(self, claude_client, timeout: int = 30):
        """Initialize Supply Planning Agent."""
        super().__init__(claude_client, timeout)
        self.agent_type = "supply_planning"
        self.supply_templates = self._load_supply_templates()

    def _load_supply_templates(self) -> Dict[str, Any]:
        """Load supply templates from data file."""
        # For now, return a basic template
        # TODO: Load from backend/src/data/supply_templates.json
        return {
            "hurricane": {
                "critical": [
                    {"name": "Water", "unit": "gallon", "price_per_unit": 1.5, "priority": "critical"},
                    {"name": "Non-perishable food", "unit": "day", "price_per_unit": 8.0, "priority": "critical"},
                    {"name": "Flashlight with batteries", "unit": "piece", "price_per_unit": 15.0, "priority": "critical"},
                    {"name": "Battery-powered radio", "unit": "piece", "price_per_unit": 20.0, "priority": "critical"},
                    {"name": "First aid kit", "unit": "piece", "price_per_unit": 18.0, "priority": "critical"},
                ],
                "prepared": [
                    {"name": "Extra batteries", "unit": "pack", "price_per_unit": 12.0, "priority": "prepared"},
                    {"name": "Manual can opener", "unit": "piece", "price_per_unit": 5.0, "priority": "prepared"},
                    {"name": "Hygiene items", "unit": "set", "price_per_unit": 15.0, "priority": "prepared"},
                ]
            },
            "earthquake": {
                "critical": [
                    {"name": "Water", "unit": "gallon", "price_per_unit": 1.5, "priority": "critical"},
                    {"name": "Non-perishable food", "unit": "day", "price_per_unit": 8.0, "priority": "critical"},
                    {"name": "Flashlight", "unit": "piece", "price_per_unit": 15.0, "priority": "critical"},
                    {"name": "First aid kit", "unit": "piece", "price_per_unit": 18.0, "priority": "critical"},
                    {"name": "Whistle", "unit": "piece", "price_per_unit": 3.0, "priority": "critical"},
                ]
            }
        }

    async def process(self, blackboard: Blackboard) -> Blackboard:
        """
        Create personalized supply plan using blackboard pattern.

        Reads from blackboard:
        - crisis_profile (crisis_mode, specific_threat, household, budget_tier)
        - risk_assessment (for context on severity)

        Writes to blackboard:
        - supply_plan (tier-based supply recommendations)

        Args:
            blackboard: Shared blackboard state

        Returns:
            Updated blackboard with supply_plan populated
        """
        self.start_time = datetime.utcnow()
        crisis_profile = blackboard.crisis_profile

        if not crisis_profile:
            raise ValueError("Blackboard missing crisis_profile")

        task_id = crisis_profile.get('task_id', 'unknown')
        crisis_mode = crisis_profile.get('crisis_mode')

        # Get mode-specific UI presentation
        agent_label = self.get_agent_label(crisis_mode)
        agent_emoji = self.get_agent_emoji(crisis_mode)

        logger.info(f"{agent_emoji} {agent_label} starting for task_id={task_id}, mode={crisis_mode}")

        try:
            # Route to mode-specific processing
            if crisis_mode == "natural_disaster":
                supply_plan = await self._process_natural_disaster(crisis_profile, blackboard, task_id)
            elif crisis_mode == "economic_crisis":
                supply_plan = await self._process_economic_crisis(crisis_profile, blackboard, task_id)
            else:
                raise ValueError(f"Unknown crisis_mode: {crisis_mode}")

            # Write to blackboard
            blackboard.supply_plan = supply_plan
            blackboard.mark_agent_complete(
                self.agent_class_name,
                self.tokens_used,
                self.cost
            )

            self.end_time = datetime.utcnow()
            logger.info(f"{agent_emoji} {agent_label} completed: {supply_plan.get('total_items', 0)} items")

            return blackboard

        except Exception as e:
            self.end_time = datetime.utcnow()
            logger.error(f"{agent_emoji} {agent_label} error: {e}")
            raise

    async def _process_natural_disaster(
        self,
        crisis_profile: Dict[str, Any],
        blackboard: Blackboard,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Process natural disaster supply planning.

        Creates emergency supply list for immediate survival (72 hours - 2 weeks).

        Args:
            crisis_profile: User's crisis scenario
            blackboard: Current blackboard state
            task_id: Task identifier

        Returns:
            Supply plan with tier-based recommendations
        """
        # Validate required fields
        self.validate_input(crisis_profile, ['specific_threat', 'household', 'budget_tier'])

        threat = crisis_profile['specific_threat']
        household = crisis_profile['household']
        budget = crisis_profile['budget_tier']

        household_size = household.get('adults', 0) + household.get('children', 0)

        logger.info(f"📦 Creating emergency supply plan for {household_size} people with ${budget} budget")

        # Get risk assessment from blackboard
        risk_level = "MEDIUM"
        if blackboard.risk_assessment:
            risk_level = blackboard.risk_assessment.get('overall_risk_level', 'MEDIUM')

        # Build prompt for Claude
        prompt = self._build_natural_disaster_prompt(threat, household, budget, risk_level)
        system_prompt = """You are an emergency preparedness supply planning expert.
You help families prepare emergency supply kits based on their specific situation and budget.
You must respect budget constraints and provide practical, actionable recommendations.
Always include free alternatives when possible.
Base recommendations on FEMA and Red Cross guidance."""

        # Call Claude API
        response, tokens, cost = await self.claude_client.generate_async(
            prompt=prompt,
            system=system_prompt,
            max_tokens=3000
        )

        self.tokens_used = tokens
        self.cost = cost

        logger.info(f"📦 Processing supply recommendations (tokens={tokens}, cost=${cost:.4f})")

        # Parse Claude's response
        supply_plan = self._parse_supply_response(response, threat, household_size, budget)
        supply_plan['tokens_used'] = tokens
        supply_plan['cost_estimate'] = cost
        supply_plan['task_id'] = task_id

        return supply_plan

    async def _process_economic_crisis(
        self,
        crisis_profile: Dict[str, Any],
        blackboard: Blackboard,
        task_id: str
    ) -> Dict[str, Any]:
        """
        Process economic crisis supply planning.

        Creates food stockpiling plan for 30-90 day runway within budget constraints.

        Args:
            crisis_profile: User's crisis scenario
            blackboard: Current blackboard state
            task_id: Task identifier

        Returns:
            Supply plan focused on food security
        """
        # Validate required fields
        self.validate_input(crisis_profile, ['specific_threat', 'household', 'budget_tier'])

        threat = crisis_profile['specific_threat']
        household = crisis_profile['household']
        budget = crisis_profile['budget_tier']
        runtime_questions = crisis_profile.get('runtime_questions', {})

        household_size = household.get('adults', 0) + household.get('children', 0)

        logger.info(f"📊 Creating economic crisis supply plan for {household_size} people with ${budget} budget")

        # Get risk assessment from blackboard
        runway = "Unknown"
        primary_concern = runtime_questions.get('primary_concern', 'Unknown')

        if blackboard.risk_assessment:
            runway = blackboard.risk_assessment.get('financial_runway', 'Unknown')

        # Build prompt for Claude
        prompt = self._build_economic_crisis_prompt(
            threat, household, budget, runway, primary_concern, runtime_questions
        )
        system_prompt = """You are a financial crisis preparedness expert specializing in food security.
You help families build affordable food stockpiles for economic uncertainty (job loss, recession, inflation).
You must respect strict budget constraints and focus on maximizing calories per dollar.
Prioritize non-perishable staples with long shelf life.
Base recommendations on USDA nutrition guidelines and emergency food storage best practices."""

        # Call Claude API
        response, tokens, cost = await self.claude_client.generate_async(
            prompt=prompt,
            system=system_prompt,
            max_tokens=3000
        )

        self.tokens_used = tokens
        self.cost = cost

        logger.info(f"📊 Processing food stockpiling recommendations (tokens={tokens}, cost=${cost:.4f})")

        # Parse Claude's response
        supply_plan = self._parse_supply_response(response, threat, household_size, budget)
        supply_plan['tokens_used'] = tokens
        supply_plan['cost_estimate'] = cost
        supply_plan['task_id'] = task_id
        supply_plan['financial_runway'] = runway
        supply_plan['primary_concern'] = primary_concern

        return supply_plan

    def _build_natural_disaster_prompt(self, threat: str, household: Dict, budget: int, risk_level: str) -> str:
        """Build prompt for natural disaster supply planning."""
        adults = household.get('adults', 0)
        children = household.get('children', 0)
        pets = household.get('pets', 0)
        special_needs = household.get('special_needs', '')

        prompt = f"""Create an emergency supply list for a {threat} scenario:

Household:
- Adults: {adults}
- Children: {children}
- Pets: {pets}
- Special needs: {special_needs or 'None'}

Budget: ${budget}
Risk Level: {risk_level}

Create a supply list with these THREE tiers:

1. CRITICAL tier (bare minimum for 72 hours survival)
2. PREPARED tier (extended safety for 1 week)
3. COMPREHENSIVE tier (maximum readiness for 2+ weeks)

For the ${budget} budget, ONLY include items up to the appropriate tier.
- $50 budget = CRITICAL tier only
- $100 budget = CRITICAL + PREPARED tiers
- $200+ budget = ALL three tiers

STRICT BUDGET ENFORCEMENT:
- NEVER exceed ${budget} total cost
- If EXTREME risk + $50 budget, include warning about limited supplies
- Prioritize survival essentials (water, food, first aid) over convenience

For each item, provide:
- Name
- Quantity (scaled for household size)
- Unit (gallons, pieces, days)
- Estimated price
- Priority tier (critical/prepared/comprehensive)
- Category (water/food/first_aid/tools/etc)
- Free alternatives where possible
- Rationale (why needed)

Return as JSON:
{{
  "recommended_tier": "critical|prepared|comprehensive",
  "tiers": {{
    "critical": {{
      "items": [
        {{
          "name": "Water",
          "quantity": 9,
          "unit": "gallons",
          "estimated_price": 12.00,
          "category": "water",
          "alternatives": ["Fill bathtub and containers at home (FREE)"],
          "rationale": "1 gallon per person per day for 3 days"
        }},
        ...
      ],
      "total_cost": 90.00,
      "duration_days": 3
    }},
    "prepared": {{ ... }},
    "comprehensive": {{ ... }}
  }},
  "storage_tips": ["tip1", "tip2", ...],
  "acquisition_timeline": "Purchase within X hours/days",
  "budget_warning": "Optional warning if EXTREME risk + low budget"
}}

Be specific to {threat}. Scale quantities for {adults + children} people. Stay within ${budget} budget."""

        return prompt

    def _build_economic_crisis_prompt(
        self,
        threat: str,
        household: Dict,
        budget: int,
        runway: str,
        primary_concern: str,
        runtime_questions: Dict
    ) -> str:
        """Build prompt for economic crisis supply planning (food stockpiling)."""
        adults = household.get('adults', 0)
        children = household.get('children', 0)
        pets = household.get('pets', 0)
        special_needs = household.get('special_needs', '')

        # Extract runtime question: What should we prioritize in your budget?
        priority = runtime_questions.get('budget_priority', 'balanced nutrition and shelf life')

        prompt = f"""Create a food stockpiling plan for economic crisis ({threat}):

Household:
- Adults: {adults}
- Children: {children}
- Pets: {pets}
- Special needs: {special_needs or 'None'}

Financial Situation:
- Budget: ${budget}
- Estimated runway: {runway}
- Primary concern: {primary_concern}
- Budget priority: {priority}

Create a food stockpiling plan with these THREE tiers:

1. CRITICAL tier (30 days of essential calories)
2. PREPARED tier (60 days of balanced nutrition)
3. COMPREHENSIVE tier (90 days with variety)

For the ${budget} budget, ONLY include items up to the appropriate tier.
- $50 budget = CRITICAL tier only (maximize calories/dollar)
- $100 budget = CRITICAL + PREPARED tiers
- $200+ budget = ALL three tiers

ECONOMIC CRISIS FOCUS:
- Prioritize non-perishable staples (rice, beans, pasta, canned goods)
- Maximize shelf life (1+ year)
- Focus on calories per dollar
- Include protein sources (canned tuna, peanut butter, dried beans)
- Consider dietary restrictions in household
- NEVER exceed ${budget} total cost

For each item, provide:
- Name
- Quantity (pounds, cans, boxes)
- Unit
- Estimated price
- Priority tier (critical/prepared/comprehensive)
- Category (grains/protein/canned_goods/etc)
- Shelf life
- Calories per dollar (rough estimate)
- Storage tips
- Rationale

Return as JSON:
{{
  "recommended_tier": "critical|prepared|comprehensive",
  "tiers": {{
    "critical": {{
      "items": [
        {{
          "name": "White Rice (bulk)",
          "quantity": 20,
          "unit": "pounds",
          "estimated_price": 15.00,
          "category": "grains",
          "shelf_life": "2-3 years",
          "calories_per_dollar": "~1200 cal/$1",
          "storage_tips": "Store in airtight container",
          "rationale": "High calories per dollar, long shelf life, versatile"
        }},
        ...
      ],
      "total_cost": 45.00,
      "duration_days": 30,
      "total_calories": 54000
    }},
    "prepared": {{ ... }},
    "comprehensive": {{ ... }}
  }},
  "storage_tips": ["Cool, dry place", "Airtight containers", "Rotate stock"],
  "acquisition_timeline": "Purchase gradually over 2-4 weeks to spread cost",
  "nutritional_notes": "Supplement with vitamins if needed"
}}

Be specific to economic crisis food security. Scale for {adults + children} people. Respect ${budget} budget strictly."""

        return prompt

    def _parse_supply_response(self, response: str, threat: str, household_size: int, budget: int) -> Dict[str, Any]:
        """Parse Claude's response into structured supply plan."""
        try:
            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)

            # Build structured supply plan
            supply_plan = {
                "task_id": '',
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "crisis_type": threat,
                "household_size": household_size,
                "budget_constraint": budget,
                "tiers": data.get("tiers", {}),
                "recommended_tier": data.get("recommended_tier", "critical"),
                "total_items": sum(len(tier.get("items", [])) for tier in data.get("tiers", {}).values() if isinstance(tier, dict)),
                "storage_tips": data.get("storage_tips", ["Store in waterproof container", "Keep supplies accessible"]),
                "acquisition_timeline": data.get("acquisition_timeline", "Purchase as soon as possible")
            }

            return supply_plan

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not parse supply response: {e}. Using fallback.")

            # Fallback: Use template-based supply list
            return self._generate_fallback_supply_plan(threat, household_size, budget)

    def _generate_fallback_supply_plan(self, threat: str, household_size: int, budget: int) -> Dict[str, Any]:
        """Generate fallback supply plan using templates."""
        # Get template for threat type
        template = self.supply_templates.get(threat, self.supply_templates.get("hurricane", {}))

        # Scale quantities for household size
        critical_items = []
        total_cost = 0

        for item in template.get("critical", []):
            quantity = self._scale_quantity(item, household_size)
            price = quantity * item['price_per_unit']

            if total_cost + price <= budget:
                critical_items.append({
                    "name": item['name'],
                    "quantity": quantity,
                    "unit": item['unit'],
                    "estimated_price": price,
                    "priority": "critical",
                    "category": "essential",
                    "alternatives": [f"Check home supplies first"],
                    "rationale": f"Essential for {threat} preparedness"
                })
                total_cost += price

        return {
            "task_id": '',
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "crisis_type": threat,
            "household_size": household_size,
            "budget_constraint": budget,
            "tiers": {
                "critical": {
                    "tier_name": "Critical",
                    "description": "Bare minimum for 72 hours",
                    "items": critical_items,
                    "total_cost": total_cost,
                    "duration_days": 3
                }
            },
            "recommended_tier": "critical",
            "total_items": len(critical_items),
            "storage_tips": ["Store in cool, dry place", "Keep supplies together in one location"],
            "acquisition_timeline": "Purchase immediately if threat is imminent"
        }

    def _scale_quantity(self, item: Dict, household_size: int) -> int:
        """Scale item quantity based on household size."""
        base_quantity = 1

        if item['name'].lower() in ['water', 'food']:
            # Scale by household size (per person)
            base_quantity = household_size

        if item['unit'] == 'day':
            # Food is typically counted in days
            base_quantity = household_size * 3  # 3 days

        return max(1, base_quantity)
