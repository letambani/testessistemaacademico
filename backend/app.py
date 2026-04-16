# app.py
import base64
import json
import os

from dotenv import load_dotenv

load_dotenv()
import re
import uuid
from datetime import datetime, timedelta
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import plotly.express as px
import pytz
import requests
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

from chat_data_assistant import (
    answer_from_dataframe,
    build_compact_summary,
    fallback_summary_answer,
)
from config import Config
from coordinator_analysis import (
    COORDINATOR_QUESTIONS,
    get_periods_cursos,
    non_remat_csv_bytes,
    run_coordinator_analysis,
)
from models.enrollment import Enrollment
from models.log import Log
from models.recuperacao_senha import RecuperacaoSenha
from models.user import User, bcrypt, db




# ---------------- app / config ----------------
app = Flask(__name__)
app.config.from_object(Config)

# ---------------- extensões ----------------
db.init_app(app)
bcrypt.init_app(app)
mail = Mail(app)

# Cria tabelas (usuario, log, etc.) em qualquer modo de execução (run_stack, flask run, gunicorn).
# Sem isso, um spa.db novo gera OperationalError: no such table.
with app.app_context():
    db.create_all()


def faculdade_api_url(path):
    base = app.config.get('FACULDADE_API_BASE_URL', 'http://127.0.0.1:5001').rstrip('/') + '/'
    return urljoin(base, path.lstrip('/'))


# ---------------- login ----------------
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ---------------- ADMIN FLASK ----------------

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(app, name='Painel Administrativo')

# adiciona tabelas do SQLAlchemy
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Log, db.session))
admin.add_view(ModelView(RecuperacaoSenha, db.session))
admin.add_view(ModelView(Enrollment, db.session))

#função para definir fuso horario do brasil
def agora_br():
    return datetime.now(pytz.timezone('America/Sao_Paulo'))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ---------------- utilitários ----------------
def enviar_email_boas_vindas(email, nome):
    try:
        msg = Message(subject="🎉 Bem-vindo(a) ao SPA - FMPSC!",
                      recipients=[email])
        msg.html = f"""
        <div style="font-family:Arial,sans-serif;color:#0B3353;">
            <h2>Olá, {nome}!</h2>
            <p>Seu cadastro no <strong>SPA - Sistema de Perfil Acadêmico</strong> foi realizado com sucesso!</p>
            <p>Agora você pode acessar sua conta e começar a usar a plataforma.</p>
            <p style="margin-top:20px;">💡 Caso não tenha sido você, ignore este e-mail.</p>
            <br>
            <p>Atenciosamente,<br><strong>Equipe SPA</strong></p>
        </div>
        """
        mail.send(msg)
        app.logger.info("E-mail de boas-vindas enviado para %s", email)
    except Exception as e:
        app.logger.exception("Erro ao enviar e-mail de boas-vindas: %s", e)

# itsdangerous serializer (para tokens)
def _serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

# ---------------- ROTAS ----------------
# DEVE SER APAGADO AO FINAL, JÁ ESTÁ EM faculdade_app.py
# @app.route('/matricula', methods=['GET', 'POST'])
# @login_required
# def matricula():
#     if request.method == 'POST':
#         try:
#             # Puxa dados do formulário
#             nova_matricula = Enrollment(
#                 user_id=current_user.id,
#                 email=current_user.email,
#                 periodo_ingresso=request.form.get('periodo_ingresso'),
#                 curso=request.form.get('curso'),
#                 fase=request.form.get('fase'),
#                 tem_deficiencia=request.form.get('tem_deficiencia'),
#                 qual_deficiencia=request.form.get('qual_deficiencia'),
#                 faixa_etaria=request.form.get('faixa_etaria'),
#                 cor_raca=request.form.get('cor_raca'),
#                 genero=request.form.get('genero'),
#                 cidade=request.form.get('cidade'),
#                 tipo_moradia=request.form.get('tipo_moradia'),
#                 escolaridade=request.form.get('escolaridade'),
#                 trabalha=request.form.get('trabalha'),
#                 trabalha_na_area=request.form.get('trabalha_na_area'),
#                 atividade_principal=request.form.get('atividade_principal'),
#                 jornada_trabalho=request.form.get('jornada_trabalho'),
#                 tem_filhos=request.form.get('tem_filhos'),
#                 quantos_filhos=request.form.get('quantos_filhos'),
#                 faixa_renda=request.form.get('faixa_renda'),
#                 pratica_atividade_fisica=request.form.get('pratica_atividade_fisica'),
#                 qual_atividade_fisica=request.form.get('qual_atividade_fisica'),
#                 possui_computador=request.form.get('possui_computador'),
#                 acesso_internet=request.form.get('acesso_internet'),
#                 dificuldade_tecnologia=request.form.get('dificuldade_tecnologia'),
#                 meio_transporte=request.form.get('meio_transporte'),
#                 dificuldade_frequencia=request.form.get('dificuldade_frequencia'),
#                 forma_alimentacao=request.form.get('forma_alimentacao'),
#                 meio_comunicacao=request.form.get('meio_comunicacao'),
#                 meio_divulgacao=request.form.get('meio_divulgacao'),
#                 segue_redes_sociais=request.form.get('segue_redes_sociais')
#             )
#             db.session.add(nova_matricula)
#             db.session.commit()

