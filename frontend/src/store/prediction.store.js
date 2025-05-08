// src/store/prediction.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const usePredictionStore = defineStore('prediction', {
  state: () => ({
    topPredictions: [],
    verifiedPredictions: [],
    predictionsBySymbol: {},
    stats: {
      accuracy: 0,
      accuracyChange: 0,
      upPredictions: 0,
      downPredictions: 0,
      upAccuracy: 0,
      downAccuracy: 0,
      avgDaysToFulfill: 0
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
      accuracyTrend: false,
      symbolPredictions: false
    }
  }),

  actions: {
    /**
     * Fetch global prediction statistics
     * @returns {Object} Prediction stats
     */
    fetchPredictionStats: async function () {
      this.loading.stats = true;

      try {
        const response = await api.get('/predictions/status/accuracy');

        // Update state with response data
        this.stats.accuracy = response.data.accuracy || 0;
        this.stats.accuracyChange = response.data.accuracyChange || 0;
        this.stats.upPredictions = response.data.upPredictions || 0;
        this.stats.downPredictions = response.data.downPredictions || 0;

        if (response.data.directionAccuracy) {
          this.stats.upAccuracy = response.data.directionAccuracy;
          this.stats.downAccuracy = response.data.directionAccuracy;
        } else {
          // If separate direction accuracies are provided
          this.stats.upAccuracy = response.data.upAccuracy || 0;
          this.stats.downAccuracy = response.data.downAccuracy || 0;
        }

        this.stats.avgDaysToFulfill = response.data.avgDaysToFulfill || 0;

        return response.data;
      } catch (error) {
        console.error('Error fetching prediction stats:', error);
        throw error;
      } finally {
        this.loading.stats = false;
      }
    },

    /**
     * Fetch prediction stats for a specific symbol
     * @param {string} symbol - Trading symbol
     * @returns {Object} Symbol-specific prediction stats
     */
    fetchPredictionStatsBySymbol: async function (symbol) {
      this.loading.stats = true;

      try {
        const response = await api.get(`/predictions/summary/${symbol}`);
        return response.data;
      } catch (error) {
        console.error('Error fetching prediction stats for symbol:', error);
        throw error;
      } finally {
        this.loading.stats = false;
      }
    },

    /**
     * Fetch predictions for a specific symbol
     * @param {string} symbol - Trading symbol
     * @param {Object} params - Optional query parameters
     * @returns {Array} Symbol-specific predictions
     */
    fetchPredictionsBySymbol: async function (symbol, params = {}) {
      this.loading.symbolPredictions = true;

      try {
        const response = await api.get(`/predictions/symbol/${symbol}`, { params });

        // Store in the cache by symbol
        this.predictionsBySymbol[symbol] = response.data.predictions || [];

        return this.predictionsBySymbol[symbol];
      } catch (error) {
        console.error('Error fetching predictions for symbol:', error);
        throw error;
      } finally {
        this.loading.symbolPredictions = false;
      }
    },

    /**
     * Fetch top predictions with high confidence
     * @param {number} confidence - Minimum confidence threshold (0-1)
     * @param {number} limit - Maximum number of predictions to return
     * @returns {Array} High confidence predictions
     */
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

    /**
     * Fetch verified predictions
     * @param {number} limit - Maximum number of predictions to return
     * @param {boolean} foEligible - Whether to filter for F&O eligible symbols
     * @returns {Array} Verified predictions
     */
    fetchVerifiedPredictions: async function (limit = 10, foEligible = true) {
      this.loading.verifiedPredictions = true;

      try {
        const response = await api.get('/predictions', {
          params: { verified: true, limit, fo_eligible: foEligible }
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

    /**
     * Fetch accuracy trend over time
     * @param {string} period - Time period (e.g., '30d')
     * @returns {Object} Accuracy trend data for charts
     */
    fetchAccuracyTrend: async function (period = '30d') {
      this.loading.accuracyTrend = true;

      try {
        // In a production environment, this would call an API endpoint:
        // const response = await api.get(`/predictions/accuracy/trend?period=${period}`);

        // For now, simulate the API response with mock data
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
    },

    /**
     * Refresh a prediction by symbol
     * @param {string} symbol - Trading symbol to refresh
     * @returns {Object} Updated prediction data
     */
    refreshPrediction: async function (symbol) {
      try {
        const response = await api.post(`/predictions/refresh/${symbol}`);
        return response.data;
      } catch (error) {
        console.error('Error fetching prediction refresh:', error);
        throw error;
      }
    },

    /**
     * Clear all predictions data
     */
    clearPredictions: function () {
      this.topPredictions = [];
      this.verifiedPredictions = [];
      this.predictionsBySymbol = {};
    }
  }
});