"""Frame for purchase""" 
# built-in module imports
import datetime
from pytz import timezone
import logging
from tkinter import messagebox
from tkinter import *
from ttkwidgets.autocomplete import AutocompleteEntry
# core imports
from core import nepali_datetime
# frontend imports
import frontend.config as globals
from frontend.utils.frontend import makeColumnResponsive, get_utc_datetime_from_nepali_date
from frontend.utils.bills import refreshBillsList
import frontend.windows.dashboard as dashboard
from core.tkNepaliCalendar import DateEntry
# backend imports
from backend.api.bills import delete_bill, get_bills
from backend.api.products import update_product
from backend.api.accounts import get_accounts, delete_account


log = logging.getLogger("frontend")


def deleteBill(record):
    id = record.get("id")
    bill_number = record.get("extra").get("bill_number")
    customer_name = record.get("customer").get("full_name") if record.get("customer").get("full_name") else record.get("customer").get("company")
    response = messagebox.askyesnocancel("Delete the bill", f"Are you sure?\n\nInvoice number: #{bill_number}\nCustomer Name: {customer_name}")
    if response == 1:
        status, message = delete_bill(id=id)
        if not status:
            messagebox.showerror("Delete Bill", message)
        else:
            for id, details in record.get("products").items():
                product_update_status, product_update_message = update_product(id, data={"stock": float(details.get("stock")) + float(details.get("quantity"))})
                if not status:
                    log.error(f"{product_update_status} {product_update_message}")
                else:
                    log.info(f"{product_update_status} {product_update_message}")
            
            # deleting related accounts on ledger
            account_status, accounts = get_accounts(queryDict={"bill_id":id}, limit=None)
            if not account_status:
                log.error(f"{account_status} -> {accounts}")
            else:
                log.info(f"Got accounts related to bill -> {accounts['data']}")

            for account in accounts["data"]:
                    delete_status, delete_message = delete_account(account['id'])
                    if not delete_status:
                        log.error(f"{delete_status} -> {delete_message}")
                    else:
                        log.info(f"{delete_status} {delete_message}")

            messagebox.showinfo("Delete Bill",f"{message}")
            
            # refreshing products list
            refreshBillsList()
            # reload the inventory table
            handleSearchBill(globals.CURRENT_SEARCH_QUERY.get("bills"))
            # refresh auto complete values in search entry
            if globals.billsFilterOptionsMap.get(globals.filterOption.get()):
                column_name = globals.billsFilterOptionsMap.get(globals.filterOption.get())
                completevalues = []
                if column_name in ["full_name", "phone_number", "telephone", "company", "company_pan_no", "email"]:
                    completevalues = [str(record["customer"].get(column_name)) if record.get("customer").get(column_name) else "" for record in globals.BILLS_LIST]
                else:
                    completevalues = [str(record[column_name]) if record.get(column_name) else "" for record in globals.BILLS_LIST]
                globals.queryEntry.config(completevalues=set(completevalues))
                

def handleSearchBill(queryColumnDict, page=1, limit=11, sort_column="bill_number", asc=True, from_=None, to=None):
    try:
        log.info(f"Handling search bill with {queryColumnDict=} {from_=} {to=}")
        globals.CURRENT_SEARCH_QUERY["bills"] = {}
        for column, query in queryColumnDict.items():
            globals.CURRENT_SEARCH_QUERY["bills"][column] = query
        status, data = get_bills(globals.CURRENT_SEARCH_QUERY["bills"], page=page, limit=6, sort_column=sort_column, asc=asc, from_=from_, to=to)
        if status:
            for d in data["data"]:
                log.info(d)
            globals.CURRENT_BILL_ENTRIES = data.copy()
            globals.CURRENT_BILL_ENTRIES["from"] = from_
            globals.CURRENT_BILL_ENTRIES["to"] = to
            createBillsTable(data=data)
        else:
            globals.CURRENT_BILL_ENTRIES = {}
            Label(globals.billsViewFrame, text="Error occured while fetching bills from database.").pack()
            Label(globals.billsViewFrame, text="Please check logs or contact the developer.").pack()
        return True
    except Exception as e:
        log.exception(f"ERROR: while handling Search bill -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")


