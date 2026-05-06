<template>
  <div class="flex flex-col gap-4">

    <h2 class="ui-title font-semibold text-[--color-text-primary]">系統狀態</h2>

    <!-- Models -->
    <div class="rounded-xl border border-[--color-border] overflow-hidden">
      <div class="px-4 py-3 bg-[--color-bg-elevated] border-b border-[--color-border]">
        <h3 class="ui-body font-medium text-[--color-text-primary]">模型</h3>
      </div>
      <div class="p-4 bg-[--color-bg-surface] space-y-2">
        <div v-for="m in models" :key="m.label"
          class="flex items-center gap-3 px-3 py-2 rounded-lg bg-[--color-bg-elevated] border border-[--color-border]">
          <span class="w-2 h-2 rounded-full bg-[--color-success] flex-shrink-0" />
          <div>
            <p class="ui-body text-[--color-text-primary]">{{ m.label }}</p>
            <p class="ui-caption text-[--color-text-muted]">{{ m.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Vector store -->
    <div class="rounded-xl border border-[--color-border] overflow-hidden">
      <div class="px-4 py-3 bg-[--color-bg-elevated] border-b border-[--color-border]">
        <h3 class="ui-body font-medium text-[--color-text-primary]">向量庫</h3>
      </div>
      <div class="p-4 bg-[--color-bg-surface] space-y-3">
        <div class="flex items-center justify-between px-3 py-2 rounded-lg bg-[--color-bg-elevated] border border-[--color-border]">
          <div>
            <p class="ui-body text-[--color-text-primary]">knowledge_base</p>
            <p class="ui-caption text-[--color-text-muted]">Qdrant · COSINE · 768 維</p>
          </div>
          <div class="text-right">
            <p class="ui-body font-medium text-[--color-text-primary]">{{ uploadStore.chunkCount ?? 0 }}</p>
            <p class="ui-caption text-[--color-text-muted]">筆向量</p>
          </div>
        </div>

        <!-- KB status -->
        <div class="flex items-center gap-2 px-3 py-2 rounded-lg border ui-body transition-colors"
          :class="uploadStore.isReady
            ? 'bg-[--color-success-subtle] border-[--color-success-text]/40 text-[--color-success-text]'
            : uploadStore.isProcessing
              ? 'bg-[--color-warning-subtle] border-[--color-warning-text]/40 text-[--color-warning-text]'
              : 'bg-[--color-bg-elevated] border-[--color-border] text-[--color-text-muted]'">
          <span class="w-2 h-2 rounded-full flex-shrink-0"
            :class="uploadStore.isReady ? 'bg-[--color-success]'
              : uploadStore.isProcessing ? 'bg-[--color-warning] animate-pulse'
              : 'bg-[--color-border]'" />
          {{ uploadStore.isReady ? '就緒' : uploadStore.isProcessing ? '建立中' : '等待上傳' }}
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useUploadStore } from '../../stores/upload'

const uploadStore = useUploadStore()

const models = [
  { label: 'Gemini 2.0 Flash',    desc: '對話生成 · Function Calling' },
  { label: 'text-embedding-004',  desc: '文字向量嵌入 · 768 維' },
]
</script>
