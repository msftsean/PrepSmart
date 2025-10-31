# PrepSmart Debugging Guide

**Last Updated**: October 31, 2025

This guide helps you troubleshoot issues with agent execution and view what each agent is producing.

---

## Quick Debugging Checklist

When results aren't showing up:

1. ✅ Check the debug viewer: `http://localhost:5000/debug-viewer`
2. ✅ Look at backend console logs for agent output
3. ✅ Query the debug API endpoint
4. ✅ Inspect the SQLite database directly

---

## Debug Tools Overview

### 1. Debug Viewer (Web UI)

**URL**: `http://localhost:5000/debug-viewer`

**Best for**: Visual inspection of agent results

**Features**:
- Real-time status monitoring (auto-refresh every 3 seconds)
- Color-coded agent cards (green = has data, red = no data)
- Complete JSON output for each agent
- Execution summary (time, cost, errors)
- Clickable task_id entry (paste URL or UUID)

**Usage**:
```bash
# Get a task_id from your app
# Example: After generating a crisis plan, check the URL or API response

# Visit debug viewer
open http://localhost:5000/debug-viewer

# Paste the task_id or full URL
# Click "Load Debug Data"
# Enable "Auto-Refresh" to watch live execution
```

**What to check**:
- Green cards = agent produced data ✅
- Red cards = agent didn't run or failed ❌
- Click any card to expand and see full JSON
- Check "Execution Summary" for errors

---

### 2. Debug API Endpoint

**URL**: `GET /api/crisis/{task_id}/debug`

**Best for**: Programmatic access, scripting, CI/CD

**Response Structure**:
```json
{
  "task_id": "...",
  "status": "completed|processing|failed",
  "execution_summary": {
    "status": "completed",
    "execution_start": "2025-10-31T12:00:00",
    "execution_end": "2025-10-31T12:02:15",
    "total_execution_seconds": 135.5,
    "total_tokens_used": 15420,
    "total_cost_estimate": 0.0732,
    "agents_completed": ["RiskAssessmentAgent", "SupplyPlanningAgent", ...],
    "agents_failed": [],
    "errors": []
  },
  "agent_logs": [
    {
      "agent_name": "RiskAssessmentAgent",
      "status": "completed",
      "progress_percentage": 100,
      "started_at": "...",
      "completed_at": "..."
    }
  ],
  "agent_results": {
    "risk_assessment": { ... },
    "supply_plan": { ... },
    "economic_plan": { ... },
    "resource_locations": [ ... ],
    "video_recommendations": [ ... ],
    "complete_plan": { ... }
  },
  "crisis_profile": { ... }
}
```

**Usage**:
```bash
# Get debug data for a task
curl http://localhost:5000/api/crisis/{task_id}/debug | python -m json.tool

# Save to file
curl http://localhost:5000/api/crisis/{task_id}/debug > debug_output.json

# Check if specific agent has data
curl -s http://localhost:5000/api/crisis/{task_id}/debug | jq '.agent_results.supply_plan'

# Check which agents completed
curl -s http://localhost:5000/api/crisis/{task_id}/debug | jq '.execution_summary.agents_completed'
```

**What to check**:
- `agent_results` - null values indicate missing agent output
- `agents_completed` - list should have all expected agents
- `agents_failed` - should be empty
- `errors` - array of error objects

---

### 3. Console Logging

**Location**: Backend terminal output

**Best for**: Real-time debugging during development

**Format**:
```
================================================================================
🌪️ RiskAssessmentAgent COMPLETE OUTPUT (task_id=abc123)
================================================================================
Result Data:
{
  "overall_risk_level": "EXTREME",
  "primary_threat": { ... },
  "recommendations": [ ... ]
}
================================================================================
```

**What agents log**:
- ✅ Risk Assessment Agent
- ✅ Supply Planning Agent
- ✅ Financial Advisor Agent
- ✅ Resource Locator Agent
- ✅ Video Curator Agent
- ✅ Documentation Agent

**How to view**:
```bash
# Start backend in foreground (logs to console)
cd backend && python -m src.api.app

# Or tail logs if running in background
tail -f /tmp/backend.log

# Search for specific agent
grep "SupplyPlanningAgent COMPLETE OUTPUT" /tmp/backend.log
```

---

### 4. Database Inspection

**Location**: `backend/prepsmart.db`

**Best for**: Deep inspection, SQL queries, data validation

**Tables**:
- `crisis_profiles` - User input data
- `blackboards` - Agent results and coordination state
- `agent_logs` - Agent execution timeline

**Useful Queries**:

