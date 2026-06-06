<template>
  <div class="home">
    <div v-if="loading" class="spinner"></div>

    <template v-else>
      <FeaturedCarousel :songs="songs" />

      <section v-if="playlists.length" class="block">
        <div class="head">
          <h2 class="section-title">热门歌单</h2>
          <router-link class="more" :to="{ name: 'collections' }">我的收藏 ›</router-link>
        </div>
        <div class="h-scroll">
          <div v-for="pl in playlists" :key="pl.id" class="pl-slot">
            <PlaylistCard :pl="pl" />
          </div>
        </div>
      </section>

      <section class="block">
        <div class="head">
          <h2 class="section-title">最新歌曲</h2>
        </div>
        <div v-if="songs.length" class="card-grid">
          <SongCard v-for="s in songs" :key="s.id" :song="s" :queue="songs" />
        </div>
        <div v-else class="empty">还没有歌曲，去“歌曲管理”上传第一首吧</div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { songsApi } from '@/api/songs'
import { playlistsApi } from '@/api/playlists'
import FeaturedCarousel from '@/components/cards/FeaturedCarousel.vue'
import SongCard from '@/components/cards/SongCard.vue'
import PlaylistCard from '@/components/cards/PlaylistCard.vue'

const loading = ref(true)
const songs = ref([])
const playlists = ref([])

onMounted(async () => {
  try {
    const [songRes, plRes] = await Promise.all([
      songsApi.viewAll(1, 18),
      playlistsApi.viewAll(1, 10),
    ])
    songs.value = songRes?.songs || []
    playlists.value = (plRes || []).map((r) => r.playlist)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.block {
  margin-bottom: 32px;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.more {
  font-size: 13px;
  color: var(--text-muted);
}
.more:hover {
  color: var(--accent);
}
.pl-slot {
  width: 168px;
  flex-shrink: 0;
}
</style>
