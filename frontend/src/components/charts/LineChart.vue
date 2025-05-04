<template>
  <div class="chart-container">
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script>
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

// Register ECharts components
use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

export default {
  name: 'LineChartComponent',
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
    },
    isPercentage: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    chartOption() {
      const dataset = this.chartData.datasets[0]

      const defaultOptions = {
        tooltip: {
          trigger: 'axis',
          formatter: (params) => {
            const value = params[0].value
            return this.isPercentage
              ? `${params[0].name}: ${(value * 100).toFixed(1)}%`
              : `${params[0].name}: ₹${value.toFixed(2)}`
          }
        },
        textStyle: {
          fontFamily: 'Inter'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.chartData.labels || []
        },
        yAxis: {
          type: 'value',
          min: this.isPercentage ? 0 : 'dataMin',
          max: this.isPercentage ? 1 : 'dataMax',
          axisLabel: {
            formatter: (value) =>
              this.isPercentage ? `${(value * 100).toFixed(0)}%` : `₹${value.toFixed(0)}`
          }
        },
        series: [
          {
            name: dataset.label || 'Data',
            type: 'line',
            stack: 'Total',
            data: dataset.data || [],
            areaStyle: {
              color: dataset.backgroundColor || 'rgba(30, 58, 138, 0.1)'
            },
            lineStyle: {
              color: dataset.borderColor || '#1E3A8A',
              width: 2
            },
            smooth: true,
            symbol: 'circle',
            symbolSize: 5,
            itemStyle: {
              color: dataset.borderColor || '#1E3A8A'
            }
          }
        ]
      }

      // Merge with external options
      return {
        ...defaultOptions,
        ...this.options,
        yAxis: {
          ...defaultOptions.yAxis,
          ...(this.options.yAxis || {}),
          axisLabel: {
            ...defaultOptions.yAxis.axisLabel,
            ...(this.options.yAxis?.axisLabel || {})
          }
        },
        tooltip: {
          ...defaultOptions.tooltip,
          ...(this.options.tooltip || {})
        }
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
