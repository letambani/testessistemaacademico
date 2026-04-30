import path from "node:path";
import { fileURLToPath } from "node:url";
import type { Plugin } from "vite";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/** Base URL dos assets (local: `/` | GitHub Pages projeto: `/testessistemaacademico/`). */
const base = process.env.VITE_BASE ?? "/";

/** Garante resolução correta de `./cadastro.html` etc. em GitHub Pages (`/repo/`). */
function injectHtmlBase(): Plugin {
  return {
    name: "inject-html-base",
    transformIndexHtml(html) {
      const href = base.endsWith("/") ? base : `${base}/`;
      if (/<base\s/i.test(html)) return html;
      return html.replace(/<head(\s[^>]*)?>/i, `<head$1>\n    <base href="${href}" />`);
    },
  };
}

export default defineConfig({
  base,
  plugins: [react(), injectHtmlBase()],
  build: {
    rollupOptions: {
      input: {
        index: path.resolve(__dirname, "index.html"),
        cadastro: path.resolve(__dirname, "cadastro.html"),
        recuperar: path.resolve(__dirname, "recuperar_senha.html"),
        analises: path.resolve(__dirname, "index-1.html"),
      },
    },
  },
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
