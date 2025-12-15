<template>
  <div class="analytics animate-fade-in">
    <!-- 全局加载状态 -->
    <LoadingSpinner
      v-if="isLoading"
      size="large"
      variant="primary"
      text="正在加载客流分析数据..."
      fullscreen
    />

    <!-- 页面标题和操作 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">客流分析</h1>
        <p class="page-description">客流统计、时空分布和预测分析</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary touch-target touch-feedback" :disabled="isRefreshing" @click="refreshData">
          <svg v-if="!isRefreshing" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C14.1974 3 16.1958 3.86095 17.6576 5.27264M21 3V7M21 7H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else class="animate-spin" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2V6M12 18V22M4.93 4.93L7.76 7.76M16.24 16.24L19.07 19.07M2 12H6M18 12H22M4.93 19.07L7.76 16.24M16.24 7.76L19.07 4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ isRefreshing ? '刷新中...' : '刷新数据' }}
        </button>
        <button class="btn btn-outline touch-target touch-feedback" @click="exportData">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
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
        <div v-if="selectedRange === 'custom'" class="date-picker">
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
        <div v-if="selectedRange !== 'custom'" class="filter-stats">
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
          <span class="kpi-period">{{ timeRangeLabel }}</span>
        </div>
      </div>

      <!-- 站点平均客流 -->
      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon avg-passengers">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12 11C13.1046 11 14 10.1046 14 9C14 7.89543 13.1046 7 12 7C10.8954 7 10 7.89543 10 9C10 10.1046 10.8954 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.avgPassengers >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.avgPassengers >= 0 ? '+' : '' }}{{ kpiData.trends.avgPassengers }}%</span>
            <svg v-if="kpiData.trends.avgPassengers >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
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
              <AnimatedNumber :value="kpiData.avgPassengers" :duration="1200" :animate="true" />
            </h3>
            <p class="kpi-label">站点平均客流</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">{{ timeRangeLabel }}</span>
        </div>
      </div>

      <!-- 最高客流站点 -->
      <div class="kpi-card">
        <div class="kpi-header">
          <div class="kpi-icon peak-station">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="kpi-trend" :class="kpiData.trends.peakStation >= 0 ? 'positive' : 'negative'">
            <span>{{ kpiData.trends.peakStation >= 0 ? '+' : '' }}{{ kpiData.trends.peakStation }}%</span>
            <svg v-if="kpiData.trends.peakStation >= 0" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 17L17 7M17 7H7M17 7V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7 7L17 17M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>
        <div class="kpi-content">
          <template v-if="!isLoading">
            <h3 class="kpi-value">{{ kpiData.peakStationName }}</h3>
            <p class="kpi-label">最高客流站点</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">{{ kpiData.peakStationValue.toLocaleString() }} 人</span>
        </div>
      </div>

      <!-- 总收入 -->
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
          <span class="kpi-period">{{ timeRangeLabel }}</span>
        </div>
      </div>
    </div>

    <!-- 主要分析区域 -->
    <div class="analysis-grid">
      <!-- 客流趋势分析 -->
      <div class="analysis-card">
        <div class="card-header">
          <h3 class="card-title">客流趋势分析</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: trendFrequency === 'hourly' }"
              @click="changeTrendFrequency('hourly')"
            >
              小时
            </button>
            <button
              class="card-action-btn"
              :class="{ active: trendFrequency === 'daily' }"
              @click="changeTrendFrequency('daily')"
            >
              日
            </button>
            <button
              class="card-action-btn"
              :class="{ active: trendFrequency === 'weekly' }"
              @click="changeTrendFrequency('weekly')"
            >
              周
            </button>
            <button
              class="card-action-btn"
              :class="{ active: trendFrequency === 'monthly' }"
              @click="changeTrendFrequency('monthly')"
            >
              月
            </button>
          </div>
        </div>
        <div class="card-body">
          <TrendChart
            title="客流趋势"
            :data="trendData"
          />
        </div>
      </div>

      <!-- 站点客流排名 -->
      <div class="analysis-card">
        <div class="card-header">
          <h3 class="card-title">站点客流排名</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: rankingMetric === 'total' }"
              @click="changeRankingMetric('total')"
            >
              总客流
            </button>
            <button
              class="card-action-btn"
              :class="{ active: rankingMetric === 'inbound' }"
              @click="changeRankingMetric('inbound')"
            >
              到达客流
            </button>
            <button
              class="card-action-btn"
              :class="{ active: rankingMetric === 'outbound' }"
              @click="changeRankingMetric('outbound')"
            >
              发送客流
            </button>
          </div>
        </div>
        <div class="card-body">
          <StationRankingTable
            :data="stationRankings"
            title="站点客流排名"
            :show-actions="false"
          />
        </div>
      </div>

      <!-- 线路负载分析 -->
      <div class="analysis-card">
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
                    v-for="line in lineLoads"
                    :key="line.id"
                    class="load-bar-item"
                    @mouseenter="showLineTooltip(line, $event)"
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
          </div>
        </div>
      </div>

      <!-- 时空分布地图 -->
      <div class="analysis-card map-card">
        <div class="card-header">
          <h3 class="card-title">客流时空分布</h3>
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

      <!-- 时间分布分析 -->
      <div class="analysis-card">
        <div class="card-header">
          <h3 class="card-title">时间分布分析</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: timeDistributionType === 'hourly' }"
              @click="changeTimeDistributionType('hourly')"
            >
              小时分布
            </button>
            <button
              class="card-action-btn"
              :class="{ active: timeDistributionType === 'daily' }"
              @click="changeTimeDistributionType('daily')"
            >
              日分布
            </button>
            <button
              class="card-action-btn"
              :class="{ active: timeDistributionType === 'weekly' }"
              @click="changeTimeDistributionType('weekly')"
            >
              周分布
            </button>
          </div>
        </div>
        <div class="card-body">
          <div class="time-distribution-chart">
            <div class="chart-container">
              <div class="time-bars">
                <div
                  v-for="period in timeDistributionData"
                  :key="period.id"
                  class="time-bar-item"
                >
                  <div class="bar-label">
                    <div class="period-name">{{ period.name }}</div>
                    <div class="period-time">{{ period.time }}</div>
                  </div>
                  <div class="bar-container">
                    <div class="bar-track">
                      <div
                        class="bar-fill"
                        :style="{ width: period.percentage + '%' }"
                        :class="getTimeDistributionClass(period.percentage)"
                      >
                        <span class="bar-value">{{ period.percentage }}%</span>
                      </div>
                    </div>
                  </div>
                  <div class="bar-stats">
                    <div class="stat">
                      <div class="stat-label">客流量</div>
                      <div class="stat-value">{{ period.passengers.toLocaleString() }}</div>
                    </div>
                    <div class="stat">
                      <div class="stat-label">车次</div>
                      <div class="stat-value">{{ period.trains }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 客流预测 -->
      <div class="analysis-card">
        <div class="card-header">
          <h3 class="card-title">客流预测</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: forecastDays === 7 }"
              @click="changeForecastDays(7)"
            >
              7天
            </button>
            <button
              class="card-action-btn"
              :class="{ active: forecastDays === 14 }"
              @click="changeForecastDays(14)"
            >
              14天
            </button>
            <button
              class="card-action-btn"
              :class="{ active: forecastDays === 30 }"
              @click="changeForecastDays(30)"
            >
              30天
            </button>
          </div>
        </div>
        <div class="card-body">
          <div class="forecast-chart">
            <div class="chart-container">
              <div class="forecast-bars">
                <div
                  v-for="day in forecastData"
                  :key="day.id"
                  class="forecast-bar-item"
                >
                  <div class="bar-label">
                    <div class="day-name">{{ day.day }}</div>
                    <div class="date">{{ day.date }}</div>
                  </div>
                  <div class="bar-container">
                    <div class="bar-track">
                      <div
                        class="bar-fill forecast"
                        :style="{ width: day.percentage + '%' }"
                      >
                        <span class="bar-value">{{ day.forecast.toLocaleString() }}</span>
                      </div>
                      <div
                        v-if="day.actual"
                        class="bar-fill actual"
                        :style="{ width: day.actualPercentage + '%' }"
                      >
                        <span class="bar-value">{{ day.actual.toLocaleString() }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="bar-stats">
                    <div class="stat">
                      <div class="stat-label">预测</div>
                      <div class="stat-value">{{ day.forecast.toLocaleString() }}</div>
                    </div>
                    <div v-if="day.actual" class="stat">
                      <div class="stat-label">实际</div>
                      <div class="stat-value">{{ day.actual.toLocaleString() }}</div>
                    </div>
                    <div class="stat">
                      <div class="stat-label">置信度</div>
                      <div class="stat-value">{{ day.confidence }}%</div>
                    </div>
                  </div>
                </div>
              </div>
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
          <span class="tooltip-label">趋势：</span>
          <span class="tooltip-value" :class="lineTooltip.line.trend >= 0 ? 'positive' : 'negative'">
            {{ lineTooltip.line.trend >= 0 ? '+' : '' }}{{ lineTooltip.line.trend }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { usePassengerStore } from '@/stores/passenger';
import { format, subDays, startOfWeek, endOfWeek, startOfMonth, endOfMonth, startOfQuarter, endOfQuarter, startOfYear, endOfYear } from 'date-fns';
import { zhCN } from 'date-fns/locale';

// 组件导入
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import AnimatedNumber from '@/components/ui/AnimatedNumber.vue';
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue';
import FlowTrendChart from '@/components/passenger/FlowTrendChart.vue';
import StationRankingTable from '@/components/passenger/StationRankingTable.vue';
import TimeDistributionChart from '@/components/passenger/TimeDistributionChart.vue';

// Store
const passengerStore = usePassengerStore();

// 状态
const isLoading = ref(false);
const isRefreshing = ref(false);
const selectedRange = ref<'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom'>('week');
const startDate = ref('');
const endDate = ref('');

// 图表状态
const trendFrequency = ref<'hourly' | 'daily' | 'weekly' | 'monthly'>('daily');
const rankingMetric = ref<'total' | 'inbound' | 'outbound'>('total');
const loadMetric = ref<'occupancy' | 'load' | 'efficiency'>('occupancy');
const mapViewMode = ref<'heatmap' | 'flow' | 'markers'>('heatmap');
const timeDistributionType = ref<'hourly' | 'daily' | 'weekly'>('hourly');
const forecastDays = ref<7 | 14 | 30>(7);

// 工具提示状态
const lineTooltip = ref({
  visible: false,
  line: null as any,
  x: 0,
  y: 0
});

// 计算属性
const timeRangeLabel = computed(() => {
  const now = new Date();
  switch (selectedRange.value) {
    case 'today':
      return format(now, 'yyyy年MM月dd日', { locale: zhCN });
    case 'week':
      const weekStart = startOfWeek(now, { locale: zhCN });
      const weekEnd = endOfWeek(now, { locale: zhCN });
      return `${format(weekStart, 'MM/dd')} - ${format(weekEnd, 'MM/dd')}`;
    case 'month':
      return format(now, 'yyyy年MM月', { locale: zhCN });
    case 'quarter':
      const quarterStart = startOfQuarter(now);
      const quarterEnd = endOfQuarter(now);
      return `${format(quarterStart, 'MM/dd')} - ${format(quarterEnd, 'MM/dd')}`;
    case 'year':
      return format(now, 'yyyy年', { locale: zhCN });
    case 'custom':
      if (startDate.value && endDate.value) {
        return `${format(new Date(startDate.value), 'MM/dd')} - ${format(new Date(endDate.value), 'MM/dd')}`;
      }
      return '自定义范围';
    default:
      return '';
  }
});

const timeRangeDuration = computed(() => {
  switch (selectedRange.value) {
    case 'today': return '1天';
    case 'week': return '7天';
    case 'month': return '约30天';
    case 'quarter': return '约90天';
    case 'year': return '365天';
    case 'custom': return '自定义';
    default: return '';
  }
});

// KPI数据（模拟）
const kpiData = computed(() => {
  return {
    totalPassengers: 1258473,
    avgPassengers: 85642,
    peakStationName: '成都东站',
    peakStationValue: 245832,
    totalRevenue: 85642350,
    trends: {
      totalPassengers: 12.5,
      avgPassengers: 8.3,
      peakStation: 15.2,
      totalRevenue: 18.7
    }
  };
});

// 趋势数据（模拟）
const trendData = computed(() => {
  // 这里应该从store获取真实数据
  return {
    granularity: 'day' as const,
    data: Array.from({ length: 30 }, (_, i) => ({
      time: format(subDays(new Date(), 29 - i), 'yyyy-MM-dd'),
      value: Math.floor(Math.random() * 50000) + 30000
    })),
    total: 1258473,
    average: 41949,
    max: 85642,
    min: 24583,
    growthRate: 0.125
  };
});

// 站点排名数据（模拟）
const stationRankings = computed(() => {
  const stations = [
    '成都东站', '重庆北站', '成都站', '重庆西站', '内江北站',
    '永川东站', '荣昌北站', '大足南站', '璧山站', '沙坪坝站'
  ];

  return stations.map((name, index) => ({
    stationId: index + 1,
    stationName: name,
    stationTelecode: `CD${String(index + 1).padStart(3, '0')}`,
    totalPassengers: Math.floor(Math.random() * 200000) + 100000,
    passengersIn: Math.floor(Math.random() * 100000) + 50000,
    passengersOut: Math.floor(Math.random() * 100000) + 50000,
    revenue: Math.floor(Math.random() * 10000000) + 5000000,
    ranking: index + 1,
    change: Math.floor(Math.random() * 6) - 3 // -3到+2的变化
  }));
});

// 线路负载数据（模拟）
const lineLoads = computed(() => {
  return [
    { id: 1, name: '成渝高铁', code: 'G8501', occupancyRate: 85, loadRate: 92, efficiency: 78, trend: 5.2 },
    { id: 2, name: '成贵高铁', code: 'G2963', occupancyRate: 72, loadRate: 81, efficiency: 65, trend: 3.8 },
    { id: 3, name: '西成高铁', code: 'D1917', occupancyRate: 91, loadRate: 95, efficiency: 82, trend: 8.1 },
    { id: 4, name: '成昆铁路', code: 'K113', occupancyRate: 68, loadRate: 75, efficiency: 62, trend: -2.3 },
    { id: 5, name: '宝成铁路', code: 'T8', occupancyRate: 79, loadRate: 86, efficiency: 71, trend: 1.5 }
  ];
});

// 热力图数据（模拟）
const heatmapData = computed(() => {
  return {
    data: Array.from({ length: 50 }, (_, i) => ({
      x: `站点${i + 1}`,
      y: Math.floor(Math.random() * 24).toString(),
      value: Math.floor(Math.random() * 1000)
    }))
  };
});

// 流向数据（模拟）
const flowData = computed(() => {
  return [
    { id: 1, label: '成都→重庆', style: { left: '20%', top: '30%', width: '200px', transform: 'rotate(45deg)' } },
    { id: 2, label: '重庆→成都', style: { left: '60%', top: '40%', width: '180px', transform: 'rotate(-30deg)' } },
    { id: 3, label: '成都→西安', style: { left: '30%', top: '60%', width: '220px', transform: 'rotate(15deg)' } }
  ];
});

// 时间分布数据（模拟）
const timeDistributionData = computed(() => {
  const hours = Array.from({ length: 24 }, (_, i) => i);
  return hours.map(hour => ({
    id: hour,
    name: `${hour}:00`,
    time: `${hour}:00-${hour + 1}:00`,
    percentage: Math.floor(Math.random() * 30) + 10,
    passengers: Math.floor(Math.random() * 50000) + 20000,
    trains: Math.floor(Math.random() * 50) + 20
  }));
});

// 预测数据（模拟）
const forecastData = computed(() => {
  const days = Array.from({ length: forecastDays.value }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() + i + 1);
    const forecast = Math.floor(Math.random() * 60000) + 40000;
    const actual = i < 3 ? Math.floor(Math.random() * 60000) + 40000 : undefined;

    return {
      id: i,
      day: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date.getDay()],
      date: format(date, 'MM/dd'),
      forecast,
      actual,
      percentage: (forecast / 100000) * 100,
      actualPercentage: actual ? (actual / 100000) * 100 : 0,
      confidence: Math.floor(Math.random() * 20) + 80
    };
  });
  return days;
});

