<template>
  <div class="station-ranking-table">
    <!-- 表格标题和操作 -->
    <div class="table-header">
      <div class="table-title">
        <h3>{{ title }}</h3>
        <p class="table-subtitle" v-if="subtitle">{{ subtitle }}</p>
      </div>
      <div class="table-actions" v-if="showActions">
        <div class="search-box">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索站点..."
            class="search-input"
          />
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <button class="btn-icon" title="刷新数据" @click="$emit('refresh')">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 4V9H4.58152M19.9381 9C19.446 5.05369 16.0796 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22C17.5228 22 22 17.5228 22 12C22 9.27455 20.9097 6.80375 19.1414 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="btn-icon" title="导出数据" @click="exportData">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15M7 10L12 15M12 15L17 10M12 15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 表格容器 -->
    <div class="table-container">
      <table class="ranking-table">
        <thead>
          <tr>
            <th class="rank-col">排名</th>
            <th class="station-col">站点</th>
            <th class="metric-col" v-for="column in visibleColumns" :key="column.key">
              <div class="column-header">
                <span>{{ column.label }}</span>
                <button
                  v-if="column.sortable"
                  class="sort-btn"
                  @click="toggleSort(column.key)"
                >
                  <svg
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    :class="{ 'active': sortBy === column.key }"
                  >
                    <path d="M7 15L12 20L17 15M7 9L12 4L17 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </th>
            <th class="action-col">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(station, index) in paginatedData" :key="station.stationId">
            <td class="rank-col">
              <div class="rank-badge" :class="getRankClass(station.ranking)">
                {{ station.ranking }}
                <span
                  v-if="station.change"
                  class="rank-change"
                  :class="getChangeClass(station.change)"
                >
                  {{ formatChange(station.change) }}
                </span>
              </div>
            </td>
            <td class="station-col">
              <div class="station-info">
                <div class="station-name">{{ station.stationName }}</div>
                <div class="station-code">{{ station.stationTelecode }}</div>
              </div>
            </td>
            <td class="metric-col" v-for="column in visibleColumns" :key="column.key">
              <div class="metric-value">
                {{ formatMetric(station[column.key], column.key) }}
              </div>
            </td>
            <td class="action-col">
              <div class="action-buttons">
                <button
                  class="btn-action"
                  title="查看详情"
                  @click="$emit('view-details', station)"
                >
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" stroke-width="2"/>
                    <path d="M2.458 12C3.732 7.943 7.523 5 12 5C16.477 5 20.268 7.943 21.542 12C20.268 16.057 16.477 19 12 19C7.523 19 3.732 16.057 2.458 12Z" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </button>
                <button
                  class="btn-action"
                  title="对比分析"
                  @click="$emit('compare', station)"
                >
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 13V12C8 10.8954 8.89543 10 10 10H14C15.1046 10 16 10.8954 16 12V13C16 14.1046 15.1046 15 14 15H10C8.89543 15 8 14.1046 8 13Z" stroke="currentColor" stroke-width="2"/>
                    <path d="M7 8V7C7 5.89543 7.89543 5 9 5H15C16.1046 5 17 5.89543 17 7V8C17 9.10457 16.1046 10 15 10H9C7.89543 10 7 9.10457 7 8Z" stroke="currentColor" stroke-width="2"/>
                    <path d="M11 19H13C14.1046 19 15 18.1046 15 17V16C15 14.8954 14.1046 14 13 14H11C9.89543 14 9 14.8954 9 16V17C9 18.1046 9.89543 19 11 19Z" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredData.length === 0">
            <td :colspan="visibleColumns.length + 3" class="empty-state">
              <div class="empty-content">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9.172 16.172L4.343 21M14.828 16.172L19.657 21M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <p>未找到匹配的站点</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 表格分页 -->
    <div class="table-footer" v-if="showPagination">
      <div class="pagination-info">
        显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ filteredData.length }} 条
      </div>
      <div class="pagination-controls">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          上一页
        </button>
        <div class="page-numbers">
          <button
            v-for="page in visiblePages"
            :key="page"
            class="page-btn"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
          <span v-if="showEllipsis" class="page-ellipsis">...</span>
        </div>
        <button
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          下一页
        </button>
      </div>
      <div class="page-size-selector">
        <label>每页显示:</label>
        <select v-model="pageSize" class="page-size-select">
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import type { StationRanking } from '@/types/passenger';

