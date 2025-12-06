import httpx
# importing the httpx module and using the get function
# from this module through: httpx.get
from app.config import (
    FMP_API_KEY,
    base_URL,
    income_statement_endpoint,
    company_profile_endpoint,
    shares_float_endpoint,
)


def safe_fmp_get(url: str, parameters: dict) -> dict:
    """
    helper function to safely call the FMP API
    and return the data or an error dict
    """
    try:
        response = httpx.get(url, params=parameters)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        return {
            "HTTP Error": f"HTTP {e.response.status_code}: {e.response.text}"
        }
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

    if not isinstance(data, list) or len(data) == 0:
        return {"error": "No income statement data found"}

    item = data[0]
    return {
        "revenue": item.get("revenue", 0),
        "net_income": item.get("netIncome", 0),
    }


def get_company_profile(ticker: str) -> dict:
    parameters = {"symbol": ticker, "apikey": FMP_API_KEY}
    data = safe_fmp_get(base_URL + company_profile_endpoint, parameters)

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

    if not isinstance(data, list) or len(data) == 0:
        return {"error": "No shares data found"}

    item = data[0]
    return {
        "shares_outstanding": item.get("outstandingShares", 0),
    }
