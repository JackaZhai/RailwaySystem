/**
 * 应用配置文件
 * 从环境变量读取配置，提供默认值
 */

// 高德地图配置
export const GAODE_MAP_CONFIG = {
  // API Key，从环境变量读取
  API_KEY: import.meta.env.VITE_GAODE_MAP_API_KEY || 'YOUR_GAODE_MAP_API_KEY',

  // 地图版本
  VERSION: '2.0',

  // 插件列表
  PLUGINS: [
    'AMap.Scale',      // 比例尺
    'AMap.ToolBar',    // 工具条
    'AMap.HawkEye',    // 鹰眼图
    'AMap.MapType',    // 地图类型切换
    'AMap.Geolocation', // 定位
    'AMap.Marker',     // 点标记
    'AMap.Polyline',   // 折线
    'AMap.InfoWindow', // 信息窗口
  ],

  // 地图样式配置
  STYLE: {
    normal: 'normal',      // 标准地图
    satellite: 'satellite', // 卫星地图
    roadnet: 'roadnet',    // 路网地图
  },

  // 默认地图中心点 (成都)
  DEFAULT_CENTER: [104.0659, 30.6595] as [number, number], // [lng, lat]

  // 默认缩放级别
  DEFAULT_ZOOM: 12,

  // 地图最小/最大缩放级别
  MIN_ZOOM: 8,
  MAX_ZOOM: 18,
}

// API配置
export const API_CONFIG = {
  // API基础URL
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',

  // 请求超时时间（毫秒）
  TIMEOUT: 30000,

  // 重试次数
  RETRY_COUNT: 3,

  // 重试延迟（毫秒）
  RETRY_DELAY: 1000,
}

// 应用配置
export const APP_CONFIG = {
  // 应用名称
  NAME: import.meta.env.VITE_APP_NAME || '铁路客运分析系统',

  // 应用版本
  VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',

  // 应用描述
  DESCRIPTION: '成渝地区铁路客运分析与可视化系统',

  // 默认语言
  DEFAULT_LANGUAGE: 'zh',

  // 支持的语言列表
  SUPPORTED_LANGUAGES: ['zh', 'en'] as const,

  // 默认主题
  DEFAULT_THEME: 'light' as 'light' | 'dark',

  // 主题色
  PRIMARY_COLOR: '#0066cc',
  SECONDARY_COLOR: '#00aaff',
  SUCCESS_COLOR: '#00c853',
  WARNING_COLOR: '#ff9800',
  ERROR_COLOR: '#f44336',
  INFO_COLOR: '#2196f3',
}

// 图表配置
export const CHART_CONFIG = {
  // 默认颜色方案
  COLOR_SCHEME: [
    '#0066cc', '#00aaff', '#00c853', '#ff9800', '#f44336',
    '#2196f3', '#9c27b0', '#3f51b5', '#009688', '#ff5722',
  ],

  // 动画配置
  ANIMATION: {
    duration: 1000,
    easing: 'cubicOut' as const,
  },

  // 响应式断点
  RESPONSIVE_BREAKPOINTS: {
    xs: 480,
    sm: 768,
    md: 992,
    lg: 1200,
    xl: 1600,
  },
}

// 地图默认车站坐标（成渝地区主要火车站）
export const DEFAULT_STATIONS = [
  { id: 1001, name: '成都东', lng: 104.1432, lat: 30.6332, type: 'high_speed' },
  { id: 1002, name: '重庆北', lng: 106.5507, lat: 29.6085, type: 'high_speed' },
  { id: 1003, name: '成都南', lng: 104.0704, lat: 30.6069, type: 'high_speed' },
  { id: 1004, name: '重庆西', lng: 106.4354, lat: 29.5018, type: 'high_speed' },
  { id: 1005, name: '内江北', lng: 105.0677, lat: 29.5802, type: 'high_speed' },
  { id: 1006, name: '永川东', lng: 105.9271, lat: 29.3569, type: 'high_speed' },
  { id: 1007, name: '资阳北', lng: 104.6579, lat: 30.1260, type: 'high_speed' },
  { id: 1008, name: '大足南', lng: 105.7153, lat: 29.7005, type: 'high_speed' },
  { id: 1009, name: '荣昌北', lng: 105.5945, lat: 29.4056, type: 'high_speed' },
  { id: 1010, name: '璧山', lng: 106.2273, lat: 29.5920, type: 'high_speed' },
  { id: 1011, name: '简阳南', lng: 104.5513, lat: 30.3905, type: 'high_speed' },
  { id: 1012, name: '潼南', lng: 105.8401, lat: 30.1911, type: 'high_speed' },
  { id: 1013, name: '合川', lng: 106.2760, lat: 29.9720, type: 'high_speed' },
  { id: 1014, name: '遂宁', lng: 105.5733, lat: 30.5088, type: 'high_speed' },
  { id: 1015, name: '南充北', lng: 106.0836, lat: 30.7994, type: 'high_speed' },
]

// 环境变量检查
export function checkEnvVariables() {
  const requiredEnvVars = [
    'VITE_GAODE_MAP_API_KEY',
    'VITE_API_BASE_URL',
  ]

  const missingVars = requiredEnvVars.filter(
    varName => !import.meta.env[varName]
  )

  if (missingVars.length > 0) {
    console.warn('缺少以下环境变量:', missingVars)
    console.warn('请检查 .env 文件配置')
  }

  return missingVars.length === 0
}

// 默认导出
export default {
  GAODE_MAP_CONFIG,
  API_CONFIG,
  APP_CONFIG,
  CHART_CONFIG,
  DEFAULT_STATIONS,
  checkEnvVariables,
}