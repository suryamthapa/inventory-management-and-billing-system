"""Frame for purchase""" 
# built-in module imports
import logging
from tkinter import messagebox
from tkinter import *
from ttkwidgets.autocomplete import AutocompleteEntry
# frontend imports
import frontend.config as globals
from frontend.utils.frontend import makeColumnResponsive
from frontend.utils.purchase import refreshPurchasesList
import frontend.windows.dashboard as dashboard
# backend imports
from backend.api.purchase import delete_purchase, get_purchase


log = logging.getLogger("frontend")


def deletePurchase(id, vendor_name, invoice_number):
    response = messagebox.askyesnocancel("Delete the purchase", f"Are you sure?\n\nid: {id}\nInvoice number: #{invoice_number}\nVendor Name: {vendor_name}")
    if response == 1:
        status, message = delete_purchase(id=id)
        if not status:
            messagebox.showerror("Delete Purchase", message)
        else:
            messagebox.showinfo("Delete Purchase",f"{message}")
            # refreshing products list
            refreshPurchasesList()
            # reload the inventory table
            handleSearchPurchase(globals.CURRENT_SEARCH_QUERY.get("purchases"))
            # refresh auto complete values in search entry
            if globals.purchaseFilterOptionsMap.get(globals.filterOption.get()):
                column_name = globals.purchaseFilterOptionsMap.get(globals.filterOption.get())
                completevalues = []
                if column_name in ["vendor_name", "vat_number", "email", "telephone", "phone_number"]:
                    completevalues = [str(record["vendor"].get(column_name)) if record.get("vendor").get(column_name) else "" for record in globals.PURCHASE_LIST]
                else:
                    completevalues = [str(record[column_name]) if record.get(column_name) else "" for record in globals.PURCHASE_LIST]
                globals.queryEntry.config(completevalues=completevalues)
            globals.queryEntry.config(completevalues=[record["purchase_name"] if record["purchase_name"] else "" for record in globals.PURCHASE_LIST])


def handleSearchPurchase(queryColumnDict, page=1, limit=11, sort_column="id", asc=True):
    try:
        globals.CURRENT_SEARCH_QUERY["purchases"] = {}
        for column, query in queryColumnDict.items():
            globals.CURRENT_SEARCH_QUERY["purchases"][column] = query
        status, data = get_purchases(globals.CURRENT_SEARCH_QUERY["purchases"], page=page, limit=limit, sort_column=sort_column, asc=asc)
        
        if status:
            createPurchasesTable(globals.purchasesFrame, data=data)
        else:
            Label(globals.purchasesFrame, text="Error occured while fetching products from database.").pack()
            Label(globals.purchasesFrame, text="Please check logs or contact the developer.").pack()
        return True
    except Exception as e:
        log.error(f"ERROR: while handling Search purchase -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")