#             # Log
#             log = Log(id_usuario=current_user.id, acao='Matrícula/Rematrícula',
#                       descricao=f'Usuário realizou matrícula/rematrícula para {nova_matricula.periodo_ingresso}',
#                       ip=request.remote_addr)
#             db.session.add(log)
#             db.session.commit()

#             flash('Matrícula/Rematrícula realizada com sucesso!', 'success')
#             return redirect(url_for('analises'))
#         except Exception as e:
#             db.session.rollback()
#             app.logger.exception("Erro ao salvar matrícula: %s", e)
#             flash('Erro ao processar matrícula. Tente novamente.', 'danger')

#     return render_template('matricula.html')

@app.route('/')
def home():
    """Entrada principal do sistema: tela de login (após autenticação, fluxo em /analises → index-1)."""
    return render_template('login.html', email='')

# ----- LOGIN -----
@app.route('/login', methods=['GET', 'POST'])
def login():
    email = ""  # inicializa a variável

    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        senha = request.form['senha']
        usuario = User.query.filter_by(email=email).first()

        if usuario and usuario.verificar_senha(senha):
            login_user(usuario)

            log = Log(id_usuario=usuario.id, acao='Login',
                      descricao='Usuário fez login no sistema', ip=request.remote_addr)
            db.session.add(log)
            db.session.commit()

            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('analises'))
        else:
            flash('E-mail ou senha incorretos.', 'danger')

    return render_template('login.html', email=email)


# -------------------- HELPERS --------------------
def validate_password(pw: str):
    """
    Retorna lista de mensagens de erro (vazia = senha OK).
    Regras:
      - >= 8 chars
      - 1 maiúscula
      - 1 minúscula
      - 1 número
      - 1 caracter especial (não alfa-numérico)
    """
    erros = []
    if not pw:
        erros.append("Senha não pode ser vazia.")
        return erros

    if len(pw) < 8:
        erros.append("A senha deve ter pelo menos 8 caracteres.")
    if not re.search(r"[A-Z]", pw):
        erros.append("A senha deve conter pelo menos uma letra maiúscula.")
    if not re.search(r"[a-z]", pw):
        erros.append("A senha deve conter pelo menos uma letra minúscula.")
    if not re.search(r"\d", pw):
        erros.append("A senha deve conter pelo menos um número.")
    if not re.search(r"[^\w\s]", pw):  # qualquer caracter que não seja letra/número/underscore/space
        erros.append("A senha deve conter pelo menos um caractere especial (ex: !@#$%).")
    return erros

def respond_errors_or_flash(errors, template, context=None, status=400):
    """
    Se request.is_json ou cabeçalho aceitar json -> retorna jsonify com erros.
    Senão -> flash primeira mensagem e render_template(template, **context).
    """
    # garante lista
    if not isinstance(errors, list):
        errors = [str(errors)]

    # se for requisição JSON/AJAX -> devolve JSON
    wants_json = request.is_json or 'application/json' in request.headers.get('Accept', '')
    if wants_json:
        return jsonify(success=False, errors=errors), status

    # fluxo tradicional -> flash e voltar para template com mesmo contexto (opcional)
    flash(errors[0], 'warning' if status == 400 else 'danger')
    context = context or {}
    return render_template(template, **context), status


