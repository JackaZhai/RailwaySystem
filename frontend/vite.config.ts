import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = (env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/api\/?$/, '')

  return {
    plugins: [vue()],

    // 开发服务器配置
    server: {
      port: 5173,
      host: true,
      open: true, // 自动打开浏览器
      proxy: {
        // 代理API请求到Django后端
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          // Django后端API路径已经包含/api前缀，所以不需要重写
        },
        // 高德地图API代理（如果需要）
        '/v3': {
          target: 'https://restapi.amap.com',
          changeOrigin: true,
          rewrite: (path) => path,
        }
      }
    },

    // 构建配置
    build: {
      outDir: 'dist',
      sourcemap: mode !== 'production',
      rollupOptions: {
        output: {
          manualChunks(id) {
            // 手动分块策略
            if (id.includes('node_modules')) {
              if (id.includes('vue')) {
                return 'vue-vendor'
              }
              if (id.includes('element-plus')) {
                return 'ui-vendor'
              }
              if (id.includes('echarts')) {
                return 'chart-vendor'
              }
              if (id.includes('amap')) {
                return 'map-vendor'
              }
              // 其他依赖归到vendor
              return 'vendor'
            }
          }
        }
      }
    },

    // 路径别名
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
        '@components': fileURLToPath(new URL('./src/components', import.meta.url)),
        '@views': fileURLToPath(new URL('./src/views', import.meta.url)),
        '@stores': fileURLToPath(new URL('./src/stores', import.meta.url)),
        '@api': fileURLToPath(new URL('./src/api', import.meta.url)),
        '@utils': fileURLToPath(new URL('./src/utils', import.meta.url)),
        '@types': fileURLToPath(new URL('./src/types', import.meta.url)),
      }
    },

    // CSS配置
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/styles/variables.css";`
        }
      }
    }
  }
})
