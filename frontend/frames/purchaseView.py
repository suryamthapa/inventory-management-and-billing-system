"""Frame for purchase""" 
# built-in module imports
import datetime
from pytz import timezone
import logging
from tkinter import messagebox
from tkinter import *
from ttkwidgets.autocomplete import AutocompleteEntry
# frontend imports
import frontend.config as globals
from frontend.utils.frontend import makeColumnResponsive, get_utc_datetime_from_nepali_date
from frontend.utils.purchase import refreshPurchasesList
import frontend.windows.dashboard as dashboard
from core.tkNepaliCalendar import DateEntry
# backend imports
from backend.api.purchase import delete_purchase, get_purchases
from backend.api.products import update_product


log = logging.getLogger("frontend")


def deletePurchase(record):
    id = record.get("id")
    vendor_name = record.get("vendor").get("vendor_name")
    invoice_number = record.get("extra").get("invoice_number")
    response = messagebox.askyesnocancel("Delete the purchase", f"Are you sure?\n\nid: {id}\nInvoice number: #{invoice_number}\nVendor Name: {vendor_name}")
    if response == 1:
        status, message = delete_purchase(id=id)
        if not status:
            messagebox.showerror("Delete Purchase", message)
        else:
            for id, details in record.get("products").items():
                product_update_status, product_update_message = update_product(id, data={"stock": float(details.get("stock")) - float(details.get("quantity"))})
                if not status:
                    log.error(f"{product_update_status} {product_update_message}")
                else:
                    log.info(f"{product_update_status} {product_update_message}")
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
                globals.queryEntry.config(completevalues=set(completevalues))


