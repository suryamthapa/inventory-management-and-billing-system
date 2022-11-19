"""Frame for customers""" 
# built-in module imports
import logging
import nepali_datetime
from tkinter import messagebox
from tkinter import *
from ttkwidgets.autocomplete import AutocompleteEntry
# frontend imports
import frontend.config as globals
from frontend.utils.accounts import get_formatted_account
from frontend.utils.frontend import makeColumnResponsive
from frontend.utils.customers import refreshCustomersList
import frontend.windows.updateCustomers as updateCustomers
import frontend.windows.addCustomers as addCustomers
from frontend.utils.tkNepaliCalendar import DateEntry
# backend imports
from backend.api.customers import get_customer
from backend.api.accounts import delete_account


log = logging.getLogger("frontend")


def handleSearchAccount(column="", query="", from_="", to=""):
    globals.CURRENT_SEARCH_QUERY["account"] = {
        "column": column,
        "query": query
    }
    data = {
        "customer":{},
        "account":{},
        "from":from_,
        "to":to,
        "summary":{
            "dr_amount":0.00,
            "cr_amount":0.00,
            "account_balance":0.00
        }
    }
    if not column or not query:
        createDetailsArea(globals.accountsFrame, data=data)
        return False, "Insufficient data"

    toEval = f"get_customer({column}='{query}')"
    customerStatus, customerDetails = eval(toEval)
    if not customerStatus:
        createDetailsArea(globals.accountsFrame, data=data)
        return False, "Customer not found."
    
    account_data = get_formatted_account(customer_id=customerDetails.get("id"), from_=from_, to=to)
    if account_data:
        data["account"] = account_data
        for record in account_data:
            if record["type"]=="debit":
                data["summary"]["dr_amount"] += float(record["amount"])
            if record["type"]=="credit":
                data["summary"]["cr_amount"] += float(record["amount"])
        data["summary"]["account_balance"] = account_data[-1]["account_balance"]

    data["customer"] = customerDetails
    globals.CURRENT_LEDGER_ACCOUNT = data
    createDetailsArea(globals.accountsFrame, data=data)
    return True


def createLedgerDetailsTableHeader(parent):
    Label(parent, text="S No.", width=4, font=globals.appFontSmallBold).grid(row=1, column=0, sticky=W)
    Label(parent, text="Date", font=globals.appFontSmallBold).grid(row=1, column=1, sticky=W)
    Label(parent, text="Account Description", font=globals.appFontSmallBold).grid(row=1, column=2, sticky=W)
    Label(parent, text="Dr Amount", font=globals.appFontSmallBold).grid(row=1, column=3, sticky=W)
    Label(parent, text="Cr Amount", font=globals.appFontSmallBold).grid(row=1, column=4, sticky=W)
    Label(parent, text="Balance", font=globals.appFontSmallBold).grid(row=1, column=5, sticky=W)
    makeColumnResponsive(parent)


def createLedgerDetailsTableBody(parent, data):
    if not data:
        Label(parent, text="No records found!").grid(columnspan=6, pady=10)
        return True
    for index, record in enumerate(data):
        bg = "white" if (index+1)%2==0 else globals.appWhite
        Label(parent, text=str(index+1)).grid(row=index+2, column=0, pady=5, sticky=W)
        Label(parent, text=record.get("date"), bg=bg, wraplength=140, justify=LEFT).grid(row=index+2, column=1,pady=5, sticky=W, padx=2)
        Label(parent, text=record.get("description"), bg=bg).grid(row=index+2, column=2, pady=5, sticky=W, padx=2)
        Label(parent, text="{:,.2f}".format(float(record.get("amount"))) if record.get("type") == "debit" else "---", bg=bg).grid(row=index+2, column=3, pady=5, sticky=W, padx=2)
        Label(parent, text="{:,.2f}".format(float(record.get("amount"))) if record.get("type") == "credit" else "---", bg=bg).grid(row=index+2, column=4, pady=5, sticky=W, padx=2)
        Label(parent, text=record.get("account_balance"), bg=bg).grid(row=index+2, column=5, pady=5, sticky=W, padx=2)
        
        def proceedToUpdate(record):
            print("To update: ", record)

        def deleteRecordFromAccount(record):
            response = messagebox.askyesnocancel("Delete the customer", f"Are you sure?\n\nTransaction Id: {record.get('id')}\nDate: {record.get('date')}\nType: {record.get('type')}\nAmount: {record.get('amount')}")
            if response == 1:
                status, message = delete_account(id=record.get("id"))
                if not status:
                    messagebox.showerror("Delete Customer", message)
                else:
                    messagebox.showinfo("Delete Customer",f"{message}")
                    # reload the inventory table
                    handleSearchAccount(column=globals.CURRENT_SEARCH_QUERY["account"]["column"], 
                                        query=globals.CURRENT_SEARCH_QUERY["account"]["query"], 
                                        from_=globals.CURRENT_LEDGER_ACCOUNT["from"], 
                                        to=globals.CURRENT_LEDGER_ACCOUNT["to"])


        Button(parent, text="update", width=6, bg="#47B5FF", command=lambda record=record: proceedToUpdate(record)).grid(row=index+2, column=6, pady=5, padx=(0,2), sticky=W)
        Button(parent, text="delete", width=6, bg="red", command=lambda record=record: deleteRecordFromAccount(record)).grid(row=index+2, column=7, pady=5, padx=(2,0), sticky=W)
        
    makeColumnResponsive(parent)


