<template>
  <div class="flex flex-col gap-3">

    <UploadPanel />
    <ProgressPanel />

    <!-- Doc + System info — visible after upload starts -->
    <template v-if="uploadStore.filename">

      <!-- Document info -->
      <div class="rounded-xl border border-[--color-border] overflow-hidden">
        <div class="px-4 py-2.5 bg-[--color-bg-elevated] border-b border-[--color-border]">
          <h3 class="ui-body font-medium text-[--color-text-primary]">文件資訊</h3>
        </div>
        <div class="p-4 bg-[--color-bg-surface] space-y-2">
          <div class="flex items-center justify-between">
            <span class="ui-caption text-[--color-text-muted]">檔案名稱</span>
            <span class="ui-caption text-[--color-text-primary] truncate max-w-[60%] text-right">{{ uploadStore.filename }}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="ui-caption text-[--color-text-muted]">段落數</span>
            <span class="ui-caption text-[--color-text-primary]">
              {{ uploadStore.isReady ? uploadStore.chunkCount ?? 0 : '—' }}
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="ui-caption text-[--color-text-muted]">狀態</span>
            <span class="ui-caption"
              :class="uploadStore.isReady ? 'text-[--color-success-text]'
                : uploadStore.isProcessing ? 'text-[--color-warning-text]'
                : 'text-[--color-text-muted]'"
            >{{ uploadStore.isReady ? '就緒' : uploadStore.isProcessing ? '處理中' : '等待中' }}</span>
          </div>
        </div>
      </div>

      <!-- System info -->
      <div class="rounded-xl border border-[--color-border] overflow-hidden">
        <div class="px-4 py-2.5 bg-[--color-bg-elevated] border-b border-[--color-border]">
          <h3 class="ui-body font-medium text-[--color-text-primary]">系統資訊</h3>
        </div>
        <div class="p-4 bg-[--color-bg-surface] space-y-2">
          <div v-for="m in models" :key="m.label" class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-[--color-success] flex-shrink-0" />
            <span class="ui-caption text-[--color-text-secondary]">{{ m.label }}</span>
            <span class="ui-caption text-[--color-text-muted] ml-auto">{{ m.desc }}</span>
          </div>
          <div class="border-t border-[--color-border] pt-2 mt-1">
            <div class="flex items-center justify-between">
              <span class="ui-caption text-[--color-text-muted]">向量庫</span>
              <span class="ui-caption text-[--color-text-secondary]">knowledge_base · 768d</span>
            </div>
          </div>
        </div>
      </div>

    </template>

  </div>
</template>

<script setup lang="ts">
import UploadPanel   from '../UploadPanel.vue'
import ProgressPanel from '../ProgressPanel.vue'
import { useUploadStore } from '../../stores/upload'

const uploadStore = useUploadStore()

const models = [
  { label: 'Gemini 2.0 Flash',   desc: '對話 · Function Calling' },
  { label: 'text-embedding-004', desc: '向量嵌入 · 768 維' },
]
</script>
