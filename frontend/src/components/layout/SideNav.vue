<script setup lang="ts">
import { useNavigationStore } from '../../stores/navigation'

const navigation = useNavigationStore()

const navItems: { id: 'upload' | 'status'; label: string }[] = [
  { id: 'upload', label: '上傳文件' },
  { id: 'status', label: '系統狀態' },
]
</script>

<template>
  <nav class="w-[10vw] bg-[--color-bg-surface] border-r border-[--color-border] flex flex-col flex-shrink-0 select-none">
    <div class="flex-1 py-3 px-2 flex flex-col gap-0.5">
      <button
        v-for="item in navItems"
        :key="item.id"
        :class="[
          'w-full text-left px-3 py-2 rounded-lg ui-body transition flex items-center gap-2.5',
          navigation.activeSection === item.id
            ? 'bg-[--color-primary] text-[--color-text-on-primary] font-medium'
            : 'text-[--color-text-secondary] hover:bg-[--color-bg-elevated] hover:text-[--color-text-primary]',
        ]"
        @click="navigation.navigate(item.id)"
      >
        <!-- 上傳文件圖示 -->
        <svg v-if="item.id === 'upload'" class="flex-shrink-0 w-[15px] h-[15px]" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <!-- 系統狀態圖示 -->
        <svg v-else-if="item.id === 'status'" class="flex-shrink-0 w-[15px] h-[15px]" fill="none" stroke="currentColor" stroke-width="1.75" viewBox="0 0 24 24" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
        </svg>
        <span>{{ item.label }}</span>
      </button>
    </div>
  </nav>
</template>
