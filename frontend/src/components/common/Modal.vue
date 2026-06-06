<template>
  <Teleport to="body">
    <transition name="fade">
      <div v-if="modelValue" class="mask" @click.self="close">
        <div class="dialog">
          <div class="head">
            <h3>{{ title }}</h3>
            <button class="x" @click="close">✕</button>
          </div>
          <div class="body">
            <slot />
          </div>
          <div class="foot" v-if="$slots.footer">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])
function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: grid;
  place-items: center;
  z-index: 100;
  padding: 20px;
}
.dialog {
  width: 100%;
  max-width: 440px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 20px;
  border-bottom: 1px solid var(--border);
}
.head h3 {
  font-size: 17px;
}
.x {
  color: var(--text-muted);
  font-size: 16px;
}
.x:hover {
  color: var(--text);
}
.body {
  padding: 20px;
  overflow-y: auto;
}
.foot {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.18s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
