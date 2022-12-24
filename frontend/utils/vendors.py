from tkinter import *
from tkinter import messagebox
import frontend.config as Settings
from backend.api.vendors import get_vendors, update_vendor, add_vendor


def refreshVendorsList():
    status, data = get_vendors(limit=None)
    if status:
        Settings.VENDORS_LIST = data["data"]


def updateVendor(id, data):
    status, message = update_vendor(id=id, data=data)
    if not status:
        messagebox.showerror("Update Vendor", message)
        return False
    else:
        messagebox.showinfo("Update Vendor",message)
        return True


def saveVendor(data):
    status, message = add_vendor(data)
    if not status:
        messagebox.showerror("Add Vendor", message)
        return False
    else:
        messagebox.showinfo("Add Vendor",f"{message} \n id: {status}")
        return True