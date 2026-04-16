# models/recuperacao_senha.py
from datetime import datetime, timedelta
import pytz
import secrets
from models.user import db  # apenas db, sem importar app.py

# Função para retornar o horário de São Paulo
def agora_br():
    return datetime.now(pytz.timezone("America/Sao_Paulo"))

class RecuperacaoSenha(db.Model):
    __tablename__ = 'recuperacao_senha'

    id_recuperacao = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    data_criacao = db.Column(db.DateTime(timezone=True), default=agora_br)
    data_expiracao = db.Column(db.DateTime(timezone=True), nullable=False)

    @staticmethod
    def gerar_token(id_usuario):
        agora = agora_br()
        expira = agora + timedelta(hours=1)
        token = secrets.token_urlsafe(32)
        rec = RecuperacaoSenha(
            id_usuario=id_usuario,
            token=token,
            data_criacao=agora,
            data_expiracao=expira
        )
        db.session.add(rec)
        db.session.commit()
        return token

    def __repr__(self):
        return f"<RecuperacaoSenha usuario_id={self.id_usuario} token={self.token}>"
