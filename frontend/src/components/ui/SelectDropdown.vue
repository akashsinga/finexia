<template>
  <div :class="['select-wrapper', { 'select-error': error, 'select-disabled': disabled, customClass }]">
    <label v-if="label" :for="id" class="select-label">
      {{ label }}
      <span v-if="required" class="select-required">*</span>
    </label>

    <div class="select-container">
      <select :id="id" :value="modelValue" :disabled="disabled" :required="required" class="select-field" @change="$emit('update:modelValue', $event.target.value)" @focus="$emit('focus', $event)" @blur="$emit('blur', $event)">
        <option v-if="placeholder" value="" disabled selected>{{ placeholder }}</option>
        <option v-for="option in options" :key="option.value" :value="option.value">
          {{ option.label }}
        </option>
      </select>
      <div class="select-arrow">
        <v-icon size="small">mdi-chevron-down</v-icon>
      </div>
    </div>

    <div v-if="error || hint" class="select-message">
      <span v-if="error" class="select-error-message">{{ error }}</span>
      <span v-else-if="hint" class="select-hint">{{ hint }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SelectDropdown',
  props: {
    modelValue: {
      type: [String, Number, Boolean],
      default: ''
    },
    id: {
      type: String,
      default() {
        return `select-${Math.random().toString(36).substring(2, 9)}`
      }
    },
    options: {
      type: Array,
      required: true,
      validator: (value) => {
        return value.every(option =>
          typeof option === 'object' &&
          'value' in option &&
          'label' in option
        )
      }
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Select an option'
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
  emits: ['update:modelValue', 'focus', 'blur']
}
</script>

<style lang="postcss" scoped>
.select-wrapper {
  @apply w-full mb-4;
}

.select-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.select-required {
  @apply text-error ml-0.5;
}

.select-container {
  @apply relative;
}

.select-field {
  @apply appearance-none w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-gray-700 text-sm pr-10 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed transition-colors duration-200;
}

.select-arrow {
  @apply absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 pointer-events-none;
}

.select-message {
  @apply mt-1 text-xs;
}

.select-error-message {
  @apply text-error;
}

.select-hint {
  @apply text-gray-500;
}

.select-error .select-field {
  @apply border-error focus:ring-error focus:border-error;
}

.select-disabled .select-label {
  @apply text-gray-500;
}
</style>