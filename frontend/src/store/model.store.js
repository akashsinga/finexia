// src/store/model.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useModelStore = defineStore('model', {
  state: () => ({
    topModels: [],
    loading: false
  }),

  actions: {
    async fetchModelPerformance(topN = 5, metric = 'f1_score', foEligible = true) {
      this.loading = true;
      try {
        const response = await api.post('/models/performance', { top_n: topN, metric, fo_eligible: foEligible });
        this.topModels = response.data || [];
        return this.topModels;
      } catch (error) {
        console.error('Error fetching model performance:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
});