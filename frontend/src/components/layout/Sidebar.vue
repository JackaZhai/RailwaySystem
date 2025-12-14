<template>
  <aside class="sidebar" :class="{ collapsed }">
    <!-- 侧边栏头部 -->
    <div class="sidebar-header">
      <div class="logo" @click="$router.push('/')">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 12H15M9 6H15M9 18H15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span v-show="!collapsed" class="logo-text">铁路数据分析</span>
      </div>
      <button class="collapse-btn" @click="$emit('update:collapsed', !collapsed)">
        <svg :class="{ rotated: collapsed }" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 5L16 12L9 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <!-- 导航菜单 -->
    <nav class="sidebar-nav">
      <ul class="nav-list">
        <li v-for="item in navItems" :key="item.path" class="nav-item">
          <router-link
            :to="item.path"
            class="nav-link"
            :class="{ active: $route.path === item.path }"
            :title="item.title"
          >
            <span class="nav-icon" v-html="item.icon"></span>
            <span v-show="!collapsed" class="nav-text">{{ item.title }}</span>
            <span v-if="item.badge" v-show="!collapsed" class="nav-badge">{{ item.badge }}</span>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- 侧边栏底部 -->
    <div v-show="!collapsed" class="sidebar-footer">
      <div class="system-status">
        <div class="status-indicator online"></div>
        <span class="status-text">系统在线</span>
      </div>
      <div class="last-update">
        最后更新: {{ lastUpdateTime }}
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

defineProps<{
  collapsed: boolean
}>()

defineEmits<{
  'update:collapsed': [value: boolean]
}>()

// 路由对象（当前未使用，注释掉以避免编译错误）
// const route = useRoute()

// 导航菜单项
const navItems = ref([
  {
    path: '/',
    title: '总览',
    icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 22V12H15V22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    badge: ''
  },
  {
    path: '/analytics',
    title: '客流分析',
    icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 20V10M12 20V4M6 20V14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    badge: ''
  },
  {
    path: '/optimization',
    title: '线路优化',
    icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    badge: ''
  },
  {
    path: '/stations',
    title: '站点评估',
    icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M12 11C13.1046 11 14 10.1046 14 9C14 7.89543 13.1046 7 12 7C10.8954 7 10 7.89543 10 9C10 10.1046 10.8954 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    badge: ''
  },
  {
    path: '/data',
    title: '数据管理',
    icon: '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M21 12V7H3V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M3 17H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M9 12V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M15 12V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    badge: ''
  }
])

// 最后更新时间
const lastUpdateTime = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${(now.getMonth() + 1).toString().padStart(2, '0')}-${now.getDate().toString().padStart(2, '0')} ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
})
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  background-color: var(--color-bg-sidebar);
  color: var(--color-text-inverse);
  display: flex;
  flex-direction: column;
  z-index: var(--z-index-sidebar);
  transition: width var(--transition-base);
  box-shadow: var(--shadow-md);
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: var(--spacing-6) var(--spacing-4);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  cursor: pointer;
  user-select: none;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-primary);
  border-radius: var(--border-radius-base);
  color: white;
  flex-shrink: 0;
}

.logo-icon svg {
  width: 20px;
  height: 20px;
}

.logo-text {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.collapse-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--border-radius-base);
  color: var(--color-text-inverse);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  flex-shrink: 0;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.collapse-btn svg {
  width: 16px;
  height: 16px;
  transition: transform var(--transition-base);
}

.collapse-btn svg.rotated {
  transform: rotate(180deg);
}

.sidebar-nav {
  flex: 1;
  padding: var(--spacing-4) 0;
  overflow-y: auto;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0 var(--spacing-2);
}

.nav-link {
  display: flex;
  align-items: center;
  padding: var(--spacing-3) var(--spacing-4);
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  border-radius: var(--border-radius-base);
  transition: all var(--transition-fast);
  position: relative;
  gap: var(--spacing-3);
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--color-text-inverse);
}

.nav-link.active {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.nav-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
}

.nav-text {
  flex: 1;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-badge {
  background-color: var(--color-accent);
  color: var(--color-text-inverse);
  font-size: var(--font-size-xs);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius-full);
}

.sidebar-footer {
  padding: var(--spacing-4);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: var(--font-size-xs);
}

.system-status {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-2);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.online {
  background-color: var(--color-success);
  box-shadow: 0 0 0 2px rgba(46, 139, 87, 0.2);
}

.status-text {
  color: rgba(255, 255, 255, 0.7);
}

.last-update {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 64px;
  }

  .sidebar:not(.collapsed) {
    width: 280px;
    z-index: var(--z-index-modal);
  }
}
</style>