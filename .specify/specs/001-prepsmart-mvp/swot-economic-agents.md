# SWOT Analysis: Economic Crisis Agent Role Strategy

**Date**: 2025-10-28
**Decision**: Should we use the same 7 agents that adapt behavior based on crisis_mode, or create different specialized agents for economic vs. natural disaster?

---

## Option A: Same 7 Agents with Adaptive Behavior

### Strengths
1. **Code Reusability**: Single agent codebase reduces development time (~30% faster implementation)
2. **Simplified Architecture**: One coordinator, one orchestration pattern, easier to maintain
3. **Consistent User Experience**: Same agent names and UI flow regardless of crisis type
4. **Resource Efficiency**: No duplicate agent infrastructure, lower memory footprint
5. **Easier Testing**: Single test suite per agent with mode-based branches
6. **Unified Logging**: Single logging pattern for all agent activity
7. **Faster MVP Delivery**: Critical for 4-day hackathon deadline

### Weaknesses
1. **Agent Complexity**: Each agent must handle dual-mode logic (if/else branches throughout)
2. **Semantic Mismatch**: "Risk Assessment Agent" works for hurricanes, but feels odd for "financial risk"
3. **Confusing Prompts**: Claude prompts must handle both disaster and economic contexts, potentially diluting quality
4. **Less Focused AI Output**: Generic agent instructions may produce lower quality recommendations
5. **Harder to Optimize**: Difficult to tune agent behavior independently per crisis type
6. **Naming Ambiguity**: "Supply Planning Agent" for both emergency supplies AND food stockpiling feels forced

### Opportunities
1. **Cross-Mode Learning**: Agents could learn patterns across both crisis types
2. **Hybrid Scenarios**: Easy to handle combined crises (e.g., hurricane + unemployment)
3. **Future Scalability**: Adding new crisis types (pandemic, wildfire evacuation) is straightforward
4. **Agent Specialization Over Time**: Start broad, refine with user feedback
5. **Lower Cognitive Load**: Users don't need to understand different agent teams

### Threats
1. **AI Quality Degradation**: Claude may struggle with overly broad agent instructions
2. **Maintenance Complexity**: Future changes risk breaking both modes
3. **User Confusion**: Seeing "Risk Assessment Agent" for financial crisis might feel inappropriate
4. **Demo Clarity**: Judges may not understand why same agents work for hurricanes and unemployment
5. **Technical Debt**: Dual-mode code quickly becomes spaghetti without discipline

---

## Option B: Specialized Agent Teams

**Natural Disaster Team**: Risk Assessment, Supply Planning, Emergency Coordinator, Resource Locator, Video Curator, Emergency Plan Generator, Documentation

**Economic Crisis Team**: Financial Risk Assessor, Budget Planner, Crisis Navigator, Assistance Locator, Resource Curator, Economic Plan Generator, Documentation

### Strengths
1. **Semantic Clarity**: Agent names perfectly match their crisis-specific roles
2. **Focused AI Prompts**: Claude gets laser-focused context, likely higher quality output
3. **Independent Optimization**: Tune economic agents without affecting disaster agents
4. **Demo Impact**: Clear specialization impresses hackathon judges with sophistication
5. **Better User Trust**: "Financial Risk Assessor" feels more credible than generic "Risk Assessment"
6. **Code Clarity**: No if/else mode branches, each agent has single clear purpose
7. **Easier Collaboration**: Different developers can own different agent teams

### Weaknesses
1. **2x Development Time**: Must build and test 14 agents instead of 7 (~80% more work)
2. **Duplicated Infrastructure**: Two coordinators, two orchestration patterns, more complexity
3. **Inconsistent Architecture**: Risk of drift between implementations
4. **Higher Resource Usage**: More agents loaded in memory, higher API costs
5. **Complex Testing**: Double the test suite, double the maintenance burden
6. **Slower MVP**: Incompatible with 4-day hackathon deadline
7. **Coordination Risk**: Two systems to debug, integrate, and deploy

### Opportunities
1. **Premium Feature Path**: Offer specialized agents as paid upgrade
2. **Domain Expertise**: Partner with FEMA for disaster agents, financial advisors for economic agents
3. **Better Marketing**: "14 specialized AI agents" sounds more impressive
4. **Modular Sales**: License disaster agents separately from economic agents
5. **Clearer Metrics**: Track performance independently per crisis type

### Threats
1. **Deadline Failure**: May not finish MVP in time for hackathon
2. **Scope Creep**: Team distracted by perfectionism instead of shipping
3. **Fragmented Codebase**: Harder to maintain long-term consistency
4. **User Confusion**: Which agent team am I using? Adds cognitive load
5. **Resource Limits**: Azure free tier may not support 14 concurrent agents

---

## Decision Matrix

| Criteria | Weight | Option A Score | Option B Score | A Weighted | B Weighted |
|----------|--------|----------------|----------------|------------|------------|
| **Hackathon Deadline (4 days)** | 30% | 9 | 3 | 2.7 | 0.9 |
| **AI Output Quality** | 20% | 6 | 9 | 1.2 | 1.8 |
| **Demo Impact for Judges** | 15% | 6 | 8 | 0.9 | 1.2 |
| **Long-term Maintainability** | 15% | 5 | 7 | 0.75 | 1.05 |
| **User Trust & Clarity** | 10% | 6 | 9 | 0.6 | 0.9 |
| **Resource Efficiency** | 5% | 8 | 4 | 0.4 | 0.2 |
| **Testing Complexity** | 5% | 7 | 4 | 0.35 | 0.2 |
| **TOTAL** | 100% | - | - | **6.9** | **6.25** |

