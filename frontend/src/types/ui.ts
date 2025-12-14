/**
 * UI相关类型定义
 */

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  read: boolean
  action?: {
    label: string
    handler: () => void
  }
  priority?: 'low' | 'medium' | 'high'
}

export interface ModalState {
  open: boolean
  data?: any
}

export interface Toast {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  message: string
  duration?: number // 毫秒，0表示不自动关闭
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center'
  dismissible?: boolean
}

export interface Breadcrumb {
  label: string
  path?: string
  icon?: string
}

export interface NavItem {
  id: string
  label: string
  icon: string
  path: string
  children?: NavItem[]
  badge?: number | string
  requiresAuth?: boolean
  permissions?: string[]
}

export interface Pagination {
  page: number
  pageSize: number
  total: number
  totalPages: number
}

export interface SortOption {
  field: string
  direction: 'asc' | 'desc'
}

export interface FilterOption {
  field: string
  operator: 'equals' | 'contains' | 'greaterThan' | 'lessThan' | 'between'
  value: any
}