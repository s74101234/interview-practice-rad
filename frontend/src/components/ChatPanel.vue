<template>
  <div class="rounded-xl border border-[--color-border] overflow-hidden flex flex-col h-full">
    <div class="px-4 py-3 bg-[--color-bg-elevated] border-b border-[--color-border]">
      <h3 class="text-sm font-medium text-[--color-text-primary]">對話</h3>
    </div>

    <!-- Messages -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto p-4 space-y-4 bg-[--color-bg-surface]">
      <div v-if="chatStore.history.length === 0" class="text-sm text-[--color-text-muted] text-center mt-8">
        {{ uploadStore.isReady ? '請輸入問題開始對話' : '請先上傳文件' }}
      </div>

      <div v-for="(msg, i) in chatStore.history" :key="i" class="flex flex-col gap-1"
        :class="msg.role === 'user' ? 'items-end' : 'items-start'">
        <div
          class="max-w-[80%] rounded-xl px-4 py-2 text-sm whitespace-pre-wrap"
          :class="msg.role === 'user'
            ? 'bg-[--color-primary] text-[--color-primary-text]'
            : 'bg-[--color-bg-elevated] text-[--color-text-primary] border border-[--color-border]'"
        >{{ msg.content }}</div>
        <span v-if="msg.tool" class="text-xs text-[--color-text-muted] px-1">
          [ {{ msg.tool }} ]
        </span>
      </div>

      <div v-if="chatStore.isAnswering" class="flex items-start">
        <div class="bg-[--color-bg-elevated] border border-[--color-border] rounded-xl px-4 py-2 text-sm text-[--color-text-muted]">
          <span class="animate-pulse">···</span>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="p-3 border-t border-[--color-border] bg-[--color-bg-elevated] flex gap-2">
      <input
        v-model="input"
        type="text"
        placeholder="輸入問題..."
        :disabled="!uploadStore.isReady || chatStore.isAnswering"
        class="flex-1 rounded-lg border border-[--color-border] bg-[--color-bg-surface] px-3 py-2 text-sm text-[--color-text-primary] placeholder-[--color-text-muted] outline-none focus:border-[--color-border-focus] disabled:opacity-40"
        @keydown.enter="submit"
      />
      <button
        :disabled="!input.trim() || !uploadStore.isReady || chatStore.isAnswering"
        class="px-4 py-2 rounded-lg text-sm font-medium bg-[--color-primary] text-[--color-primary-text] disabled:opacity-40"
        @click="submit"
      >送出</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '../stores/chat'
import { useUploadStore } from '../stores/upload'

const chatStore = useChatStore()
const uploadStore = useUploadStore()
const input = ref('')
const messagesEl = ref<HTMLElement | null>(null)

async function submit() {
  const msg = input.value.trim()
  if (!msg) return
  input.value = ''
  await chatStore.send(msg)
}

watch(
  () => chatStore.history.length,
  async () => {
    await nextTick()
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  }
)
</script>
