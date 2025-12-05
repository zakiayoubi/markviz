import httpx
# importing the httpx module and using the get function from this module through: httpx.get


from app.config import (
    FMP_API_KEY,
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

def safe_fmp_get(url: str, parameters: dict) -> dict:

    """
    helper function to safely call the FMP API and return the data or an error dict
    """
    try:
        response = httpx.get(url, params=parameters)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {"HTTP Error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except httpx.RequestError:
        return {"error": "Network Error"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
        
def get_income_statement_info(ticker: str) -> dict:
    parameters = {
        "symbol": ticker,
        "period": "annual",
        "limit": 1,
        "apikey": FMP_API_KEY,
    }
    data = safe_fmp_get(base_URL + income_statement_endpoint, parameters)

    # ← FIXED: check for errors OR empty list
    if not isinstance(data, list) or len(data) == 0:
        return {"error": "No income statement data found"}

    item = data[0]
    return {
        "revenue": item.get("revenue", 0),
        "net_income": item.get("netIncome", 0)
    }


def get_company_profile(ticker: str) -> dict:
    parameters = {"symbol": ticker, "apikey": FMP_API_KEY}
    data = safe_fmp_get(base_URL + company_profile_endpoint, parameters)

    # ← FIXED: check for errors OR empty list
    if not isinstance(data, list) or len(data) == 0:
        return {"error": "Company not found"}

    item = data[0]
    return {
        "company_name": item.get("companyName", "Unknown"),
        "current_price": item.get("price", 0),
        "current_market_cap": item.get("marketCap", 0),
        "exchange": item.get("exchange", "Unknown"),
    }


def get_num_shares(ticker: str) -> dict:
    parameters = {"symbol": ticker, "apikey": FMP_API_KEY}
    data = safe_fmp_get(base_URL + shares_float_endpoint, parameters)

    # ← FIXED: check for errors OR empty list
    if not isinstance(data, list) or len(data) == 0:
        return {"error": "No shares data found"}

    item = data[0]
    return {
        "shares_outstanding": item.get("outstandingShares", 0),
    }