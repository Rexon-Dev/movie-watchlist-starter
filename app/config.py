import os

from dotenv import load_dotenv

load_dotenv()  

DATABASE_URL = "sqlite:///./filmlog.db"

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY belum diisi. Salin .env.example menjadi .env lalu isi nilainya."
    )
