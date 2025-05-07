<!-- 
  Card Component
  A reusable card component that follows the Finexia design system
  
  Props:
  - title: string - Card title
  - subtitle: string - Card subtitle
  - variant: default (default) | elevated | flat | outlined
  - loading: boolean - Show loading state
  - noPadding: boolean - Remove internal padding
  - fullHeight: boolean - Make card take full height of container
  - clickable: boolean - Add hover effects for clickable behavior
-->
<template>
  <div :class="['finexia-card', `variant-${variant}`, { 'is-loading': loading }, { 'no-padding': noPadding }, { 'full-height': fullHeight }, { 'clickable': clickable }]" @click="emitClick">
    <!-- Card Header -->
    <div v-if="hasHeader" class="card-header">
      <div class="header-content">
        <h3 v-if="title" class="card-title">{{ title }}</h3>
        <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions"></slot>
      </div>
    </div>

    <!-- Card Body -->
    <div class="card-body">
      <div v-if="loading" class="loader-container">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>
      <slot v-else></slot>
    </div>

    <!-- Card Footer -->
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FinexiaCard',

  props: {
    title: {
      type: String,
      default: ''
    },

    subtitle: {
      type: String,
      default: ''
    },

    variant: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'elevated', 'flat', 'outlined'].includes(value)
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

    clickable: {
      type: Boolean,
      default: false
    }
  },

  emits: ['click'],

  computed: {
    hasHeader() {
      return this.title || this.subtitle || this.$slots.actions;
    }
  },

  methods: {
    emitClick(event) {
      if (this.clickable) {
        this.$emit('click', event);
      }
    }
  }
}
</script>

<style lang="postcss" scoped>
.finexia-card {
  @apply bg-white rounded-lg flex flex-col overflow-hidden;
  @apply transition-all duration-200;

  /* Card Variants */
  &.variant-default {
    @apply shadow-sm border border-gray-200;
  }

  &.variant-elevated {
    @apply shadow-md border border-gray-100;
  }

  &.variant-flat {
    @apply shadow-none border-0;
  }

  &.variant-outlined {
    @apply shadow-none border border-gray-200;
  }

  /* Header Styles */
  .card-header {
    @apply flex justify-between items-center px-4 py-3 border-b border-gray-200;

    .header-content {
      @apply flex-1;
    }

    .card-title {
      @apply text-base font-medium text-gray-800;
    }

    .card-subtitle {
      @apply text-xs text-gray-500 mt-0.5;
    }

    .card-actions {
      @apply flex items-center space-x-2 ml-4;
    }
  }

  /* Body Styles */
  .card-body {
    @apply flex-grow relative;

    &:not(.no-padding) {
      @apply p-4;
    }
  }

  /* Footer Styles */
  .card-footer {
    @apply px-4 py-3 bg-gray-50 border-t border-gray-200;
  }

  /* Loading State */
  &.is-loading {
    @apply relative;

    .loader-container {
      @apply flex items-center justify-center py-8;
    }
  }

  /* Full Height */
  &.full-height {
    @apply h-full;
  }

  /* No Padding */
  &.no-padding {
    .card-body {
      @apply p-0;
    }
  }

  /* Clickable */
  &.clickable {
    @apply cursor-pointer hover:shadow-md;

    &:hover {
      @apply border-primary-400;
    }

    &:active {
      @apply transform scale-[0.99];
    }
  }
}

/* Dark mode overrides */
@media (prefers-color-scheme: dark) {
  .finexia-card {
    @apply bg-gray-800;

    &.variant-default,
    &.variant-elevated,
    &.variant-outlined {
      @apply border-gray-700;
    }

    .card-header {
      @apply border-gray-700;

      .card-title {
        @apply text-gray-100;
      }

      .card-subtitle {
        @apply text-gray-400;
      }
    }

    .card-footer {
      @apply bg-gray-900 border-gray-700;
    }

    &.clickable:hover {
      @apply border-primary-600;
    }
  }
}
</style>