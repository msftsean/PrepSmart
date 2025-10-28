# PrepSmart

**Multi-Agent AI Crisis Preparedness Assistant**

PrepSmart helps people survive both natural disasters AND economic emergencies through personalized, AI-generated crisis preparedness plans delivered in under 5 minutes.

---

## 🌟 The Problem

**Right now (October 2025)**, we face TWO major crises:
1. **Hurricane Melissa** - Category 5 hurricane devastating Jamaica
2. **US Government Shutdown** - 900,000+ federal workers furloughed, 700,000+ working without pay

People want to be prepared, but existing resources are:
- **Overwhelming**: Generic 50-page PDFs that no one reads
- **Expensive**: "Ultimate survival kits" cost $500+
- **Inaccessible**: Assumes everyone has money, internet, and time

---

## 💡 The Solution

PrepSmart uses **7 specialized AI agents** working together to create personalized crisis plans in minutes:

### 🤖 The Multi-Agent System

1. **Coordinator Agent** - Triages requests and orchestrates workflow
2. **Risk Assessment Agent** - Analyzes disaster threats for your location
3. **Supply Planning Agent** - Creates budget-optimized supply lists (3 tiers)
4. **Financial Advisor Agent** - Builds 30-day economic survival plans
5. **Resource Locator Agent** - Finds local food banks, shelters, unemployment offices
6. **Video Curator Agent** - Recommends relevant preparedness videos
7. **Documentation Agent** - Compiles everything into downloadable PDF

### 🎯 What You Get

**For Natural Disasters (hurricanes, earthquakes, wildfires, floods, tornadoes, blizzards)**:
- Risk assessment with severity levels (EXTREME/HIGH/MEDIUM/LOW)
- Prioritized supply checklists (Critical/Prepared/Comprehensive tiers)
- Family emergency plan (evacuation routes, meeting points, communication)
- Local emergency resources (shelters, hospitals)
- Educational video recommendations
- Downloadable PDF plan

**For Economic Crises (unemployment, furlough, government shutdown, layoffs)**:
- 30-day survival budget (must-pay vs defer vs eliminate)
- Day-by-day action plan
- Benefits eligibility (unemployment, SNAP, Medicaid)
- Hardship letter templates (for landlords, creditors)
- Local assistance resources (food banks, free legal aid)
- How-to videos (filing unemployment, etc.)
- Downloadable survival guide PDF

---

## ✨ Key Features

- ⚡ **Fast**: Complete plan in under 5 minutes (target: 3 minutes)
- 💰 **Budget-Conscious**: Three tiers ($50/$100/$200+) with free alternatives
- 📱 **Mobile-First**: Works on phones (320px+) with offline support
- 🌍 **Accessible**: Simple language, high contrast, large touch targets
- 🔒 **Privacy-Focused**: No selling data, minimal collection, session-only storage
- 📄 **Evidence-Based**: All recommendations from FEMA, CDC, Red Cross
- 🎨 **Transparent**: Watch agents work in real-time on dashboard

---

## 🏗️ Architecture

### Tech Stack

**Backend**:
- Python 3.11+ with Flask
- AutoGen (Microsoft Agent Framework) for multi-agent orchestration
- Claude 3.5 Sonnet (Anthropic) for AI intelligence
- ReportLab for PDF generation
- SQLite (MVP) → PostgreSQL (production)
- uszipcode for location validation

**Frontend**:
- Vanilla HTML/CSS/JavaScript (mobile-first)
- Service Worker for offline support
- No framework overhead for fast load times

**Deployment**:
- Azure Container Apps (primary)
- Railway/Render (fallback)

### Project Structure

