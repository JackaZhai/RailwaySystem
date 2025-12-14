<template>
  <header class="app-header">
    <!-- 左侧：面包屑和侧边栏切换 -->
    <div class="header-left">
      <button class="sidebar-toggle" @click="$emit('toggle-sidebar')">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <nav class="breadcrumb">
        <router-link to="/" class="breadcrumb-item">首页</router-link>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-current">{{ currentPageTitle }}</span>
      </nav>
    </div>

    <!-- 中间：全局搜索 -->
    <div class="header-center">
      <div class="search-container">
        <div class="search-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M11 19C15.4183 19 19 15.4183 19 11C19 6.58172 15.4183 3 11 3C6.58172 3 3 6.58172 3 11C3 15.4183 6.58172 19 11 19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M21 21L16.65 16.65" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索站点、线路、数据..."
          @keyup.enter="performSearch"
        />
        <button v-if="searchQuery" class="search-clear" @click="clearSearch">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 右侧：用户操作 -->
    <div class="header-right">
      <!-- 通知 -->
      <div class="notification-container">
        <button class="notification-btn" @click="toggleNotifications">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 8C18 6.4087 17.3679 4.88258 16.2426 3.75736C15.1174 2.63214 13.5913 2 12 2C10.4087 2 8.88258 2.63214 7.75736 3.75736C6.63214 4.88258 6 6.4087 6 8C6 15 3 17 3 17H21C21 17 18 15 18 8Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13.73 21C13.5542 21.3031 13.3018 21.5547 12.9982 21.7295C12.6946 21.9044 12.3504 21.9965 12 21.9965C11.6496 21.9965 11.3054 21.9044 11.0018 21.7295C10.6982 21.5547 10.4458 21.3031 10.27 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
        </button>
        <div v-if="showNotifications" class="notification-dropdown">
          <div class="notification-header">
            <h3>通知</h3>
            <button class="mark-all-read" @click="markAllAsRead">全部已读</button>
          </div>
          <div class="notification-list">
            <div v-for="notification in notifications" :key="notification.id" class="notification-item" :class="{ unread: !notification.read }">
              <div class="notification-icon" :class="notification.type">
                <svg v-if="notification.type === 'info'" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 16V12M12 8H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 2C6.477 2 2 6.477 2 12C2 17.523 6.477 22 12 22C17.523 22 22 17.523 22 12C22 6.477 17.523 2 12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg v-else-if="notification.type === 'warning'" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M10.29 3.86L1.82 18C1.64538 18.3024 1.55297 18.6453 1.552 19C1.55103 19.3547 1.64154 19.698 1.81445 20.001C1.98735 20.304 2.23675 20.5561 2.53773 20.732C2.83871 20.9079 3.18082 21.0013 3.53 21H20.47C20.8192 21.0013 21.1613 20.9079 21.4623 20.732C21.7632 20.5561 22.0127 20.304 22.1855 20.001C22.3585 19.698 22.449 19.3547 22.448 19C22.447 18.6453 22.3546 18.3024 22.18 18L13.71 3.86C13.5318 3.56611 13.2807 3.32312 12.9812 3.15448C12.6817 2.98585 12.3437 2.89725 12 2.89725C11.6563 2.89725 11.3183 2.98585 11.0188 3.15448C10.7193 3.32312 10.4682 3.56611 10.29 3.86Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 9V13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 17H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 8V12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 16H12.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="notification-content">
                <p class="notification-title">{{ notification.title }}</p>
                <p class="notification-time">{{ notification.time }}</p>
              </div>
            </div>
          </div>
          <div class="notification-footer">
            <router-link to="/notifications" class="view-all">查看全部</router-link>
          </div>
        </div>
      </div>

      <!-- 用户信息 -->
      <div class="user-container">
        <button class="user-btn" @click="toggleUserMenu">
          <div class="user-avatar">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Railway" alt="用户头像" />
          </div>
          <span class="user-name">管理员</span>
          <svg class="chevron" :class="{ rotated: showUserMenu }" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div v-if="showUserMenu" class="user-menu">
          <div class="user-info">
            <div class="user-avatar-large">
              <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Railway" alt="用户头像" />
            </div>
            <div class="user-details">
              <p class="user-name-large">管理员</p>
              <p class="user-email">admin@railway-analysis.cn</p>
            </div>
          </div>
          <div class="user-menu-items">
            <router-link to="/profile" class="menu-item">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>个人资料</span>
            </router-link>
            <router-link to="/settings" class="menu-item">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M19.4 15C19.2669 15.3068 19.1333 15.6133 19 15.92C19.151 16.248 19.302 16.576 19.453 16.904L21 17C21.95 17 22.425 18.07 21.726 18.768L20 20.394C19.696 20.698 19.848 21.075 20.276 21.11C20.5897 21.1358 20.9047 21.1358 21.2184 21.11C22.2684 21.011 23 20.105 23 19.05V18C23 17.447 22.552 17 22 17H21.349M4.6 15C4.73306 15.3068 4.86665 15.6133 5 15.92C4.84904 16.248 4.69808 16.576 4.54712 16.904L3 17C2.05 17 1.575 18.07 2.274 18.768L4 20.394C4.304 20.698 4.152 21.075 3.724 21.11C3.4103 21.1358 3.09534 21.1358 2.78164 21.11C1.73164 21.011 1 20.105 1 19.05V18C1 17.447 1.448 17 2 17H2.651M12 5V3M12 21V19M3 12H1M23 12H21M5.6 7.4L4 5.8M18.4 7.4L20 5.8M5.6 16.6L4 18.2M18.4 16.6L20 18.2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>系统设置</span>
            </router-link>
            <div class="menu-divider"></div>
            <button class="menu-item logout" @click="logout">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 17L21 12L16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>退出登录</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

