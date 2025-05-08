// src/store/historical.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';
import { formatDate } from '@/utils';

export const useHistoricalStore = defineStore('historical', {
  state: () => ({
    loading: false,
    eod_data: [],
    error: null
  }),

  getters: {
    /**
     * Get latest EOD data entry
     * @returns {Object|null} Latest EOD data with additional fields
     */
    latestEOD: (state) => {
      if (!state.eod_data || state.eod_data.length === 0) {
        return null;
      }

      const latestEOD = state.eod_data[0];
      const prevClose = state.eod_data[1] ? state.eod_data[1].close : latestEOD.close;

      return { date: latestEOD.date, open: latestEOD.open, high: latestEOD.high, low: latestEOD.low, close: latestEOD.close, volume: latestEOD.volume, change: prevClose ? ((latestEOD.close - prevClose) / prevClose) * 100 : 0 };
    },

    /**
     * Get chart data formated for chart components 
     * @returns {Object} Formatted chart data object
     */
    chartData: (state) => {
      if (!state.eod_data || state.eod_data.length === 0) {
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
      const dates = [...state.eod_data]
        .map((item) => formatDate(item.date, 'MMM D'))
        .reverse();

      const prices = [...state.eod_data]
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
    }
  },

  actions: {
    /**
     * Fetch historical EOD data for a symbol
     * @param {string} symbol - Trading symbol
     * @param {Object} params - Optional query parameters
     * @returns {Array} EOD data
     */
    fetchHistoricalEODData: async function (symbol, params = {}) {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get(`/historical/eod/${symbol}`, { params });
        this.eod_data = response.data.data;
        return this.eod_data;
      } catch (error) {
        console.error('Error fetching historical data:', error);
        this.error = error.message || 'Failed to fetch historical data';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * Clear historical data
     */
    clearHistoricalData: function () {
      this.eod_data = [];
    }
  }
});