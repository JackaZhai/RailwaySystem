
<template>
  <div class="data-management">
    <section class="page-hero">
      <div class="hero-main">
        <div class="hero-title">
          <h1>数据管理</h1>
          <p class="hero-subtitle">统一管理客运记录、站点、列车与线路数据</p>
        </div>
        <div class="hero-controls">
          <div class="control-block">
            <span class="control-label">统计维度</span>
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
          <div class="control-block">
            <span class="control-label">数据时间范围</span>
            <span class="control-value">{{ stats.dateRange || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <div class="hero-stats">
        <div class="metric-card">
          <div class="metric-icon">
            <el-icon><DataBoard /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ stats.totalRecords?.toLocaleString() || '0' }}</div>
            <div class="metric-label">客运记录总数</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ stats.dateRange || 'N/A' }}</div>
            <div class="metric-label">数据时间范围</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">
            <el-icon><Van /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ stats.trains?.toLocaleString() || '0' }}</div>
            <div class="metric-label">列车总数</div>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon">
            <el-icon><SetUp /></el-icon>
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ stats.lines?.toLocaleString() || '0' }}</div>
            <div class="metric-label">线路总数</div>
          </div>
        </div>
      </div>
    </section>

    <section class="data-body">
      <input
        ref="fileInputRef"
        type="file"
        class="hidden-file-input"
        @change="handleFileChange"
      />
      <el-tabs v-model="activeTable" class="data-tabs">
        <el-tab-pane label="客运记录" name="passengerFlows">
          <div class="table-section">
            <el-card class="panel-card">
              <template #header>
                <div class="panel-header">
                  <div>
                    <h3>筛选条件</h3>
                    <p class="panel-subtitle">按时间、线路、列车与站点过滤客运记录</p>
                  </div>
                  <div class="panel-actions">
                    <el-button type="primary" @click="searchPassengerFlows">查询</el-button>
                    <el-button @click="resetPassengerFlowQuery">重置</el-button>
                  </div>
                </div>
              </template>

              <div class="panel-body">
                <el-form :model="passengerFlowQuery" label-width="100px" label-position="top">
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
              </div>
            </el-card>

            <el-card class="panel-card">
              <template #header>
                <div class="panel-header">
                  <div>
                    <h3>客运记录</h3>
                    <p class="panel-subtitle">共 {{ passengerFlowTotal.toLocaleString() }} 条记录</p>
                  </div>
                  <div class="panel-actions">
                    <span v-if="selectedFileName" class="file-hint">{{ selectedFileName }}</span>
                    <el-button @click="fileInputRef?.click()">选择文件</el-button>
                    <el-button :loading="validating" :disabled="!selectedFile" @click="uploadData(true)">
                      仅验证
                    </el-button>
                    <el-button type="primary" :loading="importing" :disabled="!selectedFile" @click="uploadData(false)">
                      导入
                    </el-button>
                    <el-select v-model="exportFormat" size="small" class="format-select">
                      <el-option label="CSV" value="csv" />
                      <el-option label="Excel" value="excel" />
                      <el-option label="JSON" value="json" />
                    </el-select>
                    <el-button type="primary" :loading="exporting" @click="exportData">
                      导出
                    </el-button>
                    <el-button type="primary" @click="refreshPassengerFlows">刷新</el-button>
                  </div>
                </div>
              </template>

              <div class="panel-body table-body">
                <el-table
                  v-loading="passengerFlowLoading"
                  :data="passengerFlowData"
                  style="width: 100%"
                >
                  <el-table-column prop="id" label="ID" width="80" sortable />
                  <el-table-column prop="operation_date" label="运营日期" width="120" sortable />
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
                  <el-table-column label="客流量" width="140">
                    <template #default="{ row }">
                      <div>上客: {{ row.passengers_in }}</div>
                      <div>下客: {{ row.passengers_out }}</div>
                      <div class="total-passengers">总计: {{ row.total_passengers || row.passengers_in + row.passengers_out }}</div>
                    </template>
                  </el-table-column>
                  <el-table-column label="票价 / 收入" width="140">
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
              </div>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="站点" name="stations">
          <div class="table-section">
            <el-card class="panel-card">
              <template #header>
                <div class="panel-header">
                  <div>
                    <h3>筛选条件</h3>
                    <p class="panel-subtitle">按站点名称、电报码或简称搜索</p>
                  </div>
                  <div class="panel-actions">
                    <el-button type="primary" @click="searchStations">查询</el-button>
                    <el-button @click="resetStationQuery">重置</el-button>
                  </div>
                </div>
              </template>

              <div class="panel-body">
                <el-form :model="stationQuery" label-width="100px" label-position="top">
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
              </div>
            </el-card>

            <el-card class="panel-card">
              <template #header>
                <div class="panel-header">
                  <div>
                    <h3>站点列表</h3>
                    <p class="panel-subtitle">共 {{ stationTotal.toLocaleString() }} 个站点</p>
                  </div>
                  <div class="panel-actions">
                    <span v-if="selectedFileName" class="file-hint">{{ selectedFileName }}</span>
                    <el-button @click="fileInputRef?.click()">选择文件</el-button>
                    <el-button :loading="validating" :disabled="!selectedFile" @click="uploadData(true)">
                      仅验证
                    </el-button>
                    <el-button type="primary" :loading="importing" :disabled="!selectedFile" @click="uploadData(false)">
                      导入
                    </el-button>
                    <el-select v-model="exportFormat" size="small" class="format-select">
                      <el-option label="CSV" value="csv" />
                      <el-option label="Excel" value="excel" />
                      <el-option label="JSON" value="json" />
                    </el-select>
                    <el-button type="primary" :loading="exporting" @click="exportData">
                      导出
                    </el-button>
                    <el-button type="primary" @click="refreshStations">刷新</el-button>
                  </div>
                </div>
              </template>

              <div class="panel-body table-body">
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
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <el-tab-pane label="列车" name="trains">
          <div class="table-section">
            <el-card class="panel-card">
              <template #header>
                <div class="panel-header">
                  <div>
                    <h3>筛选条件</h3>
                    <p class="panel-subtitle">按列车代码搜索</p>
                  </div>
                  <div class="panel-actions">
                    <el-button type="primary" @click="searchTrains">查询</el-button>
                    <el-button @click="resetTrainQuery">重置</el-button>
                  </div>
                </div>
              </template>

              <div class="panel-body">
                <el-form :model="trainQuery" label-width="100px" label-position="top">
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
              </div>
            </el-card>

            <el-card class="panel-card">
              <template #header>
                <div class="panel-header">
                  <div>
                    <h3>列车列表</h3>
                    <p class="panel-subtitle">共 {{ trainTotal.toLocaleString() }} 列列车</p>
                  </div>
                  <div class="panel-actions">
                    <span v-if="selectedFileName" class="file-hint">{{ selectedFileName }}</span>
                    <el-button @click="fileInputRef?.click()">选择文件</el-button>
                    <el-button :loading="validating" :disabled="!selectedFile" @click="uploadData(true)">
                      仅验证
                    </el-button>
                    <el-button type="primary" :loading="importing" :disabled="!selectedFile" @click="uploadData(false)">
                      导入
                    </el-button>
                    <el-select v-model="exportFormat" size="small" class="format-select">
                      <el-option label="CSV" value="csv" />
                      <el-option label="Excel" value="excel" />
                      <el-option label="JSON" value="json" />
                    </el-select>
                    <el-button type="primary" :loading="exporting" @click="exportData">
                      导出
                    </el-button>
                    <el-button type="primary" @click="refreshTrains">刷新</el-button>
                  </div>
                </div>
              </template>

              <div class="panel-body table-body">
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
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <el-tab-pane label="线路" name="routes">
          <div class="table-section">
            <el-card class="panel-card">
              <template #header>
                <div class="panel-header">
                  <div>
                    <h3>筛选条件</h3>
                    <p class="panel-subtitle">按线路名称搜索</p>
                  </div>
                  <div class="panel-actions">
                    <el-button type="primary" @click="searchRoutes">查询</el-button>
                    <el-button @click="resetRouteQuery">重置</el-button>
                  </div>
                </div>
              </template>

              <div class="panel-body">
                <el-form :model="routeQuery" label-width="100px" label-position="top">
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
              </div>
            </el-card>

            <el-card class="panel-card">
              <template #header>
                <div class="panel-header">
                  <div>
                    <h3>线路列表</h3>
                    <p class="panel-subtitle">共 {{ routeTotal.toLocaleString() }} 条线路</p>
                  </div>
                  <div class="panel-actions">
                    <span v-if="selectedFileName" class="file-hint">{{ selectedFileName }}</span>
                    <el-button @click="fileInputRef?.click()">选择文件</el-button>
                    <el-button :loading="validating" :disabled="!selectedFile" @click="uploadData(true)">
                      仅验证
                    </el-button>
                    <el-button type="primary" :loading="importing" :disabled="!selectedFile" @click="uploadData(false)">
                      导入
                    </el-button>
                    <el-select v-model="exportFormat" size="small" class="format-select">
                      <el-option label="CSV" value="csv" />
                      <el-option label="Excel" value="excel" />
                      <el-option label="JSON" value="json" />
                    </el-select>
                    <el-button type="primary" :loading="exporting" @click="exportData">
                      导出
                    </el-button>
                    <el-button type="primary" @click="refreshRoutes">刷新</el-button>
                  </div>
                </div>
              </template>

              <div class="panel-body table-body">
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
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </section>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataBoard,
  Van,
  SetUp,
  Calendar
} from '@element-plus/icons-vue'

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
  ElIcon,
  ElLoading
} from 'element-plus'

