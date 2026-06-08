<template>
  <div class="admin">
    <div class="head">
      <h2 class="section-title">歌曲管理</h2>
      <button class="btn btn-primary" @click="openCreate">＋ 新建歌曲</button>
    </div>

    <div v-if="loading" class="spinner"></div>

    <template v-else>
      <div v-if="songs.length" class="list">
        <div v-for="s in songs" :key="s.id" class="row">
          <div class="rcover" :style="rowCover(s)"></div>
          <div class="rmeta">
            <div class="rname">{{ s.name }}</div>
            <div class="rsinger">{{ s.singer }}</div>
          </div>
          <span class="audio-flag" :class="{ ok: s.url }">{{ s.url ? '有音频' : '无音频' }}</span>
          <button class="btn sm" @click="openEdit(s)">编辑</button>
          <button class="btn btn-danger sm" @click="remove(s)">删除</button>
        </div>
      </div>
      <div v-else class="empty">还没有歌曲，点击右上角新建</div>
      <Pager :page="page" :has-next="songs.length >= pageSize" @change="go" />
    </template>

    <Modal v-model="formOpen" :title="editingId ? '编辑歌曲' : '新建歌曲'">
      <label class="lb">歌曲名 *</label>
      <input v-model.trim="form.song_name" class="input" />

      <label class="lb">歌手 *</label>
      <input v-model.trim="form.song_singer" class="input" />

      <div class="two">
        <div>
          <label class="lb">作词</label>
          <input v-model.trim="form.song_lyricist" class="input" />
        </div>
        <div>
          <label class="lb">作曲</label>
          <input v-model.trim="form.song_composer" class="input" />
        </div>
      </div>

      <label class="lb">专辑</label>
      <input v-model.trim="form.song_album" class="input" />

      <label class="lb">封面</label>
      <div class="upload">
        <input v-model.trim="form.song_cover_url" class="input" placeholder="/static/covers/..." />
        <label class="btn sm file-btn">
          {{ coverUploading ? '上传中…' : '上传图片' }}
          <input type="file" accept="image/*" hidden @change="uploadCover" />
        </label>
      </div>

      <label class="lb">音频</label>
      <div class="upload">
        <input v-model.trim="form.song_url" class="input" placeholder="/static/songs/..." />
        <label class="btn sm file-btn">
          {{ songUploading ? '上传中…' : '上传音频' }}
          <input type="file" accept="audio/*" hidden @change="uploadSong" />
        </label>
      </div>

      <template #footer>
        <button class="btn" @click="formOpen = false">取消</button>
        <button class="btn btn-primary" :disabled="!valid" @click="save">保存</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { songsApi } from '@/api/songs'
import { filesApi } from '@/api/files'
import { resolveMedia, coverFallback } from '@/utils/media'
import Modal from '@/components/common/Modal.vue'
import Pager from '@/components/common/Pager.vue'
import { toastOk, toastErr } from '@/utils/toast'

const pageSize = 12
const loading = ref(true)
const songs = ref([])
const page = ref(1)

const formOpen = ref(false)
const editingId = ref(null)
const form = reactive({
  song_name: '',
  song_singer: '',
  song_lyricist: '',
  song_composer: '',
  song_album: '',
  song_cover_url: '',
  song_url: '',
})
const coverUploading = ref(false)
const songUploading = ref(false)

const valid = computed(() => form.song_name && form.song_singer)

function rowCover(s) {
  const url = resolveMedia(s.cover_url)
  return url ? { backgroundImage: `url(${url})` } : { backgroundImage: coverFallback(s.name) }
}

async function load() {
  loading.value = true
  try {
    const res = await songsApi.viewAll(page.value, pageSize)
    songs.value = res?.songs || []
  } finally {
    loading.value = false
  }
}
function go(p) {
  page.value = p
  load()
}

function resetForm() {
  Object.keys(form).forEach((k) => (form[k] = ''))
}
function openCreate() {
  editingId.value = null
  resetForm()
  formOpen.value = true
}
async function openEdit(s) {
  editingId.value = s.id
  resetForm()
  // 列表数据有限，拉详情补全
  try {
    const res = await songsApi.viewSingle(s.id)
    const d = res.song
    form.song_name = d.name
    form.song_singer = d.singer
    form.song_lyricist = d.lyricist || ''
    form.song_composer = d.composer || ''
    form.song_album = d.album || ''
    form.song_cover_url = d.cover_url || ''
    form.song_url = d.url || ''
  } catch (e) {
    toastErr(e.message)
  }
  formOpen.value = true
}

async function uploadCover(e) {
  const file = e.target.files[0]
  if (!file) return
  coverUploading.value = true
  try {
    const res = await filesApi.uploadCover(file)
    form.song_cover_url = res.data.file_url
    toastOk('封面已上传')
  } catch (err) {
    toastErr(err.message)
  } finally {
    coverUploading.value = false
    e.target.value = ''
  }
}

async function uploadSong(e) {
  const file = e.target.files[0]
  if (!file) return
  songUploading.value = true
  try {
    const res = await filesApi.uploadSong(file)
    form.song_url = res.data.file_url
    toastOk('音频已上传')
  } catch (err) {
    toastErr(err.message)
  } finally {
    songUploading.value = false
    e.target.value = ''
  }
}

async function save() {
  try {
    if (editingId.value) {
      await songsApi.update(editingId.value, { ...form })
      toastOk('已更新')
    } else {
      await songsApi.create({ ...form })
      toastOk('已创建')
    }
    formOpen.value = false
    load()
  } catch (e) {
    toastErr(e.message)
  }
}

async function remove(s) {
  if (!confirm(`删除歌曲「${s.name}」？`)) return
  try {
    await songsApi.remove(s.id)
    toastOk('已删除')
    load()
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
}
.list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 12px;
  border-radius: 10px;
}
.row:hover {
  background: var(--bg-surface);
}
.rcover {
  width: 46px;
  height: 46px;
  border-radius: 8px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}
.rmeta {
  flex: 1;
}
.rname {
  font-size: 14px;
  font-weight: 600;
}
.rsinger {
  font-size: 12px;
  color: var(--text-muted);
}
.audio-flag {
  font-size: 12px;
  color: var(--text-dim);
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--bg-surface-2);
}
.audio-flag.ok {
  color: var(--accent);
}
.btn.sm {
  padding: 7px 14px;
  font-size: 13px;
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
.two {
  display: flex;
  gap: 12px;
}
.two > div {
  flex: 1;
}
.upload {
  display: flex;
  gap: 8px;
}
.file-btn {
  white-space: nowrap;
  cursor: pointer;
}
</style>
