from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .database import Base, engine
from .models import User, Holding  # Import models FIRST
from contextlib import asynccontextmanager
from .scheduler import start_scheduler, shutdown_scheduler


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    Base.metadata.create_all(bind=engine)
    logging.info("✅ Database tables created")

    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://markviz.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routes import auth, stocks, portfolio

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)


@app.get("/live")
def live():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"status": "ok", "message": "MarkViz API is running"}
