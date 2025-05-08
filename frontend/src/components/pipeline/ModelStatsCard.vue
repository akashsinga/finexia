<template>
  <div class="stat-card">
    <div class="stat-card-header">
      <h2 class="stat-card-title">Model Information</h2>
      <v-btn icon="mdi-refresh" variant="text" density="comfortable" color="gray" @click="$emit('refresh')"></v-btn>
    </div>
    <div class="stat-grid">
      <div class="stat-item">
        <div class="stat-icon bg-indigo-50 text-indigo-600">
          <v-icon>mdi-brain</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.modelFileCount || 0 }}</div>
          <div class="stat-label">Model Files</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon bg-cyan-50 text-cyan-600">
          <v-icon>mdi-file-chart</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatSize(stats.modelDirectorySizeMb || 0) }}</div>
          <div class="stat-label">Storage Used</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon bg-pink-50 text-pink-600">
          <v-icon>mdi-update</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.recentModelTrainingCount || 0 }}</div>
          <div class="stat-label">Recent Trainings</div>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon bg-amber-50 text-amber-600">
          <v-icon>mdi-database</v-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.databaseStatus || 'N/A' }}</div>
          <div class="stat-label">Database Status</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ModelStatsCard',
  props: {
    stats: {
      type: Object,
      required: true
    }
  },
  emits: ['refresh'],
  methods: {
    formatSize(size) {
      if (size < 1) {
        return `${(size * 1024).toFixed(0)} KB`;
      }
      return `${size.toFixed(1)} MB`;
    }
  }
}
</script>

<style lang="postcss" scoped>
.stat-card {
  @apply bg-white rounded-xl border border-gray-200 p-6;
}

.stat-card-header {
  @apply flex justify-between items-center mb-5;
}

.stat-card-title {
  @apply text-base font-bold text-gray-800;
}

.stat-grid {
  @apply grid grid-cols-2 gap-5;
}

.stat-item {
  @apply flex items-start gap-3 p-1 rounded-lg;
}

.stat-icon {
  @apply w-10 h-10 flex items-center justify-center rounded-lg;
}

.stat-content {
  @apply flex-1;
}

.stat-value {
  @apply text-lg font-semibold text-gray-900;
}

.stat-label {
  @apply text-xs text-gray-500;
}
</style>