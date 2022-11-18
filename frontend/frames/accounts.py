"""Frame for customers""" 
# built-in module imports
import logging
from tkinter import messagebox
from tkinter import *
from ttkwidgets.autocomplete import AutocompleteEntry
# frontend imports
import frontend.config as globals
from frontend.utils.accounts import get_formatted_accounts
from frontend.utils.frontend import makeColumnResponsive
from frontend.utils.customers import refreshCustomersList
import frontend.windows.updateCustomers as updateCustomers
import frontend.windows.addCustomers as addCustomers
# backend imports


log = logging.getLogger("frontend")


def proceedToShowLedger():
    messagebox.showinfo("InaBi System", f"Please wait! Pdf of ledger will open in the browser.\n\nThank you!")


def handleSearchAccount(queryColumnDict, page=1, limit=11, sort_column="id", asc=True):
    globals.CURRENT_SEARCH_QUERY["accounts"] = {}
    for column, query in queryColumnDict.items():
        globals.CURRENT_SEARCH_QUERY["accounts"][column] = query
    data = get_formatted_accounts(page=page, limit=limit, sort_column=sort_column, asc=asc)
    if data:
        createAccountsTable(globals.accountsFrame, data=data)
    else:
        Label(globals.accountsFrame, text="Error occured while fetching products from database.").pack()
        Label(globals.accountsFrame, text="Please check logs or contact the developer.").pack()
    return True


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

    def setCompleteValues():
        filterOptionsMap = {
            "Individual Name": "full_name",
            "Company Name": "company",
            "Phone Number": "phone_number",
            "Telephone": "telephone",
            "Email": "email"
        }
        if filterOptionsMap.get(filterOption.get()):
            column_name = filterOptionsMap.get(filterOption.get())
            completevalues = [record[column_name] if record[column_name] else "" for record in globals.CUSTOMERS_LIST]
            globals.queryEntry.config(completevalues=completevalues)
    
    filterOption = StringVar()
    filterOption.set("Select a filter")
    filters = ["Individual Name", "Company Name", "Phone Number", "Telephone", "Email"]

    filter = OptionMenu(globals.tableTop, filterOption, *filters, command=lambda x: setCompleteValues())
    filter.grid(row=0, column=1, padx=(2, 5), sticky="w")

    def proceedToSearch():
        filterOptionsMap = {
            "Individual Name": "full_name",
            "Company Name": "company",
            "Phone Number": "phone_number",
            "Telephone": "telephone",
            "Email": "email"
        }
        if globals.queryEntry.get():
            if filterOptionsMap.get(filterOption.get()):
                handleSearchAccount({filterOptionsMap.get(filterOption.get()):globals.queryEntry.get()})
            else:
                messagebox.showwarning("Customers", "Please select a filter to search by.")

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
        globals.CURRENT_SEARCH_QUERY["customers"] = {}
        handleSearchAccount({})

    clearButton = Button(globals.tableTop,
                        text="Clear", 
                        width=10, 
                        bg="#47B5FF",
                        command=clearSearch)
    clearButton.grid(row=0, column=4, padx=5, sticky="w")
    
    Grid.columnconfigure(globals.tableTop, 4, weight=1)


def createTableHeader(parent):
    Label(parent, text="ID", font=globals.appFontNormalBold).grid(row=0, column=0, sticky=W)
    Label(parent, text="Customer Name", font=globals.appFontNormalBold).grid(row=0, column=1, sticky=W)
    Label(parent, text="Company PAN no", font=globals.appFontNormalBold).grid(row=0, column=2, sticky=W)
    Label(parent, text="Account Balance", font=globals.appFontNormalBold).grid(row=0, column=3, sticky=W)
    makeColumnResponsive(parent)


def createTableBody(parent, records):
    if not records:
        Label(parent, text="No records found!").grid(row=1, column=0, columnspan=8, pady=5)
        return True
    for index, record in enumerate(records):
        bg = "white" if (index+1)%2==0 else globals.appWhite
        Label(parent, text=record.get("customer_id"), bg=bg).grid(row=index+1, column=0, pady=5, sticky=W),
        Label(parent, text=record.get("customer_name") if record.get("customer_name") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=1,pady=5, sticky=W)
        Label(parent, text=record.get("customer_company_pan_no") if record.get("customer_company_pan_no") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=2, pady=5, sticky=W)
        Label(parent, text=record.get("account_balance") if record.get("account_balance") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=3, pady=5, sticky=W)
        Button(parent, text="Update account", width=11, bg=globals.appBlue, command=lambda x=record: updateCustomers.createUpdateCustomerWindow(x)).grid(row=index+1, column=4, pady=5, sticky=W)
        Button(parent, text="View Ledger", width=10, bg=globals.appBlue, command=lambda : proceedToShowLedger()).grid(row=index+1, column=5, pady=5, sticky=W)

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

    handleSearchAccount(globals.CURRENT_SEARCH_QUERY["customers"], page=globals.PAGINATION_PAGE, limit=globals.PAGINATION_PAGE_LIMIT)
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
    globals.paginationBackButton.grid(row=14, column=3, pady=10)

    globals.paginationPageInfo = Label(parent, text=f"Page {currentPage} out of {totalPages}")
    globals.paginationPageInfo.grid(row=globals.PAGINATION_PAGE_LIMIT+3, column=4, pady=10)
    
    globals.paginationForwardButton = Button(parent, 
                                            text=">>", 
                                            bg=globals.appGreen, 
                                            fg=globals.appWhite, 
                                            command=lambda : handlePagination(currentPage, totalPages, "forward"))
    globals.paginationForwardButton.grid(row=14, column=5, pady=10)

    handlePaginationButtonState(currentPage, totalPages)
    
    
def createAccountsTable(parent, data):
    globals.accountsTable.destroy() if globals.accountsTable else None
    globals.accountsTable = Frame(parent)
    globals.accountsTable.pack(fill="both", expand=True)

    createTableHeader(globals.accountsTable)
    createTableBody(globals.accountsTable, records=data["data"])
    createTableFooter(globals.accountsTable, currentPage=data["current_page"], totalPages=data["total_pages"])


def createAccountsFrame(parent):
    globals.accountsFrame = Frame(parent, borderwidth=1)
    globals.accountsFrame.pack(fill="both", expand=True, padx=10)
    
    createAccountsTop(globals.accountsFrame)
    handleSearchAccount({})


def openAccounts(parent):
    try:
        createAccountsFrame(parent)
    except Exception as e:
        log.error(f"ERROR: while creating accounts frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")
    