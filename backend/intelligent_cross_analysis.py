"""
Cruzamentos inteligentes — atalhos de análise com configuração centralizada.
Regra: filtro período/curso → deduplicação por e-mail (coordinator_analysis).
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from coordinator_analysis import (
    COL_CIDADE,
    COL_CURSO,
    COL_FAIXA_ETARIA,
    COL_NET,
    COL_PC,
    COL_RENDA,
    COL_TRABALHA,
    COL_TRANSPORTE,
    LOW_RENDA_MARKERS,
    apply_period_course_filter,
    build_leaflet_city_cluster_payload,
    build_q1,
    build_q2,
    build_q5,
    build_q7,
    deduplicate_by_email,
)


def _convert(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, dict):
        return {k: _convert(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert(v) for v in obj]
    return obj


def _fig_json(fig) -> dict:
    return _convert(fig.to_plotly_json())


def _require_cols(df: pd.DataFrame, cols: list[str]) -> str | None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        return f"Colunas ausentes na base: {', '.join(missing)}"
    return None


def _share_trabalha_sim(sub: pd.DataFrame) -> float:
    if sub.empty or COL_TRABALHA not in sub.columns:
        return 0.0
    return float((sub[COL_TRABALHA].astype(str).str.lower().eq("sim")).mean())


def _plotly_geo_from_city_spec(
    spec: dict[str, Any], title: str
) -> go.Figure | None:
    markers = spec.get("markers") or []
    if not markers:
        return None
    lats = [float(m["lat"]) for m in markers]
    lngs = [float(m["lng"]) for m in markers]
    sizes = [max(10, min(48, 10 + int(m.get("count", 1)) * 2)) for m in markers]
    texts = [f"{m.get('city', '')}<br>{int(m.get('count', 0))} aluno(s)" for m in markers]
    fig = go.Figure(
        data=[
            go.Scattergeo(
                lat=lats,
                lon=lngs,
                text=texts,
                mode="markers",
                marker=dict(
                    size=sizes,
                    color=[int(m.get("count", 1)) for m in markers],
                    colorscale="Blues",
                    showscale=True,
                    colorbar=dict(title="Alunos"),
                ),
                hovertext=texts,
                hoverinfo="text",
            )
        ]
    )
    fig.update_layout(
        title=title,
        geo=dict(
            scope="south america",
            resolution=50,
            showland=True,
            landcolor="rgb(243,243,243)",
            countrycolor="rgb(204,204,204)",
            lataxis_range=[-34, -22],
            lonaxis_range=[-54, -47],
        ),
        margin=dict(l=0, r=0, t=48, b=0),
    )
    return fig


def build_ic_renda_trabalho(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_RENDA, COL_TRABALHA])
    if err:
        return [], err
    ct = (
        d.groupby([COL_RENDA, COL_TRABALHA], dropna=False)
        .size()
        .reset_index(name="n")
    )
    pivot = ct.pivot_table(
        index=COL_TRABALHA, columns=COL_RENDA, values="n", fill_value=0
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=[str(c) for c in pivot.columns],
            y=[str(i) for i in pivot.index],
            colorscale="Blues",
            hoverongaps=False,
        )
    )
    fig.update_layout(
        title="Renda × trabalho (alunos únicos por e-mail)",
        xaxis_title="Faixa de renda",
        yaxis_title="Trabalha",
    )
    low = d[d[COL_RENDA].isin(LOW_RENDA_MARKERS)]
    high = d[~d[COL_RENDA].isin(LOW_RENDA_MARKERS)]
    sl, sh = _share_trabalha_sim(low), _share_trabalha_sim(high)
    if low.empty and high.empty:
        insight = "Mapa de calor entre faixa de renda e declaração de trabalho."
    elif sl > sh + 0.03:
        insight = (
            f"Alunos nas faixas de renda mais baixas declaram trabalhar em cerca de "
            f"{sl * 100:.0f}% dos casos, contra {sh * 100:.0f}% nas demais faixas — "
            "maior pressão de conciliação estudo-trabalho na base inferior."
        )
    elif sh > sl + 0.03:
        insight = (
            "Nas faixas de renda mais altas há proporção maior de declaração de trabalho "
            "do que nas faixas inferiores — verifique distribuição por curso e idade."
        )
    else:
        insight = (
            "A proporção de quem declara trabalhar é semelhante entre faixas de renda; "
            "o heatmap mostra onde estão as maiores contagens absolutas."
        )
    return [{"title": "Heatmap: renda × trabalho", "fig": _fig_json(fig)}], insight


def build_ic_recursos_renda(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_RENDA, COL_PC, COL_NET])
    if err:
        return [], err
    work = d.copy()
    work["_recursos"] = (
        "Internet: "
        + work[COL_NET].astype(str).str.strip()
        + " · PC: "
        + work[COL_PC].astype(str).str.strip()
    )
    ct = (
        work.groupby([COL_RENDA, "_recursos"], dropna=False)
        .size()
        .reset_index(name="n")
    )
    fig = px.bar(
        ct,
        x=COL_RENDA,
        y="n",
        color="_recursos",
        barmode="stack",
        title="Combinação de internet e computador por faixa de renda",
    )
    top = (
        ct.sort_values("n", ascending=False).iloc[0]
        if len(ct)
        else None
    )
    if top is not None:
        insight = (
            f"A combinação mais frequente é «{top['_recursos']}» na faixa «{top[COL_RENDA]}» "
            f"({int(top['n'])} alunos). Compare barras inferiores vs superiores para políticas de inclusão digital."
        )
    else:
        insight = "Distribuição de acesso a internet e computador por faixa de renda."
    return [{"title": "Recursos educacionais × renda", "fig": _fig_json(fig)}], insight


def build_ic_cidades_map_plotly(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_CIDADE])
    if err:
        return [], err
    spec = build_leaflet_city_cluster_payload(d)
    fig = _plotly_geo_from_city_spec(
        spec, "Distribuição geográfica (cidade declarada — alunos únicos)"
    )
    if fig is None:
        return [], "Não há dados suficientes para o mapa."
    vc = d[COL_CIDADE].fillna("N/D").astype(str).value_counts()
    top_city = str(vc.index[0]) if len(vc) else ""
    insight = (
        f"Concentração em {len(vc)} cidades distintas. "
        f"Maior volume: {top_city} ({int(vc.iloc[0])} alunos) — use o mapa para comparar regiões."
    )
    return [{"title": "Mapa: cidades dos alunos", "fig": _fig_json(fig)}], insight


def build_ic_cidade_transporte_plotly_table(
    d: pd.DataFrame,
) -> tuple[list[dict], str, dict[str, Any]]:
    _leaf, insight_base, rows = build_q7(d)
    err = _require_cols(d, [COL_CIDADE, COL_TRANSPORTE])
    if err:
        return [], err, {}
    spec = build_leaflet_city_cluster_payload(d)
    fig = _plotly_geo_from_city_spec(
        spec, "Alunos por cidade (tamanho ∝ quantidade)"
    )
    extras: dict[str, Any] = {"table_city_transport": rows}
    if fig is None:
        return [], insight_base or "Não há dados suficientes para o mapa.", extras
    out = [{"title": "Mapa: cidade × padrão de deslocamento", "fig": _fig_json(fig)}]
    insight = (
        (insight_base or "")
        + " A tabela resume o meio de transporte mais frequente por cidade (após deduplicação)."
    )
    return out, insight.strip(), extras


def _insight_curso_trabalho(d: pd.DataFrame) -> str:
    err = _require_cols(d, [COL_CURSO, COL_TRABALHA])
    if err:
        return err
    sub = d[d[COL_TRABALHA].astype(str).str.lower().eq("sim")]
    if sub.empty:
        return "Nenhum aluno declara trabalhar com os filtros atuais."
    top = sub[COL_CURSO].value_counts().head(1)
    curso = str(top.index[0])
    n = int(top.iloc[0])
    return (
        f"O curso «{curso}» concentra o maior número de alunos que declaram trabalhar ({n}). "
        f"No total, {len(sub)} alunos únicos trabalham."
    )


def _insight_curso_transporte(d: pd.DataFrame) -> str:
    err = _require_cols(d, [COL_TRANSPORTE])
    if err:
        return err
    vc = d[COL_TRANSPORTE].fillna("N/D").astype(str).value_counts()
    top = str(vc.index[0]) if len(vc) else ""
    pct = float(vc.iloc[0]) / len(d) * 100 if len(d) else 0
    return (
        f"A maioria utiliza «{top}» ({pct:.0f}% dos alunos únicos). "
        "O gráfico agrupado mostra como isso varia por curso."
    )


def _insight_curso_idade(d: pd.DataFrame) -> str:
    err = _require_cols(d, [COL_FAIXA_ETARIA])
    if err:
        return err
    faixa_top = d[COL_FAIXA_ETARIA].astype(str).value_counts().head(1)
    f = str(faixa_top.index[0]) if len(faixa_top) else ""
    return (
        f"A faixa etária mais frequente na base filtrada é «{f}». "
        "O empilhamento mostra o perfil etário dentro de cada curso."
    )


def _insight_cidade_transporte_table(rows: list[dict]) -> str:
    if not rows:
        return "Sem linhas para a tabela de cidades."
    top = rows[0]
    return (
        f"«{top.get('cidade', '')}» reúne {top.get('quantidade', 0)} alunos; "
        f"o meio de transporte mais citado nessa cidade é «{top.get('principal_meio', '')}»."
    )


CrossFn = Callable[[pd.DataFrame], tuple[list[dict], str] | tuple[list[dict], str, dict[str, Any]]]


def _wrap_q1(d: pd.DataFrame) -> tuple[list[dict], str]:
    g, ins = build_q1(d)
    if not g:
        return g, ins
    return g, _insight_curso_transporte(d)


def _wrap_q2(d: pd.DataFrame) -> tuple[list[dict], str]:
    g, ins = build_q2(d)
    if not g:
        return g, ins
    return g, _insight_curso_trabalho(d)


def _wrap_q5(d: pd.DataFrame) -> tuple[list[dict], str]:
    g, ins = build_q5(d)
    if not g:
        return g, ins
    return g, _insight_curso_idade(d)


INTELLIGENT_CROSSINGS: list[dict[str, Any]] = [
    {
        "id": "ic_renda_trabalho",
        "label": "Renda × Trabalho",
        "description": "Heatmap: faixa de renda no eixo X, trabalha (Sim/Não) no eixo Y; intensidade = quantidade de alunos únicos.",
        "chart_type": "heatmap",
    },
    {
        "id": "ic_curso_trabalho",
        "label": "Curso × Trabalho",
        "description": "Barras empilhadas: cursos com maior participação de alunos que trabalham.",
        "chart_type": "bar_stacked",
    },
    {
        "id": "ic_curso_transporte",
        "label": "Curso × Transporte",
        "description": "Barras agrupadas: meio de deslocamento por curso.",
        "chart_type": "bar_grouped",
    },
    {
        "id": "ic_cidade_alunos",
        "label": "Cidade dos alunos",
        "description": "Mapa: bolhas por cidade com tooltip (cidade + quantidade).",
        "chart_type": "map",
    },
    {
        "id": "ic_curso_faixa_etaria",
        "label": "Curso × Faixa etária",
        "description": "Barras empilhadas: perfil etário em cada curso.",
        "chart_type": "bar_stacked",
    },
    {
        "id": "ic_recursos_renda",
        "label": "Recursos educacionais × Renda",
        "description": "Barras empilhadas: combinação de internet e computador por faixa de renda.",
        "chart_type": "bar_stacked",
    },
    {
        "id": "ic_cidade_transporte",
        "label": "Cidade × Transporte",
        "description": "Mapa + tabela: principal meio de transporte por cidade.",
        "chart_type": "map_table",
    },
]

_CROSS_BUILDERS: dict[str, CrossFn] = {
    "ic_renda_trabalho": build_ic_renda_trabalho,
    "ic_curso_trabalho": _wrap_q2,
    "ic_curso_transporte": _wrap_q1,
    "ic_cidade_alunos": build_ic_cidades_map_plotly,
    "ic_curso_faixa_etaria": _wrap_q5,
    "ic_recursos_renda": build_ic_recursos_renda,
    "ic_cidade_transporte": build_ic_cidade_transporte_plotly_table,
}


def run_intelligent_cross_analysis(
    df_raw: pd.DataFrame,
    crossing_id: str,
    periodo: str | None,
    curso: str | None,
) -> dict[str, Any]:
    meta = next((c for c in INTELLIGENT_CROSSINGS if c["id"] == crossing_id), None)
    if not meta:
        return {"error": "Cruzamento inválido."}
    fn = _CROSS_BUILDERS.get(crossing_id)
    if not fn:
        return {"error": "Cruzamento não implementado."}

    filtered = apply_period_course_filter(df_raw, periodo, curso)
    d = deduplicate_by_email(filtered)
    if d.empty:
        return {"error": "Sem dados após filtros e deduplicação por e-mail."}

    period_label = (
        f"{periodo or 'Todos os períodos'}"
        + (f" — {curso}" if curso else "")
        + " · 1 registro por e-mail (última data; empate → maior id)"
    )

    out = fn(d)
    extras: dict[str, Any] = {}
    if len(out) == 3:
        graficos, insight, extras = out[0], out[1], out[2] or {}
    else:
        graficos, insight = out[0], out[1]

    if crossing_id == "ic_cidade_transporte" and extras.get("table_city_transport"):
        insight = (insight + " " + _insight_cidade_transporte_table(
            extras["table_city_transport"]
        )).strip()

    if not graficos:
        return {"error": insight or "Não foi possível gerar a visualização."}

    title = f"Cruzamento Inteligente — {meta['label']}"
    return {
        "title": title,
        "question_id": crossing_id,
        "insight": (insight or "").strip(),
        "graficos": graficos,
        "extras": extras,
        "period_label": period_label,
        "mode": "intelligent_cross",
    }
