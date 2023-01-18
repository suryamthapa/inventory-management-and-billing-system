# Window to add products in inventory.

import threading
import logging
from tkinter import *
from tkinter import messagebox
from ttkwidgets.autocomplete import AutocompleteEntry
import frontend.config as globals
import frontend.frames.inventory as inventory
import frontend.frames.billing as billingFrame
import frontend.frames.purchaseEntry as purchaseEntryFrame
from frontend.utils.products import saveProduct, refreshProductsList


log = logging.getLogger("frontend")


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def createAddProductWindow():
    try:
        addProductWindow = Toplevel()
        addProductWindow.grab_set()
        addProductWindow.title("Add new product")
        addProductWindow.resizable(0,0)
        addProductWindow.iconbitmap("./frontend/assets/images/favicon.ico")

        addProductFrame = LabelFrame(addProductWindow, text="Product Details", borderwidth=1)
        addProductFrame.pack(fill="both", padx=10, pady=10, expand=True)

        Label(addProductFrame, text="Product Name", justify="left").grid(row=0, column=0, padx=5, pady=5)
        productNameEntry = Entry(addProductFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        productNameEntry.grid(row=0, column=1, padx=5, pady=5)

        Label(addProductFrame, text="Unit").grid(row=0, column=2, padx=5, pady=5)
        unitEntry = AutocompleteEntry(addProductFrame, font=globals.appFontNormal,
                completevalues=set([record["unit"] if record["unit"] else "" for record in globals.PRODUCTS_LIST]+globals.UNITS_LIST))
        unitEntry.grid(row=0, column=3, padx=5, pady=5)

        Label(addProductFrame, text="Stock").grid(row=1, column=0, padx=5, pady=5)
        stockEntry = Entry(addProductFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        stockEntry.grid(row=1, column=1, padx=5, pady=5)

        Label(addProductFrame, text="Cost Price").grid(row=1, column=2, padx=5, pady=5)
        costPriceEntry = Entry(addProductFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        costPriceEntry.grid(row=1, column=3, padx=5, pady=5)

        def validateProduct(quitWindow=False):
            if not productNameEntry.get():
                productNameEntry.focus()
                return False
            elif not unitEntry.get():
                unitEntry.focus()
                return False

            if costPriceEntry.get() and not isfloat(costPriceEntry.get()):
                messagebox.showwarning("Invalid", "Cost price should contain numbers only.")
                costPriceEntry.focus()
                return False
            if stockEntry.get() and not isfloat(stockEntry.get()):
                stockEntry.focus()
                messagebox.showwarning("Invalid", "Stock should contain numbers only.")
                return False
            
            data = {"product_name": productNameEntry.get().upper(),
                    "cost_price":costPriceEntry.get() if costPriceEntry.get() else 0,
                    "unit":unitEntry.get().upper(),
                    "stock":stockEntry.get() if stockEntry.get() else 0}
            status = saveProduct(data)

            if status:
                # refreshing products list
                refreshProductsList()
                if globals.CURRENT_FRAME=="inventoryFrame":
                    # refresh auto complete values in search entry
                    field = globals.productsFilterOptionsMap.get(globals.filterOption.get())
                    globals.queryEntry.config(completevalues=[record[field] if record.get(field) else "" for record in globals.PRODUCTS_LIST])
                    # reload the inventory table
                    inventory.handleSearchProduct(globals.CURRENT_SEARCH_QUERY.get("products"))
                if globals.CURRENT_FRAME=="billingSystemFrame":
                    # refresh auto complete values in product search entry in billing frame
                    globals.billingProductNameEntry.config(completevalues=[record["product_name"] if record.get("product_name") else "" for record in globals.PRODUCTS_LIST])
                    globals.billingProductNameEntry.delete(0, END)
                    globals.billingProductNameEntry.insert(0, data["product_name"])
                    data["id"] = status
                    billingFrame.loadProductDetails(globals.rateQtyFrame, data)
                if globals.CURRENT_FRAME=="purchaseEntrySystemFrame":
                    # refresh auto complete values in product search entry in billing frame
                    globals.purchaseProductNameEntry.config(completevalues=[record["product_name"] if record.get("product_name") else "" for record in globals.PRODUCTS_LIST])
                    globals.purchaseProductNameEntry.delete(0, END)
                    globals.purchaseProductNameEntry.insert(0, data["product_name"])
                    data["id"] = status
                    purchaseEntryFrame.loadProductDetails(globals.rateQtyFrame, data)
            else:
                return False
                
            if quitWindow:
                addProductWindow.destroy()
                return True
            return True

        Button(addProductWindow,
            text="Save and quit",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : validateProduct(quitWindow=True),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)
        
        if globals.CURRENT_FRAME == "inventoryFrame":
            Button(addProductWindow,
                text="Save",
                bg=globals.appBlue,
                fg=globals.appDarkGreen,
                command=validateProduct,
                width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        # bring to the center of screen
        addProductWindow.update()
        x = int((globals.screen_width/2) - (addProductWindow.winfo_width()/2))
        y = int((globals.screen_height/2) - (addProductWindow.winfo_height()/2))
        addProductWindow.geometry(f'{addProductWindow.winfo_width()}x{addProductWindow.winfo_height()}+{x}+{y}')
    except Exception as e:
        log.exception(f"ERROR: while creating Add Products window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")