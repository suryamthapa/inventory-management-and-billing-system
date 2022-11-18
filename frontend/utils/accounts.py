
from tkinter import *
from tkinter import messagebox
import nepali_datetime
import datetime
import pytz
from pytz import timezone
import logging
# frontend imports
import frontend.config as Settings
# backend imports
from backend.models import AccountType
from backend.api.accounts import get_accounts
from backend.api.customers import get_customers, get_customer


log = logging.getLogger("frontend")



def get_formatted_account(customer_id, asc = True, sort_column: str = "created_at", page=1, limit=None, from_="",to=""):
    status, accounts_data = get_accounts({"customer_id":customer_id}, page=page, limit=limit, sort_column=sort_column, asc=asc)
    if not status:
        messagebox.showerror("Inabi System", accounts_data["message"])
        return False

    if from_ and to:
        from_month, from_day, from_year = from_.split("/")
        from_date = nepali_datetime.date(year=int(from_year), month=int(from_month), day=int(from_day))
        to_month, to_day, to_year = to.split("/")
        to_date = nepali_datetime.date(year=int(to_year), month=int(to_month), day=int(to_day))

    account_balance = 0
    payload = []
    start_from_found = False
    end_to_found = False

    for index, record in enumerate(accounts_data["data"]):
        nepali_timezone = timezone("Asia/Kathmandu")
        utc = pytz.utc
        utc_dt = record["date"].replace(tzinfo=utc)
        ne_dt = utc_dt.astimezone(nepali_timezone)
        temp_utc_date = datetime.date(year=ne_dt.year, month=ne_dt.month, day=ne_dt.day)
        final_nepali_date = nepali_datetime.date.from_datetime_date(temp_utc_date)
        record["date"] = final_nepali_date.strftime("%d/%m/%Y")
        
        if from_ and to:
            exact_from_day = final_nepali_date == from_date
            just_greater_than_from_day = final_nepali_date > from_date
            if not start_from_found and (exact_from_day or just_greater_than_from_day):
                start_from_found = True
                if payload: # if previous records exist, then need opening balance
                    last_record = payload[-1]
                    opening_record = {
                        "id":"",
                        "date":"",
                        "bill_id":"",
                        "type":"",
                        "description":"Opening Balance",
                        "amount":abs(account_balance),
                        "account_balance": last_record["account_balance"]
                    }
                    type = last_record["account_balance"].split(" ")[-1]
                    if type=="Dr":
                        opening_record["type"]="debit"
                    else:
                        opening_record["type"]="credit"

                    payload = []
                    payload.append(opening_record)
                # if previous records does not exist, no need to find opening balance
                 
            exact_to_day = final_nepali_date == to_day
            just_greater_than_to_day = final_nepali_date > to_date
            if not end_to_found and (exact_to_day or just_greater_than_to_day):
                end_to_found = True
                if just_greater_than_to_day:
                    break

        if record["type"]=="debit":
            account_balance = account_balance - record["amount"]
        else:
            account_balance = account_balance + record["amount"]
        if account_balance!=abs(account_balance):
            record["account_balance"] = f"{'Rs. {:,.2f}'.format(abs(account_balance))} Dr"
        else:
            record["account_balance"] = f"{'Rs. {:,.2f}'.format(abs(account_balance))} Cr"
        
        payload.append(record)

    if (from_ and to) and not start_from_found:
        return []
    return payload


