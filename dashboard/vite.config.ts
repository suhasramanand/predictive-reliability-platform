import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api/anomaly': {
        target: 'http://anomaly-service:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/anomaly/, '')
      },
      '/api/policy': {
        target: 'http://policy-engine:8081',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/policy/, '')
      }
    }
  }
})


