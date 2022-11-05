"""Frame for inventory """ 
# built-in module imports
import logging
from tkinter import messagebox
from tkinter import *
from ttkwidgets.autocomplete import AutocompleteEntry
# frontend imports
import frontend.config as globals
from frontend.utils.frontend import makeColumnResponsive
from frontend.utils.products import refreshProductsList
import frontend.windows.updateProducts as updateProducts
import frontend.windows.addProducts as addProducts
# backend imports
from backend.api.products import delete_product, get_products


log = logging.getLogger("frontend")


def deleteProduct(id, name):
    response = messagebox.askyesnocancel("Delete the product", f"Are you sure?\n\nid: {id}\nProduct name: {name}")
    if response == 1:
        status, message = delete_product(id=id)
        if not status:
            messagebox.showerror("Delete Product", message)
        else:
            messagebox.showinfo("Delete Product",f"Product deleted successfully! \n id: {message}")
            # refreshing products list
            refreshProductsList()
            # reload the inventory table
            handleSearchProduct(globals.CURRENT_SEARCH_QUERY.get("products"))
            # refresh auto complete values in search entry
            globals.queryEntry.config(completevalues=[record["product_name"] for record in globals.PRODUCTS_LIST])


def handleSearchProduct(queryColumnDict, page=1, limit=11, sort_column="id", asc=True):
    globals.CURRENT_SEARCH_QUERY["customers"] = {}
    for column, query in queryColumnDict.items():
        globals.CURRENT_SEARCH_QUERY["products"][column] = query
    status, data = get_products(globals.CURRENT_SEARCH_QUERY["products"], page=page, limit=limit, sort_column=sort_column, asc=asc)
    
    if status:
        createInventoryTable(globals.inventoryFrame, data=data)
    else:
        Label(globals.inventoryFrame, text="Error occured while fetching products from database.").pack()
        Label(globals.inventoryFrame, text="Please check logs or contact the developer.").pack()
    return True


def createtableTop(parent):
    # For search bar and add item button
    globals.tableTop = Frame(parent)
    globals.tableTop.pack(fill="x", pady=20, padx=10)

    Label(globals.tableTop, text="Search product by").grid(row=0, column=0, sticky="w")

    globals.queryEntry = AutocompleteEntry(globals.tableTop,
                width=30, 
                font=20, 
                completevalues=[])
    globals.queryEntry.grid(row=0, column=2, ipady=5)
    globals.queryEntry.bind("<Return>", lambda x: proceedToSearch())

    def setCompleteValues():
        filterOptionsMap = {
            "Product name": "product_name"
        }
        if filterOptionsMap.get(filterOption.get()):
            column_name = filterOptionsMap.get(filterOption.get())
            completevalues = [record[column_name] if record[column_name] else "" for record in globals.PRODUCTS_LIST]
            globals.queryEntry.config(completevalues=completevalues)
    
    filterOption = StringVar()
    filterOption.set("Select a filter")
    filters = ["Product name"]

    filter = OptionMenu(globals.tableTop, filterOption, *filters, command=lambda x: setCompleteValues())
    filter.grid(row=0, column=1, padx=(2, 5), sticky="w")

    def proceedToSearch():
        filterOptionsMap = {
            "Product name": "product_name"
        }
        if globals.queryEntry.get():
            if filterOptionsMap.get(filterOption.get()):
                handleSearchProduct({filterOptionsMap.get(filterOption.get()):globals.queryEntry.get()})
            else:
                messagebox.showwarning("Inventory", "Please select a filter to search by.")

    searchButton = Button(globals.tableTop, 
                        text="Search", 
                        width=10, 
                        bg="#47B5FF",
                        command=proceedToSearch)
    searchButton.grid(row=0, column=3, padx=5)

    def clearSearch():
        filterOption.set("Select a filter")
        globals.queryEntry.delete(0, END)
        globals.queryEntry.insert(0, "")
        globals.CURRENT_SEARCH_QUERY["products"] = {}
        handleSearchProduct({})

    clearButton = Button(globals.tableTop, 
                        text="Clear", 
                        width=10, 
                        bg="#47B5FF",
                        command=clearSearch)
    clearButton.grid(row=0, column=4, padx=5, sticky="w")

    addItemButton = Button(globals.tableTop, 
                        text="Add New Product", 
                        width=20, 
                        bg=globals.appBlue, 
                        command=lambda: addProducts.createAddProductWindow())
    addItemButton.grid(row=0, column=5, padx=5, sticky="e")

    exportButton = Button(globals.tableTop, 
                        text="Export",
                        width=10, 
                        bg=globals.appBlue, 
                        command=lambda : messagebox.showinfo("Export Customers", "Feature comming soon in next update!\n\nYou will be able to export products to an excel file with the help of this feature.\n\nThank you!"))
    exportButton.grid(row=0, column=6, padx=5, sticky="e")
    
    Grid.columnconfigure(globals.tableTop, 4, weight=1)


