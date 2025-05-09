// src/components/symbols/tabs/OverviewTab.vue
<template>
  <div>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Price Chart Card -->
      <div class="content-card lg:col-span-2">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Price History</h3>
          <div class="flex rounded-lg bg-gray-100 p-0.5">
            <button v-for="period in chartPeriods" :key="period.value" class="period-btn" :class="currentPeriod === period.value ? 'period-active' : ''" @click="handlePeriodChange(period.value)">
              {{ period.label }}
            </button>
          </div>
        </div>
        <div class="h-72 relative">
          <LineChart :chart-data="priceChartData" :options="priceChartOptions" />
          <div v-if="loading.historical" class="loading-overlay">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </div>
        </div>
      </div>

      <!-- Prediction Summary Card -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Prediction Summary</h3>
          <v-btn icon="mdi-refresh" variant="text" size="small" color="gray" @click="refreshPredictionStats"></v-btn>
        </div>

        <div v-if="loading.predictionStats" class="flex justify-center items-center h-64">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <template v-else>
          <div class="flex justify-between mb-6">
            <div class="text-center">
              <div class="text-2xl font-bold text-primary">{{ formatPercentage(predictionStats.accuracy) }}</div>
              <div class="text-xs text-gray-500">Accuracy</div>
            </div>
            <div class="text-center">
              <div class="text-2xl font-bold text-primary">{{ predictionStats.totalPredictions || 0 }}</div>
              <div class="text-xs text-gray-500">Total Predictions</div>
            </div>
          </div>

          <div class="mb-4">
            <div class="flex justify-between items-center mb-1">
              <div class="text-sm font-medium">Direction Split</div>
              <div class="text-xs font-medium">
                <span class="text-success">{{ upPercentage }}%</span> /
                <span class="text-error">{{ downPercentage }}%</span>
              </div>
            </div>
            <div class="h-2 w-full flex rounded-full overflow-hidden">
              <div class="bg-success h-full transition-all duration-500" :style="{ width: `${upPercentage}%` }"></div>
              <div class="bg-error h-full transition-all duration-500" :style="{ width: `${downPercentage}%` }"></div>
            </div>
          </div>

          <div class="space-y-2 mb-6">
            <div class="flex items-center text-xs">
              <div class="h-4 w-4 rounded-full bg-success bg-opacity-10 flex items-center justify-center text-success mr-2">
                <v-icon size="x-small">mdi-arrow-up-bold</v-icon>
              </div>
              <span class="mr-1">UP ({{ predictionStats.upPredictions || 0 }})</span>
              <span class="text-success ml-auto">{{ formatPercentage(predictionStats.upAccuracy) }} accurate</span>
            </div>
            <div class="flex items-center text-xs">
              <div class="h-4 w-4 rounded-full bg-error bg-opacity-10 flex items-center justify-center text-error mr-2">
                <v-icon size="x-small">mdi-arrow-down-bold</v-icon>
              </div>
              <span class="mr-1">DOWN ({{ predictionStats.downPredictions || 0 }})</span>
              <span class="text-error ml-auto">{{ formatPercentage(predictionStats.downAccuracy) }} accurate</span>
            </div>
          </div>

          <v-btn block variant="tonal" color="primary" class="mt-auto" @click="$emit('change-tab', 'predictions')">
            View All Predictions
          </v-btn>
        </template>
      </div>
    </div>

    <!-- EOD & Technical Analysis Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      <!-- Latest EOD Data Card -->
      <div v-if="latestEOD" class="content-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Latest EOD Data</h3>
          <div class="text-xs text-gray-500">{{ formatDate(latestEOD.date) }}</div>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div class="eod-item">
            <div class="text-xs text-gray-500">Open</div>
            <div class="font-medium">₹{{ latestEOD.open.toFixed(2) }}</div>
          </div>
          <div class="eod-item">
            <div class="text-xs text-gray-500">High</div>
            <div class="font-medium">₹{{ latestEOD.high.toFixed(2) }}</div>
          </div>
          <div class="eod-item">
            <div class="text-xs text-gray-500">Low</div>
            <div class="font-medium">₹{{ latestEOD.low.toFixed(2) }}</div>
          </div>
          <div class="eod-item">
            <div class="text-xs text-gray-500">Close</div>
            <div class="font-medium">₹{{ latestEOD.close.toFixed(2) }}</div>
          </div>
          <div class="eod-item">
            <div class="text-xs text-gray-500">Volume</div>
            <div class="font-medium">{{ formatNumber(latestEOD.volume) }}</div>
          </div>
          <div class="eod-item">
            <div class="text-xs text-gray-500">Change</div>
            <div class="font-medium" :class="latestEOD.change >= 0 ? 'text-success' : 'text-error'">
              {{ latestEOD.change >= 0 ? '+' : '' }}{{ latestEOD.change.toFixed(2) }}%
            </div>
          </div>
        </div>
      </div>

      <!-- Technical Indicators Summary (Placeholder) -->
      <div class="content-card flex items-center justify-center">
        <div class="text-center text-gray-500">
          <v-icon size="large" color="gray-300">mdi-chart-bell-curve</v-icon>
          <p class="mt-2">Technical analysis will be available soon</p>
        </div>
      </div>
    </div>

    <!-- Latest Predictions Table -->
    <div class="content-card mt-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-base font-medium">Latest Predictions</h3>
        <v-btn icon="mdi-refresh" variant="text" size="small" color="gray" @click="refreshPredictions"></v-btn>
      </div>

      <div v-if="loading.predictions" class="flex justify-center items-center py-8">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <v-table v-else density="compact" class="text-xs">
        <thead>
          <tr>
            <th class="text-left">Date</th>
            <th class="text-left">Type</th>
            <th class="text-left">Direction</th>
            <th class="text-left">Confidence</th>
            <th class="text-left">Status</th>
            <th class="text-left">Actual</th>
            <th class="text-left">Fulfilled On</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(prediction, index) in latestPredictions" :key="index">
            <td>{{ formatDate(prediction.date) }}</td>
            <td>{{ prediction.type }}</td>
            <td>
              <div class="direction-chip" :class="prediction.direction_prediction === 'UP' ? 'direction-up' : 'direction-down'">
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
                {{ prediction.status }}
              </div>
            </td>
            <td>
              <div v-if="prediction.actual_direction" class="direction-chip" :class="prediction.actual_direction === 'UP' ? 'direction-up' : 'direction-down'">
                <v-icon size="x-small">{{ getDirectionIcon(prediction.actual_direction) }}</v-icon>
                {{ prediction.actual_direction }}
              </div>
              <div v-else>-</div>
            </td>
            <td>{{ prediction.verification_date ? formatDate(prediction.verification_date) : '-' }}</td>
          </tr>
          <tr v-if="!latestPredictions.length">
            <td colspan="7" class="text-center py-4 text-gray-500">No predictions available</td>
          </tr>
        </tbody>
      </v-table>
    </div>
  </div>