// 工具提示样式
const lineTooltipStyle = computed(() => {
  return {
    left: `${lineTooltip.value.x}px`,
    top: `${lineTooltip.value.y}px`,
    display: lineTooltip.value.visible ? 'block' : 'none'
  };
});

// 方法
const selectTimeRange = (range: 'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom') => {
  selectedRange.value = range;
  if (range !== 'custom') {
    loadData();
  }
};

const updateCustomDateRange = () => {
  if (startDate.value && endDate.value) {
    loadData();
  }
};

const refreshData = async () => {
  isRefreshing.value = true;
  try {
    await loadData();
  } finally {
    isRefreshing.value = false;
  }
};

const exportData = () => {
  // 导出功能实现
  console.log('导出数据');
  alert('导出功能开发中...');
};

const changeTrendFrequency = (frequency: 'hourly' | 'daily' | 'weekly' | 'monthly') => {
  trendFrequency.value = frequency;
  // 这里应该重新加载对应粒度的数据
};

const changeRankingMetric = (metric: 'total' | 'inbound' | 'outbound') => {
  rankingMetric.value = metric;
  // 这里应该重新加载对应指标的数据
};

const changeLoadMetric = (metric: 'occupancy' | 'load' | 'efficiency') => {
  loadMetric.value = metric;
};

