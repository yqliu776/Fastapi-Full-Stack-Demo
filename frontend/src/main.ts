import './assets/main.css'
import 'element-plus/theme-chalk/dark/css-vars.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import { registerIcons } from '@/utils/icons'
import '@/utils/theme'

// 创建应用实例
const app = createApp(App)

// 按需注册 Element Plus 图标
registerIcons(app)

// 创建并安装Pinia
const pinia = createPinia()
app.use(pinia)

// 安装路由
app.use(router)

// 安装Element Plus
app.use(ElementPlus, { size: 'default', zIndex: 3000 })

// 挂载应用
app.mount('#app')
