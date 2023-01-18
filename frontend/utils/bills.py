import os
import tempfile
import logging
import datetime
from tkinter import messagebox
import threading
# frontend imports
import frontend.config as Settings
from core.nepali_datetime import date
from frontend.utils.products import refreshProductsList
# from frontend.utils.sales import refreshTotalSales
from frontend.utils.billPdfGen import CustomerBill
import frontend.frames.billing as billingFrame
# backend imports
from sqlalchemy.orm import Session
from backend.database.deps import get_db
from backend.models import AccountType
from backend.api.bills import add_bill, get_bills, update_bill, delete_bill
from backend.api.products import update_product
from backend.api.accounts import add_account, update_account, get_accounts


log = logging.getLogger("frontend")


def refreshBillsList():
    status, data = get_bills(limit=None)
    if status:
        Settings.BILLS_LIST = data["data"]


def updateBill(id, data, db, is_commit):
    status, message = update_bill(id=id, data=data, db=db, is_commit=is_commit)
    if not status:
        log.error(f"Error while updating bill -> {message}")
        messagebox.showerror("Update Bill", message)
        return False
    else:
        return status


def add_bill_and_reduce_stock(db):
    product_qty_info = {}
    for id, info in Settings.BILL_DETAILS.get("products").items():
        product_qty_info[id] = {
            "rate":info.get("rate"),
            "quantity":info.get("quantity")
        }
    data = {"customer_id":Settings.BILL_DETAILS["customer"].get("customer_id"),
            "sale_year": Settings.BILL_DETAILS.get("extra").get("sale_year"),
            "sale_month": Settings.BILL_DETAILS.get("extra").get("sale_month"),
            "sale_day": Settings.BILL_DETAILS.get("extra").get("sale_day"),
            "product_qty":product_qty_info,
            "discount_amount":Settings.BILL_DETAILS["extra"].get("discount_amount"),
            "discount_percentage":Settings.BILL_DETAILS["extra"].get("discount_percentage"),
            "vat":Settings.BILL_DETAILS["extra"].get("vat"),
            "tax":Settings.BILL_DETAILS["extra"].get("tax"),
            "paid_amount":Settings.BILL_DETAILS["final"].get("paid_amount"),
            "extra_info":Settings.BILL_DETAILS.get("extra").get("extra_info")
            }
    
    log.info(f"Adding bill in db with data -> {data}")
    bill_number, message = add_bill(data, db=db, is_commit=False)
    if not bill_number:
        log.error(f"{bill_number} {message}")
        return False, message
    for id, details in Settings.BILL_DETAILS.get("products").items():
        product_status, product_message = update_product(id, data={"stock": float(details.get("stock"))-float(details.get("quantity"))}, db=db, is_commit=False)
        if not product_status:
            log.error(f"{product_status} {product_message}")
            return False, product_message
        else:
            log.info(f"{product_status} {product_message}")
            
    return bill_number, f"COMPLETE: Bill entry made in db with id {bill_number}."


def add_customer_account(data, db, is_commit):
    log.info(f"Adding customer account entry with data -> {data}")
    status, message = add_account(data, db=db, is_commit=is_commit)
    if not status:
        log.error(f"{status} {message}")
        return False, message
    else:
        return status, message


