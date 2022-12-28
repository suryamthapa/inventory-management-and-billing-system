import logging
from tkinter import messagebox
import frontend.config as Settings
# frontend imports
from frontend.utils.products import refreshProductsList
import frontend.frames.purchaseEntry as purchaseEntryFrame
# backend imports
from backend.api.products import update_product
from backend.api.purchase import add_purchase, update_purchase, get_purchases


log = logging.getLogger("frontend")


def refreshPurchasesList():
    status, data = get_purchases(limit=None)
    if status:
        Settings.PURCHASE_LIST = data["data"]


def updatePurchase(id, data):
    status, message = update_purchase(id=id, data=data)
    if not status:
        log.error(f"Error while updating purchase -> {message}")
        messagebox.showerror("Update Purchase", message)
        return False
    else:
        return status


def entry_purchase_and_add_stock():
    invoice_number = Settings.PURCHASE_DETAILS.get("extra").get("invoice_number")
    date_of_purchase_utc = Settings.PURCHASE_DETAILS.get("extra").get("date_of_purchase_utc")
    excise_duty = Settings.PURCHASE_DETAILS.get("extra").get("excise_duty")
    cash_discount = Settings.PURCHASE_DETAILS.get("extra").get("cash_discount")
    p_discount = Settings.PURCHASE_DETAILS.get("extra").get("p_discount")
    extra_discount = Settings.PURCHASE_DETAILS.get("extra").get("extra_discount")
    vat = Settings.PURCHASE_DETAILS.get("extra").get("vat")
    cash_payment = Settings.PURCHASE_DETAILS.get("extra").get("cash_payment")
    balance_amount = Settings.PURCHASE_DETAILS.get("extra").get("balance_amount")
    extra_info = Settings.PURCHASE_DETAILS.get("extra").get("extra_info")
    
    product_qty_info = {}
    for id, info in Settings.PURCHASE_DETAILS.get("products").items():
        product_qty_info[id] = {
            "rate":info.get("rate"),
            "quantity":info.get("quantity")
        }

    data = {"invoice_number":invoice_number,
        "date_of_purchase": date_of_purchase_utc,
        "product_qty":product_qty_info,
        "vendor_id":Settings.PURCHASE_DETAILS.get("vendor").get("vendor_id"),
        "excise_duty":excise_duty,
        "cash_discount":cash_discount,
        "p_discount":p_discount,
        "extra_discount":extra_discount,
        "vat":vat,
        "cash_payment":cash_payment,
        "balance_amount":balance_amount,
        "extra_info": extra_info}
    purchase_id, message = add_purchase(data)
    if not purchase_id:
        log.error(f"{purchase_id} {message}")
        return False, message
    for id, details in Settings.PURCHASE_DETAILS.get("products").items():
        status, message = update_product(id, data={"stock": float(details.get("stock"))+float(details.get("quantity"))})
        if not status:
            log.error(f"{status} {message}")
            return False, message

    return True, f"COMPLETE: Purchase entry made in db with id {purchase_id}."


def entry_purchase():
    # purchase entry and adding stock in database
    status, message = entry_purchase_and_add_stock()
    if not status:
        messagebox.showerror("Purchase Entry System", message)
        return False
    log.info(f"Purchase entry for vendor id: {Settings.PURCHASE_DETAILS['vendor'].get('vendor_id')} -> {message}")

    refreshProductsList()
    refreshPurchasesList()
    return True


def update_purchase_and_fix_stock():
    log.info(Settings.PURCHASE_DETAILS)
    id = Settings.PURCHASE_DETAILS.get("id")
    invoice_number = Settings.PURCHASE_DETAILS.get("extra").get("invoice_number")
    date_of_purchase_utc = Settings.PURCHASE_DETAILS.get("extra").get("date_of_purchase_utc")
    excise_duty = Settings.PURCHASE_DETAILS.get("extra").get("excise_duty")
    cash_discount = Settings.PURCHASE_DETAILS.get("extra").get("cash_discount")
    p_discount = Settings.PURCHASE_DETAILS.get("extra").get("p_discount")
    extra_discount = Settings.PURCHASE_DETAILS.get("extra").get("extra_discount")
    vat = Settings.PURCHASE_DETAILS.get("extra").get("vat")
    cash_payment = Settings.PURCHASE_DETAILS.get("extra").get("cash_payment")
    balance_amount = Settings.PURCHASE_DETAILS.get("extra").get("balance_amount")
    extra_info = Settings.PURCHASE_DETAILS.get("extra").get("extra_info")
    
    product_qty_info = {}
    for product_id, info in Settings.PURCHASE_DETAILS.get("products").items():
        product_qty_info[product_id] = {
            "rate":info.get("rate"),
            "quantity":info.get("quantity")
        }
 
    data = {"invoice_number":invoice_number,
        "date_of_purchase": date_of_purchase_utc,
        "product_qty":product_qty_info,
        "vendor_id":Settings.PURCHASE_DETAILS.get("vendor").get("vendor_id"),
        "excise_duty":excise_duty,
        "cash_discount":cash_discount,
        "p_discount":p_discount,
        "extra_discount":extra_discount,
        "vat":vat,
        "cash_payment":cash_payment,
        "balance_amount":balance_amount,
        "extra_info": extra_info}
    purchase_id = updatePurchase(id, data)
    if not purchase_id:
        return False, purchase_id

    for id, details in Settings.PURCHASE_DETAILS.get("products").items():
        if Settings.PURCHASE_DETAILS.get("saved_products").get(id) is None:
            stock_to_update = float(details.get("stock")) + float(details.get("quantity"))
        else:
            stock_to_update = float(details.get("stock")) + float(details.get("quantity")) - float(Settings.PURCHASE_DETAILS.get("saved_products").get(id).get("quantity"))
        status, message = update_product(id, data={"stock": stock_to_update})
        if not status:
            log.error(f"{status} {message}")
            return False, message
    
    for id, details in Settings.PURCHASE_DETAILS.get("saved_products").items():
        if Settings.PURCHASE_DETAILS.get("products").get(id) is None:
            status, message = update_product(id, data={"stock": float(details.get("stock")) - float(details.get("quantity"))})
            if not status:
                log.error(f"{status} {message}")
                return False, message

    return True, f"COMPLETE: Purchase entry updated in db with id {purchase_id}."


def update_purchase_entry():
    # purchase update and updating stock in database
    status, message = update_purchase_and_fix_stock()
    if not status:
        return False

    refreshProductsList()
    refreshPurchasesList()
    purchaseEntryFrame.clearPurchaseEntryFrame(force=True)
    return True


def preprocess_purchase_details():
    if not Settings.PURCHASE_DETAILS.get("vendor") or not Settings.PURCHASE_DETAILS.get("vendor").get("vendor_id"):
            messagebox.showinfo("Purchase Entry System", "Please add a vendor.")
            return False
    if not Settings.PURCHASE_DETAILS.get("extra").get("invoice_number"):
            messagebox.showinfo("Purchase Entry System", "Please add invoice number.")
            return False
    if not Settings.PURCHASE_DETAILS.get("products"):
        messagebox.showinfo("Purchase Entry System", "Please add products.")
        return False
    return True