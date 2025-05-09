// src/components/symbols/tabs/ComparisonTab.vue
<template>
  <div>
    <!-- Comparison Selection Header -->
    <div class="comparison-header mb-6">
      <div class="flex-1">
        <h3 class="text-base font-medium mb-2">Compare with Similar Symbols</h3>
        <p class="text-sm text-gray-500">Select symbols to compare {{ symbol.trading_symbol }} with</p>
      </div>
      <div class="comparison-actions">
        <v-autocomplete v-model="selectedSymbols" :items="availableSymbols" item-title="trading_symbol" item-value="trading_symbol" label="Add Symbols" variant="outlined" density="compact" multiple chips closable-chips hide-details class="w-64" @update:model-value="updateComparison"></v-autocomplete>

        <v-btn color="primary" size="small" variant="tonal" @click="refreshComparison" :loading="loading.comparison">
          Compare
        </v-btn>
      </div>
    </div>

    <!-- Performance Comparison Chart -->
    <div class="content-card mb-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-base font-medium">Performance Comparison</h3>
        <div class="flex gap-2">
          <v-btn-toggle v-model="comparisonPeriod" density="compact" color="primary">
            <v-btn value="1M" size="small">1M</v-btn>
            <v-btn value="3M" size="small">3M</v-btn>
            <v-btn value="6M" size="small">6M</v-btn>
            <v-btn value="1Y" size="small">1Y</v-btn>
            <v-btn value="YTD" size="small">YTD</v-btn>
          </v-btn-toggle>
        </div>
      </div>

      <div v-if="loading.chart" class="flex justify-center items-center h-96">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <div v-else-if="comparisonData.length" class="h-96 relative">
        <LineChart :chart-data="comparisonChartData" :options="comparisonChartOptions" />
      </div>

      <div v-else class="flex justify-center items-center h-96 bg-gray-50 rounded-lg">
        <div class="text-center text-gray-500">
          <v-icon size="large" color="gray-300">mdi-chart-line</v-icon>
          <p class="mt-2">Select symbols to compare</p>
        </div>
      </div>
    </div>

    <!-- Key Metrics Comparison Table -->
    <div class="content-card">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-base font-medium">Key Metrics Comparison</h3>
        <v-btn size="x-small" icon="mdi-download" variant="text" color="gray" @click="downloadComparisonData"></v-btn>
      </div>

      <div v-if="loading.metrics" class="flex justify-center items-center py-8">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <v-table v-else-if="comparisonMetrics.length" density="compact" class="text-sm">
        <thead>
          <tr>
            <th class="text-left">Metric</th>
            <th v-for="sym in [symbol, ...selectedSymbolDetails]" :key="sym.trading_symbol" class="text-center">
              {{ sym.trading_symbol }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(metric, index) in comparisonMetrics" :key="index">
            <td class="font-medium">{{ metric.name }}</td>
            <td v-for="sym in [symbol, ...selectedSymbolDetails]" :key="`${sym.trading_symbol}-${metric.id}`" class="text-center">
              <template v-if="metric.type === 'price'">
                ₹{{ formatMetricValue(metric.values[sym.trading_symbol], metric.type) }}
              </template>
              <template v-else-if="metric.type === 'change'">
                <span :class="getChangeClass(metric.values[sym.trading_symbol])">
                  {{ formatMetricValue(metric.values[sym.trading_symbol], metric.type) }}
                </span>
              </template>
              <template v-else>
                {{ formatMetricValue(metric.values[sym.trading_symbol], metric.type) }}
              </template>
            </td>
          </tr>
        </tbody>
      </v-table>

      <div v-else class="flex justify-center items-center py-8 text-gray-500">
        <div class="text-center">
          <v-icon size="large" color="gray-300">mdi-table</v-icon>
          <p class="mt-2">No comparison data available</p>
          <v-btn v-if="selectedSymbols.length" color="primary" size="small" variant="tonal" class="mt-2" @click="refreshComparison">
            Load Comparison Data
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useSymbolStore } from '@/store/symbol.store';
import LineChart from '@/components/charts/LineChart.vue';
import { formatDate, formatNumber } from '@/utils/format';

