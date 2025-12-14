<script setup lang="ts">
import { onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { useMapStore } from '@/stores/map'
import { useUIStore } from '@/stores/ui'

// 初始化store
const appStore = useAppStore()
const authStore = useAuthStore()
const mapStore = useMapStore()
const uiStore = useUIStore()

onMounted(() => {
  // 初始化应用
  appStore.init()
  authStore.checkAuth()
  mapStore.loadMapConfig()
  uiStore.init()
})
</script>

<template>
  <router-view />
</template>

<style>
/* 全局样式 */
#app {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
