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
      <LineChart :chart-data="chartData" :isPercentage="isPercentage" :options="mergedOptions" />
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
    },
    isPercentage: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    // Merge default options with provided options
    mergedOptions() {
      const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 0,
            max: 1,
            ticks: {
              callback: function (value) {
                return (value * 100) + '%';
              }
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return 'Accuracy: ' + (context.parsed.y * 100).toFixed(1) + '%';
              }
            }
          }
        }
      };

      // Deep merge the default options with provided options
      return this.deepMerge(defaultOptions, this.chartOptions);
    }
  },
  methods: {
    // Deep merge utility for objects
    deepMerge(target, source) {
      const output = { ...target };

      if (this.isObject(target) && this.isObject(source)) {
        Object.keys(source).forEach(key => {
          if (this.isObject(source[key])) {
            if (!(key in target)) {
              Object.assign(output, { [key]: source[key] });
            } else {
              output[key] = this.deepMerge(target[key], source[key]);
            }
          } else {
            Object.assign(output, { [key]: source[key] });
          }
        });
      }

      return output;
    },

    isObject(item) {
      return (item && typeof item === 'object' && !Array.isArray(item));
    }
  },
  emits: ['refresh', 'period-change']
}
</script>