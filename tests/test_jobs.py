from src import jobs


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_adzuna_normaliza_vaga(monkeypatch):
    data = {"results": [{
        "id": "42",
        "title": "Dev <strong>Python</strong>",
        "company": {"display_name": "ACME"},
        "location": {"display_name": "São Paulo"},
        "redirect_url": "https://exemplo.com/42",
        "description": "Python e Django",
    }]}
    monkeypatch.setattr(jobs, "ADZUNA_APP_ID", "id")
    monkeypatch.setattr(jobs, "ADZUNA_APP_KEY", "chave")
    monkeypatch.setattr(jobs.requests, "get", lambda *a, **k: FakeResponse(data))
    result = jobs.fetch_adzuna("python")
    assert result[0]["id"] == "adzuna-42"
    assert result[0]["title"] == "Dev  Python"
    assert result[0]["company"] == "ACME"
    assert result[0]["source"] == "Adzuna"


def test_adzuna_sem_chave_devolve_vazio(monkeypatch):
    monkeypatch.setattr(jobs, "ADZUNA_APP_ID", None)
    assert jobs.fetch_adzuna("python") == []


def test_github_ignora_pr_e_filtra_por_skill(monkeypatch):
    data = [
        {"id": 1, "title": "[São Paulo] Dev Python na ACME",
         "html_url": "https://github.com/x/1", "body": "Python e Django"},
        {"id": 2, "title": "[Recife] Chef de cozinha",
         "html_url": "https://github.com/x/2", "body": "cozinha"},
        {"id": 3, "title": "PR sobre Python",
         "html_url": "https://github.com/x/3", "body": "Python",
         "pull_request": {}},
    ]
    monkeypatch.setattr(jobs.requests, "get", lambda *a, **k: FakeResponse(data))
    result = jobs.fetch_github_issues("backend-br/vagas", ["python"])
    assert [j["id"] for j in result] == ["github-1"]
    assert result[0]["location"] == "São Paulo"
    assert result[0]["title"] == "Dev Python na ACME"


def test_fonte_com_erro_nao_derruba_as_outras(monkeypatch):
    def quebra(*args, **kwargs):
        raise jobs.requests.RequestException("falhou")

    monkeypatch.setattr(jobs.requests, "get", quebra)
    assert jobs.fetch_jobs_for_skills(["python"]) == []