```
prepsmart/
├── .specify/                    # Spec-Driven Development artifacts
│   ├── memory/
│   │   └── constitution.md      # 9 core principles
│   ├── specs/001-prepsmart-mvp/
│   │   ├── spec.md              # Feature specification (5 user stories)
│   │   ├── plan.md              # Implementation plan (6 phases, 64 hours)
│   │   ├── research.md          # Tech validation
│   │   ├── data-model.md        # 9 entities with schemas
│   │   ├── quickstart.md        # 15-minute setup guide
│   │   ├── tasks.md             # 110 tasks organized by user story
│   │   └── contracts/           # API & agent message contracts
│   └── templates/               # Spec-kit templates
├── backend/
│   ├── src/
│   │   ├── agents/              # 7 AI agents
│   │   ├── models/              # Pydantic data models
│   │   ├── services/            # Orchestration, Claude client, PDF
│   │   ├── api/                 # Flask routes
│   │   ├── data/                # Static datasets (videos, resources)
│   │   └── utils/               # Config, logging, validators
│   ├── tests/
│   │   ├── contract/            # API contract tests
│   │   ├── integration/         # E2E agent tests
│   │   └── unit/                # Agent unit tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html               # Landing page
│   ├── pages/                   # Crisis selection, questionnaire, results
│   └── assets/
│       ├── css/                 # Global, mobile, component styles
│       ├── js/                  # App logic, API client, agent dashboard
│       └── images/              # Agent icons, disaster icons
├── deployment/
│   ├── azure-deploy.yaml        # Azure Container Apps config
│   └── docker-compose.yml       # Local development
└── docs/
    ├── AGENT_ARCHITECTURE.md    # Agent design documentation
    ├── API_REFERENCE.md         # REST API docs
    └── DEMO_SCRIPT.md           # Hackathon presentation guide
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **uv** ([Install](https://docs.astral.sh/uv/)): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Claude API Key** from Anthropic ([Get one](https://console.anthropic.com/))

### Setup (15 minutes)

```bash
# Clone and navigate to project
cd /workspaces/prepsmart

# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
cd backend
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt

# Configure environment
cat > .env << EOF
CLAUDE_API_KEY=sk-ant-your-api-key-here
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=sqlite:///prepsmart.db
AGENT_TIMEOUT=30
LOG_LEVEL=INFO
EOF

# Initialize database
python -c "from src.api.app import init_db; init_db()"

# Start backend (Terminal 1)
python -m src.api.app

# Start frontend (Terminal 2)
cd ../frontend
python -m http.server 8000
```

Visit **http://localhost:8000** and generate your first crisis plan!

For detailed setup instructions, see [quickstart.md](.specify/specs/001-prepsmart-mvp/quickstart.md).

---

## 📋 Development Roadmap

### Phase 1: Setup ✅ COMPLETE
- [x] Project structure
- [x] Constitution (9 core principles)
- [x] Feature specification (5 user stories)
- [x] Implementation plan (6 phases, 64 hours)
- [x] Data models (9 entities)
- [x] API contracts (OpenAPI 3.0)
- [x] Task breakdown (110 tasks)

### Phase 2: Foundation (Day 1) - READY TO START
- [ ] Database schema
- [ ] Flask app initialization
- [ ] Claude API client
- [ ] Base agent interface
- [ ] Static data files

### Phase 3: Natural Disaster MVP (Days 1-2)
- [ ] 7 AI agents implementation
- [ ] Agent orchestration
- [ ] PDF generation
- [ ] Frontend (questionnaire → agent dashboard → results)
- [ ] End-to-end testing

### Phase 4: Economic Crisis (Day 3)
- [ ] Financial Advisor Agent
- [ ] Economic plan frontend
- [ ] Hardship letter templates
- [ ] Integration testing

### Phase 5: Polish & Deploy (Day 4)
- [ ] Mobile responsiveness
- [ ] Offline support
- [ ] Azure deployment
- [ ] Hackathon demo prep

---

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test suite
pytest backend/tests/unit/agents/ -v
pytest backend/tests/integration/ -v

# Run with coverage
pytest --cov=backend/src backend/tests/

# Type checking
mypy backend/src/

# Linting
ruff check backend/src/
```

### Validation Scenarios

1. **Hurricane in Miami** (33139): EXTREME risk → $100 supply list → evacuation plan
2. **Government Shutdown in DC**: $0 income → 30-day action plan → $2,480/mo benefits
3. **Earthquake in SF** (94102): HIGH risk → $50 supply list → shelter-in-place

---

## 📊 Performance Benchmarks

| Metric | Target | Typical |
|--------|--------|---------|
| Complete plan generation | <5min | 2-3min |
| Agent response time | <30s | 10-15s |
| PDF generation | <10s | 3-5s |
| Page load (mobile 3G) | <3s | 1-2s |
| API cost per plan | <$0.10 | ~$0.075 |

---

## 🎯 Success Criteria (from spec.md)

