import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TemporalAnalysis, SpatialAnalysis, ForecastResult, StationRanking } from '@/types/analytics'

/**
 * 分析结果状态管理
 */
export const useAnalyticsStore = defineStore('analytics', () => {
  // 状态
  const temporalAnalysis = ref<TemporalAnalysis | null>(null)
  const spatialAnalysis = ref<SpatialAnalysis | null>(null)
  const forecastResults = ref<ForecastResult | null>(null)
  const stationRankings = ref<StationRanking[]>([])
  const isLoading = ref(false)
  const lastAnalysisTime = ref<Date | null>(null)
  const analysisParameters = ref<Record<string, any>>({})

  // 计算属性
  const hasAnalysisData = computed(() => {
    return !!temporalAnalysis.value || !!spatialAnalysis.value || !!forecastResults.value || stationRankings.value.length > 0
  })

  const topStations = computed(() => {
    return [...stationRankings.value]
      .sort((a, b) => b.totalPassengers - a.totalPassengers)
      .slice(0, 10)
  })

  const busyHours = computed(() => {
    if (!temporalAnalysis.value?.hourlyDistribution) return []
    const hourly = temporalAnalysis.value.hourlyDistribution
    return Object.entries(hourly)
      .map(([hour, count]) => ({ hour: parseInt(hour), count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)
  })

  // 操作
  const setTemporalAnalysis = (data: TemporalAnalysis) => {
    temporalAnalysis.value = data
    lastAnalysisTime.value = new Date()
  }

  const setSpatialAnalysis = (data: SpatialAnalysis) => {
    spatialAnalysis.value = data
    lastAnalysisTime.value = new Date()
  }

  const setForecastResults = (data: ForecastResult) => {
    forecastResults.value = data
    lastAnalysisTime.value = new Date()
  }

  const setStationRankings = (data: StationRanking[]) => {
    stationRankings.value = data
    lastAnalysisTime.value = new Date()
  }

  const clearAnalysis = () => {
    temporalAnalysis.value = null
    spatialAnalysis.value = null
    forecastResults.value = null
    stationRankings.value = []
    lastAnalysisTime.value = null
    analysisParameters.value = {}
  }

  const updateAnalysisParameters = (params: Record<string, any>) => {
    analysisParameters.value = { ...analysisParameters.value, ...params }
  }

  const runTemporalAnalysis = async (params: {
    startDate: Date
    endDate: Date
    frequency: 'hourly' | 'daily' | 'weekly' | 'monthly'
    stationId?: number
    lineId?: number
  }) => {
    try {
      isLoading.value = true
      updateAnalysisParameters({ temporal: params })

      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1500))

      // 模拟分析结果
      const mockAnalysis: TemporalAnalysis = {
        period: `${params.startDate.toISOString().split('T')[0]} 至 ${params.endDate.toISOString().split('T')[0]}`,
        totalPassengers: 1250000,
        averageDailyPassengers: 25000,
        peakDay: '2024-06-15',
        peakDayPassengers: 45000,
        growthRate: 12.5,
        hourlyDistribution: {
          6: 1200, 7: 4500, 8: 7800, 9: 6500, 10: 5200,
          11: 4800, 12: 5100, 13: 4900, 14: 5300, 15: 5600,
          16: 6200, 17: 7100, 18: 6800, 19: 5200, 20: 3800,
          21: 2500, 22: 1500, 23: 800,
        },
        dailyPattern: {
          Monday: 22000, Tuesday: 23000, Wednesday: 24000,
          Thursday: 23500, Friday: 26000, Saturday: 28000, Sunday: 25000,
        },
        monthlyTrend: {
          '2024-01': 650000, '2024-02': 680000, '2024-03': 720000,
          '2024-04': 750000, '2024-05': 780000, '2024-06': 820000,
        },
      }

      setTemporalAnalysis(mockAnalysis)
      return mockAnalysis
    } catch (error) {
      console.error('时空分析失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const runSpatialAnalysis = async (params: {
    date: Date
    aggregationLevel: 'station' | 'city' | 'region'
  }) => {
    try {
      isLoading.value = true
      updateAnalysisParameters({ spatial: params })

      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1200))

      // 模拟分析结果
      const mockAnalysis: SpatialAnalysis = {
        date: params.date,
        totalStations: 45,
        passengerDistribution: [
          { stationId: 1001, stationName: '成都东', passengers: 85000, percentage: 18.5 },
          { stationId: 1002, stationName: '重庆北', passengers: 72000, percentage: 15.7 },
          { stationId: 1003, stationName: '成都南', passengers: 58000, percentage: 12.6 },
          { stationId: 1004, stationName: '重庆西', passengers: 52000, percentage: 11.3 },
          { stationId: 1005, stationName: '内江北', passengers: 32000, percentage: 7.0 },
          { stationId: 1006, stationName: '永川东', passengers: 28000, percentage: 6.1 },
          { stationId: 1007, stationName: '资阳北', passengers: 25000, percentage: 5.4 },
          { stationId: 1008, stationName: '大足南', passengers: 22000, percentage: 4.8 },
          { stationId: 1009, stationName: '荣昌北', passengers: 19000, percentage: 4.1 },
          { stationId: 1010, stationName: '璧山', passengers: 16000, percentage: 3.5 },
        ],
        heatmapData: [], // 实际应用中会有热力图数据
        flowLines: [], // 实际应用中会有流向线数据
      }

      setSpatialAnalysis(mockAnalysis)
      return mockAnalysis
    } catch (error) {
      console.error('空间分析失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const runForecast = async (params: {
    stationId: number
    lineId: number
    forecastPeriod: 7 | 30 | 90 // 预测天数
    model: 'arima' | 'prophet' | 'lstm'
  }) => {
    try {
      isLoading.value = true
      updateAnalysisParameters({ forecast: params })

      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000))

      // 模拟预测结果
      const mockForecast: ForecastResult = {
        stationId: params.stationId,
        lineId: params.lineId,
        forecastPeriod: params.forecastPeriod,
        modelUsed: params.model,
        accuracy: 0.89,
        mse: 1250.5,
        predictions: Array.from({ length: params.forecastPeriod }, (_, i) => ({
          date: new Date(Date.now() + (i + 1) * 24 * 60 * 60 * 1000),
          predictedPassengers: 25000 + Math.random() * 5000,
          lowerBound: 20000 + Math.random() * 4000,
          upperBound: 30000 + Math.random() * 6000,
        })),
        historicalData: Array.from({ length: 30 }, (_, i) => ({
          date: new Date(Date.now() - (30 - i) * 24 * 60 * 60 * 1000),
          actualPassengers: 24000 + Math.random() * 6000,
        })),
      }

      setForecastResults(mockForecast)
      return mockForecast
    } catch (error) {
      console.error('预测分析失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const calculateStationRankings = async (params: {
    metric: 'passenger_volume' | 'growth_rate' | 'occupancy_rate' | 'service_quality'
    dateRange: { start: Date; end: Date }
    limit?: number
  }) => {
    try {
      isLoading.value = true
      updateAnalysisParameters({ rankings: params })

      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000))

      // 模拟排名数据
      const mockRankings: StationRanking[] = [
        { stationId: 1001, stationName: '成都东', rank: 1, totalPassengers: 85000, growthRate: 15.2, occupancyRate: 0.92, score: 4.8 },
        { stationId: 1002, stationName: '重庆北', rank: 2, totalPassengers: 72000, growthRate: 12.8, occupancyRate: 0.88, score: 4.6 },
        { stationId: 1003, stationName: '成都南', rank: 3, totalPassengers: 58000, growthRate: 10.5, occupancyRate: 0.85, score: 4.4 },
        { stationId: 1004, stationName: '重庆西', rank: 4, totalPassengers: 52000, growthRate: 9.8, occupancyRate: 0.82, score: 4.3 },
        { stationId: 1005, stationName: '内江北', rank: 5, totalPassengers: 32000, growthRate: 8.5, occupancyRate: 0.78, score: 4.1 },
        { stationId: 1006, stationName: '永川东', rank: 6, totalPassengers: 28000, growthRate: 7.9, occupancyRate: 0.75, score: 4.0 },
        { stationId: 1007, stationName: '资阳北', rank: 7, totalPassengers: 25000, growthRate: 7.2, occupancyRate: 0.72, score: 3.9 },
        { stationId: 1008, stationName: '大足南', rank: 8, totalPassengers: 22000, growthRate: 6.8, occupancyRate: 0.70, score: 3.8 },
        { stationId: 1009, stationName: '荣昌北', rank: 9, totalPassengers: 19000, growthRate: 6.3, occupancyRate: 0.68, score: 3.7 },
        { stationId: 1010, stationName: '璧山', rank: 10, totalPassengers: 16000, growthRate: 5.9, occupancyRate: 0.65, score: 3.6 },
      ].slice(0, params.limit || 10)

      setStationRankings(mockRankings)
      return mockRankings
    } catch (error) {
      console.error('站点排名计算失败:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  return {
    // 状态
    temporalAnalysis,
    spatialAnalysis,
    forecastResults,
    stationRankings,
    isLoading,
    lastAnalysisTime,
    analysisParameters,

    // 计算属性
    hasAnalysisData,
    topStations,
    busyHours,

    // 操作
    setTemporalAnalysis,
    setSpatialAnalysis,
    setForecastResults,
    setStationRankings,
    clearAnalysis,
    updateAnalysisParameters,
    runTemporalAnalysis,
    runSpatialAnalysis,
    runForecast,
    calculateStationRankings,
  }
})