import React, { useState } from 'react';
import { useMap } from 'react-leaflet';
import { GaodeMapType } from './GaodeTileLayer';

interface MapControlsProps {
  /** 当前地图类型 */
  currentMapType: GaodeMapType;
  /** 地图类型切换回调 */
  onMapTypeChange: (mapType: GaodeMapType) => void;
  /** 是否显示缩放控制 */
  showZoomControl?: boolean;
  /** 是否显示定位按钮 */
  showLocateControl?: boolean;
}

/**
 * 地图控制组件
 * 提供地图图层切换、缩放控制等功能
 */
export const MapControls: React.FC<MapControlsProps> = ({
  currentMapType,
  onMapTypeChange,
  showZoomControl = true,
  showLocateControl = true,
}) => {
  const map = useMap();
  const [isLocating, setIsLocating] = useState(false);

  const handleLocate = () => {
    if (!navigator.geolocation) {
      alert('您的浏览器不支持定位功能');
      return;
    }

    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        map.flyTo([latitude, longitude], 15);
        setIsLocating(false);
      },
      (error) => {
        console.error('定位失败:', error);
        alert(`定位失败: ${error.message}`);
        setIsLocating(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );
  };

  const mapTypes: Array<{ value: GaodeMapType; label: string }> = [
    { value: 'normal', label: '标准地图' },
    { value: 'satellite', label: '卫星地图' },
    { value: 'roadnet', label: '路网地图' },
  ];

  return (
    <div
      className="leaflet-control leaflet-bar map-controls"
      style={{
        background: 'white',
        borderRadius: '4px',
        boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
        padding: '5px',
        display: 'flex',
        flexDirection: 'column',
        gap: '5px',
      }}
    >
      {/* 图层切换 */}
      <div style={{ display: 'flex', gap: '2px' }}>
        {mapTypes.map((type) => (
          <button
            key={type.value}
            style={{
              padding: '4px 8px',
              border: '1px solid #ddd',
              background: currentMapType === type.value ? '#2563eb' : '#f8f9fa',
              color: currentMapType === type.value ? 'white' : 'inherit',
              borderColor: currentMapType === type.value ? '#2563eb' : '#ddd',
              cursor: 'pointer',
              fontSize: '12px',
              whiteSpace: 'nowrap',
            }}
            onClick={() => onMapTypeChange(type.value)}
            title={`切换到${type.label}`}
            onMouseEnter={(e) => {
              if (currentMapType !== type.value) {
                e.currentTarget.style.background = '#e9ecef';
              }
            }}
            onMouseLeave={(e) => {
              if (currentMapType !== type.value) {
                e.currentTarget.style.background = '#f8f9fa';
              }
            }}
          >
            {type.label}
          </button>
        ))}
      </div>

      {/* 缩放控制 */}
      {showZoomControl && (
        <div style={{ display: 'flex', gap: '2px' }}>
          <button
            style={{
              width: '26px',
              height: '26px',
              border: '1px solid #ddd',
              background: 'white',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '14px',
            }}
            onClick={() => map.zoomIn()}
            title="放大"
            onMouseEnter={(e) => (e.currentTarget.style.background = '#f8f9fa')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'white')}
          >
            +
          </button>
          <button
            style={{
              width: '26px',
              height: '26px',
              border: '1px solid #ddd',
              background: 'white',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '14px',
            }}
            onClick={() => map.zoomOut()}
            title="缩小"
            onMouseEnter={(e) => (e.currentTarget.style.background = '#f8f9fa')}
            onMouseLeave={(e) => (e.currentTarget.style.background = 'white')}
          >
            -
          </button>
        </div>
      )}

      {/* 定位按钮 */}
      {showLocateControl && (
        <button
          style={{
            padding: '4px 8px',
            border: '1px solid #ddd',
            background: 'white',
            cursor: isLocating ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            opacity: isLocating ? 0.5 : 1,
          }}
          onClick={handleLocate}
          title="定位到我的位置"
          disabled={isLocating}
          onMouseEnter={(e) => {
            if (!isLocating) e.currentTarget.style.background = '#f8f9fa';
          }}
          onMouseLeave={(e) => {
            if (!isLocating) e.currentTarget.style.background = 'white';
          }}
        >
          {isLocating ? '定位中...' : '📍'}
        </button>
      )}
    </div>
  );
};