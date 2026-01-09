import os
from dotenv import load_dotenv

load_dotenv()

API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")
NINJAS_BASE_URL = "https://api.api-ninjas.com/v1"
SP500_ENDPOINT = "/sp500"

MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")
MASSIVE_BASE_URL = "https://api.massive.com/v3"
MASSIVE_All_Tickers_ENDPOINT = "/reference/tickers"
