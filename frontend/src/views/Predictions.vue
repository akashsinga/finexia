<template>
  <div class="predictions-page">
    <!-- Header with filters -->
    <div class="filter-card">
      <div class="filter-header">
        <h1 class="page-title">Predictions</h1>
        <div class="filter-actions">
          <v-btn color="primary" size="small" prepend-icon="mdi-refresh" @click="refreshPredictions" :loading="loading.predictions">
            Refresh
          </v-btn>
        </div>
      </div>

      <div class="filter-form">
        <div class="filter-row">
          <div class="filter-group">
            <v-select v-model="filters.direction" label="Direction" :items="directionOptions" density="compact" variant="outlined" hide-details class="filter-input"></v-select>
          </div>
          <div class="filter-group">
            <v-select v-model="filters.verified" label="Status" :items="verificationOptions" density="compact" variant="outlined" hide-details class="filter-input"></v-select>
          </div>
          <div class="filter-group">
            <v-select v-model="filters.foEligible" label="F&O Eligible" :items="foEligibleOptions" density="compact" variant="outlined" hide-details class="filter-input"></v-select>
          </div>
          <div class="filter-group date-filter">
            <v-menu v-model="datePickerOpen" :close-on-content-click="false" transition="scale-transition" min-width="auto">
              <template v-slot:activator="{ props }">
                <v-text-field v-model="formattedDateFilter" label="Prediction Date" prepend-inner-icon="mdi-calendar" readonly variant="outlined" density="compact" hide-details v-bind="props" class="filter-input" clearable @click:clear="filters.predictionDate = null"></v-text-field>
              </template>
              <v-date-picker v-model="filters.predictionDate" @update:model-value="datePickerOpen = false"></v-date-picker>
            </v-menu>
          </div>
        </div>

        <div class="filter-row">
          <div class="confidence-filter">
            <div class="confidence-label">Confidence Threshold: {{ filters.minConfidence * 100 }}%</div>
            <v-slider v-model="filters.minConfidence" min="0" max="1" step="0.05" thumb-label :thumb-size="20" hide-details density="compact" color="primary" track-color="primary-lighten-3" :thumb-label-formatter="val => Math.round(val * 100) + '%'"></v-slider>
          </div>
          <div class="filter-actions-right">
            <v-btn variant="text" size="small" @click="resetFilters">
              Reset Filters
            </v-btn>
            <v-btn color="primary" size="small" @click="applyFilters">
              Apply Filters
            </v-btn>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Summary Cards -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon bg-primary-light">
          <v-icon color="primary">mdi-chart-arc</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercentage(predictionStats.accuracy) }}</div>
          <div class="stat-label">Overall Accuracy</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-success-light">
          <v-icon color="success">mdi-arrow-up-bold</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercentage(predictionStats.upAccuracy) }}</div>
          <div class="stat-label">UP Accuracy</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-error-light">
          <v-icon color="error">mdi-arrow-down-bold</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatPercentage(predictionStats.downAccuracy) }}</div>
          <div class="stat-label">DOWN Accuracy</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-info-light">
          <v-icon color="info">mdi-calendar-check</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ predictionStats.avgDaysToFullfill ? predictionStats.avgDaysToFullfill.toFixed(1) : 'N/A' }}</div>
          <div class="stat-label">Avg. Days to Verify</div>
        </div>
      </div>
    </div>

    <!-- Predictions Data Table -->
    <div class="data-table-card">
      <v-data-table :headers="tableHeaders" :items="predictions" :loading="loading.predictions" :items-per-page="itemsPerPage" :page="page" :server-items-length="totalPredictions" @update:page="page = $event" @update:items-per-page="itemsPerPage = $event" class="predictions-table" density="comfortable">
        <template v-slot:no-data>
          <div class="empty-state">
            <v-icon size="large" color="gray">mdi-chart-timeline-variant</v-icon>
            <p>No predictions found matching your filters</p>
          </div>
        </template>

        <template #item="{ item }">
          <tr>
            <!-- Symbol column -->
            <td>
              <div class="symbol-cell">
                <div class="symbol">{{ item.trading_symbol }}</div>
                <v-btn variant="text" size="x-small" density="compact" icon="mdi-open-in-new" @click="viewSymbolDetails(item.trading_symbol)" class="view-symbol-btn"></v-btn>
              </div>
            </td>

            <!-- Date column -->
            <td>{{ formatDate(item.date) }}</td>

            <!-- Direction prediction column -->
            <td>
              <div v-if="item.direction_prediction" class="direction-chip" :class="getDirectionClass(item.direction_prediction)">
                <v-icon size="x-small">{{ getDirectionIcon(item.direction_prediction) }}</v-icon>
                {{ item.direction_prediction }}
              </div>
              <div v-else class="text-gray-400">-</div>
            </td>

            <!-- Move confidence column -->
            <td>
              <div class="confidence-bar-container">
                <div class="confidence-value">{{ (item.strong_move_confidence * 100).toFixed(0) }}%</div>
                <div class="confidence-bar">
                  <div class="confidence-bar-fill" :style="{ width: `${item.strong_move_confidence * 100}%` }"></div>
                </div>
              </div>
            </td>

            <!-- Direction confidence column -->
            <td>
              <div v-if="item.direction_confidence" class="confidence-bar-container">
                <div class="confidence-value">{{ (item.direction_confidence * 100).toFixed(0) }}%</div>
                <div class="confidence-bar">
                  <div class="confidence-bar-fill" :class="item.direction_prediction === 'UP' ? 'bg-success' : 'bg-error'" :style="{ width: `${item.direction_confidence * 100}%` }"></div>
                </div>
              </div>
              <div v-else class="text-gray-400">-</div>
            </td>

            <!-- Verification status column -->
            <td>
              <v-chip v-if="item.verified !== null" :color="item.verified ? 'success' : 'error'" size="x-small" text-color="white" class="status-chip">
                {{ item.verified ? 'Success' : 'Failed' }}
              </v-chip>
              <v-chip v-else color="warning" size="x-small" variant="outlined" class="status-chip">
                Pending
              </v-chip>
            </td>

            <!-- Actual direction column -->
            <td>
              <div v-if="item.actual_direction" class="direction-chip" :class="getDirectionClass(item.actual_direction)">
                <v-icon size="x-small">{{ getDirectionIcon(item.actual_direction) }}</v-icon>
                {{ item.actual_direction }}
              </div>
              <div v-else class="text-gray-400">-</div>
            </td>

            <!-- Days to fulfill column -->
            <td>
              <div v-if="item.days_to_fulfill !== null">{{ item.days_to_fulfill }}</div>
              <div v-else class="text-gray-400">-</div>
            </td>

            <!-- Actions column -->
            <td>
              <div class="actions-cell">
                <v-tooltip location="top" text="View Details">
                  <template #activator="{ props }">
                    <v-btn variant="text" density="comfortable" icon="mdi-information-outline" size="small" v-bind="props" @click="viewPredictionDetails(item)"></v-btn>
                  </template>
                </v-tooltip>
                <v-tooltip location="top" text="Refresh Prediction">
                  <template #activator="{ props }">
                    <v-btn variant="text" density="comfortable" icon="mdi-refresh" size="small" v-bind="props" @click="refreshPrediction(item)" :loading="item.refreshing"></v-btn>
                  </template>
                </v-tooltip>
              </div>
            </td>
          </tr>
        </template>
      </v-data-table>
    </div>

    <!-- Prediction Details Dialog -->
    <v-dialog v-model="showPredictionDialog" max-width="600px">
      <div v-if="selectedPrediction" class="prediction-dialog">
        <div class="dialog-header">
          <h2 class="dialog-title">
            Prediction Details
            <span class="symbol-badge">{{ selectedPrediction.trading_symbol }}</span>
          </h2>
          <v-btn icon="mdi-close" variant="text" @click="showPredictionDialog = false"></v-btn>
        </div>

        <div class="dialog-content">
          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">Prediction Date</div>
              <div class="info-value">{{ formatDate(selectedPrediction.date) }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Strong Move Confidence</div>
              <div class="info-value confidence-display">
                <div class="value-text">{{ (selectedPrediction.strong_move_confidence * 100).toFixed(1) }}%</div>
                <v-progress-linear :model-value="selectedPrediction.strong_move_confidence * 100" height="8" rounded color="primary"></v-progress-linear>
              </div>
            </div>

            <div class="info-item" v-if="selectedPrediction.direction_prediction">
              <div class="info-label">Direction Prediction</div>
              <div class="info-value">
                <div class="prediction-direction-badge" :class="getDirectionClass(selectedPrediction.direction_prediction)">
                  <v-icon size="small">{{ getDirectionIcon(selectedPrediction.direction_prediction) }}</v-icon>
                  {{ selectedPrediction.direction_prediction }}
                </div>
              </div>
            </div>

            <div class="info-item" v-if="selectedPrediction.direction_confidence">
              <div class="info-label">Direction Confidence</div>
              <div class="info-value confidence-display">
                <div class="value-text">{{ (selectedPrediction.direction_confidence * 100).toFixed(1) }}%</div>
                <v-progress-linear :model-value="selectedPrediction.direction_confidence * 100" height="8" rounded :color="selectedPrediction.direction_prediction === 'UP' ? 'success' : 'error'"></v-progress-linear>
              </div>
            </div>

            <div class="info-item">
              <div class="info-label">Verification Status</div>
              <div class="info-value">
                <v-chip v-if="selectedPrediction.verified !== null" :color="selectedPrediction.verified ? 'success' : 'error'" size="small" text-color="white">
                  {{ selectedPrediction.verified ? 'Verified Success' : 'Verified Failure' }}
                </v-chip>
                <v-chip v-else color="warning" size="small" variant="outlined">
                  Pending Verification
                </v-chip>
              </div>
            </div>

            <div class="info-item" v-if="selectedPrediction.actual_direction">
              <div class="info-label">Actual Direction</div>
              <div class="info-value">
                <div class="prediction-direction-badge" :class="getDirectionClass(selectedPrediction.actual_direction)">
                  <v-icon size="small">{{ getDirectionIcon(selectedPrediction.actual_direction) }}</v-icon>
                  {{ selectedPrediction.actual_direction }}
                </div>
              </div>
            </div>

            <div class="info-item" v-if="selectedPrediction.actual_move_percent !== null">
              <div class="info-label">Actual Move Percent</div>
              <div class="info-value">{{ selectedPrediction.actual_move_percent.toFixed(2) }}%</div>
            </div>

            <div class="info-item" v-if="selectedPrediction.days_to_fulfill !== null">
              <div class="info-label">Days to Fulfill</div>
              <div class="info-value">{{ selectedPrediction.days_to_fulfill }} days</div>
            </div>

            <div class="info-item" v-if="selectedPrediction.verification_date">
              <div class="info-label">Verification Date</div>
              <div class="info-value">{{ formatDate(selectedPrediction.verification_date) }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Created At</div>
              <div class="info-value">{{ formatDateTime(selectedPrediction.created_at) }}</div>
            </div>
          </div>
        </div>

        <div class="dialog-actions">
          <v-btn variant="outlined" @click="showPredictionDialog = false">
            Close
          </v-btn>
          <v-btn color="primary" prepend-icon="mdi-refresh" @click="refreshPrediction(selectedPrediction, true)">
            Refresh Prediction
          </v-btn>
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script>
import { usePredictionStore } from '@/store/prediction.store'
import { api } from '@/plugins'

export default {
  name: 'PredictionsView',

  data() {
    return {
      // Store
      predictionStore: usePredictionStore(),

      // UI state
      page: 1,
      itemsPerPage: 10,
      totalPredictions: 0,
      datePickerOpen: false,
      showPredictionDialog: false,
      selectedPrediction: null,

      // Data
      predictions: [],
      predictionStats: {
        accuracy: 0,
        totalPredictions: 0,
        verifiedPredictions: 0,
        upPredictions: 0,
        downPredictions: 0,
        upAccuracy: 0,
        downAccuracy: 0,
        avgDaysToFullfill: null
      },

      // Loading states
      loading: {
        predictions: false,
        stats: false
      },

      // Filters
      filters: {
        direction: null,
        verified: null,
        foEligible: true,
        predictionDate: null,
        minConfidence: 0.5
      },

      // Table headers
      tableHeaders: [
        { title: 'Symbol', key: 'trading_symbol', width: '100px' },
        { title: 'Date', key: 'date', width: '100px' },
        { title: 'Direction', key: 'direction_prediction', width: '100px' },
        { title: 'Move Conf.', key: 'strong_move_confidence', width: '150px' },
        { title: 'Dir. Conf.', key: 'direction_confidence', width: '150px' },
        { title: 'Status', key: 'verified', width: '100px' },
        { title: 'Actual', key: 'actual_direction', width: '100px' },
        { title: 'Days', key: 'days_to_fulfill', width: '80px' },
        { title: 'Actions', key: 'actions', width: '100px', sortable: false }
      ],

      // Options for filters
      directionOptions: [
        { title: 'All Directions', value: null },
        { title: 'UP', value: 'UP' },
        { title: 'DOWN', value: 'DOWN' }
      ],
      verificationOptions: [
        { title: 'All Status', value: null },
        { title: 'Verified', value: true },
        { title: 'Pending', value: false }
      ],
      foEligibleOptions: [
        { title: 'All Symbols', value: null },
        { title: 'F&O Eligible', value: true },
        { title: 'Non-F&O', value: false }
      ]
    }
  },

  computed: {
    formattedDateFilter() {
      if (!this.filters.predictionDate) return '';
      return new Date(this.filters.predictionDate).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
  },

  watch: {
    page() {
      this.fetchPredictions();
    },
    itemsPerPage() {
      this.fetchPredictions();
    }
  },

  methods: {
    async fetchPredictions() {
      this.loading.predictions = true;

      try {
        // Calculate pagination
        const skip = (this.page - 1) * this.itemsPerPage;

        // Prepare filter params
        const params = {
          skip,
          limit: this.itemsPerPage,
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
        this.predictions = response.data.predictions;
        this.totalPredictions = response.data.count;
      } catch (error) {
        console.error('Error fetching predictions:', error);
      } finally {
        this.loading.predictions = false;
      }
    },

    async fetchPredictionStats() {
      this.loading.stats = true;

      try {
        const response = await api.get('/predictions/status/accuracy');
        this.predictionStats = response.data;
      } catch (error) {
        console.error('Error fetching prediction stats:', error);
      } finally {
        this.loading.stats = false;
      }
    },

    async refreshPrediction(prediction, closeDialog = false) {
      // Set loading state for specific prediction
      const index = this.predictions.findIndex(p => p.id === prediction.id);
      if (index !== -1) {
        this.$set(this.predictions[index], 'refreshing', true);
      }

      try {
        const response = await api.post(`/predictions/refresh/${prediction.trading_symbol}`);

        // Update prediction in list
        if (index !== -1) {
          this.$set(this.predictions, index, { ...response.data, refreshing: false });
        }

        // Update selected prediction if in dialog
        if (this.selectedPrediction && this.selectedPrediction.id === prediction.id) {
          this.selectedPrediction = { ...response.data };
        }

        // Close dialog if requested
        if (closeDialog) {
          this.showPredictionDialog = false;
        }

        // Show success message
        this.$toast.success('Prediction refreshed successfully');
      } catch (error) {
        console.error('Error refreshing prediction:', error);
        this.$toast.error('Failed to refresh prediction');

        // Reset loading state
        if (index !== -1) {
          this.$set(this.predictions[index], 'refreshing', false);
        }
      }
    },

    viewPredictionDetails(prediction) {
      this.selectedPrediction = prediction;
      this.showPredictionDialog = true;
    },

    viewSymbolDetails(symbol) {
      this.$router.push(`/app/symbols/${symbol}`);
    },

    refreshPredictions() {
      this.fetchPredictions();
      this.fetchPredictionStats();
    },

    resetFilters() {
      this.filters = {
        direction: null,
        verified: null,
        foEligible: null,
        predictionDate: null,
        minConfidence: 0.5
      };

      // Reset to first page and refresh
      this.page = 1;
      this.fetchPredictions();
    },

    applyFilters() {
      // Reset to first page and refresh
      this.page = 1;
      this.fetchPredictions();
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },

    formatDateTime(dateTimeString) {
      if (!dateTimeString) return 'N/A';
      return new Date(dateTimeString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
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
  },

  mounted() {
    this.fetchPredictions();
    this.fetchPredictionStats();
  }
}
</script>

<style lang="postcss" scoped>
.predictions-page {
  @apply w-full flex flex-col gap-6;
}

/* Filter Card */
.filter-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 p-5;
}

.filter-header {
  @apply flex justify-between items-center mb-4;
}

.page-title {
  @apply text-xl font-bold text-gray-800;
}

.filter-form {
  @apply space-y-4;
}

.filter-row {
  @apply flex flex-wrap items-center gap-4;
}

.filter-group {
  @apply min-w-[200px] flex-1;
}

.date-filter {
  @apply min-w-[220px];
}

.confidence-filter {
  @apply flex-grow flex flex-col gap-1 max-w-xl;
}

.confidence-label {
  @apply text-sm font-medium text-gray-700;
}

.filter-actions-right {
  @apply flex items-center gap-2 ml-auto;
}

/* Stats Row */
.stats-row {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4;
}

.stat-card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 p-4 flex items-center;
}

.stat-icon {
  @apply w-12 h-12 rounded-lg flex items-center justify-center mr-4;
}

.bg-primary-light {
  @apply bg-primary bg-opacity-10;
}

.bg-success-light {
  @apply bg-success bg-opacity-10;
}

.bg-error-light {
  @apply bg-error bg-opacity-10;
}

.bg-info-light {
  @apply bg-info bg-opacity-10;
}

.stat-content {
  @apply flex-1;
}

.stat-value {
  @apply text-xl font-semibold;
}

.stat-label {
  @apply text-sm text-gray-500;
}

/* Data Table Card */
.data-table-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden;
}

/* Symbol Cell */
.symbol-cell {
  @apply flex items-center;
}

.symbol {
  @apply font-medium;
}

.view-symbol-btn {
  @apply ml-1 text-gray-400 hover:text-primary;
}

/* Direction Chip */
.direction-chip {
  @apply inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium;
}

.direction-up {
  @apply bg-success bg-opacity-10 text-success;
}

.direction-down {
  @apply bg-error bg-opacity-10 text-error;
}

/* Confidence Bar */
.confidence-bar-container {
  @apply flex items-center gap-2;
}

.confidence-value {
  @apply text-xs font-medium w-10;
}

.confidence-bar {
  @apply h-1.5 bg-gray-200 rounded-full w-16 overflow-hidden;
}

.confidence-bar-fill {
  @apply h-full bg-primary rounded-full;
}

/* Status Chip */
.status-chip {
  @apply text-xs;
}

/* Actions Cell */
.actions-cell {
  @apply flex items-center;
}

/* Empty State */
.empty-state {
  @apply flex flex-col items-center justify-center py-8 text-gray-500;
}

/* Prediction Dialog */
.prediction-dialog {
  @apply bg-white rounded-xl overflow-hidden;
}

.dialog-header {
  @apply flex justify-between items-center px-6 py-4 border-b border-gray-200 bg-gray-50;
}

.dialog-title {
  @apply text-lg font-bold text-gray-800 flex items-center gap-2;
}

.symbol-badge {
  @apply text-sm px-2 py-0.5 bg-primary text-white rounded;
}

.dialog-content {
  @apply p-6;
}

.info-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-4;
}

.info-item {
  @apply bg-gray-50 p-3 rounded-lg border border-gray-100;
}

.info-label {
  @apply text-xs text-gray-500 mb-1;
}

.info-value {
  @apply font-medium;
}

.confidence-display {
  @apply space-y-1;
}

.value-text {
  @apply text-sm font-medium;
}

.prediction-direction-badge {
  @apply inline-flex items-center gap-1 px-3 py-1 rounded-full;
}

.dialog-actions {
  @apply flex justify-end gap-2 p-4 bg-gray-50 border-t border-gray-200;
}
</style>