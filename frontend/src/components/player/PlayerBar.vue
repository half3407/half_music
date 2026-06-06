<template>
  <footer class="player">
    <!-- 当前曲目信息 -->
    <div class="now">
      <template v-if="cur">
        <div class="cover" :style="coverStyle"></div>
        <div class="meta">
          <router-link class="name" :to="{ name: 'song', params: { id: cur.id } }">
            {{ cur.name }}
          </router-link>
          <div class="singer">{{ cur.singer }}</div>
        </div>
      </template>
      <div v-else class="meta">
        <div class="name muted">未在播放</div>
        <div class="singer">选择一首歌曲开始</div>
      </div>
    </div>

    <!-- 控制区 -->
    <div class="center">
      <div class="controls">
        <button class="ctl" :class="{ on: player.shuffle }" @click="player.toggleShuffle()" title="随机">🔀</button>
        <button class="ctl" @click="player.prev()" title="上一首">⏮</button>
        <button class="play" @click="player.toggle()" :title="player.isPlaying ? '暂停' : '播放'">
          {{ player.isPlaying ? '❚❚' : '▶' }}
        </button>
        <button class="ctl" @click="player.next()" title="下一首">⏭</button>
        <button class="ctl" :class="{ on: player.repeat !== 'off' }" @click="player.cycleRepeat()" title="循环">
          {{ player.repeat === 'one' ? '🔂' : '🔁' }}
        </button>
      </div>
      <div class="progress">
        <span class="t">{{ fmt(player.progress) }}</span>
        <input
          class="bar"
          type="range"
          min="0"
          :max="player.duration || 0"
          step="0.1"
          :value="player.progress"
          @input="onSeek"
        />
        <span class="t">{{ fmt(player.duration) }}</span>
      </div>
    </div>

    <!-- 音量 -->
    <div class="volume">
      <button class="ctl" @click="player.toggleMute()">{{ player.muted || player.volume === 0 ? '🔇' : '🔊' }}</button>
      <input
        class="vol"
        type="range"
        min="0"
        max="1"
        step="0.01"
        :value="player.muted ? 0 : player.volume"
        @input="onVol"
      />
    </div>

    <audio
      ref="audioEl"
      @timeupdate="onTime"
      @loadedmetadata="onMeta"
      @ended="player.next()"
      @play="player.setPlaying(true)"
      @pause="player.setPlaying(false)"
    ></audio>
  </footer>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { resolveMedia, coverFallback } from '@/utils/media'
import { toastErr } from '@/utils/toast'

const player = usePlayerStore()
const audioEl = ref(null)
const cur = computed(() => player.current)

const coverStyle = computed(() => {
  if (!cur.value) return {}
  const url = resolveMedia(cur.value.cover_url)
  return url
    ? { backgroundImage: `url(${url})` }
    : { backgroundImage: coverFallback(cur.value.name) }
})

function fmt(s) {
  if (!s || isNaN(s)) return '0:00'
  const m = Math.floor(s / 60)
  const ss = Math.floor(s % 60)
  return `${m}:${ss.toString().padStart(2, '0')}`
}

// 切歌：换 src
watch(
  () => cur.value && cur.value.id,
  () => {
    const a = audioEl.value
    if (!a || !cur.value) return
    const src = resolveMedia(cur.value.url)
    if (!src) {
      toastErr('该歌曲没有可播放的音频文件')
      return
    }
    a.src = src
    a.load()
    if (player.isPlaying) a.play().catch(() => {})
  }
)

// 播放/暂停
watch(
  () => player.isPlaying,
  (v) => {
    const a = audioEl.value
    if (!a || !cur.value) return
    if (v) a.play().catch((e) => toastErr('无法播放：' + e.message))
    else a.pause()
  }
)

// 音量 / 静音
watch(
  [() => player.volume, () => player.muted],
  () => {
    const a = audioEl.value
    if (a) a.volume = player.muted ? 0 : player.volume
  }
)

function onTime() {
  player.setProgress(audioEl.value.currentTime)
}
function onMeta() {
  player.setDuration(audioEl.value.duration)
  audioEl.value.volume = player.muted ? 0 : player.volume
}
function onSeek(e) {
  const v = Number(e.target.value)
  audioEl.value.currentTime = v
  player.setProgress(v)
}
function onVol(e) {
  player.setVolume(Number(e.target.value))
}

onMounted(() => {
  if (audioEl.value) audioEl.value.volume = player.volume
})
</script>

<style scoped>
.player {
  height: var(--player-h);
  flex-shrink: 0;
  background: var(--bg-panel);
  border-top: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 0 24px;
}
.now {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 240px;
  flex-shrink: 0;
}
.cover {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}
.meta {
  overflow: hidden;
}
.name {
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}
.name:hover {
  color: var(--accent);
}
.singer {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  max-width: 620px;
  margin: 0 auto;
}
.controls {
  display: flex;
  align-items: center;
  gap: 18px;
}
.ctl {
  color: var(--text-muted);
  font-size: 15px;
}
.ctl:hover {
  color: var(--text);
}
.ctl.on {
  color: var(--accent);
}
.play {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--text);
  color: var(--bg-panel);
  font-size: 14px;
  display: grid;
  place-items: center;
}
.play:hover {
  background: var(--accent);
}
.progress {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}
.t {
  font-size: 11px;
  color: var(--text-dim);
  width: 34px;
  text-align: center;
}
.bar {
  flex: 1;
}
.volume {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 140px;
  flex-shrink: 0;
  justify-content: flex-end;
}
.vol {
  width: 90px;
}
input[type='range'] {
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  background: var(--bg-surface-2);
  border-radius: 4px;
  outline: none;
  cursor: pointer;
}
input[type='range']::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--accent);
}
</style>
