from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Movie
from app.schemas import MovieOut

router = APIRouter(prefix="/api/movies", tags=["Movies"])


@router.get("", response_model=list[MovieOut])
def list_movies(
    search: str | None = None, 
    genre: str | None = None, 
    db: Session = Depends(get_db),
):
    movies = db.scalars(select(Movie).order_by(Movie.id)).all()

    if search and search.strip():
        keyword = search.strip().lower()
        movies = [m for m in movies if keyword in m.title.lower() or keyword in m.director.lower()]
    if genre and genre.strip():
        wanted = genre.strip().lower()
        movies = [m for m in movies if wanted in (g.lower() for g in m.genres)]

    return movies


@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(Movie, movie_id)
    if movie is None:
        raise HTTPException(404, "Film tidak ditemukan")
    return movie