interface Props {
  // 数据
  data?: StationRanking[];
  // 表格配置
  title?: string;
  subtitle?: string;
  columns?: TableColumn[];
  // 显示选项
  showActions?: boolean;
  showPagination?: boolean;
  pageSize?: number;
  // 排序
  defaultSort?: string;
  defaultSortOrder?: 'asc' | 'desc';
}

interface TableColumn {
  key: keyof StationRanking;
  label: string;
  sortable?: boolean;
  visible?: boolean;
  formatter?: (value: any) => string;
}

interface Emits {
  (e: 'refresh'): void;
  (e: 'view-details', station: StationRanking): void;
  (e: 'compare', station: StationRanking): void;
  (e: 'export'): void;
}

const props = withDefaults(defineProps<Props>(), {
  title: '站点客流排名',
  subtitle: '按总客流量排序',
  showActions: true,
  showPagination: true,
  pageSize: 10,
  defaultSort: 'totalPassengers',
  defaultSortOrder: 'desc',
});

const emit = defineEmits<Emits>();

// 搜索和筛选
const searchQuery = ref('');
const sortBy = ref(props.defaultSort);
const sortOrder = ref<'asc' | 'desc'>(props.defaultSortOrder);
const currentPage = ref(1);
const pageSize = ref(props.pageSize);

// 默认列配置
const defaultColumns: TableColumn[] = [
  { key: 'totalPassengers', label: '总客流量', sortable: true, visible: true },
  { key: 'passengersIn', label: '上客量', sortable: true, visible: true },
  { key: 'passengersOut', label: '下客量', sortable: true, visible: true },
  { key: 'revenue', label: '收入', sortable: true, visible: true },
];

// 计算属性
const visibleColumns = computed(() => {
  const columns = props.columns || defaultColumns;
  return columns.filter(col => col.visible !== false);
});

const filteredData = computed(() => {
  if (!props.data) return [];

  let data = [...props.data];

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    data = data.filter(station =>
      station.stationName.toLowerCase().includes(query) ||
      station.stationTelecode.toLowerCase().includes(query)
    );
  }

  // 排序
  if (sortBy.value) {
    data.sort((a, b) => {
      const aValue = a[sortBy.value as keyof StationRanking];
      const bValue = b[sortBy.value as keyof StationRanking];

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortOrder.value === 'asc' ? aValue - bValue : bValue - aValue;
      }

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder.value === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return 0;
    });
  }

  return data;
});

const totalPages = computed(() => {
  return Math.ceil(filteredData.value.length / pageSize.value);
});

const startIndex = computed(() => {
  return (currentPage.value - 1) * pageSize.value;
});

const endIndex = computed(() => {
  return Math.min(startIndex.value + pageSize.value, filteredData.value.length);
});

const paginatedData = computed(() => {
  return filteredData.value.slice(startIndex.value, endIndex.value);
});

const visiblePages = computed(() => {
  const pages: number[] = [];
  const maxVisible = 5;
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2));
  let end = Math.min(totalPages.value, start + maxVisible - 1);

  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1);
  }

  for (let i = start; i <= end; i++) {
    pages.push(i);
  }

  return pages;
});

const showEllipsis = computed(() => {
  return totalPages.value > visiblePages.value.length &&
    visiblePages.value[visiblePages.value.length - 1] < totalPages.value;
});

// 方法
const toggleSort = (columnKey: string) => {
  if (sortBy.value === columnKey) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortBy.value = columnKey;
    sortOrder.value = 'desc';
  }
  currentPage.value = 1;
};

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

const formatMetric = (value: any, key: string): string => {
  if (typeof value === 'number') {
    // 根据键名选择格式化方式
    if (key.includes('Passengers') || key === 'totalPassengers') {
      if (value >= 10000) {
        return (value / 10000).toFixed(1) + '万';
      }
      return value.toLocaleString();
    } else if (key === 'revenue') {
      if (value >= 10000) {
        return '¥' + (value / 10000).toFixed(1) + '万';
      }
      return '¥' + value.toLocaleString();
    } else if (key === 'ranking') {
      return '#' + value;
    }
    return value.toLocaleString();
  }
  return String(value);
};

