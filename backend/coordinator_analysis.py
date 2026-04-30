"""
Análises orientadas por perguntas de coordenadores — configuração centralizada e builders.
Regra global: deduplicar por e-mail (último registro por critério de data/id), exceto Q11
que usa série temporal por semestre.
"""
from __future__ import annotations

import hashlib
import io
import re
import unicodedata
from typing import Any, Callable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# --- Colunas canônicas (API faculdade / CSV alinhados) ---
COL_EMAIL = "E-mail"
COL_CURSO = "Curso"
COL_PERIODO = "Período de Ingresso"
COL_TIPO = "Tipo de Matrícula"
COL_TRANSPORTE = "Meio de Transporte"
COL_TRABALHA = "Trabalha"
COL_RENDA = "Faixa de Renda"
COL_FAIXA_ETARIA = "Faixa Etária"
COL_CIDADE = "Cidade"
COL_PC = "Possui Computador"
COL_NET = "Acesso Internet"
ORDER_DATE_COLS = (
    "updated_at",
    "submitted_at",
    "created_at",
    "data_matricula",
    "data_rematricula",
    "Data Matrícula",
    "Data Rematrícula",
)

# Coordenadas aproximadas (SC / cidades frequentes no formulário) — fallback sem geocoding externo
CITY_COORDS: dict[str, tuple[float, float]] = {
    "palhoça": (-27.5954, -48.5548),
    "são josé": (-27.5954, -48.6367),
    "santo amaro da imperatriz": (-27.6882, -48.7817),
    "santo amaro": (-27.6882, -48.7817),
    "biguaçu": (-27.4941, -48.6556),
    "paulo lopes": (-27.9606, -48.6847),
    "florianópolis": (-27.5954, -48.5480),
    "são pedro de alcântara": (-27.5667, -48.8000),
    "tubarão": (-28.4833, -49.0069),
    "criciúma": (-28.6778, -49.3697),
    "joinville": (-26.3044, -48.8461),
    "blumenau": (-26.9194, -49.0661),
    "itajaí": (-26.9078, -48.6619),
    "chapecó": (-27.0964, -52.6182),
    "curitiba": (-25.4284, -49.2733),
    "porto alegre": (-30.0346, -51.2177),
    "são paulo": (-23.5505, -46.6333),
    "rio de janeiro": (-22.9068, -43.1729),
    "belo horizonte": (-19.9167, -43.9345),
    "brasília": (-15.7942, -47.8822),
    "salvador": (-12.9714, -38.5014),
    "fortaleza": (-3.7319, -38.5267),
    "recife": (-8.0476, -34.8770),
    "manaus": (-3.1190, -60.0217),
    "belém": (-1.4558, -48.5039),
    "outro": (-27.6000, -48.6000),
}

LOW_RENDA_MARKERS = (
    "500,00 - 1000,00",
    "1100,00 - 1700,00",
    "1800,00 - 2300,00",
)


def _norm_city(s: str) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower())


def city_lat_lon(cidade: str) -> tuple[float | None, float | None]:
    k = _norm_city(cidade)
    if k in CITY_COORDS:
        return CITY_COORDS[k]
    for name, ll in CITY_COORDS.items():
        if name in k or k in name:
            return ll
    return None, None


def fallback_city_coords(cidade: str) -> tuple[float, float]:
    """
    Coordenadas determinísticas para cidades sem entrada em CITY_COORDS
    (pequeno deslocamento para não sobrepor todas no mesmo ponto).
    """
    h = hashlib.md5(_norm_city(cidade).encode("utf-8")).hexdigest()
    i, j = int(h[:8], 16), int(h[8:16], 16)
    lat = -27.59 + ((i % 1000) / 1000.0 - 0.5) * 0.85
    lng = -48.55 + ((j % 1000) / 1000.0 - 0.5) * 0.85
    return float(lat), float(lng)


