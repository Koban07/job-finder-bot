import re

from pypdf import PdfReader

# Adicione aqui as tecnologias que importam para você
SKILLS = [
    "python", "java", "javascript", "typescript", "c#", "c++", "php", "golang",
    "sql", "postgresql", "mysql", "mongodb", "django", "flask", "fastapi",
    "react", "vue", "angular", "node", "spring", "docker", "kubernetes",
    "git", "aws", "azure", "linux", "excel", "power bi", "pandas", "html",
    "css", "pytest", "machine learning", "data science",
]


def extract_text(path: str) -> str:
    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def extract_skills(text: str) -> list[str]:
    lower = text.lower()
    found = []
    for skill in SKILLS:
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, lower):
            found.append(skill)
    return found
