import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.accounts import Accounts
from backend.models.customers import Customers
from backend.models.bills import Bills
from backend.models import AccountType


log = logging.getLogger("backend")


def get_accounts(queryDict: dict = {}, asc = True, sort_column: str = "id", 
                page=1, limit=11, db: Session = get_db()):
    try:
        table_columns = [column.name for column in inspect(Accounts).c]
        if sort_column not in table_columns:
            db.close()
            return False,  {"message": f"Column '{sort_column}' does not exist in Accounts table.",
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns:
                db.close()
                return False,  {"message": f"Column '{key}' does not exist in Accounts table.",
                            "data": []}

        toEval = ", ".join(f"Accounts.{key} == '{value}'" for key, value in queryDict.items()) if queryDict else None
        query = db.query(Accounts).filter(eval(toEval)) if toEval else db.query(Accounts)
        
        total_products = query.count()
        skip = ((page-1)*limit)
        totalPages = math.ceil(total_products/limit)
        
        sort_query = eval(f"Accounts.{sort_column}") if asc else eval(f"Accounts.{sort_column}.desc()")
        accounts = query.order_by(sort_query).offset(skip).limit(limit).all()
        
        def rowToDict(account):
            customer = db.query(Customers).filter(Customers.id==account.customer_id).first()
            if customer:
                customer_name = customer.full_name if customer.full_name else customer.company
                customer_id = customer.id
                company_pan_no = customer.company_pan_no
            else:
                customer_name = "Deleted Customer"
                customer_id = "N/A"
                company_pan_no = "N/A"
            return {"id":account.id,
                    "date":account.created_at,
                    "customer_id":customer_id,
                    "customer_name":customer_name,
                    "customer_company_pan_no":company_pan_no,
                    "bill_id":account.bill_id,
                    "type": "CR" if account.type==AccountType.credit else "DR",
                    "description":account.description,
                    "amount": account.amount}

        payload = {
            "message": "Success",
            "data": list(map(rowToDict, accounts)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(accounts)
        }
        db.close()
        log.info(f"FETCHED: Accounts with filter -> {queryDict}")
        return True, payload
    except Exception as e:
        db.close()
        log.error(f"Error occured while fetching Accounts with queryDict: {queryDict} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_account(id: int = 0, db: Session = get_db()):
    try:
        if not id:
            db.close()
            return False, f"Please provide account id."

        account = db.query(Accounts).filter(Accounts.id==id).first()
        if not account:
            db.close()
            return False, f"Account not found."
        
        customer = db.query(Customers).filter(Customers.id==account.id).first()
        if customer:
            customer_name = customer.full_name if customer.full_name else customer.company
        else:
            customer_name = "Deleted Customer"

        payload = {
            "id":account.id,
            "customer_name":customer_name,
            "bill_id":account.bill_id,
            "type": "CR" if account.type==AccountType.credit else "DR",
            "description":account.description,
            "amount": account.amount
        }
        db.close()
        return True, payload
    except Exception as e:
        db.close()
        log.error(f"Error occured while fetching account with id -> {id} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def add_account(data:dict = {}, db: Session=get_db()):
    try:
        account = Accounts(customer_id=data.get("customer_id"), 
                    bill_id=data.get("bill_id"),
                    type=data.get("type"),
                    description=data.get("description"),
                    amount=data.get("amount"))
        db.add(account)
        db.commit()
        db.refresh(account)
        db.close()
        return account.id, "Account added successfully!"
    except Exception as e:
        db.close()
        log.error(f"Error occured while adding account with data -> {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def update_account(id: int, data: dict = {}, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."

        account = db.query(Accounts).filter(Accounts.id==id).first()
        if not account:
            db.close()
            return False, "Account with given id does not exist."
        for key, value in data.items():
            setattr(account, key, value)
    
        db.commit()
        db.close()
        return True, "Account updated successfully!"
    except Exception as e:
        db.close()
        log.error(f"ERROR: while adding or updating account -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def delete_account(id=None, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."

        db.query(Accounts).filter(Accounts.id==id).delete()
        db.commit()
        db.close()
        return id, "Account deleted successfully!"
    except Exception as e:
        db.close()
        log.error(f"ERROR: while deleting account with id -> {id} and configuration -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"