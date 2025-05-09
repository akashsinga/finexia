<template>
  <div class="status-message-container">
    <div class="status-message" :class="messageClass">
      <v-icon :icon="messageIcon" class="status-icon"></v-icon>
      <div class="status-message-content">
        <div class="status-message-title">{{ messageTitle }}</div>
        <div class="status-message-text">{{ message }}</div>
      </div>
      <v-btn icon="mdi-close" variant="text" size="small" @click="$emit('close')" class="close-btn"></v-btn>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatusMessage',
  props: {
    message: {
      type: String,
      required: true
    },
    type: {
      type: String,
      default: 'info',
      validator: value => ['info', 'success', 'warning', 'error'].includes(value)
    }
  },
  emits: ['close'],
  computed: {
    messageClass() {
      return `message-${this.type}`;
    },
    messageIcon() {
      const icons = {
        info: 'mdi-information',
        success: 'mdi-check-circle',
        warning: 'mdi-alert',
        error: 'mdi-alert-circle'
      };
      return icons[this.type] || icons.info;
    },
    messageTitle() {
      const titles = {
        info: 'Information',
        success: 'Success',
        warning: 'Warning',
        error: 'Error'
      };
      return titles[this.type] || titles.info;
    }
  }
}
</script>

<style lang="postcss" scoped>
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
</style>