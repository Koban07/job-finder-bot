import smtplib
from email.message import EmailMessage
from html import escape

from src.config import EMAIL_APP_PASSWORD, EMAIL_FROM


def build_message(jobs: list[dict], sender: str, to: str) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Job Finder: {len(jobs)} vaga(s) para você hoje"
    msg["From"] = sender
    msg["To"] = to

    plain = []
    html = ["<h2>Suas vagas de hoje</h2>"]
    for job in jobs:
        pct = round(job["score"] * 100)
        source = job.get("source", "Remotive")
        plain.append(
            f"{job['title']}\n"
            f"{job['company']} - {job['location']}\n"
            f"Compatibilidade: {pct}%\n"
            f"Fonte: {source}\n"
            f"{job['url']}\n"
        )
        html.append(
            f"<p><b>{escape(job['title'])}</b><br>"
            f"{escape(job['company'])} - {escape(job['location'])}<br>"
            f"Compatibilidade: {pct}% | Fonte: {escape(source)}<br>"
            f'<a href="{escape(job["url"])}">Ver vaga</a></p>'
        )
    footer = (
        "Vagas obtidas via Remotive (remotive.com), Adzuna (adzuna.com.br) "
        "e comunidades de vagas do GitHub."
    )
    plain.append(footer)
    html.append(f"<p><small>{footer}</small></p>")

    msg.set_content("\n".join(plain))
    msg.add_alternative("".join(html), subtype="html")
    return msg


def send_email(msg: EmailMessage):
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
        server.send_message(msg)
