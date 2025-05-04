<template>
  <div class="symbols-explorer">
    <!-- Header with Search and Filters Bar -->
    <div class="explorer-header-container">
      <div class="explorer-header">
        <div class="header-left">
          <h1 class="page-title">Symbols Explorer</h1>
          <div class="header-stats">
            <div class="stat-pill">
              <span>{{ filteredSymbols.length }}</span> symbols
            </div>
            <div v-if="activeFilter === 'fo'" class="stat-pill accent">
              <v-icon size="x-small">mdi-filter</v-icon>
              <span>F&O only</span>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <v-btn color="primary" variant="tonal" size="small" prepend-icon="mdi-refresh" @click="refreshSymbols" :loading="symbolStore.loading" :disabled="symbolStore.loading">
            Refresh
          </v-btn>
        </div>
      </div>

      <!-- Search & Filter Bar -->
      <div class="search-filter-bar">
        <div class="search-container">
          <v-text-field v-model="searchQuery" placeholder="Search symbols or companies..." variant="outlined" density="compact" hide-details class="search-input" prepend-inner-icon="mdi-magnify" @update:model-value="debouncedSearch" clearable>
            <template #append-inner>
              <v-fade-transition leave-absolute>
                <v-progress-circular v-if="symbolStore.loading" indeterminate color="primary" size="20"></v-progress-circular>
              </v-fade-transition>
            </template>
          </v-text-field>
        </div>
        <div class="filter-container">
          <v-chip-group v-model="activeFilter" mandatory selected-class="filter-selected">
            <v-chip value="all" filter variant="elevated" size="small">All Symbols</v-chip>
            <v-chip value="fo" filter variant="elevated" size="small">F&O Eligible</v-chip>
          </v-chip-group>
        </div>
      </div>
    </div>

    <!-- Main Content: Symbol Cards Grid -->
    <div v-if="!symbolStore.loading || filteredSymbols.length > 0" class="symbols-grid-container">
      <TransitionGroup name="symbols-list" tag="div" class="symbols-grid">
        <div v-for="symbol in paginatedSymbols" :key="symbol.trading_symbol" class="symbol-card" @click="viewSymbolDetails(symbol)">
          <div class="symbol-card-header">
            <div class="symbol-badge" :class="getSymbolBadgeClass(symbol.instrument_type)">
              {{ symbol.trading_symbol.charAt(0) }}
            </div>
            <div class="symbol-info">
              <div class="symbol-name">{{ symbol.trading_symbol }}</div>
              <div class="symbol-exchange">{{ symbol.exchange }}</div>
            </div>
            <div v-if="symbol.fo_eligible" class="fo-badge">F&O</div>
          </div>

          <div class="symbol-card-body">
            <div class="company-name">{{ symbol.name }}</div>
            <div class="symbol-details">
              <div class="detail-item">
                <div class="detail-label">Type</div>
                <v-chip size="x-small" :color="getInstrumentTypeColor(symbol.instrument_type)" text-color="white">
                  {{ symbol.instrument_type }}
                </v-chip>
              </div>
              <div class="detail-item">
                <div class="detail-label">Lot Size</div>
                <div class="detail-value">{{ symbol.lot_size || 'N/A' }}</div>
              </div>
            </div>
          </div>

          <div class="symbol-card-footer">
            <v-btn size="small" variant="text" color="primary" @click.stop="viewPredictions(symbol)">
              <v-icon size="small" class="mr-1">mdi-chart-line</v-icon>
              Predictions
            </v-btn>
            <v-btn size="small" variant="text" @click.stop="viewSymbolDetails(symbol)">
              <v-icon size="small">mdi-information-outline</v-icon>
            </v-btn>
          </div>
        </div>
      </TransitionGroup>

      <!-- Empty State -->
      <div v-if="filteredSymbols.length === 0 && !symbolStore.loading" class="empty-state">
        <div class="empty-state-icon">
          <v-icon size="64" color="grey-lighten-2">mdi-finance</v-icon>
        </div>
        <h3>No symbols found</h3>
        <p>Try adjusting your search criteria or filters</p>
        <v-btn variant="outlined" color="primary" @click="resetFilters">
          Reset Filters
        </v-btn>
      </div>

      <!-- Loading Skeleton -->
      <div v-if="symbolStore.loading && filteredSymbols.length === 0" class="symbols-grid">
        <div v-for="i in 9" :key="i" class="symbol-card skeleton">
          <div class="symbol-card-header">
            <div class="skeleton-badge"></div>
            <div class="skeleton-info">
              <div class="skeleton-line short"></div>
              <div class="skeleton-line shorter"></div>
            </div>
          </div>
          <div class="symbol-card-body">
            <div class="skeleton-line"></div>
            <div class="skeleton-details">
              <div class="skeleton-line short"></div>
              <div class="skeleton-line short"></div>
            </div>
          </div>
          <div class="symbol-card-footer">
            <div class="skeleton-button"></div>
            <div class="skeleton-icon"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination Controls (if needed) -->
    <div v-if="filteredSymbols.length > 0" class="pagination-controls">
      <v-pagination v-model="currentPage" :length="totalPages" :total-visible="7" :disabled="symbolStore.loading"></v-pagination>
    </div>

    <!-- Symbol Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="800">
      <v-card v-if="symbolStore.selectedSymbol" class="symbol-detail-card">
        <v-card-item>
          <div class="symbol-detail-header">
            <div class="symbol-detail-badge" :class="getSymbolBadgeClass(symbolStore.selectedSymbol.instrument_type)">
              {{ symbolStore.selectedSymbol.trading_symbol.charAt(0) }}
            </div>
            <div class="symbol-detail-title">
              <v-card-title class="symbol-detail-name">
                {{ symbolStore.selectedSymbol.trading_symbol }}
                <v-chip v-if="symbolStore.selectedSymbol.fo_eligible" size="small" color="primary" class="ml-2" variant="flat">
                  F&O
                </v-chip>
              </v-card-title>
              <v-card-subtitle>{{ symbolStore.selectedSymbol.name }}</v-card-subtitle>
            </div>
            <v-spacer></v-spacer>
            <v-btn icon variant="text" @click="closeDetailsDialog">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
        </v-card-item>

        <v-divider></v-divider>

        <v-card-text>
          <div class="symbol-detail-content">
            <div class="symbol-detail-grid">
              <div class="detail-grid-item">
                <div class="detail-grid-label">Exchange</div>
                <div class="detail-grid-value">{{ symbolStore.selectedSymbol.exchange }}</div>
              </div>
              <div class="detail-grid-item">
                <div class="detail-grid-label">Security ID</div>
                <div class="detail-grid-value">{{ symbolStore.selectedSymbol.security_id }}</div>
              </div>
              <div class="detail-grid-item">
                <div class="detail-grid-label">Instrument Type</div>
                <div class="detail-grid-value">
                  <v-chip size="small" :color="getInstrumentTypeColor(symbolStore.selectedSymbol.instrument_type)">
                    {{ symbolStore.selectedSymbol.instrument_type }}
                  </v-chip>
                </div>
              </div>
              <div class="detail-grid-item">
                <div class="detail-grid-label">F&O Eligible</div>
                <div class="detail-grid-value">
                  <v-icon v-if="symbolStore.selectedSymbol.fo_eligible" color="success">mdi-check-circle</v-icon>
                  <v-icon v-else color="grey-lighten-1">mdi-minus-circle</v-icon>
                  <span class="ml-1">{{ symbolStore.selectedSymbol.fo_eligible ? 'Yes' : 'No' }}</span>
                </div>
              </div>
              <div class="detail-grid-item">
                <div class="detail-grid-label">Lot Size</div>
                <div class="detail-grid-value">{{ symbolStore.selectedSymbol.lot_size || 'N/A' }}</div>
              </div>
              <div class="detail-grid-item">
                <div class="detail-grid-label">Segment</div>
                <div class="detail-grid-value">{{ symbolStore.selectedSymbol.segment }}</div>
              </div>
              <div class="detail-grid-item">
                <div class="detail-grid-label">Status</div>
                <div class="detail-grid-value">
                  <v-chip size="small" :color="symbolStore.selectedSymbol.active ? 'success' : 'error'" text-color="white">
                    {{ symbolStore.selectedSymbol.active ? 'Active' : 'Inactive' }}
                  </v-chip>
                </div>
              </div>
              <div class="detail-grid-item">
                <div class="detail-grid-label">Added On</div>
                <div class="detail-grid-value">{{ formatDate(symbolStore.selectedSymbol.created_at) }}</div>
              </div>
            </div>
          </div>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="tonal" @click="closeDetailsDialog">
            Close
          </v-btn>
          <v-btn color="primary" @click="viewPredictions(symbolStore.selectedSymbol)">
            View Predictions
            <v-icon class="ml-1">mdi-chart-line</v-icon>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { debounce } from 'lodash-es';
