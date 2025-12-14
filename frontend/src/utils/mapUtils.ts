/**
 * 地图工具函数
 */

import type { StationMarker, FlowLine } from '@/types/map'

/**
 * 计算标记大小基于客流量
 * @param passengerCount 客流量
 * @param minSize 最小大小
 * @param maxSize 最大大小
 * @param maxPassengers 最大客流量（用于归一化）
 * @returns 标记大小
 */
export function calculateMarkerSize(
  passengerCount: number,
  minSize = 20,
  maxSize = 60,
  maxPassengers?: number
): number {
  if (!maxPassengers) {
    maxPassengers = passengerCount * 2 // 简单估计
  }

  const normalized = Math.min(1, passengerCount / maxPassengers)
  const size = minSize + normalized * (maxSize - minSize)
  return Math.round(size)
}

/**
 * 计算标记颜色基于客流量
 * @param passengerCount 客流量
 * @param maxPassengers 最大客流量
 * @returns 颜色值
 */
export function calculateMarkerColor(
  passengerCount: number,
  maxPassengers: number
): string {
  const ratio = passengerCount / maxPassengers

  if (ratio < 0.3) return '#4caf50' // 绿色 - 低客流
  if (ratio < 0.6) return '#ff9800' // 橙色 - 中等客流
  return '#f44336' // 红色 - 高客流
}

/**
 * 生成流向线数据
 * @param fromStation 起点站
 * @param toStation 终点站
 * @param passengerCount 客流量
 * @returns FlowLine对象
 */
export function createFlowLine(
  fromStation: { id: number; position: [number, number] },
  toStation: { id: number; position: [number, number] },
  passengerCount: number
): FlowLine {
  return {
    id: `flow-${fromStation.id}-${toStation.id}`,
    fromStationId: fromStation.id,
    toStationId: toStation.id,
    fromPosition: fromStation.position,
    toPosition: toStation.position,
    passengers: passengerCount,
    color: '#00aaff',
    width: Math.max(1, Math.min(8, passengerCount / 5000)),
    dashArray: '5,5',
  }
}

/**
 * 计算两点间距离（公里）
 * @param lat1 纬度1
 * @param lng1 经度1
 * @param lat2 纬度2
 * @param lng2 经度2
 * @returns 距离（公里）
 */
export function calculateDistance(
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number
): number {
  const R = 6371 // 地球半径（公里）
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lng2 - lng1)
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

/**
 * 度数转弧度
 */
function toRad(degrees: number): number {
  return degrees * (Math.PI / 180)
}

/**
 * 生成热力图数据
 * @param stations 车站列表
 * @param passengerData 客流数据
 * @returns 热力图数据点
 */
export function generateHeatmapData(
  stations: Array<{ position: [number, number] }>,
  passengerData: number[]
): Array<{ lat: number; lng: number; intensity: number }> {
  return stations.map((station, index) => ({
    lat: station.position[1],
    lng: station.position[0],
    intensity: passengerData[index] || 0,
  }))
}

/**
 * 计算地图边界以适应所有标记
 * @param markers 标记列表
 * @returns 边界 [[west, south], [east, north]]
 */
export function calculateBounds(
  markers: StationMarker[]
): [[number, number], [number, number]] | null {
  if (markers.length === 0) return null

  let west = Infinity
  let east = -Infinity
  let south = Infinity
  let north = -Infinity

  markers.forEach(marker => {
    const [lng, lat] = marker.position
    west = Math.min(west, lng)
    east = Math.max(east, lng)
    south = Math.min(south, lat)
    north = Math.max(north, lat)
  })

  // 添加一些边距
  const padding = 0.01
  west -= padding
  east += padding
  south -= padding
  north += padding

  return [[west, south], [east, north]]
}

/**
 * 计算地图中心点
 * @param markers 标记列表
 * @returns 中心点 [lng, lat]
 */
export function calculateCenter(markers: StationMarker[]): [number, number] {
  if (markers.length === 0) return [104.0659, 30.6595] // 默认成都

  let totalLng = 0
  let totalLat = 0

  markers.forEach(marker => {
    const [lng, lat] = marker.position
    totalLng += lng
    totalLat += lat
  })

  return [totalLng / markers.length, totalLat / markers.length]
}

/**
 * 根据缩放级别计算标记聚类
 * @param markers 标记列表
 * @param zoom 缩放级别
 * @param clusterDistance 聚类距离（像素）
 * @returns 聚类后的标记
 */
export function clusterMarkers(
  markers: StationMarker[],
  zoom: number,
  _clusterDistance = 50
): StationMarker[] {
  if (zoom >= 14 || markers.length <= 10) {
    return markers // 高缩放级别或标记较少时不需要聚类
  }

  // 简化的聚类算法
  const clustered: StationMarker[] = []
  const clusteredIndexes = new Set<number>()

  for (let i = 0; i < markers.length; i++) {
    if (clusteredIndexes.has(i)) continue

    const cluster = [markers[i]!]
    clusteredIndexes.add(i)

    for (let j = i + 1; j < markers.length; j++) {
      if (clusteredIndexes.has(j)) continue

      // 计算标记间的距离（简化处理）
      const [lng1, lat1] = markers[i]!.position
      const [lng2, lat2] = markers[j]!.position
      const distance = Math.sqrt(Math.pow(lng2 - lng1, 2) + Math.pow(lat2 - lat1, 2))

      // 根据缩放级别调整聚类阈值
      const threshold = 0.1 / Math.pow(2, zoom - 10)

      if (distance < threshold) {
        cluster.push(markers[j]!)
        clusteredIndexes.add(j)
      }
    }

    if (cluster.length === 1) {
      clustered.push(markers[i]!)
    } else {
      // 创建聚类标记
      const totalPassengers = (cluster as StationMarker[]).reduce((sum, marker) => sum + marker.passengerCount, 0)
      const [centerLng, centerLat] = calculateCenter(cluster as StationMarker[])

      clustered.push({
        stationId: cluster[0]!.stationId, // 使用第一个标记的ID
        stationName: `${cluster.length}个站点`,
        position: [centerLng, centerLat],
        size: calculateMarkerSize(totalPassengers),
        passengerCount: totalPassengers,
        data: {
          isCluster: true,
          originalMarkers: cluster,
          count: cluster.length,
        },
      })
    }
  }

  return clustered
}

/**
 * 格式化坐标显示
 * @param lng 经度
 * @param lat 纬度
 * @param precision 精度
 * @returns 格式化后的字符串
 */
export function formatCoordinate(lng: number, lat: number, precision = 4): string {
  const lngStr = lng.toFixed(precision)
  const latStr = lat.toFixed(precision)
  return `${latStr}°N, ${lngStr}°E`
}

/**
 * 检查是否在中国境内
 * @param lng 经度
 * @param lat 纬度
 * @returns 是否在中国境内
 */
export function isInChina(lng: number, lat: number): boolean {
  // 中国大致边界
  const chinaBounds = {
    west: 73.66,  // 新疆最西
    east: 135.05, // 黑龙江最东
    south: 18.16, // 曾母暗沙
    north: 53.55, // 漠河
  }

  return (
    lng >= chinaBounds.west &&
    lng <= chinaBounds.east &&
    lat >= chinaBounds.south &&
    lat <= chinaBounds.north
  )
}