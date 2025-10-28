# Implementation Plan: PrepSmart Multi-Agent Crisis Preparedness Assistant

**Branch**: `001-prepsmart-mvp` | **Date**: 2025-10-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-prepsmart-mvp/spec.md`

## Summary

PrepSmart is a web application that uses 7 specialized AI agents orchestrated via blackboard pattern architecture to generate personalized crisis preparedness plans within 5 minutes. The system supports both natural disaster preparedness (hurricanes, earthquakes, etc.) and economic crisis survival (government shutdown, unemployment). Technical approach: Python/Flask backend with blackboard pattern coordination + Claude API for multi-agent intelligence, vanilla JavaScript frontend with mobile-first design and live log streaming, SQLite for MVP data persistence, Azure Container Apps deployment.

## Technical Context

**Language/Version**: Python 3.11+ (backend), HTML/CSS/JavaScript ES6+ (frontend)
**Primary Dependencies**:
- Flask 3.0+ (web framework)
- Blackboard Pattern (multi-agent coordination architecture)
- Anthropic Python SDK (Claude API integration)
- ReportLab (PDF generation)
- SQLite3 (built-in, for session/cache storage, blackboard state persistence)

**Storage**: SQLite for MVP (session data, agent logs, cached responses); local storage (browser) for form state
**Testing**: pytest (backend unit/integration), Playwright (e2e), manual mobile testing
**Target Platform**: Web (mobile-first responsive), Azure Container Apps (Linux container)
**Project Type**: Web application (backend API + frontend SPA)
**Performance Goals**:
- Page load: <3s on 3G
- Agent response: <30s per agent
- Complete plan generation: <5 minutes (target 3 min)
- Support 100 concurrent users

**Constraints**:
- Azure free tier limits (CPU, memory)
- Claude API rate limits (tier-dependent)
- Must work offline for core checklists
- Mobile-responsive (320px-428px viewport)
- <$50 API cost for 1000 plans

**Scale/Scope**:
- MVP: 1000 plans/week
- 7 AI agents with inter-agent communication
- ~15-20 web pages/components
- PDF export with multi-page layouts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Article I: Life-Saving Priority ✅
- **Pass**: Critical information (evacuation, emergency contacts) prioritized in UI flow
- **Pass**: Fail-safe defaults implemented (offline checklists, worst-case guidance)
- **Pass**: No feature delays access to life-saving data

### Article II: Accessibility & Inclusion ✅
- **Pass**: Mobile-first responsive design (320px+)
- **Pass**: 8th-grade reading level for all content
- **Pass**: High contrast UI, 44px+ touch targets
- **Pass**: Budget tiers ($50/$100/$200+) with free alternatives

### Article III: Multi-Agent Transparency ✅
- **Pass**: Real-time agent activity dashboard required
- **Pass**: Plain-language agent descriptions ("Risk Assessment Agent analyzing weather patterns...")
- **Pass**: Progress indicators and status for all agents

### Article IV: Data Privacy & Security ✅
- **Pass**: Minimal data collection (location, household info only)
- **Pass**: HTTPS enforced for all API calls
- **Pass**: No persistent storage of sensitive financial data
- **Pass**: Session-only retention with browser local storage

### Article V: Budget-Consciousness ✅
- **Pass**: Multiple budget tiers in supply planning
- **Pass**: Free alternatives highlighted
- **Pass**: No affiliate links or sponsored content
- **Pass**: Transparent pricing in all recommendations

### Article VI: Evidence-Based Guidance ✅
- **Pass**: All recommendations sourced from FEMA, CDC, Red Cross
- **Pass**: Video curation from authoritative sources only
- **Pass**: Disclaimer prominently displayed

### Article VII: Speed & Simplicity ✅
- **Pass**: 5-minute target for complete plan
- **Pass**: Minimal form fields (6-8 inputs max)
- **Pass**: Progressive disclosure (most critical first)
- **Pass**: Single-page flow for questionnaire

### Article VIII: Test-First Development ✅
- **Will enforce**: Unit tests for each agent before implementation
- **Will enforce**: Integration tests for agent orchestration
- **Will enforce**: E2E tests for critical user flows

### Article IX: Graceful Degradation ✅
- **Pass**: Agent failure handling with partial plan delivery
- **Pass**: Cached fallbacks for API failures
- **Pass**: Static checklists if AI unavailable

**Constitution Status**: ✅ ALL GATES PASSED

## Project Structure

### Documentation (this feature)

```text
.specify/specs/001-prepsmart-mvp/
├── plan.md              # This file
├── research.md          # Phase 0: Tech stack validation, API research
├── data-model.md        # Phase 1: Agent schemas, database tables
├── quickstart.md        # Phase 1: Quick setup and validation guide
├── contracts/           # Phase 1: API endpoints, agent message contracts
│   ├── api-spec.json        # REST API OpenAPI spec
│   ├── agent-messages.json  # Inter-agent message schemas
│   └── pdf-spec.md          # PDF layout specification
└── tasks.md             # Phase 2: Generated by /speckit.tasks
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py           # Base agent interface
│   │   ├── coordinator_agent.py     # Coordinator Agent
│   │   ├── risk_assessment_agent.py
│   │   ├── supply_planning_agent.py
│   │   ├── financial_advisor_agent.py
│   │   ├── resource_locator_agent.py
│   │   ├── video_curator_agent.py
│   │   └── documentation_agent.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── crisis_profile.py
│   │   ├── risk_assessment.py
│   │   ├── supply_plan.py
│   │   ├── emergency_plan.py
│   │   ├── economic_plan.py
│   │   └── agent_log.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # Agent Framework orchestration
│   │   ├── claude_client.py         # Claude API wrapper
│   │   ├── pdf_generator.py         # PDF creation service
│   │   ├── location_service.py      # ZIP/location validation
│   │   └── cache_service.py         # Response caching
│   ├── api/
│   │   ├── __init__.py
│   │   ├── app.py                   # Flask app initialization
│   │   ├── routes.py                # API endpoints
│   │   └── middleware.py            # CORS, error handling
│   ├── data/
│   │   ├── disaster_types.json      # Static disaster definitions
│   │   ├── supply_templates.json    # Base supply lists by disaster
│   │   ├── video_library.json       # Curated video database
│   │   └── offline_checklists.json  # Emergency fallback data
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       ├── logger.py
│       └── config.py
├── tests/
│   ├── contract/
│   │   ├── test_agent_contracts.py
│   │   └── test_api_contracts.py
│   ├── integration/
│   │   ├── test_agent_orchestration.py
│   │   ├── test_end_to_end_natural.py
│   │   └── test_end_to_end_economic.py
│   └── unit/
│       ├── agents/
│       │   ├── test_coordinator.py
│       │   ├── test_risk_assessment.py
│       │   └── [one test file per agent]
│       ├── services/
│       │   └── [test files for each service]
│       └── models/
│           └── [test files for each model]
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
└── README.md

