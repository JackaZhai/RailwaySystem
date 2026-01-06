<template>
  <div class="dashboard animate-fade-in">
    <!-- 全局加载状态 -->
    <LoadingSpinner
      v-if="isLoading"
      size="large"
      variant="primary"
      text="正在加载数据..."
      fullscreen
    />

    <!-- 页面标题和操作 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">总览</h1>
        <p class="page-description">系统核心指标与客流分析概览</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary touch-target touch-feedback" :disabled="isRefreshing" @click="refreshData">
          <svg v-if="!isRefreshing" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else class="animate-spin" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2V6M12 18V22M4.93 4.93L7.76 7.76M16.24 16.24L19.07 19.07M2 12H6M18 12H22M4.93 19.07L7.76 16.24M16.24 7.76L19.07 4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ isRefreshing ? '刷新中...' : '刷新数据' }}
        </button>
        <button class="btn btn-outline touch-target touch-feedback">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 16.5L12 21.75L21 16.5M3 12L12 17.25L21 12M3 7.5L12 12.75L21 7.5L12 2.25L3 7.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          导出报告
        </button>
      </div>
    </div>

    <!-- 时间筛选 -->
    <div class="time-filter animate-fade-in">
      <div class="filter-container">
        <div class="filter-group">
          <label class="filter-label">时间范围</label>
          <div class="filter-buttons">
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'today' }"
              @click="selectTimeRange('today')"
            >
              今天
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'week' }"
              @click="selectTimeRange('week')"
            >
              本周
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'month' }"
              @click="selectTimeRange('month')"
            >
              本月
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'quarter' }"
              @click="selectTimeRange('quarter')"
            >
              本季度
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'year' }"
              @click="selectTimeRange('year')"
            >
              本年
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'custom' }"
              @click="selectTimeRange('custom')"
            >
              自定义
            </button>
          </div>
        </div>
        <div v-if="selectedRange === 'custom'" class="date-picker">
          <input
            v-model="startDate"
            type="date"
            class="date-input"
            @change="updateCustomDateRange"
          />
          <span class="date-separator">至</span>
          <input
            v-model="endDate"
            type="date"
            class="date-input"
            @change="updateCustomDateRange"
          />
        </div>
        <div v-if="selectedRange !== 'custom'" class="filter-stats">
          <span class="stat-label">统计周期：</span>
          <span class="stat-value">{{ timeRangeLabel }}</span>
          <span class="stat-duration">（{{ timeRangeDuration }}）</span>
        </div>
      </div>
    </div>

    <!-- KPI指标卡片 -->
    <div class="kpi-grid">
      <!-- 总客流量卡片 -->
      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon total-passengers">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 11C11.2091 11 13 9.20914 13 7C13 4.79086 11.2091 3 9 3C6.79086 3 5 4.79086 5 7C5 9.20914 6.79086 11 9 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.totalPassengers >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.totalPassengers >= 0 ? '+' : '' }}{{ kpiData.trends.totalPassengers }}%</span>
            <svg v-if="kpiData.trends.totalPassengers >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-content">
          <template v-if="!isLoading">
            <h3 class="kpi-value">
              <AnimatedNumber :value="kpiData.totalPassengers" :duration="1500" :animate="true" />
            </h3>
            <p class="kpi-label">总客流量</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">今日累计</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon total-trains">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 19C9 19.7956 9.31607 20.5587 9.87868 21.1213C10.4413 21.6839 11.2044 22 12 22C12.7956 22 13.5587 21.6839 14.1213 21.1213C14.6839 20.5587 15 19.7956 15 19M9 19C9 18.2044 9.31607 17.4413 9.87868 16.8787C10.4413 16.3161 11.2044 16 12 16C12.7956 16 13.5587 16.3161 14.1213 16.8787C14.6839 17.4413 15 18.2044 15 19M9 19H3V13C3 11.1435 3.7375 9.36301 5.05025 8.05025C6.36301 6.7375 8.14348 6 10 6H14C15.8565 6 17.637 6.7375 18.9497 8.05025C20.2625 9.36301 21 11.1435 21 13V19H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8 12H8.01M12 12H12.01M16 12H16.01M9 12C9 12.5523 8.55228 13 8 13C7.44772 13 7 12.5523 7 12C7 11.4477 7.44772 11 8 11C8.55228 11 9 11.4477 9 12ZM13 12C13 12.5523 12.5523 13 12 13C11.4477 13 11 12.5523 11 12C11 11.4477 11.4477 11 12 11C12.5523 11 13 11.4477 13 12ZM17 12C17 12.5523 16.5523 13 16 13C15.4477 13 15 12.5523 15 12C15 11.4477 15.4477 11 16 11C16.5523 11 17 11.4477 17 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.totalTrains >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.totalTrains >= 0 ? '+' : '' }}{{ kpiData.trends.totalTrains }}%</span>
            <svg v-if="kpiData.trends.totalTrains >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-content">
          <template v-if="!isLoading">
            <h3 class="kpi-value">
              <AnimatedNumber :value="kpiData.totalTrains" :duration="1200" :animate="true" />
            </h3>
            <p class="kpi-label">运营车次</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">今日累计</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon busy-stations">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 11C13.1046 11 14 10.1046 14 9C14 7.89543 13.1046 7 12 7C10.8954 7 10 7.89543 10 9C10 10.1046 10.8954 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.busyStations >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.busyStations >= 0 ? '+' : '' }}{{ kpiData.trends.busyStations }}%</span>
            <svg v-if="kpiData.trends.busyStations >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-content">
          <template v-if="!isLoading">
            <h3 class="kpi-value">
              <AnimatedNumber :value="kpiData.busyStations" :duration="1000" :animate="true" />
            </h3>
            <p class="kpi-label">繁忙站点</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">活跃站点数</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon revenue">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 1V23M17 5H9.5C8.57174 5 7.6815 5.36875 7.02513 6.02513C6.36875 6.6815 6 7.57174 6 8.5C6 9.42826 6.36875 10.3185 7.02513 10.9749C7.6815 11.6313 8.57174 12 9.5 12H14.5C15.4283 12 16.3185 12.3687 16.9749 13.0251C17.6313 13.6815 18 14.5717 18 15.5C18 16.4283 17.6313 17.3185 16.9749 17.9749C16.3185 18.6313 15.4283 19 14.5 19H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.totalRevenue >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.totalRevenue >= 0 ? '+' : '' }}{{ kpiData.trends.totalRevenue }}%</span>
            <svg v-if="kpiData.trends.totalRevenue >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-content">
          <template v-if="!isLoading">
            <h3 class="kpi-value">
              ¥<AnimatedNumber :value="kpiData.totalRevenue" :duration="1800" :animate="true" />
            </h3>
            <p class="kpi-label">总收入</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">今日累计</span>
        </div>
      </div>
    </div>

    <!-- 主要图表区域 -->
    <div class="chart-grid">
      <!-- 地图区域 -->
      <div class="chart-card map-card">
        <div class="card-header">
          <h3 class="card-title">客流空间分布</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: spatialView === 'map' }"
              @click="spatialView = 'map'"
            >
              地图
            </button>
            <button
              class="card-action-btn"
              :class="{ active: spatialView === 'trend' }"
              @click="spatialView = 'trend'"
            >
              客流趋势
            </button>
          </div>
        </div>
        <div class="card-body">
          <!-- 流向图（高德地图） -->
          <div v-if="spatialView === 'map'" class="station-map-container">
            <div v-if="!mapHasFlows" class="map-empty">暂无流向数据</div>
            <GaodeMap
              map-id="dashboard-flow-map"
              class-name="gaode-map-container"
              :fit-view-to-markers="true"
              :show-controls="true"
            />
          </div>
          <div v-else class="trend-panel">
            <TrendChart
              title="客流趋势分析"
              :data="trendData"
              :granularity="trendGranularity"
              flat
              @granularity-change="handleTrendGranularityChange"
            />
          </div>
        </div>
      </div>

      <div class="chart-card analysis-card">
        <div class="card-body">
          <PassengerFlowAnalysis
            title="客流量深度分析"
            :start-date="startDate"
            :end-date="endDate"
          />
        </div>
      </div>

    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import AnimatedNumber from '@/components/ui/AnimatedNumber.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import GaodeMap from '@/components/map/GaodeMap.vue'
