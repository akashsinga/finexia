<template>
  <div class="direction-indicator" :class="[variant, size]">
    <v-icon :size="iconSize">{{ icon }}</v-icon>
    <span v-if="showLabel" class="direction-text">{{ direction }}</span>
  </div>
</template>

<script>
export default {
  name: 'DirectionIndicator',
  props: {
    direction: {
      type: String,
      required: true,
      validator: value => ['UP', 'DOWN'].includes(value)
    },
    size: {
      type: String,
      default: 'medium',
      validator: value => ['small', 'medium', 'large'].includes(value)
    },
    showLabel: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    variant() {
      return this.direction === 'UP' ? 'direction-up' : 'direction-down';
    },
    icon() {
      return this.direction === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold';
    },
    iconSize() {
      const sizes = {
        small: 'x-small',
        medium: 'small',
        large: 'default'
      };
      return sizes[this.size];
    }
  }
}
</script>

<style lang="postcss" scoped>
.direction-indicator {
  @apply inline-flex items-center justify-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium;
}

.direction-up {
  @apply bg-success bg-opacity-10 text-success;
}

.direction-down {
  @apply bg-error bg-opacity-10 text-error;
}

.direction-text {
  @apply font-medium;
}

/* Sizes */
.small {
  @apply text-[10px] px-1.5 py-0;
}

.large {
  @apply text-sm px-2.5 py-1;
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .direction-up {
    @apply bg-success bg-opacity-20;
  }

  .direction-down {
    @apply bg-error bg-opacity-20;
  }
}
</style>