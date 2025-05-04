<template>
  <div v-if="!symbolStore.loading && symbolData" class="symbol-details-page">
    <!-- Header Section with Symbol Info -->
    <div class="overview-section">
      <div class="overview-header">
        <div class="symbol-info">
          <div class="symbol-badge" :class="getSymbolBadgeClass(symbolData.instrument_type)">
            {{ symbolData.trading_symbol.charAt(0) }}
          </div>
          <div class="symbol-meta">
            <div class="symbol-title-row">
              <h1 class="symbol-title">{{ symbolData.trading_symbol }}</h1>
              <div v-if="symbolData.fo_eligible" class="fo-badge">F&O</div>
              <div class="instrument-badge" :class="getInstrumentClass(symbolData.instrument_type)">
                {{ symbolData.instrument_type }}
              </div>
            </div>
            <div class="company-name">{{ symbolData.name }}</div>
          </div>
        </div>
        <div class="symbol-actions">
          <button class="action-btn action-btn-outline">
            <v-icon size="small" class="mr-1">mdi-star-outline</v-icon>
            Add to Watchlist
          </button>
        </div>
      </div>

      <!-- Quick Stats Cards -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-label">Exchange</div>
          <div class="stat-value">{{ symbolData.exchange }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Security ID</div>
          <div class="stat-value">{{ symbolData.security_id }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Segment</div>
          <div class="stat-value">{{ symbolData.segment }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Status</div>
          <div class="stat-value">
            <span class="status-pill" :class="symbolData.active ? 'status-active' : 'status-inactive'">
              {{ symbolData.active ? 'Active' : 'Inactive' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <div class="content-tabs">
      <v-tabs v-model="activeTab" show-arrows>
        <v-tab value="overview">Overview</v-tab>
        <v-tab value="historical">Historical Data</v-tab>
        <v-tab value="predictions">Predictions</v-tab>
        <v-tab value="models">Model Performance</v-tab>
        <v-tab value="technical">Technical Analysis</v-tab>
        <v-tab value="comparison">Comparison</v-tab>
        <v-tab value="news">News & Events</v-tab>
      </v-tabs>
      <v-window v-model="activeTab" class="tab-content">
        <v-window-item value="overview">
          <div class="overview-tab">
            <div class="overview-grid">
              <!-- Price Chart Card -->
              <div class="overview-card chart-card">
                <div class="card-header">
                  <h3 class="card-title">Price History</h3>
                  <div class="time-range-selector">
                    <button v-for="period in chartPeriods" :key="period.value" :class="['period-btn', currentPeriod === period.value ? 'period-active' : '']" @click="currentPeriod = period.value; fetchHistoricalData()">
                      {{ period.label }}
                    </button>
                  </div>
                </div>
                <div class="chart-container">
                  <LineChart :chart-data="priceChartData" :options="priceChartOptions" />
                </div>
              </div>

              <!-- Prediction Summary Card -->
              <!-- <div class="overview-card prediction-summary-card">
                <div class="card-header">
                  <h3 class="card-title">Prediction Summary</h3>
                  <button class="refresh-btn">
                    <v-icon size="small">mdi-refresh</v-icon>
                  </button>
                </div>
                <div class="prediction-metrics">
                  <div class="metric-row">
                    <div class="metric-item">
                      <div class="metric-value">{{ (predictionStats.accuracy * 100).toFixed(1) }}%</div>
                      <div class="metric-label">Accuracy</div>
                    </div>
                    <div class="metric-item">
                      <div class="metric-value">{{ predictionStats.totalPredictions }}</div>
                      <div class="metric-label">Total Predictions</div>
                    </div>
                  </div>

                  <div class="direction-summary">
                    <div class="direction-header">
                      <div class="direction-title">Direction Predictions</div>
                      <div class="direction-split">
                        <span class="up-percent">{{ upPercentage }}%</span> /
                        <span class="down-percent">{{ downPercentage }}%</span>
                      </div>
                    </div>
                    <div class="direction-bar">
                      <div class="direction-segment up" :style="{ width: `${upPercentage}%` }"></div>
                      <div class="direction-segment down" :style="{ width: `${downPercentage}%` }"></div>
                    </div>
                    <div class="direction-labels">
                      <div class="direction-label">
                        <div class="direction-indicator up">
                          <v-icon size="x-small">mdi-arrow-up-bold</v-icon>
                        </div>
                        <span>UP ({{ predictionStats.upPredictions }})</span>
                        <span class="accuracy">{{ (predictionStats.upAccuracy * 100).toFixed(1) }}% accurate</span>
                      </div>
                      <div class="direction-label">
                        <div class="direction-indicator down">
                          <v-icon size="x-small">mdi-arrow-down-bold</v-icon>
                        </div>
                        <span>DOWN ({{ predictionStats.downPredictions }})</span>
                        <span class="accuracy">{{ (predictionStats.downAccuracy * 100).toFixed(1) }}% accurate</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="prediction-footer">
                  <button class="view-all-btn" @click="activeTab = 'predictions'">
                    View All Predictions
                    <v-icon size="small">mdi-arrow-right</v-icon>
                  </button>
                </div>
              </div> -->

              <!-- Latest EOD Data Card -->
              <!-- <div class="overview-card eod-card">
                <div class="card-header">
                  <h3 class="card-title">Latest EOD Data</h3>
                  <div class="eod-date">{{ formatDate(latestEOD.date) }}</div>
                </div>
                <div class="eod-data">
                  <div class="eod-item">
                    <div class="eod-label">Open</div>
                    <div class="eod-value">₹{{ latestEOD.open.toFixed(2) }}</div>
                  </div>
                  <div class="eod-item">
                    <div class="eod-label">High</div>
                    <div class="eod-value">₹{{ latestEOD.high.toFixed(2) }}</div>
                  </div>
                  <div class="eod-item">
                    <div class="eod-label">Low</div>
                    <div class="eod-value">₹{{ latestEOD.low.toFixed(2) }}</div>
                  </div>
                  <div class="eod-item">
                    <div class="eod-label">Close</div>
                    <div class="eod-value">₹{{ latestEOD.close.toFixed(2) }}</div>
                  </div>
                  <div class="eod-item">
                    <div class="eod-label">Volume</div>
                    <div class="eod-value">{{ formatNumber(latestEOD.volume) }}</div>
                  </div>
                  <div class="eod-item">
                    <div class="eod-label">Change</div>
                    <div class="eod-value" :class="latestEOD.change >= 0 ? 'text-success' : 'text-error'">
                      {{ latestEOD.change >= 0 ? '+' : '' }}{{ latestEOD.change.toFixed(2) }}%
                    </div>
                  </div>
                </div>
              </div> -->

              <!-- Technical Indicators Summary -->
              <!-- <div class="overview-card technical-card">
                <div class="card-header">
                  <h3 class="card-title">Technical Indicators</h3>
                </div>
                <div class="indicator-grid">
                  <div class="indicator-item">
                    <div class="indicator-title">RSI (14)</div>
                    <div class="indicator-value">{{ indicators.rsi.toFixed(2) }}</div>
                    <div class="indicator-signal" :class="getSignalClass(indicators.rsiSignal)">
                      {{ indicators.rsiSignal }}
                    </div>
                  </div>
                  <div class="indicator-item">
                    <div class="indicator-title">MACD</div>
                    <div class="indicator-value">{{ indicators.macd.toFixed(2) }}</div>
                    <div class="indicator-signal" :class="getSignalClass(indicators.macdSignal)">
                      {{ indicators.macdSignal }}
                    </div>
                  </div>
                  <div class="indicator-item">
                    <div class="indicator-title">Bollinger Bands</div>
                    <div class="indicator-value">{{ indicators.bollingerWidth.toFixed(2) }}</div>
                    <div class="indicator-signal" :class="getSignalClass(indicators.bollingerSignal)">
                      {{ indicators.bollingerSignal }}
                    </div>
                  </div>
                  <div class="indicator-item">
                    <div class="indicator-title">Stochastic</div>
                    <div class="indicator-value">{{ indicators.stochastic.toFixed(2) }}</div>
                    <div class="indicator-signal" :class="getSignalClass(indicators.stochasticSignal)">
                      {{ indicators.stochasticSignal }}
                    </div>
                  </div>
                </div>
                <div class="technical-summary">
                  <div class="summary-label">Overall Signal:</div>
                  <div class="summary-value" :class="getSignalClass(indicators.overallSignal)">
                    {{ indicators.overallSignal }}
                  </div>
                </div>
              </div> -->
            </div>

            <!-- Latest Predictions Table -->
            <!-- <div class="predictions-table-card">
              <div class="card-header">
                <h3 class="card-title">Latest Predictions</h3>
                <button class="refresh-btn">
                  <v-icon size="small">mdi-refresh</v-icon>
                </button>
              </div>

              <v-table density="compact">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Direction</th>
                    <th>Confidence</th>
                    <th>Status</th>
                    <th>Actual</th>
                    <th>Fulfilled On</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(prediction, index) in latestPredictions" :key="index">
                    <td>{{ formatDate(prediction.date) }}</td>
                    <td>{{ prediction.type }}</td>
                    <td>
                      <div class="direction-badge" :class="prediction.direction === 'UP' ? 'up' : 'down'">
                        <v-icon size="x-small">{{ prediction.direction === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold' }}</v-icon>
                        {{ prediction.direction }}
                      </div>
                    </td>
                    <td>
                      <div class="confidence-bar-container">
                        <div class="confidence-value">{{ (prediction.confidence * 100).toFixed(0) }}%</div>
                        <div class="confidence-bar">
                          <div class="confidence-fill" :style="{ width: `${prediction.confidence * 100}%` }" :class="prediction.direction === 'UP' ? 'bg-success' : 'bg-error'"></div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="status-chip" :class="getStatusClass(prediction.status)">
                        {{ prediction.status }}
                      </div>
                    </td>
                    <td>
                      <div v-if="prediction.actual" class="direction-badge" :class="prediction.actual === 'UP' ? 'up' : 'down'">
                        <v-icon size="x-small">{{ prediction.actual === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold' }}</v-icon>
                        {{ prediction.actual }}
                      </div>
                      <div v-else>-</div>
                    </td>
                    <td>{{ prediction.fulfilledOn ? formatDate(prediction.fulfilledOn) : '-' }}</td>
                  </tr>
                </tbody>
              </v-table>
            </div> -->
          </div>
        </v-window-item>
      </v-window>
    </div>
  </div>
</template>

<script>
import LineChart from '@/components/charts/LineChart.vue';
import CandleStickChart from '@/components/charts/CandleStickChart.vue'
import { useSymbolStore } from '@/store/symbol.store';
import { usePredictionStore } from '@/store/prediction.store';
import { useHistoricalStore } from '@/store/historical.store';

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
        { label: 'ALL', value: 'ALL' }
      ],
      priceChartData: {
        labels: [],
        datasets: [{
          label: 'Price',
          data: [],
          borderColor: '#1E3A8A',
          backgroundColor: 'rgba(30, 58, 138, 0.1)',
          tension: 0.3,
          fill: true
        }]
      },
      priceChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        }
      },
      predictionStats: {},
      latestEOD: {},
      indicators: {},
      latestPredictions: []
    };
  },
  computed: {
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
    fetchSymbolData: async function () {
      try {
        await this.symbolStore.fetchSymbolByTradingSymbol(this.$route.params.symbol);
        this.symbolData = this.symbolStore.selectedSymbol;
      } catch (error) {
        console.error('Error fetching symbol data:', error);
      }
    },
    fetchHistoricalData: async function () {
      const { from_date, to_date } = this.getDateRange()
      let dates, data
      try {
        await this.historicalStore.fetchHistoricalEODData(this.$route.params.symbol, { from_date, to_date });
        dates = this.historicalStore.eod_data.map((eod_data) => eod_data.date)
        data = this.historicalStore.eod_data.map((eod_data) => eod_data.close)
      } catch (error) {
        console.error('Error fetching symbol data:', error);
      }
      this.priceChartData = {
        labels: dates,
        datasets: [{
          label: 'Price',
          data,
          borderColor: '#1E3A8A',
          backgroundColor: 'rgba(30, 58, 138, 0.1)',
          tension: 0.3,
          fill: true
        }]
      };
    },
    async fetchPredictions() {
      // In a real implementation, this would fetch prediction data for the symbol
    },
    getDateRange: function () {
      const to_date = new Date()
      let from_date = new Date()

      switch (this.currentPeriod) {
        case '1D':
          from_date.setDate(to_date.getDate() - 1)
          break
        case '1W':
          from_date.setDate(to_date.getDate() - 7)
          break
        case '1M':
          from_date.setMonth(to_date.getMonth() - 1)
          break
        case '3M':
          from_date.setMonth(to_date.getMonth() - 3)
          break
        case '6M':
          from_date.setMonth(to_date.getMonth() - 6)
          break
        case '1Y':
          from_date.setFullYear(to_date.getFullYear() - 1)
          break
        case 'ALL':
          from_date = new Date('2000-01-01') // or the earliest supported date
          break
      }

      // Format as YYYY-MM-DD
      const format = (date) => date.toISOString().split('T')[0]

      return { from_date: format(from_date), to_date: format(to_date) }
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    },
    formatNumber(num) {
      return new Intl.NumberFormat('en-IN').format(num);
    },
    getSymbolBadgeClass(type) {
      const classMap = { 'EQUITY': 'badge-eq', 'FNO': 'badge-fut', 'OPT': 'badge-opt', 'ETF': 'badge-etf', 'INDEX': 'badge-index' };
      return classMap[type] || '';
    },
    getInstrumentClass(type) {
      const classMap = { 'EQUITY': 'instrument-eq', 'FNO': 'instrument-fut', 'OPT': 'instrument-opt', 'ETF': 'instrument-etf', 'INDEX': 'instrument-index' };
      return classMap[type] || '';
    },
    getSignalClass(signal) {
      if (signal === 'BUY') return 'signal-buy';
      if (signal === 'SELL') return 'signal-sell';
      return 'signal-neutral';
    },
    getStatusClass(status) {
      if (status === 'VERIFIED') return 'status-verified';
      if (status === 'FAILED') return 'status-failed';
      if (status === 'PENDING') return 'status-pending';
      return '';
    }
  },
  mounted() {
    this.fetchSymbolData();
    this.fetchHistoricalData()
  }
};
</script>

<style lang="postcss" scoped>
.symbol-details-page {
  @apply w-full flex flex-col gap-6;
}

/* Overview Section */
.overview-section {
  @apply bg-white rounded-xl border border-gray-200 p-6;
}

.overview-header {
  @apply flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6;
}

.symbol-info {
  @apply flex items-center gap-4;
}

.symbol-badge {
  @apply flex items-center justify-center w-14 h-14 rounded-xl text-2xl font-bold text-white;
}

.badge-eq {
  @apply bg-blue-600;
}

.badge-fut {
  @apply bg-purple-600;
}

.badge-opt {
  @apply bg-orange-500;
}

.badge-etf {
  @apply bg-green-600;
}

.badge-index {
  @apply bg-cyan-600;
}

.symbol-meta {
  @apply flex flex-col;
}

.symbol-title-row {
  @apply flex items-center gap-2;
}

.symbol-title {
  @apply text-2xl font-bold text-gray-800;
}

.fo-badge {
  @apply px-2 py-0.5 text-xs font-medium bg-primary bg-opacity-10 text-primary rounded;
}

.instrument-badge {
  @apply px-2 py-0.5 text-xs font-medium text-white rounded;
}

.instrument-eq {
  @apply bg-blue-600;
}

.instrument-fut {
  @apply bg-purple-600;
}

.instrument-opt {
  @apply bg-orange-500;
}

.instrument-etf {
  @apply bg-green-600;
}

.instrument-index {
  @apply bg-cyan-600;
}

.company-name {
  @apply text-sm text-gray-600 mt-1;
}

.symbol-actions {
  @apply flex flex-wrap gap-2;
}

.action-btn {
  @apply px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-1 transition-colors;
}

.action-btn-outline {
  @apply border border-gray-300 text-gray-700 hover:bg-gray-50;
}

.action-btn-primary {
  @apply bg-primary text-white hover:bg-primary-dark;
}

/* Stats Cards */
.stats-cards {
  @apply grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4;
}

.stat-card {
  @apply bg-gray-50 p-3 rounded-lg;
}

.stat-label {
  @apply text-xs text-gray-500 mb-1;
}

.stat-value {
  @apply font-semibold;
}

.status-pill {
  @apply px-2 py-0.5 text-xs font-medium text-white rounded;
}

.status-active {
  @apply bg-green-500;
}

.status-inactive {
  @apply bg-red-500;
}

/* Content Tabs */
.content-tabs {
  @apply bg-white rounded-xl border border-gray-200 overflow-hidden;

  .v-tab.v-btn {
    @apply text-sm capitalize font-normal;
  }
}

.tab-content {
  @apply p-6;
}

.tab-placeholder {
  @apply flex flex-col items-center justify-center py-12;
}

/* Overview Tab */
.overview-tab {
  @apply flex flex-col gap-6;
}

.overview-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6;
}

.overview-card {
  @apply bg-gray-50 rounded-lg border border-gray-200 overflow-hidden;
}

.card-header {
  @apply flex justify-between items-center p-4 border-b border-gray-200;
}

.card-title {
  @apply font-medium;
}

.time-range-selector {
  @apply flex gap-1;
}

.period-btn {
  @apply px-2 py-1 text-xs rounded font-medium text-gray-600 hover:bg-gray-200 transition-colors;
}

.period-active {
  @apply bg-primary text-white;
}

.refresh-btn {
  @apply p-1 rounded text-gray-500 hover:bg-gray-200 transition-colors;
}

.chart-container {
  @apply h-[280px];
}

/* Prediction Summary Card */
.prediction-summary-card {
  @apply flex flex-col;
}

.prediction-metrics {
  @apply p-4;
}

.metric-row {
  @apply flex justify-between mb-4;
}

.metric-item {
  @apply flex flex-col items-center;
}

.metric-value {
  @apply text-xl font-bold text-primary;
}

.metric-label {
  @apply text-xs text-gray-500;
}

.direction-summary {
  @apply mt-4;
}

.direction-header {
  @apply flex justify-between items-center mb-2;
}

.direction-title {
  @apply text-sm font-medium;
}

.direction-split {
  @apply text-xs;
}

.up-percent {
  @apply text-success font-medium;
}

.down-percent {
  @apply text-error font-medium;
}

.direction-bar {
  @apply h-2 w-full flex rounded-full overflow-hidden mb-2;
}

.direction-segment {
  @apply h-full transition-all duration-500;
}

.direction-segment.up {
  @apply bg-success;
}

.direction-segment.down {
  @apply bg-error;
}

.direction-labels {
  @apply flex justify-between text-xs;
}

.direction-label {
  @apply flex items-center gap-1;
}

.direction-indicator {
  @apply w-4 h-4 rounded-full flex items-center justify-center;
}

.direction-indicator.up {
  @apply bg-success bg-opacity-10 text-success;
}

.direction-indicator.down {
  @apply bg-error bg-opacity-10 text-error;
}

.accuracy {
  @apply ml-1 text-gray-500;
}

.prediction-footer {
  @apply mt-auto p-4;
}
</style>