from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Movie, User, Watchlist
from app.schemas import MessageOut, MovieOut, WatchlistAddedOut, WatchlistIn
from app.security import get_current_user

router = APIRouter(prefix="/api/watchlist", tags=["Watchlist"])


@router.get("", response_model=list[MovieOut])
def get_watchlist(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(Watchlist)
        .where(Watchlist.user_id == user.id)
        .order_by(Watchlist.created_at.desc(), Watchlist.id.desc())
    ).all()
    return [row.movie for row in rows]


@router.post("", response_model=WatchlistAddedOut, status_code=201)
def add_to_watchlist(
    data: WatchlistIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(Movie, data.movieId) is None:
        raise HTTPException(404, "Film tidak ditemukan")

    already = db.scalar(
        select(Watchlist).where(Watchlist.user_id == user.id, Watchlist.movie_id == data.movieId)
    )
    if already:
        raise HTTPException(409, "Film sudah ada di watchlist")

    db.add(Watchlist(user_id=user.id, movie_id=data.movieId))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Film sudah ada di watchlist")

    return WatchlistAddedOut(message="Film ditambahkan ke watchlist", movieId=data.movieId)


@router.delete("/{movie_id}", response_model=MessageOut)
def remove_from_watchlist(
    movie_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.scalar(
        select(Watchlist).where(Watchlist.user_id == user.id, Watchlist.movie_id == movie_id)
    )
    if row is None:
        raise HTTPException(404, "Film tidak ada di watchlist")

    db.delete(row)
    db.commit()
    return MessageOut(message="Film dihapus dari watchlist")
