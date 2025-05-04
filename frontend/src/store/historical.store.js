// src/store/historical.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useHistoricalStore = defineStore('historical', {
  state: () => ({
    loading: false,
    eod_data: [],
    error: null
  }),
  actions: {
    fetchHistoricalEODData: async function (symbol, params) {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.get(`/historical/eod/${symbol}`, { params });
        this.eod_data = response.data.data;
        return this.eod_data;
      } catch (error) {
        console.error('Error fetching symbols:', error);
        this.error = error.message || 'Failed to fetch symbols';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
})