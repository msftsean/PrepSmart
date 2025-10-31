const { test, expect } = require('@playwright/test');

test.describe('Message Ticker on Agent Progress Page', () => {
  test('should display inspirational messages ticker', async ({ page }) => {
    // Start a crisis assessment to get to agent progress page
    await page.goto('http://127.0.0.1:8080/index.html');

    console.log('📍 On homepage');

    // Click Economic Crisis
    await page.click('button:has-text("Economic Crisis")');
    await page.waitForTimeout(500);

    // Select Layoff
    await page.click('button:has-text("Layoff")');
    await page.waitForTimeout(500);

    // Click Next to location
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(500);

    console.log('📍 On location page');

    // Fill location
    await page.fill('input[placeholder*="City"]', 'Brooklyn');
    await page.fill('input[placeholder*="State"]', 'NY');
    await page.fill('input[placeholder*="ZIP"]', '11238');

    // Click Next to household
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(500);

    console.log('📍 On household page');

    // Fill household
    await page.fill('input[placeholder*="How many"]', '2');
    await page.click('button:has-text("House")'); // housing type
    await page.waitForTimeout(300);

    // Click Next to budget
    await page.click('button:has-text("Next")');
    await page.waitForTimeout(500);

    console.log('📍 On budget page');

    // Select $100 budget
    await page.click('button:has-text("$100")');
    await page.waitForTimeout(300);

    // Fill income
    await page.fill('input[placeholder*="annual income"]', '50000');
    await page.fill('input[placeholder*="Monthly expenses"]', '3000');
    await page.fill('input[placeholder*="Emergency fund"]', '2000');
    await page.fill('input[placeholder*="Monthly debt"]', '500');

    // Start assessment
    await page.click('button:has-text("Generate My Plan")');

    console.log('🚀 Started assessment, waiting for agent progress page...');

    // Wait for agent progress page
    await page.waitForURL('**/pages/agent-progress.html**', { timeout: 10000 });

    console.log('✅ On agent progress page');

    // Check if message ticker element exists and is visible
    const ticker = page.locator('.message-ticker');
    await expect(ticker).toBeVisible({ timeout: 5000 });

    console.log('✅ Message ticker is visible');

    // Check if ticker has content
    const tickerText = page.locator('#uplifting-message');
    await expect(tickerText).toBeVisible();

    // Get initial message
    const initialMessage = await tickerText.textContent();
    console.log(`📝 Initial message: "${initialMessage}"`);

    // Verify initial message is one of our expected messages
    expect(initialMessage).toContain('✨'); // All messages have emojis
    expect(initialMessage.length).toBeGreaterThan(20);

    // Wait 5 seconds and verify message changes
    console.log('⏳ Waiting 5 seconds for message to rotate...');
    await page.waitForTimeout(5000);

    const secondMessage = await tickerText.textContent();
    console.log(`📝 Second message: "${secondMessage}"`);

    // Verify message changed
    expect(secondMessage).not.toBe(initialMessage);
    expect(secondMessage.length).toBeGreaterThan(20);

    console.log('🎉 SUCCESS: Message ticker is working and rotating!');

    // Take screenshot
    await page.screenshot({ path: 'message-ticker-test.png', fullPage: true });
    console.log('📸 Screenshot saved: message-ticker-test.png');
  });

  test('should display message ticker with proper styling', async ({ page }) => {
    // Go directly to agent progress page with a task ID (mock)
    await page.goto('http://127.0.0.1:8080/pages/agent-progress.html?taskId=test-123');

    console.log('📍 On agent progress page (direct)');

    // Wait for ticker
    const ticker = page.locator('.message-ticker');
    await expect(ticker).toBeVisible({ timeout: 5000 });

    // Check CSS properties
    const bgColor = await ticker.evaluate(el => {
      return window.getComputedStyle(el).background;
    });

    console.log(`🎨 Background: ${bgColor}`);
    expect(bgColor).toContain('linear-gradient');

    // Check color is white
    const color = await ticker.evaluate(el => {
      return window.getComputedStyle(el).color;
    });

    console.log(`🎨 Text color: ${color}`);
    expect(color).toContain('rgb(255, 255, 255)'); // white

    // Check display is flex
    const display = await ticker.evaluate(el => {
      return window.getComputedStyle(el).display;
    });

    console.log(`🎨 Display: ${display}`);
    expect(display).toBe('flex');

    console.log('✅ Message ticker styling is correct!');
  });
});
