// src/components/symbols/SymbolHeader.vue
<template>
  <div class="overview-card">
    <div class="flex items-center gap-4">
      <div class="symbol-avatar" :class="getSymbolBadgeClass(symbol.instrument_type)">
        {{ symbol.trading_symbol.charAt(0) }}
      </div>
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <h1 class="text-xl font-bold">{{ symbol.trading_symbol }}</h1>
          <div v-if="symbol.fo_eligible" class="fo-badge">F&O</div>
          <div class="instrument-badge" :class="getInstrumentClass(symbol.instrument_type)">
            {{ symbol.instrument_type }}
          </div>
        </div>
        <div class="text-gray-600 text-sm">{{ symbol.name }}</div>
      </div>
      <div class="flex items-center gap-2">
        <v-btn size="small" variant="outlined" color="primary" prepend-icon="mdi-star-outline">
          Add to Watchlist
        </v-btn>
      </div>
    </div>

    <!-- Quick Stats Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
      <div class="stat-pill">
        <div class="text-xs text-gray-500">Exchange</div>
        <div class="font-medium">{{ symbol.exchange }}</div>
      </div>
      <div class="stat-pill">
        <div class="text-xs text-gray-500">Security ID</div>
        <div class="font-medium">{{ symbol.security_id }}</div>
      </div>
      <div class="stat-pill">
        <div class="text-xs text-gray-500">Segment</div>
        <div class="font-medium">{{ symbol.segment }}</div>
      </div>
      <div class="stat-pill">
        <div class="text-xs text-gray-500">Status</div>
        <div>
          <span class="status-badge" :class="symbol.active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
            {{ symbol.active ? 'Active' : 'Inactive' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getSymbolBadgeClass, getInstrumentClass } from '@/utils/symbols';

export default {
  name: 'SymbolHeader',
  props: {
    symbol: {
      type: Object,
      required: true
    }
  },
  methods: {
    getSymbolBadgeClass,
    getInstrumentClass
  }
}
</script>

<style lang="postcss" scoped>
.overview-card {
  @apply bg-white rounded-xl p-5 shadow-sm border border-gray-200;
}

.symbol-avatar {
  @apply w-12 h-12 rounded-xl flex items-center justify-center text-white text-xl font-bold;
}

.fo-badge {
  @apply px-2 py-0.5 text-xs font-medium bg-primary/10 text-primary rounded;
}

.instrument-badge {
  @apply px-2 py-0.5 text-xs font-medium text-white rounded;
}

.stat-pill {
  @apply bg-gray-50 p-3 rounded-lg border border-gray-100;
}

.status-badge {
  @apply px-2 py-0.5 text-xs font-medium rounded;
}
</style>