def build_leaflet_city_cluster_payload(d: pd.DataFrame) -> dict[str, Any]:
    """
    Dados para mapa Leaflet + MarkerCluster: bolhas por cidade, zoom via bounds.
    """
    vc = d[COL_CIDADE].fillna("N/D").astype(str).value_counts()
    markers: list[dict[str, Any]] = []
    lats: list[float] = []
    lngs: list[float] = []
    for cidade, n in vc.items():
        la, lo = city_lat_lon(str(cidade))
        if la is None or lo is None:
            la, lo = fallback_city_coords(str(cidade))
        la, lo = float(la), float(lo)
        markers.append(
            {
                "lat": la,
                "lng": lo,
                "city": str(cidade),
                "count": int(n),
            }
        )
        lats.append(la)
        lngs.append(lo)
    if not markers:
        return {}
    pad = 0.15
    sw = [min(lats) - pad, min(lngs) - pad]
    ne = [max(lats) + pad, max(lngs) + pad]
    return {"markers": markers, "bounds": [sw, ne]}


def period_sort_key(val: Any) -> tuple:
    s = str(val)
    m = re.search(r"(\d{4}).*?(\d)", s)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return (0, 0)


def _pick_sort_column(df: pd.DataFrame) -> str | None:
    for c in ORDER_DATE_COLS:
        if c in df.columns:
            return c
    if "id" in df.columns:
        return "id"
    return None


def deduplicate_by_email(df: pd.DataFrame) -> pd.DataFrame:
    """Um registro por e-mail: último por data conhecida ou maior id."""
    if df.empty:
        return df
    d = df.copy()
    if COL_EMAIL not in d.columns:
        alt = [c for c in d.columns if "mail" in c.lower()]
        if not alt:
            return d
        d = d.rename(columns={alt[0]: COL_EMAIL})
    d[COL_EMAIL] = d[COL_EMAIL].astype(str).str.strip().str.lower()
    ord_col = _pick_sort_column(d)
    if ord_col:
        try:
            d[ord_col] = pd.to_datetime(d[ord_col], errors="coerce")
        except Exception:
            pass
        sort_cols: list[str] = [ord_col]
        sort_asc: list[bool] = [True]
        if "id" in d.columns:
            sort_cols.append("id")
            sort_asc.append(True)
        d = d.sort_values(sort_cols, ascending=sort_asc, na_position="first")
    elif "id" in d.columns:
        d = d.sort_values("id", ascending=True, na_position="first")
    else:
        d = d.reset_index(drop=True)
    out = d.drop_duplicates(subset=[COL_EMAIL], keep="last")
    return out


def apply_period_course_filter(
    df: pd.DataFrame, periodo: str | None, curso: str | None
) -> pd.DataFrame:
    d = df.copy()
    if periodo and str(periodo).strip() and COL_PERIODO in d.columns:
        d = d[d[COL_PERIODO].astype(str).str.strip() == str(periodo).strip()]
    if curso and str(curso).strip() and COL_CURSO in d.columns:
        d = d[d[COL_CURSO].astype(str).str.strip() == str(curso).strip()]
    return d


def _ascii_lower(s: str) -> str:
    return (
        unicodedata.normalize("NFKD", str(s))
        .encode("ascii", "ignore")
        .decode()
        .lower()
    )


def transport_class(meio: str) -> str:
    m = _ascii_lower(meio)
    if m in ("", "nan", "none"):
        return "Não informado"
    if any(x in m for x in ("onibus", "app")):
        return "Transporte coletivo / apps"
    if any(x in m for x in ("carro", "moto", "bicicleta")):
        return "Transporte próprio"
    if "nenhum" in m:
        return "Nenhum"
    return "Outros"


