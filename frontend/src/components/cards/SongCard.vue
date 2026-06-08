<template>
  <div class="song-card" @click="onPlay">
    <div class="cover" :style="coverStyle">
      <button class="play-fab" title="播放">▶</button>
    </div>
    <div class="meta">
      <div class="name" :title="song.name">{{ song.name }}</div>
      <div class="singer" :title="song.singer">{{ song.singer }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { resolveMedia, coverFallback } from '@/utils/media'
import { usePlayerStore } from '@/stores/player'

const props = defineProps({
  song: { type: Object, required: true },
  // 点击时把整个列表设为播放队列
  queue: { type: Array, default: () => [] },
})

const player = usePlayerStore()

const coverStyle = computed(() => {
  const url = resolveMedia(props.song.cover_url)
  return url
    ? { backgroundImage: `url(${url})` }
    : { backgroundImage: coverFallback(props.song.name + props.song.singer) }
})

function onPlay() {
  player.playTrack(props.song, props.queue)
}
</script>

<style scoped>
.song-card {
  cursor: pointer;
  width: 100%;
}
.cover {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: var(--radius);
  background-size: cover;
  background-position: center;
  overflow: hidden;
  box-shadow: var(--shadow);
}
.cover::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 55%, rgba(0, 0, 0, 0.55));
  opacity: 0;
  transition: opacity 0.2s;
}
.song-card:hover .cover::after {
  opacity: 1;
}
.play-fab {
  position: absolute;
  right: 10px;
  bottom: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent);
  color: #07211c;
  font-size: 14px;
  display: grid;
  place-items: center;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.2s, transform 0.2s;
  z-index: 1;
}
.song-card:hover .play-fab {
  opacity: 1;
  transform: translateY(0);
}
.meta {
  margin-top: 10px;
}
.name {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.singer {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}
</style>