def make_payment_and_add_bill_entry(amount, db: Session=get_db()):
    Settings.BILL_DETAILS["final"]["paid_amount"] = float(amount)
    log.info(f"Saving bill, updating account and reducing stock with bill details -> {Settings.BILL_DETAILS}")

    # creating bill record and getting bill number and reducing stock in database
    bill_number, message = add_bill_and_reduce_stock(db=db)
    if not bill_number:
        db.rollback()
        log.error(message)
        messagebox.showerror("Billing System", message)
        return False
    # refreshTotalSales()
    refreshProductsList()
    log.info(f"for customer id: {Settings.BILL_DETAILS['customer'].get('customer_id')} -> {message}")

    # updating final bill details
    Settings.BILL_DETAILS["final"]["bill_number"] = f"{bill_number + 42341}"

    # updating to ledger
    data = {"customer_id":Settings.BILL_DETAILS['customer'].get('customer_id'),
            "transaction_year":Settings.BILL_DETAILS.get("extra").get("sale_year"),
            "transaction_month":Settings.BILL_DETAILS.get("extra").get("sale_month"),
            "transaction_day":Settings.BILL_DETAILS.get("extra").get("sale_day"),
            "bill_id":bill_number,
            "type":AccountType.debit,
            "description":f"Sales Bill #{Settings.BILL_DETAILS['final']['bill_number']}",
            "amount":Settings.BILL_DETAILS.get("final")["total"]}
    account_status, account_message = add_customer_account(data, db=db, is_commit=False)
    if not account_status:
        db.rollback()
        messagebox.showerror("Billing System", account_message)
        return False
    log.info(f"{account_message} -> id -> {account_status}")
    if amount:
        data = {"customer_id":Settings.BILL_DETAILS['customer'].get('customer_id'), 
                "transaction_year":Settings.BILL_DETAILS.get("extra").get("sale_year"),
                "transaction_month":Settings.BILL_DETAILS.get("extra").get("sale_month"),
                "transaction_day":Settings.BILL_DETAILS.get("extra").get("sale_day"),
                "bill_id":bill_number,
                "type":AccountType.credit,
                "description":f"Bill Payment #{Settings.BILL_DETAILS['final']['bill_number']}",
                "amount":amount}
        account_status, account_message = add_customer_account(data, db=db, is_commit=False)
        if not status:
            db.rollback()
            messagebox.showerror("Billing System", message)
            return False
        log.info(f"{account_message} -> id -> {account_status}")
    
    # committing the changes
    db.commit()
    db.close()

    # generating bill and saving to bills folder
    Settings.BILL_DETAILS["final"]["date"] = Settings.BILL_DETAILS.get("extra").get("date_of_sale")
    
    status, filename = generate_and_save_bill()
    if status:
        messagebox.showinfo("Billing System", f"Pdf file of invoice will open in the browser.\n\nInvoice no: #{Settings.BILL_DETAILS['final']['bill_number']}\n\nFile name: {filename}")
        threading.Thread(target=preview_pdf_in_browser, args=(filename,)).start()
    else:
        messagebox.showerror("Billing System", "Error occured while generating bill.")
    
    billingFrame.clearBillingFrame(force=True)
    return True


def update_bill_and_fix_stock(db):
    bill_id = Settings.BILL_DETAILS.get("id")
    product_qty_info = {}
    for id, info in Settings.BILL_DETAILS.get("products").items():
        product_qty_info[id] = {
            "rate":info.get("rate"),
            "quantity":info.get("quantity")
        }
    data = {"customer_id":Settings.BILL_DETAILS["customer"].get("customer_id"),
            "sale_year": Settings.BILL_DETAILS.get("extra").get("sale_year"),
            "sale_month": Settings.BILL_DETAILS.get("extra").get("sale_month"),
            "sale_day": Settings.BILL_DETAILS.get("extra").get("sale_day"),
            "product_qty":product_qty_info,
            "discount_amount":Settings.BILL_DETAILS["extra"].get("discount_amount"),
            "discount_percentage":Settings.BILL_DETAILS["extra"].get("discount_percentage"),
            "vat":Settings.BILL_DETAILS["extra"].get("vat"),
            "tax":Settings.BILL_DETAILS["extra"].get("tax"),
            "paid_amount":Settings.BILL_DETAILS["final"].get("paid_amount"),
            "extra_info":Settings.BILL_DETAILS.get("extra").get("extra_info")
            }

    bill_id = updateBill(bill_id, data, db=db, is_commit=False)
    if not bill_id:
        return False, bill_id

    for id, details in Settings.BILL_DETAILS.get("products").items():
        if Settings.BILL_DETAILS.get("saved_products").get(id) is None:
            stock_to_update = float(details.get("stock")) - float(details.get("quantity"))
        else:
            stock_to_update = float(details.get("stock")) + float(Settings.BILL_DETAILS.get("saved_products").get(id).get("quantity")) - float(details.get("quantity"))
        status, message = update_product(id, data={"stock": stock_to_update}, db=db, is_commit=False)
        if not status:
            log.error(f"{status} {message}")
            return False, message
        else:
            log.info(f"{status} {message}")
    
    for id, details in Settings.BILL_DETAILS.get("saved_products").items():
        if Settings.BILL_DETAILS.get("products").get(id) is None:
            status, message = update_product(id, data={"stock": float(details.get("stock")) + float(details.get("quantity"))}, db=db, is_commit=False)
            if not status:
                log.error(f"{status} {message}")
                return False, message
            else:
                log.info(f"{status} {message}")
    
    return bill_id, f"COMPLETE: Bill entry updated in db with id {bill_id}."