COORDINATOR_QUESTIONS: list[dict[str, Any]] = [
    {
        "id": "q1",
        "label": "Qual o meio de transporte mais utilizado pelos alunos e como ele varia por curso?",
        "description": "Barras agrupadas: curso × quantidade, cor = meio de transporte.",
        "chart_type": "bar_grouped",
    },
    {
        "id": "q2",
        "label": "Qual o perfil de alunos que trabalham atualmente e como isso se distribui entre os cursos?",
        "description": "Barras empilhadas: curso × quantidade, segmentação Sim/Não em trabalha.",
        "chart_type": "bar_stacked",
    },
    {
        "id": "q3",
        "label": "Existe relação entre renda familiar e a necessidade de trabalhar durante o curso?",
        "description": "Mapa de calor entre faixa de renda e situação de trabalho.",
        "chart_type": "heatmap",
    },
    {
        "id": "q4",
        "label": "Quais cursos concentram maior número de alunos que precisam conciliar estudo e trabalho?",
        "description": "Barras horizontais ordenadas (alunos que trabalham = Sim).",
        "chart_type": "bar_h",
    },
    {
        "id": "q5",
        "label": "Qual a faixa etária predominante em cada curso?",
        "description": "Barras empilhadas por curso e faixa etária.",
        "chart_type": "bar_stacked_age",
    },
    {
        "id": "q6",
        "label": "Cidade onde as pessoas moram",
        "description": "Mapa de bolhas por cidade (coordenadas aproximadas).",
        "chart_type": "map",
    },
    {
        "id": "q7",
        "label": "De quais cidades/regiões vêm os alunos e como isso se relaciona com o meio de transporte?",
        "description": "Mapa + tabela cidade / quantidade / transporte principal.",
        "chart_type": "map_table",
    },
    {
        "id": "q8",
        "label": "Alunos com menor renda estão mais concentrados em quais cursos?",
        "description": "Barras horizontais para faixas de renda mais baixas.",
        "chart_type": "bar_h_low_income",
    },
    {
        "id": "q9",
        "label": "Qual o nível de acesso a recursos educacionais (internet e computador)?",
        "description": "Duas visualizações empilhadas (computador e internet).",
        "chart_type": "twin_stacked",
    },
    {
        "id": "q10",
        "label": "Perfil dos alunos: transporte coletivo/apps vs transporte próprio",
        "description": "Barras comparativas por faixa etária, renda, cidade e trabalho.",
        "chart_type": "compare_transport",
    },
    {
        "id": "q11",
        "label": "Quantas pessoas se rematricularam no último semestre?",
        "description": "Card + comparação com semestre anterior e lista de não rematriculados.",
        "chart_type": "rematricula",
    },
    {
        "id": "relatorio-geral",
        "label": "Relatório Geral",
        "description": "Visão consolidada: indicadores, gráficos e mapas em um único painel.",
        "chart_type": "report",
    },
]


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


def build_q1(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_CURSO, COL_TRANSPORTE])
    if err:
        return [], err
    ct = (
        d.groupby([COL_CURSO, COL_TRANSPORTE], dropna=False)
        .size()
        .reset_index(name="n")
    )
    fig = px.bar(
        ct,
        x=COL_CURSO,
        y="n",
        color=COL_TRANSPORTE,
        barmode="group",
        title="Meio de transporte por curso (alunos únicos no período)",
    )
    insight = (
        f"Distribuição do meio de transporte entre {len(d)} alunos únicos "
        f"em {d[COL_CURSO].nunique()} cursos."
    )
    return [{"title": "Transporte por curso", "fig": _fig_json(fig)}], insight


def build_q2(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_CURSO, COL_TRABALHA])
    if err:
        return [], err
    ct = d.groupby([COL_CURSO, COL_TRABALHA], dropna=False).size().reset_index(name="n")
    fig = px.bar(
        ct,
        x=COL_CURSO,
        y="n",
        color=COL_TRABALHA,
        barmode="stack",
        title="Situação de trabalho por curso",
    )
    n_sim = (d[COL_TRABALHA].astype(str).str.lower() == "sim").sum()
    insight = (
        f"{n_sim} alunos únicos declaram trabalhar atualmente, de um total de {len(d)}."
    )
    return [{"title": "Trabalho por curso", "fig": _fig_json(fig)}], insight


