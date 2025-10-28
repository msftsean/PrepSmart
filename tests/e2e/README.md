# PrepSmart E2E Tests - Playwright

Comprehensive end-to-end testing suite for PrepSmart multi-agent crisis preparedness system.

## 🎯 Test Coverage

### Test Scenarios

#### TS-001: Natural Disaster (Hurricane Miami)
**File**: `specs/01-natural-disaster-flow.spec.ts`
- Crisis mode selection
- Form validation and input
- Multi-agent orchestration
- Live log streaming
- Resource and video recommendations
- PDF generation and download
- Mobile responsiveness (320px-1280px)
- Performance (<180 seconds)

**Agents Tested**:
- 🎯 Coordinator Agent
- 🌪️ Risk Assessment Agent (natural disaster mode)
- 📦 Supply Planning Agent (emergency supplies)
- 🗺️ Resource Locator Agent (shelters, hospitals)
- 🎥 Video Curator Agent (hurricane prep videos)
- 📄 Documentation Agent (2-page PDF)

#### TS-003: Economic Crisis (Unemployment Austin)
**File**: `specs/02-economic-crisis-flow.spec.ts`
- Economic crisis form inputs
- Runtime question integration
- Financial advisor agent execution
- Economic plan structure validation
- Benefits eligibility analysis
- Hardship letter templates
- Budget enforcement ($50 strict limit)

**Agents Tested**:
- 🎯 Coordinator Agent
- 💰 Risk Assessment Agent (economic mode)
- 📊 Supply Planning Agent (food stockpiling)
- 💼 Financial Advisor Agent (30-day survival strategy)
- 🗺️ Resource Locator Agent (food banks, unemployment offices)
- 🎥 Video Curator Agent (economic crisis videos)
- 📄 Documentation Agent (2-page PDF)

## 📦 Installation

```bash
cd tests/e2e
npm install
npx playwright install
```

## 🚀 Running Tests

### All Tests
```bash
npm test
```

### Specific Scenarios
```bash
# Natural disaster flow only
npm run test:natural

# Economic crisis flow only
npm run test:economic
```

### Different Devices
```bash
# Mobile (320px - smallest viewport)
npm run test:mobile

# Tablet
npm run test:tablet

# Desktop (default)
npm test -- --project='Desktop Chrome'
```

### Debug Mode
```bash
# Interactive debugging
npm run test:debug

# UI mode (recommended)
npm run test:ui

# Headed mode (see browser)
npm run test:headed
```

## 📊 Test Reports

### Generate HTML Report
```bash
npm test
npm run report
```

### View Results
Open `playwright-report/index.html` in your browser.

## 🧪 Test Structure

### Configuration
`playwright.config.ts`:
- 5-minute timeout per test (plan generation takes 2-3 min)
- Screenshots on failure
- Video retention on failure
- Traces on first retry

### Projects (Viewports)
1. Desktop Chrome (1280x720)
2. iPhone 13 (390x844)
3. iPhone SE (320x568) - smallest mobile
4. iPhone 12 Pro (390x844)
5. iPad Pro (1024x1366)

### Test Files
```
tests/e2e/
├── playwright.config.ts       # Configuration
├── package.json                # Dependencies
├── specs/
│   ├── 01-natural-disaster-flow.spec.ts
│   └── 02-economic-crisis-flow.spec.ts
├── playwright-report/          # HTML reports (generated)
└── test-results/               # Screenshots, videos, traces
```

## ✅ Test Assertions

### Natural Disaster Tests
1. ✓ Homepage loads correctly
2. ✓ Crisis mode selection works
3. ✓ Form inputs validated (city, state, zip, household, budget)
4. ✓ Task ID created on submission
5. ✓ Live log streaming shows all 6 agents
6. ✓ All agents complete successfully
7. ✓ Risk assessment includes severity score and recommendations
8. ✓ Supply plan has tier-based items within budget
9. ✓ Resources found (sorted by distance)
10. ✓ Videos curated (5-7 videos, <5 min each)
11. ✓ PDF generated and downloadable (<5MB)
12. ✓ Mobile responsive at 320px
13. ✓ Touch targets ≥44px (iOS guideline)
14. ✓ Complete in <180 seconds

### Economic Crisis Tests
1. ✓ Economic mode selection
2. ✓ Runtime questions captured
3. ✓ Financial Advisor agent runs
4. ✓ Economic plan structure validated:
   - Financial summary
   - Expense categories (Must-Pay/Defer/Eliminate)
   - 30 daily actions
   - Benefits eligibility (unemployment, SNAP, Medicaid)
   - Hardship letter templates
   - Survival outlook (3 scenarios)
