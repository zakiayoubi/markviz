import asyncio
from fastapi import HTTPException
import httpx
import logging
from datetime import datetime, timedelta
import yfinance as yf
from ..config import (
    API_NINJAS_KEY,
    NINJAS_BASE_URL,
    SP500_ENDPOINT,
    MASSIVE_API_KEY,
    MASSIVE_BASE_URL,
    MASSIVE_All_Tickers_ENDPOINT,
)

# Set up logging
logger = logging.getLogger(__name__)

cache_lock = asyncio.Lock()

# Global cache
CACHE = {
    "static_list": None,
    "static_timestamp": None,
    "price_data": None,
    "price_timestamp": None,
}

STATIC_CACHE_DURATION = timedelta(days=1)
PRICE_CACHE_DURATION = timedelta(minutes=60)
REQUEST_TIMEOUT = 30.0


async def fetch_sp500_constituents():
    """
    Fetch and cache S&P 500 constituent list from API Ninjas.

    Cache duration: 1 day. Returns stale data if API call fails.

    Returns:
        List of dicts with ticker, name, sector

    Raises:
        HTTPException: If API fails and no cache is available
    """
    now = datetime.now()

    async with cache_lock:
        if (
            CACHE["static_list"] is not None
            and CACHE["static_timestamp"] is not None
            and (now - CACHE["static_timestamp"]) <= STATIC_CACHE_DURATION
        ):
            logger.info("Returning cached S&P500 data")
            return CACHE["static_list"]

        url = NINJAS_BASE_URL + SP500_ENDPOINT
        headers = {"X-Api-Key": API_NINJAS_KEY}

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                logger.info("Fetching S&P500 data from API Ninjas")
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Filter out problematic tickers
                excluded_tickers = {
                    "WBA",
                    "PARA",
                    "IPG",
                    "BRK.B",
                    "BF.B",
                    "k",
                    "GOOG",
                    "FOXA",
                }

                filtered_stocks = [
                    {
                        "ticker": stock["ticker"],
                        "name": stock["company_name"],
                        "sector": stock["sector"],
                    }
                    for stock in data
                    if stock["ticker"] not in excluded_tickers
                ]

                CACHE["static_list"] = filtered_stocks
                CACHE["static_timestamp"] = now
                logger.info(f"Cached {len(filtered_stocks)} S&P500 stocks")

                return filtered_stocks

        except httpx.TimeoutException:
            logger.warning("API Ninjas request timed out")
            if CACHE["static_list"] is not None:
                logger.info("Returning stale cached data")
                return CACHE["static_list"]
            raise HTTPException(
                status_code=504,
                detail="API timeout and no cached data available",
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"API Ninjas HTTP Error: {e.response.status_code}")
            if CACHE["static_list"] is not None:
                logger.info("Returning stale cached data")
                return CACHE["static_list"]
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"API Error: {e.response.status_code}",
            )

        except (httpx.RequestError, ValueError) as e:
            logger.error(f"API Ninjas error: {str(e)}")
            if CACHE["static_list"] is not None:
                logger.info("Returning stale cached data")
                return CACHE["static_list"]
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch S&P 500 data and no cache available",
            )


async def fetch_single_ticker_async(ticker):
    """
    Fetch current price and market data for a single ticker using yfinance.

    Args:
        ticker: Stock ticker symbol

    Returns:
        dict with market_cap, current_price, change_percent or None if failed
    """

    def fetch_sync():
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            current_price = info.get("currentPrice", 0)
            previous_close = info.get("previousClose", 0)

            change_percent = (
                round(
                    (current_price - previous_close) / previous_close * 100, 2
                )
                if previous_close
                else 0
            )

            market_cap = info.get("marketCap", 0)

            return {
                "market_cap": market_cap,
                "current_price": (
                    round(current_price, 2) if current_price else 0
                ),
                "change_percent": change_percent,
            }

        except Exception as e:
            logger.warning(f"Failed to fetch {ticker}: {e}")
            return None

    # Run blocking yfinance call in thread pool
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_sync)
    # None: use's the fastapi built thread pool


