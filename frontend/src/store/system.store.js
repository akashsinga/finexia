// src/store/system.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useSystemStore = defineStore('system', {
  state: () => ({
    stats: {
      status: 'offline',
      serverTime: null,
      databaseStatus: 'disconnected',
      totalPredictions: 0,
      todayPredictions: 0,
      yesterdayPredictions: 0,
      verifiedPredictions: 0,
      verifiedPredictionPercent: 0,
      directionPredictions: 0,
      recentModelTrainingCount: 0,
      modelDirectorySizeMb: 0,
      modelFileCount: 0
    },
    pipelineStatus: null,
    lastUpdateTime: 'Never',
    loading: false,
    error: null
  }),

  getters: {
    isPipelineRunning: (state) => state.pipelineStatus?.status === 'running'
  },

  actions: {
    async fetchSystemStatus() {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get('/system/status');
        const data = response.data;

        // Update system stats
        this.stats = {
          status: data.status || 'offline',
          serverTime: data.server_time,
          databaseStatus: data.database_status || 'disconnected',
          totalPredictions: data.total_predictions || 0,
          todayPredictions: data.today_predictions || 0,
          yesterdayPredictions: data.yesterday_predictions || 0,
          verifiedPredictions: data.verified_predictions || 0,
          verifiedPredictionPercent: data.verified_prediction_percent || 0,
          directionPredictions: data.direction_predictions || 0,
          recentModelTrainingCount: data.recent_model_training_count || 0,
          modelDirectorySizeMb: data.model_directory_size_mb || 0,
          modelFileCount: data.model_file_count || 0
        };

        // Update pipeline status if it exists
        if (data.pipeline_status) {
          this.pipelineStatus = {
            status: data.pipeline_status.status,
            message: data.pipeline_status.message,
            startTime: data.pipeline_status.start_time,
            requestedBy: data.pipeline_status.requested_by,
            estimatedDurationMinutes: data.pipeline_status.estimated_duration_minutes,
            progress: this.calculateProgress(data.pipeline_status),
            steps: data.pipeline_status.steps || [],
            currentStep: this.getCurrentStep(data.pipeline_status)
          };
        } else {
          // Reset pipeline status if no active pipeline
          this.pipelineStatus = {
            status: 'idle',
            progress: 0
          };
        }

        // Update last refresh time
        this.updateLastRefreshTime();

        return this.stats;
      } catch (error) {
        console.error('Error fetching system status:', error);
        this.error = error.message || 'Failed to fetch system status';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Trigger a pipeline run with the specified configuration
     * @param {Object} config The pipeline configuration
     * @param {boolean} config.force Whether to force retraining
     * @param {Array<string>} config.steps Which pipeline steps to run
     * @returns {Promise} Promise that resolves when the pipeline starts
     */
    async triggerPipelineRun(config) {
      this.loading = true;
      this.error = null;

      try {
        // Setup pipeline request payload
        const payload = {
          force: config.force || false,
          steps: config.steps || null
        };

        // Call API to trigger pipeline
        const response = await api.post('/system/run-pipeline', payload);
        const data = response.data;

        // Update pipeline status with response data
        this.pipelineStatus = {
          status: 'running',
          message: data.message,
          startTime: data.start_time,
          requestedBy: data.requested_by,
          estimatedDurationMinutes: data.estimated_duration_minutes,
          progress: 0,
          steps: data.steps || [],
          currentStep: data.steps && data.steps.length > 0 ? data.steps[0] : null
        };

        this.updateLastRefreshTime();
        return data;
      } catch (error) {
        console.error('Error triggering pipeline:', error);
        this.error = error.message || 'Failed to trigger pipeline';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Calculate progress percentage from pipeline status
     * @param {Object} pipelineStatus The pipeline status object
     * @returns {number} Progress percentage (0-100)
     */
    calculateProgress(pipelineStatus) {
      // If the API provides a progress value, use it
      if (pipelineStatus.progress !== undefined) {
        return pipelineStatus.progress;
      }

      // Calculate progress based on steps if available
      if (pipelineStatus.completed_steps !== undefined && pipelineStatus.total_steps !== undefined) {
        return (pipelineStatus.completed_steps / pipelineStatus.total_steps) * 100;
      }

      // Calculate progress based on time if available
      if (pipelineStatus.start_time && pipelineStatus.estimated_duration_minutes) {
        const startTime = new Date(pipelineStatus.start_time).getTime();
        const expectedEndTime = startTime + (pipelineStatus.estimated_duration_minutes * 60 * 1000);
        const now = new Date().getTime();
        const totalDuration = expectedEndTime - startTime;
        const elapsed = now - startTime;

        // Ensure progress doesn't exceed 99% until complete
        return Math.min(99, (elapsed / totalDuration) * 100);
      }

      // Default indeterminate progress
      return 0;
    },

    /**
     * Extract current step from pipeline status
     * @param {Object} pipelineStatus The pipeline status object
     * @returns {string|null} Current step name or null
     */
    getCurrentStep(pipelineStatus) {
      if (pipelineStatus.current_step) {
        return pipelineStatus.current_step;
      }

      return null;
    },

    /**
     * Update the last refresh timestamp
     */
    updateLastRefreshTime() {
      const now = new Date();
      this.lastUpdateTime = now.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
});