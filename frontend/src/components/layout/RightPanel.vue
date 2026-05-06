<template>
  <aside class="w-[14vw] min-w-[150px] bg-[--color-bg-surface] border-l border-[--color-border] flex flex-col flex-shrink-0 select-none overflow-hidden">
    <div class="px-3 py-3 border-b border-[--color-border]">
      <p class="ui-caption font-medium text-[--color-text-muted] uppercase tracking-wide">系統資訊</p>
    </div>
    <div class="flex-1 py-3 px-3 flex flex-col gap-4 overflow-y-auto">

      <div>
        <p class="ui-caption text-[--color-text-muted] mb-1.5">模型</p>
        <div class="flex items-center gap-2 px-2 py-1.5 rounded bg-[--color-bg-elevated] border border-[--color-border]">
          <span class="w-1.5 h-1.5 rounded-full bg-[--color-success] flex-shrink-0" />
          <span class="ui-caption text-[--color-text-secondary] truncate">Gemini 2.0 Flash</span>
        </div>
        <div class="flex items-center gap-2 px-2 py-1.5 rounded bg-[--color-bg-elevated] border border-[--color-border] mt-1">
          <span class="w-1.5 h-1.5 rounded-full bg-[--color-success] flex-shrink-0" />
          <span class="ui-caption text-[--color-text-secondary] truncate">text-embedding-004</span>
        </div>
      </div>

      <div>
        <p class="ui-caption text-[--color-text-muted] mb-1.5">向量庫</p>
        <div class="px-2 py-1.5 rounded bg-[--color-bg-elevated] border border-[--color-border]">
          <p class="ui-caption text-[--color-text-secondary]">knowledge_base</p>
          <p class="ui-caption text-[--color-text-muted] mt-0.5">
            {{ uploadStore.isReady ? `${uploadStore.chunkCount ?? 0} 筆` : '未就緒' }}
          </p>
        </div>
      </div>

      <div>
        <p class="ui-caption text-[--color-text-muted] mb-1.5">知識庫狀態</p>
        <div
          class="flex items-center gap-2 px-2 py-1.5 rounded border ui-caption"
          :class="uploadStore.isReady
            ? 'bg-[--color-success-subtle] border-[--color-success-text] text-[--color-success-text]'
            : uploadStore.isProcessing
              ? 'bg-[--color-warning-subtle] border-[--color-warning-text] text-[--color-warning-text]'
              : 'bg-[--color-bg-elevated] border-[--color-border] text-[--color-text-muted]'"
        >
          <span class="w-1.5 h-1.5 rounded-full flex-shrink-0"
            :class="uploadStore.isReady ? 'bg-[--color-success]' : uploadStore.isProcessing ? 'bg-[--color-warning] animate-pulse' : 'bg-[--color-border]'" />
          {{ uploadStore.isReady ? '就緒' : uploadStore.isProcessing ? '建立中' : '等待上傳' }}
        </div>
      </div>

    </div>
  </aside>
</template>

<script setup lang="ts">
import { useUploadStore } from '../../stores/upload'
const uploadStore = useUploadStore()
</script>
