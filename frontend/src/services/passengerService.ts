/**
 * 客流分析服务
 */
import axios from 'axios';
import type {
  AnalysisRequest,
  AnalysisResponse,
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
  ExportOptions
} from '@/types/passenger';

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API请求错误:', error);

    // 统一错误处理
    const errorMessage = error.response?.data?.message ||
                        error.response?.data?.detail ||
                        error.message ||
                        '请求失败';

    return Promise.reject({
      message: errorMessage,
      status: error.response?.status,
      data: error.response?.data,
    });
  }
);

/**
 * 客流分析服务
 */
export const passengerService = {
  /**
   * 获取客流趋势分析
   */
  async getFlowTrends(params: AnalysisRequest): Promise<FlowTrendData> {
    try {
      const response = await apiClient.post('/analytics/flow/trends/', params);
      return response.data;
    } catch (error) {
      console.error('获取客流趋势失败:', error);
      throw error;
    }
  },

  /**
   * 获取站点客流排名
   */
  async getStationRankings(params: AnalysisRequest): Promise<StationRanking[]> {
    try {
      const response = await apiClient.post('/analytics/flow/station-rankings/', params);
      return response.data;
    } catch (error) {
      console.error('获取站点排名失败:', error);
      throw error;
    }
  },

  /**
   * 获取线路负载分析
   */
  async getLineLoads(params: AnalysisRequest): Promise<LineLoadData[]> {
    try {
      const response = await apiClient.post('/analytics/flow/line-loads/', params);
      return response.data;
    } catch (error) {
      console.error('获取线路负载失败:', error);
      throw error;
    }
  },

  /**
   * 获取时间分布分析
   */
  async getTimeDistribution(params: AnalysisRequest): Promise<TimeDistribution[]> {
    try {
      const response = await apiClient.post('/analytics/flow/time-distribution/', params);
      return response.data;
    } catch (error) {
      console.error('获取时间分布失败:', error);
      throw error;
    }
  },

  /**
   * 获取空间分布分析（用于地图）
   */
  async getSpatialDistribution(params: AnalysisRequest): Promise<SpatialDistribution[]> {
    try {
      const response = await apiClient.post('/analytics/flow/spatial-distribution/', params);
      return response.data;
    } catch (error) {
      console.error('获取空间分布失败:', error);
      throw error;
    }
  },

  /**
   * 获取客流预测
   */
  async getFlowForecast(params: AnalysisRequest): Promise<FlowForecast[]> {
    try {
      const response = await apiClient.post('/analytics/flow/forecast/', params);
      return response.data;
    } catch (error) {
      console.error('获取客流预测失败:', error);
      throw error;
    }
  },

  /**
   * 获取实时客流数据
   */
  async getRealTimeFlows(): Promise<RealTimeFlow[]> {
    try {
      const response = await apiClient.get('/analytics/flow/real-time/');
      return response.data;
    } catch (error) {
      console.error('获取实时客流失败:', error);
      throw error;
    }
  },

  /**
   * 获取客流异常检测
   */
  async getFlowAnomalies(params: AnalysisRequest): Promise<FlowAnomaly[]> {
    try {
      const response = await apiClient.post('/analytics/flow/anomalies/', params);
      return response.data;
    } catch (error) {
      console.error('获取客流异常失败:', error);
      throw error;
    }
  },

  /**
   * 获取对比分析数据
   */
  async getComparisonData(params: {
    currentPeriod: AnalysisRequest;
    previousPeriod: AnalysisRequest;
  }): Promise<ComparisonData> {
    try {
      const response = await apiClient.post('/analytics/flow/comparison/', params);
      return response.data;
    } catch (error) {
      console.error('获取对比分析失败:', error);
      throw error;
    }
  },

  /**
   * 获取客流热力图数据
   */
  async getHeatmapData(params: AnalysisRequest): Promise<HeatmapData[]> {
    try {
      const response = await apiClient.post('/analytics/flow/heatmap/', params);
      return response.data;
    } catch (error) {
      console.error('获取热力图数据失败:', error);
      throw error;
    }
  },

  /**
   * 获取综合分析报告
   */
  async getComprehensiveAnalysis(params: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      const response = await apiClient.post('/analytics/flow/comprehensive/', params);
      return response.data;
    } catch (error) {
      console.error('获取综合分析失败:', error);
      throw error;
    }
  },

  /**
   * 导出分析数据
   */
  async exportAnalysisData(params: AnalysisRequest, options: ExportOptions): Promise<Blob> {
    try {
      const response = await apiClient.post(
        '/analytics/flow/export/',
        { ...params, options },
        { responseType: 'blob' }
      );
      return response;
    } catch (error) {
      console.error('导出数据失败:', error);
      throw error;
    }
  },

  /**
   * 获取数据统计摘要
   */
  async getDataSummary(): Promise<{
    totalRecords: number;
    dateRange: { start: string; end: string };
    stations: number;
    lines: number;
    trains: number;
    lastUpdate: string;
  }> {
    try {
      const response = await apiClient.get('/analytics/flow/summary/');
      return response.data;
    } catch (error) {
      console.error('获取数据摘要失败:', error);
      throw error;
    }
  },

  /**
   * 获取站点列表
   */
  async getStations(): Promise<Array<{
    id: number;
    name: string;
    telecode: string;
    shortname: string;
  }>> {
    try {
      const response = await apiClient.get('/analytics/stations/');
      return response.data;
    } catch (error) {
      console.error('获取站点列表失败:', error);
      throw error;
    }
  },

  /**
   * 获取线路列表
   */
  async getLines(): Promise<Array<{
    id: number;
    name: string;
    code: string;
  }>> {
    try {
      const response = await apiClient.get('/analytics/lines/');
      return response.data;
    } catch (error) {
      console.error('获取线路列表失败:', error);
      throw error;
    }
  },

  /**
   * 获取列车列表
   */
  async getTrains(): Promise<Array<{
    id: number;
    code: string;
    capacity: number;
  }>> {
    try {
      const response = await apiClient.get('/analytics/trains/');
      return response.data;
    } catch (error) {
      console.error('获取列车列表失败:', error);
      throw error;
    }
  },
};

// 默认导出
export default passengerService;