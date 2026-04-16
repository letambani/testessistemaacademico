"""
Insere no banco da faculdade os mesmos dados fictícios do gerador (50 alunos × histórico),
para a API /api/todas-matriculas nunca começar vazia em desenvolvimento.

Desativar: export SEED_FACULDADE=0

Forçar novo seed: apagar backend/instance/banco_faculdade.db (ou o caminho do SQLite)
e subir de novo faculdade_app.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def run(db, Enrollment) -> int:
    """
    Retorna quantidade de linhas inseridas, ou 0 se já havia dados ou seed desligado.
    """
    if os.environ.get("SEED_FACULDADE", "1").lower() in ("0", "false", "no"):
        return 0
    if Enrollment.query.first() is not None:
        return 0

    backend_root = Path(__file__).resolve().parent
    test_data = backend_root / "test_data"
    if str(test_data) not in sys.path:
        sys.path.insert(0, str(test_data))

    from generate_fictitious_students import build_student_list, build_timeline

    students = build_student_list()
    timeline = build_timeline(students)
    n = 0
    for ev in timeline:
        if ev.get("operacao") == "omitido":
            continue
        fp = ev["form_payload"]
        tipo = ev["tipo_matricula_esperado"]
        row = Enrollment(
            email=fp["email"],
            tipo_matricula=tipo,
            periodo_ingresso=fp["periodo_ingresso"],
            curso=fp["curso"],
            fase=fp["fase"],
            tem_deficiencia=fp["tem_deficiencia"],
            qual_deficiencia=(fp.get("qual_deficiencia") or "")[:100],
            faixa_etaria=fp["faixa_etaria"][:50],
            cor_raca=fp["cor_raca"][:50],
            genero=fp["genero"][:50],
            cidade=fp["cidade"][:100],
            tipo_moradia=fp["tipo_moradia"][:100],
            escolaridade=fp["escolaridade"][:100],
            trabalha=fp["trabalha"][:10],
            trabalha_na_area=fp["trabalha_na_area"][:10],
            atividade_principal=fp["atividade_principal"][:100],
            jornada_trabalho=fp["jornada_trabalho"][:50],
            tem_filhos=fp["tem_filhos"][:10],
            quantos_filhos=(fp.get("quantos_filhos") or "")[:10],
            faixa_renda=fp["faixa_renda"][:50],
            pratica_atividade_fisica=fp["pratica_atividade_fisica"][:10],
            qual_atividade_fisica=(fp.get("qual_atividade_fisica") or "")[:100],
            possui_computador=fp["possui_computador"][:10],
            acesso_internet=fp["acesso_internet"][:10],
            dificuldade_tecnologia=fp["dificuldade_tecnologia"][:10],
            meio_transporte=fp["meio_transporte"][:50],
            dificuldade_frequencia=fp["dificuldade_frequencia"][:100],
            forma_alimentacao=fp["forma_alimentacao"][:100],
            meio_comunicacao=fp["meio_comunicacao"][:100],
            meio_divulgacao=fp["meio_divulgacao"][:100],
            segue_redes_sociais=fp["segue_redes_sociais"][:10],
        )
        db.session.add(row)
        n += 1
    db.session.commit()
    return n
