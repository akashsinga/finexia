// src/store/model.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useModelStore = defineStore('model', {
  state: () => ({
    topModels: [],
    loading: false
  }),

  actions: {
    async fetchModelPerformance(topN = 5, metric = 'f1_score') {
      this.loading = true;
      try {
        const response = await api.get('/models/performance', {
          params: { top_n: topN, metric }
        });
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