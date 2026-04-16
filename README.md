# Sistema acadêmico (SPA + backend)

Monorepo com **frontend** (React + Vite, estático) e **backend** (Flask/Python). O site público no **GitHub Pages** publica apenas o build estático do frontend; o backend precisa rodar em outro ambiente (máquina local, VPS, etc.).

## Estrutura de pastas

| Pasta / arquivo | Conteúdo |
|-----------------|----------|
| `frontend/` | `index.html` (login), `cadastro.html` (espelho de `backend/templates/cadastro.html`), `index-1.html` (análises). Build em `frontend/dist/`. |
| `backend/` | Flask (`app.py`, `faculdade_app.py`), templates HTML, `static/`, modelos, testes, `test_data/`. |
| `run_stack.py` | Na raiz: delega para `backend/run_stack.py` (sobe API da faculdade + SPA Flask conforme script). |
| `requirements.txt` | Na raiz: inclui `backend/requirements.txt`. |
| `.github/workflows/deploy-gh-pages.yml` | Build do frontend e deploy para GitHub Pages (branch `main`). |

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

### Frontend (desenvolvimento com proxy para API)

Com o backend atendendo em `5050` (ou a porta que o Vite apontar no proxy), em outro terminal:

```bash
cd frontend
npm ci
npm run dev
```

O Vite (`frontend/vite.config.ts`) encaminha `/api`, `/list_files`, `/upload` e `/delete_file` para `http://127.0.0.1:5050`.

### Build de produção do frontend

Para o mesmo **base path** do GitHub Pages (repositório `testessistemaacademico`):

```bash
cd frontend
VITE_BASE=/testessistemaacademico/ npm run build
```

Saída em `frontend/dist/`. Para desenvolvimento local com `npm run preview`, use o mesmo `VITE_BASE` se quiser simular o caminho do Pages.

## GitHub Pages

- **O que é publicado:** apenas o conteúdo estático gerado em `frontend/dist` (HTML, JS, CSS, assets). O workflow faz o build com `VITE_BASE=/testessistemaacademico/`.
- **Fluxo no site estático:** `index.html` (login). Após **Entrar**, **`index-1.html`** (mesmo layout que `backend/templates/index-1.html`). Sessão em `sessionStorage` (`fmp_gh_pages_auth`); **Sair** volta ao login. Em dev: `http://localhost:5173/index-1.html` após login (o proxy Vite encaminha `/api` ao Flask se estiver em `5050`).
- **Cadastro:** o botão **Cadastrar** no login abre **`cadastro.html`** (mesmo conteúdo visual do template Flask). O **envio** do formulário faz POST para `{fmp-backend-origin}/cadastro` — é preciso o Flask ativo (`python run_stack.py`). **Esqueci a senha** e **Quem somos** continuam indo direto ao Flask (`/recuperar_senha`, `/quem_somos`). Ajuste a meta **`fmp-backend-origin`** se o backend não estiver em `http://127.0.0.1:5050`.
- **O que não roda no Pages:** Python/Flask, SQLite, uploads e qualquer rota de API. No site estático, chamadas a `/api/...` não têm servidor Flask atrás; a interface pode carregar, mas **dados em tempo real e integrações com o backend exigem o backend em execução** (local ou hospedado) ou uma URL de API configurável no futuro.
- **Configuração no GitHub:** em **Settings → Pages → Build and deployment**, escolha **GitHub Actions** como origem. O workflow `Deploy frontend to GitHub Pages` dispara em push para `main`.
- **URL típica do site de projeto:** `https://letambani.github.io/testessistemaacademico/` (caminho base `/testessistemaacademico/` já considerado no build).

### O site abre o README em vez da tela de login?

Isso acontece quando o Pages publica a **árvore do repositório** (branch `main` na raiz ou pasta `/docs`), onde **não existe** `index.html` na origem publicada — o GitHub acaba exibindo o `README.md`.

**Correção:**

1. No repositório: **Settings → Pages → Build and deployment**.
2. Em **Source**, selecione **GitHub Actions** (não “Deploy from a branch”).
3. Confirme que o workflow **Deploy frontend to GitHub Pages** concluiu com sucesso em **Actions** (último push em `main`).
4. Aguarde alguns minutos e abra de novo: `https://letambani.github.io/testessistemaacademico/` — deve carregar o **`index.html`** gerado em `frontend/dist` (login).

Se a origem já for **GitHub Actions** e ainda aparecer o README, abra **Actions**, verifique se o job falhou, e em **Settings → Pages** veja qual deploy está ativo (às vezes é preciso um novo push ou **Run workflow** manual).

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
git commit -m "Estrutura monorepo: frontend (Vite) + backend (Flask) e deploy GitHub Pages"

git push -u origin main
```

Se o repositório remoto já tiver histórico e for preciso integrar:

```bash
git pull origin main --rebase
git push -u origin main
```

---

Resumo: **GitHub Pages = só o frontend buildado**; **funcionalidade completa com API e banco = use `python run_stack.py` (ou equivalente) no `backend/`**.
