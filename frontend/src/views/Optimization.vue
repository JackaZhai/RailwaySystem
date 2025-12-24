<template>
  <div class="optimization-view animate-fade-in">
    <section class="page-hero">
      <div class="hero-text">
        <span class="eyebrow">运营效率与线路优化</span>
        <h1 class="page-title">线路优化</h1>
        <p class="page-subtitle">
          基于实际客流数据评估线路运营效率，聚焦负载、密度与枢纽影响，输出可执行的增开与调度建议。
        </p>
        <div class="hero-tags">
          <span class="tag">线路负载分析</span>
          <span class="tag">车次密度监测</span>
          <span class="tag">时刻表优化</span>
          <span class="tag">枢纽识别</span>
        </div>
      </div>
      <div class="hero-panel">
        <div class="panel-header">
          <span>运营效率快照</span>
          <span class="panel-time">更新于 09:30</span>
        </div>
        <div class="panel-body">
          <div class="pulse-grid">
            <div class="pulse-item" v-for="item in pulseIndicators" :key="item.label">
              <span class="pulse-label">{{ item.label }}</span>
              <div class="pulse-track">
                <div class="pulse-fill" :style="{ width: item.value + '%' }"></div>
              </div>
              <span class="pulse-value">{{ item.value }}%</span>
            </div>
          </div>
        </div>
        <div class="panel-footer">
          <span class="panel-note">超载占比 {{ overloadedRatio }}%，建议优先关注 {{ focusLine }}</span>
        </div>
      </div>
    </section>

    <section class="filter-bar">
      <div class="filter-group">
        <label class="filter-label">时间范围</label>
        <select class="filter-select" v-model="filters.range">
          <option>今日</option>
          <option>本周</option>
          <option>本月</option>
          <option>自定义</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="filter-label">线路范围</label>
        <select class="filter-select" v-model="filters.lineGroup">
          <option>全部线路</option>
          <option>城区主干线</option>
          <option>城郊支线</option>
          <option>机场快线</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="filter-label">出行类型</label>
        <select class="filter-select" v-model="filters.dayType">
          <option>工作日</option>
          <option>周末</option>
          <option>节假日</option>
        </select>
      </div>
      <button class="btn btn-primary touch-target">生成优化建议</button>
      <button class="btn btn-outline touch-target">导出策略</button>
    </section>

    <section class="insight-grid">
      <div class="insight-card">
        <span class="insight-label">平均上座率</span>
        <h3 class="insight-value">{{ averageOccupancy }}%</h3>
        <span class="insight-meta">过去7日均值</span>
      </div>
      <div class="insight-card">
        <span class="insight-label">峰值断面满载率</span>
        <h3 class="insight-value">{{ maxSectionLoad }}%</h3>
        <span class="insight-meta">最高负载区间</span>
      </div>
      <div class="insight-card">
        <span class="insight-label">长期过载线路</span>
        <h3 class="insight-value">{{ overloadedCount }} 条</h3>
        <span class="insight-meta">连续高负载 >= 10天</span>
      </div>
      <div class="insight-card">
        <span class="insight-label">运力闲置线路</span>
        <h3 class="insight-value">{{ idleCount }} 条</h3>
        <span class="insight-meta">上座率 < 55%</span>
      </div>
    </section>

    <section class="section-grid">
      <div class="section-card wide">
        <header class="section-header">
          <div>
            <h2 class="section-title">线路负载分析</h2>
            <p class="section-subtitle">对比上座率与断面满载率，定位长期瓶颈区间。</p>
          </div>
          <div class="section-actions">
            <button class="chip active">上座率</button>
            <button class="chip">断面满载率</button>
            <button class="chip">运营效率</button>
          </div>
        </header>
        <div class="line-list">
          <div v-for="line in lineLoads" :key="line.id" class="line-row">
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

      <div class="section-card">
        <header class="section-header">
          <div>
            <h2 class="section-title">OD区间预警</h2>
            <p class="section-subtitle">识别断面连续过载的重点区间。</p>
          </div>
        </header>
        <div class="od-list">
          <div v-for="alert in odAlerts" :key="alert.segment" class="od-item">
            <div class="od-title">{{ alert.segment }}</div>
            <div class="od-metrics">
              <span class="od-load" :class="loadClass(alert.load * 100)">{{ Math.round(alert.load * 100) }}%</span>
              <span class="od-duration">{{ alert.duration }}</span>
            </div>
            <div class="od-suggestion">{{ alert.suggestion }}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="section-grid">
      <div class="section-card">
        <header class="section-header">
          <div>
            <h2 class="section-title">车次客流密度矩阵</h2>
            <p class="section-subtitle">对比不同线路与车次的密度水平，识别运力闲置。</p>
          </div>
        </header>
        <div class="density-grid">
          <div class="density-head">线路 / 车次</div>
          <div v-for="train in densityTrains" :key="train" class="density-head">{{ train }}</div>
          <template v-for="row in densityMatrix" :key="row.line">
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

      <div class="section-card">
        <header class="section-header">
          <div>
            <h2 class="section-title">时刻表优化</h2>
            <p class="section-subtitle">评估客流与发车时刻的匹配度，建议调整频次。</p>
          </div>
        </header>
        <div class="timetable-list">
          <div v-for="window in timetableWindows" :key="window.time" class="timetable-row">
            <div class="timetable-time">{{ window.time }}</div>
            <div class="timetable-bar">
              <div class="timetable-fill" :class="densityClass(window.load)" :style="{ width: Math.round(window.load * 100) + '%' }"></div>
            </div>
            <div class="timetable-note">{{ window.suggestion }}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="section-grid">
      <div class="section-card">
        <header class="section-header">
          <div>
            <h2 class="section-title">枢纽识别</h2>
            <p class="section-subtitle">基于度中心性与介数中心性识别关键枢纽站点。</p>
          </div>
        </header>
        <div class="hub-list">
          <div v-for="hub in hubs" :key="hub.name" class="hub-row">
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

      <div class="section-card wide">
        <header class="section-header">
          <div>
            <h2 class="section-title">优化建议</h2>
            <p class="section-subtitle">结合负载与客流变化，形成可执行的增开与调度建议。</p>
          </div>
        </header>
        <div class="recommendation-grid">
          <div v-for="card in recommendations" :key="card.title" class="recommendation-card">
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
import { computed, reactive } from 'vue'