</template>

<script>
import { useSymbolStore } from '@/store/symbol.store';
import LineChart from '@/components/charts/LineChart.vue';
import { formatDate, formatNumber, formatPercentage, getDirectionIcon, getStatusChipClass } from '@/utils/format';

export default {
  name: 'OverviewTab',
  components: {
    LineChart
  },
  props: {
    symbol: {
      type: Object,
      required: true
    }
  },
  emits: ['change-tab'],
  data() {
    return {
      symbolStore: useSymbolStore(),
      loading: {
        historical: false,
        predictionStats: false,
        predictions: false
      },
      currentPeriod: '1M',
      chartPeriods: [
        { label: '1W', value: '1W' },
        { label: '1M', value: '1M' },
        { label: '3M', value: '3M' },
        { label: '6M', value: '6M' },
        { label: '1Y', value: '1Y' }
      ],
      priceChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        }
      },
      predictionStats: {
        accuracy: 0,
        totalPredictions: 0,
        upPredictions: 0,
        downPredictions: 0,
        upAccuracy: 0,
        downAccuracy: 0
      },
      latestPredictions: []
    };
  },
  computed: {
    priceChartData() {
      if (!this.symbolStore.historicalData || !this.symbolStore.historicalData.length) {
        return {
          labels: [],
          datasets: [{
            label: 'Price',
            data: [],
            borderColor: '#1E3A8A',
            backgroundColor: 'rgba(30, 58, 138, 0.1)',
            tension: 0.3,
            fill: true
          }]
        };
      }

      // Extract and format dates and prices from the EOD data
      const dates = [...this.symbolStore.historicalData]
        .map((item) => formatDate(item.date, 'MMM D'))
        .reverse();

      const prices = [...this.symbolStore.historicalData]
        .map((item) => item.close)
        .reverse();

      return {
        labels: dates,
        datasets: [{
          label: 'Price',
          data: prices,
          borderColor: '#1E3A8A',
          backgroundColor: 'rgba(30, 58, 138, 0.1)',
          tension: 0.3,
          fill: true
        }]
      };
    },
    latestEOD() {
      if (!this.symbolStore.historicalData || !this.symbolStore.historicalData.length) {
        return null;
      }

      const latest = this.symbolStore.historicalData[0]; // Assuming sorted with newest first
      return latest;
    },
    upPercentage() {
      if (this.predictionStats.totalPredictions === 0) return 50;
      return Math.round((this.predictionStats.upPredictions / this.predictionStats.totalPredictions) * 100);
    },
    downPercentage() {
      if (this.predictionStats.totalPredictions === 0) return 50;
      return Math.round((this.predictionStats.downPredictions / this.predictionStats.totalPredictions) * 100);
    }
  },
  methods: {
    // Format utility functions
    formatDate,
    formatNumber,
    formatPercentage,
    getDirectionIcon,
    getStatusChipClass,

    // API calls
    async handlePeriodChange(period) {
      this.currentPeriod = period;
      this.loading.historical = true;
      try {
        await this.symbolStore.fetchHistoricalData(this.symbol.trading_symbol, period);
      } catch (error) {
        console.error('Error fetching historical data:', error);
      } finally {
        this.loading.historical = false;
      }
    },

    async refreshPredictionStats() {
      this.loading.predictionStats = true;
      try {
        const stats = await this.symbolStore.fetchPredictionStats(this.symbol.trading_symbol);
        this.predictionStats = stats;
      } catch (error) {
        console.error('Error refreshing prediction stats:', error);
      } finally {
        this.loading.predictionStats = false;
      }
    },

    async refreshPredictions() {
      this.loading.predictions = true;
      try {
        const predictions = await this.symbolStore.fetchPredictions(this.symbol.trading_symbol);
        this.latestPredictions = predictions;
      } catch (error) {
        console.error('Error refreshing predictions:', error);
      } finally {
        this.loading.predictions = false;
      }
    }
  },
  mounted() {
    // Load all data for the overview tab
    this.handlePeriodChange(this.currentPeriod);
    this.refreshPredictionStats();
    this.refreshPredictions();
  },
  watch: {
    // Reload data if symbol changes
    'symbol.trading_symbol': {
      handler(newSymbol) {
        if (newSymbol) {
          this.handlePeriodChange(this.currentPeriod);
          this.refreshPredictionStats();
          this.refreshPredictions();
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

.period-btn {
  @apply px-3 py-1 text-xs rounded font-medium text-gray-600 transition-colors;
}

.period-active {
  @apply bg-primary text-white;
}

.loading-overlay {
  @apply absolute top-0 left-0 w-full h-full flex items-center justify-center bg-white bg-opacity-70;
}

.eod-item {
  @apply p-3;
}

.direction-chip {
  @apply inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium;
}

.direction-up {
  @apply bg-success bg-opacity-10 text-success;
}

.direction-down {
  @apply bg-error bg-opacity-10 text-error;
}

.status-chip {
  @apply inline-flex px-2 py-0.5 rounded-full text-xs font-medium;
}
</style>