- [ ] SC-001: Plans generated in under 5 minutes (target: 3 min avg)
- [ ] SC-002: 100% of valid US ZIP codes supported
- [ ] SC-003: 90% of users report actionable next steps
- [ ] SC-004: Multi-agent orchestration visible and understandable
- [ ] SC-005: 100 concurrent users supported
- [ ] SC-006: PDF generation 95%+ success rate
- [ ] SC-007: 100% mobile functionality (320px-428px)
- [ ] SC-008: Supply plans within budget 90%+ of time
- [ ] SC-009: Graceful degradation on agent failures
- [ ] SC-010: 100% of advice sourced from FEMA/CDC/Red Cross
- [ ] SC-011: Minimum 20 action items in economic plans
- [ ] SC-012: Hackathon judges impressed with demo
- [ ] SC-013: Page load <3s on 3G
- [ ] SC-014: Lighthouse accessibility score 90+
- [ ] SC-015: Zero sensitive data stored beyond session

---

## 🏛️ Constitutional Principles

PrepSmart is governed by **9 core principles** defined in [constitution.md](.specify/memory/constitution.md):

1. **Life-Saving Priority** - Critical info first, fail-safe defaults
2. **Accessibility & Inclusion** - Mobile-first, 8th-grade reading level, budget-conscious
3. **Multi-Agent Transparency** - Real-time agent activity visible
4. **Data Privacy & Security** - Minimal collection, HTTPS only, no selling data
5. **Budget-Consciousness** - Multiple tiers, free alternatives highlighted
6. **Evidence-Based Guidance** - FEMA/CDC/Red Cross sources only
7. **Speed & Simplicity** - 5-minute target, minimal form fields
8. **Test-First Development** - All agents tested before implementation
9. **Graceful Degradation** - Partial plans if agents fail

All development decisions must align with these principles.

---

## 📚 Documentation

- **[Feature Specification](.specify/specs/001-prepsmart-mvp/spec.md)** - 5 user stories with acceptance criteria
- **[Implementation Plan](.specify/specs/001-prepsmart-mvp/plan.md)** - 6-phase, 64-hour roadmap
- **[Data Model](.specify/specs/001-prepsmart-mvp/data-model.md)** - 9 entities with schemas
- **[API Contracts](.specify/specs/001-prepsmart-mvp/contracts/)** - OpenAPI spec + agent messages
- **[Quickstart Guide](.specify/specs/001-prepsmart-mvp/quickstart.md)** - 15-minute setup
- **[Task Breakdown](.specify/specs/001-prepsmart-mvp/tasks.md)** - 110 tasks organized by user story
- **[Research](.specify/specs/001-prepsmart-mvp/research.md)** - Tech stack validation

---

## 🎓 Hackathon Context

**Event**: AI Bootcamp Hackathon
**Deadline**: October 31, 2025
**Timeline**: 4 days (Oct 27-31)

**Demo Focus**:
- Multi-agent orchestration (7 agents visible on dashboard)
- Real-world urgency (Hurricane Melissa + Government Shutdown)
- Live value (could actually save lives)
- Technical sophistication (AutoGen + Claude API + PDF generation)

**Demo Script**: See [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) (to be created)

---

## 🤝 Contributing

PrepSmart follows **Spec-Driven Development** methodology:

1. Review [constitution.md](.specify/memory/constitution.md) for core principles
2. All changes must align with constitutional gates
3. Tests written BEFORE implementation (Article VIII)
4. User stories implemented independently
5. See [tasks.md](.specify/specs/001-prepsmart-mvp/tasks.md) for current task list

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgements

- **Spec-Driven Development** methodology by [John Lam](https://github.com/jflam) and [Spec Kit](https://github.com/github/spec-kit)
- **Microsoft Agent Framework** (AutoGen)
- **Anthropic Claude API** for AI intelligence
- **FEMA, CDC, Red Cross** for emergency preparedness guidance

---

## 📞 Support

**For Hackathon Judges/Reviewers**:
- Demo walkthrough: [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) (to be created)
- Agent architecture: [docs/AGENT_ARCHITECTURE.md](docs/AGENT_ARCHITECTURE.md) (to be created)
- API reference: [docs/API_REFERENCE.md](docs/API_REFERENCE.md) (to be created)

**For Developers**:
- Issues: Use GitHub Issues with appropriate labels (`bug`, `enhancement`, `question`)
- Questions: Check [quickstart.md](.specify/specs/001-prepsmart-mvp/quickstart.md) first

---

**Built with ❤️ and AI to help people survive crises**

**Timeline**: 4 days | **Status**: Planning Complete ✅ | **Next**: Implementation Phase 1 🚀
