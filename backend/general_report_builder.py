"""
Relatório Geral consolidado (pergunta orientada relatorio-geral).
Reutiliza builders de coordinator_analysis; base sempre deduplicada por e-mail após filtros.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px

from coordinator_analysis import (
    COL_CIDADE,
    COL_CURSO,
    COL_RENDA,
    COL_TRABALHA,
    COL_TRANSPORTE,
    LOW_RENDA_MARKERS,
    apply_period_course_filter,
    build_leaflet_city_cluster_payload,
    build_q1,
    build_q11,
    build_q2,
    build_q3,
    build_q5,
    build_q9,
    deduplicate_by_email,
    _fig_json,
)


def _table_city_transport_enriched(d: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for cidade, g in d.groupby(COL_CIDADE):
        top = (
            g[COL_TRANSPORTE]
            .fillna("N/D")
            .astype(str)
            .value_counts()
            .idxmax()
        )
        mod = g[COL_CURSO].dropna().astype(str).mode()
        pred = str(mod.iloc[0]) if len(mod) else ""
        rows.append(
            {
                "cidade": str(cidade),
                "quantidade": int(len(g)),
                "principal_meio": str(top),
                "curso_predominante": pred,
            }
        )
    rows.sort(key=lambda x: -x["quantidade"])
    return rows


def _summary_cards_and_highlights(d: pd.DataFrame) -> tuple[list[dict], dict[str, Any]]:
    n = len(d)
    highlights: dict[str, Any] = {}

    cards: list[dict[str, Any]] = [
        {"label": "Alunos únicos", "value": str(n), "sub": "Último registro por e-mail"},
    ]

    if COL_CURSO in d.columns:
        highlights["totais_por_curso"] = (
            d[COL_CURSO].fillna("N/D").astype(str).value_counts().head(12).to_dict()
        )
        vc = d[COL_CURSO].fillna("N/D").astype(str).value_counts()
        cards.append(
            {
                "label": "Cursos (distintos)",
                "value": str(d[COL_CURSO].nunique()),
                "sub": f"Maior: {vc.index[0]} ({int(vc.iloc[0])})" if len(vc) else "",
            }
        )
        highlights["top_curso"] = str(vc.index[0]) if len(vc) else "—"

    if COL_TRABALHA in d.columns:
        tb = d[COL_TRABALHA].fillna("N/D").astype(str).str.lower()
        sim = int((tb == "sim").sum())
        nao = int((tb == "não").sum() + (tb == "nao").sum())
        cards.append({"label": "Trabalha — Sim", "value": str(sim), "sub": ""})
        cards.append({"label": "Trabalha — Não", "value": str(nao), "sub": ""})
        highlights["pct_trabalha"] = f"{round(100.0 * sim / n, 1)}%" if n else "0%"

    if COL_CIDADE in d.columns:
        vc = d[COL_CIDADE].fillna("N/D").astype(str).value_counts()
        highlights["top_cidade"] = str(vc.index[0]) if len(vc) else "—"
        highlights["totais_por_cidade_top5"] = vc.head(5).to_dict()

    if COL_TRANSPORTE in d.columns:
        vt = d[COL_TRANSPORTE].fillna("N/D").astype(str).value_counts()
        highlights["top_transporte"] = str(vt.index[0]) if len(vt) else "—"

    if COL_RENDA in d.columns:
        highlights["totais_por_renda"] = (
            d[COL_RENDA].fillna("N/D").astype(str).value_counts().head(8).to_dict()
        )

    low_n = len(d[d[COL_RENDA].isin(LOW_RENDA_MARKERS)]) if COL_RENDA in d.columns else 0
    highlights["baixa_renda_n"] = low_n
    cards.append(
        {
            "label": "Baixa renda (faixas definidas)",
            "value": str(int(low_n)),
            "sub": "Ver seção específica",
        }
    )

    return cards, highlights


def _executive_paragraph(d: pd.DataFrame, highlights: dict[str, Any]) -> str:
    n = len(d)
    parts = [
        f"Total de {n} alunos únicos analisados (deduplicação por e-mail no filtro aplicado). "
    ]
    if highlights.get("top_curso"):
        parts.append(f"Maior concentração no curso «{highlights['top_curso']}». ")
    if highlights.get("top_cidade"):
        parts.append(f"Principal cidade: {highlights['top_cidade']}. ")
    if highlights.get("top_transporte"):
        parts.append(f"Transporte mais citado: {highlights['top_transporte']}. ")
    if highlights.get("pct_trabalha"):
        parts.append(f"Declaram trabalhar: {highlights['pct_trabalha']} dos alunos. ")
    br = int(highlights.get("baixa_renda_n", 0) or 0)
    if br > 0:
        parts.append(f"Faixas de renda mais baixas: {br} alunos. ")
    return "".join(parts).strip()


def _add_plotly_section(blocks: list, title: str, graficos: list[dict]) -> None:
    blocks.append({"kind": "section_title", "text": title})
    for g in graficos:
        if g.get("fig"):
            blocks.append(
                {
                    "kind": "plotly",
                    "title": g.get("title", ""),
                    "fig": g["fig"],
                }
            )


def build_general_report_payload(
    df_raw: pd.DataFrame,
    periodo: str | None,
    curso: str | None,
) -> dict[str, Any]:
    filtered = apply_period_course_filter(df_raw, periodo, curso)
    d = deduplicate_by_email(filtered)
    if d.empty:
        return {"error": "Sem dados após filtros e deduplicação por e-mail."}

    period_label = (
        f"{periodo or 'Todos os períodos'}" + (f" — {curso}" if curso else "")
    )

    cards, highlights = _summary_cards_and_highlights(d)
    insight = _executive_paragraph(d, highlights)

    blocks: list[dict[str, Any]] = []

    # Distribuição por curso
    if COL_CURSO in d.columns:
        vc = d[COL_CURSO].fillna("N/D").astype(str).value_counts().reset_index()
        vc.columns = ["curso", "n"]
        fig = px.bar(vc, x="curso", y="n", text="n", title="Alunos únicos por curso")
        fig.update_traces(textposition="outside")
        blocks.append({"kind": "section_title", "text": "Distribuição por curso"})
        blocks.append(
            {
                "kind": "plotly",
                "title": "Quantidade por curso",
                "fig": _fig_json(fig),
            }
        )

    g1, _ = build_q1(d)
    if g1:
        _add_plotly_section(blocks, "Meio de transporte por curso", g1)

    g2, _ = build_q2(d)
    if g2:
        _add_plotly_section(blocks, "Trabalho por curso", g2)

    g3, _ = build_q3(d)
    if g3:
        _add_plotly_section(blocks, "Relação renda × trabalho (heatmap)", g3)

    g5, _ = build_q5(d)
    if g5:
        _add_plotly_section(blocks, "Faixa etária por curso", g5)

    spec_map = build_leaflet_city_cluster_payload(d)
    if spec_map.get("markers"):
        blocks.append({"kind": "section_title", "text": "Cidade onde as pessoas moram"})
        blocks.append(
            {
                "kind": "leaflet",
                "title": "Concentração por cidade",
                "leaflet_cluster_map": spec_map,
            }
        )

    rows_enriched = _table_city_transport_enriched(d)
    if rows_enriched:
        blocks.append({"kind": "section_title", "text": "Cidade × transporte"})
        spec_m2 = build_leaflet_city_cluster_payload(d)
        if spec_m2.get("markers"):
            blocks.append(
                {
                    "kind": "leaflet",
                    "title": "Mapa por cidade",
                    "leaflet_cluster_map": spec_m2,
                }
            )
        blocks.append(
            {
                "kind": "table",
                "title": "Tabela complementar",
                "columns": [
                    "cidade",
                    "quantidade",
                    "principal_meio",
                    "curso_predominante",
                ],
                "rows": rows_enriched,
            }
        )

    g9, _ = build_q9(d)
    if g9:
        _add_plotly_section(blocks, "Recursos educacionais (computador e internet)", g9)

    sub = (
        d[d[COL_RENDA].isin(LOW_RENDA_MARKERS)]
        if COL_RENDA in d.columns
        else pd.DataFrame()
    )
    if not sub.empty and COL_CURSO in sub.columns:
        blocks.append(
            {"kind": "section_title", "text": "Alunos de menor renda por curso"}
        )
        ct = sub.groupby(COL_CURSO).size().sort_values(ascending=True)
        fig = px.bar(
            x=ct.values,
            y=ct.index.astype(str),
            orientation="h",
            title="Concentração (faixas de renda mais baixas)",
            labels={"x": "Alunos únicos", "y": "Curso"},
        )
        blocks.append(
            {
                "kind": "plotly",
                "title": "Baixa renda por curso",
                "fig": _fig_json(fig),
            }
        )

    extras: dict[str, Any] = {}
    work = df_raw.copy()
    if curso and str(curso).strip() and COL_CURSO in work.columns:
        work = work[
            work[COL_CURSO].astype(str).str.strip() == str(curso).strip()
        ]
    r11 = build_q11(work, periodo)
    if not r11.get("error"):
        blocks.append(
            {"kind": "section_title", "text": "Rematrícula — último semestre"}
        )
        blocks.append({"kind": "insight", "text": r11.get("insight", "")})
        if r11.get("extras", {}).get("card"):
            blocks.append({"kind": "remat_card", "card": r11["extras"]["card"]})
        for g in r11.get("graficos", []):
            if g.get("fig"):
                blocks.append(
                    {
                        "kind": "plotly",
                        "title": g.get("title", ""),
                        "fig": g["fig"],
                    }
                )
        lst = list(r11.get("extras", {}).get("table_non_remat") or [])
        for row in lst:
            row.setdefault("nome", "")
        extras["table_non_remat"] = lst
        blocks.append(
            {
                "kind": "section_title",
                "text": "Lista de e-mails não rematriculados",
            }
        )
        blocks.append(
            {
                "kind": "non_remat_table",
                "rows": lst,
                "page_size": 25,
            }
        )
    else:
        blocks.append(
            {
                "kind": "note",
                "text": f"Rematrícula: {r11.get('error', 'dados insuficientes.')}",
            }
        )

    return {
        "title": "Relatório Geral",
        "question_id": "relatorio-geral",
        "insight": insight,
        "period_label": period_label,
        "mode": "coordinator",
        "report_type": "general",
        "general_report": {
            "summary_cards": cards,
            "highlights": highlights,
            "blocks": blocks,
        },
        "extras": extras,
    }
