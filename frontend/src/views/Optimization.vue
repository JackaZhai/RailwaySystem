<template>
  <div class="optimization animate-fade-in">
    <LoadingSpinner v-if="isLoading" size="large" variant="primary" text="线路优化数据加载中..." fullscreen />

    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">线路优化</h1>
        <p class="page-description">线路负载分析、断面诊断与优化建议。</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" :disabled="isLoading" @click="refreshAll">
          刷新数据
        </button>
      </div>
    </div>

    <div class="filters-card">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">日期范围</label>
          <div class="range-inputs">
            <input v-model="filters.timeRange[0]" type="date" class="input" />
            <span class="range-separator">至</span>
            <input v-model="filters.timeRange[1]" type="date" class="input" />
          </div>
        </div>
        <div class="filter-group">
          <label class="filter-label">日期类型</label>
          <select v-model="filters.dayType" class="input">
            <option value="workday">工作日</option>
            <option value="weekend">周末</option>
            <option value="all">全部</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">方向</label>
          <select v-model="filters.direction" class="input">
            <option value="up">上行</option>
            <option value="down">下行</option>
            <option value="all">全部</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">粒度</label>
          <select v-model="filters.granularity" class="input">
            <option value="15min">15 分钟</option>
            <option value="hour">小时</option>
            <option value="day">天</option>
          </select>
        </div>
      </div>
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">线路</label>
          <div class="chip-group">
            <button
              v-for="line in lines"
              :key="line.id"
              class="chip"
              :class="{ active: filters.lineIds.includes(line.id) }"
              @click="toggleLine(line.id)"
            >
              {{ line.name }}
            </button>
          </div>
        </div>
        <div class="filter-group threshold-group">
          <label class="filter-label">阈值</label>
          <div class="threshold-inputs">
            <div class="threshold-item">
              <span class="threshold-label">过载</span>
              <input v-model.number="filters.threshold.overload" class="input small" type="number" step="0.05" />
            </div>
            <div class="threshold-item">
              <span class="threshold-label">闲置</span>
              <input v-model.number="filters.threshold.idle" class="input small" type="number" step="0.05" />
            </div>
          </div>
        </div>
        <div class="filter-group">
          <label class="filter-label">&nbsp;</label>
          <button class="btn btn-primary" :disabled="isLoading" @click="refreshAll">
            应用筛选
          </button>
        </div>
      </div>
    </div>
    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-title">过载线路</div>
        <div class="kpi-value">{{ kpi?.overloadLineCount ?? 0 }}</div>
        <div class="kpi-footnote">p95 负载 &gt; {{ filters.threshold.overload.toFixed(2) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">闲置线路</div>
        <div class="kpi-value">{{ kpi?.idleLineCount ?? 0 }}</div>
        <div class="kpi-footnote">平均负载 &lt; {{ filters.threshold.idle.toFixed(2) }}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">最拥挤区间</div>
        <div class="kpi-value">
          <span v-if="kpi?.topSection">{{ kpi.topSection.fromStationId }} → {{ kpi.topSection.toStationId }}</span>
          <span v-else>-</span>
        </div>
        <div class="kpi-footnote">
          p95 {{ kpi?.topSection ? kpi.topSection.p95FullRate.toFixed(2) : '无' }}
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">高峰时段</div>
        <div class="kpi-value">
          <span v-if="kpi?.peakHours?.length">{{ kpi.peakHours[0].hour.toString().padStart(2, '0') }}:00</span>
          <span v-else>-</span>
        </div>
        <div class="kpi-footnote">
          {{ kpi?.peakHours?.[0] ? kpi.peakHours[0].value.toFixed(2) : '无' }}
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">优化建议</div>
        <div class="kpi-value">{{ suggestionList?.total ?? 0 }}</div>
        <div class="kpi-footnote">
          加开 {{ kpi?.suggestionCount?.addTrips ?? 0 }} · 时刻表 {{ kpi?.suggestionCount?.timetable ?? 0 }} · 枢纽 {{ kpi?.suggestionCount?.hub ?? 0 }}
        </div>
      </div>
    </div>

    <div class="tab-bar">
      <button class="tab-btn" :class="{ active: activeTab === 'line' }" @click="activeTab = 'line'">线路负载</button>
      <button class="tab-btn" :class="{ active: activeTab === 'section' }" @click="activeTab = 'section'">断面分析</button>
      <button class="tab-btn" :class="{ active: activeTab === 'trip' }" @click="activeTab = 'trip'">车次分析</button>
      <button class="tab-btn" :class="{ active: activeTab === 'hub' }" @click="activeTab = 'hub'">枢纽识别</button>
    </div>

    <div v-if="activeTab === 'line'" class="tab-panel">
      <div class="panel-grid">
        <div class="panel-card">
          <div class="panel-header">
            <h3>线路负载热力</h3>
            <span class="panel-subtitle">按小时的平均与 p95 负载</span>
          </div>
          <div class="heatmap">
            <div class="heatmap-header">
              <div class="heatmap-spacer"></div>
              <div v-for="label in lineHeatmap?.xAxis || []" :key="label" class="heatmap-label">{{ label }}</div>
            </div>
            <div
              v-for="(row, rowIndex) in heatmapGrid"
              :key="rowIndex"
              class="heatmap-row"
            >
              <div class="heatmap-label y-label">{{ row.label }}</div>
              <button
                v-for="(cell, cellIndex) in row.cells"
                :key="cellIndex"
                class="heatmap-cell"
                :style="{ background: cell.color }"
                @click="selectHeatCell(row.label, cell)"
              >
                <span>{{ cell.value.toFixed(2) }}</span>
              </button>
            </div>
          </div>
        </div>
        <div class="panel-card side-panel">
          <div class="panel-header">
            <h3>选中详情</h3>
            <span class="panel-subtitle">点击热力格查看负载</span>
          </div>
          <div class="selection-card" v-if="selectedHeatCell">
            <div class="selection-title">{{ selectedHeatCell.line }}</div>
            <div class="selection-row">
              <span>时间</span>
              <strong>{{ selectedHeatCell.time }}</strong>
            </div>
            <div class="selection-row">
              <span>平均负载</span>
              <strong>{{ selectedHeatCell.avgLoad.toFixed(2) }}</strong>
            </div>
            <div class="selection-row">
              <span>p95 负载</span>
              <strong>{{ selectedHeatCell.p95Load.toFixed(2) }}</strong>
            </div>
            <div class="selection-row">
              <span>超载分钟</span>
              <strong>{{ selectedHeatCell.overMinutes }}</strong>
            </div>
          </div>
          <div v-else class="empty-state">请选择热力格查看详情。</div>
        </div>
      </div>
      <div class="panel-card trend-card">
        <LineChart
          v-if="lineTrendSeries.length > 0"
          chart-id="line-load-trend"
          :title="'线路负载趋势'"
          :x-axis-data="lineTrendXAxis"
          :series="lineTrendSeries"
          y-axis-name="负载"
          :legend="true"
          :toolbox="false"
          :area-style="true"
        />
        <div v-else class="empty-state">暂无趋势数据。</div>
      </div>
    </div>

    <div v-if="activeTab === 'section'" class="tab-panel">
      <div class="panel-card">
        <div class="panel-header">
          <h3>断面负载走廊</h3>
          <span class="panel-subtitle">拥挤区间排名</span>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>区间</th>
              <th>平均负载</th>
              <th>p95 负载</th>
              <th>高峰时段</th>
              <th>客流</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="segment in sectionSegments" :key="segment.fromStationId + '-' + segment.toStationId">
              <td>{{ segment.fromStationId }} → {{ segment.toStationId }}</td>
              <td>{{ segment.avgFullRate.toFixed(2) }}</td>
              <td>{{ segment.p95FullRate.toFixed(2) }}</td>
              <td>{{ segment.peakHour.toString().padStart(2, '0') }}:00</td>
              <td>{{ segment.flow.toFixed(0) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="activeTab === 'trip'" class="tab-panel">
      <div class="panel-grid">
        <div class="panel-card">
          <div class="panel-header">
          <h3>车次负载概览</h3>
          <span class="panel-subtitle">负载最高车次</span>
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>车次</th>
                <th>发车时间</th>
                <th>最大负载</th>
                <th>平均客流</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="trip in topTrips" :key="trip.tripId">
                <td>{{ trip.tripId }}</td>
                <td>{{ trip.departTime }}</td>
                <td>{{ trip.maxLoad.toFixed(2) }}</td>
                <td>{{ trip.avgFlow.toFixed(0) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="panel-card">
          <div class="panel-header">
          <h3>发车需求分布</h3>
          <span class="panel-subtitle">发车时间与负载</span>
          </div>
          <table class="data-table">
            <thead>
              <tr>
                <th>发车时间</th>
                <th>平均负载</th>
                <th>p95 负载</th>
                <th>样本数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="point in timetablePoints" :key="point.departTime">
                <td>{{ point.departTime }}</td>
                <td>{{ point.avgLoad.toFixed(2) }}</td>
                <td>{{ point.p95Load.toFixed(2) }}</td>
                <td>{{ point.sampleTrips }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'hub'" class="tab-panel">
      <div class="panel-card">
        <div class="panel-header">
          <h3>枢纽指标</h3>
          <span class="panel-subtitle">站点连接度排名</span>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>站点</th>
              <th>度数</th>
              <th>介数</th>
              <th>接近度</th>
              <th>进出流量</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="node in hubNodes" :key="node.stationId">
              <td>{{ node.name }}</td>
              <td>{{ node.degree }}</td>
              <td>{{ node.betweenness.toFixed(2) }}</td>
              <td>{{ node.closeness.toFixed(2) }}</td>
              <td>{{ node.inOutFlow.toFixed(0) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="panel-card suggestion-card">
      <div class="panel-header">
        <h3>优化建议</h3>
        <span class="panel-subtitle">优先级建议清单</span>
      </div>
      <div class="suggestion-list">
        <div v-for="item in suggestionItems" :key="item.id" class="suggestion-item">
          <div class="suggestion-main">
            <div class="suggestion-title">{{ item.title }}</div>
            <div class="suggestion-meta">{{ item.reason }}</div>
          </div>
          <div class="suggestion-stats">
            <span class="pill">{{ suggestionTypeLabel(item.type) }}</span>
            <span class="pill">p95 {{ item.impact.p95Before.toFixed(2) }} → {{ item.impact.p95After.toFixed(2) }}</span>
          </div>
        </div>
        <div v-if="suggestionItems.length === 0" class="empty-state">当前筛选无建议。</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { dataService } from '@/services/api'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import LineChart from '@/components/charts/LineChart.vue'
import type {
  RouteLine,
  RouteOptFilters,
  RouteKpi,
  LineLoadHeatmap,
  LineLoadTrend,
  SectionCorridor,
  TripHeatmap,
  TimetableScatter,
  SuggestionList,
  HubMetrics
} from '@/types/optimization'

const isLoading = ref(false)
const errorMessage = ref('')
const activeTab = ref<'line' | 'section' | 'trip' | 'hub'>('line')

const filters = reactive<RouteOptFilters>({
  timeRange: ['2015-01-01', '2015-01-07'],
  dayType: 'workday',
  granularity: 'hour',
  lineIds: [],
  direction: 'up',
  threshold: {
    overload: 1.0,
    idle: 0.35
  }
})

const lines = ref<RouteLine[]>([])
const kpi = ref<RouteKpi | null>(null)
const lineHeatmap = ref<LineLoadHeatmap | null>(null)
const lineTrend = ref<LineLoadTrend | null>(null)
const sectionCorridor = ref<SectionCorridor | null>(null)
const tripHeatmap = ref<TripHeatmap | null>(null)
const timetableScatter = ref<TimetableScatter | null>(null)
const suggestionList = ref<SuggestionList | null>(null)
const hubMetrics = ref<HubMetrics | null>(null)

const selectedHeatCell = ref<{
  line: string
  time: string
  avgLoad: number
  p95Load: number
  overMinutes: number
} | null>(null)

const activeLineId = computed(() => filters.lineIds[0] || lines.value[0]?.id || '')

const heatmapGrid = computed(() => {
  if (!lineHeatmap.value) {
    return []
  }
  const xAxis = lineHeatmap.value.xAxis
  const points = lineHeatmap.value.points
  const pointMap = new Map<string, typeof points[number]>()
  points.forEach((point) => {
    pointMap.set(`${point.y}-${point.x}`, point)
  })

  return lineHeatmap.value.yAxis.map((line, rowIndex) => {
    const cells = xAxis.map((_label, colIndex) => {
      const point = pointMap.get(`${rowIndex}-${colIndex}`)
      const value = point ? point.p95Load : 0
      const color = heatColor(value)
      return {
        time: xAxis[colIndex],
        avgLoad: point?.avgLoad || 0,
        p95Load: point?.p95Load || 0,
        overMinutes: point?.overMinutes || 0,
        value,
        color
      }
    })
    return {
      label: line.name,
      cells
    }
  })
})

const lineTrendXAxis = computed(() => {
  const series = lineTrend.value?.series.find((item) => item.lineId === activeLineId.value)
  return series ? series.points.map((point) => point.t) : []
})

const lineTrendSeries = computed(() => {
  const series = lineTrend.value?.series.find((item) => item.lineId === activeLineId.value)
  if (!series) {
    return []
  }
  return [
    {
      name: '平均负载',
      data: series.points.map((point) => point.avgLoad)
    },
    {
      name: 'p95 负载',
      data: series.points.map((point) => point.p95Load)
    }
  ]
})

const sectionSegments = computed(() => {
  return (sectionCorridor.value?.segments || []).slice(0, 12)
})

const timetablePoints = computed(() => {
  return (timetableScatter.value?.points || []).slice(0, 12)
})

const topTrips = computed(() => {
  if (!tripHeatmap.value) {
    return []
  }
  const tripStats = new Map<string, { tripId: string; departTime: string; maxLoad: number; avgFlow: number; count: number }>()
  tripHeatmap.value.cells.forEach((cell) => {
    const trip = tripHeatmap.value?.trips.find((item) => item.tripId === cell.tripId)
    if (!trip) {
      return
    }
    if (!tripStats.has(cell.tripId)) {
      tripStats.set(cell.tripId, {
        tripId: cell.tripId,
        departTime: trip.departTime,
        maxLoad: cell.load,
        avgFlow: cell.flow,
        count: 1
      })
    } else {
      const stat = tripStats.get(cell.tripId)!
      stat.maxLoad = Math.max(stat.maxLoad, cell.load)
      stat.avgFlow += cell.flow
      stat.count += 1
    }
  })
  return Array.from(tripStats.values())
    .map((stat) => ({ ...stat, avgFlow: stat.count ? stat.avgFlow / stat.count : 0 }))
    .sort((a, b) => b.maxLoad - a.maxLoad)
    .slice(0, 10)
})

const hubNodes = computed(() => {
  return (hubMetrics.value?.nodes || []).slice(0, 12)
})

const suggestionItems = computed(() => {
  return suggestionList.value?.items || []
})

const suggestionTypeLabel = (type: string) => {
  if (type === 'addTrips') return '加开'
  if (type === 'timetable') return '时刻表'
  if (type === 'hub') return '枢纽'
  return type
}

const toggleLine = (lineId: string) => {
  if (filters.lineIds.includes(lineId)) {
    filters.lineIds = filters.lineIds.filter((id) => id !== lineId)
  } else {
    filters.lineIds = [lineId]
  }
}

const selectHeatCell = (lineLabel: string, cell: { time: string; avgLoad: number; p95Load: number; overMinutes: number }) => {
  selectedHeatCell.value = {
    line: lineLabel,
    time: cell.time,
    avgLoad: cell.avgLoad,
    p95Load: cell.p95Load,
    overMinutes: cell.overMinutes
  }
}

const heatColor = (value: number) => {
  const clamped = Math.min(Math.max(value, 0), 1.6)
  const intensity = clamped / 1.6
  const r = Math.round(255 * intensity)
  const g = Math.round(80 + 120 * (1 - intensity))
  const b = Math.round(120 * (1 - intensity))
  return `rgb(${r}, ${g}, ${b})`
}

const refreshAll = async () => {
  if (!filters.timeRange[0] || !filters.timeRange[1]) {
    return
  }
  isLoading.value = true
  try {
    const filterPayload = { ...filters }
    const lineIdPayload = activeLineId.value ? { ...filters, lineId: activeLineId.value } : filterPayload

    errorMessage.value = ''
    const [
      kpiRes,
      heatRes,
      trendRes,
      sectionRes,
      tripRes,
      timetableRes,
      suggestionRes,
      hubRes
    ] = await Promise.all([
      dataService.getRouteOptKpi(filterPayload),
      dataService.getLineLoadHeatmap(filterPayload),
      dataService.getLineLoadTrend(filterPayload),
      dataService.getSectionCorridor(lineIdPayload),
      dataService.getTripHeatmap(lineIdPayload),
      dataService.getTimetableScatter(lineIdPayload),
      dataService.getSuggestionList({ filters: filterPayload, sortBy: 'impact', page: 1, pageSize: 20 }),
      dataService.getHubMetrics(filterPayload)
    ])

    kpi.value = kpiRes
    lineHeatmap.value = heatRes
    lineTrend.value = trendRes
    sectionCorridor.value = sectionRes
    tripHeatmap.value = tripRes
    timetableScatter.value = timetableRes
    suggestionList.value = suggestionRes
    hubMetrics.value = hubRes
  } catch (error) {
    console.error('线路优化数据加载失败:', error)
    errorMessage.value = '数据加载失败，请稍后重试或检查后端服务。'
  } finally {
    isLoading.value = false
  }
}

const loadLines = async () => {
  const result = await dataService.getRouteLines()
  lines.value = result
  if (lines.value.length > 0 && filters.lineIds.length === 0) {
    filters.lineIds = [lines.value[0].id]
  }
}

onMounted(async () => {
  await loadLines()
  await refreshAll()
})
</script>

<style scoped>
.optimization {
  padding: var(--spacing-4);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

.page-title {
  margin: 0;
  font-size: var(--font-size-2xl);
}

.page-description {
  margin: var(--spacing-2) 0 0;
  color: var(--color-text-secondary);
}

.filters-card {
  background: var(--color-bg-card);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-5);
  box-shadow: var(--shadow-md);
  margin-bottom: var(--spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.error-banner {
  background: rgba(220, 20, 60, 0.1);
  color: var(--color-error);
  border: 1px solid rgba(220, 20, 60, 0.2);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-3);
  margin-bottom: var(--spacing-6);
  font-size: var(--font-size-sm);
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacing-4);
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.filter-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.input {
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.input.small {
  max-width: 120px;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.range-separator {
  color: var(--color-text-tertiary);
}

.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.chip {
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--border-radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
}

.chip.active {
  background: var(--color-secondary);
  color: var(--color-text-inverse);
  border-color: var(--color-secondary);
}

.threshold-group {
  grid-column: span 2;
}

.threshold-inputs {
  display: flex;
  gap: var(--spacing-3);
}

.threshold-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.threshold-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.btn {
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-primary {
  background: var(--color-secondary);
  color: var(--color-text-inverse);
  border-color: var(--color-secondary);
}

.btn-outline {
  background: transparent;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

.kpi-card {
  background: var(--color-bg-card);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-sm);
}

.kpi-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.kpi-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  margin-top: var(--spacing-2);
}

.kpi-footnote {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-1);
}

.tab-bar {
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-4);
  flex-wrap: wrap;
}

.tab-btn {
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  cursor: pointer;
}

.tab-btn.active {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.tab-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

.panel-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr);
  gap: var(--spacing-4);
}

.panel-card {
  background: var(--color-bg-card);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
}

.panel-header h3 {
  margin: 0;
  font-size: var(--font-size-lg);
}

.panel-subtitle {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

.heatmap {
  margin-top: var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.heatmap-header,
.heatmap-row {
  display: grid;
  grid-template-columns: 140px repeat(auto-fit, minmax(60px, 1fr));
  gap: var(--spacing-2);
  align-items: center;
}

.heatmap-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: center;
}

.heatmap-label.y-label {
  text-align: left;
}

.heatmap-cell {
  height: 40px;
  border-radius: var(--border-radius-sm);
  border: none;
  color: #fff;
  font-size: var(--font-size-xs);
}

.heatmap-spacer {
  height: 1px;
}

.side-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.selection-card {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-3);
}

.selection-title {
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-2);
}

.selection-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-1);
}

.trend-card {
  min-height: 320px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: var(--spacing-3);
  font-size: var(--font-size-sm);
}

.data-table th,
.data-table td {
  text-align: left;
  padding: var(--spacing-2);
  border-bottom: 1px solid var(--color-border-light);
}

.data-table th {
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.suggestion-card {
  margin-bottom: var(--spacing-6);
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  margin-top: var(--spacing-3);
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  border-radius: var(--border-radius-lg);
  background: var(--color-bg-secondary);
}

.suggestion-title {
  font-weight: var(--font-weight-semibold);
}

.suggestion-meta {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
}

.suggestion-stats {
  display: flex;
  gap: var(--spacing-2);
  flex-wrap: wrap;
}

.pill {
  padding: 2px 8px;
  border-radius: var(--border-radius-full);
  background: var(--color-bg-primary);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.empty-state {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
  padding: var(--spacing-3) 0;
}

@media (max-width: 960px) {
  .panel-grid {
    grid-template-columns: 1fr;
  }
}
</style>
