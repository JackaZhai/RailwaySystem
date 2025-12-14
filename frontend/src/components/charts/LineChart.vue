<script setup lang="ts">
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'
import type { EChartsOption } from 'echarts'
import { CHART_CONFIG } from '@/config'

// Props
const props = withDefaults(defineProps<{
  // 数据
  data: Array<{
    name: string
    value: number
    date?: string
    [key: string]: any
  }>
  series?: Array<{
    name: string
    data: number[]
    type?: string
    [key: string]: any
  }>
  xAxisData?: string[]

  // 配置
  title?: string
  subtext?: string
  xAxisName?: string
  yAxisName?: string
  smooth?: boolean
  showSymbol?: boolean
  areaStyle?: boolean
  stack?: boolean
  grid?: any
  colors?: string[]
  legend?: boolean
  tooltip?: any
  toolbox?: boolean

  // BaseChart Props
  chartId?: string
  className?: string
  loading?: boolean
  autoresize?: boolean
}>(), {
  data: () => [],
  series: () => [],
  xAxisData: () => [],
  title: '',
  subtext: '',
  xAxisName: '',
  yAxisName: '',
  smooth: true,
  showSymbol: false,
  areaStyle: false,
  stack: false,
  grid: () => ({
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true,
  }),
  colors: () => CHART_CONFIG.COLOR_SCHEME,
  legend: true,
  tooltip: () => ({
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      label: {
        backgroundColor: '#6a7985',
      },
    },
  }),
  toolbox: true,
  chartId: 'line-chart',
  className: '',
  loading: false,
  autoresize: true,
})

// 计算图表配置
const chartOption = computed<EChartsOption>(() => {
  const isMultiSeries = props.series && props.series.length > 0
  const xAxisData = props.xAxisData.length > 0
    ? props.xAxisData
    : props.data.map(item => item.name || item.date || '')

  // 处理系列数据
  const seriesData = isMultiSeries
    ? props.series!.map((seriesItem, index) => ({
        ...seriesItem,
        name: seriesItem.name,
        type: (seriesItem.type || 'line') as 'line' | 'bar' | 'scatter' | 'pie' | 'radar' | 'map' | 'treemap' | 'graph' | 'gauge' | 'funnel' | 'parallel' | 'sankey' | 'boxplot' | 'candlestick' | 'effectScatter' | 'lines' | 'heatmap' | 'pictorialBar' | 'themeRiver' | 'custom',
        data: seriesItem.data,
        smooth: props.smooth,
        showSymbol: props.showSymbol,
        areaStyle: props.areaStyle ? {} : undefined,
        stack: props.stack ? '总量' : undefined,
        itemStyle: {
          ...seriesItem.itemStyle,
          color: props.colors[index % props.colors.length] || CHART_CONFIG.COLOR_SCHEME[index % CHART_CONFIG.COLOR_SCHEME.length],
        },
        lineStyle: {
          width: 2,
          ...seriesItem.lineStyle,
        },
      }))
    : [
        {
          name: props.title,
          type: 'line' as const,
          data: props.data.map(item => item.value),
          smooth: props.smooth,
          showSymbol: props.showSymbol,
          areaStyle: props.areaStyle ? {} : undefined,
          stack: props.stack ? '总量' : undefined,
          itemStyle: {
            color: props.colors[0] || CHART_CONFIG.COLOR_SCHEME[0],
          },
          lineStyle: {
            width: 2,
          },
        },
      ]

  return {
    title: props.title
      ? {
          text: props.title,
          subtext: props.subtext,
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold',
          },
        }
      : undefined,

    tooltip: props.tooltip,

    legend: props.legend
      ? {
          data: isMultiSeries
            ? props.series.map(s => s.name)
            : [props.title],
          top: 30,
        }
      : undefined,

    grid: props.grid,

    toolbox: props.toolbox
      ? {
          feature: {
            saveAsImage: {
              title: '保存为图片',
            },
            dataView: {
              title: '数据视图',
              readOnly: true,
            },
            restore: {
              title: '还原',
            },
            dataZoom: {
              title: {
                zoom: '区域缩放',
                back: '缩放还原',
              },
            },
            magicType: {
              type: ['line', 'bar'],
              title: {
                line: '切换为折线图',
                bar: '切换为柱状图',
              },
            },
          },
          right: 20,
        }
      : undefined,

    xAxis: {
      type: 'category' as const,
      data: xAxisData,
      name: props.xAxisName,
      nameLocation: 'center' as const,
      nameGap: 25,
      axisLine: {
        lineStyle: {
          color: '#ccc',
        },
      },
      axisTick: {
        alignWithLabel: true,
      },
    },

    yAxis: {
      type: 'value' as const,
      name: props.yAxisName,
      axisLine: {
        lineStyle: {
          color: '#ccc',
        },
      },
      splitLine: {
        lineStyle: {
          type: 'dashed' as const,
          color: '#e0e0e0',
        },
      },
    },

    series: seriesData as any,

    animation: CHART_CONFIG.ANIMATION as any,
  }
})

// Emits
const emit = defineEmits<{
  'chart-ready': [chart: any]
  'chart-click': [params: any]
}>()

// 处理BaseChart事件
const handleChartReady = (chart: any) => {
  emit('chart-ready', chart)
}

const handleChartClick = (params: any) => {
  emit('chart-click', params)
}
</script>

<template>
  <BaseChart
    :chart-id="chartId"
    :class-name="className"
    :option="chartOption"
    :loading="loading"
    :autoresize="autoresize"
    @chart-ready="handleChartReady"
    @chart-click="handleChartClick"
  />
</template>

<style scoped>
.line-chart {
  width: 100%;
  height: 100%;
}
</style>