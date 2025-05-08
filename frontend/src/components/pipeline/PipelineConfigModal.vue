<template>
  <v-dialog :model-value="modelValue" max-width="600" scrollable @update:model-value="$emit('update:modelValue', $event)">
    <div class="modal-card">
      <div class="modal-header">
        <h2 class="modal-title">Pipeline Configuration</h2>
        <v-btn icon="mdi-close" variant="text" @click="$emit('update:modelValue', false)"></v-btn>
      </div>

      <div class="modal-content">
        <div class="modal-section">
          <h3 class="section-title">Steps to Execute</h3>
          <div class="steps-grid">
            <v-checkbox v-for="step in steps" :key="step.id" v-model="localSelectedSteps" :value="step.id" :label="step.name" color="primary" hide-details density="comfortable"></v-checkbox>
          </div>
        </div>

        <div class="modal-section">
          <h3 class="section-title">Options</h3>
          <v-switch v-model="localPipelineConfig.force" color="primary" hide-details density="comfortable" label="Force Retraining of All Models"></v-switch>

          <v-text-field v-model="localPipelineConfig.maxSymbols" label="Maximum Symbols to Process" type="number" min="1" max="500" hint="Limit the number of symbols to process (leave empty for all)" persistent-hint density="comfortable" variant="outlined" class="mt-4"></v-text-field>
        </div>

        <div class="modal-section">
          <h3 class="section-title">Schedule Settings</h3>
          <div class="schedule-grid">
            <v-select v-model="localScheduleTime" :items="scheduleOptions" label="Daily run time" variant="outlined" density="comfortable"></v-select>

            <v-select v-model="localScheduleFrequency" :items="['Daily', 'Weekdays only', 'Custom']" label="Frequency" variant="outlined" density="comfortable"></v-select>
          </div>

          <div v-if="localScheduleFrequency === 'Custom'" class="days-selection mt-3">
            <div class="text-sm font-medium mb-2">Days of Week</div>
            <div class="days-grid">
              <v-checkbox v-for="day in weekDays" :key="day.value" v-model="localSelectedDays" :value="day.value" :label="day.label" hide-details density="comfortable" class="mr-2"></v-checkbox>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <v-btn variant="text" color="gray" @click="$emit('update:modelValue', false)">
          Cancel
        </v-btn>
        <v-btn color="primary" @click="saveConfig">
          Save Configuration
        </v-btn>
      </div>
    </div>
  </v-dialog>
</template>

<script>
export default {
  name: 'PipelineConfigModal',
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    selectedSteps: {
      type: Array,
      required: true
    },
    pipelineConfig: {
      type: Object,
      required: true
    },
    scheduleTime: {
      type: String,
      required: true
    },
    scheduleFrequency: {
      type: String,
      required: true
    },
    selectedDays: {
      type: Array,
      required: true
    },
    steps: {
      type: Array,
      required: true
    },
    scheduleOptions: {
      type: Array,
      required: true
    }
  },
  emits: [
    'update:modelValue',
    'update:selectedSteps',
    'update:pipelineConfig',
    'update:scheduleTime',
    'update:scheduleFrequency',
    'update:selectedDays',
    'save'
  ],
  computed: {
    localSelectedSteps: {
      get() {
        return this.selectedSteps;
      },
      set(value) {
        this.$emit('update:selectedSteps', value);
      }
    },
    localPipelineConfig: {
      get() {
        return this.pipelineConfig;
      },
      set(value) {
        this.$emit('update:pipelineConfig', value);
      }
    },
    localScheduleTime: {
      get() {
        return this.scheduleTime;
      },
      set(value) {
        this.$emit('update:scheduleTime', value);
      }
    },
    localScheduleFrequency: {
      get() {
        return this.scheduleFrequency;
      },
      set(value) {
        this.$emit('update:scheduleFrequency', value);
      }
    },
    localSelectedDays: {
      get() {
        return this.selectedDays;
      },
      set(value) {
        this.$emit('update:selectedDays', value);
      }
    },
    weekDays() {
      return [
        { label: 'Monday', value: 1 },
        { label: 'Tuesday', value: 2 },
        { label: 'Wednesday', value: 3 },
        { label: 'Thursday', value: 4 },
        { label: 'Friday', value: 5 },
        { label: 'Saturday', value: 6 },
        { label: 'Sunday', value: 0 }
      ];
    }
  },
  methods: {
    saveConfig() {
      this.$emit('save');
    }
  }
}
</script>

<style lang="postcss" scoped>
.modal-card {
  @apply bg-white rounded-xl border border-gray-200 overflow-hidden;
}

.modal-header {
  @apply flex justify-between items-center px-6 py-4 border-b border-gray-200 bg-gray-50;
}

.modal-title {
  @apply text-lg font-bold text-gray-800;
}

.modal-content {
  @apply p-6 max-h-[70vh] overflow-y-auto;
}

.modal-section {
  @apply mb-6 last:mb-0;
}

.section-title {
  @apply text-base font-medium mb-3 pb-2 border-b border-gray-200 text-gray-700;
}

.steps-grid {
  @apply grid grid-cols-2 gap-4;
}

.schedule-grid {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-4;
}

.days-selection {
  @apply bg-gray-50 p-4 rounded-lg border border-gray-100;
}

.days-grid {
  @apply flex flex-wrap gap-x-8 gap-y-2;
}

.modal-footer {
  @apply flex justify-end gap-3 p-5 bg-gray-50 border-t border-gray-200;
}

@media (max-width: 640px) {

  .steps-grid,
  .schedule-grid {
    @apply grid-cols-1;
  }
}
</style>