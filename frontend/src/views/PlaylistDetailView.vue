<template>
  <div class="pl-detail">
    <div v-if="loading" class="spinner"></div>

    <template v-else-if="pl">
      <header class="hero">
        <div class="cover" :style="coverStyle"></div>
        <div class="info">
          <span class="kind">歌单</span>
          <h1 class="title">{{ pl.name }}</h1>
          <p class="intro">{{ pl.introduction || '暂无简介' }}</p>
          <div class="stat">
            <span>{{ pl.songs_count }} 首歌曲</span>
            <span>·</span>
            <span>{{ pl.collect_num }} 人收藏</span>
          </div>
          <div class="actions">
            <button class="btn btn-primary" @click="playAll" :disabled="!pl.songs.length">
              ▶ 播放全部
            </button>
            <button class="btn" @click="collect">❤ 收藏</button>
            <template v-if="canManage">
              <button class="btn" @click="openEdit">✎ 编辑</button>
              <button class="btn btn-danger" @click="remove">🗑 删除</button>
            </template>
          </div>
        </div>
      </header>

      <section class="songs">
        <div class="songs-head">
          <h2 class="section-title">歌曲列表</h2>
          <button v-if="isOwner" class="btn" @click="openAdd">＋ 添加歌曲</button>
        </div>

        <div v-if="pl.songs.length" class="list">
          <div v-for="(s, i) in pl.songs" :key="s.id" class="row" @click="playFrom(i)">
            <span class="idx">{{ i + 1 }}</span>
            <div class="rcover" :style="rowCover(s)"></div>
            <div class="rmeta">
              <div class="rname">{{ s.name }}</div>
              <div class="rsinger">{{ s.singer }}</div>
            </div>
            <router-link class="rlink" :to="{ name: 'song', params: { id: s.id } }" @click.stop>
              详情
            </router-link>
            <button v-if="isOwner" class="rdel" @click.stop="removeSong(s)" title="移出歌单">✕</button>
          </div>
        </div>
        <div v-else class="empty">歌单还没有歌曲</div>
      </section>

      <!-- 编辑歌单 -->
      <Modal v-model="editOpen" title="编辑歌单">
        <label class="lb">名称</label>
        <input v-model.trim="form.playlist_name" class="input" />
        <label class="lb">简介</label>
        <textarea v-model.trim="form.playlist_introduction" class="input" rows="3"></textarea>
        <label class="lb">封面 URL</label>
        <input v-model.trim="form.playlist_cover_url" class="input" placeholder="/static/covers/..." />
        <template #footer>
          <button class="btn" @click="editOpen = false">取消</button>
          <button class="btn btn-primary" @click="saveEdit">保存</button>
        </template>
      </Modal>

      <!-- 添加歌曲 -->
      <Modal v-model="addOpen" title="添加歌曲到歌单">
        <input
          v-model.trim="addKeyword"
          class="input"
          placeholder="搜索歌曲名 / 歌手，回车搜索"
          @keyup.enter="searchAddable"
        />
        <div class="addable">
          <div v-if="addLoading" class="spinner"></div>
          <div v-for="s in addable" :key="s.id" class="arow">
            <span class="aname">{{ s.name }} <em>· {{ s.singer }}</em></span>
            <button class="btn btn-primary sm" @click="addSong(s)">添加</button>
          </div>
          <div v-if="!addLoading && !addable.length" class="empty">输入关键词搜索歌曲</div>
        </div>
      </Modal>
    </template>

    <div v-else class="empty">歌单不存在</div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { playlistsApi } from '@/api/playlists'
import { songsApi } from '@/api/songs'
import { usePlayerStore } from '@/stores/player'
import { useAuthStore } from '@/stores/auth'
import { resolveMedia, coverFallback } from '@/utils/media'
import Modal from '@/components/common/Modal.vue'
import { toastOk, toastErr } from '@/utils/toast'

const route = useRoute()
const router = useRouter()
const player = usePlayerStore()
const auth = useAuthStore()

const loading = ref(true)
const pl = ref(null)

const isOwner = computed(() => pl.value && String(pl.value.creater_id) === String(auth.userId))
const canManage = computed(() => isOwner.value || auth.isAdmin)

const coverStyle = computed(() => {
  if (!pl.value) return {}
  const url = resolveMedia(pl.value.cover_url)
  return url ? { backgroundImage: `url(${url})` } : { backgroundImage: coverFallback(pl.value.name) }
})

