// src/views/SymbolDetail.vue
<template>
  <div v-if="!loadingSymbol && symbolData" class="symbol-details">
    <!-- Header Section with Symbol Info -->
    <SymbolHeader :symbol="symbolData" />

    <!-- Main Content Tabs -->
    <div class="tab-container">
      <v-tabs v-model="activeTab" show-arrows color="primary" class="mb-4">
        <v-tab value="overview">Overview</v-tab>
        <v-tab value="historical">Historical Data</v-tab>
        <v-tab value="predictions">Predictions</v-tab>
        <v-tab value="models">Model Performance</v-tab>
        <v-tab value="technical">Technical Analysis</v-tab>
        <v-tab value="comparison">Comparison</v-tab>
      </v-tabs>

      <v-window v-model="activeTab" class="tab-content">
        <!-- Overview Tab -->
        <v-window-item value="overview">
          <OverviewTab :symbol="symbolData" @change-tab="activeTab = $event" />
        </v-window-item>

        <!-- Historical Data Tab -->
        <v-window-item value="historical">
          <HistoricalDataTab :symbol="symbolData" />
        </v-window-item>

        <!-- Predictions Tab -->
        <v-window-item value="predictions">
          <PredictionsTab :symbol="symbolData" />
        </v-window-item>

        <!-- Model Performance Tab -->
        <v-window-item value="models">
          <ModelPerformanceTab :symbol="symbolData" />
        </v-window-item>

        <!-- Technical Analysis Tab -->
        <v-window-item value="technical">
          <TechnicalAnalysisTab :symbol="symbolData" />
        </v-window-item>

        <!-- Comparison Tab -->
        <v-window-item value="comparison">
          <ComparisonTab :symbol="symbolData" />
        </v-window-item>
      </v-window>
    </div>
  </div>

  <!-- Loading State -->
  <div v-else class="symbol-details">
    <div class="overview-card animate-pulse">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 bg-gray-200 rounded-lg"></div>
        <div class="flex-1">
          <div class="h-6 bg-gray-200 rounded w-24 mb-2"></div>
          <div class="h-4 bg-gray-200 rounded w-48"></div>
        </div>
      </div>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
        <div v-for="i in 4" :key="i" class="h-12 bg-gray-200 rounded"></div>
      </div>
    </div>

    <div class="tab-container mt-6">
      <div class="h-10 bg-gray-200 rounded mb-4"></div>
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="h-72 bg-gray-200 rounded lg:col-span-2"></div>
        <div class="h-72 bg-gray-200 rounded"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { useSymbolStore } from '@/store/symbol.store';

// Import components
import SymbolHeader from '@/components/symbols/SymbolHeader.vue';
import OverviewTab from '@/components/symbols/SymbolOverview.vue';
import HistoricalDataTab from '@/components/symbols/SymbolHistorical.vue';
import PredictionsTab from '@/components/symbols/SymbolPredictions.vue';
import ModelPerformanceTab from '@/components/symbols/SymbolModels.vue';
import TechnicalAnalysisTab from '@/components/symbols/SymbolTechnical.vue';
import ComparisonTab from '@/components/symbols/SymbolComparision.vue';

export default {
  name: 'SymbolDetails',
  components: {
    SymbolHeader,
    OverviewTab,
    HistoricalDataTab,
    PredictionsTab,
    ModelPerformanceTab,
    TechnicalAnalysisTab,
    ComparisonTab
  },
  data() {
    return {
      symbolStore: useSymbolStore(),
      loadingSymbol: true,
      symbolData: null,
      activeTab: 'overview'
    };
  },
  computed: {
    // Get symbol from route
    symbolId() {
      return this.$route.params.symbol;
    }
  },
  methods: {
    async loadSymbolData() {
      this.loadingSymbol = true;
      try {
        await this.symbolStore.fetchSymbolByTradingSymbol(this.symbolId);
        this.symbolData = this.symbolStore.selectedSymbol;
      } catch (error) {
        console.error('Error loading symbol data:', error);
      } finally {
        this.loadingSymbol = false;
      }
    }
  },
  mounted() {
    this.loadSymbolData();
  },
  // If symbol route param changes, reload data
  watch: {
    symbolId(newSymbol) {
      if (newSymbol) {
        this.loadSymbolData();
      }
    }
  }
};
</script>

<style lang="postcss" scoped>
.symbol-details {
  @apply w-full flex flex-col gap-6;
}

.overview-card {
  @apply bg-white rounded-xl p-5 shadow-sm border border-gray-200;
}

.tab-container {
  @apply bg-white rounded-xl p-5 shadow-sm border border-gray-200;
}

/* Reduce tab font size */
:deep(.v-tab) {
  @apply text-xs font-medium;
}
</style>