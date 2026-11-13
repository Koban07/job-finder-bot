import re

import requests

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"


def clean_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "")


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
        })
    return jobs


def fetch_jobs_for_skills(skills: list[str], per_skill: int = 30) -> list[dict]:
    seen = set()
    result = []
    for skill in skills[:3]:  # poucas chamadas: a API pede uso moderado
        for job in fetch_remotive(skill, per_skill):
            if job["id"] not in seen:
                seen.add(job["id"])
                result.append(job)
    return result
