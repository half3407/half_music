import { reactive } from 'vue'

// 极简全局提示。被 ToastHost 组件渲染。
export const toasts = reactive([])
let seq = 0

export function toast(message, type = 'info') {
  const id = ++seq
  toasts.push({ id, message, type })
  setTimeout(() => {
    const i = toasts.findIndex((t) => t.id === id)
    if (i >= 0) toasts.splice(i, 1)
  }, 2800)
}

export const toastOk = (m) => toast(m, 'ok')
export const toastErr = (m) => toast(m, 'err')
