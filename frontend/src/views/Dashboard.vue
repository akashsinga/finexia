<template>
  <div class="dashboard">
    <!-- Performance Overview Section -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <StatCard label="Total Predictions" :value="systemStats.totalPredictions || 0" icon="mdi-chart-timeline-variant" icon-color="primary" icon-background="bg-primary-light" :change-text="`${Math.abs(systemStats.predictionChange)}% from last week`" :change-type="systemStats.predictionChange >= 0 ? 'positive' : 'negative'" />

      <StatCard label="Prediction Accuracy" :value="`${(predictionStats.accuracy * 100).toFixed(1)}%`" icon="mdi-check-circle" icon-color="success" icon-background="bg-success-light" :change-text="`${Math.abs(predictionStats.accuracyChange)}% from last week`" :change-type="predictionStats.accuracyChange >= 0 ? 'positive' : 'negative'" />

      <StatCard label="Today's Predictions" :value="systemStats.todayPredictions || 0" icon="mdi-calendar-check" icon-color="info" icon-background="bg-info-light" :change-text="`Updated ${lastUpdateTime}`" change-type="neutral" />

      <StatCard label="Active Models" :value="systemStats.activeModels || 0" icon="mdi-brain" icon-color="warning" icon-background="bg-warning-light" :change-text="`${systemStats.newModels || 0} new this week`" change-type="positive" />
    </div>
    <!-- Charts & Predictions Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- Prediction Accuracy Trend -->
      <LineChartCard title="Prediction Accuracy Trend" :chart-data="accuracyTrendData" :chart-options="accuracyChartOptions" :isPercentage="true" :loading="loading.accuracyTrend" :periods="timePeriods" @refresh="refreshAccuracyTrend" @period-change="setAccuracyPeriod" />

      <!-- Direction Predictions -->
      <DirectionPredictionsCard :direction-stats="directionStats" :loading="loading.directionStats" @refresh="refreshDirectionStats" />

      <!-- Top Predictions -->
      <PredictionListCard title="High Confidence Predictions" :predictions="topPredictions" :loading="loading.topPredictions" empty-message="No high confidence predictions available" @refresh="refreshTopPredictions" @view-all="navigateTo('Predictions')" />
    </div>

    <!-- Recent Verifications & Model Performance -->
    <div class="grid grid-cols-1 gap-6">
      <!-- Recent Verified Predictions -->
      <DataTableCard title="Recently Verified Predictions" :headers="verifiedPredictionsHeaders" :loading="loading.verifiedPredictions" :is-empty="verifiedPredictions.length === 0" empty-message="No verified predictions available" @refresh="refreshVerifiedPredictions" @view-all="navigateTo('Predictions')">
        <tr v-for="(prediction, i) in verifiedPredictions" :key="i">
          <td>{{ prediction.trading_symbol }}</td>
          <td :class="prediction.direction_prediction === 'UP' ? 'text-success' : 'text-error'">
            <v-icon size="large">{{ prediction.direction_prediction === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold' }}</v-icon>
          </td>
          <td :class="prediction.actual_direction === 'UP' ? 'text-success' : 'text-error'">
            <v-icon size="large">{{ prediction.actual_direction === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold' }}</v-icon>
          </td>
          <td>{{ $filters.formatDate(prediction.date, 'MMM D, YYYY') }}</td>
          <td>{{ prediction.days_to_fulfill }}</td>
          <td>
            <v-chip size="small" :color="prediction.verified ? 'success' : 'error'" text-color="white">
              {{ prediction.verified ? 'Success' : 'Failed' }}
            </v-chip>
          </td>
        </tr>
      </DataTableCard>

      <!-- Top Performing Models -->
      <DataTableCard title="Top Performing Models" :headers="modelPerformanceHeaders" :loading="loading.modelPerformance" :is-empty="topModels.length === 0" empty-message="No model performance data available" @refresh="refreshModelPerformance" @view-all="navigateTo('ModelPerformance')">
        <tr v-for="(model, i) in topModels" :key="i">
          <td>{{ model.trading_symbol }}</td>
          <td>{{ (model.accuracy * 100).toFixed(1) }}%</td>
          <td>{{ (model.precision * 100).toFixed(1) }}%</td>
          <td>{{ (model.recall * 100).toFixed(1) }}%</td>
          <td>{{ (model.f1_score * 100).toFixed(1) }}%</td>
          <td>{{ $filters.formatDate(model.evaluation_date, 'MMM D, YYYY') }}</td>
        </tr>
      </DataTableCard>
    </div>
  </div>
</template>
<script>
import { useSystemStore } from '@/store/system.store'
import { usePredictionStore } from '@/store/prediction.store'
import { useModelStore } from '@/store/model.store'

// Import components
import StatCard from '@/components/dashboard/StatCard.vue'
import LineChartCard from '@/components/dashboard/LineChartCard.vue'
import DirectionPredictionsCard from '@/components/dashboard/DirectionPredictionsCard.vue';
import PredictionListCard from '@/components/dashboard/PredictionListCard.vue'
import DataTableCard from '@/components/dashboard/DataTableCard.vue'

export default {
  components: {
    StatCard,
    LineChartCard,
    DirectionPredictionsCard,
    PredictionListCard,
    DataTableCard
  },

  setup() {
    const systemStore = useSystemStore()
    const predictionStore = usePredictionStore()
    const modelStore = useModelStore()

    return {
      systemStore,
      predictionStore,
      modelStore
    }
  },

  data: function () {
    return {
      accuracyPeriod: 7,
      accuracyChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 1,
            ticks: {
              callback: function (value) {
                return (value * 100) + '%'
              }
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return 'Accuracy: ' + (context.parsed.y * 100).toFixed(1) + '%'
              }
            }
          }
        }
      },
      directionChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        cutout: '70%'
      },
      timePeriods: [
        { label: 'Last 7 Days', value: 7 },
        { label: 'Last 30 Days', value: 30 },
        { label: 'Last 90 Days', value: 90 }
      ],
      verifiedPredictionsHeaders: [
        { text: 'Symbol', value: 'trading_symbol' },
        { text: 'Prediction', value: 'direction_prediction' },
        { text: 'Actual', value: 'actual_direction' },
        { text: 'Date', value: 'date' },
        { text: 'Days to Verify', value: 'days_to_fulfill' },
        { text: 'Status', value: 'verified' }
      ],
      modelPerformanceHeaders: [
        { text: 'Symbol', value: 'trading_symbol' },
        { text: 'Accuracy', value: 'accuracy' },
        { text: 'Precision', value: 'precision' },
        { text: 'Recall', value: 'recall' },
        { text: 'F1 Score', value: 'f1_score' },
        { text: 'Last Eval', value: 'evaluation_date' }
      ]
    }
  },

  computed: {
    systemStats() {
      return this.systemStore.stats
    },
    lastUpdateTime() {
      return this.systemStore.lastUpdateTime
    },
    predictionStats() {
      return this.predictionStore.stats
    },
    directionStats() {
      return {
        upPredictions: this.predictionStore.stats.upPredictions,
        downPredictions: this.predictionStore.stats.downPredictions,
        upAccuracy: this.predictionStore.stats.upAccuracy,
        downAccuracy: this.predictionStore.stats.downAccuracy
      }
    },
    topPredictions() {
      return this.predictionStore.topPredictions
    },
    verifiedPredictions() {
      return this.predictionStore.verifiedPredictions
    },
    accuracyTrendData() {
      return this.predictionStore.accuracyTrend
    },
    topModels() {
      return this.modelStore.topModels
    },
    loading() {
      return {
        systemStatus: this.systemStore.loading,
        accuracyTrend: this.predictionStore.loading.accuracyTrend,
        directionStats: this.predictionStore.loading.stats,
        topPredictions: this.predictionStore.loading.topPredictions,
        verifiedPredictions: this.predictionStore.loading.verifiedPredictions,
        modelPerformance: this.modelStore.loading
      }
    },
    directionData() {
      const upCount = this.directionStats.upPredictions || 0;
      const downCount = this.directionStats.downPredictions || 0;

      if (upCount === 0 && downCount === 0) {
        return {
          labels: ['No Data'],
          datasets: [{
            data: [1],
            backgroundColor: ['#94a3b8'], // Gray for no data
          }]
        };
      }

      return {
        labels: ['UP', 'DOWN'],
        datasets: [
          {
            data: [upCount, downCount],
            backgroundColor: ['#4ADE80', '#EF4444'],
            hoverOffset: 4
          }
        ]
      }
    }
  },

  methods: {
    refreshSystemStatus() {
      return this.systemStore.fetchSystemStatus();
    },

    refreshDirectionStats() {
      return this.predictionStore.fetchPredictionStats();
    },

    refreshAccuracyTrend() {
      return this.predictionStore.fetchAccuracyTrend(this.accuracyPeriod);
    },

    refreshTopPredictions() {
      return this.predictionStore.fetchTopPredictions();
    },

    refreshVerifiedPredictions() {
      return this.predictionStore.fetchVerifiedPredictions();
    },

    refreshModelPerformance() {
      return this.modelStore.fetchModelPerformance();
    },

    setAccuracyPeriod(period) {
      this.accuracyPeriod = period;
      this.refreshAccuracyTrend();
    },

    navigateTo(routeName) {
      this.$router.push({ name: routeName });
    },

    loadAllData() {
      return Promise.all([
        this.refreshSystemStatus(),
        this.refreshDirectionStats(),
        this.refreshAccuracyTrend(),
        this.refreshTopPredictions(),
        this.refreshVerifiedPredictions(),
        this.refreshModelPerformance()
      ]);
    }
  },

  mounted() {
    this.loadAllData();
  }
}
</script>
<style lang="postcss" scoped>
.dashboard {
  @apply max-w-full;
}
</style>