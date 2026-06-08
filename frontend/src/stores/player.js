import { defineStore } from 'pinia'

// 播放队列里的曲目统一形如：
// { id, name, singer, url, cover_url }
function normalize(track) {
  if (!track) return null
  return {
    id: track.id,
    name: track.name || track.song_name || '未知歌曲',
    singer: track.singer || track.song_singer || '未知歌手',
    url: track.url || track.song_url || '',
    cover_url: track.cover_url || track.song_cover_url || '',
  }
}

export const usePlayerStore = defineStore('player', {
  state: () => ({
    queue: [],
    index: -1,
    isPlaying: false,
    progress: 0, // 当前秒
    duration: 0, // 总秒
    volume: 0.8,
    muted: false,
    shuffle: false,
    repeat: 'off', // off | one | all
  }),
  getters: {
    current: (s) => (s.index >= 0 ? s.queue[s.index] : null),
    hasTrack: (s) => s.index >= 0 && !!s.queue[s.index],
  },
  actions: {
    // 播放单曲，并把所在列表设为队列
    playTrack(track, list) {
      const queue = (list && list.length ? list : [track]).map(normalize)
      const t = normalize(track)
      const idx = queue.findIndex((x) => x.id === t.id)
      this.queue = queue
      this.index = idx >= 0 ? idx : 0
      this.isPlaying = true
    },
    toggle() {
      if (this.hasTrack) this.isPlaying = !this.isPlaying
    },
    setPlaying(v) {
      this.isPlaying = v
    },
    next() {
      if (!this.queue.length) return
      if (this.repeat === 'one') {
        this.progress = 0
        this.isPlaying = true
        return
      }
      if (this.shuffle) {
        this.index = Math.floor(Math.random() * this.queue.length)
      } else if (this.index < this.queue.length - 1) {
        this.index++
      } else if (this.repeat === 'all') {
        this.index = 0
      } else {
        this.isPlaying = false
        return
      }
      this.isPlaying = true
    },
    prev() {
      if (!this.queue.length) return
      if (this.progress > 3) {
        this.progress = 0
        return
      }
      if (this.index > 0) this.index--
      else this.index = this.queue.length - 1
      this.isPlaying = true
    },
    setProgress(v) {
      this.progress = v
    },
    setDuration(v) {
      this.duration = v
    },
    setVolume(v) {
      this.volume = Math.min(1, Math.max(0, v))
      if (this.volume > 0) this.muted = false
    },
    toggleMute() {
      this.muted = !this.muted
    },
    toggleShuffle() {
      this.shuffle = !this.shuffle
    },
    cycleRepeat() {
      this.repeat = this.repeat === 'off' ? 'all' : this.repeat === 'all' ? 'one' : 'off'
    },
  },
})
