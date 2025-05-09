// src/components/symbols/tabs/ModelPerformanceTab.vue
<template>
  <div>
    <!-- Model Performance Summary -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
      <div class="metric-card">
        <div class="metric-header">
          <h3 class="metric-title">Accuracy</h3>
          <div class="metric-icon bg-primary-light">
            <v-icon color="primary" size="small">mdi-check-circle</v-icon>
          </div>
        </div>
        <div class="metric-value">{{ formatPercentage(modelStats.accuracy) }}</div>
        <div class="metric-trend" :class="modelStats.accuracyTrend >= 0 ? 'trend-up' : 'trend-down'">
          <v-icon size="small">{{ modelStats.accuracyTrend >= 0 ? 'mdi-arrow-up' : 'mdi-arrow-down' }}</v-icon>
          {{ Math.abs(modelStats.accuracyTrend).toFixed(1) }}% from previous version
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <h3 class="metric-title">Precision</h3>
          <div class="metric-icon bg-info-light">
            <v-icon color="info" size="small">mdi-target</v-icon>
          </div>
        </div>
        <div class="metric-value">{{ formatPercentage(modelStats.precision) }}</div>
        <div class="metric-trend" :class="modelStats.precisionTrend >= 0 ? 'trend-up' : 'trend-down'">
          <v-icon size="small">{{ modelStats.precisionTrend >= 0 ? 'mdi-arrow-up' : 'mdi-arrow-down' }}</v-icon>
          {{ Math.abs(modelStats.precisionTrend).toFixed(1) }}% from previous version
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <h3 class="metric-title">Recall</h3>
          <div class="metric-icon bg-warning-light">
            <v-icon color="warning" size="small">mdi-chart-bell-curve</v-icon>
          </div>
        </div>
        <div class="metric-value">{{ formatPercentage(modelStats.recall) }}</div>
        <div class="metric-trend" :class="modelStats.recallTrend >= 0 ? 'trend-up' : 'trend-down'">
          <v-icon size="small">{{ modelStats.recallTrend >= 0 ? 'mdi-arrow-up' : 'mdi-arrow-down' }}</v-icon>
          {{ Math.abs(modelStats.recallTrend).toFixed(1) }}% from previous version
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <h3 class="metric-title">F1 Score</h3>
          <div class="metric-icon bg-success-light">
            <v-icon color="success" size="small">mdi-check-decagram</v-icon>
          </div>
        </div>
        <div class="metric-value">{{ formatPercentage(modelStats.f1Score) }}</div>
        <div class="metric-trend" :class="modelStats.f1ScoreTrend >= 0 ? 'trend-up' : 'trend-down'">
          <v-icon size="small">{{ modelStats.f1ScoreTrend >= 0 ? 'mdi-arrow-up' : 'mdi-arrow-down' }}</v-icon>
          {{ Math.abs(modelStats.f1ScoreTrend).toFixed(1) }}% from previous version
        </div>
      </div>
    </div>

    <!-- History Chart & Model Details Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- Performance History Chart -->
      <div class="content-card lg:col-span-2">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Model Performance History</h3>
          <v-btn icon="mdi-refresh" variant="text" size="small" color="gray" @click="fetchModelHistory"></v-btn>
        </div>
        <div class="h-80 relative">
          <LineChart :chart-data="historyChartData" :options="historyChartOptions" />
          <div v-if="loading.history" class="loading-overlay">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </div>
        </div>
      </div>

      <!-- Model Details Card -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Current Model</h3>
          <v-btn color="primary" size="small" variant="tonal" :loading="loading.retraining" @click="retrainModel">
            Retrain Model
          </v-btn>
        </div>

        <div v-if="loading.details" class="flex justify-center items-center py-8">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <div v-else class="model-details">
          <div class="detail-item">
            <div class="detail-label">Model Version</div>
            <div class="detail-value">{{ modelDetails.version || 'v1.0.0' }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">Last Trained</div>
            <div class="detail-value">{{ formatDate(modelDetails.lastTrainedDate) }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">Last Evaluated</div>
            <div class="detail-value">{{ formatDate(modelDetails.lastEvaluatedDate) }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">Classifier Type</div>
            <div class="detail-value">{{ modelDetails.classifierType }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">Feature Count</div>
            <div class="detail-value">{{ modelDetails.featureCount || 0 }}</div>
          </div>

          <div class="detail-item">
            <div class="detail-label">Training Samples</div>
            <div class="detail-value">{{ formatNumber(modelDetails.trainingSamples) }}</div>
          </div>

          <div class="model-status mt-4">
            <div class="flex justify-between items-center mb-1">
              <div class="status-label">Model Health</div>
              <div class="status-value">{{ modelDetails.health || 'Good' }}</div>
            </div>
            <div class="health-bar">
              <div class="health-indicator" :class="getHealthClass(modelDetails.healthScore)" :style="{ width: `${modelDetails.healthScore || 85}%` }">
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Feature Importance & Confusion Matrix -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Feature Importance -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Feature Importance</h3>
          <v-btn size="x-small" icon="mdi-information" variant="text" color="gray"></v-btn>
        </div>

        <div v-if="loading.details" class="flex justify-center items-center py-8">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <div v-else-if="featureImportance.length" class="feature-importance">
          <div v-for="(feature, index) in featureImportance" :key="index" class="feature-item">
            <div class="feature-details">
              <div class="feature-rank">{{ index + 1 }}</div>
              <div class="feature-name">{{ feature.name }}</div>
              <div class="feature-score">{{ feature.importance.toFixed(2) }}</div>
            </div>
            <div class="feature-bar">
              <div class="feature-indicator" :style="{ width: `${feature.importance * 100}%` }"></div>
            </div>
          </div>
        </div>

        <div v-else class="flex justify-center items-center py-8 text-gray-500">
          <div class="text-center">
            <v-icon size="large" color="gray-300">mdi-chart-bar</v-icon>
            <p class="mt-2">Feature importance data not available</p>
          </div>
        </div>
      </div>

      <!-- Confusion Matrix -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Confusion Matrix</h3>
          <v-btn size="x-small" icon="mdi-information" variant="text" color="gray"></v-btn>
        </div>

        <div v-if="loading.details" class="flex justify-center items-center py-8">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <div v-else-if="confusionMatrix" class="confusion-matrix">
          <div class="matrix-container">
            <div class="matrix-labels">
              <div class="matrix-corner"></div>
              <div class="matrix-top-label">Predicted UP</div>
              <div class="matrix-top-label">Predicted DOWN</div>
              <div class="matrix-side-label">Actual UP</div>
              <div class="matrix-cell" :class="{ 'cell-correct': true }">
                <div class="cell-value">{{ confusionMatrix.truePositives }}</div>
                <div class="cell-subtext">True Positives</div>
              </div>
              <div class="matrix-cell" :class="{ 'cell-incorrect': true }">
                <div class="cell-value">{{ confusionMatrix.falseNegatives }}</div>
                <div class="cell-subtext">False Negatives</div>
              </div>
              <div class="matrix-side-label">Actual DOWN</div>
              <div class="matrix-cell" :class="{ 'cell-incorrect': true }">
                <div class="cell-value">{{ confusionMatrix.falsePositives }}</div>
                <div class="cell-subtext">False Positives</div>
              </div>
              <div class="matrix-cell" :class="{ 'cell-correct': true }">
                <div class="cell-value">{{ confusionMatrix.trueNegatives }}</div>
                <div class="cell-subtext">True Negatives</div>
              </div>
            </div>
          </div>

          <div class="matrix-legend mt-4 grid grid-cols-2 gap-2">
            <div class="legend-item">
              <div class="legend-color bg-green-100"></div>
              <div class="legend-text">Correct Predictions</div>
            </div>
            <div class="legend-item">
              <div class="legend-color bg-red-100"></div>
              <div class="legend-text">Incorrect Predictions</div>
            </div>
          </div>
        </div>

        <div v-else class="flex justify-center items-center py-8 text-gray-500">
          <div class="text-center">
            <v-icon size="large" color="gray-300">mdi-grid</v-icon>
            <p class="mt-2">Confusion matrix data not available</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useSymbolStore } from '@/store/symbol.store';
import { useModelStore } from '@/store/model.store';
import LineChart from '@/components/charts/LineChart.vue';
import { formatDate, formatNumber, formatPercentage } from '@/utils/format';

export default {
  name: 'ModelPerformanceTab',
  components: {
    LineChart
  },
  props: {
    symbol: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      symbolStore: useSymbolStore(),
      modelStore: useModelStore(),
      loading: {
        details: false,
        history: false,
        retraining: false
      },
      modelStats: {
        accuracy: 0.82,
        precision: 0.77,
        recall: 0.85,
        f1Score: 0.81,
        accuracyTrend: 2.3,
        precisionTrend: 1.5,
        recallTrend: -0.7,
        f1ScoreTrend: 1.1
      },
      modelDetails: {
        version: 'v2.3.1',
        lastTrainedDate: '2024-12-15',
        lastEvaluatedDate: '2024-12-20',
        classifierType: 'LightGBM',
        featureCount: 27,
        trainingSamples: 12450,
        health: 'Good',
        healthScore: 85
      },
      modelHistory: [],
      featureImportance: [
        { name: 'MACD Signal', importance: 0.85 },
        { name: 'Volume Change 5d', importance: 0.78 },
        { name: 'Bollinger %B', importance: 0.72 },
        { name: 'RSI 14', importance: 0.68 },
        { name: 'ADX', importance: 0.65 },
        { name: 'Price/SMA 50', importance: 0.62 },
        { name: 'OBV Normalized', importance: 0.58 },
        { name: 'ATR Ratio', importance: 0.55 }
      ],
      confusionMatrix: {
        truePositives: 235,
        falsePositives: 62,
        falseNegatives: 53,
        trueNegatives: 212
      },
      historyChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          },
          legend: {
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 1,
            ticks: {
              callback: function (value) {
                return (value * 100) + '%';
              }
            }
          }
        }
      }
    };
  },
  computed: {
    historyChartData() {
      if (!this.modelHistory?.length) {
        return {
          labels: [],
          datasets: []
        };
      }

      // Sort by date
      const sortedHistory = [...this.modelHistory].sort((a, b) =>
        new Date(a.date) - new Date(b.date)
      );

      // Prepare data for chart
      const dates = sortedHistory.map(item => formatDate(item.date));
      const accuracyData = sortedHistory.map(item => item.accuracy);
      const precisionData = sortedHistory.map(item => item.precision);
      const recallData = sortedHistory.map(item => item.recall);
      const f1Data = sortedHistory.map(item => item.f1Score);

      return {
        labels: dates,
        datasets: [
          {
            label: 'Accuracy',
            data: accuracyData,
            borderColor: '#1E3A8A', // primary
            backgroundColor: 'rgba(30, 58, 138, 0.1)',
            tension: 0.3,
            fill: false
          },
          {
            label: 'Precision',
            data: precisionData,
            borderColor: '#60A5FA', // info
            backgroundColor: 'transparent',
            tension: 0.3,
            fill: false
          },
          {
            label: 'Recall',
            data: recallData,
            borderColor: '#F59E0B', // warning
            backgroundColor: 'transparent',
            tension: 0.3,
            fill: false
          },
          {
            label: 'F1 Score',
            data: f1Data,
            borderColor: '#10B981', // success
            backgroundColor: 'transparent',
            tension: 0.3,
            fill: false
          }
        ]
      };
    }
  },
  methods: {
    formatDate,
    formatNumber,
    formatPercentage,

    getHealthClass(score) {
      if (!score) return 'health-good';
      if (score >= 80) return 'health-good';
      if (score >= 60) return 'health-warning';
      return 'health-poor';
    },

    async fetchModelDetails() {
      this.loading.details = true;
      try {
        // In a real implementation, fetch from API
        const response = await this.modelStore.fetchModelDetails(this.symbol.trading_symbol);

        if (response) {
          this.modelDetails = response.details;
          this.modelStats = response.stats;
          this.featureImportance = response.featureImportance;
          this.confusionMatrix = response.confusionMatrix;
        }
      } catch (error) {
        console.error('Error fetching model details:', error);
        // Leave default data
      } finally {
        this.loading.details = false;
      }
    },

    async fetchModelHistory() {
      this.loading.history = true;
      try {
        // In a real implementation, fetch from API
        const history = await this.modelStore.fetchModelHistory(this.symbol.trading_symbol);

        if (history) {
          this.modelHistory = history;
        } else {
          // Generate some sample data if real data not available
          this.generateSampleModelHistory();
        }
      } catch (error) {
        console.error('Error fetching model history:', error);
        // Generate sample data on error
        this.generateSampleModelHistory();
      } finally {
        this.loading.history = false;
      }
    },

    generateSampleModelHistory() {
      // Generate sample history data if API call fails
      const history = [];
      const today = new Date();

      for (let i = 10; i >= 0; i--) {
        const date = new Date();
        date.setMonth(today.getMonth() - i);

        // Each version improves slightly with some random variation
        const baseAccuracy = 0.65 + (i * 0.015);
        const accuracy = Math.min(baseAccuracy + (Math.random() * 0.05 - 0.025), 0.95);
        const precision = Math.min(baseAccuracy - 0.05 + (Math.random() * 0.06 - 0.03), 0.95);
        const recall = Math.min(baseAccuracy + 0.02 + (Math.random() * 0.06 - 0.03), 0.95);
        const f1Score = Math.min((2 * precision * recall) / (precision + recall), 0.95);

        history.push({
          date: date.toISOString().split('T')[0],
          version: `v${1 + Math.floor(i / 3)}.${(i % 3) + 1}.0`,
          accuracy,
          precision,
          recall,
          f1Score
        });
      }

      this.modelHistory = history;
    },

    async retrainModel() {
      this.loading.retraining = true;
      try {
        await this.modelStore.retrainModel(this.symbol.trading_symbol);
        // Success message
        this.$toast.success(`Model retraining initiated for ${this.symbol.trading_symbol}`);

        // Refetch details after a short delay to allow backend to update
        setTimeout(() => {
          this.fetchModelDetails();
          this.fetchModelHistory();
        }, 2000);
      } catch (error) {
        console.error('Error retraining model:', error);
        this.$toast.error('Failed to initiate model retraining');
      } finally {
        this.loading.retraining = false;
      }
    }
  },
  mounted() {
    this.fetchModelDetails();
    this.fetchModelHistory();
  },
  watch: {
    'symbol.trading_symbol': {
      handler(newSymbol) {
        if (newSymbol) {
          this.fetchModelDetails();
          this.fetchModelHistory();
        }
      },
      immediate: true
    }
  }
};
</script>

