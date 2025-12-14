<template>
  <div class="station-map">
    <div class="map-header">
      <h3 class="map-title">{{ title }}</h3>
      <div class="map-controls">
        <button
          class="control-btn"
          :class="{ active: zoomLevel === 1 }"
          @click="setZoomLevel(1)"
        >
          区域视图
        </button>
        <button
          class="control-btn"
          :class="{ active: zoomLevel === 2 }"
          @click="setZoomLevel(2)"
        >
          城市视图
        </button>
        <button
          class="control-btn"
          :class="{ active: zoomLevel === 3 }"
          @click="setZoomLevel(3)"
        >
          站点视图
        </button>
        <button class="control-btn" @click="resetView">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 8V4M12 4L8 8M12 4L16 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 12H8M20 12H16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 16V20M12 20L8 16M12 20L16 16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          重置
        </button>
      </div>
    </div>
    <div class="map-container">
      <div class="map-background" :style="mapStyle">
        <!-- 地图网格 -->
        <div class="map-grid">
          <div v-for="i in gridLines" :key="i" class="grid-line"></div>
        </div>

        <!-- 站点标记 -->
        <div
          v-for="station in visibleStations"
          :key="station.id"
          class="station-marker"
          :style="getStationStyle(station)"
          @mouseenter="showStationTooltip(station)"
          @mouseleave="hideStationTooltip"
          @click="selectStation(station)"
        >
          <div class="marker-dot" :class="getStationSizeClass(station)">
            <div class="marker-pulse"></div>
          </div>
          <div class="marker-label" :class="{ active: selectedStationId === station.id }">
            {{ station.name }}
          </div>
        </div>

        <!-- 连接线 -->
        <svg class="connection-lines" width="100%" height="100%">
          <line
            v-for="connection in visibleConnections"
            :key="connection.id"
            :x1="connection.x1"
            :y1="connection.y1"
            :x2="connection.x2"
            :y2="connection.y2"
            class="connection-line"
            :class="connection.intensity"
          />
        </svg>
      </div>

      <!-- 图例 -->
      <div class="map-legend">
        <div class="legend-section">
          <h4 class="legend-title">站点客流量</h4>
          <div class="legend-items">
            <div class="legend-item">
              <div class="legend-marker large"></div>
              <span>高客流量 (>10万)</span>
            </div>
            <div class="legend-item">
              <div class="legend-marker medium"></div>
              <span>中客流量 (5-10万)</span>
            </div>
            <div class="legend-item">
              <div class="legend-marker small"></div>
              <span>低客流量 (<5万)</span>
            </div>
          </div>
        </div>
        <div class="legend-section">
          <h4 class="legend-title">线路流量</h4>
          <div class="legend-items">
            <div class="legend-item">
              <div class="legend-line high"></div>
              <span>高流量</span>
            </div>
            <div class="legend-item">
              <div class="legend-line medium"></div>
              <span>中流量</span>
            </div>
            <div class="legend-item">
              <div class="legend-line low"></div>
              <span>低流量</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 站点详情面板 -->
    <div v-if="selectedStation" class="station-details">
      <div class="details-header">
        <h4 class="details-title">{{ selectedStation.name }} 站</h4>
        <button class="close-btn" @click="deselectStation">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      <div class="details-content">
        <div class="station-info">
          <div class="info-row">
            <span class="info-label">车站代码：</span>
            <span class="info-value">{{ selectedStation.code }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">今日客流量：</span>
            <span class="info-value">{{ selectedStation.todayPassengers.toLocaleString() }} 人</span>
          </div>
          <div class="info-row">
            <span class="info-label">累计客流量：</span>
            <span class="info-value">{{ selectedStation.totalPassengers.toLocaleString() }} 人</span>
          </div>
          <div class="info-row">
            <span class="info-label">上座率：</span>
            <span class="info-value">{{ selectedStation.occupancyRate }}%</span>
          </div>
          <div class="info-row">
            <span class="info-label">连接线路：</span>
            <span class="info-value">{{ selectedStation.connectedLines.join(', ') }}</span>
          </div>
        </div>
        <div class="station-stats">
          <div class="stat-card">
            <div class="stat-value">{{ selectedStation.departures }}</div>
            <div class="stat-label">今日发车</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ selectedStation.arrivals }}</div>
            <div class="stat-label">今日到达</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ selectedStation.delayRate }}%</div>
            <div class="stat-label">准点率</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 工具提示 -->
    <div
      v-if="tooltip.visible"
      class="station-tooltip"
      :style="tooltipStyle"
    >
      <div class="tooltip-header">
        <strong>{{ tooltip.station.name }}</strong>
      </div>
      <div class="tooltip-content">
        <div class="tooltip-row">
          <span class="tooltip-label">代码：</span>
          <span class="tooltip-value">{{ tooltip.station.code }}</span>
        </div>
        <div class="tooltip-row">
          <span class="tooltip-label">今日客流：</span>
          <span class="tooltip-value">{{ tooltip.station.todayPassengers.toLocaleString() }} 人</span>
        </div>
        <div class="tooltip-row">
          <span class="tooltip-label">上座率：</span>
          <span class="tooltip-value">{{ tooltip.station.occupancyRate }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Station {
  id: number
  name: string
  code: string
  x: number
  y: number
  todayPassengers: number
  totalPassengers: number
  occupancyRate: number
  departures: number
  arrivals: number
  delayRate: number
  connectedLines: string[]
}

interface Connection {
  id: number
  fromStationId: number
  toStationId: number
  intensity: 'high' | 'medium' | 'low'
}

interface TooltipData {
  visible: boolean
  station: Station
  x: number
  y: number
}

const props = withDefaults(defineProps<{
  title?: string
  stations?: Station[]
  connections?: Connection[]
}>(), {
  title: '成渝地区铁路站点分布',
  stations: () => [],
  connections: () => []
})

// 缩放级别
const zoomLevel = ref(2)

// 选中的站点
const selectedStationId = ref<number | null>(null)

// 工具提示
const tooltip = ref<TooltipData>({
  visible: false,
  station: {} as Station,
  x: 0,
  y: 0
})

// 地图样式
const mapStyle = computed(() => {
  const scale = zoomLevel.value
  return {
    transform: `scale(${scale})`,
    transformOrigin: 'center center'
  }
})

// 网格线数量
const gridLines = computed(() => {
  return zoomLevel.value * 10
})

// 可见的站点
const visibleStations = computed(() => {
  if (props.stations.length > 0) {
    return props.stations
  }
  return generateMockStations()
})

// 可见的连接线
const visibleConnections = computed(() => {
  if (props.connections.length > 0) {
    return calculateConnectionLines(props.connections)
  }
  return calculateConnectionLines(generateMockConnections())
})

// 选中的站点
const selectedStation = computed(() => {
  if (!selectedStationId.value) return null
  return visibleStations.value.find(station => station.id === selectedStationId.value)
})

// 工具提示样式
const tooltipStyle = computed(() => ({
  left: `${tooltip.value.x}px`,
  top: `${tooltip.value.y}px`
}))

// 生成模拟站点数据
const generateMockStations = (): Station[] => {
  return [
    {
      id: 1,
      name: '成都东站',
      code: 'CDW',
      x: 30,
      y: 40,
      todayPassengers: 125678,
      totalPassengers: 4567890,
      occupancyRate: 92,
      departures: 156,
      arrivals: 148,
      delayRate: 98,
      connectedLines: ['成渝高铁', '成贵高铁', '西成高铁']
    },
    {
      id: 2,
      name: '重庆北站',
      code: 'CUW',
      x: 60,
      y: 60,
      todayPassengers: 98765,
      totalPassengers: 3456789,
      occupancyRate: 88,
      departures: 142,
      arrivals: 135,
      delayRate: 96,
      connectedLines: ['成渝高铁', '渝贵铁路', '渝万铁路']
    },
    {
      id: 3,
      name: '内江北站',
      code: 'NKW',
      x: 40,
      y: 50,
      todayPassengers: 65432,
      totalPassengers: 2345678,
      occupancyRate: 78,
      departures: 98,
      arrivals: 95,
      delayRate: 97,
      connectedLines: ['成渝高铁', '内昆铁路']
    },
    {
      id: 4,
      name: '资阳北站',
      code: 'ZYW',
      x: 35,
      y: 45,
      todayPassengers: 54321,
      totalPassengers: 1234567,
      occupancyRate: 65,
      departures: 76,
      arrivals: 72,
      delayRate: 99,
      connectedLines: ['成渝高铁']
    },
    {
      id: 5,
      name: '永川东站',
      code: 'YCW',
      x: 55,
      y: 55,
      todayPassengers: 43210,
      totalPassengers: 987654,
      occupancyRate: 72,
      departures: 65,
      arrivals: 68,
      delayRate: 98,
      connectedLines: ['成渝高铁']
    },
    {
      id: 6,
      name: '荣昌北站',
      code: 'RCW',
      x: 50,
      y: 58,
      todayPassengers: 32109,
      totalPassengers: 876543,
      occupancyRate: 58,
      departures: 54,
      arrivals: 56,
      delayRate: 99,
      connectedLines: ['成渝高铁']
    }
  ]
}

// 生成模拟连接数据
const generateMockConnections = (): Connection[] => {
  return [
    { id: 1, fromStationId: 1, toStationId: 2, intensity: 'high' },
    { id: 2, fromStationId: 2, toStationId: 1, intensity: 'high' },
    { id: 3, fromStationId: 1, toStationId: 3, intensity: 'medium' },
    { id: 4, fromStationId: 3, toStationId: 1, intensity: 'medium' },
    { id: 5, fromStationId: 1, toStationId: 4, intensity: 'low' },
    { id: 6, fromStationId: 4, toStationId: 1, intensity: 'low' },
    { id: 7, fromStationId: 2, toStationId: 5, intensity: 'medium' },
    { id: 8, fromStationId: 5, toStationId: 2, intensity: 'medium' },
    { id: 9, fromStationId: 2, toStationId: 6, intensity: 'low' },
    { id: 10, fromStationId: 6, toStationId: 2, intensity: 'low' }
  ]
}

// 计算连接线坐标
const calculateConnectionLines = (connections: Connection[]) => {
  return connections.map(connection => {
    const fromStation = visibleStations.value.find(s => s.id === connection.fromStationId)
    const toStation = visibleStations.value.find(s => s.id === connection.toStationId)

    if (!fromStation || !toStation) {
      return {
        id: connection.id,
        x1: 0,
        y1: 0,
        x2: 0,
        y2: 0,
        intensity: connection.intensity
      }
    }

    return {
      id: connection.id,
      x1: `${fromStation.x}%`,
      y1: `${fromStation.y}%`,
      x2: `${toStation.x}%`,
      y2: `${toStation.y}%`,
      intensity: connection.intensity
    }
  })
}

// 获取站点样式
const getStationStyle = (station: Station) => {
  return {
    left: `${station.x}%`,
    top: `${station.y}%`
  }
}

// 获取站点大小类
const getStationSizeClass = (station: Station) => {
  if (station.todayPassengers > 100000) return 'large'
  if (station.todayPassengers > 50000) return 'medium'
  return 'small'
}

// 显示站点工具提示
const showStationTooltip = (station: Station) => {
  tooltip.value = {
    visible: true,
    station,
    x: station.x * 10,
    y: station.y * 10
  }
}

// 隐藏站点工具提示
const hideStationTooltip = () => {
  tooltip.value.visible = false
}

// 选择站点
const selectStation = (station: Station) => {
  selectedStationId.value = station.id
}

// 取消选择站点
const deselectStation = () => {
  selectedStationId.value = null
}

// 设置缩放级别
const setZoomLevel = (level: number) => {
  zoomLevel.value = level
}

// 重置视图
const resetView = () => {
  zoomLevel.value = 2
  selectedStationId.value = null
}

// 初始化
onMounted(() => {
  // 可以在这里加载真实数据
})
</script>

<style scoped>
.station-map {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
  position: relative;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.map-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.map-controls {
  display: flex;
  gap: var(--spacing-2);
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
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.control-btn:hover {
  background-color: var(--color-bg-tertiary);
}

.control-btn.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.control-btn svg {
  width: 14px;
  height: 14px;
}

.map-container {
  position: relative;
  height: 400px;
  overflow: hidden;
  border-radius: var(--border-radius-base);
  background-color: var(--color-bg-secondary);
}

.map-background {
  width: 100%;
  height: 100%;
  position: relative;
  transition: transform var(--transition-base);
}

.map-grid {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(v-bind(gridLines), 1fr);
  grid-template-rows: repeat(v-bind(gridLines), 1fr);
}

.grid-line {
  border-right: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
}

.station-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 2;
}

.marker-dot {
  position: relative;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  transition: all var(--transition-fast);
}

.marker-dot.large {
  width: 36px;
  height: 36px;
  background-color: var(--color-error);
}

.marker-dot.medium {
  width: 28px;
  height: 28px;
  background-color: var(--color-warning);
}

.marker-dot.small {
  width: 20px;
  height: 20px;
  background-color: var(--color-success);
}

.marker-pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background-color: inherit;
  opacity: 0.6;
  animation: pulse 2s infinite;
}

.marker-label {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  font-size: var(--font-size-xs);
  white-space: nowrap;
  background-color: white;
  padding: 4px 8px;
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-sm);
  margin-top: 4px;
  transition: all var(--transition-fast);
  opacity: 0.8;
}