frontend/
├── index.html                   # Landing page
├── assets/
│   ├── css/
│   │   ├── main.css             # Global styles
│   │   ├── mobile.css           # Mobile-specific
│   │   └── components.css       # Reusable components
│   ├── js/
│   │   ├── app.js               # Main application logic
│   │   ├── api-client.js        # Backend API calls
│   │   ├── agent-dashboard.js   # Real-time agent UI
│   │   ├── form-handler.js      # Questionnaire logic
│   │   └── offline.js           # Service worker, local storage
│   └── images/
│       ├── agent-icons/         # Icons for each agent
│       └── disaster-icons/      # Icons for disaster types
├── pages/
│   ├── crisis-select.html       # Crisis type selection
│   ├── questionnaire.html       # Data collection form
│   ├── agent-progress.html      # Agent activity display
│   └── plan-results.html        # Final plan display
└── service-worker.js            # Offline support

.specify/
├── memory/
│   └── constitution.md          # Project principles
├── scripts/
│   └── [spec-kit scripts]
├── specs/
│   └── 001-prepsmart-mvp/       # This feature
└── templates/
    └── [spec-kit templates]

deployment/
├── azure-deploy.yaml            # Azure Container Apps config
├── docker-compose.yml           # Local development setup
└── .env.example                 # Environment variables template

