from fastapi import APIRouter, status, Depends, HTTPException
from ..schemas import HoldingOut, HoldingCreate
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Holding
import yfinance as yf
from .auth import get_current_user
from decimal import Decimal
from datetime import datetime, timedelta, timezone
import pandas_market_calendars as mcal

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/holdings", status_code=status.HTTP_201_CREATED)
async def add_holding(
    holding_in: HoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate ticker exists and get current price
    print(holding_in)
    try:
        stock = yf.Ticker(holding_in.ticker.upper())
        info = stock.info
        current_price = info.get("currentPrice") or info.get(
            "regularMarketPrice"
        )

        if not current_price:
            raise HTTPException(status_code=400, detail="No price data")
    except:
        raise HTTPException(status_code=400, detail="Invalid ticker")

    # Create new holding
    new_holding = Holding(
        user_id=current_user.id,
        ticker=holding_in.ticker.upper(),
        shares=holding_in.shares,
        buy_price=holding_in.buy_price,
    )

    db.add(new_holding)
    db.commit()
    db.refresh(new_holding)

    return {"data": "The holding was successfully added.", "status": 200}


# def fetch_stock_hist(
#     ticker: str, start_date: datetime, end_date: datetime, timeRange: str
# ):
#     intervals = {
#         "1D": "30m",
#         "1W": "30m",
#         "1M": "1d",
#         "3M": "1d",
#         "1Y": "1d",
#         "ALL": "1d",
#     }
#     interval = intervals.get(timeRange)
#     stock = yf.Ticker(ticker)
#     hist = stock.history(start=start_date, end=end_date, interval=interval)
#     return hist


# @router.get("/graph")
# async def get_portfolio(
#     timeRange: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     # Get all holdings for this user
#     holdings = (
#         db.query(Holding).filter(Holding.user_id == current_user.id).all()
#     )
#     firstHolding = holdings[2]
#     purchase_price = float(firstHolding.buy_price)
#     ticker = firstHolding.ticker
#     purchase_date = firstHolding.created_at
#     now = datetime.now(purchase_date.tzinfo)

#     stock = yf.Ticker(ticker)
#     intervals = {
#         "1D": "30m",
#         "1W": "30m",
#         "1M": "1d",
#         "3M": "1d",
#         "1Y": "1d",
#         "ALL": "1d",
#     }

#     interval = intervals.get(timeRange)
#     baseline_price = None
#     baseline_date = None  # Track which date to filter from

#     if timeRange == "1D":
#         market_open_date = stock.history(
#             start=(now - timedelta(days=1)), end=now, interval=interval
#         ).index[0]
#         print("market open date: ", market_open_date)

#         if purchase_date > market_open_date:
#             baseline_price = purchase_price
#             baseline_date = purchase_date
#             print("purchase date used as baseline price.")
#         else:
#             baseline_price = float(
#                 stock.info.get("previousClose", purchase_price)
#             )
#             baseline_date = market_open_date
#             print("previous close used as baseline price.")

#     elif timeRange == "ALL":
#         baseline_price = purchase_price
#         baseline_date = purchase_date
#         print("purchase price used as baseline (ALL time).")

#     elif timeRange == "1W":
#         seven_days_prior_date = now - timedelta(days=7)
#         print("seven days prior date: ", seven_days_prior_date)

#         if purchase_date > seven_days_prior_date:
#             baseline_price = purchase_price
#             baseline_date = purchase_date
#             print("purchase date used as baseline price.")
#         else:
#             hist = stock.history(
#                 start=seven_days_prior_date, end=now, interval=interval
#             )
#             baseline_price = round(float(hist["Close"].iloc[0]), 2)
#             baseline_date = hist.index[0]
#             print("seven days prior price: ", baseline_price)

#     elif timeRange == "1M":
#         thirty_days_prior_date = now - timedelta(days=30)
#         print("thirty days prior date: ", thirty_days_prior_date)

#         if purchase_date > thirty_days_prior_date:
#             baseline_price = purchase_price
#             baseline_date = purchase_date
#             print("purchase date used as baseline price.")
#         else:
#             hist = stock.history(
#                 start=thirty_days_prior_date, end=now, interval=interval
#             )
#             baseline_price = round(float(hist["Close"].iloc[0]), 2)
#             baseline_date = hist.index[0]
#             print("thirty days prior price: ", baseline_price)

#     elif timeRange == "3M":
#         ninety_days_prior_date = now - timedelta(days=90)

#         if purchase_date > ninety_days_prior_date:
#             baseline_price = purchase_price
#             baseline_date = purchase_date
#         else:
#             hist = stock.history(
#                 start=ninety_days_prior_date, end=now, interval=interval
#             )
#             baseline_price = round(float(hist["Close"].iloc[0]), 2)
#             baseline_date = hist.index[0]

#     elif timeRange == "1Y":
#         one_year_prior_date = now - timedelta(days=365)

#         if purchase_date > one_year_prior_date:
#             baseline_price = purchase_price
#             baseline_date = purchase_date
#         else:
#             hist = stock.history(
#                 start=one_year_prior_date, end=now, interval=interval
#             )
#             baseline_price = round(float(hist["Close"].iloc[0]), 2)
#             baseline_date = hist.index[0]

#     print(f"Final baseline price: {baseline_price}")
#     print(f"Baseline date: {baseline_date}")

#     hist_filtered = fetch_stock_hist(ticker, baseline_date, now, timeRange)
#     prices = hist_filtered["Close"].round(2).tolist()
#     labels = hist_filtered.index.strftime(
#         "%Y-%m-%d %H:%M" if interval in ["5m", "30m"] else "%Y-%m-%d"
#     ).tolist()

#     # Calculate percent change
#     percent_change = [
#         round((p - baseline_price) / baseline_price * 100, 2) for p in prices
#     ]

#     print("prices: ", prices)
#     print("daily return: ", percent_change)
#     print("lables: ", labels)

#     # Build response
#     data = [
#         {"date": labels[i], "value": percent_change[i]}
#         for i in range(len(labels))
#     ]

#     return {"data": data}


def fetch_stock_hist(
    ticker: str, start_date: datetime, end_date: datetime, timeRange: str
):
    """
    takes a ticker, start of the period and end of a period and a time range
    and returns a dataframe for the period.
    """
    intervals = {
        "1D": "30m",
        "1W": "30m",
        "1M": "1d",
        "3M": "1d",
        "1Y": "1d",
        "ALL": "1d",
    }
    interval = intervals.get(timeRange)
    stock = yf.Ticker(ticker)
    hist = stock.history(start=start_date, end=end_date, interval=interval)
    return hist


def determine_baseline(
    timeRange: str,
    purchase_date: datetime,
    now: datetime,
    stock: yf.Ticker,
    purchase_price: float,
    interval: str,
) -> tuple[float, datetime]:
    """
    Determine the baseline price and date based on timeRange.
    Returns: (baseline_price, baseline_date)
    """
    if timeRange == "1D":
        hist = stock.history(
            start=(now - timedelta(days=1)), end=now, interval=interval
        )
        if hist.empty:
            return purchase_price, purchase_date

        market_open_date = hist.index[0]

        if purchase_date > market_open_date:
            return purchase_price, purchase_date
        else:
            previous_close = float(
                stock.info.get("previousClose", purchase_price)
            )
            return previous_close, market_open_date

    elif timeRange == "ALL":
        return purchase_price, purchase_date

    else:
        # Handle 1W, 1M, 3M, 1Y
        period_days = {"1W": 7, "1M": 30, "3M": 90, "1Y": 365}

        days = period_days.get(timeRange, 7)
        period_prior_date = now - timedelta(days=days)

        if purchase_date > period_prior_date:
            return purchase_price, purchase_date
        else:
            hist = stock.history(
                start=period_prior_date, end=now, interval=interval
            )
            if hist.empty:
                return purchase_price, purchase_date

            baseline_price = round(float(hist["Close"].iloc[0]), 2)
            baseline_date = hist.index[0]
            return baseline_price, baseline_date


def calculate_holding_data(
    holding: Holding, timeRange: str, now: datetime, interval: str
) -> dict:
    """
    Calculate historical data for a single holding.
    Returns dict with ticker, shares, baseline info, prices, and timestamps.
    """
    ticker = holding.ticker
    purchase_price = float(holding.buy_price)
    shares = float(holding.shares)
    purchase_date = holding.created_at

    stock = yf.Ticker(ticker)

    # Determine baseline
    baseline_price, baseline_date = determine_baseline(
        timeRange, purchase_date, now, stock, purchase_price, interval
    )

    # Fetch filtered historical data
    hist_filtered = fetch_stock_hist(ticker, baseline_date, now, timeRange)

    if hist_filtered.empty:
        return None

    prices = hist_filtered["Close"].round(2).tolist()
    position_values = [p * shares for p in prices]

    return {
        "ticker": ticker,
        "shares": shares,
        "baseline_price": baseline_price,
        "baseline_value": baseline_price * shares,
        "position_values": position_values,
        "timestamps": hist_filtered.index.tolist(),
    }


def calculate_portfolio_returns(
    all_holdings_data: list[dict], interval: str
) -> list[dict]:
    """
    Calculate weighted average portfolio returns from individual holdings data.
    Returns list of {date, value} dicts.
    """
    if not all_holdings_data:
        return []

    # Use the timestamps from the first holding as reference
    reference_timestamps = all_holdings_data[0]["timestamps"]

    portfolio_data = []

    for i, timestamp in enumerate(reference_timestamps):
        total_current_value = 0
        total_baseline_value = 0

        for holding_data in all_holdings_data:
            # Check if this holding has data for this timestamp
            if i < len(holding_data["position_values"]):
                total_current_value += holding_data["position_values"][i]
                total_baseline_value += holding_data["baseline_value"]

        # Calculate portfolio return percentage
        if total_baseline_value > 0:
            portfolio_return = round(
                (
                    (total_current_value - total_baseline_value)
                    / total_baseline_value
                )
                * 100,
                2,
            )
        else:
            portfolio_return = 0

        portfolio_data.append(
            {
                "date": timestamp.strftime(
                    "%Y-%m-%d %H:%M"
                    if interval in ["5m", "30m"]
                    else "%Y-%m-%d"
                ),
                "value": portfolio_return,
            }
        )

    return portfolio_data


@router.get("/graph")
async def get_portfolio(
    timeRange: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get portfolio performance graph data."""
    # Get all holdings
    holdings = (
        db.query(Holding).filter(Holding.user_id == current_user.id).all()
    )

    if not holdings:
        return {"error": "No holdings found"}

    # Set timezone-aware now
    now = datetime.now(holdings[0].created_at.tzinfo)

    # Define interval
    intervals = {
        "1D": "30m",
        "1W": "30m",
        "1M": "1d",
        "3M": "1d",
        "1Y": "1d",
        "ALL": "1d",
    }
    interval = intervals.get(timeRange)

    # Calculate data for each holding
    all_holdings_data = []
    print(holdings[0].created_at)
    print(holdings[1].created_at)
    for holding in holdings:
        holding_data = calculate_holding_data(
            holding, timeRange, now, interval
        )
        if holding_data:
            all_holdings_data.append(holding_data)

    if not all_holdings_data:
        return {"error": "No data available for any holdings"}

    # Calculate weighted portfolio returns
    portfolio_data = calculate_portfolio_returns(all_holdings_data, interval)

    return {"data": portfolio_data, "holdings_count": len(all_holdings_data)}


@router.get("/table")
async def get_portfolio_table(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        holdings = (
            db.query(Holding).filter(Holding.user_id == current_user.id).all()
        )
        if not holdings:
            return {"error": "No holdings found"}
        data = []
        for h in holdings:
            stock = yf.Ticker(h.ticker)
            name = stock.info.get("longName")
            current_price = stock.info.get("currentPrice")
            previous_close = stock.info.get("previousClose")

            data.append(
                {
                    "ticker": h.ticker,
                    "name": name,
                    "shares": float(h.shares),
                    "currentPrice": current_price,
                    "totalValue": round(
                        (
                            (current_price - float(h.buy_price))
                            * float(h.shares)
                        ),
                        2,
                    ),
                    "todayChangePercent": round(
                        (((current_price / previous_close) - 1) * 100), 2
                    ),
                    "allTimeReturn": round(
                        ((current_price - float(h.buy_price)) - 1) * 100, 2
                    ),
                    "allTimeReturnAmount": round(
                        (current_price - float(h.buy_price)) * float(h.shares),
                        2,
                    ),
                }
            )

        return {"data": data}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail=f"unable to fetch data: {e}"
        )
