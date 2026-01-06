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
        <p class="page-description">客流统计、时空分布和预测分析 (v2.1)</p>
      </div>
      <div class="header-meta">
        <div class="range-chip">
          <span class="chip-label">统计周期</span>
          <span class="chip-value">{{ timeRangeLabel }}</span>
          <span class="chip-sub">（{{ timeRangeDuration }}）</span>
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
    </div>

    <!-- 顶部 Tab 切换 -->
    <div class="analytics-tabs">
      <el-tabs v-model="mainTab" class="main-tabs">
        <el-tab-pane label="客流总览" name="general">
          <div class="general-analytics-content">
            <section class="section time-section">
              <div class="section-header">
                <div>
                  <h2 class="section-title">时间范围</h2>
                  <p class="section-subtitle">选择分析周期，系统会同步刷新所有图表与榜单</p>
                </div>
              </div>
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
                    <span class="stat-label">统计周期</span>
                    <span class="stat-value">{{ timeRangeLabel }}</span>
                    <span class="stat-duration">（{{ timeRangeDuration }}）</span>
                  </div>
                </div>
              </div>
            </section>
            <section class="section kpi-section">
              <div class="section-header">
                <div>
                  <h2 class="section-title">核心指标</h2>
                  <p class="section-subtitle">汇总展示客流规模与核心站点表现</p>
                </div>
              </div>
              <div class="kpi-grid">
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
              </div>
            </section>
            <section class="section analysis-section">
              <div class="section-header">
                <div>
                  <h2 class="section-title">趋势与分布</h2>
                  <p class="section-subtitle">从时间与站点维度观察客流结构</p>
                </div>
              </div>
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
                    <FlowTrendChart
                      :data="trendData"
                      :show-actions="false"
                      :show-footer="false"
                      :show-legend="false"
                      :show-header="false"
                      height="320px"
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
                        总客流量
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
                      :key="rankingMetric"
                      :data="stationRankings"
                      title="站点客流排名"
                      :subtitle="rankingSubtitle"
                      :columns="rankingColumns"
                      :default-sort="rankingSortKey"
                      :show-actions="false"
                    />
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

              </div>
            </section>
          </div>
        </el-tab-pane>
        <el-tab-pane label="线路负载分析" name="load-analysis">
          <div class="load-map-layout">
            <div class="load-map-main">
              <div class="load-map-toolbar">
                <div class="toolbar-group">
                  <span class="toolbar-label">视图切换</span>
                  <el-radio-group v-model="loadViewMode" size="small">
                    <el-radio-button label="flow">客流量视图</el-radio-button>
                    <el-radio-button label="load">负载率视图</el-radio-button>
                  </el-radio-group>
                </div>
                <div class="toolbar-legend">
                  <div class="legend-item"><span class="legend-dot level-0"></span>舒适 (&lt;60%)</div>
                  <div class="legend-item"><span class="legend-dot level-1"></span>适中 (60% - 90%)</div>
                  <div class="legend-item"><span class="legend-dot level-2"></span>拥挤 (&gt;90%)</div>
                  <div class="legend-item"><span class="legend-dot level-3"></span>超载 (&gt;100%)</div>
                </div>
              </div>
              <div class="load-map-container">
                <div v-if="loadMapSegments.length === 0" class="map-empty">暂无负载数据</div>
                <GaodeMap
                  ref="loadMapRef"
                  map-id="load-analysis-map"
                  class-name="gaode-map-container"
                  :fit-view-to-markers="true"
                  :show-controls="true"
                />
              </div>
              <div class="load-timebar">
                <div class="time-info">
                  <span class="time-label">时间</span>
                  <span class="time-value">{{ currentLoadTimeLabel }}</span>
                </div>
                <el-slider
                  v-model="loadTimeIndex"
                  :min="0"
                  :max="loadTimeMax"
                  :marks="loadTimeMarks"
                  :show-tooltip="false"
                  @change="handleLoadTimeChange"
                />
                <el-button size="small" type="primary" plain :disabled="peakTimeIndex === null" @click="jumpToPeakTime">跳转峰值</el-button>
              </div>
            </div>
            <div class="load-map-side">
              <div class="side-header">
                <h4>今日最拥挤区段 Top 5</h4>
                <span class="side-sub">当前时刻 {{ currentLoadTimeLabel }}</span>
              </div>
              <div v-if="topCongestedSegments.length === 0" class="side-empty">暂无区段数据</div>
              <div v-else class="segment-list">
                <button
                  v-for="(segment, index) in topCongestedSegments"
                  :key="segment.id"
                  class="segment-item"
                  @click="focusSegment(segment)"
                >
                  <div class="segment-rank">{{ index + 1 }}</div>
                  <div class="segment-info">
                    <div class="segment-name">{{ segment.start }} -> {{ segment.end }}</div>
                    <div class="segment-meta">
                      <span class="segment-rate" :class="getLoadRateClass(segment.loadRate)">{{ (segment.loadRate * 100).toFixed(1) }}%</span>
                      <span class="segment-gap">剩余运力：{{ segment.capacity - segment.load }}</span>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </el-tab-pane>
        <el-tab-pane label="客流预测" name="forecast">
          <div class="forecast-content">
            <section class="section analysis-section">
              <div class="section-header">
                <div>
                  <h2 class="section-title">客流预测</h2>
                  <p class="section-subtitle">基于历史趋势与实时数据生成预测结果</p>
                </div>
              </div>
              <div class="analysis-grid forecast-grid">
                <div class="analysis-card">
                  <div class="card-header">
                    <h3 class="card-title">客流预测</h3>
                    <div class="card-actions">
                      <div class="view-toggles">
                        <button
                          class="view-toggle-btn"
                          :class="{ active: forecastViewMode === 'bar' }"
                          @click="forecastViewMode = 'bar'"
                          title="柱状图"
                        >
                          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 20V10M12 20V4M6 20V14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                        </button>
                        <button
                          class="view-toggle-btn"
                          :class="{ active: forecastViewMode === 'line' }"
                          @click="forecastViewMode = 'line'"
                          title="折线图"
                        >
                          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M3 17L9 11L13 15L21 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                          </svg>
                        </button>
                      </div>
                      <div class="divider"></div>
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
                        <div v-if="forecastViewMode === 'bar'" class="forecast-bars">
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
                              </div>
                              <div v-if="day.actual" class="bar-track actual">
                                <div
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
                            </div>
                          </div>
                        </div>

                        <div v-else class="forecast-line-chart">
                          <div class="line-chart-wrapper">
                            <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
                              <line v-for="i in 5" :key="i" x1="0" :y1="i * 20" x2="100" :y2="i * 20" stroke="var(--color-border-light)" stroke-width="0.5" vector-effect="non-scaling-stroke" />
                              <polyline :points="forecastChartPoints.forecast" fill="none" stroke="var(--color-secondary)" stroke-width="2" vector-effect="non-scaling-stroke" stroke-dasharray="4 2" />
                              <polyline :points="forecastChartPoints.actual" fill="none" stroke="var(--color-error)" stroke-width="2" vector-effect="non-scaling-stroke" />
                            </svg>
                          </div>
                          <div class="chart-labels">
                            <div v-for="(point, index) in forecastChartPoints.points" :key="index" class="chart-label" :style="{ left: point.x + '%' }">
                              <div class="label-date">{{ point.data.date }}</div>
                              <div class="label-day">{{ point.data.day }}</div>
                            </div>
                          </div>
                          <div class="chart-legend">
                            <div class="legend-item">
                              <div class="legend-line forecast"></div>
                              <span>预测值</span>
                            </div>
                            <div class="legend-item">
                              <div class="legend-line actual"></div>
                              <span>实际值</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { usePassengerStore } from '@/stores/passenger';
