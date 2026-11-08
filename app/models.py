from datetime import datetime, timezone

from sqlalchemy import JSON, CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def now_utc():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255)) 


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    year: Mapped[int]
    director: Mapped[str] = mapped_column(String(255))
    genres: Mapped[list] = mapped_column(JSON)
    rating: Mapped[float] 
    duration: Mapped[str] = mapped_column(String(50))
    synopsis: Mapped[str] = mapped_column(Text)
    poster_url: Mapped[str] = mapped_column(Text)
    cast: Mapped[list] = mapped_column(JSON) 


class Watchlist(Base):
    __tablename__ = "watchlists"
    __table_args__ = (UniqueConstraint("user_id", "movie_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    created_at: Mapped[datetime] = mapped_column(default=now_utc)

    movie: Mapped["Movie"] = relationship() 


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id"), 
        CheckConstraint("rating BETWEEN 1 AND 5"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    rating: Mapped[int]  
    review: Mapped[str | None] = mapped_column(Text)  
    created_at: Mapped[datetime] = mapped_column(default=now_utc)

    movie: Mapped["Movie"] = relationship()