import TrendChart from '@/components/charts/TrendChart.vue'
import PassengerFlowAnalysis from '@/components/analytics/PassengerFlowAnalysis.vue'
import { apiService, type TimeRange, type KpiData, type Station, type TrendData, type TimePeriodData } from '@/services/api'
import { usePassengerStore } from '@/stores/passenger'
import { useMapStore } from '@/stores/map'
import { calculateMarkerSize, calculateMarkerColor, createFlowLine, calculateCenter } from '@/utils/mapUtils'

const passengerStore = usePassengerStore()
const mapStore = useMapStore()

// 时间范围筛选
const selectedRange = ref<'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom'>('custom')
const startDate = ref('')
const endDate = ref('')

const getBaseDate = () => {
  if (endDate.value) {
    const parsed = new Date(endDate.value)
    if (!Number.isNaN(parsed.getTime())) {
      return parsed
    }
  }
  return new Date()
}

// 计算时间范围标签
const timeRangeLabel = computed(() => {
  const now = getBaseDate()
  switch (selectedRange.value) {
    case 'today':
      return now.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
    case 'week': {
      const weekStart = new Date(now.setDate(now.getDate() - now.getDay()))
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      return `${weekStart.getMonth() + 1}月${weekStart.getDate()}日 - ${weekEnd.getMonth() + 1}月${weekEnd.getDate()}日`
    }
    case 'month':
      return `${now.getMonth() + 1}月`
    case 'quarter': {
      const quarter = Math.floor(now.getMonth() / 3) + 1
      return `第${quarter}季度`
    }
    case 'year':
      return `${now.getFullYear()}年`
    default:
      return '自定义范围'
  }
})

