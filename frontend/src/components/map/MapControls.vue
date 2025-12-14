<script setup lang="ts">
import { computed } from 'vue'
import { useMapStore } from '@/stores/map'

const mapStore = useMapStore()

// 地图类型选项
const mapTypeOptions = [
  { value: 'normal', label: '标准地图', icon: 'map' },
  { value: 'satellite', label: '卫星地图', icon: 'satellite' },
  { value: 'roadnet', label: '路网地图', icon: 'road' },
]

// 计算当前地图类型标签
const currentMapTypeLabel = computed(() => {
  const option = mapTypeOptions.find(opt => opt.value === mapStore.mapConfig.mapType)
  return option?.label || '标准地图'
})

// 切换地图类型
const toggleMapType = () => {
  mapStore.toggleMapType()
}

// 定位到用户位置
const locateUser = () => {
  if (!navigator.geolocation) {
    alert('您的浏览器不支持地理定位')
    return
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords
      mapStore.updateViewState({
        center: [longitude, latitude],
        zoom: 15,
      })
    },
    (error) => {
      console.error('定位失败:', error)
      alert('定位失败，请检查浏览器权限')
    },
    {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0,
    }
  )
}

// 重置视图
const resetView = () => {
  mapStore.resetView()
}

// 放大
const zoomIn = () => {
  mapStore.updateViewState({
    zoom: Math.min(mapStore.mapConfig.maxZoom, mapStore.viewState.zoom + 1),
  })
}

// 缩小
const zoomOut = () => {
  mapStore.updateViewState({
    zoom: Math.max(mapStore.mapConfig.minZoom, mapStore.viewState.zoom - 1),
  })
}

// 切换交通状况
const toggleTraffic = () => {
  mapStore.toggleTraffic()
}

// 切换标记显示
const toggleMarkers = () => {
  mapStore.toggleStationMarkers()
}

// 切换流向线显示
const toggleFlowLines = () => {
  mapStore.toggleFlowLines()
}

// 切换热力图显示
const toggleHeatmap = () => {
  mapStore.toggleHeatmap()
}
</script>

<template>
  <div class="map-controls">
    <!-- 地图类型切换 -->
    <div class="control-group">
      <button
        :title="`切换地图类型 (当前: ${currentMapTypeLabel})`"
        class="control-button"
        @click="toggleMapType"
      >
        <span class="control-icon">🗺️</span>
        <span class="control-label">{{ currentMapTypeLabel }}</span>
      </button>
    </div>

    <!-- 缩放控制 -->
    <div class="control-group">
      <button title="放大" class="control-button" @click="zoomIn">
        <span class="control-icon">➕</span>
        <span class="control-label">放大</span>
      </button>
      <button title="缩小" class="control-button" @click="zoomOut">
        <span class="control-icon">➖</span>
        <span class="control-label">缩小</span>
      </button>
      <button title="重置视图" class="control-button" @click="resetView">
        <span class="control-icon">↺</span>
        <span class="control-label">重置</span>
      </button>
    </div>

    <!-- 定位控制 -->
    <div class="control-group">
      <button title="定位到我的位置" class="control-button" @click="locateUser">
        <span class="control-icon">📍</span>
        <span class="control-label">定位</span>
      </button>
    </div>

    <!-- 图层控制 -->
    <div class="control-group">
      <button
        :title="`${mapStore.mapConfig.showTraffic ? '隐藏' : '显示'}交通状况`"
        class="control-button"
        :class="{ active: mapStore.mapConfig.showTraffic }"
        @click="toggleTraffic"
      >
        <span class="control-icon">🚦</span>
        <span class="control-label">交通</span>
      </button>
      <button
        :title="`${mapStore.mapConfig.showStationMarkers ? '隐藏' : '显示'}车站标记`"
        class="control-button"
        :class="{ active: mapStore.mapConfig.showStationMarkers }"
        @click="toggleMarkers"
      >
        <span class="control-icon">📍</span>
        <span class="control-label">标记</span>
      </button>
      <button
        :title="`${mapStore.mapConfig.showFlowLines ? '隐藏' : '显示'}流向线`"
        class="control-button"
        :class="{ active: mapStore.mapConfig.showFlowLines }"
        @click="toggleFlowLines"
      >
        <span class="control-icon">↕️</span>
        <span class="control-label">流向</span>
      </button>
      <button
        :title="`${mapStore.mapConfig.showHeatmap ? '隐藏' : '显示'}热力图`"
        class="control-button"
        :class="{ active: mapStore.mapConfig.showHeatmap }"
        @click="toggleHeatmap"
      >
        <span class="control-icon">🔥</span>
        <span class="control-label">热力</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.map-controls {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
  background-color: white;
  border-radius: 6px;
  padding: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.control-button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  color: #333;
  transition: all 0.2s;
  min-width: 100px;
  text-align: left;
}

.control-button:hover {
  background-color: #f5f5f5;
  border-color: #0066cc;
}

.control-button.active {
  background-color: #e6f2ff;
  border-color: #0066cc;
  color: #0066cc;
}

.control-icon {
  font-size: 16px;
  line-height: 1;
}

.control-label {
  flex: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .map-controls {
    top: 8px;
    right: 8px;
  }

  .control-button {
    min-width: auto;
    padding: 6px 8px;
    font-size: 12px;
  }

  .control-label {
    display: none;
  }
}
</style>