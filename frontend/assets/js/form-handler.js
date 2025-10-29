/**
 * PrepSmart Form Handler
 *
 * Manages multi-step questionnaire, validation, and submission
 */

let currentStep = 1;
const totalSteps = 4;
let formData = {};

// Initialize form on page load
document.addEventListener('DOMContentLoaded', () => {
  initializeForm();
  setupEventListeners();
  loadSavedData();
});

/**
 * Initialize form based on crisis mode
 */
function initializeForm() {
  const urlParams = new URLSearchParams(window.location.search);
  const mode = urlParams.get('mode');

  // Load crisis info from sessionStorage
  const crisisMode = sessionStorage.getItem('crisis_mode');
  const disasterType = sessionStorage.getItem('disaster_type');
  const crisisType = sessionStorage.getItem('crisis_type');

  // Update back link
  const backLink = document.getElementById('back-link');
  if (backLink) {
    backLink.href = `crisis-select.html?mode=${mode}`;
  }

  // Show appropriate step 3 content
  if (mode === 'economic') {
    document.getElementById('budget-card')?.classList.add('hidden');
    document.getElementById('financial-card')?.classList.remove('hidden');
  } else {
    document.getElementById('budget-card')?.classList.remove('hidden');
    document.getElementById('financial-card')?.classList.add('hidden');
  }

  // Store mode
  formData.crisis_mode = crisisMode;
  formData.disaster_type = disasterType;
  formData.crisis_type = crisisType;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Form submission
  const form = document.getElementById('questionnaire-form');
  if (form) {
    form.addEventListener('submit', handleSubmit);
  }

  // Budget tier selection
  document.querySelectorAll('.budget-tier').forEach(tier => {
    tier.addEventListener('click', () => {
      document.querySelectorAll('.budget-tier').forEach(t => t.classList.remove('selected'));
      tier.classList.add('selected');
      document.getElementById('budget-tier').value = tier.dataset.tier;
    });
  });

  // Housing type radio selection
  document.querySelectorAll('input[name="housing-type"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      document.querySelectorAll('.radio-option').forEach(opt => opt.classList.remove('selected'));
      e.target.closest('.radio-option').classList.add('selected');
    });
  });

  // ZIP code validation
  const zipInput = document.getElementById('zip-code');
  if (zipInput) {
    zipInput.addEventListener('blur', validateZipCode);
  }
}

/**
 * Navigate to next step
 */
