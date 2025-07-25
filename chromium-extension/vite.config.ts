import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import { viteStaticCopy } from "vite-plugin-static-copy"
import { resolve } from 'path'

export default defineConfig({
    build: {
        outDir: 'dist',
        emptyOutDir: true,
        rollupOptions: {
            input: {
                popup: resolve(__dirname, 'src/popup/index.html'),
                contentScript: resolve(__dirname, 'src/scripts/contentScript.ts'),
                serviceWorker: resolve(__dirname, 'src/scripts/serviceWorker.ts'),
            },
            output: {
                entryFileNames: chunk => {
                    if (chunk.name === 'contentScript') return 'scripts/contentScript.js'
                    if (chunk.name === 'serviceWorker') return 'scripts/serviceWorker.js'
                    if (chunk.name === 'popup') return 'popup/popup.js'
                    return 'popup/[name].js'
                },
                assetFileNames: asset => {
                    const name = asset.name || ''
                    if (name.includes('icon')) return 'assets/[name].[ext]'
                    return 'popup/[name].[ext]'
                }
            }
        }
    },
    plugins: [
        tailwindcss(),
        viteStaticCopy({
            targets: [
                { src: 'src/manifest.json', dest: '.' },
                { src: 'src/assets/*', dest: 'assets' }
            ]
        }),
    ]
})