const getLineMetric = (line: any) => {
  switch (loadMetric.value) {
    case 'occupancy': return line.occupancyRate;
    case 'load': return line.loadRate;
    case 'efficiency': return line.efficiency;
    default: return line.occupancyRate;
  }
};

const getLoadStatusClass = (value: number) => {
  if (value >= 90) return 'high';
  if (value >= 70) return 'medium';
  return 'low';
};

const showLineTooltip = (line: any, event: MouseEvent) => {
  lineTooltip.value = {
    visible: true,
    line,
    x: event.clientX + 10,
    y: event.clientY + 10
  };
};

const hideLineTooltip = () => {
  lineTooltip.value.visible = false;
};

const changeMapViewMode = (mode: 'heatmap' | 'flow' | 'markers') => {
  mapViewMode.value = mode;
};

const changeTimeDistributionType = (type: 'hourly' | 'daily' | 'weekly') => {
  timeDistributionType.value = type;
  // 这里应该重新加载对应类型的数据
};

const changeForecastDays = (days: 7 | 14 | 30) => {
  forecastDays.value = days;
  // 这里应该重新加载对应天数的预测数据
};

const getTimeDistributionClass = (percentage: number) => {
  if (percentage >= 20) return 'high';
  if (percentage >= 10) return 'medium';
  return 'low';
};

