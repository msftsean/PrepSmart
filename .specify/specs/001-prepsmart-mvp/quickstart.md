# PrepSmart Quickstart Guide

**Purpose**: Get PrepSmart running locally in under 15 minutes for development and testing.

**Last Updated**: 2025-10-28

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **uv** ([Install](https://docs.astral.sh/uv/)): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git** ([Download](https://git-scm.com/downloads))
- **Claude API Key** from Anthropic ([Get one](https://console.anthropic.com/))
- **Code Editor** (VS Code, Cursor, or your preference)
- **Modern Web Browser** (Chrome, Firefox, Safari recommended)

---

## Step 1: Clone & Setup (3 minutes)

```bash
# Clone the repository
cd /workspaces/prepsmart

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
cd backend
uv pip install -r requirements.txt
uv pip install -r requirements-dev.txt  # For testing

# Verify installation
python -c "import anthropic; import pyautogen; print('✅ Dependencies installed')"
```

---

## Step 2: Configure Environment (2 minutes)

```bash
# Create .env file in backend/ directory
cat > .env << EOF
# Claude API Configuration
CLAUDE_API_KEY=sk-ant-your-api-key-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Database
DATABASE_URL=sqlite:///prepsmart.db

# Agent Configuration
AGENT_TIMEOUT=30
MAX_CONCURRENT_TASKS=10

# Logging
LOG_LEVEL=INFO
EOF

# ⚠️ IMPORTANT: Replace 'sk-ant-your-api-key-here' with your actual Claude API key
```

---

## Step 3: Initialize Database (1 minute)

```bash
# Still in backend/ directory
python -c "
from src.api.app import init_db
init_db()
print('✅ Database initialized')
"
```

---

## Step 4: Start Backend Server (1 minute)

```bash
# Start Flask development server
python -m src.api.app

# You should see:
# * Running on http://127.0.0.1:5000
# * Debug mode: on
```

**Keep this terminal open**. Backend is now running on `http://localhost:5000`.

---

## Step 5: Verify Backend Health (1 minute)

In a **new terminal**, test the API:

```bash
# Health check
curl http://localhost:5000/api/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-28T15:00:00Z",
#   "dependencies": {
#     "claude_api": "up",
#     "database": "up"
#   }
# }
```

---

## Step 6: Start Frontend (1 minute)

```bash
# In a new terminal, navigate to frontend directory
cd /workspaces/prepsmart/frontend

# Start a simple HTTP server (Python 3 built-in)
python -m http.server 8000

# Or use Node.js http-server if available:
# npx http-server -p 8000

# Frontend now running at http://localhost:8000
```

---

## Step 7: Test End-to-End Flow (5 minutes)

### Option A: Web UI Test (Recommended)

1. Open browser to **http://localhost:8000**
2. Click **"Natural Disaster"**
3. Fill out questionnaire:
   - ZIP Code: `33139` (Miami Beach, FL)
   - Adults: `2`, Children: `1`, Pets: `1`
   - Housing: `Apartment`
   - Budget: `$100`
4. Click **"Generate Plan"**
5. Watch agents process (should see real-time status updates)
6. View complete plan (should appear in 2-3 minutes)
7. Click **"Download PDF"** to test PDF generation

### Option B: API Test (For Developers)

```bash
# Start a crisis plan generation
curl -X POST http://localhost:5000/api/crisis/start \
  -H "Content-Type: application/json" \
  -d '{
    "crisis_mode": "natural_disaster",
    "specific_threat": "hurricane",
    "location": {
      "zip_code": "33139"
    },
    "household": {
      "adults": 2,
      "children": 1,
      "pets": 1
    },
    "housing_type": "apartment",
    "budget_tier": 100
  }'

# Save the task_id from response
TASK_ID="<task_id_from_response>"

# Poll status (run every 5 seconds)
curl http://localhost:5000/api/crisis/$TASK_ID/status

# Get complete result (when status is "completed")
curl http://localhost:5000/api/crisis/$TASK_ID/result

# Download PDF
curl http://localhost:5000/api/crisis/$TASK_ID/pdf -o plan.pdf
```

---

## Step 8: Test Individual Agents (Optional - 5 minutes)

```bash
# Test Risk Assessment Agent
cd /workspaces/prepsmart/backend
python -c "
from src.agents.risk_assessment_agent import RiskAssessmentAgent
from src.services.claude_client import ClaudeClient
import os

client = ClaudeClient(os.getenv('CLAUDE_API_KEY'))
agent = RiskAssessmentAgent(client)

crisis_profile = {
    'location': {'city': 'Miami Beach', 'state': 'FL'},
    'specific_threat': 'hurricane'
}

result = agent.process(crisis_profile)
print('✅ Risk Assessment Agent:', result['overall_risk_level'])
"

# Test Supply Planning Agent
python -c "
from src.agents.supply_planning_agent import SupplyPlanningAgent
from src.services.claude_client import ClaudeClient
import os

client = ClaudeClient(os.getenv('CLAUDE_API_KEY'))
agent = SupplyPlanningAgent(client)

crisis_profile = {
    'specific_threat': 'hurricane',
    'household': {'adults': 2, 'children': 1, 'pets': 1},
    'budget_tier': 100
}

result = agent.process(crisis_profile)
print('✅ Supply Planning Agent:', len(result['tiers']['critical']['items']), 'items')
"
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'anthropic'"

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install anthropic
```

### Issue: "401 Unauthorized" when calling Claude API

**Solution**:
```bash
# Verify API key is set correctly
echo $CLAUDE_API_KEY

# If empty, export it:
export CLAUDE_API_KEY=sk-ant-your-actual-key
```

### Issue: "Address already in use" for port 5000 or 8000

**Solution**:
```bash
# Find process using port
lsof -i :5000  # or :8000

# Kill process
kill -9 <PID>

# Or use different ports:
flask run --port 5001
python -m http.server 8001
```

### Issue: "Database locked" error

**Solution**:
```bash
# Stop all Flask processes
pkill -f flask

# Delete database and reinitialize
rm backend/prepsmart.db
python -c "from src.api.app import init_db; init_db()"
```

### Issue: Claude API is slow or timing out

**Solution**:
- Check internet connection
- Verify API key has quota remaining
- Increase `AGENT_TIMEOUT` in `.env` (default 30 seconds)
- Check Anthropic status: https://status.anthropic.com

---

## Validation Scenarios

Use these scenarios to validate PrepSmart is working correctly:

### Scenario 1: Hurricane in Miami (EXTREME Risk)

**Input**:
- Crisis: Natural Disaster → Hurricane
- Location: `33139` (Miami Beach, FL)
- Household: 2 adults, 1 child, 1 pet
- Housing: Apartment
- Budget: $100

**Expected Output**:
- Risk Level: **EXTREME** (90-100 severity)
- Evacuation Recommended: **Yes**
- Supply List: 5-7 critical items ~$90
- Emergency Plan: Evacuation routes to inland shelter
- Resources: Miami area shelters, hospitals
- Videos: 5-7 hurricane prep videos

**Validation Time**: ~3 minutes

---

### Scenario 2: Government Shutdown Economic Crisis

**Input**:
- Crisis: Economic Crisis → Government Shutdown
- Location: Washington, DC
- Household: 2 adults, 2 children
- Financial Situation:
  - Current Income: $0
  - Monthly Expenses: $3200
  - Savings: $2000
  - Debt: $500
  - Employment: Furloughed

**Expected Output**:
- Runway: ~18 days without action
- Expense Categories: Must-Pay, Defer, Eliminate
- 30-Day Action Plan: Day-by-day tasks
- Benefits: Unemployment + SNAP estimates
- Hardship Letters: Landlord, creditor templates
- Resources: DC food banks, unemployment office

**Validation Time**: ~3 minutes

---

### Scenario 3: Earthquake in San Francisco (HIGH Risk)

**Input**:
- Crisis: Natural Disaster → Earthquake
- Location: `94102` (San Francisco, CA)
- Household: 1 adult, no children, no pets
- Housing: Apartment
- Budget: $50

**Expected Output**:
- Risk Level: **HIGH** (70-80 severity)
- Evacuation Recommended: **No** (shelter in place)
- Supply List: 4-5 critical items ~$45
- Emergency Plan: Drop/Cover/Hold, safe rooms
- Resources: SF shelters, emergency services
- Videos: Earthquake safety videos

**Validation Time**: ~2 minutes

---

## Development Workflow

### Running Tests

```bash
cd /workspaces/prepsmart/backend

# Run all tests
pytest

# Run specific test file
pytest tests/unit/agents/test_risk_assessment.py

# Run with coverage
pytest --cov=src tests/

# Run integration tests only
pytest tests/integration/ -v
```

### Linting & Type Checking

```bash
# Ruff linting (Python)
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/

# Type checking with mypy
mypy src/
```

### Frontend Testing (Manual)

1. Test mobile responsiveness:
   - Open Chrome DevTools (F12)
   - Toggle device toolbar (Ctrl+Shift+M)
   - Test on iPhone SE (320px), Galaxy S20 (428px)

2. Test offline mode:
   - Open DevTools → Application → Service Workers
   - Check "Offline"
   - Reload page (should show cached checklists)

---

## Performance Benchmarks

Expected performance on local development:

| Metric | Target | Typical |
|--------|--------|---------|
| Backend startup | <5s | 2-3s |
| Health check response | <100ms | 30-50ms |
| Single agent processing | <30s | 10-15s |
| Complete plan generation | <5min | 2-3min |
| PDF generation | <10s | 3-5s |
| Frontend page load | <3s | 1-2s |

---

## Next Steps

Once quickstart is complete:

1. **Read [AGENT_ARCHITECTURE.md](../../docs/AGENT_ARCHITECTURE.md)** to understand agent design
2. **Review [API_REFERENCE.md](../../docs/API_REFERENCE.md)** for endpoint documentation
3. **Explore [data-model.md](./data-model.md)** for entity schemas
4. **Practice [DEMO_SCRIPT.md](../../docs/DEMO_SCRIPT.md)** for hackathon presentation

---

## Support

- **Issues**: Open GitHub issue with `bug` label
- **Questions**: Use `question` label
- **Feature Requests**: Use `enhancement` label

**Happy Hacking!** 🚀
