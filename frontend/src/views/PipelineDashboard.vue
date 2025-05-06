<template>
  <div class="pipeline-dashboard">
    <!-- Status Card with Pipeline Controls -->
    <div class="status-card">
      <div class="status-header">
        <div class="status-info">
          <div class="status-title-row">
            <h1 class="status-title">Pipeline Dashboard</h1>
            <div class="connection-status" :class="{ 'connected': wsConnected }">
              <span class="status-dot"></span>
              <span class="status-text">{{ wsConnected ? 'Live' : 'Offline' }}</span>
            </div>
          </div>
          <div class="status-badge" :class="getStatusClass(pipelineStatus.status)">
            {{ capitalizeFirst(pipelineStatus.status) }}
          </div>
        </div>
        <div class="action-buttons">
          <v-btn color="primary" :variant="isRunning ? 'outlined' : 'tonal'" :disabled="isRunning" size="small" prepend-icon="mdi-cog" @click="showConfigModal = true">
            Configure
          </v-btn>
          <v-btn color="primary" :variant="isRunning ? 'outlined' : 'elevated'" :disabled="isRunning" size="small" :loading="isRunning" prepend-icon="mdi-play" @click="runPipeline">
            Run Pipeline
          </v-btn>
        </div>
      </div>

      <!-- Progress bar when pipeline is running -->
      <div v-if="isRunning" class="progress-container">
        <div class="progress-header">
          <div class="progress-message">{{ pipelineStatus.message || 'Running pipeline...' }}</div>
          <div class="progress-info">
            <span class="progress-percentage">{{ Math.round(pipelineStatus.progress) }}%</span>
            <span v-if="pipelineStatus.estimatedDurationMinutes" class="progress-time">
              {{ formatTimeRemaining(pipelineStatus.estimatedDurationMinutes) }} remaining
            </span>
          </div>
        </div>
        <v-progress-linear :model-value="pipelineStatus.progress" color="primary" height="8" rounded></v-progress-linear>
      </div>
    </div>

    <!-- Stats Cards Grid -->
    <div class="stats-grid">
      <!-- System Stats Card -->
      <div class="stat-card">
        <div class="stat-card-header">
          <h2 class="stat-card-title">System Statistics</h2>
          <span v-if="lastUpdateTime" class="last-update">Updated {{ lastUpdateTime }}</span>
        </div>
        <div class="stat-grid">
          <div class="stat-item">
            <div class="stat-icon bg-blue-50 text-blue-600">
              <v-icon>mdi-chart-line</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ systemStats.totalPredictions || 0 }}</div>
              <div class="stat-label">Total Predictions</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon bg-green-50 text-green-600">
              <v-icon>mdi-calendar-check</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ systemStats.todayPredictions || 0 }}</div>
              <div class="stat-label">Today's Predictions</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon bg-amber-50 text-amber-600">
              <v-icon>mdi-check-decagram</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ systemStats.verifiedPredictions || 0 }}</div>
              <div class="stat-label">Verified Predictions</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon bg-purple-50 text-purple-600">
              <v-icon>mdi-arrow-decision</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ systemStats.directionPredictions || 0 }}</div>
              <div class="stat-label">Direction Predictions</div>
            </div>
          </div>
        </div>
        <div class="success-rate-container">
          <div class="success-rate-header">
            <div class="success-rate-label">Success Rate</div>
            <div class="success-rate-value">{{ (systemStats.verifiedPredictionPercent || 0).toFixed(1) }}%</div>
          </div>
          <v-progress-linear :model-value="systemStats.verifiedPredictionPercent || 0" :color="getSuccessRateColor(systemStats.verifiedPredictionPercent)" height="8" rounded></v-progress-linear>
        </div>
      </div>

      <!-- Models Stats Card -->
      <div class="stat-card">
        <div class="stat-card-header">
          <h2 class="stat-card-title">Model Information</h2>
          <v-btn icon="mdi-refresh" variant="text" density="comfortable" color="gray" @click="fetchInitialSystemStatus"></v-btn>
        </div>
        <div class="stat-grid">
          <div class="stat-item">
            <div class="stat-icon bg-indigo-50 text-indigo-600">
              <v-icon>mdi-brain</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ systemStats.modelFileCount || 0 }}</div>
              <div class="stat-label">Model Files</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon bg-cyan-50 text-cyan-600">
              <v-icon>mdi-file-chart</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ formatSize(systemStats.modelDirectorySizeMb || 0) }}</div>
              <div class="stat-label">Storage Used</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon bg-pink-50 text-pink-600">
              <v-icon>mdi-update</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ systemStats.recentModelTrainingCount || 0 }}</div>
              <div class="stat-label">Recent Trainings</div>
            </div>
          </div>
          <div class="stat-item">
            <div class="stat-icon bg-amber-50 text-amber-600">
              <v-icon>mdi-database</v-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ systemStats.databaseStatus || 'N/A' }}</div>
              <div class="stat-label">Database Status</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pipeline Steps Panel -->
    <div class="steps-card">
      <div class="steps-header">
        <h2 class="steps-title">Pipeline Steps</h2>
        <div class="steps-actions">
          <v-btn size="small" variant="text" color="primary" @click="selectAllSteps" class="select-btn">
            {{ allStepsSelected ? 'Deselect All' : 'Select All' }}
          </v-btn>
        </div>
      </div>
      <div class="steps-container">
        <div v-for="(step, index) in pipelineSteps" :key="step.id" class="step-item" :class="{
          'step-running': isRunning && pipelineStatus.currentStep === step.name,
          'step-selected': selectedSteps.includes(step.id)
        }" @click="toggleStep(step.id)">
          <div class="step-indicator" :class="getStepClass(step, pipelineStatus)">
            <v-icon v-if="getStepStatus(step, pipelineStatus) === 'completed'" size="small">mdi-check</v-icon>
            <v-icon v-else-if="getStepStatus(step, pipelineStatus) === 'running'" size="small">mdi-loading mdi-spin</v-icon>
            <v-icon v-else-if="getStepStatus(step, pipelineStatus) === 'failed'" size="small">mdi-close</v-icon>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <div class="step-content">
            <div class="step-title">{{ step.name }}</div>
            <div class="step-description">{{ step.description }}</div>
          </div>
          <div class="step-toggle">
            <v-checkbox v-model="selectedSteps" :value="step.id" color="primary" hide-details density="compact" @click.stop></v-checkbox>
          </div>
        </div>
      </div>
    </div>

    <!-- Two-column Layout for Config and Logs -->
    <div class="config-logs-grid">
      <!-- Quick Config Panel -->
      <div class="config-card">
        <div class="config-header">
          <h2 class="config-title">Quick Configuration</h2>
          <v-btn color="primary" size="small" variant="text" @click="showConfigModal = true">
            Advanced Settings
          </v-btn>
        </div>

        <div class="config-content">
          <div class="config-item">
            <div class="config-item-header">
              <div class="config-item-title">Force Retraining</div>
              <v-switch v-model="pipelineConfig.force" color="primary" hide-details density="compact"></v-switch>
            </div>
            <div class="config-item-description">
              Force retraining of all models even if they were recently updated
            </div>
          </div>

          <div class="config-item">
            <div class="config-item-header">
              <div class="config-item-title">Schedule</div>
            </div>
            <div class="config-schedule">
              <v-select v-model="scheduleTime" :items="scheduleTimes" label="Daily run time" variant="outlined" density="compact" hide-details class="mr-2"></v-select>
              <v-btn size="small" color="primary" variant="tonal" :disabled="!scheduleTime" @click="saveSchedule">
                Save
              </v-btn>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Logs Panel -->
      <div class="logs-card">
        <div class="logs-header">
          <h2 class="logs-title">Recent Logs</h2>
          <v-btn icon="mdi-refresh" variant="text" density="comfortable" color="gray" @click="refreshLogs"></v-btn>
        </div>

        <div v-if="isLoading" class="logs-loading">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <div v-else-if="pipelineLogs.length === 0" class="logs-empty">
          No logs available
        </div>

        <div v-else class="logs-content">
          <div v-for="(log, index) in pipelineLogs.slice(0, 5)" :key="index" class="log-entry" :class="getLogClass(log.level)">
            <div class="log-time">{{ formatTime(log.timestamp) }}</div>
            <div class="log-message">{{ log.message }}</div>
          </div>

          <div v-if="pipelineLogs.length > 5" class="logs-more">
            <v-btn size="small" variant="text" color="primary" @click="showLogsModal = true">
              View All Logs
            </v-btn>
          </div>
        </div>
      </div>
    </div>

    <!-- Status Message -->
    <div v-if="statusMessage" class="status-message-container">
      <div class="status-message" :class="statusMessageClass">
        <v-icon :icon="statusMessageIcon" class="status-icon"></v-icon>
        <div class="status-message-content">
          <div class="status-message-title">{{ statusMessageTitle }}</div>
          <div class="status-message-text">{{ statusMessage }}</div>
        </div>
        <v-btn icon="mdi-close" variant="text" size="small" @click="clearStatusMessage" class="close-btn"></v-btn>
      </div>
    </div>

    <!-- Configuration Modal -->
    <v-dialog v-model="showConfigModal" max-width="600" scrollable>
      <div class="modal-card">
        <div class="modal-header">
          <h2 class="modal-title">Pipeline Configuration</h2>
          <v-btn icon="mdi-close" variant="text" @click="showConfigModal = false"></v-btn>
        </div>

        <div class="modal-content">
          <div class="modal-section">
            <h3 class="section-title">Steps to Execute</h3>
            <div class="steps-grid">
              <v-checkbox v-for="step in pipelineSteps" :key="step.id" v-model="selectedSteps" :value="step.id" :label="step.name" color="primary" hide-details density="comfortable"></v-checkbox>
            </div>
          </div>

          <div class="modal-section">
            <h3 class="section-title">Options</h3>
            <v-switch v-model="pipelineConfig.force" color="primary" hide-details density="comfortable" label="Force Retraining of All Models"></v-switch>

            <v-text-field v-model="pipelineConfig.maxSymbols" label="Maximum Symbols to Process" type="number" min="1" max="500" hint="Limit the number of symbols to process (leave empty for all)" persistent-hint density="comfortable" variant="outlined" class="mt-4"></v-text-field>
          </div>

          <div class="modal-section">
            <h3 class="section-title">Schedule Settings</h3>
            <div class="schedule-grid">
              <v-select v-model="scheduleTime" :items="scheduleTimes" label="Daily run time" variant="outlined" density="comfortable"></v-select>

              <v-select v-model="scheduleFrequency" :items="['Daily', 'Weekdays only', 'Custom']" label="Frequency" variant="outlined" density="comfortable"></v-select>
            </div>

            <div v-if="scheduleFrequency === 'Custom'" class="days-selection mt-3">
              <div class="text-sm font-medium mb-2">Days of Week</div>
              <div class="days-grid">
                <v-checkbox v-for="day in weekDays" :key="day.value" v-model="selectedDays" :value="day.value" :label="day.label" hide-details density="comfortable" class="mr-2"></v-checkbox>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <v-btn variant="text" color="gray" @click="showConfigModal = false">
            Cancel
          </v-btn>
          <v-btn color="primary" @click="saveConfig">
            Save Configuration
          </v-btn>
        </div>
      </div>
    </v-dialog>

    <!-- Logs Modal -->
    <v-dialog v-model="showLogsModal" max-width="800" scrollable>
      <div class="modal-card">
        <div class="modal-header">
          <h2 class="modal-title">Pipeline Logs</h2>
          <v-btn icon="mdi-close" variant="text" @click="showLogsModal = false"></v-btn>
        </div>

        <div class="modal-content logs-modal-content">
          <div v-for="(log, index) in pipelineLogs" :key="index" class="log-entry-full" :class="getLogClass(log.level)">
            <div class="log-time-full">{{ formatTime(log.timestamp) }}</div>
            <div class="log-message-full">{{ log.message }}</div>
          </div>

          <div v-if="pipelineLogs.length === 0" class="logs-empty-full">
            No logs available
          </div>
        </div>

        <div class="modal-footer">
          <v-btn color="primary" @click="showLogsModal = false">
            Close
          </v-btn>
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script>
import { api } from '@/plugins';
import { useSystemStore } from '@/store/system.store';

