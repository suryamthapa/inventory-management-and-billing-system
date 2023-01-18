import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.accounts import Accounts
from backend.models.customers import Customers
from backend.models.bills import Bills
from backend.models import AccountType


log = logging.getLogger("backend")


def get_accounts(queryDict: dict = {}, from_= None, to=None, asc = True, sort_column: str = "id", 
                page=1, limit=11, db: Session = get_db()):
    try:
        table_columns = [column.name for column in inspect(Accounts).c] + ["transaction_date"]
        if sort_column not in table_columns:
            db.close()
            message = f"Column '{sort_column}' provided for sorting, does not exist in Accounts table."
            log.error(f"Sort {message}")
            return False,  {"message": message,
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns:
                db.close()
                message = f"Column '{key}' provided for query, does not exist in Accounts table."
                log.error(f"In querydict {queryDict} : {message}")
                return False,  {"message": message,
                            "data": []}

        toEval = ", ".join(f"Accounts.{key} == int('{value}')" for key, value in queryDict.items()) if queryDict else None
        query = db.query(Accounts).filter(eval(toEval)) if toEval else db.query(Accounts)
        
        total_products = query.count()
        if limit:
            skip = ((page-1)*limit)
            totalPages = math.ceil(total_products/limit)
        else:
            skip = 0
            totalPages = 1

        if sort_column and sort_column in table_columns:
            if sort_column == "transaction_date":
                query = query.order_by(Accounts.transaction_year, Accounts.transaction_month, Accounts.transaction_day) if asc else query.order_by(Accounts.transaction_year.desc(), Accounts.transaction_month.desc(), Accounts.transaction_day.desc())
            else:
                sort_query = eval(f"Accounts.{sort_column}") if asc else eval(f"Accounts.{sort_column}.desc()")
                query = query.order_by(sort_query)

        if from_ is not None and to is not None:
            from_meta = from_.split("/")
            from_year = int(from_meta[2])
            from_month = int(from_meta[1])
            from_day = int(from_meta[0])
            query = query.filter(and_(Accounts.transaction_year >= from_year, Accounts.transaction_month >= from_month, Accounts.transaction_day >= from_day))
        
            to_meta = to.split("/")
            to_year = int(to_meta[2])
            to_month = int(to_meta[1])
            to_day = int(to_meta[0])
            query = query.filter(and_(Accounts.transaction_year <= to_year, Accounts.transaction_month <= to_month, Accounts.transaction_day <= to_day))

        if not limit:
            accounts = query.all()
        else:
            accounts = query.offset(skip).limit(limit).all()
        def rowToDict(account):
            if not queryDict.get("customer_id"):
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
                        "transaction_year":account.transaction_year,
                        "transaction_month":account.transaction_month,
                        "transaction_day":account.transaction_day,
                        "customer_id":customer_id,
                        "customer_name":customer_name,
                        "customer_company_pan_no":company_pan_no,
                        "bill_id":account.bill_id,
                        "type": "credit" if account.type==AccountType.credit else "debit",
                        "description":account.description,
                        "amount": account.amount}
            else:
                return {"id":account.id,
                        "transaction_year":account.transaction_year,
                        "transaction_month":account.transaction_month,
                        "transaction_day":account.transaction_day,
                        "bill_id":account.bill_id,
                        "type": "credit" if account.type==AccountType.credit else "debit",
                        "description":account.description,
                        "amount": account.amount}
        payload = {
            "message": "Success",
            "data": list(map(rowToDict, accounts)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(accounts)
        }
        log.info(f"FETCHED: Accounts with filter -> {queryDict}")
        return True, payload
    except Exception as e:
        log.exception(f"Error occured while fetching Accounts with queryDict: {queryDict} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_account(id: int = 0, db: Session = get_db()):
    try:
        if not id:
            return False, f"Please provide account id."

        account = db.query(Accounts).filter(Accounts.id==id).first()
        if not account:
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
        return True, payload
    except Exception as e:
        log.exception(f"Error occured while fetching account with id -> {id} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def add_account(data:dict = {}, db: Session=get_db(), is_commit=True):
    try:
        account = Accounts(customer_id=data.get("customer_id"), 
                    transaction_year=data.get("transaction_year"),
                    transaction_month=data.get("transaction_month"),
                    transaction_day=data.get("transaction_day"),
                    bill_id=data.get("bill_id"),
                    type=data.get("type"),
                    description=data.get("description"),
                    amount=data.get("amount"))
        db.add(account)
        db.commit() if is_commit else db.flush()
        db.refresh(account)
        return account.id, "Account added successfully!"
    except Exception as e:
        log.exception(f"Error occured while adding account with data -> {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def update_account(id: int, data: dict = {}, db: Session=get_db(), is_commit=True):
    try:
        if not id: return False, "Please provide valid id."

        account = db.query(Accounts).filter(Accounts.id==id).first()
        if not account:
            return False, "Account with given id does not exist."
        for key, value in data.items():
            setattr(account, key, value)
    
        db.commit() if is_commit else db.flush()
        return id, "Account updated successfully!"
    except Exception as e:
        log.exception(f"ERROR: while adding or updating account -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def delete_account(id=None, db: Session=get_db(), is_commit=True):
    try:
        if not id: return False, "Please provide valid id."

        db.query(Accounts).filter(Accounts.id==id).delete()
        db.commit() if is_commit else db.flush()
        return id, "Account deleted successfully!"
    except Exception as e:
        log.exception(f"ERROR: while deleting account with id -> {id} and configuration -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"