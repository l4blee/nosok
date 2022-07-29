import { defineConfig } from 'vite';
import solidPlugin from 'vite-plugin-solid';

export default defineConfig({
  plugins: [solidPlugin()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
      '/signin': 'http://localhost:5000',
      '/signup': 'http://localhost:5000',
      '/logout': 'http://localhost:5000',
      '/secret': 'http://localhost:5000',
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
