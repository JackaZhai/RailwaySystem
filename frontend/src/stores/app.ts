import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 应用全局状态管理
 */
export const useAppStore = defineStore('app', () => {
  // 状态
  const theme = ref<'light' | 'dark'>('light')
  const language = ref<'zh' | 'en'>('zh')
  const isLoading = ref(false)
  const loadingMessage = ref('')
  const sidebarCollapsed = ref(false)
  const isMobile = ref(false)

  // 计算属性
  const isDarkMode = computed(() => theme.value === 'dark')
  const isChinese = computed(() => language.value === 'zh')

  // 操作
  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    // 可以在这里添加保存到本地存储的逻辑
    localStorage.setItem('theme', theme.value)
  }

  const toggleLanguage = () => {
    language.value = language.value === 'zh' ? 'en' : 'zh'
    localStorage.setItem('language', language.value)
  }

  const setLoading = (loading: boolean, message = '') => {
    isLoading.value = loading
    loadingMessage.value = message
  }

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  const setMobile = (mobile: boolean) => {
    isMobile.value = mobile
  }

  // 初始化
  const init = () => {
    // 从本地存储恢复主题和语言
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark'
    const savedLanguage = localStorage.getItem('language') as 'zh' | 'en'

    if (savedTheme) theme.value = savedTheme
    if (savedLanguage) language.value = savedLanguage

    // 检测移动设备
    const checkMobile = () => {
      setMobile(window.innerWidth < 768)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
  }

  return {
    // 状态
    theme,
    language,
    isLoading,
    loadingMessage,
    sidebarCollapsed,
    isMobile,

    // 计算属性
    isDarkMode,
    isChinese,

    // 操作
    toggleTheme,
    toggleLanguage,
    setLoading,
    toggleSidebar,
    setMobile,
    init,
  }
})