// 计算时间范围时长
const timeRangeDuration = computed(() => {
  switch (selectedRange.value) {
    case 'today':
      return '1天'
    case 'week':
      return '7天'
    case 'month': {
      const now = getBaseDate()
      const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
      return `${daysInMonth}天`
    }
    case 'quarter':
      return '约90天'
    case 'year':
      return '365天'
    default:
      if (startDate.value && endDate.value) {
        const start = new Date(startDate.value)
        const end = new Date(endDate.value)
        const diffTime = Math.abs(end.getTime() - start.getTime())
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        return `${diffDays}天`
      }
      return '请选择日期'
  }
})

// 选择时间范围
const selectTimeRange = (range: typeof selectedRange.value) => {
  selectedRange.value = range
  const now = getBaseDate()

  switch (range) {
    case 'today':
      startDate.value = now.toISOString().split('T')[0]
      endDate.value = now.toISOString().split('T')[0]
      break
    case 'week': {
      const weekStart = new Date(now.setDate(now.getDate() - now.getDay()))
      startDate.value = weekStart.toISOString().split('T')[0]
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      endDate.value = weekEnd.toISOString().split('T')[0]
      break
    }
    case 'month': {
      const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
      startDate.value = monthStart.toISOString().split('T')[0]
      const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      endDate.value = monthEnd.toISOString().split('T')[0]
      break
    }
    case 'quarter': {
      const quarter = Math.floor(now.getMonth() / 3)
      const quarterStart = new Date(now.getFullYear(), quarter * 3, 1)
      startDate.value = quarterStart.toISOString().split('T')[0]
      const quarterEnd = new Date(now.getFullYear(), (quarter + 1) * 3, 0)
      endDate.value = quarterEnd.toISOString().split('T')[0]
      break
    }
    case 'year': {
      const yearStart = new Date(now.getFullYear(), 0, 1)
      startDate.value = yearStart.toISOString().split('T')[0]
      const yearEnd = new Date(now.getFullYear(), 11, 31)
      endDate.value = yearEnd.toISOString().split('T')[0]
      break
    }
    case 'custom':
      // 保持当前日期选择
      break
  }

  // 触发数据更新
  updateDataByTimeRange()
}

// 更新自定义日期范围
const updateCustomDateRange = () => {
  if (startDate.value && endDate.value) {
    selectedRange.value = 'custom'
    updateDataByTimeRange()
  }
}

