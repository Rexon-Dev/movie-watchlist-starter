"""Bentuk data request (masuk) dan response (keluar). Pydantic memvalidasi otomatis."""
from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator

Username = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=50)]


# ---------- Auth ----------
class RegisterIn(BaseModel):
    username: Username
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_max_72_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password maksimal 72 byte")
        return value


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str


class RegisterOut(BaseModel):
    message: str
    user: UserOut


class LoginOut(BaseModel):
    token: str
    user: UserOut


# ---------- Movies ----------
class MovieOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    year: int
    director: str
    genres: list[str]
    rating: float
    duration: str
    synopsis: str
    poster_url: str
    cast: list[str]


# ---------- Watchlist ----------
class WatchlistIn(BaseModel):
    movieId: int = Field(ge=1)


class WatchlistAddedOut(BaseModel):
    message: str
    movieId: int


class MessageOut(BaseModel):
    message: str


# ---------- Watched & Review ----------
class WatchedIn(BaseModel):
    movieId: int = Field(ge=1)
    rating: int = Field(ge=1, le=5)
    review: str | None = Field(default=None, max_length=2000)

    @field_validator("review")
    @classmethod
    def empty_review_becomes_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class WatchedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    movie_id: int
    rating: int
    review: str | None
    created_at: datetime
    movie: MovieOut

    @field_validator("created_at")
    @classmethod
    def mark_as_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


# ---------- Rekomendasi Gemini ----------
class RecommendIn(BaseModel):
    prompt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]


class RecommendOut(BaseModel):
    movie_id: int
    reasoning: str
