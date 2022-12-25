# Billing system
import os
import math
import logging
from tkinter import messagebox
import frontend.config as globals
from sqlalchemy import table
from ttkwidgets.autocomplete import AutocompleteEntry
from tkinter import *
# frontend imports
import frontend.windows.dashboard as dashboard
import frontend.windows.addProducts as addProductsWindow
import frontend.windows.addCustomers as addCustomersWindow
import frontend.windows.updateProducts as updateProductsWindow
import frontend.windows.payment as paymentWindow
from frontend.utils.frontend import makeColumnResponsive
from frontend.utils.products import updateProduct
import frontend.utils.bills as billUtils
# backend imports
from backend.api.products import get_product
from backend.api.customers import get_customer


log = logging.getLogger("frontend")


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def clearCustomerDetails():
        for child in globals.namePhFrame.winfo_children():
            child.destroy()
        globals.billingCustomerNameEntry.delete(0, END)
        Label(globals.namePhFrame, text="Please load customer details.").pack()


def clearProductDetails():
    for child in globals.rateQtyFrame.winfo_children():
        child.destroy()
    globals.rateQtyFrame.config(bg=globals.defaultBgColor)
    globals.billingProductNameEntry.delete(0, END)
    Label(globals.rateQtyFrame, text="Please load product details.").pack()


def loadProductDetails(parent, productDetails, toUpdate=False):
    # destroy childrens of globals.rateQtyFrame
    # before loading details of another product
    for child in parent.winfo_children():
        child.destroy()

    parent.config(bg=globals.appWhite if toUpdate else globals.defaultBgColor)
    Label(parent, text=f"Name: {productDetails['product_name']}", font=globals.appFontNormalBold).grid(row=0, column=0, columnspan=2, padx=5, pady=(5,5), sticky=W)
    Label(parent, text=f"In Stock: {productDetails['stock']}", font=globals.appFontNormalBold).grid(row=0, column=2, columnspan=2, padx=5, pady=(5,5), sticky=W)

    Label(parent, text="Rate").grid(row=1, column=0, padx=5, pady=(5, 10), sticky=W)
    rateEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
    rateEntry.grid(row=1, column=1, padx=5, pady=(5, 10), sticky=W)
    rateEntry.insert(0, productDetails["marked_price"] if not toUpdate else productDetails["rate"])

    Label(parent, text="Quantity").grid(row=1, column=2, padx=5, pady=(5, 10), sticky=W)
    quantityEntry = Spinbox(parent, 
                            bd=globals.defaultEntryBorderWidth, 
                            font=globals.appFontNormal, 
                            from_=1, 
                            to=int(productDetails["stock"]),
                            width=5)
    quantityEntry.grid(row=1, column=3, padx=5, pady=(5, 10), sticky=W)
    quantityEntry.delete(0, END)
    quantityEntry.insert(0, 1 if not toUpdate else int(productDetails["quantity"]))

    def validateProductDetails():
        rate = rateEntry.get()
        quantity = quantityEntry.get()

        if not rate:
            rateEntry.focus()
            return False
        elif  not quantity:
            quantityEntry.focus()
            return False

        if not isfloat(rate):
            messagebox.showwarning("Invalid", "Rate must be a number.")
            rateEntry.focus()
            return False
        if not quantity.isdigit():
            messagebox.showwarning("Invalid", "Quantity must be a number.")
            quantityEntry.focus()
            return False

        stockChanged = int(quantity)>int(productDetails["stock"])

        if stockChanged:
            response = messagebox.askyesno("Please confirm", 
                                        f"""Available stock: {productDetails["stock"]}\nQuantity you provided: {quantity}\n\nDo you want to update the stock in inventory?""")
            if response==1:
                updateProductsWindow.createUpdateProductWindow(productDetails)
                clearProductDetails()
                return True
            else:
                return None

        productDetails["rate"] = str(rate)
        productDetails["quantity"] = str(quantity)

        addProductToBill(productDetails)

    def addProductToBill(productDetails):
        parent.config(bg=globals.defaultBgColor) if toUpdate else None
        if globals.BILL_DETAILS["products"].get(productDetails["id"]) and not toUpdate:
            messagebox.showinfo("Billing System", f"'{productDetails['product_name']}' is already added to the bill!\nIf you want to update, please click update button.")
            return False
        if len(globals.BILL_DETAILS["products"].keys())>15:
            messagebox.showinfo("Billing System", f"You can add upto 15 products only at once.\n\nPlease generate this bill and create another bill for remaining products.\n\nThank you!")
            return False

        globals.BILL_DETAILS["products"][productDetails["id"]] = {"product_name": productDetails["product_name"],
                                                                "stock":productDetails["stock"],
                                                                "unit":productDetails["unit"],
                                                                "quantity":productDetails["quantity"],
                                                                "marked_price":productDetails["marked_price"],
                                                                "cost_price":productDetails["cost_price"],
                                                                "rate":productDetails["rate"]}
        clearProductDetails()
        createBillDetailsTable(globals.billDetailsFrame)

    ctaBtn = Button(parent,
        text="Add to Bill" if not toUpdate else "Update",
        bg=globals.appGreen,
        fg=globals.appWhite,
        width=10,
        command=validateProductDetails)
    ctaBtn.grid(row=1, column=4, pady=(5, 10), padx=5)

    makeColumnResponsive(parent)


