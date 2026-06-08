<template>
  <div class="search-view">
    <h2 class="section-title">搜索结果：“{{ q }}”</h2>

    <div v-if="loading" class="spinner"></div>

    <template v-else>
      <section class="block">
        <h3 class="sub-title">歌曲</h3>
        <div v-if="songs.length" class="card-grid">
          <SongCard v-for="s in songs" :key="s.id" :song="s" :queue="songs" />
        </div>
        <div v-else class="empty">没有匹配的歌曲</div>
        <Pager :page="songPage" :has-next="songs.length >= pageSize" @change="goSong" />
      </section>

      <section class="block">
        <h3 class="sub-title">歌单</h3>
        <div v-if="playlists.length" class="card-grid">
          <PlaylistCard v-for="pl in playlists" :key="pl.id" :pl="pl" />
        </div>
        <div v-else class="empty">没有匹配的歌单</div>
        <Pager :page="plPage" :has-next="playlists.length >= pageSize" @change="goPl" />
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { songsApi } from '@/api/songs'
import { playlistsApi } from '@/api/playlists'
import SongCard from '@/components/cards/SongCard.vue'
import PlaylistCard from '@/components/cards/PlaylistCard.vue'
import Pager from '@/components/common/Pager.vue'

const route = useRoute()
const pageSize = 12

const q = ref(route.query.q || '')
const songs = ref([])
const playlists = ref([])
const songPage = ref(1)
const plPage = ref(1)
const loading = ref(false)

async function loadSongs() {
  const res = await songsApi.search(q.value, songPage.value, pageSize)
  songs.value = res?.songs || []
}
async function loadPlaylists() {
  const res = await playlistsApi.search(q.value, plPage.value, pageSize)
  playlists.value = (res || []).map((r) => r.playlist)
}

async function loadAll() {
  if (!q.value) return
  loading.value = true
  songPage.value = 1
  plPage.value = 1
  try {
    await Promise.all([loadSongs(), loadPlaylists()])
  } finally {
    loading.value = false
  }
}

function goSong(p) {
  songPage.value = p
  loadSongs()
}
function goPl(p) {
  plPage.value = p
  loadPlaylists()
}

watch(
  () => route.query.q,
  (v) => {
    q.value = v || ''
    loadAll()
  },
  { immediate: true }
)
</script>

<style scoped>
.block {
  margin-bottom: 32px;
}
.sub-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 14px;
  color: var(--text-muted);
}
</style>
