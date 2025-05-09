<template>
  <div class="predictions-page">
    <!-- Header with filters -->
    <div class="filter-card">
      <div class="filter-header">
        <h1 class="page-title">Predictions</h1>
        <div class="filter-actions">
          <v-btn color="primary" size="small" prepend-icon="mdi-refresh" @click="refreshPredictions" :loading="predictionStore.loading.predictions">
            Refresh
          </v-btn>
        </div>
      </div>

      <div class="filter-form">
        <div class="filter-row">
          <div class="filter-group">
            <v-select v-model="direction" label="Direction" :items="directionOptions" density="compact" variant="outlined" hide-details class="filter-input"></v-select>
          </div>
          <div class="filter-group">
            <v-select v-model="verified" label="Status" :items="verificationOptions" density="compact" variant="outlined" hide-details class="filter-input"></v-select>
          </div>
          <div class="filter-group">
            <v-select v-model="foEligible" label="F&O Eligible" :items="foEligibleOptions" density="compact" variant="outlined" hide-details class="filter-input"></v-select>
          </div>
          <div class="filter-group date-filter">
            <v-menu v-model="datePickerOpen" :close-on-content-click="false" transition="scale-transition" min-width="auto">
              <template v-slot:activator="{ props }">
                <v-text-field v-model="dateFilterDisplay" label="Prediction Date" prepend-inner-icon="mdi-calendar" readonly variant="outlined" density="compact" hide-details v-bind="props" class="filter-input" clearable @click:clear="predictionDate = null"></v-text-field>
              </template>
              <v-date-picker v-model="predictionDate" @update:model-value="datePickerOpen = false"></v-date-picker>
            </v-menu>
          </div>
        </div>

        <div class="filter-row">
          <div class="confidence-filter">
            <div class="confidence-label">Confidence Threshold: {{ minConfidence * 100 }}%</div>
            <v-slider v-model="minConfidence" min="0" max="1" step="0.05" thumb-label :thumb-size="20" hide-details density="compact" color="primary" track-color="primary-lighten-3" :thumb-label-formatter="val => Math.round(val * 100) + '%'"></v-slider>
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
          <div class="stat-value">{{ predictionStore.formatPercentage(predictionStore.stats.accuracy) }}</div>
          <div class="stat-label">Overall Accuracy</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-success-light">
          <v-icon color="success">mdi-arrow-up-bold</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ predictionStore.formatPercentage(predictionStore.stats.upAccuracy) }}</div>
          <div class="stat-label">UP Accuracy</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-error-light">
          <v-icon color="error">mdi-arrow-down-bold</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ predictionStore.formatPercentage(predictionStore.stats.downAccuracy) }}</div>
          <div class="stat-label">DOWN Accuracy</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon bg-info-light">
          <v-icon color="info">mdi-calendar-check</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ predictionStore.stats.avgDaysToFulfill ? predictionStore.stats.avgDaysToFulfill.toFixed(1) : 'N/A' }}</div>
          <div class="stat-label">Avg. Days to Verify</div>
        </div>
      </div>
    </div>

    <!-- Predictions Data Table -->
    <div class="data-table-card">
      <v-data-table :headers="tableHeaders" :items="predictionStore.predictions" :loading="predictionStore.loading.predictions" :items-per-page="itemsPerPage" :page="page" :server-items-length="predictionStore.pagination.totalPredictions" @update:page="page = $event" @update:items-per-page="itemsPerPage = $event" class="predictions-table" density="comfortable">
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
            <td>{{ predictionStore.formatDate(item.date) }}</td>

            <!-- Direction prediction column -->
            <td>
              <div v-if="item.direction_prediction" class="direction-chip" :class="predictionStore.getDirectionClass(item.direction_prediction)">
                <v-icon size="x-small">{{ predictionStore.getDirectionIcon(item.direction_prediction) }}</v-icon>
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
              <div v-if="item.actual_direction" class="direction-chip" :class="predictionStore.getDirectionClass(item.actual_direction)">
                <v-icon size="x-small">{{ predictionStore.getDirectionIcon(item.actual_direction) }}</v-icon>
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
      <div v-if="predictionStore.selectedPrediction" class="prediction-dialog">
        <div class="dialog-header">
          <h2 class="dialog-title">
            Prediction Details
            <span class="symbol-badge">{{ predictionStore.selectedPrediction.trading_symbol }}</span>
          </h2>
          <v-btn icon="mdi-close" variant="text" @click="closePredictionDialog"></v-btn>
        </div>

        <div class="dialog-content">
          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">Prediction Date</div>
              <div class="info-value">{{ predictionStore.formatDate(predictionStore.selectedPrediction.date) }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Strong Move Confidence</div>
              <div class="info-value confidence-display">
                <div class="value-text">{{ (predictionStore.selectedPrediction.strong_move_confidence * 100).toFixed(1) }}%</div>
                <v-progress-linear :model-value="predictionStore.selectedPrediction.strong_move_confidence * 100" height="8" rounded color="primary"></v-progress-linear>
              </div>
            </div>

            <div class="info-item" v-if="predictionStore.selectedPrediction.direction_prediction">
              <div class="info-label">Direction Prediction</div>
              <div class="info-value">
                <div class="prediction-direction-badge" :class="predictionStore.getDirectionClass(predictionStore.selectedPrediction.direction_prediction)">
                  <v-icon size="small">{{ predictionStore.getDirectionIcon(predictionStore.selectedPrediction.direction_prediction) }}</v-icon>
                  {{ predictionStore.selectedPrediction.direction_prediction }}
                </div>
              </div>
            </div>

            <div class="info-item" v-if="predictionStore.selectedPrediction.direction_confidence">
              <div class="info-label">Direction Confidence</div>
              <div class="info-value confidence-display">
                <div class="value-text">{{ (predictionStore.selectedPrediction.direction_confidence * 100).toFixed(1) }}%</div>
                <v-progress-linear :model-value="predictionStore.selectedPrediction.direction_confidence * 100" height="8" rounded :color="predictionStore.selectedPrediction.direction_prediction === 'UP' ? 'success' : 'error'"></v-progress-linear>
              </div>
            </div>

            <div class="info-item">
              <div class="info-label">Verification Status</div>
              <div class="info-value">
                <v-chip v-if="predictionStore.selectedPrediction.verified !== null" :color="predictionStore.selectedPrediction.verified ? 'success' : 'error'" size="small" text-color="white">
                  {{ predictionStore.selectedPrediction.verified ? 'Verified Success' : 'Verified Failure' }}
                </v-chip>
                <v-chip v-else color="warning" size="small" variant="outlined">
                  Pending Verification
                </v-chip>
              </div>
            </div>

            <div class="info-item" v-if="predictionStore.selectedPrediction.actual_direction">
              <div class="info-label">Actual Direction</div>
              <div class="info-value">
                <div class="prediction-direction-badge" :class="predictionStore.getDirectionClass(predictionStore.selectedPrediction.actual_direction)">
                  <v-icon size="small">{{ predictionStore.getDirectionIcon(predictionStore.selectedPrediction.actual_direction) }}</v-icon>
                  {{ predictionStore.selectedPrediction.actual_direction }}
                </div>
              </div>
            </div>

            <div class="info-item" v-if="predictionStore.selectedPrediction.actual_move_percent !== null">
              <div class="info-label">Actual Move Percent</div>
              <div class="info-value">{{ predictionStore.selectedPrediction.actual_move_percent.toFixed(2) }}%</div>
            </div>

            <div class="info-item" v-if="predictionStore.selectedPrediction.days_to_fulfill !== null">
              <div class="info-label">Days to Fulfill</div>
              <div class="info-value">{{ predictionStore.selectedPrediction.days_to_fulfill }} days</div>
            </div>

            <div class="info-item" v-if="predictionStore.selectedPrediction.verification_date">
              <div class="info-label">Verification Date</div>
              <div class="info-value">{{ predictionStore.formatDate(predictionStore.selectedPrediction.verification_date) }}</div>
            </div>

            <div class="info-item">
              <div class="info-label">Created At</div>
              <div class="info-value">{{ predictionStore.formatDateTime(predictionStore.selectedPrediction.created_at) }}</div>
            </div>
          </div>
        </div>

        <div class="dialog-actions">
          <v-btn variant="outlined" @click="closePredictionDialog">
            Close
          </v-btn>
          <v-btn color="primary" prepend-icon="mdi-refresh" @click="refreshPrediction(predictionStore.selectedPrediction, true)">
            Refresh Prediction
          </v-btn>
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script>
import { usePredictionStore } from '@/store/prediction.store'

export default {
  name: 'PredictionsView',

  data() {
    return {
      // Store instance
      predictionStore: usePredictionStore(),

      // UI state
      datePickerOpen: false,
      showPredictionDialog: false,

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
    // Computed properties that proxy to store state
    direction: {
      get() { return this.predictionStore.filters.direction },
      set(value) { this.predictionStore.setFilter('direction', value) }
    },
    verified: {
      get() { return this.predictionStore.filters.verified },
      set(value) { this.predictionStore.setFilter('verified', value) }
    },
    foEligible: {
      get() { return this.predictionStore.filters.foEligible },
      set(value) { this.predictionStore.setFilter('foEligible', value) }
    },
    predictionDate: {
      get() { return this.predictionStore.filters.predictionDate },
      set(value) { this.predictionStore.setFilter('predictionDate', value) }
    },
    minConfidence: {
      get() { return this.predictionStore.filters.minConfidence },
      set(value) { this.predictionStore.setFilter('minConfidence', value) }
    },
    page: {
      get() { return this.predictionStore.pagination.page },
      set(value) { this.predictionStore.setPagination(value) }
    },
    itemsPerPage: {
      get() { return this.predictionStore.pagination.itemsPerPage },
      set(value) { this.predictionStore.setPagination(null, value) }
    },
    dateFilterDisplay() {
      return this.predictionStore.formattedDateFilter;
    }
  },

  watch: {
    // Watch for page changes to fetch new data
    'predictionStore.pagination.page'() {
      this.predictionStore.fetchPredictions();
    },
    'predictionStore.pagination.itemsPerPage'() {
      this.predictionStore.fetchPredictions();
    }
  },

  methods: {
    refreshPredictions() {
      this.predictionStore.fetchPredictionStats();
      this.predictionStore.fetchPredictions();
    },

    resetFilters() {
      this.predictionStore.resetFilters();
      this.predictionStore.fetchPredictions();
    },

    applyFilters() {
      this.predictionStore.setPagination(1); // Reset to first page
      this.predictionStore.fetchPredictions();
    },

    viewPredictionDetails(prediction) {
      this.predictionStore.setSelectedPrediction(prediction);
      this.showPredictionDialog = true;
    },

    closePredictionDialog() {
      this.showPredictionDialog = false;
      this.predictionStore.clearSelectedPrediction();
    },

    viewSymbolDetails(symbol) {
      this.$router.push(`/app/symbols/${symbol}`);
    },

    async refreshPrediction(prediction, closeDialog = false) {
      try {
        await this.predictionStore.refreshPrediction(prediction);

        // Show success message
        this.$toast.success('Prediction refreshed successfully');

        // Close dialog if requested
        if (closeDialog) {
          this.closePredictionDialog();
        }
      } catch (error) {
        this.$toast.error('Failed to refresh prediction');
      }
    }
  },

  mounted() {
    this.refreshPredictions();
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