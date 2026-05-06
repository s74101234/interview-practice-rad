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

  let es: EventSource | null = null

  function startStatusStream() {
    if (es) return
    es = new EventSource('/status/stream')

    es.addEventListener('pipeline_start', (e) => {
      const d = JSON.parse(e.data)
      isProcessing.value = true
      filename.value = d.filename
      error.value = null
      isReady.value = false
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
    })

    es.addEventListener('pipeline_error', (e) => {
      const d = JSON.parse(e.data)
      isProcessing.value = false
      currentStage.value = null
      error.value = d.message
    })

    es.onerror = () => {
      es?.close()
      es = null
      setTimeout(startStatusStream, 3000)
    }
  }

  async function upload(file: File) {
    await uploadFile(file)
    startStatusStream()
  }

  return { isProcessing, currentStage, chunkCount, filename, error, isReady, upload, startStatusStream }
})