docs/
├── AGENT_ARCHITECTURE.md        # Agent design documentation
├── API_REFERENCE.md             # REST API documentation
└── DEMO_SCRIPT.md               # Hackathon demo walkthrough
```

**Structure Decision**: Web application structure (Option 2) selected because PrepSmart has distinct backend (Python/Flask API + AI agents) and frontend (mobile-responsive web UI). Separation allows independent testing, enables future mobile app to reuse backend API, and aligns with deployment model (backend in Azure Container Apps, frontend as static assets).

## Complexity Tracking

> **No violations to report** - all Constitution gates passed without exceptions.

## Phase 0: Research & Validation

**Goal**: ✅ COMPLETED - Blackboard pattern validated, Claude API integration confirmed, Azure feasibility verified, PDF generation options researched.

**Research Tasks** (Status: ✅ Complete):

1. **Blackboard Pattern Architecture** ✅ COMPLETED
   - **Decision**: Implement blackboard shared state pattern for multi-agent coordination
   - Agents read from and write to central blackboard entity atomically
   - Coordinator monitors blackboard to determine agent execution order
   - Supports parallel execution when agent dependencies permit
   - Cleaner architecture than custom asyncio orchestration
   - **Alternative considered**: Microsoft Agent Framework / AutoGen (optional support layer)

2. **Claude API Integration Verification**
   - Test Anthropic Python SDK with Claude 3.5 Sonnet (or latest available)
   - Benchmark response times for typical prompts (risk assessment, supply planning)
   - Estimate token costs for 1000 plan generations (target: <$50)
   - Confirm rate limits for free tier vs paid tier
   - Test prompt engineering for each agent's role

3. **Azure Container Apps Feasibility**
   - Confirm free tier CPU/memory limits support Flask + 7 agents
   - Test deployment of simple Flask app to Azure Container Apps
   - Verify HTTPS/custom domain support on free tier
   - Research cold start times and mitigation strategies
   - **Fallback**: Render.com or Fly.io if Azure limits too restrictive

4. **PDF Generation Options**
   - Compare ReportLab (Python library) vs wkhtmltopdf (HTML to PDF)
   - Test multi-page layouts with tables, bullet lists, images
   - Measure generation time for 5-page document
   - **Decision**: ReportLab preferred for programmatic control, wkhtmltopdf if HTML templating preferred

5. **Location/ZIP Code Data**
   - Research free ZIP code to lat/long APIs (ZipCodeAPI, GeoNames)
   - Identify disaster risk data sources (NOAA, USGS for earthquakes, FEMA flood maps)
   - **Clarification needed**: Use static dataset vs live API for MVP?

6. **Video Curation Strategy**
   - Test YouTube Data API (requires API key, rate limits)
   - **Alternative**: Curate static list of 50-100 high-quality videos in JSON
   - Decision: Static list for MVP (faster, free, reliable for demo)

**Research Output**: Document findings in `research.md` with recommendations, code samples, and decision rationale.

**Duration**: 4 hours

## Phase 1: Core Design

**Goal**: Define agent message contracts, data models, API endpoints, and PDF layout.

### 1.1: Agent Message Contracts

Define JSON schemas for inter-agent communication:

**Coordinator → Specialist Agents**:
```json
{
  "task_id": "string (UUID)",
  "crisis_profile": {
    "crisis_type": "natural_disaster | economic_crisis",
    "specific_threat": "string",
    "location": {"zip": "string", "city": "string", "state": "string"},
    "household": {"adults": "int", "children": "int", "pets": "int"},
    "housing_type": "apartment | house | mobile_home",
    "budget": 50 | 100 | 200
  },
  "agent_type": "risk_assessment | supply_planning | ...",
  "timeout": "int (seconds)",
  "priority": "high | medium | low"
}
```

**Specialist Agent → Coordinator**:
```json
{
  "task_id": "string (UUID)",
  "agent_type": "string",
  "status": "success | partial | error",
  "result": {/* agent-specific data */},
  "error": "string | null",
  "execution_time": "float (seconds)",
  "tokens_used": "int | null"
}
```

Document all contracts in `contracts/agent-messages.json`.

### 1.2: Data Models

Define Python dataclasses (or Pydantic models) for each entity in spec.md:

- `CrisisProfile`: User input data
- `RiskAssessment`: Risk analysis results
- `SupplyPlan`: Tiered supply lists
- `EmergencyPlan`: Family action plan
- `EconomicPlan`: Financial survival strategy
- `ResourceLocation`: Local assistance resource
- `VideoRecommendation`: Educational video
- `AgentLog`: Real-time agent status

Document in `data-model.md` with field types, validation rules, relationships.

### 1.3: REST API Endpoints

Define Flask routes:

- `POST /api/crisis/start` - Submit questionnaire, start agent processing
- `GET /api/crisis/{task_id}/status` - Poll agent progress (for real-time dashboard)
- `GET /api/crisis/{task_id}/result` - Retrieve complete plan
- `GET /api/crisis/{task_id}/pdf` - Download PDF
- `POST /api/crisis/validate-location` - Validate ZIP code (called during form entry)
- `GET /api/health` - Health check for deployment

Document in `contracts/api-spec.json` (OpenAPI 3.0 format).

### 1.4: PDF Layout Specification

Define PDF structure:
- **Page 1**: Cover with PrepSmart logo, crisis type, user location, generation date
- **Page 2**: Risk Assessment (for natural disaster) or Financial Overview (for economic)
- **Page 3-4**: Supply Plan or Economic Action Plan
- **Page 5**: Emergency Plan or Resources
- **Page 6**: Video recommendations, disclaimers

Document in `contracts/pdf-spec.md` with page layouts, font sizes, spacing.

### 1.5: Quickstart Validation Guide

Create `quickstart.md` with:
- How to set up development environment
- How to run backend + frontend locally
- How to test each agent individually
- How to trigger end-to-end plan generation
- Key validation scenarios (hurricane in Miami, government shutdown)

**Duration**: 6 hours

## Phase 2: Agent Implementation (Test-First)

**Goal**: Implement all 7 agents with unit tests first, then implementation.

### 2.1: Base Agent Interface

**Test**: `tests/unit/agents/test_base_agent.py`
- Test abstract base class enforces required methods
- Test timeout handling
- Test error wrapping

**Implementation**: `src/agents/base_agent.py`
```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self, claude_client, timeout: int = 30):
        self.claude_client = claude_client
        self.timeout = timeout

    @abstractmethod
    async def process(self, crisis_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Each agent implements its specific logic."""
        pass

    def log_activity(self, status: str, message: str):
        """Log to agent activity tracking."""
        pass
```

### 2.2: Coordinator Agent

**Test**: `tests/unit/agents/test_coordinator.py`
- Test crisis type routing (natural disaster → 6 agents, economic → 4 agents)
- Test parallel agent dispatch
- Test result aggregation
- Test partial failure handling (if 1 agent fails, others continue)

**Implementation**: `src/agents/coordinator_agent.py`
- Analyze crisis profile
- Determine which specialist agents to activate
- Dispatch tasks in parallel (asyncio.gather)
- Collect results with timeout handling
- Return aggregated plan

### 2.3: Risk Assessment Agent

**Test**: `tests/unit/agents/test_risk_assessment.py`
- Test hurricane risk calculation (distance to coast, historical data)
- Test earthquake risk (proximity to fault lines)
- Test severity scoring (0-100 scale)
- Test EXTREME/HIGH/MEDIUM/LOW categorization

**Implementation**: `src/agents/risk_assessment_agent.py`
- Use Claude API with prompt: "Analyze disaster risk for [location] considering [threat type]. Provide severity score and specific warnings."
- Parse Claude response into structured `RiskAssessment` model
- Augment with static data (NOAA, USGS) if available

### 2.4: Supply Planning Agent

**Test**: `tests/unit/agents/test_supply_planning.py`
- Test budget tier selection ($50 → Critical only)
- Test household scaling (2 adults + 1 child → 3x water quantity)
- Test crisis-specific items (hurricane → plywood, earthquake → gas shutoff wrench)
- Test price totaling stays within budget

**Implementation**: `src/agents/supply_planning_agent.py`
- Load base supply list from `data/supply_templates.json`
- Use Claude API to personalize: "Create supply list for [crisis] with [household size] and [$X budget]. Prioritize life-safety."
- Scale quantities, filter to budget tier
- Return `SupplyPlan` with Critical/Prepared/Comprehensive tiers

### 2.5: Financial Advisor Agent

**Test**: `tests/unit/agents/test_financial_advisor.py`
- Test expense categorization (Must-Pay: rent, utilities; Defer: credit cards; Eliminate: subscriptions)
- Test 30-day timeline generation (Day 1: landlord letter, Day 2: unemployment application)
- Test benefits eligibility calculation
- Test hardship letter template personalization

**Implementation**: `src/agents/financial_advisor_agent.py`
- Use Claude API with financial prompt: "Create 30-day survival budget for [income loss scenario] with [expenses] and [savings]."
- Parse into Must-Pay/Defer/Eliminate buckets
- Generate day-by-day action plan
- Include benefits estimate, hardship templates

### 2.6: Resource Locator Agent

**Test**: `tests/unit/agents/test_resource_locator.py`
- Test location-based search (ZIP → nearby shelters)
- Test resource type filtering (food banks vs unemployment offices)
- Test distance calculation and sorting
- Test fallback to wider radius if no nearby results

**Implementation**: `src/agents/resource_locator_agent.py`
- Use static dataset or API (Google Places, OpenStreetMap) to find:
  - Shelters (Red Cross, community centers)
  - Food banks
  - Unemployment offices
  - Hospitals (for medical emergencies)
- Return list of `ResourceLocation` sorted by distance

### 2.7: Video Curator Agent

**Test**: `tests/unit/agents/test_video_curator.py`
- Test crisis-type matching (hurricane → hurricane prep videos)
- Test relevance scoring
- Test limit to 5-7 videos
- Test fallback to general preparedness if specific crisis videos unavailable

**Implementation**: `src/agents/video_curator_agent.py`
- Load curated video database from `data/video_library.json`
- Filter by crisis type
- Use Claude API for relevance ranking: "Rank these videos by relevance to [crisis] for [household]."
- Return top 5-7 `VideoRecommendation` objects

### 2.8: Documentation Agent

**Test**: `tests/unit/agents/test_documentation.py`
- Test PDF generation from complete plan data
- Test multi-page layout
- Test missing data handling (if agent failed, show "Data unavailable")
- Test file size stays under 5MB

**Implementation**: `src/agents/documentation_agent.py`
- Receive all specialist agent results
- Use ReportLab to generate PDF:
  - Cover page
  - Risk assessment or financial overview
  - Supply/economic plan tables
  - Emergency plan bullet lists
  - Resources and videos
- Return PDF as bytes for download

**Duration**: 16 hours (2 hours per agent average, Coordinator and Documentation Agent more complex)

## Phase 3: Backend Services & API

**Goal**: Implement orchestration service, Flask API routes, caching.

### 3.1: Orchestration Service

**Test**: `tests/integration/test_agent_orchestration.py`
- Test end-to-end orchestration with all 7 agents
- Test parallel execution (agents run concurrently)
- Test timeout enforcement (agent exceeds 30s → graceful failure)
- Test result caching (same request within 1 hour → cached response)

**Implementation**: `src/services/orchestrator.py`
```python
class AgentOrchestrator:
    def __init__(self, claude_client, cache_service):
        self.coordinator = CoordinatorAgent(claude_client)
        # Initialize all specialist agents
        self.cache = cache_service

    async def generate_plan(self, crisis_profile: CrisisProfile) -> Dict:
        # Check cache
        cached = self.cache.get(crisis_profile)
        if cached:
            return cached

        # Coordinate agents
        result = await self.coordinator.process(crisis_profile)

        # Cache result
        self.cache.set(crisis_profile, result, ttl=3600)
        return result
```

### 3.2: Flask API Routes

**Test**: `tests/contract/test_api_contracts.py`
- Test POST /api/crisis/start returns task_id
- Test GET /api/crisis/{task_id}/status returns agent progress
- Test GET /api/crisis/{task_id}/result returns complete plan
- Test error responses (404, 500) match OpenAPI spec

**Implementation**: `src/api/routes.py`
```python
@app.route('/api/crisis/start', methods=['POST'])
def start_crisis_plan():
    data = request.json
    crisis_profile = CrisisProfile(**data)

    # Start async orchestration
    task_id = str(uuid.uuid4())
    asyncio.create_task(orchestrator.generate_plan(crisis_profile))

    return jsonify({"task_id": task_id}), 202

@app.route('/api/crisis/<task_id>/status', methods=['GET'])
def get_status(task_id):
    # Query agent logs for task_id
    logs = db.get_agent_logs(task_id)
    return jsonify({"agents": logs, "complete": all_complete(logs)})
```

### 3.3: Claude API Client

**Test**: `tests/unit/services/test_claude_client.py`
- Test successful API call
- Test rate limit handling (429 → exponential backoff)
- Test timeout handling
- Test token counting for cost estimation

**Implementation**: `src/services/claude_client.py`
```python
from anthropic import Anthropic

class ClaudeClient:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    async def generate(self, prompt: str, system: str = "") -> str:
        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
```

### 3.4: PDF Generator Service

**Test**: `tests/unit/services/test_pdf_generator.py`
- Test PDF generation from plan data
- Test page breaks
- Test image embedding (agent icons)
- Test file size < 5MB

**Implementation**: `src/services/pdf_generator.py`
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

class PDFGenerator:
    def generate(self, plan_data: Dict) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []

        # Add content
        story.append(Paragraph("<b>PrepSmart Crisis Plan</b>", title_style))
        # ... build document

        doc.build(story)
        return buffer.getvalue()
```

**Duration**: 10 hours

## Phase 4: Frontend Implementation

**Goal**: Build mobile-first web UI with agent dashboard, questionnaire, results display.

### 4.1: Landing Page & Crisis Selection

**Manual Test**: Navigate to index.html, verify responsive layout, buttons work on mobile.

**Implementation**: `frontend/index.html` + `frontend/assets/css/main.css`
- Hero section with PrepSmart mission
- Two large buttons: "Natural Disaster" | "Economic Crisis"
- Clicking either navigates to `crisis-select.html` with type pre-selected
- Mobile: full-width buttons, large text (18px+), high contrast

### 4.2: Questionnaire Form

**Manual Test**: Fill out form on mobile, verify keyboard handling, validation.

**Implementation**: `frontend/pages/questionnaire.html` + `frontend/assets/js/form-handler.js`
- Form fields:
  - Location (ZIP or city/state)
  - Household (adults, children, pets)
  - Housing type (radio buttons)
  - Budget (radio buttons: $50/$100/$200+)
  - Economic crisis fields (current income, expenses, savings) shown conditionally
- Validation: ZIP code format, numeric fields, required fields
- Save to local storage on every input change (FR-023)
- Submit → POST /api/crisis/start → redirect to agent-progress.html with task_id

### 4.3: Agent Activity Dashboard

**Manual Test**: Start plan, verify agents show "Active" status, progress updates.

**Implementation**: `frontend/pages/agent-progress.html` + `frontend/assets/js/agent-dashboard.js`
- Display 7 agent cards (or 4-6 depending on crisis type)
- Each card shows:
  - Agent icon
  - Agent name ("Risk Assessment Agent")
  - Description ("Analyzing weather patterns for your location...")
  - Status badge (Waiting/Active/Complete/Error)
  - Progress bar (0-100%)
- Poll GET /api/crisis/{task_id}/status every 2 seconds
- Update UI in real-time as agents complete
- When all complete, show "View Your Plan" button → plan-results.html

### 4.4: Plan Results Display

**Manual Test**: View completed plan on mobile, verify all sections readable, PDF downloads.

**Implementation**: `frontend/pages/plan-results.html`
- Sections (collapsible on mobile):
  - Risk Assessment summary (for natural disaster)
  - Supply Plan with tiered lists
  - Emergency Plan with action items
  - Local Resources with map (static image or embedded map)
  - Video Recommendations with thumbnails and links
- "Download PDF" button → GET /api/crisis/{task_id}/pdf
- "Start New Plan" button → return to index.html

### 4.5: Offline Support

**Test**: Enable airplane mode, verify static checklists load.

**Implementation**: `frontend/service-worker.js` + `frontend/assets/js/offline.js`
- Cache critical HTML, CSS, JS files
- Cache `data/offline_checklists.json` (basic hurricane/earthquake/economic guides)
- If offline, show warning banner: "You're offline. Viewing cached emergency checklists."
- Service worker intercepts requests, serves cached content

### 4.6: Responsive CSS

**Test**: Chrome DevTools mobile emulation (iPhone SE, Galaxy S20), verify 320px-428px.

**Implementation**: `frontend/assets/css/mobile.css`
- Mobile-first media queries
- Touch targets ≥44px
- Font sizes ≥16px (body), ≥18px (headings)
- High contrast (WCAG AA compliant)
- Collapsible sections for long content

**Duration**: 12 hours

## Phase 5: Integration Testing & E2E Scenarios

**Goal**: Test complete user flows end-to-end with realistic data.

### 5.1: Natural Disaster Flow (Hurricane in Jamaica)

**Test**: `tests/integration/test_end_to_end_natural.py`
- Scenario: User in Kingston, Jamaica (Hurricane Melissa)
- Submit: ZIP code (or equivalent), 3 adults, 2 children, 1 pet, house, $100 budget
- Verify: Risk Assessment shows EXTREME for hurricane
- Verify: Supply Plan includes hurricane-specific items (plywood, generator)
- Verify: Emergency Plan includes evacuation routes
- Verify: PDF generates successfully
- Measure: Complete flow <5 minutes

### 5.2: Economic Crisis Flow (Government Shutdown)

**Test**: `tests/integration/test_end_to_end_economic.py`
- Scenario: Federal worker in Washington D.C., furloughed
- Submit: Economic crisis, government shutdown, $0 income, $3000 expenses, $2000 savings
- Verify: Financial Advisor categorizes expenses correctly
- Verify: 30-day action plan includes Day 1: Contact landlord, Day 2: File unemployment
- Verify: Benefits eligibility shows SNAP, unemployment estimates
- Verify: Hardship letter templates populate with user data
- Verify: Resource Locator finds D.C. food banks, unemployment office

### 5.3: Agent Failure Handling

**Test**: Manually disable one agent (e.g., Video Curator), run flow
- Verify: Plan still generates with 6/7 agents
- Verify: Video section shows "Video recommendations unavailable" message
- Verify: PDF generates with note about missing section

### 5.4: Mobile E2E Test

**Test**: Playwright script on mobile viewport (375x667)
- Navigate to index.html
- Click "Natural Disaster"
- Fill questionnaire
- Wait for agent processing
- View results
- Download PDF
- Verify: All interactions work with touch, no layout breaks

**Duration**: 6 hours

## Phase 6: Deployment & Polish

**Goal**: Deploy to Azure, add final polish (loading states, error messages, demo script).

### 6.1: Azure Container Apps Deployment

**Implementation**:
- Create `Dockerfile` for Flask backend
- Create `azure-deploy.yaml` for Azure Container Apps
- Set environment variables (CLAUDE_API_KEY, FLASK_SECRET)
- Deploy backend container
- Host frontend as static assets (Azure Blob Storage or CDN)
- Configure CORS for frontend → backend communication
- Test deployed app end-to-end

### 6.2: Error Handling & Loading States

- Add loading spinners during agent processing
- Add error messages for common failures (invalid ZIP, API timeout)
- Add retry logic for transient API failures
- Add "Contact Support" message for unrecoverable errors

### 6.3: Demo Script & Documentation

Create `docs/DEMO_SCRIPT.md` for hackathon presentation:
- 2-minute pitch (problem, solution, multi-agent innovation)
- 3-minute live demo (start plan, watch agents, show results)
- 1-minute Q&A prep (FAQs, technical deep-dive)

Create `docs/AGENT_ARCHITECTURE.md`:
- Diagram of agent orchestration
- Message flow between agents
- Rationale for each agent's role

### 6.4: Final Testing & Validation

- Run full constitution compliance checklist
- Test on real devices (iPhone, Android)
- Load test with 10 concurrent users
- Verify API cost tracking (<$50 for 1000 plans)
- Final review of all acceptance scenarios from spec.md

**Duration**: 10 hours

## Total Estimated Duration: 64 hours (~4 days with focus)

### Day 1 (16 hours): Research, Design, Base Agents
- Morning: Phase 0 (Research) - 4h
- Afternoon: Phase 1 (Core Design) - 6h
- Evening: Phase 2 Start (Base Agent, Coordinator, Risk Assessment) - 6h

### Day 2 (16 hours): Agent Implementation
- Full day: Phase 2 Continue (Supply, Financial, Resource, Video, Documentation agents) - 16h

### Day 3 (16 hours): Backend & Frontend
- Morning: Phase 3 (Backend Services & API) - 10h
- Afternoon: Phase 4 Start (Landing, Questionnaire, Agent Dashboard) - 6h

### Day 4 (16 hours): Frontend, Testing, Deployment
- Morning: Phase 4 Finish (Results Display, Offline, CSS) - 6h
- Afternoon: Phase 5 (Integration Testing) - 6h
- Evening: Phase 6 (Deployment & Polish) - 4h

**Buffer**: If behind schedule, prioritize P1 user stories. Cut Video Curator Agent (use static list) or offline support if necessary.

## Risk Mitigation

**Risk**: Microsoft Agent Framework insufficient or buggy
**Mitigation**: Fallback to custom orchestration with asyncio + message queue (Redis)

**Risk**: Claude API rate limits hit during demo
**Mitigation**: Pre-generate 5-10 cached plans for common scenarios (Miami hurricane, D.C. shutdown)

**Risk**: Azure free tier too restrictive
**Mitigation**: Deploy to Render.com or Fly.io instead (both have free tiers)

**Risk**: PDF generation too slow
**Mitigation**: Generate PDF asynchronously, provide email delivery option

**Risk**: Location data unavailable for Jamaica
**Mitigation**: Use manual lat/long entry, focus demo on US location (Miami) where data is robust

## Clarifications Resolved

Based on spec.md clarifications:

1. **Accounts/Saving Plans**: MVP is anonymous, one-time usage. No login/account required. Local storage for form resume only.

2. **Video Curator**: Use static curated list in `data/video_library.json` (50-100 videos). No YouTube API for MVP (avoids rate limits, cost, complexity).

3. **Resource Locator**: Use OpenStreetMap Nominatim API (free, no key required) + static dataset of major shelters/food banks. No Google Maps API for MVP.

4. **Disaster Types**: MVP supports all 6 natural disaster types (hurricane, earthquake, wildfire, flood, tornado, blizzard). Supply templates differentiate per type.

5. **Demo Agent Processing**: Real agent processing with Claude API for demo. Pre-cache 3-5 common scenarios as fallback if API fails during presentation.

6. **Languages**: English only for MVP. Code structured for i18n (use string constants file), Spanish translation in v2 roadmap.

## Success Validation

Before considering MVP complete, verify:

- [ ] All P1 user stories pass acceptance scenarios
- [ ] Constitution gates all pass (especially Life-Saving Priority, Accessibility)
- [ ] Complete plan generates in <5 minutes (test with 10 different scenarios)
- [ ] Mobile responsive on iPhone SE (320px) and Galaxy S20 (428px)
- [ ] Agent dashboard clearly shows 7 agents with real-time status
- [ ] PDF downloads successfully with all sections populated
- [ ] Graceful degradation tested (disable 1 agent, verify partial plan)
- [ ] Hackathon demo script practiced and under 6 minutes
- [ ] Real-world scenario tested (Hurricane Melissa in Jamaica, Government Shutdown in D.C.)
- [ ] API cost tracking shows <$0.05 per plan generation

**Ready for Implementation**: Yes, pending clarification resolutions noted above.
