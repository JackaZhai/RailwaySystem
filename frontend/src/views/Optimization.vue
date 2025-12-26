
<template>
  <div class="optimization-view animate-fade-in">
    <section class="optimization-hero">
      <div class="hero-main">
        <div class="hero-header">
          <div>
            <span class="hero-eyebrow">运营效率优化舱</span>
            <h1 class="hero-title">线路优化工作台</h1>
            <p class="hero-subtitle">
              以客流与运力的动态匹配为核心，快速定位瓶颈区间、枢纽压力与调度弹性，输出可落地的优化策略。
            </p>
          </div>
          <div class="hero-status">
            <div class="status-item">
              <span class="status-label">最新更新</span>
              <span class="status-value">{{ overview.updatedAt }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">效率评分</span>
              <span class="status-value">{{ overview.snapshot.efficiencyScore }}</span>
            </div>
          </div>
        </div>
        <div class="hero-actions">
          <button class="btn btn-primary touch-target" :disabled="loading" @click="runPlan">
            生成优化方案
          </button>
          <button class="btn btn-outline touch-target" :disabled="loading" @click="refreshOverview">
            刷新数据
          </button>
          <button class="btn btn-outline touch-target" :disabled="!overview.lastPlan" @click="exportPlan">
            导出方案
          </button>
          <span v-if="errorMessage" class="inline-error">{{ errorMessage }}</span>
        </div>
        <div class="hero-strip">
          <div class="strip-card">
            <span class="strip-label">超载占比</span>
            <span class="strip-value">{{ overview.snapshot.overloadedRatio }}%</span>
            <span class="strip-meta">关注 {{ focusLine }}</span>
          </div>
          <div class="strip-card">
            <span class="strip-label">负载匹配</span>
            <div class="strip-progress">
              <div class="strip-bar" :style="{ width: overview.snapshot.loadMatch + '%' }"></div>
            </div>
            <span class="strip-value">{{ overview.snapshot.loadMatch }}%</span>
          </div>
          <div class="strip-card">
            <span class="strip-label">高峰吸纳</span>
            <div class="strip-progress">
              <div class="strip-bar" :style="{ width: overview.snapshot.peakAbsorb + '%' }"></div>
            </div>
            <span class="strip-value">{{ overview.snapshot.peakAbsorb }}%</span>
          </div>
          <div class="strip-card">
            <span class="strip-label">运力弹性</span>
            <div class="strip-progress">
              <div class="strip-bar" :style="{ width: overview.snapshot.capacityElastic + '%' }"></div>
            </div>
            <span class="strip-value">{{ overview.snapshot.capacityElastic }}%</span>
          </div>
        </div>
      </div>
      <div class="hero-side">
        <div class="side-card">
          <div class="side-header">
            <h3>策略场景</h3>
            <span class="badge">{{ scenarioOptions.length }}</span>
          </div>
          <div class="scenario-list">
            <button
              v-for="scenario in scenarioOptions"
              :key="scenario.id"
              class="scenario-item"
              :class="{ active: scenario.id === selectedScenario }"
              @click="selectedScenario = scenario.id"
            >
              <div>
                <div class="scenario-name">{{ scenario.name }}</div>
                <div class="scenario-meta">{{ scenario.owner }} · {{ scenario.updatedAt }}</div>
              </div>
              <span class="status-chip" :class="statusClass(scenario.status)">
                {{ statusLabel(scenario.status) }}
              </span>
            </button>
          </div>
        </div>
        <div class="side-card">
          <div class="side-header">
            <h3>最近方案</h3>
          </div>
          <div v-if="overview.lastPlan" class="plan-summary">
            <div class="plan-title">{{ overview.lastPlan.title }}</div>
            <div class="plan-meta">{{ overview.lastPlan.createdAt }}</div>
            <div class="plan-impact">{{ overview.lastPlan.expectedImpact }}</div>
            <span class="status-chip" :class="statusClass(overview.lastPlan.status)">
              {{ statusLabel(overview.lastPlan.status) }}
            </span>
          </div>
          <div v-else class="plan-empty">暂无已生成方案</div>
        </div>
      </div>
    </section>

    <section class="control-dock">
      <div class="dock-grid">
        <div class="dock-item">
          <label class="dock-label">时间范围</label>
          <select class="dock-select" v-model="filters.timeRange.type">
            <option value="today">今日</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
            <option value="custom">自定义</option>
          </select>
        </div>
        <div class="dock-item">
          <label class="dock-label">线路范围</label>
          <select class="dock-select" v-model="filters.lineGroup">
            <option value="all">全部线路</option>
            <option value="trunk">城区主干线</option>
            <option value="branch">城郊支线</option>
            <option value="airport">机场快线</option>
          </select>
        </div>
        <div class="dock-item">
          <label class="dock-label">出行类型</label>
          <select class="dock-select" v-model="filters.dayType">
            <option value="weekday">工作日</option>
            <option value="weekend">周末</option>
            <option value="holiday">节假日</option>
          </select>
        </div>
        <div class="dock-item">
          <label class="dock-label">优化目标</label>
          <select class="dock-select" v-model="goal">
            <option>提升高峰承载能力</option>
            <option>压缩平峰运力成本</option>
            <option>提升枢纽换乘效率</option>
            <option>稳定全局负载波动</option>
          </select>
        </div>
      </div>
      <div class="constraint-row">
        <span class="dock-label">关键约束</span>
        <div class="constraint-tags">
          <span v-for="tag in constraints" :key="tag" class="tag-pill">{{ tag }}</span>
        </div>
      </div>
      <div class="dock-footer">
        <textarea
          v-model="notes"
          class="dock-notes"
          placeholder="记录补充说明、调度假设或风险提示…"
        ></textarea>
        <div class="dock-actions">
          <button class="btn btn-outline touch-target" @click="notes = ''">清空备注</button>
          <button class="btn btn-primary touch-target" :disabled="loading" @click="runPlan">
            立即测算
          </button>
        </div>
      </div>
    </section>

    <section class="dashboard-grid">
      <div class="panel card wide">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">运营脉冲</h2>
            <p class="panel-subtitle">综合评估线路负载、断面满载与波动趋势。</p>
          </div>
          <div class="panel-kpis">
            <div class="kpi-card">
              <span class="kpi-label">平均上座率</span>
              <span class="kpi-value">{{ overview.kpis.averageOccupancy }}%</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">峰值断面满载率</span>
              <span class="kpi-value">{{ overview.kpis.maxSectionLoad }}%</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">长期过载线路</span>
              <span class="kpi-value">{{ overview.kpis.overloadedCount }} 条</span>
            </div>
            <div class="kpi-card">
              <span class="kpi-label">运力闲置线路</span>
              <span class="kpi-value">{{ overview.kpis.idleCount }} 条</span>
            </div>
          </div>
        </header>
        <div class="pulse-grid">
          <div v-for="insight in overview.insights" :key="insight.title" class="insight-card">
            <div class="insight-tag">{{ insight.tag }}</div>
            <div class="insight-title">{{ insight.title }}</div>
            <div class="insight-detail">{{ insight.detail }}</div>
            <div class="insight-impact">{{ insight.impact }}</div>
          </div>
        </div>
      </div>
      <div class="panel card">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">线路负载雷达</h2>
            <p class="panel-subtitle">对比上座率与断面满载率，定位长期瓶颈区间。</p>
          </div>
        </header>
        <div class="line-list">
          <div v-for="line in overview.lines" :key="line.id" class="line-row">
            <div class="line-info">
              <div class="line-name">{{ line.name }}</div>
              <div class="line-code">{{ line.code }}</div>
            </div>
            <div class="line-bars">
              <div class="bar-row">
                <span class="bar-label">上座率</span>
                <div class="bar-track">
                  <div class="bar-fill" :class="loadClass(line.occupancy)" :style="{ width: line.occupancy + '%' }"></div>
                </div>
                <span class="bar-value">{{ line.occupancy }}%</span>
              </div>
              <div class="bar-row">
                <span class="bar-label">断面满载率</span>
                <div class="bar-track">
                  <div class="bar-fill" :class="loadClass(line.sectionLoad)" :style="{ width: Math.min(line.sectionLoad, 110) + '%' }"></div>
                </div>
                <span class="bar-value">{{ line.sectionLoad }}%</span>
              </div>
            </div>
            <div class="line-meta">
              <span class="meta-label">高峰区间</span>
              <span class="meta-value">{{ line.peakSegment }}</span>
              <span class="trend" :class="trendClass(line.trend)">
                {{ line.trend > 0 ? '+' : '' }}{{ line.trend }}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel card">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">OD区间预警</h2>
            <p class="panel-subtitle">识别断面连续过载的重点区间。</p>
          </div>
        </header>
        <div class="od-list">
          <div v-for="alert in overview.odAlerts" :key="alert.segment" class="od-item">
            <div class="od-title">{{ alert.segment }}</div>
            <div class="od-metrics">
              <span class="od-load" :class="loadClass(alert.load * 100)">{{ Math.round(alert.load * 100) }}%</span>
              <span class="od-duration">{{ alert.duration }}</span>
            </div>
            <div class="od-suggestion">{{ alert.suggestion }}</div>
          </div>
        </div>
      </div>

      <div class="panel card">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">OD流量矩阵</h2>
            <p class="panel-subtitle">按真实起讫站点统计客流，输出Top OD对。</p>
          </div>
        </header>
        <div class="od-matrix">
          <div class="od-matrix-head">
            <span>起点</span>
            <span>终点</span>
            <span>总客流</span>
            <span>覆盖天数</span>
          </div>
          <div
            v-for="pair in overview.odMatrix.pairs"
            :key="`${pair.from}-${pair.to}`"
            class="od-matrix-row"
          >
            <span class="od-matrix-station">{{ pair.from }}</span>
            <span class="od-matrix-station">{{ pair.to }}</span>
            <span class="od-matrix-value">{{ pair.total.toLocaleString() }}</span>
            <span class="od-matrix-meta">{{ pair.days }} 天</span>
          </div>
          <div v-if="!overview.odMatrix.pairs.length" class="od-matrix-empty">暂无 OD 数据</div>
        </div>
      </div>

      <div class="panel card wide">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">车次客流密度矩阵</h2>
            <p class="panel-subtitle">对比不同线路与车次的密度水平，识别运力闲置。</p>
          </div>
        </header>
        <div class="density-grid">
          <div class="density-head">线路 / 车次</div>
          <div v-for="train in densityTrains" :key="train" class="density-head">{{ train }}</div>
          <template v-for="row in overview.density.matrix" :key="row.line">
            <div class="density-line">{{ row.line }}</div>
            <div
              v-for="cell in row.trains"
              :key="cell.name"
              class="density-cell"
              :class="densityClass(cell.density)"
            >
              {{ formatPercent(cell.density) }}
            </div>
          </template>
        </div>
        <div class="density-legend">
          <span class="legend-item"><span class="legend-swatch high"></span> 高负载</span>
          <span class="legend-item"><span class="legend-swatch medium"></span> 中负载</span>
          <span class="legend-item"><span class="legend-swatch low"></span> 平衡</span>
          <span class="legend-item"><span class="legend-swatch idle"></span> 闲置</span>
        </div>
      </div>

      <div class="panel card">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">时刻表优化</h2>
            <p class="panel-subtitle">评估客流与发车时刻的匹配度，建议调整频次。</p>
          </div>
        </header>
        <div class="timetable-list">
          <div v-for="window in overview.timetable" :key="window.time" class="timetable-row">
            <div class="timetable-time">{{ window.time }}</div>
            <div class="timetable-bar">
              <div class="timetable-fill" :class="densityClass(window.load)" :style="{ width: Math.round(window.load * 100) + '%' }"></div>
            </div>
            <div class="timetable-note">{{ window.suggestion }}</div>
          </div>
        </div>
      </div>

      <div class="panel card">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">枢纽识别</h2>
            <p class="panel-subtitle">基于中心性指标识别关键枢纽站点。</p>
          </div>
        </header>
        <div class="hub-list">
          <div v-for="hub in overview.hubs" :key="hub.name" class="hub-row">
            <div class="hub-main">
              <div class="hub-name">{{ hub.name }}</div>
              <div class="hub-tag">{{ hub.role }}</div>
            </div>
            <div class="hub-metrics">
              <span>度中心性 {{ formatPercent(hub.degree) }}</span>
              <span>介数中心性 {{ formatPercent(hub.betweenness) }}</span>
              <span>接近中心性 {{ formatPercent(hub.closeness) }}</span>
            </div>
            <div class="hub-trend" :class="trendClass(hub.trend)">
              {{ hub.trend > 0 ? '+' : '' }}{{ hub.trend }}%
            </div>
          </div>
        </div>
      </div>

      <div class="panel card wide">
        <header class="panel-header">
          <div>
            <h2 class="panel-title">优化建议</h2>
            <p class="panel-subtitle">结合负载与客流变化，形成可执行的增开与调度建议。</p>
          </div>
        </header>
        <div class="recommendation-grid">
          <div v-for="card in overview.recommendations" :key="card.title" class="recommendation-card">
            <div class="recommendation-header">
              <span class="priority" :class="card.priorityClass">{{ card.priority }}</span>
              <span class="recommendation-type">{{ card.type }}</span>
            </div>
            <h3 class="recommendation-title">{{ card.title }}</h3>
            <p class="recommendation-detail">{{ card.detail }}</p>
            <div class="recommendation-footer">
              <span>{{ card.impact }}</span>
              <span class="recommendation-line">{{ card.line }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { apiService } from '@/services/api'
import type {
  OptimizationFilters,
  OptimizationOverview,
  OptimizationPlanRequest,
  OptimizationScenario
} from '@/types/optimization'

const defaultOverview: OptimizationOverview = {
  updatedAt: '2024-03-18 09:30',
  snapshot: {
    efficiencyScore: 82,
    loadMatch: 78,
    peakAbsorb: 84,
    capacityElastic: 63,
    overloadedRatio: 40,
    focusLine: '3号线'
  },
  kpis: {
    averageOccupancy: 74,
    maxSectionLoad: 102,
    overloadedCount: 2,
    idleCount: 1
  },
  lines: [
    { id: 1, name: '1号线', code: 'L1', occupancy: 82, sectionLoad: 94, trend: 6, peakSegment: '南城站 - 中山站' },
    { id: 2, name: '2号线', code: 'L2', occupancy: 68, sectionLoad: 73, trend: -3, peakSegment: '北站 - 科技园' },
    { id: 3, name: '3号线', code: 'L3', occupancy: 91, sectionLoad: 102, trend: 9, peakSegment: '大学城 - 东港' },
    { id: 4, name: '机场线', code: 'A1', occupancy: 52, sectionLoad: 57, trend: -4, peakSegment: '航站楼 - 机场南' },
    { id: 5, name: '环线', code: 'R1', occupancy: 76, sectionLoad: 88, trend: 2, peakSegment: '金融城 - 南广场' }
  ],
  odAlerts: [
    { segment: '中央站 → 西湖站', load: 1.08, duration: '连续 12 天高负载', suggestion: '建议增开 2 列临客' },
    { segment: '大学城 → 科技园', load: 0.97, duration: '连续 9 天满载', suggestion: '增加早高峰区间快车' },
    { segment: '南城 → 东港', load: 0.91, duration: '断面拥挤明显', suggestion: '建议工作日加密班次' }
  ],
  odMatrix: {
    pairs: [
      { from: '中央站', to: '西湖站', total: 182340, days: 7 },
      { from: '大学城', to: '科技园', total: 164220, days: 6 },
      { from: '南城', to: '东港', total: 139880, days: 6 },
      { from: '金融城', to: '南广场', total: 112540, days: 5 }
    ]
  },
  density: {
    trains: ['G01', 'G05', 'G12', 'D03', 'K21'],
    matrix: [
      { line: '1号线', trains: [
        { name: 'G01', density: 0.92 },
        { name: 'G05', density: 0.76 },
        { name: 'G12', density: 0.64 },
        { name: 'D03', density: 0.48 },
        { name: 'K21', density: 0.32 }
      ] },
      { line: '2号线', trains: [
        { name: 'G01', density: 0.58 },
        { name: 'G05', density: 0.66 },
        { name: 'G12', density: 0.71 },
        { name: 'D03', density: 0.43 },
        { name: 'K21', density: 0.29 }
      ] },
      { line: '3号线', trains: [
        { name: 'G01', density: 0.96 },
        { name: 'G05', density: 0.84 },
        { name: 'G12', density: 0.79 },
        { name: 'D03', density: 0.61 },
        { name: 'K21', density: 0.54 }
      ] },
      { line: '机场线', trains: [
        { name: 'G01', density: 0.41 },
        { name: 'G05', density: 0.38 },
        { name: 'G12', density: 0.45 },
        { name: 'D03', density: 0.33 },
        { name: 'K21', density: 0.21 }
      ] }
    ]
  },
  timetable: [
    { time: '06:00-08:00', load: 0.92, suggestion: '加密发车至 3-4 分钟' },
    { time: '08:00-10:00', load: 0.88, suggestion: '保持现有频次，优化站停' },
    { time: '10:00-16:00', load: 0.55, suggestion: '合并班次，节约运力' },
    { time: '16:00-19:00', load: 0.93, suggestion: '增加区间车 2 班次' },
    { time: '19:00-22:00', load: 0.62, suggestion: '恢复均衡发车' }
  ],
  hubs: [
    { name: '中央站', role: '核心枢纽', degree: 0.86, betweenness: 0.74, closeness: 0.69, trend: 4 },
    { name: '科技园站', role: '通勤换乘', degree: 0.78, betweenness: 0.61, closeness: 0.63, trend: 2 },
    { name: '南城站', role: '区域枢纽', degree: 0.72, betweenness: 0.57, closeness: 0.58, trend: -1 },
    { name: '西湖站', role: '旅游集散', degree: 0.68, betweenness: 0.49, closeness: 0.55, trend: 3 }
  ],
  recommendations: [
    {
      priority: 'P0',
      priorityClass: 'priority-high',
      type: '增开建议',
      title: '早高峰东环线增开 2 列',
      detail: '07:30-09:00 断面“中央站-东港”持续满载，建议加开短线区间车。',
      impact: '预计削峰 7%',
      line: '3号线'
    },
    {
      priority: 'P1',
      priorityClass: 'priority-medium',
      type: '时刻表优化',
      title: '平峰期延长发车间隔',
      detail: '10:00-15:30 上座率不足 60%，建议将间隔从 6 分钟调整为 8 分钟。',
      impact: '运力节约 5%',
      line: '2号线'
    },
    {
      priority: 'P2',
      priorityClass: 'priority-low',
      type: '枢纽优化',
      title: '中央站优化换乘动线',
      detail: '介数中心性长期居高，建议增加客流引导与分流标识。',
      impact: '换乘效率 +6%',
      line: '枢纽网络'
    }
  ],
  scenarios: [
    { id: 'base', name: '基线方案', status: 'ready', updatedAt: '09:10', owner: '优化中心', tags: ['默认'] },
    { id: 'peak', name: '早高峰强化', status: 'draft', updatedAt: '08:40', owner: '线路组', tags: ['早高峰', '增开'] },
    { id: 'green', name: '节能降耗', status: 'running', updatedAt: '09:05', owner: '调度组', tags: ['平峰', '降耗'] }
  ],
  insights: [
    { title: '早高峰瓶颈', detail: '中央站-东港连续三周高负载', tag: '瓶颈', impact: '预计提升 6%' },
    { title: '平峰冗余', detail: '10:00-15:00 运力利用率偏低', tag: '节能', impact: '预计节约 5%' },
    { title: '换乘拥堵', detail: '中央站换乘通道流速下降', tag: '枢纽', impact: '预计提升 3%' }
  ],
  lastPlan: {
    id: 'plan-20240318',
    title: '周内优化方案',
    status: 'ready',
    createdAt: '2024-03-18 08:50',
    expectedImpact: '削峰 7%，节约 4%'
  }
}

const filters = reactive<OptimizationFilters>({
  timeRange: { type: 'week' },
  lineGroup: 'all',
  dayType: 'weekday'
})

const loading = ref(false)
const errorMessage = ref('')
const overview = ref<OptimizationOverview>(defaultOverview)
const selectedScenario = ref<string>('base')
const goal = ref('提升高峰承载能力')
const constraints = ref<string[]>(['最小发车间隔 3 分钟', '车辆编组不变'])
const notes = ref('')

const densityTrains = computed(() => overview.value.density.trains)
const focusLine = computed(() => overview.value.snapshot.focusLine)
const scenarioOptions = computed<OptimizationScenario[]>(() => overview.value.scenarios)

const refreshOverview = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const data = await apiService.getOptimizationOverview(filters)
    overview.value = data
    if (data.scenarios?.length) {
      selectedScenario.value = data.scenarios[0].id
    }
  } catch (error) {
    errorMessage.value = '获取优化数据失败，已使用本地样例。'
    overview.value = defaultOverview
  } finally {
    loading.value = false
  }
}

