# PrepSmart MVP - User Clarifications
**Date**: 2025-10-28
**Status**: Approved
**Version**: 1.0

## Purpose
This document captures all user decisions and clarifications that refine the original specification. These decisions supersede any conflicting information in other spec documents.

---

## 1. Agent Orchestration & Dependencies

### Decision: Blackboard Pattern with Parallel Orchestration
- **Pattern**: Implement blackboard shared state architecture
- **Rationale**: Best fit for multi-agent system where agents need to:
  - Share intermediate results
  - Work in parallel when possible
  - React to new information from other agents
- **Agent Dependency Strategy**: Iterative discovery
  - Make best engineering decisions for initial dependencies
  - Adjust based on test results and observed behavior
  - Document dependency changes as they emerge

### Blackboard Architecture Components
1. **Blackboard (Shared State)**:
   - CrisisProfile (input data)
   - RiskAssessment (from Risk Assessment Agent)
   - SupplyPlan (from Supply Planning Agent)
   - FinancialAdvice (from Financial Advisor Agent)
   - ResourceLocations (from Resource Locator Agent)
   - VideoRecommendations (from Video Curator Agent)
   - CompletePlan (from Documentation Agent)

2. **Knowledge Sources (Agents)**:
   - Each agent reads from blackboard
   - Each agent writes results back to blackboard
   - Agents trigger when their preconditions are met

3. **Control Component (Coordinator)**:
   - Monitors blackboard state
   - Determines which agents can run
   - Manages parallel execution
   - Detects completion

---

## 2. Economic Crisis Specifications

### Decision: Dual-Mode Agent Behavior

#### Risk Assessment Agent
- **Natural Disaster Mode**: Assess environmental/physical risks (hurricane severity, earthquake likelihood, etc.)
- **Economic Crisis Mode**: **Ask user at runtime** what financial risks to assess
  - Examples: "How long can you survive without income?" "What bills are at risk?"
  - User provides context, agent analyzes financial risk level

#### Supply Planning Agent
- **Natural Disaster Mode**: Emergency supplies (water, food, batteries, first aid)
- **Economic Crisis Mode**: **Ask user at runtime** for priorities
  - Examples: "Focus on food stockpiling?" "Prioritize medication?" "Essential bills only?"
  - User guides supply focus, agent creates budget-optimized plan

#### Agent Role Strategy
- **Decision**: Perform SWOT analysis to determine if different agent roles needed
- **Action Required**: SWOT analysis comparing:
  - **Option A**: Same 7 agents adapt behavior based on crisis_mode
  - **Option B**: Different specialized agents for economic vs. natural disaster
- **Criteria**: Evaluate complexity, maintainability, user experience, development time

### MVP Economic Crisis Plan: "Survive 30-90 Days"
**Primary Focus** (MVP - v1):
- Survive 30-90 days with available budget
- Essential expenses prioritization
- Food/medication stockpiling strategy
- Immediate cost reduction tactics

**Secondary Feature** (v1.1+): "Strategic Crisis Planning"
- User can toggle this option for expanded guidance:
  - Unemployment benefit filing guidance
  - Resume/job search resources
  - Bill payment prioritization strategies
  - Food assistance program finder
  - Long-term financial recovery planning

**Implementation Note**:
- v1: Simple survival focus, fast to implement
- v1.1: Add `/api/crisis/{task_id}/strategic-plan` endpoint for expanded guidance

---

## 3. Video Curator Agent

### Decision: Static Curated Library (MVP)
- **v1 Approach**: 10-20 manually curated videos per crisis type
- **Source Mix**: Both official sources AND trusted creators
  - Official: FEMA, Red Cross, NOAA, CDC, Department of Labor
  - Trusted: Weather Channel, survival experts, financial advisors (verified credentials)
- **Video Length Filter**: Under 5 minutes per video
- **Future Enhancement**: Real-time API searches if app becomes profitable

