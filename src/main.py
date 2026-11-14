import argparse
import logging
import os
import sys

import requests

from src.config import CV_PATH, EMAIL_FROM, EMAIL_TO, MAX_JOBS, MIN_SCORE
from src.cv_parser import extract_skills, extract_text
from src.database import init_db, mark_sent, was_sent
from src.emailer import build_message, send_email
from src.jobs import fetch_jobs_for_skills
from src.matcher import score_jobs

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run(dry_run: bool = False) -> int:
    init_db()

    if not os.path.exists(CV_PATH):
        logger.error("Currículo não encontrado em %s", CV_PATH)
        return 1
    text = extract_text(CV_PATH)
    if not text:
        logger.error("Não consegui ler texto do PDF. Ele pode ser escaneado.")
        return 1

    skills = extract_skills(text)
    logger.info("Skills encontradas: %s", skills)
    if not skills:
        logger.error("Nenhuma skill encontrada. Ajuste SKILLS em cv_parser.py")
        return 1

    try:
        jobs = fetch_jobs_for_skills(skills)
    except requests.RequestException:
        logger.exception("Falha ao buscar vagas")
        return 1

    jobs = [j for j in jobs if not was_sent(j["id"])]
    ranked = score_jobs(text, jobs)
    logger.info("Top scores: %s", [round(j["score"], 2) for j in ranked[:10]])

    best = [j for j in ranked if j["score"] >= MIN_SCORE][:MAX_JOBS]
    if not best:
        logger.info("Nenhuma vaga nova boa o suficiente hoje.")
        return 0

    if dry_run:
        for j in best:
            pct = round(j["score"] * 100)
            src = j.get("source", "")
            print(f"{pct}% | {j['title']} | {j['company']} | {src} | {j['url']}")
        return 0

    send_email(build_message(best, EMAIL_FROM, EMAIL_TO))
    for j in best:
        mark_sent(j["id"])
    logger.info("E-mail enviado com %d vaga(s)", len(best))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Envia vagas por e-mail")
    parser.add_argument(
        "--dry-run", action="store_true", help="mostra as vagas sem enviar e-mail"
    )
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
