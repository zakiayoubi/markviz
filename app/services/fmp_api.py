import httpx
from app.config import (
    FMP_API_key,
    base_URL,
    income_statement_endpoint,
    company_profile_endpoint,
    shares_float_endpoint,
)

companies = {

    "Apple Inc.": "AAPL",
    "Tesla Inc.": "TSLA",
    "Amazon.com Inc.": "AMZN",
    "Microsoft Corporation": "MSFT",
    "NVIDIA Corporation": "NVDA",
    "Alphabet Inc. (Google)": "GOOGL",
    "Meta Platforms Inc.": "META",
    "Netflix Inc.": "NFLX",
    "JPMorgan Chase & Co.": "JPM",
    "Visa Inc.": "V",
    "Bank of America Corporation": "BAC",
    "Advanced Micro Devices Inc.": "AMD",
    "PayPal Holdings Inc.": "PYPL",
    "The Walt Disney Company": "DIS",
    "AT&T Inc.": "T",
    "Pfizer Inc.": "PFE",
    "Costco Wholesale Corporation": "COST",
    "Intel Corporation": "INTC",
    "The Coca-Cola Company": "KO",
    "Target Corporation": "TGT",
    "Nike Inc.": "NKE",
    "SPDR S&P 500 ETF Trust": "SPY",
    "The Boeing Company": "BA",
    "Alibaba Group Holding Limited": "BABA",
    "Exxon Mobil Corporation": "XOM",
    "Walmart Inc.": "WMT",
    "General Electric Company": "GE",
    "Cisco Systems Inc.": "CSCO",
    "Verizon Communications Inc.": "VZ",
    "Johnson & Johnson": "JNJ",
    "Chevron Corporation": "CVX",
    "Palantir Technologies Inc.": "PLTR",
    "Block Inc. (Square)": "SQ",
    "Shopify Inc.": "SHOP",
    "Starbucks Corporation": "SBUX",
    "SoFi Technologies Inc.": "SOFI",
    "Robinhood Markets Inc.": "HOOD",
    "Roblox Corporation": "RBLX",
    "Snap Inc.": "SNAP",
    "Uber Technologies Inc.": "UBER",
    "FedEx Corporation": "FDX",
    "AbbVie Inc.": "ABBV",
    "Etsy Inc.": "ETSY",
    "Moderna Inc.": "MRNA",
    "Lockheed Martin Corporation": "LMT",
    "General Motors Company": "GM",
    "Ford Motor Company": "F",
    "Rivian Automotive Inc.": "RIVN",
    "Lucid Group Inc.": "LCID",
    "Carnival Corporation": "CCL",
    "Delta Air Lines Inc.": "DAL",
    "United Airlines Holdings Inc.": "UAL"
}


def get_income_statement_info(ticker: str):
    parameters = {
        "symbol": ticker,
        "period": "annual",
        "limit": 1,
        "apikey": FMP_API_key,
    }
    response = httpx.get(base_URL + income_statement_endpoint, params=parameters)
    revenue = response.json()[0]["revenue"]
    net_income = response.json()[0]["netIncome"]
    return {
        "revenue": revenue,
        "net_income": net_income
    }

def get_company_profile(ticker: str):
    parameters = {
        "symbol": ticker,
        "apikey": FMP_API_key,
    }
    response = httpx.get(base_URL + company_profile_endpoint, params=parameters)
    company_name = response.json()[0]["companyName"]
    current_price = response.json()[0]["price"]
    current_market_cap = response.json()[0]["marketCap"]
    exchange = response.json()[0]["exchange"]

    return {
        "company_name": company_name,
        "current_price": current_price,
        "current_market_cap": current_market_cap,
        "exchange": exchange,
    }

def get_num_shares(ticker: str):
    parameters = {
        "symbol": ticker,
        "apikey": FMP_API_key,
    }
    response = httpx.get(base_URL + shares_float_endpoint, params=parameters)
    shares_outstanding = response.json()[0]["outstandingShares"]

    return {
        "shares_outstanding": shares_outstanding,
    }

