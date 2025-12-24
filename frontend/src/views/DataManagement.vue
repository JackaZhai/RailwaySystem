<template>
  <div class="data-management">
    <!-- 页面标题和统计切换 -->
    <div class="page-header">
      <div class="header-main">
        <h1>数据管理</h1>
        <div class="stats-switcher">
          <el-select
            v-model="activeStat"
            placeholder="选择统计类型"
            size="large"
            @change="handleStatChange"
          >
            <el-option label="客运记录统计" value="passengerFlows" />
            <el-option label="站点统计" value="stations" />
            <el-option label="列车统计" value="trains" />
            <el-option label="线路统计" value="routes" />
          </el-select>
        </div>
      </div>

      <!-- 动态统计卡片 -->
      <div class="stats-summary">
        <template v-if="activeStat === 'passengerFlows'">
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><DataBoard /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ stats.totalRecords?.toLocaleString() || '0' }}</div>
                <div class="summary-label">客运记录总数</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><Calendar /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ stats.dateRange || 'N/A' }}</div>
                <div class="summary-label">数据时间范围</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ formatNumber(stats.avgPassengersPerDay) }}</div>
                <div class="summary-label">日均客流量</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><Money /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ formatCurrency(stats.totalRevenue) }}</div>
                <div class="summary-label">总收入</div>
              </div>
            </div>
          </el-card>
        </template>

        <template v-else-if="activeStat === 'stations'">
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><Location /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ stats.stations?.toLocaleString() || '0' }}</div>
                <div class="summary-label">站点总数</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ formatNumber(stats.topStationPassengers) }}</div>
                <div class="summary-label">最繁忙站点客流量</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><MapLocation /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ stats.stationsByProvince || 'N/A' }}</div>
                <div class="summary-label">省份分布</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><Histogram /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ formatNumber(stats.avgStationPassengers) }}</div>
                <div class="summary-label">站点平均客流量</div>
              </div>
            </div>
          </el-card>
        </template>

        <template v-else-if="activeStat === 'trains'">
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><Train /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ stats.trains?.toLocaleString() || '0' }}</div>
                <div class="summary-label">列车总数</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><Ship /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ formatNumber(stats.avgTrainCapacity) }}</div>
                <div class="summary-label">平均运量</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ stats.trainTypes || 'N/A' }}</div>
                <div class="summary-label">列车类型分布</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ formatNumber(stats.busiestTrainPassengers) }}</div>
                <div class="summary-label">最繁忙列车客流量</div>
              </div>
            </div>
          </el-card>
        </template>

        <template v-else-if="activeStat === 'routes'">
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><SetUp /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ stats.lines?.toLocaleString() || '0' }}</div>
                <div class="summary-label">线路总数</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><Connection /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ formatNumber(stats.avgRouteLength) }}</div>
                <div class="summary-label">平均线路长度(km)</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><PieChart /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ stats.routeRegions || 'N/A' }}</div>
                <div class="summary-label">区域分布</div>
              </div>
            </div>
          </el-card>
          <el-card class="summary-card">
            <div class="summary-content">
              <div class="summary-icon">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="summary-info">
                <div class="summary-value">{{ formatNumber(stats.busiestRoutePassengers) }}</div>
                <div class="summary-label">最繁忙线路客流量</div>
              </div>
            </div>
          </el-card>
        </template>
      </div>
    </div>

    <!-- 数据表标签页 -->
    <el-tabs v-model="activeTable" class="data-tabs">
      <!-- 客运记录标签页 -->
      <el-tab-pane label="客运记录" name="passengerFlows">
        <div class="table-section">
          <!-- 查询条件 -->
          <el-card class="query-card">
            <template #header>
              <div class="card-header">
                <span>查询条件</span>
                <div class="query-actions">
                  <el-button type="primary" @click="searchPassengerFlows">查询</el-button>
                  <el-button @click="resetPassengerFlowQuery">重置</el-button>
                </div>
              </div>
            </template>

            <el-form :model="passengerFlowQuery" label-width="100px">
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="日期范围">
                    <el-date-picker
                      v-model="passengerFlowQuery.dateRange"
                      type="daterange"
                      range-separator="至"
                      start-placeholder="开始日期"
                      end-placeholder="结束日期"
                      value-format="YYYY-MM-DD"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="线路">
                    <el-select
                      v-model="passengerFlowQuery.route"
                      placeholder="选择线路"
                      filterable
                      clearable
                    >
                      <el-option
                        v-for="route in routes"
                        :key="route.id"
                        :label="route.name || `线路 ${route.code}`"
                        :value="route.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="列车">
                    <el-select
                      v-model="passengerFlowQuery.train"
                      placeholder="选择列车"
                      filterable
                      clearable
                    >
                      <el-option
                        v-for="train in trains"
                        :key="train.id"
                        :label="train.code"
                        :value="train.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="站点">
                    <el-select
                      v-model="passengerFlowQuery.station"
                      placeholder="选择站点"
                      filterable
                      clearable
                    >
                      <el-option
                        v-for="station in stations"
                        :key="station.id"
                        :label="station.name"
                        :value="station.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="关键词">
                    <el-input
                      v-model="passengerFlowQuery.search"
                      placeholder="输入关键词搜索"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <!-- 数据表格 -->
          <el-card class="data-table-card">
            <template #header>
              <div class="card-header">
                <span>客运记录</span>
                <div class="table-actions">
                  <el-button type="primary" @click="refreshPassengerFlows">刷新</el-button>
                </div>
              </div>
            </template>

            <el-table
              v-loading="passengerFlowLoading"
              :data="passengerFlowData"
              style="width: 100%"
            >
              <el-table-column prop="id" label="ID" width="80" sortable />
              <el-table-column prop="operation_date" label="运行日期" width="120" sortable />
              <el-table-column label="时间" width="120">
                <template #default="{ row }">
                  <div v-if="row.arrival_time || row.departure_time">
                    {{ row.arrival_time || '' }}<br v-if="row.arrival_time && row.departure_time" />
                    {{ row.departure_time || '' }}
                  </div>
                  <span v-else>N/A</span>
                </template>
              </el-table-column>
              <el-table-column label="线路" width="150">
                <template #default="{ row }">
                  {{ row.route_code ? `线路 ${row.route_code}` : `线路ID: ${row.route}` }}
                </template>
              </el-table-column>
              <el-table-column label="列车" width="120">
                <template #default="{ row }">
                  {{ row.train_code || `列车ID: ${row.train}` }}
                </template>
              </el-table-column>
              <el-table-column label="站点" width="150">
                <template #default="{ row }">
                  {{ row.station_name || `站点ID: ${row.station}` }}
                  <div v-if="row.station_telecode" class="telecode">({{ row.station_telecode }})</div>
                </template>
              </el-table-column>
              <el-table-column label="客流量" width="120">
                <template #default="{ row }">
                  <div>上客: {{ row.passengers_in }}</div>
                  <div>下客: {{ row.passengers_out }}</div>
                  <div class="total-passengers">总计: {{ row.total_passengers || row.passengers_in + row.passengers_out }}</div>
                </template>
              </el-table-column>
              <el-table-column label="票价/收入" width="120">
                <template #default="{ row }">
                  <div v-if="row.ticket_price">票价: ¥{{ row.ticket_price }}</div>
                  <div v-if="row.revenue">收入: ¥{{ row.revenue }}</div>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间" width="180" sortable>
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="passengerFlowQuery.page"
                v-model:page-size="passengerFlowQuery.page_size"
                :page-sizes="[10, 20, 50, 100]"
                :total="passengerFlowTotal"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handlePassengerFlowSizeChange"
                @current-change="handlePassengerFlowPageChange"
              />
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 站点标签页 -->
      <el-tab-pane label="站点" name="stations">
        <div class="table-section">
          <!-- 查询条件 -->
          <el-card class="query-card">
            <template #header>
              <div class="card-header">
                <span>查询条件</span>
                <div class="query-actions">
                  <el-button type="primary" @click="searchStations">查询</el-button>
                  <el-button @click="resetStationQuery">重置</el-button>
                </div>
              </div>
            </template>

            <el-form :model="stationQuery" label-width="100px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="关键词">
                    <el-input
                      v-model="stationQuery.search"
                      placeholder="输入站点名称、电报码或简称搜索"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <!-- 数据表格 -->
          <el-card class="data-table-card">
            <template #header>
              <div class="card-header">
                <span>站点列表</span>
                <div class="table-actions">
                  <el-button type="primary" @click="refreshStations">刷新</el-button>
                </div>
              </div>
            </template>

            <el-table
              v-loading="stationLoading"
              :data="stationData"
              style="width: 100%"
            >
              <el-table-column prop="id" label="ID" width="80" sortable />
              <el-table-column prop="name" label="站点名称" width="150" sortable />
              <el-table-column prop="telecode" label="电报码" width="100" sortable />
              <el-table-column prop="shortname" label="简称" width="100" />
              <el-table-column prop="code" label="站点代码" width="100" />
              <el-table-column prop="travel_area_id" label="旅行区ID" width="100" />
              <el-table-column prop="created_at" label="创建时间" width="180" sortable>
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="更新时间" width="180" sortable>
                <template #default="{ row }">
                  {{ formatDateTime(row.updated_at) }}
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="stationQuery.page"
                v-model:page-size="stationQuery.page_size"
                :page-sizes="[10, 20, 50, 100]"
                :total="stationTotal"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleStationSizeChange"
                @current-change="handleStationPageChange"
              />
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 列车标签页 -->
      <el-tab-pane label="列车" name="trains">
        <div class="table-section">
          <!-- 查询条件 -->
          <el-card class="query-card">
            <template #header>
              <div class="card-header">
                <span>查询条件</span>
                <div class="query-actions">
                  <el-button type="primary" @click="searchTrains">查询</el-button>
                  <el-button @click="resetTrainQuery">重置</el-button>
                </div>
              </div>
            </template>

            <el-form :model="trainQuery" label-width="100px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="关键词">
                    <el-input
                      v-model="trainQuery.search"
                      placeholder="输入列车代码搜索"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <!-- 数据表格 -->
          <el-card class="data-table-card">
            <template #header>
              <div class="card-header">
                <span>列车列表</span>
                <div class="table-actions">
                  <el-button type="primary" @click="refreshTrains">刷新</el-button>
                </div>
              </div>
            </template>

            <el-table
              v-loading="trainLoading"
              :data="trainData"
              style="width: 100%"
            >
              <el-table-column prop="id" label="ID" width="80" sortable />
              <el-table-column prop="code" label="列车代码" width="120" sortable />
              <el-table-column prop="capacity" label="运量" width="100" sortable />
              <el-table-column prop="created_at" label="创建时间" width="180" sortable>
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="更新时间" width="180" sortable>
                <template #default="{ row }">
                  {{ formatDateTime(row.updated_at) }}
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="trainQuery.page"
                v-model:page-size="trainQuery.page_size"
                :page-sizes="[10, 20, 50, 100]"
                :total="trainTotal"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleTrainSizeChange"
                @current-change="handleTrainPageChange"
              />
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 线路标签页 -->
      <el-tab-pane label="线路" name="routes">
        <div class="table-section">
          <!-- 查询条件 -->
          <el-card class="query-card">
            <template #header>
              <div class="card-header">
                <span>查询条件</span>
                <div class="query-actions">
                  <el-button type="primary" @click="searchRoutes">查询</el-button>
                  <el-button @click="resetRouteQuery">重置</el-button>
                </div>
              </div>
            </template>

            <el-form :model="routeQuery" label-width="100px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="关键词">
                    <el-input
                      v-model="routeQuery.search"
                      placeholder="输入线路名称搜索"
                      clearable
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <!-- 数据表格 -->
          <el-card class="data-table-card">
            <template #header>
              <div class="card-header">
                <span>线路列表</span>
                <div class="table-actions">
                  <el-button type="primary" @click="refreshRoutes">刷新</el-button>
                </div>
              </div>
            </template>

            <el-table
              v-loading="routeLoading"
              :data="routeData"
              style="width: 100%"
            >
              <el-table-column prop="id" label="ID" width="80" sortable />
              <el-table-column prop="code" label="线路代码" width="120" sortable />
              <el-table-column prop="name" label="线路名称" width="200" />
              <el-table-column prop="created_at" label="创建时间" width="180" sortable>
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column prop="updated_at" label="更新时间" width="180" sortable>
                <template #default="{ row }">
                  {{ formatDateTime(row.updated_at) }}
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="routeQuery.page"
                v-model:page-size="routeQuery.page_size"
                :page-sizes="[10, 20, 50, 100]"
                :total="routeTotal"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleRouteSizeChange"
                @current-change="handleRoutePageChange"
              />
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataBoard,
  Location,
  Train,
  SetUp,
  Calendar,
  TrendCharts,
  Money,
  OfficeBuilding,
  MapLocation,
  Histogram,
  Ship,
  DataLine,
  Connection,
  PieChart
} from '@element-plus/icons-vue'

