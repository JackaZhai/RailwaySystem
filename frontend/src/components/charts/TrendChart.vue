<template>
  <div class="trend-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-actions">
        <button
          class="action-btn"
          :class="{ active: timeRange === 'hourly' }"
          @click="changeTimeRange('hourly')"
        >
          小时趋势
        </button>
        <button
          class="action-btn"
          :class="{ active: timeRange === 'daily' }"
          @click="changeTimeRange('daily')"
        >
          日趋势
        </button>
        <button
          class="action-btn"
          :class="{ active: timeRange === 'weekly' }"
          @click="changeTimeRange('weekly')"
        >
          周趋势
        </button>
        <button
          class="action-btn"
          :class="{ active: timeRange === 'monthly' }"
          @click="changeTimeRange('monthly')"
        >
          月趋势
        </button>
        <div class="chart-legend">
          <div class="legend-item">
            <div class="legend-color total"></div>
            <span>总客流量</span>
          </div>
          <div class="legend-item">
            <div class="legend-color inbound"></div>
            <span>到达客流</span>
          </div>
          <div class="legend-item">
            <div class="legend-color outbound"></div>
            <span>发送客流</span>
          </div>
        </div>
      </div>
    </div>
    <div class="chart-container">
      <!-- 图表主体 -->
      <div class="chart-body">
        <!-- Y轴 -->
        <div class="y-axis">
          <div
            v-for="(label, index) in yAxisLabels"
            :key="index"
            class="y-label"
          >
            {{ label }}
          </div>
        </div>

        <!-- 图表区域 -->
        <div class="chart-area">
          <!-- X轴 -->
          <div class="x-axis">
            <div
              v-for="(label, index) in xAxisLabels"
              :key="index"
              class="x-label"
            >
              {{ label }}
            </div>
          </div>

          <!-- 网格线 -->
          <div class="chart-grid">
            <div
              v-for="i in 5"
              :key="i"
              class="grid-line"
            ></div>
          </div>

          <!-- 趋势线 -->
          <div class="trend-lines">
            <!-- 总客流量线 -->
            <svg class="trend-line-svg" width="100%" height="100%">
              <polyline
                :points="totalPoints"
                class="trend-line total"
                fill="none"
              />
              <circle
                v-for="(point, index) in totalDataPoints"
                :key="`total-${index}`"
                :cx="point.x"
                :cy="point.y"
                r="4"
                class="data-point total"
                @mouseenter="showTooltip('total', index)"
                @mouseleave="hideTooltip"
              />
            </svg>

            <!-- 到达客流线 -->
            <svg class="trend-line-svg" width="100%" height="100%">
              <polyline
                :points="inboundPoints"
                class="trend-line inbound"
                fill="none"
              />
              <circle
                v-for="(point, index) in inboundDataPoints"
                :key="`inbound-${index}`"
                :cx="point.x"
                :cy="point.y"
                r="4"
                class="data-point inbound"
                @mouseenter="showTooltip('inbound', index)"
                @mouseleave="hideTooltip"
              />
            </svg>

            <!-- 发送客流线 -->
            <svg class="trend-line-svg" width="100%" height="100%">
              <polyline
                :points="outboundPoints"
                class="trend-line outbound"
                fill="none"
              />
              <circle
                v-for="(point, index) in outboundDataPoints"
                :key="`outbound-${index}`"
                :cx="point.x"
                :cy="point.y"
                r="4"
                class="data-point outbound"
                @mouseenter="showTooltip('outbound', index)"
                @mouseleave="hideTooltip"
              />
            </svg>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="chart-stats">
        <div class="stat-card">
          <div class="stat-value">{{ formatNumber(stats.total) }}</div>
          <div class="stat-label">总客流量</div>
          <div class="stat-trend" :class="stats.totalTrend >= 0 ? 'positive' : 'negative'">
            <span>{{ stats.totalTrend >= 0 ? '+' : '' }}{{ stats.totalTrend }}%</span>
            <svg v-if="stats.totalTrend >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ formatNumber(stats.inbound) }}</div>
          <div class="stat-label">到达客流</div>
          <div class="stat-trend" :class="stats.inboundTrend >= 0 ? 'positive' : 'negative'">
            <span>{{ stats.inboundTrend >= 0 ? '+' : '' }}{{ stats.inboundTrend }}%</span>
            <svg v-if="stats.inboundTrend >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ formatNumber(stats.outbound) }}</div>
          <div class="stat-label">发送客流</div>
          <div class="stat-trend" :class="stats.outboundTrend >= 0 ? 'positive' : 'negative'">
            <span>{{ stats.outboundTrend >= 0 ? '+' : '' }}{{ stats.outboundTrend }}%</span>
            <svg v-if="stats.outboundTrend >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.peakTime }}</div>
          <div class="stat-label">高峰时段</div>
          <div class="stat-detail">{{ stats.peakValue.toLocaleString() }} 人</div>
        </div>
      </div>
    </div>

    <!-- 工具提示 -->
    <div
      v-if="tooltip.visible"
      class="trend-tooltip"
      :style="tooltipStyle"
    >
      <div class="tooltip-header">
        <strong>{{ tooltip.time }}</strong>
      </div>
      <div class="tooltip-content">
        <div class="tooltip-row">
          <div class="tooltip-label">
            <div class="legend-color total"></div>
            <span>总客流量：</span>
          </div>
          <div class="tooltip-value">{{ tooltip.total.toLocaleString() }} 人</div>
        </div>
        <div class="tooltip-row">
          <div class="tooltip-label">
            <div class="legend-color inbound"></div>
            <span>到达客流：</span>
          </div>
          <div class="tooltip-value">{{ tooltip.inbound.toLocaleString() }} 人</div>
        </div>
        <div class="tooltip-row">
          <div class="tooltip-label">
            <div class="legend-color outbound"></div>
            <span>发送客流：</span>
          </div>
          <div class="tooltip-value">{{ tooltip.outbound.toLocaleString() }} 人</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface TrendData {
  time: string
  total: number
  inbound: number
  outbound: number
}