### Video Library Structure
```
videos/
  natural_disaster/
    hurricane/
      - fema_hurricane_prep.json (2:45, official)
      - weather_channel_evacuation.json (4:30, trusted)
    earthquake/
      - usgs_earthquake_safety.json (3:15, official)
    wildfire/
    flood/
    tornado/
    blizzard/
  economic_crisis/
    unemployment/
      - dol_filing_benefits.json (4:00, official)
      - financial_advisor_budget.json (3:30, trusted)
    layoff/
    furlough/
    government_shutdown/
```

---

## 4. Resource Locator Agent

### Decision: Comprehensive Resource Finding

#### Natural Disasters
Find and provide:
- Emergency shelters (Red Cross, local)
- Evacuation routes (DOT, local emergency management)
- Hospitals and urgent care centers
- Supply stores (Home Depot, Walmart, Lowe's, local hardware)
- Gas stations (with current availability if possible)
- Pharmacies (24-hour if available)

#### Economic Crisis
Find and provide:
- Food banks and pantries
- Unemployment offices (federal and state)
- Free clinics and community health centers
- Job centers and workforce development
- Public libraries (free internet, resources)
- Social services offices

### Decision: Hybrid Data Approach (Cost Management)
- **Static Database**: Primary source (free, fast, offline-capable)
  - Pre-loaded datasets for common resources
  - FEMA shelter database
  - USDA food bank directory
  - State unemployment office listings
- **Real-Time API**: Secondary/fallback (cost-managed)
  - Google Places API for live data when database insufficient
  - Rate limiting: Max 100 API calls/day for MVP
  - Cache API results for 7 days
  - Use API only for:
    - Locations not in static database
    - User-requested "fresh data" option
    - Verification of critical resources (shelters, hospitals)

**Cost Management**:
- Estimated API usage: 10-30 calls/plan × 1000 plans = 10,000-30,000 calls
- At $17/1000 requests = $170-$510/month if all API
- With hybrid: ~$20-$50/month (90% cache hit rate)

---

## 5. Budget Tiers & Financial Situation

### Decision: Hard Limits for v1
- **Budget Tiers**: $50 / $100 / $200+ are **hard limits**
- Never suggest items that would exceed user's chosen tier
- If critical items exceed budget, show warning: "Your budget may be insufficient for EXTREME risk. Consider increasing to $100 tier."

### Decision: Risk-Based Recommendations (No Override)
- If user selects $50 tier BUT Risk Assessment returns EXTREME:
  - **Do NOT** automatically override to higher tier
  - **DO** show clear warning: "⚠️ EXTREME risk detected. $50 tier may not provide adequate protection. Recommend $100+ tier."
  - **DO** offer "See $100 tier plan" button
  - User must explicitly choose to upgrade

### Decision: Financial Data Collection SWOT Required
**Action Required**: Perform SWOT analysis for collecting additional financial data in economic crisis mode:

**Potential Data to Collect**:
- Current savings amount
- Monthly expenses breakdown
- Debt obligations (rent, mortgage, loans)
- Income sources (unemployment, spouse, side gigs)

**SWOT Criteria**:
- **Strengths**: Better personalized advice, more accurate survival timeline
- **Weaknesses**: User privacy concerns, friction in signup, data security requirements
- **Opportunities**: Premium feature differentiation, long-term financial planning
- **Threats**: User abandonment, regulatory compliance (GDPR, CCPA), data breach risk

**Decision Point**: Based on SWOT, determine:
1. Collect all data upfront (comprehensive but high friction)
2. Collect minimal data, offer optional detailed profile (progressive disclosure)
3. Skip financial data collection for MVP, use budget tier as proxy

---

## 6. Testing & Validation Strategy

### Decision: Minimal Smoke Tests Now, Comprehensive After Hackathon
- **Pre-Hackathon (Option C)**:
  - Write minimal smoke tests for each agent
  - End-to-end test for 5 critical scenarios
  - Focus on "does it work?" not "is it perfect?"
- **Post-Hackathon**:
  - Comprehensive unit tests (80%+ coverage)
  - Integration tests for all user stories
  - Performance tests (< 180 sec per plan)
  - Edge case handling

### Decision: 5 Critical Test Scenarios
**Action Required**: Generate 5 realistic test scenarios covering:
1. High-risk natural disaster (EXTREME risk, low budget)
2. Moderate natural disaster (MEDIUM risk, high budget)
3. Economic crisis (single adult, unemployment, minimal savings)
4. Economic crisis (family of 4, dual income loss, moderate savings)
5. Edge case (rural location, limited resources, EXTREME risk)

**Success Criteria for Each**:
- Plan generated in under 180 seconds
- All 7 agents complete successfully
- PDF downloads without errors
- Budget recommendations stay within tier
- Resources found within 50-mile radius (or note if unavailable)

---

## 7. PDF Documentation Agent

### Decision: Simplified 2-Page PDF (MVP)
- **v1 Scope**: 2-page essential information PDF (~2 hours implementation)
- Reduce from original 6-page spec to core content:

**Page 1: Crisis Overview & Action Plan**
- Crisis type and risk level
- Top 5 immediate actions
- Supply checklist (condensed)
- Emergency contacts

**Page 2: Resources & Budget**
- Local resource map (top 10 locations)
- Budget breakdown
- QR codes for digital resources
- PrepSmart branding

### Decision: PDF Requirements
✅ **Must work offline after generation**: User can print/save without internet
✅ **Include QR codes**: Link to online resources, video playlist, resource map
✅ **Print-optimized layout**: Black & white friendly, high-contrast, readable at 50% scale

---

## 8. Multi-Agent Transparency (Article III)

### Decision: Live Log Stream with Emojis
**UI Display**:
```
🎯 Coordinator Agent: Starting crisis plan for Miami hurricane...
🌪️ Risk Assessment Agent: Analyzing hurricane risk for Miami, FL...
   └─ Risk Level: EXTREME (95/100)
📦 Supply Planning Agent: Building supply list for family of 4...
   └─ 23 items identified within $100 budget
💰 Financial Advisor Agent: Calculating emergency fund needs...
🗺️ Resource Locator Agent: Finding shelters and supply stores...
   └─ Found 12 shelters, 8 supply stores within 20 miles
🎥 Video Curator Agent: Selecting hurricane prep videos...
   └─ 5 videos curated (total runtime: 18 minutes)
📄 Documentation Agent: Generating your personalized plan...
   ✅ Complete! Your crisis plan is ready.
```

**Features**:
- Real-time log streaming (WebSocket or SSE)
- Agent-specific emojis for visual scanning
- Progress indicators (percentage or checkmarks)
- Nested sub-task display (indent with └─)

### Decision: Overall Transparency (Not Per-Data-Field)
- Show what each agent DID (high-level)
- Don't show granular data access ("Agent read field X, Y, Z")
- Example: "Risk Assessment Agent used your location and NOAA historical data" ✅
- Not: "Risk Assessment Agent accessed crisis_profile.location.city, crisis_profile.location.state, noaa_api.hurricane_history..." ❌

---

## 9. Scope for Hackathon Demo

### Decision: Full Dual-Mode End-to-End with Beautiful UI
**Absolute Must-Haves for Demo Day (Oct 27-31)**:
✅ **Both crisis modes working end-to-end**
   - Natural disaster flow (hurricane, earthquake, wildfire, flood, tornado, blizzard)
   - Economic crisis flow (unemployment, layoff, furlough, government shutdown)

✅ **Beautiful UI + working backend**
   - Mobile-responsive (320px+)
   - Real-time agent activity display with emojis
   - Clean, accessible design
   - Fast loading (< 3 sec initial, < 180 sec plan generation)

### Decision: Judging Criteria Assessment
**Hackathon Rules**:
- ✅ One submission per team
- ✅ Original work created during event period (Oct 27-31)
- ✅ Uses AI meaningfully (multi-agent AI system with Claude API)
- ✅ Judged on: creativity, execution, impact

**Winning Strategy**:
1. **Creativity**: Multi-agent architecture + dual crisis modes (natural + economic)
2. **Execution**: Working demo, beautiful UI, comprehensive testing
3. **Impact**: Life-saving potential for disasters + economic hardship

**Time Management Strategy**:
- Assess progress at 12-hour intervals
- If behind schedule, cut scope in this order:
  1. Remove 2-3 natural disaster types (keep hurricane, earthquake only)
  2. Simplify PDF to 1 page
  3. Remove video curation (static list only)
  4. Reduce resource locator to static database only
- Never cut: Core agent functionality, UI polish, one complete user story

---

## 10. Deployment & Access

### Decision: Dual Deployment Strategy
1. **Azure Container Apps** (primary demo)
   - Public URL for judges and users
   - Production-ready deployment
   - Cost estimate: $20-50/month for hackathon period

2. **Local Demo** (backup)
   - Laptop presentation if Azure issues occur
   - Faster demonstration control
   - Fallback for live coding/adjustments

### Decision: Access Control & Rate Limiting
**During Hackathon**:
- Judges: Priority access (no rate limiting)
- Public: Rate limited to 10 requests/hour/IP

**After Hackathon**:
- Public demo URL: Yes, keep live
- Rate limiting:
  - Free tier: 3 plans/day/user
  - Registered users: 10 plans/day
  - Premium (future): Unlimited
- Authentication:
  - MVP: Optional email signup (for saving plans)
  - Required for: Saving multiple plans, accessing strategic planning feature
  - Anonymous: Allowed for 1 plan generation (demo purposes)

**Cost Protection**:
- Hard cap: $200 Claude API spend/month for MVP
- If exceeded, show "Service temporarily at capacity" message
- Monitor spend daily during hackathon

---

## 11. Specification Updates Required

### Action Items (To Be Completed Before Implementation Resumes)

1. **Constitution.md**:
   - Add Article X: "Blackboard Shared State" principle
   - Update Article III transparency requirements with emoji log spec

2. **Spec.md**:
   - Add US6: Strategic Crisis Planning (economic mode secondary feature)
   - Update US2 acceptance criteria with "ask user" interaction requirements
   - Add non-functional requirement: Rate limiting and cost caps

3. **Plan.md**:
   - Replace "custom asyncio orchestration" with "blackboard pattern implementation"
   - Update Phase 3 tasks to reflect dual-mode agent behavior
   - Add Phase 3.5: SWOT analyses (economic agent roles, financial data collection)
   - Adjust time estimates for 2-page PDF vs. 6-page

4. **Tasks.md**:
   - Break down blackboard implementation into tasks
   - Add tasks for static video library curation
   - Add tasks for hybrid resource locator (database + API)
   - Add tasks for live log streaming with emojis
   - Add SWOT analysis tasks

5. **Data-model.md**:
   - Add Blackboard entity/schema
   - Add AgentPrecondition entity (when agent can execute)
   - Update CrisisProfile to support runtime user questions

6. **API-spec.json**:
   - Add `/api/crisis/{task_id}/strategic-plan` endpoint
   - Add `/api/crisis/{task_id}/logs` endpoint (WebSocket or SSE)
   - Add rate limiting headers (X-RateLimit-Remaining, etc.)

7. **Test-scenarios.md** (NEW):
   - Document 5 critical test scenarios with expected outputs

8. **SWOT-economic-agents.md** (NEW):
   - Analyze agent role strategy (same agents vs. specialized)

9. **SWOT-financial-data.md** (NEW):
   - Analyze financial data collection approach

---

## 12. Open Questions (To Be Resolved During Implementation)

1. **Agent Dependencies**: Will be discovered iteratively during testing
2. **WebSocket vs. SSE**: Determine best approach for live log streaming based on deployment environment
3. **Static Database Source**: Identify best free/open datasets for shelters, food banks, unemployment offices
4. **Video Curation**: Who curates? Manual vs. semi-automated vetting process?
5. **Rate Limiting Implementation**: Use Flask-Limiter vs. Redis-based vs. API Gateway?

---

## Version History
- **v1.0** (2025-10-28): Initial clarifications document based on user Q&A session
