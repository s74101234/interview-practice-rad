<template>
  <div
    class="rounded-xl border overflow-hidden"
    :class="isDragging ? 'border-[--color-border-focus]' : 'border-[--color-border]'"
  >
    <div class="px-4 py-3 bg-[--color-bg-elevated] border-b border-[--color-border]">
      <h3 class="text-sm font-medium text-[--color-text-primary]">上傳文件</h3>
    </div>
    <div class="p-4 bg-[--color-bg-surface]">
      <div
        class="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors"
        :class="isDragging ? 'border-[--color-border-focus] bg-[--color-primary-subtle]' : 'border-[--color-border]'"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <input ref="fileInput" type="file" accept=".pdf,.pptx,.ppt" class="hidden" @change="onSelect" />
        <template v-if="uploadStore.isProcessing">
          <p class="text-sm text-[--color-text-muted]">處理中...</p>
        </template>
        <template v-else-if="uploadStore.isReady">
          <p class="text-sm text-[--color-text-primary] font-medium">{{ uploadStore.filename }}</p>
          <p class="text-xs text-[--color-text-muted] mt-1">點擊或拖曳以重新上傳</p>
        </template>
        <template v-else>
          <p class="text-sm text-[--color-text-secondary]">拖曳或點擊上傳 PDF / PPTX</p>
        </template>
      </div>
      <p v-if="uploadStore.error" class="mt-2 text-xs text-[--color-danger]">{{ uploadStore.error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUploadStore } from '../stores/upload'

const uploadStore = useUploadStore()
const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)

function onDrop(e: DragEvent) {
  isDragging.value = false
  const file = e.dataTransfer?.files[0]
  if (file) uploadStore.upload(file)
}

function onSelect(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (file) uploadStore.upload(file)
}
</script>
