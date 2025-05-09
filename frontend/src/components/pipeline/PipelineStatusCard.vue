<template>
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
        <div class="status-badge" :class="getStatusClass(pipelineStatus?.status)">
          {{ capitalizeFirst(pipelineStatus?.status || 'idle') }}
        </div>
      </div>
      <div class="action-buttons">
        <v-btn color="primary" :variant="isRunning ? 'outlined' : 'tonal'" :disabled="isRunning" size="small" prepend-icon="mdi-cog" @click="$emit('configure')">
          Configure
        </v-btn>
        <v-btn color="primary" :variant="isRunning ? 'outlined' : 'elevated'" :disabled="isRunning" size="small" :loading="isRunning" prepend-icon="mdi-play" @click="$emit('run')">
          Run Pipeline
        </v-btn>
      </div>
    </div>

    <div v-if="isRunning" class="progress-container">
      <div class="progress-header">
        <div class="progress-message">{{ pipelineStatus?.message || 'Running pipeline...' }}</div>
        <div class="progress-info">
          <span class="progress-percentage">{{ Math.round(pipelineStatus?.progress || 0) }}%</span>
          <span v-if="pipelineStatus?.estimatedDurationMinutes" class="progress-time">
            {{ formatTimeRemaining(pipelineStatus.estimatedDurationMinutes) }} remaining
          </span>
        </div>
      </div>
      <v-progress-linear :model-value="pipelineStatus?.progress || 0" color="primary" height="8" rounded></v-progress-linear>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineStatusCard',
  props: {
    pipelineStatus: {
      type: Object,
      default: () => ({ status: 'idle', progress: 0 })
    },
    isRunning: {
      type: Boolean,
      default: false
    },
    wsConnected: {
      type: Boolean,
      default: false
    }
  },
  emits: ['configure', 'run'],
  methods: {
    getStatusClass(status) {
      switch (status) {
        case 'running': return 'status-running';
        case 'completed': return 'status-completed';
        case 'failed': return 'status-failed';
        default: return 'status-idle';
      }
    },
    capitalizeFirst(str) {
      if (!str) return '';
      return str.charAt(0).toUpperCase() + str.slice(1);
    },
    formatTimeRemaining(minutes) {
      if (!minutes) return 'Unknown';
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
    }
  }
}
</script>

<style lang="postcss" scoped>
.status-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden;
}

.status-header {
  @apply p-5 flex flex-col md:flex-row justify-between items-start md:items-center gap-4;
}

.status-info {
  @apply flex flex-col;
}

.status-title-row {
  @apply flex items-center gap-3;
}

.status-title {
  @apply text-xl font-bold text-gray-800 mb-1;
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
</style>