// 手动导入Element Plus组件
import {
  ElCard,
  ElTabs,
  ElTabPane,
  ElForm,
  ElFormItem,
  ElTable,
  ElTableColumn,
  ElDatePicker,
  ElSelect,
  ElOption,
  ElInput,
  ElButton,
  ElPagination,
  ElIcon
} from 'element-plus'

import { dataService } from '@/services/api'
import type { Station, Train as TrainType, Route, PassengerFlow } from '@/types/data'

// 响应式数据
const activeTable = ref('passengerFlows')
const activeStat = ref('passengerFlows')

// 统计数据
const stats = reactive({
  // 基础统计
  totalRecords: 0,
  stations: 0,
  trains: 0,
  lines: 0,
  dateRange: '',

  // 客运记录相关统计
  avgPassengersPerDay: 0,
  totalRevenue: 0,

  // 站点相关统计
  topStationPassengers: 0,
  stationsByProvince: '',
  avgStationPassengers: 0,

  // 列车相关统计
  avgTrainCapacity: 0,
  trainTypes: '',
  busiestTrainPassengers: 0,

  // 线路相关统计
  avgRouteLength: 0,
  routeRegions: '',
  busiestRoutePassengers: 0
})

// 客运记录相关
const passengerFlowLoading = ref(false)
const passengerFlowData = ref<PassengerFlow[]>([])
const passengerFlowTotal = ref(0)
const passengerFlowQuery = reactive({
  page: 1,
  page_size: 20,
  dateRange: [] as string[],
  route: null as number | null,
  train: null as number | null,
  station: null as number | null,
  search: ''
})

