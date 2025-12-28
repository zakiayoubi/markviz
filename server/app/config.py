import os
from dotenv import load_dotenv

load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
base_URL = "https://financialmodelingprep.com/"

income_statement_endpoint = "stable/income-statement"
company_profile_endpoint = "stable/profile"
shares_float_endpoint = "stable/shares-float"


API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")
NINJAS_BASE_URL = "https://api.api-ninjas.com/v1"
SP500_ENDPOINT = "/sp500"

MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")
MASSIVE_BASE_URL = "https://api.massive.com/v3"
MASSIVE_All_Tickers_ENDPOINT = "/reference/tickers"
