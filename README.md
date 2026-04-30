# Sistema acadêmico (SPA + backend)

Monorepo com **tudo sob `backend/`**: API Flask/Python, templates, e o **site estático** (React + Vite) em `backend/frontend/`. O **GitHub Pages** publica só o build em `backend/frontend/dist/`; o servidor Python corre noutro ambiente (local, VPS, etc.).

## Estrutura de pastas

| Pasta / arquivo | Conteúdo |
|-----------------|----------|
| `backend/` | Flask (`app.py`, `faculdade_app.py`), `templates/`, `static/`, modelos, testes, `test_data/`. |
| `backend/frontend/` | Vite + React: `index.html`, `cadastro.html`, `recuperar_senha.html`, `index-1.html` (espelhos dos templates). Build em `backend/frontend/dist/`. |
| `run_stack.py` | Na raiz: delega para `backend/run_stack.py` (API da faculdade + SPA Flask). |
| `requirements.txt` | Na raiz: inclui `backend/requirements.txt`. |
| `.github/workflows/deploy-gh-pages.yml` | Build do Vite e deploy para GitHub Pages (branch `main`). |

## Rodar localmente

### Backend (stack completo Flask)

Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_stack.py
```

Portas padrão: faculdade **5001**, SPA principal **5050** (ajustável com `FACULDADE_PORT` e `SPA_PORT`). Detalhes em `backend/run_stack.py`.

### Site estático / Vite (desenvolvimento com proxy para API)

Com o backend atendendo em `5050`, noutro terminal:

```bash
cd backend/frontend
npm ci
npm run dev
```

O Vite (`backend/frontend/vite.config.ts`) encaminha `/api`, `/list_files`, `/upload` e `/delete_file` para `http://127.0.0.1:5050`.

### Build de produção (GitHub Pages)

Para o mesmo **base path** do repositório `testessistemaacademico`:

```bash
cd backend/frontend
VITE_BASE=/testessistemaacademico/ npm run build
```

Saída em `backend/frontend/dist/`. Para `npm run preview`, use o mesmo `VITE_BASE` se quiser simular o caminho do Pages.

### Sincronizar assets do Flask para o espelho estático

Após alterar `backend/static/js/` ou CSS usados pelo `index-1.html` estático:

```bash
cd backend/frontend
npm run sync:index1-assets
```

## GitHub Pages

- **O que é publicado:** o conteúdo de `backend/frontend/dist` (HTML, JS, CSS, assets). O workflow usa `VITE_BASE=/testessistemaacademico/`.
- **Fluxo no site estático:** `index.html` (login). Após **Entrar**, **`index-1.html`**. Sessão em `sessionStorage` (`fmp_gh_pages_auth`); **Sair** volta ao login. Em dev: `http://localhost:5173/index-1.html` com proxy para o Flask em `5050`.
- **Cadastro / recuperar senha:** equivalentes aos templates em `backend/templates/`. POST para `{fmp-backend-origin}/cadastro` e `/recuperar_senha`. Suba o backend com `python run_stack.py` e ajuste **`fmp-backend-origin`** se necessário.
- **O que não roda no Pages:** Python/Flask, SQLite, uploads e rotas de API sem backend atrás.
- **Settings → Pages:** origem **GitHub Actions**; workflow **Deploy frontend to GitHub Pages** no push para `main`.

### O site abre o README em vez da tela de login?

Na raiz do repo existe **`index.html`** que redireciona para **`backend/frontend/index.html`** (login em cópia de ficheiros; o deploy recomendado é o **dist** do workflow).

1. **Settings → Pages** → **Source: GitHub Actions**.
2. Confirme que o workflow terminou com sucesso em **Actions**.

### 404 em `/cadastro.html` no Pages

Com subcaminho (`/testessistemaacademico/`), o build do Vite injeta `<base href="...">`. Use o workflow com `VITE_BASE` correto.

## Testes (backend)

```bash
cd backend
pytest
```

## Comandos Git (primeiro envio ao remoto)

Substitua a mensagem de commit conforme necessário.

```bash
cd /caminho/para/ProjetoSpa14-04-2026100-FuncionalcomIA

git init
git branch -M main
git remote add origin https://github.com/letambani/testessistemaacademico.git

git add .
git status
git commit -m "Estrutura: backend/ com Flask + frontend Vite e deploy GitHub Pages"

git push -u origin main
```

Se o repositório remoto já tiver histórico:

```bash
git pull origin main --rebase
git push -u origin main
```

---

Resumo: **GitHub Pages = build estático em `backend/frontend/dist`**; **stack completo = `python run_stack.py`** (na raiz ou `cd backend && python run_stack.py`).
