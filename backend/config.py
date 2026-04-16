import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-only-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///spa.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', '').lower() in ('1', 'true', 'yes')

    # API do módulo faculdade (faculdade_app.py na porta 5001 por padrão)
    FACULDADE_API_BASE_URL = os.getenv('FACULDADE_API_BASE_URL', 'http://127.0.0.1:5001')
    # Se a API retornar [], usar este CSV em uploads/ só para "🟢 API - Todos" (desenvolvimento/demo)
    FACULDADE_FALLBACK_CSV = os.getenv('FACULDADE_FALLBACK_CSV', '2024.csv')

    # Google Gemini (opcional — chat de análises)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # Configuração de e-mail (SSL)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = (
        'FMPSC - SPA',
        os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME', 'noreply@localhost')),
    )


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_ECHO = False
    MAIL_SUPPRESS_SEND = True
    WTF_CSRF_ENABLED = False
    FACULDADE_API_BASE_URL = 'http://test-faculdade.invalid'
    FACULDADE_FALLBACK_CSV = ''
    GEMINI_API_KEY = ''