<style lang="postcss" scoped>
.content-card {
  @apply bg-gray-50 rounded-lg p-4 border border-gray-100;
}

.metric-card {
  @apply bg-white p-4 rounded-lg shadow-sm border border-gray-200;
}

.metric-header {
  @apply flex justify-between items-center mb-2;
}

.metric-title {
  @apply text-sm font-medium text-gray-600;
}

.metric-icon {
  @apply w-8 h-8 rounded-lg flex items-center justify-center;
}

.bg-primary-light {
  @apply bg-primary bg-opacity-10;
}

.bg-info-light {
  @apply bg-info bg-opacity-10;
}

.bg-warning-light {
  @apply bg-warning bg-opacity-10;
}

.bg-success-light {
  @apply bg-success bg-opacity-10;
}

.metric-value {
  @apply text-2xl font-bold mb-1;
}

.metric-trend {
  @apply text-xs flex items-center gap-1;
}

.trend-up {
  @apply text-success;
}

.trend-down {
  @apply text-error;
}

.loading-overlay {
  @apply absolute top-0 left-0 w-full h-full flex items-center justify-center bg-white/70;
}

.model-details {
  @apply space-y-3;
}

.detail-item {
  @apply flex justify-between;
}

.detail-label {
  @apply text-xs text-gray-500;
}

