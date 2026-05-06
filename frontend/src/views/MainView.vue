<template>
  <div class="h-screen flex flex-col bg-[--color-bg-base]">
    <!-- Header -->
    <header class="px-6 py-4 border-b border-[--color-border] bg-[--color-bg-elevated] flex-shrink-0">
      <h1 class="text-lg font-semibold text-[--color-text-primary]">DocMind</h1>
      <p class="text-xs text-[--color-text-muted]">上傳文件，與 AI 對話，建立 NotebookLM 簡報</p>
    </header>

    <!-- Body: resizable split -->
    <div class="flex-1 flex flex-col overflow-hidden" ref="containerEl">
      <!-- Top pane: upload + progress -->
      <div :style="{ height: topHeight + 'px' }" class="overflow-y-auto p-4 space-y-3 flex-shrink-0">
        <UploadPanel />
        <ProgressPanel />
      </div>

      <!-- Drag handle -->
      <div
        class="h-1.5 bg-[--color-border] cursor-row-resize hover:bg-[--color-border-focus] flex-shrink-0 transition-colors"
        @mousedown="startDrag"
      />

      <!-- Bottom pane: chat -->
      <div class="flex-1 p-4 overflow-hidden min-h-0">
        <ChatPanel class="h-full" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import UploadPanel from '../components/UploadPanel.vue'
import ProgressPanel from '../components/ProgressPanel.vue'
import ChatPanel from '../components/ChatPanel.vue'
import { useUploadStore } from '../stores/upload'

const uploadStore = useUploadStore()
uploadStore.startStatusStream()

const containerEl = ref<HTMLElement | null>(null)
const topHeight = ref(220)
let dragging = false
let startY = 0
let startH = 0

function startDrag(e: MouseEvent) {
  dragging = true
  startY = e.clientY
  startH = topHeight.value
}

function onMouseMove(e: MouseEvent) {
  if (!dragging || !containerEl.value) return
  const delta = e.clientY - startY
  const total = containerEl.value.clientHeight
  topHeight.value = Math.min(Math.max(startH + delta, 100), total - 200)
}

function onMouseUp() { dragging = false }

onMounted(() => {
  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('mouseup', onMouseUp)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('mouseup', onMouseUp)
})
</script>
