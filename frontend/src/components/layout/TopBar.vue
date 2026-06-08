<template>
  <header class="topbar">
    <form class="search" @submit.prevent="doSearch">
      <span class="ico">🔍</span>
      <input
        v-model="keyword"
        class="search-input"
        type="text"
        placeholder="搜索歌曲、歌单…"
      />
    </form>

    <div class="right">
      <router-link class="profile" :to="{ name: 'profile' }">
        <span class="avatar">{{ initial }}</span>
        <span class="info">
          <span class="uname">{{ auth.username }}</span>
          <span class="role">{{ auth.isAdmin ? '管理员' : '会员' }}</span>
        </span>
      </router-link>
      <router-link class="circle" :to="{ name: 'collections' }" title="我的收藏">❤</router-link>
      <router-link class="circle" :to="{ name: 'profile' }" title="设置">⚙</router-link>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const keyword = ref('')

const initial = computed(() => (auth.username || '?').charAt(0).toUpperCase())

function doSearch() {
  const q = keyword.value.trim()
  if (!q) return
  router.push({ name: 'search', query: { q } })
}
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 18px 28px;
}
.search {
  flex: 1;
  max-width: 520px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0 18px;
}
.search:focus-within {
  border-color: var(--accent);
}
.ico {
  color: var(--text-dim);
}
.search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  padding: 13px 0;
  font-size: 14px;
}
.right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}
.profile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 14px 5px 5px;
  border-radius: 999px;
  transition: background 0.15s;
}
.profile:hover {
  background: var(--bg-surface);
}
.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), #c2410c);
  display: grid;
  place-items: center;
  font-weight: 700;
}
.info {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}
.uname {
  font-size: 14px;
  font-weight: 700;
}
.role {
  font-size: 11px;
  color: var(--accent);
}
.circle {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--bg-surface);
  display: grid;
  place-items: center;
  color: var(--text-muted);
  font-size: 16px;
  transition: background 0.15s, color 0.15s;
}
.circle:hover {
  background: var(--bg-hover);
  color: var(--text);
}
</style>
