<template>
  <div class="flex flex-wrap gap-3 px-3 pb-3">
    <button
      v-for="s in suggestions"
      :key="s"
      @click="emit('select', s)"
      class="ui-caption bg-[--color-bg-elevated] hover:bg-[--color-primary-subtle] text-[--color-text-secondary] hover:text-[--color-text-primary] px-3 py-1.5 rounded-full transition"
    >{{ s }}</button>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{ select: [text: string] }>()

const suggestions = [
  '這個系統有什麼功能？',
  '作者有哪些技術能力與專案經驗？',
  '幫我將這份文件建立成 NotebookLM 筆記本',
]
</script>
