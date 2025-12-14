<template>
  <div class="dashboard animate-fade-in">
    <!-- 全局加载状态 -->
    <LoadingSpinner
      v-if="isLoading"
      size="large"
      variant="primary"
      text="正在加载数据..."
      fullscreen
    />

    <!-- 页面标题和操作 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">总览</h1>
        <p class="page-description">系统核心指标和实时监控</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary touch-target touch-feedback" @click="refreshData" :disabled="isRefreshing">
          <svg v-if="!isRefreshing" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else class="animate-spin" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2V6M12 18V22M4.93 4.93L7.76 7.76M16.24 16.24L19.07 19.07M2 12H6M18 12H22M4.93 19.07L7.76 16.24M16.24 7.76L19.07 4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ isRefreshing ? '刷新中...' : '刷新数据' }}
        </button>
        <button class="btn btn-outline touch-target touch-feedback">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 16.5L12 21.75L21 16.5M3 12L12 17.25L21 12M3 7.5L12 12.75L21 7.5L12 2.25L3 7.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          导出报告
        </button>
      </div>
    </div>

    <!-- 时间筛选 -->
    <div class="time-filter animate-fade-in">
      <div class="filter-container">
        <div class="filter-group">
          <label class="filter-label">时间范围</label>
          <div class="filter-buttons">
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'today' }"
              @click="selectTimeRange('today')"
            >
              今天
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'week' }"
              @click="selectTimeRange('week')"
            >
              本周
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'month' }"
              @click="selectTimeRange('month')"
            >
              本月
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'quarter' }"
              @click="selectTimeRange('quarter')"
            >
              本季度
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'year' }"
              @click="selectTimeRange('year')"
            >
              本年
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'custom' }"
              @click="selectTimeRange('custom')"
            >
              自定义
            </button>
          </div>
        </div>
        <div class="date-picker" v-if="selectedRange === 'custom'">
          <input
            v-model="startDate"
            type="date"
            class="date-input"
            @change="updateCustomDateRange"
          />
          <span class="date-separator">至</span>
          <input
            v-model="endDate"
            type="date"
            class="date-input"
            @change="updateCustomDateRange"
          />
        </div>
        <div class="filter-stats" v-if="selectedRange !== 'custom'">
          <span class="stat-label">统计周期：</span>
          <span class="stat-value">{{ timeRangeLabel }}</span>
          <span class="stat-duration">（{{ timeRangeDuration }}）</span>
        </div>
      </div>
    </div>

    <!-- KPI指标卡片 -->
    <div class="kpi-grid">
      <!-- 总客流量卡片 -->
      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon total-passengers">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 11C11.2091 11 13 9.20914 13 7C13 4.79086 11.2091 3 9 3C6.79086 3 5 4.79086 5 7C5 9.20914 6.79086 11 9 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.totalPassengers >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.totalPassengers >= 0 ? '+' : '' }}{{ kpiData.trends.totalPassengers }}%</span>
            <svg v-if="kpiData.trends.totalPassengers >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-content">
          <template v-if="!isLoading">
            <h3 class="kpi-value">
              <AnimatedNumber :value="kpiData.totalPassengers" :duration="1500" :animate="true" />
            </h3>
            <p class="kpi-label">总客流量</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">今日累计</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon total-trains">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 19C9 19.7956 9.31607 20.5587 9.87868 21.1213C10.4413 21.6839 11.2044 22 12 22C12.7956 22 13.5587 21.6839 14.1213 21.1213C14.6839 20.5587 15 19.7956 15 19M9 19C9 18.2044 9.31607 17.4413 9.87868 16.8787C10.4413 16.3161 11.2044 16 12 16C12.7956 16 13.5587 16.3161 14.1213 16.8787C14.6839 17.4413 15 18.2044 15 19M9 19H3V13C3 11.1435 3.7375 9.36301 5.05025 8.05025C6.36301 6.7375 8.14348 6 10 6H14C15.8565 6 17.637 6.7375 18.9497 8.05025C20.2625 9.36301 21 11.1435 21 13V19H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8 12H8.01M12 12H12.01M16 12H16.01M9 12C9 12.5523 8.55228 13 8 13C7.44772 13 7 12.5523 7 12C7 11.4477 7.44772 11 8 11C8.55228 11 9 11.4477 9 12ZM13 12C13 12.5523 12.5523 13 12 13C11.4477 13 11 12.5523 11 12C11 11.4477 11.4477 11 12 11C12.5523 11 13 11.4477 13 12ZM17 12C17 12.5523 16.5523 13 16 13C15.4477 13 15 12.5523 15 12C15 11.4477 15.4477 11 16 11C16.5523 11 17 11.4477 17 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.totalTrains >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.totalTrains >= 0 ? '+' : '' }}{{ kpiData.trends.totalTrains }}%</span>
            <svg v-if="kpiData.trends.totalTrains >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-content">
          <template v-if="!isLoading">
            <h3 class="kpi-value">
              <AnimatedNumber :value="kpiData.totalTrains" :duration="1200" :animate="true" />
            </h3>
            <p class="kpi-label">运营车次</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">今日累计</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon busy-stations">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 11C13.1046 11 14 10.1046 14 9C14 7.89543 13.1046 7 12 7C10.8954 7 10 7.89543 10 9C10 10.1046 10.8954 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.busyStations >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.busyStations >= 0 ? '+' : '' }}{{ kpiData.trends.busyStations }}%</span>
            <svg v-if="kpiData.trends.busyStations >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-content">
          <template v-if="!isLoading">
            <h3 class="kpi-value">
              <AnimatedNumber :value="kpiData.busyStations" :duration="1000" :animate="true" />
            </h3>
            <p class="kpi-label">繁忙站点</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">活跃站点数</span>
        </div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon revenue">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 1V23M17 5H9.5C8.57174 5 7.6815 5.36875 7.02513 6.02513C6.36875 6.6815 6 7.57174 6 8.5C6 9.42826 6.36875 10.3185 7.02513 10.9749C7.6815 11.6313 8.57174 12 9.5 12H14.5C15.4283 12 16.3185 12.3687 16.9749 13.0251C17.6313 13.6815 18 14.5717 18 15.5C18 16.4283 17.6313 17.3185 16.9749 17.9749C16.3185 18.6313 15.4283 19 14.5 19H6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.totalRevenue >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.totalRevenue >= 0 ? '+' : '' }}{{ kpiData.trends.totalRevenue }}%</span>
            <svg v-if="kpiData.trends.totalRevenue >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-content">
          <template v-if="!isLoading">
            <h3 class="kpi-value">
              ¥<AnimatedNumber :value="kpiData.totalRevenue" :duration="1800" :animate="true" />
            </h3>
            <p class="kpi-label">总收入</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">今日累计</span>
        </div>
      </div>
    </div>

    <!-- 主要图表区域 -->
    <div class="chart-grid">
      <!-- 地图区域 -->
      <div class="chart-card map-card">
        <div class="card-header">
          <h3 class="card-title">客流空间分布</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: mapViewMode === 'heatmap' }"
              @click="changeMapViewMode('heatmap')"
            >
              热力图
            </button>
            <button
              class="card-action-btn"
              :class="{ active: mapViewMode === 'flow' }"
              @click="changeMapViewMode('flow')"
            >
              流向图
            </button>
            <button
              class="card-action-btn"
              :class="{ active: mapViewMode === 'markers' }"
              @click="changeMapViewMode('markers')"
            >
              站点标记
            </button>
          </div>
        </div>
        <div class="card-body">
          <!-- 热力图模式 -->
          <div v-if="mapViewMode === 'heatmap'" class="heatmap-container">
            <HeatMapChart
              title="站点客流热力图"
              :data="heatmapData"
            />
          </div>

          <!-- 流向图模式 -->
          <div v-if="mapViewMode === 'flow'" class="flow-container">
            <div class="flow-placeholder">
              <div class="flow-mock">
                <div class="flow-map">
                  <div class="flow-grid">
                    <div v-for="i in 10" :key="i" class="grid-line"></div>
                  </div>
                  <div
                    v-for="flow in flowData"
                    :key="flow.id"
                    class="flow-line"
                    :style="flow.style"
                  >
                    <div class="flow-arrow"></div>
                    <div class="flow-label">{{ flow.label }}</div>
                  </div>
                </div>
                <div class="flow-legend">
                  <div class="legend-item">
                    <div class="legend-line high"></div>
                    <span>高流量</span>
                  </div>
                  <div class="legend-item">
                    <div class="legend-line medium"></div>
                    <span>中流量</span>
                  </div>
                  <div class="legend-item">
                    <div class="legend-line low"></div>
                    <span>低流量</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 站点标记模式 -->
          <div v-if="mapViewMode === 'markers'" class="station-map-container">
            <StationMap
              title="成渝地区铁路站点分布"
            />
          </div>
        </div>
      </div>

      <!-- 客流趋势图 -->
      <div class="chart-card">
        <div class="card-body">
          <TrendChart
            title="客流趋势分析"
          />
        </div>
      </div>

      <!-- 客流量分析 -->
      <div class="chart-card">
        <div class="card-body">
          <PassengerFlowAnalysis
            title="客流量深度分析"
          />
        </div>
      </div>

      <!-- 线路负载分析 -->
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">线路负载分析</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: loadMetric === 'occupancy' }"
              @click="changeLoadMetric('occupancy')"
            >
              上座率
            </button>
            <button
              class="card-action-btn"
              :class="{ active: loadMetric === 'load' }"
              @click="changeLoadMetric('load')"
            >
              满载率
            </button>
            <button
              class="card-action-btn"
              :class="{ active: loadMetric === 'efficiency' }"
              @click="changeLoadMetric('efficiency')"
            >
              运营效率
            </button>
          </div>
        </div>
        <div class="card-body">
          <div class="load-analysis">
            <div class="load-chart">
              <div class="chart-container">
                <div class="load-bars">
                  <div
                    v-for="line in (lineLoads.length > 0 ? lineLoads : lineLoadsData)"
                    :key="line.id"
                    class="load-bar-item"
                    @mouseenter="showLineTooltip(line)"
                    @mouseleave="hideLineTooltip"
                  >
                    <div class="bar-label">
                      <div class="line-name">{{ line.name }}</div>
                      <div class="line-code">{{ line.code }}</div>
                    </div>
                    <div class="bar-container">
                      <div class="bar-track">
                        <div
                          class="bar-fill"
                          :style="{ width: getLineMetric(line) + '%' }"
                          :class="getLoadStatusClass(getLineMetric(line))"
                        >
                          <span class="bar-value">{{ getLineMetric(line) }}%</span>
                        </div>
                      </div>
                      <div class="bar-comparison">
                        <div class="comparison-label">行业平均</div>
                        <div class="comparison-bar">
                          <div class="comparison-fill" :style="{ width: line.industryAverage + '%' }"></div>
                        </div>
                        <div class="comparison-value">{{ line.industryAverage }}%</div>
                      </div>
                    </div>
                    <div class="bar-stats">
                      <div class="stat">
                        <div class="stat-label">上座率</div>
                        <div class="stat-value">{{ line.occupancyRate }}%</div>
                      </div>
                      <div class="stat">
                        <div class="stat-label">满载率</div>
                        <div class="stat-value">{{ line.loadRate }}%</div>
                      </div>
                      <div class="stat">
                        <div class="stat-label">运营效率</div>
                        <div class="stat-value">{{ line.efficiency }}%</div>
                      </div>
                    </div>
                    <div class="bar-trend" :class="line.trend >= 0 ? 'positive' : 'negative'">
                      <span>{{ line.trend >= 0 ? '+' : '' }}{{ line.trend }}%</span>
                      <svg v-if="line.trend >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                      <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="load-summary">
              <div class="summary-card">
                <div class="summary-value">{{ avgOccupancyRate }}%</div>
                <div class="summary-label">平均上座率</div>
                <div class="summary-trend" :class="avgOccupancyTrend >= 0 ? 'positive' : 'negative'">
                  <span>{{ avgOccupancyTrend >= 0 ? '+' : '' }}{{ avgOccupancyTrend }}%</span>
                  <svg v-if="avgOccupancyTrend >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-value">{{ avgLoadRate }}%</div>
                <div class="summary-label">平均满载率</div>
                <div class="summary-trend" :class="avgLoadTrend >= 0 ? 'positive' : 'negative'">
                  <span>{{ avgLoadTrend >= 0 ? '+' : '' }}{{ avgLoadTrend }}%</span>
                  <svg v-if="avgLoadTrend >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
              <div class="summary-card">
                <div class="summary-value">{{ peakLine.name }}</div>
                <div class="summary-label">最高负载线路</div>
                <div class="summary-detail">{{ peakLine.value }}%</div>
              </div>
              <div class="summary-card">
                <div class="summary-value">{{ optimizationPotential }}%</div>
                <div class="summary-label">优化潜力</div>
                <div class="summary-detail">可提升空间</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 线路负载工具提示 -->
      <div
        v-if="lineTooltip.visible"
        class="line-tooltip"
        :style="lineTooltipStyle"
      >
        <div class="tooltip-header">
          <strong>{{ lineTooltip.line.name }} ({{ lineTooltip.line.code }})</strong>
        </div>
        <div class="tooltip-content">
          <div class="tooltip-row">
            <span class="tooltip-label">上座率：</span>
            <span class="tooltip-value">{{ lineTooltip.line.occupancyRate }}%</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">满载率：</span>
            <span class="tooltip-value">{{ lineTooltip.line.loadRate }}%</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">运营效率：</span>
            <span class="tooltip-value">{{ lineTooltip.line.efficiency }}%</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">行业平均：</span>
            <span class="tooltip-value">{{ lineTooltip.line.industryAverage }}%</span>
          </div>
          <div class="tooltip-row">
            <span class="tooltip-label">趋势：</span>
            <span class="tooltip-value" :class="lineTooltip.line.trend >= 0 ? 'positive' : 'negative'">
              {{ lineTooltip.line.trend >= 0 ? '+' : '' }}{{ lineTooltip.line.trend }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="data-table-section">
      <div class="section-header">
        <h3 class="section-title">实时数据</h3>
        <div class="section-actions">
          <button class="btn btn-outline btn-sm">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            导出CSV
          </button>
          <button class="btn btn-primary btn-sm">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 12V7H3V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M3 17H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 12V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M15 12V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            查看详情
          </button>
        </div>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>车次</th>
              <th>出发站</th>
              <th>到达站</th>
              <th>出发时间</th>
              <th>到达时间</th>
              <th>上座率</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="train in recentTrains" :key="train.id">
              <td>
                <div class="train-code">{{ train.code }}</div>
                <div class="train-type">{{ train.type }}</div>
              </td>
              <td>{{ train.departureStation }}</td>
              <td>{{ train.arrivalStation }}</td>
              <td>{{ train.departureTime }}</td>
              <td>{{ train.arrivalTime }}</td>
              <td>
                <div class="occupancy">
                  <div class="occupancy-bar">
                    <div class="occupancy-fill" :style="{ width: train.occupancy + '%' }"></div>
                  </div>
                  <span class="occupancy-percentage">{{ train.occupancy }}%</span>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="train.status">{{ train.statusText }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <div class="pagination">
          <button class="pagination-btn" :disabled="currentPage === 1">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <span class="pagination-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
          <button class="pagination-btn" :disabled="currentPage === totalPages">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AnimatedNumber from '@/components/ui/AnimatedNumber.vue'
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'
import HeatMapChart from '@/components/charts/HeatMapChart.vue'
import StationMap from '@/components/maps/StationMap.vue'
import TrendChart from '@/components/charts/TrendChart.vue'
import PassengerFlowAnalysis from '@/components/analytics/PassengerFlowAnalysis.vue'
import { dataService, type TimeRange, type KpiData, type Station, type Line, type TrendData, type TimePeriodData } from '@/services/api'

// 时间范围筛选
const selectedRange = ref<'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom'>('today')
const startDate = ref('')
const endDate = ref('')

// 计算时间范围标签
const timeRangeLabel = computed(() => {
  const now = new Date()
  switch (selectedRange.value) {
    case 'today':
      return now.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' })
    case 'week':
      const weekStart = new Date(now.setDate(now.getDate() - now.getDay()))
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      return `${weekStart.getMonth() + 1}月${weekStart.getDate()}日 - ${weekEnd.getMonth() + 1}月${weekEnd.getDate()}日`
    case 'month':
      return `${now.getMonth() + 1}月`
    case 'quarter':
      const quarter = Math.floor(now.getMonth() / 3) + 1
      return `第${quarter}季度`
    case 'year':
      return `${now.getFullYear()}年`
    default:
      return '自定义范围'
  }
})

// 计算时间范围时长
const timeRangeDuration = computed(() => {
  switch (selectedRange.value) {
    case 'today':
      return '1天'
    case 'week':
      return '7天'
    case 'month':
      const now = new Date()
      const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
      return `${daysInMonth}天`
    case 'quarter':
      return '约90天'
    case 'year':
      return '365天'
    default:
      if (startDate.value && endDate.value) {
        const start = new Date(startDate.value)
        const end = new Date(endDate.value)
        const diffTime = Math.abs(end.getTime() - start.getTime())
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
        return `${diffDays}天`
      }
      return '请选择日期'
  }
})

// 选择时间范围
const selectTimeRange = (range: typeof selectedRange.value) => {
  selectedRange.value = range
  const now = new Date()

  switch (range) {
    case 'today':
      startDate.value = now.toISOString().split('T')[0]
      endDate.value = now.toISOString().split('T')[0]
      break
    case 'week':
      const weekStart = new Date(now.setDate(now.getDate() - now.getDay()))
      startDate.value = weekStart.toISOString().split('T')[0]
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      endDate.value = weekEnd.toISOString().split('T')[0]
      break
    case 'month':
      const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
      startDate.value = monthStart.toISOString().split('T')[0]
      const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0)
      endDate.value = monthEnd.toISOString().split('T')[0]
      break
    case 'quarter':
      const quarter = Math.floor(now.getMonth() / 3)
      const quarterStart = new Date(now.getFullYear(), quarter * 3, 1)
      startDate.value = quarterStart.toISOString().split('T')[0]
      const quarterEnd = new Date(now.getFullYear(), (quarter + 1) * 3, 0)
      endDate.value = quarterEnd.toISOString().split('T')[0]
      break
    case 'year':
      const yearStart = new Date(now.getFullYear(), 0, 1)
      startDate.value = yearStart.toISOString().split('T')[0]
      const yearEnd = new Date(now.getFullYear(), 11, 31)
      endDate.value = yearEnd.toISOString().split('T')[0]
      break
    case 'custom':
      // 保持当前日期选择
      break
  }

  // 触发数据更新
  updateDataByTimeRange()
}

// 更新自定义日期范围
const updateCustomDateRange = () => {
  if (startDate.value && endDate.value) {
    selectedRange.value = 'custom'
    updateDataByTimeRange()
  }
}

// 根据时间范围更新数据
const updateDataByTimeRange = () => {
  console.log('更新数据，时间范围:', selectedRange.value, '开始日期:', startDate.value, '结束日期:', endDate.value)
  // 加载对应时间范围的数据
  loadData()
}

// 地图视图模式
const mapViewMode = ref<'heatmap' | 'flow' | 'markers'>('markers')

// 热力图数据
const heatmapData = computed(() => {
  // 生成模拟热力图数据
  const stations = ['成都东', '重庆北', '内江北', '资阳北', '永川东']
  const times = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']

  return stations.map((station, rowIndex) => {
    return times.map((time, colIndex) => {
      const baseValue = 1000 + Math.random() * 5000
      const timeFactor = colIndex < 2 ? 0.3 : colIndex < 4 ? 0.7 : 1.0
      const stationFactor = rowIndex < 2 ? 1.2 : rowIndex < 4 ? 0.8 : 1.0
      const value = Math.round(baseValue * timeFactor * stationFactor)

      return {
        value,
        time,
        label: `${station}站`
      }
    })
  })
})

// 流向图数据
const flowData = ref([
  { id: 1, label: '成都→重庆', style: 'left: 30%; top: 40%; width: 30%; transform: rotate(30deg);', intensity: 'high' },
  { id: 2, label: '重庆→成都', style: 'left: 60%; top: 60%; width: 30%; transform: rotate(210deg);', intensity: 'high' },
  { id: 3, label: '内江→资阳', style: 'left: 40%; top: 50%; width: 15%; transform: rotate(45deg);', intensity: 'medium' },
  { id: 4, label: '资阳→内江', style: 'left: 35%; top: 45%; width: 15%; transform: rotate(225deg);', intensity: 'medium' },
  { id: 5, label: '永川→荣昌', style: 'left: 55%; top: 55%; width: 10%; transform: rotate(60deg);', intensity: 'low' },
  { id: 6, label: '荣昌→永川', style: 'left: 50%; top: 58%; width: 10%; transform: rotate(240deg);', intensity: 'low' }
])

// 切换地图视图模式
const changeMapViewMode = (mode: 'heatmap' | 'flow' | 'markers') => {
  mapViewMode.value = mode
}

// 初始化时间范围
onMounted(() => {
  selectTimeRange('today')
})

// KPI数据
const kpiData = ref<KpiData>({
  totalPassengers: 0,
  totalTrains: 0,
  busyStations: 0,
  totalRevenue: 0,
  trends: {
    totalPassengers: 0,
    totalTrains: 0,
    busyStations: 0,
    totalRevenue: 0
  }
})

// 加载状态
const isLoading = ref(false)
const isRefreshing = ref(false)

// 获取当前时间范围
const getCurrentTimeRange = (): TimeRange => {
  return {
    startDate: startDate.value,
    endDate: endDate.value,
    rangeType: selectedRange.value
  }
}

// 加载数据
const loadData = async () => {
  try {
    isLoading.value = true
    const timeRange = getCurrentTimeRange()

    // 并行加载所有数据
    const [kpiResponse, stationsResponse, linesResponse, trendResponse, timePeriodResponse] = await Promise.all([
      dataService.getKpiData(timeRange),
      dataService.getStations(timeRange),
      dataService.getLines(timeRange),
      dataService.getTrendData(timeRange, 'hourly'),
      dataService.getTimePeriodData(timeRange)
    ])

    // 更新数据
    kpiData.value = kpiResponse
    stationsData.value = stationsResponse
    lineLoads.value = linesResponse
    trendData.value = trendResponse
    timePeriodsData.value = timePeriodResponse

  } catch (error) {
    console.error('加载数据失败:', error)
    // 保持模拟数据作为回退
  } finally {
    isLoading.value = false
  }
}

// 刷新数据
const refreshData = async () => {
  if (isRefreshing.value) return

  isRefreshing.value = true

  try {
    const timeRange = getCurrentTimeRange()

    // 调用API刷新数据
    await dataService.refreshData(timeRange)

    // 重新加载数据
    await loadData()
  } catch (error) {
    console.error('刷新数据失败:', error)
    // 可以在这里添加用户友好的错误提示
  } finally {
    isRefreshing.value = false
  }
}

// 初始加载
onMounted(() => {
  loadData()
})

// 模拟数据 - 地图站点
const mockStations = ref([
  { id: 1, name: '成都', size: 'large', style: 'left: 30%; top: 40%;' },
  { id: 2, name: '重庆', size: 'large', style: 'left: 60%; top: 60%;' },
  { id: 3, name: '内江', size: 'medium', style: 'left: 40%; top: 50%;' },
  { id: 4, name: '资阳', size: 'small', style: 'left: 35%; top: 45%;' },
  { id: 5, name: '永川', size: 'small', style: 'left: 55%; top: 55%;' },
  { id: 6, name: '荣昌', size: 'small', style: 'left: 50%; top: 58%;' }
])

// 模拟数据 - 趋势图（已移除，使用API数据）

// 模拟数据 - 站点排名
const topStations = ref([
  { id: 1, rank: 1, name: '成都东站', code: 'CDW', count: 125678, percentage: 100 },
  { id: 2, rank: 2, name: '重庆北站', code: 'CUW', count: 98765, percentage: 78 },
  { id: 3, rank: 3, name: '内江北站', code: 'NKW', count: 65432, percentage: 52 },
  { id: 4, rank: 4, name: '资阳北站', code: 'ZYW', count: 54321, percentage: 43 },
  { id: 5, rank: 5, name: '永川东站', code: 'YCW', count: 43210, percentage: 34 }
])

// 线路负载分析
const loadMetric = ref<'occupancy' | 'load' | 'efficiency'>('occupancy')

// 数据变量
const stationsData = ref<Station[]>([])
const lineLoads = ref<Line[]>([])
const trendData = ref<TrendData[]>([])
const timePeriodsData = ref<TimePeriodData[]>([])

// 线路负载数据（回退数据）
const lineLoadsData = ref<Line[]>([
  {
    id: 1,
    name: '成渝高铁',
    code: 'CYG',
    occupancyRate: 92,
    loadRate: 85,
    efficiency: 88,
    industryAverage: 75,
    trend: 15.2,
    status: 'high'
  },
  {
    id: 2,
    name: '渝贵铁路',
    code: 'YGR',
    occupancyRate: 78,
    loadRate: 72,
    efficiency: 75,
    industryAverage: 70,
    trend: 8.7,
    status: 'medium'
  },
  {
    id: 3,
    name: '成贵高铁',
    code: 'CGG',
    occupancyRate: 65,
    loadRate: 58,
    efficiency: 62,
    industryAverage: 65,
    trend: 6.3,
    status: 'medium'
  },
  {
    id: 4,
    name: '西成高铁',
    code: 'XCG',
    occupancyRate: 45,
    loadRate: 42,
    efficiency: 44,
    industryAverage: 60,
    trend: -2.1,
    status: 'low'
  },
  {
    id: 5,
    name: '渝万铁路',
    code: 'YWR',
    occupancyRate: 82,
    loadRate: 76,
    efficiency: 79,
    industryAverage: 68,
    trend: 11.4,
    status: 'high'
  }
])

// 线路工具提示
const lineTooltip = ref({
  visible: false,
  line: {} as Line,
  x: 0,
  y: 0
})

// 获取线路指标
const getLineMetric = (line: Line) => {
  switch (loadMetric.value) {
    case 'occupancy':
      return line.occupancyRate
    case 'load':
      return line.loadRate
    case 'efficiency':
      return line.efficiency
    default:
      return line.occupancyRate
  }
}

// 获取负载状态类
const getLoadStatusClass = (value: number) => {
  if (value > 80) return 'load-high'
  if (value > 60) return 'load-medium'
  return 'load-low'
}

// 平均上座率
const avgOccupancyRate = computed(() => {
  const data = lineLoads.value.length > 0 ? lineLoads.value : lineLoadsData.value
  const sum = data.reduce((total, line) => total + line.occupancyRate, 0)
  return Math.round(sum / data.length)
})

// 平均满载率
const avgLoadRate = computed(() => {
  const data = lineLoads.value.length > 0 ? lineLoads.value : lineLoadsData.value
  const sum = data.reduce((total, line) => total + line.loadRate, 0)
  return Math.round(sum / data.length)
})

// 平均上座率趋势
const avgOccupancyTrend = computed(() => {
  return 8.5 // 模拟数据
})

// 平均满载率趋势
const avgLoadTrend = computed(() => {
  return 7.2 // 模拟数据
})

// 最高负载线路
const peakLine = computed(() => {
  const data = lineLoads.value.length > 0 ? lineLoads.value : lineLoadsData.value
  const line = data.reduce((max, l) =>
    l.occupancyRate > max.occupancyRate ? l : max, data[0])
  return {
    name: line.name,
    value: line.occupancyRate
  }
})

// 优化潜力
const optimizationPotential = computed(() => {
  const data = lineLoads.value.length > 0 ? lineLoads.value : lineLoadsData.value
  const maxOccupancy = Math.max(...data.map(l => l.occupancyRate))
  const minOccupancy = Math.min(...data.map(l => l.occupancyRate))
  return Math.round((maxOccupancy - minOccupancy) / 2)
})

// 线路工具提示样式
const lineTooltipStyle = computed(() => ({
  left: `${lineTooltip.value.x}px`,
  top: `${lineTooltip.value.y}px`
}))

// 显示线路工具提示
const showLineTooltip = (line: Line) => {
  lineTooltip.value = {
    visible: true,
    line,
    x: 100,
    y: 200
  }
}

// 隐藏线路工具提示
const hideLineTooltip = () => {
  lineTooltip.value.visible = false
}

// 切换负载指标
const changeLoadMetric = (metric: 'occupancy' | 'load' | 'efficiency') => {
  loadMetric.value = metric
}

// 模拟数据 - 实时列车
const recentTrains = ref([
  { id: 1, code: 'G8501', type: '高铁', departureStation: '成都东', arrivalStation: '重庆北', departureTime: '08:00', arrivalTime: '09:30', occupancy: 92, status: 'running', statusText: '运行中' },
  { id: 2, code: 'G8503', type: '高铁', departureStation: '重庆北', arrivalStation: '成都东', departureTime: '09:00', arrivalTime: '10:30', occupancy: 85, status: 'running', statusText: '运行中' },
  { id: 3, code: 'D5101', type: '动车', departureStation: '内江北', arrivalStation: '资阳北', departureTime: '10:30', arrivalTime: '11:15', occupancy: 78, status: 'running', statusText: '运行中' },
  { id: 4, code: 'G8505', type: '高铁', departureStation: '成都东', arrivalStation: '永川东', departureTime: '11:00', arrivalTime: '12:00', occupancy: 65, status: 'running', statusText: '运行中' },
  { id: 5, code: 'G8507', type: '高铁', departureStation: '重庆北', arrivalStation: '荣昌北', departureTime: '12:30', arrivalTime: '13:15', occupancy: 88, status: 'scheduled', statusText: '待发车' }
])

// 分页
const currentPage = ref(1)
const totalPages = ref(5)
</script>

<style scoped>
@keyframes ripple {
  0% {
    transform: scale(0, 0);
    opacity: 0.5;
  }
  20% {
    transform: scale(25, 25);
    opacity: 0.3;
  }
  100% {
    opacity: 0;
    transform: scale(40, 40);
  }
}

.dashboard {
  padding: var(--spacing-4);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-6);
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-2) 0;
}

