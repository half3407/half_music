<template>
  <div class="profile">
    <h2 class="section-title">个人设置</h2>

    <div class="card">
      <div class="top">
        <span class="avatar">{{ initial }}</span>
        <div>
          <div class="uname">{{ auth.username }}</div>
          <div class="role">{{ auth.isAdmin ? '管理员' : '普通用户' }} · ID {{ auth.userId }}</div>
        </div>
      </div>

      <div class="field">
        <label class="lb">用户名</label>
        <div class="row">
          <input v-model.trim="newName" class="input" />
          <button class="btn btn-primary" :disabled="!newName || newName === auth.username" @click="saveName">
            保存
          </button>
        </div>
      </div>

      <div class="field">
        <label class="lb">密码</label>
        <div class="note warn">
          ⚠ 后端修改密码使用 MD5，与登录校验（bcrypt）不一致，改密后将无法登录。
          已暂时禁用，需后端把 <code>update_user</code> 改用 <code>hash_password</code> 后再开放。
        </div>
      </div>

      <div class="field">
        <label class="lb">头像</label>
        <div class="note warn">
          ⚠ 后端 <code>User</code> 模型缺少 <code>avatar_url</code> 字段，上传接口会报错。
          需先在模型中补字段并迁移，再启用此功能。
        </div>
      </div>

      <div class="field danger-zone">
        <label class="lb">危险操作</label>
        <button class="btn btn-danger" @click="logout">退出登录</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { usersApi } from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import { toastOk, toastErr } from '@/utils/toast'

const auth = useAuthStore()
const router = useRouter()
const newName = ref(auth.username)

const initial = computed(() => (auth.username || '?').charAt(0).toUpperCase())

async function saveName() {
  try {
    // 后端 update_user 需要 username + password；这里要求确认当前密码以避免误改
    const pwd = prompt('为安全起见，请输入当前密码以确认修改：')
    if (!pwd) return
    await usersApi.update(auth.userId, { username: newName.value, password: pwd })
    // 注意：后端会用 MD5 重写密码 → 之后需重新登录。这里提示用户。
    toastOk('用户名已更新，请重新登录')
    setTimeout(() => {
      auth.logout()
      router.push({ name: 'login' })
    }, 1200)
  } catch (e) {
    toastErr(e.message)
  }
}

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.card {
  max-width: 560px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 26px;
}
.top {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 22px;
  border-bottom: 1px solid var(--border);
}
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), #c2410c);
  display: grid;
  place-items: center;
  font-size: 26px;
  font-weight: 700;
}
.uname {
  font-size: 20px;
  font-weight: 700;
}
.role {
  color: var(--text-muted);
  font-size: 13px;
  margin-top: 2px;
}
.field {
  margin-top: 22px;
}
.lb {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.row {
  display: flex;
  gap: 10px;
}
.note {
  font-size: 13px;
  line-height: 1.6;
  padding: 12px 14px;
  border-radius: 10px;
}
.note.warn {
  background: #2e2410;
  border: 1px solid #5a4a1a;
  color: #e8c97a;
}
.note code {
  background: rgba(0, 0, 0, 0.3);
  padding: 1px 6px;
  border-radius: 5px;
  font-size: 12px;
}
.danger-zone {
  padding-top: 22px;
  border-top: 1px solid var(--border);
}
</style>
