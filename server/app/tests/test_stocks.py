import pytest


@pytest.mark.asyncio
async def test_get_sp500_success(client, mocker):
    """
    Test that get_sp500() successfully returns a list of dicts
    """

    mock_constituents = [
        {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
        {"ticker": "MSFT", "name": "Microsoft", "sector": "Technology"},
    ]
    mocker.patch(
        "app.services.stocks_services.fetch_sp500_constituents",
        return_value=mock_constituents,
    )

    mock_price_data = {
        "AAPL": {
            "market_cap": 3000000000000,
            "current_price": 180.50,
            "change_percent": 2.5,
        },
        "MSFT": {
            "market_cap": 2800000000000,
            "current_price": 380.25,
            "change_percent": 1.8,
        },
    }
    mocker.patch(
        "app.services.stocks_services.fetch_price_data",
        return_value=mock_price_data,
    )

    response = client.get("/stocks/sp500")
    assert response.status_code == 200

    data = response.json()["data"]
    assert len(data) == 2

    aapl = data[0]
    assert aapl["ticker"] == "AAPL"
    assert aapl["name"] == "Apple Inc."
    assert aapl["sector"] == "Technology"
    assert aapl["market_cap"] == 3000000000000
    assert aapl["current_price"] == 180.50
    assert aapl["change_percent"] == 2.5

    msft = data[1]
    assert msft["ticker"] == "MSFT"
    assert msft["name"] == "Microsoft"
    assert msft["current_price"] == 380.25
    assert msft["market_cap"] == 2800000000000
    assert msft["current_price"] == 380.25
    assert msft["change_percent"] == 1.8


# I need to Write more tests below ...
