<template>
  <div class="passenger-flow-analysis">
    <div class="analysis-header">
      <h3 class="analysis-title">{{ title }}</h3>
      <div class="analysis-controls">
        <button
          class="control-btn"
          :class="{ active: analysisType === 'stations' }"
          @click="changeAnalysisType('stations')"
        >
          站点分析
        </button>
        <button
          class="control-btn"
          :class="{ active: analysisType === 'lines' }"
          @click="changeAnalysisType('lines')"
        >
          线路分析
        </button>
        <button
          class="control-btn"
          :class="{ active: analysisType === 'time' }"
          @click="changeAnalysisType('time')"
        >
          时段分析
        </button>
        <div class="metric-selector">
          <select v-model="selectedMetric" class="metric-select">
            <option value="total">总客流量</option>
            <option value="inbound">到达客流</option>
            <option value="outbound">发送客流</option>
            <option value="transfer">中转客流</option>
          </select>
        </div>
      </div>
    </div>

    <div class="analysis-content">
      <!-- 站点分析 -->
      <div v-if="analysisType === 'stations'" class="station-analysis">
        <div class="analysis-chart">
          <div class="chart-container">
            <div class="bar-chart">
              <div
                v-for="station in topStations"
                :key="station.id"
                class="bar-item"
              >
                <div class="bar-label">
                  <span class="station-name">{{ station.name }}</span>
                  <span class="station-code">{{ station.code }}</span>
                </div>
                <div class="bar-track">
                  <div
                    class="bar-fill"
                    :style="{ width: station.percentage + '%' }"
                    :class="getBarClass(station.percentage)"
                  >
                    <span class="bar-value">{{ station[selectedMetric].toLocaleString() }}</span>
                  </div>
                </div>
                <div class="bar-percentage">{{ station.percentage }}%</div>
                <div class="bar-trend" :class="station.trend >= 0 ? 'positive' : 'negative'">
                  <span>{{ station.trend >= 0 ? '+' : '' }}{{ station.trend }}%</span>
                  <svg v-if="station.trend >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="analysis-stats">
          <div class="stats-card">
            <div class="stats-value">{{ formatNumber(totalPassengers) }}</div>
            <div class="stats-label">总客流量</div>
            <div class="stats-detail">{{ dateRangeLabel }}</div>
          </div>
          <div class="stats-card">
            <div class="stats-value">{{ peakStation.name }}</div>
            <div class="stats-label">最繁忙站点</div>
            <div class="stats-detail">{{ peakStation.value.toLocaleString() }} 人</div>
          </div>
          <div class="stats-card">
            <div class="stats-value">{{ avgPassengersPerStation.toLocaleString() }}</div>
            <div class="stats-label">站点平均客流</div>
            <div class="stats-detail">{{ dateRangeLabel }}</div>
          </div>
          <div class="stats-card">
            <div class="stats-value">{{ growthRate }}%</div>
            <div class="stats-label">同比增长</div>
            <div class="stats-detail">较去年同期</div>
          </div>
        </div>
      </div>

      <!-- 线路分析 -->
      <div v-else-if="analysisType === 'lines'" class="line-analysis">
        <div class="line-chart">
          <div class="chart-container">
            <div class="line-list">
              <div
                v-for="line in lineData"
                :key="line.id"
                class="line-item"
              >
                <div class="line-info">
                  <div class="line-name">{{ line.code || line.name }}</div>
                  <div class="line-code">{{ line.name || line.code }}</div>
                </div>
                <div class="line-metrics">
                  <div class="metric">
                    <span class="metric-label">总客流：</span>
                    <span class="metric-value">{{ line.totalPassengers.toLocaleString() }}</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">上座率：</span>
                    <span class="metric-value">{{ line.occupancyRate }}%</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">满载率：</span>
                    <span class="metric-value">{{ line.loadRate }}%</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">运营效率：</span>
                    <span class="metric-value">{{ line.efficiency }}%</span>
                  </div>
                </div>
                <div class="line-progress">
                  <div class="progress-track">
                    <div
                      class="progress-fill"
                      :style="{ width: line.occupancyRate + '%' }"
                      :class="getLoadClass(line.occupancyRate)"
                    ></div>
                  </div>
                  <div class="progress-label">上座率</div>
                </div>
                <div class="line-trend" :class="line.trend >= 0 ? 'positive' : 'negative'">
                  <span>{{ line.trend >= 0 ? '+' : '' }}{{ line.trend }}%</span>
                  <svg v-if="line.trend >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 时段分析 -->
      <div v-else class="time-analysis">
        <div class="time-chart">
          <div class="chart-container">
            <div class="time-distribution">
              <div class="time-periods">
                <div
                  v-for="period in timePeriods"
                  :key="period.id"
                  class="period-item"
                >
                  <div class="period-info">
                    <div class="period-name">{{ period.name }}</div>
                    <div class="period-time">{{ period.time }}</div>
                  </div>
                  <div class="period-metrics">
                    <div class="metric">
                      <span class="metric-label">客流量：</span>
                      <span class="metric-value">{{ period.passengers.toLocaleString() }}</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">占比：</span>
                      <span class="metric-value">{{ period.percentage }}%</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">车次：</span>
                      <span class="metric-value">{{ period.trains }}</span>
                    </div>
                  </div>
                  <div class="period-progress">
                    <div class="progress-track">
                      <div
                        class="progress-fill"
                        :style="{ width: period.percentage + '%' }"
                        :class="getPeriodClass(period.percentage)"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="time-stats">
          <div class="stats-card">
            <div class="stats-value">{{ peakPeriod.name }}</div>
            <div class="stats-label">高峰时段</div>
            <div class="stats-detail">{{ peakPeriod.passengers.toLocaleString() }} 人</div>
          </div>
          <div class="stats-card">
            <div class="stats-value">{{ offPeakPeriod.name }}</div>
            <div class="stats-label">低谷时段</div>
            <div class="stats-detail">{{ offPeakPeriod.passengers.toLocaleString() }} 人</div>
          </div>
          <div class="stats-card">
            <div class="stats-value">{{ peakToOffPeakRatio }}:1</div>
            <div class="stats-label">峰谷比</div>
            <div class="stats-detail">高峰/低谷</div>
          </div>
          <div class="stats-card">
            <div class="stats-value">{{ avgPassengersPerHour.toLocaleString() }}</div>
            <div class="stats-label">小时均客流</div>
            <div class="stats-detail">今日平均</div>
          </div>
        </div>
      </div>
    </div>

    <div class="analysis-footer">
      <div class="footer-info">
        <span class="info-label">数据更新时间：</span>
        <span class="info-value">{{ lastUpdateTime }} (v2.0)</span>
      </div>
      <div class="footer-actions">
        <button class="footer-btn" @click="refreshData">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C14.1974 3 16.1958 3.86095 17.6576 5.27264M21 3V7M21 7H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          刷新数据
        </button>
        <button class="footer-btn secondary">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
