<template>
  <div class="flow-trend-chart">
    <!-- 图表标题和操作 -->
    <div v-if="showHeader" class="chart-header">
      <div class="chart-title">
        <h3>{{ title }}</h3>
        <p class="chart-subtitle" v-if="subtitle">{{ subtitle }}</p>
      </div>
      <div class="chart-actions" v-if="showActions">
        <button
          class="btn-icon"
          :title="isFullscreen ? '退出全屏' : '全屏查看'"
          @click="toggleFullscreen"
        >
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path v-if="!isFullscreen" d="M8 3H5C4.46957 3 3.96086 3.21071 3.58579 3.58579C3.21071 3.96086 3 4.46957 3 5V8M21 8V5C21 4.46957 20.7893 3.96086 20.4142 3.58579C20.0391 3.21071 19.5304 3 19 3H16M16 21H19C19.5304 21 20.0391 20.7893 20.4142 20.4142C20.7893 20.0391 21 19.5304 21 19V16M3 16V19C3 19.5304 3.21071 20.0391 3.58579 20.4142C3.96086 20.7893 4.46957 21 5 21H8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path v-else d="M9 9L4 4M4 9L9 4M15 15L20 20M20 15L15 20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="btn-icon" title="下载图表" @click="downloadChart">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 图表容器 -->
    <div
      ref="chartContainer"
      class="chart-container"
      :class="{ 'fullscreen': isFullscreen }"
      :style="{ height: height }"
    ></div>

    <!-- 图表说明 -->
    <div class="chart-footer" v-if="showFooter">
      <div class="chart-stats" v-if="stats">
        <div class="stat-item">
          <span class="stat-label">总计:</span>
          <span class="stat-value">{{ formatNumber(stats.total) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">平均:</span>
          <span class="stat-value">{{ formatNumber(stats.average) }}</span>
        </div>
        <div class="stat-item" v-if="stats.growthRate !== undefined">
          <span class="stat-label">增长率:</span>
          <span class="stat-value" :class="getGrowthRateClass(stats.growthRate)">
            {{ formatPercent(stats.growthRate) }}
          </span>
        </div>
      </div>
      <div class="chart-legend" v-if="showLegend">
        <div class="legend-item" v-for="item in legendItems" :key="item.name">
          <span class="legend-color" :style="{ backgroundColor: item.color }"></span>
          <span class="legend-text">{{ item.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts';
import type { ECharts, EChartsOption } from 'echarts';
import type { FlowTrendData, FlowTrendPoint } from '@/types/passenger';

interface Props {
  // 数据
  data?: FlowTrendData | null;
  // 图表配置
  title?: string;
  subtitle?: string;
  height?: string;
  // 显示选项
  showActions?: boolean;
  showFooter?: boolean;
  showLegend?: boolean;
  showHeader?: boolean;
  // 自定义配置
  customOptions?: Partial<EChartsOption>;
}

const props = withDefaults(defineProps<Props>(), {
  title: '客流趋势分析',
  subtitle: '',
  height: '400px',
  showActions: true,
  showFooter: true,
  showLegend: true,
  showHeader: true,
  customOptions: () => ({}),
});

// 引用
const chartContainer = ref<HTMLElement | null>(null);
const chartInstance = ref<ECharts | null>(null);

// 状态
const isFullscreen = ref(false);
const isLoading = ref(false);

// 计算属性
const stats = computed(() => {
  if (!props.data) return null;
  return {
    total: props.data.total,
    average: props.data.average,
    max: props.data.max,
    min: props.data.min,
    growthRate: props.data.growthRate,
  };
});

const macaronPalette = [
  '#F4A7B9',
  '#A7C7E7',
  '#B8E0D2',
  '#FFD6A5',
  '#CDB4DB',
  '#FFB7B2',
  '#BDE0FE',
];

const legendItems = computed(() => {
  const seriesData = props.data?.data || [];
  const categories = [...new Set(seriesData.map(item => item.category).filter(Boolean))];
  if (categories.length > 0) {
    return categories.map((name, index) => ({
      name: name as string,
      color: macaronPalette[index % macaronPalette.length]
    }));
  }
  return [{ name: '客流量', color: macaronPalette[0] }];
});

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万';
  }
  return num.toLocaleString();
};

// 格式化百分比
const formatPercent = (num: number): string => {
  return (num * 100).toFixed(1) + '%';
};

// 获取增长率样式类
const getGrowthRateClass = (rate: number): string => {
  if (rate > 0) return 'positive';
  if (rate < 0) return 'negative';
  return 'neutral';
};

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return;

  // 销毁旧实例
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }

  // 创建新实例
  chartInstance.value = echarts.init(chartContainer.value);

  // 设置默认配置
  const defaultOptions: EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: {
        color: '#303133',
      },
      axisPointer: {
        type: 'line',
        lineStyle: {
          color: 'rgba(244, 167, 185, 0.4)',
          width: 2,
        },
      },
      formatter: (params: any) => {
        const date = params[0].axisValue;
        const values = params.map((item: any) => {
          return `
            <div style="display: flex; align-items: center; margin: 2px 0;">
              <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: ${item.color}; margin-right: 8px;"></span>
              <span style="flex: 1;">${item.seriesName}:</span>
              <span style="font-weight: bold; margin-left: 8px;">${formatNumber(item.value)}</span>
            </div>
          `;
        }).join('');
        return `
          <div style="padding: 8px;">
            <div style="font-weight: bold; margin-bottom: 8px;">${date}</div>
            ${values}
          </div>
        `;
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#e6e8ef',
        },
      },
      axisLabel: {
        color: '#7b8190',
        fontSize: 12,
      },
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        color: '#606266',
        fontSize: 12,
        formatter: (value: number) => {
          if (value >= 10000) {
            return (value / 10000).toFixed(0) + '万';
          }
          return value.toString();
        },
      },
      splitLine: {
        lineStyle: {
          color: '#f2f3f7',
          type: 'dashed',
        },
      },
    },
    series: [],
    animation: true,
    animationDuration: 1000,
    animationEasing: 'cubicOut',
  };

  // 合并自定义配置
  const options = { ...defaultOptions, ...props.customOptions };
  chartInstance.value.setOption(options);

  // 添加resize监听
  window.addEventListener('resize', handleResize);
};