defineEmits<{
  'toggle-sidebar': []
}>()

const route = useRoute()
const searchQuery = ref('')
const showNotifications = ref(false)
const showUserMenu = ref(false)

// 页面标题映射
const pageTitles: Record<string, string> = {
  '/': '总览',
  '/analytics': '客流分析',
  '/optimization': '线路优化',
  '/stations': '站点评估',
  '/data': '数据管理'
}

const currentPageTitle = computed(() => {
  return pageTitles[route.path] || '未知页面'
})

// 通知相关
const notifications = ref([
  { id: 1, title: '今日客流高峰预警', type: 'warning', time: '10分钟前', read: false },
  { id: 2, title: '数据导入完成', type: 'success', time: '1小时前', read: true },
  { id: 3, title: '系统维护通知', type: 'info', time: '3小时前', read: true },
  { id: 4, title: '新版本可用', type: 'info', time: '1天前', read: true }
])

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  showUserMenu.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showNotifications.value = false
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
}

const performSearch = () => {
  if (searchQuery.value.trim()) {
    console.log('搜索:', searchQuery.value)
    // 实际项目中这里会触发搜索逻辑
  }
}

const clearSearch = () => {
  searchQuery.value = ''
}

const logout = () => {
  console.log('退出登录')
  // 实际项目中这里会调用退出登录API
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.notification-container')) {
    showNotifications.value = false
  }
  if (!target.closest('.user-container')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-6);
  height: 64px;
  background-color: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border);
  z-index: var(--z-index-header);
  position: sticky;
  top: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  flex: 1;
}

.sidebar-toggle {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-secondary);
  border-radius: var(--border-radius-base);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.sidebar-toggle:hover {
  background-color: var(--color-bg-tertiary);
}

.sidebar-toggle svg {
  width: 20px;
  height: 20px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  font-size: var(--font-size-sm);
}

.breadcrumb-item {
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.breadcrumb-item:hover {
  color: var(--color-text-primary);
}

.breadcrumb-separator {
  color: var(--color-text-tertiary);
}

.breadcrumb-current {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.header-center {
  flex: 2;
  display: flex;
  justify-content: center;
}

.search-container {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: var(--spacing-3);
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--color-text-tertiary);
}

.search-icon svg {
  width: 100%;
  height: 100%;
}

.search-input {
  width: 100%;
  padding: var(--spacing-2) var(--spacing-3) var(--spacing-2) 40px;
  font-size: var(--font-size-sm);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-full);
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-secondary);
  box-shadow: 0 0 0 3px rgba(70, 130, 180, 0.1);
}