.marker-label.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  opacity: 1;
  font-weight: var(--font-weight-medium);
}

.station-marker:hover .marker-dot {
  transform: scale(1.2);
}

.station-marker:hover .marker-label {
  opacity: 1;
  transform: translateX(-50%) translateY(2px);
}

.connection-lines {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

.connection-line {
  stroke-width: 2;
  stroke-linecap: round;
}

.connection-line.high {
  stroke: var(--color-error);
  stroke-width: 3;
}

.connection-line.medium {
  stroke: var(--color-warning);
  stroke-width: 2;
}

.connection-line.low {
  stroke: var(--color-success);
  stroke-width: 1;
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
  gap: var(--spacing-4);
  max-width: 300px;
}

.legend-section {
  flex: 1;
}

.legend-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-2) 0;
}

.legend-items {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.legend-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid white;
}

.legend-marker.large {
  background-color: var(--color-error);
}

.legend-marker.medium {
  background-color: var(--color-warning);
}

.legend-marker.small {
  background-color: var(--color-success);
}

.legend-line {
  width: 20px;
  height: 2px;
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

.station-details {
  position: absolute;
  top: var(--spacing-4);
  right: var(--spacing-4);
  width: 300px;
  background-color: white;
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-lg);
  z-index: 10;
  animation: slideInRight var(--transition-base);
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-3) var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
}

.details-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.close-btn {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  border-radius: var(--border-radius-sm);
  transition: all var(--transition-fast);
}

.close-btn:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.close-btn svg {
  width: 16px;
  height: 16px;
}

.details-content {
  padding: var(--spacing-4);
}

.station-info {
  margin-bottom: var(--spacing-4);
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-2);
  font-size: var(--font-size-sm);
}

.info-label {
  color: var(--color-text-secondary);
}

.info-value {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.station-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-3);
}

.stat-card {
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-2);
  text-align: center;
}

.stat-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-1);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.station-tooltip {
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

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.5);
    opacity: 0;
  }
  100% {
    transform: scale(1);
    opacity: 0.6;
  }
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
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
  .map-container {
    height: 300px;
  }

  .map-legend {
    flex-direction: column;
    gap: var(--spacing-3);
    max-width: 200px;
  }

  .station-details {
    position: relative;
    top: auto;
    right: auto;
    width: 100%;
    margin-top: var(--spacing-4);
  }

  .map-controls {
    flex-wrap: wrap;
  }

  .control-btn {
    padding: var(--spacing-1) var(--spacing-2);
    font-size: 11px;
  }
}
</style>