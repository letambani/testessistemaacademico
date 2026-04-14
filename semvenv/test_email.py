from flask import Flask
from flask_mail import Mail, Message
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)

with app.app_context():
    msg = Message(
        subject="Teste Flask-Mail via SSL",
        recipients=["marcelo.souza@aluno.fmpsc.edu.br"],
        body="Envio de e-mail bem-sucedido via Flask-Mail usando SSL (porta 465) 🎉"
    )
    try:
        mail.send(msg)
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print("❌ Erro ao enviar e-mail:", e)
