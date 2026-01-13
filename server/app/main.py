from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .database import Base, engine
from .models import User, Holding  # Import models FIRST

app = FastAPI()

# Now create tables (Base knows about User, Holding)
try:
    Base.metadata.create_all(bind=engine)
    logging.info("✅ Database tables created successfully")
except Exception as e:
    logging.error(f"❌ Failed to create tables: {e}")

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

logging.basicConfig(level=logging.INFO)

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
