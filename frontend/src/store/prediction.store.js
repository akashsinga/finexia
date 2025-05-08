// src/store/prediction.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const usePredictionStore = defineStore('prediction', {
  state: () => ({
    // Prediction lists
    topPredictions: [],
    verifiedPredictions: [],
    predictionsBySymbol: {},
    predictions: [],

    // Prediction details
    selectedPrediction: null,

    // Pagination
    pagination: { page: 1, itemsPerPage: 10, totalPredictions: 0 },
    filters: { direction: null, verified: null, foEligible: true, predictionDate: null, minConfidence: 0.5 },
    stats: { accuracy: 0, accuracyChange: 0, totalPredictions: 0, upPredictions: 0, downPredictions: 0, upAccuracy: 0, downAccuracy: 0, avgDaysToFulfill: 0 },
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
    loading: { stats: false, topPredictions: false, verifiedPredictions: false, accuracyTrend: false, symbolPredictions: false, predictions: false },
    error: null
  }),

  getters: {
    // Get formatted date for display
    formattedDateFilter: (state) => {
      if (!state.filters.predictionDate) return '';

      return new Date(state.filters.predictionDate).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
  },

  actions: {
    /**
     * Set filter values
     */
    setFilter(filterName, value) {
      this.filters[filterName] = value;
    },

    /**
     * Reset all filters to defaults
     */
    resetFilters() {
      this.filters = { direction: null, verified: null, foEligible: null, predictionDate: null, minConfidence: 0.5 };

      // Reset to first page
      this.pagination.page = 1;
    },

    /**
     * Set pagination values
     */
    setPagination(page, itemsPerPage) {
      if (page) this.pagination.page = page;
      if (itemsPerPage) this.pagination.itemsPerPage = itemsPerPage;
    },

    /**
     * Fetch global prediction statistics
     * @returns {Object} Prediction stats
     */
    async fetchPredictionStats() {
      this.loading.stats = true;

      try {
        const response = await api.get('/predictions/status/accuracy');

        // Update state with response data
        this.stats.accuracy = response.data.accuracy || 0;
        this.stats.accuracyChange = response.data.accuracyChange || 0;
        this.stats.upPredictions = response.data.upPredictions || 0;
        this.stats.downPredictions = response.data.downPredictions || 0;
        this.stats.totalPredictions = response.data.totalPredictions || 0;

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
        this.error = error.message || 'Failed to fetch prediction stats';
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
    async fetchPredictionStatsBySymbol(symbol) {
      this.loading.stats = true;

      try {
        const response = await api.get(`/predictions/summary/${symbol}`);
        return response.data;
      } catch (error) {
        console.error('Error fetching prediction stats for symbol:', error);
        this.error = error.message || 'Failed to fetch prediction stats for symbol';
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
    async fetchPredictionsBySymbol(symbol, params = {}) {
      this.loading.symbolPredictions = true;

      try {
        const response = await api.get(`/predictions/symbol/${symbol}`, { params });

        // Store in the cache by symbol
        this.predictionsBySymbol[symbol] = response.data.predictions || [];

        return this.predictionsBySymbol[symbol];
      } catch (error) {
        console.error('Error fetching predictions for symbol:', error);
        this.error = error.message || 'Failed to fetch predictions for symbol';
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
    async fetchTopPredictions(confidence = 0.7, limit = 5) {
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
        this.error = error.message || 'Failed to fetch top predictions';
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
    async fetchVerifiedPredictions(limit = 10, foEligible = true) {
      this.loading.verifiedPredictions = true;

      try {
        const response = await api.get('/predictions', {
          params: { verified: true, limit, fo_eligible: foEligible }
        });

        this.verifiedPredictions = response.data.predictions || [];
        return this.verifiedPredictions;
      } catch (error) {
        console.error('Error fetching verified predictions:', error);
        this.error = error.message || 'Failed to fetch verified predictions';
        throw error;
      } finally {
        this.loading.verifiedPredictions = false;
      }
    },

    /**
     * Fetch all predictions with filtering and pagination
     */
    async fetchPredictions() {
      this.loading.predictions = true;

      try {
        // Calculate pagination
        const skip = (this.pagination.page - 1) * this.pagination.itemsPerPage;

        // Prepare filter params
        const params = {
          skip,
          limit: this.pagination.itemsPerPage,
          min_confidence: this.filters.minConfidence
        };

        // Add optional filters if set
        if (this.filters.direction) {
          params.direction = this.filters.direction;
        }

        if (this.filters.verified !== null) {
          params.verified = this.filters.verified;
        }

        if (this.filters.foEligible !== null) {
          params.fo_eligible = this.filters.foEligible;
        }

        if (this.filters.predictionDate) {
          // Ensure we have a date that's converted to local timezone YYYY-MM-DD 
          let date;

          if (this.filters.predictionDate instanceof Date) {
            date = this.filters.predictionDate;
          } else {
            date = new Date(this.filters.predictionDate);
          }

          // Format to YYYY-MM-DD without timezone conversion
          const year = date.getFullYear();
          const month = String(date.getMonth() + 1).padStart(2, '0');
          const day = String(date.getDate()).padStart(2, '0');

          params.prediction_date = `${year}-${month}-${day}`;
        }

        // Call API
        const response = await api.get('/predictions', { params });

        // Update data
        this.predictions = response.data.predictions.map(pred => ({
          ...pred,
          refreshing: false
        }));
        this.pagination.totalPredictions = response.data.count;

        return this.predictions;
      } catch (error) {
        console.error('Error fetching predictions:', error);
        this.error = error.message || 'Failed to fetch predictions';
        throw error;
      } finally {
        this.loading.predictions = false;
      }
    },

    /**
     * Fetch accuracy trend over time
     * @param {string} period - Time period (e.g., '30d')
     * @returns {Object} Accuracy trend data for charts
     */
    async fetchAccuracyTrend(period = '30d') {
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
        this.error = error.message || 'Failed to fetch accuracy trend';
        this.loading.accuracyTrend = false;
        throw error;
      }
    },

    /**
     * Refresh a prediction by symbol
     * @param {string} symbol - Trading symbol to refresh
     * @returns {Object} Updated prediction data
     */
    async refreshPrediction(prediction) {
      // Find prediction index and set refreshing state if it's in the predictions array
      const index = this.predictions.findIndex(p => p.id === prediction.id);
      if (index !== -1) {
        this.predictions[index].refreshing = true;
      }

      try {
        const response = await api.post(`/predictions/refresh/${prediction.trading_symbol}`);
        const updatedPrediction = { ...response.data, refreshing: false };

        // Update in predictions array if it exists there
        if (index !== -1) {
          this.predictions.splice(index, 1, updatedPrediction);
        }

        // Update selected prediction if this was the one
        if (this.selectedPrediction && this.selectedPrediction.id === prediction.id) {
          this.selectedPrediction = updatedPrediction;
        }

        return updatedPrediction;
      } catch (error) {
        console.error('Error refreshing prediction:', error);
        this.error = error.message || 'Failed to refresh prediction';
        throw error;
      } finally {
        // Ensure refreshing state is reset
        if (index !== -1) {
          this.predictions[index].refreshing = false;
        }
      }
    },

    /**
     * Set the selected prediction for detail view
     */
    setSelectedPrediction(prediction) {
      this.selectedPrediction = prediction;
    },

    /**
     * Clear the selected prediction
     */
    clearSelectedPrediction() {
      this.selectedPrediction = null;
    },

    /**
     * Clear all predictions data
     */
    clearPredictions() {
      this.topPredictions = [];
      this.verifiedPredictions = [];
      this.predictionsBySymbol = {};
      this.predictions = [];
      this.selectedPrediction = null;
    },

    // Utility methods
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    },

    formatDateTime(dateTimeString) {
      if (!dateTimeString) return 'N/A';
      return new Date(dateTimeString).toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    },

    formatPercentage(value) {
      if (value === null || value === undefined) return 'N/A';
      return (value * 100).toFixed(1) + '%';
    },

    getDirectionClass(direction) {
      return direction === 'UP' ? 'direction-up' : 'direction-down';
    },

    getDirectionIcon(direction) {
      return direction === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold';
    }
  }
});