def handleSearchPurchase(queryColumnDict, page=1, limit=11, sort_column="id", asc=True, from_=None, to=None):
    try:
        log.info(f"{queryColumnDict} {from_} {to}")
        globals.CURRENT_SEARCH_QUERY["purchases"] = {}
        for column, query in queryColumnDict.items():
            globals.CURRENT_SEARCH_QUERY["purchases"][column] = query
        status, data = get_purchases(globals.CURRENT_SEARCH_QUERY["purchases"], page=page, limit=limit, sort_column=sort_column, asc=asc, from_=from_, to=to)
        if status:
            globals.CURRENT_PURCHASE_ENTRIES = data.copy()
            globals.CURRENT_PURCHASE_ENTRIES["from"] = from_
            globals.CURRENT_PURCHASE_ENTRIES["to"] = to
            createPurchasesTable(data=data)
        else:
            globals.CURRENT_PURCHASE_ENTRIES = {}
            Label(globals.purchaseViewFrame, text="Error occured while fetching purchases from database.").pack()
            Label(globals.purchaseViewFrame, text="Please check logs or contact the developer.").pack()
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
                completevalues = [str(record["extra"].get(column_name)) if record.get("extra") else "" for record in globals.PURCHASE_LIST]
            globals.queryEntry.config(completevalues=set(completevalues))
    
    globals.filterOption = StringVar()
    globals.filterOption.set("Invoice Number")
    filters = list(globals.purchaseFilterOptionsMap.keys())

    filter = OptionMenu(globals.tableTop, globals.filterOption, *filters, command=lambda x: setCompleteValues())
    filter.grid(row=0, column=1, padx=(2, 5), sticky="w")
    setCompleteValues()

    def proceedToSearch(forSort = False, forDateFilter = False):
        if forSort and globals.purchaseSortOptionsMap.get(globals.sortOption.get()) is None:
            messagebox.showerror("Purhase View", "Please select a field to sort by.")
            return False

        from_ = fromDateEntry.get()
        to = toDateEntry.get()
        if from_ == "Select date" and to == "Select date":
            final_from_ = None
            final_to = None
        else:
            utc_timezone = timezone("UTC")
            final_from_ = datetime.datetime.utcnow().astimezone(utc_timezone)
            final_to = datetime.datetime.utcnow().astimezone(utc_timezone)
            if from_ != "Select date":
                final_from_, message = get_utc_datetime_from_nepali_date(from_)
            if to != "Select date":
                final_to, msg = get_utc_datetime_from_nepali_date(to)
            log.info(f"In Purchase View Frame: {final_from_=} {final_to=}")
            if not final_from_ or not final_to:
                log.error(f"Error on from -> {message}")
                log.error(f"Error on to -> {msg}")
                messagebox.showerror("Purhase View", "Invalid Date.")
                return False
            if final_from_ > final_to:
                messagebox.showerror("Purhase View", "'From' date should not be greater than 'To' date.")
                return False
            final_from_ = datetime.date(final_from_.year, final_from_.month, final_from_.day)
            final_to = datetime.date(final_to.year, final_to.month, final_to.day)

        if globals.queryEntry.get() or forSort or forDateFilter:
            if globals.purchaseFilterOptionsMap.get(globals.filterOption.get()):
                handleSearchPurchase({globals.purchaseFilterOptionsMap.get(globals.filterOption.get()):globals.queryEntry.get()}, 
                                    sort_column=globals.purchaseSortOptionsMap.get(globals.sortOption.get()),
                                    asc=False if globals.sortOrder.get() else True,
                                    from_=final_from_,
                                    to=final_to)
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
        fromDateEntry.delete(0,END)
        fromDateEntry.insert(0,"Select date")
        toDateEntry.delete(0,END)
        toDateEntry.insert(0,"Select date")
        globals.sortOption.set("Select a field")
        proceedToSearch(forDateFilter=True)

    clearButton = Button(globals.tableTop,
                        text="Clear", 
                        width=10, 
                        bg="#47B5FF",
                        command=clearSearch)
    clearButton.grid(row=0, column=4, padx=5, sticky="w")

    addItemButton = Button(globals.tableTop, 
                        text="Add Purchase Entry", 
                        width=15,
                        bg=globals.appBlue,
                        command=lambda: dashboard.showFrame("purchaseEntrySystemFrame"))
    addItemButton.grid(row=0, column=5, padx=5, sticky="e")
    
    exportButton = Button(globals.tableTop, 
                        text="Export in Pdf",
                        width=10, 
                        bg=globals.appBlue, 
                        command=lambda : messagebox.showinfo("Export Purchases", "Feature comming soon in next update!\n\nYou will be able to export purchases to an excel file with the help of this feature.\n\nThank you!"))
    exportButton.grid(row=0, column=6, padx=5, sticky="e")
    
    fromToSortGroup = Frame(globals.tableTop)
    fromToSortGroup.grid(row=1, column=0, columnspan=7, pady=(20,0), sticky="w")

    Label(fromToSortGroup, text="Sort By").grid(row=0, column=0, sticky="w")

    globals.sortOption = StringVar()
    globals.sortOption.set("Select a field")
    filters = list(globals.purchaseSortOptionsMap.keys())

    filter = OptionMenu(fromToSortGroup, globals.sortOption, *filters, command=lambda x: proceedToSearch(forSort=True))
    filter.grid(row=0, column=1, padx=(2, 5), sticky="w")

    globals.sortOrder = IntVar()
    checkBtn = Checkbutton(fromToSortGroup, text = "Descending", variable = globals.sortOrder,
                    onvalue = 1, offvalue = 0, width = 8, justify="left", command= lambda : proceedToSearch(forSort=True))
    checkBtn.grid(row=0, column=2, padx=(1, 10), sticky="w")

    Label(fromToSortGroup, text="From: ").grid(row=0, column=3, padx=(20,0))
    fromDateEntry = DateEntry(fromToSortGroup)
    fromDateEntry.grid(row=0, column=4, sticky="w", padx=(10,5))
    fromDateEntry.delete(0,END)
    fromDateEntry.insert(0,"Select date")
    
    Label(fromToSortGroup, text="To: ").grid(row=0, column=5, sticky="w")
    toDateEntry = DateEntry(fromToSortGroup)
    toDateEntry.grid(row=0, column=6, sticky="w", padx=(2,5))
    toDateEntry.delete(0,END)
    toDateEntry.insert(0,"Select date")

    applyDateButton = Button(fromToSortGroup, 
                        text="Apply Date", 
                        width=12,
                        bg=globals.appGreen,
                        fg=globals.appWhite,
                        command=lambda : proceedToSearch(forDateFilter=True))
    applyDateButton.grid(row=0, column=7, padx=2, sticky="w")

    makeColumnResponsive(fromToSortGroup)
    Grid.columnconfigure(globals.tableTop, 4, weight=1)


