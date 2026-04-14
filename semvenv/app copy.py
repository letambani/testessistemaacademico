# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
import re
import numpy as np
import pandas as pd
import plotly.express as px

from config import Config
from models.user import db, bcrypt, User
from models.log import Log
from models.recuperacao_senha import RecuperacaoSenha




# ---------------- app / config ----------------
app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_ECHO'] = True

# ---------------- extensões ----------------
db.init_app(app)
bcrypt.init_app(app)
mail = Mail(app)


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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- utilitários ----------------
def enviar_email_boas_vindas(email, nome):
    try:
        msg = Message(subject="🎉 Bem-vindo(a) ao SPA - FMPSC!",
                      recipients=[email])
        msg.html = f"""
        <div style="font-family:Arial,sans-serif;color:#0B3353;">
            <h2>Olá, {nome}!</h2>
            <p>Seu cadastro no <strong>SPA - Sistema de Perfil Discente</strong> foi realizado com sucesso!</p>
            <p>Agora você pode acessar sua conta e começar a usar a plataforma.</p>
            <p style="margin-top:20px;">💡 Caso não tenha sido você, ignore este e-mail.</p>
            <br>
            <p>Atenciosamente,<br><strong>Equipe FMPSC</strong></p>
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

@app.route('/')
def home():
    return redirect(url_for('login'))

# ----- LOGIN -----
@app.route('/login', methods=['GET', 'POST'])
def login():
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

    return render_template('login.html')

# ----- CADASTRO -----
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        cpf = request.form['cpf'].strip()
        email = request.form['email'].strip().lower()
        cargo = request.form['cargo']
        senha = request.form['senha']
        confirmar = request.form['confirmar']

        padrao_email = re.compile(r'.+@aluno\.fmpsc\.edu\.br$', re.IGNORECASE)
        padrao_cpf = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$')

        if not padrao_email.match(email):
            flash('Use um e-mail institucional válido (@aluno.fmpsc.edu.br).', 'warning')
            return render_template('cadastro.html')

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
            flash('Digite o CPF no formato 000.000.000-00.', 'warning')
            return render_template('cadastro.html')

        if not validar_cpf(cpf):
            flash('CPF inválido. Verifique e tente novamente.', 'warning')
            return render_template('cadastro.html')

        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'info')
            return render_template('cadastro.html')

        if User.query.filter_by(cpf=cpf).first():
            flash('CPF já cadastrado.', 'info')
            return render_template('cadastro.html')

        if len(senha) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'warning')
            return render_template('cadastro.html')

        if senha != confirmar:
            flash('As senhas não coincidem.', 'danger')
            return render_template('cadastro.html')

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
            flash('Cadastro realizado com sucesso!', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            app.logger.exception("Erro ao cadastrar usuário: %s", e)
            flash('Erro ao cadastrar usuário. Tente novamente.', 'danger')
            return render_template('cadastro.html')

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
        email = request.form['email'].strip().lower()
        usuario = User.query.filter_by(email=email).first()

        if not usuario:
            flash('E-mail não encontrado.', 'warning')
            return redirect(url_for('login'))

        # gera token itsdangerous
        s = _serializer()
        token = s.dumps(usuario.email, salt='recuperar-senha')

        # grava token na tabela de recuperacao (opcional p/ auditoria/expiração)
        agora = datetime.utcnow()
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

            flash('Um e-mail com instruções foi enviado.', 'success')
        except Exception as e:
            app.logger.exception("Erro ao enviar e-mail de recuperação: %s", e)
            flash('Erro ao enviar e-mail. Tente novamente mais tarde.', 'danger')

        return redirect(url_for('login'))

    return render_template('recuperar_senha.html')

# ---------------- REDEFINIR SENHA (usa token) ----------------
@app.route('/reset_senha/<token>', methods=['GET', 'POST'])
def reset_senha(token):
    # primeiro valida token com itsdangerous (tempo)
    s = _serializer()
    try:
        email = s.loads(token, salt='recuperar-senha', max_age=3600)
    except Exception:
        flash("Link inválido ou expirado.", "danger")
        return redirect(url_for('recuperar_senha'))

    # também valida existência no DB (p/ garantir token válido)
    rec = RecuperacaoSenha.query.filter_by(token=token).first()
    if not rec or rec.data_expiracao < datetime.utcnow():
        flash("Token inválido ou expirado.", "danger")
        return redirect(url_for('recuperar_senha'))

    if request.method == 'POST':
        nova_senha = request.form.get('senha')
        confirmar = request.form.get('confirmar_senha')


        if not nova_senha or not confirmar:
            flash('Preencha ambos os campos de senha.', 'warning')
            return render_template('reset_senha.html')

        if nova_senha != confirmar:
            flash('As senhas não coincidem.', 'danger')
            return render_template('reset_senha.html')

        if len(nova_senha) < 8:
            flash('A senha deve ter pelo menos 8 caracteres.', 'warning')
            return render_template('reset_senha.html')


        usuario = User.query.filter_by(email=email).first()
        if not usuario:
            flash('Usuário não encontrado.', 'danger')
            return redirect(url_for('recuperar_senha'))

        # 🔒 atualiza com hash via setter do modelo
        usuario.senha = nova_senha
        db.session.add(usuario)

        # log
        novo_log = Log(
            id_usuario=usuario.id,
            acao="Recuperação de Senha",
            descricao="Usuário redefiniu a senha via link",
            ip=request.remote_addr,
            data_hora=datetime.utcnow()
        )
        db.session.add(novo_log)

        # remove token usado
        db.session.delete(rec)
        db.session.commit()

        flash("Senha redefinida com sucesso! Você já pode fazer login.", "success")
        return redirect(url_for('login'))


    return render_template('reset_senha.html')

# ------------------------------------------------------
# 🔵 MÓDULO DE GRÁFICOS / CSV / ABA DE ANÁLISES
# ------------------------------------------------------
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
import json
import base64
import uuid
from flask import jsonify, send_file
import io

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
@app.route('/list_files')

@login_required
def list_files():
    files = list_uploaded_files()
    return jsonify(files=files)


def load_csv(filename):
    """Carrega CSV especificado"""
    path = os.path.join(UPLOADS_DIR, filename)
    return pd.read_csv(path)


# ---------------- INDEX DOS GRÁFICOS ----------------
@app.route('/analises')
@login_required
def analises():
    files = list_uploaded_files()
    return render_template('index.html', files=files)


# ---------------- API: COLUNAS ----------------
@app.route('/api/columns', methods=['POST'])
@login_required
def api_columns():
    data = request.get_json()
    filename = data.get("filename")

    if not filename:
        return jsonify(error="Nenhum arquivo selecionado"), 400

    try:
        df = load_csv(filename)
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
    modo = payload.get("modo", "grafico")   # <--- NOVO ("grafico" ou "texto")

    if not filename or not coluna:
        return jsonify(error="Informe 'filename' e 'coluna'."), 400

    # carrega base
    try:
        df1 = load_csv(filename)
    except Exception as e:
        return jsonify(error=f"Erro ao abrir arquivo base: {e}"), 400

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

    # se modo for "texto", não gera gráficos
    if modo == "texto":

        if not groupby:
            return jsonify(error="Para gerar relatório textual é necessário informar 'groupby'."), 400

        relatorio = []

        grupos = df1[groupby].dropna().astype(str).unique().tolist()

        for g in grupos:
            sub = df1[df1[groupby].astype(str) == str(g)]
            contagens = sub[coluna].fillna("N/A").astype(str).value_counts()

            relatorio.append(f"\n{g.upper()}:")
            for cat, num in contagens.items():
                relatorio.append(f"  {cat} = {num}")

        texto_final = "\n".join(relatorio)
        return jsonify({"relatorio_texto": texto_final})

    # ---------------- MODO GRÁFICO A PARTIR DAQUI ----------------

    # função auxiliar: gerar figura de contagem por 'coluna'
    def fig_from_df(df, title_suffix=""):
        ser = df[coluna].fillna("N/A").astype(str)
        counts = ser.value_counts().reset_index()
        counts.columns = ["categoria", "total"]
        counts = counts.sort_values("total", ascending=False)

        if tipo == "bar":
            fig = px.bar(
                counts,
                x="categoria",
                y="total",
                text="total",   # <<< mostra número na barra
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
            fig.update_traces(textinfo='label+percent+value')  # <<< mostra valores

        elif tipo == "line":
            fig = px.line(
                counts,
                x="categoria",
                y="total",
                text="total",   # <<< mostra número
                title=f"{coluna} {title_suffix}"
            )
            fig.update_traces(textposition="top center")

        elif tipo == "histogram":
            fig = px.histogram(df, x=coluna, title=f"{coluna} {title_suffix}")

        else:
            fig = px.bar(counts, x="categoria", y="total", title=f"{coluna} {title_suffix}")

        return fig
    if tipo == "texto":
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
            df2 = load_csv(compare_with)
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

            # diferenças %
            c1 = sub1[coluna].fillna("N/A").astype(str).value_counts()
            c2 = sub2[coluna].fillna("N/A").astype(str).value_counts()

            categorias = sorted(set(c1.index.tolist() + c2.index.tolist()))

            diffs = []
            for cat in categorias:
                v1 = int(c1.get(cat, 0))
                v2 = int(c2.get(cat, 0))

                if v1 == 0: pct = 100.0 if v2 > 0 else 0
                else: pct = ((v2 - v1) / v1) * 100

                diffs.append({"categoria": cat, "pct": round(pct, 2)})

            df_diff = pd.DataFrame(diffs)

            fig_diff = px.bar(
                df_diff,
                x="categoria",
                y="pct",
                title=f"Variação % (Comparador vs Base) {title_post}",
                text="pct"   # <-- RÓTULO DAS BARRAS
            )
            fig_diff.update_traces(textposition='outside')

            resultados.append({"title": f"Variação % — {compare_with} vs {filename} {title_post}", "fig": convert(fig_diff.to_plotly_json())})

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


# ---------------- criar banco e rodar ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
