<template>
  <div class="heatmap-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div v-if="!hasCustomLabels" class="chart-actions">
        <button
          class="action-btn"
          :class="{ active: viewMode === 'hourly' }"
          @click="changeViewMode('hourly')"
        >
          小时热力图
        </button>
        <button
          class="action-btn"
          :class="{ active: viewMode === 'daily' }"
          @click="changeViewMode('daily')"
        >
          日热力图
        </button>
        <button
          class="action-btn"
          :class="{ active: viewMode === 'weekly' }"
          @click="changeViewMode('weekly')"
        >
          周热力图
        </button>
      </div>
    </div>
    <div class="chart-container">
      <div class="heatmap-grid">
        <!-- Y轴标签 -->
        <div class="y-axis">
          <div
            v-for="label in yAxisLabels"
            :key="label"
            class="y-label"
          >
            {{ label }}
          </div>
        </div>

        <!-- 热力图主体 -->
        <div class="heatmap-body">
          <!-- X轴标签 -->
          <div class="x-axis">
            <div
              v-for="label in xAxisLabels"
              :key="label"
              class="x-label"
            >
              {{ label }}
            </div>
          </div>

          <!-- 热力单元格 -->
          <div class="heatmap-cells">
            <div
              v-for="(row, rowIndex) in heatmapData"
              :key="rowIndex"
              class="heatmap-row"
            >
              <div
                v-for="(cell, colIndex) in row"
                :key="colIndex"
                class="heatmap-cell"
                :class="getCellClass(cell.value)"
                :style="{ backgroundColor: getCellColor(cell.value) }"
                @mouseenter="showTooltip(cell, rowIndex, colIndex)"
                @mouseleave="hideTooltip"
              >
                <div class="cell-value">{{ cell.value }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 图例 -->
      <div class="heatmap-legend">
        <div class="legend-title">客流量强度</div>
        <div class="legend-gradient">
          <div
            v-for="i in 5"
            :key="i"
            class="legend-step"
            :style="{ backgroundColor: getLegendColor(i) }"
          >
            <span class="step-label">{{ getLegendLabel(i) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 工具提示 -->
    <div
      v-if="tooltip.visible"
      class="heatmap-tooltip"
      :style="tooltipStyle"
    >
      <div class="tooltip-header">
        <strong>{{ tooltip.title }}</strong>
      </div>
      <div class="tooltip-content">
        <div class="tooltip-row">
          <span class="tooltip-label">时间：</span>
          <span class="tooltip-value">{{ tooltip.time }}</span>
        </div>
        <div class="tooltip-row">
          <span class="tooltip-label">客流量：</span>
          <span class="tooltip-value">{{ tooltip.value.toLocaleString() }} 人</span>
        </div>
        <div class="tooltip-row">
          <span class="tooltip-label">占比：</span>
          <span class="tooltip-value">{{ tooltip.percentage }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface HeatMapCell {
  value: number
  time: string
  label: string
}

interface TooltipData {
  visible: boolean
  title: string
  time: string
  value: number
  percentage: string
  x: number
  y: number
}

const props = withDefaults(defineProps<{
  title?: string
  data?: HeatMapCell[][]
  xLabels?: string[]
  yLabels?: string[]
}>(), {
  title: '客流热力图',
  data: () => [],
  xLabels: () => [],
  yLabels: () => []
})

// 视图模式
const viewMode = ref<'hourly' | 'daily' | 'weekly'>('hourly')

// 工具提示
const tooltip = ref<TooltipData>({
  visible: false,
  title: '',
  time: '',
  value: 0,
  percentage: '0%',
  x: 0,
  y: 0
})

// 热力图数据
const heatmapData = computed(() => {
  if (props.data.length > 0) {
    return props.data
  }

  // 生成模拟数据
  return generateMockData()
})

const hasCustomLabels = computed(() => props.xLabels.length > 0 || props.yLabels.length > 0)

// X轴标签
const xAxisLabels = computed(() => {
  if (props.xLabels.length > 0) {
    return props.xLabels
  }

  switch (viewMode.value) {
    case 'hourly':
      return ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
    case 'daily':
      return ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    case 'weekly':
      return ['第1周', '第2周', '第3周', '第4周']
    default:
      return []
  }
})

// Y轴标签
const yAxisLabels = computed(() => {
  if (props.yLabels.length > 0) {
    return props.yLabels
  }

  switch (viewMode.value) {
    case 'hourly':
      return ['成都东', '重庆北', '内江北', '资阳北', '永川东']
    case 'daily':
      return ['成都东', '重庆北', '内江北', '资阳北', '永川东']
    case 'weekly':
      return ['成渝高铁', '渝贵铁路', '成贵高铁', '西成高铁', '渝万铁路']
    default:
      return []
  }
})

// 工具提示样式
const tooltipStyle = computed(() => ({
  left: `${tooltip.value.x}px`,
  top: `${tooltip.value.y}px`
}))

// 生成模拟数据
const generateMockData = (): HeatMapCell[][] => {
  const rows = yAxisLabels.value.length
  const cols = xAxisLabels.value.length
  const data: HeatMapCell[][] = []

  for (let i = 0; i < rows; i++) {
    const row: HeatMapCell[] = []
    for (let j = 0; j < cols; j++) {
      const baseValue = 1000 + Math.random() * 5000
      const timeFactor = j < 2 ? 0.3 : j < 4 ? 0.7 : 1.0
      const stationFactor = i < 2 ? 1.2 : i < 4 ? 0.8 : 1.0
      const value = Math.round(baseValue * timeFactor * stationFactor)

      let time = ''
      let label = ''

      switch (viewMode.value) {
        case 'hourly':
          time = `${xAxisLabels.value[j]}`
          label = `${yAxisLabels.value[i]}站`
          break
        case 'daily':
          time = `${xAxisLabels.value[j]}`
          label = `${yAxisLabels.value[i]}站`
          break
        case 'weekly':
          time = `${xAxisLabels.value[j]}`
          label = `${yAxisLabels.value[i]}`
          break
      }

      row.push({
        value,
        time,
        label
      })
    }
    data.push(row)
  }

  return data
}

// 获取单元格颜色
const getCellColor = (value: number): string => {
  const maxValue = 6000
  const intensity = Math.min(value / maxValue, 1)

  // 从浅绿色到深红色的渐变
  const r = Math.round(255 * intensity)
  const g = Math.round(255 * (1 - intensity))
  const b = 100

  return `rgb(${r}, ${g}, ${b})`
}

// 获取单元格类名
const getCellClass = (value: number): string => {
  if (value > 5000) return 'cell-high'
  if (value > 3000) return 'cell-medium'
  if (value > 1000) return 'cell-low'
  return 'cell-very-low'
}

// 获取图例颜色
const getLegendColor = (step: number): string => {
  const intensity = (step - 1) / 4
  const r = Math.round(255 * intensity)
  const g = Math.round(255 * (1 - intensity))
  const b = 100
  return `rgb(${r}, ${g}, ${b})`
}

// 获取图例标签
const getLegendLabel = (step: number): string => {
  const labels = ['极低', '较低', '中等', '较高', '极高']
  return labels[step - 1]
}

// 显示工具提示
const showTooltip = (cell: HeatMapCell, rowIndex: number, colIndex: number) => {
  const total = heatmapData.value.flat().reduce((sum, c) => sum + c.value, 0)
  const percentage = ((cell.value / total) * 100).toFixed(1)

  tooltip.value = {
    visible: true,
    title: `${cell.label} - ${cell.time}`,
    time: cell.time,
    value: cell.value,
    percentage: `${percentage}%`,
    x: colIndex * 60 + 100,
    y: rowIndex * 50 + 100
  }
}

// 隐藏工具提示
const hideTooltip = () => {
  tooltip.value.visible = false
}

// 切换视图模式
const changeViewMode = (mode: 'hourly' | 'daily' | 'weekly') => {
  if (hasCustomLabels.value) {
    return
  }
  viewMode.value = mode
}

// 初始化
onMounted(() => {
  // 可以在这里加载真实数据
})
</script>

<style scoped>
.heatmap-chart {
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
  gap: var(--spacing-2);
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

.chart-container {
  position: relative;
}

.heatmap-grid {
  display: flex;
  gap: var(--spacing-4);
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  min-width: 80px;
}

.y-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-align: right;
  padding: var(--spacing-2) var(--spacing-3);
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.heatmap-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.x-axis {
  display: flex;
  justify-content: space-around;
  margin-bottom: var(--spacing-2);
  padding-left: 40px;
}

.x-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-align: center;
  width: 60px;
}

.heatmap-cells {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.heatmap-row {
  display: flex;
  gap: 2px;
}

.heatmap-cell {
  width: 60px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.heatmap-cell:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
  z-index: 1;
}

.cell-value {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.cell-high {
  border: 2px solid rgba(255, 0, 0, 0.3);
}

.cell-medium {
  border: 2px solid rgba(255, 165, 0, 0.3);
}

.cell-low {
  border: 2px solid rgba(0, 128, 0, 0.3);
}

.cell-very-low {
  border: 2px solid rgba(128, 128, 128, 0.3);
}

.heatmap-legend {
  margin-top: var(--spacing-6);
  padding: var(--spacing-3);
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
}

.legend-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.legend-gradient {
  display: flex;
  height: 24px;
  border-radius: var(--border-radius-sm);
  overflow: hidden;
}

.legend-step {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.step-label {
  font-size: var(--font-size-xs);
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  font-weight: var(--font-weight-medium);
}

.heatmap-tooltip {
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
  gap: var(--spacing-1);
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
}

.tooltip-label {
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
  .heatmap-grid {
    flex-direction: column;
  }

  .y-axis {
    flex-direction: row;
    min-width: auto;
    margin-bottom: var(--spacing-2);
  }

  .y-label {
    text-align: center;
    justify-content: center;
    height: auto;
    padding: var(--spacing-1);
  }

  .x-axis {
    padding-left: 0;
  }

  .heatmap-cell {
    width: 40px;
    height: 40px;
  }

  .cell-value {
    font-size: 10px;
  }
}
</style>
