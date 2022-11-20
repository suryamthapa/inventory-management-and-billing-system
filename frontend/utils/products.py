from tkinter import *
from tkinter import messagebox
import frontend.config as Settings
from backend.api.products import get_products, update_product, add_product


def refreshProductsList():
    status, data = get_products(limit=None)
    if status:
        Settings.PRODUCTS_LIST = data["data"]


def updateProduct(id, data):
    status, message = update_product(id=id, data=data)
    if not status:
        messagebox.showerror("Update Product", message)
        return False
    else:
        messagebox.showinfo("Update Product",f"{message}")
        return True


def saveProduct(data):
        status, message = add_product(data)
        if not status:
            messagebox.showerror("Add Product", message)
            return False
        else:
            messagebox.showinfo("Add Product",f"{message} \n id: {status}")
            return True