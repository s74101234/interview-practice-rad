<template>
  <aside class="w-[13vw] min-w-[140px] bg-[--color-bg-surface] border-r border-[--color-border] flex flex-col flex-shrink-0 select-none overflow-hidden">

    <div class="px-3 py-3 border-b border-[--color-border]">
      <p class="ui-caption font-semibold text-[--color-text-muted] uppercase tracking-wide">文件</p>
    </div>

    <div class="flex-1 py-2 px-2 flex flex-col gap-1 overflow-y-auto">

      <div v-if="!uploadStore.filename" class="px-3 py-6 flex flex-col items-center gap-2 text-center">
        <div class="w-8 h-8 rounded-full bg-[--color-bg-elevated] border border-[--color-border] flex items-center justify-center">
          <svg class="w-4 h-4 text-[--color-text-muted]" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
        </div>
        <p class="ui-caption text-[--color-text-muted]">尚未上傳文件</p>
      </div>

      <template v-else>
        <div class="px-3 py-2.5 rounded-lg bg-[--color-primary-subtle] border border-[--color-border-focus]/40">
          <p class="ui-caption font-semibold text-[--color-text-primary] truncate">{{ uploadStore.filename }}</p>
          <p class="ui-caption text-[--color-text-muted] mt-0.5">
            {{ uploadStore.isProcessing ? '處理中...' : uploadStore.isReady ? `${uploadStore.chunkCount ?? 0} 個段落` : '' }}
          </p>
        </div>

        <div class="mt-2 px-1 space-y-0.5">
          <div v-for="step in stages" :key="step.key"
            class="flex items-center gap-2 px-2 py-1.5 rounded-lg ui-caption transition-colors"
            :class="stageStatus(step.key) === 'done'
              ? 'text-[--color-success-text]'
              : stageStatus(step.key) === 'active'
                ? 'text-[--color-text-primary] font-medium bg-[--color-bg-elevated]'
                : 'text-[--color-text-muted]'"
          >
            <span class="w-1.5 h-1.5 rounded-full flex-shrink-0 transition-colors"
              :class="stageStatus(step.key) === 'done'
                ? 'bg-[--color-success]'
                : stageStatus(step.key) === 'active'
                  ? 'bg-[--color-primary] animate-pulse'
                  : 'bg-[--color-border]'"
            />
            {{ step.label }}
          </div>
        </div>
      </template>

    </div>
  </aside>
</template>

<script setup lang="ts">
import { useUploadStore } from '../../stores/upload'

const uploadStore = useUploadStore()

const stages = [
  { key: 'parse', label: '解析文件' },
  { key: 'clean', label: '清洗文字' },
  { key: 'chunk', label: '切分段落' },
  { key: 'embed', label: '建立索引' },
]
const order = ['parse', 'clean', 'chunk', 'embed']

function stageStatus(key: string): 'done' | 'active' | 'idle' {
  if (uploadStore.isReady) return 'done'
  const cur = uploadStore.currentStage
  if (!cur) return 'idle'
  const ci = order.indexOf(cur)
  const ki = order.indexOf(key)
  if (ki < ci) return 'done'
  if (ki === ci) return 'active'
  return 'idle'
}
</script>