# ----- CADASTRO -----
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        email = request.form.get('email', '').strip().lower()
        cargo = request.form.get('cargo', '')
        senha = request.form.get('senha', '')
        confirmar = request.form.get('confirmar', '')

        padrao_email = re.compile(r'.+@aluno\.fmpsc\.edu\.br$', re.IGNORECASE)
        padrao_cpf = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')

        # Valida e retorna erros através do helper
        if not padrao_email.match(email):
            return respond_errors_or_flash(
                ["Use um e-mail institucional válido (@aluno.fmpsc.edu.br)."],
                'cadastro.html',
                context={'nome': nome, 'cpf': cpf, 'email': email, 'cargo': cargo}
            )

        # validação CPF matemática (server-side)
        def validar_cpf(cpf_val):
            cpf_n = re.sub(r'[^0-9]', '', cpf_val)
            if len(cpf_n) != 11 or cpf_n == cpf_n[0]*11:
                return False
            soma = sum(int(cpf_n[i]) * (10 - i) for i in range(9))
            resto = (soma * 10) % 11
            if resto == 10: resto = 0
            if resto != int(cpf_n[9]): return False
            soma = sum(int(cpf_n[i]) * (11 - i) for i in range(10))
            resto = (soma * 10) % 11
            if resto == 10: resto = 0
            return resto == int(cpf_n[10])




        if not padrao_cpf.match(cpf):
            return respond_errors_or_flash(
                ['Digite o CPF no formato 000.000.000-00.'],
                'cadastro.html',
                context={'nome': nome, 'cpf': cpf, 'email': email, 'cargo': cargo}
            )

        if not validar_cpf(cpf):
            return respond_errors_or_flash(
                ['CPF inválido. Verifique e tente novamente.'],
                'cadastro.html',
                context={'nome': nome, 'cpf': cpf, 'email': email, 'cargo': cargo}
            )

        if User.query.filter_by(email=email).first():
            return respond_errors_or_flash(
                ['E-mail já cadastrado.'],
                'cadastro.html',
                context={'nome': nome, 'cpf': cpf, 'email': email, 'cargo': cargo}
            )

        if User.query.filter_by(cpf=cpf).first():
            return respond_errors_or_flash(
                ['CPF já cadastrado.'],
                'cadastro.html',
                context={'nome': nome, 'cpf': cpf, 'email': email, 'cargo': cargo}
            )

        # if senha != confirmar:
        #     return respond_errors_or_flash(
        #         ['As senhas não coincidem.'],
        #         'cadastro.html',
        #         context={'nome': nome, 'cpf': cpf, 'email': email, 'cargo': cargo}
        #     )

        # validação de senha via helper
        senha_erros = validate_password(senha)
        if senha_erros:
            return respond_errors_or_flash(senha_erros, 'cadastro.html', context={'nome': nome, 'cpf': cpf, 'email': email, 'cargo': cargo})

        if senha != confirmar:
            return respond_errors_or_flash(['As senhas não coincidem.'], 'cadastro.html', context={'nome': nome, 'cpf': cpf, 'email': email, 'cargo': cargo})

        try:
            novo_usuario = User(nome=nome, email=email, cargo=cargo, cpf=cpf)
            novo_usuario.senha = senha
            db.session.add(novo_usuario)
            db.session.commit()

            log = Log(id_usuario=novo_usuario.id, acao='Cadastro',
                      descricao='Novo usuário cadastrado', ip=request.remote_addr)
            db.session.add(log)
            db.session.commit()

            enviar_email_boas_vindas(email, nome)

            # retorno AJAX
            wants_json = request.is_json or 'application/json' in request.headers.get('Accept', '')
            if wants_json:
                return jsonify(success=True, redirect=url_for('login'))

            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            app.logger.exception("Erro ao cadastrar usuário: %s", e)
            return respond_errors_or_flash(['Erro ao cadastrar usuário. Tente novamente.'], 'cadastro.html', status=500)

    return render_template('cadastro.html')


# ----- DASHBOARD -----
# @app.route('/dashboard')
# @login_required
# def dashboard():
#     return render_template('dashboard.html', nome=current_user.nome)

# ----- LOGOUT -----
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('login'))

# ---------------- RECUPERAR SENHA (envia link por e-mail e registra token) ----------------
@app.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        usuario = User.query.filter_by(email=email).first()

        if not usuario:
            return respond_errors_or_flash(['E-mail não encontrado.'], 'recuperar_senha.html')

        # gera token itsdangerous
        s = _serializer()
        token = s.dumps(usuario.email, salt='recuperar-senha')

        # grava token na tabela de recuperacao (opcional p/ auditoria/expiração)
        agora = agora_br()
        expira = agora + timedelta(minutes=60)
        rec = RecuperacaoSenha(id_usuario=usuario.id, token=token,
                               data_criacao=agora, data_expiracao=expira)
        db.session.add(rec)
        db.session.commit()

        link = url_for('reset_senha', token=token, _external=True)

        # envia e-mail
        msg = Message(subject="Recuperação de Senha - FMPSC SPA",
                      recipients=[usuario.email])
        msg.html = (f"<p>Olá {usuario.nome},</p>"
                    f"<p>Recebemos uma solicitação para redefinir sua senha. Clique no link abaixo:</p>"
                    f"<p><a href='{link}'>{link}</a></p>"
                    f"<p>O link expira em 60 minutos.</p>")
        try:
            mail.send(msg)
            # log da solicitação
            log = Log(id_usuario=usuario.id, acao='Solicitou recuperação',
                      descricao='Solicitação de recuperação de senha (envio de token)', ip=request.remote_addr)
            db.session.add(log)
            db.session.commit()

            wants_json = request.is_json or 'application/json' in request.headers.get('Accept', '')
            if wants_json:
                return jsonify(success=True, message="E-mail enviado com instruções.")

            flash('Um e-mail com instruções foi enviado.', 'success')
        except Exception as e:
            app.logger.exception("Erro ao enviar e-mail de recuperação: %s", e)
            return respond_errors_or_flash(['Erro ao enviar e-mail. Tente novamente mais tarde.'], 'recuperar_senha.html', status=500)

        return redirect(url_for('login'))

    return render_template('recuperar_senha.html')