// 根据时间范围更新数据
const updateDataByTimeRange = () => {
  console.log('更新数据，时间范围:', selectedRange.value, '开始日期:', startDate.value, '结束日期:', endDate.value)
  if (startDate.value && endDate.value) {
    passengerStore.setTimeRange(startDate.value, endDate.value)
  }
  // 加载对应时间范围的数据
  loadData()
}

watch(() => [startDate.value, endDate.value, selectedRange.value], ([newStart, newEnd]) => {
  if (!newStart || !newEnd) return
  if (isLoading.value) return
  loadData()
})

watch(
  () => [passengerStore.analysisParams.startDate, passengerStore.analysisParams.endDate],
  ([newStart, newEnd]) => {
    if (newStart && newStart !== startDate.value) startDate.value = newStart
    if (newEnd && newEnd !== endDate.value) endDate.value = newEnd
  }
)

// 空间分布视图
const spatialView = ref<'map' | 'trend'>('map')

// 趋势粒度
const trendGranularity = ref<'hourly' | 'daily' | 'weekly' | 'monthly'>('daily')

// 热力图数据

const handleTrendGranularityChange = (granularity: 'hourly' | 'daily' | 'weekly' | 'monthly') => {
  if (trendGranularity.value === granularity) return
  trendGranularity.value = granularity
  if (!isLoading.value) {
    loadData()
  }
}

const mapHasFlows = computed(() => passengerStore.flowLines.length > 0)

const applyMapMode = () => {
  mapStore.updateMapConfig({
    showStationMarkers: false,
    showFlowLines: true
  })
}

const syncMapData = () => {
  const stations = Array.isArray(passengerStore.spatialDistribution)
    ? passengerStore.spatialDistribution
    : []
  if (!stations.length) {
    mapStore.setStationMarkers([])
    return
  }

  const maxPassengers = Math.max(...stations.map(s => s.totalPassengers || 0), 1)
  const markers = stations
    .filter(s => Number.isFinite(s.latitude) && Number.isFinite(s.longitude))
    .map((station) => ({
      stationId: station.stationId,
      stationName: station.stationName,
      position: [station.longitude, station.latitude] as [number, number],
      size: calculateMarkerSize(station.totalPassengers || 0, 20, 60, maxPassengers),
      color: calculateMarkerColor(station.totalPassengers || 0, maxPassengers),
      passengerCount: station.totalPassengers || 0,
      data: station
    }))

  mapStore.setStationMarkers(markers)

  if (markers.length > 0) {
    mapStore.updateViewState({
      center: calculateCenter(markers)
    })
  }

  const markerMap = new Map(markers.map(marker => [marker.stationId, marker]))
  const flowLines = Array.isArray(passengerStore.flowLines)
    ? passengerStore.flowLines
    : []
  if (!flowLines.length) {
    mapStore.clearFlowLines()
    return
  }
  const lines = flowLines.map((flow) => {
      const from = markerMap.get(flow.fromStationId)
      const to = markerMap.get(flow.toStationId)
      if (!from || !to) return null
        const line = createFlowLine(
          { id: from.stationId, position: from.position, name: from.stationName },
          { id: to.stationId, position: to.position, name: to.stationName },
          flow.passengerCount
        )
      const color = flow.intensity === 'high' ? '#f44336' :
        flow.intensity === 'medium' ? '#ff9800' : '#4caf50'
      return { ...line, color, dashArray: flow.intensity === 'low' ? '6,6' : 'solid' }
    })
    .filter(Boolean) as any[]

  mapStore.setFlowLines(lines)
}


// 初始化时间范围
onMounted(async () => {
  const synced = await passengerStore.syncDateRangeFromStats()
  if (synced) {
    selectedRange.value = 'custom'
    startDate.value = passengerStore.analysisParams.startDate
    endDate.value = passengerStore.analysisParams.endDate
  }
  applyMapMode()
  await loadData()
})

// KPI数据
const kpiData = ref<KpiData>({
  totalPassengers: 0,
  totalTrains: 0,
  busyStations: 0,
  totalRevenue: 0,
  trends: {
    totalPassengers: 0,
    totalTrains: 0,
    busyStations: 0,
    totalRevenue: 0
  }
})

