import pytest

from config import TestConfig


@pytest.fixture
def app():
    import app as app_module

    app_module._genai_client = None
    app_module.app.config.from_object(TestConfig)
    with app_module.app.app_context():
        app_module.db.drop_all()
        app_module.db.create_all()
    yield app_module.app
    with app_module.app.app_context():
        app_module.db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(app, client):
    import app as app_module
    from models.user import User

    with app.app_context():
        u = User(
            nome="Usuário Teste",
            email="usuario.teste@aluno.fmpsc.edu.br",
            cargo="Aluno",
            cpf="529.982.247-25",
        )
        u.senha = "SenhaForte1!"
        app_module.db.session.add(u)
        app_module.db.session.commit()

    client.post(
        "/login",
        data={"email": "usuario.teste@aluno.fmpsc.edu.br", "senha": "SenhaForte1!"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def faculty_app(tmp_path):
    import faculdade_app as fa

    uri = f"sqlite:///{tmp_path / 'faculdade_test.db'}"
    fa.app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI=uri)
    with fa.app.app_context():
        fa.db.drop_all()
        fa.db.create_all()
    return fa.app


@pytest.fixture
def faculty_client(faculty_app):
    return faculty_app.test_client()
