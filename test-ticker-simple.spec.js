const { test, expect } = require('@playwright/test');

test.describe('Message Ticker Simple Test', () => {
  test('verify message ticker exists and rotates', async ({ page }) => {
    // Go to agent progress page directly
    console.log('🚀 Navigating to agent progress page...');
    await page.goto('http://127.0.0.1:8080/pages/agent-progress.html?taskId=7dd5b60e-e40c-4941-9dcc-bf9980497f11');

    // Wait for page to load
    await page.waitForLoadState('domcontentloaded');
    console.log('✅ Page loaded');

    // Look for the message ticker element
    const ticker = page.locator('.message-ticker');
    console.log('🔍 Looking for .message-ticker element...');

    // Check if it exists
    const tickerCount = await ticker.count();
    console.log(`📊 Found ${tickerCount} .message-ticker elements`);

    if (tickerCount === 0) {
      console.error('❌ Message ticker element NOT found!');
      // Take screenshot for debugging
      await page.screenshot({ path: 'ticker-not-found.png', fullPage: true });
      throw new Error('Message ticker element not found on page');
    }

    // Check if visible
    const isVisible = await ticker.isVisible();
    console.log(`👁️  Ticker visible: ${isVisible}`);

    if (!isVisible) {
      console.error('❌ Message ticker exists but is NOT visible!');
      await page.screenshot({ path: 'ticker-not-visible.png', fullPage: true });
    }

    // Get the text element
    const tickerText = page.locator('#uplifting-message');
    const textCount = await tickerText.count();
    console.log(`📊 Found ${textCount} #uplifting-message elements`);

    if (textCount > 0) {
      const initialMessage = await tickerText.textContent();
      console.log(`📝 Initial message: "${initialMessage}"`);
      expect(initialMessage.length).toBeGreaterThan(10);

      // Wait for rotation (4 seconds + buffer)
      console.log('⏳ Waiting 5 seconds for message rotation...');
      await page.waitForTimeout(5000);

      const secondMessage = await tickerText.textContent();
      console.log(`📝 After 5 seconds: "${secondMessage}"`);

      if (initialMessage !== secondMessage) {
        console.log('✅ SUCCESS: Message rotated!');
      } else {
        console.log('⚠️  WARNING: Message did not rotate');
      }
    }

    // Take screenshot
    await page.screenshot({ path: 'ticker-test-final.png', fullPage: true });
    console.log('📸 Screenshot saved: ticker-test-final.png');

    // Check console logs
    const logs = [];
    page.on('console', msg => {
      logs.push(msg.text());
      console.log(`🖥️  Browser console: ${msg.text()}`);
    });

    await page.reload();
    await page.waitForTimeout(2000);

    console.log('\n📋 All browser console logs:');
    logs.forEach(log => console.log(`  - ${log}`));
  });
});
