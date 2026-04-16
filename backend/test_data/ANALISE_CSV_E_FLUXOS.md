# Análise: 2024.csv, 2025.csv × formulário web × API

## 1. Natureza dos arquivos CSV

| Aspecto | 2024.csv | 2025.csv |
|--------|----------|----------|
| Origem típica | Exportação de formulário (ex.: Google Forms) | Idem, questionário evoluído |
| Colunas (aprox.) | 31 | 33 |
| Primeira coluna | Carimbo de data/hora | Idem |
| Identificação do respondente | **Não há e-mail nem CPF** nas colunas (anonimizado agregado) | Idem |

### Diferenças relevantes entre anos

- **2025** inclui: nacionalidade; pergunta sobre ensino superior dos pais; renda como “renda per capita familiar”; redação diferente para dificuldade com tecnologia; remove colunas separadas Facebook/Instagram e unifica “segue nas redes”; não replica o bloco detalhado de alimentação do 2024 em alguns itens.
- **Valores categóricos** (meios de divulgação, bairros, cursos) são **livres** no CSV (texto longo), enquanto o **site atual** (`matricula.html`) usa **listas fechadas** (`<select>`).

**Hipótese adotada:** os CSVs são a **fonte de domínio e vocabulário**; o **contrato técnico** para automação é o **POST do formulário** em `faculdade_app`, não uma importação linha a linha do CSV.

---

## 2. Formulário web (matrícula / rematrícula)

- **URL:** `POST /matricula-rematricula` no app da faculdade (porta **5001** por padrão).
- **Campos:** ver `FIELD_NAMES` em `config_mapping.py` (espelho dos `name="..."` do HTML).
- **Regra de negócio (servidor):** primeiro envio com um **e-mail** → `tipo_matricula = "Matrícula"`; mesmo e-mail já existente → `"Rematrícula"`.

Não há no HTML: **CPF, RG, telefone, endereço completo, responsáveis, turno, unidade** — esses entram na **modelagem fictícia** para rastreio e relatório, mas **não** são enviados a este endpoint.

---

## 3. APIs identificadas

| Etapa | Método | Endpoint | Observação |
|-------|--------|----------|------------|
| Envio do formulário | POST | `/matricula-rematricula` | `application/x-www-form-urlencoded` ou multipart (Flask `request.form`) |
| Listagem para o SPA / gráficos | GET | `/api/todas-matriculas` | JSON array; opcional `?tipo=Matrícula` ou `Rematrícula` |
| Cadastro de usuário no SPA (login) | GET/POST | `/cadastro`, `/login` | **Outro fluxo** (CPF, senha forte, e-mail `@aluno.fmpsc.edu.br`) — não obrigatório para popular a API da faculdade |

---

## 4. Ambiguidades e decisões

1. **Curso no CSV** (“Tecnólogo em Análise e Desenvolvimento de Sistemas”) **vs** select (“Análise e Desenvolvimento de Sistemas”) → usar **mapeamento explícito** em `config_mapping.py`.
2. **Período:** CSV `2024/01` → formulário `2024/1º`.
3. **Faixa etária:** CSV usa faixas tipo “Entre 22 e 26 anos”; formulário usa “18 - 22 anos”, etc. → **mapeamento aproximado** por idade sintética.
4. **Simulação de 4 semestres:** cada “semestre” é um **envio** com mesma identidade (e-mail), incrementando **fase** e, se desejado, ajustando `periodo_ingresso` apenas quando coerente; **matrícula inicial** = primeiro envio; **rematrículas** = envios seguintes (comportamento do backend).

---

## 5. Estratégia de automação

1. **Gerar** 50 perfis + identificadores sintéticos → `alunos_ficticios_50.json`.
2. **Planejar** 4 ondas (semestres) → `historico_4_semestres.json` (matrícula vs rematrícula por linha do tempo).
3. **Executar** (opcional): `requests` para POST (equivalente ao preenchimento do formulário, sem Playwright obrigatório). Playwright só se for necessário validar JS/máscaras no navegador.
4. **Validar:** GET `/api/todas-matriculas` e conferir contagem e presença de e-mails esperados.
5. **Registrar:** `relatorio_execucao.json` por aluno e por requisição.

---

## 6. Dados pessoais

Todos os nomes, CPFs, RGs, telefones e endereços são **gerados algoritmicamente** para teste, sem correspondência com pessoas reais.
