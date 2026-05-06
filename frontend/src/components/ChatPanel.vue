<template>
  <div class="border-t border-[--color-border] bg-[--color-bg-surface]/60 flex flex-col overflow-hidden">

    <!-- Message list -->
    <div ref="messagesEl" class="flex-1 overflow-y-auto px-3 py-3 space-y-3 flex flex-col min-h-0">

      <template v-if="chatStore.history.length === 0">
        <p class="text-center text-[--color-text-muted] ui-caption py-6">輸入問題開始對話</p>
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

    <!-- Prompt suggestions -->
    <PromptSuggestions
      v-if="showSuggestions && chatStore.history.length === 0 && !chatStore.isAnswering"
      @select="selectSuggestion"
    />

    <!-- Input row -->
    <div class="flex items-end gap-2 px-3 pb-3">
      <textarea
        v-model="input"
        rows="1"
        :disabled="chatStore.isAnswering"
        placeholder="輸入問題..."
        @keydown.enter.exact.prevent="submit"
        @input="onInput"
        ref="textareaEl"
        class="flex-1 bg-[--color-bg-elevated] text-[--color-text-primary] placeholder-[--color-text-muted] rounded-xl px-4 py-2.5 ui-body outline-none focus:ring-2 focus:ring-[--color-primary] resize-none disabled:opacity-40 transition"
        style="field-sizing: content; max-height: 120px;"
      />
      <button
        @click="submit"
        :disabled="!input.trim() || chatStore.isAnswering"
        class="bg-[--color-primary] hover:bg-[--color-primary-hover] disabled:opacity-40 text-[--color-text-on-primary] w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M5 12h14M12 5l7 7-7 7"/>
        </svg>
      </button>
      <button
        @click="onClear"
        :disabled="chatStore.history.length === 0 && !input.trim()"
        title="清除對話"
        class="border border-[--color-border] w-10 h-10 flex items-center justify-center flex-shrink-0 transition rounded-xl disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:border-[--color-border] disabled:hover:bg-transparent text-[--color-text-secondary] hover:text-[--color-text-primary] hover:border-[--color-border-focus] hover:bg-[--color-bg-elevated]"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
          <line x1="10" y1="11" x2="10" y2="17"/>
          <line x1="14" y1="11" x2="14" y2="17"/>
        </svg>
      </button>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '../stores/chat'
import PromptSuggestions from './chat/PromptSuggestions.vue'

const chatStore      = useChatStore()
const input          = ref('')
const bottomEl       = ref<HTMLElement | null>(null)
const textareaEl     = ref<HTMLTextAreaElement | null>(null)
const showSuggestions = ref(true)

function autoResize() {
  const el = textareaEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = el.scrollHeight + 'px'
}

function onInput() {
  autoResize()
  showSuggestions.value = !input.value.trim()
}

function selectSuggestion(text: string) {
  input.value = text
  showSuggestions.value = false
  nextTick(() => textareaEl.value?.focus())
}

function onClear() {
  chatStore.clear()
  input.value = ''
  showSuggestions.value = true
  nextTick(() => autoResize())
}

async function submit() {
  const msg = input.value.trim()
  if (!msg) return
  input.value = ''
  showSuggestions.value = false
  await nextTick()
  autoResize()
  await chatStore.send(msg)
}

watch(() => chatStore.history.length, async () => {
  await nextTick()
  bottomEl.value?.scrollIntoView({ behavior: 'smooth' })
})
</script>
