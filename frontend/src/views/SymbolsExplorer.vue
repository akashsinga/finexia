<template>
  <div class="symbols-explorer">
    <!-- Header with search and filters -->
    <div class="explorer-header">
      <div class="header-container">
        <div class="header-left">
          <h1 class="page-title">Symbols Explorer</h1>
          <div class="header-stats">
            <div class="stat-badge">
              <span class="stat-count">{{ filteredSymbols.length }}</span>
              <span class="stat-label">symbols</span>
            </div>
            <div v-if="activeFilter === 'fo'" class="fo-badge">
              <v-icon size="x-small">mdi-filter</v-icon>
              <span>F&O only</span>
            </div>
          </div>
        </div>

        <div class="search-area">
          <div class="search-field">
            <v-text-field v-model="searchQuery" placeholder="Search symbols or companies..." variant="outlined" density="compact" hide-details prepend-inner-icon="mdi-magnify" @update:model-value="debouncedSearch" clearable>
              <template #append-inner>
                <v-fade-transition leave-absolute>
                  <v-progress-circular v-if="symbolStore.loading" indeterminate color="primary" size="20"></v-progress-circular>
                </v-fade-transition>
              </template>
            </v-text-field>
          </div>

          <div class="filter-actions">
            <v-chip-group v-model="activeFilter" mandatory selected-class="filter-selected">
              <v-chip value="all" filter variant="elevated" size="small" class="filter-chip">All</v-chip>
              <v-chip value="fo" filter variant="elevated" size="small" class="filter-chip">F&O</v-chip>
            </v-chip-group>

            <v-btn color="primary" variant="tonal" prepend-icon="mdi-refresh" @click="refreshSymbols" :loading="symbolStore.loading" :disabled="symbolStore.loading" class="refresh-btn">
              Refresh
            </v-btn>
          </div>
        </div>
      </div>
    </div>

    <!-- Symbol Cards Grid -->
    <div v-if="!symbolStore.loading || filteredSymbols.length > 0" class="grid-container">
      <TransitionGroup name="symbols-list" tag="div" class="symbols-grid">
        <div v-for="symbol in paginatedSymbols" :key="symbol.trading_symbol" class="symbol-card" @click="viewSymbolDetails(symbol)">

          <!-- Colored stripe for instrument type -->
          <div class="card-stripe" :class="getSymbolBadgeClass(symbol.instrument_type)"></div>

          <div class="card-content">
            <!-- Header with symbol and type -->
            <div class="card-header">
              <div class="symbol-title">
                <h3 class="symbol-name">{{ symbol.trading_symbol }}</h3>
                <div v-if="symbol.fo_eligible" class="fo-indicator">F&O</div>
              </div>
              <div class="type-badge">
                <v-chip size="x-small" :color="getInstrumentTypeColor(symbol.instrument_type)" class="type-chip">
                  {{ symbol.instrument_type }}
                </v-chip>
              </div>
            </div>

            <!-- Company name -->
            <div class="company-name">{{ symbol.name }}</div>

            <!-- Symbol details -->
            <div class="details-container">
              <div class="detail-item">
                <v-icon size="x-small" class="detail-icon">mdi-cube-outline</v-icon>
                <span class="detail-label">Lot:</span>
                <span class="detail-value">{{ symbol.lot_size || 'N/A' }}</span>
              </div>
              <div class="detail-item">
                <v-icon size="x-small" class="detail-icon">mdi-bank</v-icon>
                <span class="detail-label">Exchange:</span>
                <span class="detail-value">{{ symbol.exchange }}</span>
              </div>
            </div>

            <!-- Card actions -->
            <div class="card-actions">
              <v-btn size="small" variant="flat" color="primary" class="view-btn" @click.stop="viewSymbolDetails(symbol)">
                <v-icon size="small" class="mr-1">mdi-eye</v-icon>
                View Details
              </v-btn>
              <v-btn size="small" icon variant="text" class="watchlist-btn" @click.stop="addToWatchlist(symbol)">
                <v-icon size="small">mdi-star-outline</v-icon>
              </v-btn>
            </div>
          </div>
        </div>
      </TransitionGroup>

      <!-- Empty state when no symbols found -->
      <div v-if="filteredSymbols.length === 0 && !symbolStore.loading" class="empty-state">
        <div class="empty-icon">
          <v-icon size="64" color="primary">mdi-finance</v-icon>
        </div>
        <h3 class="empty-title">No symbols found</h3>
        <p class="empty-message">Try adjusting your search criteria or filters</p>
        <v-btn variant="outlined" color="primary" @click="resetFilters">
          Reset Filters
        </v-btn>
      </div>

      <!-- Loading skeletons -->
      <div v-if="symbolStore.loading && filteredSymbols.length === 0" class="symbols-grid">
        <div v-for="i in 12" :key="i" class="symbol-card is-skeleton">
          <div class="card-stripe skeleton-stripe"></div>
          <div class="card-content">
            <div class="card-header skeleton-header">
              <div class="skeleton-line w-2/5"></div>
              <div class="skeleton-chip"></div>
            </div>
            <div class="skeleton-line w-4/5"></div>
            <div class="skeleton-details">
              <div class="skeleton-line w-2/5"></div>
              <div class="skeleton-line w-2/5"></div>
            </div>
            <div class="skeleton-actions">
              <div class="skeleton-button"></div>
              <div class="skeleton-circle"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination controls -->
    <div v-if="filteredSymbols.length > 0" class="pagination-wrapper">
      <v-pagination v-model="currentPage" :length="totalPages" :total-visible="7" :disabled="symbolStore.loading" class="pagination"></v-pagination>
    </div>

    <!-- Enhanced Symbol Details Dialog -->
    <v-dialog v-model="showDetailsDialog" max-width="800">
      <div v-if="symbolStore.selectedSymbol" class="detail-dialog">
        <div class="detail-stripe" :class="getSymbolBadgeClass(symbolStore.selectedSymbol.instrument_type)"></div>

        <div class="dialog-header">
          <div class="dialog-title-area">
            <h2 class="dialog-title">{{ symbolStore.selectedSymbol.trading_symbol }}</h2>
            <div v-if="symbolStore.selectedSymbol.fo_eligible" class="dialog-fo-badge">F&O</div>
            <p class="dialog-subtitle">{{ symbolStore.selectedSymbol.name }}</p>
          </div>
          <button class="dialog-close-btn" @click="closeDetailsDialog">
            <v-icon>mdi-close</v-icon>
          </button>
        </div>

        <div class="dialog-divider"></div>

        <div class="dialog-content">
          <div class="dialog-grid">
            <div class="grid-item">
              <div class="grid-icon"><v-icon size="small">mdi-bank</v-icon></div>
              <div class="grid-info">
                <div class="grid-label">Exchange</div>
                <div class="grid-value">{{ symbolStore.selectedSymbol.exchange }}</div>
              </div>
            </div>
            <div class="grid-item">
              <div class="grid-icon"><v-icon size="small">mdi-identifier</v-icon></div>
              <div class="grid-info">
                <div class="grid-label">Security ID</div>
                <div class="grid-value">{{ symbolStore.selectedSymbol.security_id }}</div>
              </div>
            </div>
            <div class="grid-item">
              <div class="grid-icon"><v-icon size="small">mdi-tag</v-icon></div>
              <div class="grid-info">
                <div class="grid-label">Instrument Type</div>
                <div class="grid-value">
                  <span class="type-pill" :class="getInstrumentPillClass(symbolStore.selectedSymbol.instrument_type)">
                    {{ symbolStore.selectedSymbol.instrument_type }}
                  </span>
                </div>
              </div>
            </div>
            <div class="grid-item">
              <div class="grid-icon"><v-icon size="small">mdi-certificate</v-icon></div>
              <div class="grid-info">
                <div class="grid-label">F&O Eligible</div>
                <div class="grid-value">
                  <div class="eligibility-indicator">
                    <v-icon v-if="symbolStore.selectedSymbol.fo_eligible" size="small" color="success">mdi-check-circle</v-icon>
                    <v-icon v-else size="small" color="grey-lighten-1">mdi-minus-circle</v-icon>
                    <span>{{ symbolStore.selectedSymbol.fo_eligible ? 'Yes' : 'No' }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="grid-item">
              <div class="grid-icon"><v-icon size="small">mdi-cube-outline</v-icon></div>
              <div class="grid-info">
                <div class="grid-label">Lot Size</div>
                <div class="grid-value">{{ symbolStore.selectedSymbol.lot_size || 'N/A' }}</div>
              </div>
            </div>
            <div class="grid-item">
              <div class="grid-icon"><v-icon size="small">mdi-segment</v-icon></div>
              <div class="grid-info">
                <div class="grid-label">Segment</div>
                <div class="grid-value">{{ symbolStore.selectedSymbol.segment }}</div>
              </div>
            </div>
            <div class="grid-item">
              <div class="grid-icon"><v-icon size="small">mdi-checkbox-marked-circle</v-icon></div>
              <div class="grid-info">
                <div class="grid-label">Status</div>
                <div class="grid-value">
                  <span class="status-pill" :class="symbolStore.selectedSymbol.active ? 'status-active' : 'status-inactive'">
                    {{ symbolStore.selectedSymbol.active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>
            </div>
            <div class="grid-item">
              <div class="grid-icon"><v-icon size="small">mdi-calendar</v-icon></div>
              <div class="grid-info">
                <div class="grid-label">Added On</div>
                <div class="grid-value">{{ formatDate(symbolStore.selectedSymbol.created_at) }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="dialog-divider"></div>

        <div class="dialog-actions">
          <button class="dialog-btn dialog-btn-secondary" @click="closeDetailsDialog">
            Cancel
          </button>
          <button class="dialog-btn dialog-btn-primary" @click="addToWatchlist(symbolStore.selectedSymbol)">
            <v-icon class="mr-1" size="small">mdi-star-outline</v-icon>
            Add to Watchlist
          </button>
          <button class="dialog-btn dialog-btn-primary" @click="$router.push(`/app/symbols/${symbolStore.selectedSymbol.trading_symbol}`); closeDetailsDialog();">
            <v-icon class="mr-1" size="small">mdi-chart-line</v-icon>
            Symbol Details
          </button>
        </div>
      </div>
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

    addToWatchlist(symbol) {
      // Implementation for adding to watchlist
      console.log('Added to watchlist:', symbol.trading_symbol);
      // You can add implementation to add the symbol to a watchlist
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

    getInstrumentPillClass(type) {
      const classMap = {
        'EQ': 'pill-eq',
        'FUT': 'pill-fut',
        'OPT': 'pill-opt',
        'ETF': 'pill-etf',
        'INDEX': 'pill-index'
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
/* Common styles */
.symbols-explorer {
  @apply w-full flex flex-col gap-6;
}

/* Header styles */
.explorer-header {
  @apply bg-white rounded-xl border border-gray-200 overflow-hidden;
}

.header-container {
  @apply p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4;
}

.header-left {
  @apply flex flex-col;
}

.page-title {
  @apply text-2xl font-bold text-gray-800 mb-2;
}

.header-stats {
  @apply flex gap-2;
}

.stat-badge {
  @apply inline-flex items-center px-3 py-1 bg-primary bg-opacity-5 rounded-full;
}

.stat-count {
  @apply text-sm font-semibold text-primary;
}

.stat-label {
  @apply text-xs text-gray-600 ml-1;
}

.fo-badge {
  @apply inline-flex items-center px-3 py-1 bg-primary bg-opacity-10 rounded-full;
}

.fo-badge span {
  @apply text-xs text-primary ml-1;
}

.search-area {
  @apply flex flex-col sm:flex-row items-stretch gap-3 w-full md:w-auto;
}

.search-field {
  @apply flex-grow;
}

.filter-actions {
  @apply flex items-center gap-2;
}

.filter-selected {
  @apply !bg-primary !text-white;
}

.filter-chip {
  @apply font-medium;
}

.refresh-btn {
  @apply whitespace-nowrap;
}

/* Symbol grid styles */
.grid-container {
  @apply relative min-h-[400px];
}

.symbols-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4;
}

.symbol-card {
  @apply relative bg-white rounded-xl border border-gray-200 overflow-hidden flex flex-col transition-all duration-200 hover:border-primary hover:border-opacity-50 cursor-pointer;
}

.card-stripe {
  @apply h-1 w-full;
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

.card-content {
  @apply p-4 flex flex-col h-full;
}

.card-header {
  @apply flex justify-between items-center mb-3;
}

.symbol-title {
  @apply flex items-center gap-2;
}

.symbol-name {
  @apply font-bold text-gray-800;
}

.fo-indicator {
  @apply text-xs px-2 py-0.5 bg-primary bg-opacity-10 text-primary rounded font-medium;
}

.type-badge {
  @apply flex-shrink-0;
}

.type-chip {
  @apply text-white;
}

.company-name {
  @apply text-sm text-gray-600 mb-4 line-clamp-2;
}

.details-container {
  @apply grid grid-cols-2 gap-2 mt-auto mb-3;
}

.detail-item {
  @apply flex items-center text-xs;
}

.detail-icon {
  @apply text-gray-400 mr-1;
}

.detail-label {
  @apply text-gray-500 mr-1;
}

.detail-value {
  @apply font-medium;
}

.card-actions {
  @apply flex justify-between items-center mt-auto pt-2 border-t border-gray-100;
}

.view-btn {
  @apply text-xs;
}

.watchlist-btn {
  @apply text-gray-400 hover:text-primary;
}

/* Empty state */
.empty-state {
  @apply flex flex-col items-center justify-center py-16 gap-3 text-center;
}

.empty-icon {
  @apply mb-2 opacity-50;
}

.empty-title {
  @apply text-lg font-medium text-gray-700;
}

.empty-message {
  @apply text-sm text-gray-500 mb-2;
}

/* Skeleton loading */
.is-skeleton {
  @apply animate-pulse;
}

.skeleton-stripe {
  @apply bg-gray-200;
}

.skeleton-header {
  @apply flex justify-between mb-3;
}

.skeleton-line {
  @apply h-4 bg-gray-200 rounded;
}

.skeleton-chip {
  @apply h-4 w-16 bg-gray-200 rounded-full;
}

.skeleton-details {
  @apply grid grid-cols-2 gap-2 my-4;
}

.skeleton-actions {
  @apply flex justify-between items-center pt-2 border-t border-gray-100;
}

.skeleton-button {
  @apply h-8 w-24 bg-gray-200 rounded;
}

.skeleton-circle {
  @apply h-8 w-8 bg-gray-200 rounded-full;
}

/* Pagination */
.pagination-wrapper {
  @apply flex justify-center my-6;
}

/* Enhanced Detail dialog */
.detail-dialog {
  @apply relative bg-white rounded-xl overflow-hidden;
}

.detail-stripe {
  @apply h-2 w-full;
}

.dialog-header {
  @apply flex justify-between items-start p-6;
}

.dialog-title-area {
  @apply flex flex-col;
}

.dialog-title {
  @apply text-xl font-bold text-gray-800 flex items-center gap-2;
}

.dialog-fo-badge {
  @apply inline-flex ml-2 text-xs px-2 py-0.5 bg-primary bg-opacity-10 text-primary rounded font-medium;
}

.dialog-subtitle {
  @apply text-sm text-gray-600 mt-1;
}

.dialog-close-btn {
  @apply p-1 rounded-full hover:bg-gray-100 text-gray-500 transition-colors;
}

.dialog-divider {
  @apply h-px w-full bg-gray-200;
}

.dialog-content {
  @apply p-6;
}

.dialog-grid {
  @apply grid grid-cols-1 md:grid-cols-2 gap-6;
}

.grid-item {
  @apply flex items-start gap-3;
}

.grid-icon {
  @apply mt-0.5 text-primary;
}

.grid-info {
  @apply flex flex-col;
}

.grid-label {
  @apply text-sm text-gray-500;
}

.grid-value {
  @apply font-medium flex items-center;
}

.type-pill {
  @apply px-2 py-0.5 rounded text-white text-xs font-medium;
}

.pill-eq {
  @apply bg-blue-600;
}

.pill-fut {
  @apply bg-purple-600;
}

.pill-opt {
  @apply bg-orange-500;
}

.pill-etf {
  @apply bg-green-600;
}

.pill-index {
  @apply bg-cyan-600;
}

.eligibility-indicator {
  @apply flex items-center gap-1;
}

.status-pill {
  @apply px-2 py-0.5 rounded text-white text-xs font-medium;
}

.status-active {
  @apply bg-green-500;
}

.status-inactive {
  @apply bg-red-500;
}

.dialog-actions {
  @apply flex flex-wrap justify-end gap-2 p-4 bg-gray-50;
}

.dialog-btn {
  @apply px-4 py-2 rounded-lg text-sm font-medium transition-colors;
}

.dialog-btn-secondary {
  @apply bg-white text-gray-700 border border-gray-300 hover:bg-gray-50;
}

.dialog-btn-primary {
  @apply bg-primary text-white hover:bg-primary-dark;
}

/* Transition animations */
.symbols-list-enter-active,
.symbols-list-leave-active {
  @apply transition-all duration-300 ease-in-out;
}

.symbols-list-enter-from,
.symbols-list-leave-to {
  @apply opacity-0 transform translate-y-4;
}
</style>