def build_q3(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_RENDA, COL_TRABALHA])
    if err:
        return [], err
    ct = (
        d.groupby([COL_RENDA, COL_TRABALHA], dropna=False)
        .size()
        .reset_index(name="n")
    )
    pivot = ct.pivot_table(
        index=COL_RENDA, columns=COL_TRABALHA, values="n", fill_value=0
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=list(pivot.columns),
            y=[str(i) for i in pivot.index],
            colorscale="Blues",
            hoverongaps=False,
        )
    )
    fig.update_layout(
        title="Renda × trabalha (quantidade de alunos únicos)",
        xaxis_title="Trabalha",
        yaxis_title="Faixa de renda",
    )
    insight = "Mapa de calor entre faixa de renda e declaração de trabalho (valores = alunos únicos)."
    return [{"title": "Calor: renda × trabalho", "fig": _fig_json(fig)}], insight


def build_q4(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_CURSO, COL_TRABALHA])
    if err:
        return [], err
    sub = d[d[COL_TRABALHA].astype(str).str.lower().eq("sim")]
    ct = sub.groupby(COL_CURSO).size().sort_values(ascending=True)
    fig = px.bar(
        x=ct.values,
        y=ct.index.astype(str),
        orientation="h",
        title="Cursos com mais alunos que trabalham (Sim)",
        labels={"x": "Alunos únicos", "y": "Curso"},
    )
    insight = "Ordenado do menor para o maior número de alunos que conciliam estudo e trabalho."
    return [{"title": "Estudo e trabalho por curso", "fig": _fig_json(fig)}], insight


def build_q5(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_CURSO, COL_FAIXA_ETARIA])
    if err:
        return [], err
    ct = (
        d.groupby([COL_CURSO, COL_FAIXA_ETARIA], dropna=False)
        .size()
        .reset_index(name="n")
    )
    fig = px.bar(
        ct,
        x=COL_CURSO,
        y="n",
        color=COL_FAIXA_ETARIA,
        barmode="stack",
        title="Faixa etária por curso",
    )
    insight = "Distribuição de faixas etárias em cada curso (alunos únicos)."
    return [{"title": "Faixa etária por curso", "fig": _fig_json(fig)}], insight


def build_q6(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_CIDADE])
    if err:
        return [], err
    spec = build_leaflet_city_cluster_payload(d)
    if not spec.get("markers"):
        return [], "Não há dados suficientes para o mapa."
    insight = (
        "Mapa interativo (cidades com cadastros): zoom ajustado automaticamente às localizações. "
        "Coordenadas conhecidas usam posição real; demais usam estimativa próxima à região."
    )
    return [
        {
            "title": "Residência — mapa dinâmico por cidade",
            "leaflet_cluster_map": spec,
        }
    ], insight


def build_q7(d: pd.DataFrame) -> tuple[list[dict], str, list[dict]]:
    err = _require_cols(d, [COL_CIDADE, COL_TRANSPORTE])
    if err:
        return [], err, []
    rows = []
    for cidade, g in d.groupby(COL_CIDADE):
        top = (
            g[COL_TRANSPORTE]
            .fillna("N/D")
            .astype(str)
            .value_counts()
            .idxmax()
        )
        rows.append(
            {
                "cidade": str(cidade),
                "quantidade": int(len(g)),
                "principal_meio": str(top),
            }
        )
    rows.sort(key=lambda r: -r["quantidade"])
    spec = build_leaflet_city_cluster_payload(d)
    if not spec.get("markers"):
        return [], "Não há dados suficientes para o mapa.", rows
    insight = (
        "Mapa interativo por cidade (zoom automático) + tabela com principal meio de transporte."
    )
    graficos = [
        {
            "title": "Regiões — mapa dinâmico por cidade",
            "leaflet_cluster_map": spec,
        }
    ]
    return graficos, insight, rows


