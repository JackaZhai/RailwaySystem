import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import { MapContainer, CircleMarker, Tooltip as LeafletTooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { GaodeTileLayer, GaodeMapType } from "./components/map/GaodeTileLayer";
import { MapControls } from "./components/map/MapControls";
import { GAODE_MAP_CONFIG } from "./config";
import Sidebar from "./components/Sidebar";

// 数据类型定义
interface PassengerFlowSummary {
  station: string;
  line: string;
  total_in: number;
  total_out: number;
}

interface TemporalTrendPoint {
  timestamp: string;
  passengers_in: number;
  passengers_out: number;
}

interface SpatialDistributionPoint {
  station: string;
  total_in: number;
  total_out: number;
}

interface Recommendation {
  line: string;
  recommendation: string;
  rationale: string;
}

interface StationMetric {
  station: string;
  total_passengers: number;
  average_headway: number;
  peak_hour: number | null;
}

// CSV 数据接口
interface StationData {
  zdid: number;
  zdmc: string;
  station_code: string;
  station_telecode: string;
}

interface TrainData {
  lcbm: string;
  lcdm: string;
  lcyn: number;
}

interface LineStationData {
  yyxlbm: string;
  zdid: number;
  xlzdid: number;
  xldm: string;
  ysjl: number;
}

interface PassengerVolumeData {
  yyxlbm: string;
  lcbm: string;
  zdid: number;
  yxrq: string;
  skl: number;
  xkl: number;
  ticket_price: number;
  shouru: number;
}

const defaultPosition: [number, number] = GAODE_MAP_CONFIG.DEFAULT_CENTER;
const stationCoordinates: Record<string, [number, number]> = GAODE_MAP_CONFIG.STATION_COORDINATES;

function App() {
  // 页面状态
  const [activePage, setActivePage] = useState<string>("dashboard");

  // 数据状态
  const [flow, setFlow] = useState<PassengerFlowSummary[]>([]);
  const [trend, setTrend] = useState<TemporalTrendPoint[]>([]);
  const [spatial, setSpatial] = useState<SpatialDistributionPoint[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [metrics, setMetrics] = useState<StationMetric[]>([]);

  // CSV 数据状态
  const [stationData, setStationData] = useState<StationData[]>([]);
  const [trainData, setTrainData] = useState<TrainData[]>([]);
  const [lineStationData, setLineStationData] = useState<LineStationData[]>([]);
  const [passengerVolumeData, setPassengerVolumeData] = useState<PassengerVolumeData[]>([]);

  // UI 状态
  const [filters, setFilters] = useState({ line: "", station: "" });
  const [mapType, setMapType] = useState<GaodeMapType>("normal");
  const [loading, setLoading] = useState(true);

  // 获取所有数据
  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      try {
        // 获取后端API数据
        const [flowRes, trendRes, spatialRes, recRes, metricsRes] = await Promise.all([
          axios.get<PassengerFlowSummary[]>("/api/analytics/flow/"),
          axios.get<TemporalTrendPoint[]>("/api/analytics/temporal/?freq=H"),
          axios.get<SpatialDistributionPoint[]>("/api/analytics/spatial/"),
          axios.get<Recommendation[]>("/api/lines/recommendations/"),
          axios.get<StationMetric[]>("/api/stations/metrics/")
        ]);

        setFlow(flowRes.data);
        setTrend(trendRes.data);
        setSpatial(spatialRes.data);
        setRecommendations(recRes.data);
        setMetrics(metricsRes.data);

        // 获取CSV数据（模拟数据，实际应从后端API获取）
        // 这里我们模拟一些数据
        const mockStationData: StationData[] = [
          { zdid: 1, zdmc: "北京", station_code: "10001", station_telecode: "BJP" },
          { zdid: 2, zdmc: "天津", station_code: "10004", station_telecode: "YUP" },
          { zdid: 3, zdmc: "成都", station_code: "51001", station_telecode: "CDW" },
          { zdid: 4, zdmc: "重庆", station_code: "50001", station_telecode: "CQW" },
        ];

        const mockTrainData: TrainData[] = [
          { lcbm: "1", lcdm: "Z95", lcyn: 1683 },
          { lcbm: "2", lcdm: "Z96", lcyn: 1577 },
          { lcbm: "3", lcdm: "3022", lcyn: 2596 },
          { lcbm: "4", lcdm: "K4033", lcyn: 2482 },
        ];

        const mockLineStationData: LineStationData[] = [
          { yyxlbm: "1", zdid: 1640, xlzdid: 1, xldm: "3100", ysjl: 669 },
          { yyxlbm: "1", zdid: 1639, xlzdid: 2, xldm: "3100", ysjl: 631 },
          { yyxlbm: "1", zdid: 1638, xlzdid: 3, xldm: "3100", ysjl: 608 },
        ];

        const mockPassengerVolumeData: PassengerVolumeData[] = [
          { yyxlbm: "39", lcbm: "148", zdid: 1, yxrq: "2024-01-01", skl: 150, xkl: 120, ticket_price: 48.5, shouru: 7275 },
          { yyxlbm: "39", lcbm: "148", zdid: 2, yxrq: "2024-01-01", skl: 200, xkl: 180, ticket_price: 52.0, shouru: 10400 },
          { yyxlbm: "39", lcbm: "148", zdid: 3, yxrq: "2024-01-01", skl: 300, xkl: 250, ticket_price: 78.0, shouru: 23400 },
        ];

        setStationData(mockStationData);
        setTrainData(mockTrainData);
        setLineStationData(mockLineStationData);
        setPassengerVolumeData(mockPassengerVolumeData);

      } catch (error) {
        console.error("获取数据失败:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  // 筛选客流数据
  const filteredFlow = useMemo(() => {
    return flow.filter((item) => {
      const lineMatches = filters.line ? item.line === filters.line : true;
      const stationMatches = filters.station ? item.station === filters.station : true;
      return lineMatches && stationMatches;
    });
  }, [flow, filters]);

  // 计算统计数据
  const stats = useMemo(() => {
    const totalPassengers = flow.reduce((sum, item) => sum + item.total_in + item.total_out, 0);
    const totalStations = new Set(flow.map(item => item.station)).size;
    const totalLines = new Set(flow.map(item => item.line)).size;
    const avgPassengers = flow.length > 0 ? totalPassengers / flow.length : 0;

    return { totalPassengers, totalStations, totalLines, avgPassengers };
  }, [flow]);

  // 渲染不同页面
  const renderPage = () => {
    if (loading) {
      return (
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>正在加载数据...</p>
        </div>
      );
    }

    switch (activePage) {
      case "dashboard":
        return renderDashboard();
      case "passenger-flow":
        return renderPassengerFlow();
      case "temporal-trend":
        return renderTemporalTrend();
      case "spatial-distribution":
        return renderSpatialDistribution();
      case "line-optimization":
        return renderLineOptimization();
      case "station-metrics":
        return renderStationMetrics();
      case "data-management":
        return renderDataManagement();
      case "settings":
        return renderSettings();
      default:
        return renderDashboard();
    }
  };

  // 仪表盘概览
  const renderDashboard = () => (
    <div className="fade-in">
      <div className="main-header">
        <div className="header-title">
          <h1>铁路运营仪表盘</h1>
          <p>实时监控成渝地区铁路客运数据与分析</p>
        </div>
        <div className="header-actions">
          <button className="header-btn primary-btn">
            <span>📊</span> 生成报告
          </button>
          <button className="header-btn secondary-btn">
            <span>🔄</span> 刷新数据
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="card-grid">
        <div className="card">
          <p className="card-title">总客流量</p>
          <p className="card-value">{stats.totalPassengers.toLocaleString()}</p>
          <p className="card-change positive">↑ 12.5% 较上周</p>
        </div>
        <div className="card">
          <p className="card-title">站点数量</p>
          <p className="card-value">{stats.totalStations}</p>
          <p className="card-change positive">↑ 2个 新增</p>
        </div>
        <div className="card">
          <p className="card-title">运营线路</p>
          <p className="card-value">{stats.totalLines}</p>
          <p className="card-change">持平</p>
        </div>
        <div className="card">
          <p className="card-title">平均客流</p>
          <p className="card-value">{Math.round(stats.avgPassengers)}</p>
          <p className="card-change positive">↑ 8.3% 较昨日</p>
        </div>
      </div>

      {/* 主要图表 */}
      <div className="dashboard">
        <div className="panel">
          <div className="panel-header">
            <h2><span>📈</span> 客流趋势</h2>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trend.slice(0, 24)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" tickFormatter={(v) => v.slice(11, 16)} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="passengers_in" stroke="#2c3e50" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="passengers_out" stroke="#7f8c8d" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h2><span>🚆</span> 热门站点</h2>
          </div>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>站点</th>
                  <th>线路</th>
                  <th>进站人数</th>
                  <th>出站人数</th>
                </tr>
              </thead>
              <tbody>
                {flow.slice(0, 5).map((item) => (
                  <tr key={`${item.station}-${item.line}`}>
                    <td>{item.station}</td>
                    <td>{item.line}</td>
                    <td>{item.total_in.toLocaleString()}</td>
                    <td>{item.total_out.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );

  // 客流分析页面
  const renderPassengerFlow = () => (
    <div className="fade-in">
      <div className="main-header">
        <div className="header-title">
          <h1>客流分析</h1>
          <p>详细分析各站点线路的进出站客流数据</p>
        </div>
      </div>

      <div className="filters">
        <input
          className="filter-input"
          placeholder="按线路筛选 (如: 成渝线)"
          value={filters.line}
          onChange={(e) => setFilters(prev => ({ ...prev, line: e.target.value }))}
        />
        <input
          className="filter-input"
          placeholder="按站点筛选 (如: 成都)"
          value={filters.station}
          onChange={(e) => setFilters(prev => ({ ...prev, station: e.target.value }))}
        />
        <button
          className="header-btn secondary-btn"
          onClick={() => setFilters({ line: "", station: "" })}
        >
          清除筛选
        </button>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><span>📊</span> 客流数据表</h2>
          <div className="panel-actions">
            <button className="header-btn secondary-btn" style={{ fontSize: '0.875rem' }}>
              导出数据
            </button>
          </div>
        </div>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>站点</th>
                <th>线路</th>
                <th>进站总人数</th>
                <th>出站总人数</th>
                <th>总客流量</th>
                <th>净流量</th>
              </tr>
            </thead>
            <tbody>
              {filteredFlow.map((item) => (
                <tr key={`${item.station}-${item.line}`}>
                  <td><strong>{item.station}</strong></td>
                  <td><span className="text-primary">{item.line}</span></td>
                  <td>{item.total_in.toLocaleString()}</td>
                  <td>{item.total_out.toLocaleString()}</td>
                  <td><strong>{(item.total_in + item.total_out).toLocaleString()}</strong></td>
                  <td className={item.total_in > item.total_out ? "text-primary" : "text-danger"}>
                    {Math.abs(item.total_in - item.total_out).toLocaleString()}
                    {item.total_in > item.total_out ? " (净流入)" : " (净流出)"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><span>📈</span> 客流分布图</h2>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={filteredFlow.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="station" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="total_in" fill="#2c3e50" name="进站人数" />
              <Bar dataKey="total_out" fill="#7f8c8d" name="出站人数" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  // 时间趋势页面
  const renderTemporalTrend = () => (
    <div className="fade-in">
      <div className="main-header">
        <div className="header-title">
          <h1>时间趋势分析</h1>
          <p>分析客流随时间的变化趋势和规律</p>
        </div>
        <div className="header-actions">
          <select className="filter-select" style={{ width: '150px' }}>
            <option value="H">小时数据</option>
            <option value="D">日数据</option>
            <option value="W">周数据</option>
            <option value="M">月数据</option>
          </select>
        </div>
      </div>

      <div className="panel" style={{ gridColumn: "1 / span 2" }}>
        <div className="panel-header">
          <h2><span>⏰</span> 客流时间趋势</h2>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" tickFormatter={(v) => v.slice(5, 16)} />
              <YAxis />
              <Tooltip
                labelFormatter={(value) => `时间: ${value}`}
                formatter={(value: number) => [value.toLocaleString(), '人次']}
              />
              <Line
                type="monotone"
                dataKey="passengers_in"
                stroke="#2c3e50"
                strokeWidth={3}
                dot={false}
                name="进站人数"
              />
              <Line
                type="monotone"
                dataKey="passengers_out"
                stroke="#7f8c8d"
                strokeWidth={3}
                dot={false}
                name="出站人数"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><span>📅</span> 日统计</h2>
        </div>
        <div className="card-grid">
          <div className="card">
            <p className="card-title">最高峰时段</p>
            <p className="card-value">08:00-09:00</p>
            <p className="card-change">进站峰值</p>
          </div>
          <div className="card">
            <p className="card-title">日均客流量</p>
            <p className="card-value">
              {trend.length > 0
                ? Math.round(trend.reduce((sum, item) => sum + item.passengers_in + item.passengers_out, 0) / (trend.length / 24))
                : 0
              }
            </p>
            <p className="card-change positive">↑ 15% 较上周</p>
          </div>
        </div>
      </div>
    </div>
  );

  // 空间分布页面
  const renderSpatialDistribution = () => (
    <div className="fade-in">
      <div className="main-header">
        <div className="header-title">
          <h1>空间分布</h1>
          <p>在地图上可视化各站点的客流分布情况</p>
        </div>
        <div className="header-actions">
          <button
            className={`header-btn ${mapType === 'normal' ? 'primary-btn' : 'secondary-btn'}`}
            onClick={() => setMapType('normal')}
          >
            标准地图
          </button>
          <button
            className={`header-btn ${mapType === 'satellite' ? 'primary-btn' : 'secondary-btn'}`}
            onClick={() => setMapType('satellite')}
          >
            卫星地图
          </button>
          <button
            className={`header-btn ${mapType === 'roadnet' ? 'primary-btn' : 'secondary-btn'}`}
            onClick={() => setMapType('roadnet')}
          >
            路网地图
          </button>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><span>🗺️</span> 客流空间分布图</h2>
        </div>
        <div style={{ position: 'relative' }}>
          <MapContainer
            center={defaultPosition}
            zoom={GAODE_MAP_CONFIG.DEFAULT_ZOOM}
            className="map-container"
          >
            <GaodeTileLayer mapType={mapType} />
            {spatial.map((point) => {
              const position = stationCoordinates[point.station] ?? defaultPosition;
              return (
                <CircleMarker
                  key={point.station}
                  center={position}
                  radius={Math.max(8, (point.total_in + point.total_out) / 50)}
                  color="#3b82f6"
                  fillColor="#3b82f6"
                  fillOpacity={0.6}
                  weight={2}
                >
                  <LeafletTooltip>
                    <div style={{ textAlign: 'center' }}>
                      <strong>{point.station}</strong><br />
                      进站: {point.total_in.toLocaleString()} 人次<br />
                      出站: {point.total_out.toLocaleString()} 人次<br />
                      总计: {(point.total_in + point.total_out).toLocaleString()} 人次
                    </div>
                  </LeafletTooltip>
                </CircleMarker>
              );
            })}
            <MapControls
              currentMapType={mapType}
              onMapTypeChange={setMapType}
              showZoomControl={true}
              showLocateControl={true}
            />
          </MapContainer>
          <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
            <small>地图数据 © 高德地图 | 双击地图可放大，拖动可平移</small>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><span>📍</span> 站点客流排行</h2>
        </div>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>站点</th>
                <th>总客流量</th>
                <th>进站排名</th>
                <th>出站排名</th>
              </tr>
            </thead>
            <tbody>
              {spatial
                .sort((a, b) => (b.total_in + b.total_out) - (a.total_in + a.total_out))
                .slice(0, 8)
                .map((point, index) => (
                  <tr key={point.station}>
                    <td><strong>{point.station}</strong></td>
                    <td>{(point.total_in + point.total_out).toLocaleString()}</td>
                    <td>
                      <span className="text-primary">#{index + 1}</span>
                    </td>
                    <td>
                      <span className="text-primary">#{index + 1}</span>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // 线路优化页面
  const renderLineOptimization = () => (
    <div className="fade-in">
      <div className="main-header">
        <div className="header-title">
          <h1>线路优化建议</h1>
          <p>基于数据分析的线路运营优化建议</p>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><span>📈</span> 优化建议列表</h2>
        </div>
        <div className="card-grid">
          {recommendations.map((item, index) => (
            <div className="card" key={item.line}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0 }}>{item.line}</h3>
                <span className="text-primary" style={{ fontSize: '0.75rem', fontWeight: 600 }}>
                  建议 #{index + 1}
                </span>
              </div>
              <p style={{ margin: '1rem 0', color: '#475569' }}>
                <strong>建议:</strong> {item.recommendation}
              </p>
              <p style={{ margin: 0, fontSize: '0.875rem', color: '#64748b' }}>
                <strong>理由:</strong> {item.rationale}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // 站点指标页面
  const renderStationMetrics = () => (
    <div className="fade-in">
      <div className="main-header">
        <div className="header-title">
          <h1>站点指标</h1>
          <p>各站点的运营效率和服务质量指标</p>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><span>🚆</span> 站点性能指标</h2>
        </div>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>站点</th>
                <th>总客流</th>
                <th>平均发车间隔 (分)</th>
                <th>高峰时段</th>
                <th>运营效率</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric) => (
                <tr key={metric.station}>
                  <td><strong>{metric.station}</strong></td>
                  <td>{metric.total_passengers.toLocaleString()}</td>
                  <td>
                    <span className={metric.average_headway < 15 ? "text-success" : "text-warning"}>
                      {metric.average_headway.toFixed(1)}
                    </span>
                  </td>
                  <td>{metric.peak_hour ? `${metric.peak_hour}:00` : "-"}</td>
                  <td>
                    {metric.total_passengers > 10000 && metric.average_headway < 10 ? (
                      <span className="text-success">优秀</span>
                    ) : metric.total_passengers > 5000 && metric.average_headway < 15 ? (
                      <span className="text-primary">良好</span>
                    ) : (
                      <span className="text-warning">一般</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  // 数据管理页面
  const renderDataManagement = () => (
    <div className="fade-in">
      <div className="main-header">
        <div className="header-title">
          <h1>数据管理</h1>
          <p>管理原始数据和迁移数据</p>
        </div>
        <div className="header-actions">
          <button className="header-btn primary-btn">
            <span>📥</span> 导入数据
          </button>
          <button className="header-btn secondary-btn">
            <span>🔄</span> 同步数据
          </button>
        </div>
      </div>

      <div className="data-grid">
        {/* 站点数据 */}
        <div className="data-card">
          <h3><span>📍</span> 站点数据</h3>
          <p>来自 db/migrations/客运站点.csv</p>
          <div className="data-stats">
            <div className="stat">
              <p className="stat-value">{stationData.length}</p>
              <p className="stat-label">站点数量</p>
            </div>
            <div className="stat">
              <p className="stat-value">
                {stationData.filter(s => s.station_telecode).length}
              </p>
              <p className="stat-label">有电报码</p>
            </div>
          </div>
          <div className="table-container" style={{ marginTop: '1rem', maxHeight: '200px', overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>站点ID</th>
                  <th>站点名称</th>
                  <th>站点代码</th>
                </tr>
              </thead>
              <tbody>
                {stationData.slice(0, 5).map((station) => (
                  <tr key={station.zdid}>
                    <td>{station.zdid}</td>
                    <td>{station.zdmc}</td>
                    <td>{station.station_code}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 列车数据 */}
        <div className="data-card">
          <h3><span>🚆</span> 列车数据</h3>
          <p>来自 db/migrations/列车表.csv</p>
          <div className="data-stats">
            <div className="stat">
              <p className="stat-value">{trainData.length}</p>
              <p className="stat-label">列车数量</p>
            </div>
            <div className="stat">
              <p className="stat-value">
                {trainData.reduce((sum, train) => sum + train.lcyn, 0).toLocaleString()}
              </p>
              <p className="stat-label">总运量</p>
            </div>
          </div>
          <div className="table-container" style={{ marginTop: '1rem', maxHeight: '200px', overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>列车编码</th>
                  <th>列车代码</th>
                  <th>运量</th>
                </tr>
              </thead>
              <tbody>
                {trainData.slice(0, 5).map((train) => (
                  <tr key={train.lcbm}>
                    <td>{train.lcbm}</td>
                    <td>{train.lcdm}</td>
                    <td>{train.lcyn.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 线路站点数据 */}
        <div className="data-card">
          <h3><span>🛤️</span> 线路站点数据</h3>
          <p>来自 db/migrations/运营线路客运站.csv</p>
          <div className="data-stats">
            <div className="stat">
              <p className="stat-value">{lineStationData.length}</p>
              <p className="stat-label">站点关系</p>
            </div>
            <div className="stat">
              <p className="stat-value">
                {new Set(lineStationData.map(item => item.yyxlbm)).size}
              </p>
              <p className="stat-label">线路数量</p>
            </div>
          </div>
          <div className="table-container" style={{ marginTop: '1rem', maxHeight: '200px', overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>运营线路</th>
                  <th>站点ID</th>
                  <th>站点顺序</th>
                  <th>运输距离</th>
                </tr>
              </thead>
              <tbody>
                {lineStationData.slice(0, 5).map((item) => (
                  <tr key={`${item.yyxlbm}-${item.zdid}`}>
                    <td>{item.yyxlbm}</td>
                    <td>{item.zdid}</td>
                    <td>{item.xlzdid}</td>
                    <td>{item.ysjl} km</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 客流数据 */}
        <div className="data-card">
          <h3><span>👥</span> 高铁客流数据</h3>
          <p>来自 db/migrations/高铁客运量.csv</p>
          <div className="data-stats">
            <div className="stat">
              <p className="stat-value">
                {passengerVolumeData.reduce((sum, item) => sum + item.skl + item.xkl, 0).toLocaleString()}
              </p>
              <p className="stat-label">总客流</p>
            </div>
            <div className="stat">
              <p className="stat-value">
                ¥{passengerVolumeData.reduce((sum, item) => sum + item.shouru, 0).toLocaleString()}
              </p>
              <p className="stat-label">总收入</p>
            </div>
          </div>
          <div className="table-container" style={{ marginTop: '1rem', maxHeight: '200px', overflowY: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>日期</th>
                  <th>上客量</th>
                  <th>下客量</th>
                  <th>票价</th>
                  <th>收入</th>
                </tr>
              </thead>
              <tbody>
                {passengerVolumeData.slice(0, 5).map((item, index) => (
                  <tr key={index}>
                    <td>{item.yxrq}</td>
                    <td>{item.skl}</td>
                    <td>{item.xkl}</td>
                    <td>¥{item.ticket_price}</td>
                    <td>¥{item.shouru}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );

  // 系统设置页面
  const renderSettings = () => (
    <div className="fade-in">
      <div className="main-header">
        <div className="header-title">
          <h1>系统设置</h1>
          <p>配置系统参数和个性化选项</p>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <h2><span>⚙️</span> 系统配置</h2>
        </div>
        <div style={{ display: 'grid', gap: '1.5rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>数据刷新频率</label>
            <select className="filter-select">
              <option value="5">5分钟</option>
              <option value="15">15分钟</option>
              <option value="30">30分钟</option>
              <option value="60">1小时</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>默认地图类型</label>
            <select
              className="filter-select"
              value={mapType}
              onChange={(e) => setMapType(e.target.value as GaodeMapType)}
            >
              <option value="normal">标准地图</option>
              <option value="satellite">卫星地图</option>
              <option value="roadnet">路网地图</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              <input type="checkbox" style={{ marginRight: '0.5rem' }} />
              启用实时数据推送
            </label>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 600 }}>
              <input type="checkbox" style={{ marginRight: '0.5rem' }} defaultChecked />
              显示数据动画效果
            </label>
          </div>
          <div>
            <button className="header-btn primary-btn" style={{ width: 'auto' }}>
              保存设置
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app-container">
      <Sidebar activePage={activePage} onPageChange={setActivePage} />
      <div className="main-content">
        {renderPage()}
      </div>
    </div>
  );
}

export default App;