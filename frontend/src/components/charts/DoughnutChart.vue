<template>
  <div class="chart-container">
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

// Register ECharts components
use([CanvasRenderer, PieChart, TooltipComponent, LegendComponent])

export default {
  name: 'DoughnutChartComponent',
  components: {
    VChart
  },
  props: {
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: function () {
        return {}
      }
    }
  },
  computed: {
    chartOption: function () {
      // Convert Chart.js format to ECharts format
      const dataset = this.chartData.datasets[0]

      return {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          show: false
        },
        series: [
          {
            name: 'Predictions',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '14',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: this.chartData.labels.map((label, index) => ({
              value: dataset.data[index],
              name: label,
              itemStyle: {
                color: dataset.backgroundColor[index]
              }
            }))
          }
        ],
        ...this.options
      }
    }
  }
}
</script>

<style lang="postcss" scoped>
.chart-container {
  @apply w-full h-full relative;
}

.chart {
  @apply w-full h-full;
}
</style>