<template>
  <Teleport to="body">
    <div class="toast-host">
      <transition-group name="toast">
        <div v-for="t in toasts" :key="t.id" class="toast" :class="t.type">
          {{ t.message }}
        </div>
      </transition-group>
    </div>
  </Teleport>
</template>

<script setup>
import { toasts } from '@/utils/toast'
</script>

<style scoped>
.toast-host {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 200;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}
.toast {
  padding: 11px 20px;
  border-radius: 999px;
  background: var(--bg-surface-2);
  border: 1px solid var(--border);
  font-size: 14px;
  box-shadow: var(--shadow);
}
.toast.ok {
  background: #0f2e28;
  border-color: #1a5a4c;
  color: #6ee7c8;
}
.toast.err {
  background: #3a1f23;
  border-color: #6b2f37;
  color: #ff9aa2;
}
.toast-enter-active,
.toast-leave-active {
  transition: all 0.25s;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
