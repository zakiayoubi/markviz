from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import httpx
import yfinance as yf
import asyncio
from ..config import (
    API_NINJAS_KEY,
    NINJAS_BASE_URL,
    SP500_ENDPOINT,
    MASSIVE_API_KEY,
    MASSIVE_BASE_URL,
    MASSIVE_All_Tickers_ENDPOINT,
)


router = APIRouter(prefix="/stocks", tags=["stocks"])

# Global cache
CACHE = {
    "static_list": None,
    "static_timestamp": None,
    "price_data": None,
    "price_timestamp": None,
}

STATIC_CACHE_DURATION = timedelta(days=1)
PRICE_CACHE_DURATION = timedelta(minutes=20)


async def fetch_sp500_constituents():
    """Fetch and cache S&P 500 static list from API Ninjas (once a day)."""
    now = datetime.now()
    if (
        CACHE["static_list"] is None
        or (now - CACHE["static_timestamp"]) > STATIC_CACHE_DURATION
    ):
        url = NINJAS_BASE_URL + SP500_ENDPOINT
        headers = {"X-Api-Key": API_NINJAS_KEY}
        try:
            response = await httpx.AsyncClient().get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            CACHE["static_list"] = [
                {
                    "ticker": stock["ticker"],
                    "name": stock["company_name"],
                    "sector": stock["sector"],
                }
                for stock in data
            ]
            CACHE["static_timestamp"] = now
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500, detail=f"API Ninjas error: {str(e)}"
            )


def fetch_price_data():
    """Fetch and cache price/market cap data from yfinance (every 20 min)."""
    now = datetime.now()
    if (
        CACHE["price_data"] is None
        or (now - CACHE["price_timestamp"]) > PRICE_CACHE_DURATION
    ):
        if CACHE["static_list"] is None:
            raise HTTPException(
                status_code=500, detail="Constituents not loaded"
            )

        tickers = [s["ticker"] for s in CACHE["static_list"]]
        try:
            infos = {}
            for ticker in tickers:
                try:
                    info = yf.Ticker(ticker).info
                    infos[ticker] = {
                        "market_cap": info.get("marketCap", 0),
                        "current_price": info.get("currentPrice", 0),
                        "previous_close": info.get("previousClose", 0),
                        "open": info.get("open", 0),
                        "close": info.get("close", 0),
                        "high": info.get("high", 0),
                        "low": info.get("low", 0),
                    }
                except:
                    continue  # Skip bad tickers
            CACHE["price_data"] = infos
            CACHE["price_timestamp"] = now
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"yfinance error: {str(e)}"
            )


@router.get("/sp500")
async def get_sp500():
    """Return combined S&P 500 data (static + prices)."""
    # Fetch static list if needed
    await fetch_sp500_constituents()

    # Fetch price data if needed
    fetch_price_data()

    # Combine
    result = []
    for stock in CACHE["static_list"]:
        ticker = stock["ticker"]
        price = CACHE["price_data"].get(ticker, {})
        change_percent = 0
        if (
            price.get("current_price", 0) > 0
            and price.get("previous_close", 0) > 0
        ):
            change_percent = round(
                (
                    (price["current_price"] - price["previous_close"])
                    / price["previous_close"]
                )
                * 100,
                2,
            )

        result.append(
            {
                **stock,
                "market_cap": price.get("market_cap", 0),
                "current_price": price.get("current_price", 0),
                "change_percent": change_percent,
                "low": price.get("low", 0),
                "high": price.get("high", 0),
                "open": price.get("open", 0),
                "close": price.get("close", 0),
            }
        )

    return {"data": result}


