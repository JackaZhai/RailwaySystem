/**
 * 铁路数据相关类型定义
 * 对应后端4种核心数据表
 */

// 1. 站点表 (Station)
export interface Station {
  id: number
  travel_area_id: number | null
  name: string
  code: number | null
  telecode: string
  shortname: string | null
  created_at: string
  updated_at: string
}

// 2. 列车表 (Train)
export interface Train {
  id: number
  code: string
  capacity: number
  created_at: string
  updated_at: string
}

// 3. 线路表 (Route)
export interface Route {
  id: number
  code: number
  name: string | null
  created_at: string
  updated_at: string
}

// 4. 客运记录表 (PassengerFlow) - 核心事实表
export interface PassengerFlow {
  id: number
  serial_number: number | null
  route: number  // 外键，对应Route.id
  train: number  // 外键，对应Train.id
  station: number  // 外键，对应Station.id
  route_station_sequence: number | null
  operation_date: string  // YYYY-MM-DD
  arrival_time: string | null  // HH:MM:SS
  departure_time: string | null  // HH:MM:SS
  passengers_in: number
  passengers_out: number
  ticket_price: string | null  // Decimal as string
  start_station_telecode: string | null
  end_station_telecode: string | null
  revenue: string | null  // Decimal as string
  created_at: string
  updated_at: string
  // 以下字段来自序列化器，不是模型直接字段
  route_code?: number
  train_code?: string
  station_name?: string
  station_telecode?: string
  total_passengers?: number
}

// 分页响应通用接口
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}