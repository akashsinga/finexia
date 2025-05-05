<template>
  <div class="pipeline-dashboard">
    <!-- Header Section with Pipeline Status -->
    <div class="dashboard-header bg-white rounded-xl shadow-sm border border-gray-200 p-5">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-xl font-bold text-gray-800">Data Pipeline</h1>
          <div class="flex items-center mt-1">
            <div class="status-badge" :class="getStatusBadgeClass(pipelineStatus.status)">
              {{ capitalizeFirst(pipelineStatus.status) }}
            </div>
            <span v-if="lastUpdateTime" class="text-xs text-gray-500 ml-2">
              Last updated: {{ lastUpdateTime }}
            </span>
            <div v-if="wsConnected" class="ml-2 flex items-center text-xs text-green-600">
              <div class="h-2 w-2 rounded-full bg-green-500 mr-1"></div>
              <span>Live</span>
            </div>
          </div>
        </div>
        <div class="flex gap-2">
          <v-btn color="primary" size="small" variant="tonal" prepend-icon="mdi-cog" @click="showConfigModal = true">
            Configure
          </v-btn>
          <v-btn color="primary" size="small" variant="elevated" prepend-icon="mdi-play" :loading="isRunning" :disabled="isRunning" @click="runPipeline">
            Run Pipeline
          </v-btn>
        </div>
      </div>

      <!-- Progress bar when pipeline is running -->
      <div v-if="isRunning" class="mt-4">
        <div class="flex justify-between items-center mb-1">
          <div class="text-sm font-medium">
            {{ pipelineStatus.message || 'Running pipeline...' }}
          </div>
          <div class="text-xs">
            {{ Math.round(pipelineStatus.progress) }}% complete
            <span v-if="pipelineStatus.estimatedDurationMinutes" class="ml-2">
              ({{ formatTimeRemaining(pipelineStatus.estimatedDurationMinutes) }} remaining)
            </span>
          </div>
        </div>
        <v-progress-linear :model-value="pipelineStatus.progress" color="primary" height="8" rounded></v-progress-linear>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      <!-- System Stats Card -->
      <div class="stats-card bg-white rounded-xl shadow-sm border border-gray-200 p-5">
        <h2 class="text-base font-bold text-gray-800 mb-4">System Statistics</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="stat-item">
            <div class="text-xs text-gray-500">Total Predictions</div>
            <div class="text-lg font-semibold">{{ systemStats.totalPredictions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Today's Predictions</div>
            <div class="text-lg font-semibold">{{ systemStats.todayPredictions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Yesterday's Predictions</div>
            <div class="text-lg font-semibold">{{ systemStats.yesterdayPredictions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Verified Predictions</div>
            <div class="text-lg font-semibold">{{ systemStats.verifiedPredictions || 0 }}</div>
          </div>
          <div class="stat-item col-span-2">
            <div class="text-xs text-gray-500">Success Rate</div>
            <div class="flex items-center">
              <div class="text-lg font-semibold">{{ (systemStats.verifiedPredictionPercent || 0).toFixed(1) }}%</div>
              <v-progress-linear :model-value="systemStats.verifiedPredictionPercent || 0" color="success" height="4" class="ml-3 flex-grow max-w-[200px]"></v-progress-linear>
            </div>
          </div>
        </div>
      </div>

      <!-- Model Stats Card -->
      <div class="models-card bg-white rounded-xl shadow-sm border border-gray-200 p-5">
        <h2 class="text-base font-bold text-gray-800 mb-4">Model Information</h2>
        <div class="grid grid-cols-2 gap-4">
          <div class="stat-item">
            <div class="text-xs text-gray-500">Direction Predictions</div>
            <div class="text-lg font-semibold">{{ systemStats.directionPredictions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Recent Model Training</div>
            <div class="text-lg font-semibold">{{ systemStats.recentModelTrainingCount || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Model Files</div>
            <div class="text-lg font-semibold">{{ systemStats.modelFileCount || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Model Directory Size</div>
            <div class="text-lg font-semibold">{{ formatSize(systemStats.modelDirectorySizeMb || 0) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pipeline Steps Section -->
    <div class="steps-card bg-white rounded-xl shadow-sm border border-gray-200 p-5 mt-6">
      <h2 class="text-base font-bold text-gray-800 mb-4">Pipeline Steps</h2>
      <div class="steps-container">
        <div v-for="(step, index) in pipelineSteps" :key="step.id" class="step-item" :class="{ 'step-running': isRunning && pipelineStatus.currentStep === step.name }">
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
            <v-checkbox v-model="selectedSteps" :value="step.id" color="primary" hide-details density="compact"></v-checkbox>
          </div>
        </div>
      </div>
    </div>

    <!-- Pipeline Configuration Section -->
    <div class="config-card bg-white rounded-xl shadow-sm border border-gray-200 p-5 mt-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-base font-bold text-gray-800">Quick Configuration</h2>
        <v-btn color="primary" size="small" variant="tonal" @click="showConfigModal = true">
          Advanced
        </v-btn>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="config-group">
          <div class="text-sm font-medium mb-2">Force Retraining</div>
          <v-switch v-model="pipelineConfig.force" color="primary" hide-details density="compact" label="Force retraining of all models"></v-switch>
        </div>
      </div>
    </div>

    <!-- Status Message -->
    <div v-if="statusMessage" class="status-message mt-6 p-4 rounded-lg" :class="statusMessageClass">
      <div class="flex items-start">
        <v-icon :icon="statusMessageIcon" class="mr-2 mt-0.5"></v-icon>
        <div>
          <div class="font-medium">{{ statusMessageTitle }}</div>
          <div class="text-sm">{{ statusMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Configuration Modal -->
    <v-dialog v-model="showConfigModal" max-width="600">
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="p-5 border-b border-gray-200">
          <h2 class="text-lg font-bold">Pipeline Configuration</h2>
        </div>

        <div class="p-5">
          <h3 class="text-base font-medium mb-3">Steps to Execute</h3>
          <div class="grid grid-cols-2 gap-3 mb-5">
            <v-checkbox v-for="step in pipelineSteps" :key="step.id" v-model="selectedSteps" :value="step.id" :label="step.name" color="primary" hide-details density="compact"></v-checkbox>
          </div>

          <h3 class="text-base font-medium mb-3">Options</h3>
          <div class="mb-3">
            <v-switch v-model="pipelineConfig.force" color="primary" hide-details density="compact" label="Force Retraining of All Models"></v-switch>
          </div>
        </div>

        <div class="p-4 bg-gray-50 border-t border-gray-200 flex justify-end gap-2">
          <v-btn variant="text" color="gray" @click="showConfigModal = false">
            Cancel
          </v-btn>
          <v-btn color="primary" @click="saveConfig">
            Save Configuration
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
        requestedBy: null
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
        force: false
      },

      // UI state
      showConfigModal: false,

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

    statusMessageClass() {
      switch (this.statusMessageType) {
        case 'success': return 'bg-green-100 text-green-800';
        case 'error': return 'bg-red-100 text-red-800';
        case 'warning': return 'bg-amber-100 text-amber-800';
        default: return 'bg-blue-100 text-blue-800';
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

        // Connect to system status WebSocket with token
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const baseUrl = `${wsProtocol}//${window.location.host}`;
        const wsUrl = `${baseUrl}/system/status?token=${token}`;

        this.wsConnection = new WebSocket(wsUrl);

        // WebSocket event handlers
        this.wsConnection.onopen = this.handleWsOpen;
        this.wsConnection.onmessage = this.handleWsMessage;
        this.wsConnection.onclose = this.handleWsClose;
        this.wsConnection.onerror = this.handleWsError;
      } catch (error) {
        console.error('WebSocket initialization error:', error);
        this.showStatusMessage('Failed to establish live connection', 'error');
      }
    },

    /**
     * Handle WebSocket open event
     */
    handleWsOpen() {
      this.wsConnected = true;
      this.wsReconnectAttempts = 0;
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
        }
        else if (data.type === 'pipeline_update') {
          // Update pipeline status
          this.updatePipelineStatus(data.pipeline_status);
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
    },

    /**
     * Handle WebSocket error
     */
    handleWsError(error) {
      console.error('WebSocket error:', error);
      this.wsConnected = false;

      // Show error message only on first occurrence
      if (this.wsReconnectAttempts === 0) {
        this.showStatusMessage('Connection error. Attempting to reconnect...', 'warning');
      }

      // Attempt to reconnect
      this.attemptReconnect();
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
        this.showStatusMessage('Failed to reconnect. Please refresh the page.', 'error');
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
          steps: this.selectedSteps.length > 0 ? this.selectedSteps : null
        };

        // Call API to run pipeline using the api service
        const response = await api.post('/system/run-pipeline', payload);

        // Get response data
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

      this.pipelineStatus = {
        status: pipelineStatus.status || 'idle',
        message: pipelineStatus.message,
        currentStep: pipelineStatus.current_step,
        requestedBy: pipelineStatus.requested_by,
        estimatedDurationMinutes: pipelineStatus.estimated_duration_minutes,
        progress: this.calculateProgress(pipelineStatus)
      };

      // If pipeline just completed, show message
      if (pipelineStatus.status === 'completed' && this.isRunning) {
        this.showStatusMessage('Pipeline execution completed successfully', 'success');
      }
      // If pipeline just failed, show error
      else if (pipelineStatus.status === 'failed' && this.isRunning) {
        this.showStatusMessage('Pipeline execution failed', 'error');
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
      // Just close the modal - configuration is saved in the data properties
      this.showConfigModal = false;
      this.showStatusMessage('Pipeline configuration saved', 'success');
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
     * Get CSS class for status badge
     */
    getStatusBadgeClass(status) {
      switch (status) {
        case 'running': return 'bg-blue-100 text-blue-800';
        case 'completed': return 'bg-green-100 text-green-800';
        case 'failed': return 'bg-red-100 text-red-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    },

    /**
     * Get CSS class for step indicator
     */
    getStepClass(step, pipelineStatus) {
      const status = this.getStepStatus(step, pipelineStatus);
      switch (status) {
        case 'running': return 'bg-blue-500 text-white';
        case 'completed': return 'bg-green-500 text-white';
        case 'failed': return 'bg-red-500 text-white';
        default: return 'bg-gray-200 text-gray-700';
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
  }
};
</script>

<style lang="postcss" scoped>
.pipeline-dashboard {
  @apply max-w-7xl mx-auto;
}

/* Status Badge */
.status-badge {
  @apply px-2.5 py-0.5 rounded-full text-xs font-medium;
}

/* Statistics Cards */
.stat-item {
  @apply bg-gray-50 rounded-lg p-3 border border-gray-100;
}

/* Pipeline Steps */
.steps-container {
  @apply space-y-3;
}

.step-item {
  @apply flex items-center bg-gray-50 rounded-lg p-3 border border-gray-100 transition-colors duration-200;
}

.step-running {
  @apply bg-blue-50 border-blue-200;
}
</style>