```bash
# Open database
sqlite3 backend/prepsmart.db

# View all tasks
SELECT task_id, status, created_at FROM blackboards ORDER BY created_at DESC LIMIT 10;

# Check specific task
SELECT task_id, status, agents_completed_json, agents_failed_json
FROM blackboards
WHERE task_id = 'YOUR_TASK_ID';

# View agent logs for a task
SELECT agent_name, status, current_task_description, started_at, completed_at
FROM agent_logs
WHERE task_id = 'YOUR_TASK_ID'
ORDER BY started_at;

# Find tasks with missing supply plans
SELECT task_id, status FROM blackboards WHERE supply_plan_json IS NULL;

# Find failed tasks
SELECT task_id, status, agents_failed_json FROM blackboards WHERE status = 'failed';

# Check agent completion rate
SELECT
  json_array_length(agents_completed_json) as completed_count,
  COUNT(*) as task_count
FROM blackboards
GROUP BY json_array_length(agents_completed_json);
```

---

## Common Issues & Solutions

### Issue 1: No results showing on summary page

**Symptoms**:
- Results page loads but shows "No plan data"
- Some sections are empty
- Economic plan missing for economic crisis mode

**Debug Steps**:

1. Get the task_id from the URL or network tab
2. Check debug viewer: `http://localhost:5000/debug-viewer?task_id={task_id}`
3. Look at `agent_results` - which fields are null?
4. Check `agents_completed` list - which agents finished?
5. Review backend console logs for errors

**Common Causes**:
- Agent timed out (default: 120 seconds)
- Claude API rate limit hit
- JSON parsing error in agent response
- Agent dependency not met (e.g., Financial Advisor needs Risk Assessment first)

**Solutions**:
```bash
# Increase agent timeout
# Edit backend/src/agents/coordinator_agent.py
self.agent_timeout = 180  # Change from 120 to 180

# Check Claude API key
grep CLAUDE_API_KEY backend/.env

# Retry the task with a new submission
```

---

### Issue 2: Agents stuck in "processing" state

**Symptoms**:
- Status endpoint shows `"status": "processing"`
- Same agents in `agents_completed` for minutes
- Agent dashboard shows no progress

**Debug Steps**:

1. Check database status:
   ```bash
   sqlite3 backend/prepsmart.db "SELECT status, agents_completed_json FROM blackboards WHERE task_id = 'YOUR_TASK_ID';"
   ```

2. Check for orphaned background threads:
   ```bash
   ps aux | grep python | grep app.py
   ```

3. Look for errors in console:
   ```bash
   grep -i "error\|exception\|failed" /tmp/backend.log | tail -20
   ```

**Common Causes**:
- Background thread crashed silently
- Database lock (SQLite limitation)
- Infinite loop in orchestration
- Agent dependency deadlock

**Solutions**:
```bash
# Restart backend
pkill -f "python.*app.py"
cd backend && python -m src.api.app

# Force mark task as failed (manual database edit)
sqlite3 backend/prepsmart.db "UPDATE blackboards SET status='failed' WHERE task_id='YOUR_TASK_ID';"

# Create a new task
```

---

### Issue 3: Supply plan is empty (null)

**Symptoms**:
- Debug viewer shows `supply_plan: null`
- `SupplyPlanningAgent` not in `agents_completed`
- No supply items in results page

**Debug Steps**:

1. Check if Risk Assessment Agent completed first:
   ```bash
   curl -s http://localhost:5000/api/crisis/{task_id}/debug | jq '.execution_summary.agents_completed'
   ```

2. Look for SupplyPlanningAgent logs:
   ```bash
   grep "SupplyPlanningAgent" /tmp/backend.log | tail -20
   ```

3. Check for JSON parsing errors:
   ```bash
   grep "Could not parse.*supply" /tmp/backend.log
   ```

**Common Causes**:
- Risk Assessment Agent failed (dependency not met)
- Claude API returned malformed JSON
- Budget tier validation failed
- Agent timeout before completion

**Solutions**:
```bash
# Check risk assessment completed
curl -s http://localhost:5000/api/crisis/{task_id}/debug | jq '.agent_results.risk_assessment'

# Verify budget_tier is valid (50, 100, or 200 for natural disaster)
sqlite3 backend/prepsmart.db "SELECT budget_tier FROM crisis_profiles WHERE task_id='YOUR_TASK_ID';"

# Increase timeout for slow Claude responses
# Edit coordinator_agent.py: self.agent_timeout = 180
```

---

### Issue 4: Economic plan missing for economic crisis

**Symptoms**:
- Crisis mode is "economic_crisis"
- Debug viewer shows `economic_plan: null`
- Financial dashboard shows no data

**Debug Steps**:

