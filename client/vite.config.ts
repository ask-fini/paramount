import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  const envPath = path.join(__dirname, '../')
  const env = loadEnv(mode, envPath, '')

  return {
    plugins: [react()],
    envDir: envPath,
    define: {
      __APP_ENV__: JSON.stringify(env.APP_ENV),
    },
    resolve: {
      alias: [{ find: '@', replacement: path.resolve(__dirname, './src') }],
    },
    server: {
      port: 3002,
      proxy: {
        '/api': {
          target: 'http://jsonplaceholder.typicode.com',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
  }
})
