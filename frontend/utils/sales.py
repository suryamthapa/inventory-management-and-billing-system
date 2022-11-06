from backend.api.sales import get_sales
import frontend.config as Settings
from datetime import date


def formatTotalSales():
    formatted_sales = {}
    for record in Settings.TOTAL_SALES:
        if not formatted_sales.get(record.get("product_name")):
            formatted_sales[record.get("product_name")] = {"quantity": record.get("quantity"),
                                                        "unit": record.get("unit")}
        else:
            formatted_sales[record.get("product_name")]["quantity"] += record.get("quantity")

    Settings.TOTAL_SALES = formatted_sales


def refreshTotalSales():
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    status, data = get_sales(from_=today, to=today, asc=False, limit=None)
    if status:
        Settings.TOTAL_SALES = data["data"]
        formatTotalSales()