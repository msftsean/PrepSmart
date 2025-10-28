# Task Breakdown Updates - New Tasks for Blackboard Pattern & Clarifications

**Date**: 2025-10-28
**Purpose**: Document all new tasks to be added to tasks.md reflecting blackboard pattern, runtime questions, and clarification decisions

---

## Summary

The original tasks.md had 110 tasks (T001-T110). Based on clarifications and architectural decisions, we need to add **35+ new tasks** and mark **15 tasks as completed**.

---

## Tasks to Mark as COMPLETE (Phase 0 & 1)

**Phase 0: Research & Validation** (Tasks T001-T009) - ✅ ALL COMPLETE
- T001: Research Microsoft Agent Framework ✅
- T002: Test Claude API integration ✅
- T003: Benchmark Claude response times ✅
- T004: Estimate token costs ✅
- T005: Azure Container Apps feasibility ✅
- T006: PDF generation options ✅
- T007: Test ZIP code validation ✅
- T008: Research mobile-first frameworks ✅
- T009: Validate accessibility requirements ✅

**Phase 1: Project Setup** (Tasks T010-T015) - ✅ ALL COMPLETE
- T010: Initialize git repository ✅
- T011: Set up Python virtual environment ✅
- T012: Install Flask and dependencies ✅
- T013: Create backend folder structure ✅
- T014: Create frontend folder structure ✅
- T015: Set up .env file and config ✅

**Status**: 15 tasks marked complete

---

## NEW TASKS - Phase 2: Foundation

### Blackboard Pattern Implementation

**T111: Create Blackboard Pydantic Model** (2 hours)
- **File**: `backend/src/models/blackboard.py`
- **Requirements**:
  - Define all fields (task_id, crisis_profile, intermediate results, final output)
  - Add coordination state (status, agents_completed, agents_failed)
  - Add execution tracking (start, end, duration, tokens, cost)
  - Add JSON serialization/deserialization
  - Add validation rules
- **Test**: Unit test blackboard creation and updates
- **Dependencies**: None (first task)
- **Acceptance**: Blackboard model passes type checking and validation tests

**T112: Create Blackboard Database Schema** (1 hour)
- **File**: `backend/src/api/app.py` (init_db function)
- **Requirements**:
  - CREATE TABLE blackboards with all JSON fields
  - Add foreign key to crisis_profiles(task_id)
  - Add indexes on status and updated_at
  - Update init_db() to create blackboards table
- **Test**: Run init_db(), verify schema with SQLite browser
- **Dependencies**: T111
- **Acceptance**: Database schema created successfully, indexes present

**T113: Implement Blackboard Atomic Read/Write** (1 hour)
- **File**: `backend/src/services/blackboard_service.py`
- **Requirements**:
  - `get_blackboard(task_id)` - fetch from database
  - `update_blackboard(blackboard)` - atomic write to database
  - `create_blackboard(crisis_profile)` - initialize new blackboard
  - Handle concurrent updates with locking or optimistic concurrency
- **Test**: Test concurrent writes don't corrupt data
- **Dependencies**: T112
- **Acceptance**: Blackboard operations are atomic and thread-safe

**T114: Create Agent Base Class with Blackboard Integration** (1 hour)
- **File**: `backend/src/agents/base_agent.py` (UPDATE existing)
- **Requirements**:
  - Change signature: `process(blackboard: Blackboard) -> Blackboard`
  - Add `read_from_blackboard()` helper
  - Add `write_to_blackboard()` helper with automatic timestamp/token tracking
  - Add mode-specific UI label property
  - Add mode-specific prompt template loading
- **Test**: Verify signature changes don't break existing agents
- **Dependencies**: T111, T113
- **Acceptance**: Base agent supports blackboard pattern

**T115: Implement Coordinator Monitoring Logic** (2 hours)
- **File**: `backend/src/agents/coordinator_agent.py`
- **Requirements**:
  - `get_ready_agents(blackboard)` - check which agents can run based on preconditions
  - `dispatch_agents(ready_agents, blackboard)` - parallel execution with asyncio.gather()
  - `check_completion(blackboard)` - detect when all agents done
  - Handle agent failures gracefully (mark failed, continue others)
  - Update blackboard status throughout execution
- **Test**: Integration test with 3 mock agents (1 depends on another)
- **Dependencies**: T113, T114
- **Acceptance**: Coordinator successfully orchestrates parallel agent execution

---

## NEW TASKS - Phase 3: AI Agents

### Runtime Questions for Economic Crisis