import { useMapStore } from '@/stores/map';
import { format, startOfWeek, endOfWeek, startOfMonth, endOfMonth, startOfQuarter, endOfQuarter, startOfYear, endOfYear, differenceInCalendarDays } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { apiService } from '@/services/api';

import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import AnimatedNumber from '@/components/ui/AnimatedNumber.vue';
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue';
import FlowTrendChart from '@/components/passenger/FlowTrendChart.vue';
import StationRankingTable from '@/components/passenger/StationRankingTable.vue';
import GaodeMap from '@/components/map/GaodeMap.vue';
import type { StationMarker, FlowLine } from '@/types/map';

const passengerStore = usePassengerStore();
const mapStore = useMapStore();

const mainTab = ref<'general' | 'load-analysis' | 'forecast'>('general');
const isLoading = ref(false);
const isRefreshing = ref(false);
const selectedRange = ref<'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom'>('week');
const startDate = ref('');
const endDate = ref('');

const trendFrequency = ref<'hourly' | 'daily' | 'weekly' | 'monthly'>('daily');
const rankingMetric = ref<'total' | 'inbound' | 'outbound'>('total');
const timeDistributionType = ref<'hourly' | 'daily' | 'weekly'>('hourly');
const forecastDays = ref<7 | 14 | 30>(7);
const forecastViewMode = ref<'bar' | 'line'>('bar');