const formatChange = (change: number): string => {
  if (change > 0) return `↑${Math.abs(change)}`;
  if (change < 0) return `↓${Math.abs(change)}`;
  return '→';
};

const getRankClass = (rank: number): string => {
  if (rank <= 3) return 'rank-top';
  if (rank <= 10) return 'rank-high';
  return 'rank-normal';
};

const getChangeClass = (change: number): string => {
  if (change > 0) return 'change-up';
  if (change < 0) return 'change-down';
  return 'change-stable';
};

const exportData = () => {
  emit('export');
};

// 监听数据变化
watch(() => props.data, () => {
  currentPage.value = 1;
});

// 监听页面大小变化
watch(pageSize, () => {
  currentPage.value = 1;
});
</script>

<style scoped lang="scss">
.station-ranking-table {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.table-title {
  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }

  .table-subtitle {
    margin: 4px 0 0;
    font-size: 12px;
    color: #909399;
  }
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  position: relative;
  width: 200px;
}

.search-input {
  width: 100%;
  padding: 8px 32px 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  background: #fff;
  transition: all 0.2s ease;

  &:focus {
    outline: none;
    border-color: #409eff;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
  }

  &::placeholder {
    color: #c0c4cc;
  }
}

.search-icon {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #c0c4cc;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #c0c4cc;
    background: #f5f7fa;
  }

  &:active {
    border-color: #409eff;
    color: #409eff;
  }

  svg {
    width: 16px;
    height: 16px;
  }
}

.table-container {
  overflow-x: auto;
}

.ranking-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.ranking-table thead {
  background: #fafafa;
}

.ranking-table th {
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #909399;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
}

.ranking-table td {
  padding: 16px;
  font-size: 14px;
  color: #606266;
  border-bottom: 1px solid #f0f0f0;
}

.ranking-table tbody tr {
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #f5f7fa;
  }

  &:last-child td {
    border-bottom: none;
  }
}

.rank-col {
  width: 80px;
}

.station-col {
  min-width: 150px;
}

.metric-col {
  min-width: 120px;
}

.action-col {
  width: 100px;
}

.column-header {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sort-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  border: none;
  background: transparent;
  color: #c0c4cc;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    color: #409eff;
  }

  svg {
    width: 12px;
    height: 12px;
    transition: transform 0.2s ease;

    &.active {
      color: #409eff;
    }
  }
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  background: #f5f7fa;
  color: #606266;

  &.rank-top {
    background: #f0f9ff;
    color: #409eff;
  }

  &.rank-high {
    background: #fdf6ec;
    color: #e6a23c;
  }
}

.rank-change {
  font-size: 10px;
  font-weight: normal;

  &.change-up {
    color: #67c23a;
  }

  &.change-down {
    color: #f56c6c;
  }

  &.change-stable {
    color: #909399;
  }
}

.station-info {
  .station-name {
    font-weight: 500;
    color: #303133;
    margin-bottom: 2px;
  }

  .station-code {
    font-size: 12px;
    color: #909399;
  }
}

.metric-value {
  font-weight: 500;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #409eff;
    color: #409eff;
    background: #f0f9ff;
  }

  svg {
    width: 14px;
    height: 14px;
  }
}

.empty-state {
  text-align: center;
  padding: 48px 16px;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #909399;

  svg {
    width: 48px;
    height: 48px;
    color: #dcdfe6;
  }

  p {
    margin: 0;
    font-size: 14px;
  }
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.pagination-info {
  font-size: 12px;
  color: #909399;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-btn {
  padding: 6px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover:not(:disabled) {
    border-color: #409eff;
    color: #409eff;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #409eff;
    color: #409eff;
  }

  &.active {
    border-color: #409eff;
    background: #409eff;
    color: #fff;
  }
}

.page-ellipsis {
  padding: 0 8px;
  font-size: 12px;
  color: #909399;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.page-size-select {
  padding: 4px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  font-size: 12px;
  color: #606266;
  cursor: pointer;

  &:focus {
    outline: none;
    border-color: #409eff;
  }
}
</style>