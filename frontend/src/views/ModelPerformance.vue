<template>
  <div class="model-performance">
    <!-- Header with filters -->
    <div class="filter-card">
      <div class="filter-header">
        <h1 class="page-title">Model Performance</h1>
        <div class="filter-actions">
          <v-btn color="primary" size="small" prepend-icon="mdi-refresh" @click="refreshModels" :loading="modelStore.loading">
            Refresh
          </v-btn>
        </div>
      </div>

      <div class="filter-form">
        <div class="filter-row">
          <div class="filter-group">
            <v-select v-model="filters.metric" label="Ranking Metric" :items="metricOptions" density="compact" variant="outlined" hide-details class="filter-input text-sm"></v-select>
          </div>
          <div class="filter-group">
            <v-select v-model="filters.topN" label="Top Models" :items="topNOptions" density="compact" variant="outlined" hide-details class="filter-input text-sm"></v-select>
          </div>
          <div class="filter-group">
            <v-select v-model="filters.foEligible" label="F&O Eligible" :items="foEligibleOptions" density="compact" variant="outlined" hide-details class="filter-input text-sm"></v-select>
          </div>
          <div class="filter-actions-right">
            <v-btn color="primary" size="small" @click="applyFilters">
              Apply Filters
            </v-btn>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Models Performance Chart -->
    <div class="chart-card">
      <div class="card-header">
        <h2 class="card-title">Top Models by {{ selectedChartView }}</h2>
        <div class="time-selector">
          <v-btn-toggle v-model="selectedChartView" color="primary" density="comfortable" variant="outlined">
            <v-btn value="f1_score" size="small">F1 Score</v-btn>
            <v-btn value="accuracy" size="small">Accuracy</v-btn>
          </v-btn-toggle>
        </div>
      </div>
      <div class="chart-container" v-if="!modelStore.loading">
        <v-chart class="chart" :option="modelStore.performanceChartOption" autoresize />
      </div>
      <div v-else class="chart-loading">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>
    </div>

    <!-- Models Comparison Table -->
    <div class="models-table-card">
      <div class="table-card-header">
        <h2 class="card-title">Models Comparison</h2>
        <div class="card-actions">
          <v-btn size="small" variant="text" icon="mdi-refresh" @click="refreshModels"></v-btn>
          <v-btn size="small" variant="text" icon="mdi-download" @click="downloadModelData"></v-btn>
        </div>
      </div>

      <v-data-table :headers="tableHeaders" :items="modelStore.topModels" :loading="modelStore.loading" density="comfortable" hover class="model-table">
        <template #[`item.trading_symbol`]="{ item }">
          <div class="symbol-cell">
            <span class="symbol">{{ item.trading_symbol }}</span>
            <v-btn variant="text" size="x-small" density="compact" icon="mdi-open-in-new" @click="viewSymbolDetails(item.trading_symbol)" class="view-symbol-btn"></v-btn>
          </div>
        </template>

        <template #[`item.accuracy`]="{ item }">
          <div class="metric-cell">
            <div class="metric-value">{{ modelStore.formatPercentage(item.accuracy) }}</div>
            <div class="metric-bar-container">
              <div class="metric-bar-bg">
                <div class="metric-bar-fill bg-primary" :style="{ width: `${item.accuracy * 100}%` }"></div>
              </div>
            </div>
          </div>
        </template>

        <template #[`item.precision`]="{ item }">
          <div class="metric-cell">
            <div class="metric-value">{{ modelStore.formatPercentage(item.precision) }}</div>
            <div class="metric-bar-container">
              <div class="metric-bar-bg">
                <div class="metric-bar-fill bg-info" :style="{ width: `${item.precision * 100}%` }"></div>
              </div>
            </div>
          </div>
        </template>

        <template #[`item.recall`]="{ item }">
          <div class="metric-cell">
            <div class="metric-value">{{ modelStore.formatPercentage(item.recall) }}</div>
            <div class="metric-bar-container">
              <div class="metric-bar-bg">
                <div class="metric-bar-fill bg-success" :style="{ width: `${item.recall * 100}%` }"></div>
              </div>
            </div>
          </div>
        </template>

        <template #[`item.f1_score`]="{ item }">
          <div class="metric-cell">
            <div class="metric-value">{{ modelStore.formatPercentage(item.f1_score) }}</div>
            <div class="metric-bar-container">
              <div class="metric-bar-bg">
                <div class="metric-bar-fill bg-warning" :style="{ width: `${item.f1_score * 100}%` }"></div>
              </div>
            </div>
          </div>
        </template>

        <template #[`item.evaluation_date`]="{ item }">
          {{ modelStore.formatDate(item.evaluation_date) }}
        </template>

        <template #[`item.actions`]="{ item }">
          <div class="actions-cell">
            <v-btn size="small" variant="text" icon="mdi-chart-line" @click="viewModelHistory(item.trading_symbol)"></v-btn>
            <v-btn size="small" variant="text" icon="mdi-refresh" @click="retrainModel(item.trading_symbol)" :loading="item.retraining"></v-btn>
          </div>
        </template>
      </v-data-table>
    </div>

    <!-- Model History Dialog -->
    <v-dialog v-model="showHistoryDialog" max-width="800">
      <div v-if="modelStore.selectedModelHistory.length" class="history-dialog">
        <div class="dialog-header">
          <h2 class="dialog-title">
            Performance History
            <span class="symbol-badge">{{ modelStore.selectedModelSymbol }}</span>
          </h2>
          <v-btn icon="mdi-close" variant="text" @click="showHistoryDialog = false"></v-btn>
        </div>

        <div class="dialog-content">
          <div class="history-chart-container">
            <v-chart v-if="modelStore.historyChartOption" class="history-chart" :option="modelStore.historyChartOption" autoresize />
            <div v-else class="chart-loading">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>
          </div>

          <div class="history-table">
            <v-data-table :headers="historyTableHeaders" :items="modelStore.selectedModelHistory" density="compact" class="mt-4">
              <template #[`item.accuracy`]="{ item }">
                {{ modelStore.formatPercentage(item.accuracy) }}
              </template>
              <template #[`item.precision`]="{ item }">
                {{ modelStore.formatPercentage(item.precision) }}
              </template>
              <template #[`item.recall`]="{ item }">
                {{ modelStore.formatPercentage(item.recall) }}
              </template>
              <template #[`item.f1_score`]="{ item }">
                {{ modelStore.formatPercentage(item.f1_score) }}
              </template>
              <template #[`item.evaluation_date`]="{ item }">
                {{ modelStore.formatDate(item.evaluation_date) }}
              </template>
              <template #[`item.training_date`]="{ item }">
                {{ modelStore.formatDate(item.training_date) }}
              </template>
            </v-data-table>
          </div>
        </div>

        <div class="dialog-actions">
          <v-btn variant="outlined" @click="showHistoryDialog = false">
            Close
          </v-btn>
          <v-btn color="primary" prepend-icon="mdi-refresh" @click="retrainModel(modelStore.selectedModelSymbol)">
            Retrain Model
          </v-btn>
        </div>
      </div>
    </v-dialog>
  </div>