const timeRangeLabel = computed(() => {
  const now = new Date();
  switch (selectedRange.value) {
    case 'today':
      return format(now, 'yyyy年MM月dd日', { locale: zhCN });
    case 'week': {
      const weekStart = startOfWeek(now, { locale: zhCN });
      const weekEnd = endOfWeek(now, { locale: zhCN });
      return `${format(weekStart, 'MM/dd')} - ${format(weekEnd, 'MM/dd')}`;
    }
    case 'month':
      return format(now, 'yyyy年MM月', { locale: zhCN });
    case 'quarter': {
      const quarterStart = startOfQuarter(now);
      const quarterEnd = endOfQuarter(now);
      return `${format(quarterStart, 'MM/dd')} - ${format(quarterEnd, 'MM/dd')}`;
    }
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
  if (startDate.value && endDate.value) {
    const start = new Date(startDate.value);
    const end = new Date(endDate.value);
    if (!Number.isNaN(start.getTime()) && !Number.isNaN(end.getTime())) {
      const days = Math.abs(differenceInCalendarDays(end, start)) + 1;
      return `${days}天`;
    }
  }

  switch (selectedRange.value) {
    case 'today': return '1天';
    case 'week': return '7天';
    case 'month': return '30天';
    case 'quarter': return '90天';
    case 'year': return '365天';
    case 'custom': return '自定义';
    default: return '';
  }
});

const kpiData = computed(() => {
  const trends = passengerStore.flowTrends;
  const rankings = passengerStore.stationRankings;
  const trendValues = passengerStore.kpiTrends;

  if (!trends || rankings.length === 0) {
    return {
      totalPassengers: 0,
      avgPassengers: 0,
      peakStationName: '无数据',
      peakStationValue: 0,
      trends: {
        totalPassengers: trendValues.totalPassengers || 0,
        avgPassengers: trendValues.avgPassengers || 0,
        peakStation: trendValues.peakStation || 0
      }
    };
  }

  const peakStation = rankings.length > 0 ? rankings[0] : null;

  return {
    totalPassengers: trends.total || 0,
    avgPassengers: trends.average || 0,
    peakStationName: peakStation?.stationName || '无数据',
    peakStationValue: peakStation?.totalPassengers || 0,
    trends: {
      totalPassengers: trendValues.totalPassengers || 0,
      avgPassengers: trendValues.avgPassengers || 0,
      peakStation: trendValues.peakStation || 0
    }
  };
});

const trendData = computed(() => {
  const trends = passengerStore.flowTrends;
  if (!trends) {
    return {
      granularity: 'day' as const,
      data: [],
      total: 0,
      average: 0,
      max: 0,
      min: 0,
      growthRate: 0
    };
  }
  return trends;
});

const rankingConfig = {
  total: { key: 'totalPassengers', label: '总客流量', subtitle: '按总客流量排序' },
  inbound: { key: 'passengersIn', label: '到达客流', subtitle: '按到达客流排序' },
  outbound: { key: 'passengersOut', label: '发送客流', subtitle: '按发送客流排序' }
} as const;

const rankingSortKey = computed(() => rankingConfig[rankingMetric.value].key);
const rankingSubtitle = computed(() => rankingConfig[rankingMetric.value].subtitle);
const rankingColumns = computed(() => [
  {
    key: rankingConfig[rankingMetric.value].key,
    label: rankingConfig[rankingMetric.value].label,
    sortable: false,
    visible: true
  }
]);

const stationRankings = computed(() => {
  const rankings = passengerStore.stationRankings;
  if (rankings.length === 0) {
    return [];
  }

  const sorted = [...rankings].sort((a, b) => {
    const aValue = a[rankingSortKey.value] || 0;
    const bValue = b[rankingSortKey.value] || 0;
    return bValue - aValue;
  });

  return sorted.map((station, index) => ({
    ...station,
    ranking: index + 1
  }));
});

const timeDistributionData = computed(() => {
  const periods = passengerStore.timePeriods;
  if (!Array.isArray(periods) || periods.length === 0) {
    return [];
  }
  return [...periods].sort((a, b) => a.id - b.id);
});

const forecastData = computed(() => {
  const forecasts = passengerStore.flowForecasts;
  if (forecasts.length === 0) {
    return [];
  }

  const sliced = forecasts.slice(0, forecastDays.value);
  const maxValue = Math.max(...sliced.map((item) => item.forecast || 0), 0);

  return sliced.map((item, index) => {
    const date = new Date(item.timestamp);
    const forecast = Math.round(item.forecast);
    const actual = item.actual ? Math.round(item.actual) : undefined;
    const confidence = item.confidence ?? 0;
    const confidencePercent = confidence <= 1 ? Math.round(confidence * 100) : Math.round(confidence);

    return {
      id: index,
      day: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date.getDay()],
      date: format(date, 'MM/dd'),
      forecast,
      actual,
      percentage: maxValue > 0 ? (forecast / maxValue) * 100 : 0,
      actualPercentage: actual && maxValue > 0 ? (actual / maxValue) * 100 : 0,
      confidence: confidencePercent
    };
  });
});

