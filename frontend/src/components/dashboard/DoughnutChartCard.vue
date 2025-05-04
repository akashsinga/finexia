<template>
  <CardContainer :title="title" :loading="loading" :full-height="true" class="min-h-[350px]">
    <template #actions>
      <v-btn size="small" variant="text" @click="$emit('refresh')">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
    </template>

    <div class="h-[280px] flex flex-col justify-center">
      <div class="flex justify-center mb-4">
        <DoughnutChart :chart-data="chartData" :options="chartOptions" />
      </div>
      <slot name="chart-details"></slot>
    </div>
  </CardContainer>
</template>

<script>
import CardContainer from '@/components/common/CardContainer.vue'
import DoughnutChart from '@/components/charts/DoughnutChart.vue'

export default {
  name: 'DoughnutChartCard',
  components: {
    CardContainer,
    DoughnutChart
  },
  props: {
    title: {
      type: String,
      required: true
    },
    chartData: {
      type: Object,
      required: true
    },
    chartOptions: {
      type: Object,
      default: function () {
        return {}
      }
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh']
}
</script>