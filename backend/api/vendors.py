import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from backend.database.deps import get_db
from backend.models.vendors import Vendors


log = logging.getLogger("backend")


def get_vendors(queryDict: dict = {}, asc = True, sort_column: str = "id", 
                page=1, limit=11, db: Session = get_db()):
    try:
        table_columns = [column.name for column in inspect(Vendors).c]
        if (sort_column not in table_columns):
            db.close()
            return False,  {"message": f"Column '{sort_column}' does not exist in Vendors table.",
                            "data": []}
        
        for key in queryDict.keys():
            if key not in table_columns:
                db.close()
                return False,  {"message": f"Column '{key}' does not exist in Vendors table.",
                            "data": []}
                            
        toEval = ", ".join(f"Vendors.{key}.ilike('%{value}%')" for key, value in queryDict.items()) if queryDict else None
        query = db.query(Vendors).filter(eval(toEval)) if toEval else db.query(Vendors)
        
        total_vendors = query.count()
        if limit:
            skip = ((page-1)*limit)
            totalPages = math.ceil(total_vendors/limit)
        else:
            skip = 0
            totalPages = 1
        
        sort_query = eval(f"Vendors.{sort_column}") if asc else eval(f"Vendors.{sort_column}.desc()")
        vendors = query.order_by(sort_query)

        if not limit:
            vendors = query.all()
        else:
            vendors = query.offset(skip).limit(limit).all()
        
        def rowToDict(vendor):
            return {"id": vendor.id,
                    "vat_number":vendor.vat_number,
                    "vendor_name": vendor.vendor_name,
                    "address": vendor.address,
                    "phone_number":vendor.phone_number,
                    "telephone": vendor.telephone,
                    "email":vendor.email,
                    "extra_info": vendor.extra_info
                    }

        payload = {
            "message": "Success",
            "data": list(map(rowToDict, vendors)),
            "total_pages": totalPages if totalPages else 1,
            "current_page": page,
            "page_size": len(vendors)
        }
        db.close()
        log.info(f"FETCHED: Vendors with filter -> {queryDict}")
        return True, payload
    except Exception as e:
        db.close()
        log.error(f"Error occured while fetching vendors with queryDict: {queryDict} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def get_vendor(id: int = 0, vendor_name: str = "", vat_number: str = "", phone_number: str = "",
                email: str = "", telephone: str = "", db: Session = get_db()):
    try:
        if not id and not vendor_name and not vat_number and not phone_number and not email and not telephone:
            db.close()
            return False, f"Please provide one of the following.\nid/name/email/phone_number/telephone/company"
        vendor = db.query(Vendors)
        if id:
            vendor = vendor.filter(Vendors.id == id)
        if vendor_name:
            vendor = vendor.filter(Vendors.vendor_name == vendor_name)
        if vat_number:
            vendor = vendor.filter(Vendors.vat_number == vat_number)
        if phone_number:
            vendor = vendor.filter(Vendors.phone_number == phone_number)
        if telephone:
            vendor = vendor.filter(Vendors.telephone == telephone)
        if email:
            vendor = vendor.filter(Vendors.email == email)
        
        vendor = vendor.first()

        if not vendor: 
            db.close()
            return False, f"Vendor not found."

        payload = {"id": vendor.id,
                    "vat_number":vendor.vat_number,
                    "vendor_name": vendor.vendor_name,
                    "address": vendor.address,
                    "phone_number":vendor.phone_number,
                    "telephone": vendor.telephone,
                    "email":vendor.email,
                    "extra_info": vendor.extra_info
                    }
        db.close()
        return True, payload
    except Exception as e:
        db.close()
        log.error(f"Error occured while fetching vendor with id: {id} name: {vendor_name} phone number: {phone_number} email: {email} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def add_vendor(data:dict ={}, db: Session=get_db()):
    try:
        vendor = Vendors(vendor_name=data.get("vendor_name"), 
                        vat_number=data.get("vat_number"),
                        phone_number=data.get("phone_number"),
                        telephone=data.get("telephone"),
                        email=data.get("email"),
                        address=data.get("address"),
                        extra_info=data.get("extra_info"))
    
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        db.close()
        return vendor.id, "Vendor added successfully!"
    except IntegrityError as f:
        db.close()
        log.error(f"ERROR: while adding vendor with data {data} -> {f}")
        return False, "Vendor with same name/phone/telephone/email already exists."
    except Exception as e:
        db.close()
        log.error(f"ERROR: while adding vendor with data {data} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def update_vendor(id: int, data: dict = {}, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."

        vendor = db.query(Vendors).filter(Vendors.id==id).first()
        if not vendor: 
            db.close()
            return False, "Vendor with given id does not exist."
        for key, value in data.items():
            setattr(vendor, key, value)
    
        db.commit()
        db.close()
        return True, "Vendor updated successfully!"
    except IntegrityError as f:
        db.close()
        log.error(f"ERROR: while updating vendor with id {id}-> {f}")
        return False, f"Vendor already exists with provided name."
    except Exception as e:
        db.close()
        log.error(f"ERROR: while updating vendor with id {id}-> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"


def delete_vendor(id=None, db: Session=get_db()):
    try:
        if not id: return False, "Please provide valid id."
    
        db.query(Vendors).filter(Vendors.id==id).delete()
        db.commit()
        db.close()
        return id, "Vendor deleted successfully!"
    except Exception as e:
        db.close()
        log.error(f"ERROR: while deleting vendor with id {id} -> {e}")
        return False, "Something went wrong. Please check logs or contact the developer.\n\nThank you!"