def createPurchasesTop(parent):
    # For search bar and add item button
    globals.tableTop = Frame(parent)
    globals.tableTop.pack(fill="x", pady=20, padx=10)

    Label(globals.tableTop, text="Search purchase by").grid(row=0, column=0, sticky="w")

    globals.queryEntry = AutocompleteEntry(globals.tableTop,
                width=30, 
                font=20,
                completevalues=[])
    globals.queryEntry.grid(row=0, column=2, ipady=5, sticky="w")
    globals.queryEntry.bind("<Return>", lambda x: proceedToSearch())

    def setCompleteValues():
        if globals.purchaseFilterOptionsMap.get(globals.filterOption.get()):
            column_name = globals.purchaseFilterOptionsMap.get(globals.filterOption.get())
            completevalues = []
            if column_name in ["vendor_name", "vat_number", "email", "telephone", "phone_number"]:
                completevalues = [str(record["vendor"].get(column_name)) if record.get("vendor").get(column_name) else "" for record in globals.PURCHASE_LIST]
            else:
                completevalues = [str(record[column_name]) if record.get(column_name) else "" for record in globals.PURCHASE_LIST]
            globals.queryEntry.config(completevalues=completevalues)
    
    globals.filterOption = StringVar()
    globals.filterOption.set("Invoice Number")
    filters = list(globals.purchaseFilterOptionsMap.keys())

    filter = OptionMenu(globals.tableTop, globals.filterOption, *filters, command=lambda x: setCompleteValues())
    filter.grid(row=0, column=1, padx=(2, 5), sticky="w")
    setCompleteValues()

    def proceedToSearch():
        
        if globals.queryEntry.get():
            if globals.purchaseFilterOptionsMap.get(globals.filterOption.get()):
                handleSearchPurchase({globals.purchaseFilterOptionsMap.get(globals.filterOption.get()):globals.queryEntry.get()})
            else:
                messagebox.showwarning("Purchases", "Please select a filter to search by.")

    searchButton = Button(globals.tableTop, 
                        text="Search", 
                        width=10, 
                        bg="#47B5FF",
                        command=proceedToSearch)
    searchButton.grid(row=0, column=3, padx=5, sticky="w")

    def clearSearch():
        globals.queryEntry.delete(0, END)
        globals.queryEntry.insert(0, "")
        globals.CURRENT_SEARCH_QUERY["purchases"] = {}
        handleSearchPurchase({})

    clearButton = Button(globals.tableTop,
                        text="Clear", 
                        width=10, 
                        bg="#47B5FF",
                        command=clearSearch)
    clearButton.grid(row=0, column=4, padx=5, sticky="w")

    addItemButton = Button(globals.tableTop, 
                        text="Add New Purchase", 
                        width=15, 
                        bg=globals.appBlue, 
                        command=lambda: dashboard.showFrame("homeFrame"))
    addItemButton.grid(row=0, column=5, padx=5, sticky="e")
    
    exportButton = Button(globals.tableTop, 
                        text="Export",
                        width=10, 
                        bg=globals.appBlue, 
                        command=lambda : messagebox.showinfo("Export Purchases", "Feature comming soon in next update!\n\nYou will be able to export purchases to an excel file with the help of this feature.\n\nThank you!"))
    exportButton.grid(row=0, column=6, padx=5, sticky="e")
    
    Grid.columnconfigure(globals.tableTop, 4, weight=1)


def createTableHeader(parent):
    Label(parent, text="SN", font=globals.appFontNormalBold).grid(row=0, column=0, sticky=W)
    Label(parent, text="", font=globals.appFontNormalBold).grid(row=0, column=1, sticky=W)
    Label(parent, text="", font=globals.appFontNormalBold).grid(row=0, column=2, sticky=W)
    Label(parent, text="Date", font=globals.appFontNormalBold).grid(row=0, column=3, sticky=W)
    Label(parent, text="Invoice number", font=globals.appFontNormalBold).grid(row=0, column=4, sticky=W)
    Label(parent, text="Vendor", font=globals.appFontNormalBold).grid(row=0, column=5, sticky=W)
    Label(parent, text="Qty", font=globals.appFontNormalBold).grid(row=0, column=6, sticky=W)
    Label(parent, text="B. Amount", font=globals.appFontNormalBold).grid(row=0, column=7, sticky=W)
    Label(parent, text="Cash Discount", font=globals.appFontNormalBold).grid(row=0, column=8, sticky=W)
    Label(parent, text="% Discount", font=globals.appFontNormalBold).grid(row=0, column=9, sticky=W)
    Label(parent, text="Extra Discount", font=globals.appFontNormalBold).grid(row=0, column=10, sticky=W)
    Label(parent, text="Excise Duty", font=globals.appFontNormalBold).grid(row=0, column=11, sticky=W)
    Label(parent, text="VAT", font=globals.appFontNormalBold).grid(row=0, column=12, sticky=W)
    Label(parent, text="Cash Payment", font=globals.appFontNormalBold).grid(row=0, column=13, sticky=W)
    Label(parent, text="Total", font=globals.appFontNormalBold).grid(row=0, column=14, sticky=W)
    makeColumnResponsive(parent)


