<template>
  <aside class="sidebar">
    <div class="brand">
      <span class="logo">♫</span>
      <span class="name">Rhythmo<span class="accent">Tune</span></span>
    </div>

    <nav class="nav">
      <router-link class="item" :to="{ name: 'home' }">
        <span class="ico">🏠</span> 首页
      </router-link>
      <router-link class="item" :to="{ name: 'collections' }">
        <span class="ico">❤️</span> 我的收藏
      </router-link>

      <div class="group">
        <button class="item group-head" @click="plOpen = !plOpen">
          <span class="ico">🎵</span> 热门歌单
          <span class="chev" :class="{ open: plOpen }">⌃</span>
        </button>
        <div class="sub" v-show="plOpen">
          <div v-if="loadingPl" class="sub-hint">加载中…</div>
          <router-link
            v-for="pl in playlists"
            :key="pl.id"
            class="sub-item"
            :to="{ name: 'playlist', params: { id: pl.id } }"
          >
            <span class="dot" :style="{ background: dot(pl.name) }"></span>
            <span class="txt">{{ pl.name }}</span>
          </router-link>
          <div v-if="!loadingPl && !playlists.length" class="sub-hint">暂无歌单</div>
        </div>
      </div>

      <router-link v-if="auth.isAdmin" class="item" :to="{ name: 'admin-songs' }">
        <span class="ico">🛠️</span> 歌曲管理
      </router-link>
    </nav>

    <button class="item logout" @click="logout">
      <span class="ico">⎋</span> 退出登录
    </button>
  </aside>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { playlistsApi } from '@/api/playlists'
import { coverFallback } from '@/utils/media'

const auth = useAuthStore()
const router = useRouter()
const plOpen = ref(true)
const playlists = ref([])
const loadingPl = ref(false)

function dot(seed) {
  return coverFallback(seed)
}

async function loadPlaylists() {
  loadingPl.value = true
  try {
    const res = await playlistsApi.viewAll(1, 6)
    playlists.value = (res || []).map((r) => r.playlist)
  } catch {
    playlists.value = []
  } finally {
    loadingPl.value = false
  }
}

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}

onMounted(loadPlaylists)
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-w);
  flex-shrink: 0;
  background: var(--bg-panel);
  display: flex;
  flex-direction: column;
  padding: 22px 16px;
  height: 100%;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px 26px;
}
.logo {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background: var(--brand);
  color: #fff;
  display: grid;
  place-items: center;
  font-size: 18px;
}
.name {
  font-size: 19px;
  font-weight: 800;
}
.accent {
  color: var(--brand);
}
.nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}
.item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-muted);
  text-align: left;
  transition: background 0.15s, color 0.15s;
}
.item:hover {
  background: var(--bg-surface);
  color: var(--text);
}
.item.router-link-exact-active {
  background: var(--bg-surface-2);
  color: var(--text);
}
.ico {
  width: 20px;
  text-align: center;
}
.group-head {
  position: relative;
}
.chev {
  margin-left: auto;
  transition: transform 0.2s;
  display: inline-block;
}
.chev.open {
  transform: rotate(180deg);
}
.sub {
  margin: 2px 0 4px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.sub-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 10px;
  font-size: 13px;
  color: var(--text-muted);
}
.sub-item:hover {
  background: var(--bg-surface);
  color: var(--text);
}
.dot {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  flex-shrink: 0;
}
.txt {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sub-hint {
  font-size: 12px;
  color: var(--text-dim);
  padding: 6px 12px;
}
.logout {
  margin-top: 8px;
  color: var(--text-muted);
}
</style>
