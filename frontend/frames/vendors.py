"""Frame for vendors""" 
# built-in module imports
import logging
from tkinter import messagebox
from tkinter import *
from ttkwidgets.autocomplete import AutocompleteEntry
# frontend imports
import frontend.config as globals
from frontend.utils.frontend import makeColumnResponsive
from frontend.utils.vendors import refreshVendorsList
import frontend.windows.updateVendors as updateVendors
import frontend.windows.addVendors as addVendors
# backend imports
from backend.api.vendors import delete_vendor, get_vendors


log = logging.getLogger("frontend")


def deleteVendor(id, name):
    response = messagebox.askyesnocancel("Delete the vendor", f"Are you sure?\n\nid: {id}\nVendor name: {name}")
    if response == 1:
        status, message = delete_vendor(id=id)
        if not status:
            messagebox.showerror("Delete Vendor", message)
        else:
            messagebox.showinfo("Delete Vendor",f"{message}")
            # refreshing products list
            refreshVendorsList()
            # reload the inventory table
            handleSearchVendor(globals.CURRENT_SEARCH_QUERY.get("vendors"))
            # refresh auto complete values in search entry
            globals.queryEntry.config(completevalues=[record["vendor_name"] if record["vendor_name"] else "" for record in globals.VENDORS_LIST])


def handleSearchVendor(queryColumnDict, page=1, limit=11, sort_column="id", asc=True):
    try:
        globals.CURRENT_SEARCH_QUERY["vendors"] = {}
        for column, query in queryColumnDict.items():
            globals.CURRENT_SEARCH_QUERY["vendors"][column] = query
        status, data = get_vendors(globals.CURRENT_SEARCH_QUERY["vendors"], page=page, limit=limit, sort_column=sort_column, asc=asc)
        
        if status:
            createVendorsTable(globals.vendorsFrame, data=data)
        else:
            Label(globals.vendorsFrame, text="Error occured while fetching products from database.").pack()
            Label(globals.vendorsFrame, text="Please check logs or contact the developer.").pack()
        return True
    except Exception as e:
        log.exception(f"ERROR: while handling Search vendor -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")


def createVendorsTop(parent):
    # For search bar and add item button
    globals.tableTop = Frame(parent)
    globals.tableTop.pack(fill="x", pady=20, padx=10)

    Label(globals.tableTop, text="Search vendor by").grid(row=0, column=0, sticky="w")

    globals.queryEntry = AutocompleteEntry(globals.tableTop,
                width=30, 
                font=20,
                completevalues=[])
    globals.queryEntry.grid(row=0, column=2, ipady=5, sticky="w")
    globals.queryEntry.bind("<Return>", lambda x: proceedToSearch())

    def setCompleteValues():
        if globals.vendorsFilterOptionsMap.get(globals.filterOption.get()):
            column_name = globals.vendorsFilterOptionsMap.get(globals.filterOption.get())
            completevalues = [str(record[column_name]) if record.get(column_name) else "" for record in globals.VENDORS_LIST]
            globals.queryEntry.config(completevalues=completevalues)
    
    globals.filterOption = StringVar()
    globals.filterOption.set("Vendor Name")
    filters = list(globals.vendorsFilterOptionsMap.keys())

    filter = OptionMenu(globals.tableTop, globals.filterOption, *filters, command=lambda x: setCompleteValues())
    filter.grid(row=0, column=1, padx=(2, 5), sticky="w")
    setCompleteValues()

    def proceedToSearch():
        
        if globals.queryEntry.get():
            if globals.vendorsFilterOptionsMap.get(globals.filterOption.get()):
                handleSearchVendor({globals.vendorsFilterOptionsMap.get(globals.filterOption.get()):globals.queryEntry.get()})
            else:
                messagebox.showwarning("Vendors", "Please select a filter to search by.")

    searchButton = Button(globals.tableTop, 
                        text="Search", 
                        width=10, 
                        bg="#47B5FF",
                        command=proceedToSearch)
    searchButton.grid(row=0, column=3, padx=5, sticky="w")

    def clearSearch():
        globals.queryEntry.delete(0, END)
        globals.queryEntry.insert(0, "")
        globals.CURRENT_SEARCH_QUERY["vendors"] = {}
        handleSearchVendor({})

    clearButton = Button(globals.tableTop,
                        text="Clear", 
                        width=10, 
                        bg="#47B5FF",
                        command=clearSearch)
    clearButton.grid(row=0, column=4, padx=5, sticky="w")

    addItemButton = Button(globals.tableTop, 
                        text="Add New Vendor", 
                        width=15, 
                        bg=globals.appBlue, 
                        command=lambda: addVendors.createAddVendorWindow())
    addItemButton.grid(row=0, column=5, padx=5, sticky="e")
    
    exportButton = Button(globals.tableTop, 
                        text="Export",
                        width=10, 
                        bg=globals.appBlue, 
                        command=lambda : messagebox.showinfo("Export Vendors", "Feature comming soon in next update!\n\nYou will be able to export vendors to an excel file with the help of this feature.\n\nThank you!"))
    exportButton.grid(row=0, column=6, padx=5, sticky="e")
    
    Grid.columnconfigure(globals.tableTop, 4, weight=1)


