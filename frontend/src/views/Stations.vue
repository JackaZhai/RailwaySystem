<template>
  <div class="stations-view">
    <div class="page-header">
      <div class="header-content">
        <h1>站点评估</h1>
        <p>多维度评估客运站点的运营效率与服务能力</p>
      </div>
      <div class="header-actions">
        <div class="date-filter">
          <input
            v-model="timeRange.startDate"
            type="date"
            class="date-input"
            @change="handleDateRangeChange"
          />
          <span class="date-separator">至</span>
          <input
            v-model="timeRange.endDate"
            type="date"
            class="date-input"
            @change="handleDateRangeChange"
          />
        </div>
        <span v-if="dateRangeError" class="date-error">{{ dateRangeError }}</span>
        <button class="btn-refresh" :disabled="loading" @click="fetchData">
          {{ loading ? '加载中...' : '刷新数据' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在分析站点数据...</p>
    </div>

    <div v-else class="content-grid">
      <!-- 1. 站点繁忙度评估 -->
      <section class="assessment-section">
        <div class="section-header">
          <h2>1. 站点繁忙度评估</h2>
          <span class="subtitle">基于旅客发送量、到达量的综合繁忙指数</span>
        </div>
        
        <div class="charts-row">
          <!-- 繁忙站点排名 -->
          <div class="card ranking-card">
            <h3>繁忙站点排名 (Top 10)</h3>
            <div v-if="rankingChartData.length > 0" class="chart-container">
              <BarChart :data="rankingChartData" />
            </div>
            <div v-else class="no-data">
              暂无数据
            </div>
          </div>
          
          <!-- 客流时间分布 -->
          <div class="card distribution-card">
            <div class="distribution-header">
              <h3 class="distribution-title">站点客流时间分布 (高峰时段识别)</h3>
              <div class="distribution-controls">
                <select v-model="selectedTimeDistributionStationId" class="distribution-select">
                  <option :value="null">全部站点</option>
                  <option v-for="opt in stationOptionsForTimeDistribution" :key="opt.id" :value="opt.id">
                    {{ opt.name }}
                  </option>
                </select>
                <span v-if="timeDistributionViewModel.peakRatio > 0" class="distribution-ratio">
                  峰均比 {{ timeDistributionViewModel.peakRatio.toFixed(2) }}
                </span>
              </div>
            </div>
            <div v-if="timeDistributionViewModel.data.length > 0" class="chart-container">
              <TimeDistributionChart
                :data="timeDistributionViewModel.data"
                title="站点客流时间分布"
                subtitle="24小时客流分布情况"
                height="300px"
                :show-actions="true"
                :show-stats="false"
                :show-periods="false"
              />
            </div>
            <div v-else class="no-data">暂无数据</div>
            <div v-if="peakHours.length" class="peak-info">
              <span class="label">识别到的高峰时段:</span>
              <span v-for="hour in peakHours" :key="hour" class="tag">{{ hour }}</span>
            </div>
          </div>
        </div>

        <div class="card ranking-table-card">
          <div class="ranking-table-header">
            <div class="ranking-table-title">
              <h3>繁忙站点完整排名</h3>
              <p class="ranking-table-subtitle">支持分页、搜索与权重调整</p>
            </div>
            <div class="ranking-table-actions">
              <input
                v-model="busyRankingQuery"
                class="ranking-search"
                placeholder="搜索站点名称"
                @keyup.enter="handleBusySearch"
              />
              <button class="btn-refresh btn-small" :disabled="busyRankingLoading" @click="handleBusySearch">
                {{ busyRankingLoading ? '加载中...' : '查询' }}
              </button>
            </div>
          </div>

          <div class="ranking-weights">
            <div class="weight-item">
              <span class="weight-label">发送权重</span>
              <input v-model.number="busyWeights.wSend" type="number" step="0.05" min="0" max="1" class="weight-input" />
            </div>
            <div class="weight-item">
              <span class="weight-label">到达权重</span>
              <input v-model.number="busyWeights.wArrive" type="number" step="0.05" min="0" max="1" class="weight-input" />
            </div>
            <div class="weight-item">
              <span class="weight-label">中转权重</span>
              <input v-model.number="busyWeights.wTransfer" type="number" step="0.05" min="0" max="1" class="weight-input" />
            </div>
            <button class="btn-refresh btn-small" :disabled="busyRankingLoading" @click="applyBusyWeights">
              应用权重
            </button>
          </div>

          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>排名</th>
                  <th>站点名称</th>
                  <th>繁忙指数</th>
                  <th>发送量</th>
                  <th>到达量</th>
                  <th>中转量</th>
                  <th>高峰时段</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in busyRanking" :key="row.stationId">
                  <td>{{ row.rank }}</td>
                  <td>{{ row.stationName }}</td>
                  <td>{{ row.busyIndex.toFixed(2) }}</td>
                  <td>{{ formatNumber(row.send) }}</td>
                  <td>{{ formatNumber(row.arrive) }}</td>
                  <td>{{ formatNumber(row.transfer) }}</td>
                  <td>{{ row.peakHour || '-' }}</td>
                </tr>
              </tbody>
            </table>
            <div v-if="!busyRankingLoading && busyRanking.length === 0" class="no-data">
              暂无数据
            </div>
          </div>

          <div class="ranking-pagination">
            <div class="pagination-info">
              共 {{ busyRankingCount.toLocaleString() }} 条
            </div>
            <div class="pagination-controls">
              <button class="pagination-btn" :disabled="busyRankingPage <= 1 || busyRankingLoading" @click="handleBusyPageChange(busyRankingPage - 1)">
                上一页
              </button>
              <span class="pagination-page">
                第 {{ busyRankingPage }} / {{ busyRankingTotalPages }} 页
              </span>
              <button class="pagination-btn" :disabled="busyRankingPage >= busyRankingTotalPages || busyRankingLoading" @click="handleBusyPageChange(busyRankingPage + 1)">
                下一页
              </button>
              <select class="page-size-select" :value="busyRankingPageSize" @change="handleBusyPageSizeChange">
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
            </div>
          </div>
        </div>
      </section>

      <!-- 2. 站点功能角色分析 -->
      <section class="assessment-section">
        <div class="section-header">
          <h2>2. 站点功能角色分析</h2>
          <span class="subtitle">基于OD客流数据的站点分类与角色识别</span>
        </div>

        <div class="charts-row">
          <!-- 角色分布饼图 -->
          <div class="card role-chart-card">
            <h3>站点角色分布</h3>
            <div class="chart-container">
              <PieChart :data="roleDistributionChartData" />
            </div>
          </div>

          <!-- 重点站点角色列表 -->
          <div class="card role-table-card">
            <h3>重点站点角色详情</h3>
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>站点名称</th>
                    <th>总客流</th>
                    <th>发送占比</th>
                    <th>到达占比</th>
                    <th>连接线路</th>
                    <th>判定角色</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="station in topStationsForRoles" :key="station.id">
                    <td>{{ station.name }}</td>
                    <td>{{ formatNumber(station.totalFlow) }}</td>
                    <td>{{ formatPercent(station.outboundRatio) }}</td>
                    <td>{{ formatPercent(station.inboundRatio) }}</td>
                    <td>{{ station.routeCount || '-' }}</td>
                    <td>
                      <span class="role-tag" :class="station.roleType">
                        {{ station.roleName }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <!-- 3. 服务能力评估 -->
      <section class="assessment-section">
        <div class="section-header">
          <h2>3. 服务能力评估</h2>
          <span class="subtitle">基础设施与客流需求的匹配度分析</span>
        </div>

        <div class="card capacity-card">
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>站点名称</th>
                  <th>预估站台数</th>
                  <th>设计容量 (人/小时)</th>
                  <th>实际高峰客流 (人/小时)</th>
                  <th>高峰时段</th>
                  <th>容量饱和度</th>
                  <th>评估结果</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="station in capacityAssessmentPageData" :key="station.id">
                  <td>{{ station.name }}</td>
                  <td>{{ station.platformCount }}</td>
                  <td>{{ formatNumber(station.designCapacity) }}</td>
                  <td>{{ formatNumber(station.peakFlow) }}</td>
                  <td>{{ station.peakHour || '-' }}</td>
                  <td>
                    <div class="progress-bar-container">
                      <div class="progress-bar" :style="{ width: Math.min(station.saturation * 100, 100) + '%', backgroundColor: getSaturationColor(station.saturation) }"></div>
                      <span class="progress-text">{{ (station.saturation * 100).toFixed(1) }}%</span>
                    </div>
                  </td>
                  <td>
                    <span class="status-tag" :class="station.status">
                      {{ station.statusText }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="ranking-pagination">
            <div class="pagination-info">
              显示 {{ capacityStartIndex + 1 }}-{{ capacityEndIndex }} 条，共 {{ capacityAssessmentAll.length.toLocaleString() }} 条
            </div>
            <div class="pagination-controls">
              <button class="pagination-btn" :disabled="capacityPage <= 1" @click="handleCapacityPageChange(capacityPage - 1)">
                上一页
              </button>
              <span class="pagination-page">
                第 {{ capacityPage }} / {{ capacityTotalPages }} 页
              </span>
              <button class="pagination-btn" :disabled="capacityPage >= capacityTotalPages" @click="handleCapacityPageChange(capacityPage + 1)">
                下一页
              </button>
              <select class="page-size-select" :value="capacityPageSize" @change="handleCapacityPageSizeChange">
                <option :value="10">10</option>
                <option :value="20">20</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive, onUnmounted, watch } from 'vue'
import { apiService, type TimeRange, type StationAssessmentData, type BusyRankingItem, type StationRoleDistributionItem, type StationRoleItem } from '@/services/api'
import BarChart from '@/components/charts/BarChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import TimeDistributionChart from '@/components/passenger/TimeDistributionChart.vue'
import type { TimeDistribution } from '@/types/passenger'
import { format, parseISO, subDays } from 'date-fns'
import { DATE_CONFIG } from '@/config'

// 状态定义
const loading = ref(false)
const isUnmounted = ref(false)
const dateRangeError = ref('')
const timeRange = reactive<TimeRange>({
  startDate: '',
  endDate: '',
  rangeType: 'custom'
})

onUnmounted(() => {
  isUnmounted.value = true
})

// 数据存储
const stationMetrics = ref<StationAssessmentData[]>([])
const timeDistributionData = ref<TimeDistribution[]>([])
const roleAnalysisLoading = ref(false)
const roleDistribution = ref<StationRoleDistributionItem[]>([])
const roleStations = ref<StationRoleItem[]>([])
const busyRankingLoading = ref(false)
const busyRanking = ref<BusyRankingItem[]>([])
const busyRankingCount = ref(0)
const busyRankingPage = ref(1)
const busyRankingPageSize = ref(50)
const busyRankingQuery = ref('')
const busyWeights = reactive({
  wSend: 0.4,
  wArrive: 0.4,
  wTransfer: 0.2,
})
const selectedTimeDistributionStationId = ref<number | null>(null)
const anchorDate = ref<Date | null>(null)

const capacityPage = ref(1)
const capacityPageSize = ref(10)

const toYmd = (date: Date) => format(date, 'yyyy-MM-dd')

const resolveAnchorDate = async () => {
  if (anchorDate.value) return
  try {
    const stats = await apiService.getDataStats()
    const maxDate = stats?.dateRange?.maxDate
    if (maxDate) anchorDate.value = parseISO(maxDate)
  } catch {
    anchorDate.value = null
  }
}

const normalizeDateRange = () => {
  if (!timeRange.startDate || !timeRange.endDate) return
  const start = new Date(timeRange.startDate)
  const end = new Date(timeRange.endDate)
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return
  if (end.getTime() < start.getTime()) {
    const tmp = timeRange.startDate
    timeRange.startDate = timeRange.endDate
    timeRange.endDate = tmp
  }
}

const validateDateRange = () => {
  dateRangeError.value = ''
  if (!timeRange.startDate || !timeRange.endDate) {
    dateRangeError.value = '请选择开始和结束日期'
    return false
  }
  const start = new Date(timeRange.startDate)
  const end = new Date(timeRange.endDate)
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
    dateRangeError.value = '日期格式不合法'
    return false
  }
  const startMs = Math.min(start.getTime(), end.getTime())
  const endMs = Math.max(start.getTime(), end.getTime())
  const days = Math.floor((endMs - startMs) / (1000 * 60 * 60 * 24)) + 1
  if (days > DATE_CONFIG.MAX_RANGE_DAYS) {
    dateRangeError.value = `日期范围过大（最多${DATE_CONFIG.MAX_RANGE_DAYS}天）`
    return false
  }
  return true
}

const ensureDefaultDateRange = () => {
  if (timeRange.startDate && timeRange.endDate) return
  const base = anchorDate.value ?? new Date()
  const end = base
  const start = subDays(base, 29)
  timeRange.startDate = toYmd(start)
  timeRange.endDate = toYmd(end)
}

const busyRankingTotalPages = computed(() => {
  const total = Math.ceil(busyRankingCount.value / busyRankingPageSize.value)
  return total > 0 ? total : 1
})

const getOptionalDateRange = () => {
  if (!timeRange.startDate || !timeRange.endDate) return { startDate: undefined as string | undefined, endDate: undefined as string | undefined }
  return {
    startDate: timeRange.startDate || undefined,
    endDate: timeRange.endDate || undefined,
  }
}

const handleDateRangeChange = () => {
  normalizeDateRange()
  if (!validateDateRange()) return
  fetchData()
}

const fetchStationRoleAnalysis = async () => {
  if (roleAnalysisLoading.value) return
  roleAnalysisLoading.value = true

  try {
    const dateRange = getOptionalDateRange()
    if (!dateRange.startDate || !dateRange.endDate) {
      roleDistribution.value = []
      roleStations.value = []
      return
    }
    const result = await apiService.getStationRoleAnalysis({
      rangeType: 'custom',
      startDate: dateRange.startDate,
      endDate: dateRange.endDate,
      page: 1,
      page_size: 5,
    })

    if (isUnmounted.value) return

    roleDistribution.value = result.distribution || []
    roleStations.value = result.results || []
  } catch (error) {
    console.error('获取站点角色分析失败:', error)
    roleDistribution.value = []
    roleStations.value = []
  } finally {
    roleAnalysisLoading.value = false
  }
}

const fetchBusyRanking = async () => {
  if (busyRankingLoading.value) return
  busyRankingLoading.value = true

  try {
    const dateRange = getOptionalDateRange()
    if (!dateRange.startDate || !dateRange.endDate) {
      busyRanking.value = []
      busyRankingCount.value = 0
      return
    }
    const result = await apiService.getBusyRanking({
      rangeType: 'custom',
      startDate: dateRange.startDate,
      endDate: dateRange.endDate,
      q: busyRankingQuery.value.trim() || undefined,
      page: busyRankingPage.value,
      page_size: busyRankingPageSize.value,
      wSend: busyWeights.wSend,
      wArrive: busyWeights.wArrive,
      wTransfer: busyWeights.wTransfer,
    })

    if (isUnmounted.value) return

    busyRanking.value = result.results || []
    busyRankingCount.value = result.count || 0
  } catch (error) {
    console.error('获取繁忙度排名失败:', error)
    busyRanking.value = []
    busyRankingCount.value = 0
  } finally {
    busyRankingLoading.value = false
  }
}

const handleBusySearch = () => {
  busyRankingPage.value = 1
  fetchBusyRanking()
}

const applyBusyWeights = () => {
  busyRankingPage.value = 1
  fetchBusyRanking()
}

const handleBusyPageChange = (page: number) => {
  busyRankingPage.value = Math.min(Math.max(page, 1), busyRankingTotalPages.value)
  fetchBusyRanking()
}

const handleBusyPageSizeChange = (e: Event) => {
  const target = e.target as HTMLSelectElement | null
  const nextSize = target ? Number(target.value) : 50
  busyRankingPageSize.value = Number.isFinite(nextSize) ? nextSize : 50
  busyRankingPage.value = 1
  fetchBusyRanking()
}

const stationOptionsForTimeDistribution = computed(() => {
  if (busyRanking.value && busyRanking.value.length > 0) {
    return busyRanking.value.map(item => ({
      id: item.stationId,
      name: item.stationName
    }))
  }
  return stationMetrics.value.map(item => ({
    id: item.id,
    name: item.name
  }))
})

const fetchTimeDistribution = async () => {
  try {
    const dateRange = getOptionalDateRange()
    const raw = await apiService.getTimeDistribution({
      startDate: dateRange.startDate,
      endDate: dateRange.endDate,
      stationId: selectedTimeDistributionStationId.value,
    })

    const toNumber = (value: unknown, fallback: number = 0) => {
      const num = typeof value === 'number' ? value : typeof value === 'string' ? Number(value) : NaN
      return Number.isFinite(num) ? num : fallback
    }

    const mapped = (Array.isArray(raw) ? raw : []).map((item: unknown): TimeDistribution => {
      const record = (item ?? {}) as Record<string, unknown>

      const hourRaw = toNumber(record['hour'], 0)
      const hour = Math.min(23, Math.max(0, Math.trunc(hourRaw)))
      const passengersIn = toNumber(record['passengersIn'] ?? record['passengers_in'], 0)
      const passengersOut = toNumber(record['passengersOut'] ?? record['passengers_out'], 0)
      const totalPassengers = toNumber(
        record['totalPassengers'] ?? record['total_passengers'],
        passengersIn + passengersOut
      )
      const avgPassengers = toNumber(record['avgPassengers'] ?? record['avg_passengers'], totalPassengers)

      return {
        hour,
        passengersIn,
        passengersOut,
        totalPassengers,
        avgPassengers,
      }
    })
    timeDistributionData.value = mapped
  } catch (error) {
    console.error('获取时间分布数据失败:', error)
    timeDistributionData.value = []
  }
}

// 获取数据
const fetchData = async () => {
  if (loading.value) return
  loading.value = true
  await resolveAnchorDate()
  ensureDefaultDateRange()
  normalizeDateRange()
  if (!validateDateRange()) {
    loading.value = false
    return
  }
  
  try {
    const dateRange = getOptionalDateRange()
    const startDate = dateRange.startDate as string
    const endDate = dateRange.endDate as string
    const [assessmentResult] = await Promise.allSettled([
      apiService.getStationAssessment({
        rangeType: 'custom',
        startDate,
        endDate,
      })
    ])

    if (isUnmounted.value) return

    // 1. 处理站点评估数据
    if (assessmentResult.status === 'fulfilled') {
      stationMetrics.value = assessmentResult.value
    } else {
      console.error('API获取站点评估数据失败', assessmentResult.reason)
      stationMetrics.value = []
    }
    await Promise.all([fetchTimeDistribution(), fetchBusyRanking(), fetchStationRoleAnalysis()])
    
  } catch (error) {
    console.error('获取站点评估数据严重错误:', error)
  } finally {
    if (!isUnmounted.value) {
      loading.value = false
    }
  }
}

watch(selectedTimeDistributionStationId, () => {
  fetchTimeDistribution()
})

// --- 计算属性：图表数据 ---

// 1. 繁忙度排名 (BarChart)
const rankingChartData = computed(() => {
  if (busyRanking.value && busyRanking.value.length > 0) {
    return busyRanking.value.slice(0, 10).map(row => ({
      name: row.stationName,
      value: row.busyIndex,
    }))
  }

  if (!stationMetrics.value) return []
  return stationMetrics.value.slice(0, 10).map(s => ({
    name: s.name,
    value: s.totalFlow,
  }))
})

type TimeDistributionViewModel = {
  data: TimeDistribution[]
  stationId: number | null
  peakHours: string[]
  peakRatio: number
}

const timeDistributionViewModel = computed<TimeDistributionViewModel>(() => {
  const data = timeDistributionData.value ?? []
  const nonZero = data.filter(item => item.totalPassengers > 0)
  const effective = nonZero.length > 0 ? nonZero : []

  if (effective.length === 0) {
    return { data: [], stationId: selectedTimeDistributionStationId.value, peakHours: [], peakRatio: 0 }
  }

  const total = effective.reduce((sum, item) => sum + item.totalPassengers, 0)
  const avg = total / effective.length

  const sorted = [...effective].sort((a, b) => b.totalPassengers - a.totalPassengers)
  const topHours = sorted
    .filter(item => item.totalPassengers > avg * 1.2)
    .slice(0, 5)
    .map(item => item.hour)
    .sort((a, b) => a - b)

  const merged: Array<{ start: number; end: number }> = []
  for (const hour of topHours) {
    const last = merged.length === 0 ? null : merged[merged.length - 1]
    if (!last) {
      merged.push({ start: hour, end: hour + 1 })
      continue
    }
    if (hour === last.end) {
      last.end = hour + 1
      continue
    }
    merged.push({ start: hour, end: hour + 1 })
  }

  const peakHours = merged.map(r => `${r.start}:00 - ${r.end}:00`)
  const peakValue = sorted.length > 0 ? sorted[0].totalPassengers : 0
  const peakRatio = avg > 0 ? peakValue / avg : 0

  return {
    data: effective,
    stationId: selectedTimeDistributionStationId.value,
    peakHours,
    peakRatio
  }
})

const peakHours = computed(() => timeDistributionViewModel.value.peakHours)

// 3. 角色分布 (PieChart)
const roleDistributionChartData = computed(() => {
  if (roleDistribution.value.length > 0) {
    return roleDistribution.value.map(item => ({
      name: item.roleName,
      value: item.count
    }))
  }

  const counts = {
    '枢纽/中转站': 0,
    '始发站': 0,
    '终到站': 0,
    '通过站': 0
  }

  stationMetrics.value.forEach(s => {
    if (counts[s.roleName as keyof typeof counts] !== undefined) {
      counts[s.roleName as keyof typeof counts]++
    }
  })

  return Object.entries(counts).map(([name, value]) => ({ name, value }))
})

// 4. 重点站点列表
const topStationsForRoles = computed(() => {
  if (roleStations.value.length > 0) return roleStations.value
  return stationMetrics.value.slice(0, 5)
})

// 5. 服务能力评估数据
const capacityAssessmentAll = computed(() => {
  return stationMetrics.value.map(s => ({
    ...s,
    status: s.saturation > 1.2 ? 'overloaded' : (s.saturation > 0.8 ? 'warning' : 'good'),
    statusText: s.saturation > 1.2 ? '严重超载' : (s.saturation > 0.8 ? '接近饱和' : '运行良好')
  }))
})

const capacityTotalPages = computed(() => {
  const total = Math.ceil(capacityAssessmentAll.value.length / capacityPageSize.value)
  return total > 0 ? total : 1
})

watch(capacityTotalPages, (totalPages) => {
  capacityPage.value = Math.min(Math.max(capacityPage.value, 1), totalPages)
})

const capacityStartIndex = computed(() => (capacityPage.value - 1) * capacityPageSize.value)
const capacityEndIndex = computed(() => Math.min(capacityStartIndex.value + capacityPageSize.value, capacityAssessmentAll.value.length))

const capacityAssessmentPageData = computed(() => {
  return capacityAssessmentAll.value.slice(capacityStartIndex.value, capacityEndIndex.value)
})

const handleCapacityPageChange = (page: number) => {
  capacityPage.value = Math.min(Math.max(page, 1), capacityTotalPages.value)
}

const handleCapacityPageSizeChange = (e: Event) => {
  const target = e.target as HTMLSelectElement | null
  const nextSize = target ? Number(target.value) : 10
  capacityPageSize.value = Number.isFinite(nextSize) ? nextSize : 10
  capacityPage.value = 1
}

// 工具函数
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const formatPercent = (val: number) => {
  return (val * 100).toFixed(1) + '%'
}

const getSaturationColor = (saturation: number) => {
  if (saturation > 1.2) return '#ef4444'
  if (saturation > 0.8) return '#f59e0b'
  return '#10b981'
}

// 初始化
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.stations-view {
  padding: var(--spacing-6);
  max-width: 1600px;
  margin: 0 auto;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-8);
}

.header-content h1 {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.header-content p {
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
}

.header-actions {
  display: flex;
  gap: var(--spacing-4);
}

.date-filter {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.date-input {
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.date-separator {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.date-error {
  color: var(--color-error);
  font-size: var(--font-size-sm);
}

.btn-refresh {
  padding: var(--spacing-2) var(--spacing-6);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: background 0.2s;
}

.btn-refresh:hover {
  background: var(--color-primary-dark);
}

.btn-refresh:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Content Grid */
.content-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-8);
}

.assessment-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.section-header {
  border-left: 4px solid var(--color-primary);
  padding-left: var(--spacing-4);
}

.section-header h2 {
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
  font-weight: 600;
}

.section-header .subtitle {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

/* Charts Layout */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-6);
}

.card {
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
}

.card h3 {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-6);
  color: var(--color-text-primary);
  font-weight: 600;
}

.chart-container {
  height: 300px;
  position: relative;
}

.distribution-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-4);
}

