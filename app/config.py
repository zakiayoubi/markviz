import os
from dotenv import load_dotenv

load_dotenv()
FMP_API_key = os.getenv("FMP_API_key")
base_URL = "https://financialmodelingprep.com/"

income_statement_endpoint = "stable/income-statement"
company_profile_endpoint = "stable/profile"
shares_float_endpoint = "stable/shares-float"
