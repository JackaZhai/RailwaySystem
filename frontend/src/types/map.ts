/**
 * 地图相关类型定义
 */

export interface MapConfig {
  center: [number, number] // [lng, lat]
  zoom: number
  minZoom: number
  maxZoom: number
  mapType: 'normal' | 'satellite' | 'roadnet'
  showTraffic: boolean
  showLabels: boolean
  showStationMarkers: boolean
  showFlowLines: boolean
  showHeatmap: boolean
}

export interface StationMarker {
  stationId: number
  stationName: string
  position: [number, number] // [lng, lat]
  size: number // 标记大小
  color?: string
  passengerCount: number
  data?: Record<string, any>
}

export interface FlowLine {
  id: string
  fromStationId: number
  toStationId: number
  fromPosition: [number, number]
  toPosition: [number, number]
  passengers: number
  color?: string
  width?: number
  dashArray?: string
}

export interface MapViewState {
  center: [number, number]
  zoom: number
  bounds: [[number, number], [number, number]] | null // [[west, south], [east, north]]
}

export interface HeatmapPoint {
  lat: number
  lng: number
  intensity: number
}

export interface MapBounds {
  north: number
  south: number
  east: number
  west: number
}

export interface MapEvent {
  type: 'click' | 'move' | 'zoom' | 'station_select' | 'station_hover'
  data: any
  timestamp: Date
}