export default {
  name: 'ComparisonTab',
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
        symbols: false,
        comparison: false,
        chart: false,
        metrics: false
      },
      comparisonPeriod: '3M',
      selectedSymbols: [],
      availableSymbols: [],
      selectedSymbolDetails: [],
      comparisonData: [],
      comparisonMetrics: [],
      comparisonChartOptions: {
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
            ticks: {
              callback: function (value) {
                return value + '%';
              }
            }
          }
        }
      }
    };
  },
  computed: {
    comparisonChartData() {
      if (!this.comparisonData.length) {
        return {
          labels: [],
          datasets: []
        };
      }

      // Extract unique dates from all symbols
      const allDates = this.comparisonData.reduce((dates, item) => {
        item.data.forEach(point => {
          if (!dates.includes(point.date)) {
            dates.push(point.date);
          }
        });
        return dates;
      }, []).sort();

      // Format dates for display
      const formattedDates = allDates.map(date => formatDate(date));

      // Create datasets for each symbol
      const colors = [
        { borderColor: '#1E3A8A', backgroundColor: 'rgba(30, 58, 138, 0.1)' }, // Primary
        { borderColor: '#60A5FA', backgroundColor: 'transparent' }, // Info
        { borderColor: '#F59E0B', backgroundColor: 'transparent' }, // Warning
        { borderColor: '#10B981', backgroundColor: 'transparent' }, // Success
        { borderColor: '#6366F1', backgroundColor: 'transparent' }, // Indigo
        { borderColor: '#EC4899', backgroundColor: 'transparent' }  // Pink
      ];

      const datasets = this.comparisonData.map((item, index) => {
        // Create a map of date to value for easy lookup
        const dataMap = {};
        item.data.forEach(point => {
          dataMap[point.date] = point.value;
        });

        // Create dataset with values for all dates (or null if not available)
        const dataValues = allDates.map(date => dataMap[date] !== undefined ? dataMap[date] : null);

        return {
          label: item.symbol,
          data: dataValues,
          borderColor: colors[index % colors.length].borderColor,
          backgroundColor: colors[index % colors.length].backgroundColor,
          tension: 0.3,
          fill: index === 0, // Only fill the primary symbol
          pointRadius: 2
        };
      });

      return {
        labels: formattedDates,
        datasets
      };
    }
  },
  methods: {
    formatDate,
    formatNumber,

    async fetchSymbolOptions() {
      this.loading.symbols = true;
      try {
        // In a real implementation, fetch similar symbols from API
        const response = await this.symbolStore.fetchSimilarSymbols(this.symbol.trading_symbol);

        if (response) {
          this.availableSymbols = response.symbols;
        } else {
          // Fallback to dummy data
          this.availableSymbols = [
            { trading_symbol: 'TATAMOTORS', name: 'Tata Motors Ltd.' },
            { trading_symbol: 'MARUTI', name: 'Maruti Suzuki India Ltd.' },
            { trading_symbol: 'M&M', name: 'Mahindra & Mahindra Ltd.' },
            { trading_symbol: 'HEROMOTOCO', name: 'Hero MotoCorp Ltd.' },
            { trading_symbol: 'BAJAJ-AUTO', name: 'Bajaj Auto Ltd.' },
            { trading_symbol: 'ASHOKLEY', name: 'Ashok Leyland Ltd.' }
          ];
        }
      } catch (error) {
        console.error('Error fetching symbol options:', error);
        // Fallback to dummy data
        this.availableSymbols = [
          { trading_symbol: 'TATAMOTORS', name: 'Tata Motors Ltd.' },
          { trading_symbol: 'MARUTI', name: 'Maruti Suzuki India Ltd.' },
          { trading_symbol: 'M&M', name: 'Mahindra & Mahindra Ltd.' },
          { trading_symbol: 'HEROMOTOCO', name: 'Hero MotoCorp Ltd.' },
          { trading_symbol: 'BAJAJ-AUTO', name: 'Bajaj Auto Ltd.' },
          { trading_symbol: 'ASHOKLEY', name: 'Ashok Leyland Ltd.' }
        ];
      } finally {
        this.loading.symbols = false;
      }
    },

    async updateComparison() {
      this.loading.comparison = true;

      try {
        // Fetch details for selected symbols
        const symbolsToFetch = [...this.selectedSymbols];
        const details = [];

        for (const sym of symbolsToFetch) {
          const detail = await this.symbolStore.getSymbolDetails(sym);
          if (detail) {
            details.push(detail);
          }
        }

        this.selectedSymbolDetails = details;

        // Then fetch comparison data
        this.refreshComparison();
      } catch (error) {
        console.error('Error updating comparison:', error);
      } finally {
        this.loading.comparison = false;
      }
    },

    async refreshComparison() {
      if (!this.selectedSymbols.length) {
        this.comparisonData = [];
        this.comparisonMetrics = [];
        return;
      }

      this.loading.chart = true;
      this.loading.metrics = true;

      try {
        // Fetch chart comparison data
        const symbolsToCompare = [this.symbol.trading_symbol, ...this.selectedSymbols];
        const chartResponse = await this.symbolStore.fetchComparisonChartData(
          symbolsToCompare,
          this.comparisonPeriod
        );

        if (chartResponse) {
          this.comparisonData = chartResponse;
        } else {
          // Generate sample data
          this.generateSampleComparisonData();
        }

        // Fetch metrics comparison data
        const metricsResponse = await this.symbolStore.fetchComparisonMetrics(symbolsToCompare);

        if (metricsResponse) {
          this.comparisonMetrics = metricsResponse;
        } else {
          // Generate sample metrics
          this.generateSampleMetricsData();
        }
      } catch (error) {
        console.error('Error refreshing comparison data:', error);
        // Generate sample data on error
        this.generateSampleComparisonData();
        this.generateSampleMetricsData();
      } finally {
        this.loading.chart = false;
        this.loading.metrics = false;
      }
    },

    generateSampleComparisonData() {
      const period = this.comparisonPeriod;
      const dayCount = period === '1M' ? 30 : period === '3M' ? 90 : period === '6M' ? 180 : 365;

      const symbols = [this.symbol.trading_symbol, ...this.selectedSymbols];
      const comparisonData = [];

      for (let i = 0; i < symbols.length; i++) {
        const sym = symbols[i];
        const baseTrend = i === 0 ? 12 : -5 + Math.random() * 20; // Primary symbol tends to perform better

        // Generate data points
        const data = [];
        let cumulativeReturn = 0;

        for (let day = 0; day < dayCount; day++) {
          const date = new Date();
          date.setDate(date.getDate() - (dayCount - day));

          // Daily return with some randomness but following the trend
          const dailyReturn = (baseTrend / dayCount) + (Math.random() * 0.6 - 0.3);
          cumulativeReturn += dailyReturn;

          data.push({
            date: date.toISOString().split('T')[0],
            value: cumulativeReturn
          });
        }

        comparisonData.push({
          symbol: sym,
          data
        });
      }

      this.comparisonData = comparisonData;
    },

    generateSampleMetricsData() {
      const symbols = [this.symbol.trading_symbol, ...this.selectedSymbols.map(s => s)];

      // Generate random but plausible metric values for each symbol
      const metrics = [
        {
          id: 'last_price',
          name: 'Last Price',
          type: 'price',
          values: {}
        },
        {
          id: 'change_percent',
          name: 'Change %',
          type: 'change',
          values: {}
        },
        {
          id: 'market_cap',
          name: 'Market Cap (Cr)',
          type: 'number',
          values: {}
        },
        {
          id: 'pe_ratio',
          name: 'P/E Ratio',
          type: 'decimal',
          values: {}
        },
        {
          id: 'eps',
          name: 'EPS (₹)',
          type: 'decimal',
          values: {}
        },
        {
          id: 'volume',
          name: 'Volume',
          type: 'number',
          values: {}
        },
        {
          id: 'avg_volume',
          name: 'Avg Volume (10D)',
          type: 'number',
          values: {}
        },
        {
          id: 'dividend_yield',
          name: 'Dividend Yield',
          type: 'percent',
          values: {}
        }
      ];

      // Fill in values for each symbol
      symbols.forEach(sym => {
        // Base values with variations for each symbol
        const basePrice = 1500 + Math.random() * 1000;
        const baseMarketCap = 50000 + Math.random() * 100000;
        const basePE = 15 + Math.random() * 25;

        metrics[0].values[sym] = basePrice;
        metrics[1].values[sym] = (Math.random() * 6) - 3; // -3% to +3%
        metrics[2].values[sym] = baseMarketCap;
        metrics[3].values[sym] = basePE;
        metrics[4].values[sym] = basePrice / basePE;
        metrics[5].values[sym] = Math.round(100000 + Math.random() * 900000);
        metrics[6].values[sym] = Math.round(80000 + Math.random() * 800000);
        metrics[7].values[sym] = Math.random() * 3.5;
      });

      this.comparisonMetrics = metrics;
    },

    formatMetricValue(value, type) {
      if (value === undefined || value === null) return 'N/A';

      switch (type) {
        case 'price':
          return value.toFixed(2);
        case 'decimal':
          return value.toFixed(2);
        case 'number':
          return this.formatNumber(value);
        case 'percent':
          return value.toFixed(2) + '%';
        case 'change':
          return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
        default:
          return value;
      }
    },

    getChangeClass(value) {
      if (value === null || value === undefined) return '';
      return value >= 0 ? 'text-success' : 'text-error';
    },

    downloadComparisonData() {
      if (!this.comparisonMetrics.length) return;

      const symbols = [this.symbol.trading_symbol, ...this.selectedSymbols];

      // Create CSV content
      const headers = ['Metric', ...symbols];
      const rows = this.comparisonMetrics.map(metric => {
        return [
          metric.name,
          ...symbols.map(sym => this.formatMetricValue(metric.values[sym], metric.type))
        ];
      });

      // Combine headers and rows
      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.join(','))
      ].join('\n');

      // Create download link
      const encodedUri = encodeURI(`data:text/csv;charset=utf-8,${csvContent}`);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', `symbol_comparison_${this.symbol.trading_symbol}.csv`);
      document.body.appendChild(link);

      // Trigger download
      link.click();

      // Clean up
      document.body.removeChild(link);
    }
  },
  mounted() {
    this.fetchSymbolOptions();
  },
  watch: {
    'symbol.trading_symbol': {
      handler(newSymbol) {
        if (newSymbol) {
          this.fetchSymbolOptions();
          this.selectedSymbols = [];
          this.comparisonData = [];
          this.comparisonMetrics = [];
        }
      },
      immediate: true
    },
    comparisonPeriod() {
      if (this.selectedSymbols.length > 0) {
        this.refreshComparison();
      }
    }
  }
};
</script>

<style lang="postcss" scoped>
.content-card {
  @apply bg-gray-50 rounded-lg p-4 border border-gray-100;
}

.comparison-header {
  @apply flex flex-col md:flex-row justify-between items-start md:items-center bg-white rounded-lg shadow-sm border border-gray-200 p-4 gap-4;
}

.comparison-actions {
  @apply flex flex-col sm:flex-row gap-2 min-w-64;
}
</style>