const filters = reactive({
  range: '本周',
  lineGroup: '全部线路',
  dayType: '工作日'
})

const lineLoads = [
  {
    id: 1,
    name: '1号线',
    code: 'L1',
    occupancy: 82,
    sectionLoad: 94,
    trend: 6,
    peakSegment: '南城站 - 中山站'
  },
  {
    id: 2,
    name: '2号线',
    code: 'L2',
    occupancy: 68,
    sectionLoad: 73,
    trend: -3,
    peakSegment: '北站 - 科技园'
  },
  {
    id: 3,
    name: '3号线',
    code: 'L3',
    occupancy: 91,
    sectionLoad: 102,
    trend: 9,
    peakSegment: '大学城 - 东港'
  },
  {
    id: 4,
    name: '机场线',
    code: 'A1',
    occupancy: 52,
    sectionLoad: 57,
    trend: -4,
    peakSegment: '航站楼 - 机场南'
  },
  {
    id: 5,
    name: '环线',
    code: 'R1',
    occupancy: 76,
    sectionLoad: 88,
    trend: 2,
    peakSegment: '金融城 - 南广场'
  }
]

const odAlerts = [
  {
    segment: '中央站 → 西湖站',
    load: 1.08,
    duration: '连续 12 天高负载',
    suggestion: '建议增开 2 列临客'
  },
  {
    segment: '大学城 → 科技园',
    load: 0.97,
    duration: '连续 9 天满载',
    suggestion: '增加早高峰区间快车'
  },
  {
    segment: '南城 → 东港',
    load: 0.91,
    duration: '断面拥挤明显',
    suggestion: '建议工作日加密班次'
  }
]

const densityMatrix = [
  {
    line: '1号线',
    trains: [
      { name: 'G01', density: 0.92 },
      { name: 'G05', density: 0.76 },
      { name: 'G12', density: 0.64 },
      { name: 'D03', density: 0.48 },
      { name: 'K21', density: 0.32 }
    ]
  },
  {
    line: '2号线',
    trains: [
      { name: 'G01', density: 0.58 },
      { name: 'G05', density: 0.66 },
      { name: 'G12', density: 0.71 },
      { name: 'D03', density: 0.43 },
      { name: 'K21', density: 0.29 }
    ]
  },
  {
    line: '3号线',
    trains: [
      { name: 'G01', density: 0.96 },
      { name: 'G05', density: 0.84 },
      { name: 'G12', density: 0.79 },
      { name: 'D03', density: 0.61 },
      { name: 'K21', density: 0.54 }
    ]
  },
  {
    line: '机场线',
    trains: [
      { name: 'G01', density: 0.41 },
      { name: 'G05', density: 0.38 },
      { name: 'G12', density: 0.45 },
      { name: 'D03', density: 0.33 },
      { name: 'K21', density: 0.21 }
    ]
  }
]

const timetableWindows = [
  { time: '06:00-08:00', load: 0.92, suggestion: '加密发车至 3-4 分钟' },
  { time: '08:00-10:00', load: 0.88, suggestion: '保持现有频次，优化站停' },
  { time: '10:00-16:00', load: 0.55, suggestion: '合并班次，节约运力' },
  { time: '16:00-19:00', load: 0.93, suggestion: '增加区间车 2 班次' },
  { time: '19:00-22:00', load: 0.62, suggestion: '恢复均衡发车' }
]

