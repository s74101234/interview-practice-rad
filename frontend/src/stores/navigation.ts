import { defineStore } from 'pinia'
import { ref } from 'vue'

export type SectionId = 'upload' | 'status'

export const useNavigationStore = defineStore('navigation', () => {
  const activeSection = ref<SectionId>('upload')

  function navigate(id: SectionId) {
    activeSection.value = id
  }

  return { activeSection, navigate }
})
