import os

from flask import Flask, render_template, request, redirect, jsonify, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'senha-secreta-faculdade'
# O banco de dados da faculdade será separado do seu sistema principal
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco_faculdade.db'
db = SQLAlchemy(app)


# 1. MODELO DO BANCO DE DADOS
class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    
    # -------- OLHA A NOSSA COLUNA AQUI --------
    tipo_matricula = db.Column(db.String(20))
    # ------------------------------------------

    periodo_ingresso = db.Column(db.String(50))
    curso = db.Column(db.String(100))
    fase = db.Column(db.String(50))
    tem_deficiencia = db.Column(db.String(10))
    qual_deficiencia = db.Column(db.String(100))
    faixa_etaria = db.Column(db.String(50))
    cor_raca = db.Column(db.String(50))
    genero = db.Column(db.String(50))
    cidade = db.Column(db.String(100))
    tipo_moradia = db.Column(db.String(100))
    escolaridade = db.Column(db.String(100))
    trabalha = db.Column(db.String(10))
    trabalha_na_area = db.Column(db.String(10))
    atividade_principal = db.Column(db.String(100))
    jornada_trabalho = db.Column(db.String(50))
    tem_filhos = db.Column(db.String(10))
    quantos_filhos = db.Column(db.String(10))
    faixa_renda = db.Column(db.String(50))
    pratica_atividade_fisica = db.Column(db.String(10))
    qual_atividade_fisica = db.Column(db.String(100))
    possui_computador = db.Column(db.String(10))
    acesso_internet = db.Column(db.String(10))
    dificuldade_tecnologia = db.Column(db.String(10))
    meio_transporte = db.Column(db.String(50))
    dificuldade_frequencia = db.Column(db.String(100))
    forma_alimentacao = db.Column(db.String(100))
    meio_comunicacao = db.Column(db.String(100))
    meio_divulgacao = db.Column(db.String(100))
    segue_redes_sociais = db.Column(db.String(10))


