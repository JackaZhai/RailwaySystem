<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import type { EChartsType, EChartsOption } from 'echarts'
import { CHART_CONFIG } from '@/config'

// Props
const props = withDefaults(defineProps<{
  option: EChartsOption
  chartId?: string
  className?: string
  theme?: string | object
  loading?: boolean
  loadingText?: string
  autoresize?: boolean
  manualUpdate?: boolean
  initOptions?: any
  updateOptions?: any
  group?: string
}>(), {
  chartId: 'echarts-chart',
  className: '',
  theme: 'light',
  loading: false,
  loadingText: '加载中...',
  autoresize: true,
  manualUpdate: false,
  initOptions: () => ({}),
  updateOptions: () => ({}),
  group: '',
})

// Emits
const emit = defineEmits<{
  'chart-ready': [chart: EChartsType]
  'chart-click': [params: any]
  'chart-dblclick': [params: any]
  'chart-mouseover': [params: any]
  'chart-mouseout': [params: any]
  'chart-datazoom': [params: any]
  'chart-legendselectchanged': [params: any]
}>()

// 状态
const chartInstance = ref<EChartsType | null>(null)
const chartContainer = ref<HTMLElement | null>(null)
const chartError = ref<string | null>(null)

// 计算属性
const chartStyle = computed(() => ({
  width: '100%',
  height: '100%',
  minHeight: '300px',
}))

// 初始化图表
const initChart = () => {
  if (!chartContainer.value) return

  try {
    // 销毁现有实例
    if (chartInstance.value) {
      chartInstance.value.dispose()
    }

    // 创建新实例
    chartInstance.value = echarts.init(
      chartContainer.value,
      props.theme,
      props.initOptions
    )

    // 设置图表选项（添加动画配置）
    const animatedOption = {
      ...props.option,
      animation: true,
      animationDuration: 1000,
      animationEasing: 'cubicOut',
      animationThreshold: 2000,
    }

    chartInstance.value.setOption(animatedOption, {
      notMerge: true,
      lazyUpdate: false,
      ...props.updateOptions,
    })

    // 加入分组
    if (props.group && chartInstance.value) {
      chartInstance.value.group = props.group
      echarts.connect(props.group)
    }

    // 绑定事件
    bindChartEvents()

    // 监听窗口大小变化
    if (props.autoresize) {
      window.addEventListener('resize', handleResize)
    }

    ;(emit as any)('chart-ready', chartInstance.value!)

    console.log('ECharts图表初始化成功')
  } catch (error) {
    chartError.value = error instanceof Error ? error.message : '图表初始化失败'
    console.error('ECharts图表初始化失败:', error)
  }
}

// 绑定图表事件
const bindChartEvents = () => {
  if (!chartInstance.value) return

  const events = [
    'click',
    'dblclick',
    'mouseover',
    'mouseout',
    'datazoom',
    'legendselectchanged',
  ] as const

  events.forEach(eventName => {
    chartInstance.value?.on(eventName, (...args: any[]) => {
      const params = args[0]
      ;(emit as any)(`chart-${eventName}`, params)
    })
  })
}

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance.value) {
    chartInstance.value.resize()
  }
}

// 更新图表数据
const updateChart = (newOption: EChartsOption) => {
  if (!chartInstance.value) return

  try {
    // 添加动画配置
    const animatedOption = {
      ...newOption,
      animation: true,
      animationDuration: 800,
      animationEasing: 'cubicOut',
    }

    chartInstance.value.setOption(animatedOption, {
      notMerge: false,
      lazyUpdate: true,
    })
  } catch (error) {
    console.error('图表更新失败:', error)
  }
}

// 显示加载状态
const showLoading = () => {
  if (!chartInstance.value) return

  chartInstance.value.showLoading({
    text: props.loadingText,
    color: CHART_CONFIG.COLOR_SCHEME[0],
    textColor: '#666',
    maskColor: 'rgba(255, 255, 255, 0.9)',
    zlevel: 0,
    lineWidth: 3,
    fontSize: 14,
    showSpinner: true,
    spinnerRadius: 10,
  })
}

// 隐藏加载状态
const hideLoading = () => {
  if (!chartInstance.value) return

  chartInstance.value.hideLoading()
}

// 获取图表实例
const getChartInstance = () => chartInstance.value

// 清空图表
const clearChart = () => {
  if (!chartInstance.value) return

  chartInstance.value.clear()
}

// 销毁图表
const disposeChart = () => {
  if (!chartInstance.value) return

  // 移除事件监听
  if (props.autoresize) {
    window.removeEventListener('resize', handleResize)
  }

  // 断开分组连接
  if (props.group) {
    echarts.disconnect(props.group)
  }

  // 销毁实例
  chartInstance.value.dispose()
  chartInstance.value = null
}

// 监听props变化
watch(() => props.option, (newOption) => {
  if (!props.manualUpdate && chartInstance.value) {
    updateChart(newOption)
  }
}, { deep: true })

watch(() => props.loading, (isLoading) => {
  if (isLoading) {
    showLoading()
  } else {
    hideLoading()
  }
})

watch(() => props.theme, () => {
  // 主题变化需要重新初始化
  initChart()
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

onUnmounted(() => {
  disposeChart()
})

// 暴露方法给父组件
defineExpose({
  getChartInstance,
  updateChart,
  clearChart,
  disposeChart,
  initChart,
})
</script>

<template>
  <div :id="chartId" :class="['echarts-chart', className]" :style="chartStyle">
    <!-- 图表错误状态 -->
    <div v-if="chartError" class="chart-error">
      <div class="error-icon">⚠️</div>
      <div class="error-text">{{ chartError }}</div>
      <button class="retry-button" @click="initChart">重试</button>
    </div>

    <!-- 图表容器 -->
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<style scoped>
.echarts-chart {
  position: relative;
  background-color: white;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
}

.echarts-chart:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.chart-error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.95);
  z-index: 1000;
  animation: fadeIn var(--transition-base);
}

.error-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-4);
  animation: bounce 0.5s ease-in-out infinite;
}

.error-text {
  color: var(--color-error);
  margin-bottom: var(--spacing-4);
  text-align: center;
  padding: 0 var(--spacing-4);
  font-size: var(--font-size-sm);
}

.retry-button {
  padding: var(--spacing-2) var(--spacing-4);
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
  border-radius: var(--border-radius-base);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
}

.retry-button:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.retry-button:active {
  transform: translateY(0);
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style>