async def fetch_price_data():
    """
    Fetch and cache price data for all S&P 500 stocks.

    Cache duration: 20 minutes. Returns stale cache if fetch fails.

    Raises:
        HTTPException: If constituents not loaded or fetch fails with no cache
    """
    now = datetime.now()

    async with cache_lock:
        # Check if cache is still valid
        if (
            CACHE["price_data"] is not None
            and CACHE["price_timestamp"] is not None
            and (now - CACHE["price_timestamp"]) <= PRICE_CACHE_DURATION
        ):
            logger.info("Returning cached price data")
            return CACHE["price_data"]

        # Check if we have static list
        if CACHE["static_list"] is None:
            raise HTTPException(
                status_code=500, detail="S&P 500 constituents not loaded"
            )

        tickers = [stock["ticker"] for stock in CACHE["static_list"]]

        try:
            logger.info(f"Fetching price data for {len(tickers)} tickers")
            price_data = {}

            # Create all fetch tasks
            # tasks = [fetch_single_ticker_async(ticker) for ticker in tickers]
            tasks = [
                fetch_single_ticker_async(ticker) for ticker in tickers[:5]
            ]

            # Run all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for ticker, result in zip(tickers, results):
                if result and not isinstance(result, Exception):
                    price_data[ticker] = (
                        result  # Store as dict with ticker as key
                    )

            CACHE["price_data"] = price_data
            CACHE["price_timestamp"] = now
            logger.info(
                f"Cached price data for {len(price_data)}/{len(tickers)} tickers"
            )
            return price_data

        except Exception as e:
            logger.error(f"Error fetching price data: {str(e)}")

            # Return stale cache if available
            if CACHE["price_data"] is not None:
                logger.info("Using stale price cache")
                return CACHE["price_data"]

            raise HTTPException(
                status_code=503,
                detail="Unable to fetch price data and no cache available",
            )


async def fetch_tickers(exchange: str):
    """
    Fetch all tickers for a given exchange.
    Args:
        exchange: Exchange name (nasdaq or nyse)
    Returns:
        List of dicts with ticker, name, exchange
    """
    exchange_codes = {"nasdaq": "XNAS", "nyse": "XNYS"}

    url = MASSIVE_BASE_URL + MASSIVE_All_Tickers_ENDPOINT
    params = {
        "market": "stocks",
        "exchange": exchange_codes[exchange],
        "limit": 1000,
        "apiKey": MASSIVE_API_KEY,
    }

    tickers = []
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            # First request with params
            response = await client.get(url, params=params)
            logger.info(f"Fetching all the tickers on {exchange}")
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
            logger.info(f"Next URL: {next_url}")

            # Subsequent requests
            while next_url:
                # Api rate limit delay
                await asyncio.sleep(30)

                # Append API key to next_url
                url_with_key = f"{next_url}&apiKey={MASSIVE_API_KEY}"

                response = await client.get(url_with_key)
                # No params on pagination
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
                logger.info(f"Next URL: {next_url}")

            logger.info(f"Fetched {len(tickers)} tickers from {exchange}")
            return tickers

    except httpx.TimeoutException:
        logger.error(f"Massive API request timeout for {exchange}.")
        raise HTTPException(
            status_code=504, detail=f"API timeout fetching {exchange} tickers"
        )
    except httpx.HTTPStatusError as e:
        logger.error(
            f"Massive API HTTP Error for {exchange}. {str(e.response.status_code)}"
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"API error fetching {exchange} tickers",
        )
    except (httpx.RequestError, ValueError) as e:
        logger.error(f"Error fetching {exchange} tickers: {str(e)}")
        raise HTTPException(
            status_code=503, detail=f"Unable to fetch {exchange} tickers"
        )


def truncate_summary(text, max_chars=700):
    """Truncate text to max_chars, ending at a sentence if possible."""
    if not text or len(text) <= max_chars:
        return text

    truncated = text[:max_chars]

    # Try to end at a sentence (period)
    last_period = truncated.rfind(".")
    if last_period > max_chars * 0.7:  # At least 70% of target length
        return truncated[: last_period + 1]

    # Otherwise just truncate and add ellipsis
    return truncated.rstrip() + "..."


# Helper to safely get values from yf
def get(ticker, key, default="N/A"):
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        if not info:
            logger.error("HTTP error occurred")
            raise HTTPException(
                status_code=404, detail=f"Ticker '{ticker}' not found"
            )
        val = info.get(key)
        if val is None or val == "":
            return default
        return val

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"An unexpected error occured: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Unexpected error occurred"
        )


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
