<template>
  <div class="skeleton-loader" :class="[type, { 'animate': animate }]">
    <!-- 卡片类型 -->
    <div v-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-header">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-title"></div>
      </div>
      <div class="skeleton-content">
        <div v-for="i in lines" :key="i" class="skeleton-line" :style="lineStyle(i)"></div>
      </div>
      <div class="skeleton-footer">
        <div class="skeleton-button"></div>
        <div class="skeleton-button"></div>
      </div>
    </div>

    <!-- 列表类型 -->
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div v-for="i in items" :key="i" class="skeleton-list-item">
        <div class="skeleton-list-avatar"></div>
        <div class="skeleton-list-content">
          <div class="skeleton-line" style="width: 70%"></div>
          <div class="skeleton-line" style="width: 40%"></div>
        </div>
      </div>
    </div>

    <!-- 表格类型 -->
    <div v-else-if="type === 'table'" class="skeleton-table">
      <div class="skeleton-table-header">
        <div v-for="i in columns" :key="i" class="skeleton-line" :style="headerCellStyle(i)"></div>
      </div>
      <div class="skeleton-table-body">
        <div v-for="row in rows" :key="row" class="skeleton-table-row">
          <div v-for="col in columns" :key="col" class="skeleton-line" :style="cellStyle(col)"></div>
        </div>
      </div>
    </div>

    <!-- 自定义类型 -->
    <div v-else-if="type === 'custom'" class="skeleton-custom">
      <slot></slot>
    </div>

    <!-- 文本类型（默认） -->
    <div v-else class="skeleton-text">
      <div v-for="i in lines" :key="i" class="skeleton-line" :style="lineStyle(i)"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'text' | 'card' | 'list' | 'table' | 'custom'
  lines?: number
  items?: number
  rows?: number
  columns?: number
  animate?: boolean
  speed?: 'slow' | 'normal' | 'fast'
  variant?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  lines: 3,
  items: 5,
  rows: 5,
  columns: 4,
  animate: true,
  speed: 'normal',
  variant: 'light'
})

const lineStyle = (index: number) => {
  const widths = ['100%', '90%', '80%', '70%', '60%']
  const width = widths[index % widths.length] || '100%'

  const heights = {
    slow: '1.5s',
    normal: '1s',
    fast: '0.7s'
  }

  return {
    width,
    animationDuration: heights[props.speed]
  }
}

const headerCellStyle = (index: number) => {
  const widths = ['15%', '20%', '25%', '20%', '15%', '5%']
  const width = widths[index % widths.length] || '100%'

  return {
    width,
    height: '24px'
  }
}

const cellStyle = (index: number) => {
  const widths = ['15%', '20%', '25%', '20%', '15%', '5%']
  const width = widths[index % widths.length] || '100%'

  return {
    width,
    height: '20px'
  }
}

const skeletonClass = computed(() => {
  const variants = {
    light: 'skeleton-light',
    dark: 'skeleton-dark'
  }
  return variants[props.variant]
})
</script>

<style scoped>
.skeleton-loader {
  width: 100%;
}

.skeleton-loader.animate {
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

/* 通用骨架线 */
.skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, var(--color-bg-secondary) 25%, var(--color-bg-tertiary) 50%, var(--color-bg-secondary) 75%);
  background-size: 200% 100%;
  border-radius: var(--border-radius-base);
  margin-bottom: var(--spacing-3);
}

.skeleton-line:last-child {
  margin-bottom: 0;
}

/* 卡片骨架 */
.skeleton-card {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4);
  box-shadow: var(--shadow-sm);
}

.skeleton-header {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-4);
}

.skeleton-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(90deg, var(--color-bg-secondary) 25%, var(--color-bg-tertiary) 50%, var(--color-bg-secondary) 75%);
  background-size: 200% 100%;
  margin-right: var(--spacing-3);
}

.skeleton-title {
  flex: 1;
  height: 20px;
  background: linear-gradient(90deg, var(--color-bg-secondary) 25%, var(--color-bg-tertiary) 50%, var(--color-bg-secondary) 75%);
  background-size: 200% 100%;
  border-radius: var(--border-radius-base);
}

.skeleton-content {
  margin-bottom: var(--spacing-4);
}

.skeleton-footer {
  display: flex;
  gap: var(--spacing-3);
}

.skeleton-button {
  width: 80px;
  height: 32px;
  background: linear-gradient(90deg, var(--color-bg-secondary) 25%, var(--color-bg-tertiary) 50%, var(--color-bg-secondary) 75%);
  background-size: 200% 100%;
  border-radius: var(--border-radius-base);
}

/* 列表骨架 */
.skeleton-list {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-3) var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
}

.skeleton-list-item:last-child {
  border-bottom: none;
}

.skeleton-list-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(90deg, var(--color-bg-secondary) 25%, var(--color-bg-tertiary) 50%, var(--color-bg-secondary) 75%);
  background-size: 200% 100%;
  margin-right: var(--spacing-3);
}

.skeleton-list-content {
  flex: 1;
}

/* 表格骨架 */
.skeleton-table {
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

.skeleton-table-header {
  display: flex;
  padding: var(--spacing-3) var(--spacing-4);
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.skeleton-table-header .skeleton-line {
  margin: 0 var(--spacing-2);
  background: linear-gradient(90deg, var(--color-bg-tertiary) 25%, var(--color-neutral-light) 50%, var(--color-bg-tertiary) 75%);
  background-size: 200% 100%;
}

.skeleton-table-body {
  padding: var(--spacing-3) var(--spacing-4);
}

.skeleton-table-row {
  display: flex;
  margin-bottom: var(--spacing-3);
}

.skeleton-table-row:last-child {
  margin-bottom: 0;
}

.skeleton-table-row .skeleton-line {
  margin: 0 var(--spacing-2);
}

/* 自定义骨架 */
.skeleton-custom {
  width: 100%;
}

/* 动画关键帧 */
@keyframes skeleton-loading {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

/* 变体样式 */
.skeleton-light .skeleton-line,
.skeleton-light .skeleton-avatar,
.skeleton-light .skeleton-title,
.skeleton-light .skeleton-button,
.skeleton-light .skeleton-list-avatar {
  background: linear-gradient(90deg, var(--color-bg-secondary) 25%, var(--color-bg-tertiary) 50%, var(--color-bg-secondary) 75%);
}

.skeleton-dark .skeleton-line,
.skeleton-dark .skeleton-avatar,
.skeleton-dark .skeleton-title,
.skeleton-dark .skeleton-button,
.skeleton-dark .skeleton-list-avatar {
  background: linear-gradient(90deg, var(--color-neutral-light) 25%, var(--color-neutral) 50%, var(--color-neutral-light) 75%);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .skeleton-table-header,
  .skeleton-table-row {
    flex-wrap: wrap;
  }

  .skeleton-table-header .skeleton-line,
  .skeleton-table-row .skeleton-line {
    flex: 1 0 calc(50% - var(--spacing-4));
    margin-bottom: var(--spacing-2);
  }

  .skeleton-card {
    padding: var(--spacing-3);
  }

  .skeleton-list-item {
    padding: var(--spacing-2) var(--spacing-3);
  }
}
</style>