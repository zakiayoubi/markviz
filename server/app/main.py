from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.fmp_api import (
    get_income_statement_info,
    get_company_profile,
    get_num_shares,
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# landing route
@app.get("/")
def get_root():
    return {"message": "Welcome to MarkViz!"}


# At the bottom, after creating app = FastAPI()
from .routes import auth, stocks, portfolio

app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)


# health check route
@app.get("/live")
def live():
    return {"status": "ok"}


# summary route
@app.get("/stock_summary/{symbol}")
def get_stock_summary(symbol: str) -> dict:
    income = get_income_statement_info(symbol)
    profile = get_company_profile(symbol)
    shares = get_num_shares(symbol)

    for result in (income, profile, shares):
        if "error" in result or "HTTP Error" in result:
            raise HTTPException(status_code=400, detail=result)

    stock_summary = {**profile, **income, **shares}
    return {"summary": stock_summary}
