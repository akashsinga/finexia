<template>
  <div :class="['input-wrapper', { 'input-error': error, 'input-disabled': disabled, customClass }]">
    <label v-if="label" :for="id" class="input-label">
      {{ label }}
      <span v-if="required" class="input-required">*</span>
    </label>

    <div class="input-container">
      <div v-if="prefixIcon || $slots.prefix" class="input-prefix">
        <v-icon v-if="prefixIcon" :size="iconSize">{{ prefixIcon }}</v-icon>
        <slot v-else name="prefix"></slot>
      </div>

      <input :id="id" :type="type" :value="modelValue" :placeholder="placeholder" :disabled="disabled" :readonly="readonly" :required="required" :autofocus="autofocus" :class="['input-field', { 'has-prefix': prefixIcon || $slots.prefix, 'has-suffix': suffixIcon || $slots.suffix }]" @input="$emit('update:modelValue', $event.target.value)" @focus="$emit('focus', $event)" @blur="$emit('blur', $event)" />

      <div v-if="suffixIcon || clearable || $slots.suffix" class="input-suffix">
        <slot name="suffix"></slot>
        <v-icon v-if="clearable && modelValue" size="small" class="clear-icon" @click="clearInput">mdi-close-circle</v-icon>
        <v-icon v-else-if="suffixIcon" :size="iconSize">{{ suffixIcon }}</v-icon>
      </div>
    </div>

    <div v-if="error || hint" class="input-message">
      <span v-if="error" class="input-error-message">{{ error }}</span>
      <span v-else-if="hint" class="input-hint">{{ hint }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TextInput',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    id: {
      type: String,
      default() {
        return `input-${Math.random().toString(36).substring(2, 9)}`
      }
    },
    label: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'text',
      validator: (value) => ['text', 'password', 'email', 'number', 'tel', 'url', 'search', 'date', 'time', 'datetime-local'].includes(value)
    },
    placeholder: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    readonly: {
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
    prefixIcon: {
      type: String,
      default: ''
    },
    suffixIcon: {
      type: String,
      default: ''
    },
    iconSize: {
      type: String,
      default: 'small'
    },
    clearable: {
      type: Boolean,
      default: false
    },
    autofocus: {
      type: Boolean,
      default: false
    },
    customClass: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'focus', 'blur', 'clear'],
  methods: {
    clearInput() {
      this.$emit('update:modelValue', '');
      this.$emit('clear');
    }
  }
}
</script>

<style lang="postcss" scoped>
.input-wrapper {
  @apply w-full mb-4;
}

.input-label {
  @apply block text-sm font-medium text-gray-700 mb-1;
}

.input-required {
  @apply text-error ml-0.5;
}

.input-container {
  @apply relative flex items-center w-full;
}

.input-field {
  @apply w-full px-3 py-2 bg-white border border-gray-300 rounded-md text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed transition-colors duration-200;
}

.input-field.has-prefix {
  @apply pl-10;
}

.input-field.has-suffix {
  @apply pr-10;
}

.input-prefix,
.input-suffix {
  @apply absolute flex items-center justify-center h-full px-3 text-gray-500;
}

.input-prefix {
  @apply left-0;
}

.input-suffix {
  @apply right-0;
}

.clear-icon {
  @apply cursor-pointer text-gray-400 hover:text-gray-600 transition-colors;
}

.input-message {
  @apply mt-1 text-xs;
}

.input-error-message {
  @apply text-error;
}

.input-hint {
  @apply text-gray-500;
}

.input-error .input-field {
  @apply border-error focus:ring-error focus:border-error;
}

.input-disabled .input-label {
  @apply text-gray-500;
}
</style>