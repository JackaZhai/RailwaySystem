/**
 * 客流分析相关类型定义
 */

// 基础客流数据
export interface PassengerFlowData {
  id: number;
  timestamp: string; // 时间戳
  stationId: number; // 站点ID
  stationName: string; // 站点名称
  stationTelecode: string; // 站点电报码
  lineId: number; // 线路ID
  lineName: string; // 线路名称
  passengersIn: number; // 上客量
  passengersOut: number; // 下客量
  totalPassengers: number; // 总客流量
  occupancyRate: number; // 满载率 (0-1)
  revenue: number; // 收入
  ticketPrice: number; // 票价
}

// 时间粒度
export type TimeGranularity = 'hour' | 'day' | 'week' | 'month' | 'quarter' | 'year';

// 客流趋势数据点
export interface FlowTrendPoint {
  time: string;
  value: number;
  category?: string; // 分类（如站点、线路等）
}

// 客流趋势数据
export interface FlowTrendData {
  granularity: TimeGranularity;
  data: FlowTrendPoint[];
  total: number;
  average: number;
  max: number;
  min: number;
  growthRate?: number; // 增长率
}

// 站点客流排名
export interface StationRanking {
  stationId: number;
  stationName: string;
  stationTelecode: string;
  totalPassengers: number;
  passengersIn: number;
  passengersOut: number;
  revenue: number;
  ranking: number;
  change?: number; // 排名变化
}

// 线路负载数据
export interface LineLoadData {
  lineId: number;
  lineName: string;
  lineCode?: string;
  totalPassengers: number;
  capacity: number; // 运力
  loadRate: number; // 负载率 (0-1)
  stations: number; // 站点数量
  avgPassengersPerStation: number; // 平均每站客流量
}

// 时间分布数据
export interface TimeDistribution {
  hour: number; // 0-23
  passengersIn: number;
  passengersOut: number;
  totalPassengers: number;
  avgPassengers: number;
}

// 空间分布数据（用于地图）
export interface SpatialDistribution {
  stationId: number;
  stationName: string;
  stationTelecode: string;
  latitude: number;
  longitude: number;
  totalPassengers: number;
  passengersIn: number;
  passengersOut: number;
  radius: number; // 用于地图显示的半径
  color: string; // 用于地图显示的颜色
}

// 客流预测数据
export interface FlowForecast {
  timestamp: string;
  actual?: number; // 实际值
  forecast: number; // 预测值
  lowerBound: number; // 预测下限
  upperBound: number; // 预测上限
  confidence: number; // 置信度
}

// 分析请求参数
export interface AnalysisRequest {
  startDate: string;
  endDate: string;
  timeGranularity?: TimeGranularity;
  stationIds?: number[];
  lineIds?: number[];
  trainIds?: number[];
  metrics?: string[]; // 需要计算的指标
}

// 分析响应
export interface AnalysisResponse {
  success: boolean;
  data: {
    trends?: FlowTrendData;
    stationRankings?: StationRanking[];
    lineLoads?: LineLoadData[];
    timeDistribution?: TimeDistribution[];
    spatialDistribution?: SpatialDistribution[];
    forecasts?: FlowForecast[];
    summary?: {
      totalPassengers: number;
      totalRevenue: number;
      avgOccupancyRate: number;
      peakHour: number;
      busiestStation: string;
      busiestLine: string;
    };
  };
  message?: string;
}

// 实时客流数据
export interface RealTimeFlow {
  stationId: number;
  stationName: string;
  currentPassengers: number;
  capacity: number;
  occupancyRate: number;
  lastUpdate: string;
  trend: 'up' | 'down' | 'stable';
}

// 客流异常检测
export interface FlowAnomaly {
  id: number;
  timestamp: string;
  stationId: number;
  stationName: string;
  expectedValue: number;
  actualValue: number;
  deviation: number; // 偏差百分比
  severity: 'low' | 'medium' | 'high';
  description: string;
}

// 对比分析数据
export interface ComparisonData {
  currentPeriod: {
    start: string;
    end: string;
    data: FlowTrendData;
  };
  previousPeriod: {
    start: string;
    end: string;
    data: FlowTrendData;
  };
  comparison: {
    totalChange: number;
    avgChange: number;
    growthRate: number;
    peakChange: number;
  };
}

// 客流热力图数据
export interface HeatmapData {
  x: string; // 时间或分类
  y: string; // 站点或线路
  value: number; // 客流量
}

// 时间段统计数据
export interface TimePeriodData {
  id: number;
  name: string;
  time: string;
  passengers: number;
  percentage: number;
  trains: number;
}

// 流向线数据
export interface FlowLineData {
  fromStationId: number;
  toStationId: number;
  fromStationName?: string;
  toStationName?: string;
  passengerCount: number;
  intensity: 'high' | 'medium' | 'low';
}

// 导出选项
export interface ExportOptions {
  format: 'csv' | 'excel' | 'json' | 'pdf';
  includeCharts: boolean;
  timeRange: string;
  metrics: string[];
}
