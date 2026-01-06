<template>
  <div class="time-distribution-chart">
    <!-- 图表标题和操作 -->
    <div class="chart-header">
      <div class="chart-title">
        <h3>{{ title }}</h3>
        <p class="chart-subtitle" v-if="subtitle">{{ subtitle }}</p>
      </div>
      <div class="chart-actions" v-if="showActions">
        <div class="view-toggle">
          <button
            class="view-btn"
            :class="{ active: viewMode === 'bar' }"
            @click="viewMode = 'bar'"
          >
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button
            class="view-btn"
            :class="{ active: viewMode === 'line' }"
            @click="viewMode = 'line'"
          >
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 12L7 8L11 12L15 8L21 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button
            class="view-btn"
            :class="{ active: viewMode === 'area' }"
            @click="viewMode = 'area'"
          >
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 12L7 8L11 12L15 8L21 14V18H3V12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
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
      :style="{ height: height }"
    ></div>

    <!-- 统计信息 -->
    <div class="chart-stats" v-if="showStats && stats">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">高峰时段</div>
          <div class="stat-value">{{ stats.peakHour }}:00</div>
          <div class="stat-desc">客流量最高</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">低谷时段</div>
          <div class="stat-value">{{ stats.valleyHour }}:00</div>
          <div class="stat-desc">客流量最低</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">平均客流量</div>
          <div class="stat-value">{{ formatNumber(stats.avgPassengers) }}</div>
          <div class="stat-desc">每小时平均</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">峰值比例</div>
          <div class="stat-value">{{ formatPercent(stats.peakRatio) }}</div>
          <div class="stat-desc">高峰/平均</div>
        </div>
      </div>
    </div>

    <!-- 时段分类 -->
    <div class="time-periods" v-if="showPeriods">
      <div class="periods-title">时段分类</div>
      <div class="periods-grid">
        <div
          v-for="period in timePeriods"
          :key="period.name"
          class="period-card"
          :class="period.class"
        >
          <div class="period-name">{{ period.name }}</div>
          <div class="period-time">{{ period.time }}</div>
          <div class="period-passengers">{{ formatNumber(period.passengers) }}</div>
          <div class="period-percent">{{ formatPercent(period.percent) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue';
import * as echarts from 'echarts';
import type { ECharts, EChartsOption } from 'echarts';
import type { TimeDistribution } from '@/types/passenger';

interface Props {
  // 数据
  data?: TimeDistribution[];
  // 图表配置
  title?: string;
  subtitle?: string;
  height?: string;
  // 显示选项
  showActions?: boolean;
  showStats?: boolean;
  showPeriods?: boolean;
  // 自定义配置
  customOptions?: Partial<EChartsOption>;
}

const props = withDefaults(defineProps<Props>(), {
  title: '客流时间分布',
  subtitle: '24小时客流分布情况',
  height: '400px',
  showActions: true,
  showStats: true,
  showPeriods: true,
  customOptions: () => ({}),
});

// 引用
const chartContainer = ref<HTMLElement | null>(null);
const chartInstance = ref<ECharts | null>(null);

// 状态
const viewMode = ref<'bar' | 'line' | 'area'>('bar');
const isLoading = ref(false);

// 计算属性
const stats = computed(() => {
  if (!props.data || props.data.length === 0) return null;

  const totalPassengers = props.data.reduce((sum, item) => sum + item.totalPassengers, 0);
  const avgPassengers = totalPassengers / props.data.length;

  // 找到高峰和低谷时段
  let peakHour = 0;
  let peakValue = 0;
  let valleyHour = 0;
  let valleyValue = Infinity;

  props.data.forEach(item => {
    if (item.totalPassengers > peakValue) {
      peakValue = item.totalPassengers;
      peakHour = item.hour;
    }
    if (item.totalPassengers < valleyValue) {
      valleyValue = item.totalPassengers;
      valleyHour = item.hour;
    }
  });

  return {
    peakHour,
    valleyHour,
    avgPassengers,
    peakRatio: peakValue / avgPassengers,
    totalPassengers,
  };
});

const timePeriods = computed(() => {
  if (!props.data) return [];

  // 定义时段
  const periods = [
    { name: '凌晨', start: 0, end: 6, class: 'period-night' },
    { name: '早高峰', start: 7, end: 9, class: 'period-morning' },
    { name: '日间', start: 10, end: 16, class: 'period-day' },
    { name: '晚高峰', start: 17, end: 19, class: 'period-evening' },
    { name: '夜间', start: 20, end: 23, class: 'period-night' },
  ];

  const totalPassengers = props.data.reduce((sum, item) => sum + item.totalPassengers, 0);

  return periods.map(period => {
    const periodData = props.data!.filter(item =>
      item.hour >= period.start && item.hour <= period.end
    );
    const passengers = periodData.reduce((sum, item) => sum + item.totalPassengers, 0);
    const percent = totalPassengers > 0 ? passengers / totalPassengers : 0;

    return {
      ...period,
      time: `${period.start}:00-${period.end}:00`,
      passengers,
      percent,
    };
  });
});

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万';
  }
  return Math.round(num).toLocaleString();
};