def createTableHeader(parent):
    Label(parent, text="ID", font=globals.appFontNormalBold).grid(row=0, column=0, sticky=W)
    Label(parent, text="Name", font=globals.appFontNormalBold).grid(row=0, column=1, sticky=W)
    Label(parent, text="VAT No", font=globals.appFontNormalBold).grid(row=0, column=2, sticky=W)
    Label(parent, text="Phone Number", font=globals.appFontNormalBold).grid(row=0, column=3, sticky=W)
    Label(parent, text="Telephone", font=globals.appFontNormalBold).grid(row=0, column=4, sticky=W)
    Label(parent, text="Email", font=globals.appFontNormalBold).grid(row=0, column=5, sticky=W)
    Label(parent, text="Address", font=globals.appFontNormalBold).grid(row=0, column=6, sticky=W)
    makeColumnResponsive(parent)


def createTableBody(parent, records):
    if not records:
        Label(parent, text="No records found!").grid(row=1, column=0, columnspan=8, pady=5)
        return True
    for index, record in enumerate(records):
        bg = "white" if (index+1)%2==0 else globals.appWhite
        Label(parent, text=record.get("id"), bg=bg).grid(row=index+1, column=0, pady=5, sticky=W),
        Label(parent, text=record.get("vendor_name") if record.get("vendor_name") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=1,pady=5, sticky=W)
        Label(parent, text=record.get("vat_number") if record.get("vat_number") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=2, pady=5, sticky=W)
        Label(parent, text=record.get("phone_number") if record.get("phone_number") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=3, pady=5, sticky=W)
        Label(parent, text=record.get("telephone") if record.get("telephone") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=4, pady=5, sticky=W)
        Label(parent, text=record.get("email") if record.get("email") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=5, pady=5, sticky=W)
        Label(parent, text=record.get("address") if record.get("address") else "---", bg=bg, wraplength=160, justify="left").grid(row=index+1, column=6, pady=5, sticky=W)
        Button(parent, text="update", width=10, bg=globals.appBlue, command=lambda x=record: updateVendors.createUpdateVendorWindow(x)).grid(row=index+1, column=7, pady=5, sticky=W)
        Button(parent, text="delete", width=10, bg="red", command=lambda id=record.get("id"), name=record.get("vendor_name"): deleteVendor(id, name)).grid(row=index+1, column=8, pady=5, sticky=W)

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

    handleSearchVendor(globals.CURRENT_SEARCH_QUERY["vendors"], page=globals.PAGINATION_PAGE, limit=globals.PAGINATION_PAGE_LIMIT)
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
    
    
def createVendorsTable(parent, data):
    globals.vendorsTable.destroy() if globals.vendorsTable else None
    globals.vendorsTable = Frame(parent)
    globals.vendorsTable.pack(fill="both", expand=True)

    createTableHeader(globals.vendorsTable)
    createTableBody(globals.vendorsTable, records=data["data"])
    createTableFooter(globals.vendorsTable, currentPage=data["current_page"], totalPages=data["total_pages"])


def createVendorsFrame(parent):
    globals.vendorsFrame = Frame(parent, borderwidth=1)
    globals.vendorsFrame.pack(fill="both", expand=True, padx=10)
    
    createVendorsTop(globals.vendorsFrame)
    handleSearchVendor({})


def openVendors(parent):
    try:
        createVendorsFrame(parent)
    except Exception as e:
        log.exception(f"ERROR: while creating vendors frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")
    