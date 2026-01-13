from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def refresh_stock_data():
    """
    Background task to refresh s&p 500 data at 5 am daily
    """
    try:
        logger.info(
            "Starting scheduled S&P 500 and NYSE and Nasdaq ticker data refresh"
        )
        from .services.stocks_services import (
            fetch_sp500_constituents,
            fetch_tickers,
        )

        await fetch_sp500_constituents()
        await fetch_tickers()
        logger.info(
            "S&P 500 and NYSE and Nasdaq ticker data refreshed successfully"
        )

    except Exception as e:
        logger.error(
            f"Failed to refresh S&P 500 and NYSE and Nasdaq ticker data: {str(e)}"
        )


def start_scheduler():
    """
    Start the scheduler
    """
    scheduler.add_job(
        refresh_stock_data,
        trigger=CronTrigger(hour=5, minute=0),  # 5 am daily
        id="refresh_stock",
        replace_exisiting=True,
    )
    scheduler.start()
    logger.info("Scheduler started - refresh at 5:00 AM daily")


def shutdown_scheduler():
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
