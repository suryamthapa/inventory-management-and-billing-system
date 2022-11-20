from tkinter import *
from tkinter import messagebox
import frontend.config as Settings
from backend.api.customers import get_customers, update_customer, add_customer


def refreshCustomersList():
    status, data = get_customers(limit=None)
    if status:
        Settings.CUSTOMERS_LIST = data["data"]


def updateCustomer(id, data):
    status, message = update_customer(id=id, data=data)
    if not status:
        messagebox.showerror("Update Customer", message)
        return False
    else:
        messagebox.showinfo("Update Customer",message)
        return True


def saveCustomer(data):
    status, message = add_customer(data)
    if not status:
        messagebox.showerror("Add Customer", message)
        return False
    else:
        messagebox.showinfo("Add Customer",f"{message} \n id: {status}")
        return True