import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// 后端默认运行在 localhost:8000（见项目根 .env）。
// 开发期把 /api 与 /static 代理到后端，统一同源，规避 CORS 与媒体跨域。
const BACKEND = 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: BACKEND, changeOrigin: true },
      '/static': { target: BACKEND, changeOrigin: true },
    },
  },
})