1. Verify crisis mode:
   ```bash
   curl -s http://localhost:5000/api/crisis/{task_id}/debug | jq '.crisis_profile.crisis_mode'
   ```

2. Check if Financial Advisor Agent ran:
   ```bash
   curl -s http://localhost:5000/api/crisis/{task_id}/debug | jq '.execution_summary.agents_completed | contains(["FinancialAdvisorAgent"])'
   ```

3. Look for Financial Advisor logs:
   ```bash
   grep "FinancialAdvisorAgent" /tmp/backend.log | tail -30
   ```

**Common Causes**:
- Financial Advisor Agent only runs for economic_crisis mode
- Risk Assessment dependency not met
- JSON parsing error in Claude response
- Timeout (Financial Advisor uses Sonnet, which is slower)

**Solutions**:
```bash
# Verify mode is economic_crisis
sqlite3 backend/prepsmart.db "SELECT crisis_mode FROM crisis_profiles WHERE task_id='YOUR_TASK_ID';"

# Check budget_tier is set (can be any value for economic_crisis)
sqlite3 backend/prepsmart.db "SELECT budget_tier FROM crisis_profiles WHERE task_id='YOUR_TASK_ID';"

# Increase timeout for Financial Advisor (uses Claude Sonnet 3.5)
# Already set to 120s in coordinator_agent.py
```

---

## Performance Debugging

### Check Agent Execution Times

```bash
# SQL query for agent performance
sqlite3 backend/prepsmart.db <<EOF
SELECT
  agent_name,
  AVG(execution_time_seconds) as avg_time,
  MIN(execution_time_seconds) as min_time,
  MAX(execution_time_seconds) as max_time,
  COUNT(*) as executions
FROM agent_logs
WHERE status = 'completed'
GROUP BY agent_name;
EOF
```

### Check Claude API Costs

```bash
# Total cost across all tasks
sqlite3 backend/prepsmart.db "SELECT SUM(total_cost_estimate) as total_cost FROM blackboards;"

# Cost per task
sqlite3 backend/prepsmart.db "SELECT task_id, total_cost_estimate, total_tokens_used FROM blackboards ORDER BY total_cost_estimate DESC LIMIT 10;"

# Cost by agent (approximate from logs)
curl -s http://localhost:5000/api/crisis/{task_id}/debug | jq '.agent_results | to_entries[] | select(.value != null) | {agent: .key, cost: .value.cost_estimate, tokens: .value.tokens_used}'
```

### Monitor Real-Time Execution

```bash
# Watch backend logs in real-time
tail -f /tmp/backend.log | grep -E "Agent starting|Agent completed|COMPLETE OUTPUT"

# Monitor database updates
watch -n 2 "sqlite3 backend/prepsmart.db 'SELECT task_id, status, json_array_length(agents_completed_json) as completed FROM blackboards ORDER BY updated_at DESC LIMIT 5;'"
```

---

## Advanced Debugging

### Enable Detailed Logging

Edit `backend/src/utils/logger.py` or set environment variable:

```bash
export LOG_LEVEL=DEBUG
python -m src.api.app
```

### Trace Agent Execution

Add breakpoints or logging to agents:

```python
# In any agent file (e.g., financial_advisor_agent.py)
import pdb; pdb.set_trace()  # Add breakpoint

# Or add custom logging
logger.debug(f"Prompt sent to Claude: {prompt[:200]}...")
logger.debug(f"Claude response received: {response[:200]}...")
```

### Test Individual Agents

```python
# backend/test_agent.py
import asyncio
from src.agents.financial_advisor_agent import FinancialAdvisorAgent
from src.services.claude_client import ClaudeClient
from src.models.blackboard import Blackboard

async def test_financial_advisor():
    client = ClaudeClient()
    agent = FinancialAdvisorAgent(client)

    # Create test blackboard
    blackboard = Blackboard(
        task_id="test-123",
        crisis_profile={
            "crisis_mode": "economic_crisis",
            "specific_threat": "layoff",
            "household": {"adults": 2, "children": 1},
            "budget_tier": 500
        },
        risk_assessment={
            "overall_risk_level": "HIGH",
            "financial_runway": "30 days"
        }
    )

    # Run agent
    result = await agent.process(blackboard)
    print(result.economic_plan)

# Run test
asyncio.run(test_financial_advisor())
```

---

## Getting Help

If you're still stuck:

1. Check the [README.md](README.md) for setup instructions
2. Review [spec.md](.specify/specs/001-prepsmart-mvp/spec.md) for expected behavior
3. Open an issue with:
   - Task ID
   - Expected behavior
   - Actual behavior
   - Debug API output
   - Console logs

---

**Happy Debugging!** 🐛🔍