**T116: Define Runtime Questions Schema** (30 minutes)
- **File**: `backend/src/models/runtime_questions.py`
- **Requirements**:
  - Define RUNTIME_QUESTIONS dict with all questions per agent
  - primary_concern, runway, top_priority, income_check, income_range, supply_focus
  - Include question text, type (single_choice, conditional), and options
  - Validation schema for user responses
- **Test**: Unit test question validation
- **Dependencies**: None
- **Acceptance**: Runtime questions schema complete and validated

**T117: Create Runtime Questions API Endpoint** (1 hour)
- **File**: `backend/src/api/routes.py`
- **Endpoint**: `POST /api/crisis/{task_id}/questions`
- **Requirements**:
  - Accept agent_name and question_id
  - Return question text and options from schema
  - Accept user response and update blackboard.crisis_profile.runtime_questions
  - Return next question or "complete" signal
- **Test**: API test for question flow
- **Dependencies**: T116
- **Acceptance**: API endpoint returns questions and accepts responses

**T118: Integrate Runtime Questions into Agent Processing** (1 hour)
- **Files**: `backend/src/agents/risk_assessment_agent.py`, `backend/src/agents/supply_planning_agent.py`
- **Requirements**:
  - Check if crisis_mode is "economic_crisis"
  - If runtime_questions not present in blackboard, pause and request questions
  - Inject runtime_question responses into Claude prompt context
  - Resume processing once questions answered
- **Test**: E2E test with economic crisis flow
- **Dependencies**: T117
- **Acceptance**: Agents successfully use runtime question responses

### Static Video Library

**T119: Curate Static Video Library** (2 hours)
- **File**: `backend/data/video_library.json`
- **Requirements**:
  - Research and select 10-20 videos per crisis type (6 natural disasters + 4 economic)
  - Criteria: Official sources (FEMA, Red Cross, NOAA, DOL) + trusted creators
  - All videos under 5 minutes duration
  - Include: title, url, source, duration, description, crisis_types (array)
  - Verify all URLs are active
- **Test**: Manual review of video quality and relevance
- **Dependencies**: None
- **Acceptance**: 60-80 videos curated, JSON file created

**T120: Implement Video Curator Agent with Static Lookup** (1 hour)
- **File**: `backend/src/agents/video_curator_agent.py`
- **Requirements**:
  - Load video_library.json on agent initialization
  - Filter videos by crisis_profile.specific_threat
  - Return 5-7 most relevant videos
  - Sort by: official sources first, then duration (shorter first)
  - Write results to blackboard.video_recommendations
- **Test**: Unit test with mock crisis profiles (hurricane, unemployment)
- **Dependencies**: T119
- **Acceptance**: Agent returns 5-7 relevant videos under 5 min each

### Hybrid Resource Locator

**T121: Load Static Resource Database** (2 hours)
- **File**: `backend/data/resources_static.json`
- **Requirements**:
  - Research and compile static database:
    - FEMA shelter directory (500+ locations)
    - USDA food bank directory (200+ locations per state)
    - State unemployment office listings (all 50 states)
    - Major supply store chains (Walmart, Home Depot, CVS, etc.)
  - Schema: name, address, city, state, zip, lat, lon, resource_type, phone, hours, services
  - Geocode all addresses (lat/lon for distance calculations)
- **Test**: Verify data completeness and accuracy
- **Dependencies**: None
- **Acceptance**: Static database with 1000+ resources created

**T122: Implement Resource Locator with Static Database** (2 hours)
- **File**: `backend/src/agents/resource_locator_agent.py`
- **Requirements**:
  - Load resources_static.json on initialization
  - Filter by resource_type based on crisis_mode:
    - Natural disaster: shelters, hospitals, supply_stores, gas_stations
    - Economic crisis: food_banks, unemployment_offices, job_centers, free_clinics, libraries
  - Calculate distance from user location (haversine formula)
  - Return top 10 resources within 20-mile radius
  - If <5 results, expand radius to 50 miles
  - Write results to blackboard.resource_locations
- **Test**: Unit test with Miami (many resources) and Paradise CA (few resources)
- **Dependencies**: T121
- **Acceptance**: Agent returns 5-10 resources, expands radius if needed

**T123: Add Google Places API Fallback** (3 hours)
- **File**: `backend/src/agents/resource_locator_agent.py` (enhance)
- **Requirements**:
  - If static database returns <3 results, call Google Places API
  - Implement rate limiting: max 100 API calls/day (track in database)
  - API query by resource type and location
  - Parse API response and normalize to resource schema
  - Cache API results in database for 7 days
  - Log API usage and cost
- **Test**: Integration test with API key, verify rate limiting works
- **Dependencies**: T122
- **Acceptance**: API fallback works, rate limiting enforced, results cached