def update_customer_account(id, data, db, is_commit):
    status, message = update_account(id, data, db=db, is_commit=is_commit)
    if not status:
        log.error(f"{status} {message}")
        return False, message
    else:
        return status, message


def make_payment_and_update_bill_entry(amount, db: Session=get_db()):
    # updating bill record and getting bill number and reducing stock in database
    Settings.BILL_DETAILS["final"]["paid_amount"] = float(amount)
    log.info(f"Updating bill ->  {Settings.BILL_DETAILS['extra'].get('bill_number')} -> with bill details -> {Settings.BILL_DETAILS}")

    bill_id, message = update_bill_and_fix_stock(db=db)
    if not bill_id:
        db.rollback()
        log.error(message)
        messagebox.showerror("Billing System", message)
        return False
    log.info(f"Updated bill with id {bill_id} for customer id: {Settings.BILL_DETAILS['customer'].get('customer_id')} -> {message}")

    # updating bill details
    Settings.BILL_DETAILS["final"]["bill_number"] = f"{int(bill_id) + 42341}"
    Settings.BILL_DETAILS["final"]["date"] = Settings.BILL_DETAILS["extra"].get("date_of_sale")

    # updating to ledger
    account_status, accounts = get_accounts(queryDict={"bill_id":bill_id}, limit=None, db=db)
    if not account_status:
        db.rollback()
        log.error(f"{account_status} -> {accounts}")
        messagebox.showerror("Billing System", message)
        return False
    log.info(f"Got accounts related to bill -> {accounts['data']}")

    accountForPaymentFound = False
    for account in accounts["data"]:
        if account['type'] == "debit":
            log.info(f"Updating account with id{account['id']}")
            data = {"customer_id":Settings.BILL_DETAILS['customer'].get('customer_id'), 
                    "transaction_year":Settings.BILL_DETAILS.get("extra").get("sale_year"),
                    "transaction_month":Settings.BILL_DETAILS.get("extra").get("sale_month"),
                    "transaction_day":Settings.BILL_DETAILS.get("extra").get("sale_day"),
                    "amount":Settings.BILL_DETAILS.get("final")["total"]}
            status, message = update_customer_account(account['id'], data, db=db, is_commit=False)
            if not status:
                db.rollback()
                return False
            log.info(message)
        if account['type'] == "credit":
            accountForPaymentFound = True
            if amount:
                data = {"customer_id":Settings.BILL_DETAILS['customer'].get('customer_id'), 
                        "transaction_year":Settings.BILL_DETAILS.get("extra").get("sale_year"),
                        "transaction_month":Settings.BILL_DETAILS.get("extra").get("sale_month"),
                        "transaction_day":Settings.BILL_DETAILS.get("extra").get("sale_day"),
                        "amount":amount}
                status, message = update_customer_account(account['id'], data, db=db, is_commit=False)
                if not status:
                    db.rollback()
                    return False
                log.info(message)
    
    if amount and not accountForPaymentFound:
        data = {"customer_id":Settings.BILL_DETAILS['customer'].get('customer_id'), 
                "transaction_date":Settings.BILL_DETAILS.get("extra").get("date_of_sale_utc"),
                "bill_id":bill_id,
                "type":AccountType.credit,
                "description":f"Bill Payment #{Settings.BILL_DETAILS['final']['bill_number']}",
                "amount":amount}
        account_status, account_message = add_customer_account(data, db=db, is_commit=False)
        if not status:
            db.rollback()
            messagebox.showerror("Billing System", message)
            return False
        log.info(f"{account_message} -> id -> {account_status}")
    
    # committing the changes
    db.commit()
    db.close()

    response = messagebox.askyesno("Update bill", "Do you want to print the updated bill?")
    if response==1:
        # generating bill and saving to bills folder
        log.info(f"Generating bill pdf with data -> {Settings.BILL_DETAILS}")
        status, filename = generate_and_save_bill()
        if status:
            messagebox.showinfo("Billing System", f"Pdf file of invoice will open in the browser.\n\nInvoice no: #{Settings.BILL_DETAILS['final']['bill_number']}\n\nFile name: {filename}")
            threading.Thread(target=preview_pdf_in_browser, args=(filename,)).start()
        else:
            messagebox.showerror("Billing System", "Error occured while generating bill.")

    billingFrame.clearBillingFrame(force=True)
    # refreshTotalSales()
    refreshProductsList()

    return True


