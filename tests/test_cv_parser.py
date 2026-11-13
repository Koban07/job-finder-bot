from src.cv_parser import extract_skills


def test_encontra_skills():
    skills = extract_skills("Trabalho com Python, SQL e Docker")
    assert "python" in skills
    assert "sql" in skills


def test_java_nao_confunde_com_javascript():
    assert "java" not in extract_skills("Experiência com JavaScript")
