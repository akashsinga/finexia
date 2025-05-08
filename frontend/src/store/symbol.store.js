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
    }
  }
});