def createBillsTop(parent):
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
        if globals.billsFilterOptionsMap.get(globals.filterOption.get()):
            column_name = globals.billsFilterOptionsMap.get(globals.filterOption.get())
            completevalues = []
            if column_name in ["full_name", "phone_number", "telephone", "company", "company_pan_no", "email"]:
                completevalues = [str(record["customer"].get(column_name)) if record.get("customer").get(column_name) else "" for record in globals.BILLS_LIST]
            else:
                completevalues = [str(record["extra"].get(column_name)) if record.get("extra") else "" for record in globals.BILLS_LIST]
            globals.queryEntry.config(completevalues=set(completevalues))
    
    globals.filterOption = StringVar()
    globals.filterOption.set("Invoice Number")
    filters = list(globals.billsFilterOptionsMap.keys())

    filter = OptionMenu(globals.tableTop, globals.filterOption, *filters, command=lambda x: setCompleteValues())
    filter.grid(row=0, column=1, padx=(2, 5), sticky="w")
    setCompleteValues()

    def proceedToSearch(forSort = False, forDateFilter = False):
        if forSort and globals.billsSortOptionsMap.get(globals.sortOption.get()) is None:
            messagebox.showerror("Bill View", "Please select a field to sort by.")
            return False

        from_ = fromDateEntry.get()
        to = toDateEntry.get()
        if (from_ == "Select date" or not from_) and (to == "Select date" or not to):
            final_from_ = None
            final_to = None
        else:
            # date validation
            from_meta = from_.split("/")
            if len(from_meta)!=3:
                messagebox.showwarning("InaBi System", "'From' date is invalid.")
                return False
            for m in from_meta:
                if not m.isdigit():
                    messagebox.showwarning("InaBi System", "'From' date is invalid.")
                    return False
            
            from_year = int(from_meta[2])
            from_month = int(from_meta[1])
            if from_month > 12 or from_month < 1:
                messagebox.showwarning("InaBi System", "'From' date is invalid.")
                return False
            from_day = int(from_meta[0])
            if from_day > 32 or from_day < 1:
                messagebox.showwarning("InaBi System", "'From' date is invalid.")
                return False
            
            if to != "Select date":
                to_meta = to.split("/")
                if len(to_meta)!=3:
                    messagebox.showwarning("InaBi System", "'To' date is invalid.")
                    return False
                for m in to_meta:
                    if not m.isdigit():
                        messagebox.showwarning("InaBi System", "'To' date is invalid.")
                        return False
                
                to_year = int(to_meta[2])
                to_month = int(to_meta[1])
                if to_month > 12 or to_month < 1:
                    messagebox.showwarning("InaBi System", "'To' date is invalid.")
                    return False
                to_day = int(to_meta[0])
                if to_day > 32 or to_day < 1:
                    messagebox.showwarning("InaBi System", "'To' date is invalid.")
                    return False

                final_to = to
            else:
                final_to = None

            final_from_ = from_

        if globals.queryEntry.get() or forSort or forDateFilter:
            if globals.billsFilterOptionsMap.get(globals.filterOption.get()):
                handleSearchBill({globals.billsFilterOptionsMap.get(globals.filterOption.get()):globals.queryEntry.get()}, 
                                    sort_column=globals.billsSortOptionsMap.get(globals.sortOption.get()),
                                    asc=False if globals.sortOrder.get() else True,
                                    from_=final_from_,
                                    to=final_to)
            else:
                messagebox.showwarning("Bills", "Please select a filter to search by.")

    searchButton = Button(globals.tableTop, 
                        text="Search", 
                        width=10, 
                        bg="#47B5FF",
                        command=proceedToSearch)
    searchButton.grid(row=0, column=3, padx=5, sticky="w")

    def clearSearch():
        globals.queryEntry.delete(0, END)
        globals.queryEntry.insert(0, "")
        globals.CURRENT_SEARCH_QUERY["bills"] = {}
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
                        text="Add Bill Entry", 
                        width=15,
                        bg=globals.appBlue,
                        command=lambda: dashboard.showFrame("billingSystemFrame"))
    addItemButton.grid(row=0, column=5, padx=5, sticky="e")
    
    exportButton = Button(globals.tableTop, 
                        text="Export in Pdf",
                        width=10, 
                        bg=globals.appBlue, 
                        command=lambda : messagebox.showinfo("Export Bills", "Feature comming soon in next update!\n\nYou will be able to export bills to an excel file or a pdf file with the help of this feature.\n\nThank you!"))
    exportButton.grid(row=0, column=6, padx=5, sticky="e")
    
    fromToSortGroup = Frame(globals.tableTop)
    fromToSortGroup.grid(row=1, column=0, columnspan=7, pady=(20,0), sticky="w")

    Label(fromToSortGroup, text="Sort By").grid(row=0, column=0, sticky="w")

    globals.sortOption = StringVar()
    globals.sortOption.set("Select a field")
    filters = list(globals.billsSortOptionsMap.keys())

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
    Label(parent, text="Customer", font=globals.appFontNormalBold).grid(row=0, column=5, sticky=W, padx=5)
    Label(parent, text="Quantity", font=globals.appFontNormalBold).grid(row=0, column=6, sticky=W, padx=5)
    Label(parent, text="Discount Amount", font=globals.appFontNormalBold).grid(row=0, column=7, sticky=W, padx=5)
    Label(parent, text="Discount Percentage", font=globals.appFontNormalBold).grid(row=0, column=8, sticky=W, padx=5)
    Label(parent, text="Vat", font=globals.appFontNormalBold).grid(row=0, column=9, sticky=W, padx=5)
    Label(parent, text="Payment", font=globals.appFontNormalBold).grid(row=0, column=10, sticky=W, padx=5)
    Label(parent, text="Total", font=globals.appFontNormalBold).grid(row=0, column=11, sticky=W, padx=5)
    makeColumnResponsive(parent)


