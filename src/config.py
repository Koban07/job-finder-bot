import os

from dotenv import load_dotenv

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO") or EMAIL_FROM
CV_PATH = os.getenv("CV_PATH", "data/curriculo.pdf")
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.10"))
MAX_JOBS = int(os.getenv("MAX_JOBS", "5"))
DB_PATH = os.getenv("DB_PATH", "jobs.db")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