const vLoading = ElLoading.directive

import { dataService } from '@/services/api'
import type { Station, Train as TrainType, Route, PassengerFlow } from '@/types/data'

const activeTable = ref('passengerFlows')
const activeStat = ref('passengerFlows')

const stats = reactive({
  totalRecords: 0,
  stations: 0,
  trains: 0,
  lines: 0,
  dateRange: '',
  avgPassengersPerDay: 0,
  totalRevenue: 0,
  topStationPassengers: 0,
  stationsByProvince: '',
  avgStationPassengers: 0,
  avgTrainCapacity: 0,
  trainTypes: '',
  busiestTrainPassengers: 0,
  avgRouteLength: 0,
  routeRegions: '',
  busiestRoutePassengers: 0
})

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

const stationLoading = ref(false)
const stationData = ref<Station[]>([])
const stationTotal = ref(0)
const stationQuery = reactive({
  page: 1,
  page_size: 20,
  search: ''
})

const trainLoading = ref(false)
const trainData = ref<TrainType[]>([])
const trainTotal = ref(0)
const trainQuery = reactive({
  page: 1,
  page_size: 20,
  search: ''
})

const routeLoading = ref(false)
const routeData = ref<Route[]>([])
const routeTotal = ref(0)
const routeQuery = reactive({
  page: 1,
  page_size: 20,
  search: ''
})