def createTableHeader(parent):
    Label(parent, text="SN", font=globals.appFontNormalBold).grid(row=0, column=0, sticky=W, padx=5)
    Label(parent, text="", font=globals.appFontNormalBold).grid(row=0, column=1, sticky=W, padx=5)
    Label(parent, text="", font=globals.appFontNormalBold).grid(row=0, column=2, sticky=W, padx=5)
    Label(parent, text="Date", font=globals.appFontNormalBold).grid(row=0, column=3, sticky=W, padx=5)
    Label(parent, text="Invoice number", font=globals.appFontNormalBold).grid(row=0, column=4, sticky=W, padx=5)
    Label(parent, text="Vendor", font=globals.appFontNormalBold).grid(row=0, column=5, sticky=W, padx=5)
    Label(parent, text="Qty", font=globals.appFontNormalBold).grid(row=0, column=6, sticky=W, padx=5)
    Label(parent, text="B. Amount", font=globals.appFontNormalBold).grid(row=0, column=7, sticky=W, padx=5)
    Label(parent, text="Cash Discount", font=globals.appFontNormalBold).grid(row=0, column=8, sticky=W, padx=5)
    Label(parent, text="% Discount", font=globals.appFontNormalBold).grid(row=0, column=9, sticky=W, padx=5)
    Label(parent, text="Extra Discount", font=globals.appFontNormalBold).grid(row=0, column=10, sticky=W, padx=5)
    Label(parent, text="Excise Duty", font=globals.appFontNormalBold).grid(row=0, column=11, sticky=W, padx=5)
    Label(parent, text="VAT", font=globals.appFontNormalBold).grid(row=0, column=12, sticky=W, padx=5)
    Label(parent, text="Cash Payment", font=globals.appFontNormalBold).grid(row=0, column=13, sticky=W, padx=5)
    Label(parent, text="Total", font=globals.appFontNormalBold).grid(row=0, column=14, sticky=W, padx=5)
    makeColumnResponsive(parent)


def createTableBody(parent, records):
    if not records:
        Label(parent, text="No records found!").grid(row=1, column=0, columnspan=8, pady=5)
        return True

    def proceedToUpdate(record):
        globals.PURCHASE_DETAILS = record
        dashboard.showFrame("purchaseEntrySystemFrame")

    for index, record in enumerate(records):
        quantity = sum([float(r.get("quantity")) for r in record.get("products").values()])
        totalAmount = float(sum([float(r["rate"])*float(r["quantity"]) for r in record.get("products").values()]))

        cashPayment = float(record.get("extra").get("cash_payment")) if record.get("extra").get("cash_payment") else 0
        cashDiscount = float(record.get("extra").get("cash_discount")) if record.get("extra").get("cash_discount") else 0
        percentageDiscount = float(record.get("extra").get("p_discount")) if record.get("extra").get("p_discount") else 0
        extraDiscount = float(record.get("extra").get("extra_discount")) if record.get("extra").get("extra_discount") else 0
        exciseDuty = float(record.get("extra").get("excise_duty")) if record.get("extra").get("excise_duty") else 0
        vatPercentage = float(record.get("extra").get("vat")) if record.get("extra").get("vat") else 0
        
        discountByPercentage = float(totalAmount * (percentageDiscount/100))
        totalDiscountAmount = discountByPercentage + cashDiscount + extraDiscount
        
        taxableAmount = float((totalAmount - totalDiscountAmount) + exciseDuty)
        vatAmount = float(0)
        if vatPercentage:
            vatAmount = float(taxableAmount * (vatPercentage/100))

        totalPayable = float(taxableAmount + vatAmount)

        bg = "white" if (index+1)%2==0 else globals.appWhite
        Label(parent, text=index+1, bg=bg).grid(row=index+1, column=0, pady=5, sticky=W),
        Button(parent, text="update", width=10, bg=globals.appBlue, command=lambda x=record: proceedToUpdate(x)).grid(row=index+1, column=1, pady=5, sticky=W, padx=5)
        Button(parent, text="delete", width=10, bg="red", command=lambda x=record: deletePurchase(x)).\
                grid(row=index+1, column=2, pady=5, sticky=W, padx=5)
        Label(parent, text=record.get("extra").get("date_of_purchase") if record.get("extra").get("date_of_purchase") else "---", bg=bg, wraplength=160, justify="left").\
                grid(row=index+1, column=3,pady=5, sticky=W, padx=5)
        Label(parent, text=record.get("extra").get("invoice_number") if record.get("extra").get("invoice_number") else "---", bg=bg, wraplength=160, justify="left").\
                grid(row=index+1, column=4,pady=5, sticky=W, padx=5)
        Label(parent, text=record.get("vendor").get("vendor_name") if record.get("vendor").get("vendor_name") else "---", bg=bg, wraplength=160, justify="left").\
                grid(row=index+1, column=5, pady=5, sticky=W, padx=5)
        Label(parent, text=quantity if quantity else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=6, pady=5, sticky=W, padx=5)
        Label(parent, text=record.get("extra").get("balance_amount") if record.get("extra").get("balance_amount") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=7, pady=5, sticky=W, padx=5)
        Label(parent, text=cashDiscount if cashDiscount else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=8, pady=5, sticky=W, padx=5)
        Label(parent, text=percentageDiscount if percentageDiscount else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=9, pady=5, sticky=W, padx=5)
        Label(parent, text=extraDiscount if extraDiscount else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=10, pady=5, sticky=W, padx=5)
        Label(parent, text=exciseDuty if exciseDuty else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=11, pady=5, sticky=W, padx=5)
        Label(parent, text=vatPercentage if vatPercentage else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=12, pady=5, sticky=W, padx=5)
        Label(parent, text=cashPayment if cashPayment else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=13, pady=5, sticky=W, padx=5)
        Label(parent, text=totalPayable if totalPayable else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=14, pady=5, sticky=W, padx=5)

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
    globals.paginationBackButton.grid(row=14, column=0, pady=10, sticky="E")

    globals.paginationPageInfo = Label(parent, text=f"Page {currentPage} out of {totalPages}")
    globals.paginationPageInfo.grid(row=globals.PAGINATION_PAGE_LIMIT+3, column=1, pady=10, sticky="NSWE")
    
    globals.paginationForwardButton = Button(parent, 
                                            text=">>", 
                                            bg=globals.appGreen, 
                                            fg=globals.appWhite, 
                                            command=lambda : handlePagination(currentPage, totalPages, "forward"))
    globals.paginationForwardButton.grid(row=14, column=2, pady=10, sticky="W")

    handlePaginationButtonState(currentPage, totalPages)
    
    