def createLedgerDetailsTableFooter(parent):
    tableFooter = Frame(parent)
    tableFooter.grid(row=2, column=0, sticky="nswe")
    dr_amount = globals.CURRENT_LEDGER_ACCOUNT["summary"]["dr_amount"]
    cr_amount = globals.CURRENT_LEDGER_ACCOUNT["summary"]["cr_amount"]
    account_balance = globals.CURRENT_LEDGER_ACCOUNT["summary"]["account_balance"]

    Label(tableFooter, text="Dr Amount", font=globals.appFontSmallBold, justify="left").grid(row=0, column=1, sticky=W, pady=5, padx=10)
    Label(tableFooter, text="Cr Amount", font=globals.appFontSmallBold, justify="left").grid(row=0, column=2, sticky=W, pady=5, padx=10)
    Label(tableFooter, text="Account Balance", font=globals.appFontSmallBold, justify="left").grid(row=0, column=3, sticky=W, pady=5, padx=10)

    Label(tableFooter, text="Total:", font=globals.appFontSmallBold, justify="left").grid(row=1,column=0, pady=5, sticky=W, padx=10)

    Label(tableFooter, text="Rs. {:,.2f}".format(float(dr_amount)), justify="left").grid(row=1,column=1, pady=5, sticky=W, padx=10)
    Label(tableFooter, text="Rs. {:,.2f}".format(float(cr_amount)), justify="left").grid(row=1,column=2, pady=5, sticky=W, padx=10)
    Label(tableFooter, text=account_balance, justify="left").grid(row=1,column=3, sticky=W, pady=5, padx=10)
    