# ---------------- REDEFINIR SENHA (usa token) ----------------
# ---------------- REDEFINIR SENHA (usa token) ----------------
@app.route('/reset_senha/<token>', methods=['GET', 'POST'])
def reset_senha(token):
    # valida token itsdangerous
    s = _serializer()
    try:
        email = s.loads(token, salt='recuperar-senha', max_age=3600)
    except Exception:
        flash("Link inválido ou expirado.", "danger")
        return redirect(url_for('recuperar_senha'))

    # valida token na tabela
    rec = RecuperacaoSenha.query.filter_by(token=token).first()
    if not rec or rec.data_expiracao < agora_br():
        flash("Token inválido ou expirado.", "danger")
        return redirect(url_for('recuperar_senha'))

    if request.method == 'POST':
        nova_senha = request.form.get('senha', '').strip()
        confirmar = request.form.get('confirmar_senha', '').strip()

        # ----------- VALIDAÇÕES PADRONIZADAS -----------

        erros = []

        if not nova_senha or not confirmar:
            erros.append("Preencha ambos os campos de senha.")

        if nova_senha != confirmar:
            erros.append("As senhas não coincidem.")

        # validar regras de senha
        senha_erros = validate_password(nova_senha)
        if senha_erros:
            erros.extend(senha_erros)

        if erros:
            return respond_errors_or_flash(erros, 'reset_senha.html')

        # ----------- ATUALIZA SENHA ------------

        usuario = User.query.filter_by(email=email).first()
        if not usuario:
            return respond_errors_or_flash(['Usuário não encontrado.'], 'recuperar_senha.html')

        usuario.senha = nova_senha  # usa setter com hash
        db.session.add(usuario)

        # log
        novo_log = Log(
            id_usuario=usuario.id,
            acao="Recuperação de Senha",
            descricao="Usuário redefiniu a senha via link",
            ip=request.remote_addr,
            data_hora=agora_br()
        )
        db.session.add(novo_log)

        # remove token usado
        db.session.delete(rec)
        db.session.commit()

        # ----------- JSON OU HTML -----------

        wants_json = request.is_json or 'application/json' in request.headers.get('Accept', '')
        if wants_json:
            return jsonify(success=True, redirect=url_for('login'))

        flash("Senha redefinida com sucesso! Você já pode fazer login.", "success")
        return redirect(url_for('login'))

    return render_template('reset_senha.html')



# ------------------------------------------------------
# 🔵 MÓDULO DE GRÁFICOS / CSV / ABA DE ANÁLISES
# ------------------------------------------------------
# pastas
UPLOADS_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
SAVED_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'saved_charts')
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(SAVED_DIR, exist_ok=True)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    if 'file' not in request.files:
        return jsonify(success=False, error="Nenhum arquivo enviado")

    file = request.files['file']

    if file.filename == "":
        return jsonify(success=False, error="Arquivo inválido")

    if not file.filename.lower().endswith(".csv"):
        return jsonify(success=False, error="Envie apenas CSV")

    save_path = os.path.join(UPLOADS_DIR, file.filename)
    file.save(save_path)

    return jsonify(success=True)

@app.route('/delete_file', methods=['POST'])
@login_required
def delete_file():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify(success=False, error="Arquivo inválido")

    file_path = os.path.join(UPLOADS_DIR, filename)

    if not os.path.exists(file_path):
        return jsonify(success=False, error="Arquivo não encontrado")

    try:
        os.remove(file_path)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


def list_uploaded_files():
    """Lista CSV na pasta uploads/"""
    return [f for f in os.listdir(UPLOADS_DIR) if f.lower().endswith('.csv')]


def get_arquivos_virtuais():
    """Cria bases virtuais conectadas na API da Faculdade"""
    return [
        "🟢 API - Todos (Matrículas e Rematrículas)",
        "🔵 API - Apenas Matrículas (Novatos)",
        "🟡 API - Apenas Rematrículas (Veteranos)"
    ]

@app.route('/list_files')
@login_required
def list_files():
    files = get_arquivos_virtuais() + list_uploaded_files()
    return jsonify(files=files)

@app.route('/analises')
@login_required
def analises():
    files = get_arquivos_virtuais() + list_uploaded_files()
    return render_template('index-1.html', files=files)

def load_csv(filename):
    """Carrega CSV especificado"""
    path = os.path.join(UPLOADS_DIR, filename)
    return pd.read_csv(path)

