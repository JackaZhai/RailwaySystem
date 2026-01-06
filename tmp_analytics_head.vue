<template>
  <div class="analytics animate-fade-in">
    <!-- 鍏ㄥ眬鍔犺浇鐘舵€?-->
    <LoadingSpinner
      v-if="isLoading"
      size="large"
      variant="primary"
      text="姝ｅ湪鍔犺浇瀹㈡祦鍒嗘瀽鏁版嵁..."
      fullscreen
    />

    <!-- 椤甸潰鏍囬鍜屾搷浣?-->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">瀹㈡祦鍒嗘瀽</h1>
        <p class="page-description">瀹㈡祦缁熻銆佹椂绌哄垎甯冨拰棰勬祴鍒嗘瀽</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary touch-target touch-feedback" :disabled="isRefreshing" @click="refreshData">
          <svg v-if="!isRefreshing" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C14.1974 3 16.1958 3.86095 17.6576 5.27264M21 3V7M21 7H17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else class="animate-spin" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2V6M12 18V22M4.93 4.93L7.76 7.76M16.24 16.24L19.07 19.07M2 12H6M18 12H22M4.93 19.07L7.76 16.24M16.24 7.76L19.07 4.93" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          {{ isRefreshing ? '鍒锋柊涓?..' : '鍒锋柊鏁版嵁' }}
        </button>
        <button class="btn btn-outline touch-target touch-feedback" @click="exportData">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          瀵煎嚭鎶ュ憡
        </button>
      </div>
    </div>

    <!-- 鏃堕棿绛涢€?-->
    <div class="time-filter animate-fade-in">
      <div class="filter-container">
        <div class="filter-group">
          <label class="filter-label">鏃堕棿鑼冨洿</label>
          <div class="filter-buttons">
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'today' }"
              @click="selectTimeRange('today')"
            >
              浠婂ぉ
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'week' }"
              @click="selectTimeRange('week')"
            >
              鏈懆
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'month' }"
              @click="selectTimeRange('month')"
            >
              鏈湀
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'quarter' }"
              @click="selectTimeRange('quarter')"
            >
              鏈搴?            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'year' }"
              @click="selectTimeRange('year')"
            >
              鏈勾
            </button>
            <button
              class="filter-btn touch-target touch-feedback"
              :class="{ active: selectedRange === 'custom' }"
              @click="selectTimeRange('custom')"
            >
              鑷畾涔?            </button>
          </div>
        </div>
        <div v-if="selectedRange === 'custom'" class="date-picker">
          <input
            v-model="startDate"
            type="date"
            class="date-input"
            @change="updateCustomDateRange"
          />
          <span class="date-separator">鑷?/span>
          <input
            v-model="endDate"
            type="date"
            class="date-input"
            @change="updateCustomDateRange"
          />
        </div>
        <div v-if="selectedRange !== 'custom'" class="filter-stats">
          <span class="stat-label">缁熻鍛ㄦ湡锛?/span>
          <span class="stat-value">{{ timeRangeLabel }}</span>
          <span class="stat-duration">锛坽{ timeRangeDuration }}锛?/span>
        </div>
      </div>
    </div>

    <!-- KPI鎸囨爣鍗＄墖 -->
    <div class="kpi-grid">
      <!-- 鎬诲娴侀噺鍗＄墖 -->
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
            <p class="kpi-label">鎬诲娴侀噺</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">{{ timeRangeLabel }}</span>
        </div>
      </div>

      <!-- 绔欑偣骞冲潎瀹㈡祦 -->
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
            <p class="kpi-label">绔欑偣骞冲潎瀹㈡祦</p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">{{ timeRangeLabel }}</span>
        </div>
      </div>

      <!-- 鏈€楂樺娴佺珯鐐?-->
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
            <p class="kpi-label">鏈€楂樺娴佺珯鐐?/p>
          </template>
          <div v-else class="kpi-skeleton">
            <SkeletonLoader type="text" :lines="2" />
          </div>
        </div>
        <div class="kpi-footer">
          <span class="kpi-period">{{ kpiData.peakStationValue.toLocaleString() }} 浜?/span>
        </div>
      </div>

    </div>

    <!-- 涓昏鍒嗘瀽鍖哄煙 -->
    <div class="analysis-grid">
      <!-- 瀹㈡祦瓒嬪娍鍒嗘瀽 -->
      <div class="analysis-card">
        <div class="card-header">
          <h3 class="card-title">瀹㈡祦瓒嬪娍鍒嗘瀽</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: trendFrequency === 'hourly' }"
              @click="changeTrendFrequency('hourly')"
            >
              灏忔椂
            </button>
            <button
              class="card-action-btn"
              :class="{ active: trendFrequency === 'daily' }"
              @click="changeTrendFrequency('daily')"
            >
              鏃?            </button>
            <button
              class="card-action-btn"
              :class="{ active: trendFrequency === 'weekly' }"
              @click="changeTrendFrequency('weekly')"
            >
              鍛?            </button>
            <button
              class="card-action-btn"
              :class="{ active: trendFrequency === 'monthly' }"
              @click="changeTrendFrequency('monthly')"
            >
              鏈?            </button>
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

      <!-- 绔欑偣瀹㈡祦鎺掑悕 -->
      <div class="analysis-card">
        <div class="card-header">
          <h3 class="card-title">绔欑偣瀹㈡祦鎺掑悕</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: rankingMetric === 'total' }"
              @click="changeRankingMetric('total')"
            >
              鎬诲娴?            </button>
            <button
              class="card-action-btn"
              :class="{ active: rankingMetric === 'inbound' }"
              @click="changeRankingMetric('inbound')"
            >
              鍒拌揪瀹㈡祦
            </button>
            <button
              class="card-action-btn"
              :class="{ active: rankingMetric === 'outbound' }"
              @click="changeRankingMetric('outbound')"
            >
              鍙戦€佸娴?            </button>
          </div>
        </div>
        <div class="card-body">
          <StationRankingTable
            :key="rankingMetric"
            :data="stationRankings"
            title="绔欑偣瀹㈡祦鎺掑悕"
            :subtitle="rankingSubtitle"
            :columns="rankingColumns"
            :default-sort="rankingSortKey"
            :show-actions="false"
          />
        </div>
      </div>

      <!-- 绾胯矾璐熻浇鍒嗘瀽 -->
      <div class="analysis-card">
        <div class="card-header">
          <h3 class="card-title">绾胯矾璐熻浇鍒嗘瀽</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: loadMetric === 'occupancy' }"
              @click="changeLoadMetric('occupancy')"
            >
              涓婂骇鐜?            </button>
            <button
              class="card-action-btn"
              :class="{ active: loadMetric === 'load' }"
              @click="changeLoadMetric('load')"
            >
              婊¤浇鐜?            </button>
            <button
              class="card-action-btn"
              :class="{ active: loadMetric === 'efficiency' }"
              @click="changeLoadMetric('efficiency')"
            >
              杩愯惀鏁堢巼
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
                        <div class="stat-label">涓婂骇鐜?/div>
                        <div class="stat-value">{{ line.occupancyRate }}%</div>
                      </div>
                      <div class="stat">
                        <div class="stat-label">婊¤浇鐜?/div>
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

      <!-- 鏃剁┖鍒嗗竷鍦板浘 -->
      <div class="analysis-card map-card">
        <div class="card-header">
          <h3 class="card-title">瀹㈡祦鏃剁┖鍒嗗竷</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: mapViewMode === 'heatmap' }"
              @click="changeMapViewMode('heatmap')"
            >
              鐑姏鍥?            </button>
            <button
              class="card-action-btn"
              :class="{ active: mapViewMode === 'flow' }"
              @click="changeMapViewMode('flow')"
            >
              娴佸悜鍥?            </button>
            <button
              class="card-action-btn"
              :class="{ active: mapViewMode === 'markers' }"
              @click="changeMapViewMode('markers')"
            >
              绔欑偣鏍囪
            </button>
          </div>
        </div>
        <div class="card-body">
          <!-- 鐑姏鍥炬ā寮?-->
          <div v-if="mapViewMode === 'heatmap'" class="heatmap-container">
            <div v-if="heatmapData.length === 0" class="heatmap-empty">鏆傛棤鐑姏鍥炬暟鎹?/div>
            <HeatMapChart
              v-else
              title="绔欑偣瀹㈡祦鐑姏鍥?
              :data="heatmapData"
              :x-labels="heatmapLabels.x"
              :y-labels="heatmapLabels.y"
            />
          </div>

          <!-- 娴佸悜鍥炬ā寮?-->
          <div v-if="mapViewMode === 'flow'" class="flow-container">
            <div class="flow-placeholder">
              <div class="flow-mock">
                <div class="flow-map">
                  <div class="flow-grid">
                    <div v-for="i in 10" :key="i" class="grid-line"></div>
                  </div>
                  <div v-if="flowData.length === 0" class="flow-empty">鏆傛棤娴佸悜鏁版嵁</div>
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
                    <span>楂樻祦閲?/span>
                  </div>
                  <div class="legend-item">
                    <div class="legend-line medium"></div>
                    <span>涓祦閲?/span>
                  </div>
                  <div class="legend-item">
                    <div class="legend-line low"></div>
                    <span>浣庢祦閲?/span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 绔欑偣鏍囪妯″紡 -->
          <div v-if="mapViewMode === 'markers'" class="station-map-container">
            <StationMap
              title="鎴愭笣鍦板尯閾佽矾绔欑偣鍒嗗竷"
            />
          </div>
        </div>
      </div>

      <!-- 鏃堕棿鍒嗗竷鍒嗘瀽 -->
      <div class="analysis-card">
        <div class="card-header">
          <h3 class="card-title">鏃堕棿鍒嗗竷鍒嗘瀽</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: timeDistributionType === 'hourly' }"
              @click="changeTimeDistributionType('hourly')"
            >
              灏忔椂鍒嗗竷
            </button>
            <button
              class="card-action-btn"
              :class="{ active: timeDistributionType === 'daily' }"
              @click="changeTimeDistributionType('daily')"
            >
              鏃ュ垎甯?            </button>
            <button
              class="card-action-btn"
              :class="{ active: timeDistributionType === 'weekly' }"
              @click="changeTimeDistributionType('weekly')"
            >
              鍛ㄥ垎甯?            </button>
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
                      <div class="stat-label">瀹㈡祦閲?/div>
                      <div class="stat-value">{{ period.passengers.toLocaleString() }}</div>
                    </div>
                    <div class="stat">
                      <div class="stat-label">杞︽</div>
                      <div class="stat-value">{{ period.trains }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 瀹㈡祦棰勬祴 -->
      <div class="analysis-card">
        <div class="card-header">
          <h3 class="card-title">瀹㈡祦棰勬祴</h3>
          <div class="card-actions">
            <button
              class="card-action-btn"
              :class="{ active: forecastDays === 7 }"
              @click="changeForecastDays(7)"
            >
              7澶?            </button>
            <button
              class="card-action-btn"
              :class="{ active: forecastDays === 14 }"
              @click="changeForecastDays(14)"
            >
              14澶?            </button>
            <button
              class="card-action-btn"
              :class="{ active: forecastDays === 30 }"
              @click="changeForecastDays(30)"
            >
              30澶?            </button>
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
                      <div class="stat-label">棰勬祴</div>
                      <div class="stat-value">{{ day.forecast.toLocaleString() }}</div>
                    </div>
                    <div v-if="day.actual" class="stat">
                      <div class="stat-label">瀹為檯</div>
                      <div class="stat-value">{{ day.actual.toLocaleString() }}</div>
                    </div>
                    <div class="stat">
                      <div class="stat-label">缃俊搴?/div>
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

    <!-- 绾胯矾璐熻浇宸ュ叿鎻愮ず -->
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
          <span class="tooltip-label">涓婂骇鐜囷細</span>
          <span class="tooltip-value">{{ lineTooltip.line.occupancyRate }}%</span>
        </div>
        <div class="tooltip-row">
          <span class="tooltip-label">婊¤浇鐜囷細</span>
          <span class="tooltip-value">{{ lineTooltip.line.loadRate }}%</span>
        </div>
        <div class="tooltip-row">
          <span class="tooltip-label">杩愯惀鏁堢巼锛?/span>
          <span class="tooltip-value">{{ lineTooltip.line.efficiency }}%</span>
        </div>
        <div class="tooltip-row">
          <span class="tooltip-label">瓒嬪娍锛?/span>
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
import { format, startOfWeek, endOfWeek, startOfMonth, endOfMonth, startOfQuarter, endOfQuarter, startOfYear, endOfYear, differenceInCalendarDays } from 'date-fns';
import { zhCN } from 'date-fns/locale';

// 缁勪欢瀵煎叆
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';
import AnimatedNumber from '@/components/ui/AnimatedNumber.vue';
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue';
import FlowTrendChart from '@/components/passenger/FlowTrendChart.vue';
import StationRankingTable from '@/components/passenger/StationRankingTable.vue';

// Store
const passengerStore = usePassengerStore();

// 鐘舵€?const isLoading = ref(false);
const isRefreshing = ref(false);
const selectedRange = ref<'today' | 'week' | 'month' | 'quarter' | 'year' | 'custom'>('week');
const startDate = ref('');
const endDate = ref('');

// 鍥捐〃鐘舵€?const trendFrequency = ref<'hourly' | 'daily' | 'weekly' | 'monthly'>('daily');
const rankingMetric = ref<'total' | 'inbound' | 'outbound'>('total');
const loadMetric = ref<'occupancy' | 'load' | 'efficiency'>('occupancy');
const mapViewMode = ref<'heatmap' | 'flow' | 'markers'>('heatmap');
const timeDistributionType = ref<'hourly' | 'daily' | 'weekly'>('hourly');
const forecastDays = ref<7 | 14 | 30>(7);

// 宸ュ叿鎻愮ず鐘舵€?const lineTooltip = ref({
  visible: false,
  line: null as any,
  x: 0,
  y: 0
});

