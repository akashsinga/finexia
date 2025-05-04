// src/store/symbol.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useSymbolStore = defineStore('symbol', {
  state: () => ({
    symbols: [],
    selectedSymbol: null,
    loading: false,
    error: null
  }),

  getters: {
    getSymbolByTradingSymbol: (state) => (tradingSymbol) => {
      return state.symbols.find(s => s.trading_symbol === tradingSymbol) || null;
    },

    getFOEligibleSymbols: (state) => {
      return state.symbols.filter(s => s.fo_eligible);
    },

    getSymbolCount: (state) => {
      return state.symbols.length;
    }
  },

  actions: {
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

    fetchSymbolByTradingSymbol: async function (tradingSymbol, exchange = 'NSE') {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get(`/symbols/lookup/${tradingSymbol}`, {
          params: { exchange }
        });
        this.selectedSymbol = response.data;
        return this.selectedSymbol;
      } catch (error) {
        console.error(`Error fetching symbol ${tradingSymbol}:`, error);
        this.error = error.message || 'Failed to fetch symbol';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    setSelectedSymbol(symbol) {
      this.selectedSymbol = symbol;
    },

    clearSelectedSymbol() {
      this.selectedSymbol = null;
    },

    clearSymbols() {
      this.symbols = [];
    }
  }
});