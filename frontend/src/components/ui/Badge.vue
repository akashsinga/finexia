<!-- 
  Badge Component
  A reusable badge component that follows the Finexia design system
  
  Props:
  - variant: default (default) | primary | success | error | warning | info
  - size: medium (default) | small | large
  - rounded: boolean - Fully rounded badge
  - outline: boolean - Outlined style
  - dot: boolean - Show as a dot instead of with content
  - icon: string - Material Design Icon name
-->
<template>
  <span :class="['finexia-badge', `variant-${variant}`, `size-${size}`, { rounded }, { outline }, { dot }]">
    <v-icon v-if="icon && !dot" :size="iconSize" class="badge-icon">
      {{ icon }}
    </v-icon>

    <span v-if="!dot && $slots.default" class="badge-content">
      <slot></slot>
    </span>
  </span>
</template>

<script>
export default {
  name: 'FinexiaBadge',

  props: {
    variant: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'primary', 'success', 'error', 'warning', 'info'].includes(value)
    },

    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },

    rounded: {
      type: Boolean,
      default: true
    },

    outline: {
      type: Boolean,
      default: false
    },

    dot: {
      type: Boolean,
      default: false
    },

    icon: {
      type: String,
      default: ''
    }
  },

  computed: {
    iconSize() {
      const sizes = {
        small: 'x-small',
        medium: 'small',
        large: 'small'
      };

      return sizes[this.size];
    }
  }
}
</script>

<style lang="postcss" scoped>
.finexia-badge {
  @apply inline-flex items-center justify-center transition-colors duration-200;

  /* Size variations */
  &.size-small {
    @apply text-xs px-1.5 py-0.5;

    &.dot {
      @apply w-2 h-2;
    }
  }

  &.size-medium {
    @apply text-xs px-2 py-0.5;

    &.dot {
      @apply w-2.5 h-2.5;
    }
  }

  &.size-large {
    @apply text-sm px-2.5 py-1;

    &.dot {
      @apply w-3 h-3;
    }
  }

  /* Shape variations */
  &.rounded {
    @apply rounded-full;
  }

  &:not(.rounded) {
    @apply rounded;
  }

  /* Icon styling */
  .badge-icon {
    @apply mr-1;
  }

  /* Variant styling - Default (gray) */
  &.variant-default {
    @apply bg-gray-100 text-gray-700;

    &.outline {
      @apply bg-transparent border border-gray-300 text-gray-700;
    }
  }

  /* Variant styling - Primary */
  &.variant-primary {
    @apply bg-primary bg-opacity-10 text-primary;

    &.outline {
      @apply bg-transparent border border-primary text-primary;
    }
  }

  /* Variant styling - Success */
  &.variant-success {
    @apply bg-success bg-opacity-10 text-success;

    &.outline {
      @apply bg-transparent border border-success text-success;
    }
  }

  /* Variant styling - Error */
  &.variant-error {
    @apply bg-error bg-opacity-10 text-error;

    &.outline {
      @apply bg-transparent border border-error text-error;
    }
  }

  /* Variant styling - Warning */
  &.variant-warning {
    @apply bg-warning bg-opacity-10 text-warning;

    &.outline {
      @apply bg-transparent border border-warning text-warning;
    }
  }

  /* Variant styling - Info */
  &.variant-info {
    @apply bg-info bg-opacity-10 text-info;

    &.outline {
      @apply bg-transparent border border-info text-info;
    }
  }

  /* Dot styling */
  &.dot {
    @apply rounded-full p-0;

    &.variant-default {
      @apply bg-gray-500;
    }

    &.variant-primary {
      @apply bg-primary;
    }

    &.variant-success {
      @apply bg-success;
    }

    &.variant-error {
      @apply bg-error;
    }

    &.variant-warning {
      @apply bg-warning;
    }

    &.variant-info {
      @apply bg-info;
    }
  }
}

/* Dark mode overrides */
@media (prefers-color-scheme: dark) {
  .finexia-badge {
    &.variant-default {
      @apply bg-gray-700 text-gray-200;

      &.outline {
        @apply border-gray-600 text-gray-300;
      }
    }
  }
}
</style>