interface Stats {
  total: number
  inbound: number
  outbound: number
  totalTrend: number
  inboundTrend: number
  outboundTrend: number
  peakTime: string
  peakValue: number
}

interface TooltipData {
  visible: boolean
  time: string
  total: number
  inbound: number
  outbound: number
  x: number
  y: number
}

interface DataPoint {
  x: number
  y: number
}

const props = withDefaults(defineProps<{
  title?: string
  data?: TrendData[]
}>(), {
  title: '客流趋势分析',
  data: () => []
})

// 时间范围
const timeRange = ref<'hourly' | 'daily' | 'weekly' | 'monthly'>('daily')

// 工具提示
const tooltip = ref<TooltipData>({
  visible: false,
  time: '',
  total: 0,
  inbound: 0,
  outbound: 0,
  x: 0,
  y: 0
})

// 趋势数据
const trendData = computed(() => {
  if (props.data.length > 0) {
    return props.data
  }
  return generateMockData()
})

// X轴标签
const xAxisLabels = computed(() => {
  switch (timeRange.value) {
    case 'hourly':
      return ['00:00', '06:00', '12:00', '18:00', '24:00']
    case 'daily':
      return ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    case 'weekly':
      return ['第1周', '第2周', '第3周', '第4周']
    case 'monthly':
      return ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    default:
      return []
  }
})

// Y轴标签
const yAxisLabels = computed(() => {
  const maxValue = Math.max(...trendData.value.map(d => d.total))
  const step = Math.ceil(maxValue / 4 / 1000) * 1000
  return [
    `${step * 4}K`,
    `${step * 3}K`,
    `${step * 2}K`,
    `${step}K`,
    '0'
  ]
})

// 统计数据
const stats = computed(() => {
  const data = trendData.value
  const total = data.reduce((sum, d) => sum + d.total, 0)
  const inbound = data.reduce((sum, d) => sum + d.inbound, 0)
  const outbound = data.reduce((sum, d) => sum + d.outbound, 0)

  // 计算趋势（模拟）
  const totalTrend = Math.round((Math.random() - 0.5) * 20)
  const inboundTrend = Math.round((Math.random() - 0.5) * 15)
  const outboundTrend = Math.round((Math.random() - 0.5) * 18)

  // 找到高峰时段
  const peakData = data.reduce((max, d) => d.total > max.total ? d : max, data[0])

  return {
    total,
    inbound,
    outbound,
    totalTrend,
    inboundTrend,
    outboundTrend,
    peakTime: peakData.time,
    peakValue: peakData.total
  }
})

// 总客流量数据点
const totalDataPoints = computed(() => {
  return calculateDataPoints(trendData.value.map(d => d.total))
})

// 到达客流数据点
const inboundDataPoints = computed(() => {
  return calculateDataPoints(trendData.value.map(d => d.inbound))
})

// 发送客流数据点
const outboundDataPoints = computed(() => {
  return calculateDataPoints(trendData.value.map(d => d.outbound))
})