.detail-value {
  @apply text-sm font-medium;
}

.model-status {
  @apply bg-gray-100 p-3 rounded-lg;
}

.status-label {
  @apply text-xs text-gray-500;
}

.status-value {
  @apply text-xs font-medium;
}

.health-bar {
  @apply h-2 bg-gray-200 rounded-full overflow-hidden;
}

.health-indicator {
  @apply h-full;
}

.health-good {
  @apply bg-success;
}

.health-warning {
  @apply bg-warning;
}

.health-poor {
  @apply bg-error;
}

.feature-importance {
  @apply space-y-3;
}

.feature-item {
  @apply space-y-1;
}

.feature-details {
  @apply flex items-center;
}

.feature-rank {
  @apply w-5 h-5 rounded-full bg-gray-100 flex items-center justify-center text-xs font-medium text-gray-600 mr-2;
}

.feature-name {
  @apply text-sm flex-1;
}

.feature-score {
  @apply text-xs font-medium;
}

.feature-bar {
  @apply h-1.5 bg-gray-200 rounded-full overflow-hidden;
}

.feature-indicator {
  @apply h-full bg-primary;
}

.confusion-matrix {
  @apply p-4;
}

.matrix-container {
  @apply flex justify-center;
}

.matrix-labels {
  @apply grid grid-cols-3 gap-1 text-center;
}

.matrix-corner {
  @apply bg-gray-100 rounded-tl-lg;
}

.matrix-top-label {
  @apply bg-gray-100 p-2 text-xs font-medium;
}

.matrix-side-label {
  @apply bg-gray-100 p-2 flex items-center justify-center text-xs font-medium;
}

.matrix-cell {
  @apply p-3 rounded-lg;
}

.cell-correct {
  @apply bg-green-100;
}

.cell-incorrect {
  @apply bg-red-100;
}

.cell-value {
  @apply text-lg font-bold;
}

.cell-subtext {
  @apply text-xs text-gray-500;
}

.matrix-legend {
  @apply text-xs;
}

.legend-item {
  @apply flex items-center gap-2;
}

.legend-color {
  @apply w-3 h-3 rounded;
}

.legend-text {
  @apply text-gray-600;
}
</style>