<template>
  <div class="empty-state">
    <div class="empty-icon">
      <v-icon :size="iconSize" :color="iconColor">{{ icon }}</v-icon>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p v-if="message" class="empty-message">{{ message }}</p>
    <slot name="action"></slot>
  </div>
</template>

<script>
export default {
  name: 'EmptyState',
  props: {
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      default: 'mdi-alert-circle-outline'
    },
    iconSize: {
      type: [Number, String],
      default: 48
    },
    iconColor: {
      type: String,
      default: 'gray-300'
    }
  }
}
</script>

<style lang="postcss" scoped>
.empty-state {
  @apply flex flex-col items-center justify-center py-8 text-center;
}

.empty-icon {
  @apply mb-3 text-gray-300;
}

.empty-title {
  @apply text-base font-medium text-gray-700 mb-1;
}

.empty-message {
  @apply text-sm text-gray-500 mb-3;
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .empty-title {
    @apply text-gray-200;
  }

  .empty-message {
    @apply text-gray-400;
  }
}
</style>