const forecastChartPoints = computed(() => {
  const data = forecastData.value;
  if (!data.length) {
    return { forecast: '', actual: '', points: [] as Array<{ x: number; yForecast: number; yActual: number | null; data: any }> };
  }

  const maxValue = Math.max(...data.map((item) => Math.max(item.forecast, item.actual || 0)), 0);
  const points = data.map((item, index) => {
    const x = data.length === 1 ? 50 : (index / (data.length - 1)) * 100;
    const yForecast = maxValue > 0 ? 100 - (item.forecast / maxValue) * 100 : 100;
    const yActual = item.actual !== undefined && maxValue > 0 ? 100 - (item.actual / maxValue) * 100 : null;
    return { x, yForecast, yActual, data: item };
  });

  const forecast = points.map((point) => `${point.x},${point.yForecast}`).join(' ');
  const actual = points.filter((point) => point.yActual !== null).map((point) => `${point.x},${point.yActual}`).join(' ');

  return { forecast, actual, points };
});

const setPresetDateRange = (range: 'today' | 'week' | 'month' | 'quarter' | 'year') => {
  const now = new Date();
  let rangeStart = now;
  let rangeEnd = now;

  switch (range) {
    case 'today':
      break;
    case 'week':
      rangeStart = startOfWeek(now, { locale: zhCN });
      rangeEnd = endOfWeek(now, { locale: zhCN });
      break;
    case 'month':
      rangeStart = startOfMonth(now);
      rangeEnd = endOfMonth(now);
      break;
    case 'quarter':
      rangeStart = startOfQuarter(now);
      rangeEnd = endOfQuarter(now);
      break;
    case 'year':
      rangeStart = startOfYear(now);
      rangeEnd = endOfYear(now);
      break;
    default:
      break;
  }

  startDate.value = format(rangeStart, 'yyyy-MM-dd');
  endDate.value = format(rangeEnd, 'yyyy-MM-dd');
};

const getGranularity = (frequency: 'hourly' | 'daily' | 'weekly' | 'monthly') => {
  switch (frequency) {
    case 'hourly':
      return 'hour';
    case 'weekly':
      return 'week';
    case 'monthly':
      return 'month';
    case 'daily':
    default:
      return 'day';
  }
};

