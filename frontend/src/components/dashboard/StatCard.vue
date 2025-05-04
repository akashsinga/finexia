<template>
  <div class="stat-card">
    <div class="card-content">
      <div class="stat-icon" :class="iconBackground">
        <v-icon :color="iconColor">{{ icon }}</v-icon>
      </div>
      <div class="stat-info">
        <div class="stat-label">{{ label }}</div>
        <div class="stat-value">{{ value }}</div>
        <div class="stat-change" :class="changeClass">
          <v-icon size="small">{{ changeIcon }}</v-icon>
          {{ changeText }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    label: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    iconColor: {
      type: String,
      default: 'primary'
    },
    iconBackground: {
      type: String,
      default: 'bg-primary-light'
    },
    changeText: {
      type: String,
      default: ''
    },
    changeType: {
      type: String,
      default: 'neutral',
      validator: function (value) {
        return ['positive', 'negative', 'neutral'].includes(value);
      }
    }
  },
  computed: {
    changeClass: function () {
      return this.changeType;
    },
    changeIcon: function () {
      if (this.changeType === 'positive') return 'mdi-arrow-up';
      if (this.changeType === 'negative') return 'mdi-arrow-down';
      return 'mdi-minus';
    }
  }
}
</script>

<style lang="postcss" scoped>
.stat-card {
  @apply bg-white p-4 h-full rounded-lg shadow-sm border border-gray-200;
}

.card-content {
  @apply flex items-center;
}

.stat-icon {
  @apply w-12 h-12 rounded-lg flex items-center justify-center mr-4;
}

.bg-primary-light {
  @apply bg-primary bg-opacity-10;
}

.bg-success-light {
  @apply bg-success bg-opacity-10;
}

.bg-info-light {
  @apply bg-info bg-opacity-10;
}

.bg-warning-light {
  @apply bg-warning bg-opacity-10;
}

.stat-info {
  @apply flex-1;
}

.stat-label {
  @apply text-sm text-gray-500 mb-1;
}

.stat-value {
  @apply text-xl font-semibold;
}

.stat-change {
  @apply text-xs flex items-center mt-1;
}

.positive {
  @apply text-success;
}

.negative {
  @apply text-error;
}

.neutral {
  @apply text-gray-500;
}
</style>