// 站点相关
const stationLoading = ref(false)
const stationData = ref<Station[]>([])
const stationTotal = ref(0)
const stationQuery = reactive({
  page: 1,
  page_size: 20,
  search: ''
})

// 列车相关
const trainLoading = ref(false)
const trainData = ref<TrainType[]>([])
const trainTotal = ref(0)
const trainQuery = reactive({
  page: 1,
  page_size: 20,
  search: ''
})

// 线路相关
const routeLoading = ref(false)
const routeData = ref<Route[]>([])
const routeTotal = ref(0)
const routeQuery = reactive({
  page: 1,
  page_size: 20,
  search: ''
})

// 下拉选项数据
const stations = ref<Station[]>([])
const trains = ref<TrainType[]>([])
const routes = ref<Route[]>([])

// 生命周期
onMounted(() => {
  loadStats()
  loadPassengerFlows()
  loadStations()
  loadTrains()
  loadRoutes()
  loadDropdownOptions()
})

// 加载统计数据
const loadStats = async () => {
  try {
    const statsData = await dataService.getDataStats()

    // 基础统计
    stats.totalRecords = statsData.totalRecords || 0
    stats.stations = statsData.stations || 0
    stats.trains = statsData.trains || 0
    stats.lines = statsData.lines || 0

    // 处理日期范围
    if (statsData.dateRange) {
      if (typeof statsData.dateRange === 'string') {
        stats.dateRange = statsData.dateRange
      } else if (statsData.dateRange.minDate && statsData.dateRange.maxDate) {
        stats.dateRange = `${statsData.dateRange.minDate} 至 ${statsData.dateRange.maxDate}`
      }
    }

    // 模拟其他统计数据的计算（实际项目中应该从后端获取）
    // 客运记录统计
    stats.avgPassengersPerDay = Math.round(stats.totalRecords / 365) // 假设一年数据
    stats.totalRevenue = stats.totalRecords * 100 // 模拟收入计算

    // 站点统计
    stats.topStationPassengers = Math.round(stats.totalRecords * 0.1) // 最繁忙站点占10%
    stats.stationsByProvince = '四川、重庆、贵州等' // 模拟省份分布
    stats.avgStationPassengers = Math.round(stats.totalRecords / stats.stations)

    // 列车统计
    stats.avgTrainCapacity = 2000 // 模拟平均运量
    stats.trainTypes = '高铁(G)、动车(D)、城际(C)' // 模拟类型分布
    stats.busiestTrainPassengers = Math.round(stats.totalRecords * 0.05) // 最繁忙列车占5%

    // 线路统计
    stats.avgRouteLength = 300 // 模拟平均线路长度(km)
    stats.routeRegions = '成渝、渝贵、西成等' // 模拟区域分布
    stats.busiestRoutePassengers = Math.round(stats.totalRecords * 0.15) // 最繁忙线路占15%

  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  }
}

