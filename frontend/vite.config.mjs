// vite.config.js

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import frappeui from 'frappe-ui/vite'
import ckeditor5 from '@ckeditor/vite-plugin-ckeditor5'

import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)

export default defineConfig({
  plugins: [
    frappeui({
      frappeProxy: true,
      lucideIcons: true,
      jinjaBootData: true,
      buildConfig: {
        indexHtmlPath: '../go1_cms/www/cms.html',
        emptyOutDir: true,
        sourcemap: true,
      },
    }),
    vue({
      script: {
        propsDestructure: true,
      },
    }),
    ckeditor5({
      theme: require.resolve('@ckeditor/ckeditor5-theme-lark'),
    }),
  ],
  server: {
    port: 8080,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'highlight.js/lib/core': path.resolve(__dirname, 'highlight-fix.js'),
    },
  },
  build: {
    outDir: path.resolve(__dirname, '../go1_cms/public/frontend'), // ✅ cố định rõ ràng
    emptyOutDir: true,
    target: 'es2015',
    sourcemap: true,
    commonjsOptions: {
      include: [/tailwind.config.js/, /node_modules/],
    },
    rollupOptions: {
      output: {
        format: 'esm',
      },
    },
  },
  optimizeDeps: {
    exclude: ['frappe-ui/vite'], // 🔥 tránh externalize-deps lỗi với ESM
    include: [
      'frappe-ui > feather-icons',
      'showdown',
      'tailwind.config.js',
      'engine.io-client',
      'highlight.js',
      'prosemirror-state',
      'prosemirror-view',
      'prosemirror-model',
      'lowlight',
      'package-manager-detector',
      '@antfu/install-pkg',
    ],
    esbuildOptions: {
      format: 'esm',
      mainFields: ['module', 'main'],
      resolveExtensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json'],
    },
  },
  ssr: {
    external: ['frappe-ui/vite'], // 🔥 bắt buộc nếu chạy SSR hoặc dev mode
  },
})