**T124: Implement Resource Caching** (1 hour)
- **File**: `backend/src/services/resource_cache.py`
- **Requirements**:
  - Create resource_cache table in database
  - Schema: location_hash, resource_type, results_json, cached_at, expires_at
  - Check cache before calling API (7-day TTL)
  - Store API results in cache
  - Background job to clean expired cache entries
- **Test**: Verify cache hit/miss logic
- **Dependencies**: T123
- **Acceptance**: Resource caching reduces API calls by 90%+

### Agent Mode-Specific Behaviors

**T125: Refactor Risk Assessment Agent for Dual-Mode** (2 hours)
- **File**: `backend/src/agents/risk_assessment_agent.py` (refactor existing)
- **Requirements**:
  - Detect crisis_mode from blackboard
  - Load mode-specific prompt templates:
    - Natural disaster: FEMA risk assessment prompt
    - Economic crisis: Financial risk assessment prompt
  - Set UI label based on mode:
    - Natural: "🌪️ Risk Assessment Agent"
    - Economic: "💰 Financial Risk Agent"
  - Use runtime_questions in economic mode to assess financial risk
  - Write results to blackboard.risk_assessment
- **Test**: E2E test with both crisis modes
- **Dependencies**: T118 (runtime questions)
- **Acceptance**: Agent works for both natural disaster and economic crisis

**T126: Refactor Supply Planning Agent for Dual-Mode** (2 hours)
- **File**: `backend/src/agents/supply_planning_agent.py` (refactor existing)
- **Requirements**:
  - Detect crisis_mode from blackboard
  - Load mode-specific prompt templates:
    - Natural disaster: Emergency supplies (water, food, batteries)
    - Economic crisis: Food stockpiling within budget
  - Set UI label based on mode:
    - Natural: "📦 Supply Planning Agent"
    - Economic: "📊 Budget Planning Agent"
  - Enforce hard budget limits (never exceed budget_tier)
  - If risk_level is EXTREME and budget_tier is $50, add warning to results
  - Use runtime_questions.supply_focus in economic mode
  - Write results to blackboard.supply_plan
- **Test**: E2E test with $50 budget + EXTREME risk (warning shown), $200 budget (no warning)
- **Dependencies**: T118, T125
- **Acceptance**: Agent respects budget limits, shows warnings appropriately

**T127: Implement Financial Advisor Agent for Economic Crisis** (2 hours)
- **File**: `backend/src/agents/financial_advisor_agent.py` (NEW)
- **Requirements**:
  - Only runs for crisis_mode = "economic_crisis"
  - Generate 30-90 day survival plan focused on:
    - Expense prioritization (Must-Pay, Defer, Eliminate)
    - Food/essentials stockpiling strategy
    - Immediate cost reduction tactics
  - Use runtime_questions (runway, top_priority, income_range)
  - Write results to blackboard.economic_plan
  - Stub for Strategic Planning feature (deferred to v1.1)
- **Test**: Unit test with TS-003 scenario (Austin unemployment)
- **Dependencies**: T118
- **Acceptance**: Agent generates actionable 30-90 day plan

**T128: Implement Documentation Agent with 2-Page PDF** (2 hours)
- **File**: `backend/src/agents/documentation_agent.py` (NEW)
- **Requirements**:
  - Read all results from blackboard (risk, supply, resources, videos)
  - Generate simplified 2-page PDF using ReportLab:
    - Page 1: Crisis overview, risk level, top 5 actions, supply checklist
    - Page 2: Resource map (top 10 locations), budget breakdown, QR codes
  - Ensure black & white print-friendly layout
  - QR codes link to: video playlist, resource map, PrepSmart website
  - Save PDF to filesystem, write path to blackboard.pdf_path
  - PDF must work offline after generation
- **Test**: Generate PDF for TS-001 (hurricane), verify 2 pages, QR codes work
- **Dependencies**: T125, T126, T120, T122
- **Acceptance**: 2-page PDF generated, QR codes functional, print-optimized

**T129: Implement Coordinator Agent** (1 hour)
- **File**: `backend/src/agents/coordinator_agent.py` (NEW)
- **Requirements**:
  - Initialize blackboard from crisis_profile
  - Main orchestration loop:
    1. Call get_ready_agents(blackboard)
    2. Dispatch ready agents in parallel with asyncio.gather()
    3. Wait for agents to complete
    4. Update blackboard with results
    5. Check if all agents done or max retries exceeded
  - Handle agent failures: log error, mark agent as failed, continue with others
  - Calculate total execution time and cost
  - Update blackboard status: initialized → processing → completed/failed
