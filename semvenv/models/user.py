# models/user.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from datetime import datetime
from enum import Enum
import pytz

db = SQLAlchemy()
bcrypt = Bcrypt()

# Função para retornar o horário de São Paulo
def agora_br():
    return datetime.now(pytz.timezone("America/Sao_Paulo"))

class StatusEnum(Enum):
    ATIVO = "ativo"
    INATIVO = "inativo"
    BLOQUEADO = "bloqueado"

class User(db.Model, UserMixin):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    data_cadastro = db.Column(db.DateTime(timezone=True), default=agora_br)
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.ATIVO)

    logs = db.relationship('Log', backref='usuario', lazy=True)
    recuperacoes = db.relationship('RecuperacaoSenha', backref='usuario', lazy=True)

    @property
    def senha(self):
        raise AttributeError('A senha não pode ser lida diretamente.')

    @senha.setter
    def senha(self, senha):
        self.senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

    def verificar_senha(self, senha):
        return bcrypt.check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f"<User {self.nome}>"