>
            <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          导出报告
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import api from '@/services/api'

interface StationData {
  id: number
  name: string
  code: string
  total: number
  inbound: number
  outbound: number
  transfer: number
  percentage: number
  trend: number
}

interface LineData {
  id: number
  name: string
  code: string
  totalPassengers: number
  occupancyRate: number
  loadRate: number
  efficiency: number
  trend: number
}

interface TimePeriod {
  id: number
  name: string
  time: string
  passengers: number
  percentage: number
  trains: number
}

const props = withDefaults(defineProps<{
  title?: string
  startDate?: string
  endDate?: string
}>(), {
  title: '客流量分析'
})

const title = computed(() => props.title)

// 分析类型
const analysisType = ref<'stations' | 'lines' | 'time'>('stations')

// 选择的指标
const selectedMetric = ref<'total' | 'inbound' | 'outbound' | 'transfer'>('total')

// 站点数据
const topStations = ref<StationData[]>([])

// 线路数据
const lineData = ref<LineData[]>([])

// 时段数据
const timePeriods = ref<TimePeriod[]>([])

const dateRangeLabel = computed(() => {
  if (props.startDate && props.endDate) {
    return `${props.startDate} 至 ${props.endDate}`
  }
  return '今日累计'
})

// 统计数据
const totalPassengers = computed(() => {
  return topStations.value.reduce((sum, station) => sum + station.total, 0)
})

const avgPassengersPerStation = computed(() => {
  if (topStations.value.length === 0) {
    return 0
  }
  return Math.round(totalPassengers.value / topStations.value.length)
})

const peakStation = computed(() => {
  if (topStations.value.length === 0) {
    return { name: '暂无数据', value: 0 }
  }
  const station = topStations.value.reduce((max, s) => s.total > max.total ? s : max, topStations.value[0]!)
  return {
    name: station.name,
    value: station.total
  }
})

const growthRate = computed(() => {
  return 0
})

