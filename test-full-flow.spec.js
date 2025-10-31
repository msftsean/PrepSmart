const { test, expect } = require('@playwright/test');

test('Complete economic crisis flow - form to results', async ({ page }) => {
  const BACKEND_URL = process.env.BACKEND_URL || 'https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io';
  const FRONTEND_URL = process.env.FRONTEND_URL || 'https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io';

  console.log(`Testing against: ${FRONTEND_URL}`);

  // Navigate to questionnaire
  await page.goto(`${FRONTEND_URL}/pages/questionnaire.html`);
  await page.waitForSelector('#crisis-mode-toggle');

  // Step 1: Crisis Selection
  console.log('Step 1: Crisis Selection');
  await page.click('#crisis-mode-toggle');
  await page.waitForTimeout(500);
  await page.selectOption('#crisis-type', 'unemployment');
  await page.click('button:has-text("Next Step")');
  await page.waitForTimeout(500);

  // Step 2: Location
  console.log('Step 2: Location');
  await page.fill('#city', 'Seattle');
  await page.fill('#state', 'WA');
  await page.fill('#zip-code', '98101');
  await page.click('button:has-text("Next Step")');
  await page.waitForTimeout(500);

  // Step 3: Household
  console.log('Step 3: Household');
  await page.fill('#num-adults', '2');
  await page.fill('#num-children', '1');
  await page.fill('#num-pets', '0');
  await page.selectOption('#housing-type', 'apartment');
  await page.click('button:has-text("Next Step")');
  await page.waitForTimeout(500);

  // Step 4: Financial Situation
  console.log('Step 4: Financial Situation');
  await page.fill('#current-income', '0');
  await page.fill('#monthly-expenses', '4500');
  await page.fill('#available-savings', '2000');
  await page.fill('#debt-obligations', '15000');
  await page.selectOption('#primary-concern', 'rent');
  await page.selectOption('#time-horizon', '30');

  // Submit form
  console.log('Submitting form...');
  await page.click('button:has-text("Generate Plan")');

  // Wait for redirect to agent dashboard
  console.log('Waiting for agent dashboard...');
  await page.waitForURL(/agent-dashboard\.html/, { timeout: 10000 });
  console.log('✅ Redirected to agent dashboard');

  // Check if agent cards are displayed
  const agentCards = await page.locator('.agent-card').count();
  console.log(`Agent cards displayed: ${agentCards}`);
  expect(agentCards).toBeGreaterThan(0);

  // Wait for agents to start showing activity
  await page.waitForTimeout(5000);

  // Check for chain-of-thought updates
  console.log('\n=== Checking for chain-of-thought ===');
  const descriptions = await page.locator('.agent-description').allTextContents();
  console.log('Agent descriptions:');
  descriptions.forEach((desc, i) => {
    console.log(`  Agent ${i + 1}: "${desc}"`);
  });

  // Wait for completion (max 2 minutes)
  console.log('\nWaiting for plan completion...');
  try {
    await page.waitForSelector('#completion-message', { timeout: 120000 });
    console.log('✅ Plan generation completed');
  } catch (e) {
    console.log('⏰ Timeout waiting for completion');
    const currentStatus = await page.textContent('.page-header h1');
    console.log(`Current status: ${currentStatus}`);
  }

  // Click View Results
  console.log('\nClicking View Results...');
  await page.click('button:has-text("View Results")');
  await page.waitForURL(/plan-results\.html/, { timeout: 10000 });
  console.log('✅ Redirected to results page');

  // Check results content
  console.log('\n=== Checking results content ===');

  // Check for risk assessment
  const riskSection = await page.locator('text=Risk Assessment').count();
  console.log(`Risk Assessment section: ${riskSection > 0 ? '✅ Found' : '❌ Missing'}`);

  // Check for supply plan
  const supplySection = await page.locator('text=Supply Plan').count();
  console.log(`Supply Plan section: ${supplySection > 0 ? '✅ Found' : '❌ Missing'}`);

  // Check for economic plan
  const economicSection = await page.locator('text=Economic Survival').count();
  console.log(`Economic Plan section: ${economicSection > 0 ? '✅ Found' : '❌ Missing'}`);

  // Check if daily actions are present
  const dailyActions = await page.locator('text=Daily Actions').count();
  console.log(`Daily Actions: ${dailyActions > 0 ? '✅ Found' : '❌ Missing'}`);

  // Check if benefits are present
  const benefits = await page.locator('text=Benefits').count();
  console.log(`Benefits section: ${benefits > 0 ? '✅ Found' : '❌ Missing'}`);

  // Take screenshot for review
  await page.screenshot({ path: 'test-results-page.png', fullPage: true });
  console.log('\n📸 Screenshot saved to test-results-page.png');
});
