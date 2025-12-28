from unittest.mock import patch, Mock
from app.services.fmp_api import (
    get_income_statement_info,
    get_company_profile,
    get_num_shares,
)


@patch("app.services.fmp_api.httpx.get")
def test_get_income_statement_info_success(mock_get):
    # Arrange
    mock_response = Mock()
    mock_response.status_code = 200
    sample_res = {"revenue": 394_328_000_000, "netIncome": 99_803_000_000}
    mock_response.json.return_value = [sample_res]
    mock_get.return_value = mock_response

    # Act
    result = get_income_statement_info("AAPL")
    print(result)

    # Assert
    assert result == {"revenue": 394328000000, "net_income": 99803000000}
    mock_get.assert_called_once()


@patch("app.services.fmp_api.httpx.get")
def test_get_company_profile_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [
        {
            "companyName": "Apple Inc.",
            "price": 175.5,
            "marketCap": 2800000000000,
            "exchange": "NASDAQ",
        }
    ]
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = get_company_profile("AAPL")

    assert result["company_name"] == "Apple Inc."
    assert result["current_price"] == 175.5


@patch("app.services.fmp_api.httpx.get")
def test_get_num_shares_success(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = [{"outstandingShares": 15500000000}]
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = get_num_shares("AAPL")

    assert result["shares_outstanding"] == 15500000000
