from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

app = FastAPI()

origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
origins = [o.strip() for o in origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
