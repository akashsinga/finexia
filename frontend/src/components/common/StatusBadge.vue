<template>
  <div class="status-badge" :class="badgeClass">
    <v-icon v-if="icon" size="x-small" class="badge-icon">{{ icon }}</v-icon>
    <slot>{{ text }}</slot>
  </div>
</template>

<script>
export default {
  name: 'StatusBadge',
  props: {
    status: {
      type: String,
      default: ''
    },
    variant: {
      type: String,
      default: '',
      validator: value => ['success', 'error', 'warning', 'info', 'primary', 'secondary', ''].includes(value)
    },
    text: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      default: ''
    }
  },
  computed: {
    badgeClass() {
      // If variant is provided, use it
      if (this.variant) {
        return `badge-${this.variant}`;
      }

      // Otherwise derive from status
      const statusMap = {
        'UP': 'badge-success',
        'DOWN': 'badge-error',
        'ACTIVE': 'badge-success',
        'INACTIVE': 'badge-error',
        'VERIFIED': 'badge-success',
        'FAILED': 'badge-error',
        'PENDING': 'badge-warning'
      };

      return statusMap[this.status] || 'badge-default';
    }
  }
}
</script>

<style lang="postcss" scoped>
.status-badge {
  @apply inline-flex items-center justify-center px-2 py-0.5 rounded-full text-xs font-medium;
}

.badge-icon {
  @apply mr-1;
}

.badge-primary {
  @apply bg-primary bg-opacity-10 text-primary;
}

.badge-secondary {
  @apply bg-secondary bg-opacity-10 text-secondary;
}

.badge-success {
  @apply bg-success bg-opacity-10 text-success;
}

.badge-error {
  @apply bg-error bg-opacity-10 text-error;
}

.badge-warning {
  @apply bg-warning bg-opacity-10 text-warning;
}

.badge-info {
  @apply bg-info bg-opacity-10 text-info;
}

.badge-default {
  @apply bg-gray-100 text-gray-700;
}

/* Dark mode variations */
@media (prefers-color-scheme: dark) {
  .badge-default {
    @apply bg-gray-700 text-gray-300;
  }
}
</style>