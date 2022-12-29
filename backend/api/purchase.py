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
        vendor_table_columns = ["vendor_id" if column.name == "id" else column.name for column in inspect(Vendors).c]
        if sort_column and sort_column not in table_columns and sort_column not in vendor_table_columns:
            db.close()
            message = f"Column '{sort_column}' does not exist in Purchases or Vendors table."
            log.error(f"Sort {message}")
            return False,  {"message": message,
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns and key not in vendor_table_columns:
                db.close()
                message = f"Column '{sort_column}' does not exist in Purchases or Vendors table."
                log.error(f"In querydict {queryDict} : {message}")
                return False,  {"message": message,
                            "data": []}

        toEval = ", ".join(f"Purchases.{key}.ilike('%{value}%')" for key, value in queryDict.items() if key in table_columns) if queryDict else None
        query = db.query(Purchases, Vendors).filter(Purchases.vendor_id == Vendors.id).filter(eval(toEval)) if toEval else db.query(Purchases, Vendors).filter(Purchases.vendor_id == Vendors.id)

        toEvalForVendorQueries = ", ".join(f"Vendors.{key}.ilike('%{value}%')" for key, value in queryDict.items() if key in vendor_table_columns) if queryDict else None
        query = query.filter(eval(toEvalForVendorQueries)) if toEvalForVendorQueries else query

        total_purchase = query.count()
        if limit:
            skip = ((page-1)*limit)
            totalPages = math.ceil(total_purchase/limit)
        else:
            skip = 0
            totalPages = 1
        
        if sort_column and sort_column in table_columns:
            sort_query = eval(f"Purchases.{sort_column}") if asc else eval(f"Purchases.{sort_column}.desc()")
            query = query.order_by(sort_query)
        elif sort_column and sort_column in vendor_table_columns:
            sort_column = "id" if sort_column == "vendor_id" else sort_column
            sort_query = eval(f"Vendors.{sort_column}") if asc else eval(f"Vendors.{sort_column}.desc()")
            query = query.order_by(sort_query)
        
        if from_ is not None:
            if to is not None:
                query = query.filter(and_(func.date(Purchases.date_of_purchase) >= from_, func.date(Purchases.date_of_purchase) <= to))
            else:
                query = query.filter(func.date(Purchases.date_of_purchase) >= from_)

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
                        "stock": product.stock if product else 0,
                        "unit": product.unit,
                        "quantity":values.get("quantity"),
                        "marked_price": product.marked_price if product else 0,
                        "rate":values.get("rate"),
                        }
            vendor_info = {"vendor_id": vendor.id,
                            "vat_number":vendor.vat_number,
                            "vendor_name": vendor.vendor_name,
                            "address": vendor.address,
                            "phone_number":vendor.phone_number,
                            "telephone": vendor.telephone,
                            "email":vendor.email,
                            "extra_info": eval(str(vendor.extra_info)) if vendor.extra_info else vendor.extra_info
                            } if vendor else {}
            
            date_of_purchase_utc = purchase.date_of_purchase
            ne_datetime, message = get_nepali_datetime_from_utc(purchase.date_of_purchase, format="BS")
            if ne_datetime:
                final_nepali_date = nepali_datetime.date(ne_datetime.year, ne_datetime.month, ne_datetime.day)
                date_of_purchase = final_nepali_date.strftime("%d/%m/%Y")
            else:
                date_of_purchase = "N/A" 
                log.exception(f"Error occured while getting nepali datetime from utc -> {message}")

            return {"id": purchase.id,
                    "vendor":vendor_info,
                    "saved_products":product_qty_payload.copy(),
                    "products":product_qty_payload,
                    "extra":{
                            "invoice_number":purchase.invoice_number,
                            "date_of_purchase": date_of_purchase,
                            "date_of_purchase_utc": date_of_purchase_utc,
                            "excise_duty":purchase.excise_duty,
                            "cash_discount":purchase.cash_discount,
                            "p_discount":purchase.p_discount,
                            "extra_discount":purchase.extra_discount,
                            "vat":purchase.vat,
                            "cash_payment":purchase.cash_payment,
                            "balance_amount":purchase.balance_amount,
                            "extra_info": eval(str(purchase.extra_info)) if purchase.extra_info else purchase.extra_info
                            },
                    "final":{}
                    }
        payload = {
            "message": "Success",
            "data": list(map(rowToDict, purchases)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(purchases)}

        db.close()
        log.info(f"FETCHED: All purchase with queryDict -> {queryDict} sort column -> {sort_column} in {'ascending' if asc else 'descending'} order.")
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
        return id, "Purchase updated successfully!"
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