def loadCustomerDetails(parent, customerDetails):
    try:
        log.info(f"Adding customer to bill -> {customerDetails}")
        # destroy childrens of globals.rateQtyFrame
        # before loading details of another product
        for child in parent.winfo_children():
            child.destroy()

        if customerDetails.get("full_name"):
            Label(parent, text="Name").grid(row=1, column=0, padx=5, pady=10)
            nameEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
            nameEntry.grid(row=1, column=1, padx=5, pady=10)
            nameEntry.insert(0, customerDetails["full_name"] if customerDetails.get("full_name") else "")
            nameEntry.config(state=DISABLED)

            Label(parent, text="Address").grid(row=1, column=2, padx=5, pady=10)
            addressEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
            addressEntry.grid(row=1, column=3, padx=5, pady=10)
            addressEntry.insert(0, customerDetails["address"] if customerDetails.get("address") else "")
            addressEntry.config(state=DISABLED)

        if customerDetails.get("company"):
            Label(parent, text="Company").grid(row=1, column=0, padx=5, pady=10)
            companyEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
            companyEntry.grid(row=1, column=1, padx=5, pady=10)
            companyEntry.insert(0, customerDetails["company"] if customerDetails.get("company") else "")
            companyEntry.config(state=DISABLED)

            Label(parent, text="Company Pan No").grid(row=1, column=2, padx=5, pady=10)
            companyPanEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
            companyPanEntry.grid(row=1, column=3, padx=5, pady=10)
            companyPanEntry.insert(0, customerDetails["company_pan_no"] if customerDetails.get("company_pan_no") else "")
            companyPanEntry.config(state=DISABLED)
        
        Label(parent, text="Phone").grid(row=2, column=0, padx=5, pady=10)
        phEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        phEntry.grid(row=2, column=1, padx=5, pady=10)
        phEntry.insert(0, customerDetails["phone_number"] if customerDetails.get("phone_number") else "")
        phEntry.config(state=DISABLED)

        Label(parent, text="Telephone").grid(row=2, column=2, padx=5, pady=10)
        telEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        telEntry.grid(row=2, column=3, padx=5, pady=10)
        telEntry.insert(0, customerDetails["telephone"] if customerDetails.get("telephone") else "")
        telEntry.config(state=DISABLED)

        if customerDetails.get("company"):
            Label(parent, text="Address").grid(row=3, column=0, padx=5, pady=10)
            addressEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
            addressEntry.grid(row=3, column=1, padx=5, pady=10)
            addressEntry.insert(0, customerDetails["address"] if customerDetails.get("address") else "")
            addressEntry.config(state=DISABLED)

        def addToBill():
            customerData = {"customer_id": customerDetails["id"],
                                                "full_name": customerDetails["full_name"],
                                                "phone_number": customerDetails["phone_number"] if customerDetails["phone_number"] else "",
                                                "telephone": customerDetails["telephone"] if customerDetails["telephone"] else "",
                                                "address": customerDetails["address"] if customerDetails["address"] else "",
                                                "company":customerDetails["company"] if customerDetails["company"] else "",
                                                "company_pan_no":customerDetails["company_pan_no"] if customerDetails["company_pan_no"] else ""}
            
            globals.BILL_DETAILS["customer"] = customerData
            clearCustomerDetails()
            createBillDetailsTable(globals.billDetailsFrame)

        Button(parent,
            text="Add to Bill",
            bg=globals.appGreen,
            fg=globals.appWhite,
            width=10,
            command=addToBill).grid(row=3, column=3, padx=5, pady=10)

        makeColumnResponsive(parent)
    except Exception as e:
        log.error(f"While loading customer details -> {e}")


