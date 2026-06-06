// 后端返回的封面/音频地址形如 "/static/covers/xxx.jpg"。
// 开发期 Vite 已把 /static 代理到后端，直接用相对路径即可。
// 若部署到不同源，可用 VITE_STATIC_BASE 指定后端 origin。
const STATIC_BASE = import.meta.env.VITE_STATIC_BASE || '/static'

// 当 STATIC_BASE 含 origin（http 开头）时，把以 /static 开头的路径替换为完整地址
export function resolveMedia(url) {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  if (STATIC_BASE.startsWith('http')) {
    // STATIC_BASE 是完整 origin（如 http://host:8000/static）
    return url.startsWith('/static') ? STATIC_BASE + url.slice('/static'.length) : STATIC_BASE + url
  }
  // 同源：直接返回（确保以 / 开头）
  return url.startsWith('/') ? url : '/' + url
}

// 简单的封面占位（无封面时用渐变色块），返回 CSS 背景
export function coverFallback(seed = '') {
  const hues = [12, 160, 220, 280, 40, 340]
  let h = 0
  for (const c of String(seed)) h += c.charCodeAt(0)
  const hue = hues[h % hues.length]
  return `linear-gradient(135deg, hsl(${hue} 55% 35%), hsl(${(hue + 40) % 360} 50% 22%))`
}
