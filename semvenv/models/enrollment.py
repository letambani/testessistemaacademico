# models/enrollment.py
from datetime import datetime
import pytz
from models.user import db

def agora_br():
    return datetime.now(pytz.timezone("America/Sao_Paulo"))

class Enrollment(db.Model):
    __tablename__ = 'matricula'

    id = db.Column(db.Integer, primary_key=True)
    # MUDANÇA AQUI: de False para True, pois não está enviando user_id no form
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    # Pergunta 1: E-mail (já temos no User, mas podemos repetir ou puxar do User)
    email = db.Column(db.String(120), nullable=False)
    
    # NOVA COLUNA: Tipo de Matrícula (Matrícula ou Rematrícula)
    tipo_matricula = db.Column(db.String(20), nullable=False)

    # Pergunta 2: Ano/Semestre
    periodo_ingresso = db.Column(db.String(20), nullable=False)

    # Pergunta 3: Curso
    curso = db.Column(db.String(100), nullable=False)

    # Pergunta 4: Fase
    fase = db.Column(db.String(20), nullable=False)

    # Pergunta 5: Deficiência
    tem_deficiencia = db.Column(db.String(10), nullable=False) # Sim/Não
    qual_deficiencia = db.Column(db.String(255), nullable=True)

    # Pergunta 6: Idade
    faixa_etaria = db.Column(db.String(20), nullable=False)

    # Pergunta 7: Cor/Raça
    cor_raca = db.Column(db.String(30), nullable=False)

    # Pergunta 8: Gênero
    genero = db.Column(db.String(30), nullable=False)

    # Pergunta 9: Onde mora
    cidade = db.Column(db.String(50), nullable=False)

    # Pergunta 10: Tipo de Moradia
    tipo_moradia = db.Column(db.String(50), nullable=False)

    # Pergunta 11: Escolaridade
    escolaridade = db.Column(db.String(50), nullable=False)

    # Pergunta 12: Trabalha?
    trabalha = db.Column(db.String(10), nullable=False)

    # Pergunta 13: Trabalha na área?
    trabalha_na_area = db.Column(db.String(10), nullable=False)

    # Pergunta 14: Atividade principal
    atividade_principal = db.Column(db.String(50), nullable=False)

    # Pergunta 15: Jornada de trabalho
    jornada_trabalho = db.Column(db.String(10), nullable=False)

    # Pergunta 16: Filhos/Dependentes
    tem_filhos = db.Column(db.String(10), nullable=False)
    quantos_filhos = db.Column(db.String(10), nullable=True)

    # Pergunta 17: Renda
    faixa_renda = db.Column(db.String(30), nullable=False)

    # Pergunta 18: Atividade física
    pratica_atividade_fisica = db.Column(db.String(10), nullable=False)
    qual_atividade_fisica = db.Column(db.String(100), nullable=True)

    # Pergunta 19: Computador pessoal
    possui_computador = db.Column(db.String(10), nullable=False)

    # Pergunta 20: Internet em casa
    acesso_internet = db.Column(db.String(10), nullable=False)

    # Pergunta 21: Dificuldade tecnologia
    dificuldade_tecnologia = db.Column(db.String(10), nullable=False)

    # Pergunta 22: Transporte
    meio_transporte = db.Column(db.String(30), nullable=False)

    # Pergunta 23: Dificuldades frequentar curso
    dificuldade_frequencia = db.Column(db.String(100), nullable=False)

    # Pergunta 24: Alimentação
    forma_alimentacao = db.Column(db.String(100), nullable=False)

    # Pergunta 25: Comunicação
    meio_comunicacao = db.Column(db.String(50), nullable=False)

    # Pergunta 26: Como conheceu FMP
    meio_divulgacao = db.Column(db.String(50), nullable=False)

    # Pergunta 27: Segue redes sociais
    segue_redes_sociais = db.Column(db.String(10), nullable=False)

    data_cadastro = db.Column(db.DateTime(timezone=True), default=agora_br)

    def __repr__(self):
        return f"<Enrollment {self.email} - {self.tipo_matricula} - {self.periodo_ingresso}>"