const stations = ref<Station[]>([])
const trains = ref<TrainType[]>([])
const routes = ref<Route[]>([])
const selectedFile = ref<File | null>(null)
const selectedFileName = ref('')
const importing = ref(false)
const validating = ref(false)
const exporting = ref(false)
const exportFormat = ref<'csv' | 'excel' | 'json'>('csv')
const fileInputRef = ref<HTMLInputElement | null>(null)

onMounted(() => {
  loadStats()
  loadPassengerFlows()
  loadStations()
  loadTrains()
  loadRoutes()
  loadDropdownOptions()
})

const loadStats = async () => {
  try {
    const statsData = await dataService.getDataStats()

    stats.totalRecords = statsData.totalRecords || 0
    stats.stations = statsData.stations || 0
    stats.trains = statsData.trains || 0
    stats.lines = statsData.lines || 0

    if (statsData.dateRange) {
      if (typeof statsData.dateRange === 'string') {
        stats.dateRange = statsData.dateRange
      } else if (statsData.dateRange.minDate && statsData.dateRange.maxDate) {
        stats.dateRange = `${statsData.dateRange.minDate} 至 ${statsData.dateRange.maxDate}`
      }
    }

    stats.avgPassengersPerDay = 0
    stats.totalRevenue = 0

    stats.topStationPassengers = 0
    stats.stationsByProvince = '暂无数据'
    stats.avgStationPassengers = 0

    stats.avgTrainCapacity = 0
    stats.trainTypes = '暂无数据'
    stats.busiestTrainPassengers = 0

    stats.avgRouteLength = 0
    stats.routeRegions = '暂无数据'
    stats.busiestRoutePassengers = 0
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载统计数据失败')
  }
}

const fetchAllPages = async <T,>(
  fetcher: any
) => {
  const pageSize = 200
  let page = 1
  const all: T[] = []
  let total = 0
  while (true) {
    const res = await fetcher({ page, page_size: pageSize })
    const batch = res.results || []
    if (typeof res.count === 'number') {
      total = res.count
    }
    all.push(...batch)
    if (batch.length === 0) {
      break
    }
    if (total && all.length >= total) {
      break
    }
    page += 1
  }
  return all
}

const loadDropdownOptions = async () => {
  try {
    const [allStations, allTrains, allRoutes] = await Promise.all([
      fetchAllPages((params) => dataService.getStations(params)),
      fetchAllPages((params) => dataService.getTrains(params)),
      fetchAllPages((params) => dataService.getRoutes(params))
    ])

    stations.value = allStations
    trains.value = allTrains
    routes.value = allRoutes
  } catch (error) {
    console.error('加载下拉选项失败:', error)
  }
}

const loadPassengerFlows = async () => {
  passengerFlowLoading.value = true
  try {
    const params: any = {
      page: passengerFlowQuery.page,
      page_size: passengerFlowQuery.page_size,
      search: passengerFlowQuery.search
    }

    if (passengerFlowQuery.dateRange && passengerFlowQuery.dateRange.length === 2) {
      params.start_date = passengerFlowQuery.dateRange[0]
      params.end_date = passengerFlowQuery.dateRange[1]
    }

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

const handleStatChange = (value: string) => {
  activeStat.value = value
  console.log('切换到统计类型:', value)
}

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] || null
  selectedFile.value = file
  selectedFileName.value = file?.name || ''
}

