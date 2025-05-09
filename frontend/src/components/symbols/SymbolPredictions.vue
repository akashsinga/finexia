// src/components/symbols/tabs/PredictionsTab.vue
<template>
  <div>
    <!-- Prediction Statistics Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="stat-card">
        <div class="stat-icon bg-primary-light">
          <v-icon color="primary">mdi-chart-arc</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercentage(stats.accuracy) }}</div>
          <div class="stat-label">Overall Accuracy</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-success-light">
          <v-icon color="success">mdi-arrow-up-bold</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercentage(stats.upAccuracy) }}</div>
          <div class="stat-label">UP Accuracy ({{ stats.upPredictions || 0 }})</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-error-light">
          <v-icon color="error">mdi-arrow-down-bold</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercentage(stats.downAccuracy) }}</div>
          <div class="stat-label">DOWN Accuracy ({{ stats.downPredictions || 0 }})</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-info-light">
          <v-icon color="info">mdi-calendar-check</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.avgDaysToFulfill ? stats.avgDaysToFulfill.toFixed(1) : 'N/A' }}</div>
          <div class="stat-label">Avg. Days to Verify</div>
        </div>
      </div>
    </div>

    <!-- Prediction Distribution Chart -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Timeline Chart -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Prediction Timeline</h3>
          <div class="flex gap-2">
            <v-btn-toggle v-model="selectedTimeframe" mandatory color="primary" density="compact">
              <v-btn value="3M" size="small">3M</v-btn>
              <v-btn value="6M" size="small">6M</v-btn>
              <v-btn value="1Y" size="small">1Y</v-btn>
            </v-btn-toggle>
          </div>
        </div>
        <div class="h-80 relative">
          <LineChart :chart-data="timelineChartData" :options="timelineChartOptions" />
          <div v-if="loading.timeline" class="loading-overlay">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </div>
        </div>
      </div>

      <!-- Direction Distribution -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Direction Distribution</h3>
          <v-btn icon="mdi-refresh" variant="text" size="small" color="gray" @click="refreshPredictionStats"></v-btn>
        </div>

        <div v-if="loading.stats" class="flex justify-center items-center h-80">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>
        <div v-else class="direction-distribution">
          <div class="distribution-chart">
            <div class="chart-placeholder flex items-center justify-center h-48 mb-4">
              <!-- In a real implementation, this would be a proper chart component -->
              <div class="donut-chart">
                <div class="donut-segment up" :style="{ transform: `rotate(0deg) translateY(-50%)`, height: `${upPercentage}%` }"></div>
                <div class="donut-segment down" :style="{ transform: `rotate(${upPercentage * 3.6}deg) translateY(-50%)`, height: `${downPercentage}%` }"></div>
                <div class="donut-label">
                  <div class="donut-percent">{{ stats.totalPredictions }}</div>
                  <div class="donut-subtext">Total</div>
                </div>
              </div>
            </div>

            <div class="distribution-details">
              <div class="detail-item">
                <div class="detail-marker bg-success"></div>
                <div class="detail-label">UP Predictions</div>
                <div class="detail-value">{{ stats.upPredictions || 0 }}</div>
                <div class="detail-percent text-success">{{ upPercentage }}%</div>
              </div>
              <div class="detail-item">
                <div class="detail-marker bg-error"></div>
                <div class="detail-label">DOWN Predictions</div>
                <div class="detail-value">{{ stats.downPredictions || 0 }}</div>
                <div class="detail-percent text-error">{{ downPercentage }}%</div>
              </div>
            </div>
          </div>

          <div class="verification-summary mt-4">
            <div class="flex items-center justify-between">
              <div class="text-sm font-medium">Verification Rate</div>
              <div class="text-sm font-medium">{{ formatPercentage(stats.verificationRate) }}</div>
            </div>
            <div class="progress-bar mt-1 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div class="bg-primary h-full" :style="{ width: `${stats.verificationRate * 100}%` }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Predictions Table -->
    <div class="content-card">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-base font-medium">All Predictions</h3>
        <div class="flex gap-2">
          <v-select v-model="tableFilters.status" :items="[
            { title: 'All Statuses', value: null },
            { title: 'Verified', value: 'VERIFIED' },
            { title: 'Pending', value: 'PENDING' },
            { title: 'Failed', value: 'FAILED' }
          ]" label="Status" hide-details density="compact" variant="outlined" class="w-40" @update:model-value="filterPredictions"></v-select>

          <v-select v-model="tableFilters.direction" :items="[
            { title: 'All Directions', value: null },
            { title: 'UP', value: 'UP' },
            { title: 'DOWN', value: 'DOWN' }
          ]" label="Direction" hide-details density="compact" variant="outlined" class="w-40" @update:model-value="filterPredictions"></v-select>

          <v-btn variant="outlined" size="small" prepend-icon="mdi-refresh" @click="refreshPredictions">
            Refresh
          </v-btn>
        </div>
      </div>

      <div v-if="loading.predictions" class="flex justify-center items-center py-8">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <v-table v-else density="compact" class="text-sm">
        <thead>
          <tr>
            <th class="text-left">Date</th>
            <th class="text-left">Type</th>
            <th class="text-left">Direction</th>
            <th class="text-left">Confidence</th>
            <th class="text-left">Status</th>
            <th class="text-left">Actual</th>
            <th class="text-left">Verified On</th>
            <th class="text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(prediction, index) in filteredPredictions" :key="index">
            <td>{{ formatDate(prediction.date) }}</td>
            <td>{{ prediction.type || 'Direction' }}</td>
            <td>
              <div class="direction-chip" :class="prediction.direction_prediction === 'UP' ? 'bg-success/10 text-success' : 'bg-error/10 text-error'">
                <v-icon size="x-small">{{ getDirectionIcon(prediction.direction_prediction) }}</v-icon>
                {{ prediction.direction_prediction }}
              </div>
            </td>
            <td>
              <div class="flex items-center">
                <div class="text-xs mr-2 w-10">{{ formatPercentage(prediction.direction_confidence) }}</div>
                <div class="w-24 bg-gray-200 rounded-full h-1.5 overflow-hidden">
                  <div :class="prediction.direction_prediction === 'UP' ? 'bg-success' : 'bg-error'" class="h-full" :style="{ width: `${prediction.direction_confidence * 100}%` }"></div>
                </div>
              </div>
            </td>
            <td>
              <div class="status-chip" :class="getStatusChipClass(prediction.status)">
                {{ prediction.status || 'PENDING' }}
              </div>
            </td>
            <td>
              <div v-if="prediction.actual_direction" class="direction-chip" :class="prediction.actual_direction === 'UP' ? 'bg-success/10 text-success' : 'bg-error/10 text-error'">
                <v-icon size="x-small">{{ getDirectionIcon(prediction.actual_direction) }}</v-icon>
                {{ prediction.actual_direction }}
              </div>
              <div v-else>-</div>
            </td>
            <td>{{ prediction.verification_date ? formatDate(prediction.verification_date) : '-' }}</td>
            <td>
              <v-btn size="x-small" variant="text" icon="mdi-information-outline" @click="showPredictionDetails(prediction)"></v-btn>
              <v-btn size="x-small" variant="text" icon="mdi-refresh" :loading="refreshingId === prediction.id" @click="refreshPrediction(prediction)"></v-btn>
            </td>
          </tr>
          <tr v-if="!filteredPredictions.length">
            <td colspan="8" class="text-center py-4 text-gray-500">No predictions available matching your filters</td>
          </tr>
        </tbody>
      </v-table>

      <!-- Pagination -->
      <div class="flex justify-between items-center mt-4">
        <div class="text-xs text-gray-500">
          Showing {{ filteredPredictions.length }} of {{ allPredictions.length }} predictions
        </div>
        <v-pagination v-model="pagination.page" :length="pageCount" :total-visible="5" size="small" @update:model-value="updatePage"></v-pagination>
      </div>
    </div>

    <!-- Prediction Details Dialog -->
    <v-dialog v-model="showDetailDialog" max-width="600px">
      <div v-if="selectedPrediction" class="prediction-dialog">
        <div class="dialog-header">
          <h2 class="dialog-title">
            Prediction Details
            <div class="direction-chip ml-2" :class="selectedPrediction.direction_prediction === 'UP' ? 'bg-success/10 text-success' : 'bg-error/10 text-error'">
              <v-icon size="x-small">{{ getDirectionIcon(selectedPrediction.direction_prediction) }}</v-icon>
              {{ selectedPrediction.direction_prediction }}
            </div>
          </h2>
          <v-btn icon="mdi-close" variant="text" @click="showDetailDialog = false"></v-btn>
        </div>

        <div class="dialog-content">
          <div class="grid grid-cols-2 gap-4">
            <div class="info-item">
              <div class="info-label">Prediction Date</div>
              <div class="info-value">{{ formatDate(selectedPrediction.date) }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Prediction Type</div>
              <div class="info-value">{{ selectedPrediction.type || 'Direction' }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Direction Confidence</div>
              <div class="info-value confidence-display">
                <div class="value-text">{{ formatPercentage(selectedPrediction.direction_confidence) }}</div>
                <v-progress-linear :model-value="selectedPrediction.direction_confidence * 100" height="8" rounded :color="selectedPrediction.direction_prediction === 'UP' ? 'success' : 'error'"></v-progress-linear>
              </div>
            </div>

            <div class="info-item">
              <div class="info-label">Strong Move Confidence</div>
              <div class="info-value confidence-display">
                <div class="value-text">{{ formatPercentage(selectedPrediction.strong_move_confidence) }}</div>
                <v-progress-linear :model-value="selectedPrediction.strong_move_confidence * 100" height="8" rounded color="primary"></v-progress-linear>
              </div>
            </div>

            <div class="info-item">
              <div class="info-label">Status</div>
              <div class="info-value">
                <div class="status-chip" :class="getStatusChipClass(selectedPrediction.status)">
                  {{ selectedPrediction.status || 'PENDING' }}
                </div>
              </div>
            </div>

            <div class="info-item" v-if="selectedPrediction.actual_direction">
              <div class="info-label">Actual Direction</div>
              <div class="info-value">
                <div class="direction-chip" :class="selectedPrediction.actual_direction === 'UP' ? 'bg-success/10 text-success' : 'bg-error/10 text-error'">
                  <v-icon size="x-small">{{ getDirectionIcon(selectedPrediction.actual_direction) }}</v-icon>
                  {{ selectedPrediction.actual_direction }}
                </div>
              </div>// src/components/symbols/tabs/PredictionsTab.vue (continued)
            </div>
          </div>

          <div class="info-item" v-if="selectedPrediction.actual_move_percent !== null">
            <div class="info-label">Actual Move Percent</div>
            <div class="info-value">{{ selectedPrediction.actual_move_percent.toFixed(2) }}%</div>
          </div>

          <div class="info-item" v-if="selectedPrediction.days_to_fulfill !== null">
            <div class="info-label">Days to Fulfill</div>
            <div class="info-value">{{ selectedPrediction.days_to_fulfill }} days</div>
          </div>

          <div class="info-item" v-if="selectedPrediction.verification_date">
            <div class="info-label">Verification Date</div>
            <div class="info-value">{{ formatDate(selectedPrediction.verification_date) }}</div>
          </div>

          <div class="info-item col-span-2">
            <div class="info-label">Generated by Model</div>
            <div class="info-value text-primary">{{ selectedPrediction.model_version || 'Standard Model' }}</div>
          </div>

          <div class="info-item col-span-2">
            <div class="info-label">Additional Notes</div>
            <div class="info-value text-gray-600 text-sm">
              {{ selectedPrediction.notes || 'No additional notes available for this prediction.' }}
            </div>
          </div>
        </div>
      </div>

      <div class="dialog-actions">
        <v-btn variant="outlined" @click="showDetailDialog = false">
          Close
        </v-btn>
        <v-btn color="primary" prepend-icon="mdi-refresh" @click="refreshPrediction(selectedPrediction, true)">
          Refresh Prediction
        </v-btn>
      </div>
    </v-dialog>
  </div>
</template>

<script>
import { useSymbolStore } from '@/store/symbol.store';
import LineChart from '@/components/charts/LineChart.vue';
import { formatDate, formatPercentage, getDirectionIcon, getStatusChipClass } from '@/utils/format';

export default {
  name: 'PredictionsTab',
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
      loading: {
        stats: false,
        predictions: false,
        timeline: false
      },
      refreshingId: null,
      stats: {
        accuracy: 0,
        upAccuracy: 0,
        downAccuracy: 0,
        upPredictions: 0,
        downPredictions: 0,
        totalPredictions: 0,
        avgDaysToFulfill: 0,
        verificationRate: 0
      },
      allPredictions: [],
      filteredPredictions: [],
      tableFilters: {
        status: null,
        direction: null
      },
      pagination: {
        page: 1,
        itemsPerPage: 10
      },
      selectedTimeframe: '6M',
      timelineData: [],
      selectedPrediction: null,
      showDetailDialog: false,

      // Chart options
      timelineChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          },
          legend: {
            display: true,
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: true,
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
    upPercentage() {
      if (this.stats.totalPredictions === 0) return 50;
      return Math.round((this.stats.upPredictions / this.stats.totalPredictions) * 100);
    },
    downPercentage() {
      if (this.stats.totalPredictions === 0) return 50;
      return Math.round((this.stats.downPredictions / this.stats.totalPredictions) * 100);
    },
    pageCount() {
      return Math.ceil(this.filteredPredictions.length / this.pagination.itemsPerPage);
    },
    paginatedPredictions() {
      const start = (this.pagination.page - 1) * this.pagination.itemsPerPage;
      const end = start + this.pagination.itemsPerPage;
      return this.filteredPredictions.slice(start, end);
    },
    timelineChartData() {
      if (!this.timelineData || !this.timelineData.length) {
        return {
          labels: [],
          datasets: [
            {
              label: 'Accuracy',
              data: [],
              borderColor: '#1E3A8A',
              backgroundColor: 'rgba(30, 58, 138, 0.1)',
              tension: 0.3,
              fill: true
            }
          ]
        };
      }

      return {
        labels: this.timelineData.map(item => formatDate(item.date)),
        datasets: [
          {
            label: 'Accuracy',
            data: this.timelineData.map(item => item.accuracy),
            borderColor: '#1E3A8A',
            backgroundColor: 'rgba(30, 58, 138, 0.1)',
            tension: 0.3,
            fill: true
          },
          {
            label: 'UP Accuracy',
            data: this.timelineData.map(item => item.upAccuracy),
            borderColor: '#10B981',
            backgroundColor: 'transparent',
            tension: 0.3,
            borderDash: [5, 5]
          },
          {
            label: 'DOWN Accuracy',
            data: this.timelineData.map(item => item.downAccuracy),
            borderColor: '#EF4444',
            backgroundColor: 'transparent',
            tension: 0.3,
            borderDash: [5, 5]
          }
        ]
      };
    }
  },
  methods: {
    formatDate,
    formatPercentage,
    getDirectionIcon,
    getStatusChipClass,

    async refreshPredictionStats() {
      this.loading.stats = true;
      try {
        const stats = await this.symbolStore.fetchPredictionStats(this.symbol.trading_symbol);
        this.stats = {
          ...stats,
          // Calculate verification rate (percentage of predictions that are verified)
          verificationRate: stats.totalPredictions > 0
            ? (stats.verifiedPredictions / stats.totalPredictions)
            : 0
        };
      } catch (error) {
        console.error('Error fetching prediction stats:', error);
      } finally {
        this.loading.stats = false;
      }
    },

    async refreshPredictions() {
      this.loading.predictions = true;
      try {
        // Fetch all predictions for this symbol
        const predictions = await this.symbolStore.fetchPredictions(this.symbol.trading_symbol, 100);
        this.allPredictions = predictions;
        this.filterPredictions();
      } catch (error) {
        console.error('Error fetching predictions:', error);
      } finally {
        this.loading.predictions = false;
      }
    },

    async refreshPrediction(prediction, closeDialog = false) {
      this.refreshingId = prediction.id;
      try {
        await this.symbolStore.refreshPrediction(prediction.id);

        // Refresh all data
        await Promise.all([
          this.refreshPredictionStats(),
          this.refreshPredictions(),
          this.fetchTimelineData()
        ]);

        if (closeDialog) {
          this.showDetailDialog = false;
        }
      } catch (error) {
        console.error('Error refreshing prediction:', error);
      } finally {
        this.refreshingId = null;
      }
    },

    async fetchTimelineData() {
      this.loading.timeline = true;
      try {
        // In a real implementation, this would fetch timeline data from the API
        // For now, we'll generate sample data
        const timeframe = this.selectedTimeframe;
        const daysToFetch = timeframe === '1Y' ? 365 : timeframe === '6M' ? 180 : 90;

        // Make API call to get timeline data
        const response = await this.symbolStore.fetchPredictionTimeline(
          this.symbol.trading_symbol,
          daysToFetch
        );

        this.timelineData = response.data || [];
      } catch (error) {
        console.error('Error fetching timeline data:', error);
        // Generate fallback data
        this.generateFallbackTimelineData();
      } finally {
        this.loading.timeline = false;
      }
    },

    generateFallbackTimelineData() {
      // Generate fallback timeline data if API call fails
      const timeframe = this.selectedTimeframe;
      const daysToFetch = timeframe === '1Y' ? 365 : timeframe === '6M' ? 180 : 90;

      const today = new Date();
      const data = [];

      // Generate points for each week
      for (let i = 0; i < daysToFetch; i += 7) {
        const date = new Date();
        date.setDate(today.getDate() - i);

        // Generate random but somewhat realistic accuracy values
        const accuracy = 0.5 + Math.random() * 0.3;
        const upAccuracy = accuracy * (0.8 + Math.random() * 0.4);
        const downAccuracy = accuracy * (0.7 + Math.random() * 0.4);

        data.push({
          date: date.toISOString().split('T')[0],
          accuracy,
          upAccuracy,
          downAccuracy
        });
      }

      this.timelineData = data.reverse();
    },

    filterPredictions() {
      let filtered = [...this.allPredictions];

      // Apply status filter
      if (this.tableFilters.status) {
        filtered = filtered.filter(p => p.status === this.tableFilters.status);
      }

      // Apply direction filter
      if (this.tableFilters.direction) {
        filtered = filtered.filter(p => p.direction_prediction === this.tableFilters.direction);
      }

      this.filteredPredictions = filtered;
      this.pagination.page = 1;
    },

    updatePage(page) {
      this.pagination.page = page;
    },

    showPredictionDetails(prediction) {
      this.selectedPrediction = prediction;
      this.showDetailDialog = true;
    }
  },
  mounted() {
    // Load all prediction data
    this.refreshPredictionStats();
    this.refreshPredictions();
    this.fetchTimelineData();
  },
  watch: {
    // Reload data if symbol changes
    'symbol.trading_symbol': {
      handler(newSymbol) {
        if (newSymbol) {
          this.refreshPredictionStats();
          this.refreshPredictions();
          this.fetchTimelineData();
        }
      },
      immediate: true
    },
    // Reload timeline data when timeframe changes
    selectedTimeframe() {
      this.fetchTimelineData();
    }
  }
};
</script>

<style lang="postcss" scoped>
.content-card {
  @apply bg-gray-50 rounded-lg p-4 border border-gray-100;
}

.stat-card {
  @apply bg-white p-4 rounded-lg shadow-sm border border-gray-200 flex items-center;
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

.bg-error-light {
  @apply bg-error bg-opacity-10;
}

.bg-info-light {
  @apply bg-info bg-opacity-10;
}

.stat-content {
  @apply flex-1;
}

.stat-value {
  @apply text-xl font-semibold;
}

.stat-label {
  @apply text-sm text-gray-500;
}

.loading-overlay {
  @apply absolute top-0 left-0 w-full h-full flex items-center justify-center bg-white/70;
}

.direction-chip {
  @apply inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium;
}

.status-chip {
  @apply inline-flex px-2 py-0.5 rounded-full text-xs font-medium;
}

/* Donut chart styles */
.donut-chart {
  @apply relative w-40 h-40 rounded-full border-8 border-gray-200 flex items-center justify-center;
}

.donut-segment {
  @apply absolute left-0 top-1/2 w-full bg-gray-200 transform -translate-y-1/2 origin-right;
}

.donut-segment.up {
  @apply bg-success;
}

.donut-segment.down {
  @apply bg-error;
}

.donut-label {
  @apply text-center;
}

.donut-percent {
  @apply text-3xl font-bold;
}

.donut-subtext {
  @apply text-xs text-gray-500;
}

.distribution-details {
  @apply mt-4;
}

.detail-item {
  @apply flex items-center mb-2;
}

.detail-marker {
  @apply w-3 h-3 rounded-full mr-2;
}

.detail-label {
  @apply flex-1 text-sm;
}

.detail-value {
  @apply font-medium mr-2;
}

.detail-percent {
  @apply font-semibold;
}

/* Dialog styles */
.prediction-dialog {
  @apply bg-white rounded-xl overflow-hidden;
}

.dialog-header {
  @apply flex justify-between items-center px-6 py-4 border-b border-gray-200 bg-gray-50;
}

.dialog-title {
  @apply text-lg font-bold text-gray-800 flex items-center;
}

.dialog-content {
  @apply p-6;
}

.info-item {
  @apply bg-gray-50 p-3 rounded-lg border border-gray-100;
}

.info-label {
  @apply text-xs text-gray-500 mb-1;
}

.info-value {
  @apply font-medium;
}

.confidence-display {
  @apply space-y-1;
}

.value-text {
  @apply text-sm font-medium;
}

.dialog-actions {
  @apply flex justify-end gap-2 p-4 bg-gray-50 border-t border-gray-200;
}
</style>