def createTableHeader(parent):
    Label(parent, text="ID", font=globals.appFontNormalBold).grid(row=0, column=0, sticky=W)
    Label(parent, text="Product Name", font=globals.appFontNormalBold).grid(row=0, column=1, sticky=W)
    Label(parent, text="Stock", font=globals.appFontNormalBold).grid(row=0, column=2, sticky=W)
    Label(parent, text="Unit", font=globals.appFontNormalBold).grid(row=0, column=3, sticky=W)
    Label(parent, text="CP per unit", font=globals.appFontNormalBold).grid(row=0, column=4, sticky=W)
    Label(parent, text="MP per unit", font=globals.appFontNormalBold).grid(row=0, column=5, sticky=W)
    Label(parent, text="", font=globals.appFontNormalBold).grid(row=0, column=6, sticky=W)
    Label(parent, text="", font=globals.appFontNormalBold).grid(row=0, column=7, sticky=W)
    makeColumnResponsive(parent)


def createTableBody(parent, records):
    if not records:
        Label(parent, text="No records found!").grid(row=1, column=0, columnspan=8, pady=5)
        return True
    for index, record in enumerate(records):
        bg = "white" if (index+1)%2==0 else globals.appWhite
        Label(parent, text=record.get("id"), bg=bg, wraplength=160, justify="left").grid(row=index+1, column=0, pady=5, sticky=W)
        Label(parent, text=record.get("product_name"), bg=bg, wraplength=160, justify="left").grid(row=index+1, column=1,pady=5, sticky=W)
        Label(parent, text=record.get("stock"), bg=bg, wraplength=160, justify="left").grid(row=index+1, column=2, pady=5, sticky=W)
        Label(parent, text=record.get("unit"), bg=bg, wraplength=160, justify="left").grid(row=index+1, column=3, pady=5, sticky=W)
        Label(parent, text=record.get("cost_price"), bg=bg, wraplength=160, justify="left").grid(row=index+1, column=4, pady=5, sticky=W)
        Label(parent, text=record.get("marked_price"), bg=bg, wraplength=160, justify="left").grid(row=index+1, column=5, pady=5, sticky=W)
        Button(parent, text="update", width=10, bg="#47B5FF", command=lambda x=record: updateProducts.createUpdateProductWindow(x)).grid(row=index+1, column=6, pady=5)
        Button(parent, text="delete", width=10, bg="red", command=lambda id=record.get("id"), name=record.get("product_name"): deleteProduct(id, name)).grid(row=index+1, column=7, pady=5)

    makeColumnResponsive(parent)


def handlePaginationButtonState(currentPage, totalPages):
    backBtnState = DISABLED if currentPage==1 else NORMAL
    forwardBtnState = DISABLED if currentPage==totalPages else NORMAL
    globals.paginationBackButton.config(state=backBtnState)
    globals.paginationForwardButton.config(state=forwardBtnState)


def handlePagination(currentPage, totalPages, command):
    # print(currentPage, totalPages)
    handlePaginationButtonState(currentPage, totalPages)
    # print("Previous page: ", globals.PAGINATION_PAGE)
    if command=="back":
        globals.PAGINATION_PAGE -= 1
        # print("back button pressed")
    elif command=="forward":
        globals.PAGINATION_PAGE += 1
        # print("forward button pressed")

    handleSearchProduct(globals.CURRENT_SEARCH_QUERY["products"], page=globals.PAGINATION_PAGE, limit=globals.PAGINATION_PAGE_LIMIT)
    # print("Current page: ", globals.PAGINATION_PAGE)

    globals.paginationPageInfo.config(text=f"Page {globals.PAGINATION_PAGE} out of {totalPages}")
    


def createTableFooter(parent, currentPage, totalPages):
    # print(currentPage, totalPages)
    globals.PAGINATION_PAGE = currentPage
    globals.paginationBackButton = Button(parent, 
                                        text="<<", 
                                        bg=globals.appGreen, 
                                        fg=globals.appWhite,
                                        command=lambda : handlePagination(currentPage, totalPages, "back"))
    globals.paginationBackButton.grid(row=14, column=5, pady=10)

    globals.paginationPageInfo = Label(parent, text=f"Page {currentPage} out of {totalPages}")
    globals.paginationPageInfo.grid(row=globals.PAGINATION_PAGE_LIMIT+3, column=6, pady=10)
    
    globals.paginationForwardButton = Button(parent, 
                                            text=">>", 
                                            bg=globals.appGreen, 
                                            fg=globals.appWhite, 
                                            command=lambda : handlePagination(currentPage, totalPages, "forward"))
    globals.paginationForwardButton.grid(row=14, column=7, pady=10)

    handlePaginationButtonState(currentPage, totalPages)
    
    

def createInventoryTable(parent, data):
    globals.inventoryTable.destroy() if globals.inventoryTable else None
    globals.inventoryTable = Frame(parent)
    globals.inventoryTable.pack(fill="both", expand=True)

    createTableHeader(globals.inventoryTable)
    createTableBody(globals.inventoryTable, records=data["data"])
    createTableFooter(globals.inventoryTable, currentPage=data["current_page"], totalPages=data["total_pages"])


def createInventoryFrame(parent):
    globals.inventoryFrame = Frame(parent, borderwidth=1)
    globals.inventoryFrame.pack(fill="both", expand=True, padx=10)
    
    createtableTop(globals.inventoryFrame)
    handleSearchProduct({})

def openInventory(parent):
    try:
        createInventoryFrame(parent)
    except Exception as e:
        log.error(f"ERROR: while creating home frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")
    