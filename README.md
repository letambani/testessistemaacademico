# FMP — Sistema académico e painel de análises

Projeto da **Faculdade Municipal de Palhoça (FMP)** com **cadastro**, **login**, **módulo de análises** (gráficos, perguntas orientadas, cruzamento inteligente e assistente de dúvidas) e ligação ao fluxo de **matrícula e rematrícula**.

O código do site (React + Vite) vive dentro de **`backend/frontend/`**. O servidor **Flask** e a API da faculdade ficam em **`backend/`**. O **GitHub Pages** publica apenas o **build estático** (`backend/frontend/dist/`); para dados em tempo real é necessário o Python a correr (máquina local ou servidor).

**Repositório:** [github.com/letambani/testessistemaacademico](https://github.com/letambani/testessistemaacademico)

---

## Fluxo principal (utilizador final)

1. **Cadastro** — `cadastro` (template em `backend/templates/cadastro.html`).
2. **Login** — entrada em `/` com sessão no Flask.
3. **Análises** — após login, `/analises` (template `backend/templates/index-1.html`): escolha de dados, gráficos manuais, perguntas prontas, **cruzamento inteligente** e tour **“Como usar”** (`backend/static/js/tutorial.js`).
4. **Matrícula / rematrícula** — formulário servido pela app da faculdade (porta **5001** por omissão), aberto a partir do painel de análises.

---

## Requisitos

- **Python 3** (recomendado venv na raiz do repo).
- **Node.js 20+** (para `backend/frontend`, ex.: GitHub Actions).
- Rede local se usar matrículas + análises em conjunto (`run_stack.py`).

---

## Arranque rápido (tudo local)

Na **raiz** do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_stack.py
```

- **Faculdade (matrículas / API):** por omissão `http://127.0.0.1:5001`
- **App principal (Flask, análises):** por omissão `http://127.0.0.1:5050`

Variáveis úteis: `FACULDADE_PORT`, `SPA_PORT`, `FMP_ENABLE_CORS`, `FMP_CORS_ORIGINS` (ver `backend/run_stack.py` e `backend/app.py`).

### Só o frontend (Vite) com API no Flask

Com o `run_stack.py` (ou só `app.py` na porta 5050) já a correr:

```bash
cd backend/frontend
npm ci
npm run dev
```

O proxy em `backend/frontend/vite.config.ts` envia `/api`, `/list_files`, `/upload` e `/delete_file` para `http://127.0.0.1:5050`.

### Copiar JS/CSS do Flask para o espelho estático

Depois de editar `backend/static/js/` ou `backend/static/css/` usados pelo `index-1.html` estático:

```bash
cd backend/frontend
npm run sync:index1-assets
```

---

## Estrutura de pastas (resumo)

| Local | Função |
|--------|--------|
| `backend/app.py` | Rotas Flask, APIs de análises, login, cadastro, etc. |
| `backend/faculdade_app.py` | API e formulário de matrícula/rematrícula. |
| `backend/templates/` | HTML servido pelo Flask (`login.html`, `index-1.html`, …). |
| `backend/static/` | CSS, JS e imagens do Flask (inclui `js/tutorial.js` do “Como usar”). |
| `backend/frontend/` | Projeto Vite + React; espelhos HTML e `npm run build` → `dist/`. |
| `backend/tests/` | Testes (`pytest`). |
| `run_stack.py` (raiz) | Chama `backend/run_stack.py` com o diretório de trabalho certo. |
| `requirements.txt` (raiz) | Inclui `backend/requirements.txt`. |
| `.github/workflows/deploy-gh-pages.yml` | Build e deploy do site estático para GitHub Pages. |

Documentação extra de ligações e portas: `backend/CONEXAO_INICIAL.md`.

---

## GitHub Pages

- **Origem do deploy:** GitHub Actions → artefacto = conteúdo de `backend/frontend/dist/`.
- **Base URL do build:** `VITE_BASE=/testessistemaacademico/` (já definido no workflow; ajuste se mudar o nome do repositório).
- **Site estático:** login e páginas espelhadas; sessão “simulada” em `sessionStorage` onde aplicável. Chamadas a `/api/...` precisam do **Flask** acessível (ou meta `fmp-backend-origin` apontando para o servidor certo).
- **Raiz do repo:** `index.html` redireciona para `backend/frontend/index.html` quando alguém abre o repositório como pasta web sem usar o `dist`.

**Settings → Pages:** escolha **GitHub Actions** como fonte. Em **404** em subcaminhos, confirme que o build usou o `VITE_BASE` certo (o Vite injeta `<base href="...">`).

---

## Testes

```bash
cd backend
pytest
```

---

## Alterar textos da interface

| O quê | Onde |
|--------|------|
| Tour “Como usar” no painel de análises | `backend/static/js/tutorial.js` (+ `npm run sync:index1-assets` se usar o HTML em `backend/frontend/`). |
| Textos da página de análises (Flask) | `backend/templates/index-1.html` |
| Mesmas páginas no espelho Vite | `backend/frontend/index-1.html`, `index.html`, `cadastro.html`, … |
| Painel React (dev Vite) | `backend/frontend/src/app/components/*.tsx` |

---

## Git (clonar ou atualizar)

```bash
git clone https://github.com/letambani/testessistemaacademico.git
cd testessistemaacademico
git pull origin main
```

---

**Resumo:** **Pages** = só o build em `backend/frontend/dist` **sem** Python; **funcionalidade completa** = `python run_stack.py` na raiz (com venv e dependências instaladas).
