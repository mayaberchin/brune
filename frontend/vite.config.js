import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // moving default built file locations to static so flask can serve it!
  build: {
    outDir: "../app/static/vite",
    emptyOutDir: true, // clear existing files
    rolldownOptions: {
      output: { // make filenames more predicatable you can also do some mapping nonsense...
        entryFileNames: "assets/index.js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: "assets/[name][extname]",
      },
    },
  },
});
