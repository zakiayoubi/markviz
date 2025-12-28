from fastapi import APIRouter, status, Depends, HTTPException
from ..schemas import HoldingOut, HoldingCreate
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Holding
import yfinance as yf
from .auth import get_current_user
from decimal import Decimal


router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post(
    "/holdings", response_model=HoldingOut, status_code=status.HTTP_201_CREATED
)
async def add_holding(
    holding_in: HoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate ticker exists and get current price

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

    return {
        "id": new_holding.id,
        "ticker": new_holding.ticker,
        "shares": new_holding.shares,
        "buy_price": new_holding.buy_price,
        "current_price": current_price,
        "gain_loss": (current_price - new_holding.buy_price)
        * new_holding.shares,
        "gain_loss_percent": (
            (current_price - new_holding.buy_price) / new_holding.buy_price
        )
        * 100,
    }


@router.get("/")
async def get_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Get all holdings for this user
    holdings = (
        db.query(Holding).filter(Holding.user_id == current_user.id).all()
    )

    if not holdings:
        return {
            "total_value": 0,
            "total_cost": 0,
            "total_gain_loss": 0,
            "total_gain_loss_percent": 0,
            "holdings": [],
        }

    # Fetch current prices
    tickers = [h.ticker for h in holdings]
    try:
        prices = {}
        for ticker in tickers:
            info = yf.Ticker(ticker).info
            current_price = (
                info.get("currentPrice") or info.get("regularMarketPrice") or 0
            )
            prices[ticker] = Decimal(str(current_price))
    except:
        raise HTTPException(status_code=500, detail="Failed to fetch prices")

    # Calculate everything
    portfolio_holdings = []
    total_value = Decimal("0")
    total_cost = Decimal("0")

    for holding in holdings:
        current_price = prices.get(holding.ticker, Decimal("0"))
        value = Decimal(str(holding.shares)) * current_price
        cost = Decimal(str(holding.shares)) * Decimal(str(holding.buy_price))
        gain_loss = value - cost
        gain_loss_percent = (gain_loss / cost * 100) if cost > 0 else 0

        portfolio_holdings.append(
            {
                "id": holding.id,
                "ticker": holding.ticker,
                "shares": float(holding.shares),
                "buy_price": float(holding.buy_price),
                "current_price": float(current_price),
                "value": float(value),
                "cost": float(cost),
                "gain_loss": float(gain_loss),
                "gain_loss_percent": float(gain_loss_percent),
            }
        )

        total_value += value
        total_cost += cost

    total_gain_loss = total_value - total_cost
    total_gain_loss_percent = (
        (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
    )

    return {
        "total_value": float(total_value),
        "total_cost": float(total_cost),
        "total_gain_loss": float(total_gain_loss),
        "total_gain_loss_percent": float(total_gain_loss_percent),
        "holdings": portfolio_holdings,
    }
