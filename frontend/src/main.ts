import { createApp } from 'vue'
import { createPinia } from 'pinia'

// 导入Element Plus样式
import 'element-plus/dist/index.css'

// 导入北欧美学设计系统样式
import './styles/variables.css'
import './styles/base.css'
import './styles/utilities.css'
import './styles/components.css'
import './styles/animations.css'

import App from './App.vue'
import router from './router'

// 创建Pinia实例
const pinia = createPinia()

// 创建Vue应用
const app = createApp(App)

// 使用插件
app.use(pinia)
app.use(router)

// 挂载应用
app.mount('#app')