5. ✓ Economic resources found (food banks, unemployment offices, legal aid)
6. ✓ Economic videos curated (DOL, USDA sources)
7. ✓ Budget strictly enforced (never exceeds $50)

## 🎬 Example Test Run

```bash
$ npm test

Running 17 tests using 1 worker

  ✓ 01-natural-disaster-flow.spec.ts
    ✓ 01. Homepage loads correctly (1.2s)
    ✓ 02. Crisis mode selection - Natural Disaster (0.8s)
    ✓ 03. Form inputs - Hurricane Miami FL (2.1s)
    ✓ 04. Submit form and start plan generation (1.5s)
    ✓ 05. Live log streaming - Agent progress tracking (165.3s)
    ✓ 06. Agent completion - All agents succeed (142.7s)
    ✓ 07. Plan result - Retrieve complete plan (0.6s)
    ✓ 08. PDF download - Verify file download (1.9s)
    ✓ 09. Mobile responsiveness - 320px viewport (0.7s)
    ✓ 10. Performance - Plan generation <180 seconds (158.4s)

  ✓ 02-economic-crisis-flow.spec.ts
    ✓ 01. Crisis mode selection - Economic Crisis (0.9s)
    ✓ 02. Form inputs - Unemployment Austin TX (1.8s)
    ✓ 03. Submit and verify Financial Advisor agent runs (152.3s)
    ✓ 04. Verify economic plan structure (149.6s)
    ✓ 05. Verify economic-specific resources (148.2s)
    ✓ 06. Verify economic-specific videos (147.9s)
    ✓ 07. Budget enforcement - Never exceed $50 (146.8s)

  17 passed (1074.6s)
```

## 🔧 Prerequisites

### Backend Server
The Flask backend must be running:
```bash
cd backend
python src/api/app.py
# Server runs on http://localhost:5000
```

### Frontend Server
The frontend must be running:
```bash
cd frontend
npm run dev
# Server runs on http://localhost:3000
```

### Environment Variables
Create `.env` file in `tests/e2e/`:
```env
BASE_URL=http://localhost:3000
API_URL=http://localhost:5000
```

## 🐛 Debugging Tips

### View Test in Browser
```bash
npm run test:headed
```

### Step Through Test
```bash
npm run test:debug
```

### Generate Code
Record user actions to generate test code:
```bash
npm run codegen
```

### Check Logs
Logs are in `test-results/` directory:
- `*.log` - Console logs
- `trace.zip` - Playwright trace (upload to trace.playwright.dev)

## 📈 Performance Benchmarks

### Target Metrics
- Plan generation: <180 seconds (3 minutes)
- Page load: <3 seconds on 3G
- PDF size: <5MB (typically <500KB)
- Mobile responsiveness: 320px-428px

### Actual Results (Expected)
- Hurricane Miami: ~145-165 seconds
- Unemployment Austin: ~140-155 seconds
- PDF size: ~250-350KB
- All viewports: Fully responsive

## 🚨 Common Issues

### Test Timeout
**Problem**: Test exceeds 5-minute timeout
**Solution**: Check if backend agents are hanging. Review Claude API rate limits.

### PDF Not Found
**Problem**: PDF path exists in DB but file missing
**Solution**: Check `output/pdfs/` directory permissions. Verify ReportLab installed.

### Mobile Layout Issues
**Problem**: Elements cut off at 320px
**Solution**: Check CSS media queries in frontend. Verify `viewport` meta tag.

### Agent Failure
**Problem**: One or more agents fail during orchestration
**Solution**: Check backend logs for specific agent errors. Verify Claude API key.

## 📝 Writing New Tests

### Template
```typescript
import { test, expect } from '@playwright/test';

test.describe('My New Test Suite', () => {
  test('should do something', async ({ page }) => {
    await page.goto('/');
    // ... test logic
  });
});
```

### Best Practices
1. Use `data-testid` attributes for stable selectors
2. Wait for network idle before assertions
3. Use explicit waits (`waitForSelector`) over `waitForTimeout`
4. Clean up test data after each test
5. Use Page Object Model for complex flows

## 🤝 Contributing

When adding new tests:
1. Follow existing naming convention (`XX-feature-name.spec.ts`)
2. Update this README with new test coverage
3. Ensure tests pass locally before committing
4. Add meaningful assertions (not just "element exists")
5. Include console.log for key milestones

## 📄 License

MIT License - See LICENSE file for details
