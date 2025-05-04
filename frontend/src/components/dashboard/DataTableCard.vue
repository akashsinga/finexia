<template>
  <CardContainer :title="title" :loading="loading" :full-height="true" :no-padding="true" class="min-h-[400px]">
    <template #actions>
      <v-btn size="small" variant="text" @click="$emit('refresh')">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
      <v-btn size="small" variant="text" @click="$emit('view-all')">
        <v-icon>mdi-arrow-right</v-icon>
      </v-btn>
    </template>

    <v-table density="compact">
      <thead>
        <tr>
          <th v-for="(header, index) in headers" :key="index">{{ header.text }}</th>
        </tr>
      </thead>
      <tbody>
        <slot></slot>
        <tr v-if="isEmpty">
          <td :colspan="headers.length" class="text-center text-gray-500 py-4">{{ emptyMessage }}</td>
        </tr>
      </tbody>
    </v-table>
  </CardContainer>
</template>

<script>
import CardContainer from '@/components/common/CardContainer.vue'

export default {
  name: 'DataTableCard',
  components: {
    CardContainer
  },
  props: {
    title: {
      type: String,
      required: true
    },
    headers: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    isEmpty: {
      type: Boolean,
      default: false
    },
    emptyMessage: {
      type: String,
      default: 'No data available'
    }
  },
  emits: ['refresh', 'view-all']
}
</script>