import { defineStore } from 'pinia'
import { ref } from 'vue'
import { uploadFile } from '../api/upload'

type Stage = 'parse' | 'clean' | 'chunk' | 'embed' | null

export const useUploadStore = defineStore('upload', () => {
  const isProcessing = ref(false)
  const currentStage = ref<Stage>(null)
  const chunkCount = ref<number | null>(null)
  const filename = ref<string | null>(null)
  const error = ref<string | null>(null)
  const isReady = ref(false)
  const logs = ref<string[]>([])
  const currentThought = ref<string | null>(null)

  let es: EventSource | null = null

  function addLog(msg: string) {
    const time = new Date().toLocaleTimeString('zh-TW', { hour12: false })
    logs.value.push(`[${time}] ${msg}`)
  }

  function startStatusStream() {
    if (es) return
    es = new EventSource('/status/stream')

    es.onopen = () => {
      addLog('已連線至後端服務')
    }

    es.addEventListener('pipeline_start', (e) => {
      const d = JSON.parse(e.data)
      isProcessing.value = true
      filename.value = d.filename
      error.value = null
      isReady.value = false
    })

    es.addEventListener('log', (e) => {
      const d = JSON.parse(e.data)
      addLog(d.message)
      const reactMatch   = d.message.match(/\[第 \d+ 輪\] Thought：(.+)/)
      const browserMatch = d.message.match(/\[Browser\] Thought：(.+)/)
      const match = reactMatch || browserMatch
      if (match) currentThought.value = match[1].trim()
    })

    es.addEventListener('pipeline_progress', (e) => {
      const d = JSON.parse(e.data)
      currentStage.value = d.stage
    })

    es.addEventListener('pipeline_done', (e) => {
      const d = JSON.parse(e.data)
      isProcessing.value = false
      currentStage.value = null
      chunkCount.value = d.chunk_count
      isReady.value = true
      addLog(`處理完成，共 ${d.chunk_count} 個段落`)
    })

    es.addEventListener('pipeline_error', (e) => {
      const d = JSON.parse(e.data)
      isProcessing.value = false
      currentStage.value = null
      error.value = d.message
      addLog(`錯誤：${d.message}`)
    })

    es.onerror = () => {
      addLog('連線中斷，重新連線中...')
      es?.close()
      es = null
      setTimeout(startStatusStream, 3000)
    }
  }

  async function restoreState() {
    try {
      const res = await fetch('/status')
      if (!res.ok) return
      const data = await res.json()
      if (data.ready) {
        filename.value = data.filename
        chunkCount.value = data.chunk_count
        isReady.value = true
        addLog(`恢復狀態：${data.filename}（${data.chunk_count} 個段落）`)
      }
    } catch { /* ignore */ }
  }

  async function upload(file: File) {
    addLog(`上傳檔案：${file.name}`)
    error.value = null
    isReady.value = false
    const data = await uploadFile(file)
    filename.value = data.filename
    isProcessing.value = true
    startStatusStream()
  }

  return { isProcessing, currentStage, chunkCount, filename, error, isReady, logs, currentThought, upload, startStatusStream, restoreState }
})