// 更新图表数据
const updateChartData = () => {
  if (!chartInstance.value || !props.data) return;

  const { data, granularity } = props.data;

  // 准备数据
  const xAxisData = data.map(item => item.time);
  const seriesData = data.map(item => item.value);

  // 构建系列配置
  const primaryColor = macaronPalette[0];
  const series: any[] = [
    {
      name: '客流量',
      type: 'line',
      data: seriesData,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: {
        width: 3,
        color: primaryColor,
        shadowBlur: 8,
        shadowColor: 'rgba(244, 167, 185, 0.35)',
      },
      itemStyle: {
        color: primaryColor,
        borderColor: '#fff',
        borderWidth: 2,
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(244, 167, 185, 0.35)' },
          { offset: 1, color: 'rgba(244, 167, 185, 0.05)' },
        ]),
      },
      emphasis: {
        focus: 'series',
        itemStyle: {
          color: '#fff',
          borderColor: primaryColor,
          borderWidth: 3,
          shadowBlur: 10,
          shadowColor: 'rgba(244, 167, 185, 0.45)',
        },
      },
    },
  ];

  // 如果有分类数据，添加多条线
  const categories = [...new Set(data.map(item => item.category).filter(Boolean))];
  if (categories.length > 0) {
    // 清除原有系列
    series.length = 0;

    // 为每个分类创建系列
    const colors = macaronPalette;

    categories.forEach((category, index) => {
      const categoryData = data.filter(item => item.category === category);
      const categorySeriesData = categoryData.map(item => item.value);

      series.push({
        name: category || `分类${index + 1}`,
        type: 'line',
        data: categorySeriesData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: colors[index % colors.length],
        },
        itemStyle: {
          color: colors[index % colors.length],
          borderColor: '#fff',
          borderWidth: 2,
        },
        areaStyle: {
          opacity: 0.12
        }
      });
    });
  }

  // 更新图表配置
  const updateOptions: EChartsOption = {
    xAxis: {
      data: xAxisData,
      axisLabel: {
        formatter: (value: string) => {
          // 根据粒度格式化时间标签
          switch (granularity) {
            case 'hour':
              return value.slice(-5); // 显示 HH:mm
            case 'day':
              return value.slice(5); // 显示 MM-DD
            case 'month':
              return value.slice(0, 7); // 显示 YYYY-MM
            default:
              return value;
          }
        },
      },
    },
    series,
    title: {
      text: props.title,
      subtext: props.subtitle,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#303133',
      },
      subtextStyle: {
        fontSize: 12,
        color: '#909399',
      },
    },
    legend: props.showLegend ? {
      type: 'scroll',
      bottom: 0,
      textStyle: {
        color: '#606266',
        fontSize: 12,
      },
    } : undefined,
  };

  chartInstance.value.setOption(updateOptions);
  chartInstance.value.resize();
};

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance.value) {
    chartInstance.value.resize();
  }
};

// 切换全屏
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value;
  nextTick(() => {
    handleResize();
  });
};

// 下载图表
const downloadChart = () => {
  if (!chartInstance.value) return;

  const url = chartInstance.value.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: '#fff',
  });

  const link = document.createElement('a');
  link.href = url;
  link.download = `客流趋势图表_${new Date().toISOString().slice(0, 10)}.png`;
  link.click();
};

// 监听数据变化
watch(() => props.data, (newData) => {
  if (newData) {
    updateChartData();
  }
}, { deep: true });

// 生命周期
onMounted(() => {
  initChart();
  if (props.data) {
    updateChartData();
  }
});

onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped lang="scss">
.flow-trend-chart {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;

  &.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 9999;
    border-radius: 0;
  }
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.chart-title {
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }

  .chart-subtitle {
    margin: 4px 0 0;
    font-size: 12px;
    color: #909399;
  }
}

.chart-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #c0c4cc;
    background: #f5f7fa;
  }

  &:active {
    border-color: #409eff;
    color: #409eff;
  }

  svg {
    width: 16px;
    height: 16px;
  }
}

.chart-container {
  width: 100%;
  transition: height 0.3s ease;

  &.fullscreen {
    height: calc(100vh - 120px) !important;
  }
}

.chart-footer {
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.chart-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;

  .stat-item {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .stat-label {
    font-size: 12px;
    color: #909399;
  }

  .stat-value {
    font-size: 14px;
    font-weight: 600;
    color: #303133;

    &.positive {
      color: #67c23a;
    }

    &.negative {
      color: #f56c6c;
    }

    &.neutral {
      color: #909399;
    }
  }
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .legend-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
  }

  .legend-text {
    font-size: 12px;
    color: #606266;
  }
}
</style>