// 加载数据
const loadData = async () => {
  isLoading.value = true;
  try {
    // 这里应该调用store的方法加载数据
    // await passengerStore.loadAnalyticsData({ ... });
    // 模拟加载延迟
    await new Promise(resolve => setTimeout(resolve, 1000));
  } catch (error) {
    console.error('加载数据失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 初始化
onMounted(() => {
  // 设置默认日期范围
  const today = new Date();
  const weekAgo = subDays(today, 7);
  startDate.value = format(weekAgo, 'yyyy-MM-dd');
  endDate.value = format(today, 'yyyy-MM-dd');

  // 加载初始数据
  loadData();
});
</script>

<style scoped lang="scss">
.analytics {
  padding: var(--spacing-6);
  background: var(--color-bg-secondary);
  min-height: 100vh;
}

/* 页面标题和操作 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-8);
  flex-wrap: wrap;
  gap: var(--spacing-4);

  .header-content {
    .page-title {
      margin: 0;
      font-size: var(--font-size-3xl);
      font-weight: var(--font-weight-bold);
      color: var(--color-text-primary);
      line-height: var(--line-height-tight);
    }

    .page-description {
      margin: var(--spacing-2) 0 0;
      font-size: var(--font-size-base);
      color: var(--color-text-secondary);
      line-height: var(--line-height-normal);
    }
  }

  .header-actions {
    display: flex;
    gap: var(--spacing-3);
    flex-wrap: wrap;

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: var(--spacing-2);
      padding: var(--spacing-3) var(--spacing-5);
      border-radius: var(--border-radius-lg);
      font-size: var(--font-size-base);
      font-weight: var(--font-weight-medium);
      line-height: var(--line-height-normal);
      cursor: pointer;
      transition: all var(--transition-base);
      border: 2px solid transparent;
      min-height: 44px; // 触摸目标最小高度

      svg {
        width: 20px;
        height: 20px;
      }

      &-primary {
        background: var(--color-primary);
        color: var(--color-text-inverse);
        border-color: var(--color-primary);

        &:hover:not(:disabled) {
          background: var(--color-primary-dark);
          border-color: var(--color-primary-dark);
          transform: translateY(-1px);
          box-shadow: var(--shadow-md);
        }

        &:active:not(:disabled) {
          transform: translateY(0);
          box-shadow: var(--shadow-sm);
        }

        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      }

      &-outline {
        background: transparent;
        color: var(--color-secondary);
        border-color: var(--color-secondary);

        &:hover {
          background: var(--color-secondary);
          color: var(--color-text-inverse);
          transform: translateY(-1px);
          box-shadow: var(--shadow-md);
        }

        &:active {
          transform: translateY(0);
          box-shadow: var(--shadow-sm);
        }
      }
    }
  }
}

/* 时间筛选 */
.time-filter {
  background: var(--color-bg-card);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-6);
  margin-bottom: var(--spacing-8);
  box-shadow: var(--shadow-md);

  .filter-container {
    .filter-group {
      margin-bottom: var(--spacing-4);

      .filter-label {
        display: block;
        margin-bottom: var(--spacing-3);
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-medium);
        color: var(--color-text-primary);
      }

      .filter-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-2);

        .filter-btn {
          padding: var(--spacing-2) var(--spacing-4);
          border-radius: var(--border-radius-lg);
          border: 2px solid var(--color-border);
          background: var(--color-bg-tertiary);
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          cursor: pointer;
          transition: all var(--transition-base);
          min-height: 36px;

          &:hover {
            border-color: var(--color-secondary);
            color: var(--color-secondary);
            background: var(--color-bg-secondary);
          }

          &.active {
            background: var(--color-secondary);
            border-color: var(--color-secondary);
            color: var(--color-text-inverse);
            box-shadow: var(--shadow-sm);
          }
        }
      }
    }

    .date-picker {
      display: flex;
      align-items: center;
      gap: var(--spacing-3);
      margin-top: var(--spacing-4);

      .date-input {
        padding: var(--spacing-2) var(--spacing-3);
        border: 2px solid var(--color-border);
        border-radius: var(--border-radius-lg);
        font-size: var(--font-size-base);
        color: var(--color-text-primary);
        background: var(--color-bg-card);
        transition: border-color var(--transition-base);
        min-height: 40px;

        &:focus {
          outline: none;
          border-color: var(--color-secondary);
          box-shadow: 0 0 0 3px rgba(70, 130, 180, 0.1);
        }
      }

      .date-separator {
        color: var(--color-text-tertiary);
        font-size: var(--font-size-base);
      }
    }

    .filter-stats {
      margin-top: var(--spacing-4);
      padding-top: var(--spacing-4);
      border-top: 1px solid var(--color-border-light);
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);

      .stat-label {
        font-weight: var(--font-weight-medium);
      }

      .stat-value {
        color: var(--color-text-primary);
        font-weight: var(--font-weight-semibold);
      }

      .stat-duration {
        color: var(--color-text-tertiary);
      }
    }
  }
}

