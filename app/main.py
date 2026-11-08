import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import models 
from app.database import Base, SessionLocal, engine
from app.routers import auth, movies, recommend, watched, watchlist
from app.seed import seed_movies

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        added = seed_movies(db)
    logger.info("Seeding film: %s film baru ditambahkan", added)
    yield


app = FastAPI(title="Movie Watchlist API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    field = ".".join(str(part) for part in first["loc"][1:])
    reason = first["msg"].removeprefix("Value error, ")
    message = f"{field}: {reason}" if field else reason
    return JSONResponse(status_code=400, content={"message": message})


app.include_router(auth.router)
app.include_router(recommend.router) 
app.include_router(movies.router)
app.include_router(watchlist.router)
app.include_router(watched.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Movie Watchlist API jalan"}
