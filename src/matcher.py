from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def score_jobs(cv_text: str, jobs: list[dict]) -> list[dict]:
    """Devolve as vagas com uma nota (0 a 1), da mais para a menos compatível."""
    if not jobs:
        return []
    docs = [cv_text]
    for job in jobs:
        docs.append(f"{job['title']} {job['title']} {job['description']}")
    matrix = TfidfVectorizer(lowercase=True, ngram_range=(1, 2)).fit_transform(docs)
    sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    scored = [{**job, "score": float(s)} for job, s in zip(jobs, sims)]
    return sorted(scored, key=lambda j: j["score"], reverse=True)
