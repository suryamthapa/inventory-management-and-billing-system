import logging
from datetime import date
import math
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.sales import Sales
from backend.models.products import Products


log = logging.getLogger("backend")


def add_sales(data:dict = {}, db: Session=get_db()):
    try:
        sale = Sales(product_id=data.get("product_id"),
                    bill_id=data.get("bill_id"),
                    quantity=data.get("quantity"),
                    selling_price=data.get("selling_price"),
                    discount_amount=data.get("discount_amount"),
                    discount_percentage=data.get("discount_percentage"),
                    vat=data.get("vat"),
                    tax=data.get("tax"))
    
        db.add(sale)
        db.commit()
        db.refresh(sale)
        db.close()
        return sale.id, "Sales added successfully!"
    except Exception as e:
        db.close()
        log.exception(f"ERROR: while adding sales with data {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_sales(queryDict: dict = {}, from_= None, to=None, asc = True, sort_column: str = "id", 
                page=1, limit=11, db: Session = get_db()):
    try:
        table_columns = [column.name for column in inspect(Sales).c]
        if sort_column not in table_columns:
            db.close()
            return False,  {"message": f"Column '{sort_column}' does not exist in Sales table.",
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns:
                db.close()
                return False,  {"message": f"Column '{key}' does not exist in Sales table.",
                            "data": []}

        toEval = ", ".join(f"Sales.{key} == '{value}'" for key, value in queryDict.items()) if queryDict else None
        query = db.query(Sales).filter(eval(toEval)) if toEval else db.query(Sales)
        
        total_sales = query.count()
        if limit:
            skip = ((page-1)*limit)
            totalPages = math.ceil(total_sales/limit)
        else:
            skip = 0
            totalPages = 1
        
        sort_query = eval(f"Sales.{sort_column}") if asc else eval(f"Sales.{sort_column}.desc()")
        query = query.order_by(sort_query)
        
        if from_ and to:
            query = query.filter(and_(func.date(Sales.created_at) >= from_), func.date(Sales.created_at) <= to)
        
        if limit:
            sales = query.offset(skip).limit(limit).all()
        else:
            sales = query.all()

        def rowToDict(sales):
            product = db.query(Products).filter(Products.id==sales.product_id).first()
            return {"id": sales.id,
                    "bill_id":sales.bill_id,
                    "product_name":product.product_name if product else "Deleted Product.",
                    "unit":product.unit if product else "---",
                    "quantity": sales.quantity,
                    "selling_price":sales.selling_price,
                    "discount_amount":sales.discount_amount,
                    "discount_percentage":sales.discount_percentage,
                    "vat":sales.vat,
                    "tax": sales.tax}

        payload = {
            "message": "Success",
            "data": list(map(rowToDict, sales)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(sales)}

        db.close()
        log.info("FETCHED: All sales.")
        return True, payload
    except Exception as e:
        db.close()
        log.exception(f"Error occured while fetching sales with queryDict: {queryDict} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"