import { defineConfig } from 'vite';
import solidPlugin from 'vite-plugin-solid';

export default defineConfig({
  plugins: [solidPlugin()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
      '/auth': 'http://localhost:5000',
      '/logout': 'http://localhost:5000',
      '/socket.io': {
        target: 'ws://localhost:5000',
        changeOrigin: true,
        ws: true
      }
    },
    port: 3000,
  },
  build: {
    target: 'esnext',
  },
});
