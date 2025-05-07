<template>
  <div :class="['toggle-wrapper', { 'toggle-disabled': disabled, customClass }]">
    <label class="toggle-container">
      <input type="checkbox" :checked="modelValue" :disabled="disabled" class="toggle-input" @change="$emit('update:modelValue', $event.target.checked)" />
      <span class="toggle-track" :class="{ 'toggle-checked': modelValue }">
        <span class="toggle-thumb"></span>
      </span>
      <span v-if="label" class="toggle-label">
        {{ label }}
      </span>
    </label>
    <div v-if="hint" class="toggle-hint">{{ hint }}</div>
  </div>
</template>

<script>
export default {
  name: 'ToggleSwitch',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    label: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    hint: {
      type: String,
      default: ''
    },
    customClass: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue']
}
</script>

<style lang="postcss" scoped>
.toggle-wrapper {
  @apply mb-4;
}

.toggle-container {
  @apply inline-flex items-center cursor-pointer;
}

.toggle-input {
  @apply absolute opacity-0 w-0 h-0;
}

.toggle-track {
  @apply relative inline-block w-10 h-5 bg-gray-300 rounded-full mr-3 transition-colors duration-200;
}

.toggle-thumb {
  @apply absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full transition-transform duration-200 shadow-sm;
}

.toggle-checked {
  @apply bg-primary;
}

.toggle-checked .toggle-thumb {
  @apply transform translate-x-5;
}

.toggle-label {
  @apply text-sm text-gray-700;
}

.toggle-hint {
  @apply mt-1 text-xs text-gray-500 ml-14;
}

.toggle-disabled {
  @apply opacity-60;
}

.toggle-disabled .toggle-container {
  @apply cursor-not-allowed;
}
</style>