def createLedgerDetailsTableTop(parent):
    today = nepali_datetime.date.today()
    today = today.strftime("%d/%m/%Y")

    tableTop = Frame(parent)
    tableTop.grid(row=0, column=0, sticky="nswe")

    Label(tableTop, text="From: ").grid(row=0, column=0, sticky="w")
    fromDateEntry = DateEntry(tableTop)
    fromDateEntry.grid(row=0, column=1, sticky="w", padx=(2,5))
    fromDateEntry.delete(0,END)
    fromDateEntry.insert(0,"Select date" if not globals.CURRENT_LEDGER_ACCOUNT["from"] else globals.CURRENT_LEDGER_ACCOUNT["from"])
    
    Label(tableTop, text="To: ").grid(row=0, column=2, sticky="w")
    toDateEntry = DateEntry(tableTop)
    toDateEntry.grid(row=0, column=3, sticky="w", padx=(2,5))
    toDateEntry.delete(0,END)
    toDateEntry.insert(0,"Select date" if not globals.CURRENT_LEDGER_ACCOUNT["to"] else globals.CURRENT_LEDGER_ACCOUNT["to"])

    def proceedToLoadDetails():
        from_ = fromDateEntry.get()
        to = toDateEntry.get()
        if not from_:
            fromDateEntry.focus()
            return False
        if not from_:
            toDateEntry.focus()
            return False
        
        from_date_meta = from_.split("/")
        to_date_meta = to.split("/")

        if len(from_date_meta)!=3 or len(to_date_meta)!=3:
            messagebox.showwarning("InaBi System", "Invalid Date.")
            return False
        
        for m in from_date_meta:
            if not m.isdigit():
                messagebox.showwarning("InaBi System", "Invalid Date.")
                return False
        
        for m in to_date_meta:
            if not m.isdigit():
                messagebox.showwarning("InaBi System", "Invalid Date.")
                return False

        if int(from_date_meta[2]) > int(to_date_meta[2]):
            messagebox.showwarning("InaBi System", "From date should not be greater than To date.")
            return False
        
        if int(from_date_meta[2]) == int(to_date_meta[2]) and int(from_date_meta[0])>int(to_date_meta[0]):
            messagebox.showwarning("InaBi System", "From date should not be greater than To date.")
            return False
        
        if int(from_date_meta[2]) == int(to_date_meta[2]) and int(from_date_meta[0])==int(to_date_meta[0]) and int(from_date_meta[1])>int(to_date_meta[1]):
            messagebox.showwarning("InaBi System", "From date should not be greater than To date.")
            return False
        
        handleSearchAccount(column=globals.CURRENT_SEARCH_QUERY["account"]["column"], 
                            query=globals.CURRENT_SEARCH_QUERY["account"]["query"], from_=from_, to=to)
        


    searchButton = Button(tableTop, 
                        text="Load",
                        width=10, 
                        bg="#47B5FF",
                        command=lambda : proceedToLoadDetails())
    searchButton.grid(row=0, column=4, padx=5, sticky="w")

    def clearDateFilter():
        if not globals.CURRENT_LEDGER_ACCOUNT["to"] and globals.CURRENT_LEDGER_ACCOUNT["from"]:
            return False

        # clearing global entries
        globals.CURRENT_LEDGER_ACCOUNT["to"] = ""
        globals.CURRENT_LEDGER_ACCOUNT["from"] = ""

        # resetting entries
        fromDateEntry.delete(0,END)
        fromDateEntry.insert(0, "Select date")
        toDateEntry.delete(0,END)
        toDateEntry.insert(0, "Select date")

        # reloading the frame
        handleSearchAccount(column=globals.CURRENT_SEARCH_QUERY["account"]["column"], 
                            query=globals.CURRENT_SEARCH_QUERY["account"]["query"])

    clearButton = Button(tableTop,
                        text="Clear", 
                        width=10, 
                        bg="#47B5FF",
                        command=clearDateFilter)
    clearButton.grid(row=0, column=5, padx=5, sticky="w")

    addItemButton = Button(tableTop, 
                        text="Add Transaction", 
                        width=15, 
                        bg=globals.appBlue, 
                        command=lambda: addCustomers.createAddCustomerWindow())
    addItemButton.grid(row=0, column=6, padx=5, sticky="e")
    
    exportButton = Button(tableTop, 
                        text="Export to PDF",
                        width=15, 
                        bg=globals.appBlue, 
                        command=lambda : messagebox.showinfo("Export Customers", "Feature comming soon in next update!\n\nYou will be able to export customers to an excel file with the help of this feature.\n\nThank you!"))
    exportButton.grid(row=0, column=7, padx=5, sticky="e")
    
    Grid.columnconfigure(tableTop, 5, weight=1)
    

