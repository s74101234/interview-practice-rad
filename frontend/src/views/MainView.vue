<template>
  <div class="h-screen flex flex-col bg-[--color-bg-base] text-[--color-text-secondary] overflow-hidden">

    <!-- Header -->
    <header class="h-[8vh] bg-[--color-bg-surface] border-b border-[--color-border] flex items-center justify-between px-4 flex-shrink-0 select-none">
      <span class="ui-title font-semibold text-[--color-text-primary]">Interview Practice</span>

      <div class="flex items-center gap-3">
        <div v-if="uploadStore.isProcessing"
          class="flex items-center gap-1.5 ui-caption px-2 py-0.5 rounded border bg-[--color-warning-subtle] border-[--color-warning-text] text-[--color-warning-text]">
          <span class="w-1.5 h-1.5 rounded-full bg-[--color-warning] animate-pulse" />
          {{ stageLabel(uploadStore.currentStage) }}
        </div>
        <div v-else-if="uploadStore.isReady"
          class="flex items-center gap-1.5 ui-caption px-2 py-0.5 rounded border bg-[--color-success-subtle] border-[--color-success-text] text-[--color-success-text]">
          <span class="w-1.5 h-1.5 rounded-full bg-[--color-success]" />
          知識庫就緒
        </div>
      </div>
    </header>

    <!-- Body -->
    <div class="flex-1 flex flex-col overflow-hidden">

      <!-- Scrollable content -->
      <div class="flex-1 overflow-y-auto p-4 min-h-0">
        <UploadSection />
      </div>

      <!-- Resize handle -->
      <div
        class="h-1.5 bg-[--color-border] hover:bg-[--color-primary] active:bg-[--color-primary-hover] cursor-row-resize flex-shrink-0 transition-colors"
        @mousedown="onResizeStart"
      />

      <!-- Chat -->
      <ChatPanel :style="{ height: chatHeight + 'px', flexShrink: 0 }" />

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import UploadSection from '../components/sections/UploadSection.vue'
import ChatPanel     from '../components/ChatPanel.vue'
import { useUploadStore } from '../stores/upload'

const uploadStore = useUploadStore()
uploadStore.startStatusStream()

const stageLabels: Record<string, string> = {
  parse: '解析文件', clean: '清洗文字', chunk: '切分段落', embed: '建立索引',
}
function stageLabel(key: string | null) { return key ? (stageLabels[key] ?? key) : '處理中' }

const LS_KEY = 'docmind.chatHeight'
const MIN_H  = Math.round(window.innerHeight * 0.12)
const MAX_H  = Math.round(window.innerHeight * 0.55)
function clampH(v: number) { return Math.max(MIN_H, Math.min(MAX_H, v)) }
const chatHeight = ref(clampH(parseInt(localStorage.getItem(LS_KEY) ?? String(Math.round(window.innerHeight * 0.32)))))

let dragging = false, dragStartY = 0, dragStartH = 0

function onResizeStart(e: MouseEvent) {
  dragging = true; dragStartY = e.clientY; dragStartH = chatHeight.value
  document.addEventListener('mousemove', onResizeMove)
  document.addEventListener('mouseup', onResizeEnd)
  e.preventDefault()
}
function onResizeMove(e: MouseEvent) {
  if (!dragging) return
  chatHeight.value = clampH(dragStartH - (e.clientY - dragStartY))
}
function onResizeEnd() {
  dragging = false
  localStorage.setItem(LS_KEY, String(chatHeight.value))
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeEnd)
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeEnd)
})
</script>
