<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useMapStore } from '@/stores/map'
import { GAODE_MAP_CONFIG } from '@/config'

// 加载高德地图JS API Loader
let AMapLoader: any = null

// Props
const props = withDefaults(defineProps<{
  mapId?: string
  className?: string
  interactive?: boolean
  showControls?: boolean
  fitViewToMarkers?: boolean
}>(), {
  mapId: 'gaode-map-container',
  className: '',
  interactive: true,
  showControls: true,
  fitViewToMarkers: true,
})

// Emits
const emit = defineEmits<{
  'map-loaded': [map: any]
  'map-click': [event: any]
  'map-move': [event: any]
  'station-click': [stationId: number]
  'station-hover': [stationId: number | null]
  'flowline-click': [lineId: string]
  'flowline-hover': [lineId: string | null]
}>()

// Store
const mapStore = useMapStore()

// 状态
const mapInstance = ref<any>(null)
const mapLoading = ref(false)
const mapError = ref<string | null>(null)
const markerInstances = ref<any[]>([])
const flowLineInstances = ref<Array<{ id: string; line: any; data: any }>>([])
const flowStationInstances = ref<any[]>([])
const flowLineBlinkTimers = new Map<string, number>()
const flowInfoWindow = ref<any>(null)
const activeFlowLineId = ref<string | null>(null)
const stickyFlowLineId = ref<string | null>(null)
const focusedFlowLineId = ref<string | null>(null)
const suppressNextMapClick = ref(false)

// 计算属性
const mapStyle = computed(() => {
  return {
    width: '100%',
    height: '100%',
    minHeight: '400px',
  }
})

// 初始化地图
const initMap = async () => {
  if (mapLoading.value) return

  try {
    mapLoading.value = true
    mapError.value = null

    // 动态加载高德地图JS API Loader
    if (!AMapLoader) {
      AMapLoader = (await import('@amap/amap-jsapi-loader')).default
    }

    // 加载高德地图API
    const AMap = await AMapLoader.load({
      key: GAODE_MAP_CONFIG.API_KEY,
      version: GAODE_MAP_CONFIG.VERSION,
      plugins: GAODE_MAP_CONFIG.PLUGINS,
    })

    // 创建地图实例
    mapInstance.value = new AMap.Map(props.mapId, {
      zoom: mapStore.viewState.zoom,
      center: mapStore.viewState.center,
      mapStyle: `amap://styles/${mapStore.mapConfig.mapType}`,
      viewMode: '2D',
      zoomEnable: props.interactive,
      dragEnable: props.interactive,
      rotateEnable: false,
      pitchEnable: false,
      buildingAnimation: false,
      expandZoomRange: true,
      zooms: [GAODE_MAP_CONFIG.MIN_ZOOM, GAODE_MAP_CONFIG.MAX_ZOOM],
    })

    // 添加控件
    if (props.showControls) {
      // 比例尺
      mapInstance.value.addControl(new AMap.Scale({
        position: 'LB',
      }))

      // 工具条
      mapInstance.value.addControl(new AMap.ToolBar({
        position: 'RT',
      }))

      // 地图类型切换
      mapInstance.value.addControl(new AMap.MapType({
        defaultType: 0,
        position: 'RT',
      }))

      // 鹰眼图
      mapInstance.value.addControl(new AMap.HawkEye({
        position: 'RB',
      }))
    }

    // 绑定事件
    bindMapEvents()

    // 渲染标记
    renderStationMarkers()

    // 渲染流向线
    renderFlowLines()

    // 更新store视图状态
    updateViewState()

    emit('map-loaded', mapInstance.value)

    console.log('高德地图初始化成功')
  } catch (error) {
    mapError.value = error instanceof Error ? error.message : '地图加载失败'
    console.error('高德地图初始化失败:', error)
  } finally {
    mapLoading.value = false
  }
}