def load_dataframe_by_name(nome):
    """Lê do CSV ou faz o filtro inteligente direto da API"""
    if nome.startswith("🟢") or nome.startswith("🔵") or nome.startswith("🟡") or nome == "__DB_DATA__":
        try:
            response = requests.get(faculdade_api_url('api/todas-matriculas'), timeout=60)
            response.raise_for_status()
            data_list = response.json()
        except requests.RequestException as exc:
            raise Exception(
                "Não foi possível conectar à API da faculdade (verifique se faculdade_app está "
                "rodando na porta 5001, ex.: python run_stack.py ou python faculdade_app.py)."
            ) from exc

        if not data_list:
            fb_name = (app.config.get('FACULDADE_FALLBACK_CSV') or '').strip()
            if nome.startswith("🟢") and fb_name:
                fb_path = os.path.join(UPLOADS_DIR, fb_name)
                if os.path.isfile(fb_path):
                    app.logger.warning(
                        "API da faculdade retornou lista vazia — usando CSV local uploads/%s", fb_name
                    )
                    return pd.read_csv(fb_path)
            extra = ""
            if nome.startswith("🔵") or nome.startswith("🟡"):
                extra = (
                    " Filtros de novatos/veteranos exigem a coluna 'Tipo de Matrícula' na API; "
                    "cadastre matrículas na API ou use apenas 'API - Todos' com dados populados."
                )
            raise Exception(
                "Nenhum dado na API da faculdade (banco vazio ou ainda sem matrículas). "
                "Soluções: (1) Com a API no ar, rode backend/test_data/automation_matricula_api.py --execute; "
                "(2) Na Base de Análise, escolha um arquivo .csv da pasta uploads (ex.: 2024.csv); "
                "(3) Mantenha 2024.csv em uploads/ — o sistema pode usar como fallback automático só em "
                "'API - Todos' (variável FACULDADE_FALLBACK_CSV)."
                + extra
            )

        df = pd.DataFrame(data_list)

        # Faz o filtro mágico usando o Pandas!
        if nome.startswith("🔵 API"):
            df = df[df['Tipo de Matrícula'] == 'Matrícula']
        elif nome.startswith("🟡 API"):
            df = df[df['Tipo de Matrícula'] == 'Rematrícula']

        if df.empty:
            raise Exception(f"Nenhum aluno registrado para a base: {nome}")

        return df
    else:
        return load_csv(nome)


# ---------------- API: COLUNAS ----------------
@app.route('/api/columns', methods=['POST'])
@login_required
def api_columns():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify(error="Nenhum arquivo selecionado"), 400

    try:
        # Agora usamos a nossa nova função unificada!
        df = load_dataframe_by_name(filename)
    except Exception as e:
        return jsonify(error=str(e)), 400

    cols = []
    for col in df.columns:
        col_data = df[col]
        cols.append({
            "name": col,
            "is_numeric": bool(pd.api.types.is_numeric_dtype(col_data)),
            "unique_values_count": int(col_data.nunique(dropna=True)),
            "sample_values": col_data.dropna().astype(str).unique()[:10].tolist()
        })

    return jsonify(columns=cols)


# ---------------- API: ANÁLISE ORIENTADA (COORDENADORES) ----------------
@app.route("/api/coordinator_meta", methods=["POST"])
@login_required
def api_coordinator_meta():
    data = request.get_json() or {}
    filename = data.get("filename")
    if not filename:
        return jsonify(error="Informe o arquivo/base de análise."), 400
    try:
        df = load_dataframe_by_name(filename)
    except Exception as e:
        return jsonify(error=str(e)), 400
    periods, cursos = get_periods_cursos(df)
    return jsonify(
        questions=COORDINATOR_QUESTIONS,
        periods=periods,
        cursos=cursos,
    )


@app.route("/api/coordinator_analysis", methods=["POST"])
@login_required
def api_coordinator_analysis():
    data = request.get_json() or {}
    filename = data.get("filename")
    question_id = data.get("question_id")
    periodo = (data.get("periodo") or "").strip() or None
    curso = (data.get("curso") or "").strip() or None
    if not filename or not question_id:
        return jsonify(error="Informe filename e question_id."), 400
    try:
        df = load_dataframe_by_name(filename)
    except Exception as e:
        return jsonify(error=str(e)), 400
    result = run_coordinator_analysis(df, question_id, periodo, curso)
    if result.get("error"):
        return jsonify(error=result["error"]), 400
    extras = result.get("extras") or {}
    rows = extras.get("table_non_remat")
    if rows:
        extras["non_remat_csv_base64"] = base64.b64encode(
            non_remat_csv_bytes(rows)
        ).decode("ascii")
    result["extras"] = extras
    return jsonify(result)


