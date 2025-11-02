from fastapi import FastAPI, HTTPException
from app.services.fmp_api import (
    get_income_statement_info,
    get_company_profile,
    get_num_shares,
    )


app = FastAPI()

@app.get("/")
def get_root():
    return {"message": "Welcome to MarkViz!"}


@app.get("/stock_summary/{symbol}")
def get_stock_summary(symbol: str):
    income = get_income_statement_info(symbol)
    profile = get_company_profile(symbol)
    shares = get_num_shares(symbol)

    for result in (income, profile, shares):
        if "error" in result or "HTTP Error" in result:
            raise HTTPException(status_code=400, detail=result)

    stock_summary = {**income, **profile, **shares}
    return {"summary": stock_summary}



    