// 加载下拉选项
const loadDropdownOptions = async () => {
  try {
    // 加载前100条记录用于下拉选项
    const [stationsRes, trainsRes, routesRes] = await Promise.all([
      dataService.getStations({ page_size: 100 }),
      dataService.getTrains({ page_size: 100 }),
      dataService.getRoutes({ page_size: 100 })
    ])

    stations.value = stationsRes.results || []
    trains.value = trainsRes.results || []
    routes.value = routesRes.results || []
  } catch (error) {
    console.error('加载下拉选项失败:', error)
  }
}

// ========== 客运记录相关方法 ==========
const loadPassengerFlows = async () => {
  passengerFlowLoading.value = true
  try {
    const params: any = {
      page: passengerFlowQuery.page,
      page_size: passengerFlowQuery.page_size,
      search: passengerFlowQuery.search
    }

    // 处理日期范围
    if (passengerFlowQuery.dateRange && passengerFlowQuery.dateRange.length === 2) {
      params.start_date = passengerFlowQuery.dateRange[0]
      params.end_date = passengerFlowQuery.dateRange[1]
    }

    // 处理其他过滤条件
    if (passengerFlowQuery.route) params.route = passengerFlowQuery.route
    if (passengerFlowQuery.train) params.train = passengerFlowQuery.train
    if (passengerFlowQuery.station) params.station = passengerFlowQuery.station

    const response = await dataService.getPassengerFlows(params)
    passengerFlowData.value = response.results || []
    passengerFlowTotal.value = response.count || 0
  } catch (error) {
    console.error('加载客运记录失败:', error)
    ElMessage.error('加载客运记录失败')
  } finally {
    passengerFlowLoading.value = false
  }
}