def createBillDetailsTableHeader(parent):
    Label(parent, text="S No.", width=4, font=globals.appFontSmallBold).grid(row=1, column=0, sticky=W)
    Label(parent, text="Particulars", font=globals.appFontSmallBold).grid(row=1, column=1, sticky=W)
    Label(parent, text="QTY", width=4, font=globals.appFontSmallBold).grid(row=1, column=2, sticky=W)
    Label(parent, text="Rate", width=6, font=globals.appFontSmallBold).grid(row=1, column=3, sticky=W)
    Label(parent, text="Amount", font=globals.appFontSmallBold).grid(row=1, column=4, sticky=W)
    makeColumnResponsive(parent)


def createBillDetailsTableBody(parent):
    if not globals.BILL_DETAILS.get("products"):
        Label(parent, text="Please add products to bill!").grid(columnspan=5, pady=10)
        return True
    for index, record in enumerate(globals.BILL_DETAILS.get("products").items()):
        bg = "white" if (index+1)%2==0 else globals.appWhite
        amount = float(record[1].get("quantity")) * float(record[1].get("rate"))
        Label(parent, text=str(index+1)).grid(row=index+2, column=0, pady=5, sticky=W)
        Label(parent, text=record[1].get("product_name"), bg=bg, wraplength=140, justify=LEFT).grid(row=index+2, column=1,pady=5, sticky=W, padx=2)
        Label(parent, text=record[1].get("quantity"), bg=bg).grid(row=index+2, column=2, pady=5, sticky=W, padx=2)
        Label(parent, text="{:,.2f}".format(float(record[1].get("rate"))), bg=bg).grid(row=index+2, column=3, pady=5, sticky=W, padx=2)
        Label(parent, text="{:,.2f}".format(amount), bg=bg).grid(row=index+2, column=4, pady=5, sticky=W, padx=2)
        
        def proceedToUpdate(id, details):
            data = {
                "id": id,
                "product_name":details["product_name"],
                "stock":globals.BILL_DETAILS.get("products")[id].get("stock"),
                "unit":globals.BILL_DETAILS.get("products")[id].get("unit"),
                "quantity":details["quantity"],
                "marked_price":globals.BILL_DETAILS.get("products")[id].get("marked_price"),
                "rate":details["rate"],
            }
            loadProductDetails(globals.rateQtyFrame, data, toUpdate=True)
        
        Button(parent, text="update", width=6, bg="#47B5FF", command=lambda id=record[0], details=record[1]: proceedToUpdate(id, details)).grid(row=index+2, column=5, pady=5, padx=(0,2), sticky=W)
        Button(parent, text="delete", width=6, bg="red", command=lambda id=record[0]: deleteProductFromCart(id)).grid(row=index+2, column=6, pady=5, padx=(2,0), sticky=W)
        
    makeColumnResponsive(parent)


def deleteProductFromCart(id):
    globals.BILL_DETAILS.get("products").pop(id)
    createBillDetailsTable(globals.billDetailsFrame)


