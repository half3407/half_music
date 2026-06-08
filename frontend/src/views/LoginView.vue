<template>
  <div class="auth">
    <div class="card">
      <div class="brand">
        <span class="logo">♫</span>
        <span class="name">Rhythmo<span class="accent">Tune</span></span>
      </div>
      <p class="tip">{{ mode === 'login' ? '登录以继续聆听' : '创建一个新账号' }}</p>

      <div class="tabs">
        <button :class="{ active: mode === 'login' }" @click="mode = 'login'">登录</button>
        <button :class="{ active: mode === 'register' }" @click="mode = 'register'">注册</button>
      </div>

      <form @submit.prevent="submit">
        <label>用户名</label>
        <input v-model.trim="username" class="input" placeholder="请输入用户名" autocomplete="username" />

        <label>密码</label>
        <input
          v-model="password"
          class="input"
          type="password"
          placeholder="请输入密码"
          autocomplete="current-password"
        />

        <template v-if="mode === 'register'">
          <label>账号类型</label>
          <select v-model="role" class="input">
            <option value="user">普通用户</option>
            <option value="admin">管理员</option>
          </select>
        </template>

        <button class="btn btn-primary submit" type="submit" :disabled="loading">
          {{ loading ? '请稍候…' : mode === 'login' ? '登录' : '注册' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { toastOk, toastErr } from '@/utils/toast'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const mode = ref('login')
const username = ref('')
const password = ref('')
const role = ref('user')
const loading = ref(false)

async function submit() {
  if (!username.value || !password.value) {
    toastErr('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    if (mode.value === 'register') {
      await auth.register(username.value, password.value, role.value)
      toastOk('注册成功，正在登录…')
    }
    await auth.login(username.value, password.value)
    toastOk('登录成功')
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    toastErr(e.message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: radial-gradient(1200px 600px at 70% -10%, #20323a, var(--bg-app));
  padding: 20px;
}
.card {
  width: 100%;
  max-width: 400px;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 36px 32px;
  box-shadow: var(--shadow);
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}
.logo {
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: var(--brand);
  display: grid;
  place-items: center;
  font-size: 18px;
}
.name {
  font-size: 22px;
  font-weight: 800;
}
.accent {
  color: var(--brand);
}
.tip {
  text-align: center;
  color: var(--text-muted);
  margin: 10px 0 22px;
  font-size: 14px;
}
.tabs {
  display: flex;
  background: var(--bg-surface);
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 22px;
}
.tabs button {
  flex: 1;
  padding: 10px;
  border-radius: 9px;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 14px;
}
.tabs button.active {
  background: var(--bg-surface-2);
  color: var(--text);
}
label {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  margin: 14px 0 6px;
}
.submit {
  width: 100%;
  margin-top: 24px;
  padding: 13px;
}
</style>
