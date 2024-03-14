import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { ViteToml } from 'vite-plugin-toml'

export default defineConfig(({ mode }) => {
  const envPath = path.join(__dirname, '../../')
  const env = loadEnv(mode, envPath, '')

  return {
    plugins: [react(), ViteToml()],
    envDir: envPath,
    define: {
      __APP_ENV__: JSON.stringify(env.APP_ENV),
    },
    resolve: {
      alias: [{ find: '@', replacement: path.resolve(__dirname, './src') }],
    },
    server: {
      host: true,
      port: 3002,
      proxy: {
        '/api': {
          target: env.PARAMOUNT_API_ENDPOINT,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
  }
})
