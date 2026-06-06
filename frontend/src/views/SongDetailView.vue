<template>
  <div class="song-detail">
    <div v-if="loading" class="spinner"></div>

    <template v-else-if="song">
      <header class="hero">
        <div class="cover" :style="coverStyle"></div>
        <div class="info">
          <span class="kind">歌曲</span>
          <h1 class="title">{{ song.name }}</h1>
          <div class="singer">{{ song.singer }}</div>
          <div class="meta-rows">
            <div v-if="song.album"><span>专辑</span>{{ song.album }}</div>
            <div v-if="song.lyricist"><span>作词</span>{{ song.lyricist }}</div>
            <div v-if="song.composer"><span>作曲</span>{{ song.composer }}</div>
          </div>
          <button class="btn btn-primary play" @click="play">▶ 播放</button>
        </div>
      </header>

      <section class="comments">
        <h2 class="section-title">评论</h2>

        <div class="comment-box">
          <textarea
            v-model.trim="newComment"
            class="input"
            rows="2"
            placeholder="说点什么…"
          ></textarea>
          <button class="btn btn-primary" :disabled="!newComment" @click="submitComment">发表</button>
        </div>

        <div v-if="commentsLoading" class="spinner"></div>
        <div v-else-if="comments.length" class="clist">
          <div v-for="c in comments" :key="c.id" class="citem">
            <div class="cavatar">{{ String(c.creater_id).slice(-1) }}</div>
            <div class="cbody">
              <div class="cmeta">
                <span class="cuser">用户 #{{ c.creater_id }}</span>
                <span class="ctime">{{ fmtTime(c.created_at) }}</span>
              </div>
              <div class="ctext">{{ c.content }}</div>
            </div>
            <button
              v-if="canDelete(c)"
              class="cdel"
              @click="deleteComment(c)"
              title="删除"
            >
              ✕
            </button>
          </div>
        </div>
        <div v-else class="empty">还没有评论，来抢沙发～</div>
      </section>
    </template>

    <div v-else class="empty">歌曲不存在</div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { songsApi } from '@/api/songs'
import { commentsApi } from '@/api/comments'
import { usePlayerStore } from '@/stores/player'
import { useAuthStore } from '@/stores/auth'
import { resolveMedia, coverFallback } from '@/utils/media'
import { toastOk, toastErr } from '@/utils/toast'

const route = useRoute()
const player = usePlayerStore()
const auth = useAuthStore()

const loading = ref(true)
const song = ref(null)
const comments = ref([])
const commentsLoading = ref(false)
const newComment = ref('')

const coverStyle = computed(() => {
  if (!song.value) return {}
  const url = resolveMedia(song.value.cover_url)
  return url ? { backgroundImage: `url(${url})` } : { backgroundImage: coverFallback(song.value.name) }
})

function canDelete(c) {
  return auth.isAdmin || String(c.creater_id) === String(auth.userId)
}

function fmtTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN', { hour12: false })
}

async function loadSong() {
  loading.value = true
  try {
    const res = await songsApi.viewSingle(route.params.id)
    song.value = res.song
  } catch (e) {
    toastErr(e.message)
    song.value = null
  } finally {
    loading.value = false
  }
}

// 列表接口只返回 id+时间，需逐条取详情
async function loadComments() {
  commentsLoading.value = true
  try {
    const list = await commentsApi.viewAll(route.params.id, 1, 30)
    const details = await Promise.all(
      (list || []).map((c) => commentsApi.viewOne(c.comment_id).catch(() => null))
    )
    comments.value = details
      .filter(Boolean)
      .map((d) => ({
        id: d.comment_id,
        content: d.content,
        creater_id: d.creater_id,
        created_at: d.created_at,
      }))
  } finally {
    commentsLoading.value = false
  }
}

function play() {
  player.playTrack(
    {
      id: song.value.id,
      name: song.value.name,
      singer: song.value.singer,
      url: song.value.url,
      cover_url: song.value.cover_url,
    },
    []
  )
}

async function submitComment() {
  try {
    await commentsApi.create({ content: newComment.value, song_id: Number(route.params.id) })
    newComment.value = ''
    toastOk('评论成功')
    loadComments()
  } catch (e) {
    toastErr(e.message)
  }
}

async function deleteComment(c) {
  try {
    await commentsApi.remove(c.id)
    toastOk('已删除')
    comments.value = comments.value.filter((x) => x.id !== c.id)
  } catch (e) {
    toastErr(e.message)
  }
}

watch(
  () => route.params.id,
  () => {
    loadSong()
    loadComments()
  },
  { immediate: true }
)
</script>

<style scoped>
.hero {
  display: flex;
  gap: 24px;
  margin: 12px 0 32px;
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
  margin: 6px 0 6px;
}
.singer {
  font-size: 16px;
  color: var(--text-muted);
}
.meta-rows {
  margin: 14px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: var(--text-muted);
}
.meta-rows span {
  display: inline-block;
  width: 48px;
  color: var(--text-dim);
}
.play {
  align-self: flex-start;
}
.comment-box {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 22px;
}
.comment-box textarea {
  flex: 1;
  resize: vertical;
}
.clist {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.citem {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
}
.citem:hover {
  background: var(--bg-surface);
}
.cavatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--bg-surface-2);
  display: grid;
  place-items: center;
  font-weight: 700;
  flex-shrink: 0;
}
.cbody {
  flex: 1;
}
.cmeta {
  display: flex;
  gap: 10px;
  align-items: baseline;
}
.cuser {
  font-size: 13px;
  font-weight: 600;
}
.ctime {
  font-size: 12px;
  color: var(--text-dim);
}
.ctext {
  margin-top: 4px;
  font-size: 14px;
  color: var(--text);
}
.cdel {
  color: var(--text-dim);
  align-self: center;
}
.cdel:hover {
  color: #ff8a93;
}
</style>