const runPlan = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const payload: OptimizationPlanRequest = {
      filters,
      goal: goal.value,
      constraints: constraints.value,
      notes: notes.value || undefined
    }
    const result = await apiService.createOptimizationPlan(payload)
    overview.value = {
      ...overview.value,
      lastPlan: result.summary,
      recommendations: result.recommendations.length ? result.recommendations : overview.value.recommendations
    }
  } catch (error) {
    errorMessage.value = '方案生成失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

const exportPlan = async () => {
  if (!overview.value.lastPlan) return
  loading.value = true
  errorMessage.value = ''
  try {
    await apiService.exportOptimizationPlan(overview.value.lastPlan.id, 'excel')
  } catch (error) {
    errorMessage.value = '导出失败，请检查后端服务。'
  } finally {
    loading.value = false
  }
}

const statusLabel = (status: string) => {
  if (status === 'draft') return '草案'
  if (status === 'running') return '测算中'
  if (status === 'ready') return '可用'
  return '异常'
}

const statusClass = (status: string) => {
  if (status === 'draft') return 'status-draft'
  if (status === 'running') return 'status-running'
  if (status === 'ready') return 'status-ready'
  return 'status-failed'
}

const loadClass = (value: number) => {
  if (value >= 90) return 'load-high'
  if (value >= 70) return 'load-medium'
  return 'load-low'
}

const trendClass = (value: number) => (value >= 0 ? 'trend-positive' : 'trend-negative')

const densityClass = (value: number) => {
  if (value >= 0.85) return 'density-high'
  if (value >= 0.65) return 'density-medium'
  if (value >= 0.45) return 'density-low'
  return 'density-idle'
}

const formatPercent = (value: number) => `${Math.round(value * 100)}%`

onMounted(() => {
  refreshOverview()
})
</script>
<style scoped>
.optimization-view {
  padding: var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
  position: relative;
  isolation: isolate;
}

.optimization-view::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(46, 139, 87, 0.08), transparent 55%),
    radial-gradient(circle at 15% 20%, rgba(70, 130, 180, 0.12), transparent 45%),
    radial-gradient(circle at 85% 10%, rgba(210, 105, 30, 0.1), transparent 40%),
    linear-gradient(transparent 0, transparent 96%, rgba(46, 139, 87, 0.06) 96%, rgba(46, 139, 87, 0.06) 100%),
    linear-gradient(90deg, transparent 0, transparent 96%, rgba(46, 139, 87, 0.06) 96%, rgba(46, 139, 87, 0.06) 100%);
  background-size: auto, auto, auto, 48px 48px, 48px 48px;
  z-index: -1;
}

