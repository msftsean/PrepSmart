/**
 * E2E Test: Economic Crisis Plan Generation
 *
 * Scenario: TS-003 - Unemployment in Austin, TX ($50 budget)
 * Expected: Complete plan with Financial Advisor agent, benefits analysis
 */

import { test, expect } from '@playwright/test';

test.describe('Economic Crisis Flow - Unemployment Austin', () => {
  let taskId: string;

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('01. Crisis mode selection - Economic Crisis', async ({ page }) => {
    await page.getByRole('button', { name: /get started|create plan/i }).click();

    // Select economic crisis
    const economicCrisisCard = page.locator('[data-testid="crisis-mode-economic_crisis"]')
      .or(page.getByRole('button', { name: /economic crisis|job loss|unemployment/i }).first());

    await economicCrisisCard.click();

    await expect(page).toHaveURL(/crisis-mode=economic|mode=economic/);
  });

  test('02. Form inputs - Unemployment Austin TX', async ({ page }) => {
    await page.goto('/?step=1&crisis_mode=economic_crisis');

    // Select specific threat
    const threatSelect = page.locator('select[name="specific_threat"]')
      .or(page.getByLabel(/threat type|crisis type/i));
    await threatSelect.selectOption('unemployment');

    // Fill location
    await page.getByLabel(/city/i).fill('Austin');
    await page.getByLabel(/state/i).selectOption('TX');
    await page.getByLabel(/zip/i).fill('78701');

    // Fill household
    await page.getByLabel(/adults/i).fill('1');
    await page.getByLabel(/children/i).fill('0');

    // Select budget
    const budget50 = page.locator('[data-testid="budget-tier-50"]')
      .or(page.getByRole('button', { name: /\$50/i }));
    await budget50.click();

    // Runtime questions (economic crisis specific)
    const primaryConcern = page.getByLabel(/primary concern|main worry/i);
    if (await primaryConcern.isVisible()) {
      await primaryConcern.selectOption('job_loss');
    }

    const runway = page.getByLabel(/runway|how long/i);
    if (await runway.isVisible()) {
      await runway.fill('30 days');
    }

    console.log('✅ Economic crisis form filled');
  });

  test('03. Submit and verify Financial Advisor agent runs', async ({ page, request }) => {
    // Start plan generation
    const response = await request.post('/api/crisis/start', {
      data: {
        crisis_mode: 'economic_crisis',
        specific_threat: 'unemployment',
        location: { city: 'Austin', state: 'TX', zip_code: '78701', latitude: 30.2672, longitude: -97.7431 },
        household: { adults: 1, children: 0, pets: 0 },
        housing_type: 'apartment',
        budget_tier: 50,
        runtime_questions: {
          primary_concern: 'job_loss',
          runway: '30 days',
          budget_priority: 'maximize calories per dollar'
        }
      }
    });

    expect(response.status()).toBe(202);
    const data = await response.json();
    taskId = data.task_id;

    // Navigate to plan page
    await page.goto(`/plan/${taskId}`);

    // Wait for Financial Advisor agent to appear
    const financialAdvisor = page.locator('text=💼').or(page.getByText(/financial advisor/i));
    await expect(financialAdvisor).toBeVisible({ timeout: 180000 });

    console.log('✅ Financial Advisor agent detected');
  });

  test('04. Verify economic plan structure', async ({ request }) => {
    // Start and wait for completion
    const response = await request.post('/api/crisis/start', {
      data: {
        crisis_mode: 'economic_crisis',
        specific_threat: 'unemployment',
        location: { city: 'Austin', state: 'TX', zip_code: '78701', latitude: 30.2672, longitude: -97.7431 },
        household: { adults: 1, children: 0, pets: 0 },
        housing_type: 'apartment',
        budget_tier: 50,
        runtime_questions: {
          primary_concern: 'job_loss',
          runway: '30 days'
        }
      }
    });

    const data = await response.json();
    taskId = data.task_id;

    // Poll until complete
    let completed = false;
    let attempts = 0;

    while (!completed && attempts < 60) {
      await new Promise(resolve => setTimeout(resolve, 3000));

      const statusResponse = await request.get(`/api/crisis/${taskId}/status`);
      const statusData = await statusResponse.json();

      if (statusData.status === 'completed') {
        completed = true;
      } else if (statusData.status === 'failed') {
        throw new Error('Plan generation failed');
      }

      attempts++;
    }

    expect(completed).toBe(true);

    // Get result
    const resultResponse = await request.get(`/api/crisis/${taskId}/result`);
    const result = await resultResponse.json();

    // Verify economic plan exists
    expect(result.economic_plan).toBeDefined();

    const economicPlan = result.economic_plan;

    // Verify financial summary
    expect(economicPlan.financial_summary).toBeDefined();
    expect(economicPlan.financial_summary.available_savings).toBe(50);

    // Verify expense categories
    expect(economicPlan.expense_categories).toBeDefined();
    expect(economicPlan.expense_categories.must_pay).toBeInstanceOf(Array);
    expect(economicPlan.expense_categories.defer).toBeInstanceOf(Array);
    expect(economicPlan.expense_categories.eliminate).toBeInstanceOf(Array);

    // Verify daily actions
    expect(economicPlan.daily_actions).toBeInstanceOf(Array);
    expect(economicPlan.daily_actions.length).toBeGreaterThan(0);

    // Check for Day 1 critical actions
    const day1Actions = economicPlan.daily_actions.filter((action: any) => action.day === 1);
    expect(day1Actions.length).toBeGreaterThan(0);

    // Verify benefits
    expect(economicPlan.eligible_benefits).toBeInstanceOf(Array);
    expect(economicPlan.eligible_benefits.length).toBeGreaterThan(0);

    // Check for unemployment insurance
    const hasUnemployment = economicPlan.eligible_benefits.some((benefit: any) =>
      benefit.program.toLowerCase().includes('unemployment')
    );
    expect(hasUnemployment).toBe(true);

    // Verify hardship letters
    expect(economicPlan.hardship_letters).toBeInstanceOf(Array);
    expect(economicPlan.hardship_letters.length).toBeGreaterThan(0);

    // Verify survival outlook
    expect(economicPlan.survival_outlook).toBeDefined();
    expect(economicPlan.survival_outlook.with_action).toBeDefined();

    console.log('✅ Economic plan structure validated');
    console.log(`   Daily Actions: ${economicPlan.daily_actions.length}`);
    console.log(`   Eligible Benefits: ${economicPlan.eligible_benefits.length}`);
    console.log(`   Hardship Letters: ${economicPlan.hardship_letters.length}`);
  });

  test('05. Verify economic-specific resources', async ({ request }) => {
    const response = await request.post('/api/crisis/start', {
      data: {
        crisis_mode: 'economic_crisis',
        specific_threat: 'unemployment',
        location: { city: 'Austin', state: 'TX', zip_code: '78701', latitude: 30.2672, longitude: -97.7431 },
        household: { adults: 1, children: 0, pets: 0 },
        housing_type: 'apartment',
        budget_tier: 50
      }
    });

    const data = await response.json();
    taskId = data.task_id;

    // Wait for completion
    let completed = false;
    while (!completed) {
      await new Promise(resolve => setTimeout(resolve, 3000));
      const statusResponse = await request.get(`/api/crisis/${taskId}/status`);
      const statusData = await statusResponse.json();
      if (statusData.status !== 'processing') completed = true;
    }

    // Get result
    const resultResponse = await request.get(`/api/crisis/${taskId}/result`);
    const result = await resultResponse.json();

    // Verify economic-specific resources
    const resources = result.resource_locations;
    expect(resources.length).toBeGreaterThan(0);

    // Should include economic crisis resources
    const hasEconomicResources = resources.some((resource: any) =>
      resource.resource_type === 'food_bank' ||
      resource.resource_type === 'unemployment_office' ||
      resource.resource_type === 'legal_aid'
    );

    expect(hasEconomicResources).toBe(true);

    console.log('✅ Economic resources verified');
    console.log(`   Resource types: ${[...new Set(resources.map((r: any) => r.resource_type))].join(', ')}`);
  });

  test('06. Verify economic-specific videos', async ({ request }) => {
    const response = await request.post('/api/crisis/start', {
      data: {
        crisis_mode: 'economic_crisis',
        specific_threat: 'unemployment',
        location: { city: 'Austin', state: 'TX', zip_code: '78701', latitude: 30.2672, longitude: -97.7431 },
        household: { adults: 1, children: 0, pets: 0 },
        housing_type: 'apartment',
        budget_tier: 50
      }
    });

    const data = await response.json();
    taskId = data.task_id;

    // Wait for completion
    let completed = false;
    while (!completed) {
      await new Promise(resolve => setTimeout(resolve, 3000));
      const statusResponse = await request.get(`/api/crisis/${taskId}/status`);
      const statusData = await statusResponse.json();
      if (statusData.status !== 'processing') completed = true;
    }

    // Get result
    const resultResponse = await request.get(`/api/crisis/${taskId}/result`);
    const result = await resultResponse.json();

    // Verify economic crisis videos
    const videos = result.video_recommendations;
    expect(videos.length).toBeGreaterThan(0);

    // Should include economic crisis topics
    const hasEconomicTopics = videos.some((video: any) =>
      video.crisis_types.includes('unemployment') ||
      video.topics.includes('budgeting') ||
      video.topics.includes('benefits_filing')
    );

    expect(hasEconomicTopics).toBe(true);

    // Check for DOL or USDA sources (government assistance)
    const hasGovtSources = videos.some((video: any) =>
      video.source.includes('Department of Labor') ||
      video.source.includes('USDA')
    );

    expect(hasGovtSources).toBe(true);

    console.log('✅ Economic videos verified');
    console.log(`   Video count: ${videos.length}`);
    console.log(`   Sources: ${[...new Set(videos.map((v: any) => v.source))].join(', ')}`);
  });

  test('07. Budget enforcement - Never exceed $50', async ({ request }) => {
    const response = await request.post('/api/crisis/start', {
      data: {
        crisis_mode: 'economic_crisis',
        specific_threat: 'unemployment',
        location: { city: 'Austin', state: 'TX', zip_code: '78701', latitude: 30.2672, longitude: -97.7431 },
        household: { adults: 1, children: 0, pets: 0 },
        housing_type: 'apartment',
        budget_tier: 50
      }
    });

    const data = await response.json();
    taskId = data.task_id;

    // Wait for completion
    let completed = false;
    while (!completed) {
      await new Promise(resolve => setTimeout(resolve, 3000));
      const statusResponse = await request.get(`/api/crisis/${taskId}/status`);
      const statusData = await statusResponse.json();
      if (statusData.status !== 'processing') completed = true;
    }

    // Get result
    const resultResponse = await request.get(`/api/crisis/${taskId}/result`);
    const result = await resultResponse.json();

    // Check supply plan budget
    const supplyPlan = result.supply_plan;
    expect(supplyPlan).toBeDefined();

    // Get total cost from critical tier
    const criticalTier = supplyPlan.tiers?.critical;
    if (criticalTier) {
      const totalCost = criticalTier.total_cost;
      expect(totalCost).toBeLessThanOrEqual(50);
      console.log(`✅ Budget enforced: $${totalCost} <= $50`);
    }
  });
});