const searchPassengerFlows = () => {
  passengerFlowQuery.page = 1
  loadPassengerFlows()
}

const resetPassengerFlowQuery = () => {
  passengerFlowQuery.page = 1
  passengerFlowQuery.dateRange = []
  passengerFlowQuery.route = null
  passengerFlowQuery.train = null
  passengerFlowQuery.station = null
  passengerFlowQuery.search = ''
  loadPassengerFlows()
}

const refreshPassengerFlows = () => {
  loadPassengerFlows()
}

const handlePassengerFlowSizeChange = (size: number) => {
  passengerFlowQuery.page_size = size
  passengerFlowQuery.page = 1
  loadPassengerFlows()
}

const handlePassengerFlowPageChange = (page: number) => {
  passengerFlowQuery.page = page
  loadPassengerFlows()
}

// ========== 站点相关方法 ==========
const loadStations = async () => {
  stationLoading.value = true
  try {
    const response = await dataService.getStations({
      page: stationQuery.page,
      page_size: stationQuery.page_size,
      search: stationQuery.search
    })
    stationData.value = response.results || []
    stationTotal.value = response.count || 0
  } catch (error) {
    console.error('加载站点失败:', error)
    ElMessage.error('加载站点失败')
  } finally {
    stationLoading.value = false
  }
}