.optimization-hero {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-5);
}

.hero-main {
  background: linear-gradient(135deg, rgba(46, 139, 87, 0.08), rgba(70, 130, 180, 0.15));
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-2xl);
  padding: var(--spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  box-shadow: var(--shadow-lg);
}

.hero-header {
  display: flex;
  justify-content: space-between;
  gap: var(--spacing-4);
}

.hero-eyebrow {
  font-size: var(--font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--color-text-tertiary);
}

.hero-title {
  margin: var(--spacing-1) 0 0;
  font-size: var(--font-size-3xl);
  color: var(--color-text-primary);
}

.hero-subtitle {
  margin: var(--spacing-2) 0 0;
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.hero-status {
  display: grid;
  gap: var(--spacing-2);
  align-content: start;
  min-width: 160px;
}

.status-item {
  background: rgba(255, 255, 255, 0.75);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-2) var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.status-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.status-value {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
  align-items: center;
}

.inline-error {
  font-size: var(--font-size-xs);
  color: var(--color-error);
}

.hero-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-3);
}

.strip-card {
  background: rgba(255, 255, 255, 0.8);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.strip-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.strip-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.strip-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.strip-progress {
  height: 6px;
  background: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.strip-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-secondary), var(--color-primary));
}

.hero-side {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.side-card {
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border-light);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.side-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.badge {
  background: rgba(70, 130, 180, 0.15);
  color: var(--color-secondary-dark);
  padding: 2px 8px;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.scenario-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.scenario-item {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-2) var(--spacing-3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-2);
  border: 1px solid transparent;
  cursor: pointer;
}

.scenario-item.active {
  border-color: rgba(46, 139, 87, 0.5);
  box-shadow: var(--shadow-sm);
  background: rgba(46, 139, 87, 0.08);
}

.scenario-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.scenario-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.status-chip {
  padding: 2px 8px;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.status-ready {
  background: rgba(46, 139, 87, 0.15);
  color: var(--color-success);
}

.status-draft {
  background: rgba(112, 128, 144, 0.2);
  color: var(--color-neutral);
}

.status-running {
  background: rgba(70, 130, 180, 0.2);
  color: var(--color-secondary-dark);
}

.status-failed {
  background: rgba(220, 20, 60, 0.15);
  color: var(--color-error);
}

.plan-summary {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.plan-title {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.plan-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.plan-impact {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.plan-empty {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.control-dock {
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-xl);
  border: 1px solid var(--color-border-light);
  padding: var(--spacing-5);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.dock-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(160px, 1fr));
  gap: var(--spacing-3);
}

.dock-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.dock-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.dock-select {
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--border-radius-base);
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.constraint-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.constraint-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.tag-pill {
  padding: 4px 10px;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-xs);
  background: rgba(70, 130, 180, 0.12);
  color: var(--color-secondary-dark);
}

.dock-footer {
  display: flex;
  gap: var(--spacing-3);
  align-items: flex-start;
}

.dock-notes {
  flex: 1;
  min-height: 90px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border);
  padding: var(--spacing-3);
  resize: vertical;
  font-family: var(--font-family-base);
  background: var(--color-bg-secondary);
}

.dock-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--spacing-4);
}

