/**
 * E2E Test: Natural Disaster Crisis Plan Generation
 *
 * Scenario: TS-001 - Hurricane in Miami, FL ($100 budget)
 * Expected: Complete plan in <180 seconds with all agents succeeding
 */

import { test, expect, Page } from '@playwright/test';

test.describe('Natural Disaster Flow - Hurricane Miami', () => {
  let taskId: string;

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/PrepSmart/i);
  });

  test('01. Homepage loads correctly', async ({ page }) => {
    // Check hero section
    await expect(page.locator('h1')).toContainText(/PrepSmart|Crisis Preparedness/i);

    // Check CTA buttons
    const startButton = page.getByRole('button', { name: /get started|create plan/i });
    await expect(startButton).toBeVisible();
  });

  test('02. Crisis mode selection - Natural Disaster', async ({ page }) => {
    // Click start button
    await page.getByRole('button', { name: /get started|create plan/i }).click();

    // Wait for crisis mode selection
    await expect(page.locator('h2, h3')).toContainText(/select.*crisis|what.*crisis/i);

    // Select natural disaster
    const naturalDisasterCard = page.locator('[data-testid="crisis-mode-natural_disaster"]')
      .or(page.getByRole('button', { name: /natural disaster|hurricane|earthquake/i }).first());

    await naturalDisasterCard.click();

    // Verify selection
    await expect(page).toHaveURL(/crisis-mode=natural_disaster|mode=natural/);
  });

  test('03. Form inputs - Hurricane Miami FL', async ({ page }) => {
    // Navigate to form
    await page.goto('/?step=1&crisis_mode=natural_disaster');

    // Select specific threat
    const threatSelect = page.locator('select[name="specific_threat"]')
      .or(page.getByLabel(/threat type|disaster type/i));
    await threatSelect.selectOption('hurricane');

    // Fill location (City, State, ZIP)
    await page.getByLabel(/city/i).fill('Miami');
    await page.getByLabel(/state/i).selectOption('FL');
    await page.getByLabel(/zip/i).fill('33139');

    // Fill household info
    await page.getByLabel(/adults/i).fill('2');
    await page.getByLabel(/children/i).fill('1');
    await page.getByLabel(/pets/i).fill('0');

    // Select housing type
    const housingSelect = page.locator('select[name="housing_type"]')
      .or(page.getByLabel(/housing type/i));
    await housingSelect.selectOption('apartment');

    // Select budget tier
    const budget100 = page.locator('[data-testid="budget-tier-100"]')
      .or(page.getByRole('button', { name: /\$100/i }));
    await budget100.click();

    // Verify form completion
    await expect(page.getByLabel(/city/i)).toHaveValue('Miami');
    await expect(page.getByLabel(/adults/i)).toHaveValue('2');
  });

  test('04. Submit form and start plan generation', async ({ page }) => {
    // Fill form programmatically (faster for testing)
    await page.goto('/?step=1&crisis_mode=natural_disaster');

    await page.evaluate(() => {
      const form: any = {
        crisis_mode: 'natural_disaster',
        specific_threat: 'hurricane',
        location: { city: 'Miami', state: 'FL', zip_code: '33139' },
        household: { adults: 2, children: 1, pets: 0 },
        housing_type: 'apartment',
        budget_tier: 100
      };
      window.localStorage.setItem('crisis_profile_draft', JSON.stringify(form));
    });

    // Submit form
    const submitButton = page.getByRole('button', { name: /generate plan|submit|start/i });
    await submitButton.click();

    // Wait for API response and task_id
    await page.waitForURL(/\/plan\/[a-f0-9-]{36}/i, { timeout: 10000 });

    // Extract task_id from URL
    const url = page.url();
    const match = url.match(/\/plan\/([a-f0-9-]{36})/);
    expect(match).not.toBeNull();
    taskId = match![1];

    console.log(`✅ Task ID created: ${taskId}`);
  });

  test('05. Live log streaming - Agent progress tracking', async ({ page }) => {
    // Navigate to plan generation page with test task_id
    await page.goto('/plan/test-task-id'); // Will be updated with real task_id

    // Check for agent progress dashboard
    const agentDashboard = page.locator('[data-testid="agent-dashboard"]')
      .or(page.locator('.agent-progress, .agent-status'));

    await expect(agentDashboard).toBeVisible({ timeout: 5000 });

    // Wait for agents to appear
    const agents = [
      '🎯 Coordinator',
      '🌪️ Risk Assessment',
      '📦 Supply Planning',
      '🗺️ Resource Locator',
      '🎥 Video Curator',
      '📄 Documentation'
    ];

    for (const agent of agents) {
      const agentLog = page.locator('text=' + agent).or(page.getByText(new RegExp(agent.split(' ')[1])));
      // Agent should appear within 180 seconds
      await expect(agentLog).toBeVisible({ timeout: 180000 });
    }
  });

  test('06. Agent completion - All agents succeed', async ({ page, request }) => {
    // Start plan generation
    const response = await request.post('/api/crisis/start', {
      data: {
        crisis_mode: 'natural_disaster',
        specific_threat: 'hurricane',
        location: { city: 'Miami', state: 'FL', zip_code: '33139', latitude: 25.7959, longitude: -80.1396 },
        household: { adults: 2, children: 1, pets: 0 },
        housing_type: 'apartment',
        budget_tier: 100
      }
    });

    expect(response.status()).toBe(202);
    const data = await response.json();
    taskId = data.task_id;

    // Poll status endpoint
    let completed = false;
    let attempts = 0;
    const maxAttempts = 60; // 60 attempts * 3 seconds = 3 minutes

    while (!completed && attempts < maxAttempts) {
      await page.waitForTimeout(3000); // Wait 3 seconds

      const statusResponse = await request.get(`/api/crisis/${taskId}/status`);
      const statusData = await statusResponse.json();

      console.log(`Status check ${attempts + 1}: ${statusData.status} (${statusData.progress_percentage}%)`);

      if (statusData.status === 'completed') {
        completed = true;

        // Verify all agents succeeded
        expect(statusData.agents).toBeDefined();
        const allAgentsComplete = statusData.agents.every((agent: any) =>
          agent.status === 'complete'
        );
        expect(allAgentsComplete).toBe(true);

        console.log('✅ All agents completed successfully');
      } else if (statusData.status === 'failed') {
        throw new Error('Plan generation failed');
      }

      attempts++;
    }

    expect(completed).toBe(true);
    expect(attempts).toBeLessThan(maxAttempts); // Should complete in <3 minutes
  });

  test('07. Plan result - Retrieve complete plan', async ({ request }) => {
    // Use task_id from previous test (or create new one)
    if (!taskId) {
      test.skip(); // Skip if no task_id available
    }

    // Get result
    const resultResponse = await request.get(`/api/crisis/${taskId}/result`);
    expect(resultResponse.status()).toBe(200);

    const result = await resultResponse.json();

    // Verify plan structure
    expect(result.task_id).toBe(taskId);
    expect(result.status).toBe('completed');
    expect(result.crisis_profile).toBeDefined();
    expect(result.risk_assessment).toBeDefined();
    expect(result.supply_plan).toBeDefined();
    expect(result.resource_locations).toBeInstanceOf(Array);
    expect(result.video_recommendations).toBeInstanceOf(Array);
    expect(result.pdf_path).toBeDefined();

    // Verify risk assessment
    expect(result.risk_assessment.overall_risk_level).toMatch(/LOW|MEDIUM|HIGH|EXTREME/);
    expect(result.risk_assessment.severity_score).toBeGreaterThan(0);

    // Verify supply plan
    expect(result.supply_plan.tiers).toBeDefined();
    expect(result.supply_plan.total_items).toBeGreaterThan(0);

    // Verify resources
    expect(result.resource_locations.length).toBeGreaterThan(0);
    expect(result.resource_locations[0].name).toBeDefined();
    expect(result.resource_locations[0].distance_miles).toBeDefined();

    // Verify videos
    expect(result.video_recommendations.length).toBeGreaterThan(0);
    expect(result.video_recommendations[0].title).toBeDefined();
    expect(result.video_recommendations[0].url).toMatch(/^https?:\/\//);

    console.log('✅ Complete plan retrieved successfully');
    console.log(`   Risk Level: ${result.risk_assessment.overall_risk_level}`);
    console.log(`   Supply Items: ${result.supply_plan.total_items}`);
    console.log(`   Resources: ${result.resource_locations.length}`);
    console.log(`   Videos: ${result.video_recommendations.length}`);
  });

  test('08. PDF download - Verify file download', async ({ page, request }) => {
    if (!taskId) {
      test.skip();
    }

    // Navigate to results page
    await page.goto(`/plan/${taskId}`);

    // Wait for PDF download button
    const downloadButton = page.getByRole('button', { name: /download pdf|download plan/i });
    await expect(downloadButton).toBeVisible({ timeout: 10000 });

    // Start waiting for download
    const downloadPromise = page.waitForEvent('download');

    // Click download button
    await downloadButton.click();

    // Wait for download to complete
    const download = await downloadPromise;

    // Verify filename
    expect(download.suggestedFilename()).toMatch(/crisis_plan.*\.pdf$/);

    // Save and verify file
    const path = await download.path();
    expect(path).toBeDefined();

    // Verify file size (should be <5MB, typically <500KB)
    const fs = require('fs');
    const stats = fs.statSync(path);
    expect(stats.size).toBeGreaterThan(1000); // At least 1KB
    expect(stats.size).toBeLessThan(5 * 1024 * 1024); // Less than 5MB

    console.log(`✅ PDF downloaded: ${download.suggestedFilename()} (${(stats.size / 1024).toFixed(1)} KB)`);
  });

  test('09. Mobile responsiveness - 320px viewport', async ({ page }) => {
    // Set mobile viewport (iPhone SE - smallest mobile)
    await page.setViewportSize({ width: 320, height: 568 });

    await page.goto('/');

    // Verify mobile layout
    const startButton = page.getByRole('button', { name: /get started/i });
    await expect(startButton).toBeVisible();

    // Check that text is readable (not cut off)
    const heading = page.locator('h1').first();
    const boundingBox = await heading.boundingBox();
    expect(boundingBox).not.toBeNull();
    expect(boundingBox!.width).toBeLessThanOrEqual(320);

    // Check touch targets are at least 44px (iOS guideline)
    const buttons = page.getByRole('button');
    const firstButton = buttons.first();
    const buttonBox = await firstButton.boundingBox();
    if (buttonBox) {
      expect(buttonBox.height).toBeGreaterThanOrEqual(44);
    }

    console.log('✅ Mobile 320px layout verified');
  });

  test('10. Performance - Plan generation <180 seconds', async ({ request }) => {
    const startTime = Date.now();

    // Start plan generation
    const response = await request.post('/api/crisis/start', {
      data: {
        crisis_mode: 'natural_disaster',
        specific_threat: 'hurricane',
        location: { city: 'Miami', state: 'FL', zip_code: '33139', latitude: 25.7959, longitude: -80.1396 },
        household: { adults: 2, children: 1, pets: 0 },
        housing_type: 'apartment',
        budget_tier: 100
      }
    });

    const data = await response.json();
    const newTaskId = data.task_id;

    // Poll until complete
    let completed = false;
    while (!completed) {
      await new Promise(resolve => setTimeout(resolve, 3000));

      const statusResponse = await request.get(`/api/crisis/${newTaskId}/status`);
      const statusData = await statusResponse.json();

      if (statusData.status === 'completed' || statusData.status === 'failed') {
        completed = true;
      }
    }

    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;

    console.log(`✅ Plan generation completed in ${duration.toFixed(1)} seconds`);
    expect(duration).toBeLessThan(180); // Must complete in <3 minutes
  });
});
