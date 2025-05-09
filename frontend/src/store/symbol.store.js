// src/store/symbol.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useSymbolStore = defineStore('symbol', {
  state: () => ({
    symbols: [],
    selectedSymbol: null,
    symbolDetails: {},
    filteredSymbols: [],
    pagination: {
      currentPage: 1,
      pageSize: 24,
      totalItems: 0
    },
    filters: {
      searchQuery: '',
      filterType: 'all', // 'all' or 'fo'
    },
    loading: false,
    loadingDetails: false,

    // New state properties
    historicalData: [],
    predictionStats: null,
    symbolPredictions: [],
    loadingHistorical: false,
    loadingPredictionStats: false,
    loadingPredictions: false,
    error: null
  }),

  getters: {
    /**
     * Find a symbol by trading symbol
     * @param {string} tradingSymbol - Trading symbol to find
     * @returns {Object|null} Symbol object or null if not found
     */
    getSymbolByTradingSymbol: (state) => (tradingSymbol) => {
      return state.symbols.find(s => s.trading_symbol === tradingSymbol) || null;
    },

    /**
     * Get all F&O eligible symbols
     * @returns {Array} Array of F&O eligible symbols
     */
    getFOEligibleSymbols: (state) => {
      return state.symbols.filter(s => s.fo_eligible);
    },

    /**
     * Get total symbol count
     * @returns {number} Number of symbols in the store
     */
    getSymbolCount: (state) => {
      return state.symbols.length;
    },

    /**
     * Get paginated symbols based on current filters
     */
    paginatedSymbols: (state) => {
      const startIndex = (state.pagination.currentPage - 1) * state.pagination.pageSize;
      const endIndex = startIndex + state.pagination.pageSize;
      return state.filteredSymbols.slice(startIndex, endIndex);
    },

    /**
     * Get total pages based on filtered items and page size
     */
    totalPages: (state) => {
      return Math.ceil(state.filteredSymbols.length / state.pagination.pageSize);
    }
  },

  actions: {
    /**
     * Apply filters to symbols (search and type filter)
     */
    applyFilters() {
      let result = [...this.symbols];

      // Apply search filter
      if (this.filters.searchQuery.trim()) {
        const query = this.filters.searchQuery.toLowerCase();
        result = result.filter(
          symbol =>
            symbol.trading_symbol.toLowerCase().includes(query) ||
            symbol.name.toLowerCase().includes(query)
        );
      }

      // Apply F&O filter
      if (this.filters.filterType === 'fo') {
        result = result.filter(symbol => symbol.fo_eligible);
      }

      // Update filtered symbols
      this.filteredSymbols = result;
      this.pagination.totalItems = result.length;

      // Reset to first page when filters change
      this.pagination.currentPage = 1;
    },

    /**
     * Update the current page
     */
    setPage(page) {
      this.pagination.currentPage = page;
    },

    /**
     * Update the search query and reapply filters
     */
    setSearchQuery(query) {
      this.filters.searchQuery = query;
      this.applyFilters();
    },

    /**
     * Update the filter type and reapply filters
     */
    setFilterType(type) {
      this.filters.filterType = type;
      this.applyFilters();
    },

    /**
     * Reset all filters to default values
     */
    resetFilters() {
      this.filters.searchQuery = '';
      this.filters.filterType = 'all';
      this.pagination.currentPage = 1;
      this.applyFilters();
    },

    /**
     * Fetch all symbols with optional filtering
     * @param {Object} params - Query parameters for filtering
     * @returns {Array} Array of symbol objects
     */
    async fetchSymbols(params = { active_only: true }) {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get('/symbols', { params });
        this.symbols = response.data;

        // Apply filters to update filteredSymbols
        this.applyFilters();

        return this.symbols;
      } catch (error) {
        console.error('Error fetching symbols:', error);
        this.error = error.message || 'Failed to fetch symbols';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Fetch a symbol by trading symbol
     * @param {string} tradingSymbol - Trading symbol to lookup
     * @param {string} exchange - Exchange code (default: 'NSE')
     * @returns {Object} Symbol details
     */
    async fetchSymbolByTradingSymbol(tradingSymbol, exchange = 'NSE') {
      this.loadingDetails = true;
      this.error = null;

      try {
        const response = await api.get(`/symbols/lookup/${tradingSymbol}`, { params: { exchange } });
        this.selectedSymbol = response.data;

        // Cache the symbol details
        this.symbolDetails[tradingSymbol] = response.data;

        return this.selectedSymbol;
      } catch (error) {
        console.error(`Error fetching symbol ${tradingSymbol}:`, error);
        this.error = error.message || 'Failed to fetch symbol';
        throw error;
      } finally {
        this.loadingDetails = false;
      }
    },

    /**
     * Get symbol details (fetch from cache or API if needed)
     * @param {string} tradingSymbol - Trading symbol to get details for
     * @returns {Promise<Object>} Symbol details
     */
    async getSymbolDetails(tradingSymbol) {
      // Check if we already have the details cached
      if (this.symbolDetails[tradingSymbol]) {
        this.selectedSymbol = this.symbolDetails[tradingSymbol];
        return this.selectedSymbol;
      }

      // Otherwise fetch from API
      return await this.fetchSymbolByTradingSymbol(tradingSymbol);
    },

    /**
     * Set selected symbol manually
     * @param {Object} symbol - Symbol object to select
     */
    setSelectedSymbol(symbol) {
      this.selectedSymbol = symbol;

      // Also cache in symbolDetails if not already there
      if (symbol && symbol.trading_symbol && !this.symbolDetails[symbol.trading_symbol]) {
        this.symbolDetails[symbol.trading_symbol] = symbol;
      }
    },

    /**
     * Clear selected symbol
     */
    clearSelectedSymbol() {
      this.selectedSymbol = null;
    },

    /**
     * Clear all symbols
     */
    clearSymbols() {
      this.symbols = [];
      this.symbolDetails = {};
      this.filteredSymbols = [];
    },

    /**
     * Get instrument type color for UI
     * @param {string} type - Instrument type
     * @returns {string} Color code for the type
     */
    getInstrumentTypeColor(type) {
      const colorMap = {
        'EQUITY': 'blue',
        'FUT': 'purple',
        'OPT': 'orange',
        'ETF': 'green',
        'INDEX': 'cyan'
      };
      return colorMap[type] || 'grey';
    },

    /**
     * Get CSS class for symbol badge
     * @param {string} type - Instrument type
     * @returns {string} CSS class for the badge
     */
    getSymbolBadgeClass(type) {
      const classMap = {
        'EQUITY': 'badge-eq',
        'FUT': 'badge-fut',
        'OPT': 'badge-opt',
        'ETF': 'badge-etf',
        'INDEX': 'badge-index'
      };
      return classMap[type] || '';
    },

    /**
     * Get CSS class for instrument pill
     * @param {string} type - Instrument type
     * @returns {string} CSS class for the pill
     */
    getInstrumentPillClass(type) {
      const classMap = {
        'EQUITY': 'pill-eq',
        'FUT': 'pill-fut',
        'OPT': 'pill-opt',
        'ETF': 'pill-etf',
        'INDEX': 'pill-index'
      };
      return classMap[type] || '';
    },

    /**
     * Format date for display
     * @param {string} dateString - Date string to format
     * @returns {string} Formatted date string
     */
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },

    // New methods for Symbol Details page

    /**
     * Fetch historical data for a symbol
     * @param {string} symbol - Symbol to fetch data for
     * @param {string} period - Time period (1W, 1M, 3M, 6M, 1Y)
     * @returns {Promise<Array>} Historical data array
     */
    async fetchHistoricalData(symbol, period = '1M') {
      this.loadingHistorical = true;
      try {
        const { from_date, to_date } = this.getDateRangeForPeriod(period);
        const response = await api.get(`/historical/eod/${symbol}`, {
          params: { from_date, to_date }
        });

        // Process data to add change percentage
        const data = response.data.data || [];
        for (let i = 0; i < data.length - 1; i++) {
          const current = data[i];
          const prev = data[i + 1];
          current.change = ((current.close - prev.close) / prev.close) * 100;
        }

        // For the oldest record, set change to 0
        if (data.length > 0) {
          data[data.length - 1].change = 0;
        }

        this.historicalData = data;
        return this.historicalData;
      } catch (error) {
        console.error('Error fetching historical data:', error);

        // Generate sample data for development
        const dummyData = this.generateSampleHistoricalData(period);
        this.historicalData = dummyData;
        return dummyData;
      } finally {
        this.loadingHistorical = false;
      }
    },

    /**
     * Fetch prediction statistics for a symbol
     * @param {string} symbol - Symbol to fetch prediction stats for
     * @returns {Promise<Object>} Prediction stats object
     */
    async fetchPredictionStats(symbol) {
      this.loadingPredictionStats = true;
      try {
        const response = await api.get(`/predictions/summary/${symbol}`);
        this.predictionStats = response.data;
        return this.predictionStats;
      } catch (error) {
        console.error('Error fetching prediction stats:', error);

        // Return dummy data for development
        const dummyStats = {
          accuracy: 0.83,
          upAccuracy: 0.85,
          downAccuracy: 0.79,
          upPredictions: 15,
          downPredictions: 8,
          totalPredictions: 23,
          avgDaysToFulfill: 3.2,
          verifiedPredictions: 19,
          verificationRate: 0.83
        };

        this.predictionStats = dummyStats;
        return dummyStats;
      } finally {
        this.loadingPredictionStats = false;
      }
    },

    /**
     * Fetch predictions for a symbol
     * @param {string} symbol - Symbol to fetch predictions for
     * @param {number} limit - Maximum number of predictions to fetch
     * @returns {Promise<Array>} Predictions array
     */
    async fetchPredictions(symbol, limit = 5) {
      this.loadingPredictions = true;
      try {
        const response = await api.get(`/predictions/${symbol}`, { params: { limit } });
        this.symbolPredictions = response.data.predictions || [];
        return this.symbolPredictions;
      } catch (error) {
        console.error('Error fetching symbol predictions:', error);
      } finally {
        this.loadingPredictions = false;
      }
    },

    /**
     * Calculate date range for a given period
     * @param {string} period - Period specifier (1W, 1M, 3M, 6M, 1Y)
     * @returns {Object} Object with from_date and to_date strings
     */
    getDateRangeForPeriod(period) {
      const today = new Date();
      let fromDate = new Date();

      switch (period) {
        case '1W':
          fromDate.setDate(today.getDate() - 7);
          break;
        case '1M':
          fromDate.setMonth(today.getMonth() - 1);
          break;
        case '3M':
          fromDate.setMonth(today.getMonth() - 3);
          break;
        case '6M':
          fromDate.setMonth(today.getMonth() - 6);
          break;
        case '1Y':
          fromDate.setFullYear(today.getFullYear() - 1);
          break;
        case 'ALL':
          fromDate.setFullYear(today.getFullYear() - 5); // Get up to 5 years
          break;
        default:
          fromDate.setMonth(today.getMonth() - 1); // Default to 1M
      }

      // Format dates as YYYY-MM-DD
      const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };

      return {
        from_date: formatDate(fromDate),
        to_date: formatDate(today)
      };
    },

    /**
     * Refresh a prediction
     * @param {number|object} predictionId - Prediction ID or prediction object
     * @returns {Promise<Object>} Updated prediction
     */
    async refreshPrediction(predictionId) {
      if (typeof predictionId === 'object' && predictionId.id) {
        predictionId = predictionId.id;
      }

      try {
        const response = await api.post(`/predictions/refresh/${predictionId}`);
        return response.data;
      } catch (error) {
        console.error('Error refreshing prediction:', error);
        throw error;
      }
    },

    /**
     * Generate sample historical data for development
     * @param {string} period - Time period
     * @returns {Array} Sample historical data
     */
    generateSampleHistoricalData(period) {
      const dayCount = period === '1W' ? 7 :
        period === '1M' ? 30 :
          period === '3M' ? 90 :
            period === '6M' ? 180 :
              period === '1Y' ? 365 : 30;

      const result = [];
      const basePrice = 2000 + Math.random() * 1000;
      let currentPrice = basePrice;

      for (let i = 0; i < dayCount; i++) {
        const date = new Date();
        date.setDate(date.getDate() - i);

        // Random daily variation
        const dailyChange = (Math.random() * 3 - 1.5) / 100; // -1.5% to +1.5%
        const prevPrice = currentPrice;
        currentPrice = currentPrice * (1 + dailyChange);

        // Random high/low within day
        const dayRange = currentPrice * 0.02; // 2% range
        const high = currentPrice + (dayRange * Math.random());
        const low = currentPrice - (dayRange * Math.random());

        // Volume with some randomness
        const volume = Math.round(100000 + Math.random() * 900000);

        result.push({
          date: date.toISOString().split('T')[0],
          open: prevPrice,
          high: high,
          low: low,
          close: currentPrice,
          volume: volume,
          change: ((currentPrice - prevPrice) / prevPrice) * 100
        });
      }

      return result;
    },

    // Additional methods for other tabs (can be implemented as needed)
    async fetchModelDetails(symbol) {
      try {
        const response = await api.get(`/models/${symbol}/details`);
        return response.data;
      } catch (error) {
        console.error('Error fetching model details:', error);

        // Return dummy data
        return {
          details: {
            version: 'v2.3.1',
            lastTrainedDate: '2024-12-15',
            lastEvaluatedDate: '2024-12-20',
            classifierType: 'LightGBM',
            featureCount: 27,
            trainingSamples: 12450,
            health: 'Good',
            healthScore: 85
          },
          stats: {
            accuracy: 0.82,
            precision: 0.77,
            recall: 0.85,
            f1Score: 0.81,
            accuracyTrend: 2.3,
            precisionTrend: 1.5,
            recallTrend: -0.7,
            f1ScoreTrend: 1.1
          },
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
          }
        };
      }
    },

    async fetchModelHistory(symbol) {
      try {
        const response = await api.get(`/models/${symbol}/history`);
        return response.data;
      } catch (error) {
        console.error('Error fetching model history:', error);

        // Generate sample history data
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

        return history;
      }
    },

    async retrainModel(symbol) {
      try {
        const response = await api.post(`/models/train/${symbol}`, { force_retrain: true });
        return response.data;
      } catch (error) {
        console.error('Error retraining model:', error);
        throw error;
      }
    },

    async fetchTechnicalAnalysis(symbol) {
      try {
        const response = await api.get(`/technical/${symbol}`);
        return response.data;
      } catch (error) {
        console.error('Error fetching technical analysis:', error);

        // Return dummy data
        return {
          summary: {
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
          indicators: [
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
          currentPrice: 2195.75
        };
      }
    },

    async fetchSupportResistance(symbol) {
      try {
        const response = await api.get(`/technical/${symbol}/levels`);
        return response.data;
      } catch (error) {
        console.error('Error fetching support/resistance levels:', error);

        // Return dummy data
        return {
          support: [
            { value: 2150.50, strength: 'Strong', strengthValue: 3 },
            { value: 2120.75, strength: 'Moderate', strengthValue: 2 },
            { value: 2080.25, strength: 'Weak', strengthValue: 1 }
          ],
          resistance: [
            { value: 2230.25, strength: 'Strong', strengthValue: 3 },
            { value: 2275.50, strength: 'Moderate', strengthValue: 2 },
            { value: 2310.00, strength: 'Weak', strengthValue: 1 }
          ]
        };
      }
    },

    async fetchSimilarSymbols(symbol) {
      try {
        const response = await api.get(`/symbols/similar/${symbol}`);
        return response.data;
      } catch (error) {
        console.error('Error fetching similar symbols:', error);

        // Return dummy data
        return {
          symbols: [
            { trading_symbol: 'TATAMOTORS', name: 'Tata Motors Ltd.' },
            { trading_symbol: 'MARUTI', name: 'Maruti Suzuki India Ltd.' },
            { trading_symbol: 'M&M', name: 'Mahindra & Mahindra Ltd.' },
            { trading_symbol: 'HEROMOTOCO', name: 'Hero MotoCorp Ltd.' },
            { trading_symbol: 'BAJAJ-AUTO', name: 'Bajaj Auto Ltd.' },
            { trading_symbol: 'ASHOKLEY', name: 'Ashok Leyland Ltd.' }
          ]
        };
      }
    },

    async fetchComparisonChartData(symbols, period) {
      try {
        const response = await api.post(`/comparison/chart`, {
          symbols,
          period
        });
        return response.data;
      } catch (error) {
        console.error('Error fetching comparison chart data:', error);

        // Generate sample data
        const dayCount = period === '1M' ? 30 : period === '3M' ? 90 : period === '6M' ? 180 : 365;
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

        return comparisonData;
      }
    },

    async fetchComparisonMetrics(symbols) {
      try {
        const response = await api.post(`/comparison/metrics`, {
          symbols
        });
        return response.data;
      } catch (error) {
        console.error('Error fetching comparison metrics:', error);

        // Generate sample metrics data
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

        return metrics;
      }
    },

    async fetchPredictionTimeline(symbol, days = 90) {
      try {
        const response = await api.get(`/predictions/${symbol}`, {
          params: { lookback_days: days }
        });
        return response.data;
      } catch (error) {
        console.error('Error fetching prediction timeline:', error);

        // Generate fallback timeline data
        const data = [];
        const today = new Date();

        // Generate points for each week
        for (let i = 0; i < days; i += 7) {
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

        return { data: data.reverse() };
      }
    }
  }
});