const hubs = [
  { name: '中央站', role: '核心枢纽', degree: 0.86, betweenness: 0.74, closeness: 0.69, trend: 4 },
  { name: '科技园站', role: '通勤换乘', degree: 0.78, betweenness: 0.61, closeness: 0.63, trend: 2 },
  { name: '南城站', role: '区域枢纽', degree: 0.72, betweenness: 0.57, closeness: 0.58, trend: -1 },
  { name: '西湖站', role: '旅游集散', degree: 0.68, betweenness: 0.49, closeness: 0.55, trend: 3 }
]

const recommendations = [
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
    priority: 'P1',
    priorityClass: 'priority-medium',
    type: '枢纽优化',
    title: '中央站优化换乘动线',
    detail: '介数中心性长期居高，建议增加客流引导与分流标识。',
    impact: '换乘效率 +6%',
    line: '枢纽网络'
  }
]

const pulseIndicators = [
  { label: '负载匹配', value: 78 },
  { label: '高峰吸纳', value: 84 },
  { label: '运力弹性', value: 63 }
]

const densityTrains = computed(() => densityMatrix[0]?.trains.map(item => item.name) || [])

const averageOccupancy = computed(() => {
  const sum = lineLoads.reduce((total, line) => total + line.occupancy, 0)
  return Math.round(sum / lineLoads.length)
})

const maxSectionLoad = computed(() => Math.max(...lineLoads.map(line => line.sectionLoad)))

const overloadedCount = computed(() => lineLoads.filter(line => line.sectionLoad >= 90).length)

const idleCount = computed(() => lineLoads.filter(line => line.occupancy < 55).length)

const overloadedRatio = computed(() => Math.round((overloadedCount.value / lineLoads.length) * 100))

const focusLine = computed(() => {
  const sorted = [...lineLoads].sort((a, b) => b.sectionLoad - a.sectionLoad)
  return sorted[0]?.name || ''
})

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
  background: radial-gradient(circle at 10% 20%, rgba(70, 130, 180, 0.12), transparent 45%),
    radial-gradient(circle at 90% 10%, rgba(46, 139, 87, 0.12), transparent 40%),
    radial-gradient(circle at 80% 80%, rgba(210, 105, 30, 0.12), transparent 45%);
  z-index: -1;
}

.page-hero {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-6);
  padding: var(--spacing-6);
  border-radius: var(--border-radius-2xl);
  background: linear-gradient(135deg, rgba(46, 139, 87, 0.08), rgba(70, 130, 180, 0.12));
  border: 1px solid var(--color-border-light);
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.eyebrow {
  font-size: var(--font-size-xs);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--color-text-tertiary);
}

.page-title {
  font-size: var(--font-size-3xl);
  margin: 0;
  color: var(--color-text-primary);
}

.page-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: var(--line-height-relaxed);
}

.hero-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
}

.tag {
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-xs);
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(70, 130, 180, 0.2);
  color: var(--color-text-secondary);
}

.hero-panel {
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.panel-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.pulse-grid {
  display: grid;
  gap: var(--spacing-3);
}

.pulse-item {
  display: grid;
  grid-template-columns: 1fr 2fr auto;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
}

.pulse-track {
  height: 6px;
  background: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.pulse-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-secondary), var(--color-primary));
  border-radius: inherit;
}

.panel-footer {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-4);
  align-items: flex-end;
  padding: var(--spacing-4);
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-xl);
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-sm);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  min-width: 180px;
}

.filter-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.filter-select {
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--border-radius-base);
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.insight-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-4);
}

.insight-card {
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.insight-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.insight-value {
  margin: 0;
  font-size: var(--font-size-2xl);
  color: var(--color-text-primary);
}

.insight-meta {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.section-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);
}

.section-card {
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-4);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.section-card.wide {
  grid-column: span 2;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-3);
}

.section-title {
  margin: 0;
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
}

.section-subtitle {
  margin: var(--spacing-1) 0 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.section-actions {
  display: flex;
  gap: var(--spacing-2);
}

.chip {
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  padding: var(--spacing-1) var(--spacing-3);
  border-radius: var(--border-radius-full);
  font-size: var(--font-size-xs);
  cursor: pointer;
}

.chip.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.line-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.line-row {
  display: grid;
  grid-template-columns: 140px 1fr 220px;
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
  .page-hero {
    grid-template-columns: 1fr;
  }

  .insight-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .section-grid {
    grid-template-columns: 1fr;
  }

  .section-card.wide {
    grid-column: auto;
  }

  .recommendation-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
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
