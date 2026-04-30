#!/usr/bin/env python3
"""
Gera 50 alunos fictícios + histórico de 4 semestres (envios planejados).
Saídas: out/alunos_ficticios_50.json, out/historico_4_semestres.json
"""
from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

from config_mapping import FORM_OPTIONS, FORM_FIELD_ORDER

# Mesmas chaves que faculdade_app.api_todas_matriculas (CSV compatível com relatórios).
_CSV_API_COLUMNS: tuple[str, ...] = (
    "id",
    "E-mail",
    "Tipo de Matrícula",
    "Curso",
    "Período de Ingresso",
    "Fase",
    "Tem Deficiência",
    "Qual Deficiência",
    "Faixa Etária",
    "Cor/Raça",
    "Gênero",
    "Cidade",
    "Tipo de Moradia",
    "Escolaridade",
    "Trabalha",
    "Trabalha na Área",
    "Atividade Principal",
    "Jornada de Trabalho",
    "Tem Filhos",
    "Quantos Filhos",
    "Faixa de Renda",
    "Pratica Atividade Física",
    "Qual Atividade Física",
    "Possui Computador",
    "Acesso Internet",
    "Dificuldade Tecnologia",
    "Meio de Transporte",
    "Dificuldade Frequência",
    "Forma de Alimentação",
    "Meio de Comunicação",
    "Meio de Divulgação",
    "Segue Redes Sociais",
)

OUT = Path(__file__).resolve().parent / "out"
RNG = random.Random(42)

NOMES = (
    "Ana",
    "Bruno",
    "Carla",
    "Daniel",
    "Elena",
    "Felipe",
    "Gabriela",
    "Henrique",
    "Isabela",
    "João",
    "Karen",
    "Lucas",
    "Marina",
    "Nicolas",
    "Olívia",
    "Paulo",
    "Rafaela",
    "Sérgio",
    "Tatiane",
    "Vinícius",
)
SOBRENOMES = (
    "Almeida",
    "Barbosa",
    "Carvalho",
    "Dias",
    "Esteves",
    "Ferreira",
    "Gomes",
    "Hayashi",
    "Inácio",
    "Jardim",
    "Klein",
    "Lopes",
    "Monteiro",
    "Nogueira",
    "Oliveira",
    "Prado",
    "Queiroz",
    "Ribeiro",
    "Silva",
    "Teixeira",
)


def _cpf_digitos(base9: list[int]) -> str:
    def dv(digs):
        s = sum(digs[i] * w for i, w in enumerate(range(len(digs) + 1, 1, -1)))
        r = (s * 10) % 11
        return 0 if r == 10 else r

    d1 = dv(base9)
    d2 = dv(base9 + [d1])
    return "".join(str(x) for x in base9 + [d1, d2])


def cpf_ficticio_valido(seed: int) -> str:
    RNG_local = random.Random(seed)
    while True:
        n = [RNG_local.randint(0, 9) for _ in range(9)]
        if len(set(n)) == 1:
            continue
        raw = _cpf_digitos(n)
        return f"{raw[:3]}.{raw[3:6]}.{raw[6:9]}-{raw[9:]}"


def rg_ficticio(seed: int) -> str:
    r = random.Random(seed + 999)
    return "".join(str(r.randint(0, 9)) for _ in range(9)) + "-X"


def telefone_ficticio(seed: int) -> str:
    r = random.Random(seed + 333)
    return f"(48) 9{r.randint(1000, 9999)}-{r.randint(1000, 9999)}"


def pick(seq, seed: int):
    r = random.Random(seed)
    return r.choice(seq)