const selectTimeRange = (range: 'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom') => {
  selectedRange.value = range;
  if (range !== 'custom') {
    setPresetDateRange(range);
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
  alert('导出功能开发中...');
};

const changeTrendFrequency = (frequency: 'hourly' | 'daily' | 'weekly' | 'monthly') => {
  trendFrequency.value = frequency;
  loadData();
};

const changeRankingMetric = (metric: 'total' | 'inbound' | 'outbound') => {
  rankingMetric.value = metric;
};

const changeTimeDistributionType = (type: 'hourly' | 'daily' | 'weekly') => {
  timeDistributionType.value = type;
  passengerStore.fetchTimePeriods(type).catch((error) => {
    console.error('加载时间分布数据失败:', error);
  });
};

const changeForecastDays = (days: 7 | 14 | 30) => {
  forecastDays.value = days;
  passengerStore.fetchFlowForecasts(days).catch((error) => {
    console.error('加载预测数据失败:', error);
  });
};

const getTimeDistributionClass = (percentage: number) => {
  if (percentage >= 20) return 'high';
  if (percentage >= 10) return 'medium';
  return 'low';
};

const loadData = async () => {
  isLoading.value = true;
  try {
    if (startDate.value && endDate.value) {
      passengerStore.setTimeRange(startDate.value, endDate.value);
    }
    passengerStore.setTimeGranularity(getGranularity(trendFrequency.value));
    await passengerStore.fetchComprehensiveAnalysis({
      forecastDays: forecastDays.value,
      timeDistributionType: timeDistributionType.value
    });
  } catch (error) {
    console.error('加载数据失败:', error);
  } finally {
    isLoading.value = false;
  }
};

// 线路负载分析
const loadViewMode = ref<'flow' | 'load'>('flow');
const loadSegments = ref<Array<{ id: string; time: string; route: string; start: string; end: string; load: number; capacity: number; loadRate: number; gap: number }>>([]);
const loadTimes = ref<string[]>([]);
const loadTimeIndex = ref(0);
const peakTimeIndex = ref<number | null>(null);
const focusedSegmentId = ref<string | null>(null);
const loadMapRef = ref<InstanceType<typeof GaodeMap> | null>(null);
const loadMapLoading = ref(false);

const loadTimeMax = computed(() => Math.max(loadTimes.value.length - 1, 0));

const currentLoadTimeLabel = computed(() => {
  const time = loadTimes.value[loadTimeIndex.value];
  if (!time) return '暂无';
  const parsed = new Date(time);
  if (Number.isNaN(parsed.getTime())) return time;
  return format(parsed, 'yyyy-MM-dd');
});

const loadTimeMarks = computed(() => {
  const marks: Record<number, string> = {};
  if (loadTimes.value.length === 0) return marks;

  const step = Math.max(1, Math.floor(loadTimes.value.length / 4));
  loadTimes.value.forEach((time, index) => {
    if (index % step === 0 || index === loadTimes.value.length - 1) {
      const parsed = new Date(time);
      marks[index] = Number.isNaN(parsed.getTime()) ? time : format(parsed, 'MM/dd');
    }
  });
  return marks;
});

const loadMapSegments = computed(() => {
  const time = loadTimes.value[loadTimeIndex.value];
  if (!time) return [];
  return loadSegments.value.filter((segment) => segment.time === time);
});

const topCongestedSegments = computed(() => {
  return [...loadMapSegments.value]
    .sort((a, b) => (b.loadRate || 0) - (a.loadRate || 0))
    .slice(0, 5);
});

const getLoadRateClass = (loadRate: number) => {
  if (loadRate > 1) return 'level-3';
  if (loadRate > 0.9) return 'level-2';
  if (loadRate >= 0.6) return 'level-1';
  return 'level-0';
};

const getLoadRateColor = (loadRate: number) => {
  if (loadRate > 1) return '#6a00ff';
  if (loadRate > 0.9) return '#f44336';
  if (loadRate >= 0.6) return '#ff9800';
  return '#4caf50';
};

const buildLoadMapLines = () => {
  const stations = passengerStore.spatialDistribution;
  if (!stations.length) return [] as FlowLine[];
  const stationByName = new Map(stations.map((station) => [station.stationName, station]));
  const segments = loadMapSegments.value;
  if (!segments.length) return [] as FlowLine[];

  const maxLoad = Math.max(...segments.map((segment) => segment.load), 1);

  return segments
    .map((segment) => {
      const from = stationByName.get(segment.start);
      const to = stationByName.get(segment.end);
      if (!from || !to) return null;

      const baseWidth = 2;
      const width = loadViewMode.value === 'flow' ? baseWidth + (segment.load / maxLoad) * 4 : 2.2;
      const color = loadViewMode.value === 'flow' ? '#4c9bff' : getLoadRateColor(segment.loadRate);
      const arrowColor = '#ffffff';

      return {
        id: segment.id,
        fromStationId: from.stationId,
        toStationId: to.stationId,
        fromStationName: from.stationName,
        toStationName: to.stationName,
        fromPosition: [from.longitude, from.latitude],
        toPosition: [to.longitude, to.latitude],
        passengers: segment.load,
        color,
        arrowColor,
        width,
        loadRate: segment.loadRate,
        capacity: segment.capacity,
        load: segment.load,
        gap: segment.gap,
        route: segment.route,
        time: segment.time,
        blink: segment.loadRate > 1,
        selected: segment.id === focusedSegmentId.value
      } as FlowLine;
    })
    .filter(Boolean) as FlowLine[];
};

const syncLoadMapMarkers = () => {
  const stations = passengerStore.spatialDistribution;
  if (!stations.length) {
    mapStore.setStationMarkers([]);
    return;
  }

  const maxPassengers = Math.max(...stations.map((station) => station.totalPassengers), 1);
  const markers: StationMarker[] = stations.map((station) => {
    const scale = 0.5 + (station.totalPassengers / maxPassengers) * 1.2;
    return {
      stationId: station.stationId,
      stationName: station.stationName,
      position: [station.longitude, station.latitude],
      size: Math.max(18, Math.min(42, scale * 24)),
      color: station.color,
      passengerCount: station.totalPassengers,
      data: station
    };
  });

  mapStore.setStationMarkers(markers);
};

const applyLoadMapConfig = () => {
  mapStore.updateMapConfig({
    showFlowLines: true,
    showStationMarkers: true,
    showHeatmap: false,
    showTraffic: false
  });
};

const updateLoadMapLines = () => {
  const lines = buildLoadMapLines();
  mapStore.setFlowLines(lines);
};

const focusSegment = async (segment: { id: string; start: string; end: string }) => {
  focusedSegmentId.value = segment.id;
  await nextTick();
  updateLoadMapLines();
  loadMapRef.value?.focusFlowLine(segment.id);

  const line = mapStore.flowLines.find((item) => item.id === segment.id);
  if (line) {
    const [lng1, lat1] = line.fromPosition;
    const [lng2, lat2] = line.toPosition;
    mapStore.zoomToBounds([
      [Math.min(lng1, lng2), Math.min(lat1, lat2)],
      [Math.max(lng1, lng2), Math.max(lat1, lat2)]
    ]);
  }
};

const handleLoadTimeChange = () => {
  focusedSegmentId.value = null;
  updateLoadMapLines();
};

const jumpToPeakTime = () => {
  if (peakTimeIndex.value === null) return;
  loadTimeIndex.value = peakTimeIndex.value;
  handleLoadTimeChange();
};

const loadLoadAnalysisMap = async () => {
  if (loadMapLoading.value) return;
  loadMapLoading.value = true;
  try {
    applyLoadMapConfig();
    await passengerStore.fetchSpatialDistribution();
    syncLoadMapMarkers();

    const params = {
      start_date: passengerStore.analysisParams.startDate,
      end_date: passengerStore.analysisParams.endDate
    };

    const response = await apiService.loadAnalysis.getSegments(params);
    const times = response?.times ?? [];
    const segments = (response?.segments ?? []).map((item: any) => {
      const loadRate = item.load_rate ?? item.loadRate ?? 0;
      return {
        id: `${item.route}|${item.start}|${item.end}`,
        time: item.time,
        route: item.route,
        start: item.start,
        end: item.end,
        load: item.load,
        capacity: item.capacity,
        loadRate,
        gap: item.gap ?? (item.load - item.capacity)
      };
    });

    loadTimes.value = times;
    loadSegments.value = segments;

    const peakTime = response?.peak_time ?? null;
    peakTimeIndex.value = peakTime ? times.findIndex((time: string) => time === peakTime) : null;
    loadTimeIndex.value = times.length > 0 ? times.length - 1 : 0;

    updateLoadMapLines();
  } catch (error) {
    console.error('加载负载分析数据失败:', error);
    loadTimes.value = [];
    loadSegments.value = [];
    peakTimeIndex.value = null;
  } finally {
    loadMapLoading.value = false;
  }
};

watch([loadViewMode, loadTimeIndex], () => {
  updateLoadMapLines();
});

watch(mainTab, (tab) => {
  if (tab === 'load-analysis') {
    loadLoadAnalysisMap();
  }
});

onMounted(async () => {
  const synced = await passengerStore.syncDateRangeFromStats();
  if (synced) {
    selectedRange.value = 'custom';
    startDate.value = passengerStore.analysisParams.startDate;
    endDate.value = passengerStore.analysisParams.endDate;
  } else {
    selectedRange.value = 'custom';
    startDate.value = passengerStore.analysisParams.startDate;
    endDate.value = passengerStore.analysisParams.endDate;
  }
  await loadData();
  if (mainTab.value === 'load-analysis') {
    loadLoadAnalysisMap();
  }
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

.header-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.range-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--border-radius-full);
  background: var(--color-bg-tertiary);
  border: 1px solid var(--color-border-light);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.chip-label {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.chip-value {
  color: var(--color-text-primary);
}

.chip-sub {
  color: var(--color-text-tertiary);
}

.section {
  margin-bottom: var(--spacing-8);
}

.section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-4);
}

.section-title {
  margin: 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.section-subtitle {
  margin: var(--spacing-1) 0 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
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
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
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
      .flow-container,
      .station-map-container {
        height: 400px;
        border-radius: var(--border-radius-lg);
        overflow: hidden;
        background: var(--color-bg-tertiary);
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;

      .map-empty {
        color: var(--color-text-secondary);
        font-size: var(--font-size-sm);
        position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          z-index: 2;
          background: rgba(255, 255, 255, 0.85);
          padding: var(--spacing-2) var(--spacing-4);
          border-radius: var(--border-radius-full);
        }

        .gaode-map-container {
          width: 100%;
          height: 100%;
        }

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

              .flow-empty {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: var(--color-text-secondary);
                font-size: var(--font-size-sm);
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

.forecast-grid {
  grid-template-columns: 1fr;
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

/* 视图切换按钮 */
.view-toggles {
  display: flex;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  padding: 2px;
  margin-right: var(--spacing-2);
}

.view-toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.view-toggle-btn:hover {
  color: var(--color-text-primary);
}

.view-toggle-btn.active {
  background-color: white;
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.view-toggle-btn svg {
  width: 18px;
  height: 18px;
}

.divider {
  width: 1px;
  height: 24px;
  background-color: var(--color-border);
  margin: 0 var(--spacing-2);
}

/* 预测折线图 */
.forecast-line-chart {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--spacing-2) 0;
}

.line-chart-wrapper {
  flex: 1;
  position: relative;
  margin-bottom: var(--spacing-4);
  padding: 0 var(--spacing-4);
}

.chart-labels {
  position: relative;
  height: 40px;
  margin: 0 var(--spacing-4);
}

.chart-label {
  position: absolute;
  transform: translateX(-50%);
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.label-date {
  font-weight: var(--font-weight-medium);
  margin-bottom: 2px;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: var(--spacing-4);
  margin-top: var(--spacing-2);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.legend-line {
  width: 24px;
  height: 2px;
}

.legend-line.forecast {
  background-color: transparent;
  border-top: 2px dashed var(--color-secondary);
}

.legend-line.actual {
  background-color: var(--color-error);
}

/* 线路负载分析样式 */
.load-analysis-content {
  padding: var(--spacing-4) 0;
}

.filter-bar {
  display: flex;
  gap: var(--spacing-6);
  align-items: center;
  background: var(--color-bg-tertiary);
  padding: var(--spacing-4);
  border-radius: var(--border-radius-lg);
  
  .filter-group {
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
    
    .label {
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);
      font-weight: var(--font-weight-medium);
    }
  }
}

.chart-row {
  display: flex;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-4);
  
  .chart-card {
    background: var(--color-bg-card);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-4);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--color-border-light);
    
    &.half {
      flex: 1;
      min-width: 0; /* Prevent flex overflow */
    }
    
    &.full {
      width: 100%;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--spacing-4);
      
      h3 {
        margin: 0;
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-semibold);
      }
    }
    
    .chart-container {
      height: 300px;
      width: 100%;
    }
  }
}

.map-view-container {
  position: relative;
  height: 600px;
  background: var(--color-bg-tertiary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  
  .map-controls-overlay {
    position: absolute;
    top: var(--spacing-4);
    left: var(--spacing-4);
    z-index: 10;
    background: rgba(255, 255, 255, 0.9);
    padding: var(--spacing-3);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-md);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-3);
    backdrop-filter: blur(4px);
    
    .threshold-slider {
      width: 200px;
      padding: 0 var(--spacing-2);
      
      .slider-label {
        font-size: var(--font-size-xs);
        color: var(--color-text-secondary);
        display: block;
        margin-bottom: var(--spacing-1);
      }
    }
  }
  
  .map-chart {
    height: 100%;
    width: 100%;
  }
}

.bottleneck-layout {
  display: flex;
  gap: var(--spacing-4);
  
  .ranking-section {
    flex: 3;
    background: var(--color-bg-card);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-4);
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--spacing-3);
      
      h3 { margin: 0; font-size: var(--font-size-base); }
    }
    
    .rank-badge {
      display: inline-block;
      width: 20px;
      height: 20px;
      line-height: 20px;
      text-align: center;
      border-radius: 50%;
      background: var(--color-bg-tertiary);
      font-size: var(--font-size-xs);
      color: var(--color-text-secondary);
      
      &.rank-1 { background: #F56C6C; color: white; }
      &.rank-2 { background: #E6A23C; color: white; }
      &.rank-3 { background: #409EFF; color: white; }
    }
  }
  
  .chart-section {
    flex: 2;
    
    .chart-card {
      height: 100%;
      background: var(--color-bg-card);
      border-radius: var(--border-radius-lg);
      padding: var(--spacing-4);
      
      h3 { margin: 0 0 var(--spacing-4) 0; font-size: var(--font-size-base); }
      
      .chart-container {
        height: 400px;
      }
    }
  }
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-6);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
  
  .detail-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-3);
    
    .line-tag {
      background: var(--color-primary);
      color: white;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: var(--font-size-xs);
    }
    
    .section-name {
      font-size: var(--font-size-xl);
      font-weight: bold;
    }
  }
  
  .detail-meta {
    display: flex;
    gap: var(--spacing-4);
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
  }
}

