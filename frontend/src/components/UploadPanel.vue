<template>
  <div class="rounded-xl border overflow-hidden" :class="isDragging ? 'border-[--color-border-focus]' : 'border-[--color-border]'">

    <div class="px-4 py-3 bg-[--color-bg-elevated] border-b border-[--color-border] flex items-center justify-between">
      <h3 class="ui-body font-medium text-[--color-text-primary]">上傳文件</h3>
      <span v-if="uploadStore.isReady" class="ui-caption text-[--color-success-text]">就緒</span>
    </div>

    <div class="p-4 bg-[--color-bg-surface]">
      <div
        class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors"
        :class="isDragging
          ? 'border-[--color-border-focus] bg-[--color-primary-subtle]'
          : 'border-[--color-border] hover:border-[--color-border-focus] hover:bg-[--color-primary-subtle]'"
        @dragover.prevent="isDragging = true"
        @dragleave="isDragging = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <input ref="fileInput" type="file" accept=".pdf,.pptx,.ppt" class="hidden" @change="onSelect" />

        <!-- Processing -->
        <template v-if="uploadStore.isProcessing">
          <div class="w-8 h-8 border-2 border-[--color-primary] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p class="ui-body text-[--color-text-secondary]">處理中...</p>
        </template>

        <!-- Done -->
        <template v-else-if="uploadStore.isReady">
          <div class="w-10 h-10 rounded-full bg-[--color-success-subtle] border border-[--color-success-text]/40 flex items-center justify-center mx-auto mb-3">
            <svg class="w-5 h-5 text-[--color-success-text]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
          </div>
          <p class="ui-body font-medium text-[--color-text-primary] truncate px-4">{{ uploadStore.filename }}</p>
          <p class="ui-caption text-[--color-text-muted] mt-1">點擊或拖曳以重新上傳</p>
        </template>

        <!-- Default -->
        <template v-else>
          <div class="w-10 h-10 rounded-full bg-[--color-bg-elevated] border border-[--color-border] flex items-center justify-center mx-auto mb-3">
            <svg class="w-5 h-5 text-[--color-text-muted]" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <p class="ui-body text-[--color-text-secondary]">拖曳或點擊上傳</p>
          <p class="ui-caption text-[--color-text-muted] mt-1">支援 PDF、PPTX</p>
        </template>

      </div>

      <p v-if="uploadStore.error" class="mt-2 ui-caption text-[--color-danger-text]">{{ uploadStore.error }}</p>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUploadStore } from '../stores/upload'

const uploadStore = useUploadStore()
const fileInput   = ref<HTMLInputElement | null>(null)
const isDragging  = ref(false)

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
