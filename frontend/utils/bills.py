import os
import tempfile
import logging
from tkinter import messagebox
import threading
import frontend.config as Settings
if Settings.DATE_TIME_TYPE == "NEPALI":
    from nepali_datetime import date
else:
    from datetime import date
from frontend.utils.billPdfGen import CustomerBill
import frontend.frames.billing as billingFrame
from backend.api.bills import add_bill
from backend.api.sales import add_sales
from backend.api.products import update_product


log = logging.getLogger("frontend")


def get_bill_number():
    data = {"customer_id":Settings.BILL_DETAILS["customer"].get("customer_id"), 
            "paid_amount":Settings.BILL_DETAILS["customer"].get("paid_amount"),
            "discount_amount":Settings.BILL_DETAILS["customer"].get("discount_amount"),
            "discount_percentage":Settings.BILL_DETAILS["customer"].get("discount_percentage"),
            "vat":Settings.BILL_DETAILS["customer"].get("vat"),
            "tax":Settings.BILL_DETAILS["customer"].get("tax")}

    bill_number, message = add_bill(data)
    if not bill_number:
        messagebox.showerror("Billing System", message)
        return False, message
    return bill_number, message


def entry_sales_and_reduce_stock(bill_id):
    for id, details in Settings.BILL_DETAILS.get("products").items():
        data = {"bill_id":bill_id,
                "product_id":id,
                "quantity":details.get("quantity"),
                "selling_price":details.get("rate"),
                "discount_percentage":details.get("discount_percentage"),
                "discount_amount":details.get("discount_amount"),
                "vat":details.get("vat"),
                "tax":details.get("tax")}
    
        status, message = add_sales(data)
        if not status:
            log.error(f"{status} {message}")
            return False, message
        else:
            log.info(f"UPDATED sales and reduced stock -> {data}")
        status, message = update_product(id, data={"stock": int(details.get("stock"))-int(details.get("quantity"))})
        if not status:
            log.error(f"{status} {message}")
            return False, message

    return True, f"COMPLETE: Sales detail for bill id {bill_id} added to database."


def make_payment(amount):
    bill_number, message = get_bill_number()
    
    if not bill_number:
        log.error(message)
        return False

    log.info(f"for customer id: {Settings.BILL_DETAILS['customer'].get('customer_id')} -> {message}")
    status, message = entry_sales_and_reduce_stock(bill_number)
    if not status:
        messagebox.showerror("Billing System", message)
        return False
    log.info(message)

    today = date.today()
    today = today.strftime("%Y/%m/%d")
    Settings.BILL_DETAILS["final"]["bill_number"] = bill_number + 42341
    Settings.BILL_DETAILS["final"]["date"] = today
    Settings.BILL_DETAILS["final"]["paid_amount"] = float(amount)

    status, filename = generate_and_save_bill()
    if status:
        messagebox.showinfo("Billing System", "Pdf file of the bill will open in the browser.")
        threading.Thread(target=preview_pdf_in_browser, args=(filename,)).start()
    else:
        messagebox.showerror("Billing System", "Error occured while generating bill.")
    # billingFrame.clearBillingFrame(force=True)
    return True


def generate_and_save_bill():
    askForPayment = int(Settings.CURRENT_SETTINGS.get("ask_for_payment")) if Settings.CURRENT_SETTINGS.get("ask_for_payment") else 0
    askForDiscount = int(Settings.CURRENT_SETTINGS.get("ask_for_discount")) if Settings.CURRENT_SETTINGS.get("ask_for_discount") else 0
    askForVat = int(Settings.CURRENT_SETTINGS.get("ask_for_vat")) if Settings.CURRENT_SETTINGS.get("ask_for_vat") else 0
    askForTax = int(Settings.CURRENT_SETTINGS.get("ask_for_tax")) if Settings.CURRENT_SETTINGS.get("ask_for_tax") else 0
    defaultVat = int(Settings.CURRENT_SETTINGS.get("default_vat")) if Settings.CURRENT_SETTINGS.get("default_vat") else 0
    defaultDiscount = int(Settings.CURRENT_SETTINGS.get("default_discount")) if Settings.CURRENT_SETTINGS.get("default_discount") else 0
    defaultTax = int(Settings.CURRENT_SETTINGS.get("default_tax")) if Settings.CURRENT_SETTINGS.get("default_tax") else 0

    if defaultVat and not askForVat:
        Settings.BILL_DETAILS["extra"]["vat"] = defaultVat
    if defaultDiscount and not askForDiscount:
        Settings.BILL_DETAILS["extra"]["discount_percentage"] = defaultDiscount
    if defaultTax and not askForTax:
        Settings.BILL_DETAILS["extra"]["tax"] = defaultTax
    
    customer_name = Settings.BILL_DETAILS['customer'].get('full_name') if Settings.BILL_DETAILS['customer'].get('full_name') else Settings.BILL_DETAILS['customer'].get('company')
    filename = f"{customer_name}_{Settings.BILL_DETAILS['final'].get('bill_number')}_{Settings.BILL_DETAILS['final']['date'].replace('/','_')}.pdf"
    try:
        CustomerBill(f"./bills/{filename}",
                    company_info=Settings.CURRENT_SETTINGS["company_profile"], bill_details=Settings.BILL_DETAILS, 
                    title=f"{customer_name} {Settings.BILL_DETAILS['final']['date']}",
                    author="Inventoray Management and Billing System, By Datakhoj",
                    subject=f"Bill To {customer_name}",
                    show_payment=bool(askForPayment), show_discount=bool(askForDiscount) or bool(defaultDiscount), show_vat=bool(askForVat) or bool(defaultVat), show_tax=bool(askForTax) or bool(defaultTax))
        log.info(f"Bill generated and saved as: {filename}")
        return True, filename
    except Exception as e:
        if os.path.exists(os.path.join(os.getcwd(),"bills",filename)):
            os.remove(os.path.join(os.getcwd(),"bills",filename))
        log.error(f"Error occured while generating bill -> {e}")
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
    companyProfileMustHaves = ("company_name", "pan_no", "country","province","district","municipality","ward","toll","zip_code")
    for info in companyProfileMustHaves:
        if not Settings.CURRENT_SETTINGS["company_profile"].get(info):
            messagebox.showwarning("Missing profile details", f"Please completely fill the details in company profile.\nMissing: {info}")
            return False
    if not Settings.CURRENT_SETTINGS["company_profile"].get("phone_number") and not Settings.CURRENT_SETTINGS["company_profile"].get("telephone"):
        messagebox.showwarning("Missing profile details", f"Please completely fill the details in company profile.\nMissing: Phone number or telephone")
        return False
    return True


def preview_pdf_in_browser(filename):
    os.startfile(os.path.join(os.getcwd(),"bills",filename))