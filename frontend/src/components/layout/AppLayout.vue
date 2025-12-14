<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <Sidebar v-model:collapsed="sidebarCollapsed" />

    <!-- 主内容区 -->
    <div class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- 顶部栏 -->
      <Header @toggle-sidebar="toggleSidebar" />

      <!-- 页面内容 -->
      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- 页脚 -->
      <footer class="app-footer">
        <div class="footer-content">
          <p class="copyright">
            &copy; {{ currentYear }} 成渝地区铁路客运智能分析与可视化系统
          </p>
          <p class="version">
            版本 1.0.0 | 基于北欧美学的民主化设计
          </p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'

const sidebarCollapsed = ref(false)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const currentYear = computed(() => new Date().getFullYear())
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-bg-primary);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 280px; /* 侧边栏宽度 */
  transition: margin-left var(--transition-base);
}

.main-content.sidebar-collapsed {
  margin-left: 64px; /* 侧边栏折叠后的宽度 */
}

.page-content {
  flex: 1;
  padding: var(--spacing-6);
  overflow-y: auto;
  background-color: var(--color-bg-secondary);
}

.app-footer {
  padding: var(--spacing-4) var(--spacing-6);
  background-color: var(--color-bg-primary);
  border-top: 1px solid var(--color-border);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.copyright,
.version {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }

  .main-content.sidebar-collapsed {
    margin-left: 0;
  }

  .page-content {
    padding: var(--spacing-4);
  }

  .footer-content {
    flex-direction: column;
    gap: var(--spacing-2);
    text-align: center;
  }
}
</style>