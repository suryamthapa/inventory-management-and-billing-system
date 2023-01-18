import math
import logging
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.bills import Bills
from backend.models.customers import Customers
from backend.models.products import Products
from backend.utils.date_format import get_nepali_datetime_from_utc
from core import nepali_datetime

log = logging.getLogger("backend")


def get_bills(queryDict: dict = {}, from_= None, to=None, asc = True, sort_column: str = "bill_number", 
                page=1, limit=11, db: Session = get_db()):
    try:
        table_columns = ["bill_number" if column.name=="id" else column.name for column in inspect(Bills).c] + ["date_of_sale"]
        customer_table_columns = ["customer_id" if column.name=="id" else column.name  for column in inspect(Customers).c]
        if sort_column and sort_column not in table_columns and sort_column not in customer_table_columns:
            db.close()
            message = f"Column '{sort_column}' does not exist in Bills or Customers table."
            log.error(f"Sort {message}")
            return False,  {"message": message,
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns and key not in customer_table_columns:
                db.close()
                message = f"Column '{key}' does not exist in Bills or Customers table."
                log.error(f"In querydict {queryDict} : {message}")
                return False,  {"message": message,
                            "data": []}

        toEval = []
        if queryDict:
            for key, value in queryDict.items():
                if key in table_columns:
                    if key != "bill_number":
                        toEval.append(f"Bills.{key}.ilike('%{value}%')")
                    else:
                        toEval.append(f"Bills.id == {int(value) - 42341}") if value else toEval.append(f"Bills.id.ilike('%{value}%')")
        toEval = ", ".join(toEval)

        query = db.query(Bills, Customers).filter(Bills.customer_id == Customers.id).filter(eval(toEval)) if toEval else db.query(Bills, Customers).filter(Bills.customer_id == Customers.id)

        toEvalForCustomerQueries = ", ".join(f"Customers.{key}.ilike('%{value}%')" for key, value in queryDict.items() if key in customer_table_columns) if queryDict else None
        query = query.filter(eval(toEvalForCustomerQueries)) if toEvalForCustomerQueries else query
        
        total_products = query.count()
        if limit:
            skip = ((page-1)*limit)
            totalPages = math.ceil(total_products/limit)
        else:
            skip = 0
            totalPages = 1

        if sort_column and sort_column in table_columns:
            if sort_column == "date_of_sale":
                query = query.order_by(Bills.sale_year, Bills.sale_month, Bills.sale_day) if asc else query.order_by(Bills.sale_year.desc(), Bills.sale_month.desc(), Bills.sale_day.desc())
            else:
                sort_column = "id" if sort_column == "bill_number" else sort_column
                sort_query = eval(f"Bills.{sort_column}") if asc else eval(f"Bills.{sort_column}.desc()")
                query = query.order_by(sort_query)
        elif sort_column and sort_column in customer_table_columns:
            sort_column = "id" if sort_column == "customer_id" else sort_column
            sort_query = eval(f"Customers.{sort_column}") if asc else eval(f"Customers.{sort_column}.desc()")
            query = query.order_by(sort_query)
        
        if from_ is not None:
            from_meta = from_.split("/")
            from_year = int(from_meta[2])
            from_month = int(from_meta[1])
            from_day = int(from_meta[0])
            query = query.filter(and_(Bills.sale_year >= from_year, Bills.sale_month >= from_month, Bills.sale_day >= from_day))
            if to is not None:
                to_meta = to.split("/")
                to_year = int(to_meta[2])
                to_month = int(to_meta[1])
                to_day = int(to_meta[0])
                query = query.filter(and_(Bills.sale_year <= to_year, Bills.sale_month <= to_month, Bills.sale_day <= to_day))

        if limit:
            bills = query.offset(skip).limit(limit).all()
        else:
            bills = query.all()
        
        def rowToDict(bill):
            customer = bill[1]
            bill = bill[0]
            product_qty_payload = {}
            if bill.product_qty:
                product_qty_info = eval(str(bill.product_qty)) if bill.product_qty else bill.product_qty
                for product_id, values in product_qty_info.items():
                    product = db.query(Products).filter(Products.id==product_id).first()
                    product_qty_payload[product_id] = {
                        "product_name": product.product_name if product else "Deleted Product.",
                        "stock": product.stock if product else 0,
                        "unit": product.unit if product else "",
                        "quantity":values.get("quantity"),
                        "cost_price": product.cost_price if product else 0,
                        "rate":values.get("rate"),
                        }
            customer_info = {"customer_id": customer.id,
                            "full_name":customer.full_name,
                            "company": customer.company,
                            "company_pan_no":customer.company_pan_no,
                            "phone_number": customer.phone_number,
                            "telephone": customer.telephone,
                            "address":customer.address,
                            "email":customer.email,
                            "extra_info": eval(str(customer.extra_info)) if customer.extra_info else customer.extra_info
                            } if customer else {}

            return {"id": bill.id,
                    "customer":customer_info,
                    "saved_products":product_qty_payload.copy(),
                    "products":product_qty_payload,
                    "extra":{
                            "bill_number": bill.id + 42341,
                            "sale_year": bill.sale_year,
                            "sale_month": bill.sale_month,
                            "sale_day": bill.sale_day,
                            "discount_amount":bill.discount_amount,
                            "discount_percentage":bill.discount_percentage,
                            "vat":bill.vat,
                            "tax":bill.tax,
                            "paid_amount":bill.paid_amount,
                            "extra_info": eval(str(bill.extra_info)) if bill.extra_info else bill.extra_info
                            },
                    "final":{
                        "paid_amount":bill.paid_amount,
                    }
                    }

        payload = {
            "message": "Success",
            "data": list(map(rowToDict, bills)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(bills)
        }

        db.close()
        log.info(f"FETCHED: All bills with queryDict -> {queryDict} sort column -> {sort_column} in {'ascending' if asc else 'descending'} order.")
        return True, payload
    except Exception as e:
        db.close()
        log.exception(f"Error occured while fetching bills with queryDict: {queryDict} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_bill(id: int = 0, db: Session = get_db()):
    try:
        if not id:
            return False, f"Please provide bill id."

        bill = db.query(Bills).filter(Bills.id==id).first()
        if not bill:
            return False, f"Bill not found."

        payload = {
            "id":bill.id,
            "customer_id":bill.customer_id,
            "cost_price":bill.cost_price,
            "unit":bill.unit,
            "stock": bill.stock
        }
        return True, payload
    except Exception as e:
        log.exception(f"Error occured while fetching bill with id -> {id} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def add_bill(data:dict = {}, db: Session=get_db(), is_commit = True):
    try:
        bill = Bills(customer_id=data.get("customer_id"),
                    sale_year=data.get("sale_year"),
                    sale_month=data.get("sale_month"),
                    sale_day=data.get("sale_day"),
                    product_qty=data.get("product_qty"),
                    paid_amount=data.get("paid_amount"),
                    discount_amount=data.get("discount_amount"),
                    discount_percentage=data.get("discount_percentage"),
                    vat=data.get("vat"),
                    tax=data.get("tax"),
                    extra_info=data.get("extra_info")
                    )
        db.add(bill)
        db.commit() if is_commit else db.flush()
        db.refresh(bill)
        return bill.id, "Bill added successfully!"
    except Exception as e:
        log.exception(f"Error occured while adding bill with data -> {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def update_bill(id: int, data: dict = {}, db: Session=get_db(), is_commit=True):
    try:
        if not id: return False, "Please provide valid id."

        bill = db.query(Bills).filter(Bills.id==id).first()
        if not bill:
            return False, "Product with given id does not exist."
        for key, value in data.items():
            setattr(bill, key, value)
    
        db.commit() if is_commit else db.flush()
        return id, "Bill updated successfully!"
    except IntegrityError as f:
        log.exception(f"ERROR: while updating bill with id {id}-> {f}")
        return False, f"Bill already exists with given bill id."
    except Exception as e:
        log.exception(f"ERROR: while adding or updating about app configuration -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def delete_bill(id=None, db: Session=get_db(), is_commit=True):
    try:
        if not id: return False, "Please provide valid id."

        db.query(Bills).filter(Bills.id==id).delete()
        db.commit() if is_commit else db.flush()
        return id, "Bill deleted successfully!"
    except Exception as e:
        log.exception(f"ERROR: while deleting about app configuration -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"