- **Test**: Integration test with all 7 agents, verify parallel execution
- **Dependencies**: T115, T125-T128
- **Acceptance**: Coordinator orchestrates complete plan generation in <180 seconds

---

## NEW TASKS - Phase 5: Frontend

### Live Log Streaming with Emojis

**T130: Implement Server-Sent Events (SSE) Endpoint** (2 hours)
- **File**: `backend/src/api/routes.py`
- **Endpoint**: `GET /api/crisis/{task_id}/logs` (SSE stream)
- **Requirements**:
  - Stream agent activity logs in real-time using SSE protocol
  - Events: `agent_update`, `agent_complete`, `agent_error`, `plan_complete`
  - Data format: agent_name, agent_emoji, status, message, progress, sub_tasks, timestamp
  - Poll blackboard and agent_logs table every 500ms for updates
  - Send only new updates since last poll (track last_log_id per client)
  - Close stream when plan complete or client disconnects
- **Test**: Manual test with curl or Postman SSE client
- **Dependencies**: T129 (coordinator generates logs)
- **Acceptance**: SSE endpoint streams agent updates in real-time

**T131: Create Agent Activity UI with Emoji Icons** (3 hours)
- **File**: `frontend/js/agent-activity.js`
- **Requirements**:
  - Connect to SSE endpoint `/api/crisis/{task_id}/logs`
  - Display agent activity cards for each agent:
    - Agent emoji icon (🌪️, 📦, 💰, 🗺️, 🎥, 📄, 🎯)
    - Agent name (mode-specific label)
    - Status badge (Waiting/Active/Complete/Error)
    - Current task message
    - Progress bar (0-100%)
    - Nested sub-tasks with └─ prefix
  - Update cards in real-time as events arrive
  - Animate progress bars smoothly
  - Show confetti or success animation on plan_complete event
- **Test**: Manual test with live plan generation
- **Dependencies**: T130
- **Acceptance**: UI displays live agent activity with emojis, updates in real-time

### Runtime Question Modals

**T132: Create Runtime Question Modal UI** (1 hour)
- **File**: `frontend/js/runtime-questions.js`
- **Requirements**:
  - Detect when agent needs runtime questions (SSE event: `question_required`)
  - Display modal dialog with:
    - Question text ("What worries you most right now?")
    - Dropdown or radio buttons with options
    - "Why we're asking" explanation text
    - Submit button
  - POST response to `/api/crisis/{task_id}/questions`
  - Close modal and resume agent activity display
- **Test**: Manual test with economic crisis flow
- **Dependencies**: T117, T131
- **Acceptance**: Modal displays questions, submits responses, closes automatically

---

## NEW TASKS - Phase 6: Testing

### Critical Test Scenarios

**T133: Implement TS-001 Automated Test (Hurricane, Miami, $50)** (1 hour)
- **File**: `tests/e2e/test_scenario_001.py`
- **Requirements**:
  - Test inputs: Miami FL 33101, hurricane, 1 adult + 2 children, $50 budget
  - Expected outputs:
    - Risk level: EXTREME (90-100 severity)
    - Supply list total: $48-50
    - Budget warning shown: "⚠️ EXTREME risk detected. $50 tier may not provide adequate protection."
    - 8+ resources found in Miami area
    - 5 videos curated (all <5 min)
    - PDF downloads successfully (2 pages)
    - Total time: <180 seconds
  - Assert all expectations
- **Test**: Run with pytest
- **Dependencies**: T129 (full orchestration working)
- **Acceptance**: TS-001 test passes 100%

**T134: Implement TS-003 Automated Test (Unemployment, Austin)** (1 hour)
- **File**: `tests/e2e/test_scenario_003.py`
- **Requirements**:
  - Test inputs: Austin TX, unemployment, 1 adult, $50 budget
  - Runtime questions: "Eviction/foreclosure", "<2 weeks", "Keep housing", "No income"
  - Expected outputs:
    - Risk level: EXTREME (95-100 severity)
    - Top priority: Housing preservation
    - 5+ food banks found in Austin
    - Hardship letter template included
    - Texas-specific unemployment guidance
    - 10+ action items with deadlines
    - PDF downloads successfully
    - Total time: <180 seconds
  - Assert all expectations
- **Test**: Run with pytest
- **Dependencies**: T127, T129 (economic crisis agents working)
- **Acceptance**: TS-003 test passes 100%

**T135: Manual Test TS-002 (Earthquake, SF, $200+, Pet)** (30 minutes)
- **Requirements**:
  - Manually test: San Francisco CA, earthquake, 2 adults + 1 child + 1 dog, $200+ budget
  - Verify:
    - Risk level: HIGH (75-85 severity)
    - Pet supplies included in supply list
    - 2+ pet-friendly shelters found
    - 1+ pet safety video included
    - Total cost $195-210 acceptable
    - Earthquake-specific guidance present
  - Document results in test_results.md