**Option A (Same Agents, Adaptive Behavior) wins by narrow margin: 6.9 vs 6.25**

---

## Recommended Decision: **Option A with Strategic Naming**

### Strategy: Hybrid Approach
Use Option A (same 7 agents) BUT make the agent roles semantically flexible through strategic naming and UI presentation.

### Implementation:

1. **Generic Agent Names (Backend)**:
   - `RiskAssessmentAgent` (handles both disaster risk and financial risk)
   - `PlanningAgent` (handles both supply planning and budget planning)
   - `ResourceLocatorAgent` (handles both shelters and food banks)
   - `CuratorAgent` (handles both videos and resources)
   - `DocumentationAgent` (generates PDFs for both modes)
   - `CoordinatorAgent` (orchestrates regardless of mode)

2. **Mode-Specific UI Labels (Frontend)**:
   - Natural Disaster Mode:
     - "🌪️ Risk Assessment Agent: Analyzing hurricane threat..."
     - "📦 Supply Planning Agent: Building emergency supply list..."
   - Economic Crisis Mode:
     - "💰 Financial Risk Agent: Assessing your financial situation..."
     - "📊 Budget Planning Agent: Creating survival budget..."

3. **Mode-Specific Claude Prompts**:
   - Each agent checks `crisis_mode` and loads appropriate system prompt
   - Natural disaster prompts focus on FEMA guidelines, survival supplies
   - Economic prompts focus on financial survival, benefits, job resources

4. **Runtime User Questions** (for Economic Mode):
   - Before Risk Assessment runs: Ask "What financial risks concern you most?"
   - Before Planning runs: Ask "What should we prioritize in your budget?"
   - Inject user responses into agent context

### Why This Works:
✅ **Meets Deadline**: Single codebase, ships in 4 days
✅ **Quality AI Output**: Mode-specific prompts give Claude focused context
✅ **User Clarity**: UI labels adapt to show relevant agent role
✅ **Demo Impact**: Judges see intelligent mode switching, not duplicate systems
✅ **Maintainable**: Clean separation via prompt templates, not code branches
✅ **Scalable**: Easy to add new modes (pandemic, evacuation, etc.)

### Code Structure Example:

```python
class RiskAssessmentAgent(BaseAgent):
    def __init__(self):
        self.prompts = {
            "natural_disaster": "You are a disaster risk expert analyzing threats for FEMA...",
            "economic_crisis": "You are a financial risk analyst assessing economic vulnerability..."
        }
        self.ui_labels = {
            "natural_disaster": "🌪️ Risk Assessment Agent",
            "economic_crisis": "💰 Financial Risk Agent"
        }

    async def process(self, crisis_profile: Dict) -> Dict:
        mode = crisis_profile['crisis_mode']
        system_prompt = self.prompts[mode]

        # Mode-specific logic
        if mode == "economic_crisis":
            # Ask user: "What financial risks concern you?"
            user_context = await self.ask_user_question(crisis_profile['task_id'],
                "What financial risks concern you most? (e.g., 'I have 2 weeks of savings', 'My rent is due in 3 days')")
            crisis_profile['user_risk_context'] = user_context

        # Process with mode-specific prompt
        result = await self.claude_client.generate_async(
            prompt=self._build_prompt(crisis_profile, mode),
            system=system_prompt
        )

        return self._parse_response(result, mode)
```

---

## Risk Mitigation

### If AI Quality Suffers (Option A fails in testing):
**Fallback Plan**: Create specialized `EconomicRiskAgent` and `FinancialPlanningAgent` to replace generic agents for economic mode only. This is a surgical fix that doesn't require full Option B.

### If Development Takes Too Long:
**Scope Reduction**: Cut economic mode entirely for MVP, focus only on natural disaster (US1, US3 are P1 priorities). Add economic mode as v1.1 post-hackathon.

---

## Final Recommendation

**✅ DECISION: Option A (Same 7 Agents with Adaptive Behavior)**

**Rationale**:
1. **Hackathon deadline is immovable** - Option A is the only realistic path to completion
2. **AI quality can be maintained** through mode-specific prompts and user questions
3. **User experience can be tailored** through dynamic UI labels and emoji icons
4. **Demo value is preserved** by highlighting intelligent mode switching vs brute-force duplication
5. **Technical debt is manageable** with clean prompt template architecture

**Approval Required**: This SWOT analysis and recommendation should be validated before proceeding with implementation.

**Next Steps After Approval**:
1. Create mode-specific prompt templates for each agent
2. Design user question flows for economic crisis mode
3. Update UI mockups with dynamic agent labeling
4. Add prompt template selection to agent base class
5. Write tests for both modes per agent

---

**Version**: 1.0 | **Status**: Awaiting Approval | **Impact**: Critical architectural decision