/* KPI指标卡片 */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-8);

  .kpi-card {
    background: var(--color-bg-card);
    border-radius: var(--border-radius-xl);
    padding: var(--spacing-6);
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
    border: 1px solid var(--color-border-light);

    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--shadow-lg);
      border-color: var(--color-border);
    }

    .kpi-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--spacing-4);

      .kpi-icon {
        width: 48px;
        height: 48px;
        border-radius: var(--border-radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--color-bg-tertiary);

        svg {
          width: 24px;
          height: 24px;
          color: var(--color-text-primary);
        }

        &.total-passengers {
          background: rgba(46, 139, 87, 0.1);
          svg { color: var(--color-primary); }
        }

        &.avg-passengers {
          background: rgba(70, 130, 180, 0.1);
          svg { color: var(--color-secondary); }
        }

        &.peak-station {
          background: rgba(210, 105, 30, 0.1);
          svg { color: var(--color-accent); }
        }

        &.revenue {
          background: rgba(112, 128, 144, 0.1);
          svg { color: var(--color-neutral); }
        }
      }

      .kpi-trend {
        display: flex;
        align-items: center;
        gap: var(--spacing-1);
        font-size: var(--font-size-sm);
        font-weight: var(--font-weight-medium);
        padding: var(--spacing-1) var(--spacing-2);
        border-radius: var(--border-radius-full);

        svg {
          width: 16px;
          height: 16px;
        }

        &.positive {
          color: var(--color-success);
          background: rgba(46, 139, 87, 0.1);
        }

        &.negative {
          color: var(--color-error);
          background: rgba(220, 20, 60, 0.1);
        }
      }
    }

    .kpi-content {
      margin-bottom: var(--spacing-4);

      .kpi-value {
        margin: 0 0 var(--spacing-2);
        font-size: var(--font-size-3xl);
        font-weight: var(--font-weight-bold);
        color: var(--color-text-primary);
        line-height: var(--line-height-tight);
      }

      .kpi-label {
        margin: 0;
        font-size: var(--font-size-base);
        color: var(--color-text-secondary);
        line-height: var(--line-height-normal);
      }

      .kpi-skeleton {
        height: 72px;
        display: flex;
        align-items: center;
      }
    }

    .kpi-footer {
      .kpi-period {
        font-size: var(--font-size-sm);
        color: var(--color-text-tertiary);
      }
    }
  }
}

