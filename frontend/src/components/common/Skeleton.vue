<template>
  <div class="skeleton" :class="[`skeleton-${type}`, { 'skeleton-animate': animate }]" :style="style"></div>
</template>

<script>
export default {
  name: 'Skeleton',
  props: {
    type: {
      type: String,
      default: 'line',
      validator: value => ['line', 'circle', 'rect', 'card', 'avatar', 'button'].includes(value)
    },
    width: {
      type: [String, Number],
      default: '100%'
    },
    height: {
      type: [String, Number],
      default: null
    },
    animate: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    style() {
      const style = {};

      if (this.width) {
        style.width = typeof this.width === 'number' ? `${this.width}px` : this.width;
      }

      if (this.height) {
        style.height = typeof this.height === 'number' ? `${this.height}px` : this.height;
      } else {
        // Default heights based on type
        switch (this.type) {
          case 'line':
            style.height = '16px';
            break;
          case 'circle':
          case 'avatar':
            style.height = style.width;
            break;
          case 'button':
            style.height = '36px';
            break;
          case 'card':
            style.height = '120px';
            break;
          case 'rect':
            style.height = '80px';
            break;
        }
      }

      return style;
    }
  }
}
</script>

<style lang="postcss" scoped>
.skeleton {
  @apply bg-gray-200 rounded overflow-hidden;

  &.skeleton-animate {
    @apply animate-pulse;
  }

  &.skeleton-circle,
  &.skeleton-avatar {
    @apply rounded-full;
  }

  &.skeleton-card {
    @apply rounded-lg;
  }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .skeleton {
    @apply bg-gray-700;
  }
}
</style>