def createBillDetailsTableFooter(parent):
    askForDiscount = int(globals.CURRENT_SETTINGS.get("ask_for_discount")) if globals.CURRENT_SETTINGS.get("ask_for_discount") else 0
    askForVat = int(globals.CURRENT_SETTINGS.get("ask_for_vat")) if globals.CURRENT_SETTINGS.get("ask_for_vat") else 0
    askForTax = int(globals.CURRENT_SETTINGS.get("ask_for_tax")) if globals.CURRENT_SETTINGS.get("ask_for_tax") else 0
    defaultVat = int(globals.CURRENT_SETTINGS.get("default_vat")) if globals.CURRENT_SETTINGS.get("default_vat") else 0
    defaultDiscount = int(globals.CURRENT_SETTINGS.get("default_discount")) if globals.CURRENT_SETTINGS.get("default_discount") else 0
    defaultTax = int(globals.CURRENT_SETTINGS.get("default_tax")) if globals.CURRENT_SETTINGS.get("default_tax") else 0

    baseIndex = len(globals.BILL_DETAILS.get("products")) + 4
    totalAmount = float(sum([float(record["rate"])*float(record["quantity"]) for record in globals.BILL_DETAILS.get("products").values()]))
    # creating final entry
    globals.BILL_DETAILS.get("final")["subtotal"] = totalAmount

    discountAmount = globals.BILL_DETAILS.get("extra").get("discount_amount")
    discountAmount = float(discountAmount) if discountAmount else 0
    discountPercentage = globals.BILL_DETAILS.get("extra").get("discount_percentage") if askForDiscount else defaultDiscount
    discountPercentage = float(discountPercentage) if discountPercentage else 0
    if not discountAmount:
        discountAmount = float(totalAmount * (discountPercentage/100))
    discountedAmount = float(totalAmount - discountAmount)
    # creating final entry
    globals.BILL_DETAILS.get("final")["discount"] = discountAmount

    vatPercentage = globals.BILL_DETAILS.get("extra").get("vat") if askForVat else defaultVat
    vatPercentage = float(vatPercentage) if vatPercentage else float(0)
    vatAmount = float(0)
    if vatPercentage:
        vatAmount = float(discountedAmount * (vatPercentage/100))
    # creating final entry
    globals.BILL_DETAILS.get("final")["vat"] = vatAmount

    totalPayable = float(discountedAmount + vatAmount)
    # creating final entry
    globals.BILL_DETAILS.get("final")["total"] = totalPayable

    Label(parent, text="Total:", font=globals.appFontSmallBold).grid(row=baseIndex,column=0, pady=(20, 0), sticky=W)
    Label(parent, text="Rs. {:,.2f}".format(totalAmount)).grid(row=baseIndex, column=1, pady=(20, 0), sticky=W)
    
    if globals.BILL_DETAILS.get("extra").get("discount_percentage") or defaultDiscount:
        Label(parent, text=f"Discount({defaultDiscount}%):" if defaultDiscount else f"Discount({globals.BILL_DETAILS.get('extra').get('discount_percentage')}%):", font=globals.appFontSmallBold).grid(row=baseIndex+1, column=0, sticky=W)
        Label(parent, text="Rs. {:,.2f}".format(discountAmount)).grid(row=baseIndex+1, column=1, sticky=W)
    
    if globals.BILL_DETAILS.get("extra").get("vat") or defaultVat:
        Label(parent, text=f"VAT({defaultVat}%):" if defaultVat else f"VAT({globals.BILL_DETAILS.get('extra').get('vat')}%):", font=globals.appFontSmallBold).grid(row=baseIndex+2, column=0, sticky=W)
        Label(parent, text="Rs. {:,.2f}".format(vatAmount)).grid(row=baseIndex+2, column=1, sticky=W)
    
    if discountAmount or vatAmount or vatPercentage or defaultDiscount or defaultVat:
        Label(parent, text="Grand Total:", font=globals.appFontSmallBold).grid(row=baseIndex+3, column=0, sticky=W)
        Label(parent, text="Rs. {:,.2f}".format(totalPayable)).grid(row=baseIndex+3, column=1, sticky=W)

    detailsCommands = LabelFrame(parent, borderwidth=0)
    detailsCommands.grid(row=baseIndex+3, column=0, columnspan=4, sticky=E, pady=5)

    askForPayment = int(globals.CURRENT_SETTINGS.get("ask_for_payment")) if globals.CURRENT_SETTINGS.get("ask_for_payment") else 0
    
    def proceedToMakePayment():
        status = billUtils.preprocess_bill_details()
        if status:
            if askForPayment:
                paymentWindow.createPaymentWindow()
            else:
                billUtils.make_payment(0)
    
    cta = "Pay and Generate Bill" if askForPayment else "Generate Bill"
    Button(detailsCommands,
        text=cta,
        bg=globals.appBlue,
        fg=globals.appDarkGreen,
        width=20,
        command=proceedToMakePayment,
        state = DISABLED if not globals.BILL_DETAILS else NORMAL
        ).pack(side="right", padx=5)


    clear = Button(detailsCommands,
                        text="Clear All",
                        bg=globals.appBlue,
                        fg=globals.appDarkGreen,
                        command=clearBillingFrame)
    clear.pack(side="right", padx=5)

    makeColumnResponsive(parent)


