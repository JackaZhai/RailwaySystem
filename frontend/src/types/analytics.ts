/**
 * 分析结果相关类型定义
 */

export interface TemporalAnalysis {
  period: string
  totalPassengers: number
  averageDailyPassengers: number
  peakDay: string
  peakDayPassengers: number
  growthRate: number // 百分比
  hourlyDistribution: Record<number, number> // 小时 -> 客流量
  dailyPattern: Record<string, number> // 星期几 -> 客流量
  monthlyTrend: Record<string, number> // 年月 -> 客流量
}

export interface SpatialAnalysis {
  date: Date
  totalStations: number
  passengerDistribution: Array<{
    stationId: number
    stationName: string
    passengers: number
    percentage: number
  }>
  heatmapData: Array<{
    lat: number
    lng: number
    intensity: number
  }>
  flowLines: Array<{
    from: { lat: number; lng: number }
    to: { lat: number; lng: number }
    passengers: number
  }>
}

export interface ForecastResult {
  stationId: number
  lineId: number
  forecastPeriod: number
  modelUsed: string
  accuracy: number
  mse: number
  predictions: Array<{
    date: Date
    predictedPassengers: number
    lowerBound: number
    upperBound: number
  }>
  historicalData: Array<{
    date: Date
    actualPassengers: number
  }>
}

export interface StationRanking {
  stationId: number
  stationName: string
  rank: number
  totalPassengers: number
  growthRate: number
  occupancyRate: number
  score: number // 综合评分 1-5
}

export interface LineLoadAnalysis {
  lineId: number
  lineName: string
  averageLoad: number
  peakLoad: number
  loadDistribution: Array<{
    segment: string
    load: number
  }>
  recommendations: string[]
}

export interface CorrelationAnalysis {
  variables: string[]
  correlationMatrix: number[][]
  significantCorrelations: Array<{
    var1: string
    var2: string
    correlation: number
    significance: number
  }>
}