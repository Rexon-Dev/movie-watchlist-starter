"""Isi tabel movies dari data/movies.json. Aman dijalankan berulang kali."""
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Movie

MOVIES_JSON = Path(__file__).resolve().parent.parent / "data" / "movies.json"


def seed_movies(db: Session) -> int:
    """Tambahkan film yang belum ada (dicek lewat id). Kembalikan jumlah film baru."""
    with open(MOVIES_JSON, encoding="utf-8") as file:
        movies = json.load(file)

    added = 0
    for item in movies:
        if db.get(Movie, item["id"]) is None: 
            db.add(Movie(**item))
            added += 1
    db.commit()
    return added


if __name__ == "__main__":
    from app import models 

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        total_added = seed_movies(session)
    print(f"Seeding selesai. Film baru ditambahkan: {total_added}")