def generate_and_save_bill():
    askForPayment = int(Settings.CURRENT_SETTINGS.get("ask_for_payment")) if Settings.CURRENT_SETTINGS.get("ask_for_payment") else 0
    
    customer_name = Settings.BILL_DETAILS['customer'].get('full_name') if Settings.BILL_DETAILS['customer'].get('full_name') else Settings.BILL_DETAILS['customer'].get('company')
    filename = f"{customer_name}_{Settings.BILL_DETAILS['final'].get('bill_number')}_{Settings.BILL_DETAILS['final']['date'].replace('/','_')}.pdf"
    try:
        CustomerBill(f"./bills/{filename}",
                    company_info=Settings.CURRENT_SETTINGS["company_profile"], bill_details=Settings.BILL_DETAILS, 
                    title=f"{customer_name} {Settings.BILL_DETAILS['final']['date']}",
                    author="Inventoray Management and Billing System, By Datakhoj",
                    subject=f"Bill To {customer_name}",
                    show_payment=bool(askForPayment))
        log.info(f"Bill generated and saved as: {filename}")
        return True, filename
    except Exception as e:
        if os.path.exists(os.path.join(os.getcwd(),"bills",filename)):
            os.remove(os.path.join(os.getcwd(),"bills",filename))
        log.exception(f"Error occured while generating bill -> {e}")
        return False, filename   


def preprocess_bill_details():
    if not Settings.CURRENT_SETTINGS.get("company_profile"):
        messagebox.showinfo("Billing System", "Please complete your profile in Company Profile tab.")
        return False
    if not Settings.BILL_DETAILS.get("customer"):
            messagebox.showinfo("Billing System", "Please add a customer to bill.")
            return False
    if not Settings.BILL_DETAILS.get("products"):
        messagebox.showinfo("Billing System", "Please add products to bill.")
        return False
    companyProfileMustHaves = ("company_name", "pan_no", "country","province","district","municipality","ward","toll")
    for info in companyProfileMustHaves:
        if not Settings.CURRENT_SETTINGS["company_profile"].get(info):
            messagebox.showwarning("Missing profile details", f"Please completely fill the details in company profile.\nMissing: {info}")
            return False
    if not Settings.CURRENT_SETTINGS["company_profile"].get("phone_number") and not Settings.CURRENT_SETTINGS["company_profile"].get("telephone"):
        messagebox.showwarning("Missing profile details", f"Please completely fill the details in company profile.\nMissing: Phone number or telephone")
        return False
    if not Settings.BILL_DETAILS.get("extra").get("date_of_sale"):
        messagebox.showinfo("Billing System", "Please add date of sale.")
        return False
    return True


def preview_pdf_in_browser(filename):
    os.startfile(os.path.join(os.getcwd(),"bills",filename))