def createLedgerDetailsTable(parent, data):

    createLedgerDetailsTableTop(parent)

    ledgerDetailsHeaderBodyMain = LabelFrame(parent, text="Details")
    ledgerDetailsHeaderBodyMain.grid(row=1, column=0, sticky="nswe")

    canvas = Canvas(ledgerDetailsHeaderBodyMain, bg="blue")
    
    ledgerDetailsHeaderBody = Frame(canvas)
    ledgerDetailsHeaderBody.pack(fill="both", padx=5, pady=5)
    
    canvasScrollVertical = Scrollbar(ledgerDetailsHeaderBodyMain, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=canvasScrollVertical.set)
    canvasScrollHorizontal = Scrollbar(ledgerDetailsHeaderBodyMain, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=canvasScrollHorizontal.set)

    canvasScrollVertical.pack(side="right", fill="y")
    canvasScrollHorizontal.pack(side="bottom", fill="x")
    canvas.pack(fill="both", expand=True, padx=5, pady=5)
    canvasframe = canvas.create_window(0,0, window=ledgerDetailsHeaderBody, anchor='nw')

    def frameWidth(event):
        if event.width > ledgerDetailsHeaderBody.winfo_width():
            canvas.itemconfig(canvasframe, width=event.width-4)
        if event.height > ledgerDetailsHeaderBody.winfo_height():
            canvas.itemconfig(canvasframe, height=event.height-4)

    def OnFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    canvas.bind('<Configure>', lambda e: frameWidth(e))
    ledgerDetailsHeaderBody.bind('<Configure>', lambda e: OnFrameConfigure(e))

    def _bound_to_mousewheel(event):
       canvas.bind_all("<MouseWheel>",_on_mousewheel)

    def _unbound_to_mousewheel(event):
       canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(event):
       canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    ledgerDetailsHeaderBody.bind('<Enter>',_bound_to_mousewheel)
    ledgerDetailsHeaderBody.bind('<Leave>',_unbound_to_mousewheel)

    createLedgerDetailsTableHeader(ledgerDetailsHeaderBody)
    createLedgerDetailsTableBody(ledgerDetailsHeaderBody, data)

    createLedgerDetailsTableFooter(parent)
    
    makeColumnResponsive(parent)


def createLedgerDetailsArea(parent, data):
    Label(parent, text="Ledger - Detailed", font=globals.appFontNormalBold).pack(fill="x", pady=(5, 15))
    globals.ledgerDetailsTable = Frame(globals.ledgerDetailsArea)
    globals.ledgerDetailsTable.pack(fill="both")

    createLedgerDetailsTable(globals.ledgerDetailsTable, data)