import { useSymbolStore } from '@/store/symbol.store';

export default {
  name: 'SymbolsExplorer',

  data() {
    return {
      symbolStore: useSymbolStore(),
      searchQuery: '',
      activeFilter: 'all',
      showDetailsDialog: false,
      currentPage: 1,
      pageSize: 24, // Number of items per page
      debouncedSearch: null
    };
  },

  computed: {
    filteredSymbols() {
      let result = [...this.symbolStore.symbols];

      // Apply search filter
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(
          symbol =>
            symbol.trading_symbol.toLowerCase().includes(query) ||
            symbol.name.toLowerCase().includes(query)
        );
      }

      // Apply F&O filter
      if (this.activeFilter === 'fo') {
        result = result.filter(symbol => symbol.fo_eligible);
      }

      return result;
    },

    paginatedSymbols() {
      const startIndex = (this.currentPage - 1) * this.pageSize;
      const endIndex = startIndex + this.pageSize;
      return this.filteredSymbols.slice(startIndex, endIndex);
    },

    totalPages() {
      return Math.ceil(this.filteredSymbols.length / this.pageSize);
    }
  },

  methods: {
    async refreshSymbols() {
      try {
        await this.symbolStore.fetchSymbols();
        this.resetFilters();
      } catch (error) {
        console.error('Error fetching symbols:', error);
      }
    },

    resetFilters() {
      this.searchQuery = '';
      this.activeFilter = 'all';
      this.currentPage = 1;
    },

    viewSymbolDetails(symbol) {
      this.symbolStore.setSelectedSymbol(symbol);
      this.showDetailsDialog = true;
    },

    closeDetailsDialog() {
      this.showDetailsDialog = false;
    },

    viewPredictions(symbol) {
      this.$router.push({
        name: 'SymbolDetail',
        params: { symbol: symbol.trading_symbol }
      });
    },

    getInstrumentTypeColor(type) {
      const colorMap = {
        'EQ': 'blue',
        'FUT': 'purple',
        'OPT': 'orange',
        'ETF': 'green',
        'INDEX': 'cyan'
      };
      return colorMap[type] || 'grey';
    },

    getSymbolBadgeClass(type) {
      const classMap = {
        'EQ': 'badge-eq',
        'FUT': 'badge-fut',
        'OPT': 'badge-opt',
        'ETF': 'badge-etf',
        'INDEX': 'badge-index'
      };
      return classMap[type] || '';
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
  },

  created() {
    // Create debounced search function
    this.debouncedSearch = debounce(() => {
      this.currentPage = 1; // Reset to first page when searching
    }, 300);
  },

  mounted() {
    this.refreshSymbols();
  },

  beforeUnmount() {
    // Optional: Clean up
    this.debouncedSearch.cancel();
  }
};
</script>

