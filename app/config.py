import os
from dotenv import load_dotenv

load_dotenv()

FMP_API_KEY = os.getenv("FMP_API_KEY")
base_URL = "https://financialmodelingprep.com/"

income_statement_endpoint = "stable/income-statement"
company_profile_endpoint = "stable/profile"
shares_float_endpoint = "stable/shares-float"