const searchStations = () => {
  stationQuery.page = 1
  loadStations()
}

const resetStationQuery = () => {
  stationQuery.page = 1
  stationQuery.search = ''
  loadStations()
}

const refreshStations = () => {
  loadStations()
}

const handleStationSizeChange = (size: number) => {
  stationQuery.page_size = size
  stationQuery.page = 1
  loadStations()
}

const handleStationPageChange = (page: number) => {
  stationQuery.page = page
  loadStations()
}

// ========== 列车相关方法 ==========
const loadTrains = async () => {
  trainLoading.value = true
  try {
    const response = await dataService.getTrains({
      page: trainQuery.page,
      page_size: trainQuery.page_size,
      search: trainQuery.search
    })
    trainData.value = response.results || []
    trainTotal.value = response.count || 0
  } catch (error) {
    console.error('加载列车失败:', error)
    ElMessage.error('加载列车失败')
  } finally {
    trainLoading.value = false
  }
}

const searchTrains = () => {
  trainQuery.page = 1
  loadTrains()
}

const resetTrainQuery = () => {
  trainQuery.page = 1
  trainQuery.search = ''
  loadTrains()
}

const refreshTrains = () => {
  loadTrains()
}

const handleTrainSizeChange = (size: number) => {
  trainQuery.page_size = size
  trainQuery.page = 1
  loadTrains()
}

const handleTrainPageChange = (page: number) => {
  trainQuery.page = page
  loadTrains()
}

// ========== 线路相关方法 ==========
const loadRoutes = async () => {
  routeLoading.value = true
  try {
    const response = await dataService.getRoutes({
      page: routeQuery.page,
      page_size: routeQuery.page_size,
      search: routeQuery.search
    })
    routeData.value = response.results || []
    routeTotal.value = response.count || 0
  } catch (error) {
    console.error('加载线路失败:', error)
    ElMessage.error('加载线路失败')
  } finally {
    routeLoading.value = false
  }
}

const searchRoutes = () => {
  routeQuery.page = 1
  loadRoutes()
}

const resetRouteQuery = () => {
  routeQuery.page = 1
  routeQuery.search = ''
  loadRoutes()
}

const refreshRoutes = () => {
  loadRoutes()
}

const handleRouteSizeChange = (size: number) => {
  routeQuery.page_size = size
  routeQuery.page = 1
  loadRoutes()
}

const handleRoutePageChange = (page: number) => {
  routeQuery.page = page
  loadRoutes()
}

// 统计切换处理
const handleStatChange = (value: string) => {
  activeStat.value = value
  // 可以在这里加载对应类型的详细统计数据
  console.log('切换到统计类型:', value)
}

// 工具函数
const formatDateTime = (dateString: string) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN')
  } catch (error) {
    return dateString
  }
}

const formatNumber = (num: number) => {
  if (!num && num !== 0) return 'N/A'
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString('zh-CN')
}

const formatCurrency = (amount: number) => {
  if (!amount && amount !== 0) return 'N/A'
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(1) + '万'
  }
  return '¥' + amount.toLocaleString('zh-CN')
}
</script>

<style>
.data-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-main h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.stats-switcher {
  width: 200px;
}

.stats-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  :deep(.el-card__body) {
    padding: 16px;
  }
}

.summary-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-icon {
  font-size: 32px;
  color: var(--el-color-primary);
}

.summary-info {
  flex: 1;
}

.summary-value {
  font-size: 24px;
  font-weight: 600;
  line-height: 1.2;
}

.summary-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.data-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 20px;
  }
}

.table-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.query-card,
.data-table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.query-actions,
.table-actions {
  display: flex;
  gap: 8px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.telecode {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.total-passengers {
  font-weight: 600;
  color: var(--el-color-primary);
}

@media (max-width: 1200px) {
  .stats-summary {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-summary {
    grid-template-columns: 1fr;
  }

  .query-actions,
  .table-actions {
    flex-direction: column;
    width: 100%;
  }

  .query-actions .el-button,
  .table-actions .el-button {
    width: 100%;
    margin-bottom: 8px;
  }
}
</style>