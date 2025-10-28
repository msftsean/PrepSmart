# Implementation Plan Updates - Blackboard Pattern Integration

**Date**: 2025-10-28
**Purpose**: Document all updates to plan.md reflecting blackboard pattern architecture and clarification decisions

---

## Summary of Changes

The original plan.md assumed "Microsoft Agent Framework" or "custom asyncio orchestration". Based on user clarifications and SWOT analyses, we're implementing **blackboard pattern architecture** instead.

---

## Key Architectural Changes

### 1. Agent Orchestration Pattern

**OLD Approach**:
- Microsoft Agent Framework (primary)
- Fallback: Custom asyncio orchestration with message queues

**NEW Approach** ✅:
- **Blackboard Pattern** (primary architecture)
- Central blackboard entity contains all shared state
- Agents read from and write to blackboard atomically
- Coordinator monitors blackboard to determine agent execution order
- Parallel execution when dependencies permit
- Microsoft Agent Framework/AutoGen as optional support layer (not core dependency)

**Rationale**: Cleaner coordination, easier testing, constitutional compliance (Article X)

---

## Time Estimate Adjustments

### Phase 2: Foundation (Reduced from 8h → 6h)

**Changes**:
- Blackboard entity implementation: 2 hours (simpler than asyncio message queue)
- Database schema for blackboard state: 1 hour
- Agent base class with blackboard read/write: 1 hour

**Savings**: 2 hours (no complex message queue or AutoGen integration)

### Phase 3: AI Agents (Adjusted from 24h → 22h)

**Changes**:
- Economic Crisis Runtime Questions: +2 hours (new feature)
  - Question flow UI/API
  - Integration into agent processing
- Static Video Library: -2 hours (vs real-time API search)
  - Curate 10-20 videos per crisis type: 2 hours
  - JSON database + lookup logic: 2 hours
  - **Saved**: Real-time YouTube API integration would take ~8 hours
- PDF Generation: -6 hours (2-page vs 6-page)
  - Simplified 2-page layout: 2 hours
  - **Saved**: Original 6-page design: 8-10 hours
- Hybrid Resource Locator: +2 hours (new complexity)
  - Static database loading: 2 hours
  - Google Places API fallback with rate limiting: 3 hours
  - 7-day caching: 1 hour

**Net Change**: +2 -2 -6 +2 = -4 hours
**New Estimate**: 20 hours

### Phase 4: Economic Crisis Flow (Reduced from 6h → 4h)

**Changes**:
- Simplified to 30-90 day survival focus (not comprehensive financial analysis)
- Runtime questions replace upfront financial data collection form
- Strategic Crisis Planning deferred to v1.1 (out of MVP scope)

**Savings**: 2 hours

### Phase 5: Frontend (Adjusted from 12h → 14h)

**Changes**:
- Live Log Streaming with Emojis: +3 hours (new feature)
  - Server-Sent Events (SSE) endpoint: 2 hours
  - Real-time UI updates with emoji icons: 2 hours
  - Nested sub-task display (└─): 1 hour
- Mobile-First Design: Unchanged (already prioritized)
- Runtime Question Modals: +1 hour (for economic crisis)

**Net Change**: +4 hours (but critical for demo impact)
**New Estimate**: 16 hours

### Phase 6: Testing (Adjusted from 8h → 6h)

**Changes**:
- **Decision**: Minimal smoke tests now, comprehensive tests after hackathon (per clarifications)
- 5 Critical Test Scenarios: 4 hours
  - TS-001, TS-003 automated (P0 blockers): 2 hours
  - TS-002, TS-004, TS-005 manual (P1/P2): 1 hour
  - Test execution and bug fixes: 1 hour
- Comprehensive unit/integration tests: Deferred to post-hackathon

**Savings**: 2 hours

---

## Updated Time Estimates by Phase