def createTableBody(parent, records):
    if not records:
        Label(parent, text="No records found!").grid(row=1, column=0, columnspan=8, pady=5)
        return True

    def proceedToUpdate(record):
        log.info(f"Loading data for update in billing system -> {record}")
        globals.BILL_DETAILS = record
        dashboard.showFrame("billingSystemFrame")

    for index, record in enumerate(records):
        customer = f'{record.get("customer").get("full_name")} (Individual)' if record.get("customer").get("full_name") else f'{record.get("customer").get("company")} (Company)'
        totalAmount = float(sum([float(r["rate"])*float(r["quantity"]) for r in record.get("products").values()]))
        quantity = float(sum([float(r["quantity"]) for r in record.get("products").values()]))

        cashPayment = float(record.get("extra").get("paid_amount")) if record.get("extra").get("paid_amount") else 0
        cashDiscount = float(record.get("extra").get("discount_amount")) if record.get("extra").get("discount_amount") else 0
        percentageDiscount = float(record.get("extra").get("discount_percentage")) if record.get("extra").get("discount_percentage") else 0
        vatPercentage = float(record.get("extra").get("vat")) if record.get("extra").get("vat") else 0
        
        discountByPercentage = float(totalAmount * (percentageDiscount/100))
        totalDiscountAmount = discountByPercentage + cashDiscount
        
        taxableAmount = float(totalAmount - totalDiscountAmount)
        vatAmount = float(0)
        if vatPercentage:
            vatAmount = float(taxableAmount * (vatPercentage/100))

        totalPayable = float(taxableAmount + vatAmount)
        date_of_sale = f'{record.get("extra").get("sale_day")}/{record.get("extra").get("sale_month")}/{record.get("extra").get("sale_year")}'

        bg = "white" if (index+1)%2==0 else globals.appWhite
        Label(parent, text=index+1, bg=bg).grid(row=index+1, column=0, pady=5, sticky=W),
        Button(parent, text="update", width=10, bg=globals.appBlue, command=lambda x=record: proceedToUpdate(x)).grid(row=index+1, column=1, pady=5, sticky=W, padx=5)
        Button(parent, text="delete", width=10, bg="red", command=lambda x=record: deleteBill(x)).\
                grid(row=index+1, column=2, pady=5, sticky=W, padx=5)
        Label(parent, text=date_of_sale if date_of_sale else "---", bg=bg, wraplength=160, justify="left").\
                grid(row=index+1, column=3,pady=5, sticky=W, padx=5)
        Label(parent, text=record.get("extra").get("bill_number") if record.get("extra").get("bill_number") else "---", bg=bg, wraplength=160, justify="left").\
                grid(row=index+1, column=4,pady=5, sticky=W, padx=5)
        Label(parent, text=customer if customer else "---", bg=bg, wraplength=160, justify="left").\
                grid(row=index+1, column=5, pady=5, sticky=W, padx=5)
        Label(parent, text=quantity if quantity else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=6, pady=5, sticky=W, padx=5)
        Label(parent, text=cashDiscount if cashDiscount else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=7, pady=5, sticky=W, padx=5)
        Label(parent, text=percentageDiscount if percentageDiscount else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=8, pady=5, sticky=W, padx=5)
        Label(parent, text=vatPercentage if vatPercentage else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=9, pady=5, sticky=W, padx=5)
        Label(parent, text=cashPayment if cashPayment else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=10, pady=5, sticky=W, padx=5)
        Label(parent, text=totalPayable if totalPayable else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=11, pady=5, sticky=W, padx=5)

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

    handleSearchBill(globals.CURRENT_SEARCH_QUERY["bills"], page=globals.PAGINATION_PAGE, limit=globals.PAGINATION_PAGE_LIMIT)
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
    
    
def createBillsTable(data):
    globals.billsViewTable.destroy() if globals.billsViewTable else None
    globals.billsViewTable = Frame(globals.tableCanvas)
    globals.billsViewTable.pack(fill="both", expand=True)

    canvasframe = globals.tableCanvas.create_window(0,0, window=globals.billsViewTable, anchor='nw')

    def frameWidth(event):
        if event.width > globals.billsViewTable.winfo_width():
            globals.tableCanvas.itemconfig(canvasframe, width=event.width-4)
        if event.height > globals.billsViewTable.winfo_height():
            globals.tableCanvas.itemconfig(canvasframe, height=event.height-4)

    def OnFrameConfigure(event):
        globals.tableCanvas.configure(scrollregion=globals.tableCanvas.bbox("all"))
    
    globals.tableCanvas.bind('<Configure>', lambda e: frameWidth(e))
    globals.billsViewTable.bind('<Configure>', lambda e: OnFrameConfigure(e))

    def _bound_to_mousewheel(event):
       globals.tableCanvas.bind_all("<MouseWheel>",_on_mousewheel)

    def _unbound_to_mousewheel(event):
       globals.tableCanvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(event):
       globals.tableCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    globals.billsViewTable.bind('<Enter>',_bound_to_mousewheel)
    globals.billsViewTable.bind('<Leave>',_unbound_to_mousewheel)

    createTableHeader(globals.billsViewTable)
    createTableBody(globals.billsViewTable, records=data["data"])
    createTableFooter(globals.billsViewTable, currentPage=data["current_page"], totalPages=data["total_pages"])


def createBillsFrame(parent):
    globals.billsViewFrame = Frame(parent, borderwidth=1)
    globals.billsViewFrame.pack(fill="both", expand=True, padx=10)
    
    createBillsTop(globals.billsViewFrame)

    globals.tableCanvas = Canvas(globals.billsViewFrame)

    canvasScrollVertical = Scrollbar(globals.billsViewFrame, orient="vertical", command=globals.tableCanvas.yview)
    globals.tableCanvas.configure(yscrollcommand=canvasScrollVertical.set)
    canvasScrollHorizontal = Scrollbar(globals.billsViewFrame, orient="horizontal", command=globals.tableCanvas.xview)
    globals.tableCanvas.configure(xscrollcommand=canvasScrollHorizontal.set)

    canvasScrollVertical.pack(side="right", fill="y")
    canvasScrollHorizontal.pack(side="bottom", fill="x")

    globals.tableCanvas.pack(side="left", fill="both", expand=True, padx=3, pady=5)

    handleSearchBill({})


def openBillsView(parent):
    try:
        createBillsFrame(parent)
    except Exception as e:
        log.exception(f"ERROR: while creating bills view frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")
    