// 绑定地图事件
const bindMapEvents = () => {
  if (!mapInstance.value) return

  // 地图点击事件
  mapInstance.value.on('click', (event: any) => {
    if (suppressNextMapClick.value) {
      suppressNextMapClick.value = false
      return
    }
    if (stickyFlowLineId.value) {
      resetActiveFlowLine(stickyFlowLineId.value)
      stickyFlowLineId.value = null
      closeFlowInfoWindow()
    }
    if (focusedFlowLineId.value) {
      focusedFlowLineId.value = null
      applyFlowLineStyles()
    }
    emit('map-click', event)
  })

  // 地图移动事件
  mapInstance.value.on('moveend', () => {
    updateViewState()
    emit('map-move', mapInstance.value.getCenter())
  })

  // 地图缩放事件
  mapInstance.value.on('zoomchange', () => {
    updateViewState()
  })
}

// 更新store中的视图状态
const updateViewState = () => {
  if (!mapInstance.value) return

  const center = mapInstance.value.getCenter()
  const zoom = mapInstance.value.getZoom()
  const bounds = mapInstance.value.getBounds()

  mapStore.updateViewState({
    center: [center.lng, center.lat],
    zoom,
    bounds: bounds ? [[bounds.south, bounds.west], [bounds.north, bounds.east]] : null,
  })
}

// 渲染车站标记
const renderStationMarkers = () => {
  if (!mapInstance.value) return

  // 清除现有标记
  clearAllMarkers()

  if (!mapStore.mapConfig.showStationMarkers) {
    renderFlowStationsFromLines()
    return
  }

  // 添加新标记
  mapStore.visibleMarkers.forEach(markerData => {
    const marker = createStationMarker(markerData)
    if (marker) {
      markerInstances.value.push(marker)
    }
  })

  renderFlowStationsFromLines()
}

// 创建单个车站标记
const createStationMarker = (markerData: any) => {
  if (!mapInstance.value || !window.AMap) return

  const AMap = window.AMap

  // 创建标记
  const marker = new AMap.Marker({
    position: new AMap.LngLat(markerData.position[0], markerData.position[1]),
    title: markerData.stationName,
    offset: new AMap.Pixel(-markerData.size / 2, -markerData.size / 2),
    size: [markerData.size, markerData.size],
    content: createMarkerContent(markerData),
  })

  // 绑定事件
  marker.on('click', () => {
    mapStore.selectStation(markerData.stationId)
    emit('station-click', markerData.stationId)
  })

  marker.on('mouseover', () => {
    mapStore.hoverStation(markerData.stationId)
    emit('station-hover', markerData.stationId)
  })

  marker.on('mouseout', () => {
    mapStore.hoverStation(null)
    emit('station-hover', null)
  })

  // 添加到地图
  marker.setMap(mapInstance.value)

  return marker
}

// 创建标记内容
const createMarkerContent = (markerData: any) => {
  const size = markerData.size
  const color = markerData.color || '#0066cc'
  const isSelected = mapStore.selectedStation === markerData.stationId
  const isHovered = mapStore.hoveredStation === markerData.stationId

  const borderColor = isSelected ? '#ff9800' : isHovered ? '#00aaff' : '#ffffff'
  const borderWidth = isSelected ? 3 : isHovered ? 2 : 1
  const scale = isSelected ? 1.2 : isHovered ? 1.1 : 1
  const shadow = isSelected ? '0 4px 12px rgba(0,0,0,0.4)' :
                isHovered ? '0 3px 8px rgba(0,0,0,0.35)' :
                '0 2px 6px rgba(0,0,0,0.3)'

  // 创建涟漪效果
  const rippleEffect = isSelected ? `
    <div style="
      position: absolute;
      top: 50%;
      left: 50%;
      width: ${size * 2}px;
      height: ${size * 2}px;
      background: radial-gradient(circle, ${color}40 0%, transparent 70%);
      border-radius: 50%;
      transform: translate(-50%, -50%);
      animation: ripple 1.5s ease-out infinite;
      pointer-events: none;
      z-index: -1;
    "></div>
  ` : ''

  return `
    <div style="
      position: relative;
      width: ${size}px;
      height: ${size}px;
      transform: scale(${scale});
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    ">
      ${rippleEffect}
      <div style="
        width: 100%;
        height: 100%;
        background-color: ${color};
        border-radius: 50%;
        border: ${borderWidth}px solid ${borderColor};
        box-shadow: ${shadow};
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: ${Math.max(10, size / 3)}px;
        font-weight: bold;
        cursor: pointer;
        position: relative;
        z-index: 1;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      ">
        ${markerData.passengerCount > 9999 ?
          `${(markerData.passengerCount / 10000).toFixed(1)}万` :
          markerData.passengerCount}
      </div>
    </div>
    <style>
      @keyframes ripple {
        0% {
          transform: translate(-50%, -50%) scale(0.8);
          opacity: 0.8;
        }
        100% {
          transform: translate(-50%, -50%) scale(1.5);
          opacity: 0;
        }
      }
    </style>
  `
}