@app.route("/")
def index_faculdade():
    """Evita 404 na raiz: esta app é a API; o SPA principal usa SPA_PORT (padrão 5050)."""
    spa = os.environ.get("SPA_PORT", "5050")
    return (
        f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>API Faculdade</title></head>
<body style="font-family:system-ui,sans-serif;max-width:40rem;margin:2rem;">
<h1>API Faculdade (microserviço)</h1>
<p>A <strong>interface do projeto (SPA)</strong> está em
<a href="http://127.0.0.1:{spa}">http://127.0.0.1:{spa}</a> — abra esse endereço no navegador.</p>
<p>Endpoints desta API:</p>
<ul>
<li><a href="/api/todas-matriculas">/api/todas-matriculas</a></li>
<li><a href="/matricula-rematricula">/matricula-rematricula</a> (formulário de matrícula)</li>
</ul>
</body></html>""",
        200,
        {"Content-Type": "text/html; charset=utf-8"},
    )


# 2. ROTA DA PÁGINA DE MATRÍCULA
@app.route('/matricula-rematricula', methods=['GET', 'POST'])
def matricula():
    if request.method == 'POST':
        # FAÇA O PYTHON IMPRIMIR AS COLUNAS NO TERMINAL:
        # print("COLUNAS QUE O PYTHON ESTÁ VENDO:", Enrollment.__table__.columns.keys())
        try:
            # 1. Pega o e-mail que veio do formulário
            email_aluno = request.form.get('email')

            # 2. O DETETIVE: Verifica se o aluno já existe no banco usando o e-mail
            aluno_existente = Enrollment.query.filter_by(email=email_aluno).first()

            if aluno_existente:
                tipo_calculado = "Rematrícula" # Se achou o e-mail no banco, é veterano!
            else:
                tipo_calculado = "Matrícula"   # Se não achou, é novato!

            # 3. Salva no banco com o tipo calculado
            nova_matricula = Enrollment(
                email=email_aluno,
                tipo_matricula=tipo_calculado, # <--- A mágica acontece aqui!
                periodo_ingresso=request.form.get('periodo_ingresso'),
                curso=request.form.get('curso'),
                fase=request.form.get('fase'),
                tem_deficiencia=request.form.get('tem_deficiencia'),
                qual_deficiencia=request.form.get('qual_deficiencia'),
                faixa_etaria=request.form.get('faixa_etaria'),
                cor_raca=request.form.get('cor_raca'),
                genero=request.form.get('genero'),
                cidade=request.form.get('cidade'),
                tipo_moradia=request.form.get('tipo_moradia'),
                escolaridade=request.form.get('escolaridade'),
                trabalha=request.form.get('trabalha'),
                trabalha_na_area=request.form.get('trabalha_na_area'),
                atividade_principal=request.form.get('atividade_principal'),
                jornada_trabalho=request.form.get('jornada_trabalho'),
                tem_filhos=request.form.get('tem_filhos'),
                quantos_filhos=request.form.get('quantos_filhos'),
                faixa_renda=request.form.get('faixa_renda'),
                pratica_atividade_fisica=request.form.get('pratica_atividade_fisica'),
                qual_atividade_fisica=request.form.get('qual_atividade_fisica'),
                possui_computador=request.form.get('possui_computador'),
                acesso_internet=request.form.get('acesso_internet'),
                dificuldade_tecnologia=request.form.get('dificuldade_tecnologia'),
                meio_transporte=request.form.get('meio_transporte'),
                dificuldade_frequencia=request.form.get('dificuldade_frequencia'),
                forma_alimentacao=request.form.get('forma_alimentacao'),
                meio_comunicacao=request.form.get('meio_comunicacao'),
                meio_divulgacao=request.form.get('meio_divulgacao'),
                segue_redes_sociais=request.form.get('segue_redes_sociais')
            )
            db.session.add(nova_matricula)
            db.session.commit()
            return "<h1>Matrícula realizada com sucesso no sistema da faculdade!</h1>"
        except Exception as e:
            db.session.rollback()
            return f"Erro: {e}"

    return render_template('matricula.html')
# 3. A API QUE O SISTEMA PRINCIPAL VAI CONSUMIR
@app.route('/api/todas-matriculas', methods=['GET'])
def api_todas_matriculas():
    # Pega o parâmetro 'tipo' da URL (se não tiver, vem None)
    tipo_filtro = request.args.get('tipo')
    
    if tipo_filtro:
        # Filtra no banco de dados apenas o tipo desejado
        all_enrollments = Enrollment.query.filter_by(tipo_matricula=tipo_filtro).all()
    else:
        # Se não passar nada, traz tudo (como estava antes)
        all_enrollments = Enrollment.query.all()
    
    data_list = []
    for e in all_enrollments:
        data_list.append({
            "id": e.id,
            "E-mail": e.email,
            "Tipo de Matrícula": e.tipo_matricula,
            "Curso": e.curso,
            "Período de Ingresso": e.periodo_ingresso,
            "Fase": e.fase,
            "Tem Deficiência": e.tem_deficiencia,
            "Qual Deficiência": e.qual_deficiencia,
            "Faixa Etária": e.faixa_etaria,
            "Cor/Raça": e.cor_raca,
            "Gênero": e.genero,
            "Cidade": e.cidade,
            "Tipo de Moradia": e.tipo_moradia,
            "Escolaridade": e.escolaridade,
            "Trabalha": e.trabalha,
            "Trabalha na Área": e.trabalha_na_area,
            "Atividade Principal": e.atividade_principal,
            "Jornada de Trabalho": e.jornada_trabalho,
            "Tem Filhos": e.tem_filhos,
            "Quantos Filhos": e.quantos_filhos,
            "Faixa de Renda": e.faixa_renda,
            "Pratica Atividade Física": e.pratica_atividade_fisica,
            "Qual Atividade Física": e.qual_atividade_fisica,
            "Possui Computador": e.possui_computador,
            "Acesso Internet": e.acesso_internet,
            "Dificuldade Tecnologia": e.dificuldade_tecnologia,
            "Meio de Transporte": e.meio_transporte,
            "Dificuldade Frequência": e.dificuldade_frequencia,
            "Forma de Alimentação": e.forma_alimentacao,
            "Meio de Comunicação": e.meio_comunicacao,
            "Meio de Divulgação": e.meio_divulgacao,
            "Segue Redes Sociais": e.segue_redes_sociais
        })
    return jsonify(data_list)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        from seed_faculdade_db import run as seed_faculdade

        inserted = seed_faculdade(db, Enrollment)
        if inserted:
            print(f"[faculdade_app] Seed: {inserted} registros fictícios inseridos (API com dados).")
    port = int(os.environ.get("FACULDADE_PORT", "5001"))
    app.run(port=port, debug=True)