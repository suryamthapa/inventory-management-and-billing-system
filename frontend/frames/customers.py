"""Frame for customers""" 
# built-in module imports
import logging
from tkinter import messagebox
from tkinter import *
from ttkwidgets.autocomplete import AutocompleteEntry
# frontend imports
import frontend.config as globals
from frontend.utils.frontend import makeColumnResponsive
from frontend.utils.customers import refreshCustomersList
import frontend.windows.updateCustomers as updateCustomers
import frontend.windows.addCustomers as addCustomers
# backend imports
from backend.api.customers import delete_customer, get_customers


log = logging.getLogger("frontend")


def deleteCustomer(id, name):
    response = messagebox.askyesnocancel("Delete the customer", f"Are you sure?\n\nid: {id}\nCustomer name: {name}")
    if response == 1:
        status, message = delete_customer(id=id)
        if not status:
            messagebox.showerror("Delete Customer", message)
        else:
            messagebox.showinfo("Delete Customer",f"{message}")
            # refreshing products list
            refreshCustomersList()
            # reload the inventory table
            handleSearchCustomer(globals.CURRENT_SEARCH_QUERY.get("customers"))
            # refresh auto complete values in search entry
            globals.queryEntry.config(completevalues=[record["full_name"] if record["full_name"] else "" for record in globals.CUSTOMERS_LIST])


def handleSearchCustomer(queryColumnDict, page=1, limit=11, sort_column="id", asc=True):
    globals.CURRENT_SEARCH_QUERY["customers"] = {}
    for column, query in queryColumnDict.items():
        globals.CURRENT_SEARCH_QUERY["customers"][column] = query
    status, data = get_customers(globals.CURRENT_SEARCH_QUERY["customers"], page=page, limit=limit, sort_column=sort_column, asc=asc)
    
    if status:
        createCustomersTable(globals.customersFrame, data=data)
    else:
        Label(globals.customersFrame, text="Error occured while fetching products from database.").pack()
        Label(globals.customersFrame, text="Please check logs or contact the developer.").pack()
    return True


def createCustomersTop(parent):
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
                handleSearchCustomer({filterOptionsMap.get(filterOption.get()):globals.queryEntry.get()})
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
        handleSearchCustomer({})

    clearButton = Button(globals.tableTop,
                        text="Clear", 
                        width=10, 
                        bg="#47B5FF",
                        command=clearSearch)
    clearButton.grid(row=0, column=4, padx=5, sticky="w")

    addItemButton = Button(globals.tableTop, 
                        text="Add New Customer", 
                        width=15, 
                        bg=globals.appBlue, 
                        command=lambda: addCustomers.createAddCustomerWindow())
    addItemButton.grid(row=0, column=5, padx=5, sticky="e")
    
    exportButton = Button(globals.tableTop, 
                        text="Export",
                        width=10, 
                        bg=globals.appBlue, 
                        command=lambda : messagebox.showinfo("Export Customers", "Feature comming soon in next update!\n\nYou will be able to export customers to an excel file with the help of this feature.\n\nThank you!"))
    exportButton.grid(row=0, column=6, padx=5, sticky="e")
    
    Grid.columnconfigure(globals.tableTop, 4, weight=1)


def createTableHeader(parent):
    Label(parent, text="ID", font=globals.appFontNormalBold).grid(row=0, column=0, sticky=W)
    Label(parent, text="Name", font=globals.appFontNormalBold).grid(row=0, column=1, sticky=W)
    Label(parent, text="Company", font=globals.appFontNormalBold).grid(row=0, column=2, sticky=W)
    Label(parent, text="PAN no", font=globals.appFontNormalBold).grid(row=0, column=3, sticky=W)
    Label(parent, text="Phone Number", font=globals.appFontNormalBold).grid(row=0, column=4, sticky=W)
    Label(parent, text="Telephone", font=globals.appFontNormalBold).grid(row=0, column=5, sticky=W)
    Label(parent, text="Email", font=globals.appFontNormalBold).grid(row=0, column=6, sticky=W)
    Label(parent, text="Address", font=globals.appFontNormalBold).grid(row=0, column=7, sticky=W)
    makeColumnResponsive(parent)


