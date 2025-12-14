import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'

// 页面组件（使用懒加载）
const Dashboard = () => import('@/views/Dashboard.vue')
const Analytics = () => import('@/views/Analytics.vue')
const Optimization = () => import('@/views/Optimization.vue')
const Stations = () => import('@/views/Stations.vue')
const DataManagement = () => import('@/views/DataManagement.vue')
const DataManagementSimple = () => import('@/views/DataManagementSimple.vue')

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: AppLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: {
          title: '总览',
          description: '系统总览和核心指标展示',
          requiresAuth: true,
          icon: 'dashboard'
        }
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: Analytics,
        meta: {
          title: '客流分析',
          description: '客流统计、时空分布和预测分析',
          requiresAuth: true,
          icon: 'analytics'
        }
      },
      {
        path: 'optimization',
        name: 'Optimization',
        component: Optimization,
        meta: {
          title: '线路优化',
          description: '线路负载分析和优化建议',
          requiresAuth: true,
          icon: 'optimization'
        }
      },
      {
        path: 'stations',
        name: 'Stations',
        component: Stations,
        meta: {
          title: '站点评估',
          description: '站点繁忙度评估和角色分析',
          requiresAuth: true,
          icon: 'stations'
        }
      },
      {
        path: 'data',
        name: 'DataManagement',
        component: DataManagement,
        meta: {
          title: '数据管理',
          description: '数据导入、清洗和管理',
          requiresAuth: true,
          icon: 'data'
        }
      },
      {
        path: 'data-simple',
        name: 'DataManagementSimple',
        component: DataManagementSimple,
        meta: {
          title: '数据管理测试',
          description: '数据管理页面测试',
          requiresAuth: true,
          icon: 'data'
        }
      }
    ]
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫：权限验证
router.beforeEach((to, _from, next) => {
  // 设置页面标题
  const appTitle = import.meta.env.VITE_APP_TITLE || '铁路客运分析系统'
  if (to.meta.title) {
    document.title = `${to.meta.title} - ${appTitle}`
  } else {
    document.title = appTitle
  }

  // 权限验证逻辑（示例）
  if (to.meta.requiresAuth) {
    // 这里可以添加实际的权限验证逻辑
    const isAuthenticated = true // 假设用户已认证
    if (!isAuthenticated) {
      next('/login')
      return
    }
  }

  next()
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  // 可以在这里添加错误处理逻辑，比如跳转到错误页面
})

export default router