// 渲染流向线
const renderFlowLines = () => {
  if (!mapInstance.value) return

  // 清除现有流向线
  clearAllFlowLines()
  clearAllFlowStations()

  if (!mapStore.mapConfig.showFlowLines) return

  // 添加新流向线
  mapStore.visibleFlowLines.forEach(lineData => {
    const line = createFlowLine(lineData)
    if (line) {
      flowLineInstances.value.push({ id: lineData.id, line, data: lineData })
      if (lineData.blink) {
        startFlowLineBlink(lineData.id, line)
      }
    }
  })

  renderFlowStationsFromLines()
  applyFlowLineStyles()
}

// 创建流向线
const createFlowLine = (lineData: any) => {
  if (!mapInstance.value || !window.AMap) return

  const AMap = window.AMap

  const line = new AMap.Polyline({
    path: [
      new AMap.LngLat(lineData.fromPosition[0], lineData.fromPosition[1]),
      new AMap.LngLat(lineData.toPosition[0], lineData.toPosition[1]),
    ],
    ...getFlowLineStyle(lineData, false),
  })

  line.on('mouseover', (event: any) => {
    if (focusedFlowLineId.value && focusedFlowLineId.value !== lineData.id) {
      return
    }
    if (!stickyFlowLineId.value) {
      setActiveFlowLine(lineData.id)
      openFlowInfoWindow(lineData, event?.lnglat)
    }
    emit('flowline-hover', lineData.id)
  })

  line.on('mouseout', () => {
    if (focusedFlowLineId.value && focusedFlowLineId.value !== lineData.id) {
      return
    }
    if (!stickyFlowLineId.value) {
      resetActiveFlowLine(lineData.id)
      closeFlowInfoWindow()
    }
    emit('flowline-hover', null)
  })

  line.on('click', (event: any) => {
    suppressNextMapClick.value = true
    if (stickyFlowLineId.value && stickyFlowLineId.value !== lineData.id) {
      resetActiveFlowLine(stickyFlowLineId.value)
    }

    stickyFlowLineId.value = lineData.id
    focusedFlowLineId.value = lineData.id
    setActiveFlowLine(lineData.id)
    openFlowInfoWindow(lineData, event?.lnglat)
    applyFlowLineStyles()
    emit('flowline-click', lineData.id)
  })

  line.setMap(mapInstance.value)

  return line
}

const startFlowLineBlink = (lineId: string, line: any) => {
  if (flowLineBlinkTimers.has(lineId)) return
  let high = true
  const timer = window.setInterval(() => {
    high = !high
    line.setOptions({ strokeOpacity: high ? 0.95 : 0.25 })
  }, 900)
  flowLineBlinkTimers.set(lineId, timer)
}

// 清除所有标记
const clearAllMarkers = () => {
  if (mapInstance.value) {
    markerInstances.value.forEach(marker => {
      marker.setMap(null)
    })
    markerInstances.value = []
  }
}

const clearAllFlowStations = () => {
  if (mapInstance.value) {
    flowStationInstances.value.forEach(marker => {
      marker.setMap(null)
    })
    flowStationInstances.value = []
  }
}

// 清除所有流向线
const clearAllFlowLines = () => {
  if (mapInstance.value) {
    flowLineInstances.value.forEach(item => {
      item.line.setMap(null)
    })
    flowLineInstances.value = []
    activeFlowLineId.value = null
    stickyFlowLineId.value = null
    focusedFlowLineId.value = null
    flowLineBlinkTimers.forEach(timer => {
      clearInterval(timer)
    })
    flowLineBlinkTimers.clear()
    closeFlowInfoWindow()
  }
}