@router.get("/{ticker}")
def get_stock_info(ticker: str, range: str):
    try:
        stock = yf.Ticker(ticker)
        config = {
            "1D": ("1d", "1m"),
            "1W": ("1wk", "30m"),
            "1M": ("1mo", "1d"),
            "3M": ("3mo", "1d"),
            "6M": ("6mo", "1d"),
            "YTD": ("ytd", "1d"),
            "1Y": ("2y", "1d"),
            "5Y": ("5y", "1wk"),
            "MAX": ("max", "1mo"),
        }

        period, interval = config.get(range)
        hist = stock.history(period=period, interval=interval)
        if hist.empty:
            raise HTTPException(status_code=404, detail="No Data Available.")
        prices = hist["Close"].round(2).tolist()

        if range == "1D":
            labels = hist.index.strftime("%H:%M").tolist()
            prices = hist["Close"].round(2).tolist()
        else:
            # For all other ranges
            if interval == "1mo":
                labels = hist.index.strftime("%Y").tolist()
            elif interval == "1wk":
                labels = hist.index.strftime("%b %Y").tolist()
            else:
                labels = hist.index.strftime("%b %d").tolist()

        return {"data": {"labels": labels, "prices": prices}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/about/{ticker}")
async def get_about(ticker: str):
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        # Extract the fields you want
        about = {
            "name": info.get("longName") or info.get("shortName"),
            "summary": info.get(
                "longBusinessSummary", "No description available"
            ),
            "ceo": info.get("ceo", "N/A"),  # Not always available
            "founded": info.get("founded", "N/A"),  # Rare
            "headquarters": f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}".strip(
                ", "
            ),
            "employees": info.get("fullTimeEmployees"),
            "website": info.get("website"),
        }

        return {"data": about}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching about info: {str(e)}"
        )


@router.get("/stats/{ticker}")
async def get_stock_stats(ticker: str):
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        # Helper to safely get values
        def get(key, default="N/A"):
            val = info.get(key)
            if val is None or val == "":
                return default
            return val

        stats = {
            "valuation": {
                "market_cap": get("marketCap"),
                "pe_ratio": get("trailingPE"),
                "forward_pe": get("forwardPE"),
                "price_to_sales": get("priceToSalesTrailing12Months"),
                "price_to_book": get("priceToBook"),
            },
            "performance": {
                "change_today_percent": get("regularMarketChangePercent"),
                "fifty_two_week_high": get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": get("fiftyTwoWeekLow"),
                "ytd_return": get("ytdReturn"),  # Rare, calculate if needed
                "one_year_return": get("52WeekChange"),
            },
            "financial_health": {
                "debt_to_equity": get("debtToEquity"),
                "current_ratio": get("currentRatio"),
                "profit_margin": get("profitMargins"),
                "roe": get("returnOnEquity"),
            },
            "trading_activity": {
                "volume_today": get("volume"),
                "avg_volume": get("averageVolume"),
                "beta": get("beta"),
                "shares_outstanding": get("sharesOutstanding"),
                "float": get("floatShares"),
            },
        }

        # Format large numbers
        def format_large_num(num):
            if num == "N/A":
                return "N/A"
            if num >= 1e12:
                return f"${num / 1e12:.2f}T"
            elif num >= 1e9:
                return f"${num / 1e9:.2f}B"
            elif num >= 1e6:
                return f"${num / 1e6:.2f}M"
            return f"${num:.2f}"

        # Apply formatting
        stats["valuation"]["market_cap"] = format_large_num(
            stats["valuation"]["market_cap"]
        )

        return {"data": stats}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching stats: {str(e)}"
        )


