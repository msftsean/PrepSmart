"""Supply Planning Agent for emergency supply list generation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .base_agent import BaseAgent
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class SupplyPlanningAgent(BaseAgent):
    """Agent that creates personalized emergency supply lists."""

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

    async def process(self, crisis_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create personalized supply plan.

        Args:
            crisis_profile: User's crisis scenario

        Returns:
            Dict with supply plan data
        """
        self.start_time = datetime.utcnow()

        try:
            # Validate required fields
            self.validate_input(crisis_profile, ['specific_threat', 'household', 'budget_tier'])

            threat = crisis_profile['specific_threat']
            household = crisis_profile['household']
            budget = crisis_profile['budget_tier']
            task_id = crisis_profile.get('task_id', 'unknown')

            household_size = household.get('adults', 0) + household.get('children', 0)

            self.log_activity(task_id, "active", f"Creating supply plan for {household_size} people with ${budget} budget", 25)

            # Get risk assessment if available (for context)
            risk_level = crisis_profile.get('risk_assessment', {}).get('overall_risk_level', 'MEDIUM')

            # Build prompt for Claude
            prompt = self._build_supply_prompt(threat, household, budget, risk_level)
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

            self.log_activity(task_id, "active", "Processing supply recommendations", 75)

            # Parse Claude's response
            supply_plan = self._parse_supply_response(response, threat, household_size, budget)
            supply_plan['tokens_used'] = tokens
            supply_plan['cost_estimate'] = cost

            self.end_time = datetime.utcnow()
            self.log_activity(task_id, "complete", f"Supply plan ready: {supply_plan['total_items']} items", 100)

            return supply_plan

        except Exception as e:
            self.end_time = datetime.utcnow()
            logger.error(f"Supply Planning Agent error: {e}")
            self.log_activity(task_id, "error", f"Error: {str(e)}", 0)
            raise

    def _build_supply_prompt(self, threat: str, household: Dict, budget: int, risk_level: str) -> str:
        """Build prompt for supply planning."""
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
  "acquisition_timeline": "Purchase within X hours/days"
}}

Be specific to {threat}. Scale quantities for {adults + children} people. Stay within ${budget} budget."""

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
