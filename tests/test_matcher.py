from src.matcher import score_jobs


def test_vaga_compativel_fica_em_primeiro():
    cv = "Desenvolvedor Python com experiência em Django, SQL e Docker"
    jobs = [
        {"id": "1", "title": "Chef de cozinha",
         "description": "Cozinhar pratos para restaurante"},
        {"id": "2", "title": "Python Developer",
         "description": "Django, SQL e Docker no dia a dia"},
    ]
    ranked = score_jobs(cv, jobs)
    assert ranked[0]["id"] == "2"
    assert ranked[0]["score"] > ranked[1]["score"]


def test_lista_vazia():
    assert score_jobs("qualquer coisa", []) == []
