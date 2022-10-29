from backend.api.sales import get_sales
import frontend.config as Settings
from datetime import date

def refreshTotalSales():
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    status, data = get_sales(from_=today, to=today)
    if status:
        Settings.TOTAL_SALES = data["data"]