from unittest.mock import patch

import pytest

# Linha mínima compatível com colunas esperadas pela API da faculdade
SAMPLE_MATRICULA = {
    "E-mail": "aluno@aluno.fmpsc.edu.br",
    "Tipo de Matrícula": "Matrícula",
    "Curso": "ADS",
    "Período de Ingresso": "2024.1",
    "Fase": "1",
    "Tem Deficiência": "Não",
    "Qual Deficiência": "",
    "Faixa Etária": "18-24",
    "Cor/Raça": "Branca",
    "Gênero": "Feminino",
    "Cidade": "Florianópolis",
    "Tipo de Moradia": "Urbana",
    "Escolaridade": "Médio",
    "Trabalha": "Não",
    "Trabalha na Área": "Não",
    "Atividade Principal": "Estudante",
    "Jornada de Trabalho": "-",
    "Tem Filhos": "Não",
    "Quantos Filhos": "0",
    "Faixa de Renda": "0-1",
    "Pratica Atividade Física": "Sim",
    "Qual Atividade Física": "Corrida",
    "Possui Computador": "Sim",
    "Acesso Internet": "Sim",
    "Dificuldade Tecnologia": "Não",
    "Meio de Transporte": "Ônibus",
    "Dificuldade Frequência": "Nenhuma",
    "Forma de Alimentação": "Refeitório",
    "Meio de Comunicação": "E-mail",
    "Meio de Divulgação": "Site",
    "Segue Redes Sociais": "Sim",
}


def _mock_response_ok(payload):
    class R:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    return R()


def test_home_shows_login(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 200
    assert b"FMP" in r.data or b"Login" in r.data


def test_quem_somos_ok(client):
    r = client.get("/quem_somos")
    assert r.status_code == 200


def test_analises_requires_login(client):
    r = client.get("/analises", follow_redirects=False)
    assert r.status_code == 302


@patch("app.requests.get", return_value=_mock_response_ok([SAMPLE_MATRICULA]))
def test_api_columns_authenticated(mock_get, logged_in_client):
    r = logged_in_client.post(
        "/api/columns",
        json={"filename": "API - Todos (Matrículas e Rematrículas)"},
        headers={"Accept": "application/json"},
    )
    assert r.status_code == 200
    data = r.get_json()
    assert "columns" in data
    assert len(data["columns"]) >= 1
    assert "questions" in data and len(data["questions"]) >= 1
    assert "periods" in data and "cursos" in data


@patch("app.requests.get", return_value=_mock_response_ok([SAMPLE_MATRICULA]))
def test_api_grafico_bar(mock_get, logged_in_client):
    r = logged_in_client.post(
        "/api/grafico",
        json={
            "filename": "API - Todos (Matrículas e Rematrículas)",
            "coluna": "Gênero",
            "tipo": "bar",
            "filtros": {},
        },
        headers={"Accept": "application/json"},
    )
    assert r.status_code == 200
    body = r.get_json()
    assert "graficos" in body
    assert len(body["graficos"]) >= 1


@patch("app.requests.get", return_value=_mock_response_ok([SAMPLE_MATRICULA]))
def test_api_chat_resposta_local_sem_gemini(mock_get, logged_in_client):
    r = logged_in_client.post(
        "/api/chat",
        json={"mensagem": "Quantos alunos existem?"},
        headers={"Accept": "application/json"},
    )
    assert r.status_code == 200
    texto = r.get_json().get("resposta", "")
    assert "1" in texto or "registro" in texto.lower() or "total" in texto.lower()


def test_cadastro_get_ok(client):
    r = client.get("/cadastro")
    assert r.status_code == 200


def test_coordinator_questions_get_ok(logged_in_client):
    r = logged_in_client.get("/api/coordinator_questions")
    assert r.status_code == 200
    qs = r.get_json().get("questions", [])
    assert len(qs) >= 5
    assert all("id" in x and "label" in x for x in qs)


def test_intelligent_crossings_get_ok(logged_in_client):
    r = logged_in_client.get("/api/intelligent_crossings")
    assert r.status_code == 200
    xs = r.get_json().get("crossings", [])
    assert len(xs) >= 5
    assert all("id" in x and "label" in x and "chart_type" in x for x in xs)


@patch("app.requests.get", return_value=_mock_response_ok([SAMPLE_MATRICULA]))
def test_intelligent_cross_post_heatmap(mock_get, logged_in_client):
    r = logged_in_client.post(
        "/api/intelligent_cross",
        json={
            "filename": "API - Todos (Matrículas e Rematrículas)",
            "crossing_id": "ic_renda_trabalho",
            "periodo": "",
            "curso": "",
        },
        headers={"Accept": "application/json"},
    )
    assert r.status_code == 200, r.get_data(as_text=True)
    body = r.get_json()
    assert body.get("mode") == "intelligent_cross"
    assert "insight" in body and body["insight"]
    assert body.get("graficos") and len(body["graficos"]) >= 1
    mock_get.assert_called()


def test_list_files_includes_fontes_virtuais(logged_in_client):
    r = logged_in_client.get("/list_files")
    assert r.status_code == 200
    files = r.get_json().get("files", [])
    assert any("API" in f for f in files)


@patch("app.requests.get", return_value=_mock_response_ok([SAMPLE_MATRICULA]))
def test_api_columns_db_origin_uses_faculdade_api(mock_get, logged_in_client):
    """Banco de Dados: __DB_DATA__ consome a API de matrículas (mesmo fluxo de antes)."""
    r = logged_in_client.post(
        "/api/columns",
        json={"filename": "__DB_DATA__"},
        headers={"Accept": "application/json"},
    )
    assert r.status_code == 200, r.get_data(as_text=True)
    data = r.get_json()
    names = {c["name"] for c in data.get("columns", [])}
    assert "E-mail" in names
    mock_get.assert_called()