def build_q8(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_CURSO, COL_RENDA])
    if err:
        return [], err
    sub = d[d[COL_RENDA].isin(LOW_RENDA_MARKERS)]
    if sub.empty:
        return (
            [],
            "Nenhum aluno nas faixas de renda mais baixas com os filtros atuais.",
        )
    ct = sub.groupby(COL_CURSO).size().sort_values(ascending=True)
    fig = px.bar(
        x=ct.values,
        y=ct.index.astype(str),
        orientation="h",
        title="Concentração por curso — faixas de renda mais baixas",
        labels={"x": "Alunos únicos", "y": "Curso"},
    )
    insight = (
        "Consideradas apenas faixas: "
        + ", ".join(LOW_RENDA_MARKERS)
        + "."
    )
    return [{"title": "Baixa renda por curso", "fig": _fig_json(fig)}], insight


def build_q9(d: pd.DataFrame) -> tuple[list[dict], str]:
    err = _require_cols(d, [COL_CURSO, COL_PC, COL_NET])
    if err:
        return [], err
    g1 = (
        d.groupby([COL_CURSO, COL_PC], dropna=False).size().reset_index(name="n")
    )
    g2 = (
        d.groupby([COL_CURSO, COL_NET], dropna=False).size().reset_index(name="n")
    )
    fig1 = px.bar(
        g1,
        x=COL_CURSO,
        y="n",
        color=COL_PC,
        barmode="stack",
        title="Possui computador — por curso",
    )
    fig2 = px.bar(
        g2,
        x=COL_CURSO,
        y="n",
        color=COL_NET,
        barmode="stack",
        title="Acesso à internet — por curso",
    )
    insight = "Duas visões empilhadas: disponibilidade de computador e qualidade de acesso à internet."
    return (
        [
            {"title": "Computador", "fig": _fig_json(fig1)},
            {"title": "Internet", "fig": _fig_json(fig2)},
        ],
        insight,
    )


def build_q10(d: pd.DataFrame) -> tuple[list[dict], str]:
    """Comparativo transporte coletivo/apps vs próprio em várias dimensões (um gráfico por dimensão)."""
    if COL_TRANSPORTE not in d.columns:
        return [], "Coluna de meio de transporte ausente."
    d = d.copy()
    d["_tp"] = d[COL_TRANSPORTE].map(transport_class)
    figures: list[dict] = []
    for col, ttl in [
        (COL_FAIXA_ETARIA, "Faixa etária"),
        (COL_RENDA, "Faixa de renda"),
        (COL_CIDADE, "Cidade"),
        (COL_TRABALHA, "Trabalha"),
    ]:
        if col not in d.columns:
            continue
        sub = d.groupby([col, "_tp"], dropna=False).size().reset_index(name="n")
        fig = px.bar(
            sub,
            x=col,
            y="n",
            color="_tp",
            barmode="group",
            title=f"Transporte (classificado) × {ttl}",
        )
        figures.append({"title": ttl, "fig": _fig_json(fig)})
    if not figures:
        return [], "Sem colunas para comparar."
    insight = (
        "Classificação automática do meio de transporte em "
        "'coletivo/apps', 'próprio', 'nenhum' ou 'outros'."
    )
    return figures, insight


