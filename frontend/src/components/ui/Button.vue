<!-- 
  Button Component
  A reusable button component that follows the Finexia design system
  
  Props:
  - variant: primary (default) | secondary | success | error | warning | info | text | outlined
  - size: medium (default) | small | large
  - disabled: boolean
  - loading: boolean
  - icon: string (Material Design Icon name)
  - iconPosition: left (default) | right
  - block: boolean (full width)
  - rounded: boolean (fully rounded)
-->
<template>
  <button :class="['finexia-button', `variant-${variant}`, `size-${size}`, { 'is-loading': loading }, { 'is-disabled': disabled }, { 'has-icon': icon }, { 'icon-right': icon && iconPosition === 'right' }, { 'block': block }, { 'rounded': rounded }]" :disabled="disabled || loading" @click="$emit('click', $event)">
    <v-icon v-if="icon && iconPosition === 'left'" :size="iconSize" class="button-icon left">
      {{ icon }}
    </v-icon>

    <span v-if="$slots.default" class="button-content">
      <slot></slot>
    </span>

    <v-icon v-if="icon && iconPosition === 'right'" :size="iconSize" class="button-icon right">
      {{ icon }}
    </v-icon>

    <v-progress-circular v-if="loading" indeterminate :size="loaderSize" :width="2" color="currentColor" class="button-loader"></v-progress-circular>
  </button>
</template>

<script>
export default {
  name: 'FinexiaButton',

  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => [
        'primary',
        'secondary',
        'success',
        'error',
        'warning',
        'info',
        'text',
        'outlined'
      ].includes(value)
    },

    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },

    disabled: {
      type: Boolean,
      default: false
    },

    loading: {
      type: Boolean,
      default: false
    },

    icon: {
      type: String,
      default: ''
    },

    iconPosition: {
      type: String,
      default: 'left',
      validator: (value) => ['left', 'right'].includes(value)
    },

    block: {
      type: Boolean,
      default: false
    },

    rounded: {
      type: Boolean,
      default: false
    }
  },

  emits: ['click'],

  computed: {
    iconSize() {
      const sizes = {
        small: 'small',
        medium: 'default',
        large: 'large'
      };

      return sizes[this.size];
    },

    loaderSize() {
      const sizes = {
        small: 16,
        medium: 20,
        large: 24
      };

      return sizes[this.size];
    }
  }
}
</script>

<style lang="postcss" scoped>
.finexia-button {
  @apply inline-flex items-center justify-center relative;
  @apply font-medium transition-all duration-200;
  @apply focus:outline-none focus:ring-2 focus:ring-offset-2;

  /* Base button styles */
  &.variant-primary {
    @apply bg-primary text-white hover:bg-primary-dark focus:ring-primary;
  }

  &.variant-secondary {
    @apply bg-secondary text-white hover:bg-secondary-dark focus:ring-secondary;
  }

  &.variant-success {
    @apply bg-success text-white hover:bg-success-dark focus:ring-success;
  }

  &.variant-error {
    @apply bg-error text-white hover:bg-error-dark focus:ring-error;
  }

  &.variant-warning {
    @apply bg-warning text-white hover:bg-warning-dark focus:ring-warning;
  }

  &.variant-info {
    @apply bg-info text-white hover:bg-info-dark focus:ring-info;
  }

  &.variant-text {
    @apply bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-300;
  }

  &.variant-outlined {
    @apply bg-transparent border border-current hover:bg-opacity-10 focus:ring-gray-300;

    &.variant-primary {
      @apply text-primary hover:bg-primary hover:border-primary;
    }

    &.variant-secondary {
      @apply text-secondary hover:bg-secondary hover:border-secondary;
    }

    &.variant-success {
      @apply text-success hover:bg-success hover:border-success;
    }

    &.variant-error {
      @apply text-error hover:bg-error hover:border-error;
    }

    &.variant-warning {
      @apply text-warning hover:bg-warning hover:border-warning;
    }

    &.variant-info {
      @apply text-info hover:bg-info hover:border-info;
    }
  }

  /* Button Sizes */
  &.size-small {
    @apply px-3 py-1 text-xs rounded;
  }

  &.size-medium {
    @apply px-4 py-2 text-sm rounded-md;
  }

  &.size-large {
    @apply px-6 py-3 text-base rounded-lg;
  }

  /* Icon Styling */
  &.has-icon {
    .button-icon {
      @apply flex-shrink-0;
    }

    .button-icon.left {
      @apply mr-2;
    }

    .button-icon.right {
      @apply ml-2;
    }
  }

  /* Button with icon only */
  &.has-icon:not(:has(.button-content)) {
    @apply p-2;

    &.size-small {
      @apply p-1;
    }

    &.size-large {
      @apply p-3;
    }
  }

  /* Loading state */
  &.is-loading {
    @apply cursor-wait;

    .button-content {
      @apply opacity-0;
    }

    .button-loader {
      @apply absolute;
    }
  }

  /* Disabled state */
  &.is-disabled {
    @apply opacity-60 cursor-not-allowed;
  }

  /* Full width button */
  &.block {
    @apply w-full;
  }

  /* Fully rounded button */
  &.rounded {
    @apply rounded-full;
  }
}
</style>