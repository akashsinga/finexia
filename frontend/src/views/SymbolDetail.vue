<template>
  <div v-if="!symbolStore.loading && symbolData" class="symbol-details">
    <!-- Header Section with Symbol Info -->
    <div class="overview-card">
      <div class="flex items-center gap-4">
        <div class="symbol-avatar" :class="getSymbolBadgeClass(symbolData.instrument_type)">
          {{ symbolData.trading_symbol.charAt(0) }}
        </div>
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1">
            <h1 class="text-xl font-bold">{{ symbolData.trading_symbol }}</h1>
            <div v-if="symbolData.fo_eligible" class="fo-badge">F&O</div>
            <div class="instrument-badge" :class="getInstrumentClass(symbolData.instrument_type)">
              {{ symbolData.instrument_type }}
            </div>
          </div>
          <div class="text-gray-600 text-sm">{{ symbolData.name }}</div>
        </div>
        <div class="flex items-center gap-2">
          <v-btn size="small" variant="outlined" color="primary" prepend-icon="mdi-star-outline">
            Add to Watchlist
          </v-btn>
        </div>
      </div>

      <!-- Quick Stats Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
        <div class="stat-pill">
          <div class="text-xs text-gray-500">Exchange</div>
          <div class="font-medium">{{ symbolData.exchange }}</div>
        </div>
        <div class="stat-pill">
          <div class="text-xs text-gray-500">Security ID</div>
          <div class="font-medium">{{ symbolData.security_id }}</div>
        </div>
        <div class="stat-pill">
          <div class="text-xs text-gray-500">Segment</div>
          <div class="font-medium">{{ symbolData.segment }}</div>
        </div>
        <div class="stat-pill">
          <div class="text-xs text-gray-500">Status</div>
          <div>
            <span class="status-badge" :class="symbolData.active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
              {{ symbolData.active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <div class="tab-container">
      <v-tabs v-model="activeTab" show-arrows color="primary" class="mb-4">
        <v-tab value="overview">Overview</v-tab>
        <v-tab value="historical">Historical Data</v-tab>
        <v-tab value="predictions">Predictions</v-tab>
        <v-tab value="models">Model Performance</v-tab>
        <v-tab value="technical">Technical Analysis</v-tab>
        <v-tab value="comparison">Comparison</v-tab>
      </v-tabs>

      <v-window v-model="activeTab" class="tab-content">
        <v-window-item value="overview">
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Price Chart Card -->
            <div class="content-card lg:col-span-2">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-base font-medium">Price History</h3>
                <div class="flex rounded-lg bg-gray-100 p-0.5">
                  <button v-for="period in chartPeriods" :key="period.value" class="period-btn" :class="currentPeriod === period.value ? 'period-active' : ''" @click="currentPeriod = period.value; fetchHistoricalData()">
                    {{ period.label }}
                  </button>
                </div>
              </div>
              <div class="h-72">
                <LineChart :chart-data="priceChartData" :options="priceChartOptions" />
              </div>
            </div>

            <!-- Prediction Summary Card -->
            <div class="content-card">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-base font-medium">Prediction Summary</h3>
                <v-btn icon="mdi-refresh" variant="text" size="small" color="gray" @click="fetchPredictionSummary"></v-btn>
              </div>

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
                  <div class="h-4 w-4 rounded-full bg-success/10 flex items-center justify-center text-success mr-2">
                    <v-icon size="x-small">mdi-arrow-up-bold</v-icon>
                  </div>
                  <span class="mr-1">UP ({{ predictionStats.upPredictions || 0 }})</span>
                  <span class="text-success ml-auto">{{ formatPercentage(predictionStats.upAccuracy) }} accurate</span>
                </div>
                <div class="flex items-center text-xs">
                  <div class="h-4 w-4 rounded-full bg-error/10 flex items-center justify-center text-error mr-2">
                    <v-icon size="x-small">mdi-arrow-down-bold</v-icon>
                  </div>
                  <span class="mr-1">DOWN ({{ predictionStats.downPredictions || 0 }})</span>
                  <span class="text-error ml-auto">{{ formatPercentage(predictionStats.downAccuracy) }} accurate</span>
                </div>
              </div>

              <v-btn block variant="tonal" color="primary" class="mt-auto" @click="activeTab = 'predictions'">
                View All Predictions
              </v-btn>
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
              <v-btn icon="mdi-refresh" variant="text" size="small" color="gray"></v-btn>
            </div>

            <v-table density="compact" class="text-xs">
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
                    <div class="direction-chip" :class="prediction.direction === 'UP' ? 'bg-success/10 text-success' : 'bg-error/10 text-error'">
                      <v-icon size="x-small">{{ getDirectionIcon(prediction.direction) }}</v-icon>
                      {{ prediction.direction }}
                    </div>
                  </td>
                  <td>
                    <div class="flex items-center">
                      <div class="text-xs mr-2 w-10">{{ formatPercentage(prediction.confidence) }}</div>
                      <div class="w-24 bg-gray-200 rounded-full h-1.5 overflow-hidden">
                        <div :class="prediction.direction === 'UP' ? 'bg-success' : 'bg-error'" class="h-full" :style="{ width: `${prediction.confidence * 100}%` }"></div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="status-chip" :class="getStatusChipClass(prediction.status)">
                      {{ prediction.status }}
                    </div>
                  </td>
                  <td>
                    <div v-if="prediction.actual" class="direction-chip" :class="prediction.actual === 'UP' ? 'bg-success/10 text-success' : 'bg-error/10 text-error'">
                      <v-icon size="x-small">{{ getDirectionIcon(prediction.actual) }}</v-icon>
                      {{ prediction.actual }}
                    </div>
                    <div v-else>-</div>
                  </td>
                  <td>{{ prediction.fulfilledOn ? formatDate(prediction.fulfilledOn) : '-' }}</td>
                </tr>
                <tr v-if="!latestPredictions.length">
                  <td colspan="7" class="text-center py-4 text-gray-500">No predictions available</td>
                </tr>
              </tbody>
            </v-table>
          </div>
        </v-window-item>

        <!-- Other tabs would be implemented similarly -->
        <v-window-item v-for="tab in ['historical', 'predictions', 'models', 'technical', 'comparison']" :key="tab" :value="tab">
          <div class="flex justify-center items-center py-12 text-gray-500">
            <div class="text-center">
              <v-icon size="large" color="gray-300">mdi-file-document-outline</v-icon>
              <p class="mt-2">{{ tab.charAt(0).toUpperCase() + tab.slice(1) }} content will be available soon</p>
            </div>
          </div>
        </v-window-item>
      </v-window>
    </div>
  </div>

  <!-- Loading State -->
  <div v-else class="symbol-details">
    <div class="overview-card animate-pulse">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-gray-200 rounded-lg"></div>
        <div class="flex-1">
          <div class="h-6 bg-gray-200 rounded w-24 mb-2"></div>
          <div class="h-4 bg-gray-200 rounded w-48"></div>
        </div>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
        <div v-for="i in 4" :key="i" class="h-12 bg-gray-200 rounded"></div>
      </div>
    </div>

    <div class="tab-container mt-6">
      <div class="h-10 bg-gray-200 rounded mb-4"></div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="h-72 bg-gray-200 rounded lg:col-span-2"></div>
        <div class="h-72 bg-gray-200 rounded"></div>
      </div>
    </div>
  </div>
</template>

<script>
import LineChart from '@/components/charts/LineChart.vue';
import { useSymbolStore } from '@/store/symbol.store';
import { usePredictionStore } from '@/store/prediction.store';
import { useHistoricalStore } from '@/store/historical.store';
import {
  formatDate,
  formatNumber,
  formatPercentage,
  getSymbolBadgeClass,
  getInstrumentClass,
  getStatusChipClass,
  getDirectionIcon,
  getDateRangeForPeriod
} from '@/utils';

export default {
  name: 'SymbolDetails',
  components: {
    LineChart
  },
  data() {
    return {
      symbolStore: useSymbolStore(),
      predictionStore: usePredictionStore(),
      historicalStore: useHistoricalStore(),
      symbolData: null,
      activeTab: 'overview',
      currentPeriod: '1M',
      chartPeriods: [
        { label: '1W', value: '1W' },
        { label: '1M', value: '1M' },
        { label: '3M', value: '3M' },
        { label: '6M', value: '6M' },
        { label: '1Y', value: '1Y' },
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
      latestPredictions: [
        {
          date: '2025-04-01',
          type: 'Strong Move',
          direction: 'UP',
          confidence: 0.86,
          status: 'VERIFIED',
          actual: 'UP',
          fulfilledOn: '2025-04-03'
        },
        {
          date: '2025-03-27',
          type: 'Strong Move',
          direction: 'DOWN',
          confidence: 0.72,
          status: 'VERIFIED',
          actual: 'DOWN',
          fulfilledOn: '2025-03-29'
        },
        {
          date: '2025-03-22',
          type: 'Direction',
          direction: 'UP',
          confidence: 0.65,
          status: 'FAILED',
          actual: 'DOWN',
          fulfilledOn: '2025-03-24'
        },
        {
          date: '2025-03-15',
          type: 'Strong Move',
          direction: 'UP',
          confidence: 0.78,
          status: 'VERIFIED',
          actual: 'UP',
          fulfilledOn: '2025-03-17'
        }
      ]
    };
  },
  computed: {
    // Get price chart data from historical store
    priceChartData() {
      return this.historicalStore.chartData;
    },

    // Get latest EOD data from historical store
    latestEOD() {
      return this.historicalStore.latestEOD;
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
    // Import utility functions to use in template
    formatDate,
    formatNumber,
    formatPercentage,
    getSymbolBadgeClass,
    getInstrumentClass,
    getStatusChipClass,
    getDirectionIcon,

    fetchSymbolData: async function () {
      try {
        await this.symbolStore.fetchSymbolByTradingSymbol(this.$route.params.symbol);
        this.symbolData = this.symbolStore.selectedSymbol;
      } catch (error) {
        console.error('Error fetching symbol data:', error);
      }
    },

    fetchHistoricalData: async function () {
      try {
        const { from_date, to_date } = getDateRangeForPeriod(this.currentPeriod);
        await this.historicalStore.fetchHistoricalEODData(this.$route.params.symbol, { from_date, to_date });
      } catch (error) {
        console.error('Error fetching historical data:', error);
      }
    },

    fetchPredictionSummary: async function () {
      try {
        const predictionSummary = await this.predictionStore.fetchPredictionStatsBySymbol(this.$route.params.symbol);
        this.predictionStats = predictionSummary;
      } catch (error) {
        console.error('Error fetching prediction data:', error);
      }
    }
  },
  mounted() {
    this.fetchSymbolData();
    this.fetchHistoricalData();
    this.fetchPredictionSummary();
  }
};
</script>

<style lang="postcss" scoped>
.symbol-details {
  @apply w-full flex flex-col gap-6;
}

.overview-card {
  @apply bg-white rounded-xl p-5 shadow-sm border border-gray-200;
}

.symbol-avatar {
  @apply w-12 h-12 rounded-xl flex items-center justify-center text-white text-xl font-bold;
}

.fo-badge {
  @apply px-2 py-0.5 text-xs font-medium bg-primary/10 text-primary rounded;
}

.instrument-badge {
  @apply px-2 py-0.5 text-xs font-medium text-white rounded;
}

.stat-pill {
  @apply bg-gray-50 p-3 rounded-lg border border-gray-100;
}

.status-badge {
  @apply px-2 py-0.5 text-xs font-medium rounded;
}

.tab-container {
  @apply bg-white rounded-xl p-5 shadow-sm border border-gray-200;
}

/* Reduce tab font size */
:deep(.v-tab) {
  @apply text-xs font-medium;
}

.content-card {
  @apply bg-gray-50 rounded-lg p-4 border border-gray-100;
}

.period-btn {
  @apply px-3 py-1 text-xs rounded font-medium text-gray-600 transition-colors;
}

.period-active {
  @apply bg-primary text-white;
}

.eod-item {
  @apply p-3;
}

.direction-chip {
  @apply inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium;
}

.status-chip {
  @apply inline-flex px-2 py-0.5 rounded-full text-xs font-medium;
}
</style>