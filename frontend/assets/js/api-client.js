/**
 * PrepSmart API Client
 *
 * Wrapper for all backend API calls with error handling and response validation.
 */

const API_BASE_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:5000/api'
  : 'https://prepsmart-backend.politegrass-4005e0e6.eastus.azurecontainerapps.io/api';

class PrepSmartAPI {
  /**
   * Generic fetch wrapper with error handling
   */
  async _fetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });

      // Handle non-JSON responses (like PDFs)
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/pdf')) {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.blob();
      }

      // Parse JSON response
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * Health check endpoint
   * GET /api/health
   */
  async health() {
    return this._fetch('/health');
  }

  /**
   * Start crisis plan generation
   * POST /api/crisis/start
   *
   * @param {Object} crisisProfile - Crisis profile data
   * @returns {Promise<{task_id: string}>}
   */
  async startCrisisPlan(crisisProfile) {
    return this._fetch('/crisis/start', {
      method: 'POST',
      body: JSON.stringify(crisisProfile),
    });
  }

  /**
   * Get crisis plan generation status
   * GET /api/crisis/{task_id}/status
   *
   * @param {string} taskId - Task ID from startCrisisPlan
   * @returns {Promise<Object>} Status object with agent progress
   */
  async getCrisisStatus(taskId) {
    return this._fetch(`/crisis/${taskId}/status`);
  }

  /**
   * Get complete crisis plan result
   * GET /api/crisis/{task_id}/result
   *
   * @param {string} taskId - Task ID from startCrisisPlan
   * @returns {Promise<Object>} Complete plan object or 202 if still processing
   */
  async getCrisisResult(taskId) {
    return this._fetch(`/crisis/${taskId}/result`);
  }

  /**
   * Download PDF for crisis plan
   * GET /api/crisis/{task_id}/pdf
   *
   * @param {string} taskId - Task ID from startCrisisPlan
   * @returns {Promise<Blob>} PDF blob
   */
  async downloadPDF(taskId) {
    return this._fetch(`/crisis/${taskId}/pdf`);
  }

  /**
   * Poll for crisis plan completion
   * Polls status endpoint until complete or timeout
   *
   * @param {string} taskId - Task ID from startCrisisPlan
   * @param {Function} onProgress - Callback for progress updates
   * @param {number} maxWaitMs - Maximum wait time in milliseconds (default: 5 minutes)
   * @returns {Promise<Object>} Complete plan object
   */
  async pollForCompletion(taskId, onProgress = null, maxWaitMs = 300000) {
    const startTime = Date.now();
    const pollInterval = 2000; // 2 seconds

    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          // Check timeout
          if (Date.now() - startTime > maxWaitMs) {
            reject(new Error('Plan generation timed out'));
            return;
          }

          // Get current status
          const status = await this.getCrisisStatus(taskId);

          // Call progress callback if provided
          if (onProgress) {
            onProgress(status);
          }

          // Check if complete
          if (status.status === 'completed') {
            const result = await this.getCrisisResult(taskId);
            resolve(result);
            return;
          }

          // Check if failed
          if (status.status === 'failed') {
            reject(new Error(status.error || 'Plan generation failed'));
            return;
          }

          // Continue polling
          setTimeout(poll, pollInterval);
        } catch (error) {
          reject(error);
        }
      };

      // Start polling
      poll();
    });
  }

  /**
   * Trigger PDF download in browser
   *
   * @param {string} taskId - Task ID
   * @param {string} filename - Desired filename (optional)
   */
  async triggerPDFDownload(taskId, filename = 'crisis-plan.pdf') {
    try {
      const blob = await this.downloadPDF(taskId);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();

      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('PDF download failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
const api = new PrepSmartAPI();