def createTableBody(parent, records):
    if not records:
        Label(parent, text="No records found!").grid(row=1, column=0, columnspan=8, pady=5)
        return True
    for index, record in enumerate(records):
        bg = "white" if (index+1)%2==0 else globals.appWhite
        Label(parent, text=record.get("id"), bg=bg).grid(row=index+1, column=0, pady=5, sticky=W),
        Label(parent, text=record.get("full_name") if record.get("full_name") else "---", bg=bg).grid(row=index+1, column=1,pady=5, sticky=W)
        Label(parent, text=record.get("company") if record.get("company") else "---", bg=bg).grid(row=index+1, column=2, pady=5, sticky=W)
        Label(parent, text=record.get("company_pan_no") if record.get("company_pan_no") else "---", bg=bg).grid(row=index+1, column=3, pady=5, sticky=W)
        Label(parent, text=record.get("phone_number") if record.get("phone_number") else "---", bg=bg).grid(row=index+1, column=4, pady=5, sticky=W)
        Label(parent, text=record.get("telephone") if record.get("telephone") else "---", bg=bg).grid(row=index+1, column=5, pady=5, sticky=W)
        Label(parent, text=record.get("email") if record.get("email") else "---", bg=bg).grid(row=index+1, column=6, pady=5, sticky=W)
        Label(parent, text=record.get("address") if record.get("address") else "---", bg=bg).grid(row=index+1, column=7, pady=5, sticky=W)
        Button(parent, text="update", width=10, bg=globals.appBlue, command=lambda x=record: updateCustomers.createUpdateCustomerWindow(x)).grid(row=index+1, column=8, pady=5, sticky=W)
        Button(parent, text="delete", width=10, bg="red", command=lambda id=record.get("id"), name=record.get("full_name"): deleteCustomer(id, name)).grid(row=index+1, column=9, pady=5, sticky=W)
        Button(parent, text="View Sales", width=10, bg=globals.appBlue, command=lambda : messagebox.showinfo("Sales and Analytics", "Feature comming soon in next update!\n\nYou will be able to view the sales and analytics of specific customer with the help of this feature.\n\nThank you!")).grid(row=index+1, column=10, pady=5, sticky=W)

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

    handleSearchCustomer(globals.CURRENT_SEARCH_QUERY["customers"], page=globals.PAGINATION_PAGE, limit=globals.PAGINATION_PAGE_LIMIT)
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
    globals.paginationBackButton.grid(row=14, column=8, pady=10)

    globals.paginationPageInfo = Label(parent, text=f"Page {currentPage} out of {totalPages}")
    globals.paginationPageInfo.grid(row=globals.PAGINATION_PAGE_LIMIT+3, column=9, pady=10)
    
    globals.paginationForwardButton = Button(parent, 
                                            text=">>", 
                                            bg=globals.appGreen, 
                                            fg=globals.appWhite, 
                                            command=lambda : handlePagination(currentPage, totalPages, "forward"))
    globals.paginationForwardButton.grid(row=14, column=10, pady=10)

    handlePaginationButtonState(currentPage, totalPages)
    
    
def createCustomersTable(parent, data):
    globals.customersTable.destroy() if globals.customersTable else None
    globals.customersTable = Frame(parent)
    globals.customersTable.pack(fill="both", expand=True)

    createTableHeader(globals.customersTable)
    createTableBody(globals.customersTable, records=data["data"])
    createTableFooter(globals.customersTable, currentPage=data["current_page"], totalPages=data["total_pages"])


def createCustomersFrame(parent):
    globals.customersFrame = Frame(parent, borderwidth=1)
    globals.customersFrame.pack(fill="both", expand=True, padx=10)
    
    createCustomersTop(globals.customersFrame)
    handleSearchCustomer({})


def openCustomers(parent):
    try:
        createCustomersFrame(parent)
    except Exception as e:
        log.error(f"ERROR: while creating customers frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")
    