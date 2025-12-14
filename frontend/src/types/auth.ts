/**
 * 用户认证相关类型定义
 */

export interface User {
  id: number
  username: string
  email: string
  name: string
  role: 'admin' | 'user' | 'viewer'
  permissions: string[]
  avatar: string
}

export interface LoginCredentials {
  username: string
  password: string
  remember?: boolean
}

export interface RegisterData {
  username: string
  email: string
  password: string
  confirmPassword: string
  name?: string
}

export interface AuthResponse {
  success: boolean
  user?: User
  token?: string
  error?: string
}

export interface Permission {
  id: string
  name: string
  description: string
}