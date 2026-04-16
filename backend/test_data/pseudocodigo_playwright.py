"""
Pseudo-código: automação de navegador (Playwright) para o mesmo formulário.
Útil quando for necessário validar JS (ex.: máscara de quantos_filhos) ou fluxo visual.

Instalação:
  pip install playwright
  playwright install chromium

Este arquivo NÃO é executado como teste automatizado no repositório; serve de modelo.
"""

# async def preencher_matricula(page, base_url: str, payload: dict):
#     await page.goto(f"{base_url}/matricula-rematricula")
#     await page.fill('input[name="email"]', payload["email"])
#     await page.select_option('select[name="periodo_ingresso"]', label=payload["periodo_ingresso"])
#     await page.select_option('select[name="curso"]', label=payload["curso"])
#     ...  # demais selects
#     await page.click('button[type="submit"]')
#     # await page.wait_for_load_state("networkidle")
#     return await page.content()