def build_form_payload(student_id: int, sem_idx: int, op: str) -> dict:
    """Monta dict compatível com POST do matricula.html (names = chaves)."""
    # Evolução de fase ao longo dos semestres (1..4 → fases 1º a 4º)
    fase = f"{min(sem_idx, 8)}º fase"
    periodo = pick(
        ["2024/1º", "2024/2º", "2025/1º", "2025/2º"],
        student_id * 17 + sem_idx,
    )
    tem_def = "Sim" if (student_id + sem_idx) % 11 == 0 else "Não"
    tem_filhos = "Sim" if (student_id + sem_idx) % 7 == 0 else "Não"
    pratica = "Sim" if (student_id + sem_idx) % 3 != 0 else "Não"

    payload = {
        "email": f"sim.aluno.{student_id:03d}@aluno.fmpsc.edu.br",
        "periodo_ingresso": periodo,
        "curso": pick(FORM_OPTIONS["curso"], student_id + sem_idx * 31),
        "fase": fase,
        "faixa_etaria": pick(FORM_OPTIONS["faixa_etaria"], student_id + sem_idx),
        "tem_deficiencia": tem_def,
        "qual_deficiencia": "Daltonismo" if tem_def == "Sim" else "",
        "cor_raca": pick(FORM_OPTIONS["cor_raca"], student_id),
        "genero": pick(FORM_OPTIONS["genero"], student_id + 5),
        "cidade": pick(FORM_OPTIONS["cidade"], student_id + 2),
        "tipo_moradia": pick(FORM_OPTIONS["tipo_moradia"], student_id + 8),
        "escolaridade": pick(FORM_OPTIONS["escolaridade"], student_id + 3),
        "trabalha": "Sim" if sem_idx > 2 else pick(["Sim", "Não"], student_id),
        "trabalha_na_area": pick(["Sim", "Não"], student_id + sem_idx + 1),
        "atividade_principal": pick(FORM_OPTIONS["atividade_principal"], student_id + sem_idx),
        "jornada_trabalho": pick(FORM_OPTIONS["jornada_trabalho"], student_id),
        "faixa_renda": pick(FORM_OPTIONS["faixa_renda"], student_id + sem_idx),
        "tem_filhos": tem_filhos,
        "quantos_filhos": "02" if tem_filhos == "Sim" else "",
        "pratica_atividade_fisica": pratica,
        "qual_atividade_fisica": "Caminhada" if pratica == "Sim" else "",
        "possui_computador": pick(["Sim", "Não"], student_id + 4),
        "acesso_internet": "Sim",
        "dificuldade_tecnologia": pick(["Sim", "Não"], student_id + 9),
        "meio_transporte": pick(FORM_OPTIONS["meio_transporte"], student_id),
        "dificuldade_frequencia": pick(FORM_OPTIONS["dificuldade_frequencia"], student_id + sem_idx),
        "forma_alimentacao": pick(FORM_OPTIONS["forma_alimentacao"], student_id),
        "meio_comunicacao": pick(FORM_OPTIONS["meio_comunicacao"], student_id),
        "meio_divulgacao": pick(FORM_OPTIONS["meio_divulgacao"], student_id),
        "segue_redes_sociais": pick(["Sim", "Não"], student_id + 6),
    }
    payload["_meta_operacao_esperada"] = "Matrícula" if op == "matricula_inicial" else "Rematrícula"
    return payload


def identity_block(sid: int) -> dict:
    return {
        "nome_completo": f"{pick(NOMES, sid)} {pick(SOBRENOMES, sid + 1)} {pick(SOBRENOMES, sid + 2)}",
        "data_nascimento": f"19{80 + (sid % 20):02d}-{(sid % 12) + 1:02d}-{(sid % 27) + 1:02d}",
        "cpf": cpf_ficticio_valido(10000 + sid),
        "rg": rg_ficticio(sid),
        "email_institucional": f"sim.aluno.{sid:03d}@aluno.fmpsc.edu.br",
        "telefone": telefone_ficticio(sid),
        "endereco": f"Rua Fictícia {sid * 11}, Bairro Teste {sid % 50}",
        "responsavel_nome": f"Resp. Sintético {sid}" if sid % 5 == 0 else None,
        "curso_preferencia": None,
        "turno": pick(["Matutino", "Noturno", "Vespertino"], sid),
        "unidade": "FMP (teste)",
        "semestre_entrada_planejado": "2024/1º",
        "status_academico_simulado": "regular",
    }


def classify_student(sid: int) -> str:
    """Distribui cenários entre 50 alunos."""
    if sid <= 15:
        return "matricula_inicial"  # primeiro envio = Matrícula
    if sid <= 40:
        return "rematricula_recorrente"
    return "perfil_misto"  # pode incluir “semestre pulado” simulado no histórico


def build_student_list() -> list[dict]:
    """Lista dos 50 alunos fictícios (mesma lógica de main)."""
    students = []
    for i in range(1, 51):
        students.append(
            {
                "id_interno": f"SIM-{i:03d}",
                "id_interno_num": i,
                "cenario": classify_student(i),
                "identidade": identity_block(i),
                "observacoes": "Dados 100% sintéticos para teste automatizado.",
            }
        )
    return students


