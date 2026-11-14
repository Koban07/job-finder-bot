import logging
import re

import requests

from src.config import ADZUNA_APP_ID, ADZUNA_APP_KEY

logger = logging.getLogger(__name__)

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"
ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/br/search/1"
GITHUB_REPOS = ["backend-br/vagas", "frontendbr/vagas"]


def clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "")


def mentions_any(text: str, skills: list[str]) -> bool:
    lower = text.lower()
    for skill in skills:
        if re.search(r"(?<!\w)" + re.escape(skill) + r"(?!\w)", lower):
            return True
    return False


def fetch_remotive(search: str, limit: int = 30) -> list[dict]:
    resp = requests.get(
        REMOTIVE_URL, params={"search": search, "limit": limit}, timeout=20
    )
    resp.raise_for_status()
    jobs = []
    for j in resp.json().get("jobs", []):
        jobs.append({
            "id": f"remotive-{j['id']}",
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "location": j.get("candidate_required_location", ""),
            "url": j.get("url", ""),
            "description": clean_html(j.get("description", "")),
            "source": "Remotive",
        })
    return jobs


def fetch_adzuna(search: str, limit: int = 30) -> list[dict]:
    if not (ADZUNA_APP_ID and ADZUNA_APP_KEY):
        return []  # sem chaves configuradas, a fonte é ignorada
    resp = requests.get(
        ADZUNA_URL,
        params={
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "what": search,
            "results_per_page": limit,
        },
        timeout=20,
    )
    resp.raise_for_status()
    jobs = []
    for j in resp.json().get("results", []):
        jobs.append({
            "id": f"adzuna-{j['id']}",
            "title": clean_html(j.get("title", "")).strip(),
            "company": (j.get("company") or {}).get("display_name", ""),
            "location": (j.get("location") or {}).get("display_name", ""),
            "url": j.get("redirect_url", ""),
            "description": clean_html(j.get("description", "")),
            "source": "Adzuna",
        })
    return jobs


def fetch_github_issues(repo: str, skills: list[str], limit: int = 50) -> list[dict]:
    resp = requests.get(
        f"https://api.github.com/repos/{repo}/issues",
        params={"state": "open", "per_page": limit},
        headers={"Accept": "application/vnd.github+json"},
        timeout=20,
    )
    resp.raise_for_status()
    jobs = []
    for issue in resp.json():
        if "pull_request" in issue:
            continue
        title = issue.get("title", "")
        body = (issue.get("body") or "")[:3000]
        if not mentions_any(f"{title} {body}", skills):
            continue
        city = re.match(r"\s*\[([^\]]+)\]", title)
        clean_title = re.sub(r"^\s*\[[^\]]+\]\s*", "", title) or title
        jobs.append({
            "id": f"github-{issue['id']}",
            "title": clean_title,
            "company": "Não informada",
            "location": city.group(1) if city else "Brasil",
            "url": issue.get("html_url", ""),
            "description": body,
            "source": f"GitHub {repo}",
        })
    return jobs


def _safe(fetcher, *args) -> list[dict]:
    """Se uma fonte falhar, devolve lista vazia e as outras continuam."""
    try:
        return fetcher(*args)
    except requests.RequestException as exc:
        # não registrar str(exc): a mensagem pode conter a URL com a chave
        status = getattr(getattr(exc, "response", None), "status_code", None)
        logger.warning(
            "Fonte %s falhou (%s, status %s)",
            fetcher.__name__, type(exc).__name__, status,
        )
        return []


def fetch_jobs_for_skills(skills: list[str], per_skill: int = 30) -> list[dict]:
    seen = set()
    result = []

    def add(jobs: list[dict]):
        for job in jobs:
            if job["id"] not in seen:
                seen.add(job["id"])
                result.append(job)

    for skill in skills[:3]:  # poucas chamadas: as APIs pedem uso moderado
        add(_safe(fetch_remotive, skill, per_skill))
        add(_safe(fetch_adzuna, skill, per_skill))
    for repo in GITHUB_REPOS:
        add(_safe(fetch_github_issues, repo, skills))
    return result
