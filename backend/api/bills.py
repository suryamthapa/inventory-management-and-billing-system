import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.bills import Bills


log = logging.getLogger("backend")


def get_bills(queryDict: dict = {}, asc = True, sort_column: str = "id", 
                page=1, limit=11, db: Session = get_db()):
    try:
        table_columns = [column.name for column in inspect(Bills).c]
        if sort_column not in table_columns:
            db.close()
            return False,  {"message": f"Column '{sort_column}' does not exist in Bills table.",
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns:
                db.close()
                return False,  {"message": f"Column '{key}' does not exist in Bills table.",
                            "data": []}

        toEval = ", ".join(f"Bills.{key} == '{value}'" for key, value in queryDict.items()) if queryDict else None
        query = db.query(Bills).filter(eval(toEval)) if toEval else db.query(Bills)
        
        total_products = query.count()
        skip = ((page-1)*limit)
        totalPages = math.ceil(total_products/limit)
        
        sort_query = eval(f"Bills.{sort_column}") if asc else eval(f"Bills.{sort_column}.desc()")
        products = query.order_by(sort_query).offset(skip).limit(limit).all()
        
        def rowToDict(product):
            return {"id": product.id,
                    "product_name":product.product_name,
                    "cost_price":product.cost_price,
                    "marked_price": product.marked_price,
                    "unit":product.unit,
                    "stock": product.stock}

        payload = {
            "message": "Success",
            "data": list(map(rowToDict, products)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(products)
        }
        db.close()
        log.info("FETCHED: All products.")
        return True, payload
    except Exception as e:
        db.close()
        log.exception(f"Error occured while fetching bills with queryDict: {queryDict} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_bill(id: int = 0, db: Session = get_db()):
    try:
        if not id:
            db.close()
            return False, f"Please provide bill id."

        bill = db.query(Bills).filter(Bills.id==id).first()
        if not bill:
            db.close()
            return False, f"Bill not found."

        payload = {
            "id":bill.id,
            "customer_id":bill.customer_id,
            "cost_price":bill.cost_price,
            "marked_price": bill.marked_price,
            "unit":bill.unit,
            "stock": bill.stock
        }
        db.close()
        return True, payload
    except Exception as e:
        db.close()
        log.exception(f"Error occured while fetching bill with id -> {id} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def add_bill(data:dict = {}, db: Session=get_db()):
    try:
        bill = Bills(customer_id=data.get("customer_id"), 
                    paid_amount=data.get("paid_amount"),
                    discount_amount=data.get("discount_amount"),
                    discount_percentage=data.get("discount_percentage"),
                    vat=data.get("vat"),
                    tax=data.get("tax"))
        db.add(bill)
        db.commit()
        db.refresh(bill)
        db.close()
        return bill.id, "Bill added successfully!"
    except Exception as e:
        db.close()
        log.exception(f"Error occured while adding bill with data -> {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def update_bill(id: int, data: dict = {}, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."

        bill = db.query(Bills).filter(Bills.id==id).first()
        if not bill:
            db.close()
            return False, "Product with given id does not exist."
        for key, value in data.items():
            setattr(bill, key, value)
    
        db.commit()
        db.close()
        return True, "Bill updated successfully!"
    except Exception as e:
        db.close()
        log.exception(f"ERROR: while adding or updating about app configuration -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def delete_bill(id=None, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."

        db.query(Bills).filter(Bills.id==id).delete()
        db.commit()
        db.close()
        return id, "Bill deleted successfully!"
    except Exception as e:
        db.close()
        log.exception(f"ERROR: while deleting about app configuration -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"