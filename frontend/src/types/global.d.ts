/**
 * 全局类型声明
 */

// 高德地图全局变量声明
declare global {
  interface Window {
    AMap: any
  }
}

// 确保这是一个模块
export {}