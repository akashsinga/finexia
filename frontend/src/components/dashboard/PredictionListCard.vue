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
          <div class="symbol">{{ prediction.trading_symbol }}</div>
          <div :class="['direction', prediction.direction_prediction === 'UP' ? 'up' : 'down']">
            <v-icon size="small">{{ prediction.direction_prediction === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold' }}</v-icon>
          </div>
          <div class="confidence">
            <span class="value">{{ (prediction.strong_move_confidence * 100).toFixed(0) }}%</span>
            <v-progress-linear :model-value="prediction.strong_move_confidence * 100" height="6" rounded :color="prediction.direction_prediction === 'UP' ? 'success' : 'error'"></v-progress-linear>
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
  emits: ['refresh', 'view-all']
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
  @apply flex items-center px-4 py-3 hover:bg-gray-50 transition-colors duration-150;
}

.symbol {
  @apply w-24 font-semibold text-primary-dark text-sm tracking-wide pl-2 py-1;
}

.direction {
  @apply flex items-center justify-center w-8 h-8 rounded-full mx-4;
}

.direction.up {
  @apply bg-success bg-opacity-10 text-success;
}

.direction.down {
  @apply bg-error bg-opacity-10 text-error;
}

.confidence {
  @apply flex-1;
}

.value {
  @apply text-xs font-medium float-right mb-1;
}
</style>
