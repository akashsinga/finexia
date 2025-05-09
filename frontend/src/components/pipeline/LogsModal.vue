<template>
  <v-dialog :model-value="modelValue" max-width="800" scrollable @update:model-value="$emit('update:modelValue', $event)">
    <div class="modal-card">
      <div class="modal-header">
        <h2 class="modal-title">Pipeline Logs</h2>
        <v-btn icon="mdi-close" variant="text" @click="$emit('update:modelValue', false)"></v-btn>
      </div>

      <div class="modal-content logs-modal-content">
        <div v-for="(log, index) in logs" :key="index" class="log-entry-full" :class="getLogClass(log.level)">
          <div class="log-time-full">{{ formatTime(log.timestamp) }}</div>
          <div class="log-message-full">{{ log.message }}</div>
        </div>

        <div v-if="logs.length === 0" class="logs-empty-full">
          No logs available
        </div>
      </div>

      <div class="modal-footer">
        <v-btn color="primary" @click="$emit('update:modelValue', false)">
          Close
        </v-btn>
      </div>
    </div>
  </v-dialog>
</template>

<script>
export default {
  name: 'LogsModal',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    logs: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  methods: {
    formatTime(timeString) {
      if (!timeString) return '';
      const date = new Date(timeString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
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
.modal-card {
  @apply bg-white rounded-xl border border-gray-200 overflow-hidden;
}

.modal-header {
  @apply flex justify-between items-center px-6 py-4 border-b border-gray-200 bg-gray-50;
}

.modal-title {
  @apply text-lg font-bold text-gray-800;
}

.modal-content {
  @apply p-0 max-h-[70vh] overflow-y-auto;
}

.logs-modal-content {
  @apply font-mono;
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

.modal-footer {
  @apply flex justify-end p-4 bg-gray-50 border-t border-gray-200;
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