// 调整视图以适应所有标记
const adjustViewToMarkers = () => {
  if (!mapInstance.value || mapStore.visibleMarkers.length === 0) return

  const positions = mapStore.visibleMarkers.map(marker => marker.position)
  mapInstance.value.setFitView(positions.map(([lng, lat]) => new window.AMap.LngLat(lng, lat)))
}

// 监听store变化
watch(() => mapStore.visibleMarkers, () => {
  if (mapInstance.value) {
    renderStationMarkers()
    if (props.fitViewToMarkers) {
      adjustViewToMarkers()
    }
  }
}, { deep: true })

watch(() => mapStore.visibleFlowLines, () => {
  if (mapInstance.value) {
    renderFlowLines()
  }
}, { deep: true })

watch(() => mapStore.mapConfig.showStationMarkers, () => {
  if (mapInstance.value) {
    renderStationMarkers()
  }
})

watch(() => mapStore.mapConfig.showFlowLines, () => {
  if (mapInstance.value) {
    renderFlowLines()
  }
})

const renderFlowStationsFromLines = () => {
  if (!mapInstance.value || !window.AMap) return

  clearAllFlowStations()

  if (!mapStore.mapConfig.showFlowLines) return

  const existingStationIds = new Set(mapStore.visibleMarkers.map(marker => marker.stationId))
  const shouldRenderFlowStations = !mapStore.mapConfig.showStationMarkers

  mapStore.visibleFlowLines.forEach(lineData => {
    if (shouldRenderFlowStations || !existingStationIds.has(lineData.fromStationId)) {
      const marker = createFlowStationMarker(
        lineData.fromPosition,
        lineData.fromStationName,
        lineData.fromStationId
      )
      if (marker) flowStationInstances.value.push(marker)
    }
    if (shouldRenderFlowStations || !existingStationIds.has(lineData.toStationId)) {
      const marker = createFlowStationMarker(
        lineData.toPosition,
        lineData.toStationName,
        lineData.toStationId
      )
      if (marker) flowStationInstances.value.push(marker)
    }
  })
}

const createFlowStationMarker = (
  position: [number, number],
  stationName?: string,
  stationId?: number
) => {
  if (!mapInstance.value || !window.AMap) return null
  const AMap = window.AMap
  const marker = new AMap.Marker({
    position: new AMap.LngLat(position[0], position[1]),
    title: stationName || (stationId ? `站点 ${stationId}` : '站点'),
    offset: new AMap.Pixel(-6, -6),
    content: `
      <div style="
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #ffffff;
        border: 2px solid #1e88e5;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
      "></div>
    `,
  })
  marker.setMap(mapInstance.value)
  return marker
}

const getFlowLineStyle = (lineData: any, isActive: boolean, isDimmed = false) => {
  const baseWidth = lineData.width || Math.max(1, Math.min(2.5, lineData.passengers / 25000))
  const lineColor = lineData.color || '#00aaff'
  const arrowColor = lineData.arrowColor || '#0d47a1'
  const opacity = isDimmed ? 0.15 : (isActive ? 0.9 : 0.6)
  return {
    strokeColor: lineColor,
    strokeWeight: isActive ? baseWidth + 1.2 : baseWidth,
    strokeStyle: 'solid',
    strokeOpacity: opacity,
    zIndex: isActive ? 120 : 100,
    lineJoin: 'round',
    lineCap: 'round',
    showDir: true,
    dirColor: arrowColor,
  }
}

const setActiveFlowLine = (lineId: string) => {
  if (activeFlowLineId.value && activeFlowLineId.value !== lineId && !stickyFlowLineId.value) {
    resetActiveFlowLine(activeFlowLineId.value)
  }

  const target = flowLineInstances.value.find(item => item.id === lineId)
  if (!target) return
  target.line.setOptions(getFlowLineStyle(target.data, true, false))
  activeFlowLineId.value = lineId
}

const resetActiveFlowLine = (lineId: string) => {
  const target = flowLineInstances.value.find(item => item.id === lineId)
  if (!target) return
  target.line.setOptions(getFlowLineStyle(target.data, false, false))
  if (activeFlowLineId.value === lineId) {
    activeFlowLineId.value = null
  }
}

