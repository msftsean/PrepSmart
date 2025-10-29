/**
 * PrepSmart Agent Dashboard
 *
 * Manages real-time agent status updates and progress tracking
 */

const AGENT_CONFIG = {
  'RiskAssessmentAgent': {
    icon: '🎯',
    name: 'Risk Assessment',
    description: 'Analyzing location-specific threats and severity levels'
  },
  'SupplyPlanningAgent': {
    icon: '📦',
    name: 'Supply Planning',
    description: 'Creating budget-optimized supply checklist'
  },
  'FinancialAdvisorAgent': {
    icon: '💰',
    name: 'Financial Advisor',
    description: 'Building 30-day economic survival strategy'
  },
  'ResourceLocatorAgent': {
    icon: '📍',
    name: 'Resource Locator',
    description: 'Finding nearby emergency resources and services'
  },
  'VideoCuratorAgent': {
    icon: '🎥',
    name: 'Video Curator',
    description: 'Recommending relevant preparedness videos'
  },
  'DocumentationAgent': {
    icon: '📄',
    name: 'Documentation',
    description: 'Compiling complete plan and generating PDF'
  },
  'CoordinatorAgent': {
    icon: '🤖',
    name: 'Coordinator',
    description: 'Orchestrating all agents and managing workflow'
  }
};

let pollInterval;
let startTime;
let taskId;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
  taskId = sessionStorage.getItem('task_id');

  if (!taskId) {
    showError('No task ID found. Please start over.');
    return;
  }

  startTime = Date.now();
  initializeAgentCards();
  startPolling();
});

/**
 * Initialize agent cards in the grid
 */
function initializeAgentCards() {
  const grid = document.getElementById('agents-grid');
  if (!grid) return;

  // Clear existing cards
  grid.innerHTML = '';

  // Create card for each agent (except Coordinator for now)
  const displayAgents = [
    'RiskAssessmentAgent',
    'SupplyPlanningAgent',
    'FinancialAdvisorAgent',
    'ResourceLocatorAgent',
    'VideoCuratorAgent',
    'DocumentationAgent'
  ];

  displayAgents.forEach(agentKey => {
    const config = AGENT_CONFIG[agentKey];
    if (!config) return;

    const card = createAgentCard(agentKey, config);
    grid.appendChild(card);
  });
}

/**
 * Create HTML element for agent card
 */
function createAgentCard(agentKey, config) {
  const card = document.createElement('div');
  card.className = 'agent-card pending';
  card.id = `agent-${agentKey}`;
  card.dataset.agent = agentKey;

  card.innerHTML = `
    <div class="agent-header">
      <div class="agent-icon">${config.icon}</div>
      <div class="agent-info">
        <div class="agent-name">${config.name}</div>
        <div class="agent-status">
          <span class="status-dot pending"></span>
          <span class="status-text">Waiting...</span>
        </div>
      </div>
    </div>
    <div class="agent-description">${config.description}</div>
    <div class="agent-log hidden"></div>
  `;

  return card;
}

/**
 * Start polling for status updates
 */
function startPolling() {
  // Poll immediately
  pollStatus();

  // Then poll every 2 seconds
  pollInterval = setInterval(pollStatus, 2000);
}

/**
 * Stop polling
 */
function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
}

/**
 * Poll status endpoint
 */
async function pollStatus() {
  try {
    const status = await api.getCrisisStatus(taskId);

    console.log('Status update:', status);

    updateDashboard(status);

    // Check if complete
    if (status.status === 'completed') {
      stopPolling();
      showCompletion();
    } else if (status.status === 'failed') {
      stopPolling();
      showError(status.error || 'Plan generation failed');
    }

  } catch (error) {
    console.error('Polling error:', error);

    // If 404, task might not exist
    if (error.message.includes('404')) {
      stopPolling();
      showError('Task not found. The plan generation may have expired.');
    }
    // Otherwise, keep polling - might be temporary network issue
  }
}

/**
 * Update dashboard with status data
 */
function updateDashboard(status) {
  // Update overall progress
  const progress = status.progress_percentage || 0;
  updateOverallProgress(progress, status.status);

  // Update time estimate
  updateTimeEstimate(progress);

  // Update individual agent statuses from agents array
  if (status.agents && Array.isArray(status.agents)) {
    status.agents.forEach(agent => {
      updateAgentCard(agent.agent_name, agent);
    });
  }
}

/**
 * Update overall progress bar
 */
