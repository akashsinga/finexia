<template>
  <div class="steps-card">
    <div class="steps-header">
      <h2 class="steps-title">Pipeline Steps</h2>
      <div class="steps-actions">
        <v-btn size="small" variant="text" color="primary" @click="$emit('select-all')" class="select-btn">
          {{ allStepsSelected ? 'Deselect All' : 'Select All' }}
        </v-btn>
      </div>
    </div>
    <div class="steps-container">
      <div v-for="(step, index) in steps" :key="step.id" class="step-item" :class="{
        'step-running': isRunning && currentStep === step.name,
        'step-selected': isStepSelected(step.id)
      }" @click="$emit('select', step.id)">
        <div class="step-indicator" :class="getStepClass(step)">
          <v-icon v-if="getStepStatus(step) === 'completed'" size="small">mdi-check</v-icon>
          <v-icon v-else-if="getStepStatus(step) === 'running'" size="small">mdi-loading mdi-spin</v-icon>
          <v-icon v-else-if="getStepStatus(step) === 'failed'" size="small">mdi-close</v-icon>
          <span v-else>{{ index + 1 }}</span>
        </div>
        <div class="step-content">
          <div class="step-title">{{ step.name }}</div>
          <div class="step-description">{{ step.description }}</div>
        </div>
        <div class="step-toggle">
          <v-checkbox v-model="localSelectedSteps" :value="step.id" color="primary" hide-details density="compact" @click.stop></v-checkbox>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PipelineStepsSelector',
  props: {
    steps: {
      type: Array,
      required: true
    },
    selectedSteps: {
      type: Array,
      required: true
    },
    isRunning: {
      type: Boolean,
      default: false
    },
    currentStep: {
      type: String,
      default: null
    }
  },
  emits: ['select', 'select-all'],
  computed: {
    localSelectedSteps: {
      get() {
        return this.selectedSteps;
      },
      set(value) {
        this.$emit('update:selectedSteps', value);
      }
    },
    allStepsSelected() {
      return this.selectedSteps.length === this.steps.length;
    }
  },
  methods: {
    isStepSelected(stepId) {
      return this.selectedSteps.includes(stepId);
    },
    getStepStatus(step) {
      if (!this.isRunning) {
        return 'idle';
      }

      if (this.currentStep === step.name) {
        return 'running';
      }

      // Find index of current step
      const currentStepIndex = this.steps.findIndex(s => s.name === this.currentStep);
      const thisStepIndex = this.steps.findIndex(s => s.id === step.id);

      if (currentStepIndex === -1 || thisStepIndex === -1) {
        return 'idle';
      }

      if (thisStepIndex < currentStepIndex) {
        return 'completed';
      }

      return 'idle';
    },
    getStepClass(step) {
      const status = this.getStepStatus(step);
      switch (status) {
        case 'running': return 'step-indicator-running';
        case 'completed': return 'step-indicator-completed';
        case 'failed': return 'step-indicator-failed';
        default: return 'step-indicator-idle';
      }
    }
  }
}
</script>

<style lang="postcss" scoped>
.steps-card {
  @apply bg-white rounded-xl border border-gray-200 p-6;
}

.steps-header {
  @apply flex justify-between items-center mb-5;
}

.steps-title {
  @apply text-base font-bold text-gray-800;
}

.steps-actions {
  @apply flex;
}

.select-btn {
  @apply text-xs font-medium;
}

.steps-container {
  @apply grid grid-cols-1 sm:grid-cols-2 gap-4;
}

.step-item {
  @apply flex items-center bg-gray-50 hover:bg-gray-100 rounded-lg p-3 border border-gray-100 transition-colors duration-200 cursor-pointer;
}

.step-running {
  @apply bg-blue-50 border-blue-200;
  animation: step-pulse 2s infinite alternate;
}

@keyframes step-pulse {
  0% {
    background-color: rgba(219, 234, 254, 0.8);
  }

  100% {
    background-color: rgba(219, 234, 254, 0.4);
  }
}

.step-selected {
  @apply border-primary;
}

.step-indicator {
  @apply w-9 h-9 rounded-full flex items-center justify-center mr-3 text-sm font-medium;
}

.step-indicator-idle {
  @apply bg-gray-200 text-gray-700;
}

.step-indicator-running {
  @apply bg-blue-500 text-white;
}

.step-indicator-completed {
  @apply bg-green-500 text-white;
}

.step-indicator-failed {
  @apply bg-red-500 text-white;
}

.step-content {
  @apply flex-1;
}

.step-title {
  @apply text-sm font-medium text-gray-700;
}

.step-description {
  @apply text-xs text-gray-500 mt-1;
}

.step-toggle {
  @apply ml-auto;
}
</style>