def createTableBody(parent, records):
    if not records:
        Label(parent, text="No records found!").grid(row=1, column=0, columnspan=8, pady=5)
        return True

    def proceedToUpdate(record):
        pass

    for index, record in enumerate(records):
        quantity = sum([float(r.get("quantity")) for r in record.get("product_qty").values()])
        totalAmount = float(sum([float(r["rate"])*float(r["quantity"]) for r in record.get("product_qty").values()]))

        cashPayment = float(record.get("cash_payment")) if record.get("cash_payment") else 0
        cashDiscount = float(record.get("cash_discount")) if record.get("cash_discount") else 0
        percentageDiscount = float(record.get("p_discount")) if record.get("p_discount") else 0
        extraDiscount = float(record.get("extra_discount")) if record.get("extra_discount") else 0
        exciseDuty = float(record.get("excise_duty")) if record.get("excise_duty") else 0
        vatPercentage = float(record.get("vat")) if record.get("vat") else 0
        
        discountByPercentage = float(totalAmount * (percentageDiscount/100))
        totalDiscountAmount = discountByPercentage + cashDiscount + extraDiscount
        globals.PURCHASE_DETAILS.get("final")["discount"] = totalDiscountAmount
        
        taxableAmount = float((totalAmount - totalDiscountAmount) + exciseDuty)
        vatAmount = float(0)
        if vatPercentage:
            vatAmount = float(taxableAmount * (vatPercentage/100))

        totalPayable = float(taxableAmount + vatAmount)

        bg = "white" if (index+1)%2==0 else globals.appWhite
        Label(parent, text=index+1, bg=bg).grid(row=index+1, column=0, pady=5, sticky=W),
        Button(parent, text="update", width=10, bg=globals.appBlue, command=lambda x=record: proceedToUpdate(x)).grid(row=index+1, column=1, pady=5, sticky=W)
        Button(parent, text="delete", width=10, bg="red", command=lambda id=record.get("id"), vendor_name=record.get("vendor").\
                get("vendor_name"), invoice_number=record.get("invoice_number"): deletePurchase(id, vendor_name, invoice_number)).\
                grid(row=index+1, column=2, pady=5, sticky=W)
        Label(parent, text=record.get("date_of_purchase") if record.get("date_of_purchase") else "---", bg=bg, wraplength=160, justify="left").\
                grid(row=index+1, column=3,pady=5, sticky=W)
        Label(parent, text=record.get("invoice_number") if record.get("invoice_number") else "---", bg=bg, wraplength=160, justify="left").\
                grid(row=index+1, column=3,pady=5, sticky=W)
        Label(parent, text=record.get("vendor").get("vendor_name") if record.get("vendor").get("vendor_name") else "---", bg=bg, wraplength=160, justify="left").\
                grid(row=index+1, column=4, pady=5, sticky=W)
        Label(parent, text=quantity if quantity else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=5, pady=5, sticky=W)
        Label(parent, text=record.get("balance_amount") if record.get("balance_amount") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=6, pady=5, sticky=W)
        Label(parent, text=cashDiscount if cashDiscount else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=7, pady=5, sticky=W)
        Label(parent, text=percentageDiscount if percentageDiscount else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=8, pady=5, sticky=W)
        Label(parent, text=extraDiscount if extraDiscount else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=9, pady=5, sticky=W)
        Label(parent, text=exciseDuty if exciseDuty else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=10, pady=5, sticky=W)
        Label(parent, text=vatPercentage if vatPercentage else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=11, pady=5, sticky=W)
        Label(parent, text=cashPayment if cashPayment else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=12, pady=5, sticky=W)
        Label(parent, text=totalPayable if totalPayable else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=13, pady=5, sticky=W)

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

    handleSearchPurchase(globals.CURRENT_SEARCH_QUERY["purchases"], page=globals.PAGINATION_PAGE, limit=globals.PAGINATION_PAGE_LIMIT)
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
    globals.paginationBackButton.grid(row=14, column=6, pady=10)

    globals.paginationPageInfo = Label(parent, text=f"Page {currentPage} out of {totalPages}")
    globals.paginationPageInfo.grid(row=globals.PAGINATION_PAGE_LIMIT+3, column=7, pady=10)
    
    globals.paginationForwardButton = Button(parent, 
                                            text=">>", 
                                            bg=globals.appGreen, 
                                            fg=globals.appWhite, 
                                            command=lambda : handlePagination(currentPage, totalPages, "forward"))
    globals.paginationForwardButton.grid(row=14, column=8, pady=10)

    handlePaginationButtonState(currentPage, totalPages)
    
    
def createPurchasesTable(parent, data):
    globals.purchasesTable.destroy() if globals.purchasesTable else None
    globals.purchasesTable = Frame(parent)
    globals.purchasesTable.pack(fill="both", expand=True)

    createTableHeader(globals.purchasesTable)
    createTableBody(globals.purchasesTable, records=data["data"])
    createTableFooter(globals.purchasesTable, currentPage=data["current_page"], totalPages=data["total_pages"])


def createPurchasesFrame(parent):
    globals.purchasesFrame = Frame(parent, borderwidth=1)
    globals.purchasesFrame.pack(fill="both", expand=True, padx=10)
    
    createPurchasesTop(globals.purchasesFrame)
    handleSearchPurchase({})


def openPurchaseView(parent):
    try:
        createPurchasesFrame(parent)
    except Exception as e:
        log.error(f"ERROR: while creating purchases frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")
    