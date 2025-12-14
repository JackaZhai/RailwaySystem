import axios from 'axios'

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// 数据类型定义
export interface TimeRange {
  startDate: string
  endDate: string
  rangeType: 'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom'
}

export interface KpiData {
  totalPassengers: number
  totalTrains: number
  busyStations: number
  totalRevenue: number
  trends: {
    totalPassengers: number
    totalTrains: number
    busyStations: number
    totalRevenue: number
  }
}

export interface Station {
  id: number
  name: string
  code: string
  latitude: number
  longitude: number
  todayPassengers: number
  totalPassengers: number
  occupancyRate: number
  departures: number
  arrivals: number
  delayRate: number
  connectedLines: string[]
}

export interface Line {
  id: number
  name: string
  code: string
  occupancyRate: number
  loadRate: number
  efficiency: number
  industryAverage: number
  trend: number
  status: 'high' | 'medium' | 'low'
}

export interface HeatMapData {
  stations: string[]
  times: string[]
  data: number[][]
}

export interface FlowData {
  fromStationId: number
  toStationId: number
  passengerCount: number
  intensity: 'high' | 'medium' | 'low'
}

export interface TrendData {
  time: string
  total: number
  inbound: number
  outbound: number
}

export interface TimePeriodData {
  id: number
  name: string
  time: string
  passengers: number
  percentage: number
  trains: number
}

export interface TrainRecord {
  id: number
  code: string
  type: string
  departureStation: string
  arrivalStation: string
  departureTime: string
  arrivalTime: string
  occupancy: number
  status: 'running' | 'scheduled' | 'delayed' | 'cancelled'
  statusText: string
}

// 数据管理相关接口
export interface DataRecord {
  id: number
  timestamp: string
  stationId: number
  stationName: string
  lineId: number
  lineName: string
  passengersIn: number
  passengersOut: number
  direction: 'inbound' | 'outbound' | 'both'
  metadata?: Record<string, any>
  createdAt: string
  updatedAt: string
}

export interface DataUploadResponse {
  success: boolean
  message: string
  recordsProcessed: number
  recordsFailed: number
  recordCount?: number
  duplicatesRemoved?: number
  invalidRemoved?: number
  errors?: string[]
  fileInfo?: {
    filename: string
    size: number
    type: string
  }
  file?: File
}

export interface DataQueryParams {
  page?: number
  pageSize?: number
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
  startDate?: string
  endDate?: string
  stationIds?: number[]
  lineIds?: number[]
  search?: string
}

export interface DataQueryResult {
  data: DataRecord[]
  total: number
  page: number
  pageSize: number
  totalPages: number
  filters: DataQueryParams
}

export interface DataValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
  recordCount: number
  fieldStats: Record<string, {
    count: number
    missing: number
    unique: number
    min?: number
    max?: number
    avg?: number
  }>
}

export interface DataCleanupResult {
  success: boolean
  message: string
  recordsDeleted: number
  recordsUpdated: number
  duplicatesRemoved: number
  invalidRecordsRemoved: number
  recordsProcessed?: number
  missingFilled?: number
  formatFixed?: number
  inconsistenciesFixed?: number
}

export interface DataStats {
  totalRecords: number
  stations: number
  trains?: number
  lines?: number
  dateRange: string | { minDate: string; maxDate: string }
  lastUpdated?: string
  recentUploads?: Array<{
    filename: string
    uploadedAt: string
    records: number
  }>
}

export interface ValidationIssue {
  row: number
  field: string
  issue: string
  suggestion: string
}

export interface DataValidationDetailedResult {
  totalRecords: number
  validRecords: number
  duplicateRecords: number
  invalidRecords: number
  missingFields: number
  formatErrors: number
  issues: ValidationIssue[]
}

