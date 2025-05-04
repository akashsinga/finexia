<template>
  <div class="card" :class="[{ 'min-h-full': fullHeight }, cardClass]">
    <div v-if="title || $slots.actions" class="card-header">
      <h3 class="card-title">{{ title }}</h3>
      <div class="card-actions">
        <slot name="actions"></slot>
      </div>
    </div>
    <div class="card-body" :class="{ 'p-0': noPadding }">
      <div v-if="loading" class="flex justify-center items-center py-8">
        <v-progress-circular indeterminate></v-progress-circular>
      </div>
      <slot v-else></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardContainer',
  props: {
    title: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    },
    noPadding: {
      type: Boolean,
      default: false
    },
    fullHeight: {
      type: Boolean,
      default: false
    },
    cardClass: {
      type: String,
      default: ''
    }
  }
}
</script>

<style lang="postcss" scoped>
.card {
  @apply bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col;
}

.card-header {
  @apply flex justify-between items-center px-4 py-3 border-b border-gray-200;
}

.card-title {
  @apply text-base font-medium;
}

.card-actions {
  @apply flex items-center space-x-2;
}

.card-body {
  @apply p-4 flex-grow;
}
</style>