<style lang="postcss" scoped>
.symbols-explorer {
  @apply w-full flex flex-col gap-6;
}

/* Header Styles */
.explorer-header-container {
  @apply sticky top-0 z-10 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden mb-2;
}

.explorer-header {
  @apply flex flex-wrap justify-between items-center p-4 gap-4;
}

.header-left {
  @apply flex flex-col;
}

.page-title {
  @apply text-2xl font-bold mb-1 text-gray-800;
}

.header-stats {
  @apply flex gap-2;
}

.stat-pill {
  @apply flex items-center gap-1 px-2 py-0.5 bg-gray-100 rounded-full text-xs font-medium text-gray-600;
}

.stat-pill.accent {
  @apply bg-primary bg-opacity-10 text-primary;
}

.header-actions {
  @apply flex items-center gap-2;
}

.search-filter-bar {
  @apply flex flex-col sm:flex-row items-center gap-4 px-4 py-3 border-t border-gray-200 bg-gray-50;
}

.search-container {
  @apply w-full sm:w-80 flex-shrink-0;
}

.search-input {
  @apply rounded-lg;
}

.filter-container {
  @apply w-full flex-grow flex justify-start sm:justify-end items-center;
}

.filter-selected {
  @apply bg-primary text-white;
}

/* Grid Styles */
.symbols-grid-container {
  @apply relative min-h-[400px];
}

