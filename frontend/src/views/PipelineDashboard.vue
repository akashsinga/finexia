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
            <div class="text-lg font-semibold">{{ systemStore.stats.totalPredictions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Today's Predictions</div>
            <div class="text-lg font-semibold">{{ systemStore.stats.todayPredictions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Yesterday's Predictions</div>
            <div class="text-lg font-semibold">{{ systemStore.stats.yesterdayPredictions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Verified Predictions</div>
            <div class="text-lg font-semibold">{{ systemStore.stats.verifiedPredictions || 0 }}</div>
          </div>
          <div class="stat-item col-span-2">
            <div class="text-xs text-gray-500">Success Rate</div>
            <div class="flex items-center">
              <div class="text-lg font-semibold">{{ (systemStore.stats.verifiedPredictionPercent || 0).toFixed(1) }}%</div>
              <v-progress-linear :model-value="systemStore.stats.verifiedPredictionPercent || 0" color="success" height="4" class="ml-3 flex-grow max-w-[200px]"></v-progress-linear>
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
            <div class="text-lg font-semibold">{{ systemStore.stats.directionPredictions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Recent Model Training</div>
            <div class="text-lg font-semibold">{{ systemStore.stats.recentModelTrainingCount || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Model Files</div>
            <div class="text-lg font-semibold">{{ systemStore.stats.modelFileCount || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="text-xs text-gray-500">Model Directory Size</div>
            <div class="text-lg font-semibold">{{ formatSize(systemStore.stats.modelDirectorySizeMb || 0) }}</div>
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

      // System store
      systemStore: useSystemStore()
    };
  },

  computed: {
    isRunning() {
      return this.pipelineStatus.status === 'running';
    },

    lastUpdateTime() {
      return this.systemStore.lastUpdateTime;
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

        // Use the system store to run the pipeline
        await this.systemStore.triggerPipelineRun(payload);

        // Show success message
        this.showStatusMessage('Pipeline execution started successfully', 'success');

        // Start monitoring pipeline status
        this.monitorPipelineStatus();
      } catch (error) {
        console.error('Failed to start pipeline:', error);
        this.pipelineStatus.status = 'failed';
        this.showStatusMessage(`Failed to start pipeline: ${error.message}`, 'error');
      }
    },

    /**
     * Monitor pipeline status
     */
    monitorPipelineStatus() {
      // Poll for status updates
      const checkStatus = async () => {
        try {
          // Refresh system status
          await this.systemStore.fetchSystemStatus();

          // Update local pipeline status from store
          if (this.systemStore.pipelineStatus) {
            this.pipelineStatus = {
              ...this.pipelineStatus,
              ...this.systemStore.pipelineStatus
            };

            // If pipeline is complete, show message
            if (this.pipelineStatus.status === 'completed') {
              this.showStatusMessage('Pipeline execution completed successfully', 'success');
              return; // Stop monitoring
            }
            // If pipeline failed, show error
            else if (this.pipelineStatus.status === 'failed') {
              this.showStatusMessage('Pipeline execution failed', 'error');
              return; // Stop monitoring
            }
          }

          // Continue monitoring if still running
          if (this.pipelineStatus.status === 'running') {
            setTimeout(checkStatus, 5000);
          }
        } catch (error) {
          console.error('Error monitoring pipeline status:', error);
          setTimeout(checkStatus, 5000); // Continue despite error
        }
      };

      // Start monitoring
      checkStatus();
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
    // Fetch initial system status using the store
    this.systemStore.fetchSystemStatus();
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
  @apply flex items-center bg-gray-50 rounded-lg p-3 border border-gray-100;
}

.step-running {
  @apply bg-blue-50 border-blue-200;
}

.step-indicator {
  @apply w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium mr-3 flex-shrink-0;
}

.step-content {
  @apply flex-1;
}

.step-title {
  @apply text-sm font-medium;
}

.step-description {
  @apply text-xs text-gray-500 mt-1;
}

.step-toggle {
  @apply ml-3 flex-shrink-0;
}

/* Config Groups */
.config-group {
  @apply bg-gray-50 rounded-lg p-3 border border-gray-100;
}

/* Status Message */
.status-message {
  @apply animate-fadeIn;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}
</style>