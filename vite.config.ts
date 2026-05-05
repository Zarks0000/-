import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import { UnifiedViteWeappTailwindcssPlugin as weappTwPlugin } from 'weapp-tailwindcss/vite'
import path from 'path'
import tailwindcss from 'tailwindcss'
import autoprefixer from 'autoprefixer'
import postcssRemToRpx from 'postcss-rem-to-responsive-pixel'

const isH5 = process.env.UNI_PLATFORM === 'h5' || process.argv.includes('h5') || process.argv.includes('dev:h5')

export default defineConfig({
  build: {
    sourcemap: 'hidden',
  },
  css: {
    postcss: {
      plugins: [
        tailwindcss(),
        autoprefixer(),
        postcssRemToRpx({
          rootValue: 32,
          propList: ['*'],
          transformUnit: 'rpx',
        }),
      ],
    },
  },
  plugins: [
    (uni as any).default ? (uni as any).default() : uni(),
    // @ts-ignore
    !isH5 ? weappTwPlugin() : undefined,
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  optimizeDeps: {
    include: ['lucide-vue-next'],
  },
})
