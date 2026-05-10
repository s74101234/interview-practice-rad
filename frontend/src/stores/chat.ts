import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessage, cancelChat, type ChatMessage } from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  const history = ref<ChatMessage[]>([])
  const isAnswering = ref(false)
  let _abortController: AbortController | null = null

  async function send(message: string) {
    history.value.push({ role: 'user', content: message })
    isAnswering.value = true
    _abortController = new AbortController()
    try {
      const reply = await sendMessage(message, _abortController.signal)
      history.value.push(reply)
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        history.value.push({ role: 'assistant', content: `錯誤：${e.message}` })
      }
    } finally {
      isAnswering.value = false
      _abortController = null
    }
  }

  async function cancel() {
    await cancelChat()
    _abortController?.abort()
    isAnswering.value = false
  }

  function clear() {
    history.value = []
    isAnswering.value = false
  }

  return { history, isAnswering, send, cancel, clear }
})
