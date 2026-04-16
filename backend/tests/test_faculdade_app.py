def test_api_todas_matriculas_vazia_inicial(faculty_client):
    r = faculty_client.get("/api/todas-matriculas")
    assert r.status_code == 200
    assert r.get_json() == []


def test_matricula_get_form(faculty_client):
    r = faculty_client.get("/matricula-rematricula")
    assert r.status_code == 200
