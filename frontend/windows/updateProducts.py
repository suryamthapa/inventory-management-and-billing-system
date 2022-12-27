# Window to add products in inventory.
# inbuilt module imports
import logging
from tkinter import *
from tkinter import messagebox
from ttkwidgets.autocomplete import AutocompleteEntry
# frontend imports
import frontend.config as globals
import frontend.frames.inventory as inventory
import frontend.frames.billing as billingFrame
import frontend.windows.dashboard as dashboard
from frontend.utils.products import updateProduct, refreshProductsList


log = logging.getLogger("frontend")


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False
        

def createUpdateProductWindow(productInfo):
    try:
        updateProductWindow = Toplevel()
        updateProductWindow.grab_set()
        updateProductWindow.title("Update product")
        updateProductWindow.resizable(0,0)
        updateProductWindow.iconbitmap("./frontend/assets/images/favicon.ico")

        product_id = productInfo["id"] if productInfo else ""
        product_name = productInfo["product_name"] if productInfo else ""
        cost_price = productInfo["cost_price"] if productInfo else ""
        marked_price = productInfo["marked_price"] if productInfo else ""
        unit = productInfo["unit"] if productInfo else ""
        stock = productInfo["stock"] if productInfo else ""

        updateProductFrame = LabelFrame(updateProductWindow, text="Product Details", borderwidth=1)
        updateProductFrame.pack(fill="both", padx=10, pady=10, expand=True)

        Label(updateProductFrame, text="Product Name", justify="left").grid(row=0, column=0, padx=5, pady=5)
        productNameEntry = Entry(updateProductFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        productNameEntry.grid(row=0, column=1, padx=5, pady=5)
        productNameEntry.insert(0, product_name)
        
        Label(updateProductFrame, text="Unit").grid(row=1, column=0, padx=5, pady=5)
        unitEntry = AutocompleteEntry(updateProductFrame, font=globals.appFontNormal,
                completevalues=set([record["unit"] if record["unit"] else "" for record in globals.PRODUCTS_LIST]+globals.UNITS_LIST))
        unitEntry.grid(row=1, column=1, padx=5, pady=5)
        unitEntry.insert(0, unit)

        Label(updateProductFrame, text="Stock").grid(row=1, column=2, padx=5, pady=5)
        stockEntry = Entry(updateProductFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        stockEntry.grid(row=1, column=3, padx=5, pady=5)
        stockEntry.insert(0, stock)

        Label(updateProductFrame, text="Cost Price").grid(row=2, column=0, padx=5, pady=5)
        costPriceEntry = Entry(updateProductFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        costPriceEntry.grid(row=2, column=1, padx=5, pady=5)
        costPriceEntry.insert(0, cost_price)

        Label(updateProductFrame, text="Marked Price").grid(row=2, column=2, padx=5, pady=5)
        markedPriceEntry = Entry(updateProductFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        markedPriceEntry.grid(row=2, column=3, padx=5, pady=5)
        markedPriceEntry.insert(0, marked_price)
        
        def handleUpdate(id):
            if not productNameEntry.get():
                productNameEntry.focus()
                return False
            elif  not costPriceEntry.get():
                costPriceEntry.focus()
                return False
            elif not markedPriceEntry.get():
                markedPriceEntry.focus()
                return False
            elif not unitEntry.get():
                unitEntry.focus()
                return False
            elif not stockEntry.get():
                stockEntry.focus()
                return False

            if not isfloat(markedPriceEntry.get()):
                messagebox.showwarning("Invalid", "Marked price should contain numbers only.")
                markedPriceEntry.focus()
                return False
            if not isfloat(costPriceEntry.get()):
                messagebox.showwarning("Invalid", "Cost price should contain numbers only.")
                costPriceEntry.focus()
                return False
            if not stockEntry.get().isdigit():
                stockEntry.focus()
                messagebox.showwarning("Invalid", "Stock should contain numbers only.")
                return False
            
            details = {
                "product_name":productNameEntry.get(),
                "cost_price":costPriceEntry.get(),
                "marked_price":markedPriceEntry.get(),
                "unit":unitEntry.get().upper() if unitEntry.get() else unitEntry.get(),
                "stock":stockEntry.get()
            }
            status = updateProduct(id, details)
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
                    globals.billingProductNameEntry.insert(0, details["product_name"])
                    details["id"] = status
                    billingFrame.loadProductDetails(globals.rateQtyFrame, details)
                if globals.CURRENT_FRAME=="homeFrame":
                    # refresh home frame
                    dashboard.showFrame(globals.CURRENT_FRAME, refreshMode=True)
            updateProductWindow.destroy()

        Button(updateProductWindow,
            text="Cancel",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : updateProductWindow.destroy(),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        Button(updateProductWindow,
            text="Update",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : handleUpdate(product_id),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)
        
        updateProductWindow.update()
        # bring to the center of screen
        x = int((globals.screen_width/2) - (updateProductWindow.winfo_width()/2))
        y = int((globals.screen_height/2) - (updateProductWindow.winfo_height()/2))
        updateProductWindow.geometry(f'{updateProductWindow.winfo_width()}x{updateProductWindow.winfo_height()}+{x}+{y}')
    
    except Exception as e:
        log.exception(f"ERROR: while creating Update Products window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")