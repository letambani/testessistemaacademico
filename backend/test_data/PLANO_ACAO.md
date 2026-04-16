# Plano de ação (ordem sugerida)

1. **Ler** `ANALISE_CSV_E_FLUXOS.md` e `mapeamento_endpoints.json`.
2. **Gerar dados:** `python generate_fictitious_students.py` → produz `out/alunos_ficticios_50.json` e `out/historico_4_semestres.json`.
3. **Validar payloads** (sem rede): `python automation_matricula_api.py` → `out/relatorio_execucao.json` em modo dry-run; conferir `erros_validacao` vazio.
4. **Subir** `faculdade_app` (porta 5001), opcionalmente `run_stack.py` se quiser SPA + API.
5. **Executar envios:** `python automation_matricula_api.py --execute --base-url http://127.0.0.1:5001` (ajuste `--delay` se necessário).
6. **Conferir** GET `/api/todas-matriculas` e comparar contagem com registros esperados (cada POST adiciona uma linha no banco da faculdade).
7. **Opcional:** rodar fluxo Playwright seguindo `pseudocodigo_playwright.py` para validação E2E no browser.

## Observação sobre “preencher o site”

O script `automation_matricula_api.py` envia o **mesmo corpo** que o formulário HTML envia (`requests.post(..., data=payload)`). Isso é o método usual para testes de integração da API sem dependência de browser. Para Playwright, use o mesmo `form_payload` do JSON.