# ---------------- API: GERAR GRÁFICO ----------------
@app.route('/api/grafico', methods=['POST'])
@login_required
def api_grafico():
    payload = request.get_json()
    filename = payload.get("filename")
    compare_with = payload.get("compare_with")  # optional
    coluna = payload.get("coluna")
    tipo = payload.get("tipo", "bar")
    filtros = payload.get("filtros", {}) or {}
    groupby = payload.get("groupby")  # optional
    modo = payload.get("modo", "grafico")

    if not filename or not coluna:
        return jsonify(error="Informe 'filename' e 'coluna'."), 400

    # carrega base 1 usando a função inteligente
    try:
        df1 = load_dataframe_by_name(filename)
    except Exception as e:
        return jsonify(error=f"Erro ao abrir fonte de dados base: {e}"), 400

    # se tiver comparação, também usa a função inteligente
    if compare_with:
        try:
            df2 = load_dataframe_by_name(compare_with)
        except Exception as e:
            return jsonify(error=f"Erro ao abrir arquivo para comparar: {e}"), 400



    # checa existência das colunas na base
    if coluna not in df1.columns:
        return jsonify(error=f"A coluna '{coluna}' não existe em {filename}"), 400
    if groupby and (groupby not in df1.columns):
        return jsonify(error=f"O agrupamento '{groupby}' não existe em {filename}"), 400

    # aplica filtros no df1 (assume filtros: {col: [vals]})
    def apply_filters(df, filtros):
        df = df.copy()
        for fcol, vals in (filtros or {}).items():
            if not vals: continue
            if fcol not in df.columns:
                continue
            df[fcol] = df[fcol].astype(str)
            vals = [str(v) for v in vals]
            df = df[df[fcol].isin(vals)]
        return df

    df1 = apply_filters(df1, filtros)

    # # se modo for "texto", não gera gráficos
    # if modo == "texto":

    #     if not groupby:
    #         return jsonify(error="Para gerar relatório textual é necessário informar 'groupby'."), 400

    #     relatorio = []

    #     grupos = df1[groupby].dropna().astype(str).unique().tolist()

    #     for g in grupos:
    #         sub = df1[df1[groupby].astype(str) == str(g)]
    #         contagens = sub[coluna].fillna("N/A").astype(str).value_counts()

    #         relatorio.append(f"\n{g.upper()}:")
    #         for cat, num in contagens.items():
    #             relatorio.append(f"  {cat} = {num}")

    #     texto_final = "\n".join(relatorio)
    #     return jsonify({"relatorio_texto": texto_final})
        

    # ---------------- MODO GRÁFICO A PARTIR DAQUI ----------------

    # Se modo for "texto", usa o relatório por extenso bonito e já retorna
    if modo == "texto":
        # ----------------------------
        # RELATÓRIO POR EXTENSO BONITO
        # ----------------------------

        linhas = []
        linhas.append("==============================================")
        linhas.append(f"RELATÓRIO POR EXTENSO — COLUNA: {coluna}")
        linhas.append("==============================================\n")

        # Se tiver filtros
        if filtros:
            linhas.append("FILTROS APLICADOS:")
            for k, lista in filtros.items():
                linhas.append(f" - {k}: {', '.join(lista)}")
            linhas.append("")
        else:
            linhas.append("FILTROS APLICADOS: Nenhum\n")

        # Se tiver GROUP BY
        if groupby:
            linhas.append(f"AGRUPAMENTO: {groupby}\n")
            grupos = df1[groupby].dropna().astype(str).unique().tolist()

            for g in grupos:
                linhas.append("----------------------------------------------")
                linhas.append(f"{groupby.upper()}: {g}")
                linhas.append("----------------------------------------------")

                sub = df1[df1[groupby].astype(str) == str(g)]
                contagem = sub[coluna].fillna("N/A").astype(str).value_counts()

                for valor, qtd in contagem.items():
                    linhas.append(f"{valor} → {qtd}")

                linhas.append("")  # linha em branco

        else:
            linhas.append("AGRUPAMENTO: Nenhum\n")
            contagem = df1[coluna].fillna("N/A").astype(str).value_counts()

            for valor, qtd in contagem.items():
                linhas.append(f"{valor} → {qtd}")

        linhas.append("==============================================")
        linhas.append("FIM DO RELATÓRIO")
        linhas.append("==============================================")

        texto = "\n".join(linhas)
        return jsonify({"relatorio_texto": texto})

    # ==============================================================
    # SE NÃO FOR TEXTO, CONTINUA COM A GERAÇÃO DOS GRÁFICOS
    # ==============================================================

    def wrap_labels(val, length=20):
        """Adiciona <br> em textos longos para quebra de linha no gráfico."""
        if not isinstance(val, str) or len(val) <= length:
            return val

        # Quebra a string em palavras e reconstrói as linhas
        words = val.split(' ')
        lines = []
        current_line = ""

        for word in words:
            if len(current_line + ' ' + word) > length:
                lines.append(current_line)
                current_line = word
            else:
                current_line += (' ' + word) if current_line else word

        lines.append(current_line)
        return '<br>'.join(lines)

    # função auxiliar: gerar figura de contagem por 'coluna'
    def fig_from_df(df, title_suffix=""):
        df[coluna] = df[coluna].apply(wrap_labels)

        # Lógica para gráfico empilhado com múltiplos filtros
        if filtros and tipo == "bar":
            filter_cols = [f_col for f_col in filtros.keys() if f_col in df.columns]

            if len(filter_cols) > 0:
                color_col = filter_cols[0]
                pattern_col = filter_cols[1] if len(filter_cols) > 1 else None

                # Agrupamento para contagem
                grouping_cols = [coluna, color_col]
                if pattern_col:
                    grouping_cols.append(pattern_col)

                counts = df.groupby(grouping_cols).size().reset_index(name='total')

                # Montar título
                title = f"'{coluna}' com filtros: {', '.join(filter_cols)} {title_suffix}"

                # Gerar gráfico
                fig = px.bar(
                    counts,
                    x=coluna,
                    y='total',
                    color=color_col,
                    pattern_shape=pattern_col,
                    barmode='stack',
                    text='total',
                    title=title
                )
                fig.update_traces(textposition="inside")
                return fig

        # Lógica para outros tipos de gráficos com múltiplos filtros
        filter_cols = [f_col for f_col in (filtros or {}).keys() if f_col in df.columns and df[f_col].nunique() > 1]

        # Sunburst para Gráfico de Pizza com múltiplos filtros
        if tipo == "pie" and len(filter_cols) > 0:
            path = [coluna] + filter_cols
            counts = df.groupby(path).size().reset_index(name='total')
            title = f"'{coluna}' com filtros: {', '.join(filter_cols)} {title_suffix}"

            fig = px.sunburst(
                counts,
                path=path,
                values='total',
                title=title
            )
            fig.update_traces(textinfo='label+percent entry')
            return fig

        # Gráfico de Linha com múltiplos filtros
        if tipo == "line" and len(filter_cols) > 0:
            color_col = filter_cols[0]
            style_col = filter_cols[1] if len(filter_cols) > 1 else None

            grouping_cols = [coluna, color_col]
            if style_col:
                grouping_cols.append(style_col)

            counts = df.groupby(grouping_cols).size().reset_index(name='total')
            counts = counts.sort_values(coluna) # Ordenar para a linha fazer sentido

            title = f"'{coluna}' com filtros: {', '.join(filter_cols)} {title_suffix}"

            fig = px.line(
                counts,
                x=coluna,
                y='total',
                color=color_col,
                line_dash=style_col,
                title=title,
                text='total'
            )
            fig.update_traces(textposition="top center")
            return fig

        # Histograma com múltiplos filtros
        if tipo == "histogram" and len(filter_cols) > 0:
            color_col = filter_cols[0]
            title = f"'{coluna}' com filtro: {color_col} {title_suffix}"

            fig = px.histogram(
                df,
                x=coluna,
                color=color_col,
                barmode='overlay',
                title=title
            )
            fig.update_traces(opacity=0.75)
            return fig

        # Lógica original para outros tipos de gráfico
        ser = df[coluna].fillna("N/A").astype(str)
        counts = ser.value_counts().reset_index()
        counts.columns = ["categoria", "total"]
        counts = counts.sort_values("total", ascending=False)

        if tipo == "bar":
            fig = px.bar(
                counts,
                x="categoria",
                y="total",
                text="total",
                title=f"{coluna} {title_suffix}"
            )
            fig.update_traces(textposition="outside")
        elif tipo == "pie":
            fig = px.pie(
                counts,
                names="categoria",
                values="total",
                title=f"{coluna} {title_suffix}",
                hole=0
            )
            fig.update_traces(textinfo='label+percent+value')
        elif tipo == "line":
            fig = px.line(
                counts,
                x="categoria",
                y="total",
                text="total",
                title=f"{coluna} {title_suffix}"
            )
            fig.update_traces(textposition="top center")
        elif tipo == "histogram":
            fig = px.histogram(df, x=coluna, title=f"{coluna} {title_suffix}")
        else:
            fig = px.bar(counts, x="categoria", y="total", title=f"{coluna} {title_suffix}")
        return fig

    # conversor seguro para JSON
    def convert(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    resultados = []

    # grupos
    grupos = [None]
    if groupby:
        grupos = df1[groupby].dropna().astype(str).unique().tolist()

    # compara base e comparador
    df2 = None
    if compare_with:
        try:
            df2 = load_dataframe_by_name(compare_with)
        except Exception as e:
            return jsonify(error=f"Erro ao abrir arquivo de comparação: {e}"), 400

        if coluna not in df2.columns:
            return jsonify(error=f"A coluna '{coluna}' não existe em {compare_with}"), 400

        if groupby and (groupby not in df2.columns):
            return jsonify(error=f"O agrupamento '{groupby}' não existe em {compare_with}"), 400

        df2 = apply_filters(df2, filtros)

    # percorre grupos
    for g in grupos:

        if g is None:
            sub1 = df1
            sub2 = df2
            title_post = "(GERAL)"
        else:
            sub1 = df1[df1[groupby].astype(str) == str(g)]
            sub2 = df2[df2[groupby].astype(str) == str(g)] if df2 is not None else None
            title_post = f"({groupby}: {g})"

        # gráfico base
        fig1 = fig_from_df(sub1, title_suffix=f"- Base {title_post}")
        resultados.append({"title": f"Base — {filename} {title_post}", "fig": convert(fig1.to_plotly_json())})

        # comparador
        if sub2 is not None:

            fig2 = fig_from_df(sub2, title_suffix=f"- Comparador {title_post}")
            resultados.append({"title": f"Comparador — {compare_with} {title_post}", "fig": convert(fig2.to_plotly_json())})

            # Gráfico de Comparação de Totais Absolutos
            filter_cols = [f_col for f_col in (filtros or {}).keys() if f_col in df1.columns and f_col in df2.columns and df1[f_col].nunique() > 1]
            grouping_cols = [coluna] + filter_cols

            # Tratar coluna principal como string para consistência
            sub1[coluna] = sub1[coluna].fillna("N/A").astype(str)
            sub2[coluna] = sub2[coluna].fillna("N/A").astype(str)

            # Obter contagens para o dataframe base (sub1)
            c1 = sub1.groupby(grouping_cols).size().reset_index(name='total')
            c1['source'] = filename

            # Obter contagens para o dataframe de comparação (sub2)
            c2 = sub2.groupby(grouping_cols).size().reset_index(name='total')
            c2['source'] = compare_with

            # Combinar os dois dataframes para o gráfico
            df_comp = pd.concat([c1, c2], ignore_index=True)

            # Aplicar o wrap de texto na coluna principal
            df_comp[coluna] = df_comp[coluna].apply(wrap_labels)

            # Gerar o gráfico de barras agrupado
            if not df_comp.empty:
                pattern_col = filter_cols[0] if filter_cols else None

                fig_comp = px.bar(
                    df_comp,
                    x=coluna,
                    y='total',
                    color='source',
                    pattern_shape=pattern_col,
                    barmode='group',
                    title=f"Comparação de Totais {title_post}",
                    text='total'
                )
                fig_comp.update_traces(textposition='outside')
                resultados.append({"title": f"Comparação — {filename} vs {compare_with} {title_post}", "fig": convert(fig_comp.to_plotly_json())})

    return jsonify({"graficos": resultados})


# ---------------- API: SALVAR GRÁFICO ----------------
@app.route('/api/save_chart', methods=['POST'])
@login_required
def api_save_chart():
    data = request.get_json()
    data_url = data.get("data_url")

    header, encoded = data_url.split(",", 1)
    binary = base64.b64decode(encoded)

    fname = f"chart_{uuid.uuid4().hex[:8]}.png"
    path = os.path.join(SAVED_DIR, fname)

    with open(path, "wb") as f:
        f.write(binary)

    return jsonify(saved=True, file=fname)

# ---------------- API: DOWNLOAD ----------------
@app.route('/download_chart/<filename>')
@login_required
def download_chart(filename):
    path = os.path.join(SAVED_DIR, filename)

    if not os.path.exists(path):
        flash("Arquivo não encontrado.", "danger")
        return redirect(url_for('analises'))

    return send_file(path, as_attachment=True)

# ---------------- Rota para quem somos ----------------
@app.route('/quem_somos')
def quem_somos():
    return render_template('quem_somos.html')

# ---------------- Rodapé com verifiação de login ----------------
@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'is_logged': current_user.is_authenticated
    }

