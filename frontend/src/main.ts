import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

// 创建应用实例
const app = createApp(App)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 创建并安装Pinia
const pinia = createPinia()
app.use(pinia)

// 安装路由
app.use(router)

// 安装Element Plus
app.use(ElementPlus, { size: 'default', zIndex: 3000 })

// 挂载应用
app.mount('#app')
