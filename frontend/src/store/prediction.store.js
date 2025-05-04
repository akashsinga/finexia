// src/store/prediction.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const usePredictionStore = defineStore('prediction', {
  state: () => ({
    topPredictions: [],
    verifiedPredictions: [],
    stats: {
      accuracy: 0,
      accuracyChange: 0,
      upPredictions: 0,
      downPredictions: 0,
      upAccuracy: 0,
      downAccuracy: 0
    },
    accuracyTrend: {
      labels: [],
      datasets: [{
        label: 'Prediction Accuracy',
        data: [],
        borderColor: '#1E3A8A',
        backgroundColor: 'rgba(30, 58, 138, 0.1)',
        tension: 0.3,
        fill: true
      }]
    },
    loading: {
      stats: false,
      topPredictions: false,
      verifiedPredictions: false,
      accuracyTrend: false
    }
  }),

  actions: {
    fetchPredictionStats: async function () {
      this.loading.stats = true;
      try {
        const response = await api.get('/predictions/status/accuracy');
        this.stats.accuracy = response.data.accuracy || 0;
        this.stats.accuracyChange = 2.3; // placeholder
        this.stats.upPredictions = response.data.upPredictions || 0;
        this.stats.downPredictions = response.data.downPredictions || 0;

        if (response.data.directionAccuracy) {
          this.stats.upAccuracy = response.data.directionAccuracy;
          this.stats.downAccuracy = response.data.directionAccuracy;
        }
        return response.data;
      } catch (error) {
        console.error('Error fetching prediction stats:', error);
        throw error;
      } finally {
        this.loading.stats = false;
      }
    },

    fetchPredictionStatsBySymbol: async function (symbol) {
      this.loading.stats = true
      try {
        const response = await api.get(`/predictions/summary/${symbol}`);
        return response.data;
      } catch (error) {
        console.error('Error fetching prediction stats:', error);
        throw error;
      } finally {
        this.loading.stats = false;
      }
    },

    fetchPredictionsBySymbol: async function (symbol) {
    },

    fetchTopPredictions: async function (confidence = 0.7, limit = 5) {
      this.loading.topPredictions = true;
      try {
        // Added fo_eligible=true parameter to only get eligible symbols
        const response = await api.get('/predictions', {
          params: { min_confidence: confidence, limit, fo_eligible: true }
        });
        this.topPredictions = response.data.predictions || [];
        return this.topPredictions;
      } catch (error) {
        console.error('Error fetching top predictions:', error);
        throw error;
      } finally {
        this.loading.topPredictions = false;
      }
    },

    fetchVerifiedPredictions: async function (limit = 10) {
      this.loading.verifiedPredictions = true;
      try {
        const response = await api.get('/predictions', {
          params: { verified: true, limit }
        });
        this.verifiedPredictions = response.data.predictions || [];
        return this.verifiedPredictions;
      } catch (error) {
        console.error('Error fetching verified predictions:', error);
        throw error;
      } finally {
        this.loading.verifiedPredictions = false;
      }
    },

    fetchAccuracyTrend: async function (period = '30d') {
      this.loading.accuracyTrend = true;
      try {
        // Simulating an API call with placeholder data
        // In production, this would be: await api.get(`/predictions/accuracy/trend?period=${period}`)

        return new Promise(resolve => {
          setTimeout(() => {
            const labels = [];
            const data = [];
            const days = period === '7d' ? 7 : period === '30d' ? 30 : 90;

            const now = new Date();
            for (let i = days - 1; i >= 0; i--) {
              const date = new Date(now);
              date.setDate(date.getDate() - i);
              labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
              data.push(0.7 + Math.random() * 0.2);
            }

            this.accuracyTrend = {
              labels,
              datasets: [{
                label: 'Prediction Accuracy',
                data,
                borderColor: '#1E3A8A',
                backgroundColor: 'rgba(30, 58, 138, 0.1)',
                tension: 0.3,
                fill: true
              }]
            };

            this.loading.accuracyTrend = false;
            resolve(this.accuracyTrend);
          }, 800);
        });
      } catch (error) {
        console.error('Error fetching accuracy trend:', error);
        this.loading.accuracyTrend = false;
        throw error;
      }
    }
  }
});