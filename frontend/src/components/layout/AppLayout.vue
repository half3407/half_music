<template>
  <div class="layout">
    <SideBar />
    <div class="main">
      <TopBar />
      <main class="content">
        <router-view />
      </main>
    </div>
    <PlayerBar />
    <ToastHost />
  </div>
</template>

<script setup>
import SideBar from './SideBar.vue'
import TopBar from './TopBar.vue'
import PlayerBar from '@/components/player/PlayerBar.vue'
import ToastHost from '@/components/common/ToastHost.vue'
</script>

<style scoped>
.layout {
  height: 100vh;
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  grid-template-rows: 1fr var(--player-h);
  grid-template-areas:
    'side main'
    'player player';
  background: var(--bg-app);
}
.layout > :deep(.sidebar) {
  grid-area: side;
}
.main {
  grid-area: main;
  background: var(--bg-panel);
  margin: 12px 12px 0 0;
  border-radius: 18px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 28px 32px;
}
.layout > :deep(.player) {
  grid-area: player;
}
</style>