def build_q11(df_raw: pd.DataFrame, periodo_sel: str | None) -> dict[str, Any]:
    """Usa série completa (não deduplicada globalmente) para semestres."""
    if COL_PERIODO not in df_raw.columns or COL_TIPO not in df_raw.columns:
        return {
            "error": "É necessário ter colunas de período e tipo de matrícula.",
        }
    if COL_EMAIL not in df_raw.columns:
        return {"error": f"Coluna {COL_EMAIL} ausente."}

    d = df_raw.copy()
    d[COL_EMAIL] = d[COL_EMAIL].astype(str).str.strip().str.lower()

    periods = sorted(
        d[COL_PERIODO].dropna().astype(str).unique().tolist(),
        key=period_sort_key,
    )
    if len(periods) < 2:
        return {
            "error": "É necessário ao menos dois períodos distintos na base para comparar semestres.",
        }

    if periodo_sel and str(periodo_sel).strip():
        # último = selecionado pelo usuário como referência "atual"
        s_last = str(periodo_sel).strip()
        if s_last not in periods:
            return {"error": f"Período {s_last} não encontrado nos dados."}
        idx = periods.index(s_last)
        s_prev = periods[idx - 1] if idx > 0 else None
    else:
        s_last = periods[-1]
        s_prev = periods[-2] if len(periods) >= 2 else None

    if not s_prev:
        return {"error": "Não há semestre anterior ao selecionado."}

    rem_last = d[
        (d[COL_PERIODO].astype(str).str.strip() == s_last)
        & (d[COL_TIPO].astype(str).str.strip() == "Rematrícula")
    ]
    emails_remat = set(rem_last[COL_EMAIL].unique())

    in_prev = set(
        d[d[COL_PERIODO].astype(str).str.strip() == s_prev][COL_EMAIL].unique()
    )
    not_remat = sorted(in_prev - emails_remat)

    prev_rows = d[d[COL_PERIODO].astype(str).str.strip() == s_prev].copy()
    ord_col = _pick_sort_column(prev_rows)
    if not ord_col and "id" in prev_rows.columns:
        ord_col = "id"
    if ord_col:
        prev_rows = prev_rows.sort_values(ord_col, ascending=True)
    last_prev = prev_rows.drop_duplicates(COL_EMAIL, keep="last")
    emap = last_prev.set_index(COL_EMAIL)

    def _nome_serie(r: pd.Series) -> str:
        for k in ("Nome", "nome"):
            if k in r.index and pd.notna(r[k]):
                return str(r[k])
        return ""

    list_rows = []
    for em in not_remat:
        if em in emap.index:
            r = emap.loc[em]
            if isinstance(r, pd.DataFrame):
                r = r.iloc[-1]
            list_rows.append(
                {
                    "email": em,
                    "nome": _nome_serie(r) if isinstance(r, pd.Series) else "",
                    "curso": str(r.get(COL_CURSO, "")),
                    "ultimo_periodo": str(r.get(COL_PERIODO, s_prev)),
                }
            )
        else:
            list_rows.append(
                {
                    "email": em,
                    "nome": "",
                    "curso": "",
                    "ultimo_periodo": s_prev,
                }
            )

    n_remat = len(emails_remat)
    in_prev_n = len(in_prev)
    pct = round(100.0 * n_remat / in_prev_n, 1) if in_prev_n else 0.0

    rem_prev = d[
        (d[COL_PERIODO].astype(str).str.strip() == s_prev)
        & (d[COL_TIPO].astype(str).str.strip() == "Rematrícula")
    ]
    n_prev = rem_prev[COL_EMAIL].nunique()

    comp = pd.DataFrame(
        {
            "semestre": [s_prev, s_last],
            "rematriculas_unicas": [n_prev, n_remat],
        }
    )
    fig = px.bar(
        comp,
        x="semestre",
        y="rematriculas_unicas",
        text="rematriculas_unicas",
        title=f"Rematrículas únicas: {s_prev} vs {s_last}",
    )
    insight = (
        f"No semestre {s_last}, {n_remat} e-mails distintos com rematrícula. "
        f"No semestre anterior ({s_prev}) havia {n_prev} rematrículas únicas. "
        f"Taxa aproximada de rematrícula sobre quem estava em {s_prev}: {pct}%."
    )

    extras: dict[str, Any] = {
        "card": {
            "label": "Rematrículas no último semestre (referência)",
            "value": str(n_remat),
            "sub": f"Semestre: {s_last} — comparado com {s_prev}",
        },
        "table_non_remat": list_rows,
    }

    return {
        "graficos": [{"title": "Comparativo de rematrículas", "fig": _fig_json(fig)}],
        "insight": insight,
        "extras": extras,
        "period_label": f"{s_prev} → {s_last}",
    }


