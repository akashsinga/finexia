<template>
  <div class="pipeline-dashboard">
    <!-- Status Card with Pipeline Controls -->
    <PipelineStatusCard :pipelineStatus="systemStore.pipelineStatus" :isRunning="systemStore.isPipelineRunning" :wsConnected="systemStore.wsConnected" @configure="showConfigModal = true" @run="runPipeline" />

    <!-- Stats Cards Grid -->
    <div class="stats-grid">
      <SystemStatsCard :stats="systemStore.stats" :lastUpdateTime="systemStore.lastUpdateTime" @refresh="fetchInitialSystemStatus" />
      <ModelStatsCard :stats="systemStore.stats" />
    </div>

    <!-- Pipeline Steps Panel -->
    <PipelineStepsSelector :steps="pipelineSteps" :selectedSteps="selectedSteps" :isRunning="systemStore.isPipelineRunning" :currentStep="systemStore.pipelineStatus?.currentStep" @select="toggleStep" @select-all="selectAllSteps" />

    <!-- Two-column Layout for Config and Logs -->
    <div class="config-logs-grid">
      <QuickConfigPanel v-model:force="pipelineConfig.force" v-model:scheduleTime="scheduleTime" @save-schedule="saveSchedule" />
      <RecentLogsPanel :logs="systemStore.pipelineLogs" :isLoading="isLoading" @refresh="refreshLogs" @view-all="showLogsModal = true" />
    </div>

    <!-- Status Message -->
    <StatusMessage v-if="statusMessage" :message="statusMessage" :type="statusMessageType" @close="clearStatusMessage" />

    <!-- Configuration Modal -->
    <PipelineConfigModal v-model="showConfigModal" v-model:selectedSteps="selectedSteps" v-model:pipelineConfig="pipelineConfig" v-model:scheduleTime="scheduleTime" v-model:scheduleFrequency="scheduleFrequency" v-model:selectedDays="selectedDays" :steps="pipelineSteps" :scheduleOptions="scheduleOptions" @save="saveConfig" />

    <!-- Logs Modal -->
    <LogsModal v-model="showLogsModal" :logs="systemStore.pipelineLogs" />
  </div>
</template>

<script>
import { useSystemStore } from '@/store/system.store';
import { WebSocketService } from '@/services/websocket.service';
import PipelineStatusCard from '@/components/pipeline/PipelineStatusCard.vue';
import SystemStatsCard from '@/components/pipeline/SystemStatsCard.vue';
import ModelStatsCard from '@/components/pipeline/ModelStatsCard.vue';
import PipelineStepsSelector from '@/components/pipeline/PipelineStepsSelector.vue';
import QuickConfigPanel from '@/components/pipeline/QuickConfigPanel.vue';
import RecentLogsPanel from '@/components/pipeline/RecentLogsPanel.vue';
import StatusMessage from '@/components/common/StatusMessage.vue';
import PipelineConfigModal from '@/components/pipeline/PipelineConfigModal.vue';
import LogsModal from '@/components/pipeline/LogsModal.vue';