.page-description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-3);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  border-radius: var(--border-radius-base);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  overflow: hidden;
}

.btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5px;
  height: 5px;
  background: rgba(255, 255, 255, 0.5);
  opacity: 0;
  border-radius: 100%;
  transform: scale(1, 1) translate(-50%, -50%);
  transform-origin: 50% 50%;
}

.btn:focus:not(:active)::after {
  animation: ripple 1s ease-out;
}

.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.btn-primary:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-outline {
  background-color: transparent;
  color: var(--color-text-primary);
  border-color: var(--color-border);
}

.btn-outline:hover {
  background-color: var(--color-bg-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.btn-outline:active {
  transform: translateY(0);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-sm {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
}

.btn svg {
  width: 16px;
  height: 16px;
}

.time-filter {
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-4);
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
}

.filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.filter-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.filter-buttons {
  display: flex;
  gap: var(--spacing-2);
}

.filter-btn {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-sm);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-btn.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.date-picker {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.date-input {
  padding: var(--spacing-1) var(--spacing-2);
  font-size: var(--font-size-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.date-separator {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.filter-stats {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--border-radius-base);
  border: 1px solid var(--color-border);
}

.stat-label {
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.stat-value {
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.stat-duration {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
}

/* KPI卡片 */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

@media (min-width: 768px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.kpi-card {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp var(--transition-base) forwards;
}

.kpi-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

.kpi-card:nth-child(1) { animation-delay: 100ms; }
.kpi-card:nth-child(2) { animation-delay: 200ms; }
.kpi-card:nth-child(3) { animation-delay: 300ms; }
.kpi-card:nth-child(4) { animation-delay: 400ms; }

.kpi-skeleton {
  width: 100%;
}

.kpi-skeleton .skeleton-loader {
  margin: 0;
}

.kpi-skeleton .skeleton-line {
  height: 24px;
  margin-bottom: var(--spacing-2);
}

.kpi-skeleton .skeleton-line:last-child {
  height: 16px;
  margin-bottom: 0;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--border-radius-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-icon svg {
  width: 24px;
  height: 24px;
}

.kpi-icon.total-passengers {
  background-color: rgba(70, 130, 180, 0.1);
  color: var(--color-secondary);
}

.kpi-icon.total-trains {
  background-color: rgba(46, 139, 87, 0.1);
  color: var(--color-success);
}

.kpi-icon.busy-stations {
  background-color: rgba(210, 105, 30, 0.1);
  color: var(--color-accent);
}

.kpi-icon.revenue {
  background-color: rgba(112, 128, 144, 0.1);
  color: var(--color-neutral);
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.kpi-trend.positive {
  color: var(--color-success);
}

.kpi-trend.negative {
  color: var(--color-error);
}

.kpi-trend svg {
  width: 12px;
  height: 12px;
}

.kpi-content {
  margin-bottom: var(--spacing-4);
}

.kpi-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-1) 0;
  line-height: 1;
}

.kpi-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.kpi-footer {
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--color-border-light);
}

.kpi-period {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* 图表区域 */
.chart-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

@media (min-width: 1024px) {
  .chart-grid {
    grid-template-columns: 2fr 1fr;
  }
}

.chart-card {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.map-card {
  grid-column: 1 / -1;
}

@media (min-width: 1024px) {
  .map-card {
    grid-column: 1;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.card-actions {
  display: flex;
  gap: var(--spacing-2);
}

.card-action-btn {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.card-action-btn.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
}

.card-body {
  padding: var(--spacing-4);
}

.map-placeholder,
.chart-placeholder {
  height: 300px;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.mock-map {
  width: 100%;
  height: 100%;
  position: relative;
}

.map-grid {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  grid-template-rows: repeat(10, 1fr);
}

.grid-line {
  border-right: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
}

.station-marker {
  position: absolute;
  transform: translate(-50%, -50%);
}

.marker-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--color-primary);
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.marker-dot.large {
  width: 32px;
  height: 32px;
  background-color: var(--color-error);
}

.marker-dot.medium {
  width: 24px;
  height: 24px;
  background-color: var(--color-warning);
}

.marker-dot.small {
  width: 16px;
  height: 16px;
  background-color: var(--color-success);
}

.marker-label {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  font-size: var(--font-size-xs);
  white-space: nowrap;
  background-color: white;
  padding: 2px 4px;
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-sm);
}

.map-legend {
  position: absolute;
  bottom: var(--spacing-4);
  left: var(--spacing-4);
  background-color: white;
  padding: var(--spacing-3);
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-md);
  display: flex;
  gap: var(--spacing-3);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-xs);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-color.large {
  background-color: var(--color-error);
}

.legend-color.medium {
  background-color: var(--color-warning);
}

.legend-color.small {
  background-color: var(--color-success);
}

/* 流向图样式 */
.flow-container {
  height: 300px;
}

.flow-placeholder {
  height: 100%;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.flow-map {
  width: 100%;
  height: 100%;
  position: relative;
}

.flow-grid {
  position: absolute;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  grid-template-rows: repeat(10, 1fr);
}

.flow-line {
  position: absolute;
  height: 4px;
  background-color: var(--color-primary);
  border-radius: var(--border-radius-full);
  transform-origin: left center;
}

.flow-line::before {
  content: '';
  position: absolute;
  right: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-left: 8px solid var(--color-primary);
  border-top: 6px solid transparent;
  border-bottom: 6px solid transparent;
}

.flow-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: var(--font-size-xs);
  background-color: white;
  padding: 2px 6px;
  border-radius: var(--border-radius-sm);
  box-shadow: var(--shadow-sm);
  white-space: nowrap;
}

.flow-legend {
  position: absolute;
  bottom: var(--spacing-4);
  left: var(--spacing-4);
  background-color: white;
  padding: var(--spacing-3);
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-md);
  display: flex;
  gap: var(--spacing-3);
}

.legend-line {
  width: 30px;
  height: 4px;
  border-radius: var(--border-radius-full);
}

.legend-line.high {
  background-color: var(--color-error);
}

.legend-line.medium {
  background-color: var(--color-warning);
}

.legend-line.low {
  background-color: var(--color-success);
}

.mock-chart {
  width: 100%;
  height: 100%;
  position: relative;
}

.chart-line {
  position: absolute;
  bottom: 40px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: var(--color-primary);
}

.data-point {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-primary);
  transform: translate(-50%, 50%);
}

.chart-axis {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 20px;
}

.axis-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.ranking-list,
.load-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.ranking-item,
.load-item {
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-3);
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
}

.rank {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-full);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.station-info,
.line-info {
  display: flex;
  flex-direction: column;
}

.station-name,
.line-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.station-code,
.line-code {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.passenger-count,
.load-percentage {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.progress-bar,
.load-bar {
  width: 100px;
  height: 8px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.progress-fill,
.load-fill {
  height: 100%;
  background-color: var(--color-primary);
  border-radius: var(--border-radius-full);
  transition: width var(--transition-slow);
}

.load-fill.high {
  background-color: var(--color-error);
}

.load-fill.medium {
  background-color: var(--color-warning);
}

.load-fill.low {
  background-color: var(--color-success);
}

.load-status {
  font-size: var(--font-size-xs);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius-full);
  font-weight: var(--font-weight-medium);
}

.load-status.high {
  background-color: rgba(220, 20, 60, 0.1);
  color: var(--color-error);
}

.load-status.medium {
  background-color: rgba(255, 165, 0, 0.1);
  color: var(--color-warning);
}

.load-status.low {
  background-color: rgba(46, 139, 87, 0.1);
  color: var(--color-success);
}

/* 线路负载分析样式 */
.load-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.load-chart {
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-4);
}

.load-bars {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.load-bar-item {
  display: grid;
  grid-template-columns: 120px 1fr 180px 60px;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-3);
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-base);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.load-bar-item:hover {
  background-color: var(--color-bg-secondary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.bar-label {
  display: flex;
  flex-direction: column;
}

.line-name {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.line-code {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.bar-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.bar-track {
  height: 24px;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  border-radius: var(--border-radius-full);
  transition: width var(--transition-slow);
  position: relative;
}

.bar-fill.load-high {
  background-color: var(--color-error);
}

.bar-fill.load-medium {
  background-color: var(--color-warning);
}

.bar-fill.load-low {
  background-color: var(--color-success);
}

.bar-value {
  position: absolute;
  right: var(--spacing-2);
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--font-size-xs);
  color: white;
  font-weight: var(--font-weight-medium);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.bar-comparison {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-xs);
}

.comparison-label {
  color: var(--color-text-secondary);
  min-width: 60px;
}

.comparison-bar {
  flex: 1;
  height: 4px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.comparison-fill {
  height: 100%;
  background-color: var(--color-text-tertiary);
  border-radius: var(--border-radius-full);
}

.comparison-value {
  color: var(--color-text-tertiary);
  min-width: 40px;
  text-align: right;
}

.bar-stats {
  display: flex;
  gap: var(--spacing-3);
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.stat-value {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.bar-trend {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  justify-content: center;
}

.bar-trend.positive {
  color: var(--color-success);
}

.bar-trend.negative {
  color: var(--color-error);
}

.bar-trend svg {
  width: 12px;
  height: 12px;
}

.load-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-3);
}

.summary-card {
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-3);
  text-align: center;
}

.summary-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
  margin-bottom: var(--spacing-1);
}

.summary-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-2);
}

.summary-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
}

.summary-trend.positive {
  color: var(--color-success);
}

.summary-trend.negative {
  color: var(--color-error);
}

.summary-trend svg {
  width: 12px;
  height: 12px;
}

.summary-detail {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-1);
}

.line-tooltip {
  position: fixed;
  background-color: white;
  border-radius: var(--border-radius-base);
  box-shadow: var(--shadow-lg);
  padding: var(--spacing-3);
  z-index: 1000;
  min-width: 200px;
  pointer-events: none;
  animation: fadeIn var(--transition-fast);
}

.tooltip-header {
  margin-bottom: var(--spacing-2);
  padding-bottom: var(--spacing-2);
  border-bottom: 1px solid var(--color-border-light);
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.tooltip-row {
  display: flex;
  justify-content: space-between;
}

.tooltip-label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.tooltip-value {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-sm);
}

.tooltip-value.positive {
  color: var(--color-success);
}

.tooltip-value.negative {
  color: var(--color-error);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1024px) {
  .load-bar-item {
    grid-template-columns: 1fr;
    gap: var(--spacing-2);
  }

  .bar-stats {
    flex-wrap: wrap;
    gap: var(--spacing-2);
  }

  .load-summary {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .load-summary {
    grid-template-columns: 1fr;
  }

  .bar-container {
    gap: var(--spacing-1);
  }

  .bar-comparison {
    flex-wrap: wrap;
  }
}

/* 数据表格 */
.data-table-section {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.section-actions {
  display: flex;
  gap: var(--spacing-3);
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: var(--spacing-3) var(--spacing-4);
  text-align: left;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  background-color: var(--color-bg-secondary);
  border-bottom: 2px solid var(--color-border);
  white-space: nowrap;
}

.data-table td {
  padding: var(--spacing-3) var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background-color: var(--color-bg-secondary);
}

.train-code {
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.train-type {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.occupancy {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.occupancy-bar {
  width: 60px;
  height: 6px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--border-radius-full);
  overflow: hidden;
}

.occupancy-fill {
  height: 100%;
  background-color: var(--color-primary);
  border-radius: var(--border-radius-full);
}

.occupancy-percentage {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  min-width: 40px;
}

.status-badge {
  display: inline-block;
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  border-radius: var(--border-radius-full);
}

.status-badge.running {
  background-color: rgba(46, 139, 87, 0.1);
  color: var(--color-success);
}

.status-badge.scheduled {
  background-color: rgba(70, 130, 180, 0.1);
  color: var(--color-secondary);
}

.table-footer {
  padding: var(--spacing-4);
  border-top: 1px solid var(--color-border-light);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-4);
}

.pagination-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-base);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn svg {
  width: 16px;
  height: 16px;
}

.pagination-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
</style>