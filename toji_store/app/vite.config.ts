import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8069',  // Cambia 8069 por el puerto real de Odoo
        changeOrigin: true,
        rewrite: (path) => path,
        headers: {
          'Origin': 'http://localhost:8069',
        }
      }
    }
  }
})