// 总客流量折线点
const totalPoints = computed(() => {
  return totalDataPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

// 到达客流折线点
const inboundPoints = computed(() => {
  return inboundDataPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

// 发送客流折线点
const outboundPoints = computed(() => {
  return outboundDataPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

// 工具提示样式
const tooltipStyle = computed(() => ({
  left: `${tooltip.value.x}px`,
  top: `${tooltip.value.y}px`
}))

// 生成模拟数据
const generateMockData = (): TrendData[] => {
  const count = timeRange.value === 'hourly' ? 24 :
                timeRange.value === 'daily' ? 7 :
                timeRange.value === 'weekly' ? 4 : 12

  const data: TrendData[] = []
  const baseTotal = 5000
  const baseInbound = 3000
  const baseOutbound = 2000

  for (let i = 0; i < count; i++) {
    const timeFactor = Math.sin(i / count * Math.PI) * 0.5 + 0.5
    const dayFactor = i < 2 ? 0.3 : i < 4 ? 0.7 : 1.0
    const randomFactor = 0.8 + Math.random() * 0.4

    const total = Math.round(baseTotal * timeFactor * dayFactor * randomFactor)
    const inbound = Math.round(baseInbound * timeFactor * dayFactor * randomFactor * 0.9)
    const outbound = Math.round(baseOutbound * timeFactor * dayFactor * randomFactor * 1.1)

    let time = ''
    switch (timeRange.value) {
      case 'hourly':
        time = `${i.toString().padStart(2, '0')}:00`
        break
      case 'daily':
        const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        time = days[i % 7]
        break
      case 'weekly':
        time = `第${i + 1}周`
        break
      case 'monthly':
        time = `${i + 1}月`
        break
    }

    data.push({
      time,
      total,
      inbound,
      outbound
    })
  }

  return data
}

// 计算数据点坐标
const calculateDataPoints = (values: number[]): DataPoint[] => {
  const maxValue = Math.max(...values)
  const minValue = Math.min(...values)
  const valueRange = maxValue - minValue || 1

  const chartWidth = 800 // 假设图表宽度
  const chartHeight = 200 // 假设图表高度
  const padding = 40

  return values.map((value, index) => {
    const x = padding + (index / (values.length - 1)) * (chartWidth - 2 * padding)
    const y = padding + ((maxValue - value) / valueRange) * (chartHeight - 2 * padding)
    return { x, y }
  })
}

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`
  }
  return num.toString()
}

// 显示工具提示
const showTooltip = (type: 'total' | 'inbound' | 'outbound', index: number) => {
  const data = trendData.value[index]
  tooltip.value = {
    visible: true,
    time: data.time,
    total: data.total,
    inbound: data.inbound,
    outbound: data.outbound,
    x: 100 + index * 60,
    y: 150
  }
}

// 隐藏工具提示
const hideTooltip = () => {
  tooltip.value.visible = false
}

// 切换时间范围
const changeTimeRange = (range: 'hourly' | 'daily' | 'weekly' | 'monthly') => {
  timeRange.value = range
}

// 初始化
onMounted(() => {
  // 可以在这里加载真实数据
})
</script>

<style scoped>
.trend-chart {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
  position: relative;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.chart-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.chart-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.action-btn {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background-color: var(--color-bg-tertiary);
}

.action-btn.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.chart-legend {
  display: flex;
  gap: var(--spacing-3);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: var(--border-radius-sm);
}

.legend-color.total {
  background-color: var(--color-primary);
}

.legend-color.inbound {
  background-color: var(--color-success);
}

.legend-color.outbound {
  background-color: var(--color-secondary);
}

.chart-container {
  position: relative;
}

.chart-body {
  display: flex;
  height: 300px;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 60px;
  padding-bottom: 40px;
}

.y-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: right;
  padding-right: var(--spacing-2);
}

.chart-area {
  flex: 1;
  position: relative;
  padding-bottom: 40px;
}

.x-axis {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
}

.x-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: center;
}

.chart-grid {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-bottom: 40px;
}

.grid-line {
  border-bottom: 1px solid var(--color-border-light);
}

.trend-lines {
  position: absolute;
  inset: 0;
  padding-bottom: 40px;
}

.trend-line-svg {
  position: absolute;
  top: 0;
  left: 0;
}

.trend-line {
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.trend-line.total {
  stroke: var(--color-primary);
}

.trend-line.inbound {
  stroke: var(--color-success);
}

.trend-line.outbound {
  stroke: var(--color-secondary);
}

.data-point {
  cursor: pointer;
  transition: all var(--transition-fast);
}

.data-point:hover {
  r: 6;
}

.data-point.total {
  fill: var(--color-primary);
  stroke: white;
  stroke-width: 2;
}

.data-point.inbound {
  fill: var(--color-success);
  stroke: white;
  stroke-width: 2;
}

.data-point.outbound {
  fill: var(--color-secondary);
  stroke: white;
  stroke-width: 2;
}

.chart-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-3);
  margin-top: var(--spacing-4);
}

.stat-card {
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-3);
  text-align: center;
}

.stat-value {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-1);
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-2);
}

.stat-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.stat-trend.positive {
  color: var(--color-success);
}

.stat-trend.negative {
  color: var(--color-error);
}

.stat-trend svg {
  width: 12px;
  height: 12px;
}

.stat-detail {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-1);
}

.trend-tooltip {
  position: fixed;
  background-color: white;
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-3);
  z-index: 1000;
  min-width: 200px;
  pointer-events: none;
  animation: fadeIn var(--transition-fast);
}

.tooltip-header {
  margin-bottom: var(--spacing-2);
  padding-bottom: var(--spacing-2);
  border-bottom: 1px solid var(--color-border-light);
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tooltip-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.tooltip-value {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-3);
  }

  .chart-actions {
    flex-wrap: wrap;
    gap: var(--spacing-2);
  }

  .chart-legend {
    order: -1;
    width: 100%;
    justify-content: center;
  }

  .chart-body {
    height: 250px;
  }

  .chart-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-value {
    font-size: var(--font-size-lg);
  }
}

@media (max-width: 480px) {
  .chart-stats {
    grid-template-columns: 1fr;
  }

  .chart-body {
    height: 200px;
  }

  .y-axis {
    min-width: 40px;
  }

  .x-axis {
    padding: 0 10px;
  }
}
</style>