function nextStep() {
  if (!validateCurrentStep()) {
    return;
  }

  saveCurrentStepData();

  if (currentStep < totalSteps) {
    // Hide current step
    document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.remove('active');
    document.getElementById(`step-${currentStep}`).classList.remove('active');
    document.getElementById(`step-${currentStep}`).classList.add('completed');

    // Show next step
    currentStep++;
    document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.add('active');
    document.getElementById(`step-${currentStep}`).classList.add('active');

    // Update review if on final step
    if (currentStep === totalSteps) {
      updateReviewSummary();
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

/**
 * Navigate to previous step
 */
function prevStep() {
  if (currentStep > 1) {
    // Hide current step
    document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.remove('active');
    document.getElementById(`step-${currentStep}`).classList.remove('active');

    // Show previous step
    currentStep--;
    document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.add('active');
    document.getElementById(`step-${currentStep}`).classList.remove('completed');
    document.getElementById(`step-${currentStep}`).classList.add('active');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

/**
 * Validate current step
 */
function validateCurrentStep() {
  const currentStepEl = document.querySelector(`.form-step[data-step="${currentStep}"]`);
  const requiredFields = currentStepEl.querySelectorAll('[required]');

  let isValid = true;

  requiredFields.forEach(field => {
    // For number inputs, 0 is a valid value, so check for null/undefined/empty string only
    const isEmpty = field.value === null || field.value === undefined || field.value === '';

    if (isEmpty) {
      isValid = false;
      field.classList.add('error');

      // Add red border
      field.style.borderColor = 'var(--color-danger)';
    } else {
      field.classList.remove('error');
      field.style.borderColor = '';
    }
  });

  if (!isValid) {
    alert('Please fill in all required fields');
  }

  return isValid;
}

/**
 * Validate ZIP code
 */
async function validateZipCode() {
  const zipInput = document.getElementById('zip-code');
  const zipError = document.getElementById('zip-error');
  const zip = zipInput.value;

  if (!zip || zip.length !== 5) {
    return;
  }

  // Basic validation - in production, could call a ZIP validation API
  const zipPattern = /^\d{5}$/;
  if (!zipPattern.test(zip)) {
    zipError.textContent = 'Please enter a valid 5-digit ZIP code';
    zipError.classList.remove('hidden');
    zipInput.style.borderColor = 'var(--color-danger)';
  } else {
    zipError.classList.add('hidden');
    zipInput.style.borderColor = '';
  }
}

/**
 * Save current step data to formData object
 */
function saveCurrentStepData() {
  switch (currentStep) {
    case 1:
      formData.zip_code = document.getElementById('zip-code').value;
      formData.city = document.getElementById('city').value;
      formData.state = document.getElementById('state').value;
      break;

    case 2:
      formData.adults = parseInt(document.getElementById('adults').value);
      formData.children = parseInt(document.getElementById('children').value);
      formData.pets = parseInt(document.getElementById('pets').value);
      formData.housing_type = document.querySelector('input[name="housing-type"]:checked')?.value;
      break;

    case 3:
      if (formData.crisis_mode === 'natural_disaster') {
        formData.budget_tier = parseInt(document.getElementById('budget-tier').value);
      } else {
        formData.current_income = parseFloat(document.getElementById('current-income').value || 0);
        formData.monthly_expenses = parseFloat(document.getElementById('monthly-expenses').value || 0);
        formData.available_savings = parseFloat(document.getElementById('available-savings').value || 0);
        formData.debt_obligations = parseFloat(document.getElementById('debt-obligations').value || 0);
      }
      break;
  }

  // Save to sessionStorage
  sessionStorage.setItem('formData', JSON.stringify(formData));
}

/**
 * Load saved data from sessionStorage
 */
function loadSavedData() {
  const saved = sessionStorage.getItem('formData');
  if (saved) {
    formData = JSON.parse(saved);

    // Populate fields if data exists
    if (formData.zip_code) document.getElementById('zip-code').value = formData.zip_code;
    if (formData.city) document.getElementById('city').value = formData.city;
    if (formData.state) document.getElementById('state').value = formData.state;
    if (formData.adults) document.getElementById('adults').value = formData.adults;
    if (formData.children) document.getElementById('children').value = formData.children;
    if (formData.pets) document.getElementById('pets').value = formData.pets;
  }
}

/**
 * Update review summary on final step
 */
function updateReviewSummary() {
  const reviewEl = document.getElementById('review-summary');
  if (!reviewEl) return;

  let html = '<dl style="display: grid; grid-template-columns: auto 1fr; gap: 0.5rem 1rem;">';

  // Location
  html += `
    <dt class="font-semibold">Location:</dt>
    <dd>${formData.city}, ${formData.state} ${formData.zip_code}</dd>
  `;

  // Household
  html += `
    <dt class="font-semibold">Household:</dt>
    <dd>${formData.adults} adult(s), ${formData.children} child(ren), ${formData.pets} pet(s)</dd>
  `;

  html += `
    <dt class="font-semibold">Housing:</dt>
    <dd>${formatHousingType(formData.housing_type)}</dd>
  `;

  // Crisis-specific info
  if (formData.crisis_mode === 'natural_disaster') {
    html += `
      <dt class="font-semibold">Disaster Type:</dt>
      <dd>${formatDisasterType(formData.disaster_type)}</dd>
    `;
    html += `
      <dt class="font-semibold">Budget:</dt>
      <dd>$${formData.budget_tier} Tier</dd>
    `;
  } else {
    html += `
      <dt class="font-semibold">Crisis Type:</dt>
      <dd>${formatCrisisType(formData.crisis_type)}</dd>
    `;
    html += `
      <dt class="font-semibold">Current Income:</dt>
      <dd>$${formData.current_income.toFixed(2)}/month</dd>
    `;
    html += `
      <dt class="font-semibold">Monthly Expenses:</dt>
      <dd>$${formData.monthly_expenses.toFixed(2)}</dd>
    `;
    html += `
      <dt class="font-semibold">Savings:</dt>
      <dd>$${formData.available_savings.toFixed(2)}</dd>
    `;
  }

  html += '</dl>';
  reviewEl.innerHTML = html;
}

/**
 * Format housing type for display
 */
function formatHousingType(type) {
  const map = {
    'house': 'Single-family Home',
    'apartment': 'Apartment/Condo',
    'mobile_home': 'Mobile Home/Trailer',
    'other': 'Other'
  };
  return map[type] || type;
}

/**
 * Format disaster type for display
 */
function formatDisasterType(type) {
  const map = {
    'hurricane': 'Hurricane',
    'earthquake': 'Earthquake',
    'wildfire': 'Wildfire',
    'flood': 'Flood',
    'tornado': 'Tornado',
    'blizzard': 'Blizzard'
  };
  return map[type] || type;
}

/**
 * Format crisis type for display
 */
function formatCrisisType(type) {
  const map = {
    'unemployment': 'Unemployment',
    'furlough': 'Furlough',
    'government_shutdown': 'Government Shutdown',
    'layoff': 'Layoff',
    'reduced_hours': 'Reduced Hours',
    'other': 'Other Economic Hardship'
  };
  return map[type] || type;
}

/**
 * Handle form submission
 */
async function handleSubmit(e) {
  e.preventDefault();

  // Save final step data
  saveCurrentStepData();

  // Build crisis profile payload
  const crisisProfile = buildCrisisProfile();

  console.log('Submitting crisis profile:', crisisProfile);

  try {
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Generating Plan...';

    // Call API
    const response = await api.startCrisisPlan(crisisProfile);

    console.log('API response:', response);

    // Store task ID
    sessionStorage.setItem('task_id', response.task_id);

    // Redirect to agent progress page
    window.location.href = 'agent-progress.html';

  } catch (error) {
    console.error('Form submission error:', error);
    alert(`Error: ${error.message}\n\nPlease try again or contact support.`);

    // Reset button
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Generate My Plan';
  }
}

/**
 * Build crisis profile payload for API
 */
function buildCrisisProfile() {
  const profile = {
    crisis_mode: formData.crisis_mode,
    specific_threat: formData.crisis_mode === 'natural_disaster'
      ? formData.disaster_type
      : formData.crisis_type,
    location: {
      zip_code: formData.zip_code,
      city: formData.city,
      state: formData.state
    },
    household: {
      adults: formData.adults,
      children: formData.children,
      pets: formData.pets
    },
    housing_type: formData.housing_type
  };

  if (formData.crisis_mode === 'natural_disaster') {
    profile.budget_tier = formData.budget_tier;
  } else {
    profile.budget_tier = 100; // Default budget tier for economic crisis
    profile.financial_situation = {
      current_income: formData.current_income,
      monthly_expenses: formData.monthly_expenses,
      available_savings: formData.available_savings,
      debt_obligations: formData.debt_obligations || 0,
      employment_status: formData.crisis_type
    };
  }

  return profile;
}

// Make functions available globally
window.nextStep = nextStep;
window.prevStep = prevStep;
