<template>
  <div :class="['radio-wrapper', { 'radio-disabled': disabled, customClass }]">
    <label class="radio-container">
      <input type="radio" :checked="modelValue === value" :name="name" :value="value" :disabled="disabled" :required="required" class="radio-input" @change="$emit('update:modelValue', value)" />
      <span class="radio-circle">
        <span v-if="modelValue === value" class="radio-dot"></span>
      </span>
      <span v-if="label" class="radio-label">
        {{ label }}
        <span v-if="required" class="radio-required">*</span>
      </span>
    </label>
    <div v-if="hint" class="radio-hint">{{ hint }}</div>
  </div>
</template>

<script>
export default {
  name: 'RadioButton',
  props: {
    modelValue: {
      type: [String, Number, Boolean],
      required: true
    },
    value: {
      type: [String, Number, Boolean],
      required: true
    },
    name: {
      type: String,
      required: true
    },
    label: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    required: {
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
.radio-wrapper {
  @apply mb-4;
}

.radio-container {
  @apply inline-flex items-center cursor-pointer;
}

.radio-input {
  @apply absolute opacity-0 w-0 h-0;
}

.radio-circle {
  @apply inline-flex items-center justify-center w-5 h-5 border border-gray-300 rounded-full bg-white mr-2 transition-colors duration-200;
}

.radio-dot {
  @apply block w-2.5 h-2.5 rounded-full bg-primary;
}

.radio-input:checked~.radio-circle {
  @apply border-primary;
}

.radio-input:focus~.radio-circle {
  @apply ring-2 ring-primary ring-opacity-50;
}

.radio-label {
  @apply text-sm text-gray-700;
}

.radio-required {
  @apply text-error ml-0.5;
}

.radio-hint {
  @apply mt-1 text-xs text-gray-500 ml-7;
}

.radio-disabled {
  @apply opacity-60;
}

.radio-disabled .radio-container {
  @apply cursor-not-allowed;
}

.radio-disabled .radio-circle {
  @apply bg-gray-100;
}
</style>