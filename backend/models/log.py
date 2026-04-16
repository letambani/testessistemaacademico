# models/log.py
from datetime import datetime
import pytz
from models.user import db  # só importa db, não app.py

def agora_br():
    return datetime.now(pytz.timezone("America/Sao_Paulo"))

class Log(db.Model):
    __tablename__ = 'log'

    id_log = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    acao = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    ip = db.Column(db.String(45))
    data_hora = db.Column(db.DateTime(timezone=True), default=agora_br)

    def __repr__(self):
        return f"<Log {self.acao} - Usuário {self.id_usuario}>"
