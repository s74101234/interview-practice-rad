<template>
  <aside class="w-[13vw] min-w-[140px] bg-[--color-bg-surface] border-r border-[--color-border] flex flex-col flex-shrink-0 select-none overflow-hidden">
    <div class="px-3 py-3 border-b border-[--color-border]">
      <p class="ui-caption font-medium text-[--color-text-muted] uppercase tracking-wide">文件</p>
    </div>
    <div class="flex-1 py-2 px-2 flex flex-col gap-1 overflow-y-auto">
      <div v-if="!uploadStore.filename"
        class="px-3 py-2 ui-caption text-[--color-text-muted] text-center mt-4">
        尚未上傳文件
      </div>
      <template v-else>
        <div class="px-3 py-2 rounded-lg bg-[--color-primary-subtle] border border-[--color-border-focus]">
          <p class="ui-caption font-medium text-[--color-text-primary] truncate">{{ uploadStore.filename }}</p>
          <p class="ui-caption text-[--color-text-muted] mt-0.5">
            {{ uploadStore.isProcessing ? '處理中...' : uploadStore.isReady ? `${uploadStore.chunkCount ?? 0} 個段落` : '等待上傳' }}
          </p>
        </div>
        <div class="mt-2 px-1 space-y-1">
          <div v-for="step in stages" :key="step.key"
            class="flex items-center gap-2 px-2 py-1.5 rounded ui-caption"
            :class="stageClass(step.key)">
            <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :class="stageDotClass(step.key)" />
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

function stageStatus(key: string) {
  if (!uploadStore.filename) return 'idle'
  if (uploadStore.isReady) return 'done'
  const cur = uploadStore.currentStage
  if (!cur) return 'idle'
  const ci = order.indexOf(cur)
  const ki = order.indexOf(key)
  if (ki < ci) return 'done'
  if (ki === ci) return 'active'
  return 'idle'
}

function stageClass(key: string) {
  const s = stageStatus(key)
  if (s === 'done')   return 'text-[--color-success-text]'
  if (s === 'active') return 'text-[--color-text-primary] font-medium'
  return 'text-[--color-text-muted]'
}

function stageDotClass(key: string) {
  const s = stageStatus(key)
  if (s === 'done')   return 'bg-[--color-success]'
  if (s === 'active') return 'bg-[--color-primary] animate-pulse'
  return 'bg-[--color-border]'
}
</script>
