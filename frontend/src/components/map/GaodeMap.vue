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
}>()

// Store
const mapStore = useMapStore()

// 状态
const mapInstance = ref<any>(null)
const mapLoading = ref(false)
const mapError = ref<string | null>(null)

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

  // 添加新标记
  mapStore.visibleMarkers.forEach(markerData => {
    createStationMarker(markerData)
  })
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

  // 保存标记引用（实际应用中可能需要管理标记引用）
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
  if (!mapInstance.value || !mapStore.mapConfig.showFlowLines) return

  // 清除现有流向线
  clearAllFlowLines()

  // 添加新流向线
  mapStore.visibleFlowLines.forEach(lineData => {
    createFlowLine(lineData)
  })
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
    strokeColor: lineData.color || '#00aaff',
    strokeWeight: lineData.width || Math.max(1, Math.min(8, lineData.passengers / 5000)),
    strokeStyle: lineData.dashArray || 'solid',
    strokeOpacity: 0.7,
  })

  line.setMap(mapInstance.value)
}

// 清除所有标记
const clearAllMarkers = () => {
  // 实际应用中需要管理标记引用并清除
  if (mapInstance.value) {
    mapInstance.value.clearMap()
  }
}

// 清除所有流向线
const clearAllFlowLines = () => {
  // 流向线清理逻辑
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