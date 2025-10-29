const { test, expect } = require('@playwright/test');

test('Economic crisis questionnaire flow', async ({ page }) => {
  // Navigate directly to economic crisis selection
  await page.goto('https://prepsmart-frontend.politegrass-4005e0e6.eastus.azurecontainerapps.io/pages/crisis-select.html?mode=economic');

  // Select a crisis type from dropdown
  await page.selectOption('select', 'unemployment');

  // Click Continue button
  await page.getByRole('button', { name: /continue/i }).click();

  // Should now be on questionnaire page
  await expect(page).toHaveURL(/questionnaire/i);

  console.log('Step 1: Location');

  // Fill Step 1: Location
  await page.fill('#zip-code', '10001');
  await page.fill('#city', 'New York');
  await page.selectOption('#state', 'NY');

  // Click Next
  await page.getByRole('button', { name: /next step/i }).click();

  console.log('Step 2: Household');

  // Fill Step 2: Household
  await page.fill('#adults', '2');
  await page.fill('#children', '1');
  await page.fill('#pets', '0');

  // Select housing type
  await page.getByLabel(/apartment/i).check();

  // Click Next
  await page.getByRole('button', { name: /next step/i }).click();

  console.log('Step 3: Financial Situation');

  // Wait for step 3 to be visible
  await page.waitForSelector('#current-income', { state: 'visible' });

  // Fill Step 3: Financial Situation
  await page.fill('#current-income', '0');
  await page.fill('#monthly-expenses', '7000');
  await page.fill('#available-savings', '100');
  await page.fill('#debt-obligations', '13000');

  // Take a screenshot before clicking Next
  await page.screenshot({ path: 'before-next-step.png', fullPage: true });

  console.log('Filled all fields:');
  console.log('  Current Income:', await page.inputValue('#current-income'));
  console.log('  Monthly Expenses:', await page.inputValue('#monthly-expenses'));
  console.log('  Available Savings:', await page.inputValue('#available-savings'));
  console.log('  Debt Obligations:', await page.inputValue('#debt-obligations'));

  // Try to click Next
  const nextButton = page.getByRole('button', { name: /next step/i });

  // Listen for any alerts
  page.on('dialog', async dialog => {
    console.log('Alert detected:', dialog.message());
    await dialog.accept();
  });

  console.log('Clicking Next Step button...');
  await nextButton.click();

  // Wait a moment to see if alert appears
  await page.waitForTimeout(2000);

  // Take screenshot after clicking
  await page.screenshot({ path: 'after-next-step.png', fullPage: true });

  // Check if we made it to step 4
  const step4Visible = await page.locator('[data-step="4"]').isVisible();
  console.log('Step 4 visible:', step4Visible);

  if (!step4Visible) {
    console.error('❌ Failed to proceed to Step 4');

    // Check for validation errors
    const errorFields = await page.locator('.error').count();
    console.log('Fields with error class:', errorFields);

    // Get all required fields and their values
    const requiredFields = await page.locator('[required]').all();
    for (const field of requiredFields) {
      const id = await field.getAttribute('id');
      const value = await field.inputValue();
      const isVisible = await field.isVisible();
      console.log(`Field ${id}: value="${value}", visible=${isVisible}`);
    }
  } else {
    console.log('✅ Successfully advanced to Step 4');
  }
});
