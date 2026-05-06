import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/upload': 'http://localhost:8000',
      '/chat': 'http://localhost:8000',
      '/status': 'http://localhost:8000',
      '/mcp': 'http://localhost:8000',
    },
  },
})
