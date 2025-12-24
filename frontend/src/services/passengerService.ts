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
// 在开发模式下使用相对路径，通过Vite代理
// 在生产模式下使用完整URL
const API_BASE_URL = import.meta.env.PROD
  ? (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api')
  : '/api';

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
 * 客流分析服务 - 连接到Django后端API
 */
export const passengerService = {
  /**
   * 获取客流趋势分析 - 使用Django客流分析API
   */
  async getFlowTrends(params: AnalysisRequest): Promise<FlowTrendData> {
    try {
      // 调用Django客流分析API
      const response = await apiClient.post('/analytics/flow/', params);
      const backendData = response.data;

      // 转换数据格式以匹配前端类型
      const flowTrendData: FlowTrendData = {
        granularity: params.timeGranularity || 'day',
        data: backendData.data.map((item: any) => ({
          time: item.time_period,
          value: item.total_passengers,
          category: '总客流量'
        })),
        total: backendData.data.reduce((sum: number, item: any) => sum + item.total_passengers, 0),
        average: backendData.data.length > 0 ?
          backendData.data.reduce((sum: number, item: any) => sum + item.total_passengers, 0) / backendData.data.length : 0,
        max: Math.max(...backendData.data.map((item: any) => item.total_passengers)),
        min: Math.min(...backendData.data.map((item: any) => item.total_passengers))
      };

      return flowTrendData;
    } catch (error) {
      console.error('获取客流趋势失败:', error);
      throw error;
    }
  },

  /**
   * 获取站点客流排名 - 使用Django站点排名API
   */
  async getStationRankings(params: AnalysisRequest): Promise<StationRanking[]> {
    try {
      // 构建查询参数
      const queryParams = new URLSearchParams();
      if (params.startDate) queryParams.append('start_date', params.startDate);
      if (params.endDate) queryParams.append('end_date', params.endDate);

      const response = await apiClient.get(`/passenger-flows/station_ranking/?${queryParams}`);
      const backendData = response;

      // 转换数据格式以匹配前端类型
      const stationRankings: StationRanking[] = backendData.map((item: any) => ({
        stationId: item.station_id,
        stationName: item.station_name,
        stationTelecode: item.station_telecode,
        totalPassengers: item.total_passengers,
        passengersIn: item.passengers_in,
        passengersOut: item.passengers_out,
        revenue: item.total_revenue,
        ranking: item.ranking
      }));

      return stationRankings;
    } catch (error) {
      console.error('获取站点排名失败:', error);
      throw error;
    }
  },

  /**
   * 获取线路负载分析 - 暂时使用模拟数据
   */
  async getLineLoads(params: AnalysisRequest): Promise<LineLoadData[]> {
    try {
      // 从Django获取线路数据
      const routesResponse = await apiClient.get('/routes/');
      const routes = routesResponse.results || routesResponse;

      // 获取客运记录汇总来计算负载
      const queryParams = new URLSearchParams();
      if (params.startDate) queryParams.append('start_date', params.startDate);
      if (params.endDate) queryParams.append('end_date', params.endDate);

      const flowsResponse = await apiClient.get(`/passenger-flows/?${queryParams}`);
      const flows = flowsResponse.results || flowsResponse;

      // 按线路分组计算负载
      const lineLoads: LineLoadData[] = routes.map((route: any) => {
        const routeFlows = flows.filter((flow: any) => flow.route === route.id);
        const totalPassengers = routeFlows.reduce((sum: number, flow: any) =>
          sum + (flow.passengers_in || 0) + (flow.passengers_out || 0), 0);

        // 获取线路站点数量
        const routeStations = flows.filter((flow: any) => flow.route === route.id)
          .map((flow: any) => flow.station)
          .filter((value: any, index: number, self: any[]) => self.indexOf(value) === index);

        return {
          lineId: route.id,
          lineName: route.name || `线路 ${route.code}`,
          totalPassengers,
          capacity: 10000, // 模拟运力
          loadRate: totalPassengers / 10000,
          stations: routeStations.length,
          avgPassengersPerStation: routeStations.length > 0 ? totalPassengers / routeStations.length : 0
        };
      });

      return lineLoads;
    } catch (error) {
      console.error('获取线路负载失败:', error);
      throw error;
    }
  },

  /**
   * 获取时间分布分析 - 使用Django时间分布API
   */
  async getTimeDistribution(params: AnalysisRequest): Promise<TimeDistribution[]> {
    try {
      // 构建查询参数
      const queryParams = new URLSearchParams();
      if (params.startDate) queryParams.append('start_date', params.startDate);
      if (params.endDate) queryParams.append('end_date', params.endDate);

      const response = await apiClient.get(`/passenger-flows/time_distribution/?${queryParams}`);
      const backendData = response;

      // 转换数据格式以匹配前端类型
      const timeDistribution: TimeDistribution[] = backendData.map((item: any) => ({
        hour: item.hour,
        passengersIn: item.passengers_in,
        passengersOut: item.passengers_out,
        totalPassengers: item.total_passengers,
        avgPassengers: item.avg_passengers
      }));

      return timeDistribution;
    } catch (error) {
      console.error('获取时间分布失败:', error);
      throw error;
    }
  },

  /**
   * 获取空间分布分析（用于地图）- 暂时使用模拟数据
   */
  async getSpatialDistribution(params: AnalysisRequest): Promise<SpatialDistribution[]> {
    try {
      // 获取站点排名数据
      const stationRankings = await this.getStationRankings(params);

      // 模拟地理坐标（实际项目中应从数据库获取）
      const spatialDistribution: SpatialDistribution[] = stationRankings.slice(0, 20).map((station, index) => {
        // 为前20个站点生成模拟坐标（成都-重庆区域）
        const baseLat = 30.6595; // 成都纬度
        const baseLng = 104.0659; // 成都经度
        const lat = baseLat + (Math.random() - 0.5) * 2;
        const lng = baseLng + (Math.random() - 0.5) * 2;

        // 根据客流量计算半径和颜色
        const radius = Math.max(5, Math.min(30, station.totalPassengers / 10000));
        const color = station.totalPassengers > 50000 ? '#ff4d4f' :
                     station.totalPassengers > 20000 ? '#faad14' : '#52c41a';

        return {
          stationId: station.stationId,
          stationName: station.stationName,
          stationTelecode: station.stationTelecode,
          latitude: lat,
          longitude: lng,
          totalPassengers: station.totalPassengers,
          passengersIn: station.passengersIn,
          passengersOut: station.passengersOut,
          radius,
          color
        };
      });

      return spatialDistribution;
    } catch (error) {
      console.error('获取空间分布失败:', error);
      throw error;
    }
  },

  /**
   * 获取客流预测 - 暂时使用模拟数据
   */
  async getFlowForecast(params: AnalysisRequest): Promise<FlowForecast[]> {
    try {
      // 获取历史数据用于预测
      const trends = await this.getFlowTrends(params);

      // 生成未来7天的预测数据
      const forecastData: FlowForecast[] = [];
      const lastDate = new Date(params.endDate);
      const avgValue = trends.average;

      for (let i = 1; i <= 7; i++) {
        const forecastDate = new Date(lastDate);
        forecastDate.setDate(forecastDate.getDate() + i);

        // 模拟预测值（基于平均值加上随机波动）
        const baseValue = avgValue;
        const randomFactor = 0.8 + Math.random() * 0.4; // 0.8-1.2的随机因子
        const forecastValue = baseValue * randomFactor;
        const confidence = 0.85 + Math.random() * 0.1; // 85-95%置信度

        forecastData.push({
          timestamp: forecastDate.toISOString().split('T')[0],
          forecast: forecastValue,
          lowerBound: forecastValue * (1 - 0.1 * (1 - confidence)),
          upperBound: forecastValue * (1 + 0.1 * (1 - confidence)),
          confidence
        });
      }

      return forecastData;
    } catch (error) {
      console.error('获取客流预测失败:', error);
      throw error;
    }
  },

  /**
   * 获取实时客流数据 - 暂时使用模拟数据
   */
  async getRealTimeFlows(): Promise<RealTimeFlow[]> {
    try {
      // 模拟实时数据
      const stations = await this.getStations();
      const realTimeFlows: RealTimeFlow[] = stations.slice(0, 10).map((station, index) => {
        const currentPassengers = Math.floor(Math.random() * 1000) + 500;
        const capacity = 2000;
        const occupancyRate = currentPassengers / capacity;
        const trends: ('up' | 'down' | 'stable')[] = ['up', 'down', 'stable'];
        const trend = trends[Math.floor(Math.random() * 3)];

        return {
          stationId: station.id,
          stationName: station.name,
          currentPassengers,
          capacity,
          occupancyRate,
          lastUpdate: new Date().toISOString(),
          trend
        };
      });

      return realTimeFlows;
    } catch (error) {
      console.error('获取实时客流失败:', error);
      throw error;
    }
  },

  /**
   * 获取客流异常检测 - 暂时使用模拟数据
   */
  async getFlowAnomalies(params: AnalysisRequest): Promise<FlowAnomaly[]> {
    try {
      // 模拟异常检测数据
      const stations = await this.getStations();
      const anomalies: FlowAnomaly[] = [];

      // 随机生成1-3个异常
      const numAnomalies = Math.floor(Math.random() * 3) + 1;
      for (let i = 0; i < numAnomalies; i++) {
        const station = stations[Math.floor(Math.random() * stations.length)];
        const expectedValue = Math.floor(Math.random() * 1000) + 500;
        const actualValue = expectedValue * (1.5 + Math.random() * 0.5); // 150-200%的偏差
        const deviation = ((actualValue - expectedValue) / expectedValue) * 100;
        const severity: ('low' | 'medium' | 'high')[] = ['low', 'medium', 'high'];

        anomalies.push({
          id: i + 1,
          timestamp: new Date().toISOString(),
          stationId: station.id,
          stationName: station.name,
          expectedValue,
          actualValue,
          deviation,
          severity: severity[Math.floor(Math.random() * 3)],
          description: `站点 ${station.name} 客流量异常偏高`
        });
      }

      return anomalies;
    } catch (error) {
      console.error('获取客流异常失败:', error);
      throw error;
    }
  },

  /**
   * 获取对比分析数据 - 暂时使用模拟数据
   */
  async getComparisonData(params: {
    currentPeriod: AnalysisRequest;
    previousPeriod: AnalysisRequest;
  }): Promise<ComparisonData> {
    try {
      // 获取两个时间段的数据
      const currentData = await this.getFlowTrends(params.currentPeriod);
      const previousData = await this.getFlowTrends(params.previousPeriod);

      const comparison: ComparisonData = {
        currentPeriod: {
          start: params.currentPeriod.startDate,
          end: params.currentPeriod.endDate,
          data: currentData
        },
        previousPeriod: {
          start: params.previousPeriod.startDate,
          end: params.previousPeriod.endDate,
          data: previousData
        },
        comparison: {
          totalChange: currentData.total - previousData.total,
          avgChange: currentData.average - previousData.average,
          growthRate: previousData.total > 0 ?
            ((currentData.total - previousData.total) / previousData.total) * 100 : 0,
          peakChange: currentData.max - previousData.max
        }
      };

      return comparison;
    } catch (error) {
      console.error('获取对比分析失败:', error);
      throw error;
    }
  },

  /**
   * 获取客流热力图数据 - 暂时使用模拟数据
   */
  async getHeatmapData(params: AnalysisRequest): Promise<HeatmapData[]> {
    try {
      // 模拟热力图数据
      const stations = await this.getStations();
      const timeDistribution = await this.getTimeDistribution(params);

      const heatmapData: HeatmapData[] = [];

      // 生成站点-时间热力图数据
      stations.slice(0, 10).forEach(station => {
        timeDistribution.forEach(timeSlot => {
          const value = Math.floor(Math.random() * 1000) +
            (station.id % 10) * 100 + // 使不同站点有基础差异
            timeSlot.hour * 50; // 使不同时间有基础差异

          heatmapData.push({
            x: `${timeSlot.hour}:00`,
            y: station.name,
            value
          });
        });
      });

      return heatmapData;
    } catch (error) {
      console.error('获取热力图数据失败:', error);
      throw error;
    }
  },

  /**
   * 获取综合分析报告 - 整合多个分析结果
   */
  async getComprehensiveAnalysis(params: AnalysisRequest): Promise<AnalysisResponse> {
    try {
      // 并行获取所有分析数据
      const [
        trends,
        stationRankings,
        lineLoads,
        timeDistribution,
        spatialDistribution,
        forecasts
      ] = await Promise.all([
        this.getFlowTrends(params),
        this.getStationRankings(params),
        this.getLineLoads(params),
        this.getTimeDistribution(params),
        this.getSpatialDistribution(params),
        this.getFlowForecast(params)
      ]);

      // 计算摘要统计
      const summary = {
        totalPassengers: trends.total,
        totalRevenue: stationRankings.reduce((sum, station) => sum + station.revenue, 0),
        avgOccupancyRate: lineLoads.reduce((sum, line) => sum + line.loadRate, 0) / lineLoads.length,
        peakHour: timeDistribution.reduce((max, item) =>
          item.totalPassengers > max.totalPassengers ? item : max,
          { hour: 0, totalPassengers: 0 }
        ).hour,
        busiestStation: stationRankings.length > 0 ? stationRankings[0].stationName : '无数据',
        busiestLine: lineLoads.length > 0 ?
          lineLoads.reduce((max, line) => line.totalPassengers > max.totalPassengers ? line : max).lineName : '无数据'
      };

      const analysisResponse: AnalysisResponse = {
        success: true,
        data: {
          trends,
          stationRankings,
          lineLoads,
          timeDistribution,
          spatialDistribution,
          forecasts,
          summary
        }
      };

      return analysisResponse;
    } catch (error) {
      console.error('获取综合分析失败:', error);
      throw error;
    }
  },

  /**
   * 导出分析数据 - 暂时返回模拟数据
   */
  async exportAnalysisData(params: AnalysisRequest, options: ExportOptions): Promise<Blob> {
    try {
      // 获取分析数据
      const analysisData = await this.getComprehensiveAnalysis(params);

      // 将数据转换为JSON字符串
      const jsonData = JSON.stringify(analysisData, null, 2);

      // 创建Blob对象
      const blob = new Blob([jsonData], { type: 'application/json' });

      return blob;
    } catch (error) {
      console.error('导出数据失败:', error);
      throw error;
    }
  },

  /**
   * 获取数据统计摘要 - 使用Django API
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
      // 获取各实体的数量
      const [stationsResponse, trainsResponse, routesResponse, flowsResponse] = await Promise.all([
        apiClient.get('/stations/'),
        apiClient.get('/trains/'),
        apiClient.get('/routes/'),
        apiClient.get('/passenger-flows/')
      ]);

      // 获取客运记录的日期范围
      const flows = flowsResponse.results || flowsResponse;
      const dates = flows.map((flow: any) => new Date(flow.operation_date));
      const minDate = dates.length > 0 ? new Date(Math.min(...dates.map(d => d.getTime()))) : new Date();
      const maxDate = dates.length > 0 ? new Date(Math.max(...dates.map(d => d.getTime()))) : new Date();

      return {
        totalRecords: flows.length,
        dateRange: {
          start: minDate.toISOString().split('T')[0],
          end: maxDate.toISOString().split('T')[0]
        },
        stations: stationsResponse.count || (stationsResponse.results ? stationsResponse.results.length : stationsResponse.length),
        lines: routesResponse.count || (routesResponse.results ? routesResponse.results.length : routesResponse.length),
        trains: trainsResponse.count || (trainsResponse.results ? trainsResponse.results.length : trainsResponse.length),
        lastUpdate: new Date().toISOString()
      };
    } catch (error) {
      console.error('获取数据摘要失败:', error);
      throw error;
    }
  },

  /**
   * 获取站点列表 - 使用Django站点API
   */
  async getStations(): Promise<Array<{
    id: number;
    name: string;
    telecode: string;
    shortname: string;
  }>> {
    try {
      const response = await apiClient.get('/stations/');
      const stations = response.results || response;

      return stations.map((station: any) => ({
        id: station.id,
        name: station.name,
        telecode: station.telecode,
        shortname: station.shortname || ''
      }));
    } catch (error) {
      console.error('获取站点列表失败:', error);
      throw error;
    }
  },

  /**
   * 获取线路列表 - 使用Django线路API
   */
  async getLines(): Promise<Array<{
    id: number;
    name: string;
    code: string;
  }>> {
    try {
      const response = await apiClient.get('/routes/');
      const routes = response.results || response;

      return routes.map((route: any) => ({
        id: route.id,
        name: route.name,
        code: route.code.toString()
      }));
    } catch (error) {
      console.error('获取线路列表失败:', error);
      throw error;
    }
  },

  /**
   * 获取列车列表 - 使用Django列车API
   */
  async getTrains(): Promise<Array<{
    id: number;
    code: string;
    capacity: number;
  }>> {
    try {
      const response = await apiClient.get('/trains/');
      const trains = response.results || response;

      return trains.map((train: any) => ({
        id: train.id,
        code: train.code,
        capacity: train.capacity
      }));
    } catch (error) {
      console.error('获取列车列表失败:', error);
      throw error;
    }
  },
};

// 默认导出
export default passengerService;