// 格式化百分比
const formatPercent = (num: number): string => {
  return (num * 100).toFixed(1) + '%';
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
        type: 'shadow',
        shadowStyle: {
          color: 'rgba(150, 150, 150, 0.1)',
        },
      },
      formatter: (params: any) => {
        const hour = params[0].axisValue;
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
            <div style="font-weight: bold; margin-bottom: 8px;">${hour}:00</div>
            ${values}
          </div>
        `;
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: props.showPeriods ? '25%' : '10%',
      top: '15%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 24 }, (_, i) => `${i}`),
      axisLine: {
        lineStyle: {
          color: '#dcdfe6',
        },
      },
      axisLabel: {
        color: '#606266',
        fontSize: 12,
        formatter: (value: string) => {
          const hour = parseInt(value);
          return hour % 3 === 0 ? `${hour}:00` : '';
        },
      },
      axisTick: {
        alignWithLabel: true,
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
          color: '#f0f0f0',
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

  // 准备数据
  const hours = Array.from({ length: 24 }, (_, i) => i);
  const inData = hours.map(hour => {
    const item = props.data!.find(d => d.hour === hour);
    return item ? item.passengersIn : 0;
  });
  const outData = hours.map(hour => {
    const item = props.data!.find(d => d.hour === hour);
    return item ? item.passengersOut : 0;
  });
  const totalData = hours.map(hour => {
    const item = props.data!.find(d => d.hour === hour);
    return item ? item.totalPassengers : 0;
  });

  // 根据视图模式构建系列
  let series: any[] = [];

  if (viewMode.value === 'bar') {
    // 柱状图模式
    series = [
      {
        name: '上客量',
        type: 'bar',
        data: inData,
        barWidth: '60%',
        itemStyle: {
          color: '#91cc75',
          borderRadius: [2, 2, 0, 0],
        },
        emphasis: {
          itemStyle: {
            color: '#73d13d',
          },
        },
      },
      {
        name: '下客量',
        type: 'bar',
        data: outData,
        barWidth: '60%',
        itemStyle: {
          color: '#fac858',
          borderRadius: [2, 2, 0, 0],
        },
        emphasis: {
          itemStyle: {
            color: '#faad14',
          },
        },
      },
      {
        name: '总客流量',
        type: 'line',
        data: totalData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 3,
          color: '#5470c6',
        },
        itemStyle: {
          color: '#5470c6',
          borderColor: '#fff',
          borderWidth: 2,
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            color: '#fff',
            borderColor: '#5470c6',
            borderWidth: 3,
            shadowBlur: 10,
            shadowColor: 'rgba(84, 112, 198, 0.5)',
          },
        },
      },
    ];
  } else if (viewMode.value === 'line') {
    // 折线图模式
    series = [
      {
        name: '上客量',
        type: 'line',
        data: inData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#91cc75',
        },
        itemStyle: {
          color: '#91cc75',
          borderColor: '#fff',
          borderWidth: 2,
        },
      },
      {
        name: '下客量',
        type: 'line',
        data: outData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#fac858',
        },
        itemStyle: {
          color: '#fac858',
          borderColor: '#fff',
          borderWidth: 2,
        },
      },
      {
        name: '总客流量',
        type: 'line',
        data: totalData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: '#5470c6',
        },
        itemStyle: {
          color: '#5470c6',
          borderColor: '#fff',
          borderWidth: 2,
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            color: '#fff',
            borderColor: '#5470c6',
            borderWidth: 3,
            shadowBlur: 10,
            shadowColor: 'rgba(84, 112, 198, 0.5)',
          },
        },
      },
    ];
  } else {
    // 面积图模式
    series = [
      {
        name: '上客量',
        type: 'line',
        data: inData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#91cc75',
        },
        itemStyle: {
          color: '#91cc75',
          borderColor: '#fff',
          borderWidth: 2,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(145, 204, 117, 0.3)' },
            { offset: 1, color: 'rgba(145, 204, 117, 0.05)' },
          ]),
        },
      },
      {
        name: '下客量',
        type: 'line',
        data: outData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          width: 2,
          color: '#fac858',
        },
        itemStyle: {
          color: '#fac858',
          borderColor: '#fff',
          borderWidth: 2,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(250, 200, 88, 0.3)' },
            { offset: 1, color: 'rgba(250, 200, 88, 0.05)' },
          ]),
        },
      },
      {
        name: '总客流量',
        type: 'line',
        data: totalData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: '#5470c6',
        },
        itemStyle: {
          color: '#5470c6',
          borderColor: '#fff',
          borderWidth: 2,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(84, 112, 198, 0.3)' },
            { offset: 1, color: 'rgba(84, 112, 198, 0.05)' },
          ]),
        },
        emphasis: {
          focus: 'series',
          itemStyle: {
            color: '#fff',
            borderColor: '#5470c6',
            borderWidth: 3,
            shadowBlur: 10,
            shadowColor: 'rgba(84, 112, 198, 0.5)',
          },
        },
      },
    ];
  }

  // 更新图表配置
  const updateOptions: EChartsOption = {
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
    legend: {
      type: 'scroll',
      bottom: 0,
      textStyle: {
        color: '#606266',
        fontSize: 12,
      },
    },
  };

  chartInstance.value.setOption(updateOptions, true);
};

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance.value) {
    chartInstance.value.resize();
  }
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
  link.download = `客流时间分布_${new Date().toISOString().slice(0, 10)}.png`;
  link.click();
};

// 监听数据变化
watch(() => props.data, (newData) => {
  if (newData) {
    updateChartData();
  }
}, { deep: true });

// 监听视图模式变化
watch(viewMode, () => {
  if (props.data) {
    updateChartData();
  }
});

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
.time-distribution-chart {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
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
  align-items: center;
  gap: 12px;
}

.view-toggle {
  display: flex;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.view-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: #fff;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: #f5f7fa;
  }

  &.active {
    background: #409eff;
    color: #fff;
  }

  svg {
    width: 16px;
    height: 16px;
  }
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
}

.chart-stats {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-card {
  padding: 12px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-desc {
  font-size: 11px;
  color: #c0c4cc;
}

.time-periods {
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
}

.periods-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.periods-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.period-card {
  padding: 12px;
  border-radius: 6px;
  background: #f5f7fa;
  transition: all 0.2s ease;

  &.period-morning {
    background: #f0f9ff;
    border-left: 3px solid #409eff;
  }

  &.period-day {
    background: #fdf6ec;
    border-left: 3px solid #e6a23c;
  }

  &.period-evening {
    background: #fef0f0;
    border-left: 3px solid #f56c6c;
  }

  &.period-night {
    background: #f4f4f5;
    border-left: 3px solid #909399;
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
}

.period-name {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.period-time {
  font-size: 11px;
  color: #909399;
  margin-bottom: 8px;
}

.period-passengers {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 2px;
}

.period-percent {
  font-size: 11px;
  color: #67c23a;
}
</style>