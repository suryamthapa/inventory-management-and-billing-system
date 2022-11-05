import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.customers import Customers


log = logging.getLogger("backend")


def get_customers(queryDict: dict = {}, asc = True, sort_column: str = "id", 
                page=1, limit=11, db: Session = get_db()):
    try:
        table_columns = [column.name for column in inspect(Customers).c]
        if (sort_column not in table_columns):
            db.close()
            return False,  {"message": f"Column '{sort_column}' does not exist in Customers table.",
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns:
                db.close()
                return False,  {"message": f"Column '{key}' does not exist in Customers table.",
                            "data": []}
                            
        toEval = ", ".join(f"Customers.{key}.ilike('%{value}%')" for key, value in queryDict.items()) if queryDict else None
        query = db.query(Customers).filter(eval(toEval)) if toEval else db.query(Customers)
        
        total_products = query.count()
        skip = ((page-1)*limit)
        totalPages = math.ceil(total_products/limit)
        
        sort_query = eval(f"Customers.{sort_column}") if asc else eval(f"Customers.{sort_column}.desc()")
        customers = query.order_by(sort_query).offset(skip).limit(limit).all()
        
        def rowToDict(customer):
            return {"id": customer.id,
                    "full_name":customer.full_name,
                    "company": customer.company,
                    "company_pan_no": customer.company_pan_no,
                    "phone_number":customer.phone_number,
                    "telephone": customer.telephone,
                    "email":customer.email,
                    "address": customer.address}

        payload = {
            "message": "Success",
            "data": list(map(rowToDict, customers)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(customers)
        }
        db.close()
        log.info(f"FETCHED: Customers with filter -> {queryDict}")
        return True, payload
    except Exception as e:
        db.close()
        log.error(f"Error occured while fetching customers with queryDict: {queryDict} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_customer(id: int = 0, full_name: str = "", company: str = "", phone_number: str = "",
                email: str = "", telephone: str = "", db: Session = get_db()):
    try:
        if not id and not full_name and not company and not phone_number and not email and not telephone:
            db.close()
            return False, f"Please provide one of the following.\nid/name/email/phone_number/telephone/company"
        customer = db.query(Customers)
        if id:
            customer = customer.filter(Customers.id == id)
        if full_name:
            customer = customer.filter(Customers.full_name == full_name)
        if company:
            customer = customer.filter(Customers.company == company)
        if phone_number:
            customer = customer.filter(Customers.phone_number == phone_number)
        if telephone:
            customer = customer.filter(Customers.telephone == telephone)
        if email:
            customer = customer.filter(Customers.email == email)
        
        customer = customer.first()

        if not customer: 
            db.close()
            return False, f"Customer not found."

        payload = {
            "id":customer.id,
            "full_name":customer.full_name,
            "company": customer.company,
            "company_pan_no": customer.company_pan_no,
            "phone_number":customer.phone_number,
            "telephone": customer.telephone,
            "email":customer.email,
            "address": customer.address
        }
        db.close()
        return True, payload
    except Exception as e:
        db.close()
        log.error(f"Error occured while fetching customer with id: {id} name: {name} phone number: {phone_number} email: {email} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def add_customer(data:dict ={}, db: Session=get_db()):
    try:
        customer = Customers(full_name=data.get("full_name"), 
                        phone_number=data.get("phone_number") if data.get("phone_number") else None,
                        telephone=data.get("telephone") if data.get("telephone") else None,
                        company=data.get("company") if data.get("company") else None,
                        company_pan_no=data.get("company_pan_no") if data.get("company_pan_no") else None,
                        email=data.get("email") if data.get("email") else None,
                        address=data.get("address"))
    
        db.add(customer)
        db.commit()
        db.refresh(customer)
        db.close()
        return customer.id, "Customer added successfully!"
    except IntegrityError as f:
        db.close()
        log.error(f"ERROR: while adding customer with data {data} -> {f}")
        return False, "Customer with same name/phone/telephone/email already exists."
    except Exception as e:
        db.close()
        log.error(f"ERROR: while adding customer with data {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def update_customer(id: int, data: dict = {}, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."

        customer = db.query(Customers).filter(Customers.id==id).first()
        if not customer: 
            db.close()
            return False, "Customer with given id does not exist."
        for key, value in data.items():
            setattr(customer, key, value)
    
        db.commit()
        db.close()
        return True, "Customer updated successfully!"
    except IntegrityError as f:
        db.close()
        log.error(f"ERROR: while updating customer with id {id}-> {f}")
        return False, f"Customer already exists with provided name."
    except Exception as e:
        db.close()
        log.error(f"ERROR: while updating customer with id {id}-> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def delete_customer(id=None, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."
    
        db.query(Customers).filter(Customers.id==id).delete()
        db.commit()
        db.close()
        return id, "Customer deleted successfully!"
    except Exception as e:
        db.close()
        log.error(f"ERROR: while deleting customer with id {id} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"