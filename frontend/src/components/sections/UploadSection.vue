<template>
  <div class="flex flex-col gap-3">

    <UploadPanel />
    <ProgressPanel />

    <!-- Document info — shown after upload -->
    <div v-if="uploadStore.filename" class="rounded-xl border border-[--color-border] overflow-hidden">
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

    <!-- Log — always visible -->
    <div class="rounded-xl border border-[--color-border] overflow-hidden">
      <div class="px-4 py-2.5 bg-[--color-bg-elevated] border-b border-[--color-border]">
        <h3 class="ui-body font-medium text-[--color-text-primary]">系統紀錄</h3>
      </div>
      <div ref="logEl" class="p-3 bg-[--color-bg-surface] h-32 overflow-y-auto space-y-0.5">
        <p v-if="uploadStore.logs.length === 0" class="ui-caption text-[--color-text-muted]">等待系統事件...</p>
        <p
          v-for="(log, i) in uploadStore.logs"
          :key="i"
          class="ui-caption text-[--color-text-secondary] font-mono leading-relaxed"
        >{{ log }}</p>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import UploadPanel   from '../UploadPanel.vue'
import ProgressPanel from '../ProgressPanel.vue'
import { useUploadStore } from '../../stores/upload'

const uploadStore = useUploadStore()
const logEl = ref<HTMLElement | null>(null)

// 新 log 進來時自動捲到底
watch(() => uploadStore.logs.length, async () => {
  await nextTick()
  if (logEl.value) logEl.value.scrollTop = logEl.value.scrollHeight
})
</script>
