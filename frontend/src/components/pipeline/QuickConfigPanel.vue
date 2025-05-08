<template>
  <div class="config-card">
    <div class="config-header">
      <h2 class="config-title">Quick Configuration</h2>
      <v-btn color="primary" size="small" variant="text" @click="$emit('advanced-settings')">
        Advanced Settings
      </v-btn>
    </div>

    <div class="config-content">
      <div class="config-item">
        <div class="config-item-header">
          <div class="config-item-title">Force Retraining</div>
          <v-switch v-model="localForce" color="primary" hide-details density="compact"></v-switch>
        </div>
        <div class="config-item-description">
          Force retraining of all models even if they were recently updated
        </div>
      </div>

      <div class="config-item">
        <div class="config-item-header">
          <div class="config-item-title">Schedule</div>
        </div>
        <div class="config-schedule">
          <v-select v-model="localScheduleTime" :items="scheduleTimes" label="Daily run time" variant="outlined" density="compact" hide-details class="mr-2"></v-select>
          <v-btn size="small" color="primary" variant="tonal" :disabled="!localScheduleTime" @click="$emit('save-schedule')">
            Save
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'QuickConfigPanel',
  props: {
    force: {
      type: Boolean,
      default: false
    },
    scheduleTime: {
      type: String,
      default: '02:00'
    },
    scheduleTimes: {
      type: Array,
      default: () => [
        { title: '00:00', value: '00:00' }, { title: '02:00', value: '02:00' },
        { title: '04:00', value: '04:00' }, { title: '06:00', value: '06:00' },
        { title: '08:00', value: '08:00' }, { title: '10:00', value: '10:00' },
        { title: '12:00', value: '12:00' }, { title: '14:00', value: '14:00' },
        { title: '16:00', value: '16:00' }, { title: '18:00', value: '18:00' },
        { title: '20:00', value: '20:00' }, { title: '22:00', value: '22:00' }
      ]
    }
  },
  emits: ['update:force', 'update:scheduleTime', 'save-schedule', 'advanced-settings'],
  computed: {
    localForce: {
      get() {
        return this.force;
      },
      set(value) {
        this.$emit('update:force', value);
      }
    },
    localScheduleTime: {
      get() {
        return this.scheduleTime;
      },
      set(value) {
        this.$emit('update:scheduleTime', value);
      }
    }
  }
}
</script>

<style lang="postcss" scoped>
.config-card {
  @apply bg-white rounded-xl p-6 border border-gray-200;
}

.config-header {
  @apply flex justify-between items-center mb-4;
}

.config-title {
  @apply text-base font-bold text-gray-800;
}

.config-content {
  @apply space-y-4;
}

.config-item {
  @apply bg-gray-50 p-4 rounded-lg border border-gray-100;
}

.config-item-header {
  @apply flex justify-between items-center;
}

.config-item-title {
  @apply text-sm font-medium text-gray-700;
}

.config-item-description {
  @apply text-xs text-gray-500 mt-1.5;
}

.config-schedule {
  @apply flex mt-3 gap-2 items-start;
}
</style>