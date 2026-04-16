"""
Respostas rápidas a partir do DataFrame da API de matrículas (sem LLM obrigatório).
Gemini é opcional para perguntas abertas, usando só um resumo estatístico (menos tokens, mais rápido).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

import pandas as pd


def _norm(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def _col(df: pd.DataFrame, *names: str) -> str | None:
    for n in names:
        if n in df.columns:
            return n
    return None


def build_compact_summary(df: pd.DataFrame, max_cursos: int = 12) -> str:
    """Texto enxuto para prompt de LLM (não envia linha a linha)."""
    lines: list[str] = [f"Total de registros na base: {len(df)}."]
    ct = _col(df, "Tipo de Matrícula")
    if ct:
        vc = df[ct].astype(str).value_counts()
        lines.append("Por tipo de matrícula: " + "; ".join(f"{k}={int(v)}" for k, v in vc.items()))
    cc = _col(df, "Curso")
    if cc:
        vc = df[cc].astype(str).value_counts().head(max_cursos)
        lines.append("Principais cursos: " + "; ".join(f"{k[:50]}={int(v)}" for k, v in vc.items()))
    cp = _col(df, "Período de Ingresso", "Periodo de Ingresso")
    if cp:
        vc = df[cp].astype(str).value_counts().head(8)
        lines.append("Períodos de ingresso (amostra): " + "; ".join(f"{k}={int(v)}" for k, v in vc.items()))
    cg = _col(df, "Gênero", "Genero")
    if cg:
        vc = df[cg].astype(str).value_counts().head(6)
        lines.append("Gênero: " + "; ".join(f"{k}={int(v)}" for k, v in vc.items()))
    city = _col(df, "Cidade")
    if city:
        vc = df[city].astype(str).value_counts().head(8)
        lines.append("Cidades: " + "; ".join(f"{k}={int(v)}" for k, v in vc.items()))
    return "\n".join(lines)


def answer_from_dataframe(df: pd.DataFrame, pergunta: str) -> str | None:
    """
    Resposta determinística em português. Retorna None se for melhor delegar ao LLM.
    """
    q = _norm(pergunta)
    if not q:
        return None

    ct = _col(df, "Tipo de Matrícula")
    cc = _col(df, "Curso")
    cp = _col(df, "Período de Ingresso")

    # --- Rematrícula / matrícula / totais ---
    if ct:
        is_rem = df[ct].astype(str).str.strip() == "Rematrícula"
        is_mat = df[ct].astype(str).str.strip() == "Matrícula"
        n_rem = int(is_rem.sum())
        n_mat = int(is_mat.sum())

        if any(
            w in q
            for w in (
                "rematricula",
                "rematrícula",
                "rematricularam",
                "rematriculou",
                "veterano",
                "veteranos",
            )
        ):
            return (
                f"Nos dados atuais da API há **{n_rem}** registro(s) com tipo **Rematrícula**. "
                f"(Cada registro corresponde a um envio/formulário vinculado ao e-mail no sistema.)"
            )

        if any(
            w in q
            for w in (
                "matricula",
                "matrícula",
                "matricularam",
                "novato",
                "novatos",
                "ingress",
                "calouro",
            )
        ) and "rematr" not in q:
            return (
                f"Há **{n_mat}** registro(s) com tipo **Matrícula** (primeiro vínculo daquele e-mail na base)."
            )

    if any(w in q for w in ("quantos", "total", "quantidade")) and any(
        w in q for w in ("aluno", "alunos", "registro", "matricula", "dado")
    ):
        return f"O conjunto carregado tem **{len(df)}** registro(s) no total (linhas na API)."

    # --- Filtro por período (ex.: 2024/1, 2025/1º) ---
    if cp and (m := re.search(r"(20\d{2})\s*[/\-.]\s*(\d)", pergunta)):
        ano, sem = m.group(1), m.group(2)
        # Normalizar comparação com valores como 2024/1º
        mask = df[cp].astype(str).str.contains(rf"{ano}\s*/\s*{sem}", regex=True, na=False)
        sub = df[mask]
        if len(sub) == 0:
            return (
                f"Não há registros cujo **Período de Ingresso** coincida com **{ano}/{sem}** nos dados atuais."
            )
        extra = ""
        if ct:
            vc = sub[ct].astype(str).value_counts()
            extra = " Distribuição: " + ", ".join(f"{k}={int(v)}" for k, v in vc.items()) + "."
        return f"Para o período **{ano}/{sem}** há **{len(sub)}** registro(s).{extra}"

    # --- Por curso (top) ---
    if cc and any(w in q for w in ("curso", "cursos", "qual curso")):
        vc = df[cc].astype(str).value_counts().head(10)
        body = "\n".join(f"- **{str(k)[:80]}**: {int(v)}" for k, v in vc.items())
        return "Distribuição por curso (top 10):\n" + body

    # --- Cidade ---
    city = _col(df, "Cidade")
    if city and any(w in q for w in ("cidade", "município", "municipio", "onde mora")):
        vc = df[city].astype(str).value_counts().head(10)
        body = "\n".join(f"- **{k}**: {int(v)}" for k, v in vc.items())
        return "Distribuição por cidade (top 10):\n" + body

    return None


def fallback_summary_answer(df: pd.DataFrame, pergunta: str) -> str:
    """Resposta útil sempre baseada em dados quando não há match específico nem LLM."""
    parts = [
        "Segue um **resumo objetivo** dos dados da API de matrículas (atualizado no momento da consulta):",
        f"- **Total de registros:** {len(df)}",
    ]
    ct = _col(df, "Tipo de Matrícula")
    if ct:
        vc = df[ct].astype(str).value_counts()
        parts.append(
            "- **Por tipo:** "
            + ", ".join(f"{k} ({int(v)})" for k, v in vc.items())
        )
    cc = _col(df, "Curso")
    if cc:
        top = df[cc].astype(str).value_counts().head(5)
        parts.append(
            "- **Top 5 cursos:** "
            + ", ".join(f"{str(k)[:40]} ({int(v)})" for k, v in top.items())
        )
    parts.append(
        "\nVocê pode perguntar, por exemplo: quantos se **rematricularam**, quantos são **matrícula** inicial, "
        "totais por **curso** ou **cidade**, ou mencionar um **período de ingresso** (ex.: 2024/1)."
    )
    return "\n".join(parts)
