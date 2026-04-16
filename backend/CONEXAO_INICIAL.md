# Conexão inicial — passo a passo

Este guia cobre o primeiro uso do ambiente local: dependências, variáveis, subida do **SPA** (Flask) e da **API Faculdade**, e como validar que tudo está conectado.

## 1. Pré-requisitos

- **Python** 3.12 ou superior (o projeto declara suporte a wheels para 3.12+; em 3.14 use `numpy>=2.1` conforme `requirements.txt`).
- Terminal com acesso ao diretório do repositório.

## 2. Entrar na pasta da aplicação

```bash
cd backend
```

Os comandos abaixo assumem que o diretório atual é `backend` (onde estão `app.py`, `faculdade_app.py`, `config.py` e `requirements.txt`).

## 3. Ambiente virtual (recomendado)

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows (cmd/PowerShell)
```

## 4. Instalar dependências

**Sem venv ainda:** use o módulo `pip` pelo Python (evita `command not found: pip` no macOS):

```bash
python3 -m pip install -r requirements.txt
```

**Com o venv ativado** (`source .venv/bin/activate`), pode usar `pip` ou o mesmo padrão:

```bash
python3 -m pip install -r requirements.txt
```

Se aparecer `zsh: command not found: pip`, não use `pip` sozinho — use sempre `python3 -m pip` (ou `python -m pip` depois de ativar o `.venv`).

## 5. Variáveis de ambiente (opcional)

O app carrega um arquivo `.env` na raiz de `backend` (via `python-dotenv` em `app.py`). Crie `backend/.env` se quiser sobrescrever padrões.

| Variável | Função | Padrão (se não definir) |
|----------|--------|-------------------------|
| `SECRET_KEY` | Segredo do Flask | Valor de desenvolvimento em `config.py` |
| `DATABASE_URL` | Banco do SPA (SQLAlchemy) | `sqlite:///spa.db` |
| `FACULDADE_API_BASE_URL` | URL base da API da faculdade consumida pelo SPA | `http://127.0.0.1:5001` |
| `FACULDADE_FALLBACK_CSV` | CSV em `uploads/` quando a API não retorna dados (modo demo) | `2024.csv` |
| `GEMINI_API_KEY` | Chat de análises com IA (opcional) | vazio |
| `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` | Envio de e-mail | vazio |
| `FACULDADE_PORT` | Porta do `faculdade_app.py` | `5001` |
| `SPA_PORT` | Porta do `app.py` | `5050` (evita conflito com AirPlay no macOS) |
| `SEED_FACULDADE` | Popular dados fictícios na API faculdade (`0` desliga) | `1` |

Para só subir tudo com portas padrão, **não é obrigatório** criar `.env`.

## 6. Subir os dois serviços (forma recomendada)

O SPA chama a API da faculdade em `FACULDADE_API_BASE_URL`. O script `run_stack.py` sobe os dois processos e define `FACULDADE_API_BASE_URL` para a porta da faculdade.

```bash
python run_stack.py
```

Saída esperada no terminal (valores padrão):

- **API Faculdade:** `http://127.0.0.1:5001`
- **SPA:** `http://127.0.0.1:5050`

Encerre com **Ctrl+C** (os dois processos são terminados).

**Portas alternativas** (se 5050/5001 estiverem ocupadas):

```bash
FACULDADE_PORT=5002 SPA_PORT=5060 python run_stack.py
```

Nesse caso, o stack ajusta `FACULDADE_API_BASE_URL` para `http://127.0.0.1:5002` automaticamente.

## 7. Subir manualmente (dois terminais)

Se preferir não usar `run_stack.py`:

**Terminal A — API Faculdade**

```bash
cd backend
source .venv/bin/activate
python faculdade_app.py
```

**Terminal B — SPA** (a URL da faculdade deve bater com a porta do Terminal A)

```bash
cd backend
source .venv/bin/activate
export FACULDADE_API_BASE_URL=http://127.0.0.1:5001
python app.py
```

Na primeira execução, `faculdade_app.py` cria as tabelas e pode rodar o seed de dados fictícios (se o banco estiver vazio e `SEED_FACULDADE` não for `0`). O `app.py` cria as tabelas do banco do SPA ao iniciar.

## 8. Verificar a conexão

1. Abra o navegador em **http://127.0.0.1:5050** (SPA). A raiz `/` redireciona para `/login` (tela de login).
2. Teste a API da faculdade, por exemplo: **http://127.0.0.1:5001/api/todas-matriculas** (rota usada pelo SPA para dados agregados; o caminho exato pode variar conforme `faculdade_app.py`).

Se o SPA mostrar erro ao buscar matrículas, confira se a API na porta configurada em `FACULDADE_API_BASE_URL` está no ar e se não há bloqueio de firewall local.

## 9. Bancos de dados (SQLite)

- **SPA:** URI padrão `sqlite:///spa.db` — arquivo criado no diretório de trabalho (em geral `backend/`), salvo se você definir `DATABASE_URL` com caminho absoluto.
- **Faculdade:** `sqlite:///banco_faculdade.db` em `faculdade_app.py` — mesmo critério de diretório de trabalho.

Para **forçar novo seed** na API faculdade, apague o arquivo SQLite da faculdade e suba `faculdade_app.py` de novo (veja comentários em `seed_faculdade_db.py`).

## 10. Página em branco na porta 5000 (macOS)

No **macOS**, a porta **5000** costuma ser usada pelo **AirPlay Receiver**. Nesse caso, o navegador pode mostrar página vazia ou outro serviço — não o Flask. Este projeto usa **5050** como porta padrão do SPA justamente para evitar esse conflito.

Se ainda quiser usar 5000: **Ajustes → Geral → AirDrop e Handoff** e desligue **Receptor AirPlay**, ou defina outra porta: `SPA_PORT=5060 python run_stack.py`.

### `ERR_CONNECTION_REFUSED` em http://127.0.0.1:5050

Nada está escutando nessa porta: o servidor **não está rodando** ou o **`app.py` terminou com erro** (por exemplo, `python` sem o venv — falta o pacote `python-dotenv`). Deixe o terminal aberto com `python run_stack.py` ativo e use sempre:

`cd backend && source .venv/bin/activate && python run_stack.py`

Se o `run_stack` imprimir que `app.py` encerrou ao iniciar, copie o traceback do terminal (geralmente `ModuleNotFoundError`) e rode `python3 -m pip install -r requirements.txt` **com o venv ativado**.

## 11. Testes automatizados (opcional)

Com o ambiente virtual ativo:

```bash
pytest
```

## Resumo rápido

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r requirements.txt
python run_stack.py
# Navegador: http://127.0.0.1:5050
```
