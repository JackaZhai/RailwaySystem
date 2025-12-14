/**
 * 铁路数据相关类型定义
 */

export interface PassengerRecord {
  id: number
  timestamp: Date
  stationId: number
  stationName: string
  lineId: number
  lineName: string
  direction: 'inbound' | 'outbound' | 'both'
  passengerCount: number
  passengerType?: 'adult' | 'child' | 'senior'
  ticketType?: string
  fare?: number
  metadata?: Record<string, any>
}

export interface Station {
  id: number
  name: string
  code: string
  telecode: string
  shortName: string
  type: 'high_speed' | 'regular' | 'junction'
  location: {
    lat: number
    lng: number
  }
  city: string
  province: string
  openingYear?: number
  platformCount?: number
  status: 'active' | 'inactive' | 'under_construction'
}

export interface Train {
  id: number
  code: string
  name: string
  type: 'G' | 'D' | 'C' | 'Z' | 'T' | 'K'
  capacity: number
  operator: string
  serviceStatus: 'active' | 'maintenance' | 'retired'
  manufacturer?: string
  commissioningYear?: number
}

export interface Route {
  id: number
  code: string
  name: string
  startStationId: number
  endStationId: number
  distance: number // 公里
  travelTime: number // 分钟
  stationSequence: number[]
  frequency: number // 每天班次
  operator: string
  status: 'active' | 'suspended' | 'planned'
}

export interface LineLoad {
  lineId: number
  lineName: string
  date: Date
  passengerCount: number
  loadFactor: number // 负载率 (0-1)
  averageSpeed?: number
  delayRate?: number
}

export interface StationMetrics {
  stationId: number
  stationName: string
  date: Date
  passengerIn: number
  passengerOut: number
  transferCount: number
  occupancyRate: number
  serviceQuality: number // 1-5
}