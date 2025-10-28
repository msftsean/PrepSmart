# Tasks: PrepSmart Multi-Agent Crisis Preparedness Assistant

**Input**: Design documents from `/specs/001-prepsmart-mvp/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Timeline**: 4 days (64 hours) - Oct 27-31, 2025
**Test Approach**: Test-first for all agents (per Constitution Article VIII)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story this task belongs to (US1, US2, US3, US4, US5)
- Exact file paths included in descriptions

---

## Phase 1: Setup (Day 1 Morning - 2 hours)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend directory structure: `backend/src/{agents,models,services,api,data,utils}` and `backend/tests/{contract,integration,unit}`
- [ ] T002 Create frontend directory structure: `frontend/{pages,assets/{css,js,images}}`
- [ ] T003 [P] Initialize Python project with requirements.txt: flask, anthropic, pyautogen, reportlab, uszipcode, pydantic, sqlalchemy
- [ ] T004 [P] Initialize requirements-dev.txt: pytest, pytest-cov, pytest-asyncio, playwright, ruff, mypy
- [ ] T005 [P] Create .env.example with CLAUDE_API_KEY, FLASK_SECRET_KEY, DATABASE_URL, LOG_LEVEL
- [ ] T006 [P] Create .gitignore for Python, Flask, SQLite, .env files
- [ ] T007 [P] Configure ruff.toml and pyproject.toml for linting/type checking
- [ ] T008 Create README.md with project overview and setup instructions

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Day 1 Afternoon - 4 hours)

**Purpose**: Core infrastructure that BLOCKS all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Setup SQLite database schema in `backend/src/models/__init__.py` with crisis_profiles and agent_logs tables
- [ ] T010 [P] Create CrisisProfile Pydantic model in `backend/src/models/crisis_profile.py` with validation
- [ ] T011 [P] Create AgentActivityLog Pydantic model in `backend/src/models/agent_log.py`
- [ ] T012 [P] Implement ClaudeClient service in `backend/src/services/claude_client.py` with async generate() method
- [ ] T013 [P] Implement CacheService in `backend/src/services/cache_service.py` with in-memory dict (MVP)
- [ ] T014 [P] Implement LocationService in `backend/src/services/location_service.py` using uszipcode for ZIP validation
- [ ] T015 Implement Flask app initialization in `backend/src/api/app.py` with CORS, error handlers, init_db()
- [ ] T016 Implement API routes skeleton in `backend/src/api/routes.py` for /health, /crisis/start, /crisis/{id}/status, /crisis/{id}/result, /crisis/{id}/pdf
- [ ] T017 [P] Create BaseAgent abstract class in `backend/src/agents/base_agent.py` with process() method signature
- [ ] T018 [P] Create static data files: `backend/src/data/{disaster_types.json, supply_templates.json, video_library.json, resources.json, offline_checklists.json}`
- [ ] T019 [P] Setup logging configuration in `backend/src/utils/logger.py`
- [ ] T020 [P] Create config.py in `backend/src/utils/config.py` for environment variables

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Disaster Preparedness Plan (Priority: P1) 🎯 MVP

**Goal**: User enters location/household info, receives complete personalized disaster plan in under 5 minutes with visible multi-agent processing

**Independent Test**: Enter Miami Beach ZIP 33139, select Hurricane, 2 adults + 1 child + 1 pet, $100 budget → Receive EXTREME risk assessment + supply list + emergency plan + resources + PDF download

### Tests for User Story 1 (Test-First per Constitution)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T021 [P] [US1] Contract test for POST /api/crisis/start in `backend/tests/contract/test_crisis_api.py` - verify 202 response with task_id
- [ ] T022 [P] [US1] Contract test for GET /api/crisis/{id}/status in `backend/tests/contract/test_crisis_api.py` - verify agent status structure
- [ ] T023 [P] [US1] Contract test for GET /api/crisis/{id}/result in `backend/tests/contract/test_crisis_api.py` - verify CompletePlan schema
- [ ] T024 [P] [US1] Integration test for natural disaster flow in `backend/tests/integration/test_natural_disaster_e2e.py` - Miami hurricane scenario
- [ ] T025 [P] [US1] Unit test for RiskAssessmentAgent in `backend/tests/unit/agents/test_risk_assessment.py` - test severity scoring
- [ ] T026 [P] [US1] Unit test for SupplyPlanningAgent in `backend/tests/unit/agents/test_supply_planning.py` - test budget tiers

### Implementation for User Story 1

#### Data Models (Parallel)

- [ ] T027 [P] [US1] Create RiskAssessment model in `backend/src/models/risk_assessment.py` with ThreatDetail nested model
- [ ] T028 [P] [US1] Create SupplyPlan model in `backend/src/models/supply_plan.py` with SupplyItem, SupplyTier nested models
- [ ] T029 [P] [US1] Create EmergencyPlan model in `backend/src/models/emergency_plan.py` with EvacuationRoute, MeetingPoint nested models
- [ ] T030 [P] [US1] Create ResourceLocation model in `backend/src/models/resource_location.py`
- [ ] T031 [P] [US1] Create VideoRecommendation model in `backend/src/models/video_recommendation.py`
- [ ] T032 [P] [US1] Create CompletePlan model in `backend/src/models/complete_plan.py` aggregating all outputs

#### Agents (Sequential by dependency)

- [ ] T033 [US1] Implement CoordinatorAgent in `backend/src/agents/coordinator_agent.py` - triages natural disaster requests, dispatches 6 agents (Risk, Supply, Emergency, Resource, Video, Documentation)
- [ ] T034 [US1] Implement RiskAssessmentAgent in `backend/src/agents/risk_assessment_agent.py` - uses Claude API to assess location threat, returns RiskAssessment with EXTREME/HIGH/MEDIUM/LOW
- [ ] T035 [US1] Implement SupplyPlanningAgent in `backend/src/agents/supply_planning_agent.py` - loads supply_templates.json, uses Claude API to personalize for household/budget, returns 3-tier SupplyPlan
- [ ] T036 [US1] Implement EmergencyPlanAgent (not in original spec but implied) OR extend SupplyPlanningAgent to include emergency plan generation in `backend/src/agents/supply_planning_agent.py` - generates evacuation routes, meeting points, communication plan
- [ ] T037 [US1] Implement ResourceLocatorAgent in `backend/src/agents/resource_locator_agent.py` - loads resources.json, filters by location/type, uses OpenStreetMap Nominatim as fallback
- [ ] T038 [US1] Implement VideoCuratorAgent in `backend/src/agents/video_curator_agent.py` - loads video_library.json, filters by crisis type, ranks top 5-7 with Claude API
- [ ] T039 [US1] Implement DocumentationAgent in `backend/src/agents/documentation_agent.py` - uses ReportLab to generate PDF per pdf-spec.md layout

#### Services & Orchestration

- [ ] T040 [US1] Implement AgentOrchestrator service in `backend/src/services/orchestrator.py` - async orchestration using AutoGen or custom asyncio, handles parallel agent execution, timeout management, caching
- [ ] T041 [US1] Implement PDFGenerator service in `backend/src/services/pdf_generator.py` - ReportLab implementation of pdf-spec.md (cover, risk, supply, emergency, resources, videos)
- [ ] T042 [US1] Update API routes in `backend/src/api/routes.py` to use AgentOrchestrator for /crisis/start, poll agent logs for /status, return CompletePlan for /result

#### Frontend (Natural Disaster Flow)

- [ ] T043 [P] [US1] Create landing page HTML in `frontend/index.html` - PrepSmart hero, two buttons: Natural Disaster / Economic Crisis
- [ ] T044 [P] [US1] Create crisis selection page in `frontend/pages/crisis-select.html` - select specific disaster type (hurricane, earthquake, wildfire, flood, tornado, blizzard)
- [ ] T045 [P] [US1] Create questionnaire form in `frontend/pages/questionnaire.html` - ZIP/city/state, household (adults/children/pets), housing type, budget tier
- [ ] T046 [US1] Implement form handler JS in `frontend/assets/js/form-handler.js` - validate inputs, call /api/crisis/validate-location, save to localStorage, POST to /api/crisis/start
- [ ] T047 [US1] Create agent progress dashboard in `frontend/pages/agent-progress.html` - 6 agent cards with icons, real-time status updates
- [ ] T048 [US1] Implement agent dashboard JS in `frontend/assets/js/agent-dashboard.js` - poll /api/crisis/{id}/status every 2 seconds, update UI with agent status, progress bars, task descriptions
- [ ] T049 [US1] Create plan results page in `frontend/pages/plan-results.html` - collapsible sections for risk, supply, emergency plan, resources, videos, download PDF button
- [ ] T050 [P] [US1] Implement API client in `frontend/assets/js/api-client.js` - wrapper for fetch() to backend API endpoints
- [ ] T051 [P] [US1] Create main CSS in `frontend/assets/css/main.css` - global styles, color scheme (#1E40AF blue, #DC2626 red, #16A34A green)
- [ ] T052 [P] [US1] Create mobile responsive CSS in `frontend/assets/css/mobile.css` - media queries for 320px-428px, 44px touch targets, 16px+ fonts

#### Static Data

- [ ] T053 [P] [US1] Populate disaster_types.json in `backend/src/data/` with 6 disaster definitions (hurricane, earthquake, wildfire, flood, tornado, blizzard)
- [ ] T054 [P] [US1] Populate supply_templates.json with base supply lists per disaster type and budget tier
- [ ] T055 [P] [US1] Curate video_library.json with 50 disaster prep videos from FEMA, Red Cross, YouTube (10-15 hours manual curation - can be done in parallel with dev)
- [ ] T056 [P] [US1] Populate resources.json with 100-200 US shelters, food banks, hospitals (top 50 cities)

**Checkpoint**: User Story 1 fully functional - can generate natural disaster plan end-to-end

---

## Phase 4: User Story 2 - Economic Crisis Survival Plan (Priority: P2)

**Goal**: User facing unemployment/shutdown enters financial details, receives 30-day survival budget, benefits assessment, hardship letters, action plan

**Independent Test**: Washington DC user, government shutdown, $0 income, $3200 expenses, $2000 savings → Receive must-pay/defer/eliminate breakdown + 30-day actions + benefits ($2480/mo) + hardship letters + PDF

### Tests for User Story 2

- [ ] T057 [P] [US2] Integration test for economic crisis flow in `backend/tests/integration/test_economic_crisis_e2e.py` - government shutdown scenario
- [ ] T058 [P] [US2] Unit test for FinancialAdvisorAgent in `backend/tests/unit/agents/test_financial_advisor.py` - test expense categorization, runway calculation

### Implementation for User Story 2

#### Data Models

- [ ] T059 [P] [US2] Create EconomicPlan model in `backend/src/models/economic_plan.py` with ExpenseCategory, DailyAction, BenefitProgram, HardshipLetterTemplate nested models

#### Agents

- [ ] T060 [US2] Implement FinancialAdvisorAgent in `backend/src/agents/financial_advisor_agent.py` - categorizes expenses (must-pay/defer/eliminate), generates 30-day action plan, estimates benefits (unemployment, SNAP, Medicaid), creates hardship letter templates
- [ ] T061 [US2] Update CoordinatorAgent in `backend/src/agents/coordinator_agent.py` to handle economic_crisis mode - dispatch FinancialAdvisor, Resource, Video, Documentation agents (4 agents vs 6 for natural disaster)

#### Frontend (Economic Crisis Flow)

- [ ] T062 [US2] Update questionnaire form in `frontend/pages/questionnaire.html` to conditionally show financial_situation fields (current_income, monthly_expenses, available_savings, debt_obligations, employment_status)
- [ ] T063 [US2] Update plan results page in `frontend/pages/plan-results.html` to display economic plan structure (financial summary, expense categories, 30-day timeline, benefits, hardship letters)
- [ ] T064 [US2] Update PDFGenerator service in `backend/src/services/pdf_generator.py` to render economic plan layout per pdf-spec.md (financial overview, action plan, hardship letters)

#### Static Data

- [ ] T065 [P] [US2] Populate video_library.json with 20-30 economic crisis videos (unemployment filing, SNAP application, budgeting tips)
- [ ] T066 [P] [US2] Update resources.json with unemployment offices, legal aid, financial counseling services

**Checkpoint**: User Story 2 fully functional - economic crisis plans work independently of natural disaster

---

## Phase 5: User Story 3 - Multi-Agent System Demonstration (Priority: P1) 🎯 HACKATHON

**Goal**: Hackathon judges/demo viewers clearly see 7 agents working together with visible orchestration, inter-agent communication, progress tracking

**Independent Test**: Watch any plan generation, verify agent dashboard shows each agent activating → processing → completing with real-time updates, inter-agent messages visible

### Implementation for User Story 3

- [ ] T067 [US3] Enhance AgentActivityLog model in `backend/src/models/agent_log.py` to capture inter-agent messages (from/to/content/timestamp)
- [ ] T068 [US3] Update BaseAgent in `backend/src/agents/base_agent.py` to log inter-agent communication when requesting dependencies (e.g., Supply Planning requests risk_level from Risk Assessment)
- [ ] T069 [US3] Update agent dashboard JS in `frontend/assets/js/agent-dashboard.js` to display inter-agent messages: "Supply Planning Agent requesting risk level from Risk Assessment Agent"
- [ ] T070 [P] [US3] Add agent icon assets in `frontend/assets/images/agent-icons/` - 7 SVG icons (coordinator, risk, supply, financial, resource, video, documentation)
- [ ] T071 [P] [US3] Create demo script in `docs/DEMO_SCRIPT.md` - 6-minute hackathon presentation walkthrough
- [ ] T072 [P] [US3] Create agent architecture diagram in `docs/AGENT_ARCHITECTURE.md` - visual flowchart of agent orchestration

**Checkpoint**: Multi-agent orchestration is impressive and clearly visible to judges

---

## Phase 6: User Story 4 - Mobile-Responsive Emergency Access (Priority: P2)

**Goal**: Users on mobile phones (320px-428px) can complete full questionnaire and view plan with readable text, tappable buttons

**Independent Test**: Test on iPhone SE (320px) and Galaxy S20 (428px) - complete hurricane flow, verify no horizontal scrolling, all buttons tappable, text readable without zooming

### Implementation for User Story 4

- [ ] T073 [US4] Enhance mobile.css in `frontend/assets/css/mobile.css` with breakpoints for 320px, 375px, 428px viewports
- [ ] T074 [US4] Update questionnaire form in `frontend/pages/questionnaire.html` to use appropriate mobile keyboards (numeric, email)
- [ ] T075 [US4] Update agent dashboard in `frontend/pages/agent-progress.html` to stack agent cards vertically on mobile
- [ ] T076 [US4] Update plan results in `frontend/pages/plan-results.html` to use collapsible/expandable sections for mobile
- [ ] T077 [US4] Implement service worker in `frontend/service-worker.js` to cache critical HTML, CSS, JS, offline_checklists.json
- [ ] T078 [US4] Implement offline support in `frontend/assets/js/offline.js` - detect offline mode, show cached checklists, display warning banner

### Testing for User Story 4

- [ ] T079 [US4] Manual mobile testing on real devices (iPhone, Android) or Chrome DevTools device emulation
- [ ] T080 [US4] Test 3G throttling in Chrome DevTools - verify page load <3s
- [ ] T081 [US4] Run Lighthouse accessibility audit - target 90+ score

**Checkpoint**: Mobile experience fully functional and accessible

---

## Phase 7: User Story 5 - Personalized Supply Planning with Budget Tiers (Priority: P3)

**Goal**: User with $50 budget receives realistic Critical-tier supply list under $50 with free alternatives highlighted

**Independent Test**: Complete hurricane flow with $50 budget → Supply plan shows ONLY Critical tier (5-7 items), total cost ≤$55, free alternatives listed for each item

### Implementation for User Story 5

- [ ] T082 [US5] Enhance SupplyPlanningAgent in `backend/src/agents/supply_planning_agent.py` to strictly filter by budget tier, highlight free alternatives, warn if over budget
- [ ] T083 [US5] Update supply_templates.json in `backend/src/data/` to include free alternative suggestions for each item ("Fill bathtub at home (FREE)" for water)
- [ ] T084 [US5] Update plan results in `frontend/pages/plan-results.html` to visually distinguish Critical/Prepared/Comprehensive tiers with color coding, show "Over Budget" warning if applicable

**Checkpoint**: Budget-conscious supply planning works for all tiers ($50/$100/$200+)

---

## Phase 8: Testing & Validation (Day 4 Morning - 4 hours)

**Purpose**: Run all tests, validate against spec.md acceptance criteria

- [ ] T085 [P] Run all unit tests: `pytest backend/tests/unit/ -v`
- [ ] T086 [P] Run all integration tests: `pytest backend/tests/integration/ -v`
- [ ] T087 [P] Run contract tests: `pytest backend/tests/contract/ -v`
- [ ] T088 Run E2E tests with Playwright: `pytest backend/tests/e2e/ -v`
- [ ] T089 Validate Scenario 1: Hurricane in Miami (33139) - verify EXTREME risk, $90-100 supply list, evacuation routes
- [ ] T090 Validate Scenario 2: Government Shutdown in DC - verify 18-day runway, $1950 revised expenses, $2480 benefits
- [ ] T091 Validate Scenario 3: Earthquake in San Francisco (94102) - verify HIGH risk, $45-50 supply list, shelter-in-place
- [ ] T092 Run quickstart.md validation end-to-end
- [ ] T093 [P] Check all Constitutional gates passed (Life-Saving Priority, Accessibility, Multi-Agent Transparency, etc.)
- [ ] T094 Verify all 15 Success Criteria from spec.md (plan in <5min, mobile works, PDF generates, etc.)

**Checkpoint**: All tests passing, MVP ready for demo

---

## Phase 9: Deployment & Polish (Day 4 Afternoon - 6 hours)

**Purpose**: Deploy to Azure, final polish for hackathon demo

### Deployment

- [ ] T095 Create Dockerfile for Flask backend in `backend/Dockerfile`
- [ ] T096 Create docker-compose.yml for local testing in `deployment/docker-compose.yml`
- [ ] T097 Create Azure Container Apps deployment config in `deployment/azure-deploy.yaml`
- [ ] T098 Deploy backend to Azure Container Apps - verify health check returns 200
- [ ] T099 Deploy frontend to Azure Blob Storage (static hosting) or bundle with backend
- [ ] T100 Configure CORS in `backend/src/api/app.py` for frontend → backend communication
- [ ] T101 Set environment variables in Azure: CLAUDE_API_KEY, FLASK_SECRET_KEY
- [ ] T102 Test deployed app end-to-end with public URL

### Polish

- [ ] T103 [P] Create API documentation in `docs/API_REFERENCE.md` - detailed endpoint examples
- [ ] T104 [P] Finalize demo script in `docs/DEMO_SCRIPT.md` - 2-min pitch + 3-min live demo
- [ ] T105 [P] Add loading spinners to agent dashboard for better UX
- [ ] T106 [P] Add error messages with retry logic for API failures
- [ ] T107 Add "Contact Support" message for unrecoverable errors
- [ ] T108 [P] Code cleanup: remove console.logs, unused imports, commented code
- [ ] T109 [P] Update README.md with deployment URLs, demo instructions, hackathon submission details
- [ ] T110 Practice demo presentation with team - aim for under 6 minutes

**Checkpoint**: Production deployment ready, hackathon demo rehearsed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately ✅
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories ⚠️
- **User Stories (Phase 3-7)**: All depend on Foundational completion
  - US1 (Natural Disaster) can start first - no dependencies
  - US2 (Economic Crisis) can run parallel to US1 - minimal shared code
  - US3 (Multi-Agent Demo) depends on US1 completion - enhances visibility
  - US4 (Mobile) can run parallel - CSS/UI only
  - US5 (Budget Tiers) depends on US1 SupplyPlanningAgent - enhancement
- **Testing (Phase 8)**: Depends on US1, US2 completion (US3-5 optional)
- **Deployment (Phase 9)**: Depends on Testing passing

### Critical Path (for 4-day timeline)

**Day 1**: Setup → Foundational → Start US1 agents
**Day 2**: Finish US1 agents → US1 frontend → Start US2
**Day 3**: Finish US2 → US3 agent visibility → US4 mobile CSS
**Day 4**: Testing → Deployment → Demo prep

### Parallel Opportunities

- **Phase 1**: T003-T008 can all run in parallel (different files)
- **Phase 2**: T010-T020 can run in parallel (different services/models)
- **US1 Models**: T027-T032 can run in parallel (6 models, different files)
- **US1 Frontend**: T043-T052 can partially overlap with backend agent work
- **Static Data**: T053-T056, T065-T066 can be done in parallel with development (manual curation)
- **Phase 8**: T085-T087 can run in parallel (different test suites)
- **Phase 9 Polish**: T103-T107 can run in parallel (documentation vs UI polish)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (T021-T026 before T027-T056)
- Models before agents (T027-T032 before T033-T039)
- Agents before orchestration (T033-T039 before T040)
- Backend API before frontend (T042 before T046-T049)

---

## Implementation Strategy

### MVP First (P1 User Stories Only)

1. Day 1: Complete Setup + Foundational
2. Day 2: Complete US1 (Natural Disaster) + US3 (Multi-Agent Demo)
3. Day 3: Test US1 end-to-end, polish agent visibility
4. Day 4: Deploy + Demo

**Result**: Working natural disaster plan generator with impressive multi-agent demo for hackathon

### Full MVP (All User Stories)

1. Day 1: Setup + Foundational + Start US1
2. Day 2: Finish US1 + US2 (Economic Crisis)
3. Day 3: US3 (Multi-Agent Demo) + US4 (Mobile) + US5 (Budget Tiers)
4. Day 4: Testing + Deployment + Demo

**Result**: Complete PrepSmart with both crisis modes, mobile support, budget tiers

---

## Risk Mitigation

**If behind schedule after Day 2**:
- Cut US2 (Economic Crisis) - focus on natural disaster only
- Cut US5 (Budget Tiers) - use single budget approach
- Simplify US3 - basic agent status without inter-agent messages

**If AutoGen causes issues**:
- Fallback to custom asyncio orchestration (T040)
- Use simple parallel execution with asyncio.gather()

**If Claude API slow during demo**:
- Pre-cache 3 common scenarios (Miami hurricane, DC shutdown, SF earthquake)
- Use cached responses for demo reliability

**If Azure deployment fails**:
- Deploy to Railway or Render.com instead
- Use local demo with ngrok for public URL

---

## Notes

- [P] = Parallel execution possible (different files, no dependencies)
- [Story] = User story label for traceability (US1-US5)
- Each user story independently completable and testable ✅
- Constitution Article VIII compliance: Tests written FIRST for all agents ✅
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- Prioritize P1 stories (US1, US3) for hackathon if time constrained

---

**Total Tasks**: 110
**Estimated Hours**: 64 hours (4 days × 16 hours/day)
**MVP Subset**: T001-T072 (72 tasks, ~48 hours, 3 days) - covers US1, US3 (natural disaster + demo)
**Ready for Implementation**: ✅ All planning documents complete, proceed to Phase 1
