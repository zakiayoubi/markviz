from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .database import Base, engine

app = FastAPI()

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local dev
        "https://markviz.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging config
logging.basicConfig(level=logging.INFO)


from .routes import auth, stocks, portfolio

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)


# health check route
@app.get("/live")
def live():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"status": "ok", "message": "MarkViz API is running"}
