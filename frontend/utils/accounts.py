
from tkinter import *
from tkinter import messagebox
import nepali_datetime
import datetime
import pytz
import os
from pytz import timezone
import logging
# frontend imports
import frontend.config as Settings
from frontend.utils.ledgerPdfGenerator import CustomerLedger
# backend imports
from backend.models import AccountType
from backend.api.accounts import get_accounts, add_account, update_account
from backend.api.customers import get_customers, get_customer


log = logging.getLogger("frontend")


def get_formatted_account(customer_id, asc = True, sort_column: str = "transaction_date", page=1, limit=None, from_="",to=""):
    status, accounts_data = get_accounts({"customer_id":customer_id}, page=page, limit=limit, sort_column=sort_column, asc=asc)
    if not status:
        messagebox.showerror("Inabi System", accounts_data)
        return False

    if from_ and to:
        from_day, from_month, from_year = from_.split("/")
        from_date = nepali_datetime.date(year=int(from_year), month=int(from_month), day=int(from_day))
        to_day, to_month, to_year = to.split("/")
        to_date = nepali_datetime.date(year=int(to_year), month=int(to_month), day=int(to_day))

    account_balance = 0
    payload = []
    start_from_found = False
    end_to_found = False
    for index, record in enumerate(accounts_data["data"]):
        nepali_timezone = timezone("Asia/Kathmandu")
        utc = pytz.utc
        utc_datetime = record["date"].replace(tzinfo=utc)
        ne_datetime = utc_datetime.astimezone(nepali_timezone)
        temp_utc_date = datetime.date(year=ne_datetime.year, month=ne_datetime.month, day=ne_datetime.day)
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
            record["account_balance"] = f"{'{:,.2f}'.format(abs(account_balance))} Dr"
        else:
            record["account_balance"] = f"{'{:,.2f}'.format(abs(account_balance))} Cr"
        
        payload.append(record)

    if (from_ and to) and not start_from_found:
        return []
    return payload


def saveAccount(data):
    status, message = add_account(data)
    if not status:
        messagebox.showerror("Add Customer", message)
        return False
    else:
        messagebox.showinfo("Add Customer",f"{message} \n id: {status}")
        return True


def updateAccount(id, data):
    status, message = update_account(id=id, data=data)
    if not status:
        messagebox.showerror("Update Customer", message)
        return False
    else:
        messagebox.showinfo("Update Customer",message)
        return True


def preprocess_ledger_details():
    if not Settings.CURRENT_SETTINGS.get("company_profile"):
        messagebox.showinfo("Billing System", "Please complete your profile in Company Profile tab.")
        return False
    companyProfileMustHaves = ("company_name", "pan_no", "country","province","district","municipality","ward","toll")
    for info in companyProfileMustHaves:
        if not Settings.CURRENT_SETTINGS["company_profile"].get(info):
            messagebox.showwarning("Missing profile details", f"Please completely fill the details in company profile.\nMissing: {info}")
            return False
    if not Settings.CURRENT_SETTINGS["company_profile"].get("phone_number") and not Settings.CURRENT_SETTINGS["company_profile"].get("telephone"):
        messagebox.showwarning("Missing profile details", f"Please completely fill the details in company profile.\nMissing: Phone number or telephone")
        return False
    if not Settings.CURRENT_LEDGER_ACCOUNT.get("customer"):
            messagebox.showwarning("Billing System", "Please search and load the details of customer.")
            return False
    if not Settings.CURRENT_LEDGER_ACCOUNT.get("account"):
        messagebox.showwarning("Billing System", "Given customer has no transaction records.")
        return False
    return True


def export_ledger_to_pdf():
    name = Settings.CURRENT_LEDGER_ACCOUNT["customer"]["full_name"]
    company = Settings.CURRENT_LEDGER_ACCOUNT["customer"]["company"]
    
    from_ = Settings.CURRENT_LEDGER_ACCOUNT['from'] if Settings.CURRENT_LEDGER_ACCOUNT['from'] else Settings.CURRENT_LEDGER_ACCOUNT['account'][0]["date"]
    to = Settings.CURRENT_LEDGER_ACCOUNT['to'] if Settings.CURRENT_LEDGER_ACCOUNT['to'] else Settings.CURRENT_LEDGER_ACCOUNT['account'][-1]["date"]
    from_to_part = f"FROM_{from_}_To_{to}"

    filename = f"{name if name else company}_Ledger_{from_to_part}.pdf".replace('/','_')
    try:
        CustomerLedger(f"./ledgers/{filename}",
                    company_info=Settings.CURRENT_SETTINGS.get("company_profile"), ledger_details=Settings.CURRENT_LEDGER_ACCOUNT, 
                    title=f"{name if name else company}_Ledger_{from_to_part}", author="IMAB System - Datakhoj",
                    subject=f"Ledger_A/C_{name if name else company}_{from_to_part}")
        log.info(f"Bill generated and saved as: {filename}")
        return True, filename
    except Exception as e:
        if os.path.exists(os.path.join(os.getcwd(),"bills",filename)):
            os.remove(os.path.join(os.getcwd(),"bills",filename))
        log.error(f"Error occured while generating bill -> {e}")
        return False, filename 