const peakPeriod = computed(() => {
  if (timePeriods.value.length === 0) {
    return { id: 0, name: '暂无数据', time: '', passengers: 0, percentage: 0, trains: 0 }
  }
  return timePeriods.value.reduce((max, p) => p.passengers > max.passengers ? p : max, timePeriods.value[0]!)
})

const offPeakPeriod = computed(() => {
  if (timePeriods.value.length === 0) {
    return { id: 0, name: '暂无数据', time: '', passengers: 0, percentage: 0, trains: 0 }
  }
  return timePeriods.value.reduce((min, p) => p.passengers < min.passengers ? p : min, timePeriods.value[0]!)
})

const peakToOffPeakRatio = computed(() => {
  if (offPeakPeriod.value.passengers === 0) {
    return '0.0'
  }
  const ratio = peakPeriod.value.passengers / offPeakPeriod.value.passengers
  return ratio.toFixed(1)
})

const avgPassengersPerHour = computed(() => {
  if (timePeriods.value.length === 0) {
    return 0
  }
  const total = timePeriods.value.reduce((sum, p) => sum + p.passengers, 0)
  return Math.round(total / timePeriods.value.length)
})

const lastUpdateTime = computed(() => {
  const now = new Date()
  return now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

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

// 获取柱状图类
const getBarClass = (percentage: number): string => {
  if (percentage > 80) return 'bar-high'
  if (percentage > 50) return 'bar-medium'
  return 'bar-low'
}

// 获取负载类
const getLoadClass = (rate: number): string => {
  if (rate > 80) return 'load-high'
  if (rate > 60) return 'load-medium'
  return 'load-low'
}

// 获取时段类
const getPeriodClass = (percentage: number): string => {
  if (percentage > 30) return 'period-high'
  if (percentage > 15) return 'period-medium'
  return 'period-low'
}

// 切换分析类型
const changeAnalysisType = (type: 'stations' | 'lines' | 'time') => {
  analysisType.value = type
}

// 刷新数据
const refreshData = async () => {
  console.log('刷新客流量分析数据')
  await fetchData()
}

const fetchData = async () => {
  try {
    const params = {
      start_date: props.startDate,
      end_date: props.endDate,
      _t: new Date().getTime()
    }

    console.log('Fetching analytics data in parallel with params:', params)

    // 并行请求所有数据
    const results = await Promise.allSettled([
      api.get<any[]>('/passenger-flows/station_ranking/', { params }),
      api.get<any[]>('/analytics/line-loads/', { params }),
      api.get<any[]>('/analytics/time-periods/', { params: { ...params, granularity: 'period' } })
    ])

    const stationRes = results[0].status === 'fulfilled' ? results[0].value : []
    const lineRes = results[1].status === 'fulfilled' ? results[1].value : []
    const timeRes = results[2].status === 'fulfilled' ? results[2].value : []

    if (results[0].status === 'rejected') {
      console.error('Station ranking加载失败:', results[0].reason)
    }
    if (results[1].status === 'rejected') {
      console.error('Line loads加载失败:', results[1].reason)
    }
    if (results[2].status === 'rejected') {
      console.error('Time periods加载失败:', results[2].reason)
    }

    // 1. Process Station Data
    console.log('Station response:', stationRes)
    if (Array.isArray(stationRes)) {
      const maxTotal = stationRes.length > 0 ? stationRes[0].total_passengers : 1
      topStations.value = stationRes.slice(0, 5).map((item: any) => ({
        id: item.station_id,
        name: item.station_name,
        code: item.station_telecode,
        total: item.total_passengers,
        inbound: item.passengers_in,
        outbound: item.passengers_out,
        transfer: 0,
        percentage: Math.round((item.total_passengers / maxTotal) * 100),
        trend: item.trend || 0
      }))
    } else {
      topStations.value = []
    }

    // 2. Process Line Data
    if (Array.isArray(lineRes)) {
      lineData.value = lineRes.map((item: any) => ({
        id: item.lineId,
        name: item.lineName,
        code: item.lineCode,
        totalPassengers: item.totalPassengers,
        occupancyRate: item.occupancyRate,
        loadRate: item.loadRate,
        efficiency: item.efficiency,
        trend: item.trend || 0
      }))
    } else {
      lineData.value = []
    }

    // 3. Process Time Period Data
    if (Array.isArray(timeRes)) {
      timePeriods.value = timeRes.map((item: any) => ({
        id: item.id,
        name: item.name,
        time: item.time,
        passengers: item.passengers,
        percentage: item.percentage,
        trains: item.trains
      }))
    } else {
      timePeriods.value = []
    }

  } catch (error) {
    console.error('Failed to fetch analytics data:', error)
  }
}

// 监听日期变化
watch(() => [props.startDate, props.endDate], ([newStart, newEnd]) => {
  if (newStart && newEnd) {
    fetchData()
  }
})

// 初始化
onMounted(() => {
  if (props.startDate && props.endDate) {
    fetchData()
  }
})
</script>

<style scoped>
.passenger-flow-analysis {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
}

.analysis-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.analysis-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.analysis-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.control-btn {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.control-btn:hover {
  background-color: var(--color-bg-tertiary);
}

.control-btn.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.metric-selector {
  position: relative;
}

.metric-select {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-primary);
  cursor: pointer;
  appearance: none;
  padding-right: var(--spacing-6);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--spacing-2) center;
  background-size: 12px;
}

.analysis-content {
  margin-bottom: var(--spacing-4);
}

.station-analysis,
.line-analysis,
.time-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.chart-container {
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-4);
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.bar-item {
  display: grid;
  grid-template-columns: 150px 1fr 60px 60px;
  align-items: center;
  gap: var(--spacing-4);
}

.bar-label {
  display: flex;
  flex-direction: column;
}

.station-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.station-code {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.bar-track {
  height: 24px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  border-radius: var(--border-radius-full);
  transition: width var(--transition-slow);
  position: relative;
}

.bar-fill.bar-high {
  background-color: var(--color-error);
}

.bar-fill.bar-medium {
  background-color: var(--color-warning);
}

.bar-fill.bar-low {
  background-color: var(--color-success);
}

.bar-value {
  position: absolute;
  right: var(--spacing-2);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-xs);
  color: white;
  font-weight: var(--font-weight-medium);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.bar-percentage {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  text-align: center;
}

.bar-trend {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  justify-content: center;
}

.bar-trend.positive {
  color: var(--color-success);
}

.bar-trend.negative {
  color: var(--color-error);
}

.bar-trend svg {
  width: 12px;
  height: 12px;
}

.analysis-stats,
.time-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-3);
}

