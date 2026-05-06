<template>
  <div class="border-t border-[--color-border] bg-[--color-bg-surface]/60 flex flex-col overflow-hidden">

    <!-- Message list -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto px-3 py-3 space-y-3 flex flex-col min-h-0">

      <template v-if="chatStore.history.length === 0">
        <p class="text-center text-[--color-text-muted] ui-caption py-6">
          {{ uploadStore.isReady ? '輸入問題開始對話' : '請先上傳文件' }}
        </p>
      </template>

      <div
        v-for="(msg, i) in chatStore.history" :key="i"
        class="flex flex-col gap-1"
        :class="msg.role === 'user' ? 'items-end' : 'items-start'"
      >
        <div
          class="max-w-[80%] px-4 py-2.5 ui-body whitespace-pre-wrap"
          :class="msg.role === 'user'
            ? 'bg-[--color-primary] text-[--color-text-on-primary] rounded-2xl rounded-br-sm'
            : 'bg-[--color-bg-elevated] text-[--color-text-primary] border border-[--color-border] rounded-2xl rounded-bl-sm'"
        >{{ msg.content }}</div>
        <span v-if="msg.tool" class="ui-caption text-[--color-text-muted] px-1">[ {{ msg.tool }} ]</span>
      </div>

      <!-- Loading -->
      <div v-if="chatStore.isAnswering" class="flex items-start">
        <div class="bg-[--color-bg-elevated] border border-[--color-border] rounded-2xl rounded-bl-sm px-4 py-2.5 ui-body text-[--color-text-muted] flex items-center gap-2">
          <span class="w-3 h-3 rounded-full border-2 border-[--color-primary] border-t-transparent animate-spin flex-shrink-0" />
          <span class="animate-pulse">思考中</span>
        </div>
      </div>

      <div ref="bottomEl" />
    </div>

    <!-- Input row -->
    <div class="flex items-end gap-2 px-3 pb-3">
      <textarea
        v-model="input"
        rows="1"
        :disabled="!uploadStore.isReady || chatStore.isAnswering"
        placeholder="輸入問題..."
        @keydown.enter.exact.prevent="submit"
        @input="autoResize"
        ref="textareaEl"
        class="flex-1 bg-[--color-bg-elevated] text-[--color-text-primary] placeholder-[--color-text-muted] rounded-xl px-4 py-2.5 ui-body outline-none focus:ring-2 focus:ring-[--color-primary] resize-none disabled:opacity-40 transition"
        style="field-sizing: content; max-height: 120px;"
      />
      <button
        @click="submit"
        :disabled="!input.trim() || !uploadStore.isReady || chatStore.isAnswering"
        class="bg-[--color-primary] hover:bg-[--color-primary-hover] disabled:opacity-40 text-[--color-text-on-primary] w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '../stores/chat'
import { useUploadStore } from '../stores/upload'

const chatStore   = useChatStore()
const uploadStore = useUploadStore()
const input       = ref('')
const messagesEl  = ref<HTMLElement | null>(null)
const bottomEl    = ref<HTMLElement | null>(null)
const textareaEl  = ref<HTMLTextAreaElement | null>(null)

function autoResize() {
  const el = textareaEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

async function submit() {
  const msg = input.value.trim()
  if (!msg) return
  input.value = ''
  await nextTick()
  autoResize()
  await chatStore.send(msg)
}

watch(() => chatStore.history.length, async () => {
  await nextTick()
  bottomEl.value?.scrollIntoView({ behavior: 'smooth' })
})
</script>
