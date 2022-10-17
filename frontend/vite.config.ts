import { defineConfig } from 'vite';
import solidPlugin from 'vite-plugin-solid';

export default defineConfig({
  plugins: [solidPlugin()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      '/api': 'http://localhost:5000',
      '/auth': 'http://localhost:5000',
      '/logout': 'http://localhost:5000',
      '/socket.io': {
        target: 'ws://localhost:5000',
        changeOrigin: true,
        ws: true
      }
    }
  },
  build: {
    target: 'esnext',
  },
});