</template>

<script>
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { BarChart, LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components';
import VChart from 'vue-echarts';
import { useModelStore } from '@/store/model.store';

// Register ECharts components
use([CanvasRenderer, BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent]);

export default {
  name: 'ModelPerformance',
  components: {
    VChart
  },
  data() {
    return {
      modelStore: useModelStore(),
      showHistoryDialog: false,
      selectedChartView: 'f1_score',

      // Filters
      filters: {
        metric: 'f1_score',
        topN: 10,
        foEligible: true
      },

      // Options for filters
      metricOptions: [
        { title: 'F1 Score', value: 'f1_score' },
        { title: 'Accuracy', value: 'accuracy' },
        { title: 'Precision', value: 'precision' },
        { title: 'Recall', value: 'recall' }
      ],
      topNOptions: [
        { title: 'Top 5', value: 5 },
        { title: 'Top 10', value: 10 },
        { title: 'Top 20', value: 20 },
        { title: 'Top 50', value: 50 }
      ],
      foEligibleOptions: [
        { title: 'All Models', value: false },
        { title: 'F&O Eligible Only', value: true }
      ],

      // Table headers
      tableHeaders: [
        { title: 'Symbol', key: 'trading_symbol', width: '120px' },
        { title: 'Accuracy', key: 'accuracy', width: '140px' },
        { title: 'Precision', key: 'precision', width: '140px' },
        { title: 'Recall', key: 'recall', width: '140px' },
        { title: 'F1 Score', key: 'f1_score', width: '140px' },
        { title: 'Success Count', key: 'successful_count', width: '100px' },
        { title: 'Total Count', key: 'predictions_count', width: '100px' },
        { title: 'Last Evaluated', key: 'evaluation_date', width: '120px' },
        { title: 'Actions', key: 'actions', width: '100px', sortable: false }
      ],

      // History table headers
      historyTableHeaders: [
        { title: 'Evaluation Date', key: 'evaluation_date', width: '120px' },
        { title: 'Training Date', key: 'training_date', width: '120px' },
        { title: 'Accuracy', key: 'accuracy', width: '100px' },
        { title: 'Precision', key: 'precision', width: '100px' },
        { title: 'Recall', key: 'recall', width: '100px' },
        { title: 'F1 Score', key: 'f1_score', width: '100px' },
        { title: 'Successful', key: 'successful_count', width: '100px' },
        { title: 'Predictions', key: 'predictions_count', width: '100px' }
      ]
    };
  },
  watch: {
    selectedChartView() {
      // This updates the chart when the view changes - the performanceChartOption getter will recompute
      this.modelStore.$patch({ selectedMetric: this.selectedChartView });
    }
  },
  methods: {
    refreshModels() {
      return this.modelStore.fetchModelPerformance(
        this.filters.topN,
        this.filters.metric,
        this.filters.foEligible
      );
    },

    applyFilters() {
      this.refreshModels();
    },

    async viewModelHistory(symbol) {
      this.showHistoryDialog = true;
      await this.modelStore.fetchModelHistory(symbol);
    },

    async retrainModel(symbol) {
      try {
        await this.modelStore.retrainModel(symbol);
        this.$toast.success(`Retraining started for ${symbol}`);

        // If dialog is open, close it
        if (this.showHistoryDialog && this.modelStore.selectedModelSymbol === symbol) {
          this.showHistoryDialog = false;
        }
      } catch (error) {
        this.$toast.error(`Failed to retrain model for ${symbol}`);
      }
    },

    viewSymbolDetails(symbol) {
      this.$router.push(`/app/symbols/${symbol}`);
    },

    downloadModelData() {
      const csvContent = this.modelStore.exportModelData(this.modelStore.topModels);
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `model_performance_${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  },
  mounted() {
    this.refreshModels();
  }
};
</script>

<style lang="postcss" scoped>
.model-performance {
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
  @apply min-w-[150px] flex-1;
}

.filter-actions-right {
  @apply ml-auto;
}

/* Chart Card */
.chart-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 p-5;
}

.card-header {
  @apply flex justify-between items-center mb-4;
}

.card-title {
  @apply text-lg font-medium text-gray-800;
}

.chart-container {
  @apply h-80;
}

.chart {
  @apply w-full h-full;
}

.chart-loading {
  @apply flex justify-center items-center h-full;
}

/* Models Table */
.models-table-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden;
}

.table-card-header {
  @apply flex justify-between items-center p-5 border-b border-gray-200;
}

.card-actions {
  @apply flex items-center;
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

/* Metric Cell */
.metric-cell {
  @apply flex flex-col;
}

.metric-value {
  @apply text-xs font-medium mb-1;
}

.metric-bar-container {
  @apply w-full;
}

.metric-bar-bg {
  @apply h-1.5 bg-gray-200 rounded-full overflow-hidden;
}

.metric-bar-fill {
  @apply h-full rounded-full;
}

/* Actions Cell */
.actions-cell {
  @apply flex items-center;
}

/* History Dialog */
.history-dialog {
  @apply bg-white rounded-xl overflow-hidden;
}

.dialog-header {
  @apply flex justify-between items-center px-6 py-4 border-b border-gray-200 bg-gray-50;
}

.dialog-title {
  @apply text-lg font-medium flex items-center;
}

.symbol-badge {
  @apply ml-2 px-2 py-0.5 bg-primary text-white text-sm rounded;
}

.dialog-content {
  @apply p-5 flex flex-col gap-4;
}

.history-chart-container {
  @apply h-80;
}

.history-chart {
  @apply w-full h-full;
}

.dialog-actions {
  @apply flex justify-end gap-2 p-4 bg-gray-50 border-t border-gray-200;
}

/* Make form inputs smaller text */
:deep(.v-field__input) {
  @apply text-sm;
}

:deep(.v-label) {
  @apply text-sm;
}
</style>