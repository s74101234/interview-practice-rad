<template>
  <div v-if="uploadStore.isProcessing" class="rounded-xl border border-[--color-border] overflow-hidden">

    <div class="px-4 py-3 bg-[--color-bg-elevated] border-b border-[--color-border]">
      <h3 class="ui-body font-medium text-[--color-text-primary]">處理進度</h3>
    </div>

    <div class="p-4 bg-[--color-bg-surface] space-y-3">
      <div v-for="step in steps" :key="step.key" class="flex items-center gap-3">

        <!-- Status dot -->
        <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 transition-colors"
          :class="stepStatus(step.key) === 'done'
            ? 'bg-[--color-success-subtle] border border-[--color-success-text]/40'
            : stepStatus(step.key) === 'active'
              ? 'bg-[--color-primary-subtle] border border-[--color-border-focus]'
              : 'bg-[--color-bg-elevated] border border-[--color-border]'"
        >
          <svg v-if="stepStatus(step.key) === 'done'" class="w-3 h-3 text-[--color-success-text]" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
          <span v-else-if="stepStatus(step.key) === 'active'" class="w-2 h-2 rounded-full bg-[--color-primary] animate-pulse" />
        </div>

        <!-- Label -->
        <span class="ui-body flex-shrink-0 w-20 transition-colors"
          :class="stepStatus(step.key) === 'done'
            ? 'text-[--color-success-text]'
            : stepStatus(step.key) === 'active'
              ? 'text-[--color-text-primary] font-medium'
              : 'text-[--color-text-muted]'"
        >{{ step.label }}</span>

        <!-- Bar -->
        <div class="flex-1 h-1.5 bg-[--color-bg-elevated] rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="stepStatus(step.key) === 'done'
              ? 'bg-[--color-success]'
              : stepStatus(step.key) === 'active'
                ? 'bg-[--color-primary]'
                : 'bg-transparent'"
            :style="{ width: stepStatus(step.key) === 'done' ? '100%' : stepStatus(step.key) === 'active' ? '55%' : '0%' }"
          />
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

function stepStatus(key: string): 'done' | 'active' | 'idle' {
  const cur = uploadStore.currentStage
  if (!cur) return 'idle'
  const ci = order.indexOf(cur)
  const ki = order.indexOf(key)
  if (ki < ci) return 'done'
  if (ki === ci) return 'active'
  return 'idle'
}
</script>
