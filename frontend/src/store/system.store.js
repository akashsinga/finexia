// src/store/system.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useSystemStore = defineStore('system', {
  state: () => ({
    stats: {
      totalPredictions: 0,
      predictionChange: 0,
      todayPredictions: 0,
      activeModels: 0,
      newModels: 0
    },
    lastUpdateTime: 'Just now',
    loading: false
  }),

  actions: {
    async fetchSystemStatus() {
      this.loading = true;
      try {
        const response = await api.get('/system/status');
        this.stats.totalPredictions = response.data.total_predictions;
        this.stats.todayPredictions = response.data.today_predictions;
        this.stats.predictionChange = 5; // placeholder
        this.updateLastRefreshTime();
        return this.stats;
      } catch (error) {
        console.error('Error fetching system status:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    updateLastRefreshTime() {
      const now = new Date();
      this.lastUpdateTime = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
});