/* 主要分析区域 */
.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: var(--spacing-6);

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }

  .analysis-card {
    background: var(--color-bg-card);
    border-radius: var(--border-radius-xl);
    overflow: hidden;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--color-border-light);
    transition: all var(--transition-base);

    &:hover {
      box-shadow: var(--shadow-lg);
      border-color: var(--color-border);
    }

    &.map-card {
      grid-column: 1 / -1;

      @media (max-width: 1200px) {
        grid-column: 1;
      }
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--spacing-5) var(--spacing-6);
      border-bottom: 1px solid var(--color-border-light);
      background: var(--color-bg-tertiary);

      .card-title {
        margin: 0;
        font-size: var(--font-size-lg);
        font-weight: var(--font-weight-semibold);
        color: var(--color-text-primary);
      }

      .card-actions {
        display: flex;
        gap: var(--spacing-2);

        .card-action-btn {
          padding: var(--spacing-1) var(--spacing-3);
          border-radius: var(--border-radius-lg);
          border: 2px solid var(--color-border);
          background: var(--color-bg-card);
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          font-weight: var(--font-weight-medium);
          cursor: pointer;
          transition: all var(--transition-base);
          min-height: 32px;

          &:hover {
            border-color: var(--color-secondary);
            color: var(--color-secondary);
          }

          &.active {
            background: var(--color-secondary);
            border-color: var(--color-secondary);
            color: var(--color-text-inverse);
          }
        }
      }
    }

    .card-body {
      padding: var(--spacing-6);
      min-height: 300px;

      .load-analysis,
      .time-distribution-chart,
      .forecast-chart {
        .load-bars,
        .time-bars,
        .forecast-bars {
          display: flex;
          flex-direction: column;
          gap: var(--spacing-4);

          .load-bar-item,
          .time-bar-item,
          .forecast-bar-item {
            display: grid;
            grid-template-columns: 120px 1fr auto;
            gap: var(--spacing-4);
            align-items: center;
            padding: var(--spacing-3);
            border-radius: var(--border-radius-lg);
            background: var(--color-bg-tertiary);
            transition: background var(--transition-base);

            &:hover {
              background: var(--color-bg-secondary);
            }

            .bar-label {
              .line-name,
              .period-name,
              .day-name {
                font-weight: var(--font-weight-medium);
                color: var(--color-text-primary);
                margin-bottom: var(--spacing-1);
              }

              .line-code,
              .period-time,
              .date {
                font-size: var(--font-size-sm);
                color: var(--color-text-tertiary);
              }
            }

            .bar-container {
              .bar-track {
                height: 24px;
                background: var(--color-bg-secondary);
                border-radius: var(--border-radius-full);
                overflow: hidden;
                position: relative;

                .bar-fill {
                  height: 100%;
                  border-radius: var(--border-radius-full);
                  transition: width var(--transition-slow);
                  display: flex;
                  align-items: center;
                  justify-content: flex-end;
                  padding: 0 var(--spacing-3);
                  min-width: 40px;

                  .bar-value {
                    color: var(--color-text-inverse);
                    font-size: var(--font-size-sm);
                    font-weight: var(--font-weight-medium);
                    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
                  }

                  &.high {
                    background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light));
                  }

                  &.medium {
                    background: linear-gradient(90deg, var(--color-secondary), var(--color-secondary-light));
                  }

                  &.low {
                    background: linear-gradient(90deg, var(--color-neutral), var(--color-neutral-light));
                  }

                  &.forecast {
                    background: linear-gradient(90deg, #5470c6, #91cc75);
                  }

                  &.actual {
                    background: linear-gradient(90deg, #ee6666, #fac858);
                    position: absolute;
                    top: 0;
                    left: 0;
                    opacity: 0.8;
                  }
                }
              }
            }

            .bar-stats {
              display: flex;
              gap: var(--spacing-4);

              .stat {
                text-align: center;
                min-width: 60px;

                .stat-label {
                  font-size: var(--font-size-xs);
                  color: var(--color-text-tertiary);
                  margin-bottom: var(--spacing-1);
                }

                .stat-value {
                  font-size: var(--font-size-base);
                  font-weight: var(--font-weight-semibold);
                  color: var(--color-text-primary);
                }
              }
            }

            .bar-trend {
              display: flex;
              align-items: center;
              gap: var(--spacing-1);
              font-size: var(--font-size-sm);
              font-weight: var(--font-weight-medium);
              padding: var(--spacing-1) var(--spacing-2);
              border-radius: var(--border-radius-full);

              svg {
                width: 16px;
                height: 16px;
              }

              &.positive {
                color: var(--color-success);
                background: rgba(46, 139, 87, 0.1);
              }

              &.negative {
                color: var(--color-error);
                background: rgba(220, 20, 60, 0.1);
              }
            }
          }
        }
      }

      // 地图相关样式
      .heatmap-container,
      .flow-container,
      .station-map-container {
        height: 400px;
        border-radius: var(--border-radius-lg);
        overflow: hidden;
        background: var(--color-bg-tertiary);
        display: flex;
        align-items: center;
        justify-content: center;

        .flow-placeholder {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;

          .flow-mock {
            width: 80%;
            height: 80%;
            position: relative;

            .flow-map {
              width: 100%;
              height: 100%;
              position: relative;
              background: var(--color-bg-card);
              border-radius: var(--border-radius-lg);

              .flow-grid {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                display: grid;
                grid-template-columns: repeat(10, 1fr);
                grid-template-rows: repeat(10, 1fr);

                .grid-line {
                  border-right: 1px solid var(--color-border-light);
                  border-bottom: 1px solid var(--color-border-light);

                  &:nth-child(10n) {
                    border-right: none;
                  }

                  &:nth-child(n+91) {
                    border-bottom: none;
                  }
                }
              }

              .flow-line {
                position: absolute;
                height: 4px;
                background: var(--color-secondary);
                border-radius: 2px;
                display: flex;
                align-items: center;
                justify-content: flex-end;

                .flow-arrow {
                  width: 0;
                  height: 0;
                  border-top: 6px solid transparent;
                  border-bottom: 6px solid transparent;
                  border-left: 8px solid var(--color-secondary);
                  margin-left: 4px;
                }

                .flow-label {
                  position: absolute;
                  top: -24px;
                  left: 50%;
                  transform: translateX(-50%);
                  font-size: var(--font-size-xs);
                  color: var(--color-text-secondary);
                  white-space: nowrap;
                }
              }
            }

            .flow-legend {
              position: absolute;
              bottom: 20px;
              right: 20px;
              display: flex;
              flex-direction: column;
              gap: var(--spacing-2);
              background: var(--color-bg-card);
              padding: var(--spacing-3);
              border-radius: var(--border-radius-lg);
              box-shadow: var(--shadow-sm);

              .legend-item {
                display: flex;
                align-items: center;
                gap: var(--spacing-2);

                .legend-line {
                  width: 24px;
                  height: 4px;
                  border-radius: 2px;

                  &.high {
                    background: var(--color-primary);
                  }

                  &.medium {
                    background: var(--color-secondary);
                  }

                  &.low {
                    background: var(--color-neutral);
                  }
                }

                span {
                  font-size: var(--font-size-xs);
                  color: var(--color-text-secondary);
                }
              }
            }
          }
        }
      }
    }
  }
}

