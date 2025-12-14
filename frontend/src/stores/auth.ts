import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, RegisterData } from '@/types/auth'

/**
 * 用户认证状态管理
 */
export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 操作
  const login = async (credentials: LoginCredentials) => {
    try {
      isLoading.value = true
      error.value = null

      // 模拟登录API调用
      // 实际应用中应该调用后端API
      await new Promise(resolve => setTimeout(resolve, 1000))

      // 模拟响应
      const mockUser: User = {
        id: 1,
        username: credentials.username,
        email: 'user@example.com',
        name: '铁路管理员',
        role: 'admin',
        permissions: ['view_dashboard', 'manage_data', 'view_analytics'],
        avatar: '',
      }

      const mockToken = 'mock-jwt-token'

      user.value = mockUser
      token.value = mockToken

      // 保存到本地存储
      localStorage.setItem('auth_token', mockToken)
      localStorage.setItem('user', JSON.stringify(mockUser))

      return { success: true, user: mockUser }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '登录失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    user.value = null
    token.value = null
    error.value = null

    // 清除本地存储
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
  }

  const register = async (data: RegisterData) => {
    try {
      isLoading.value = true
      error.value = null

      // 模拟注册API调用
      await new Promise(resolve => setTimeout(resolve, 1000))

      // 模拟响应
      const mockUser: User = {
        id: 2,
        username: data.username,
        email: data.email,
        name: data.name || data.username,
        role: 'user',
        permissions: ['view_dashboard', 'view_analytics'],
        avatar: '',
      }

      const mockToken = 'mock-jwt-token-registered'

      user.value = mockUser
      token.value = mockToken

      // 保存到本地存储
      localStorage.setItem('auth_token', mockToken)
      localStorage.setItem('user', JSON.stringify(mockUser))

      return { success: true, user: mockUser }
    } catch (err) {
      error.value = err instanceof Error ? err.message : '注册失败'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const checkAuth = () => {
    // 从本地存储恢复认证状态
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('user')

    if (savedToken && savedUser) {
      try {
        token.value = savedToken
        user.value = JSON.parse(savedUser)
      } catch {
        // 解析失败，清除本地存储
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user')
      }
    }
  }

  const clearError = () => {
    error.value = null
  }

  // 检查权限
  const hasPermission = (permission: string) => {
    if (!user.value) return false
    return user.value.permissions.includes(permission)
  }

  const hasRole = (role: string) => {
    if (!user.value) return false
    return user.value.role === role
  }

  return {
    // 状态
    user,
    token,
    isLoading,
    error,

    // 计算属性
    isAuthenticated,

    // 操作
    login,
    logout,
    register,
    checkAuth,
    clearError,
    hasPermission,
    hasRole,
  }
})