.stats-card {
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-3);
  text-align: center;
}

.stats-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-1);
}

.stats-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-1);
}

.stats-detail {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.line-list,
.time-periods {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.line-item,
.period-item {
  display: grid;
  grid-template-columns: 150px 1fr 200px 60px;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-3);
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-base);
}

.line-info,
.period-info {
  display: flex;
  flex-direction: column;
}

.line-name,
.period-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.line-code,
.period-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.line-metrics,
.period-metrics {
  display: flex;
  gap: var(--spacing-4);
}

.metric {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.metric-value {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.line-progress,
.period-progress {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.progress-track {
  height: 8px;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: var(--border-radius-full);
  transition: width var(--transition-slow);
}

.progress-fill.load-high,
.progress-fill.period-high {
  background-color: var(--color-error);
}

.progress-fill.load-medium,
.progress-fill.period-medium {
  background-color: var(--color-warning);
}

.progress-fill.load-low,
.progress-fill.period-low {
  background-color: var(--color-success);
}

.progress-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: center;
}

.line-trend {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  justify-content: center;
}

.line-trend.positive {
  color: var(--color-success);
}

.line-trend.negative {
  color: var(--color-error);
}

.line-trend svg {
  width: 12px;
  height: 12px;
}

.analysis-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border-light);
}

.footer-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.info-label {
  color: var(--color-text-tertiary);
}

.info-value {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.footer-actions {
  display: flex;
  gap: var(--spacing-3);
}

.footer-btn {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-sm);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.footer-btn:hover {
  background-color: var(--color-bg-tertiary);
}

.footer-btn svg {
  width: 14px;
  height: 14px;
}

.footer-btn.secondary {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.footer-btn.secondary:hover {
  background-color: var(--color-primary-dark);
}

@media (max-width: 1024px) {
  .bar-item,
  .line-item,
  .period-item {
    grid-template-columns: 1fr;
    gap: var(--spacing-2);
  }

  .analysis-stats,
  .time-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .line-metrics,
  .period-metrics {
    flex-wrap: wrap;
    gap: var(--spacing-2);
  }
}

@media (max-width: 768px) {
  .analysis-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-3);
  }

  .analysis-controls {
    flex-wrap: wrap;
    gap: var(--spacing-2);
  }

  .analysis-stats,
  .time-stats {
    grid-template-columns: 1fr;
  }

  .analysis-footer {
    flex-direction: column;
    gap: var(--spacing-3);
    align-items: flex-start;
  }

  .footer-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
