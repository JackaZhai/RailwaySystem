/**
 * 客流分析Store
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { format, subDays, startOfDay, endOfDay } from 'date-fns';
import type {
  AnalysisRequest,
  FlowTrendData,
  StationRanking,
  LineLoadData,
  TimeDistribution,
  SpatialDistribution,
  FlowForecast,
  RealTimeFlow,
  FlowAnomaly,
  ComparisonData,
  HeatmapData,
  TimePeriodData,
  FlowLineData,
  TimeGranularity
} from '@/types/passenger';
import { passengerService } from '@/services/passengerService';

// 默认时间范围：最近30天
const getDefaultDateRange = () => {
  const end = new Date();
  const start = subDays(end, 30);
  return {
    startDate: format(start, 'yyyy-MM-dd'),
    endDate: format(end, 'yyyy-MM-dd'),
  };
};

export const usePassengerStore = defineStore('passenger', () => {
  // 状态
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // 分析参数
  const analysisParams = ref<AnalysisRequest>({
    ...getDefaultDateRange(),
    timeGranularity: 'day' as TimeGranularity,
    stationIds: [],
    lineIds: [],
    trainIds: [],
    metrics: ['passengersIn', 'passengersOut', 'totalPassengers', 'revenue'],
  });

  // 分析结果
  const flowTrends = ref<FlowTrendData | null>(null);
  const stationRankings = ref<StationRanking[]>([]);
  const lineLoads = ref<LineLoadData[]>([]);
  const timeDistribution = ref<TimeDistribution[]>([]);
  const spatialDistribution = ref<SpatialDistribution[]>([]);
  const flowForecasts = ref<FlowForecast[]>([]);
  const realTimeFlows = ref<RealTimeFlow[]>([]);
  const flowAnomalies = ref<FlowAnomaly[]>([]);
  const comparisonData = ref<ComparisonData | null>(null);
  const heatmapData = ref<HeatmapData[]>([]);
  const timePeriods = ref<TimePeriodData[]>([]);
  const flowLines = ref<FlowLineData[]>([]);

  // 缓存
  const cache = ref<Map<string, any>>(new Map());

  // 计算属性
  const hasData = computed(() => {
    return flowTrends.value !== null ||
           stationRankings.value.length > 0 ||
           lineLoads.value.length > 0;
  });

  const selectedStationsCount = computed(() => {
    return analysisParams.value.stationIds?.length || 0;
  });

  const selectedLinesCount = computed(() => {
    return analysisParams.value.lineIds?.length || 0;
  });

  const dateRangeLabel = computed(() => {
    const { startDate, endDate } = analysisParams.value;
    return `${startDate} 至 ${endDate}`;
  });

  // 获取缓存键
  const getCacheKey = (endpoint: string, params: any): string => {
    return `${endpoint}:${JSON.stringify(params)}`;
  };

  // 从缓存获取数据
  const getFromCache = <T>(key: string): T | null => {
    return cache.value.get(key) || null;
  };

  // 设置缓存数据
  const setCache = (key: string, data: any, ttl: number = 5 * 60 * 1000) => {
    cache.value.set(key, {
      data,
      timestamp: Date.now(),
      ttl,
    });
  };

  // 清理过期缓存
  const cleanupCache = () => {
    const now = Date.now();
    for (const [key, value] of cache.value.entries()) {
      if (now - value.timestamp > value.ttl) {
        cache.value.delete(key);
      }
    }
  };

  // 重置状态
  const reset = () => {
    flowTrends.value = null;
    stationRankings.value = [];
    lineLoads.value = [];
    timeDistribution.value = [];
    spatialDistribution.value = [];
    flowForecasts.value = [];
    realTimeFlows.value = [];
    flowAnomalies.value = [];
    comparisonData.value = null;
    heatmapData.value = [];
    timePeriods.value = [];
    flowLines.value = [];
    error.value = null;
  };

  // 更新分析参数
  const updateAnalysisParams = (updates: Partial<AnalysisRequest>) => {
    analysisParams.value = {
      ...analysisParams.value,
      ...updates,
    };
    // 清除缓存，因为参数已更改
    cache.value.clear();
  };

  // 设置时间范围
  const setTimeRange = (startDate: string, endDate: string) => {
    updateAnalysisParams({ startDate, endDate });
  };

  // 设置时间粒度
  const setTimeGranularity = (granularity: TimeGranularity) => {
    updateAnalysisParams({ timeGranularity: granularity });
  };

  // 设置选中的站点
  const setSelectedStations = (stationIds: number[]) => {
    updateAnalysisParams({ stationIds });
  };

  // 设置选中的线路
  const setSelectedLines = (lineIds: number[]) => {
    updateAnalysisParams({ lineIds });
  };

  // 设置选中的列车
  const setSelectedTrains = (trainIds: number[]) => {
    updateAnalysisParams({ trainIds });
  };

  // 通用数据获取函数
  const fetchData = async <T>(
    endpoint: string,
    fetchFn: () => Promise<T>,
    cacheKey?: string
  ): Promise<T> => {
    try {
      isLoading.value = true;
      error.value = null;

      // 尝试从缓存获取
      const key = cacheKey || getCacheKey(endpoint, analysisParams.value);
      const cached = getFromCache<T>(key);
      if (cached) {
        return cached;
      }

      // 从API获取
      const data = await fetchFn();

      // 缓存数据
      setCache(key, data);

      return data;
    } catch (err: any) {
      error.value = err.message || '获取数据失败';
      console.error(`获取${endpoint}失败:`, err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // 获取客流趋势
  const fetchFlowTrends = async () => {
    const data = await fetchData<FlowTrendData>(
      'flowTrends',
      () => passengerService.getFlowTrends(analysisParams.value)
    );
    flowTrends.value = data;
    return data;
  };

  // 获取站点排名
  const fetchStationRankings = async () => {
    const data = await fetchData<StationRanking[]>(
      'stationRankings',
      () => passengerService.getStationRankings(analysisParams.value)
    );
    stationRankings.value = data;
    return data;
  };

  // 获取线路负载
  const fetchLineLoads = async () => {
    const data = await fetchData<LineLoadData[]>(
      'lineLoads',
      () => passengerService.getLineLoads(analysisParams.value)
    );
    lineLoads.value = data;
    return data;
  };

  // 获取时间分布
  const fetchTimeDistribution = async () => {
    const data = await fetchData<TimeDistribution[]>(
      'timeDistribution',
      () => passengerService.getTimeDistribution(analysisParams.value)
    );
    timeDistribution.value = data;
    return data;
  };

  // 获取空间分布
  const fetchSpatialDistribution = async () => {
    const data = await fetchData<SpatialDistribution[]>(
      'spatialDistribution',
      () => passengerService.getSpatialDistribution(analysisParams.value)
    );
    spatialDistribution.value = data;
    return data;
  };

  // 获取客流预测
  const fetchFlowForecasts = async (days: number = 7) => {
    const data = await fetchData<FlowForecast[]>(
      `flowForecasts:${days}`,
      () => passengerService.getFlowForecast(analysisParams.value, days)
    );
    flowForecasts.value = data;
    return data;
  };

  // 获取实时客流
  const fetchRealTimeFlows = async () => {
    const data = await fetchData<RealTimeFlow[]>(
      'realTimeFlows',
      () => passengerService.getRealTimeFlows()
    );
    realTimeFlows.value = data;
    return data;
  };

  // 获取客流异常
  const fetchFlowAnomalies = async () => {
    const data = await fetchData<FlowAnomaly[]>(
      'flowAnomalies',
      () => passengerService.getFlowAnomalies(analysisParams.value)
    );
    flowAnomalies.value = data;
    return data;
  };

  // 获取对比分析
  const fetchComparisonData = async (previousPeriodParams: AnalysisRequest) => {
    const data = await fetchData<ComparisonData>(
      'comparisonData',
      () => passengerService.getComparisonData({
        currentPeriod: analysisParams.value,
        previousPeriod: previousPeriodParams,
      })
    );
    comparisonData.value = data;
    return data;
  };

  // 获取热力图数据
  const fetchHeatmapData = async () => {
    const data = await fetchData<HeatmapData[]>(
      'heatmapData',
      () => passengerService.getHeatmapData(analysisParams.value)
    );
    heatmapData.value = data;
    return data;
  };

  // 获取时间段统计
  const fetchTimePeriods = async () => {
    const data = await fetchData<TimePeriodData[]>(
      'timePeriods',
      () => passengerService.getTimePeriods(analysisParams.value)
    );
    timePeriods.value = data;
    return data;
  };

  // 获取流向线数据
  const fetchFlowLines = async () => {
    const data = await fetchData<FlowLineData[]>(
      'flowLines',
      () => passengerService.getFlowLines(analysisParams.value)
    );
    flowLines.value = data;
    return data;
  };

  // 获取综合分析
  const fetchComprehensiveAnalysis = async (options?: { forecastDays?: number }) => {
    try {
      isLoading.value = true;
      error.value = null;
      const forecastDays = options?.forecastDays ?? 7;

      // 并行获取所有数据
      const [
        trends,
        rankings,
        loads,
        timeDist,
        timePeriodsData,
        heatmap,
        flowLinesData,
        spatialDist,
        forecasts,
        anomalies
      ] = await Promise.all([
        passengerService.getFlowTrends(analysisParams.value),
        passengerService.getStationRankings(analysisParams.value),
        passengerService.getLineLoads(analysisParams.value),
        passengerService.getTimeDistribution(analysisParams.value),
        passengerService.getTimePeriods(analysisParams.value),
        passengerService.getHeatmapData(analysisParams.value),
        passengerService.getFlowLines(analysisParams.value),
        passengerService.getSpatialDistribution(analysisParams.value),
        passengerService.getFlowForecast(analysisParams.value, forecastDays),
        passengerService.getFlowAnomalies(analysisParams.value)
      ]);

      // 更新状态
      flowTrends.value = trends;
      stationRankings.value = rankings;
      lineLoads.value = loads;
      timeDistribution.value = timeDist;
      timePeriods.value = timePeriodsData;
      heatmapData.value = heatmap;
      flowLines.value = flowLinesData;
      spatialDistribution.value = spatialDist;
      flowForecasts.value = forecasts;
      flowAnomalies.value = anomalies;

      return {
        trends,
        rankings,
        loads,
        timeDist,
        timePeriods: timePeriodsData,
        heatmap,
        flowLines: flowLinesData,
        spatialDist,
        forecasts,
        anomalies
      };
    } catch (err: any) {
      error.value = err.message || '获取综合分析失败';
      console.error('获取综合分析失败:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // 刷新所有数据
  const refreshAllData = async () => {
    cache.value.clear();
    return fetchComprehensiveAnalysis();
  };

  // 导出数据
  const exportData = async (options: any) => {
    try {
      isLoading.value = true;
      const blob = await passengerService.exportAnalysisData(analysisParams.value, options);
      return blob;
    } catch (err: any) {
      error.value = err.message || '导出数据失败';
      console.error('导出数据失败:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  // 初始化
  const init = async () => {
    try {
      // 清理过期缓存
      cleanupCache();

      // 可以在这里加载一些初始数据
      // 例如：获取站点列表、线路列表等
    } catch (err) {
      console.error('初始化客流分析store失败:', err);
    }
  };

  return {
    // 状态
    isLoading,
    error,
    analysisParams,

    // 数据
    flowTrends,
    stationRankings,
    lineLoads,
    timeDistribution,
    spatialDistribution,
    flowForecasts,
    realTimeFlows,
    flowAnomalies,
    comparisonData,
    heatmapData,
    timePeriods,
    flowLines,

    // 计算属性
    hasData,
    selectedStationsCount,
    selectedLinesCount,
    dateRangeLabel,

    // 方法
    reset,
    updateAnalysisParams,
    setTimeRange,
    setTimeGranularity,
    setSelectedStations,
    setSelectedLines,
    setSelectedTrains,

    fetchFlowTrends,
    fetchStationRankings,
    fetchLineLoads,
    fetchTimeDistribution,
    fetchSpatialDistribution,
    fetchFlowForecasts,
    fetchRealTimeFlows,
    fetchFlowAnomalies,
    fetchComparisonData,
    fetchHeatmapData,
    fetchTimePeriods,
    fetchFlowLines,
    fetchComprehensiveAnalysis,
    refreshAllData,
    exportData,
    init,
  };
});
