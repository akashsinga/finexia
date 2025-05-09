<template>
  <div class="card" :class="[{ 'card-no-padding': noPadding }, { 'card-full-height': fullHeight }, cardClass]">
    <div v-if="title || $slots.header || $slots.actions" class="card-header">
      <div class="card-header-content">
        <h3 v-if="title" class="card-title">{{ title }}</h3>
        <slot name="header"></slot>
      </div>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <div class="card-body" :class="{ 'p-0': noPadding }">
      <div v-if="loading" class="card-loading">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>
      <slot v-else></slot>
    </div>

    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EnhancedCard',
  props: {
    title: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    },
    noPadding: {
      type: Boolean,
      default: false
    },
    fullHeight: {
      type: Boolean,
      default: false
    },
    cardClass: {
      type: String,
      default: ''
    }
  }
}
</script>

<style lang="postcss" scoped>
.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 transition-shadow duration-200;
}

.card:hover {
  @apply shadow-md;
}

.card.card-no-padding .card-body {
  @apply p-0;
}

.card.card-full-height {
  @apply h-full flex flex-col;
}

.card-header {
  @apply flex justify-between items-center px-4 py-3 border-b border-gray-200;
}

.card-header-content {
  @apply flex-1;
}

.card-title {
  @apply text-base font-medium text-gray-800;
}

.card-actions {
  @apply flex items-center space-x-2;
}

.card-body {
  @apply p-4 flex-grow;
}

.card-loading {
  @apply flex justify-center items-center py-8;
}

.card-footer {
  @apply px-4 py-3 bg-gray-50 border-t border-gray-200;
}

/* Dark Mode styles */
@media (prefers-color-scheme: dark) {
  .card {
    @apply bg-gray-800 border-gray-700;
  }

  .card-header {
    @apply border-gray-700;
  }

  .card-title {
    @apply text-gray-100;
  }

  .card-footer {
    @apply bg-gray-900 border-gray-700;
  }
}
</style>