def loadCustomerDetails(parent, customerDetails):
    try:
        # destroy childrens of globals.namePhFrame
        # before loading details of another product
        for child in parent.winfo_children():
            child.destroy()

        name = customerDetails.get("full_name")
        company = customerDetails.get("company")
        company_pan_no = customerDetails.get("company_pan_no")
        phone_num = customerDetails.get("phone_number")
        telephone = customerDetails.get("telephone")
        address = customerDetails.get("address")
        contacts = []
        if phone_num: contacts.append(phone_num) 
        if telephone: contacts.append(telephone)

        Label(parent, text="Customer:", font=globals.appFontSmallBold).grid(row=0, column=0, pady=10, sticky=W)
        if name:
            Label(parent, text=name, wraplength=160, justify="left").grid(row=0, column=1, pady=10, sticky=W)
        elif company:
            Label(parent, text=company, wraplength=160, justify="left").grid(row=0, column=1, pady=10, sticky=W)
        else:
            Label(parent, text="********", wraplength=160, justify="left").grid(row=0, column=1, pady=10, sticky=W)
        
        if company:
            Label(parent, text="PAN no:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=0, column=2, pady=10, sticky=W)
            Label(parent, text=company_pan_no if company_pan_no else "**********", wraplength=160, justify="left").grid(row=0, column=3, pady=10, sticky=W)
        elif name:
            Label(parent, text="Address:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=0, column=2, pady=10, sticky=W)
            Label(parent, text=address if address else "**********", wraplength=160, justify="left").grid(row=0, column=3, pady=10, sticky=W)
        
        Label(parent, text="Contacts:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=0, column=4, pady=10, sticky=W)
        Label(parent, text=f"{', '.join(contacts)}" if contacts else "********", wraplength=160, justify="left").grid(row=0, column=5, pady=10, sticky=W)

        if company:
            Label(parent, text="Address:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=0, column=6, pady=10, sticky=W)
            Label(parent, text=address if address else "**********", wraplength=160, justify="left").grid(row=0, column=7, pady=10, sticky=W)
        
        makeColumnResponsive(parent)

    except Exception as e:
        log.error(f"While loading customer details -> {e}")


def createCustomerDetailsArea(parent, data):
    if not data:
        Label(parent, text="Please search a customer to see account details.", pady=10).grid(sticky="nswe") 
    else:
        loadCustomerDetails(parent, customerDetails=data)
    makeColumnResponsive(parent)


def createAccountsTop(parent):
    # For search bar and add item button
    globals.tableTop = Frame(parent)
    globals.tableTop.pack(fill="x", pady=20, padx=10)

    Label(globals.tableTop, text="Search customer by").grid(row=0, column=0, sticky="w")

    globals.queryEntry = AutocompleteEntry(globals.tableTop,
                width=30, 
                font=20,
                completevalues=[])
    globals.queryEntry.grid(row=0, column=2, ipady=5, sticky="w")
    globals.queryEntry.bind("<Return>", lambda x: proceedToSearch())

    filterOptionsMap = {
            "Individual Name": "full_name",
            "Company Name": "company",
            "Phone Number": "phone_number",
            "Telephone": "telephone",
            "Email": "email"
        }

    def setCompleteValues():
        if filterOptionsMap.get(filterOption.get()):
            column_name = filterOptionsMap.get(filterOption.get())
            completevalues = [record[column_name] if record[column_name] else "" for record in globals.CUSTOMERS_LIST]
            globals.queryEntry.config(completevalues=completevalues)

    filterOption = StringVar()
    filterOption.set("Company Name")
    filters = list(filterOptionsMap.keys())

    filter = OptionMenu(globals.tableTop, filterOption, *filters, command=lambda x: setCompleteValues())
    filter.grid(row=0, column=1, padx=(2, 5), sticky="w")
    setCompleteValues()

    def proceedToSearch():
        if globals.queryEntry.get():
            if filterOptionsMap.get(filterOption.get()):
                handleSearchAccount(column=filterOptionsMap.get(filterOption.get()), query=globals.queryEntry.get())
            else:
                messagebox.showwarning("Customers", "Please select a filter to search by.")
        else:
            globals.queryEntry.focus()

    searchButton = Button(globals.tableTop, 
                        text="Search", 
                        width=10, 
                        bg="#47B5FF",
                        command=proceedToSearch)
    searchButton.grid(row=0, column=3, padx=5, sticky="w")

    def clearSearch():
        filterOption.set("Select a filter")
        globals.queryEntry.delete(0, END)
        globals.queryEntry.insert(0, "")
        globals.CURRENT_LEDGER_ACCOUNT = {
                    "customer":{},
                    "account":{},
                    "from":"",
                    "to":"",
                    "summary":{
                            "dr_amount":"",
                            "cr_amount":"",
                            "account_balance":""
                        }
                }
        handleSearchAccount()

    clearButton = Button(globals.tableTop,
                        text="Clear", 
                        width=10, 
                        bg="#47B5FF",
                        command=clearSearch)
    clearButton.grid(row=0, column=4, padx=5, sticky="w")
    
    Grid.columnconfigure(globals.tableTop, 4, weight=1)


def createDetailsArea(parent, data={"customer":{}, "account":{}}):
    
    for child in globals.accountCustomerDetailsFrame.winfo_children():
        child.destroy()
    
    for child in globals.ledgerDetailsArea.winfo_children():
        child.destroy()

    createCustomerDetailsArea(globals.accountCustomerDetailsFrame, data=data["customer"])
    if data["customer"] or data["account"]:
        createLedgerDetailsArea(globals.ledgerDetailsArea, data=data["account"])


def createAccountsFrame(parent):
    globals.accountsFrame = Frame(parent, borderwidth=1)
    globals.accountsFrame.pack(fill="both", expand=True, padx=10)

    createAccountsTop(globals.accountsFrame)

    detailsArea = Frame(globals.accountsFrame)
    detailsArea.pack(fill="both", padx=5, pady=10, expand=True)
    
    globals.accountCustomerDetailsFrame = Frame(detailsArea, pady=5)
    globals.accountCustomerDetailsFrame.pack(fill="x")

    globals.ledgerDetailsArea = Frame(detailsArea)
    globals.ledgerDetailsArea.pack(side="right", fill="both", expand=True)
    
    handleSearchAccount({})


def openAccounts(parent):
    try:
        createAccountsFrame(parent)
    except Exception as e:
        log.error(f"ERROR: while creating accounts frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")
    