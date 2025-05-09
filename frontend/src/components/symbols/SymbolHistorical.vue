// src/components/symbols/tabs/HistoricalDataTab.vue (continued)
<template>
  <div>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Historical Chart Section -->
      <div class="content-card lg:col-span-2">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Historical Price Data</h3>
          <div class="flex rounded-lg bg-gray-100 p-0.5">
            <button v-for="period in chartPeriods" :key="period.value" class="period-btn" :class="currentPeriod === period.value ? 'period-active' : ''" @click="handlePeriodChange(period.value)">
              {{ period.label }}
            </button>
          </div>
        </div>
        <div class="h-96 relative">
          <LineChart :chart-data="priceChartData" :options="priceChartOptions" />
          <div v-if="loading" class="loading-overlay">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
          </div>
        </div>
      </div>

      <!-- Historical Data Stats -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Price Statistics</h3>
          <v-btn icon="mdi-refresh" variant="text" size="small" color="gray" @click="handlePeriodChange(currentPeriod)"></v-btn>
        </div>

        <div v-if="loading" class="flex justify-center items-center h-64">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>
        <template v-else-if="priceStats">
          <div class="grid grid-cols-2 gap-4">
            <div class="stat-item">
              <div class="stat-label">Highest Price</div>
              <div class="stat-value text-success">₹{{ priceStats.highest.toFixed(2) }}</div>
              <div class="stat-date">{{ formatDate(priceStats.highestDate) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Lowest Price</div>
              <div class="stat-value text-error">₹{{ priceStats.lowest.toFixed(2) }}</div>
              <div class="stat-date">{{ formatDate(priceStats.lowestDate) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Average Price</div>
              <div class="stat-value">₹{{ priceStats.average.toFixed(2) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Price Change</div>
              <div class="stat-value" :class="priceStats.change >= 0 ? 'text-success' : 'text-error'">
                {{ priceStats.change >= 0 ? '+' : '' }}{{ priceStats.change.toFixed(2) }}%
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Avg. Volume</div>
              <div class="stat-value">{{ formatNumber(priceStats.averageVolume) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Volatility</div>
              <div class="stat-value">{{ priceStats.volatility.toFixed(2) }}%</div>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Historical Data Table -->
    <div class="content-card mt-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-base font-medium">Historical EOD Data</h3>
        <div class="flex gap-2">
          <v-select v-model="dataLimit" :items="[10, 20, 50, 100]" label="Rows" hide-details density="compact" variant="outlined" class="w-20"></v-select>
          <v-btn variant="outlined" size="small" prepend-icon="mdi-download" @click="downloadHistoricalData">
            Export
          </v-btn>
        </div>
      </div>

      <div v-if="loading" class="flex justify-center items-center py-8">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <v-table v-else density="compact" class="text-xs">
        <thead>
          <tr>
            <th class="text-left">Date</th>
            <th class="text-right">Open</th>
            <th class="text-right">High</th>
            <th class="text-right">Low</th>
            <th class="text-right">Close</th>
            <th class="text-right">Volume</th>
            <th class="text-right">Change</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in limitedEodData" :key="index">
            <td>{{ formatDate(item.date) }}</td>
            <td class="text-right">₹{{ item.open.toFixed(2) }}</td>
            <td class="text-right">₹{{ item.high.toFixed(2) }}</td>
            <td class="text-right">₹{{ item.low.toFixed(2) }}</td>
            <td class="text-right">₹{{ item.close.toFixed(2) }}</td>
            <td class="text-right">{{ formatNumber(item.volume) }}</td>
            <td class="text-right" :class="item.change >= 0 ? 'text-success' : 'text-error'">
              {{ item.change >= 0 ? '+' : '' }}{{ item.change.toFixed(2) }}%
            </td>
          </tr>
          <tr v-if="!historicalData.length">
            <td colspan="7" class="text-center py-4 text-gray-500">No historical data available</td>
          </tr>
        </tbody>
      </v-table>
    </div>
  </div>
</template>

<script>
import { useSymbolStore } from '@/store/symbol.store';
import LineChart from '@/components/charts/LineChart.vue';
import { formatDate, formatNumber } from '@/utils/format';

export default {
  name: 'HistoricalDataTab',
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
      loading: false,
      currentPeriod: '3M',
      dataLimit: 20,
      chartPeriods: [
        { label: '1W', value: '1W' },
        { label: '1M', value: '1M' },
        { label: '3M', value: '3M' },
        { label: '6M', value: '6M' },
        { label: '1Y', value: '1Y' },
        { label: 'ALL', value: 'ALL' }
      ],
      priceChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            mode: 'index',
            intersect: false
          },
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: false
          }
        }
      },
      historicalData: [],
      priceStats: null
    };
  },
  computed: {
    priceChartData() {
      if (!this.historicalData.length) {
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
      const dates = [...this.historicalData]
        .map((item) => formatDate(item.date, 'MMM D'))
        .reverse();

      const prices = [...this.historicalData]
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
    limitedEodData() {
      return this.historicalData.slice(0, this.dataLimit);
    }
  },
  methods: {
    formatDate,
    formatNumber,

    async handlePeriodChange(period) {
      this.loading = true;
      try {
        const data = await this.symbolStore.fetchHistoricalData(this.symbol.trading_symbol, period);
        this.historicalData = data;

        if (data && data.length > 0) {
          this.calculatePriceStats();
        }
      } catch (error) {
        console.error('Error fetching historical data:', error);
      } finally {
        this.loading = false;
      }
    },

    calculatePriceStats() {
      if (!this.historicalData || this.historicalData.length === 0) return;

      // Get the first and last prices for price change calculation
      const firstPrice = this.historicalData[this.historicalData.length - 1].close;
      const lastPrice = this.historicalData[0].close;

      // Find highest and lowest prices
      let highest = -Infinity;
      let lowest = Infinity;
      let highestDate = null;
      let lowestDate = null;
      let totalPrice = 0;
      let totalVolume = 0;

      // Calculate dailyReturns for volatility calculation
      const dailyReturns = [];

      this.historicalData.forEach((item, index) => {
        if (item.high > highest) {
          highest = item.high;
          highestDate = item.date;
        }

        if (item.low < lowest) {
          lowest = item.low;
          lowestDate = item.date;
        }

        totalPrice += item.close;
        totalVolume += item.volume;

        // Calculate daily return if not the first day
        if (index < this.historicalData.length - 1) {
          const previousClose = this.historicalData[index + 1].close;
          const dailyReturn = (item.close - previousClose) / previousClose;
          dailyReturns.push(dailyReturn);
        }
      });

      // Calculate average price and volume
      const average = totalPrice / this.historicalData.length;
      const averageVolume = totalVolume / this.historicalData.length;

      // Calculate price change percentage
      const change = ((lastPrice - firstPrice) / firstPrice) * 100;

      // Calculate volatility (standard deviation of returns, annualized)
      const meanReturn = dailyReturns.reduce((a, b) => a + b, 0) / dailyReturns.length;
      const squaredDifferences = dailyReturns.map(return_ => Math.pow(return_ - meanReturn, 2));
      const variance = squaredDifferences.reduce((a, b) => a + b, 0) / squaredDifferences.length;
      const stdDev = Math.sqrt(variance);
      const volatility = stdDev * Math.sqrt(252) * 100; // Annualized volatility

      // Update priceStats
      this.priceStats = {
        highest,
        highestDate,
        lowest,
        lowestDate,
        average,
        averageVolume,
        change,
        volatility
      };
    },

    downloadHistoricalData() {
      if (!this.historicalData || this.historicalData.length === 0) return;

      // Create CSV content
      const headers = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Change'];
      const rows = this.historicalData.map(item => [
        formatDate(item.date),
        item.open.toFixed(2),
        item.high.toFixed(2),
        item.low.toFixed(2),
        item.close.toFixed(2),
        item.volume,
        `${item.change >= 0 ? '+' : ''}${item.change.toFixed(2)}%`
      ]);

      // Combine headers and rows
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');

      // Create download link
      const encodedUri = encodeURI(`data:text/csv;charset=utf-8,${csvContent}`);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', `${this.symbol.trading_symbol}_historical_data.csv`);
      document.body.appendChild(link);

      // Trigger download
      link.click();

      // Clean up
      document.body.removeChild(link);
    }
  },
  mounted() {
    this.handlePeriodChange(this.currentPeriod);
  },
  watch: {
    'symbol.trading_symbol': {
      handler(newSymbol) {
        if (newSymbol) {
          this.handlePeriodChange(this.currentPeriod);
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
  @apply absolute top-0 left-0 w-full h-full flex items-center justify-center bg-white/70;
}

.stat-item {
  @apply bg-white p-3 rounded-lg border border-gray-100;
}

.stat-label {
  @apply text-xs text-gray-500 mb-1;
}

.stat-value {
  @apply text-base font-semibold;
}

.stat-date {
  @apply text-xs text-gray-500 mt-1;
}
</style>