export default {
  name: 'PipelineDashboard',
  components: {
    PipelineStatusCard,
    SystemStatsCard,
    ModelStatsCard,
    PipelineStepsSelector,
    QuickConfigPanel,
    RecentLogsPanel,
    StatusMessage,
    PipelineConfigModal,
    LogsModal
  },
  data() {
    return {
      systemStore: useSystemStore(),
      wsService: null,
      pollingInterval: null,
      isLoading: false,
      selectedSteps: ['data_import', 'model_training', 'prediction', 'validation'],
      showConfigModal: false,
      showLogsModal: false,
      pipelineSteps: [
        { id: 'data_import', name: 'Data Import', description: 'Imports EOD data for selected symbols' },
        { id: 'model_training', name: 'Model Training', description: 'Trains or updates prediction models' },
        { id: 'prediction', name: 'Prediction Generation', description: 'Generates market predictions using trained models' },
        { id: 'validation', name: 'Result Validation', description: 'Validates previous predictions against actual results' }
      ],
      pipelineConfig: { force: false, maxSymbols: 100 },
      statusMessage: null,
      statusMessageType: 'info',
      scheduleTime: '02:00',
      scheduleFrequency: 'Daily',
      selectedDays: [1, 2, 3, 4, 5],
      scheduleOptions: [
        { title: '00:00', value: '00:00' }, { title: '02:00', value: '02:00' },
        { title: '04:00', value: '04:00' }, { title: '06:00', value: '06:00' },
        { title: '08:00', value: '08:00' }, { title: '10:00', value: '10:00' },
        { title: '12:00', value: '12:00' }, { title: '14:00', value: '14:00' },
        { title: '16:00', value: '16:00' }, { title: '18:00', value: '18:00' },
        { title: '20:00', value: '20:00' }, { title: '22:00', value: '22:00' }
      ]
    };
  },
  methods: {
    initWebSocket() {
      const token = localStorage.getItem('token');
      if (!token) {
        this.showStatusMessage('Authentication token not found. Live updates disabled.', 'warning');
        return;
      }

      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
      let wsHost;
      try {
        const apiUrl = new URL(apiBaseUrl);
        wsHost = apiUrl.host;
      } catch (e) {
        wsHost = window.location.host;
      }
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${wsHost}/system/status?token=${token}`;

      this.wsService = new WebSocketService(wsUrl, {
        onOpen: this.handleWsOpen.bind(this),
        onMessage: this.handleWsMessage.bind(this),
        onClose: this.handleWsClose.bind(this),
        onError: this.handleWsError.bind(this)
      });

      this.wsService.connect();
    },

    handleWsOpen() {
      // Stop polling if it was started as a fallback
      this.stopPolling();
      this.systemStore.setWsConnected(true);
      console.log('WebSocket connected to system status');
    },

    handleWsMessage({ data }) {
      try {
        // Handle the WebSocket message using the store
        this.systemStore.handleWebSocketMessage(data);
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    },

    handleWsClose() {
      this.systemStore.setWsConnected(false);
      // Start polling as fallback
      this.startPolling();
    },

    handleWsError() {
      this.systemStore.setWsConnected(false);
      // Start polling as fallback
      this.startPolling();
    },

    startPolling() {
      if (this.pollingInterval) return;

      this.pollingInterval = setInterval(async () => {
        try {
          await this.fetchInitialSystemStatus();
        } catch (error) {
          console.error('Polling error:', error);
        }
      }, 5000);
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    },

    async fetchInitialSystemStatus() {
      try {
        await this.systemStore.fetchSystemStatus();
      } catch (error) {
        console.error('Failed to fetch initial system status:', error);
      }
    },

    async refreshLogs() {
      this.isLoading = true;
      try {
        await this.systemStore.refreshLogs(50);
      } catch (error) {
        console.error('Failed to fetch logs:', error);
      } finally {
        this.isLoading = false;
      }
    },

    saveSchedule() {
      this.showStatusMessage(`Pipeline scheduled to run daily at ${this.scheduleTime}`, 'success');
    },

    async runPipeline() {
      try {
        await this.systemStore.runPipeline({
          force: this.pipelineConfig.force,
          steps: this.selectedSteps,
          maxSymbols: this.pipelineConfig.maxSymbols
        });

        this.showStatusMessage('Pipeline execution started successfully', 'success');
        this.fetchInitialSystemStatus();
      } catch (error) {
        this.showStatusMessage('Failed to start pipeline', 'error');
        console.error('Failed to start pipeline:', error);
      }
    },

    saveConfig() {
      this.showConfigModal = false;
      this.showStatusMessage('Pipeline configuration saved', 'success');
    },

    toggleStep(stepId) {
      const index = this.selectedSteps.indexOf(stepId);
      if (index === -1) {
        this.selectedSteps.push(stepId);
      } else {
        this.selectedSteps.splice(index, 1);
      }
    },

    selectAllSteps() {
      if (this.selectedSteps.length === this.pipelineSteps.length) {
        this.selectedSteps = [];
      } else {
        this.selectedSteps = this.pipelineSteps.map(step => step.id);
      }
    },

    showStatusMessage(message, type = 'info') {
      this.statusMessage = message;
      this.statusMessageType = type;
      setTimeout(() => {
        if (this.statusMessage === message) {
          this.clearStatusMessage();
        }
      }, 5000);
    },

    clearStatusMessage() {
      this.statusMessage = null;
    }
  },
  mounted() {
    this.fetchInitialSystemStatus();
    this.initWebSocket();
  },
  beforeUnmount() {
    if (this.wsService) {
      this.wsService.close();
    }
    this.stopPolling();
  }
};
</script>

<style lang="postcss" scoped>
.pipeline-dashboard {
  @apply mx-auto space-y-6;
}

.stats-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6;
}

.config-logs-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6;
}
</style>