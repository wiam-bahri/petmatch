import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En dev, les appels /api sont envoyés vers FastAPI (uvicorn main:app --port 8000)
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } } },
  test: { environment: 'node' },
})
