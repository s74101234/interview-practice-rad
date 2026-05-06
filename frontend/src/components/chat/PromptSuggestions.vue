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
  '請問你能做什麼？',
  '請介紹這份文件',
  '請將目前上傳的文件整理成簡報',
]
</script>
