<template>
  <div class="stat-card">
    <div class="stat-card-header">
      <h2 class="stat-card-title">System Statistics</h2>
      <span v-if="lastUpdateTime" class="last-update">Updated {{ lastUpdateTime }}</span>
    </div>
    <div class="stat-grid">
      <div class="stat-item">
        <div class="stat-icon bg-blue-50 text-blue-600">
          <v-icon>mdi-chart-line</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalPredictions || 0 }}</div>
          <div class="stat-label">Total Predictions</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon bg-green-50 text-green-600">
          <v-icon>mdi-calendar-check</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.todayPredictions || 0 }}</div>
          <div class="stat-label">Today's Predictions</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon bg-amber-50 text-amber-600">
          <v-icon>mdi-check-decagram</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.verifiedPredictions || 0 }}</div>
          <div class="stat-label">Verified Predictions</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon bg-purple-50 text-purple-600">
          <v-icon>mdi-arrow-decision</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.directionPredictions || 0 }}</div>
          <div class="stat-label">Direction Predictions</div>
        </div>
      </div>
    </div>
    <div class="success-rate-container">
      <div class="success-rate-header">
        <div class="success-rate-label">Success Rate</div>
        <div class="success-rate-value">{{ (stats.verifiedPredictionPercent || 0).toFixed(1) }}%</div>
      </div>
      <v-progress-linear :model-value="stats.verifiedPredictionPercent || 0" :color="getSuccessRateColor(stats.verifiedPredictionPercent)" height="8" rounded></v-progress-linear>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SystemStatsCard',
  props: {
    stats: {
      type: Object,
      required: true
    },
    lastUpdateTime: {
      type: String,
      default: 'Never'
    }
  },
  emits: ['refresh'],
  methods: {
    getSuccessRateColor(rate) {
      if (!rate) return 'gray';
      if (rate < 40) return 'error';
      if (rate < 70) return 'warning';
      return 'success';
    }
  }
}
</script>

<style lang="postcss" scoped>
.stat-card {
  @apply bg-white rounded-xl border border-gray-200 p-6;
}

.stat-card-header {
  @apply flex justify-between items-center mb-5;
}

.stat-card-title {
  @apply text-base font-bold text-gray-800;
}

.last-update {
  @apply text-xs text-gray-500 bg-gray-50 px-2.5 py-1 rounded-full;
}

.stat-grid {
  @apply grid grid-cols-2 gap-5;
}

.stat-item {
  @apply flex items-start gap-3 p-1 rounded-lg;
}

.stat-icon {
  @apply w-10 h-10 flex items-center justify-center rounded-lg;
}

.stat-content {
  @apply flex-1;
}

.stat-value {
  @apply text-lg font-semibold text-gray-900;
}

.stat-label {
  @apply text-xs text-gray-500;
}

.success-rate-container {
  @apply mt-6 bg-gray-50 p-4 rounded-lg;
}

.success-rate-header {
  @apply flex justify-between items-center mb-2;
}

.success-rate-label {
  @apply text-sm text-gray-600;
}

.success-rate-value {
  @apply text-sm font-medium;
}
</style>