def non_remat_csv_bytes(rows: list[dict]) -> bytes:
    out = io.StringIO()
    out.write("email;nome;curso;ultimo_periodo_encontrado\n")
    for r in rows:
        out.write(
            f"{r.get('email', '')};{r.get('nome', '')};{r.get('curso', '')};{r.get('ultimo_periodo', '')}\n"
        )
    return out.getvalue().encode("utf-8")


def get_periods_cursos(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    periods: list[str] = []
    cursos: list[str] = []
    if COL_PERIODO in df.columns:
        periods = sorted(
            {str(x).strip() for x in df[COL_PERIODO].dropna().unique()},
            key=period_sort_key,
        )
    if COL_CURSO in df.columns:
        cursos = sorted({str(x).strip() for x in df[COL_CURSO].dropna().unique()})
    return periods, cursos


def run_coordinator_analysis(
    df_raw: pd.DataFrame,
    question_id: str,
    periodo: str | None,
    curso: str | None,
) -> dict[str, Any]:
    qmeta = next((q for q in COORDINATOR_QUESTIONS if q["id"] == question_id), None)
    if not qmeta:
        return {"error": "Pergunta inválida."}

    if question_id == "relatorio-geral":
        from general_report_builder import build_general_report_payload

        return build_general_report_payload(df_raw, periodo, curso)

    if question_id == "q11":
        work = df_raw.copy()
        if curso and str(curso).strip() and COL_CURSO in work.columns:
            work = work[
                work[COL_CURSO].astype(str).str.strip() == str(curso).strip()
            ]
        r = build_q11(work, periodo)
        if r.get("error"):
            return {"error": r["error"]}
        title = qmeta["label"]
        return {
            "title": title,
            "question_id": question_id,
            "insight": r["insight"],
            "graficos": r["graficos"],
            "extras": r.get("extras", {}),
            "period_label": r.get("period_label", ""),
            "mode": "coordinator",
        }

    filtered = apply_period_course_filter(df_raw, periodo, curso)

    d = deduplicate_by_email(filtered)
    if d.empty:
        return {"error": "Sem dados após filtros e deduplicação por e-mail."}

    title = qmeta["label"]
    period_label = (
        f"{periodo or 'Todos os períodos'}"
        + (f" — {curso}" if curso else "")
    )

    extras: dict[str, Any] = {}
    if question_id == "q1":
        graficos, insight = build_q1(d)
    elif question_id == "q2":
        graficos, insight = build_q2(d)
    elif question_id == "q3":
        graficos, insight = build_q3(d)
    elif question_id == "q4":
        graficos, insight = build_q4(d)
    elif question_id == "q5":
        graficos, insight = build_q5(d)
    elif question_id == "q6":
        graficos, insight = build_q6(d)
    elif question_id == "q7":
        graficos, insight, rows = build_q7(d)
        if not graficos:
            return {"error": insight or "Não foi possível gerar o mapa."}
        extras["table_city_transport"] = rows
    elif question_id == "q8":
        graficos, insight = build_q8(d)
        if not graficos:
            return {"error": insight}
    elif question_id == "q9":
        graficos, insight = build_q9(d)
    elif question_id == "q10":
        graficos, insight = build_q10(d)
    else:
        return {"error": "Pergunta ainda não implementada."}

    if not graficos:
        return {"error": insight or "Não foi possível gerar o gráfico."}

    return {
        "title": title,
        "question_id": question_id,
        "insight": insight,
        "graficos": graficos,
        "extras": extras,
        "period_label": period_label,
        "mode": "coordinator",
    }
