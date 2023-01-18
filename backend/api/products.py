import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.products import Products


log = logging.getLogger("backend")


def get_products(queryDict: dict = {}, asc = True, sort_column: str = "id", 
                page=1, limit=11, db: Session = get_db()):
    try:
        table_columns = [column.name for column in inspect(Products).c]
        if sort_column not in table_columns:
            return False,  {"message": f"Column '{sort_column}' does not exist in Products table.",
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns:
                return False,  {"message": f"Column '{key}' does not exist in Products table.",
                            "data": []}

        toEval = ", ".join(f"Products.{key}.ilike('%{value}%')" for key, value in queryDict.items()) if queryDict else None
        query = db.query(Products).filter(eval(toEval)) if toEval else db.query(Products)
        
        total_products = query.count()
        if limit:
            skip = ((page-1)*limit)
            totalPages = math.ceil(total_products/limit)
        else:
            skip = 0
            totalPages = 1
        
        sort_query = eval(f"Products.{sort_column}") if asc else eval(f"Products.{sort_column}.desc()")
        products = query.order_by(sort_query)

        if not limit:
            products = query.all()
        else:
            products = query.offset(skip).limit(limit).all()
        
        def rowToDict(product):
            return {"id": product.id,
                    "product_name":product.product_name,
                    "cost_price":product.cost_price,
                    "unit":product.unit,
                    "stock": product.stock}

        payload = {
            "message": "Success",
            "data": list(map(rowToDict, products)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(products)
        }
        log.info(f"FETCHED: Products with filter -> {queryDict}")
        return True, payload
    except Exception as e:
        log.exception(f"Error occured while fetching products with queryDict: {queryDict} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_product(id: int = 0, name: str = "", db: Session = get_db()):
    try:
        if not id and not name:
            return False, f"Please provide name or id."

        product = db.query(Products)
        
        if name:
            product = product.filter(Products.product_name == name)
        elif id:
            product = product.filter(Products.id==id)
        
        product = product.first()
        
        if not product:
            return False, f"Product not found."

        payload = {
            "id":product.id,
            "product_name":product.product_name,
            "cost_price":product.cost_price,
            "unit":product.unit,
            "stock": product.stock
        }
        return True, payload
    except Exception as e:
        log.exception(f"Error occured while fetching product with id: {id} name: {name} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def add_product(data:dict = {}, db: Session=get_db(), is_commit=True):
    try:
        product = Products(product_name=data.get("product_name"), 
                        cost_price=data.get("cost_price"),
                        unit=data.get("unit"),
                        stock=data.get("stock"))
    
        db.add(product)
        db.commit() if is_commit else db.flush()
        db.refresh(product)
        return product.id, "Product added successfully!"
    except IntegrityError:
        return False, "Product with same name already exists."
    except Exception as e:
        log.exception(f"ERROR: while adding product with data {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def update_product(id: int, data: dict = {}, db: Session=get_db(), is_commit=True):
    try:
        if not id: return False, "Please provide valid id."

        product = db.query(Products).filter(Products.id==id).first()
        if not product: 
            return False, "Product with given id does not exist."
        for key, value in data.items():
            setattr(product, key, value)
    
        db.commit() if is_commit else db.flush()
        return id, "Product updated successfully!"
    except IntegrityError:
        return False, "Product already exists with provided name."
    except Exception as e:
        log.exception(f"ERROR: while updating product with id {id}-> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def delete_product(id=None, db: Session=get_db(), is_commit=True):
    try:
        if not id: return False, "Please provide valid id."

        db.query(Products).filter(Products.id==id).delete()
        db.commit() if is_commit else db.flush()
        return id, "Product deleted successfully!"
    except Exception as e:
        log.exception(f"ERROR: while deleting product with id {id} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"