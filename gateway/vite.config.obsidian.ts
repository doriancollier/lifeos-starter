import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    lib: {
      entry: path.resolve(__dirname, 'src/plugin/main.ts'),
      formats: ['cjs'],
      fileName: () => 'main.js',
    },
    rollupOptions: {
      external: [
        'obsidian', 'electron',
        '@codemirror/autocomplete', '@codemirror/collab', '@codemirror/commands',
        '@codemirror/language', '@codemirror/lint', '@codemirror/search',
        '@codemirror/state', '@codemirror/view',
        '@lezer/common', '@lezer/highlight', '@lezer/lr',
      ],
      output: {
        // Obsidian requires a single main.js file - no code splitting
        inlineDynamicImports: true,
        // Ensure `export default` maps to `module.exports`
        exports: 'default',
      },
    },
    outDir: 'dist-obsidian',
    emptyOutDir: true,
    sourcemap: 'inline',
    cssCodeSplit: false,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src/client'),
      '@shared': path.resolve(__dirname, 'src/shared'),
    },
  },
});