// 加载状态
const isLoading = ref(false)
const isRefreshing = ref(false)

// 获取当前时间范围
const getCurrentTimeRange = (): TimeRange => {
  return {
    startDate: passengerStore.analysisParams.startDate,
    endDate: passengerStore.analysisParams.endDate,
    rangeType: selectedRange.value
  }
}

// 加载数据
const loadData = async () => {
  try {
    isLoading.value = true
    if (startDate.value && endDate.value) {
      passengerStore.setTimeRange(startDate.value, endDate.value)
      startDate.value = passengerStore.analysisParams.startDate
      endDate.value = passengerStore.analysisParams.endDate
    }
    const timeRange = getCurrentTimeRange()

    // 并行加载所有数据
    const results = await Promise.allSettled([
      apiService.getKpiData(timeRange),
      apiService.getStations({ ...timeRange, page_size: 100 }).then((res: any) => res?.results ?? res ?? []),
      apiService.getTrendData(timeRange, trendGranularity.value),
      apiService.getTimePeriodData(timeRange)
    ])

    const [kpiResult, stationsResult, trendResult, timePeriodResult] = results

    if (kpiResult.status === 'fulfilled') {
      kpiData.value = kpiResult.value
    } else {
      console.error('KPI加载失败:', kpiResult.reason)
    }

    if (stationsResult.status === 'fulfilled') {
      stationsData.value = stationsResult.value
    } else {
      console.error('站点加载失败:', stationsResult.reason)
    }

    if (trendResult.status === 'fulfilled') {
      trendData.value = trendResult.value
    } else {
      console.error('趋势加载失败:', trendResult.reason)
    }

    if (timePeriodResult.status === 'fulfilled') {
      timePeriodsData.value = timePeriodResult.value
    } else {
      console.error('时段加载失败:', timePeriodResult.reason)
    }

    await Promise.allSettled([
      passengerStore.fetchSpatialDistribution(),
      passengerStore.fetchFlowLines()
    ])
    syncMapData()

  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  if (isRefreshing.value) return

  isRefreshing.value = true

  try {
    const timeRange = getCurrentTimeRange()

    await apiService.refreshData(timeRange)

    // 重新加载数据
    await loadData()
  } catch (error) {
    console.error('刷新数据失败:', error)
    // 可以在这里添加用户友好的错误提示
  } finally {
    isRefreshing.value = false
  }
}

// 初始加载在上面的 onMounted 里完成

// 初始加载在上面的 onMounted 里完成

// 数据变量
const stationsData = ref<Station[]>([])
const trendData = ref<TrendData[]>([])
const timePeriodsData = ref<TimePeriodData[]>([])

</script>

<style scoped>
@keyframes ripple {
  0% {
    transform: scale(0, 0);
    opacity: 0.5;
  }
  20% {
    transform: scale(25, 25);
    opacity: 0.3;
  }
  100% {
    opacity: 0;
    transform: scale(40, 40);
  }
}

.dashboard {
  padding: var(--spacing-4);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-6);
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-2) 0;
}

.page-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-3);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  border-radius: var(--border-radius-base);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%, -50%);
  transform-origin: 50% 50%;
}

.btn:focus:not(:active)::after {
  animation: ripple 1s ease-out;
}

.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-outline {
  background-color: transparent;
  color: var(--color-text-primary);
  border-color: var(--color-border);
}

