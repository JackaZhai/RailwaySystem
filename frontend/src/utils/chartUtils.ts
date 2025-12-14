/**
 * 图表工具函数
 */

import type { EChartsOption } from 'echarts'
import { CHART_CONFIG } from '@/config'

/**
 * 创建基础图表配置
 */
export function createBaseChartConfig(options: {
  title?: string
  subtext?: string
  xAxisData?: string[]
  yAxisData?: number[]
  series?: any[]
  legend?: boolean
  toolbox?: boolean
  grid?: any
  colors?: string[]
}): EChartsOption {
  return {
    title: options.title
      ? {
          text: options.title,
          subtext: options.subtext,
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold',
          },
        }
      : undefined,

    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985',
        },
      },
    },

    legend: options.legend
      ? {
          data: options.series?.map(s => s.name) || [],
          top: 30,
        }
      : undefined,

    grid: options.grid || {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },

    toolbox: options.toolbox
      ? {
          feature: {
            saveAsImage: {},
            dataView: { readOnly: true },
            restore: {},
            dataZoom: {},
            magicType: { type: ['line', 'bar'] },
          },
          right: 20,
        }
      : undefined,

    animation: CHART_CONFIG.ANIMATION as any,
  }
}

/**
 * 生成时间序列的X轴数据
 */
export function generateTimeSeriesData(
  startDate: Date,
  endDate: Date,
  interval: 'day' | 'week' | 'month' | 'hour' = 'day'
): string[] {
  const dates: string[] = []
  const current = new Date(startDate)

  while (current <= endDate) {
    let formattedDate: string

    switch (interval) {
      case 'hour':
        formattedDate = current.toLocaleTimeString('zh-CN', { hour: '2-digit' })
        current.setHours(current.getHours() + 1)
        break
      case 'day':
        formattedDate = current.toLocaleDateString('zh-CN')
        current.setDate(current.getDate() + 1)
        break
      case 'week':
        formattedDate = `第${getWeekNumber(current)}周`
        current.setDate(current.getDate() + 7)
        break
      case 'month':
        formattedDate = `${current.getFullYear()}-${(current.getMonth() + 1).toString().padStart(2, '0')}`
        current.setMonth(current.getMonth() + 1)
        break
    }

    dates.push(formattedDate)
  }

  return dates
}

/**
 * 获取周数
 */
function getWeekNumber(date: Date): number {
  const firstDayOfYear = new Date(date.getFullYear(), 0, 1)
  const pastDaysOfYear = (date.getTime() - firstDayOfYear.getTime()) / 86400000
  return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7)
}

/**
 * 格式化数字为易读格式
 */
export function formatNumber(value: number): string {
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(1)}亿`
  }
  if (value >= 10000) {
    return `${(value / 10000).toFixed(1)}万`
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}千`
  }
  return value.toString()
}

/**
 * 生成随机数据（用于测试）
 */
export function generateRandomData(
  count: number,
  min: number,
  max: number,
  trend: 'up' | 'down' | 'random' = 'random'
): number[] {
  const data: number[] = []
  let current = (min + max) / 2

  for (let i = 0; i < count; i++) {
    let variation: number

    switch (trend) {
      case 'up':
        variation = Math.random() * (max - min) * 0.1
        current = Math.min(max, current + variation)
        break
      case 'down':
        variation = Math.random() * (max - min) * 0.1
        current = Math.max(min, current - variation)
        break
      case 'random':
      default:
        current = min + Math.random() * (max - min)
        break
    }

    data.push(parseFloat(current.toFixed(2)))
  }

  return data
}

/**
 * 计算数据统计信息
 */
export function calculateStatistics(data: number[]): {
  min: number
  max: number
  avg: number
  sum: number
  std: number
} {
  if (data.length === 0) {
    return { min: 0, max: 0, avg: 0, sum: 0, std: 0 }
  }

  const sum = data.reduce((a, b) => a + b, 0)
  const avg = sum / data.length
  const min = Math.min(...data)
  const max = Math.max(...data)

  const variance = data.reduce((a, b) => a + Math.pow(b - avg, 2), 0) / data.length
  const std = Math.sqrt(variance)

  return {
    min: parseFloat(min.toFixed(2)),
    max: parseFloat(max.toFixed(2)),
    avg: parseFloat(avg.toFixed(2)),
    sum: parseFloat(sum.toFixed(2)),
    std: parseFloat(std.toFixed(2)),
  }
}

/**
 * 创建客流时间序列配置
 */
