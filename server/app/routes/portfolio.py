from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import logging
import yfinance as yf

from ..schemas import HoldingCreate
from ..database import get_db
from ..models import User, Holding
from .auth import get_current_user

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
logger = logging.getLogger(__name__)


@router.post("/holdings", status_code=status.HTTP_201_CREATED)
def add_holding(  # Changed to sync
    holding_in: HoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new stock holding to the user's portfolio."""
    try:
        logger.info("Printing the input user: ", holding_in)
        new_holding = Holding(
            user_id=current_user.id,
            ticker=holding_in.ticker.upper(),
            shares=holding_in.shares,
            buy_price=holding_in.buy_price,
        )

        db.add(new_holding)
        db.commit()
        db.refresh(new_holding)

        logger.info(
            f"User {current_user.id} added holding: {holding_in.ticker}"
        )
        return {
            "message": f"Successfully added {holding_in.ticker.upper()} to your portfolio",
            "holding_id": new_holding.id,
            "ticker": holding_in.ticker.upper(),
        }

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add holding")

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred"
        )


def fetch_stock_hist(
    ticker: str, start_date: datetime, end_date: datetime, timeRange: str
):
    """
    Fetch historical stock data for a given period.

    Args:
        ticker: Stock symbol
        start_date: Start of period
        end_date: End of period
        timeRange: Time range string (1D, 1W, 1M, 3M, 1Y, ALL)

    Returns:
        DataFrame with historical prices
    """
    intervals = {
        "1D": "5m",
        "1W": "30m",
        "1M": "1d",
        "3M": "1d",
        "1Y": "1d",
        "ALL": "1d",
    }

    interval = intervals.get(timeRange, "1d")

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date, interval=interval)
        return hist
    except Exception as e:
        logger.warning(f"Failed to fetch history for {ticker}: {str(e)}")
        return None


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

    Returns:
        Tuple of (baseline_price, baseline_date)
    """
    try:
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

    except Exception as e:
        logger.warning(f"Error determining baseline: {str(e)}")
        return purchase_price, purchase_date


def calculate_holding_data(
    holding: Holding, timeRange: str, now: datetime, interval: str
) -> dict:
    """
    Calculate historical data for a single holding.

    Returns:
        Dict with ticker, shares, baseline info, prices, and timestamps
        or None if data unavailable
    """
    try:
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

        if hist_filtered is None or hist_filtered.empty:
            logger.warning(f"No historical data for {ticker}")
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

    except Exception as e:
        logger.error(
            f"Error calculating holding data for {holding.ticker}: {str(e)}"
        )
        return None


def calculate_portfolio_returns(
    all_holdings_data: list[dict], interval: str
) -> list[dict]:
    """
    Calculate weighted average portfolio returns from individual holdings data.

    Returns:
        List of dicts with date and value (return percentage)
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
                    "%H:%M" if interval == "5m" else "%Y-%m-%d"
                ),
                "value": portfolio_return,
            }
        )

    return portfolio_data


@router.get("/graph")
def get_portfolio(  # Changed to sync
    timeRange: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get portfolio performance graph data for a specific time range."""

    # Validate timeRange
    valid_ranges = ["1D", "1W", "1M", "3M", "1Y", "ALL"]
    if timeRange not in valid_ranges:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timeRange. Must be one of: {valid_ranges}",
        )

    try:
        # Get all holdings
        holdings = (
            db.query(Holding).filter(Holding.user_id == current_user.id).all()
        )

        if not holdings:
            return {"data": [], "holdings_count": 0}

        # Set timezone-aware now
        now = datetime.now(holdings[0].created_at.tzinfo)

        # Define interval
        intervals = {
            "1D": "5m",
            "1W": "30m",
            "1M": "1d",
            "3M": "1d",
            "1Y": "1d",
            "ALL": "1d",
        }
        interval = intervals[timeRange]

        # Calculate data for each holding
        all_holdings_data = []
        for holding in holdings:
            holding_data = calculate_holding_data(
                holding, timeRange, now, interval
            )
            if holding_data:
                all_holdings_data.append(holding_data)

        if not all_holdings_data:
            logger.warning(f"No data available for user {current_user.id}")
            return {"data": [], "holdings_count": 0}

        # Calculate weighted portfolio returns
        portfolio_data = calculate_portfolio_returns(
            all_holdings_data, interval
        )

        logger.info(
            f"User {current_user.id} fetched portfolio graph ({timeRange})"
        )
        return {
            "data": portfolio_data,
            "holdings_count": len(all_holdings_data),
        }

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        logger.error(f"Error fetching portfolio graph: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch portfolio data"
        )


@router.get("/table")
def get_portfolio_table(  # Changed to sync
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current portfolio holdings with prices and returns."""

    try:
        holdings = (
            db.query(Holding).filter(Holding.user_id == current_user.id).all()
        )

        if not holdings:
            return {"data": []}

        data = []
        for h in holdings:
            try:
                stock = yf.Ticker(h.ticker)
                info = stock.info

                name = info.get("longName", "N/A")
                current_price = info.get("currentPrice", 0)
                previous_close = info.get("previousClose", 0)

                # Calculate metrics with safety checks
                shares = float(h.shares)
                buy_price = float(h.buy_price)

                total_value = (
                    round(current_price * shares, 2) if current_price else 0
                )

                today_change = (
                    round(((current_price / previous_close) - 1) * 100, 2)
                    if current_price and previous_close
                    else 0
                )

                all_time_return = (
                    round(((current_price / buy_price) - 1) * 100, 2)
                    if current_price and buy_price
                    else 0
                )

                all_time_return_amount = (
                    round((current_price - buy_price) * shares, 2)
                    if current_price and buy_price
                    else 0
                )

                data.append(
                    {
                        "ticker": h.ticker,
                        "name": name,
                        "shares": shares,
                        "currentPrice": current_price,
                        "totalValue": total_value,
                        "todayChangePercent": today_change,
                        "allTimeReturn": all_time_return,
                        "allTimeReturnAmount": all_time_return_amount,
                    }
                )

            except Exception as e:
                logger.warning(
                    f"Failed to fetch data for {h.ticker}: {str(e)}"
                )
                # Skip this holding and continue
                continue

        logger.info(f"User {current_user.id} fetched portfolio table")
        return {"data": data}

    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error")

    except Exception as e:
        logger.error(f"Error fetching portfolio table: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch portfolio data"
        )
