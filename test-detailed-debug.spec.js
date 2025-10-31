const { test, expect } = require('@playwright/test');

test('Detailed debugging of results page', async ({ page }) => {
  const BACKEND_URL = 'https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io';
  const FRONTEND_URL = 'https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io';
  const TASK_ID = 'b7bb6af3-52e7-44e4-944e-3eb21555d0b6';

  // Listen for console messages
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`❌ Browser Error: ${msg.text()}`);
    } else if (msg.type() === 'log') {
      console.log(`📝 Browser Log: ${msg.text()}`);
    }
  });

  // Listen for page errors
  page.on('pageerror', error => {
    console.log(`❌ Page Error: ${error.message}`);
  });

  console.log('Loading results page...');
  await page.goto(`${FRONTEND_URL}/pages/plan-results.html`);

  // Set task ID
  await page.evaluate((taskId) => {
    sessionStorage.setItem('task_id', taskId);
  }, TASK_ID);

  // Reload to trigger data load
  await page.reload();
  await page.waitForTimeout(5000);

  // Check if data was loaded
  const planData = await page.evaluate(() => {
    return window.planData;
  });

  console.log('\n=== Plan Data Status ===');
  if (planData) {
    console.log('✅ planData loaded');
    console.log(`- Has risk_assessment: ${planData.risk_assessment ? '✅' : '❌'}`);
    console.log(`- Has supply_plan: ${planData.supply_plan ? '✅' : '❌'}`);
    console.log(`- Has economic_plan: ${planData.economic_plan ? '✅' : '❌'}`);
    console.log(`- Has resource_locations: ${planData.resource_locations ? '✅' : '❌'}`);
    console.log(`- Has video_recommendations: ${planData.video_recommendations ? '✅' : '❌'}`);

    if (planData.economic_plan) {
      console.log('\n=== Economic Plan Details ===');
      console.log(`- Daily actions: ${planData.economic_plan.daily_actions?.length || 0}`);
      console.log(`- Eligible benefits: ${planData.economic_plan.eligible_benefits?.length || 0}`);
      console.log(`- Hardship letters: ${planData.economic_plan.hardship_letters?.length || 0}`);
    }
  } else {
    console.log('❌ planData is NULL');
  }

  // Check visible sections
  console.log('\n=== Visible Sections ===');
  const riskVisible = await page.locator('#risk-section').isVisible();
  const supplyVisible = await page.locator('#supply-section').isVisible();
  const economicVisible = await page.locator('#economic-section').isVisible();

  console.log(`- Risk Assessment: ${riskVisible ? '✅ Visible' : '❌ Hidden'}`);
  console.log(`- Supply Plan: ${supplyVisible ? '✅ Visible' : '❌ Hidden'}`);
  console.log(`- Economic Plan: ${economicVisible ? '✅ Visible' : '❌ Hidden'}`);

  // Check for actual content
  console.log('\n=== Content Check ===');
  if (economicVisible) {
    const economicContent = await page.locator('#economic-content').textContent();
    const contentLength = economicContent.trim().length;
    console.log(`Economic section content length: ${contentLength} characters`);

    if (contentLength > 0) {
      console.log('✅ Economic section has content');
      // Show first 200 chars
      console.log('Preview:', economicContent.substring(0, 200) + '...');
    } else {
      console.log('❌ Economic section is EMPTY');
    }
  }

  // Take screenshot
  await page.screenshot({ path: 'detailed-debug.png', fullPage: true });
  console.log('\n📸 Screenshot saved to detailed-debug.png');
});
