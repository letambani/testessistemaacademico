#!/usr/bin/env python3
"""
Automação equivalente ao preenchimento do formulário: POST application/x-www-form-urlencoded
para /matricula-rematricula (faculdade_app).

Uso:
  python automation_matricula_api.py              # dry-run (só valida payloads locais)
  python automation_matricula_api.py --execute    # envia para BASE_URL (servidor deve estar no ar)

Variáveis de ambiente:
  FACULDADE_BASE_URL  default http://127.0.0.1:5001
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    requests = None  # type: ignore

OUT = Path(__file__).resolve().parent / "out"
HIST = OUT / "historico_4_semestres.json"


def load_timeline() -> list[dict[str, Any]]:
    if not HIST.exists():
        print("Execute antes: python generate_fictitious_students.py", file=sys.stderr)
        sys.exit(1)
    return json.loads(HIST.read_text(encoding="utf-8"))


def run_dry() -> dict[str, Any]:
    from config_mapping import FORM_OPTIONS, FORM_FIELD_ORDER

    timeline = load_timeline()
    erros = []
    ok = 0
    for ev in timeline:
        if ev.get("operacao") == "omitido":
            continue
        pl = ev.get("form_payload") or {}
        event_ok = True
        for key in FORM_FIELD_ORDER:
            if key not in pl:
                erros.append({"evento": ev.get("id_interno"), "semestre": ev.get("semestre_label"), "campo_faltando": key})
                event_ok = False
                continue
            val = pl[key]
            if key in FORM_OPTIONS and val not in FORM_OPTIONS[key]:
                erros.append(
                    {
                        "evento": ev.get("id_interno"),
                        "semestre": ev.get("semestre_label"),
                        "campo": key,
                        "valor": val,
                        "msg": "valor fora das opções do formulário",
                    }
                )
                event_ok = False
        if event_ok:
            ok += 1
    return {
        "modo": "dry_run",
        "eventos_validados_ok": ok,
        "erros_validacao": erros,
        "total_eventos": len(timeline),
    }


def run_execute(base: str, delay_s: float) -> dict[str, Any]:
    if requests is None:
        raise RuntimeError("Instale requests: pip install requests")

    timeline = load_timeline()
    base = base.rstrip("/")
    resultados = []

    for ev in timeline:
        if ev.get("operacao") == "omitido":
            resultados.append({**ev, "http_status": None, "nota": "semestre omitido (simulação)"})
            continue
        pl = dict(ev["form_payload"])
        url = f"{base}/matricula-rematricula"
        t0 = time.perf_counter()
        try:
            r = requests.post(url, data=pl, timeout=60)
            elapsed_ms = int((time.perf_counter() - t0) * 1000)
            resultados.append(
                {
                    "id_interno": ev["id_interno"],
                    "semestre": ev["semestre_label"],
                    "operacao": ev["operacao"],
                    "http_status": r.status_code,
                    "elapsed_ms": elapsed_ms,
                    "response_snippet": (r.text[:500] if r.text else ""),
                    "ok": r.status_code in (200, 302),
                }
            )
        except requests.RequestException as e:
            resultados.append(
                {
                    "id_interno": ev["id_interno"],
                    "semestre": ev["semestre_label"],
                    "erro": str(e),
                    "ok": False,
                }
            )
        time.sleep(delay_s)

    # Valida API
    api_url = f"{base}/api/todas-matriculas"
    try:
        ar = requests.get(api_url, timeout=30)
        api_body = ar.json() if ar.headers.get("content-type", "").startswith("application/json") else []
    except Exception as e:
        api_body = []
        api_err = str(e)
    else:
        api_err = None

    rel = {
        "modo": "execute",
        "base_url": base,
        "resultados_por_evento": resultados,
        "api_todas_matriculas_count": len(api_body) if isinstance(api_body, list) else None,
        "api_erro": api_err,
    }
    return rel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="Enviar POSTs reais")
    ap.add_argument(
        "--base-url",
        default=os.environ.get("FACULDADE_BASE_URL", "http://127.0.0.1:5001"),
    )
    ap.add_argument("--delay", type=float, default=0.05, help="Pausa entre requisições (s)")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    if not args.execute:
        rep = run_dry()
        (OUT / "relatorio_execucao.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return

    rep = run_execute(args.base_url, args.delay)
    (OUT / "relatorio_execucao.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
