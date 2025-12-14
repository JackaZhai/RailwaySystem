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
    [key: string]: any
  }>

  // 配置
  title?: string
  subtext?: string
  radius?: [string, string] | string
  roseType?: 'radius' | 'area' | false
  showLabel?: boolean
  showLegend?: boolean
  legendPosition?: 'top' | 'bottom' | 'left' | 'right'
  colors?: string[]
  tooltip?: any
  toolbox?: boolean

  // BaseChart Props
  chartId?: string
  className?: string
  loading?: boolean
  autoresize?: boolean
}>(), {
  data: () => [],
  title: '',
  subtext: '',
  radius: () => ['40%', '70%'],
  roseType: false,
  showLabel: true,
  showLegend: true,
  legendPosition: 'top',
  colors: () => CHART_CONFIG.COLOR_SCHEME,
  tooltip: () => ({
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)',
  }),
  toolbox: false,
  chartId: 'pie-chart',
  className: '',
  loading: false,
  autoresize: true,
})

// 计算图表配置
const chartOption = computed<EChartsOption>(() => {
  // 计算总数用于显示百分比（保留计算逻辑，但移除未使用的变量）
  props.data.reduce((sum, item) => sum + item.value, 0)

  // 根据图例位置设置布局
  const legendConfig = props.showLegend
    ? {
        type: 'scroll',
        orient: (props.legendPosition === 'left' || props.legendPosition === 'right' ? 'vertical' : 'horizontal') as 'vertical' | 'horizontal',
        left: props.legendPosition === 'left' ? 'left' : 'center',
        top: props.legendPosition === 'top' ? 'top' : props.legendPosition === 'bottom' ? 'bottom' : 'middle',
        right: props.legendPosition === 'right' ? 'right' : 'auto',
        bottom: props.legendPosition === 'bottom' ? 'bottom' : 'auto',
        padding: [10, 20],
        itemGap: 10,
        itemWidth: 15,
        itemHeight: 10,
        textStyle: {
          fontSize: 12,
        },
      }
    : undefined

  // 根据图例位置调整饼图位置
  const pieCenter = props.showLegend
    ? props.legendPosition === 'left'
      ? ['65%', '50%']
      : props.legendPosition === 'right'
      ? ['35%', '50%']
      : props.legendPosition === 'bottom'
      ? ['50%', '40%']
      : ['50%', '50%']
    : ['50%', '50%']

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

    legend: legendConfig
      ? {
          ...legendConfig,
          data: props.data.map(item => item.name),
        }
      : undefined,

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
          },
          right: 20,
        }
      : undefined,

    series: [
      {
        name: props.title || '数据',
        type: 'pie' as const,
        radius: props.radius,
        center: pieCenter,
        roseType: props.roseType as any,
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: props.showLabel
          ? {
              show: true,
              formatter: (params: any) => {
                const { name, value, percent } = params
                return `${name}\n${value} (${percent}%)`
              },
              fontSize: 12,
            }
          : {
              show: false,
            },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        labelLine: {
          show: props.showLabel,
          length: 10,
          length2: 10,
        },
        data: props.data.map((item, index) => ({
          ...item,
          itemStyle: {
            color: props.colors[index % props.colors.length],
          },
        })),
      },
    ] as any,

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
.pie-chart {
  width: 100%;
  height: 100%;
}
</style>