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
    pipelineStatus: {
      status: 'idle',
      message: null,
      currentStep: null,
      progress: 0,
      requestedBy: null,
      estimatedDurationMinutes: null,
      lastRun: null
    },
    pipelineLogs: [],
    wsConnected: false,
    lastUpdateTime: 'Never',
    loading: false,
    error: null
  }),

  getters: {
    isPipelineRunning: (state) => state.pipelineStatus?.status === 'running',

    formattedModelStorageSize: (state) => {
      const size = state.stats.modelDirectorySizeMb || 0;
      if (size < 1) {
        return `${(size * 1024).toFixed(0)} KB`;
      }
      return `${size.toFixed(1)} MB`;
    }
  },

  actions: {
    // Fetch system status via HTTP
    async fetchSystemStatus() {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get('/system/status');
        const data = response.data;

        this.updateSystemStats(data);

        if (data.pipeline_status) {
          this.updatePipelineStatus(data.pipeline_status);
        }

        if (data.logs) {
          this.updateLogs(data.logs);
        }

        this.updateLastRefreshTime();
        return this.stats;
      } catch (error) {
        console.error('Failed to fetch system status:', error);
        this.error = error.message || 'Failed to fetch system status';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Update system statistics
    updateSystemStats(data) {
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
    },

    // Update pipeline status
    updatePipelineStatus(pipelineStatus) {
      if (!pipelineStatus) return;

      this.pipelineStatus = {
        status: pipelineStatus.status || 'idle',
        message: pipelineStatus.message,
        currentStep: pipelineStatus.current_step,
        requestedBy: pipelineStatus.requested_by,
        estimatedDurationMinutes: pipelineStatus.estimated_duration_minutes,
        progress: this.calculateProgress(pipelineStatus),
        lastRun: pipelineStatus.last_run || this.pipelineStatus.lastRun
      };
    },

    // Update logs
    updateLogs(logs) {
      if (Array.isArray(logs) && logs.length > 0) {
        this.pipelineLogs = logs;
      }
    },

    // Add a single log entry
    addLogEntry(logEntry) {
      if (logEntry) {
        this.pipelineLogs.unshift(logEntry);
        if (this.pipelineLogs.length > 100) {
          this.pipelineLogs = this.pipelineLogs.slice(0, 100);
        }
      }
    },

    // Set WebSocket connection status
    setWsConnected(status) {
      this.wsConnected = status;
    },

    // Refresh logs
    async refreshLogs(limit = 50) {
      try {
        const response = await api.get('/system/logs', { params: { limit } });
        this.pipelineLogs = response.data.logs || [];
        return this.pipelineLogs;
      } catch (error) {
        console.error('Failed to fetch logs:', error);
        throw error;
      }
    },

    // Calculate progress percentage
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

      // Default to indeterminate progress
      return 0;
    },

    // Run pipeline
    async runPipeline(config = {}) {
      this.loading = true;
      this.error = null;

      try {
        // Prepare request payload
        const payload = {
          force: config.force || false,
          steps: config.steps || null,
          max_symbols: config.maxSymbols || null
        };

        // Call API to trigger pipeline
        const response = await api.post('/system/run-pipeline', payload);
        const data = response.data;

        // Update status
        this.updatePipelineStatus({
          status: 'running',
          message: data.message,
          start_time: data.start_time,
          requested_by: data.requested_by,
          estimated_duration_minutes: data.estimated_duration_minutes,
          steps: data.steps || []
        });

        return data;
      } catch (error) {
        console.error('Failed to start pipeline:', error);
        this.error = error.message || 'Failed to start pipeline';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Update system settings
    async updateSystemSettings(settings) {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.post('/system/settings', settings);
        return response.data;
      } catch (error) {
        console.error('Failed to update system settings:', error);
        this.error = error.message || 'Failed to update system settings';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // Update last refresh timestamp
    updateLastRefreshTime() {
      const now = new Date();
      this.lastUpdateTime = now.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    // Handle WebSocket message
    handleWebSocketMessage(data) {
      if (data.type === 'status_update') {
        this.updateSystemStats(data.status);
        if (data.pipeline_status) {
          this.updatePipelineStatus(data.pipeline_status);
        }
        if (data.logs) {
          this.updateLogs(data.logs);
        }
        this.updateLastRefreshTime();
      }
      else if (data.type === 'pipeline_update') {
        this.updatePipelineStatus(data.pipeline_status);
        if (data.log_entry) {
          this.addLogEntry(data.log_entry);
        }
      }
    }
  }
});