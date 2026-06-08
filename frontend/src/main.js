import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import './styles/theme.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// 从 localStorage 复水登录态（须在挂载路由守卫前）
useAuthStore().hydrate()

app.use(router)
app.mount('#app')
