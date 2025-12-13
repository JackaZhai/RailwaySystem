/**
 * 高德地图配置
 * 请勿在公开仓库中提交此文件，或考虑将敏感信息移至环境变量
 */

export const GAODE_MAP_CONFIG = {
  // API Key (Web服务密钥)
  API_KEY: '1b551943faa31fa72a31d9628fb07c4f',

  // 地图瓦片服务配置
  TILE_LAYER: {
    // 标准街道图
    NORMAL: {
      url: 'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
      subdomains: ['1', '2', '3', '4'],
      attribution: '高德地图'
    },
    // 卫星图
    SATELLITE: {
      url: 'https://webst0{s}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
      subdomains: ['1', '2', '3', '4'],
      attribution: '高德地图'
    },
    // 路网
    ROADNET: {
      url: 'https://webst0{s}.is.autonavi.com/appmaptile?style=7&x={x}&y={y}&z={z}',
      subdomains: ['1', '2', '3', '4'],
      attribution: '高德地图'
    }
  },

  // 默认地图中心点 (成都)
  DEFAULT_CENTER: [30.6595, 104.0659] as [number, number],

  // 默认缩放级别
  DEFAULT_ZOOM: 12,

  // 车站坐标 (成渝地区主要火车站)
  STATION_COORDINATES: {
    "成都东": [30.6329, 104.1432] as [number, number],
    "重庆北": [29.6074, 106.5509] as [number, number],
    "成都南": [30.6063, 104.0672] as [number, number],
    "重庆西": [29.4983, 106.4462] as [number, number],
    "遂宁": [30.5085, 105.5733] as [number, number],
    "内江北": [29.5850, 105.0585] as [number, number],
    "资阳北": [30.1216, 104.6519] as [number, number],
    "永川东": [29.3569, 105.8947] as [number, number],
    "隆昌北": [29.3378, 105.2750] as [number, number],
    "大足南": [29.7000, 105.7167] as [number, number],
    "荣昌北": [29.4056, 105.5944] as [number, number],
    "璧山": [29.5917, 106.2278] as [number, number],
    "沙坪坝": [29.5589, 106.4578] as [number, number],
    "简阳南": [30.3900, 104.5514] as [number, number],
    "江油": [31.7667, 104.7167] as [number, number]
  }
} as const;