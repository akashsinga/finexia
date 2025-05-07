<template>
  <div :class="['checkbox-wrapper', { 'checkbox-disabled': disabled, customClass }]">
    <label class="checkbox-container">
      <input type="checkbox" :checked="modelValue" :disabled="disabled" :required="required" class="checkbox-input" @change="$emit('update:modelValue', $event.target.checked)" />
      <span class="checkbox-box">
        <v-icon v-if="modelValue" size="x-small" class="checkbox-icon">mdi-check</v-icon>
      </span>
      <span v-if="label" class="checkbox-label">
        {{ label }}
        <span v-if="required" class="checkbox-required">*</span>
      </span>
    </label>
    <div v-if="error || hint" class="checkbox-message">
      <span v-if="error" class="checkbox-error">{{ error }}</span>
      <span v-else-if="hint" class="checkbox-hint">{{ hint }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Checkbox',
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
    required: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: ''
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
.checkbox-wrapper {
  @apply mb-4;
}

.checkbox-container {
  @apply inline-flex items-center cursor-pointer;
}

.checkbox-input {
  @apply absolute opacity-0 w-0 h-0;
}

.checkbox-box {
  @apply inline-flex items-center justify-center w-5 h-5 border border-gray-300 rounded bg-white mr-2 transition-colors duration-200;
}

.checkbox-input:checked~.checkbox-box {
  @apply bg-primary border-primary text-white;
}

.checkbox-input:focus~.checkbox-box {
  @apply ring-2 ring-primary ring-opacity-50;
}

.checkbox-label {
  @apply text-sm text-gray-700;
}

.checkbox-required {
  @apply text-error ml-0.5;
}

.checkbox-message {
  @apply mt-1 text-xs ml-7;
}

.checkbox-error {
  @apply text-error;
}

.checkbox-hint {
  @apply text-gray-500;
}

.checkbox-disabled {
  @apply opacity-60;
}

.checkbox-disabled .checkbox-container {
  @apply cursor-not-allowed;
}

.checkbox-disabled .checkbox-box {
  @apply bg-gray-100;
}
</style>