.distribution-title {
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  font-weight: 600;
}

.distribution-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.distribution-select {
  padding: var(--spacing-2) var(--spacing-4);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.distribution-ratio {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.no-data {
  padding: var(--spacing-8);
  text-align: center;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.btn-small {
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-sm);
}

.ranking-table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-4);
}

.ranking-table-title h3 {
  margin-bottom: var(--spacing-1);
}

.ranking-table-subtitle {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.ranking-table-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.ranking-search {
  width: 240px;
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.ranking-search:focus {
  outline: none;
  border-color: var(--color-primary);
}

.ranking-weights {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-4);
}

.weight-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.weight-label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.weight-input {
  width: 90px;
  padding: var(--spacing-2) var(--spacing-2);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.weight-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.ranking-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-4);
  margin-top: var(--spacing-4);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.pagination-btn {
  padding: var(--spacing-2) var(--spacing-4);
  border: 1px solid var(--color-border);
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  color: var(--color-text-primary);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-page {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.page-size-select {
  padding: var(--spacing-2) var(--spacing-3);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-md);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

/* Peak Info */
.peak-info {
  margin-top: var(--spacing-4);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.peak-info .label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.peak-info .tag {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-xs);
  font-weight: 500;
}

/* Tables */
.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: var(--spacing-3) var(--spacing-4);
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

th {
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  font-weight: 500;
  font-size: var(--font-size-sm);
}

td {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

/* Role Tags */
.role-tag {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.role-tag.hub { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.role-tag.origin { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.role-tag.destination { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
.role-tag.through { background: rgba(107, 114, 128, 0.1); color: #6b7280; }

/* Status Tags */
.status-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.status-tag.overloaded { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
.status-tag.warning { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
.status-tag.good { background: rgba(16, 185, 129, 0.1); color: #10b981; }

/* Progress Bar */
.progress-bar-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.progress-bar {
  height: 6px;
  border-radius: 3px;
  min-width: 60px;
}

.progress-text {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  min-width: 40px;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-20);
  color: var(--color-text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-4);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 1024px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}
</style>
