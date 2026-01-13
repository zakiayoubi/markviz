from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import pytz
import httpx
import yfinance as yf
import logging
import asyncio
from ..services import stocks_services


# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/sp500")
async def get_sp500():
    """
    Return S&P 500 stocks with current prices and market data.

    Returns:
        JSON with list of stocks including ticker, name, sector, price, change%, market cap
    """
    # Fetch static list if needed (cached for 1 day)
    stocks = await stocks_services.fetch_sp500_constituents()

    # Fetch price data if needed (cached for 20 minutes)
    price_data = await stocks_services.fetch_price_data()

    # Combine static and price data
    result = []
    for stock in stocks[:5]:
        ticker = stock["ticker"]
        price_info = price_data.get(ticker, {})
        result.append({**stock, **price_info})

    return {"data": result}


@router.get("/{ticker}")
def get_stock_info(ticker: str, timeRange: str):
    """Get historical price data and current info for a stock."""
    try:
        stock = yf.Ticker(ticker)
        config = {
            "1D": ("1d", "5m"),
            "1W": ("1wk", "30m"),
            "1M": ("1mo", "1d"),
            "3M": ("3mo", "1d"),
            "6M": ("6mo", "1d"),
            "YTD": ("ytd", "1d"),
            "1Y": ("2y", "1d"),
            "5Y": ("5y", "1wk"),
            "MAX": ("max", "1mo"),
        }
        if timeRange not in config:
            logger.error("Invalid time range")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time range. Must be one of: {list(config.keys())}",
            )

        period, interval = config.get(timeRange)
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            logger.error("Was not able to fetch data")
            raise HTTPException(
                status_code=404, detail="No data available for this ticker"
            )
        # Format labels
        if timeRange == "1D":
            labels = hist.index.strftime("%H:%M").tolist()
        elif interval == "1mo":
            labels = hist.index.strftime("%Y").tolist()
        elif interval == "1wk":
            labels = hist.index.strftime("%b %Y").tolist()
        else:
            labels = hist.index.strftime("%b %d").tolist()

        prices = hist["Close"].round(2).tolist()

        # Fetch stock info once
        info = stock.info
        name = info.get("shortName", "N/A")
        exchange = info.get("fullExchangeName", "N/A")
        current_price = info.get("currentPrice", 0)
        previous_close = info.get("previousClose", 0)
        dollar_change = round(current_price - previous_close, 2)
        percent_change = round((dollar_change / previous_close) * 100, 2)

        detail = {
            "name": name,
            "exchange": exchange,
            "currentPrice": current_price,
            "dollarChange": dollar_change,
            "percentChange": percent_change,
        }

        data = [
            {"date": label, "price": price}
            for label, price in zip(labels, prices)
        ]

        logger.info(
            f"successfully fetched price data for {ticker} for {timeRange}"
        )
        return {"data": data, "stockDetail": detail}

    except Exception as e:
        logger.error(f"Failed to fetch {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch stock data"
        )


@router.get("/about/{ticker}")
def get_about(ticker: str):
    """
    Get company information and description for a stock.

    Args:
        ticker: Stock symbol (e.g., AAPL)

    Returns:
        Company details including name, summary, CEO, headquarters, employees, website
    """

    try:
        # Find CEO
        ceo = "N/A"
        company_officers = stocks_services.get(ticker, "companyOfficers", [])
        for officer in company_officers:
            title = officer.get("title", "").upper()
            if "CEO" in title or "CHIEF EXECUTIVE" in title:
                ceo = officer.get("name", "N/A")
                break

        # Build headquarters string
        city = stocks_services.get(ticker, "city", "")
        state = stocks_services.get(ticker, "state", "")
        country = stocks_services.get(ticker, "country", "")

        headquarters_parts = [p for p in [city, state, country] if p]
        headquarters = (
            ", ".join(headquarters_parts) if headquarters_parts else "N/A"
        )

        # Build response
        about = {
            "name": stocks_services.get(ticker, "longName")
            or stocks_services.get(ticker, "shortName")
            or "N/A",
            "summary": stocks_services.truncate_summary(
                stocks_services.get(
                    ticker, "longBusinessSummary", "No description available"
                )
            ),
            "ceo": ceo,
            "headquarters": headquarters,
            "employees": stocks_services.get(ticker, "fullTimeEmployees", 0),
            "website": stocks_services.get(ticker, "website", "N/A"),
        }

        logger.info(f"Successfully fetched about info for {ticker}")
        return {"data": about}

    except Exception as e:
        logger.error(f"Failed to fetch about info for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch company information"
        )


@router.get("/stats/{ticker}")
def get_stock_stats(ticker: str):
    """
    Fetches statistical data for a given ticker
    Args:
        Ticker: a stock ticker symbol (e.g. AAPL, NVDA)
    Returns:
        A dictionary of dictionaries
    """
    try:
        stats = {
            "valuation": {
                "market_cap": stocks_services.get(ticker, "marketCap"),
                "pe_ratio": stocks_services.get(ticker, "trailingPE"),
                "forward_pe": stocks_services.get(ticker, "forwardPE"),
                "price_to_sales": stocks_services.get(
                    ticker, "priceToSalesTrailing12Months"
                ),
                "price_to_book": stocks_services.get(ticker, "priceToBook"),
            },
            "performance": {
                "change_today_percent": stocks_services.get(
                    ticker, "regularMarketChangePercent"
                ),
                "fifty_two_week_high": stocks_services.get(
                    ticker, "fiftyTwoWeekHigh"
                ),
                "fifty_two_week_low": stocks_services.get(
                    ticker, "fiftyTwoWeekLow"
                ),
                "ytd_return": stocks_services.get(ticker, "ytdReturn"),
                "one_year_return": stocks_services.get(ticker, "52WeekChange"),
            },
            "financial_health": {
                "debt_to_equity": stocks_services.get(ticker, "debtToEquity"),
                "current_ratio": stocks_services.get(ticker, "currentRatio"),
                "profit_margin": stocks_services.get(ticker, "profitMargins"),
                "roe": stocks_services.get(ticker, "returnOnEquity"),
            },
            "trading_activity": {
                "volume_today": stocks_services.get(ticker, "volume"),
                "avg_volume": stocks_services.get(ticker, "averageVolume"),
                "beta": stocks_services.get(ticker, "beta"),
                "shares_outstanding": stocks_services.get(
                    ticker, "sharesOutstanding"
                ),
                "float": stocks_services.get(ticker, "floatShares"),
            },
        }

        # Apply formatting
        stats["valuation"]["market_cap"] = stocks_services.format_large_num(
            stats["valuation"]["market_cap"]
        )

        logger.info("Fetched statistical data")
        return {"data": stats}

    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching stats: {str(e)}"
        )


