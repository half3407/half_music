<template>
  <div class="carousel" v-if="songs.length">
    <div class="stage">
      <div
        v-for="(s, i) in songs"
        :key="s.id"
        class="slide"
        :class="positionClass(i)"
        :style="slideStyle(s)"
        @click="onSlideClick(i)"
      >
        <div class="overlay" v-if="i === active">
          <div class="info">
            <div class="title">{{ s.name }}</div>
            <div class="artist">{{ s.singer }}</div>
          </div>
          <button class="play" @click.stop="play(s)" title="播放">▶</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { resolveMedia, coverFallback } from '@/utils/media'
import { usePlayerStore } from '@/stores/player'

const props = defineProps({ songs: { type: Array, default: () => [] } })
const player = usePlayerStore()
const active = ref(0)
let timer = null

const songs = computed(() => props.songs.slice(0, 5))

function positionClass(i) {
  const n = songs.value.length
  const diff = (i - active.value + n) % n
  if (diff === 0) return 'pos-center'
  if (diff === 1) return 'pos-right'
  if (diff === n - 1) return 'pos-left'
  if (diff === 2) return 'pos-far-right'
  return 'pos-far-left'
}

function slideStyle(s) {
  const url = resolveMedia(s.cover_url)
  return url
    ? { backgroundImage: `url(${url})` }
    : { backgroundImage: coverFallback(s.name + s.singer) }
}

function onSlideClick(i) {
  if (i === active.value) play(songs.value[i])
  else active.value = i
}

function play(s) {
  player.playTrack(s, props.songs)
}

function rotate() {
  if (songs.value.length > 1) active.value = (active.value + 1) % songs.value.length
}

onMounted(() => {
  timer = setInterval(rotate, 5000)
})
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.carousel {
  margin: 8px 0 28px;
}
.stage {
  position: relative;
  height: 320px;
}
.slide {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 360px;
  height: 300px;
  border-radius: 22px;
  background-size: cover;
  background-position: center;
  transition: all 0.5s cubic-bezier(0.22, 0.61, 0.36, 1);
  cursor: pointer;
  box-shadow: var(--shadow);
}
.pos-center {
  transform: translate(-50%, -50%) scale(1);
  z-index: 5;
  opacity: 1;
}
.pos-right {
  transform: translate(calc(-50% + 300px), -50%) scale(0.82);
  z-index: 4;
  opacity: 0.85;
}
.pos-left {
  transform: translate(calc(-50% - 300px), -50%) scale(0.82);
  z-index: 4;
  opacity: 0.85;
}
.pos-far-right {
  transform: translate(calc(-50% + 540px), -50%) scale(0.66);
  z-index: 3;
  opacity: 0.5;
}
.pos-far-left {
  transform: translate(calc(-50% - 540px), -50%) scale(0.66);
  z-index: 3;
  opacity: 0.5;
}
.overlay {
  position: absolute;
  inset: 0;
  border-radius: 22px;
  background: linear-gradient(180deg, transparent 45%, rgba(0, 0, 0, 0.75));
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 24px;
}
.title {
  font-size: 26px;
  font-weight: 700;
}
.artist {
  color: #d7dbe2;
  margin-top: 4px;
}
.play {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(6px);
  font-size: 18px;
  display: grid;
  place-items: center;
}
.play:hover {
  background: var(--accent);
  color: #07211c;
}
</style>