// API接口定义
export const apiService = {
  // KPI数据
  getKpiData: (timeRange: TimeRange) => {
    return api.get<KpiData>('/analytics/kpi/', { params: timeRange })
  },

  // 站点数据
  getStations: (timeRange: TimeRange) => {
    return api.get<Station[]>('/analytics/stations/', { params: timeRange })
  },

  // 线路数据
  getLines: (timeRange: TimeRange) => {
    return api.get<Line[]>('/analytics/lines/', { params: timeRange })
  },

  // 热力图数据
  getHeatMapData: (timeRange: TimeRange) => {
    return api.get<HeatMapData>('/analytics/heatmap/', { params: timeRange })
  },

  // 流向图数据
  getFlowData: (timeRange: TimeRange) => {
    return api.get<FlowData[]>('/analytics/flow/', { params: timeRange })
  },

  // 趋势数据
  getTrendData: (timeRange: TimeRange, frequency: 'hourly' | 'daily' | 'weekly' | 'monthly') => {
    return api.get<TrendData[]>('/analytics/trend/', {
      params: { ...timeRange, frequency }
    })
  },

  // 时段数据
  getTimePeriodData: (timeRange: TimeRange) => {
    return api.get<TimePeriodData[]>('/analytics/time-periods/', { params: timeRange })
  },

  // 实时列车数据
  getRecentTrains: (timeRange: TimeRange, page: number = 1, pageSize: number = 10) => {
    return api.get<{
      data: TrainRecord[]
      total: number
      page: number
      pageSize: number
      totalPages: number
    }>('/analytics/trains/', {
      params: { ...timeRange, page, page_size: pageSize }
    })
  },

  // 数据刷新
  refreshData: (timeRange: TimeRange) => {
    return api.post('/analytics/refresh/', timeRange)
  },

  // 数据导出
  exportData: (timeRange: TimeRange, format: 'csv' | 'excel' | 'json') => {
    return api.get('/analytics/export/', {
      params: { ...timeRange, format },
      responseType: 'blob'
    })
  },

  // 预测数据
  getForecast: (timeRange: TimeRange, days: number = 7) => {
    return api.get('/analytics/forecast/', {
      params: { ...timeRange, days }
    })
  },

  // 数据管理接口
  // 数据上传
  uploadData: (file: File, options?: { validateOnly?: boolean }) => {
    const formData = new FormData()
    formData.append('file', file)
    if (options?.validateOnly) {
      formData.append('validate_only', 'true')
    }
    return api.post<DataUploadResponse>('/data/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 数据查询
  getDataRecords: (params: DataQueryParams) => {
    return api.get<DataQueryResult>('/data/records/', { params })
  },

  // 数据验证
  validateData: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post<DataValidationResult>('/data/validate/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 数据清理
  cleanupData: (options: {
    removeDuplicates?: boolean
    removeInvalid?: boolean
    dateRange?: { startDate: string; endDate: string }
  }) => {
    return api.post<DataCleanupResult>('/data/cleanup/', options)
  },

  // 批量删除
  deleteDataRecords: (recordIds: number[]) => {
    return api.delete('/data/records/batch/', { data: { ids: recordIds } })
  },

  // 数据导出
  exportDataRecords: (params: DataQueryParams, format: 'csv' | 'excel' | 'json') => {
    return api.get('/data/export/', {
      params: { ...params, format },
      responseType: 'blob'
    })
  },

  // 数据统计
  getDataStats: () => {
    return api.get<{
      totalRecords: number
      stations: number
      lines: number
      dateRange: { minDate: string; maxDate: string }
      recentUploads: Array<{
        filename: string
        uploadedAt: string
        records: number
      }>
    }>('/data/stats/')
  }
}

// 模拟数据服务（用于开发阶段）
export const mockService = {
  getKpiData: async (timeRange: TimeRange): Promise<KpiData> => {
    await new Promise(resolve => setTimeout(resolve, 500)) // 模拟网络延迟

    const basePassengers = 1245678
    const baseTrains = 1234
    const baseStations = 156
    const baseRevenue = 8765432

    // 根据时间范围调整数据
    const factor = timeRange.rangeType === 'today' ? 1 :
                   timeRange.rangeType === 'week' ? 7 :
                   timeRange.rangeType === 'month' ? 30 : 1

    return {
      totalPassengers: Math.round(basePassengers * factor),
      totalTrains: Math.round(baseTrains * factor),
      busyStations: Math.round(baseStations * (factor > 1 ? 1 : factor)),
      totalRevenue: Math.round(baseRevenue * factor),
      trends: {
        totalPassengers: 12.5,
        totalTrains: -3.2,
        busyStations: 5.8,
        totalRevenue: 18.3
      }
    }
  },

  getStations: async (timeRange: TimeRange): Promise<Station[]> => {
    // 模拟服务中timeRange参数未使用，但在真实API中会使用
    await new Promise(resolve => setTimeout(resolve, 300))

    return [
      {
        id: 1,
        name: '成都东站',
        code: 'CDW',
        latitude: 30.6595,
        longitude: 104.0659,
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
        latitude: 29.6075,
        longitude: 106.5475,
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
        latitude: 29.5875,
        longitude: 105.0675,
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
        latitude: 30.1275,
        longitude: 104.6575,
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
        latitude: 29.3575,
        longitude: 105.9375,
        todayPassengers: 43210,
        totalPassengers: 987654,
        occupancyRate: 72,
        departures: 65,
        arrivals: 68,
        delayRate: 98,
        connectedLines: ['成渝高铁']
      }
    ]
  },

  getLines: async (timeRange: TimeRange): Promise<Line[]> => {
    // 模拟服务中timeRange参数未使用，但在真实API中会使用
    await new Promise(resolve => setTimeout(resolve, 300))

    return [
      {
        id: 1,
        name: '成渝高铁',
        code: 'CYG',
        occupancyRate: 92,
        loadRate: 85,
        efficiency: 88,
        industryAverage: 75,
        trend: 15.2,
        status: 'high'
      },
      {
        id: 2,
        name: '渝贵铁路',
        code: 'YGR',
        occupancyRate: 78,
        loadRate: 72,
        efficiency: 75,
        industryAverage: 70,
        trend: 8.7,
        status: 'medium'
      },
      {
        id: 3,
        name: '成贵高铁',
        code: 'CGG',
        occupancyRate: 65,
        loadRate: 58,
        efficiency: 62,
        industryAverage: 65,
        trend: 6.3,
        status: 'medium'
      },
      {
        id: 4,
        name: '西成高铁',
        code: 'XCG',
        occupancyRate: 45,
        loadRate: 42,
        efficiency: 44,
        industryAverage: 60,
        trend: -2.1,
        status: 'low'
      },
      {
        id: 5,
        name: '渝万铁路',
        code: 'YWR',
        occupancyRate: 82,
        loadRate: 76,
        efficiency: 79,
        industryAverage: 68,
        trend: 11.4,
        status: 'high'
      }
    ]
  },

  getTrendData: async (timeRange: TimeRange, frequency: 'hourly' | 'daily' | 'weekly' | 'monthly'): Promise<TrendData[]> => {
    // 模拟服务中timeRange参数未使用，但在真实API中会使用
    await new Promise(resolve => setTimeout(resolve, 400))

    const count = frequency === 'hourly' ? 24 :
                  frequency === 'daily' ? 7 :
                  frequency === 'weekly' ? 4 : 12

    const data: TrendData[] = []
    const baseTotal = 5000
    const baseInbound = 3000
    const baseOutbound = 2000

    for (let i = 0; i < count; i++) {
      const timeFactor = Math.sin(i / count * Math.PI) * 0.5 + 0.5
      const dayFactor = i < 2 ? 0.3 : i < 4 ? 0.7 : 1.0
      const randomFactor = 0.8 + Math.random() * 0.4

      const total = Math.round(baseTotal * timeFactor * dayFactor * randomFactor)
      const inbound = Math.round(baseInbound * timeFactor * dayFactor * randomFactor * 0.9)
      const outbound = Math.round(baseOutbound * timeFactor * dayFactor * randomFactor * 1.1)

      let time = ''
      switch (frequency) {
        case 'hourly':
          time = `${i.toString().padStart(2, '0')}:00`
          break
        case 'daily':
          const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
          time = days[i % 7]
          break
        case 'weekly':
          time = `第${i + 1}周`
          break
        case 'monthly':
          time = `${i + 1}月`
          break
      }

      data.push({
        time,
        total,
        inbound,
        outbound
      })
    }

    return data
  },

  // 数据管理模拟接口
  uploadData: async (file: File, options?: { validateOnly?: boolean }): Promise<DataUploadResponse> => {
    await new Promise(resolve => setTimeout(resolve, 1500))

    const filename = file.name
    const size = file.size
    const recordsProcessed = Math.floor(Math.random() * 1000) + 500
    const recordsFailed = Math.floor(Math.random() * 10)

    return {
      success: true,
      message: options?.validateOnly
        ? `数据验证完成，${recordsProcessed}条记录有效，${recordsFailed}条记录有问题`
        : `数据上传成功，处理了${recordsProcessed}条记录`,
      recordsProcessed,
      recordsFailed,
      errors: recordsFailed > 0 ? [
        `第${Math.floor(Math.random() * 100) + 1}行：时间格式错误`,
        `第${Math.floor(Math.random() * 100) + 50}行：站点ID不存在`
      ] : undefined,
      fileInfo: {
        filename,
        size,
        type: file.type
      }
    }
  },

  getDataRecords: async (params: DataQueryParams): Promise<DataQueryResult> => {
    await new Promise(resolve => setTimeout(resolve, 800))

    const page = params.page || 1
    const pageSize = params.pageSize || 20
    const total = 1245
    const totalPages = Math.ceil(total / pageSize)

    // 生成模拟数据
    const data: DataRecord[] = []
    const stations = ['成都东站', '重庆北站', '内江北站', '资阳北站', '永川东站']
    const lines = ['成渝高铁', '渝贵铁路', '成贵高铁', '西成高铁', '渝万铁路']

    for (let i = 0; i < pageSize; i++) {
      const id = (page - 1) * pageSize + i + 1
      const stationIndex = i % stations.length
      const lineIndex = i % lines.length
      const date = new Date()
      date.setDate(date.getDate() - Math.floor(Math.random() * 30))

      data.push({
        id,
        timestamp: date.toISOString(),
        stationId: stationIndex + 1,
        stationName: stations[stationIndex],
        lineId: lineIndex + 1,
        lineName: lines[lineIndex],
        passengersIn: Math.floor(Math.random() * 500) + 100,
        passengersOut: Math.floor(Math.random() * 500) + 100,
        direction: Math.random() > 0.5 ? 'inbound' : 'outbound',
        createdAt: date.toISOString(),
        updatedAt: date.toISOString()
      })
    }

    return {
      data,
      total,
      page,
      pageSize,
      totalPages,
      filters: params
    }
  },

  validateData: async (file: File): Promise<DataValidationResult> => {
    await new Promise(resolve => setTimeout(resolve, 1200))

    const recordCount = Math.floor(Math.random() * 1000) + 500
    const errorCount = Math.floor(Math.random() * 5)
    const warningCount = Math.floor(Math.random() * 10)

    return {
      isValid: errorCount === 0,
      errors: errorCount > 0 ? [
        '时间字段格式不一致',
        '站点ID 999不存在',
        '客流量字段包含负值'
      ].slice(0, errorCount) : [],
      warnings: warningCount > 0 ? [
        '部分记录缺少元数据',
        '时间范围跨度较大',
        '站点名称有重复项'
      ].slice(0, warningCount) : [],
      recordCount,
      fieldStats: {
        timestamp: { count: recordCount, missing: 0, unique: recordCount },
        stationId: { count: recordCount, missing: 0, unique: 5 },
        passengersIn: { count: recordCount, missing: 0, unique: recordCount, min: 0, max: 1000, avg: 350 },
        passengersOut: { count: recordCount, missing: 0, unique: recordCount, min: 0, max: 950, avg: 320 }
      }
    }
  },

  cleanupData: async (options: {
    removeDuplicates?: boolean
    removeInvalid?: boolean
    dateRange?: { startDate: string; endDate: string }
  }): Promise<DataCleanupResult> => {
    await new Promise(resolve => setTimeout(resolve, 2000))

    const recordsDeleted = options.removeInvalid ? Math.floor(Math.random() * 50) + 10 : 0
    const duplicatesRemoved = options.removeDuplicates ? Math.floor(Math.random() * 30) + 5 : 0

    return {
      success: true,
      message: `数据清理完成，删除了${recordsDeleted}条无效记录，移除了${duplicatesRemoved}条重复记录`,
      recordsDeleted,
      recordsUpdated: 0,
      duplicatesRemoved,
      invalidRecordsRemoved: recordsDeleted
    }
  },

  deleteDataRecords: async (recordIds: number[]): Promise<{ success: boolean; message: string }> => {
    await new Promise(resolve => setTimeout(resolve, 800))

    return {
      success: true,
      message: `成功删除${recordIds.length}条记录`
    }
  },

  exportDataRecords: async (params: DataQueryParams, format: 'csv' | 'excel' | 'json'): Promise<Blob> => {
    await new Promise(resolve => setTimeout(resolve, 1500))

    // 创建模拟的Blob响应
    const content = `模拟${format.toUpperCase()}导出数据\n时间范围：${params.startDate || '全部'}\n记录数：${Math.floor(Math.random() * 1000) + 500}`
    return new Blob([content], { type: 'text/plain' })
  },

  getDataStats: async () => {
    await new Promise(resolve => setTimeout(resolve, 600))

    const now = new Date()
    const oneMonthAgo = new Date()
    oneMonthAgo.setMonth(now.getMonth() - 1)

    return {
      totalRecords: 124567,
      stations: 156,
      lines: 25,
      dateRange: {
        minDate: oneMonthAgo.toISOString().split('T')[0],
        maxDate: now.toISOString().split('T')[0]
      },
      recentUploads: [
        { filename: 'passenger_data_2024_01.csv', uploadedAt: '2024-01-15 10:30:00', records: 12500 },
        { filename: 'train_schedule.xlsx', uploadedAt: '2024-01-10 14:20:00', records: 876 },
        { filename: 'station_info.json', uploadedAt: '2024-01-05 09:15:00', records: 156 }
      ]
    }
  }
}

// 根据环境选择使用真实API还是模拟数据
const useMock = import.meta.env.VITE_USE_MOCK === 'true' || !import.meta.env.VITE_API_BASE_URL

export const dataService = useMock ? mockService : apiService

export default api