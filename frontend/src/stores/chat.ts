import { defineStore } from 'pinia'
import { ref } from 'vue'
import { sendMessage, type ChatMessage } from '../api/chat'

export const useChatStore = defineStore('chat', () => {
  const history = ref<ChatMessage[]>([])
  const isAnswering = ref(false)

  async function send(message: string) {
    history.value.push({ role: 'user', content: message })
    isAnswering.value = true
    try {
      const reply = await sendMessage(message)
      history.value.push(reply)
    } catch (e: any) {
      history.value.push({ role: 'assistant', content: `錯誤：${e.message}` })
    } finally {
      isAnswering.value = false
    }
  }

  function clear() {
    history.value = []
    isAnswering.value = false
  }

  return { history, isAnswering, send, clear }
})
