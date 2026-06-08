<template>
  <div class="pager" v-if="page > 1 || hasNext">
    <button class="btn btn-ghost" :disabled="page <= 1" @click="$emit('change', page - 1)">
      ‹ 上一页
    </button>
    <span class="num">第 {{ page }} 页</span>
    <button class="btn btn-ghost" :disabled="!hasNext" @click="$emit('change', page + 1)">
      下一页 ›
    </button>
  </div>
</template>

<script setup>
defineProps({
  page: { type: Number, required: true },
  // 后端不返回总数：满页即认为可能有下一页
  hasNext: { type: Boolean, default: false },
})
defineEmits(['change'])
</script>

<style scoped>
.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin: 24px 0 8px;
}
.num {
  font-size: 13px;
  color: var(--text-muted);
}
</style>