const resetFileInput = () => {
  selectedFile.value = null
  selectedFileName.value = ''
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const uploadData = async (validateOnly: boolean) => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的文件')
    return
  }
  if (validateOnly) {
    validating.value = true
  } else {
    importing.value = true
  }
  try {
    const response = await dataService.uploadData(selectedFile.value, { validateOnly })
    if (validateOnly) {
      ElMessage.success(response.message || '验证完成')
    } else {
      ElMessage.success(response.message || '导入成功')
      loadStats()
      if (activeTable.value === 'passengerFlows') loadPassengerFlows()
      if (activeTable.value === 'stations') loadStations()
      if (activeTable.value === 'trains') loadTrains()
      if (activeTable.value === 'routes') loadRoutes()
    }
    resetFileInput()
  } catch (error) {
    console.error('数据导入失败:', error)
    ElMessage.error('数据导入失败')
  } finally {
    validating.value = false
    importing.value = false
  }
}

const exportData = async () => {
  exporting.value = true
  try {
    const params: any = { search: '' }
    if (activeTable.value === 'passengerFlows') {
      params.search = passengerFlowQuery.search
      if (passengerFlowQuery.dateRange.length === 2) {
        params.startDate = passengerFlowQuery.dateRange[0]
        params.endDate = passengerFlowQuery.dateRange[1]
      }
      if (passengerFlowQuery.route) params.lineId = passengerFlowQuery.route
      if (passengerFlowQuery.station) params.stationId = passengerFlowQuery.station
    } else if (activeTable.value === 'stations') {
      params.search = stationQuery.search
    } else if (activeTable.value === 'trains') {
      params.search = trainQuery.search
    } else if (activeTable.value === 'routes') {
      params.search = routeQuery.search
    }

    const blob = await dataService.exportDataRecords(params, exportFormat.value)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const suffix = exportFormat.value === 'excel' ? 'xlsx' : exportFormat.value
    link.href = url
    link.download = `data_export_${activeTable.value}_${new Date().toISOString().slice(0, 10)}.${suffix}`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出完成')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

const formatDateTime = (dateString: string) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN')
  } catch {
    return dateString
  }
}

</script>
<style scoped>
.data-management {
  padding: var(--spacing-6);
  background: var(--color-bg-secondary);
  min-height: 100vh;
}

.page-hero {
  background: linear-gradient(135deg, rgba(79, 114, 237, 0.08), rgba(45, 200, 180, 0.08));
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-6);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
  margin-bottom: var(--spacing-6);
}

.hero-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-6);
  flex-wrap: wrap;
}

.hero-title h1 {
  margin: 0;
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.hero-subtitle {
  margin-top: var(--spacing-2);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

.hero-controls {
  display: flex;
  gap: var(--spacing-4);
  align-items: flex-end;
  flex-wrap: wrap;
}

.control-block {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  min-width: 180px;
}

.control-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.control-value {
  padding: var(--spacing-2) var(--spacing-3);
  background: var(--color-bg-card);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-4);
}

.metric-card {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  display: flex;
  gap: var(--spacing-4);
  align-items: center;
  box-shadow: var(--shadow-sm);
}

.metric-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--border-radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(79, 114, 237, 0.12);
  color: var(--color-primary);
  font-size: 22px;
}

.metric-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.metric-label {
  margin-top: 4px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-4);
  flex-wrap: wrap;
}

.panel-header h2,
.panel-header h3 {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.panel-subtitle {
  margin-top: 4px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.hidden-file-input {
  display: none;
}

.file-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.format-select {
  min-width: 120px;
}

.data-body {
  margin-bottom: var(--spacing-6);
}

.data-tabs :deep(.el-tabs__header) {
  margin-bottom: var(--spacing-4);
}

.data-tabs :deep(.el-tabs__item) {
  font-weight: var(--font-weight-medium);
}

.table-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-5);
}

.panel-card :deep(.el-card__body) {
  padding: 0;
}

.panel-actions {
  display: flex;
  gap: var(--spacing-2);
}

.panel-body {
  padding: var(--spacing-5);
}

.table-body {
  padding-top: 0;
}

.panel-body :deep(.el-form-item) {
  margin-bottom: var(--spacing-4);
}

.pagination-container {
  margin-top: var(--spacing-4);
  display: flex;
  justify-content: flex-end;
}

.telecode {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.total-passengers {
  font-weight: 600;
  color: var(--color-primary);
}
@media (max-width: 1200px) {
  .hero-controls {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .page-hero {
    padding: var(--spacing-4);
  }

  .panel-actions {
    flex-direction: column;
    width: 100%;
  }

  .panel-actions .el-button {
    width: 100%;
  }
}
</style>
