from unittest.mock import Mock, patch
from app.services.fmp_api import (
    get_income_statement_info, 
    get_company_profile, 
    get_num_shares
    )

@patch("app.services.fmp_api.httpx.get")
def test_get_income_statement(mock_get):
    mock_resposne = Mock()
    mock_resposne.json.return_value = [{"revenue": 100, "netIncome": 20 }]
    mock_get.return_value = mock_resposne

    result = get_income_statement_info("TSLA")
    print(result)

    mock_get.assert_called_once()

test_get_income_statement()

@patch("app.services.fmp_api.httpx.get")
def test_get_company_profile(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{
        "companyName": "Apple Inc.",
        "price": 5,
        "marketCap": 500,
        "exchange": "NYSE",
    }]
    mock_get.return_value = mock_response

    result = get_company_profile("AAPL")
    print(result)

    mock_get.assert_called_once()

test_get_company_profile()

@patch("app.services.fmp_api.httpx.get")
def test_get_num_shares(mock_get):
    mock_resposne = Mock()
    mock_resposne.json.return_value = [{"outstandingShares": 100}]
    mock_get.return_value = mock_resposne

    result = get_num_shares("AAPL")
    print(result)

    mock_get.assert_called_once()

test_get_num_shares()