@router.get("/summary/{ticker}")
def get_summary(ticker: str):
    """
    Fetches summary for a given ticker
    Args:
        Ticker: A stock ticker symbol (e.g: AAPL, NVDA)
    Returns:
        a dictionary of key value pairs.
    """
    try:
        earnings_date = stocks_services.get(ticker, "earningsTimestamp")
        utc_earnings_date = datetime.fromtimestamp(earnings_date, tz=pytz.UTC)
        earnings_date_iso = utc_earnings_date.isoformat()

        summary = {
            "current_price": stocks_services.get(ticker, "currentPrice"),
            "market_status": (
                "Open"
                if stocks_services.get(ticker, "marketState") == "REGULAR"
                else "Closed"
            ),
            "earnings_date": earnings_date_iso,
            "eps": round(stocks_services.get(ticker, "trailingEps", "N/A"), 2),
            "market_cap": stocks_services.get(ticker, "marketCap", "N/A"),
            "pe": round(stocks_services.get(ticker, "trailingPE", "N/A"), 2),
            "volume": stocks_services.get(
                ticker,
                "volume",
                stocks_services.get(ticker, "regularMarketVolume", "N/A"),
            ),
            "bid_ask": f"{stocks_services.get(ticker, 'bid', 0)} / {stocks_services.get(ticker, 'ask', 0)}",
            "day_high": stocks_services.get(
                "dayHigh",
                stocks_services.get(ticker, "regularMarketDayHigh", "N/A"),
            ),
            "day_low": stocks_services.get(
                ticker,
                "dayLow",
                stocks_services.get(ticker, "regularMarketDayLow", "N/A"),
            ),
            "year_high": stocks_services.get(
                ticker, "fiftyTwoWeekHigh", "N/A"
            ),
            "year_low": stocks_services.get(ticker, "fiftyTwoWeekLow", "N/A"),
        }

        logger.info("Fetched summary data.")
        return {"data": summary}

    except Exception as e:
        logger.error(f"Error fetching summary. {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching summary: {str(e)}"
        )


# Cache for all tickers
CACHE_ALLTICKERS = {
    "list": None,
    "timestamp": None,
}
CACHE_ALLTICKERS_DURATION = timedelta(days=1)


# @router.get("/all/tickers")
# async def get_all_tickers():
#     """
#     Get all stock tickers from NYSE and NASDAQ exchanges.

#     Returns cached data if less than 1 day old.
#     Falls back to stale cache if API fails.
#     """

#     async with stocks_services.cache_lock:
#         now = datetime.now()

#         # Return cached if fresh
#         if (
#             CACHE_ALLTICKERS["list"] is not None
#             and (now - CACHE_ALLTICKERS["timestamp"])
#             < CACHE_ALLTICKERS_DURATION
#         ):
#             logger.info("Returning cached ticker data")
#             return {"data": CACHE_ALLTICKERS["list"]}
#         try:
#             logger.info("Fetching fresh ticker data from NYSE and NASDAQ")
#             nyse, nasdaq = await asyncio.gather(
#                 stocks_services.fetch_tickers("nyse"),
#                 stocks_services.fetch_tickers("nasdaq"),
#             )
#             tickers = nyse + nasdaq

#             CACHE_ALLTICKERS["list"] = tickers
#             CACHE_ALLTICKERS["timestamp"] = now

#             logger.info(f"Cached {len(tickers)} tickers")
#             return {"data": CACHE_ALLTICKERS["list"]}

#         except HTTPException:
#             # If API fails, return stale cache if available
#             if CACHE_ALLTICKERS["list"] is not None:
#                 logger.warning("API failed, returning stale cached data")
#                 return {"data": CACHE_ALLTICKERS["list"]}
#             raise

#         except Exception as e:
#             logger.error(f"Unexpected error fetching tickers: {str(e)}")
#             # Return stale cache if available
#             if CACHE_ALLTICKERS["list"] is not None:
#                 logger.warning("Unexpected error, returning stale cached data")
#                 return {"data": CACHE_ALLTICKERS["list"]}

#             raise HTTPException(
#                 status_code=500, detail="Failed to fetch ticker data"
#             )


@router.get("/all/tickers")
async def get_all_tickers():
    """
    Get all stock tickers from NYSE and NASDAQ exchanges.

    Returns cached data if less than 1 day old.
    Falls back to stale cache if API fails.
    """
    stocks_list = [
        {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
        {
            "ticker": "MSFT",
            "name": "Microsoft Corporation",
            "exchange": "NASDAQ",
        },
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
        {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
        {"ticker": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ"},
    ]

    return {"data": stocks_list}