.symbols-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4;
}

.symbol-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden flex flex-col transition-all duration-200 hover:shadow-md hover:border-primary hover:border-opacity-50 cursor-pointer;
}

.symbol-card-header {
  @apply flex items-center gap-3 p-3 bg-gray-50 border-b border-gray-200;
}

.symbol-badge {
  @apply w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg text-white bg-primary;
}

.badge-eq {
  @apply bg-blue-600;
}

.badge-fut {
  @apply bg-purple-600;
}

.badge-opt {
  @apply bg-orange-500;
}

.badge-etf {
  @apply bg-green-600;
}

.badge-index {
  @apply bg-cyan-600;
}

.symbol-info {
  @apply flex-grow;
}

.symbol-name {
  @apply font-bold text-gray-800;
}

.symbol-exchange {
  @apply text-xs text-gray-500;
}

.fo-badge {
  @apply px-2 py-0.5 bg-primary bg-opacity-10 text-primary rounded text-xs font-medium;
}

.symbol-card-body {
  @apply p-3 flex-grow flex flex-col;
}

.company-name {
  @apply text-sm mb-3 line-clamp-2 h-10;
}

.symbol-details {
  @apply grid grid-cols-2 gap-2 mt-auto;
}

.detail-item {
  @apply flex flex-col;
}

.detail-label {
  @apply text-xs text-gray-500 mb-1;
}

.detail-value {
  @apply text-sm font-medium;
}

.symbol-card-footer {
  @apply flex justify-between items-center p-2 border-t border-gray-200;
}

/* Empty State */
.empty-state {
  @apply flex flex-col items-center justify-center py-12 gap-3 text-center;
}

.empty-state-icon {
  @apply mb-2;
}

/* Pagination */
.pagination-controls {
  @apply flex justify-center my-6;
}

/* Symbol Detail Dialog */
.symbol-detail-card {
  @apply rounded-xl overflow-hidden;
}

.symbol-detail-header {
  @apply flex items-center gap-4;
}

.symbol-detail-badge {
  @apply w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xl text-white bg-primary;
}

.symbol-detail-title {
  @apply flex flex-col justify-center;
}

.symbol-detail-name {
  @apply flex items-center text-xl font-bold;
}

.symbol-detail-content {
  @apply py-4;
}

.symbol-detail-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6;
}

.detail-grid-item {
  @apply flex flex-col gap-1;
}

.detail-grid-label {
  @apply text-sm text-gray-500;
}

.detail-grid-value {
  @apply font-medium flex items-center;
}

/* Skeleton Loading */
.skeleton {
  @apply animate-pulse;
}

.skeleton-badge {
  @apply w-10 h-10 rounded-lg bg-gray-200;
}

.skeleton-info {
  @apply flex-1 flex flex-col gap-2;
}

.skeleton-line {
  @apply h-4 bg-gray-200 rounded;
}

.skeleton-line.short {
  @apply w-2/3;
}

.skeleton-line.shorter {
  @apply w-1/3;
}

.skeleton-details {
  @apply grid grid-cols-2 gap-2 mt-3;
}

.skeleton-button {
  @apply h-8 w-24 rounded bg-gray-200;
}

.skeleton-icon {
  @apply h-8 w-8 rounded bg-gray-200;
}

/* Transitions */
.symbols-list-enter-active,
.symbols-list-leave-active {
  transition: all 0.3s ease;
}

.symbols-list-enter-from,
.symbols-list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>