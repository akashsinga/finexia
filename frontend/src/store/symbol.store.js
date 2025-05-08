// src/store/symbol.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useSymbolStore = defineStore('symbol', {
  state: () => ({
    symbols: [],
    selectedSymbol: null,
    symbolDetails: {},
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
    }
  },

  actions: {
    /**
     * Fetch all symbols with optional filtering
     * @param {Object} params - Query parameters for filtering
     * @returns {Array} Array of symbol objects
     */
    fetchSymbols: async function (params = { active_only: true }) {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get('/symbols', { params });
        this.symbols = response.data;
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
    fetchSymbolByTradingSymbol: async function (tradingSymbol, exchange = 'NSE') {
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
    getSymbolDetails: async function (tradingSymbol) {
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
    },

    /**
     * Search symbols by name or trading symbol
     * @param {string} query - Search query
     * @returns {Array} Filtered array of symbol objects
     */
    searchSymbols(query) {
      if (!query || !query.trim()) {
        return this.symbols;
      }

      const normalizedQuery = query.toLowerCase().trim();

      return this.symbols.filter(symbol =>
        symbol.trading_symbol.toLowerCase().includes(normalizedQuery) ||
        symbol.name.toLowerCase().includes(normalizedQuery)
      );
    },

    /**
     * Filter symbols by F&O eligibility
     * @param {boolean} eligible - Whether to filter for eligible symbols
     * @returns {Array} Filtered array of symbol objects
     */
    filterByFOEligibility(eligible) {
      if (eligible === null || eligible === undefined) {
        return this.symbols;
      }

      return this.symbols.filter(symbol => symbol.fo_eligible === eligible);
    }
  }
});