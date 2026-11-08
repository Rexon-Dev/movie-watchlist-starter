from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Movie, Review, User
from app.schemas import WatchedIn, WatchedOut
from app.security import get_current_user

router = APIRouter(prefix="/api/watched", tags=["Watched & Review"])


@router.get("", response_model=list[WatchedOut])
def get_watched(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Review)
        .where(Review.user_id == user.id)
        .order_by(Review.created_at.desc(), Review.id.desc())
    ).all()


@router.post("", response_model=WatchedOut, status_code=201)
def add_watched(
    data: WatchedIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(Movie, data.movieId) is None:
        raise HTTPException(404, "Film tidak ditemukan")

    already = db.scalar(
        select(Review).where(Review.user_id == user.id, Review.movie_id == data.movieId)
    )
    if already:
        raise HTTPException(409, "Film ini sudah ada di riwayat tontonan")

    review = Review(
        user_id=user.id,  
        movie_id=data.movieId,
        rating=data.rating,
        review=data.review,
    )
    db.add(review)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Film ini sudah ada di riwayat tontonan")
    db.refresh(review)
    return review
