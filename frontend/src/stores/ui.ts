import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Notification, ModalState, Toast } from '@/types/ui'

/**
 * UI状态管理
 */
export const useUIStore = defineStore('ui', () => {
  // 状态
  const notifications = ref<Notification[]>([])
  const modals = ref<Record<string, ModalState>>({})
  const toasts = ref<Toast[]>([])
  const sidebarOpen = ref(true)
  const activeNavItem = ref('dashboard')
  const breadcrumbs = ref<Array<{ label: string; path?: string }>>([])
  const pageTitle = ref('铁路客运分析系统')
  const isLoading = ref(false)
  const loadingText = ref('加载中...')

  // 计算属性
  const unreadNotifications = computed(() => {
    return notifications.value.filter(n => !n.read)
  })

  const unreadCount = computed(() => unreadNotifications.value.length)

  const activeModals = computed(() => {
    return Object.values(modals.value).filter(modal => modal.open)
  })

  const hasActiveModals = computed(() => activeModals.value.length > 0)

  // 操作 - 通知
  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false,
      ...notification,
    }

    notifications.value.unshift(newNotification)

    // 限制通知数量
    if (notifications.value.length > 50) {
      notifications.value = notifications.value.slice(0, 50)
    }

    return newNotification.id
  }

  const markNotificationAsRead = (id: string) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  }

  const markAllNotificationsAsRead = () => {
    notifications.value.forEach(n => { n.read = true })
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearNotifications = () => {
    notifications.value = []
  }

  // 操作 - 模态框
  const openModal = (name: string, data?: any) => {
    modals.value[name] = {
      open: true,
      data,
    }
  }

  const closeModal = (name: string) => {
    if (modals.value[name]) {
      modals.value[name].open = false
    }
  }

  const toggleModal = (name: string, data?: any) => {
    if (modals.value[name]?.open) {
      closeModal(name)
    } else {
      openModal(name, data)
    }
  }

  const closeAllModals = () => {
    Object.keys(modals.value).forEach(name => {
      modals.value[name]!.open = false
    })
  }

  // 操作 - Toast
  const showToast = (toast: Omit<Toast, 'id'>) => {
    const newToast: Toast = {
      id: Date.now().toString(),
      ...toast,
    }

    toasts.value.push(newToast)

    // 自动移除
    if (toast.duration !== 0) {
      const duration = toast.duration || 5000
      setTimeout(() => {
        removeToast(newToast.id)
      }, duration)
    }

    return newToast.id
  }

  const removeToast = (id: string) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  const clearToasts = () => {
    toasts.value = []
  }

  // 操作 - 导航
  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }

  const setSidebarOpen = (open: boolean) => {
    sidebarOpen.value = open
  }

  const setActiveNavItem = (item: string) => {
    activeNavItem.value = item
  }

  const setBreadcrumbs = (crumbs: Array<{ label: string; path?: string }>) => {
    breadcrumbs.value = crumbs
  }

  const addBreadcrumb = (crumb: { label: string; path?: string }) => {
    breadcrumbs.value.push(crumb)
  }

  const popBreadcrumb = () => {
    if (breadcrumbs.value.length > 1) {
      breadcrumbs.value.pop()
    }
  }

  const setPageTitle = (title: string) => {
    pageTitle.value = title
    document.title = title
  }

  // 操作 - 加载状态
  const setLoading = (loading: boolean, text = '加载中...') => {
    isLoading.value = loading
    loadingText.value = text
  }

  // 工具方法
  const showSuccess = (message: string, duration = 3000) => {
    return showToast({
      type: 'success',
      message,
      duration,
    })
  }

  const showError = (message: string, duration = 5000) => {
    return showToast({
      type: 'error',
      message,
      duration,
    })
  }

  const showWarning = (message: string, duration = 4000) => {
    return showToast({
      type: 'warning',
      message,
      duration,
    })
  }

  const showInfo = (message: string, duration = 3000) => {
    return showToast({
      type: 'info',
      message,
      duration,
    })
  }

  // 确认对话框
  const confirm = (options: {
    title: string
    message: string
    confirmText?: string
    cancelText?: string
    type?: 'warning' | 'danger' | 'info'
  }): Promise<boolean> => {
    return new Promise(resolve => {
      openModal('confirm', { ...options, resolve })
    })
  }

  // 初始化
  const init = () => {
    // 可以在这里添加初始化逻辑
  }

  return {
    // 状态
    notifications,
    modals,
    toasts,
    sidebarOpen,
    activeNavItem,
    breadcrumbs,
    pageTitle,
    isLoading,
    loadingText,

    // 计算属性
    unreadNotifications,
    unreadCount,
    activeModals,
    hasActiveModals,

    // 操作 - 通知
    addNotification,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    removeNotification,
    clearNotifications,

    // 操作 - 模态框
    openModal,
    closeModal,
    toggleModal,
    closeAllModals,

    // 操作 - Toast
    showToast,
    removeToast,
    clearToasts,

    // 操作 - 导航
    toggleSidebar,
    setSidebarOpen,
    setActiveNavItem,
    setBreadcrumbs,
    addBreadcrumb,
    popBreadcrumb,
    setPageTitle,

    // 操作 - 加载状态
    setLoading,

    // 工具方法
    showSuccess,
    showError,
    showWarning,
    showInfo,
    confirm,

    // 初始化
    init,
  }
})