<template>
  <div>
    <!-- Technical Analysis Summary -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="summary-card">
        <div class="summary-header">
          <h3 class="summary-title">Short Term</h3>
          <div :class="getSignalClass(technicalSummary.shortTerm.signal)">
            {{ technicalSummary.shortTerm.signal }}
          </div>
        </div>
        <div class="summary-strength">
          <div class="strength-label">Strength:</div>
          <div class="strength-value">{{ technicalSummary.shortTerm.strength }}</div>
          <div class="strength-bar">
            <div class="strength-indicator" :class="getSignalBarClass(technicalSummary.shortTerm.signal)" :style="{ width: `${technicalSummary.shortTerm.strengthPercentage}%` }">
            </div>
          </div>
        </div>
        <div class="summary-details">
          <div class="summary-row">
            <div class="summary-label">Buy Signals:</div>
            <div class="summary-value">{{ technicalSummary.shortTerm.buySignals }}</div>
          </div>
          <div class="summary-row">
            <div class="summary-label">Sell Signals:</div>
            <div class="summary-value">{{ technicalSummary.shortTerm.sellSignals }}</div>
          </div>
          <div class="summary-row">
            <div class="summary-label">Neutral Signals:</div>
            <div class="summary-value">{{ technicalSummary.shortTerm.neutralSignals }}</div>
          </div>
        </div>
      </div>

      <div class="summary-card">
        <div class="summary-header">
          <h3 class="summary-title">Medium Term</h3>
          <div :class="getSignalClass(technicalSummary.mediumTerm.signal)">
            {{ technicalSummary.mediumTerm.signal }}
          </div>
        </div>
        <div class="summary-strength">
          <div class="strength-label">Strength:</div>
          <div class="strength-value">{{ technicalSummary.mediumTerm.strength }}</div>
          <div class="strength-bar">
            <div class="strength-indicator" :class="getSignalBarClass(technicalSummary.mediumTerm.signal)" :style="{ width: `${technicalSummary.mediumTerm.strengthPercentage}%` }">
            </div>
          </div>
        </div>
        <div class="summary-details">
          <div class="summary-row">
            <div class="summary-label">Buy Signals:</div>
            <div class="summary-value">{{ technicalSummary.mediumTerm.buySignals }}</div>
          </div>
          <div class="summary-row">
            <div class="summary-label">Sell Signals:</div>
            <div class="summary-value">{{ technicalSummary.mediumTerm.sellSignals }}</div>
          </div>
          <div class="summary-row">
            <div class="summary-label">Neutral Signals:</div>
            <div class="summary-value">{{ technicalSummary.mediumTerm.neutralSignals }}</div>
          </div>
        </div>
      </div>

      <div class="summary-card">
        <div class="summary-header">
          <h3 class="summary-title">Long Term</h3>
          <div :class="getSignalClass(technicalSummary.longTerm.signal)">
            {{ technicalSummary.longTerm.signal }}
          </div>
        </div>
        <div class="summary-strength">
          <div class="strength-label">Strength:</div>
          <div class="strength-value">{{ technicalSummary.longTerm.strength }}</div>
          <div class="strength-bar">
            <div class="strength-indicator" :class="getSignalBarClass(technicalSummary.longTerm.signal)" :style="{ width: `${technicalSummary.longTerm.strengthPercentage}%` }">
            </div>
          </div>
        </div>
        <div class="summary-details">
          <div class="summary-row">
            <div class="summary-label">Buy Signals:</div>
            <div class="summary-value">{{ technicalSummary.longTerm.buySignals }}</div>
          </div>
          <div class="summary-row">
            <div class="summary-label">Sell Signals:</div>
            <div class="summary-value">{{ technicalSummary.longTerm.sellSignals }}</div>
          </div>
          <div class="summary-row">
            <div class="summary-label">Neutral Signals:</div>
            <div class="summary-value">{{ technicalSummary.longTerm.neutralSignals }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Technical Indicators -->
    <div class="content-card mb-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-base font-medium">Technical Indicators</h3>
        <v-btn icon="mdi-refresh" variant="text" size="small" color="gray" @click="fetchTechnicalData"></v-btn>
      </div>

      <div v-if="loading" class="flex justify-center items-center py-8">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <v-table v-else density="compact" class="text-sm">
        <thead>
          <tr>
            <th class="text-left">Indicator</th>
            <th class="text-left">Value</th>
            <th class="text-left">Previous</th>
            <th class="text-left">Signal</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(indicator, index) in technicalIndicators" :key="index">
            <td>{{ indicator.name }}</td>
            <td>{{ formatIndicatorValue(indicator.value, indicator.format) }}</td>
            <td>{{ formatIndicatorValue(indicator.previous, indicator.format) }}</td>
            <td>
              <div class="signal-badge" :class="getSignalClass(indicator.signal)">
                {{ indicator.signal }}
              </div>
            </td>
          </tr>
        </tbody>
      </v-table>
    </div>

    <!-- Support & Resistance Chart + Levels -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Chart -->
      <div class="content-card lg:col-span-2">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Support & Resistance Levels</h3>
          <div class="flex gap-2">
            <v-btn-toggle v-model="selectedChartView" density="compact" color="primary">
              <v-btn value="candlestick" size="small">Candlestick</v-btn>
              <v-btn value="line" size="small">Line</v-btn>
            </v-btn-toggle>
          </div>
        </div>
        <div class="h-96 flex items-center justify-center bg-gray-100 rounded-lg">
          <!-- Placeholder for chart - in a real implementation, this would be a chart component -->
          <div class="text-center text-gray-500">
            <v-icon size="large" color="gray-300">mdi-chart-line</v-icon>
            <p class="mt-2">Advanced chart visualization coming soon</p>
          </div>
        </div>
      </div>

      <!-- Levels -->
      <div class="content-card">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-base font-medium">Price Levels</h3>
          <v-btn icon="mdi-refresh" variant="text" size="small" color="gray" @click="fetchSupportResistanceLevels"></v-btn>
        </div>

        <div v-if="loading" class="flex justify-center items-center py-8">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </div>

        <div v-else class="levels-container">
          <!-- Resistance Levels -->
          <div class="level-section">
            <h4 class="level-section-title">Resistance Levels</h4>
            <div class="level-grid">
              <div v-for="(level, index) in resistanceLevels" :key="`resistance-${index}`" class="level-item">
                <div class="level-value">₹{{ level.value.toFixed(2) }}</div>
                <div class="level-strength" :class="`strength-${level.strength}`">
                  {{ level.strength }}
                  <v-icon v-for="i in level.strengthValue" :key="i" size="x-small">mdi-circle-small</v-icon>
                </div>
              </div>
            </div>
          </div>

          <!-- Current Price -->
          <div class="current-price">
            <div class="current-price-label">Current Price</div>
            <div class="current-price-value">₹{{ currentPrice.toFixed(2) }}</div>
          </div>

          <!-- Support Levels -->
          <div class="level-section">
            <h4 class="level-section-title">Support Levels</h4>
            <div class="level-grid">
              <div v-for="(level, index) in supportLevels" :key="`support-${index}`" class="level-item">
                <div class="level-value">₹{{ level.value.toFixed(2) }}</div>
                <div class="level-strength" :class="`strength-${level.strength}`">
                  {{ level.strength }}
                  <v-icon v-for="i in level.strengthValue" :key="i" size="x-small">mdi-circle-small</v-icon>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { useSymbolStore } from '@/store/symbol.store';
import { formatDate, formatNumber } from '@/utils/format';

export default {
  name: 'TechnicalAnalysisTab',
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
      selectedChartView: 'candlestick',
      currentPrice: 0,
      technicalSummary: {
        shortTerm: {
          signal: 'BUY',
          strength: 'Strong',
          strengthPercentage: 80,
          buySignals: 8,
          sellSignals: 2,
          neutralSignals: 2
        },
        mediumTerm: {
          signal: 'NEUTRAL',
          strength: 'Moderate',
          strengthPercentage: 50,
          buySignals: 5,
          sellSignals: 4,
          neutralSignals: 3
        },
        longTerm: {
          signal: 'SELL',
          strength: 'Weak',
          strengthPercentage: 30,
          buySignals: 3,
          sellSignals: 6,
          neutralSignals: 3
        }
      },
      technicalIndicators: [
        { name: 'RSI (14)', value: 62.45, previous: 58.32, signal: 'NEUTRAL', format: 'decimal' },
        { name: 'MACD', value: 2.85, previous: 1.42, signal: 'BUY', format: 'decimal' },
        { name: 'Stochastic %K (14, 3, 3)', value: 82.36, previous: 76.18, signal: 'SELL', format: 'percent' },
        { name: 'ADX (14)', value: 24.56, previous: 22.84, signal: 'NEUTRAL', format: 'decimal' },
        { name: 'CCI (14)', value: 125.67, previous: 105.32, signal: 'BUY', format: 'decimal' },
        { name: 'ATR (14)', value: 3.25, previous: 3.18, signal: 'NEUTRAL', format: 'decimal' },
        { name: 'Williams %R (14)', value: -20.45, previous: -25.67, signal: 'BUY', format: 'decimal' },
        { name: 'Bollinger Bands Width', value: 5.42, previous: 4.95, signal: 'NEUTRAL', format: 'decimal' },
        { name: 'Ichimoku Cloud', value: 'Above', previous: 'Above', signal: 'BUY', format: 'text' },
        { name: 'OBV', value: 356482, previous: 342765, signal: 'BUY', format: 'number' }
      ],
      supportLevels: [
        { value: 2150.50, strength: 'Strong', strengthValue: 3 },
        { value: 2120.75, strength: 'Moderate', strengthValue: 2 },
        { value: 2080.25, strength: 'Weak', strengthValue: 1 }
      ],
      resistanceLevels: [
        { value: 2230.25, strength: 'Strong', strengthValue: 3 },
        { value: 2275.50, strength: 'Moderate', strengthValue: 2 },
        { value: 2310.00, strength: 'Weak', strengthValue: 1 }
      ]
    };
  },
  methods: {
    formatDate,
    formatNumber,

    getSignalClass(signal) {
      const classMap = {
        'BUY': 'signal-buy',
        'SELL': 'signal-sell',
        'NEUTRAL': 'signal-neutral',
        'STRONG BUY': 'signal-strong-buy',
        'STRONG SELL': 'signal-strong-sell'
      };
      return classMap[signal] || 'signal-neutral';
    },

    getSignalBarClass(signal) {
      if (signal === 'BUY' || signal === 'STRONG BUY') return 'bar-buy';
      if (signal === 'SELL' || signal === 'STRONG SELL') return 'bar-sell';
      return 'bar-neutral';
    },

    formatIndicatorValue(value, format) {
      if (format === 'percent') return `${value}%`;
      if (format === 'decimal') return value.toFixed(2);
      if (format === 'number') return this.formatNumber(value);
      return value; // text or other formats
    },

    async fetchTechnicalData() {
      this.loading = true;
      try {
        // In a real implementation, fetch from API
        const response = await this.symbolStore.fetchTechnicalAnalysis(this.symbol.trading_symbol);

        if (response) {
          this.technicalSummary = response.summary;
          this.technicalIndicators = response.indicators;
          this.currentPrice = response.currentPrice;
        }
      } catch (error) {
        console.error('Error fetching technical analysis data:', error);
        // Use sample data
        this.currentPrice = 2195.75;
      } finally {
        this.loading = false;
      }
    },

    async fetchSupportResistanceLevels() {
      this.loading = true;
      try {
        // In a real implementation, fetch from API
        const response = await this.symbolStore.fetchSupportResistance(this.symbol.trading_symbol);

        if (response) {
          this.supportLevels = response.support;
          this.resistanceLevels = response.resistance;
        }
      } catch (error) {
        console.error('Error fetching support/resistance levels:', error);
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.fetchTechnicalData();
    this.fetchSupportResistanceLevels();
  },
  watch: {
    'symbol.trading_symbol': {
      handler(newSymbol) {
        if (newSymbol) {
          this.fetchTechnicalData();
          this.fetchSupportResistanceLevels();
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

.summary-card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-4;
}

.summary-header {
  @apply flex justify-between items-center mb-3;
}

.summary-title {
  @apply text-sm font-medium text-gray-600;
}

.signal-buy,
.signal-strong-buy {
  @apply text-xs font-bold text-success bg-success/10 px-2 py-0.5 rounded;
}

.signal-sell,
.signal-strong-sell {
  @apply text-xs font-bold text-error bg-error/10 px-2 py-0.5 rounded;
}

.signal-neutral {
  @apply text-xs font-bold text-gray-500 bg-gray-100 px-2 py-0.5 rounded;
}

.signal-strong-buy {
  @apply bg-success/20;
}

.signal-strong-sell {
  @apply bg-error/20;
}

.summary-strength {
  @apply mb-3;
}

.strength-label {
  @apply text-xs text-gray-500 mb-1;
}

.strength-value {
  @apply text-sm font-medium mb-1;
}

.strength-bar {
  @apply h-2 bg-gray-200 rounded-full overflow-hidden;
}

.strength-indicator {
  @apply h-full;
}

.bar-buy {
  @apply bg-success;
}

.bar-sell {
  @apply bg-error;
}

.bar-neutral {
  @apply bg-gray-400;
}

.summary-details {
  @apply space-y-1;
}

.summary-row {
  @apply flex justify-between text-xs;
}

.summary-label {
  @apply text-gray-500;
}

.summary-value {
  @apply font-medium;
}

.signal-badge {
  @apply text-xs font-medium px-2 py-0.5 rounded-full inline-flex items-center justify-center;
}

.levels-container {
  @apply space-y-4;
}

.level-section {
  @apply border border-gray-200 rounded-lg p-3;
}

.level-section-title {
  @apply text-xs font-medium text-gray-600 mb-2;
}

.level-grid {
  @apply grid grid-cols-3 gap-2;
}

.level-item {
  @apply bg-white p-2 rounded border border-gray-100 text-center;
}

.level-value {
  @apply font-medium text-sm;
}

.level-strength {
  @apply text-xs flex items-center justify-center gap-0.5;
}

.strength-Strong {
  @apply text-success;
}

.strength-Moderate {
  @apply text-warning;
}

.strength-Weak {
  @apply text-gray-500;
}

.current-price {
  @apply bg-primary/10 p-3 rounded-lg text-center border border-primary/20;
}

.current-price-label {
  @apply text-xs text-gray-600 mb-1;
}

.current-price-value {
  @apply text-xl font-bold text-primary;
}
</style>