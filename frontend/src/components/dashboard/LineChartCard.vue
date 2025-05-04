<template>
  <CardContainer :title="title" :loading="loading" :full-height="true" class="min-h-[350px]">
    <template #actions>
      <v-btn size="small" variant="text" @click="$emit('refresh')">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>
      <v-menu v-if="periods.length > 0">
        <template v-slot:activator="{ props }">
          <v-btn size="small" v-bind="props" variant="text">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item v-for="(period, i) in periods" :key="i" @click="$emit('period-change', period.value)">
            <v-list-item-title>{{ period.label }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>

    <div class="h-[280px]">
      <LineChart :chart-data="chartData" :options="chartOptions" />
    </div>
  </CardContainer>
</template>

<script>
import CardContainer from '@/components/common/CardContainer.vue'
import LineChart from '@/components/charts/LineChart.vue'

export default {
  name: 'LineChartCard',
  components: {
    CardContainer,
    LineChart
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
    },
    periods: {
      type: Array,
      default: function () {
        return []
      }
    }
  },
  emits: ['refresh', 'period-change']
}
</script>