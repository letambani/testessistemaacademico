import os

class Config:
    SECRET_KEY = 'sua_chave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///spa.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuração de e-mail (SSL)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'noreply.spasc@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'gpsu fxja fgdg atqa')  # senha de app
    MAIL_DEFAULT_SENDER = ('FMPSC - SPA', os.getenv('MAIL_USERNAME', 'noreply.spasc@gmail.com'))