/* 线路负载工具提示 */
.line-tooltip {
  position: fixed;
  z-index: var(--z-index-tooltip);
  background: var(--color-bg-card);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-3);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
  min-width: 200px;
  pointer-events: none;

  .tooltip-header {
    margin-bottom: var(--spacing-2);
    padding-bottom: var(--spacing-2);
    border-bottom: 1px solid var(--color-border-light);

    strong {
      font-size: var(--font-size-base);
      color: var(--color-text-primary);
    }
  }

  .tooltip-content {
    .tooltip-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: var(--spacing-1);

      &:last-child {
        margin-bottom: 0;
      }

      .tooltip-label {
        font-size: var(--font-size-sm);
        color: var(--color-text-secondary);
      }

      .tooltip-value {
        font-size: var(--font-size-sm);
        font-weight: var(--font-weight-medium);
        color: var(--color-text-primary);

        &.positive {
          color: var(--color-success);
        }

        &.negative {
          color: var(--color-error);
        }
      }
    }
  }
}

/* 动画效果 */
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 触摸反馈 */
.touch-target {
  min-height: 44px;
  min-width: 44px;
}

.touch-feedback {
  &:active {
    transform: scale(0.98);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .analytics {
    padding: var(--spacing-4);
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;

    .header-actions {
      justify-content: flex-start;
    }
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .analysis-grid {
    .analysis-card {
      .card-body {
        .load-bars,
        .time-bars,
        .forecast-bars {
          .load-bar-item,
          .time-bar-item,
          .forecast-bar-item {
            grid-template-columns: 1fr;
            gap: var(--spacing-3);

            .bar-stats {
              justify-content: space-between;
            }
          }
        }
      }
    }
  }
}
</style>