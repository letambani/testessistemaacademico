/**
 * Copia assets espelhados de backend/static → backend/frontend/public (index-1 + análises).
 * Rode em: cd backend/frontend && npm run sync:index1-assets
 */
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
/** Raiz do repositório (…/backend/frontend/scripts → ../../../) */
const repoRoot = join(__dirname, "..", "..", "..");

const files = [
  ["backend/static/js/scripts.js", "backend/frontend/public/js/scripts.js"],
  ["backend/static/js/index-1-layout.js", "backend/frontend/public/js/index-1-layout.js"],
  ["backend/static/js/tutorial.js", "backend/frontend/public/js/tutorial.js"],
  ["backend/static/css/style.css", "backend/frontend/public/css/style.css"],
  ["backend/static/logo-sem-fundo.png", "backend/frontend/public/logo-sem-fundo.png"],
];

for (const [relFrom, relTo] of files) {
  const from = join(repoRoot, relFrom);
  const to = join(repoRoot, relTo);
  mkdirSync(dirname(to), { recursive: true });
  copyFileSync(from, to);
  console.log("ok", relFrom, "→", relTo);
}
