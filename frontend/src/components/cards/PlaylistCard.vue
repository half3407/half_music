<template>
  <router-link class="pl-card" :to="{ name: 'playlist', params: { id: pl.id } }">
    <div class="cover" :style="coverStyle">
      <span class="badge">♫ {{ pl.songs_count ?? '—' }}</span>
    </div>
    <div class="name" :title="pl.name">{{ pl.name }}</div>
    <div class="sub">收藏 {{ pl.collect_num ?? 0 }}</div>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { resolveMedia, coverFallback } from '@/utils/media'

const props = defineProps({ pl: { type: Object, required: true } })

const coverStyle = computed(() => {
  const url = resolveMedia(props.pl.cover_url)
  return url
    ? { backgroundImage: `url(${url})` }
    : { backgroundImage: coverFallback(props.pl.name) }
})
</script>

<style scoped>
.pl-card {
  display: block;
  width: 100%;
}
.cover {
  position: relative;
  aspect-ratio: 1 / 1;
  border-radius: var(--radius);
  background-size: cover;
  background-position: center;
  box-shadow: var(--shadow);
  transition: transform 0.15s;
}
.pl-card:hover .cover {
  transform: translateY(-3px);
}
.badge {
  position: absolute;
  left: 10px;
  top: 10px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 9px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}
.name {
  margin-top: 10px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sub {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}
</style>