const applyFlowLineStyles = () => {
  flowLineInstances.value.forEach(item => {
    const isFocused = focusedFlowLineId.value === item.id
    const isActive = isFocused || activeFlowLineId.value === item.id || stickyFlowLineId.value === item.id || item.data?.selected
    const isDimmed = !!focusedFlowLineId.value && !isFocused
    item.line.setOptions(getFlowLineStyle(item.data, isActive, isDimmed))
  })
}

const focusFlowLine = (lineId: string | null) => {
  if (!lineId) {
    focusedFlowLineId.value = null
    stickyFlowLineId.value = null
    activeFlowLineId.value = null
    closeFlowInfoWindow()
    applyFlowLineStyles()
    return
  }

  const target = flowLineInstances.value.find(item => item.id === lineId)
  if (!target) return
  focusedFlowLineId.value = lineId
  stickyFlowLineId.value = lineId
  activeFlowLineId.value = lineId
  openFlowInfoWindow(target.data)
  applyFlowLineStyles()
}

const getFlowLineMidpoint = (lineData: any) => {
  const midLng = (lineData.fromPosition[0] + lineData.toPosition[0]) / 2
  const midLat = (lineData.fromPosition[1] + lineData.toPosition[1]) / 2
  return [midLng, midLat]
}

const buildFlowInfoContent = (lineData: any) => {
  const fromName = lineData.fromStationName || `站点 ${lineData.fromStationId}`
  const toName = lineData.toStationName || `站点 ${lineData.toStationId}`
  const passengers = lineData.passengers?.toLocaleString?.() ?? lineData.passengers
  const loadRate = typeof lineData.loadRate === 'number' ? lineData.loadRate : null
  const capacity = typeof lineData.capacity === 'number' ? lineData.capacity : null
  const load = typeof lineData.load === 'number' ? lineData.load : null
  const remaining = capacity !== null && load !== null ? capacity - load : null
  const ratePercent = loadRate !== null ? Math.round(loadRate * 100) : null
  const gauge = ratePercent !== null ? buildGaugeHtml(ratePercent, lineData.color || '#00aaff') : ''
  const bars = capacity !== null && load !== null ? buildSupplyDemandHtml(capacity, load) : ''
  return `
    <div style="
      background: white;
      border-radius: 8px;
      box-shadow: 0 6px 18px rgba(0,0,0,0.18);
      padding: 10px 12px;
      min-width: 200px;
      font-size: 12px;
      color: #2c3e50;
    ">
      <div style="font-weight: 600; margin-bottom: 6px;">线路流向</div>
      <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
        <span style="color: #7f8c8d;">起点</span>
        <span>${fromName}</span>
      </div>
      <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
        <span style="color: #7f8c8d;">终点</span>
        <span>${toName}</span>
      </div>
      <div style="display: flex; justify-content: space-between;">
        <span style="color: #7f8c8d;">客流</span>
        <span>${passengers}</span>
      </div>
      ${ratePercent !== null ? `
      <div style="margin-top: 10px; display: grid; gap: 8px;">
        <div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 12px; align-items: center;">
          ${gauge}
          ${bars}
        </div>
        <div style="display: flex; justify-content: space-between; font-weight: 600;">
          <span>剩余运力</span>
          <span style="color: ${remaining !== null && remaining < 0 ? '#d81b60' : '#2e7d32'};">
            ${remaining !== null ? remaining.toLocaleString() : '--'}
          </span>
        </div>
      </div>
      ` : ''}
    </div>
  `
}

const buildGaugeHtml = (percent: number, color: string) => {
  const clamped = Math.max(0, Math.min(150, percent))
  const radius = 42
  const circumference = Math.PI * radius
  const dash = (clamped / 150) * circumference
  return `
    <div style="display:flex; flex-direction:column; align-items:center; gap:6px;">
      <svg width="110" height="70" viewBox="0 0 110 70">
        <path d="M10,60 A45,45 0 0,1 100,60" stroke="#e0e0e0" stroke-width="10" fill="none" stroke-linecap="round" />
        <path d="M10,60 A45,45 0 0,1 100,60"
          stroke="${color}"
          stroke-width="10"
          fill="none"
          stroke-linecap="round"
          stroke-dasharray="${dash} ${circumference}"
        />
        <text x="55" y="55" text-anchor="middle" font-size="16" fill="#2c3e50" font-weight="600">${clamped}%</text>
      </svg>
      <div style="font-size: 11px; color: #7f8c8d;">负载率</div>
    </div>
  `
}