.btn-outline:hover {
  background-color: var(--color-bg-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.btn-outline:active {
  transform: translateY(0);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-sm {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
}

.btn svg {
  width: 16px;
  height: 16px;
}

.time-filter {
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-4);
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
}

.filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.filter-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.filter-buttons {
  display: flex;
  gap: var(--spacing-2);
}

.filter-btn {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-sm);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-btn.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.date-picker {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.date-input {
  padding: var(--spacing-1) var(--spacing-2);
  font-size: var(--font-size-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.date-separator {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.filter-stats {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--border-radius-base);
  border: 1px solid var(--color-border);
}

.stat-label {
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.stat-value {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.stat-duration {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
}

/* KPI卡片 */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

@media (min-width: 768px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.kpi-card {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp var(--transition-base) forwards;
}

.kpi-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

.kpi-card:nth-child(1) { animation-delay: 100ms; }
.kpi-card:nth-child(2) { animation-delay: 200ms; }
.kpi-card:nth-child(3) { animation-delay: 300ms; }
.kpi-card:nth-child(4) { animation-delay: 400ms; }

.kpi-skeleton {
  width: 100%;
}

.kpi-skeleton .skeleton-loader {
  margin: 0;
}

.kpi-skeleton .skeleton-line {
  height: 24px;
  margin-bottom: var(--spacing-2);
}

.kpi-skeleton .skeleton-line:last-child {
  height: 16px;
  margin-bottom: 0;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon svg {
  width: 24px;
  height: 24px;
}

.kpi-icon.total-passengers {
  background-color: rgba(70, 130, 180, 0.1);
  color: var(--color-secondary);
}

.kpi-icon.total-trains {
  background-color: rgba(46, 139, 87, 0.1);
  color: var(--color-success);
}

.kpi-icon.busy-stations {
  background-color: rgba(210, 105, 30, 0.1);
  color: var(--color-accent);
}

.kpi-icon.revenue {
  background-color: rgba(112, 128, 144, 0.1);
  color: var(--color-neutral);
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.kpi-trend.positive {
  color: var(--color-success);
}

.kpi-trend.negative {
  color: var(--color-error);
}

.kpi-trend svg {
  width: 12px;
  height: 12px;
}

.kpi-content {
  margin-bottom: var(--spacing-4);
}

.kpi-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-1) 0;
  line-height: 1;
}

.kpi-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.kpi-footer {
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--color-border-light);
}

.kpi-period {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* 图表区域 */
.chart-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

@media (min-width: 1024px) {
  .chart-grid {
    grid-template-columns: 2fr 1fr;
  }
}

.chart-card {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.map-card {
  grid-column: 1 / -1;
}

@media (min-width: 1024px) {
  .map-card {
    grid-column: 1 / -1;
  }
}

@media (min-width: 1024px) {
  .analysis-card {
    grid-column: 1 / -1;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.card-actions {
  display: flex;
  gap: var(--spacing-2);
}

.card-action-btn {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.card-action-btn.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.card-body {
  padding: var(--spacing-4);
}

.map-placeholder,
.chart-placeholder {
  height: 300px;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.mock-map {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-grid {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  grid-template-rows: repeat(10, 1fr);
}

.grid-line {
  border-right: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
}

.station-marker {
  position: absolute;
  transform: translate(-50%, -50%);
}

.marker-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--color-primary);
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.marker-dot.large {
  width: 32px;
  height: 32px;
  background-color: var(--color-error);
}

.marker-dot.medium {
  width: 24px;
  height: 24px;
  background-color: var(--color-warning);
}

.marker-dot.small {
  width: 16px;
  height: 16px;
  background-color: var(--color-success);
}

.marker-label {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  font-size: var(--font-size-xs);
  white-space: nowrap;
  background-color: white;
  padding: 2px 4px;
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-sm);
}

.map-legend {
  position: absolute;
  bottom: var(--spacing-4);
  left: var(--spacing-4);
  background-color: white;
  padding: var(--spacing-3);
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-md);
  display: flex;
  gap: var(--spacing-3);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-xs);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-color.large {
  background-color: var(--color-error);
}

.legend-color.medium {
  background-color: var(--color-warning);
}

.legend-color.small {
  background-color: var(--color-success);
}

/* 流向图样式 */
.flow-container {
  height: 300px;
}

.station-map-container {
  height: 460px;
  border-radius: var(--border-radius-base);
  overflow: hidden;
  background-color: var(--color-bg-secondary);
  position: relative;
}

.trend-panel {
  min-height: 460px;
}

.gaode-map-container {
  width: 100%;
  height: 100%;
}

.map-empty {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  background: rgba(255, 255, 255, 0.9);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-full);
}

.flow-placeholder {
  height: 100%;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.flow-map {
  width: 100%;
  height: 100%;
  position: relative;
}

.flow-grid {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  grid-template-rows: repeat(10, 1fr);
}

.flow-line {
  position: absolute;
  height: 4px;
  background-color: var(--color-primary);
  border-radius: var(--border-radius-full);
  transform-origin: left center;
}

.flow-line::before {
  content: '';
  position: absolute;
  right: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid var(--color-primary);
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
}

.flow-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: var(--font-size-xs);
  background-color: white;
  padding: 2px 6px;
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
}

.flow-legend {
  position: absolute;
  bottom: var(--spacing-4);
  left: var(--spacing-4);
  background-color: white;
  padding: var(--spacing-3);
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-md);
  display: flex;
  gap: var(--spacing-3);
}

.legend-line {
  width: 30px;
  height: 4px;
  border-radius: var(--border-radius-full);
}

.legend-line.high {
  background-color: var(--color-error);
}

.legend-line.medium {
  background-color: var(--color-warning);
}

.legend-line.low {
  background-color: var(--color-success);
}

.mock-chart {
  width: 100%;
  height: 100%;
  position: relative;
}

.chart-line {
  position: absolute;
  bottom: 40px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--color-primary);
}

.data-point {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-primary);
  transform: translate(-50%, 50%);
}

.chart-axis {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
}

.axis-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.ranking-list,
.load-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.ranking-item,
.load-item {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-3);
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
}

.rank {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-full);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.station-info,
.line-info {
  display: flex;
  flex-direction: column;
}

.station-name,
.line-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.station-code,
.line-code {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.passenger-count,
.load-percentage {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.progress-bar,
.load-bar {
  width: 100px;
  height: 8px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.progress-fill,
.load-fill {
  height: 100%;
  background-color: var(--color-primary);
  border-radius: var(--border-radius-full);
  transition: width var(--transition-slow);
}

.load-fill.high {
  background-color: var(--color-error);
}

.load-fill.medium {
  background-color: var(--color-warning);
}

.load-fill.low {
  background-color: var(--color-success);
}

.load-status {
  font-size: var(--font-size-xs);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius-full);
  font-weight: var(--font-weight-medium);
}

.load-status.high {
  background-color: rgba(220, 20, 60, 0.1);
  color: var(--color-error);
}

.load-status.medium {
  background-color: rgba(255, 165, 0, 0.1);
  color: var(--color-warning);
}

.load-status.low {
  background-color: rgba(46, 139, 87, 0.1);
  color: var(--color-success);
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

@media (max-width: 1024px) {
  .load-bar-item {
    grid-template-columns: 1fr;
    gap: var(--spacing-2);
  }

  .bar-stats {
    flex-wrap: wrap;
    gap: var(--spacing-2);
  }

  .load-summary {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .load-summary {
    grid-template-columns: 1fr;
  }

  .bar-container {
    gap: var(--spacing-1);
  }

  .bar-comparison {
    flex-wrap: wrap;
  }
}

/* 数据表格 */
.data-table-section {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.section-actions {
  display: flex;
  gap: var(--spacing-3);
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: var(--spacing-3) var(--spacing-4);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
  border-bottom: 2px solid var(--color-border);
  white-space: nowrap;
}

.data-table td {
  padding: var(--spacing-3) var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background-color: var(--color-bg-secondary);
}

.train-code {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.train-type {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.occupancy {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.occupancy-bar {
  width: 60px;
  height: 6px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.occupancy-fill {
  height: 100%;
  background-color: var(--color-primary);
  border-radius: var(--border-radius-full);
}

.occupancy-percentage {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  min-width: 40px;
}

.status-badge {
  display: inline-block;
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border-radius: var(--border-radius-full);
}

.status-badge.running {
  background-color: rgba(46, 139, 87, 0.1);
  color: var(--color-success);
}

.status-badge.scheduled {
  background-color: rgba(70, 130, 180, 0.1);
  color: var(--color-secondary);
}

.table-footer {
  padding: var(--spacing-4);
  border-top: 1px solid var(--color-border-light);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-4);
}

.pagination-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn svg {
  width: 16px;
  height: 16px;
}

.pagination-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
</style>
