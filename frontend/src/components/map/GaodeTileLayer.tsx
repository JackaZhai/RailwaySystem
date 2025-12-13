import React from 'react';
import { TileLayer } from 'react-leaflet';
import { GAODE_MAP_CONFIG } from '../../config';

export type GaodeMapType = 'normal' | 'satellite' | 'roadnet';

interface GaodeTileLayerProps {
  /** 地图类型: normal(标准街道图), satellite(卫星图), roadnet(路网图) */
  mapType?: GaodeMapType;
  /** 是否显示图层 */
  visible?: boolean;
  /** 图层透明度 0-1 */
  opacity?: number;
  /** 缩放级别范围 */
  minZoom?: number;
  maxZoom?: number;
}

/**
 * 高德地图瓦片图层组件
 * 基于Leaflet TileLayer封装的高德地图图层
 */
export const GaodeTileLayer: React.FC<GaodeTileLayerProps> = ({
  mapType = 'normal',
  visible = true,
  opacity = 1,
  minZoom = 3,
  maxZoom = 18,
}) => {
  if (!visible) {
    return null;
  }

  const tileConfig = GAODE_MAP_CONFIG.TILE_LAYER[mapType.toUpperCase() as keyof typeof GAODE_MAP_CONFIG.TILE_LAYER];

  return (
    <TileLayer
      url={tileConfig.url}
      subdomains={tileConfig.subdomains as any}
      attribution={tileConfig.attribution}
      opacity={opacity}
      minZoom={minZoom}
      maxZoom={maxZoom}
    />
  );
};

/**
 * 创建高德地图图层配置对象（用于直接传递给TileLayer组件）
 */
export const createGaodeTileLayer = (mapType: GaodeMapType = 'normal') => {
  const tileConfig = GAODE_MAP_CONFIG.TILE_LAYER[mapType.toUpperCase() as keyof typeof GAODE_MAP_CONFIG.TILE_LAYER];

  return {
    url: tileConfig.url,
    subdomains: tileConfig.subdomains,
    attribution: tileConfig.attribution,
  };
};