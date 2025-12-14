import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MapConfig, StationMarker, FlowLine, MapViewState } from '@/types/map'

/**
 * 地图状态管理
 */
export const useMapStore = defineStore('map', () => {
  // 状态
  const mapConfig = ref<MapConfig>({
    center: [30.6595, 104.0659], // 成都坐标
    zoom: 12,
    minZoom: 8,
    maxZoom: 18,
    mapType: 'normal', // normal, satellite, roadnet
    showTraffic: false,
    showLabels: true,
    showStationMarkers: true,
    showFlowLines: true,
    showHeatmap: false,
  })

  const stationMarkers = ref<StationMarker[]>([])
  const flowLines = ref<FlowLine[]>([])
  const selectedStation = ref<number | null>(null)
  const hoveredStation = ref<number | null>(null)
  const viewState = ref<MapViewState>({
    center: mapConfig.value.center,
    zoom: mapConfig.value.zoom,
    bounds: null,
  })
  const isLoading = ref(false)

  // 计算属性
  const selectedMarker = computed(() => {
    if (!selectedStation.value) return null
    return stationMarkers.value.find(marker => marker.stationId === selectedStation.value)
  })

  const hoveredMarker = computed(() => {
    if (!hoveredStation.value) return null
    return stationMarkers.value.find(marker => marker.stationId === hoveredStation.value)
  })

  const visibleMarkers = computed(() => {
    return stationMarkers.value.filter(marker => {
      // 可以根据视图状态过滤标记
      if (!viewState.value.bounds) return true

      const [lng, lat] = marker.position
      const [[west, south], [east, north]] = viewState.value.bounds

      return lng >= west && lng <= east && lat >= south && lat <= north
    })
  })

  const visibleFlowLines = computed(() => {
    if (!mapConfig.value.showFlowLines) return []
    // 可以根据视图状态过滤流向线
    return flowLines.value
  })

  // 操作
  const updateMapConfig = (config: Partial<MapConfig>) => {
    mapConfig.value = { ...mapConfig.value, ...config }
    // 保存到本地存储
    localStorage.setItem('map_config', JSON.stringify(mapConfig.value))
  }

  const setStationMarkers = (markers: StationMarker[]) => {
    stationMarkers.value = markers
  }

  const addStationMarker = (marker: StationMarker) => {
    stationMarkers.value.push(marker)
  }

  const updateStationMarker = (stationId: number, updates: Partial<StationMarker>) => {
    const index = stationMarkers.value.findIndex(marker => marker.stationId === stationId)
    if (index !== -1) {
      stationMarkers.value[index] = { ...stationMarkers.value[index], ...updates } as StationMarker
    }
  }

  const removeStationMarker = (stationId: number) => {
    const index = stationMarkers.value.findIndex(marker => marker.stationId === stationId)
    if (index !== -1) {
      stationMarkers.value.splice(index, 1)
    }
  }

  const setFlowLines = (lines: FlowLine[]) => {
    flowLines.value = lines
  }

  const addFlowLine = (line: FlowLine) => {
    flowLines.value.push(line)
  }

  const clearFlowLines = () => {
    flowLines.value = []
  }

  const selectStation = (stationId: number | null) => {
    selectedStation.value = stationId
  }

  const hoverStation = (stationId: number | null) => {
    hoveredStation.value = stationId
  }

  const updateViewState = (state: Partial<MapViewState>) => {
    viewState.value = { ...viewState.value, ...state }
  }

  const zoomToStation = (stationId: number) => {
    const marker = stationMarkers.value.find(m => m.stationId === stationId)
    if (marker) {
      viewState.value.center = marker.position
      viewState.value.zoom = 15
      selectStation(stationId)
    }
  }

  const zoomToBounds = (bounds: [[number, number], [number, number]]) => {
    viewState.value.bounds = bounds
    // 计算合适的中心点和缩放级别
    const [[west, south], [east, north]] = bounds
    viewState.value.center = [(west + east) / 2, (south + north) / 2]
    viewState.value.zoom = 12 // 简化处理，实际应该根据bounds计算
  }

  const resetView = () => {
    viewState.value.center = mapConfig.value.center
    viewState.value.zoom = mapConfig.value.zoom
    viewState.value.bounds = null
    selectedStation.value = null
    hoveredStation.value = null
  }

  const toggleMapType = () => {
    const types: MapConfig['mapType'][] = ['normal', 'satellite', 'roadnet']
    const currentIndex = types.indexOf(mapConfig.value.mapType)
    const nextIndex = (currentIndex + 1) % types.length
    updateMapConfig({ mapType: types[nextIndex] })
  }

  const toggleTraffic = () => {
    updateMapConfig({ showTraffic: !mapConfig.value.showTraffic })
  }

  const toggleLabels = () => {
    updateMapConfig({ showLabels: !mapConfig.value.showLabels })
  }

  const toggleStationMarkers = () => {
    updateMapConfig({ showStationMarkers: !mapConfig.value.showStationMarkers })
  }

  const toggleFlowLines = () => {
    updateMapConfig({ showFlowLines: !mapConfig.value.showFlowLines })
  }

  const toggleHeatmap = () => {
    updateMapConfig({ showHeatmap: !mapConfig.value.showHeatmap })
  }

  const loadMapConfig = () => {
    const saved = localStorage.getItem('map_config')
    if (saved) {
      try {
        const config = JSON.parse(saved)
        mapConfig.value = { ...mapConfig.value, ...config }
      } catch {
        // 忽略解析错误
      }
    }
  }

  // 根据客流数据更新标记大小
  const updateMarkersByPassengerData = (passengerData: Array<{ stationId: number; passengers: number }>) => {
    if (!passengerData.length) return

    // 找到最大客流量用于归一化
    const maxPassengers = Math.max(...passengerData.map(d => d.passengers))

    stationMarkers.value.forEach(marker => {
      const data = passengerData.find(d => d.stationId === marker.stationId)
      if (data) {
        // 根据客流量调整标记大小 (基础大小 + 比例缩放)
        const sizeScale = 0.5 + (data.passengers / maxPassengers) * 1.5
        marker.size = Math.max(20, Math.min(60, sizeScale * 30))
        marker.passengerCount = data.passengers
      }
    })
  }

  return {
    // 状态
    mapConfig,
    stationMarkers,
    flowLines,
    selectedStation,
    hoveredStation,
    viewState,
    isLoading,

    // 计算属性
    selectedMarker,
    hoveredMarker,
    visibleMarkers,
    visibleFlowLines,

    // 操作
    updateMapConfig,
    setStationMarkers,
    addStationMarker,
    updateStationMarker,
    removeStationMarker,
    setFlowLines,
    addFlowLine,
    clearFlowLines,
    selectStation,
    hoverStation,
    updateViewState,
    zoomToStation,
    zoomToBounds,
    resetView,
    toggleMapType,
    toggleTraffic,
    toggleLabels,
    toggleStationMarkers,
    toggleFlowLines,
    toggleHeatmap,
    loadMapConfig,
    updateMarkersByPassengerData,
  }
})