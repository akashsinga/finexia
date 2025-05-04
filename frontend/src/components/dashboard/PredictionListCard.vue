<template>
  <CardContainer :title="title" :loading="loading" :full-height="true" :no-padding="true" class="min-h-[350px]">
    <template #actions>
      <v-btn size="small" variant="text" @click="$emit('refresh')">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
      <v-btn size="small" variant="text" @click="$emit('view-all')">
        <v-icon>mdi-arrow-right</v-icon>
      </v-btn>
    </template>

    <div class="prediction-list">
      <v-list class="px-0">
        <v-list-item v-for="(prediction, i) in predictions" :key="i" :class="i % 2 === 0 ? 'bg-gray-50' : ''">
          <div class="flex w-full items-center">
            <div class="prediction-symbol font-medium">{{ prediction.trading_symbol }}</div>
            <div :class="['prediction-direction ml-auto', prediction.direction_prediction === 'UP' ? 'text-success' : 'text-error']">
              <v-icon size="small">{{ prediction.direction_prediction === 'UP' ? 'mdi-arrow-up' : 'mdi-arrow-down' }}</v-icon>
              {{ prediction.direction_prediction }}
            </div>
            <div class="prediction-confidence ml-4">
              <v-progress-linear :model-value="prediction.strong_move_confidence * 100" height="8" rounded :color="prediction.direction_prediction === 'UP' ? 'success' : 'error'"></v-progress-linear>
              <div class="text-xs text-right mt-1">{{ (prediction.strong_move_confidence * 100).toFixed(0) }}%</div>
            </div>
          </div>
        </v-list-item>
        <v-list-item v-if="predictions.length === 0" class="text-center text-gray-500">
          {{ emptyMessage }}
        </v-list-item>
      </v-list>
    </div>
  </CardContainer>
</template>

<script>
import CardContainer from '@/components/common/CardContainer.vue'

export default {
  name: 'PredictionListCard',
  components: {
    CardContainer
  },
  props: {
    title: {
      type: String,
      required: true
    },
    predictions: {
      type: Array,
      default: function () {
        return []
      }
    },
    loading: {
      type: Boolean,
      default: false
    },
    emptyMessage: {
      type: String,
      default: 'No predictions available'
    }
  },
  emits: ['refresh', 'view-all']
}
</script>

<style lang="postcss" scoped>
.prediction-list {
  @apply max-h-[280px] overflow-y-auto;
}

.prediction-symbol {
  @apply w-1/4;
}

.prediction-direction {
  @apply flex items-center;
}

.prediction-confidence {
  @apply w-1/3;
}
</style>