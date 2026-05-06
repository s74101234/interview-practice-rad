<template>
  <div v-if="uploadStore.isProcessing" class="rounded-xl border border-[--color-border] overflow-hidden">
    <div class="px-4 py-3 bg-[--color-bg-elevated] border-b border-[--color-border]">
      <h3 class="text-sm font-medium text-[--color-text-primary]">處理進度</h3>
    </div>
    <div class="p-4 bg-[--color-bg-surface] space-y-2">
      <div v-for="step in steps" :key="step.key" class="flex items-center gap-3">
        <div class="w-24 text-xs text-[--color-text-muted]">{{ step.label }}</div>
        <div class="flex-1 h-2 bg-[--color-bg-elevated] rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="stepDone(step.key) ? 'bg-[--color-success]' : isActive(step.key) ? 'bg-[--color-primary]' : 'bg-[--color-border]'"
            :style="{ width: stepDone(step.key) ? '100%' : isActive(step.key) ? '60%' : '0%' }"
          />
        </div>
        <div class="w-6 text-xs text-center text-[--color-text-muted]">
          {{ stepDone(step.key) ? '✓' : isActive(step.key) ? '…' : '' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUploadStore } from '../stores/upload'

const uploadStore = useUploadStore()

const steps = [
  { key: 'parse', label: '解析文件' },
  { key: 'clean', label: '清洗文字' },
  { key: 'chunk', label: '切分段落' },
  { key: 'embed', label: '建立索引' },
]

const order = ['parse', 'clean', 'chunk', 'embed']

function isActive(key: string) {
  return uploadStore.currentStage === key
}

function stepDone(key: string) {
  const current = uploadStore.currentStage
  if (!current) return false
  return order.indexOf(key) < order.indexOf(current)
}
</script>
