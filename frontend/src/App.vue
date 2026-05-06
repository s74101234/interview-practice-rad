<script setup lang="ts">
import { ref, onMounted } from 'vue'
import MainView from './views/MainView.vue'

const backendReady = ref(false)

async function waitForBackend() {
  while (true) {
    try {
      await fetch('/health', { signal: AbortSignal.timeout(2000) })
      backendReady.value = true
      return
    } catch {
      await new Promise(r => setTimeout(r, 1000))
    }
  }
}

onMounted(waitForBackend)
</script>

<template>
  <div class="w-full h-full">
    <div v-if="!backendReady" class="w-full h-full bg-[--color-bg-base] flex flex-col items-center justify-center gap-4">
      <svg class="animate-spin h-10 w-10 text-[--color-primary]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <p class="text-[--color-text-muted] ui-body">連線中...</p>
    </div>
    <MainView v-else class="w-full h-full" />
  </div>
</template>
