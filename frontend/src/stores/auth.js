import { defineStore } from 'pinia'
import { usersApi } from '@/api/users'

const STORAGE_KEY = 'hm_auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: '',
    userId: null,
    username: '',
    role: '',
  }),
  getters: {
    isAuthenticated: (s) => !!s.token,
    isAdmin: (s) => s.role === 'admin',
  },
  actions: {
    hydrate() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (raw) {
          const data = JSON.parse(raw)
          this.token = data.token || ''
          this.userId = data.userId ?? null
          this.username = data.username || ''
          this.role = data.role || ''
          if (this.token) localStorage.setItem('hm_token', this.token)
        }
      } catch {
        // ignore
      }
    },
    persist() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          token: this.token,
          userId: this.userId,
          username: this.username,
          role: this.role,
        })
      )
      localStorage.setItem('hm_token', this.token)
    },
    async login(username, password) {
      const res = await usersApi.login({ username, password })
      this.token = res.access_token
      this.userId = res.user_id
      this.username = res.username
      this.role = res.role
      this.persist()
      return res
    },
    async register(username, password, role = 'user') {
      return usersApi.register({ username, password, role })
    },
    logout() {
      this.token = ''
      this.userId = null
      this.username = ''
      this.role = ''
      localStorage.removeItem(STORAGE_KEY)
      localStorage.removeItem('hm_token')
    },
  },
})
