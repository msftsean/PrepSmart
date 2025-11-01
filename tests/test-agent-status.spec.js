const { test, expect } = require('@playwright/test');

test('Watch agent status updates in real-time', async ({ page }) => {
  const BACKEND_URL = 'https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io';
  const FRONTEND_URL = 'https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io';

  console.log('Starting new economic crisis plan...');

  // Start a new plan
  const response = await page.request.post(`${BACKEND_URL}/api/crisis/start`, {
    data: {
      crisis_mode: 'economic_crisis',
      specific_threat: 'unemployment',
      location: { city: 'Seattle', state: 'WA', zip_code: '98101' },
      household: { adults: 2, children: 1, pets: 0 },
      housing_type: 'apartment',
      budget_tier: 0,
      financial_situation: {
        current_income: 0,
        monthly_expenses: 4500,
        available_savings: 2000,
        debt_obligations: 15000
      }
    }
  });

  const result = await response.json();
  const TASK_ID = result.task_id;
  console.log(`Task ID: ${TASK_ID}`);

  // Navigate to agent progress page
  await page.goto(`${FRONTEND_URL}/pages/agent-progress.html`);
  await page.evaluate((taskId) => {
    sessionStorage.setItem('task_id', taskId);
  }, TASK_ID);
  await page.reload();

  console.log('\n=== Watching for agent updates (20 seconds) ===');

  // Check status every 2 seconds for 20 seconds
  for (let i = 0; i < 10; i++) {
    await page.waitForTimeout(2000);

    // Get all agent descriptions
    const agents = await page.locator('.agent-card').evaluateAll(cards => {
      return cards.map(card => {
        const name = card.querySelector('.agent-name')?.textContent || 'Unknown';
        const status = card.querySelector('.status-text')?.textContent || 'Unknown';
        const description = card.querySelector('.agent-description')?.textContent || '';
        const progress = card.querySelector('.agent-progress')?.textContent || '';

        return { name, status, description, progress };
      });
    });

    console.log(`\n--- Check ${i + 1} (${(i+1)*2}s) ---`);
    agents.forEach(agent => {
      const desc = agent.description.substring(0, 60);
      console.log(`${agent.name}: ${agent.status} | ${desc}${desc.length >= 60 ? '...' : ''} | ${agent.progress}`);
    });
  }

  await page.screenshot({ path: 'agent-status-screenshot.png', fullPage: true });
  console.log('\n📸 Screenshot saved');
});