.search-clear {
  position: absolute;
  right: var(--spacing-3);
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background: none;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
}

.search-clear svg {
  width: 100%;
  height: 100%;
}

.search-clear:hover {
  color: var(--color-text-primary);
}

.header-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-4);
}

.notification-container,
.user-container {
  position: relative;
}

.notification-btn,
.user-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--spacing-2);
  border-radius: var(--border-radius-base);
  transition: background-color var(--transition-fast);
}

.notification-btn:hover,
.user-btn:hover {
  background-color: var(--color-bg-secondary);
}

.notification-btn svg {
  width: 20px;
  height: 20px;
  color: var(--color-text-primary);
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: var(--color-error);
  color: var(--color-text-inverse);
  font-size: var(--font-size-xs);
  min-width: 16px;
  height: 16px;
  border-radius: var(--border-radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--color-bg-secondary);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.chevron {
  width: 16px;
  height: 16px;
  color: var(--color-text-tertiary);
  transition: transform var(--transition-fast);
}

.chevron.rotated {
  transform: rotate(180deg);
}

/* 通知下拉菜单 */
.notification-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 320px;
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  margin-top: var(--spacing-2);
  z-index: var(--z-index-dropdown);
  overflow: hidden;
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--color-border);
}

.notification-header h3 {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
}

.mark-all-read {
  background: none;
  border: none;
  color: var(--color-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  padding: 0;
}

.notification-list {
  max-height: 300px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--color-border-light);
  transition: background-color var(--transition-fast);
}

.notification-item:hover {
  background-color: var(--color-bg-secondary);
}

.notification-item.unread {
  background-color: rgba(70, 130, 180, 0.05);
}

.notification-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--border-radius-base);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.notification-icon.info {
  background-color: rgba(70, 130, 180, 0.1);
  color: var(--color-secondary);
}

.notification-icon.warning {
  background-color: rgba(255, 165, 0, 0.1);
  color: var(--color-warning);
}

.notification-icon.success {
  background-color: rgba(46, 139, 87, 0.1);
  color: var(--color-success);
}

.notification-icon svg {
  width: 16px;
  height: 16px;
}

.notification-content {
  flex: 1;
}

.notification-title {
  margin: 0 0 var(--spacing-1) 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.notification-time {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.notification-footer {
  padding: var(--spacing-3) var(--spacing-4);
  border-top: 1px solid var(--color-border);
  text-align: center;
}

.view-all {
  color: var(--color-secondary);
  font-size: var(--font-size-sm);
  text-decoration: none;
}

.view-all:hover {
  text-decoration: underline;
}

/* 用户菜单 */
.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 280px;
  background-color: var(--color-bg-primary);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  margin-top: var(--spacing-2);
  z-index: var(--z-index-dropdown);
  overflow: hidden;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  background-color: var(--color-bg-secondary);
}

.user-avatar-large {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--color-bg-tertiary);
}

.user-avatar-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-details {
  flex: 1;
}

.user-name-large {
  margin: 0 0 var(--spacing-1) 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.user-email {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.user-menu-items {
  padding: var(--spacing-2) 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  width: 100%;
  padding: var(--spacing-3) var(--spacing-4);
  background: none;
  border: none;
  color: var(--color-text-primary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  text-align: left;
}

.menu-item:hover {
  background-color: var(--color-bg-secondary);
}

.menu-item svg {
  width: 16px;
  height: 16px;
  color: var(--color-text-secondary);
}

.menu-item.logout {
  color: var(--color-error);
}

.menu-item.logout svg {
  color: var(--color-error);
}

.menu-divider {
  height: 1px;
  background-color: var(--color-border);
  margin: var(--spacing-2) 0;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .header-center {
    display: none;
  }
}

@media (max-width: 768px) {
  .app-header {
    padding: 0 var(--spacing-4);
  }

  .user-name {
    display: none;
  }

  .notification-dropdown {
    width: 280px;
    right: -100px;
  }

  .user-menu {
    width: 240px;
    right: -50px;
  }
}
</style>