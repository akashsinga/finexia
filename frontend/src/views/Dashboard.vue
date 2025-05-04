<template>
  <div class="dashboard">
    <!-- Performance Overview Section -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <StatCard label="Total Predictions" :value="stats.totalPredictions || 0" icon="mdi-chart-timeline-variant" icon-color="primary" icon-background="bg-primary-light" :change-text="`${Math.abs(stats.predictionChange)}% from last week`" :change-type="stats.predictionChange >= 0 ? 'positive' : 'negative'" />

      <StatCard label="Prediction Accuracy" :value="`${(stats.accuracy * 100).toFixed(1)}%`" icon="mdi-check-circle" icon-color="success" icon-background="bg-success-light" :change-text="`${Math.abs(stats.accuracyChange)}% from last week`" :change-type="stats.accuracyChange >= 0 ? 'positive' : 'negative'" />

      <StatCard label="Today's Predictions" :value="stats.todayPredictions || 0" icon="mdi-calendar-check" icon-color="info" icon-background="bg-info-light" :change-text="`Updated ${lastUpdateTime}`" change-type="neutral" />

      <StatCard label="Active Models" :value="stats.activeModels || 0" icon="mdi-brain" icon-color="warning" icon-background="bg-warning-light" :change-text="`${stats.newModels || 0} new this week`" change-type="positive" />
    </div>
    <!-- Charts & Predictions Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- Prediction Accuracy Trend -->
      <LineChartCard title="Prediction Accuracy Trend" :chart-data="accuracyTrendData" :chart-options="accuracyChartOptions" :loading="loading.accuracyTrend" :periods="timePeriods" @refresh="refreshAccuracyTrend" @period-change="setAccuracyPeriod" />

      <!-- Direction Predictions -->
      <DoughnutChartCard title="Direction Predictions" :chart-data="directionData" :chart-options="directionChartOptions" :loading="loading.directionStats" @refresh="refreshDirectionStats">
        <template #chart-details>
          <div class="flex justify-center gap-8">
            <div class="text-center">
              <div class="text-sm text-gray-500">UP Predictions</div>
              <div class="text-xl font-semibold text-success">{{ directionStats.upPredictions || 0 }}</div>
              <div class="text-xs">{{ directionStats.upAccuracy ? (directionStats.upAccuracy * 100).toFixed(1) + '%' : 'N/A' }} Accuracy</div>
            </div>
            <div class="text-center">
              <div class="text-sm text-gray-500">DOWN Predictions</div>
              <div class="text-xl font-semibold text-error">{{ directionStats.downPredictions || 0 }}</div>
              <div class="text-xs">{{ directionStats.downAccuracy ? (directionStats.downAccuracy * 100).toFixed(1) + '%' : 'N/A' }} Accuracy</div>
            </div>
          </div>
        </template>
      </DoughnutChartCard>

      <!-- Top Predictions -->
      <PredictionListCard title="High Confidence Predictions" :predictions="topPredictions" :loading="loading.topPredictions" empty-message="No high confidence predictions available" @refresh="refreshTopPredictions" @view-all="navigateTo('Predictions')" />
    </div>

    <!-- Recent Verifications & Model Performance -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Recent Verified Predictions -->
      <DataTableCard title="Recently Verified Predictions" :headers="verifiedPredictionsHeaders" :loading="loading.verifiedPredictions" :is-empty="verifiedPredictions.length === 0" empty-message="No verified predictions available" @refresh="refreshVerifiedPredictions" @view-all="navigateTo('Predictions')">
        <tr v-for="(prediction, i) in verifiedPredictions" :key="i">
          <td>{{ prediction.trading_symbol }}</td>
          <td :class="prediction.direction_prediction === 'UP' ? 'text-success' : 'text-error'">
            {{ prediction.direction_prediction }}
          </td>
          <td :class="prediction.actual_direction === 'UP' ? 'text-success' : 'text-error'">
            {{ prediction.actual_direction }}
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
          <td>{{ $filters.formatDate(model.evaluation_date, 'MMM D') }}</td>
        </tr>
      </DataTableCard>
    </div>
  </div>
</template>
<script>
import { api } from '@/plugins'

// Import components
import StatCard from '@/components/dashboard/StatCard.vue'
import LineChartCard from '@/components/dashboard/LineChartCard.vue'
import DoughnutChartCard from '@/components/dashboard/DoughnutChartCard.vue'
import PredictionListCard from '@/components/dashboard/PredictionListCard.vue'
import DataTableCard from '@/components/dashboard/DataTableCard.vue'