| Phase | Original | Updated | Delta | Reason |
|-------|----------|---------|-------|--------|
| Phase 0: Research | 4h | ✅ 0h | -4h | Completed (research.md, SWOT analyses done) |
| Phase 1: Setup | 4h | ✅ 0h | -4h | Completed (backend structure, dependencies) |
| Phase 2: Foundation | 8h | 6h | -2h | Blackboard pattern simpler than message queue |
| Phase 3: AI Agents | 24h | 20h | -4h | 2-page PDF, static video library, savings |
| Phase 4: Economic Crisis | 6h | 4h | -2h | Runtime questions, survival focus only |
| Phase 5: Frontend | 12h | 16h | +4h | Live log streaming, emoji UI (demo critical) |
| Phase 6: Testing | 8h | 6h | -2h | Minimal smoke tests (comprehensive post-hackathon) |
| Phase 7: PDF Generation | (included in Phase 3) | - | - | Already in agents |
| Phase 8: Integration | 4h | 4h | 0h | Unchanged |
| Phase 9: Deployment | 2h | 3h | +1h | Dual deployment (Azure + local backup) |
| **TOTAL** | **72h** | **59h** | **-13h** | More achievable for 4-day hackathon |

---

## New Features Added to Plan

### 1. Blackboard Entity (Phase 2)
- **File**: `backend/src/models/blackboard.py`
- **Purpose**: Central shared state for multi-agent coordination
- **Fields**:
  - Input: crisis_profile
  - Intermediate: risk_assessment, supply_plan, emergency_plan, economic_plan, resource_locations, video_recommendations
  - Final: complete_plan, pdf_path
  - Coordination: status, agents_completed, agents_failed
  - Tracking: execution timing, tokens, cost
- **Database**: SQLite schema with indexes
- **Time**: 2 hours

### 2. Runtime Questions for Economic Crisis (Phase 3 + 5)
- **Backend**: Question definitions, API endpoint to ask/receive answers
- **Frontend**: Modal dialogs with dropdowns/radio buttons
- **Questions**:
  - Risk Assessment: "What worries you most?", "How long can you cover essentials?"
  - Planning: "Top priority?", "Any income sources?"
- **Integration**: Inject responses into agent context via blackboard
- **Time**: 3 hours total (2 backend, 1 frontend)

### 3. Static Video Library (Phase 3)
- **File**: `backend/data/video_library.json`
- **Content**: 10-20 curated videos per crisis type (hurricane, earthquake, unemployment, etc.)
- **Criteria**: Official sources (FEMA, Red Cross) + trusted creators, all under 5 min
- **Agent**: VideoCuratorAgent does static lookup instead of YouTube API search
- **Time**: 4 hours (2 curation, 2 implementation)

### 4. Hybrid Resource Locator (Phase 3)
- **Static Database**: Pre-loaded FEMA shelters, food banks, unemployment offices
- **API Fallback**: Google Places API with rate limiting (max 100 calls/day MVP)
- **Caching**: 7-day result cache to minimize API costs
- **Cost Management**: $20-50/month vs $170-510/month all-API approach
- **Time**: 6 hours

### 5. Live Log Streaming with Emojis (Phase 5)
- **Protocol**: Server-Sent Events (SSE)
- **Endpoint**: `/api/crisis/{task_id}/logs`
- **Format**:
  ```
  event: agent_update
  data: {"agent_name":"Risk Assessment Agent","agent_emoji":"🌪️","status":"active","message":"Analyzing hurricane risk...","progress":50}
  ```
- **UI**: Real-time agent activity cards with emoji icons, progress bars, nested sub-tasks (└─)
- **Time**: 5 hours (3 backend SSE, 2 frontend UI)

### 6. Strategic Crisis Planning Endpoint (Phase 4 - Optional)
- **Endpoint**: `/api/crisis/{task_id}/strategic-plan`
- **Purpose**: Optional expanded guidance for economic crisis
- **Content**: Unemployment filing, job resources, bill strategies, food assistance
- **Scope**: v1.1 feature (out of MVP scope, but endpoint spec ready)
- **Time**: 0 hours MVP (deferred)

### 7. Dual Deployment Strategy (Phase 9)
- **Primary**: Azure Container Apps (public URL for judges/users)
- **Backup**: Local demo on laptop (presentation fallback)
- **Scripts**: Docker compose for local, Azure CLI scripts for cloud
- **Time**: 3 hours (1 local, 2 Azure)

---

## Updated Phase Breakdown

### Phase 2: Foundation (6 hours - revised from 8h)