.text-error { color: var(--color-error); }
.text-warning { color: var(--color-warning); }
.text-success { color: var(--color-success); }
.text-primary { color: var(--color-primary); }

.kpi-grid.mini {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-4);
  margin-top: var(--spacing-4);
  
  .kpi-card.mini {
    background: var(--color-bg-tertiary);
    padding: var(--spacing-3);
    border-radius: var(--border-radius-lg);
    text-align: center;
    
    .label { font-size: var(--font-size-xs); color: var(--color-text-secondary); }
    .value { font-size: var(--font-size-xl); font-weight: bold; margin: var(--spacing-1) 0; }
    .sub { font-size: var(--font-size-xs); color: var(--color-text-tertiary); }
  }
}

/* 线路负载分析地图 */
.load-map-layout {
  display: flex;
  gap: var(--spacing-4);
}

.load-map-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.load-map-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-3);
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-3);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.toolbar-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.toolbar-legend {
  display: flex;
  gap: var(--spacing-3);
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.level-0 { background: #4caf50; }
.legend-dot.level-1 { background: #ff9800; }
.legend-dot.level-2 { background: #f44336; }
.legend-dot.level-3 { background: #6a00ff; }

.load-map-container {
  height: 520px;
  border-radius: var(--border-radius-base);
  overflow: hidden;
  background-color: var(--color-bg-secondary);
  position: relative;
}

.load-timebar {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
}

.load-timebar .el-slider {
  flex: 1;
}

.time-info {
  min-width: 140px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.time-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.time-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.load-map-side {
  width: 320px;
  background: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-3);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.side-header h4 {
  margin: 0;
  font-size: var(--font-size-base);
}

.side-sub {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.side-empty {
  text-align: center;
  color: var(--color-text-secondary);
  padding: var(--spacing-4) 0;
}

.segment-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.segment-item {
  display: flex;
  gap: var(--spacing-2);
  align-items: center;
  padding: var(--spacing-2);
  background: var(--color-bg-primary);
  border-radius: var(--border-radius-base);
  border: 1px solid var(--color-border-light);
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.segment-item:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.segment-rank {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--color-bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.segment-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.segment-name {
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.segment-meta {
  display: flex;
  gap: var(--spacing-2);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.segment-rate {
  font-weight: 600;
}

.segment-rate.rate-low { color: #4caf50; }
.segment-rate.rate-medium { color: #ff9800; }
.segment-rate.rate-high { color: #f44336; }
.segment-rate.rate-overload { color: #6a00ff; }

@media (max-width: 1024px) {
  .load-map-layout {
    flex-direction: column;
  }

  .load-map-side {
    width: 100%;
  }
}
</style>