export default {
  components: {
    StatCard,
    LineChartCard,
    DoughnutChartCard,
    PredictionListCard,
    DataTableCard
  },
  data: function () {
    return {
      stats: {
        totalPredictions: 0,
        predictionChange: 0,
        accuracy: 0,
        accuracyChange: 0,
        todayPredictions: 0,
        activeModels: 0,
        newModels: 0
      },
      directionStats: {
        upPredictions: 0,
        downPredictions: 0,
        upAccuracy: 0,
        downAccuracy: 0
      },
      loading: {
        systemStatus: true,
        accuracyTrend: true,
        directionStats: true,
        topPredictions: true,
        verifiedPredictions: true,
        modelPerformance: true
      },
      topPredictions: [],
      verifiedPredictions: [],
      topModels: [],
      lastUpdateTime: 'Just now',
      accuracyPeriod: '30d',
      accuracyTrendData: {
        labels: [],
        datasets: [
          {
            label: 'Prediction Accuracy',
            data: [],
            borderColor: '#1E3A8A',
            backgroundColor: 'rgba(30, 58, 138, 0.1)',
            tension: 0.3,
            fill: true
          }
        ]
      },
      timePeriods: [
        { label: 'Last 7 Days', value: '7d' },
        { label: 'Last 30 Days', value: '30d' },
        { label: 'Last 90 Days', value: '90d' }
      ],
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
    directionData: function () {
      return {
        labels: ['UP', 'DOWN'],
        datasets: [
          {
            data: [
              this.directionStats.upPredictions || 0,
              this.directionStats.downPredictions || 0
            ],
            backgroundColor: [
              '#4ADE80', // success color for UP
              '#EF4444'  // error color for DOWN
            ],
            hoverOffset: 4
          }
        ]
      }
    }
  },
  methods: {
    fetchSystemStatus: function () {
      this.loading.systemStatus = true
      return api.get('/system/status')
        .then(response => {
          this.stats.totalPredictions = response.data.total_predictions
          this.stats.todayPredictions = response.data.today_predictions

          // Calculate change - this would come from your API in a real implementation
          this.stats.predictionChange = 5 // placeholder

          // Update last refresh time
          this.updateLastRefreshTime()
        })
        .catch(error => {
          console.error('Error fetching system status:', error)
        })
        .finally(() => {
          this.loading.systemStatus = false
        })
    },

    fetchPredictionStats: function () {
      return api.get('/predictions/status/accuracy')
        .then(response => {
          this.stats.accuracy = response.data.accuracy || 0
          this.stats.accuracyChange = 2.3 // placeholder

          this.directionStats.upPredictions = response.data.up_predictions || 0
          this.directionStats.downPredictions = response.data.down_predictions || 0

          // Calculate direction accuracies - these could come from your API
          if (response.data.direction_accuracy) {
            this.directionStats.upAccuracy = response.data.direction_accuracy
            this.directionStats.downAccuracy = response.data.direction_accuracy
          }
        })
        .catch(error => {
          console.error('Error fetching prediction stats:', error)
        })
    },
    fetchAccuracyTrend: function () {
      this.loading.accuracyTrend = true

      // This would be a real API call in production
      // return api.get(`/predictions/accuracy/trend?period=${this.accuracyPeriod}`)

      // Placeholder data generation for demo
      setTimeout(() => {
        const labels = []
        const data = []

        // Generate placeholder data based on selected period
        const days = this.accuracyPeriod === '7d' ? 7 :
          this.accuracyPeriod === '30d' ? 30 : 90

        const now = new Date()
        for (let i = days - 1; i >= 0; i--) {
          const date = new Date(now)
          date.setDate(date.getDate() - i)
          labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }))

          // Random accuracy between 0.7 and 0.9
          data.push(0.7 + Math.random() * 0.2)
        }

        this.accuracyTrendData = {
          labels,
          datasets: [
            {
              label: 'Prediction Accuracy',
              data,
              borderColor: '#1E3A8A',
              backgroundColor: 'rgba(30, 58, 138, 0.1)',
              tension: 0.3,
              fill: true
            }
          ]
        }

        this.loading.accuracyTrend = false
      }, 800)

      return Promise.resolve()
    },

    fetchTopPredictions: function () {
      this.loading.topPredictions = true
      return api.get('/predictions', {
        params: {
          min_confidence: 0.7,
          limit: 5
        }
      })
        .then(response => {
          this.topPredictions = response.data.predictions || []
        })
        .catch(error => {
          console.error('Error fetching top predictions:', error)
        })
        .finally(() => {
          this.loading.topPredictions = false
        })
    },
    fetchVerifiedPredictions: function () {
      this.loading.verifiedPredictions = true
      return api.get('/predictions', {
        params: {
          verified: true,
          limit: 10
        }
      })
        .then(response => {
          this.verifiedPredictions = response.data.predictions || []
        })
        .catch(error => {
          console.error('Error fetching verified predictions:', error)
        })
        .finally(() => {
          this.loading.verifiedPredictions = false
        })
    },

    fetchModelPerformance: function () {
      this.loading.modelPerformance = true
      return api.get('/models/performance', {
        params: {
          top_n: 5,
          metric: 'f1_score'
        }
      })
        .then(response => {
          this.topModels = response.data || []
          this.stats.activeModels = this.topModels.length
        })
        .catch(error => {
          console.error('Error fetching model performance:', error)
        })
        .finally(() => {
          this.loading.modelPerformance = false
        })
    }, updateLastRefreshTime: function () {
      const now = new Date()
      this.lastUpdateTime = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    },

    refreshAccuracyTrend: function () {
      this.fetchAccuracyTrend()
    },

    refreshDirectionStats: function () {
      this.loading.directionStats = true
      this.fetchPredictionStats()
        .finally(() => {
          this.loading.directionStats = false
        })
    },

    refreshTopPredictions: function () {
      this.fetchTopPredictions()
    },

    refreshVerifiedPredictions: function () {
      this.fetchVerifiedPredictions()
    },

    refreshModelPerformance: function () {
      this.fetchModelPerformance()
    },

    setAccuracyPeriod: function (period) {
      this.accuracyPeriod = period
      this.fetchAccuracyTrend()
    },

    navigateTo: function (routeName) {
      this.$router.push({ name: routeName })
    },

    loadAllData: function () {
      // Load all data in parallel
      return Promise.all([
        this.fetchSystemStatus(),
        this.fetchPredictionStats(),
        this.fetchAccuracyTrend(),
        this.fetchTopPredictions(),
        this.fetchVerifiedPredictions(),
        this.fetchModelPerformance()
      ])
    }
  },

  mounted: function () {
    this.loadAllData()
  }
}
</script>
<style lang="postcss" scoped>
.dashboard {
  @apply max-w-full;
}
</style>