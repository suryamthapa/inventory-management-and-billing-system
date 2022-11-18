
from tkinter import *
from tkinter import messagebox
import datetime
import logging
# frontend imports
import frontend.config as Settings
# backend imports
from backend.models import AccountType
from backend.api.accounts import get_accounts
from backend.api.customers import get_customers


log = logging.getLogger("frontend")


def get_account_balance(data, customer_id):
    account_balance = 0
    for record in data:
        if record["customer_id"]==customer_id:
            if record["type"]=="DR":
                account_balance = account_balance - record["amount"]
            else:
                account_balance = account_balance + record["amount"]
    if account_balance!=abs(account_balance):
        account_balance = f"{'Rs. {:,.2f}'.format(abs(account_balance))} DR"
    else:
        account_balance = f"{'Rs. {:,.2f}'.format(abs(account_balance))} CR"
    return account_balance

def get_formatted_accounts(asc = True, sort_column: str = "id", page=1, limit=11):
    status, accounts_data = get_accounts({}, page=page, limit=limit, sort_column=sort_column, asc=asc)
    if not status:
        messagebox.showerror("Inabi System", accounts_data["message"])
        return False
    
    status, customers_data = get_customers(Settings.CURRENT_SEARCH_QUERY["accounts"], page=page, limit=limit, sort_column=sort_column, asc=asc)
    if not status:
        messagebox.showerror("Inabi System", customers_data["message"])
        return False
    
    payload = customers_data.copy()
    payload["data"] = []
    formatted_customer_ids = []

    for record in customers_data["data"]:
        if record["id"] not in formatted_customer_ids:
            formatted_account = {
                "customer_id":record["id"],
                "customer_name":record["full_name"] if record.get("full_name") else record["company"],
                "customer_company_pan_no":record["company_pan_no"],
                "account_balance":""
            }
            account_balance = get_account_balance(accounts_data["data"], record["id"])
            formatted_account["account_balance"] = account_balance
            payload["data"].append(formatted_account)
            formatted_customer_ids.append(record["id"])

    # print(payload)
    return payload