function rowCover(s) {
  const url = resolveMedia(s.cover_url)
  return url ? { backgroundImage: `url(${url})` } : { backgroundImage: coverFallback(s.name) }
}

async function load() {
  loading.value = true
  try {
    const res = await playlistsApi.viewSingle(route.params.id)
    pl.value = res.playlist
  } catch (e) {
    toastErr(e.message)
    pl.value = null
  } finally {
    loading.value = false
  }
}

function playAll() {
  if (pl.value.songs.length) player.playTrack(pl.value.songs[0], pl.value.songs)
}
function playFrom(i) {
  player.playTrack(pl.value.songs[i], pl.value.songs)
}

async function collect() {
  try {
    const res = await playlistsApi.collect(pl.value.id)
    pl.value.collect_num = res.current_collect_num
    toastOk('收藏成功')
  } catch (e) {
    toastErr(e.message)
  }
}

async function remove() {
  if (!confirm('确定删除该歌单？')) return
  try {
    await playlistsApi.remove(pl.value.id)
    toastOk('已删除')
    router.push({ name: 'home' })
  } catch (e) {
    toastErr(e.message)
  }
}

/* 编辑 */
const editOpen = ref(false)
const form = reactive({ playlist_name: '', playlist_introduction: '', playlist_cover_url: '' })
function openEdit() {
  form.playlist_name = pl.value.name
  form.playlist_introduction = pl.value.introduction || ''
  form.playlist_cover_url = pl.value.cover_url || ''
  editOpen.value = true
}
async function saveEdit() {
  try {
    await playlistsApi.update(pl.value.id, { ...form })
    toastOk('已保存')
    editOpen.value = false
    load()
  } catch (e) {
    toastErr(e.message)
  }
}

/* 添加歌曲 */
const addOpen = ref(false)
const addKeyword = ref('')
const addable = ref([])
const addLoading = ref(false)
function openAdd() {
  addKeyword.value = ''
  addable.value = []
  addOpen.value = true
}
async function searchAddable() {
  if (!addKeyword.value) return
  addLoading.value = true
  try {
    const res = await songsApi.search(addKeyword.value, 1, 20)
    addable.value = res?.songs || []
  } finally {
    addLoading.value = false
  }
}
async function addSong(s) {
  try {
    await songsApi.addToPlaylist(s.id, pl.value.id)
    toastOk('已添加')
    load()
  } catch (e) {
    toastErr(e.message)
  }
}
async function removeSong(s) {
  try {
    await songsApi.removeFromPlaylist(s.id, pl.value.id)
    toastOk('已移出')
    load()
  } catch (e) {
    toastErr(e.message)
  }
}

watch(() => route.params.id, load, { immediate: true })
</script>

<style scoped>
.hero {
  display: flex;
  gap: 24px;
  margin: 12px 0 28px;
}
.cover {
  width: 200px;
  height: 200px;
  border-radius: var(--radius);
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
  box-shadow: var(--shadow);
}
.info {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}
.kind {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}
.title {
  font-size: 38px;
  font-weight: 800;
  margin: 6px 0 10px;
}
.intro {
  color: var(--text-muted);
  max-width: 600px;
}
.stat {
  display: flex;
  gap: 8px;
  color: var(--text-muted);
  font-size: 13px;
  margin: 12px 0 16px;
}
.actions {
  display: flex;
  gap: 10px;
}
.songs-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.list {
  display: flex;
  flex-direction: column;
}
.row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 8px 12px;
  border-radius: 10px;
  cursor: pointer;
}
.row:hover {
  background: var(--bg-surface);
}
.idx {
  width: 22px;
  text-align: center;
  color: var(--text-dim);
  font-size: 13px;
}
.rcover {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}
.rmeta {
  flex: 1;
  overflow: hidden;
}
.rname {
  font-size: 14px;
  font-weight: 600;
}
.rsinger {
  font-size: 12px;
  color: var(--text-muted);
}
.rlink {
  font-size: 13px;
  color: var(--text-muted);
}
.rlink:hover {
  color: var(--accent);
}
.rdel {
  color: var(--text-dim);
  font-size: 14px;
  padding: 4px 8px;
}
.rdel:hover {
  color: #ff8a93;
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
.addable {
  margin-top: 14px;
  max-height: 320px;
  overflow-y: auto;
}
.arow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 4px;
  border-bottom: 1px solid var(--border);
}
.aname em {
  color: var(--text-muted);
  font-style: normal;
}
.btn.sm {
  padding: 6px 14px;
  font-size: 13px;
}
</style>