def createPurchasesTable(data):
    globals.purchaseViewTable.destroy() if globals.purchaseViewTable else None
    globals.purchaseViewTable = Frame(globals.tableCanvas)
    globals.purchaseViewTable.pack(fill="both", expand=True)

    canvasframe = globals.tableCanvas.create_window(0,0, window=globals.purchaseViewTable, anchor='nw')

    def frameWidth(event):
        if event.width > globals.purchaseViewTable.winfo_width():
            globals.tableCanvas.itemconfig(canvasframe, width=event.width-4)
        if event.height > globals.purchaseViewTable.winfo_height():
            globals.tableCanvas.itemconfig(canvasframe, height=event.height-4)

    def OnFrameConfigure(event):
        globals.tableCanvas.configure(scrollregion=globals.tableCanvas.bbox("all"))
    
    globals.tableCanvas.bind('<Configure>', lambda e: frameWidth(e))
    globals.purchaseViewTable.bind('<Configure>', lambda e: OnFrameConfigure(e))

    def _bound_to_mousewheel(event):
       globals.tableCanvas.bind_all("<MouseWheel>",_on_mousewheel)

    def _unbound_to_mousewheel(event):
       globals.tableCanvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(event):
       globals.tableCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    globals.purchaseViewTable.bind('<Enter>',_bound_to_mousewheel)
    globals.purchaseViewTable.bind('<Leave>',_unbound_to_mousewheel)

    createTableHeader(globals.purchaseViewTable)
    createTableBody(globals.purchaseViewTable, records=data["data"])
    createTableFooter(globals.purchaseViewTable, currentPage=data["current_page"], totalPages=data["total_pages"])


def createPurchasesFrame(parent):
    globals.purchaseViewFrame = Frame(parent, borderwidth=1)
    globals.purchaseViewFrame.pack(fill="both", expand=True, padx=10)
    
    createPurchasesTop(globals.purchaseViewFrame)

    globals.tableCanvas = Canvas(globals.purchaseViewFrame)

    canvasScrollVertical = Scrollbar(globals.purchaseViewFrame, orient="vertical", command=globals.tableCanvas.yview)
    globals.tableCanvas.configure(yscrollcommand=canvasScrollVertical.set)
    canvasScrollHorizontal = Scrollbar(globals.purchaseViewFrame, orient="horizontal", command=globals.tableCanvas.xview)
    globals.tableCanvas.configure(xscrollcommand=canvasScrollHorizontal.set)

    canvasScrollVertical.pack(side="right", fill="y")
    canvasScrollHorizontal.pack(side="bottom", fill="x")

    globals.tableCanvas.pack(side="left", fill="both", expand=True, padx=3, pady=5)

    handleSearchPurchase({})


def openPurchaseView(parent):
    try:
        createPurchasesFrame(parent)
    except Exception as e:
        log.exception(f"ERROR: while creating purchases frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")
    