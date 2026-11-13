from src import database


def test_marca_e_consulta_vaga(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "teste.db"))
    database.init_db()
    assert not database.was_sent("remotive-1")
    database.mark_sent("remotive-1")
    assert database.was_sent("remotive-1")