const buildSupplyDemandHtml = (capacity: number, load: number) => {
  const maxValue = Math.max(capacity, load, 1)
  const capacityPercent = Math.round((capacity / maxValue) * 100)
  const loadPercent = Math.round((load / maxValue) * 100)
  return `
    <div style="display:flex; flex-direction:column; gap:6px;">
      <div style="font-size: 11px; color: #7f8c8d; font-weight:600;">供需关系</div>
      <div style="display:flex; align-items:center; gap:6px;">
        <div style="width: 80px; height: 8px; background:#e0e0e0; border-radius: 999px; overflow:hidden;">
          <div style="width:${capacityPercent}%; height:100%; background:#409eff;"></div>
        </div>
        <span style="font-size:11px;">运力 ${capacity.toLocaleString()}</span>
      </div>
      <div style="display:flex; align-items:center; gap:6px;">
        <div style="width: 80px; height: 8px; background:#e0e0e0; border-radius: 999px; overflow:hidden;">
          <div style="width:${loadPercent}%; height:100%; background:#f56c6c;"></div>
        </div>
        <span style="font-size:11px;">客流 ${load.toLocaleString()}</span>
      </div>
    </div>
  `
}

const openFlowInfoWindow = (lineData: any, lnglat?: any) => {
  if (!mapInstance.value || !window.AMap) return
  const AMap = window.AMap
  if (!flowInfoWindow.value) {
    flowInfoWindow.value = new AMap.InfoWindow({
      isCustom: true,
      autoMove: true,
      offset: new AMap.Pixel(0, -12),
    })
  }
  const content = buildFlowInfoContent(lineData)
  flowInfoWindow.value.setContent(content)
  const position = lnglat || new AMap.LngLat(...getFlowLineMidpoint(lineData))
  flowInfoWindow.value.open(mapInstance.value, position)
}

const closeFlowInfoWindow = () => {
  if (flowInfoWindow.value) {
    flowInfoWindow.value.close()
  }
}

watch(() => mapStore.mapConfig.mapType, (newType) => {
  if (mapInstance.value) {
    mapInstance.value.setMapStyle(`amap://styles/${newType}`)
  }
})

watch(() => mapStore.viewState, (newState) => {
  if (mapInstance.value) {
    mapInstance.value.setCenter(newState.center)
    mapInstance.value.setZoom(newState.zoom)
  }
}, { deep: true })

// 生命周期
onMounted(() => {
  initMap()
})

onUnmounted(() => {
  // 清理地图实例
  if (mapInstance.value) {
    clearAllFlowLines()
    mapInstance.value.destroy()
    mapInstance.value = null
  }
})

// 暴露方法给父组件
defineExpose({
  getMapInstance: () => mapInstance.value,
  adjustViewToMarkers,
  updateMarkers: renderStationMarkers,
  updateFlowLines: renderFlowLines,
  focusFlowLine,
})
</script>

<template>
  <div :id="mapId" :class="['gaode-map', className]" :style="mapStyle">
    <!-- 地图加载状态 -->
    <div v-if="mapLoading" class="map-loading">
      <div class="loading-spinner"></div>
      <div class="loading-text">地图加载中...</div>
    </div>

    <!-- 地图错误状态 -->
    <div v-else-if="mapError" class="map-error">
      <div class="error-icon">⚠️</div>
      <div class="error-text">{{ mapError }}</div>
      <button class="retry-button" @click="initMap">重试</button>
    </div>

    <!-- 地图容器 -->
    <div class="map-container"></div>
  </div>
</template>

<style scoped>
.gaode-map {
  position: relative;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
}

.gaode-map:hover {
  box-shadow: var(--shadow-lg);
}

.map-loading,
.map-error {
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

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid var(--color-bg-tertiary);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite;
  margin-bottom: var(--spacing-4);
}

.loading-text {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
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

.map-container {
  width: 100%;
  height: 100%;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