_genai_client = None


def get_genai_client():
    global _genai_client
    if _genai_client is not None:
        return _genai_client
    key = (app.config.get('GEMINI_API_KEY') or '').strip()
    if not key:
        return None
    from google import genai

    _genai_client = genai.Client(api_key=key)
    return _genai_client


@app.route('/api/chat', methods=['POST'])
@login_required
def chat_analise():
    payload = request.get_json()
    pergunta_usuario = (payload.get("mensagem") or "").strip()

    try:
        response = requests.get(faculdade_api_url('api/todas-matriculas'), timeout=60)
        response.raise_for_status()
        dados_json = response.json()

        if not dados_json:
            return jsonify({"resposta": "Ainda não há dados de matrículas cadastrados na API da faculdade."})

        df = pd.DataFrame(dados_json)

        # 1) Respostas determinísticas nos dados (rápidas, sem API externa)
        local = answer_from_dataframe(df, pergunta_usuario)
        if local:
            return jsonify({"resposta": local})

        # 2) Gemini opcional — só resumo agregado (menos tokens, mais rápido)
        client = get_genai_client()
        if client is not None:
            resumo = build_compact_summary(df)
            prompt = f"""Você é o assistente da gestão acadêmica da faculdade.
Use APENAS o resumo estatístico abaixo (não invente números).

{resumo}

Pergunta do usuário: "{pergunta_usuario}"

Responda em português do Brasil, de forma direta e curta. Se o resumo não permitir responder, diga o que falta nos dados."""

            response_ia = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            return jsonify({"resposta": response_ia.text})

        # 3) Sem Gemini: resumo útil automático
        return jsonify({"resposta": fallback_summary_answer(df, pergunta_usuario)})

    except Exception as e:
        app.logger.exception("Erro no chat de análise: %s", e)
        return jsonify({"resposta": "Erro ao consultar os dados. Verifique se a API da faculdade (porta 5001) está no ar."}), 500
# ---------------- criar banco e rodar ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("SPA_PORT", "5050"))
    app.run(debug=True, port=port)