export function createPassengerTimeSeriesConfig(
  timeData: string[],
  passengerData: number[],
  options: {
    title?: string
    yAxisName?: string
    smooth?: boolean
    areaStyle?: boolean
  } = {}
): EChartsOption {
  return {
    title: {
      text: options.title || '客流时间序列',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const param = params[0]
        return `${param.name}<br/>客流量: ${formatNumber(param.value)}`
      },
    },
    xAxis: {
      type: 'category',
      data: timeData,
      boundaryGap: false,
      axisLabel: {
        rotate: 45,
      },
    },
    yAxis: {
      type: 'value',
      name: options.yAxisName || '客流量',
      axisLabel: {
        formatter: (value: number) => formatNumber(value),
      },
    },
    series: [
      {
        name: '客流量',
        type: 'line',
        data: passengerData,
        smooth: options.smooth !== false,
        areaStyle: options.areaStyle
          ? {
              color: {
                type: 'linear' as const,
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: CHART_CONFIG.COLOR_SCHEME[0]!,
                  },
                  {
                    offset: 1,
                    color: `${CHART_CONFIG.COLOR_SCHEME[0]!}00`, // 完全透明
                  },
                ],
              } as any,
            }
          : undefined,
        itemStyle: {
          color: CHART_CONFIG.COLOR_SCHEME[0],
        },
        lineStyle: {
          width: 2,
        },
      },
    ],
    animation: CHART_CONFIG.ANIMATION as any,
  }
}

/**
 * 创建车站客流排名配置
 */
export function createStationRankingConfig(
  stationData: Array<{ name: string; value: number }>,
  options: {
    title?: string
    horizontal?: boolean
    showLabel?: boolean
  } = {}
): EChartsOption {
  // 按值排序
  const sortedData = [...stationData].sort((a, b) => b.value - a.value)

  return {
    title: {
      text: options.title || '车站客流排名',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
      formatter: (params: any) => {
        const param = params[0]
        return `${param.name}<br/>客流量: ${formatNumber(param.value)}`
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },
    xAxis: options.horizontal
      ? {
          type: 'value',
          axisLabel: {
            formatter: (value: number) => formatNumber(value),
          },
        }
      : {
          type: 'category',
          data: sortedData.map(item => item.name),
          axisLabel: {
            interval: 0,
            rotate: sortedData.length > 10 ? 45 : 0,
          },
        },
    yAxis: options.horizontal
      ? {
          type: 'category',
          data: sortedData.map(item => item.name),
          axisLabel: {
            interval: 0,
          },
        }
      : {
          type: 'value',
          axisLabel: {
            formatter: (value: number) => formatNumber(value),
          },
        },
    series: [
      {
        name: '客流量',
        type: 'bar',
        data: sortedData.map(item => item.value),
        label: options.showLabel
          ? {
              show: true,
              position: options.horizontal ? 'right' : 'top',
              formatter: (params: any) => formatNumber(params.value),
            }
          : undefined,
        itemStyle: {
          color: (params: any) => {
            const colorIndex = params.dataIndex % CHART_CONFIG.COLOR_SCHEME.length
            return {
              type: 'linear',
              x: 0,
              y: 0,
              x2: options.horizontal ? 1 : 0,
              y2: options.horizontal ? 0 : 1,
              colorStops: [
                {
                  offset: 0,
                  color: CHART_CONFIG.COLOR_SCHEME[colorIndex],
                },
                {
                  offset: 1,
                  color: `${CHART_CONFIG.COLOR_SCHEME[colorIndex]}80`,
                },
              ],
            }
          },
        },
        barWidth: '60%',
      },
    ] as any,
    animation: CHART_CONFIG.ANIMATION as any,
  }
}

/**
 * 创建客流组成饼图配置
 */
export function createPassengerCompositionConfig(
  compositionData: Array<{ name: string; value: number }>,
  options: {
    title?: string
    radius?: string | [string, string]
    roseType?: 'radius' | 'area'
  } = {}
): EChartsOption {
  return {
    title: {
      text: options.title || '客流组成分析',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: compositionData.map(item => item.name),
    },
    series: [
      {
        name: '客流组成',
        type: 'pie',
        radius: options.radius || '70%',
        center: ['40%', '50%'],
        roseType: options.roseType,
        data: compositionData.map((item, index) => ({
          ...item,
          itemStyle: {
            color: CHART_CONFIG.COLOR_SCHEME[index % CHART_CONFIG.COLOR_SCHEME.length],
          },
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        label: {
          formatter: '{b}: {d}%',
        },
        labelLine: {
          length: 10,
          length2: 10,
        },
      },
    ],
    animation: CHART_CONFIG.ANIMATION as any,
  }
}