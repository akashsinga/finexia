<template>
  <CardContainer title="Direction Predictions" :loading="loading" :full-height="true">
    <template #actions>
      <v-btn size="small" variant="text" @click="$emit('refresh')">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn size="small" v-bind="props" variant="text">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list density="compact">
          <v-list-item value="1" @click="timeRange = '7d'">
            <v-list-item-title>Last 7 days</v-list-item-title>
          </v-list-item>
          <v-list-item value="2" @click="timeRange = '30d'">
            <v-list-item-title>Last 30 days</v-list-item-title>
          </v-list-item>
          <v-list-item value="3" @click="timeRange = '90d'">
            <v-list-item-title>Last 90 days</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>

    <!-- Card Content -->
    <div class="prediction-content">
      <!-- Stats Summary -->
      <div class="stats-summary">
        <div class="big-numbers">
          <div class="number-item">
            <div class="number-container">
              <div class="direction-badge up">
                <v-icon size="small">mdi-arrow-up-bold</v-icon>
              </div>
              <div class="number success">{{ directionStats.upPredictions }}</div>
            </div>
            <!-- <div class="label">UP</div> -->
          </div>
          <div class="number-item">
            <div class="number-container">
              <div class="direction-badge down">
                <v-icon size="small">mdi-arrow-down-bold</v-icon>
              </div>
              <div class="number error">{{ directionStats.downPredictions }}</div>
            </div>
            <!-- <div class="label">DOWN</div> -->
          </div>
        </div>

        <div class="totals-card">
          <div class="totals-title">Total Predictions</div>
          <div class="totals-number">{{ totalPredictions }}</div>
          <div class="accuracy-summary">
            <div class="accuracy-item">
              <div class="accuracy-label">
                <div class="direction-badge success">
                  <v-icon size="large">mdi-arrow-up-bold</v-icon>
                </div>
                <span>UP accuracy</span>
              </div>
              <div class="accuracy-value success">{{ formatPercentage(directionStats.upAccuracy) }}</div>
            </div>
            <div class="accuracy-item">
              <div class="accuracy-label">
                <div class="direction-badge error">
                  <v-icon size="large">mdi-arrow-down-bold</v-icon>
                </div>
                <span>DOWN accuracy</span>
              </div>
              <div class="accuracy-value error">{{ formatPercentage(directionStats.downAccuracy) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Visual Distribution -->
      <div class="distribution-container">
        <div class="distribution-header">
          <div class="distribution-title">Direction Split</div>
          <div class="distribution-percentage">
            <div class="direction-badge mini up">
              <v-icon size="x-small">mdi-arrow-up-bold</v-icon>
            </div>
            <span>{{ upPercentage }}%</span>
          </div>
        </div>
        <div class="distribution-bar">
          <div class="distribution-segment up" :style="{ width: `${upPercentage}%` }"></div>
          <div class="distribution-segment down" :style="{ width: `${downPercentage}%` }"></div>
        </div>
        <div class="distribution-labels">
          <div class="distribution-label">
            <div class="direction-badge mini up">
              <v-icon size="x-small">mdi-arrow-up-bold</v-icon>
            </div>
            <span>UP</span>
          </div>
          <div class="distribution-label">
            <div class="direction-badge mini down">
              <v-icon size="x-small">mdi-arrow-down-bold</v-icon>
            </div>
            <span>DOWN</span>
          </div>
        </div>
      </div>

      <!-- Time Range Label -->
      <div class="time-range-label">
        Data from {{ timeRangeLabel }}
      </div>
    </div>
  </CardContainer>
</template>

<script>
import CardContainer from '@/components/common/CardContainer.vue'

export default {
  name: 'DirectionPredictionsCard',
  components: {
    CardContainer
  },
  props: {
    directionStats: {
      type: Object,
      required: true,
      default: () => ({
        upPredictions: 0,
        downPredictions: 0,
        upAccuracy: 0,
        downAccuracy: 0
      })
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  data() {
    return {
      timeRange: '30d'
    }
  },
  computed: {
    totalPredictions() {
      return this.directionStats.upPredictions + this.directionStats.downPredictions;
    },
    upPercentage() {
      if (this.totalPredictions === 0) return 50;
      return Math.round((this.directionStats.upPredictions / this.totalPredictions) * 100);
    },
    downPercentage() {
      if (this.totalPredictions === 0) return 50;
      return Math.round((this.directionStats.downPredictions / this.totalPredictions) * 100);
    },
    timeRangeLabel() {
      switch (this.timeRange) {
        case '7d': return 'the last 7 days';
        case '90d': return 'the last 90 days';
        default: return 'the last 30 days';
      }
    }
  },
  methods: {
    formatPercentage(value) {
      if (value === null || value === undefined) return 'N/A';
      return (value * 100).toFixed(1) + '%';
    }
  }
}
</script>

<style lang="postcss" scoped>
.prediction-content {
  @apply flex flex-col gap-4 h-full;
}

.stats-summary {
  @apply grid grid-cols-2 gap-4;
}

.big-numbers {
  @apply flex flex-col justify-center gap-4 bg-gray-50 p-4 rounded-lg;
}

.number-item {
  @apply flex flex-col items-center;
}

.number-container {
  @apply flex items-center gap-2;
}

.number {
  @apply text-3xl font-bold;
}

.number.success {
  @apply text-success;
}

.number.error {
  @apply text-error;
}

.label {
  @apply text-xs font-medium mt-1;
}

.direction-badge {
  @apply w-6 h-6 rounded-full flex items-center justify-center;
}

.direction-badge.up,
.direction-badge.success {
  @apply bg-success bg-opacity-10 text-success;
}

.direction-badge.down,
.direction-badge.error {
  @apply bg-error bg-opacity-10 text-error;
}

.direction-badge.mini {
  @apply w-4 h-4;
}

.totals-card {
  @apply bg-gray-50 p-4 rounded-lg flex flex-col;
}

.totals-title {
  @apply text-xs text-gray-500 mb-1;
}

.totals-number {
  @apply text-2xl font-bold text-primary mb-4;
}

.accuracy-summary {
  @apply mt-auto flex flex-col gap-2;
}

.accuracy-item {
  @apply flex justify-between items-center;
}

.accuracy-label {
  @apply flex items-center gap-1 text-xs text-gray-600;
}

.accuracy-value {
  @apply text-xs font-semibold;
}

.accuracy-value.success {
  @apply text-success;
}

.accuracy-value.error {
  @apply text-error;
}

.distribution-container {
  @apply mt-2;
}

.distribution-header {
  @apply flex justify-between items-center mb-2;
}

.distribution-title {
  @apply text-xs text-gray-500;
}

.distribution-percentage {
  @apply text-sm font-semibold flex items-center gap-1;
}

.distribution-bar {
  @apply flex h-8 rounded-lg overflow-hidden mb-2;
}

.distribution-segment {
  @apply h-full transition-all duration-700 ease-in-out;
}

.distribution-segment.up {
  @apply bg-success;
}

.distribution-segment.down {
  @apply bg-error;
}

.distribution-labels {
  @apply flex justify-between;
}

.distribution-label {
  @apply flex items-center gap-1 text-xs;
}

.time-range-label {
  @apply text-xs text-gray-500 text-center mt-auto;
}
</style>