- **Dependencies**: T129
- **Acceptance**: TS-002 verified manually, results documented

**T136: Manual Test TS-004 (Gov Shutdown, DC, Family, Strategic Planning)** (30 minutes)
- **Requirements**:
  - Manually test: Washington DC, government shutdown, 2 adults + 2 children, $100 budget
  - Runtime questions: "Can't afford food", "1-3 months", "Feed family", "Yes $500-1500"
  - Enable Strategic Planning toggle
  - Verify:
    - Risk level: MEDIUM-HIGH (60-70 severity)
    - Food security prioritized
    - SNAP and school meal programs featured
    - Strategic Planning generates 4-page PDF (2 core + 2 appendix)
    - 3+ food banks in DC area
    - Family-specific guidance (4-person quantities)
  - Document results
- **Dependencies**: T127, T129
- **Acceptance**: TS-004 verified, Strategic Planning works

**T137: Manual Test TS-005 (Wildfire, Paradise CA, Rural, Elderly)** (30 minutes)
- **Requirements**:
  - Manually test: Paradise CA 95969, wildfire, 1 adult + 1 elderly parent + 1 cat, $100 budget
  - Verify:
    - Risk level: EXTREME (95-100 severity)
    - Evacuation-focused plan (not shelter-in-place)
    - Resource search expands to Chico CA (20-50 miles)
    - Note displayed: "Limited local resources, nearest help in Chico"
    - Elderly mobility considerations mentioned
    - Pet supplies and pet-friendly shelters included
    - Evacuation routes clearly mapped
  - Document results
- **Dependencies**: T123 (resource radius expansion)
- **Acceptance**: TS-005 verified, edge case handled correctly

---

## NEW TASKS - Phase 9: Deployment

**T138: Create Docker Compose for Local Demo** (1 hour)
- **File**: `docker-compose.yml`
- **Requirements**:
  - Multi-container setup: backend (Flask), frontend (nginx)
  - Volume mounts for development
  - Environment variable configuration
  - Startup scripts
  - Health checks
- **Test**: `docker-compose up` starts full app
- **Dependencies**: None
- **Acceptance**: Local demo runs via Docker

**T139: Create Azure Deployment Scripts** (2 hours)
- **File**: `deploy/azure-deploy.sh`
- **Requirements**:
  - Azure Container Apps deployment using Azure CLI
  - Resource group creation
  - Container registry push
  - Environment variable configuration
  - Custom domain setup (if needed)
  - HTTPS certificate
- **Test**: Deploy to Azure test environment
- **Dependencies**: T138
- **Acceptance**: App deploys to Azure successfully

---

## Task Summary

### New Tasks Added:
- **Phase 2 (Blackboard)**: T111-T115 (5 tasks, 7 hours)
- **Phase 3 (Agents)**: T116-T129 (14 tasks, 22 hours)
- **Phase 5 (Frontend)**: T130-T132 (3 tasks, 6 hours)
- **Phase 6 (Testing)**: T133-T137 (5 tasks, 3.5 hours)
- **Phase 9 (Deployment)**: T138-T139 (2 tasks, 3 hours)

**Total New Tasks**: 29 tasks, 41.5 hours

### Tasks to Update:
- T016-T110: Mark dependencies on new blackboard tasks where applicable
- Update time estimates based on PLAN_UPDATES.md

### Tasks Completed:
- T001-T015: Mark as ✅ COMPLETE (Phase 0 & 1)

---

## Updated Task Count

- **Original**: T001-T110 (110 tasks)
- **New**: T111-T139 (29 tasks)
- **Total**: 139 tasks
- **Completed**: 15 tasks (T001-T015)
- **Remaining**: 124 tasks

---

## Integration into tasks.md

Recommend adding these tasks to tasks.md in the following structure:

```markdown
## Phase 2: Foundation

### Blackboard Pattern Implementation
- [ ] T111: Create Blackboard Pydantic Model (2h)
- [ ] T112: Create Blackboard Database Schema (1h)
- [ ] T113: Implement Blackboard Atomic Read/Write (1h)
- [ ] T114: Create Agent Base Class with Blackboard Integration (1h)
- [ ] T115: Implement Coordinator Monitoring Logic (2h)

... (continue for all phases)
```

---

**Version**: 1.0 | **Date**: 2025-10-28 | **Impact**: Adds 29 tasks, 41.5 hours of work