// 璁＄畻灞炴€?const timeRangeLabel = computed(() => {
  const now = new Date();
  switch (selectedRange.value) {
    case 'today':
      return format(now, 'yyyy骞碝M鏈坉d鏃?, { locale: zhCN });
    case 'week':
      const weekStart = startOfWeek(now, { locale: zhCN });
      const weekEnd = endOfWeek(now, { locale: zhCN });
      return `${format(weekStart, 'MM/dd')} - ${format(weekEnd, 'MM/dd')}`;
    case 'month':
      return format(now, 'yyyy骞碝M鏈?, { locale: zhCN });
    case 'quarter':
      const quarterStart = startOfQuarter(now);
      const quarterEnd = endOfQuarter(now);
      return `${format(quarterStart, 'MM/dd')} - ${format(quarterEnd, 'MM/dd')}`;
    case 'year':
      return format(now, 'yyyy骞?, { locale: zhCN });
    case 'custom':
      if (startDate.value && endDate.value) {
        return `${format(new Date(startDate.value), 'MM/dd')} - ${format(new Date(endDate.value), 'MM/dd')}`;
      }
      return '鑷畾涔夎寖鍥?;
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
      return `${days}澶ー;
    }
  }

  switch (selectedRange.value) {
    case 'today': return '1澶?;
    case 'week': return '7澶?;
    case 'month': return '绾?0澶?;
    case 'quarter': return '绾?0澶?;
    case 'year': return '365澶?;
    case 'custom': return '鑷畾涔?;
    default: return '';
  }
});

// KPI鏁版嵁锛堟ā鎷燂級
const kpiData = computed(() => {
  // 浣跨敤store涓殑鏁版嵁
  const trends = passengerStore.flowTrends;
  const rankings = passengerStore.stationRankings;
  const loads = passengerStore.lineLoads;
  const trendValues = passengerStore.kpiTrends;

  if (!trends || rankings.length === 0 || loads.length === 0) {
    // 濡傛灉娌℃湁鏁版嵁锛岃繑鍥為粯璁ゅ€?    return {
      totalPassengers: 0,
      avgPassengers: 0,
      peakStationName: '鏃犳暟鎹?,
      peakStationValue: 0,
      trends: {
        totalPassengers: trendValues.totalPassengers || 0,
        avgPassengers: trendValues.avgPassengers || 0,
        peakStation: trendValues.peakStation || 0
      }
    };
  }

  // 鎵惧嚭鏈€绻佸繖鐨勭珯鐐?  const peakStation = rankings.length > 0 ? rankings[0] : null;

  // 鎵惧嚭鏈€绻佸繖鐨勭嚎璺?  const peakLine = loads.length > 0 ? loads.reduce((max, line) =>
    line.totalPassengers > max.totalPassengers ? line : max
  ) : null;

  return {
    totalPassengers: trends.total || 0,
    avgPassengers: trends.average || 0,
    peakStationName: peakStation?.stationName || '鏃犳暟鎹?,
    peakStationValue: peakStation?.totalPassengers || 0,
    trends: {
      totalPassengers: trendValues.totalPassengers || 0,
      avgPassengers: trendValues.avgPassengers || 0,
      peakStation: trendValues.peakStation || 0
    }
  };
});

// 瓒嬪娍鏁版嵁
const trendData = computed(() => {
  // 浣跨敤store涓殑鏁版嵁
  const trends = passengerStore.flowTrends;

  if (!trends) {
    // 濡傛灉娌℃湁鏁版嵁锛岃繑鍥為粯璁ゅ€?    return {
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
  total: { key: 'totalPassengers', label: '鎬诲娴侀噺', subtitle: '鎸夋€诲娴侀噺鎺掑簭' },
  inbound: { key: 'passengersIn', label: '鍒拌揪瀹㈡祦', subtitle: '鎸夊埌杈惧娴佹帓搴? },
  outbound: { key: 'passengersOut', label: '鍙戦€佸娴?, subtitle: '鎸夊彂閫佸娴佹帓搴? }
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

// 绔欑偣鎺掑悕鏁版嵁
const stationRankings = computed(() => {
  // 浣跨敤store涓殑鏁版嵁
  const rankings = passengerStore.stationRankings;

  if (rankings.length === 0) {
    // 濡傛灉娌℃湁鏁版嵁锛岃繑鍥炵┖鏁扮粍
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

// 绾胯矾璐熻浇鏁版嵁
const lineLoads = computed(() => {
  const loads = passengerStore.lineLoads;

  if (loads.length === 0) {
    return [];
  }

  return loads.map((line) => {
    const capacity = line.capacity || 1;
    const occupancyRate = Math.min(100, Math.round((line.totalPassengers / capacity) * 100));
    const loadRate = Math.min(100, Math.round(line.loadRate * 100));

    return {
      id: line.lineId,
      name: line.lineName,
      code: line.lineCode || line.lineId.toString(),
      totalPassengers: line.totalPassengers,
      occupancyRate,
      loadRate,
      efficiency: loadRate,
      trend: 0
    };
  });
});

const heatmapBuckets = [
  { label: '00:00', range: '00:00-03:59', start: 0, end: 4 },
  { label: '04:00', range: '04:00-07:59', start: 4, end: 8 },
  { label: '08:00', range: '08:00-11:59', start: 8, end: 12 },
  { label: '12:00', range: '12:00-15:59', start: 12, end: 16 },
  { label: '16:00', range: '16:00-19:59', start: 16, end: 20 },
  { label: '20:00', range: '20:00-23:59', start: 20, end: 24 }
];

const heatmapLabels = computed(() => {
  const raw = passengerStore.heatmapData;
  if (raw.length === 0) {
    return { x: [], y: [] };
  }

  const stationTotals = new Map<string, number>();
  raw.forEach((item) => {
    stationTotals.set(item.y, (stationTotals.get(item.y) || 0) + item.value);
  });

  const stations = Array.from(stationTotals.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name]) => name);

  return {
    x: heatmapBuckets.map((bucket) => bucket.label),
    y: stations
  };
});

// 鐑姏鍥炬暟鎹?const heatmapData = computed(() => {
  const raw = passengerStore.heatmapData;
  const labels = heatmapLabels.value;

  if (raw.length === 0 || labels.x.length === 0 || labels.y.length === 0) {
    return [];
  }

  const valueMap = new Map<string, number>();

  raw.forEach((item) => {
    if (!labels.y.includes(item.y)) {
      return;
    }

    const hour = Number(item.x.split(':')[0]);
    if (Number.isNaN(hour)) {
      return;
    }

    const bucketIndex = Math.floor(hour / 4);
    const key = `${item.y}|${bucketIndex}`;
    valueMap.set(key, (valueMap.get(key) || 0) + item.value);
  });

  return labels.y.map((station) =>
    heatmapBuckets.map((bucket, index) => ({
      value: valueMap.get(`${station}|${index}`) || 0,
      time: bucket.range,
      label: station
    }))
  );
});

const flowLineLayouts = [
  { left: '20%', top: '30%', width: '200px', transform: 'rotate(45deg)' },
  { left: '60%', top: '40%', width: '180px', transform: 'rotate(-30deg)' },
  { left: '30%', top: '60%', width: '220px', transform: 'rotate(15deg)' },
  { left: '55%', top: '25%', width: '160px', transform: 'rotate(60deg)' },
  { left: '35%', top: '45%', width: '140px', transform: 'rotate(-10deg)' }
];

// 娴佸悜鏁版嵁
const flowData = computed(() => {
  const flows = passengerStore.flowLines;
  if (flows.length === 0) {
    return [];
  }

  const sorted = [...flows].sort((a, b) => b.passengerCount - a.passengerCount);

  return sorted.slice(0, flowLineLayouts.length).map((flow, index) => ({
    id: `${flow.fromStationId}-${flow.toStationId}-${index}`,
    label: `${flow.fromStationName || flow.fromStationId}鈫?{flow.toStationName || flow.toStationId}`,
    style: flowLineLayouts[index] || flowLineLayouts[0],
    intensity: flow.intensity
  }));
});

// 鏃堕棿鍒嗗竷鏁版嵁
const timeDistributionData = computed(() => {
  const periods = passengerStore.timePeriods;
  if (periods.length === 0) {
    return [];
  }

  return [...periods].sort((a, b) => a.id - b.id);
});

// 棰勬祴鏁版嵁
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
      day: ['鍛ㄤ竴', '鍛ㄤ簩', '鍛ㄤ笁', '鍛ㄥ洓', '鍛ㄤ簲', '鍛ㄥ叚', '鍛ㄦ棩'][date.getDay()],
      date: format(date, 'MM/dd'),
      forecast,
      actual,
      percentage: maxValue > 0 ? (forecast / maxValue) * 100 : 0,
      actualPercentage: actual && maxValue > 0 ? (actual / maxValue) * 100 : 0,
      confidence: confidencePercent
    };
  });
});

// 宸ュ叿鎻愮ず鏍峰紡
const lineTooltipStyle = computed(() => {
  return {
    left: `${lineTooltip.value.x}px`,
    top: `${lineTooltip.value.y}px`,
    display: lineTooltip.value.visible ? 'block' : 'none'
  };
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

// 鏂规硶
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
  // 瀵煎嚭鍔熻兘瀹炵幇
  console.log('瀵煎嚭鏁版嵁');
  alert('瀵煎嚭鍔熻兘寮€鍙戜腑...');
};

const changeTrendFrequency = (frequency: 'hourly' | 'daily' | 'weekly' | 'monthly') => {
  trendFrequency.value = frequency;
  loadData();
};

const changeRankingMetric = (metric: 'total' | 'inbound' | 'outbound') => {
  rankingMetric.value = metric;
  // 杩欓噷搴旇閲嶆柊鍔犺浇瀵瑰簲鎸囨爣鐨勬暟鎹?};

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
  passengerStore.fetchTimePeriods(type).catch((error) => {
    console.error('鍔犺浇鏃堕棿鍒嗗竷鏁版嵁澶辫触:', error);
  });
};

const changeForecastDays = (days: 7 | 14 | 30) => {
  forecastDays.value = days;
  passengerStore.fetchFlowForecasts(days).catch((error) => {
    console.error('鍔犺浇棰勬祴鏁版嵁澶辫触:', error);
  });
};

const getTimeDistributionClass = (percentage: number) => {
  if (percentage >= 20) return 'high';
  if (percentage >= 10) return 'medium';
  return 'low';
};

// 鍔犺浇鏁版嵁
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
    console.error('鍔犺浇鏁版嵁澶辫触:', error);
  } finally {
    isLoading.value = false;
  }
};

// 鍒濆鍖?onMounted(async () => {
  const synced = await passengerStore.syncDateRangeFromStats();
  if (synced) {
    selectedRange.value = 'custom';
    startDate.value = passengerStore.analysisParams.startDate;
    endDate.value = passengerStore.analysisParams.endDate;
    await loadData();
    return;
  }
  selectTimeRange('week');
});
</script>

<style scoped lang="scss">
.analytics {
  padding: var(--spacing-6);
  background: var(--color-bg-secondary);
  min-height: 100vh;
}

/* 椤甸潰鏍囬鍜屾搷浣?*/
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
      min-height: 44px; // 瑙︽懜鐩爣鏈€灏忛珮搴?
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

/* 鏃堕棿绛涢€?*/
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

/* KPI鎸囨爣鍗＄墖 */
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

/* 涓昏鍒嗘瀽鍖哄煙 */
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

      // 鍦板浘鐩稿叧鏍峰紡
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

        .heatmap-empty {
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
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

/* 绾胯矾璐熻浇宸ュ叿鎻愮ず */
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

/* 鍔ㄧ敾鏁堟灉 */
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

/* 瑙︽懜鍙嶉 */
.touch-target {
  min-height: 44px;
  min-width: 44px;
}

.touch-feedback {
  &:active {
    transform: scale(0.98);
  }
}

/* 鍝嶅簲寮忚璁?*/
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