def createBillDetailsTableTop(parent):
    name = globals.BILL_DETAILS.get("customer").get("full_name")
    company = globals.BILL_DETAILS.get("customer").get("company")
    company_pan_no = globals.BILL_DETAILS.get("customer").get("company_pan_no")
    phone_num = globals.BILL_DETAILS.get("customer").get("phone_number")
    telephone = globals.BILL_DETAILS.get("customer").get("telephone")
    address = globals.BILL_DETAILS.get("customer").get("address")
    contacts = []
    if phone_num: contacts.append(phone_num) 
    if telephone: contacts.append(telephone)

    Label(parent, text="Customer:", font=globals.appFontSmallBold).grid(row=0, column=0, pady=(10, 5), sticky=W)
    if name:
        Label(parent, text=name, wraplength=160, justify="left").grid(row=0, column=1, pady=(10, 5), sticky=W)
    elif company:
        Label(parent, text=company, wraplength=160, justify="left").grid(row=0, column=1, pady=(10, 5), sticky=W)
    else:
        Label(parent, text="********", wraplength=160, justify="left").grid(row=0, column=1, pady=(10, 5), sticky=W)
    
    if company:
        Label(parent, text="PAN no:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=0, column=2, pady=(10, 5), sticky=W)
        Label(parent, text=company_pan_no if company_pan_no else "**********", wraplength=160, justify="left").grid(row=0, column=3, pady=(10, 5), sticky=W)
    elif name:
        Label(parent, text="Address:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=0, column=2, pady=(10, 5), sticky=W)
        Label(parent, text=address if address else "**********", wraplength=160, justify="left").grid(row=0, column=3, pady=(10, 5), sticky=W)
    
    Label(parent, text="Contacts:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=1, column=0, pady=(5, 10), sticky=W)
    Label(parent, text=f"{', '.join(contacts)}" if contacts else "********", wraplength=160, justify="left").grid(row=1, column=1, pady=(5, 10), sticky=W)

    if company:
        Label(parent, text="Address:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=1, column=2, pady=(5, 10), sticky=W)
        Label(parent, text=address if address else "**********", wraplength=160, justify="left").grid(row=1, column=3, pady=(5, 10), sticky=W)
    
    makeColumnResponsive(parent)


def createBillDetailsTable(parent):
    globals.billDetailsTable.destroy() if globals.billDetailsTable else None
    globals.billDetailsTable = Frame(parent)
    globals.billDetailsTable.pack(fill="both")

    createBillDetailsTableTop(globals.billDetailsTable)

    billDetailsHeaderBodyMain = LabelFrame(globals.billDetailsTable, text="Products")
    billDetailsHeaderBodyMain.grid(row=2, columnspan=4, sticky="wens")

    canvas = Canvas(billDetailsHeaderBodyMain, bg="blue", height=220)
    
    billDetailsHeaderBody = Frame(canvas)
    billDetailsHeaderBody.pack(fill="both", padx=5, pady=5)
    
    canvasScrollVertical = Scrollbar(billDetailsHeaderBodyMain, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=canvasScrollVertical.set)
    canvasScrollHorizontal = Scrollbar(billDetailsHeaderBodyMain, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=canvasScrollHorizontal.set)

    canvasScrollVertical.pack(side="right", fill="y")
    canvasScrollHorizontal.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    canvasframe = canvas.create_window(0,0, window=billDetailsHeaderBody, anchor='nw')

    def frameWidth(event):
        if event.width > billDetailsHeaderBody.winfo_width():
            canvas.itemconfig(canvasframe, width=event.width-4)
        if event.height > billDetailsHeaderBody.winfo_height():
            canvas.itemconfig(canvasframe, height=event.height-4)

    def OnFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    canvas.bind('<Configure>', lambda e: frameWidth(e))
    billDetailsHeaderBody.bind('<Configure>', lambda e: OnFrameConfigure(e))

    def _bound_to_mousewheel(event):
       canvas.bind_all("<MouseWheel>",_on_mousewheel)

    def _unbound_to_mousewheel(event):
       canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(event):
       canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    billDetailsHeaderBody.bind('<Enter>',_bound_to_mousewheel)
    billDetailsHeaderBody.bind('<Leave>',_unbound_to_mousewheel)

    createBillDetailsTableHeader(billDetailsHeaderBody)
    createBillDetailsTableBody(billDetailsHeaderBody)

    createBillDetailsTableFooter(globals.billDetailsTable)
    
    makeColumnResponsive(globals.billDetailsTable)


def createCustomerDetailsArea(parent):
    customerDetailsFrame = Frame(parent)
    customerDetailsFrame.pack(fill="x", pady=20)

    Label(customerDetailsFrame, text="Search Customer by", font=("TKDefault", 12)).grid(row=0, column=0, padx=(5, 1), pady=(5,10), sticky="w")
    globals.billingCustomerNameEntry = AutocompleteEntry(customerDetailsFrame,
                                    font=globals.appFontNormal, 
                                    completevalues=[record["company"] if record["company"] else "" for record in globals.CUSTOMERS_LIST])
    globals.billingCustomerNameEntry.grid(row=0, column=2, padx=(2, 5), pady=(5,10), sticky="w")
    globals.billingCustomerNameEntry.bind("<Return>", lambda x: proceedToLoadCustomerDetails())

    filterOptionsMap = {
            "Individual Name": "full_name",
            "Company Name": "company",
            "Phone Number": "phone_number",
            "Telephone": "telephone",
            "Email": "email"
        }

    def setCompleteValues():
        if filterOptionsMap.get(globals.billingCustomerfilterOption.get()):
            column_name = filterOptionsMap.get(globals.billingCustomerfilterOption.get())
            completevalues = [record[column_name] if record[column_name] else "" for record in globals.CUSTOMERS_LIST]
            globals.billingCustomerNameEntry.config(completevalues=completevalues)
    
    globals.billingCustomerfilterOption = StringVar()
    globals.billingCustomerfilterOption.set("Company Name")
    filters = list(filterOptionsMap.keys())
    filter = OptionMenu(customerDetailsFrame, globals.billingCustomerfilterOption, *filters, command=lambda x: setCompleteValues())
    filter.grid(row=0, column=1, padx=(1, 2), sticky="w", pady=(5,10))

    globals.namePhFrame = LabelFrame(customerDetailsFrame, text="Customer Details")
    globals.namePhFrame.grid(row=1, column=0, columnspan=5, sticky="nswe", pady=10)

    Label(globals.namePhFrame, text="Please search and load customer details.").pack()

    def proceedToLoadCustomerDetails():
        if globals.billingCustomerNameEntry.get():
            status = False
            if filterOptionsMap.get(globals.billingCustomerfilterOption.get()):
                toEval = f"get_customer({filterOptionsMap.get(globals.billingCustomerfilterOption.get())}='{globals.billingCustomerNameEntry.get()}')"
                status, customerDetails = eval(toEval)
            
            if status:
                loadCustomerDetails(globals.namePhFrame, customerDetails)
            else:
                for child in globals.namePhFrame.winfo_children():
                    child.destroy()
                Label(globals.namePhFrame, text="Customer does not exist.").pack(pady=5)
                Button(globals.namePhFrame,
                    text="Add Customer",
                    bg=globals.appBlue,
                    fg=globals.appDarkGreen,
                    width=20,
                    command=lambda: addCustomersWindow.createAddCustomerWindow()).pack(pady=5)
        else:
            globals.billingCustomerNameEntry.focus()

    loadNamePhButton = Button(customerDetailsFrame,
                        text="Load Details",
                        bg=globals.appBlue,
                        fg=globals.appDarkGreen,
                        width=10,
                        command=lambda: proceedToLoadCustomerDetails())
    loadNamePhButton.grid(row=0, column=3, pady=(5,10), sticky="e")

    Button(customerDetailsFrame,
        text="Clear",
        bg=globals.appBlue,
        fg=globals.appDarkGreen,
        width=10,
        command=clearCustomerDetails).grid(row=0, column=4, pady=(5,10), sticky="e")
    
    makeColumnResponsive(customerDetailsFrame)


def createProductDetailsArea(parent):
    productDetailsFrame = Frame(parent)
    productDetailsFrame.pack(fill="x", pady=20)

    Label(productDetailsFrame, text="Search Product by name", font=("TKDefault", 12)).grid(row=0, column=0, padx=5, pady=5)
    globals.billingProductNameEntry = AutocompleteEntry(productDetailsFrame,
                                    font=globals.appFontNormal, 
                                    completevalues=[record["product_name"] for record in globals.PRODUCTS_LIST])
    globals.billingProductNameEntry.grid(row=0, column=1, padx=5, pady=5)
    globals.billingProductNameEntry.bind("<Return>", lambda x: proceedToLoadProductDetails(globals.billingProductNameEntry.get()))

    globals.rateQtyFrame = LabelFrame(productDetailsFrame, text="Product Details")
    globals.rateQtyFrame.grid(row=1, column=0, columnspan=4, sticky="nswe")

    Label(globals.rateQtyFrame, text="Please search and load product details.").pack()

    def proceedToLoadProductDetails(name):
        if name:
            status, productDetails = get_product(name=name)
            if status:
                if int(productDetails["stock"])==0:
                    for child in globals.rateQtyFrame.winfo_children():
                        child.destroy()
                    Label(globals.rateQtyFrame, text="Product out of Stock.").pack(pady=5)
                    Button(globals.rateQtyFrame,
                        text="Add Stock",
                        bg=globals.appBlue,
                        fg=globals.appDarkGreen,
                        width=20,
                        command=lambda: updateProductsWindow.createUpdateProductWindow(productDetails)).pack(pady=5)
                    return True
                else:
                    loadProductDetails(globals.rateQtyFrame, productDetails)
            else:
                for child in globals.rateQtyFrame.winfo_children():
                    child.destroy()
                Label(globals.rateQtyFrame, text="Product does not exist.").pack(pady=5)
                Button(globals.rateQtyFrame,
                    text="Add to inventory",
                    bg=globals.appBlue,
                    fg=globals.appDarkGreen,
                    width=20,
                    command=lambda: addProductsWindow.createAddProductWindow()).pack(pady=5)
                return True
            
        else:
            globals.billingProductNameEntry.focus()
        return True

    loadRateQtyButton = Button(productDetailsFrame,
                        text="Load Details",
                        bg=globals.appBlue,
                        fg=globals.appDarkGreen,
                        width=10,
                        command=lambda: proceedToLoadProductDetails(globals.billingProductNameEntry.get()))
    loadRateQtyButton.grid(row=0, column=2, pady=5)


    Button(productDetailsFrame,
        text="Clear",
        bg=globals.appBlue,
        fg=globals.appDarkGreen,
        width=10,
        command=clearProductDetails).grid(row=0, column=3, pady=5)
    
    makeColumnResponsive(productDetailsFrame)


def createExtraDetailsArea(parent):
    askForDiscount = int(globals.CURRENT_SETTINGS.get("ask_for_discount")) if globals.CURRENT_SETTINGS.get("ask_for_discount") else 0
    askForVat = int(globals.CURRENT_SETTINGS.get("ask_for_vat")) if globals.CURRENT_SETTINGS.get("ask_for_vat") else 0
    askForTax = int(globals.CURRENT_SETTINGS.get("ask_for_tax")) if globals.CURRENT_SETTINGS.get("ask_for_tax") else 0

    extraDetails = LabelFrame(parent, text="Extra")
    extraDetails.pack(fill="x", pady=20)

    dA = globals.BILL_DETAILS.get("extra").get("discount_amount")
    dA = dA if dA else ""
    dP = globals.BILL_DETAILS.get("extra").get("discount_percentage")
    dP = dP if dP else ""
    v = globals.BILL_DETAILS.get("extra").get("vat")
    v = v if v else ""
    t = globals.BILL_DETAILS.get("extra").get("tax")
    t = t if t else ""

    Label(extraDetails, text="Discount(Amount)").grid(row=0, column=0, padx=5, sticky=W)
    discountAmount = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
    discountAmount.grid(row=0, column=1, padx=5, pady=5, sticky=W)
    discountAmount.insert(0, dA)
    discountAmount.config(state=NORMAL if askForDiscount else DISABLED)

    Label(extraDetails, text="Discount(%)").grid(row=0, column=2, padx=5, sticky=W)
    discountPercentage = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
    discountPercentage.grid(row=0, column=3, padx=5, pady=5, sticky=W)
    discountPercentage.insert(0, dP)
    discountPercentage.config(state=NORMAL if askForDiscount else DISABLED)

    Label(extraDetails, text="VAT(%)").grid(row=1, column=0, padx=5, sticky=W)
    vatPercentage = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
    vatPercentage.grid(row=1, column=1, padx=5, pady=5, sticky=W)
    vatPercentage.insert(0, v)
    vatPercentage.config(state=NORMAL if askForVat else DISABLED)

    Label(extraDetails, text="TAX(%)").grid(row=1, column=2, padx=5, sticky=W)
    taxPercentage = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
    taxPercentage.grid(row=1, column=3, padx=5, pady=5, sticky=W)
    taxPercentage.insert(0, v)
    taxPercentage.config(state=NORMAL if askForTax else DISABLED)

    def addExtraDetailsToBill():
        dA = discountAmount.get()
        dP = discountPercentage.get()
        v = vatPercentage.get()
        t = taxPercentage.get()

        if not dA and not dP and not v:
            return False
        
        if  dA and dP:
            messagebox.showwarning("Billing system", "You can add either discount amount or discount percentage.\nYou can not add both.")
            return False

        if dA and not dA.isdigit():
            messagebox.showwarning("Invalid", "Discount amount must be a number.")
            discountAmount.focus()
            return False

        if dP and not dP.isdigit():
            messagebox.showwarning("Invalid", "Discount percentage must be a number.")
            discountPercentage.focus()
            return False
        elif dP and (int(dP) > 100):
            messagebox.showwarning("Invalid", "Discount percentage must not be higher than 100.")
            discountPercentage.focus()
            return False
        
        if v and not v.isdigit():
            messagebox.showwarning("Invalid", "VAT percentage must be a number.")
            vatPercentage.focus()
            return False
        elif v and (int(v) > 100):
            messagebox.showwarning("Invalid", "VAT percentage must not be higher than 100.")
            discountPercentage.focus()
            return False
        
        if t and not t.isdigit():
            messagebox.showwarning("Invalid", "Tax percentage must be a number.")
            taxPercentage.focus()
            return False
        elif t and (int(t) > 100):
            messagebox.showwarning("Invalid", "Tax percentage must not be higher than 100.")
            taxPercentage.focus()
            return False
        
        globals.BILL_DETAILS["extra"] = {"discount_amount": dA,
                                        "discount_percentage": dP,
                                        "vat": v,
                                        "tax": t,}
        createBillDetailsTable(globals.billDetailsFrame)

    Button(extraDetails,
        text="Add to Bill",
        bg=globals.appGreen,
        fg=globals.appWhite,
        width=10,
        command=addExtraDetailsToBill).grid(row=1, column=4, rowspan=2, padx=5, pady=5)

    makeColumnResponsive(extraDetails)


def createDetailsArea(parent):
    detailsArea = Frame(parent)
    detailsArea.pack(side="left", fill="both", padx=(0,5), pady=10, expand=True)

    createCustomerDetailsArea(detailsArea)
    createProductDetailsArea(detailsArea)

    askForDiscount = int(globals.CURRENT_SETTINGS.get("ask_for_discount")) if globals.CURRENT_SETTINGS.get("ask_for_discount") else 0
    askForVat = int(globals.CURRENT_SETTINGS.get("ask_for_vat")) if globals.CURRENT_SETTINGS.get("ask_for_vat") else 0
    askForTax = int(globals.CURRENT_SETTINGS.get("ask_for_tax")) if globals.CURRENT_SETTINGS.get("ask_for_tax") else 0

    if askForDiscount or askForVat or askForTax:
        createExtraDetailsArea(detailsArea)


def createBillDetailsArea(parent):
    cartArea = Frame(parent)
    cartArea.pack(side="right", fill="both", padx=(5,0), pady=10, expand=True)

    Label(cartArea, text="Billing Details", font=globals.appFontNormalBold).pack(fill="x", pady=5)

    globals.billDetailsFrame = LabelFrame(cartArea, borderwidth=2)
    globals.billDetailsFrame.pack(fill="both")

    createBillDetailsTable(globals.billDetailsFrame)


def createBillingSystemFrame(parent):
    globals.billingSystemFrame = Frame(parent, borderwidth=1)
    globals.billingSystemFrame.pack(fill="both", expand=True, padx=10, pady=10)

    detailsAndBillingFrame = Frame(globals.billingSystemFrame)
    detailsAndBillingFrame.pack(fill="both", expand=True)

    createDetailsArea(detailsAndBillingFrame)
    createBillDetailsArea(detailsAndBillingFrame)
    

def clearBillingFrame(force=False):
        response = 1
        if not force:
            response = messagebox.askyesnocancel("Clear all", "Everything will reset.\nAre you sure?")
        if response==1:
            globals.BILL_DETAILS["customer"] = {}
            globals.BILL_DETAILS["products"] = {}
            globals.BILL_DETAILS["extra"] = {}
            globals.BILL_DETAILS["final"] = {}
        dashboard.showFrame(globals.CURRENT_FRAME, True)


def openBillingSystem(parent):
    try:
        createBillingSystemFrame(parent)
    except Exception as e:
        log.error(f"ERROR: while creating billing system frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")