.panel {
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--color-border-light);
  padding: var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.panel.wide {
  grid-column: span 2;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-3);
}

.panel-title {
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
}

.panel-subtitle {
  margin: var(--spacing-1) 0 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.panel-kpis {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: var(--spacing-2);
}

.kpi-card {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-2) var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.kpi-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.kpi-value {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.pulse-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--spacing-3);
}

.insight-card {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.insight-tag {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.insight-title {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.insight-detail {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.insight-impact {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}
.line-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.line-row {
  display: grid;
  grid-template-columns: 140px 1fr 200px;
  gap: var(--spacing-4);
  padding: var(--spacing-3);
  border-radius: var(--border-radius-lg);
  background: var(--color-bg-secondary);
}

.line-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.line-code {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.line-bars {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.bar-row {
  display: grid;
  grid-template-columns: 80px 1fr 50px;
  gap: var(--spacing-2);
  align-items: center;
  font-size: var(--font-size-xs);
}

.bar-track {
  height: 10px;
  background: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: inherit;
}

.bar-fill.load-high {
  background: linear-gradient(90deg, #d0475c, #ff8b7b);
}

.bar-fill.load-medium {
  background: linear-gradient(90deg, #f5a623, #ffd166);
}

.bar-fill.load-low {
  background: linear-gradient(90deg, #2e8b57, #6fd3a3);
}

.bar-value {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.line-meta {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
}

.meta-label {
  color: var(--color-text-tertiary);
}

.meta-value {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.trend {
  padding: 2px 8px;
  border-radius: var(--border-radius-full);
  font-weight: var(--font-weight-semibold);
  width: fit-content;
}

.trend-positive {
  background: rgba(46, 139, 87, 0.12);
  color: var(--color-success);
}

.trend-negative {
  background: rgba(220, 20, 60, 0.12);
  color: var(--color-error);
}

.od-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.od-item {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.od-title {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.od-metrics {
  display: flex;
  gap: var(--spacing-3);
  align-items: center;
  font-size: var(--font-size-xs);
}

.od-load {
  padding: 2px 8px;
  border-radius: var(--border-radius-full);
  font-weight: var(--font-weight-semibold);
}

.od-duration {
  color: var(--color-text-tertiary);
}

.od-suggestion {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.od-matrix {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.od-matrix-head,
.od-matrix-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--spacing-2);
  align-items: center;
}

.od-matrix-head {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  padding: var(--spacing-2) var(--spacing-3);
}

.od-matrix-row {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-2) var(--spacing-3);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.od-matrix-station {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.od-matrix-value {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.od-matrix-meta {
  color: var(--color-text-tertiary);
}

.od-matrix-empty {
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  padding: var(--spacing-3);
}

.density-grid {
  display: grid;
  grid-template-columns: 120px repeat(5, 1fr);
  gap: var(--spacing-2);
  align-items: center;
}

.density-head {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  padding: var(--spacing-2);
}

.density-line {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  padding: var(--spacing-2);
}

.density-cell {
  text-align: center;
  padding: var(--spacing-2);
  border-radius: var(--border-radius-base);
  font-size: var(--font-size-xs);
  color: #1b1b1b;
}

.density-high {
  background: rgba(208, 71, 92, 0.25);
}

.density-medium {
  background: rgba(245, 166, 35, 0.25);
}

.density-low {
  background: rgba(46, 139, 87, 0.2);
}

.density-idle {
  background: rgba(112, 128, 144, 0.2);
}

.density-legend {
  display: flex;
  gap: var(--spacing-3);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
}

.legend-swatch {
  width: 12px;
  height: 12px;
  border-radius: var(--border-radius-sm);
  display: inline-block;
}

.legend-swatch.high {
  background: rgba(208, 71, 92, 0.45);
}

.legend-swatch.medium {
  background: rgba(245, 166, 35, 0.45);
}

.legend-swatch.low {
  background: rgba(46, 139, 87, 0.35);
}

.legend-swatch.idle {
  background: rgba(112, 128, 144, 0.35);
}

.timetable-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.timetable-row {
  display: grid;
  grid-template-columns: 110px 1fr 160px;
  gap: var(--spacing-3);
  align-items: center;
  font-size: var(--font-size-xs);
}

.timetable-bar {
  height: 10px;
  background: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.timetable-fill {
  height: 100%;
}

.timetable-note {
  color: var(--color-text-secondary);
}

.hub-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.hub-row {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-3);
  display: grid;
  grid-template-columns: 140px 1fr auto;
  gap: var(--spacing-3);
  align-items: center;
}

.hub-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.hub-tag {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.hub-metrics {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.hub-trend {
  padding: 4px 8px;
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-4);
}

.recommendation-card {
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  height: 100%;
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-xs);
}

.priority {
  padding: 2px 8px;
  border-radius: var(--border-radius-full);
  font-weight: var(--font-weight-semibold);
}

.priority-high {
  background: rgba(220, 20, 60, 0.15);
  color: var(--color-error);
}

.priority-medium {
  background: rgba(245, 166, 35, 0.2);
  color: var(--color-warning);
}

.priority-low {
  background: rgba(70, 130, 180, 0.18);
  color: var(--color-secondary-dark);
}

.recommendation-type {
  color: var(--color-text-tertiary);
}

.recommendation-title {
  margin: 0;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
}

.recommendation-detail {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.recommendation-footer {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.recommendation-line {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.load-high {
  background: rgba(220, 20, 60, 0.15);
  color: var(--color-error);
}

.load-medium {
  background: rgba(245, 166, 35, 0.18);
  color: var(--color-warning);
}

.load-low {
  background: rgba(46, 139, 87, 0.18);
  color: var(--color-success);
}
@media (max-width: 1200px) {
  .optimization-hero {
    grid-template-columns: 1fr;
  }

  .hero-strip {
    grid-template-columns: repeat(2, 1fr);
  }

  .dock-grid {
    grid-template-columns: repeat(2, minmax(160px, 1fr));
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .panel.wide {
    grid-column: auto;
  }

  .recommendation-grid {
    grid-template-columns: 1fr;
  }

  .pulse-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .hero-header {
    flex-direction: column;
  }

  .hero-strip {
    grid-template-columns: 1fr;
  }

  .dock-grid {
    grid-template-columns: 1fr;
  }

  .dock-footer {
    flex-direction: column;
  }

  .line-row {
    grid-template-columns: 1fr;
  }

  .line-meta {
    flex-direction: row;
    flex-wrap: wrap;
    gap: var(--spacing-2);
  }

  .density-grid {
    grid-template-columns: 1fr;
  }

  .timetable-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-2);
  }

  .hub-row {
    grid-template-columns: 1fr;
  }
}
</style>
