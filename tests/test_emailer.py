from src.emailer import build_message


def test_monta_email_e_escapa_html():
    jobs = [{
        "title": "Python Dev <b>",
        "company": "ACME",
        "location": "Brazil",
        "url": "https://exemplo.com/1",
        "score": 0.42,
        "source": "Adzuna",
    }]
    msg = build_message(jobs, "a@x.com", "b@x.com")
    assert msg["To"] == "b@x.com"
    assert "1 vaga" in msg["Subject"]
    plain = msg.get_body(preferencelist=("plain",)).get_content()
    html = msg.get_body(preferencelist=("html",)).get_content()
    assert "42%" in plain
    assert "Fonte: Adzuna" in plain
    assert "&lt;b&gt;" in html