def build_timeline(students: list[dict]) -> list[dict]:
    timeline = []
    for s in students:
        sid = s["id_interno_num"]
        perfil = s["cenario"]
        for sem in range(1, 5):
            if perfil == "perfil_misto" and sem == 3:
                # Simula “semestre sem envio” (trancamento leve) — observação apenas
                timeline.append(
                    {
                        "id_interno": s["id_interno"],
                        "semestre_indice": sem,
                        "semestre_label": f"S{sem}",
                        "operacao": "omitido",
                        "motivo": "Simulação: semestre sem envio (ex.: trancamento)",
                        "form_payload": None,
                    }
                )
                continue
            op = "matricula_inicial" if sem == 1 else "rematricula"
            if perfil == "matricula_inicial" and sem > 1:
                op = "rematricula"
            payload = build_form_payload(sid, sem, op)
            timeline.append(
                {
                    "id_interno": s["id_interno"],
                    "semestre_indice": sem,
                    "semestre_label": f"S{sem}",
                    "operacao": op,
                    "tipo_matricula_esperado": "Matrícula"
                    if op == "matricula_inicial"
                    else "Rematrícula",
                    "form_payload": {k: payload[k] for k in FORM_FIELD_ORDER},
                }
            )
    return timeline


def build_matricula_rows_api_shape() -> list[dict[str, Any]]:
    """Uma linha por envio (matrícula/rematrícula), igual ao seed da API — com E-mail para relatórios."""
    students = build_student_list()
    timeline = build_timeline(students)
    rows: list[dict[str, Any]] = []
    rid = 1
    for ev in timeline:
        if ev.get("operacao") == "omitido":
            continue
        fp = ev["form_payload"]
        tipo = ev["tipo_matricula_esperado"]
        rows.append(
            {
                "id": rid,
                "E-mail": fp["email"],
                "Tipo de Matrícula": tipo,
                "Curso": fp["curso"],
                "Período de Ingresso": fp["periodo_ingresso"],
                "Fase": fp["fase"],
                "Tem Deficiência": fp["tem_deficiencia"],
                "Qual Deficiência": fp.get("qual_deficiencia") or "",
                "Faixa Etária": fp["faixa_etaria"],
                "Cor/Raça": fp["cor_raca"],
                "Gênero": fp["genero"],
                "Cidade": fp["cidade"],
                "Tipo de Moradia": fp["tipo_moradia"],
                "Escolaridade": fp["escolaridade"],
                "Trabalha": fp["trabalha"],
                "Trabalha na Área": fp["trabalha_na_area"],
                "Atividade Principal": fp["atividade_principal"],
                "Jornada de Trabalho": fp["jornada_trabalho"],
                "Tem Filhos": fp["tem_filhos"],
                "Quantos Filhos": fp.get("quantos_filhos") or "",
                "Faixa de Renda": fp["faixa_renda"],
                "Pratica Atividade Física": fp["pratica_atividade_fisica"],
                "Qual Atividade Física": fp.get("qual_atividade_fisica") or "",
                "Possui Computador": fp["possui_computador"],
                "Acesso Internet": fp["acesso_internet"],
                "Dificuldade Tecnologia": fp["dificuldade_tecnologia"],
                "Meio de Transporte": fp["meio_transporte"],
                "Dificuldade Frequência": fp["dificuldade_frequencia"],
                "Forma de Alimentação": fp["forma_alimentacao"],
                "Meio de Comunicação": fp["meio_comunicacao"],
                "Meio de Divulgação": fp["meio_divulgacao"],
                "Segue Redes Sociais": fp["segue_redes_sociais"],
            }
        )
        rid += 1
    return rows


def write_demo_matriculas_csv(target: Path) -> int:
    rows = build_matricula_rows_api_shape()
    if not rows:
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(_CSV_API_COLUMNS), extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in _CSV_API_COLUMNS})
    return len(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    students = build_student_list()

    (OUT / "alunos_ficticios_50.json").write_text(
        json.dumps(students, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    timeline = build_timeline(students)
    (OUT / "historico_4_semestres.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    meta = {
        "total_alunos": 50,
        "total_eventos_agendados": len(timeline),
        "cenarios": {
            "matricula_inicial_ids": "SIM-001 a SIM-015",
            "rematricula_recorrente": "SIM-016 a SIM-040",
            "perfil_misto": "SIM-041 a SIM-050 (um semestre omitido no histórico)",
        },
        "endpoints": {
            "post_form": "POST http://127.0.0.1:5001/matricula-rematricula",
            "get_api": "GET http://127.0.0.1:5001/api/todas-matriculas",
        },
    }
    (OUT / "meta_geracao.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gerado: {OUT / 'alunos_ficticios_50.json'}")
    print(f"Gerado: {OUT / 'historico_4_semestres.json'}")

    backend_root = Path(__file__).resolve().parent.parent
    demo_csv = backend_root / "uploads" / "alunos_ficticios_demo.csv"
    n_csv = write_demo_matriculas_csv(demo_csv)
    print(f"Gerado: {demo_csv} ({n_csv} linhas) — use em Fonte de Dados → Arquivos CSV")


if __name__ == "__main__":
    main()
