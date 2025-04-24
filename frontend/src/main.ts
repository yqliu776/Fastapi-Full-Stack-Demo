import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// 创建应用实例
const app = createApp(App)

// 创建并安装Pinia
const pinia = createPinia()
app.use(pinia)

// 安装路由
app.use(router)

// 挂载应用
app.mount('#app')
