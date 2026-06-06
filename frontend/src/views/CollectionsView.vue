<template>
  <div class="collections">
    <div class="head">
      <h2 class="section-title">我的收藏</h2>
      <button class="btn btn-primary" @click="createOpen = true">＋ 新建歌单</button>
    </div>

    <div v-if="loading" class="spinner"></div>

    <template v-else>
      <div v-if="playlists.length" class="card-grid">
        <PlaylistCard v-for="pl in playlists" :key="pl.id" :pl="pl" />
      </div>
      <div v-else class="empty">还没有收藏任何歌单，去首页逛逛吧</div>
    </template>

    <Modal v-model="createOpen" title="新建歌单">
      <label class="lb">名称</label>
      <input v-model.trim="form.playlist_name" class="input" placeholder="歌单名称" />
      <label class="lb">简介</label>
      <textarea v-model.trim="form.playlist_introduction" class="input" rows="3"></textarea>
      <label class="lb">封面 URL（可选）</label>
      <input v-model.trim="form.playlist_cover_url" class="input" placeholder="/static/covers/..." />
      <template #footer>
        <button class="btn" @click="createOpen = false">取消</button>
        <button class="btn btn-primary" :disabled="!form.playlist_name" @click="createPlaylist">
          创建
        </button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usersApi } from '@/api/users'
import { playlistsApi } from '@/api/playlists'
import { useAuthStore } from '@/stores/auth'
import PlaylistCard from '@/components/cards/PlaylistCard.vue'
import Modal from '@/components/common/Modal.vue'
import { toastOk, toastErr } from '@/utils/toast'

const auth = useAuthStore()
const router = useRouter()
const loading = ref(true)
const playlists = ref([])

const createOpen = ref(false)
const form = reactive({ playlist_name: '', playlist_introduction: '', playlist_cover_url: '' })

async function load() {
  loading.value = true
  playlists.value = []
  try {
    const res = await usersApi.viewSingle(auth.userId)
    const csv = res?.user?.collected_playlists || ''
    const ids = csv.split(',').map((x) => x.trim()).filter(Boolean)
    const results = await Promise.all(
      ids.map((id) => playlistsApi.viewSingle(id).catch(() => null))
    )
    playlists.value = results
      .filter(Boolean)
      .map((r) => r.playlist)
  } catch (e) {
    toastErr(e.message)
  } finally {
    loading.value = false
  }
}

async function createPlaylist() {
  try {
    const res = await playlistsApi.create({ ...form })
    toastOk('歌单已创建')
    createOpen.value = false
    form.playlist_name = ''
    form.playlist_introduction = ''
    form.playlist_cover_url = ''
    router.push({ name: 'playlist', params: { id: res.playlist_id } })
  } catch (e) {
    toastErr(e.message)
  }
}

onMounted(load)
</script>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.lb {
  display: block;
  font-size: 13px;
  color: var(--text-muted);
  margin: 12px 0 6px;
}
.lb:first-child {
  margin-top: 0;
}
textarea.input {
  resize: vertical;
}
</style>
