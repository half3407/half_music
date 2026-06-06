import axios from 'axios'

// 统一 axios 实例。注意：后端所有接口均为 POST。
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api/v1',
  timeout: 20000,
})

// 请求拦截：注入 Bearer token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('hm_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：401 清登录态并跳登录页；统一抛出后端 detail 文案
let onUnauthorized = null
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn
}

client.interceptors.response.use(
  (resp) => resp.data,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    if (status === 401 && onUnauthorized) {
      onUnauthorized()
    }
    const message =
      (Array.isArray(detail) ? detail.map((d) => d.msg).join('; ') : detail) ||
      error.message ||
      '请求失败'
    return Promise.reject(new Error(message))
  }
)

export default client
