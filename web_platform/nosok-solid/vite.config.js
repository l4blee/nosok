import { defineConfig } from 'vite';
import solidPlugin from 'vite-plugin-solid';

export default defineConfig({
  plugins: [solidPlugin()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
      '/socket.io': {
        target: 'ws://localhost:5000',
        ws: true
      }
    },
    port: 3000,
  },
  build: {
    target: 'esnext',
  },
});