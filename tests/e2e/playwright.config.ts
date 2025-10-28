/**
 * Playwright configuration for PrepSmart E2E tests
 *
 * Test scenarios:
 * 1. Natural disaster crisis plan generation (Hurricane Miami)
 * 2. Economic crisis plan generation (Unemployment Austin)
 * 3. Live log streaming and agent progress tracking
 * 4. PDF generation and download
 * 5. Mobile responsiveness (320px, 375px, 428px viewports)
 * 6. Error handling and validation
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './specs',

  // Test execution settings
  fullyParallel: false, // Run tests sequentially to avoid API conflicts
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : 1,

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list'],
    ['junit', { outputFile: 'test-results/junit.xml' }]
  ],

  // Global timeout settings
  timeout: 5 * 60 * 1000, // 5 minutes per test (plan generation can take up to 3 min)
  expect: {
    timeout: 30 * 1000, // 30 seconds for expect assertions
  },

  use: {
    // Base URL for tests
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // API URL for backend
    apiURL: process.env.API_URL || 'http://localhost:5000',

    // Trace settings
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',

    // Browser settings
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,

    // Action settings
    actionTimeout: 15 * 1000, // 15 seconds for actions
  },

  // Test projects for different scenarios
  projects: [
    {
      name: 'Desktop Chrome',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'Mobile Chrome (iPhone 13)',
      use: { ...devices['iPhone 13'] },
    },

    {
      name: 'Mobile Chrome (iPhone SE - 320px)',
      use: {
        ...devices['iPhone SE'],
        viewport: { width: 320, height: 568 },
      },
    },

    {
      name: 'Mobile Chrome (iPhone 12 Pro - 390px)',
      use: {
        ...devices['iPhone 12 Pro'],
        viewport: { width: 390, height: 844 },
      },
    },

    {
      name: 'Tablet (iPad Pro)',
      use: { ...devices['iPad Pro'] },
    },
  ],

  // Local development server
  webServer: process.env.CI ? undefined : {
    command: 'cd ../../frontend && npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
