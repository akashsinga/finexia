<template>
  <CardContainer :title="title" :loading="loading" :full-height="true" :no-padding="true" class="min-h-[350px]">
    <template #actions>
      <v-btn size="small" variant="text" @click="$emit('refresh')"><v-icon>mdi-refresh</v-icon></v-btn>
      <v-btn size="small" variant="text" @click="$emit('view-all')"><v-icon>mdi-arrow-right</v-icon></v-btn>
    </template>

    <div class="prediction-list">
      <div v-if="predictions.length === 0" class="empty-state">{{ emptyMessage }}</div>
      <div v-else class="predictions-container">
        <div v-for="(prediction, i) in predictions" :key="i" class="prediction-item">
          <!-- Header row with symbol and date -->
          <div class="prediction-header">
            <div class="symbol">{{ prediction.trading_symbol }}</div>
            <div class="prediction-date">{{ formatDate(prediction.date) }}</div>
          </div>

          <!-- Content row with direction and confidence values -->
          <div class="prediction-content">
            <div :class="['direction', prediction.direction_prediction === 'UP' ? 'up' : 'down']">
              <v-icon size="small">{{ prediction.direction_prediction === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold' }}</v-icon>
            </div>

            <div class="confidence-container">
              <!-- Strong Move Confidence -->
              <div class="confidence-item">
                <div class="confidence-details">
                  <span class="confidence-label">Move:</span>
                  <span class="confidence-value">{{ (prediction.strong_move_confidence * 100).toFixed(0) }}%</span>
                </div>
                <v-progress-linear :model-value="prediction.strong_move_confidence * 100" height="4" rounded color="primary">
                </v-progress-linear>
              </div>

              <!-- Direction Confidence - Only show if available -->
              <div v-if="prediction.direction_confidence" class="confidence-item">
                <div class="confidence-details">
                  <span class="confidence-label">Direction:</span>
                  <span class="confidence-value">{{ (prediction.direction_confidence * 100).toFixed(0) }}%</span>
                </div>
                <v-progress-linear :model-value="prediction.direction_confidence * 100" height="4" rounded :color="prediction.direction_prediction === 'UP' ? 'success' : 'error'">
                </v-progress-linear>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </CardContainer>
</template>

<script>
import CardContainer from '@/components/common/CardContainer.vue'

export default {
  name: 'PredictionListCard',
  components: { CardContainer },
  props: {
    title: { type: String, required: true },
    predictions: { type: Array, default: () => [] },
    loading: { type: Boolean, default: false },
    emptyMessage: { type: String, default: 'No predictions available' }
  },
  emits: ['refresh', 'view-all'],
  methods: {
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    }
  }
}
</script>

<style lang="postcss" scoped>
.prediction-list {
  @apply max-h-[300px] overflow-y-auto;
}

.empty-state {
  @apply flex items-center justify-center h-64 text-gray-500;
}

.predictions-container {
  @apply divide-y divide-gray-100;
}

.prediction-item {
  @apply flex flex-col px-4 py-3 hover:bg-gray-50 transition-colors duration-150;
}

.prediction-header {
  @apply flex justify-between items-center w-full mb-2;
}

.symbol {
  @apply font-semibold text-primary-dark text-sm tracking-wide;
}

.prediction-date {
  @apply text-xs text-gray-500;
}

.prediction-content {
  @apply flex items-center w-full;
}

.direction {
  @apply flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full mr-3;
}

.direction.up {
  @apply bg-success bg-opacity-10 text-success;
}

.direction.down {
  @apply bg-error bg-opacity-10 text-error;
}

.confidence-container {
  @apply flex-1 flex flex-col gap-2;
}

.confidence-item {
  @apply w-full;
}

.confidence-details {
  @apply flex justify-between items-center mb-1;
}

.confidence-label {
  @apply text-xs text-gray-500 font-medium;
}

.confidence-value {
  @apply text-xs font-semibold;
}
</style>