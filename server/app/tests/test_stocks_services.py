from unittest.mock import AsyncMock
import pytest

# AsyncMock is a fake class. You can set its properties and methods to return
# specific values

from ..services.stocks_services import fetch_sp500_constituents


@pytest.mark.asyncio
async def test_fetch_sp500_constituents_success(mocker):
    """Test successful fetch from API Ninjas"""

    # Step 1. Create a temporary/fake Cache
    temp_cache = {
        "static_list": None,
        "static_timestamp": None,
        "price_data": None,
        "price_timestamp": None,
    }

    # Step 2. Create a fake api response
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "sector": "Technology",
        },
        {
            "ticker": "MSFT",
            "company_name": "Microsoft",
            "sector": "Technology",
        },
        {
            "ticker": "GOOG",
            "company_name": "Alphabet",
            "sector": "Technology",
        },
    ]

    # Step 3. Create a fake HTTP client
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    # Step 4. Replace the real client with our fake client
    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    # Step 5. Replace the actual cache with our fake cache (FIXED!)
    mocker.patch(
        "app.services.stocks_services.CACHE", temp_cache
    )  # ← No return_value, just pass the dict directly

    # Step 6. Call the function
    result = await fetch_sp500_constituents()

    # Check that it worked correctly
    assert len(result) == 2
    assert result[0]["ticker"] == "AAPL"
    assert result[0]["name"] == "Apple Inc."
    assert result[0]["sector"] == "Technology"

    # Check GOOG was filtered out
    tickers = [stock["ticker"] for stock in result]
    assert "GOOG" not in tickers
    assert "AAPL" in tickers
    assert "MSFT" in tickers


# Write more tests below ...