@router.get("/summary/{ticker}")
async def get_summary(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        def get(key, default="N/A"):
            val = info.get(key)
            if val is None or (isinstance(val, str) and val.strip() == ""):
                return default
            return val

        # Current price and daily change using info fields
        current_price = get("currentPrice", get("regularMarketPrice", "N/A"))
        prev_close = get(
            "previousClose", get("regularMarketPreviousClose", "N/A")
        )

        if current_price != "N/A" and prev_close != "N/A" and prev_close != 0:
            daily_change = round(current_price - prev_close, 2)
            percent_change = round((daily_change / prev_close) * 100, 2)
        else:
            daily_change = "N/A"
            percent_change = "N/A"

        summary = {
            "logo": get("logo_url", "N/A"),
            "stock_ticker": ticker.upper(),
            "name": get("longName", get("shortName", "N/A")),
            "exchange": get("primary_exchange", "N/A"),
            "current_price": (
                round(current_price, 2) if current_price != "N/A" else "N/A"
            ),
            "daily_change": daily_change,
            "percent_change": percent_change,
            "market_status": (
                "Open" if get("marketState") == "REGULAR" else "Closed"
            ),
            "date": get("regularMarketTime", "N/A"),
            "earnings_date": get("earningsTimestamp", "N/A"),
            "eps": get("trailingEps", "N/A"),
            "market_cap": get("marketCap", "N/A"),
            "pe": get("trailingPE", "N/A"),
            "volume": get("volume", get("regularMarketVolume", "N/A")),
            "bid_ask": f"{get('bid', 0)} / {get('ask', 0)}",
            "day_high": get("dayHigh", get("regularMarketDayHigh", "N/A")),
            "day_low": get("dayLow", get("regularMarketDayLow", "N/A")),
            "year_high": get("fiftyTwoWeekHigh", "N/A"),
            "year_low": get("fiftyTwoWeekLow", "N/A"),
        }

        print(summary)
        return {"data": summary}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching summary: {str(e)}"
        )


async def fetch_tickers(exchange: str):
    # exchange_codes = {"nasdaq": "XNAS", "nyse": "XNYS"}
    exchange_codes = {
        "nyse": "XNYS"
    }  # comment this line and uncomment the above line later
    url = MASSIVE_BASE_URL + MASSIVE_All_Tickers_ENDPOINT
    params = {
        "market": "stocks",
        "exchange": exchange_codes[exchange],
        "limit": 1000,
        "apiKey": MASSIVE_API_KEY,
    }

    tickers = []
    async with httpx.AsyncClient() as client:
        try:
            # First request with params
            response = await client.get(
                url, params=params
            )  # Fixed: headers not header
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            for stock in results:
                tickers.append(
                    {
                        "ticker": stock.get("ticker"),
                        "name": stock.get("name"),
                        "exchange": exchange.upper(),
                    }
                )

            next_url = data.get("next_url")
            print(f"Next URL: {next_url}")

            # Subsequent requests
            while next_url:
                # await asyncio.sleep(30)
                # Append API key to next_url
                url_with_key = f"{next_url}&apiKey={MASSIVE_API_KEY}"

                response = await client.get(
                    url_with_key
                )  # No params on pagination
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                for stock in results:
                    tickers.append(
                        {
                            "ticker": stock.get("ticker"),
                            "name": stock.get("name"),
                            "exchange": exchange.upper(),
                        }
                    )

                next_url = data.get("next_url")
                print(f"Next URL: {next_url}")

            return tickers
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, detail=f"API error: {e}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Server failed: {str(e)}"
            )


CACHE_ALLTICKERS_LIST = None
CACHE_ALLTICKERS_TIMESTAMP = None
CACHE_ALLTICKERS_DURATION = timedelta(days=1)


@router.get("/all/tickers")
async def get_all_tickers():
    global CACHE_ALLTICKERS_LIST, CACHE_ALLTICKERS_TIMESTAMP
    now = datetime.now()

    # Return cached if fresh
    if (
        CACHE_ALLTICKERS_LIST is not None
        and (now - CACHE_ALLTICKERS_TIMESTAMP) < CACHE_ALLTICKERS_DURATION
    ):
        return {"data": CACHE_ALLTICKERS_LIST}
    # nyse, nasdaq = await asyncio.gather(
    #     fetch_tickers("nyse"), fetch_tickers("nasdaq")
    # )
    # tickers = nyse + nasdaq
    tickers = await fetch_tickers("nyse")
    CACHE_ALLTICKERS_LIST = tickers
    CACHE_ALLTICKERS_TIMESTAMP = now

    return {"data": CACHE_ALLTICKERS_LIST}