export default {
  name: 'PipelineDashboard',

  data() {
    return {
      // Pipeline status
      pipelineStatus: {
        status: 'idle', // idle, running, completed, failed
        progress: 0,
        message: null,
        currentStep: null,
        estimatedDurationMinutes: null,
        requestedBy: null,
        lastRun: null
      },

      // System statistics
      systemStats: {
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

      // Polling timer
      pollingInterval: null,
      pollingFrequency: 5000, // 5 seconds

      // WebSocket connection timeout
      wsConnectionTimeout: null,

      // Pipeline steps that match your backend's steps terminology
      pipelineSteps: [
        {
          id: 'data_import',
          name: 'Data Import',
          description: 'Imports EOD (End of Day) data for selected symbols'
        },
        {
          id: 'model_training',
          name: 'Model Training',
          description: 'Trains or updates prediction models'
        },
        {
          id: 'prediction',
          name: 'Prediction Generation',
          description: 'Generates market predictions using trained models'
        },
        {
          id: 'validation',
          name: 'Result Validation',
          description: 'Validates previous predictions against actual results'
        }
      ],

      // Selected steps for running the pipeline
      selectedSteps: ['data_import', 'model_training', 'prediction', 'validation'],

      // Status message
      statusMessage: null,
      statusMessageType: 'info', // info, success, error, warning

      // Pipeline configuration
      pipelineConfig: {
        force: false,
        maxSymbols: 100
      },

      // Schedule configuration
      scheduleTime: '02:00',
      scheduleFrequency: 'Daily',
      selectedDays: [1, 2, 3, 4, 5], // Mon-Fri by default
      scheduleTimes: [
        '00:00', '01:00', '02:00', '03:00', '04:00', '05:00',
        '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
        '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',
        '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'
      ],
      weekDays: [
        { label: 'Monday', value: 1 },
        { label: 'Tuesday', value: 2 },
        { label: 'Wednesday', value: 3 },
        { label: 'Thursday', value: 4 },
        { label: 'Friday', value: 5 },
        { label: 'Saturday', value: 6 },
        { label: 'Sunday', value: 0 }
      ],

      // UI state
      showConfigModal: false,
      showLogsModal: false,
      isLoading: false,

      // Pipeline logs
      pipelineLogs: [],

      // WebSocket connection
      wsConnection: null,
      wsConnected: false,

      // Last update time
      lastUpdateTime: null,

      // System store
      systemStore: useSystemStore(),

      // Reconnection settings
      wsReconnectAttempts: 0,
      wsMaxReconnectAttempts: 5,
      wsReconnectTimeout: null
    };
  },

  computed: {
    isRunning() {
      return this.pipelineStatus.status === 'running';
    },

    allStepsSelected() {
      return this.selectedSteps.length === this.pipelineSteps.length;
    },

    getStatusClass() {
      return (status) => {
        switch (status) {
          case 'running': return 'status-running';
          case 'completed': return 'status-completed';
          case 'failed': return 'status-failed';
          default: return 'status-idle';
        }
      };
    },

    statusMessageClass() {
      switch (this.statusMessageType) {
        case 'success': return 'message-success';
        case 'error': return 'message-error';
        case 'warning': return 'message-warning';
        default: return 'message-info';
      }
    },

    statusMessageIcon() {
      switch (this.statusMessageType) {
        case 'success': return 'mdi-check-circle';
        case 'error': return 'mdi-alert-circle';
        case 'warning': return 'mdi-alert';
        default: return 'mdi-information';
      }
    },

    statusMessageTitle() {
      switch (this.statusMessageType) {
        case 'success': return 'Success';
        case 'error': return 'Error';
        case 'warning': return 'Warning';
        default: return 'Information';
      }
    }
  },

  methods: {
    /**
     * Initialize WebSocket connection to System Status
     */
    initWebSocket() {
      // Close any existing connection
      this.closeWebSocket();

      try {
        // Get token from localStorage for authentication
        const token = localStorage.getItem('token');

        if (!token) {
          this.showStatusMessage('Authentication token not found. Live updates disabled.', 'warning');
          return;
        }

        // Use configured API base URL for consistency
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

        // Extract host from API URL for WebSocket connection
        let wsHost;
        try {
          const apiUrl = new URL(apiBaseUrl);
          wsHost = apiUrl.host;
        } catch (e) {
          // Fallback to window location if API URL parsing fails
          wsHost = window.location.host;
        }

        // Determine WebSocket protocol (wss for https, ws for http)
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

        // Format WebSocket URL
        const wsUrl = `${wsProtocol}//${wsHost}/system/status?token=${token}`;

        console.log('Connecting to WebSocket:', wsUrl);

        // Create new WebSocket connection
        this.wsConnection = new WebSocket(wsUrl);

        // Use bound methods to maintain 'this' context
        this.wsConnection.onopen = this.handleWsOpen.bind(this);
        this.wsConnection.onmessage = this.handleWsMessage.bind(this);
        this.wsConnection.onclose = this.handleWsClose.bind(this);
        this.wsConnection.onerror = this.handleWsError.bind(this);

        // Set connection timeout - abort if not connected within 5 seconds
        this.wsConnectionTimeout = setTimeout(() => {
          if (this.wsConnection && this.wsConnection.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket connection timeout');
            this.wsConnection.close();
            this.wsConnected = false;

            // Fallback to polling for updates
            this.startPolling();
          }
        }, 5000);
      } catch (error) {
        console.error('WebSocket initialization error:', error);

        // Fallback to polling for updates
        this.startPolling();
      }
    },

    /**
     * Handle WebSocket open event
     */
    handleWsOpen() {
      this.wsConnected = true;
      this.wsReconnectAttempts = 0;

      // Clear connection timeout
      if (this.wsConnectionTimeout) {
        clearTimeout(this.wsConnectionTimeout);
        this.wsConnectionTimeout = null;
      }

      // Stop polling if it was started as a fallback
      this.stopPolling();

      console.log('WebSocket connected to system status');
    },

    /**
     * Handle WebSocket messages
     */
    handleWsMessage(event) {
      try {
        // Parse message data
        const data = JSON.parse(event.data);

        // Update timestamp
        this.updateLastUpdateTime();

        // Handle different message types
        if (data.type === 'connected') {
          // Connection successful - no action needed
          console.log('WebSocket connection confirmed:', data.message);
        }
        else if (data.type === 'status_update') {
          // Update system status
          this.updateSystemStats(data.status);

          // Update pipeline status if running
          if (data.pipeline_status) {
            this.updatePipelineStatus(data.pipeline_status);
          }

          // Update logs if present
          if (data.logs) {
            this.updateLogs(data.logs);
          }
        }
        else if (data.type === 'pipeline_update') {
          // Update pipeline status
          this.updatePipelineStatus(data.pipeline_status);

          // Add log entry if present
          if (data.log_entry) {
            this.pipelineLogs.unshift(data.log_entry);

            // Keep logs to a reasonable size
            if (this.pipelineLogs.length > 100) {
              this.pipelineLogs = this.pipelineLogs.slice(0, 100);
            }
          }
        }
        else if (data.type === 'error') {
          // Show error message
          this.showStatusMessage(data.message, 'error');
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    },

    /**
     * Handle WebSocket close event
     */
    handleWsClose(event) {
      this.wsConnected = false;

      // Don't attempt to reconnect if closed normally
      if (event.code === 1000 || event.code === 1001) {
        console.log('WebSocket closed normally');
        return;
      }

      // Attempt to reconnect
      this.attemptReconnect();

      // Start polling as fallback
      this.startPolling();
    },

    /**
     * Handle WebSocket error
     */
    handleWsError(error) {
      console.error('WebSocket error:', error);
      this.wsConnected = false;

      // Attempt to reconnect
      this.attemptReconnect();

      // Start polling as fallback
      this.startPolling();
    },

    /**
     * Attempt to reconnect WebSocket
     */
    attemptReconnect() {
      // Clear any existing reconnect timeout
      if (this.wsReconnectTimeout) {
        clearTimeout(this.wsReconnectTimeout);
      }

      // Check if max reconnect attempts reached
      if (this.wsReconnectAttempts >= this.wsMaxReconnectAttempts) {
        this.startPolling();
        return;
      }

      // Increment reconnect attempts
      this.wsReconnectAttempts++;

      // Exponential backoff for reconnect (1s, 2s, 4s, 8s, 16s)
      const delay = Math.min(1000 * Math.pow(2, this.wsReconnectAttempts - 1), 16000);

      console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.wsReconnectAttempts})`);

      // Set timeout for reconnect
      this.wsReconnectTimeout = setTimeout(() => {
        if (!this.wsConnected) {
          this.initWebSocket();
        }
      }, delay);
    },

    /**
     * Close WebSocket connection
     */
    closeWebSocket() {
      if (this.wsConnection) {
        this.wsConnection.onclose = null; // Prevent reconnect attempts on intentional close
        this.wsConnection.close();
        this.wsConnection = null;
        this.wsConnected = false;
      }

      // Clear any reconnect timeout
      if (this.wsReconnectTimeout) {
        clearTimeout(this.wsReconnectTimeout);
        this.wsReconnectTimeout = null;
      }

      // Clear connection timeout if exists
      if (this.wsConnectionTimeout) {
        clearTimeout(this.wsConnectionTimeout);
        this.wsConnectionTimeout = null;
      }
    },

    /**
     * Start polling for updates as a fallback mechanism
     */
    startPolling() {
      // Stop any existing polling
      this.stopPolling();

      // Start new polling interval
      this.pollingInterval = setInterval(async () => {
        try {
          // Fetch system status
          const response = await api.get('/system/status');

          // Update data with response
          if (response && response.data) {
            this.updateSystemStats(response.data);

            if (response.data.pipeline_status) {
              this.updatePipelineStatus(response.data.pipeline_status);
            }

            if (response.data.logs) {
              this.updateLogs(response.data.logs);
            }

            // Update timestamp
            this.updateLastUpdateTime();
          }
        } catch (error) {
          console.error('Polling error:', error);
        }
      }, this.pollingFrequency);

      console.log('Started polling for updates every', this.pollingFrequency / 1000, 'seconds');
    },

    /**
     * Stop polling for updates
     */
    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
        console.log('Stopped polling for updates');
      }
    },

    /**
     * Refresh pipeline logs
     */
    async refreshLogs() {
      this.isLoading = true;

      try {
        // In a real implementation, this would call an API endpoint to get logs
        // For now, we'll simulate an API call
        const response = await api.get('/system/logs', { params: { limit: 50 } })
          .catch(() => ({ data: { logs: [] } }));

        this.pipelineLogs = response.data.logs || [];
      } catch (error) {
        console.error('Failed to fetch logs:', error);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Save the scheduled pipeline configuration
     */
    saveSchedule() {
      // In a real implementation, this would call an API endpoint to set the schedule
      this.showStatusMessage(`Pipeline scheduled to run daily at ${this.scheduleTime}`, 'success');
    },

    /**
     * Run the pipeline using the configured settings
     */
    async runPipeline() {
      try {
        // Update UI state
        this.pipelineStatus.status = 'running';
        this.pipelineStatus.progress = 0;
        this.clearStatusMessage();

        // Prepare request payload based on your API's PipelineRunRequest model
        const payload = {
          force: this.pipelineConfig.force,
          steps: this.selectedSteps.length > 0 ? this.selectedSteps : null,
          max_symbols: this.pipelineConfig.maxSymbols || null
        };

        // Call API to run pipeline
        const response = await api.post('/system/run-pipeline', payload);
        const data = response.data;

        // Update status with API response
        this.updatePipelineStatus({
          status: 'running',
          message: data.message,
          start_time: data.start_time,
          requested_by: data.requested_by,
          estimated_duration_minutes: data.estimated_duration_minutes,
          steps: data.steps || []
        });

        // Show success message
        this.showStatusMessage('Pipeline execution started successfully', 'success');

        // Get a baseline of system stats
        this.fetchInitialSystemStatus();
      } catch (error) {
        console.error('Failed to start pipeline:', error);
        this.pipelineStatus.status = 'failed';
        this.showStatusMessage(`Failed to start pipeline: ${error.response?.data?.detail || error.message}`, 'error');
      }
    },

    /**
     * Fetch initial system status via HTTP
     */
    async fetchInitialSystemStatus() {
      try {
        // Use the api service to get system status
        const response = await api.get('/system/status');

        // Get response data
        const data = response.data;

        // Update system stats and pipeline status
        this.updateSystemStats(data);

        if (data.pipeline_status) {
          this.updatePipelineStatus(data.pipeline_status);
        }

        // Fetch logs if available
        if (data.logs) {
          this.pipelineLogs = data.logs;
        } else {
          // Otherwise fetch logs separately
          this.refreshLogs();
        }

        // Update timestamp
        this.updateLastUpdateTime();
      } catch (error) {
        console.error('Failed to fetch initial system status:', error);
      }
    },

    /**
     * Update system stats
     */
    updateSystemStats(data) {
      // Update system statistics
      this.systemStats = {
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

    /**
     * Update pipeline status
     */
    updatePipelineStatus(pipelineStatus) {
      if (!pipelineStatus) return;

      // Track previous status to detect changes
      const prevStatus = this.pipelineStatus.status;

      this.pipelineStatus = {
        status: pipelineStatus.status || 'idle',
        message: pipelineStatus.message,
        currentStep: pipelineStatus.current_step,
        requestedBy: pipelineStatus.requested_by,
        estimatedDurationMinutes: pipelineStatus.estimated_duration_minutes,
        progress: this.calculateProgress(pipelineStatus),
        lastRun: pipelineStatus.last_run || this.pipelineStatus.lastRun
      };

      // If pipeline just completed, show message
      if (pipelineStatus.status === 'completed' && prevStatus === 'running') {
        this.showStatusMessage('Pipeline execution completed successfully', 'success');

        // Refresh system stats after completion
        setTimeout(() => {
          this.fetchInitialSystemStatus();
        }, 1000);
      }
      // If pipeline just failed, show error
      else if (pipelineStatus.status === 'failed' && prevStatus === 'running') {
        this.showStatusMessage(pipelineStatus.message || 'Pipeline execution failed', 'error');
      }
    },

    /**
     * Update logs
     */
    updateLogs(logs) {
      if (Array.isArray(logs) && logs.length > 0) {
        this.pipelineLogs = logs;
      }
    },

    /**
     * Calculate progress percentage from pipeline status
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
     * Save pipeline configuration
     */
    saveConfig() {
      // Close the modal - configuration is saved in the data properties
      this.showConfigModal = false;

      // Prepare config for API submission
      const config = {
        default_steps: this.selectedSteps,
        force_retrain: this.pipelineConfig.force,
        max_symbols: this.pipelineConfig.maxSymbols,
        schedule: {
          time: this.scheduleTime,
          frequency: this.scheduleFrequency,
          days: this.scheduleFrequency === 'Custom' ? this.selectedDays :
            this.scheduleFrequency === 'Weekdays only' ? [1, 2, 3, 4, 5] :
              [0, 1, 2, 3, 4, 5, 6]
        }
      };

      // In a real implementation, this would save to the backend
      // api.post('/system/config', config)

      this.showStatusMessage('Pipeline configuration saved', 'success');
    },

    /**
     * Toggle step selection
     */
    toggleStep(stepId) {
      const index = this.selectedSteps.indexOf(stepId);
      if (index === -1) {
        this.selectedSteps.push(stepId);
      } else {
        this.selectedSteps.splice(index, 1);
      }
    },

    /**
     * Select or deselect all steps
     */
    selectAllSteps() {
      if (this.allStepsSelected) {
        this.selectedSteps = [];
      } else {
        this.selectedSteps = this.pipelineSteps.map(step => step.id);
      }
    },

    /**
     * Show a status message
     */
    showStatusMessage(message, type = 'info') {
      this.statusMessage = message;
      this.statusMessageType = type;

      // Clear status message after 5 seconds
      setTimeout(() => {
        if (this.statusMessage === message) {
          this.clearStatusMessage();
        }
      }, 5000);
    },

    /**
     * Clear status message
     */
    clearStatusMessage() {
      this.statusMessage = null;
    },

    /**
     * Update the last refresh timestamp
     */
    updateLastUpdateTime() {
      const now = new Date();
      this.lastUpdateTime = now.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    /**
     * Format date
     */
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },

    /**
     * Format time
     */
    formatTime(timeString) {
      if (!timeString) return '';
      const date = new Date(timeString);
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },

    /**
     * Get CSS class for log entry based on level
     */
    getLogClass(level) {
      switch (level?.toLowerCase()) {
        case 'error':
          return 'log-error';
        case 'warning':
          return 'log-warning';
        case 'success':
          return 'log-success';
        case 'info':
        default:
          return 'log-info';
      }
    },

    /**
     * Get CSS class for step indicator
     */
    getStepClass(step, pipelineStatus) {
      const status = this.getStepStatus(step, pipelineStatus);
      switch (status) {
        case 'running': return 'step-indicator-running';
        case 'completed': return 'step-indicator-completed';
        case 'failed': return 'step-indicator-failed';
        default: return 'step-indicator-idle';
      }
    },

    /**
     * Get status of a step based on current pipeline status
     */
    getStepStatus(step, pipelineStatus) {
      if (pipelineStatus.status !== 'running') {
        return 'idle';
      }

      if (pipelineStatus.currentStep === step.name) {
        return 'running';
      }

      // Find index of current step
      const currentStepIndex = this.pipelineSteps.findIndex(s => s.name === pipelineStatus.currentStep);
      const thisStepIndex = this.pipelineSteps.findIndex(s => s.id === step.id);

      if (currentStepIndex === -1 || thisStepIndex === -1) {
        return 'idle';
      }

      if (thisStepIndex < currentStepIndex) {
        return 'completed';
      }

      return 'idle';
    },

    /**
     * Format time remaining
     */
    formatTimeRemaining(minutes) {
      if (!minutes) return 'Unknown';

      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;

      if (hours > 0) {
        return `${hours}h ${mins}m`;
      }
      return `${mins}m`;
    },

    /**
     * Format size in MB to readable format
     */
    formatSize(size) {
      if (size < 1) {
        return `${(size * 1024).toFixed(0)} KB`;
      }
      return `${size.toFixed(1)} MB`;
    },

    /**
     * Capitalize first letter of string
     */
    capitalizeFirst(str) {
      if (!str) return '';
      return str.charAt(0).toUpperCase() + str.slice(1);
    },

    /**
     * Get color for success rate progress bar
     */
    getSuccessRateColor(rate) {
      if (!rate) return 'gray';
      if (rate < 40) return 'error';
      if (rate < 70) return 'warning';
      return 'success';
    }
  },

  mounted() {
    // Fetch initial system status
    this.fetchInitialSystemStatus();

    // Initialize WebSocket connection
    this.initWebSocket();
  },

  beforeUnmount() {
    // Close WebSocket connection
    this.closeWebSocket();

    // Stop polling if active
    this.stopPolling();

    // Clear any timeouts
    if (this.wsConnectionTimeout) {
      clearTimeout(this.wsConnectionTimeout);
    }
  }
};
</script>

<style lang="postcss" scoped>
/* Base layout */
.pipeline-dashboard {
  @apply max-w-7xl mx-auto space-y-6;
}

/* Status Card */
.status-card {
  @apply bg-white rounded-xl border border-gray-200 p-6;
}

.status-header {
  @apply flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4;
}

.status-info {
  @apply flex flex-col;
}

.status-title-row {
  @apply flex items-center gap-3;
}

.status-title {
  @apply text-xl font-bold text-gray-800;
}

.connection-status {
  @apply flex items-center text-xs font-medium rounded-full px-2.5 py-1;
}

.connection-status.connected {
  @apply bg-green-50 text-green-600;
}

.connection-status:not(.connected) {
  @apply bg-gray-100 text-gray-500;
}

.status-dot {
  @apply w-2 h-2 rounded-full mr-1.5;
}

.connected .status-dot {
  @apply bg-green-500;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }

  50% {
    opacity: 1;
  }

  100% {
    opacity: 0.6;
  }
}

.status-badge {
  @apply inline-flex px-3.5 py-1 rounded-full text-xs font-medium mt-2;
}

.status-idle {
  @apply bg-gray-100 text-gray-600;
}

.status-running {
  @apply bg-blue-100 text-blue-700;
}

.status-completed {
  @apply bg-green-100 text-green-700;
}

.status-failed {
  @apply bg-red-100 text-red-700;
}

.action-buttons {
  @apply flex gap-2;
}

.progress-container {
  @apply mt-5 bg-gray-50 rounded-lg p-4;
}

.progress-header {
  @apply flex justify-between items-center mb-2;
}

.progress-message {
  @apply text-sm font-medium text-gray-800;
}

.progress-info {
  @apply flex items-center gap-2 text-xs;
}

.progress-percentage {
  @apply font-semibold text-primary;
}

.progress-time {
  @apply text-gray-500;
}

/* Stats Grid */
.stats-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6;
}

.stat-card {
  @apply bg-white rounded-xl border border-gray-200 p-6;
}

.stat-card-header {
  @apply flex justify-between items-center mb-5;
}

.stat-card-title {
  @apply text-base font-bold text-gray-800;
}

.last-update {
  @apply text-xs text-gray-500 bg-gray-50 px-2.5 py-1 rounded-full;
}

.stat-grid {
  @apply grid grid-cols-2 gap-5;
}

.stat-item {
  @apply flex items-start gap-3 p-1 rounded-lg transition-colors duration-200;
}

.stat-icon {
  @apply w-10 h-10 flex items-center justify-center rounded-lg;
}

.stat-content {
  @apply flex-1;
}

.stat-value {
  @apply text-lg font-semibold text-gray-900;
}

.stat-label {
  @apply text-xs text-gray-500;
}

.success-rate-container {
  @apply mt-6 bg-gray-50 p-4 rounded-lg;
}

.success-rate-header {
  @apply flex justify-between items-center mb-2;
}

.success-rate-label {
  @apply text-sm text-gray-600;
}

.success-rate-value {
  @apply text-sm font-medium;
}

/* Steps Card */
.steps-card {
  @apply bg-white rounded-xl border border-gray-200 p-6;
}

.steps-header {
  @apply flex justify-between items-center mb-5;
}

.steps-title {
  @apply text-base font-bold text-gray-800;
}

.steps-actions {
  @apply flex;
}

.select-btn {
  @apply text-xs font-medium;
}

.steps-container {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-4;
}

.step-item {
  @apply flex items-center bg-gray-50 hover:bg-gray-100 rounded-lg p-3 border border-gray-100 transition-colors duration-200 cursor-pointer;
}

.step-running {
  @apply bg-blue-50 border-blue-200;
  animation: step-pulse 2s infinite alternate;
}

@keyframes step-pulse {
  0% {
    background-color: rgba(219, 234, 254, 0.8);
  }

  100% {
    background-color: rgba(219, 234, 254, 0.4);
  }
}

.step-selected {
  @apply border-primary;
}

.step-indicator {
  @apply w-9 h-9 rounded-full flex items-center justify-center mr-3 text-sm font-medium;
}

.step-indicator-idle {
  @apply bg-gray-200 text-gray-700;
}

.step-indicator-running {
  @apply bg-blue-500 text-white;
}

.step-indicator-completed {
  @apply bg-green-500 text-white;
}

.step-indicator-failed {
  @apply bg-red-500 text-white;
}

.step-content {
  @apply flex-1;
}

.step-title {
  @apply text-sm font-medium text-gray-700;
}

.step-description {
  @apply text-xs text-gray-500 mt-1;
}

.step-toggle {
  @apply ml-auto;
}

/* Configuration and Logs Grid */
.config-logs-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6;
}

.config-card,
.logs-card {
  @apply bg-white rounded-xl border border-gray-200 p-6;
}

.config-header,
.logs-header {
  @apply flex justify-between items-center mb-5;
}

.config-title,
.logs-title {
  @apply text-base font-bold text-gray-800;
}

.config-content {
  @apply space-y-4;
}

.config-item {
  @apply bg-gray-50 rounded-lg p-4 border border-gray-100;
}

.config-item-header {
  @apply flex justify-between items-center;
}

.config-item-title {
  @apply text-sm font-medium text-gray-700;
}

.config-item-description {
  @apply text-xs text-gray-500 mt-1.5;
}

.config-schedule {
  @apply flex mt-3 gap-2 items-start;
}

/* Logs styling */
.logs-loading {
  @apply flex justify-center items-center py-10;
}

.logs-empty {
  @apply flex justify-center items-center py-10 text-gray-500 text-sm;
}

.logs-content {
  @apply bg-gray-50 rounded-lg border border-gray-100 max-h-64 overflow-y-auto;
}

.log-entry {
  @apply flex px-3.5 py-2.5 border-b border-gray-100 last:border-0 hover:bg-gray-100/50 transition-colors duration-150;
}

.log-time {
  @apply text-gray-500 mr-3 whitespace-nowrap;
}

.log-message {
  @apply flex-1 truncate;
}

.logs-more {
  @apply flex justify-center py-2 border-t border-gray-100;
}

.log-info {
  @apply text-gray-700;
}

.log-error {
  @apply text-red-600 bg-red-50;
}

.log-warning {
  @apply text-amber-600 bg-amber-50;
}

.log-success {
  @apply text-green-600 bg-green-50;
}

/* Status Message */
.status-message-container {
  @apply fixed bottom-6 right-6 z-50 max-w-md;
}

.status-message {
  @apply flex items-start p-4 rounded-lg border;
  animation: slide-in 0.3s ease-out;
}

@keyframes slide-in {
  from {
    transform: translateY(20px);
    opacity: 0;
  }

  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.message-info {
  @apply bg-blue-50 text-blue-700 border-blue-200;
}

.message-success {
  @apply bg-green-50 text-green-700 border-green-200;
}

.message-warning {
  @apply bg-amber-50 text-amber-700 border-amber-200;
}

.message-error {
  @apply bg-red-50 text-red-700 border-red-200;
}

.status-icon {
  @apply mr-3 mt-0.5;
}

.status-message-content {
  @apply flex-1;
}

.status-message-title {
  @apply font-medium;
}

.status-message-text {
  @apply text-sm;
}

.close-btn {
  @apply ml-2 -mt-1 -mr-1 opacity-70 hover:opacity-100 transition-opacity duration-200;
}

/* Modal styling */
.modal-card {
  @apply bg-white rounded-xl border border-gray-200 overflow-hidden;
}

.modal-header {
  @apply flex justify-between items-center p-5 border-b border-gray-200 bg-gray-50;
}

.modal-title {
  @apply text-lg font-bold text-gray-800;
}

.modal-content {
  @apply p-5 max-h-[70vh] overflow-y-auto;
}

.modal-section {
  @apply mb-6 last:mb-0;
}

.section-title {
  @apply text-base font-medium mb-3 pb-2 border-b border-gray-200 text-gray-700;
}

.steps-grid {
  @apply grid grid-cols-2 gap-4;
}

.schedule-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-4;
}

.days-selection {
  @apply bg-gray-50 p-4 rounded-lg border border-gray-100;
}

.days-grid {
  @apply flex flex-wrap gap-x-8 gap-y-2;
}

.modal-footer {
  @apply flex justify-end gap-3 p-5 bg-gray-50 border-t border-gray-200;
}

/* Logs Modal Specific */
.logs-modal-content {
  @apply font-mono p-0;
}

.log-entry-full {
  @apply flex px-4 py-2.5 border-b border-gray-200 last:border-0 hover:bg-gray-50 transition-colors duration-150;
}

.log-time-full {
  @apply text-gray-500 mr-4 whitespace-nowrap font-medium;
}

.log-message-full {
  @apply flex-1;
}

.logs-empty-full {
  @apply flex justify-center items-center py-16 text-gray-500;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .status-header {
    @apply flex-col items-start gap-3;
  }

  .action-buttons {
    @apply self-end;
  }

  .steps-container {
    @apply grid-cols-1;
  }

  .stat-grid {
    @apply grid-cols-1;
  }

  .steps-grid,
  .schedule-grid {
    @apply grid-cols-1;
  }
}
</style>