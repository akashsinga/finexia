<template>
  <div class="logs-card">
    <div class="logs-header">
      <h2 class="logs-title">Recent Logs</h2>
      <v-btn icon="mdi-refresh" variant="text" density="comfortable" color="gray" @click="$emit('refresh')"></v-btn>
    </div>

    <div v-if="isLoading" class="logs-loading">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>

    <div v-else-if="logs.length === 0" class="logs-empty">
      No logs available
    </div>

    <div v-else class="logs-content">
      <div v-for="(log, index) in displayLogs" :key="index" class="log-entry" :class="getLogClass(log.level)">
        <div class="log-time">{{ formatTime(log.timestamp) }}</div>
        <div class="log-message">{{ log.message }}</div>
      </div>

      <div v-if="logs.length > displayCount" class="logs-more">
        <v-btn size="small" variant="text" color="primary" @click="$emit('view-all')">
          View All Logs
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecentLogsPanel',
  props: {
    logs: {
      type: Array,
      default: () => []
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    displayCount: {
      type: Number,
      default: 5
    }
  },
  emits: ['refresh', 'view-all'],
  computed: {
    displayLogs() {
      return this.logs.slice(0, this.displayCount);
    }
  },
  methods: {
    formatTime(timeString) {
      if (!timeString) return '';
      const date = new Date(timeString);
      return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
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
    }
  }
}
</script>

<style lang="postcss" scoped>
.logs-card {
  @apply bg-white rounded-xl border border-gray-200 p-6;
}

.logs-header {
  @apply flex justify-between items-center mb-5;
}

.logs-title {
  @apply text-base font-bold text-gray-800;
}

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
</style>