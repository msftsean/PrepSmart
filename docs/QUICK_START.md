# PrepSmart - Quick Start Guide

**🚀 Get running in 2 minutes**

---

## Start the App

```bash
# Terminal 1: Backend
cd /workspaces/prepsmart/backend
python -m src.api.app

# Terminal 2: Frontend
cd /workspaces/prepsmart/frontend
python -m http.server 8000
```

**Open browser**: `http://localhost:8000`

---

## Test the App

### Natural Disaster Test
1. Select "Natural Disaster - Hurricane"
2. Enter ZIP: `33139` (Miami Beach, FL)
3. Household: 2 adults, 1 child
4. Budget: $100
5. Wait ~90 seconds
6. Download PDF

### Economic Crisis Test
1. Select "Economic Crisis - Layoff"
2. Location: Washington, DC
3. Household: 2 adults, 1 child
4. Savings: $800
5. Wait ~90 seconds
6. View financial survival plan

---

## Debug Tools

**Web Viewer**: `http://localhost:5000/debug-viewer`
- Paste any task_id
- See all agent results
- Enable auto-refresh to watch live

**API**: `http://localhost:5000/api/crisis/{task_id}/debug`
- Returns complete JSON
- Shows which agents completed
- Includes error messages

**Logs**: `tail -f /tmp/backend.log | grep "COMPLETE OUTPUT"`

---

## Sample Task IDs (Already Complete)

**Natural Disaster**: `80ac4e0a-0363-4d9d-b518-49c1d79c6e92`
**Economic Crisis**: `d08ea197-f33d-4f10-a781-98ec6e4390e0`

Use these in debug viewer to see successful results.

---

## Common Issues

**Backend won't start**:
```bash
# Check if Claude API key is set
grep CLAUDE_API_KEY backend/.env

# Kill any existing processes
pkill -f "python.*app.py"
```

**No results showing**:
1. Get task_id from URL
2. Check debug viewer: `http://localhost:5000/debug-viewer`
3. Look for null values in agent_results
4. Check backend logs for errors

**Agents stuck**:
- Wait 2 minutes (agents have 120s timeout)
- Check backend console for errors
- Create new task if needed

---

## Key Architecture

**6 AI Agents**:
1. Risk Assessment Agent - Analyzes threats
2. Supply Planning Agent - Creates shopping lists
3. Financial Advisor Agent - 30-day survival plan (economic only)
4. Resource Locator Agent - Finds shelters, food banks
5. Video Curator Agent - Educational videos
6. Documentation Agent - Generates PDF

**Coordination**: Blackboard Pattern
- All agents read/write to shared state
- Coordinator orchestrates execution
- Parallel execution when possible

**APIs Used**:
- Claude 3.5 Sonnet (complex reasoning)
- Claude 3.5 Haiku (simple tasks)

---

## File Structure

```
/workspaces/prepsmart/
├── backend/
│   ├── src/
│   │   ├── agents/          # 6 AI agents
│   │   ├── api/             # Flask routes
│   │   ├── models/          # Data schemas
│   │   └── services/        # Claude client, blackboard
│   ├── prepsmart.db         # SQLite database
│   └── debug_viewer.html    # Debug UI
├── frontend/
│   ├── index.html           # Landing page
│   └── pages/               # Crisis select, questionnaire, results
├── README.md                # Full documentation
├── DEBUGGING.md             # Troubleshooting guide
└── SUBMISSION_READY.md      # Submission checklist
```

---

## Documentation

- **Full README**: [README.md](README.md)
- **Debug Guide**: [DEBUGGING.md](DEBUGGING.md)
- **Submission Checklist**: [SUBMISSION_READY.md](SUBMISSION_READY.md)
- **Spec Document**: `.specify/specs/001-prepsmart-mvp/spec.md`

---

## Demo in 30 Seconds

1. Open `http://localhost:8000`
2. Click "Economic Crisis - Layoff"
3. Fill form (any values)
4. Watch agents on dashboard
5. View results with financial plan
6. Show debug viewer
7. Download PDF

**Done!** ✅

---

**For questions, check [DEBUGGING.md](DEBUGGING.md) or [README.md](README.md)**
