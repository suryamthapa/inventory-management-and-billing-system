import logging
from datetime import date
import math
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.purchase import Purchases
from backend.models.products import Products
from backend.models.vendors import Vendors
from backend.utils.date_format import get_nepali_datetime_from_utc
from core import nepali_datetime


log = logging.getLogger("backend")


def add_purchase(data:dict = {}, db: Session=get_db()):
    try:
        purchase = Purchases(invoice_number=data.get("invoice_number"),
                    date_of_purchase=data.get("date_of_purchase"),
                    product_qty=data.get("product_qty"),
                    vendor_id=data.get("vendor_id"),
                    excise_duty=data.get("excise_duty"),
                    cash_discount=data.get("cash_discount"),
                    p_discount=data.get("p_discount"),
                    extra_discount=data.get("extra_discount"),
                    vat=data.get("vat"),
                    cash_payment=data.get("cash_payment"),
                    balance_amount=data.get("balance_amount"),
                    extra_info=data.get("extra_info"))
    
        db.add(purchase)
        db.commit()
        db.refresh(purchase)
        db.close()
        return purchase.id, "Purchase added successfully!"
    except IntegrityError as f:
        db.close()
        log.exception(f"ERROR: while adding purchase with data {data} -> {f}")
        return False, "Purchase with same invoice number already exists."
    except Exception as e:
        db.close()
        log.exception(f"ERROR: while adding purchase with data {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_purchases(queryDict: dict = {}, from_= None, to=None, asc = True, sort_column: str = "id", 
                page=1, limit=11, db: Session = get_db()):
    try:
        table_columns = [column.name for column in inspect(Purchases).c]
        vendor_table_columns = [column.name for column in inspect(Vendors).c]
        if sort_column not in table_columns and sort_column not in vendor_table_columns:
            db.close()
            return False,  {"message": f"Column '{sort_column}' does not exist in Purchases or Vendors table.",
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns and key not in vendor_table_columns:
                db.close()
                return False,  {"message": f"Column '{key}' does not exist in Purchases or Vendors table.",
                            "data": []}

        toEval = ", ".join(f"Purchases.{key} == '{value}'" for key, value in queryDict.items() if key in table_columns) if queryDict else None
        query = db.query(Purchases, Vendors).filter(Purchases.vendor_id == Vendors.id).filter(eval(toEval)) if toEval else db.query(Purchases, Vendors).filter(Purchases.vendor_id == Vendors.id)

        toEvalForVendorQueries = ", ".join(f"Vendors.{key} == '{value}'" for key, value in queryDict.items() if key in vendor_table_columns) if queryDict else None
        query = query.filter(eval(toEvalForVendorQueries)) if toEvalForVendorQueries else query

        total_purchase = query.count()
        if limit:
            skip = ((page-1)*limit)
            totalPages = math.ceil(total_purchase/limit)
        else:
            skip = 0
            totalPages = 1
        
        sort_query = eval(f"Purchases.{sort_column}") if asc else eval(f"Purchases.{sort_column}.desc()")
        query = query.order_by(sort_query)
        
        if from_ and to:
            query = query.filter(and_(func.date(Purchases.created_at) >= from_), func.date(Purchases.created_at) <= to)
        
        if limit:
            purchases = query.offset(skip).limit(limit).all()
        else:
            purchases = query.all()

        def rowToDict(purchase):
            vendor = purchase[1]
            purchase = purchase[0]
            product_qty_payload = {}
            if purchase.product_qty:
                product_qty_info = eval(str(purchase.product_qty)) if purchase.product_qty else purchase.product_qty
                for product_id, values in product_qty_info.items():
                    product = db.query(Products).filter(Products.id==product_id).first()
                    product_qty_payload[product_id] = {
                        "product_name": product.product_name if product else "Deleted Product.",
                        "quantity":values.get("quantity"),
                        "rate":values.get("rate")
                        }
            # vendor = db.query(Vendors).filter(Vendors.id==purchase.vendor_id).first()
            vendor_info = {"id": vendor.id,
                            "vat_number":vendor.vat_number,
                            "vendor_name": vendor.vendor_name,
                            "address": vendor.address,
                            "phone_number":vendor.phone_number,
                            "telephone": vendor.telephone,
                            "email":vendor.email,
                            "extra_info": eval(str(vendor.extra_info)) if vendor.extra_info else vendor.extra_info
                            } if vendor else {}
            
            ne_datetime, message = get_nepali_datetime_from_utc(purchase.date_of_purchase, format="BS")
            if ne_datetime:
                final_nepali_date = nepali_datetime.date(ne_datetime.year, ne_datetime.month, ne_datetime.day)
                date_of_purchase = final_nepali_date.strftime("%d/%m/%Y")
            else:
                date_of_purchase = "N/A" 
                log.exception(f"Error occured while getting nepali datetime from utc -> {message}")

            return {"id": purchase.id,
                    "invoice_number":purchase.invoice_number,
                    "date_of_purchase": date_of_purchase,
                    "product_qty":product_qty_payload,
                    "vendor":vendor_info,
                    "excise_duty":purchase.excise_duty,
                    "cash_discount":purchase.cash_discount,
                    "p_discount":purchase.p_discount,
                    "extra_discount":purchase.extra_discount,
                    "vat":purchase.vat,
                    "cash_payment":purchase.cash_payment,
                    "balance_amount":purchase.balance_amount,
                    "extra_info": eval(str(purchase.extra_info)) if purchase.extra_info else purchase.extra_info}
        payload = {
            "message": "Success",
            "data": list(map(rowToDict, purchases)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(purchases)}

        db.close()
        log.info(f"FETCHED: All purchase with queryDict -> {queryDict}.")
        return True, payload
    except Exception as e:
        db.close()
        log.exception(f"Error occured while fetching purchase with queryDict: {queryDict} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def update_purchase(id: int, data: dict = {}, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."

        purchase = db.query(Purchases).filter(Purchases.id==id).first()
        if not purchase: 
            db.close()
            return False, "Purchase with given id does not exist."
        for key, value in data.items():
            setattr(purchase, key, value)
    
        db.commit()
        db.close()
        return True, "Purchase updated successfully!"
    except IntegrityError as f:
        db.close()
        log.exception(f"ERROR: while updating purchase with id {id}-> {f}")
        return False, f"Purchase already exists with given invoice number."
    except Exception as e:
        db.close()
        log.exception(f"ERROR: while updating purchase with id {id}-> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def delete_purchase(id=None, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."
    
        db.query(Purchases).filter(Purchases.id==id).delete()
        db.commit()
        db.close()
        return id, "Purchase deleted successfully!"
    except Exception as e:
        db.close()
        log.exception(f"ERROR: while deleting purchase with id {id} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"