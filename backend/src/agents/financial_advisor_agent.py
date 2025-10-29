"""Financial Advisor Agent for economic crisis planning.

IMPORTANT: This agent ONLY runs for economic_crisis mode.
For natural disasters, this agent is skipped entirely.
"""

import json
from datetime import datetime
from typing import Any, Dict

from .base_agent import BaseAgent
from ..models.blackboard import Blackboard
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class FinancialAdvisorAgent(BaseAgent):
    """Agent that creates 30-day economic survival strategies.

    Economic crisis only: Provides expense categorization, daily action plans,
    benefits eligibility, and hardship letter templates.
    """

    def __init__(self, claude_client, timeout: int = 30):
        """Initialize Financial Advisor Agent."""
        super().__init__(claude_client, timeout)
        self.agent_type = "financial_advisor"

    async def process(self, blackboard: Blackboard) -> Blackboard:
        """
        Create 30-day economic survival plan using blackboard pattern.

        ONLY runs for economic_crisis mode.

        Reads from blackboard:
        - crisis_profile (crisis_mode, specific_threat, household, budget_tier, runtime_questions)
        - risk_assessment (for financial runway context)

        Writes to blackboard:
        - economic_plan (expense categorization, daily actions, benefits, letters)

        Args:
            blackboard: Shared blackboard state

        Returns:
            Updated blackboard with economic_plan populated
        """
        self.start_time = datetime.utcnow()
        crisis_profile = blackboard.crisis_profile

        if not crisis_profile:
            raise ValueError("Blackboard missing crisis_profile")

        task_id = crisis_profile.get('task_id', 'unknown')
        crisis_mode = crisis_profile.get('crisis_mode')

        # Validate this agent should run
        if crisis_mode != "economic_crisis":
            logger.warning(
                f"💼 Financial Advisor Agent skipped: only runs for economic_crisis, got {crisis_mode}"
            )
            # Don't mark as failed, just skip
            return blackboard

        # Get mode-specific UI presentation
        agent_label = self.get_agent_label(crisis_mode)
        agent_emoji = self.get_agent_emoji(crisis_mode)

        logger.info(f"{agent_emoji} {agent_label} starting for task_id={task_id}")

        try:
            # Validate required fields
            self.validate_input(crisis_profile, ['specific_threat', 'household', 'budget_tier'])

            threat = crisis_profile['specific_threat']
            household = crisis_profile['household']
            budget = crisis_profile['budget_tier']
            runtime_questions = crisis_profile.get('runtime_questions', {})

            household_size = household.get('adults', 0) + household.get('children', 0)

            logger.info(
                f"{agent_emoji} Creating 30-day survival strategy for {threat} "
                f"({household_size} people, ${budget} budget)"
            )

            # Get risk assessment from blackboard for context
            financial_runway = "Unknown"
            risk_level = "MEDIUM"

            if blackboard.risk_assessment:
                financial_runway = blackboard.risk_assessment.get('financial_runway', 'Unknown')
                risk_level = blackboard.risk_assessment.get('overall_risk_level', 'MEDIUM')

            # Build prompt for Claude
            prompt = self._build_financial_advisor_prompt(
                threat, household, budget, financial_runway, risk_level, runtime_questions
            )

            system_prompt = """You are a financial crisis survival expert with expertise in:
- Emergency budgeting for sudden income loss
- Government benefits programs (unemployment, SNAP, Medicaid, rental assistance)
- Creditor negotiation and hardship programs
- Cash flow management during financial shocks

You help families create actionable 30-day survival strategies for economic crises.
You must be realistic about timeline (benefits take weeks), empathetic to stress,
and provide concrete daily actions (not generic advice).

Base recommendations on:
- CFPB (Consumer Financial Protection Bureau) guidance
- State unemployment program rules
- Federal benefits eligibility criteria
- Proven debt management strategies

IMPORTANT: Return valid JSON only. Ensure all strings are properly escaped with no unescaped quotes or newlines inside string values. Use \\n for newlines within strings."""

            # Call Claude API
            response, tokens, cost = await self.claude_client.generate_async(
                prompt=prompt,
                system=system_prompt,
                max_tokens=4000
            )

            self.tokens_used = tokens
            self.cost = cost

            logger.info(f"{agent_emoji} Processing economic plan (tokens={tokens}, cost=${cost:.4f})")

            # Parse Claude's response
            economic_plan = self._parse_economic_response(
                response, threat, household_size, budget, financial_runway, task_id
            )
            economic_plan['tokens_used'] = tokens
            economic_plan['cost_estimate'] = cost

            # Write to blackboard
            blackboard.economic_plan = economic_plan
            blackboard.mark_agent_complete(
                self.agent_class_name,
                self.tokens_used,
                self.cost
            )

            self.end_time = datetime.utcnow()

            # Log completion for UI
            self.log_activity(
                task_id,
                "completed",
                "Economic survival strategy complete",
                100
            )

            logger.info(
                f"{agent_emoji} {agent_label} completed: "
                f"{len(economic_plan.get('daily_actions', []))} daily actions, "
                f"{len(economic_plan.get('eligible_benefits', []))} benefits identified"
            )

            return blackboard

        except Exception as e:
            self.end_time = datetime.utcnow()
            logger.error(f"{agent_emoji} {agent_label} error: {e}")
            raise

    def _build_financial_advisor_prompt(
        self,
        threat: str,
        household: Dict,
        budget: int,
        financial_runway: str,
        risk_level: str,
        runtime_questions: Dict
    ) -> str:
        """Build prompt for 30-day economic survival planning."""
        adults = household.get('adults', 0)
        children = household.get('children', 0)
        special_needs = household.get('special_needs', '')

        # Extract runtime questions
        primary_concern = runtime_questions.get('primary_concern', 'Unknown')
        current_expenses = runtime_questions.get('current_expenses', 'Unknown')

        prompt = f"""Create a 30-day economic survival strategy for a household facing {threat}:

Household:
- Adults: {adults}
- Children: {children}
- Special needs: {special_needs or 'None'}

Financial Situation:
- Available budget/savings: ${budget}
- Financial runway: {financial_runway}
- Risk level: {risk_level}
- Primary concern: {primary_concern}
- Current monthly expenses: {current_expenses}

Your task is to create a detailed 30-day action plan to help this household survive financially.

PART 1: EXPENSE CATEGORIZATION
Categorize typical household expenses into three buckets:

1. MUST-PAY (Cannot defer without severe consequences):
   - Rent/mortgage
   - Utilities (electricity, water, heat)
   - Groceries (minimum)
   - Essential medications
   - Car payment (if needed for job search)

2. DEFER (Can negotiate 30-90 day forbearance):
   - Credit card payments
   - Student loans
   - Medical bills
   - Non-essential insurance

3. ELIMINATE (Cancel immediately):
   - Streaming services
   - Gym memberships
   - Dining out
   - Non-essential subscriptions

For each expense category, provide:
- Typical monthly amount
- Negotiation strategy (for DEFER items)
- Cancellation steps (for ELIMINATE items)

PART 2: DAILY ACTION PLAN (Days 1-30)
Create a day-by-day checklist of specific actions:

Day 1-3: Immediate crisis response
- File unemployment claim
- Contact landlord/mortgage servicer
- Apply for SNAP benefits
- Contact utility companies about hardship programs

Day 4-7: Benefits and assistance
- Complete unemployment certification
- Visit local food bank
- Apply for Medicaid (if eligible)
- Research rental assistance programs

Day 8-14: Income replacement
- Update resume
- Apply to 10+ jobs
- Sign up for gig work (Uber, TaskRabbit, etc.)
- Explore local temp agencies

Day 15-30: Long-term sustainability
- Follow up on applications
- Attend required unemployment meetings
- Network with contacts
- Plan for next 30 days

PART 3: BENEFITS ELIGIBILITY
Identify programs this household likely qualifies for:

1. Unemployment Insurance
   - Estimated weekly benefit: $XXX
   - Timeline: 2-3 weeks for first payment
   - Duration: Up to 26 weeks (state-dependent)

2. SNAP (Food Stamps)
   - Estimated monthly benefit: $XXX (based on household size)
   - Timeline: 7-30 days for approval
   - Application: Online or in-person

3. Medicaid
   - Eligibility: If income below ${budget}/month threshold
   - Timeline: 30-45 days

4. Emergency Rental Assistance
   - Potential: 1-3 months rent coverage
   - Availability: Limited, apply ASAP

5. Utility Assistance (LIHEAP)
   - Heating/cooling bill help
   - Seasonal availability

PART 4: HARDSHIP LETTER TEMPLATES
Provide 2-3 letter templates for:

1. Landlord (requesting 30-60 day rent deferral)
2. Credit card company (requesting hardship forbearance)
3. Utility company (requesting payment plan)

Each template should:
- Be respectful and concise
- Explain situation briefly
- Propose specific solution (e.g., "defer payment for 60 days, then resume with $50 extra/month")
- Include household details like children

PART 5: SURVIVAL OUTLOOK
Provide three scenarios:

1. Without action: "Savings depleted in X days"
2. With action (cuts + benefits): "Can survive X days"
3. Best case (all benefits + income): "Financial stability restored in X days"

Return as JSON:
{{
  "financial_summary": {{
    "available_savings": {budget},
    "estimated_monthly_expenses_before": 2500,
    "estimated_monthly_expenses_after": 1200,
    "monthly_deficit": -800,
    "runway_days": {financial_runway}
  }},
  "expense_categories": {{
    "must_pay": [
      {{"name": "Rent", "amount": 1200, "strategy": "Contact landlord immediately"}},
      ...
    ],
    "defer": [
      {{"name": "Credit cards", "amount": 200, "strategy": "Call for hardship forbearance"}},
      ...
    ],
    "eliminate": [
      {{"name": "Netflix", "amount": 15, "action": "Cancel online today"}},
      ...
    ]
  }},
  "revised_monthly_expenses": 1200,
  "daily_actions": [
    {{"day": 1, "action": "File unemployment claim online", "priority": "critical", "time_required": "1 hour"}},
    {{"day": 1, "action": "Email landlord about situation", "priority": "critical", "time_required": "30 min"}},
    ...
  ],
  "eligible_benefits": [
    {{
      "program": "Unemployment Insurance",
      "estimated_amount": "$350/week",
      "timeline": "2-3 weeks",
      "application_steps": ["Go to state website", "Create account", "File claim", "Certify weekly"],
      "eligibility_notes": "Must have lost job through no fault of your own"
    }},
    ...
  ],
  "estimated_total_relief": "$1,400-$2,000/month (unemployment + SNAP)",
  "hardship_letters": [
    {{
      "recipient_type": "landlord",
      "template_text": "Dear [Landlord Name],\\n\\nI am writing to inform you...",
      "tips": ["Send via certified mail", "Propose specific payment plan", "Emphasize good rental history"]
    }},
    ...
  ],
  "survival_outlook": {{
    "without_action": "Savings depleted in 15 days, eviction risk in 45 days",
    "with_action": "Can survive 45-60 days with expense cuts + benefits",
    "best_case": "Financial stability restored in 60-90 days if benefits approved and job found"
  }}
}}

Be specific to {threat}. Scale for household of {adults + children} people. Be realistic about timelines and benefit amounts."""

        return prompt

    def _parse_economic_response(
        self,
        response: str,
        threat: str,
        household_size: int,
        budget: int,
        financial_runway: str,
        task_id: str
    ) -> Dict[str, Any]:
        """Parse Claude's response into structured economic plan."""
        try:
            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            # Try to fix common JSON issues
            # Remove any trailing commas before closing braces/brackets
            import re
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)

            # Try parsing
            data = json.loads(json_str)

            # Build structured economic plan
            economic_plan = {
                "task_id": task_id,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "crisis_type": threat,
                "household_size": household_size,
                "financial_summary": data.get("financial_summary", {}),
                "expense_categories": data.get("expense_categories", {}),
                "revised_monthly_expenses": data.get("revised_monthly_expenses", 0),
                "daily_actions": data.get("daily_actions", []),
                "eligible_benefits": data.get("eligible_benefits", []),
                "estimated_total_relief": data.get("estimated_total_relief", "Unknown"),
                "hardship_letters": data.get("hardship_letters", []),
                "survival_outlook": data.get("survival_outlook", {}),
            }

            return economic_plan

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not parse economic response: {e}. Using fallback.")

            # Fallback: Generate basic economic plan
            return self._generate_fallback_economic_plan(
                threat, household_size, budget, financial_runway, task_id
            )

    def _generate_fallback_economic_plan(
        self,
        threat: str,
        household_size: int,
        budget: int,
        financial_runway: str,
        task_id: str
    ) -> Dict[str, Any]:
        """Generate fallback economic plan if parsing fails."""
        return {
            "task_id": task_id,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "crisis_type": threat,
            "household_size": household_size,
            "financial_summary": {
                "available_savings": budget,
                "estimated_monthly_expenses_before": 2500,
                "estimated_monthly_expenses_after": 1500,
                "monthly_deficit": -1500,
                "runway_days": financial_runway
            },
            "expense_categories": {
                "must_pay": [
                    {"name": "Rent/Mortgage", "amount": 1200, "strategy": "Contact landlord/servicer immediately"},
                    {"name": "Utilities", "amount": 200, "strategy": "Apply for hardship programs"},
                    {"name": "Groceries", "amount": 400, "strategy": "Use SNAP, food banks"}
                ],
                "defer": [
                    {"name": "Credit cards", "amount": 300, "strategy": "Call for forbearance programs"},
                    {"name": "Student loans", "amount": 200, "strategy": "Federal loans offer automatic forbearance"}
                ],
                "eliminate": [
                    {"name": "Subscriptions", "amount": 50, "action": "Cancel all non-essential services"},
                    {"name": "Dining out", "amount": 200, "action": "Cook at home exclusively"}
                ]
            },
            "revised_monthly_expenses": 1500,
            "daily_actions": [
                {"day": 1, "action": "File unemployment claim", "priority": "critical", "time_required": "1 hour"},
                {"day": 1, "action": "Contact landlord", "priority": "critical", "time_required": "30 min"},
                {"day": 2, "action": "Apply for SNAP benefits", "priority": "high", "time_required": "1 hour"},
                {"day": 3, "action": "Visit local food bank", "priority": "high", "time_required": "2 hours"}
            ],
            "eligible_benefits": [
                {
                    "program": "Unemployment Insurance",
                    "estimated_amount": "$300-500/week",
                    "timeline": "2-3 weeks",
                    "application_steps": ["Visit state unemployment website", "Create account", "File claim"],
                    "eligibility_notes": "Must have lost job through no fault of your own"
                },
                {
                    "program": "SNAP (Food Stamps)",
                    "estimated_amount": f"${200 * household_size}/month",
                    "timeline": "7-30 days",
                    "application_steps": ["Apply online or in-person", "Provide income docs", "Attend interview"],
                    "eligibility_notes": "Based on household size and income"
                }
            ],
            "estimated_total_relief": "$1,500-$2,500/month",
            "hardship_letters": [
                {
                    "recipient_type": "landlord",
                    "template_text": "Dear Landlord,\n\nI am writing to request a 60-day deferral on rent due to unexpected job loss. I have applied for unemployment and am actively seeking new employment. I propose resuming normal payments on [DATE] with an additional $100/month to catch up. Thank you for your understanding.\n\nSincerely,\n[Your name]",
                    "tips": ["Send via certified mail", "Propose specific repayment plan", "Mention good rental history"]
                }
            ],
            "survival_outlook": {
                "without_action": f"Savings of ${budget} depleted in {int(budget/2500*30)} days",
                "with_action": f"Can survive 45-60 days with cuts and benefits",
                "best_case": "Financial stability in 60-90 days with benefits + new job"
            }
        }