function updateOverallProgress(progress, status) {
  const progressBar = document.getElementById('overall-progress-bar');
  const progressLabel = document.getElementById('progress-label');
  const progressPercentage = document.getElementById('progress-percentage');

  if (progressBar) {
    progressBar.style.width = `${progress}%`;

    // Change color based on progress
    if (progress >= 100) {
      progressBar.classList.add('progress-bar-success');
    }
  }

  if (progressLabel) {
    const labels = {
      'pending': 'Initializing...',
      'in_progress': 'Analyzing your situation...',
      'completed': 'Analysis complete!',
      'failed': 'Error occurred'
    };
    progressLabel.textContent = labels[status] || 'Processing...';
  }

  if (progressPercentage) {
    progressPercentage.textContent = `${Math.round(progress)}%`;
  }
}

/**
 * Update time estimate
 */
function updateTimeEstimate(progress) {
  const timeRemaining = document.getElementById('time-remaining');
  if (!timeRemaining) return;

  const elapsed = (Date.now() - startTime) / 1000; // seconds
  const estimatedTotal = 180; // 3 minutes

  if (progress > 0 && progress < 100) {
    const remaining = Math.max(0, estimatedTotal - elapsed);
    const minutes = Math.floor(remaining / 60);
    const seconds = Math.floor(remaining % 60);

    if (minutes > 0) {
      timeRemaining.textContent = `~${minutes}m ${seconds}s`;
    } else {
      timeRemaining.textContent = `~${seconds}s`;
    }
  } else if (progress >= 100) {
    timeRemaining.textContent = 'Complete!';
  }
}

/**
 * Update individual agent card
 */
function updateAgentCard(agentName, agentStatus) {
  const card = document.getElementById(`agent-${agentName}`);
  if (!card) return;

  const status = agentStatus.status || 'pending';
  const message = agentStatus.current_task_description || agentStatus.message || '';

  // Update card class (map 'active' to 'in_progress' for styling)
  const displayStatus = status === 'active' ? 'in_progress' : status;
  card.className = `agent-card ${displayStatus}`;

  // Update status dot
  const statusDot = card.querySelector('.status-dot');
  if (statusDot) {
    statusDot.className = `status-dot ${displayStatus}`;
  }

  // Update status text
  const statusText = card.querySelector('.status-text');
  if (statusText) {
    const statusLabels = {
      'pending': 'Waiting...',
      'active': 'Working...',
      'in_progress': 'Working...',
      'completed': 'Complete ✓',
      'failed': 'Error ✗',
      'error': 'Error ✗',
      'skipped': 'Skipped'
    };
    statusText.textContent = statusLabels[status] || status;
  }

  // Update description with current task
  const descriptionEl = card.querySelector('.agent-description');
  if (descriptionEl && message) {
    descriptionEl.textContent = message;
    descriptionEl.style.fontStyle = 'italic';
    descriptionEl.style.color = '#666';
  }

  // Update progress percentage if available
  if (agentStatus.progress_percentage !== undefined) {
    let progressEl = card.querySelector('.agent-progress');
    if (!progressEl) {
      progressEl = document.createElement('div');
      progressEl.className = 'agent-progress';
      progressEl.style.fontSize = '0.85rem';
      progressEl.style.color = '#888';
      progressEl.style.marginTop = '0.5rem';
      card.appendChild(progressEl);
    }
    progressEl.textContent = `${agentStatus.progress_percentage}% complete`;
  }
}

/**
 * Show completion message
 */
function showCompletion() {
  const completionMsg = document.getElementById('completion-message');
  const timeEstimate = document.getElementById('time-estimate');

  if (completionMsg) {
    completionMsg.classList.remove('hidden');
  }

  if (timeEstimate) {
    timeEstimate.classList.add('hidden');
  }

  // Celebrate!
  document.querySelector('.page-header h1').textContent = 'Your Plan is Ready! 🎉';
}

/**
 * Show error message
 */
function showError(errorText) {
  const errorMsg = document.getElementById('error-message');
  const errorTextEl = document.getElementById('error-text');
  const agentsGrid = document.getElementById('agents-grid');
  const timeEstimate = document.getElementById('time-estimate');

  if (errorMsg) {
    errorMsg.classList.remove('hidden');
  }

  if (errorTextEl) {
    errorTextEl.textContent = errorText;
  }

  if (agentsGrid) {
    agentsGrid.classList.add('hidden');
  }

  if (timeEstimate) {
    timeEstimate.classList.add('hidden');
  }

  document.querySelector('.page-header h1').textContent = 'Error Generating Plan';
}

/**
 * Navigate to results page
 */
function viewResults() {
  window.location.href = 'plan-results.html';
}

// Make viewResults available globally
window.viewResults = viewResults;

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  stopPolling();
});
