// src/store/model.store.js
import { defineStore } from 'pinia';
import { api } from '@/plugins';

export const useModelStore = defineStore('model', {
  state: () => ({
    topModels: [],
    selectedModelHistory: [],
    selectedModelSymbol: null,
    loading: false,
    historyLoading: false
  }),

  getters: {
    performanceChartOption() {
      if (!this.topModels.length) return null;

      // Prepare chart data from the top models
      const symbols = this.topModels.map(model => model.trading_symbol);
      const metricData = this.topModels.map(model => (model[this.selectedMetric || 'f1_score'] * 100).toFixed(1));
      const metricColors = {
        'f1_score': '#FBBF24', // warning
        'accuracy': '#1E3A8A', // primary
        'precision': '#60A5FA', // info
        'recall': '#4ADE80'  // success
      };

      // Create the chart option
      return {
        textStyle: {
          fontFamily: 'Inter'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function (params) {
            return `<div style="font-weight:bold">${params[0].name}</div>
                 <div style="display:flex;align-items:center;gap:5px;margin:3px 0">
                   <span style="display:inline-block;width:10px;height:10px;background-color:${params[0].color}"></span>
                   <span>${params[0].value}%</span>
                 </div>`;
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '10px',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: 'Percentage (%)',
          nameLocation: 'middle',
          nameGap: 30,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        yAxis: {
          type: 'category',
          data: symbols,
          axisLabel: {
            formatter: function (value) {
              return value.length > 8 ? value.substring(0, 8) + '...' : value;
            }
          }
        },
        series: [
          {
            name: this.selectedMetric || 'f1_score',
            type: 'bar',
            data: metricData,
            itemStyle: { color: metricColors[this.selectedMetric || 'f1_score'] || '#1E3A8A' },
            emphasis: {
              focus: 'series'
            },
            label: {
              show: true,
              position: 'right',
              formatter: '{c}%',
              fontSize: 12
            }
          }
        ]
      };
    },

    historyChartOption() {
      if (!this.selectedModelHistory?.length) {
        return null;
      }

      // Sort by date
      const sortedHistory = [...this.selectedModelHistory].sort((a, b) =>
        new Date(a.evaluation_date) - new Date(b.evaluation_date)
      );

      // Prepare data for chart
      const dates = sortedHistory.map(item => this.formatDate(item.evaluation_date, 'MMM D, YY'));
      const accuracyData = sortedHistory.map(item => (item.accuracy * 100).toFixed(1));
      const precisionData = sortedHistory.map(item => (item.precision * 100).toFixed(1));
      const recallData = sortedHistory.map(item => (item.recall * 100).toFixed(1));
      const f1Data = sortedHistory.map(item => (item.f1_score * 100).toFixed(1));

      return {
        tooltip: {
          trigger: 'axis',
          formatter: function (params) {
            let tooltip = `<div style="font-weight:bold">${params[0].name}</div>`;
            params.forEach(param => {
              tooltip += `<div style="display:flex;justify-content:space-between;margin:3px 0">
              <span style="margin-right:15px;display:inline-block;width:10px;height:10px;border-radius:50%;background-color:${param.color}"></span>
              <span style="flex:1">${param.seriesName}:</span>
              <span style="font-weight:bold">${param.value}%</span>
            </div>`;
            });
            return tooltip;
          }
        },
        legend: {
          data: ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
          top: 0
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          top: '40px',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          name: 'Percentage (%)',
          min: 0,
          max: 100,
          axisLabel: {
            formatter: '{value}%'
          }
        },
        dataZoom: [
          {
            type: 'inside',
            start: 0,
            end: 100
          },
          {
            start: 0,
            end: 100
          }
        ],
        series: [
          {
            name: 'Accuracy',
            type: 'line',
            data: accuracyData,
            itemStyle: { color: '#1E3A8A' },
            lineStyle: { width: 2 },
            symbol: 'circle',
            symbolSize: 6
          },
          {
            name: 'Precision',
            type: 'line',
            data: precisionData,
            itemStyle: { color: '#60A5FA' },
            lineStyle: { width: 2 },
            symbol: 'circle',
            symbolSize: 6
          },
          {
            name: 'Recall',
            type: 'line',
            data: recallData,
            itemStyle: { color: '#4ADE80' },
            lineStyle: { width: 2 },
            symbol: 'circle',
            symbolSize: 6
          },
          {
            name: 'F1 Score',
            type: 'line',
            data: f1Data,
            itemStyle: { color: '#FBBF24' },
            lineStyle: { width: 2 },
            symbol: 'circle',
            symbolSize: 6
          }
        ]
      };
    }
  },

  actions: {
    async fetchModelPerformance(topN = 5, metric = 'f1_score', foEligible = true) {
      this.loading = true;
      try {
        const response = await api.post('/models/performance', { top_n: topN, metric, fo_eligible: foEligible });
        this.topModels = (response.data || []).map(model => ({ ...model, retraining: false }));
        return this.topModels;
      } catch (error) {
        console.error('Error fetching model performance:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchModelHistory(symbol) {
      this.historyLoading = true;
      this.selectedModelSymbol = symbol;

      try {
        const response = await api.get(`/models/${symbol}/history`);
        this.selectedModelHistory = response.data || [];
        return this.selectedModelHistory;
      } catch (error) {
        console.error(`Error fetching history for ${symbol}:`, error);
        throw error;
      } finally {
        this.historyLoading = false;
      }
    },

    async retrainModel(symbol) {
      // Find the model in the array and update its retraining status
      const modelIndex = this.topModels.findIndex(model => model.trading_symbol === symbol);
      if (modelIndex !== -1) {
        this.topModels[modelIndex].retraining = true;
      }

      try {
        await api.post(`/models/train/${symbol}`, {
          force_retrain: true
        });
        return true;
      } catch (error) {
        console.error(`Error retraining model for ${symbol}:`, error);
        throw error;
      } finally {
        if (modelIndex !== -1) {
          this.topModels[modelIndex].retraining = false;
        }
      }
    },

    // Utility methods
    formatDate(dateString, format = 'MMM D, YYYY') {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: format.includes('Y') ? 'numeric' : undefined,
        month: 'short',
        day: 'numeric'
      });
    },

    formatPercentage(value) {
      if (value === null || value === undefined) return 'N/A';
      return (value * 100).toFixed(1) + '%';
    },

    exportModelData(models) {
      // Generate CSV data
      const headers = ['Symbol', 'Accuracy', 'Precision', 'Recall', 'F1 Score', 'Success Count', 'Total Count', 'Last Evaluated'];
      const csvRows = [];

      // Add headers
      csvRows.push(headers.join(','));

      // Add data rows
      models.forEach(model => {
        const row = [
          model.trading_symbol,
          (model.accuracy * 100).toFixed(2) + '%',
          (model.precision * 100).toFixed(2) + '%',
          (model.recall * 100).toFixed(2) + '%',
          (model.f1_score * 100).toFixed(2) + '%',
          model.successful_count,
          model.predictions_count,
          this.formatDate(model.evaluation_date)
        ];
        csvRows.push(row.join(','));
      });

      // Create CSV content
      return csvRows.join('\n');
    }
  }
});