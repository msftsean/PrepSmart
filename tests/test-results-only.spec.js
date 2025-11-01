const { test, expect } = require('@playwright/test');

test('Check results page display', async ({ page }) => {
  const BACKEND_URL = 'https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io';
  const FRONTEND_URL = 'https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io';
  const TASK_ID = 'b7bb6af3-52e7-44e4-944e-3eb21555d0b6'; // Known working task

  console.log('Setting task ID in session storage...');
  await page.goto(`${FRONTEND_URL}/pages/plan-results.html`);

  // Set task ID in sessionStorage
  await page.evaluate((taskId) => {
    sessionStorage.setItem('task_id', taskId);
  }, TASK_ID);

  // Reload page to load data
  await page.reload();
  await page.waitForTimeout(3000);

  console.log('\n=== Checking results page content ===');

  // Get all text content
  const bodyText = await page.textContent('body');
  console.log('\nPage contains:');
  console.log(`- "Risk Assessment": ${bodyText.includes('Risk Assessment') ? '✅' : '❌'}`);
  console.log(`- "Supply Plan": ${bodyText.includes('Supply Plan') || bodyText.includes('Supply') ? '✅' : '❌'}`);
  console.log(`- "Economic": ${bodyText.includes('Economic') || bodyText.includes('Financial') ? '✅' : '❌'}`);
  console.log(`- "Daily Actions": ${bodyText.includes('Daily Actions') || bodyText.includes('Action') ? '✅' : '❌'}`);
  console.log(`- "Benefits": ${bodyText.includes('Benefits') || bodyText.includes('benefit') ? '✅' : '❌'}`);

  // Check if sections are visible or collapsed
  const sections = await page.locator('.section-card').count();
  console.log(`\nTotal sections found: ${sections}`);

  // Check if there's any data loaded
  const hasContent = await page.locator('p, ul, li').count();
  console.log(`Content elements (p, ul, li): ${hasContent}`);

  // Take screenshot
  await page.screenshot({ path: 'results-page-debug.png', fullPage: true });
  console.log('\n📸 Screenshot saved to results-page-debug.png');

  // Check for error messages
  const errorMsg = await page.locator('text=error').count();
  console.log(`Error messages: ${errorMsg > 0 ? '❌ FOUND' : '✅ None'}`);

  // Log the HTML structure
  const mainContent = await page.locator('main').innerHTML();
  console.log('\n=== Main content structure ===');
  console.log(mainContent.substring(0, 500) + '...');
});