**Tasks**:
1. Create Blackboard Pydantic model (2h)
   - All fields for shared state
   - Validation rules
   - JSON serialization

2. Database schema for blackboard (1h)
   - Create `blackboards` table
   - Foreign key to `crisis_profiles`
   - Update `init_db()` function

3. Agent base class with blackboard integration (1h)
   - `process(blackboard: Blackboard) -> Blackboard` method signature
   - Atomic read/write helpers
   - Cost and token tracking

4. Coordinator monitoring logic (2h)
   - `get_ready_agents(blackboard)` - check preconditions
   - Parallel agent execution with `asyncio.gather()`
   - Completion detection and status updates

### Phase 3: AI Agents (20 hours - revised from 24h)

**Agent Implementation Order** (with mode-specific behaviors):

1. Risk Assessment Agent (3h)
   - Natural disaster: FEMA data, severity scoring
   - Economic crisis: Financial risk from runtime questions
   - Mode-specific UI labels: "🌪️ Risk Assessment" vs "💰 Financial Risk"
   - Mode-specific Claude prompts

2. Supply Planning Agent (4h)
   - Natural disaster: Emergency supplies (water, food, batteries)
   - Economic crisis: Food stockpiling within budget
   - Runtime question: "What should we prioritize?"
   - Budget tier hard limits enforced
   - Warning UI for EXTREME risk + low budget

3. Resource Locator Agent (6h) - **Most Complex**
   - Load static database (FEMA shelters, food banks, etc.) - 2h
   - Implement Google Places API fallback - 3h
   - Rate limiting (100 calls/day) and 7-day caching - 1h
   - Expand search radius for rural locations (edge case TS-005)

4. Video Curator Agent (2h)
   - Static video library JSON database - 1h
   - Lookup logic by crisis type - 0.5h
   - Filter by duration (<5 min) - 0.5h

5. Financial Advisor Agent (2h)
   - Economic crisis only (30-90 day survival plan)
   - Expense prioritization from runtime questions
   - Strategic Planning stub (deferred to v1.1)

6. Documentation Agent (2h)
   - Generate 2-page PDF (simplified layout)
   - Page 1: Crisis overview + action plan
   - Page 2: Resources + budget with QR codes
   - ReportLab implementation

7. Coordinator Agent (1h)
   - Blackboard monitoring
   - Agent precondition checks
   - Parallel dispatch with `asyncio.gather()`
   - Error handling and graceful degradation

**Runtime Questions Integration** (2h):
- API endpoint to present questions
- Modal UI components
- Inject responses into blackboard

**Static Video Curation** (2h):
- Research and select 60-80 videos (10-20 per crisis type)
- Create JSON database with metadata
- Verification all videos <5 min, authoritative sources

### Phase 5: Frontend (16 hours - revised from 12h)

**Tasks**:
1. Landing page and crisis mode selection (2h)
2. Crisis questionnaire form (3h)
   - Multi-step wizard
   - ZIP code validation
   - Mobile-optimized inputs (44px+ touch targets)
3. **Runtime Question Modals (1h)** - NEW
   - Economic crisis mode only
   - Dropdowns and radio buttons
   - Inject into API request
4. **Live Log Streaming UI (5h)** - NEW ⚠️ DEMO CRITICAL
   - SSE client connection (1h)
   - Agent activity cards with emojis (2h)
   - Progress bars and nested sub-tasks (└─) (1h)
   - Real-time updates without page refresh (1h)
5. Results page (3h)
   - Risk level display
   - Supply checklist
   - Resource map
   - Video embeds/links
6. PDF download button (1h)
7. Mobile responsiveness testing (1h)

### Phase 6: Testing (6 hours - revised from 8h)

**Minimal Smoke Tests** (per clarifications):
1. Implement 5 critical test scenarios (4h)
   - TS-001: Hurricane Miami $50 (P0 - automated)
   - TS-003: Unemployment Austin (P0 - automated)
   - TS-002, TS-004, TS-005: Manual testing

2. Bug fixes from test failures (2h)

**Deferred to Post-Hackathon**:
- Comprehensive unit tests (80%+ coverage)
- Full integration test suite
- Performance testing (load, stress)

---

