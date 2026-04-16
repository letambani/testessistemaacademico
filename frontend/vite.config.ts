import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/** Base URL dos assets (local: `/` | GitHub Pages projeto: `/testessistemaacademico/`). */
const base = process.env.VITE_BASE ?? "/";

export default defineConfig({
  base,
  plugins: [react()],
  optimizeDeps: {
    include: ["plotly.js-dist-min"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:5050", changeOrigin: true },
      "/list_files": { target: "http://127.0.0.1:5050", changeOrigin: true },
      "/upload": { target: "http://127.0.0.1:5050", changeOrigin: true },
      "/delete_file": { target: "http://127.0.0.1:5050", changeOrigin: true },
    },
  },
});