## Risk Mitigation Updates

### Risk: Blackboard Pattern Implementation Complexity
**Original**: Microsoft Agent Framework might be insufficient
**Updated**: Blackboard pattern is simpler, well-understood architecture
**Mitigation**: Extensive code examples in data-model.md, clear agent interaction pattern

### Risk: Runtime Questions Confuse Users
**Mitigation**:
- Only 2-3 questions total per crisis
- Clear, plain language options (dropdowns, not free text)
- "Why we're asking" explanations
- Progressive disclosure (ask only when needed)

### Risk: Live Log Streaming Performance Issues
**Mitigation**:
- Server-Sent Events (SSE) are lightweight vs WebSockets
- Throttle updates to max 2/second per agent
- Fallback to polling if SSE unavailable
- Test with 10+ concurrent users

### Risk: Static Video Library Becomes Outdated
**Mitigation**:
- Include video publish dates in JSON
- Monthly review process (post-MVP)
- Flag for review if video >2 years old
- v1.1: Add YouTube API search as optional enhancement

---

## Constitutional Gate Updates

All 10 constitutional gates remain passed with blackboard pattern:

- ✅ Article I (Life-Saving Priority): Blackboard enables faster parallel processing → quicker plans
- ✅ Article II (Accessibility): Runtime questions reduce form complexity
- ✅ Article III (Transparency): Live log streaming with emojis exceeds transparency requirements
- ✅ Article IV (Privacy): Runtime questions collect less data than original financial_situation approach
- ✅ Article V (Budget-Consciousness): Hard budget limits enforced in Supply Planning Agent
- ✅ Article VI (Evidence-Based): Static video library ensures all content vetted before inclusion
- ✅ Article VII (Speed & Simplicity): Blackboard parallelization improves speed, runtime questions simplify UX
- ✅ Article VIII (Test-First): 5 critical scenarios defined, automated tests for P0 blockers
- ✅ Article IX (Graceful Degradation): Blackboard tracks agent failures, allows partial plan completion
- ✅ **Article X (Blackboard Shared State)**: Architecture directly implements this principle

---

## Implementation Sequence (Recommended)

### Day 1 (16 hours):
- ✅ Phase 0: Research (COMPLETE)
- ✅ Phase 1: Setup (COMPLETE)
- Phase 2: Foundation (6h)
- Phase 3: Start agents (4h - Risk + Supply)

### Day 2 (16 hours):
- Phase 3: Continue agents (16h - Resource, Video, Financial, Documentation, Coordinator)

### Day 3 (16 hours):
- Phase 4: Economic Crisis (4h)
- Phase 5: Frontend (12h)

### Day 4 (11 hours):
- Phase 5: Frontend completion (4h)
- Phase 6: Testing (6h)
- Phase 8: Integration (1h - already mostly done)

**Final Hours** (4 hours):
- Phase 9: Deployment (3h)
- Buffer for bug fixes (1h)

**TOTAL**: 59 hours across 4 days = ~15 hours/day (achievable for hackathon sprint)

---

## Files Affected by Plan Updates

**Updated**:
- [x] plan.md (summary section, Phase 0, time estimates table)
- [x] PLAN_UPDATES.md (this document - comprehensive change log)

**To Update** (in tasks.md):
- [ ] Add 30+ new tasks for blackboard, runtime questions, static libraries
- [ ] Mark Phase 0 and Phase 1 tasks as complete
- [ ] Update task dependencies to reflect blackboard pattern
- [ ] Add time estimates to each task

---

## Summary

The blackboard pattern architecture, combined with strategic scope decisions (runtime questions, static video library, 2-page PDF, minimal testing MVP), results in:

- ✅ **13 hours saved** (72h → 59h)
- ✅ **More demo impact** (live log streaming with emojis)
- ✅ **Cleaner architecture** (blackboard vs complex message queue)
- ✅ **Better constitutional compliance** (all 10 articles validated)
- ✅ **Realistic 4-day timeline** (15 hrs/day vs original 18 hrs/day)

**Status**: Plan updates complete, ready for tasks.md breakdown

---

**Version**: 1.0 | **Date**: 2025-10-28 | **Impact**: Critical - affects all remaining implementation
