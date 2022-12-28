# Billing system
import os
import math
import logging
from pytz import timezone
from tkinter import messagebox
import frontend.config as globals
from sqlalchemy import table
from ttkwidgets.autocomplete import AutocompleteEntry
from tkinter import *
# frontend imports
from core import nepali_datetime
import frontend.windows.dashboard as dashboard
import frontend.windows.addProducts as addProductsWindow
import frontend.windows.addVendors as addVendorsWindow
from frontend.utils.frontend import makeColumnResponsive
import frontend.utils.purchase as purchaseUtils
from core.tkNepaliCalendar import DateEntry
# backend imports
from backend.api.products import get_product
from backend.api.vendors import get_vendor


log = logging.getLogger("frontend")


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def clearVendorDetails():
        for child in globals.namePhFrame.winfo_children():
            child.destroy()
        globals.purchaseVendorNameEntry.delete(0, END)
        Label(globals.namePhFrame, text="Please load vendor details.").pack()


def clearProductDetails():
    for child in globals.rateQtyFrame.winfo_children():
        child.destroy()
    globals.rateQtyFrame.config(bg=globals.defaultBgColor)
    globals.purchaseProductNameEntry.delete(0, END)
    Label(globals.rateQtyFrame, text="Please load product details.").pack()


def loadProductDetails(parent, productDetails, toUpdate=False):
    # destroy childrens of globals.rateQtyFrame
    # before loading details of another product
    for child in parent.winfo_children():
        child.destroy()

    parent.config(bg=globals.appWhite if toUpdate else globals.defaultBgColor)
    Label(parent, text=f"Name: {productDetails['product_name']}", font=globals.appFontNormalBold).grid(row=0, column=1, columnspan=2, padx=5, pady=(5,5), sticky=W)

    Label(parent, text="Rate").grid(row=1, column=0, padx=5, pady=(5, 10), sticky=W)
    rateEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
    rateEntry.grid(row=1, column=1, padx=5, pady=(5, 10), sticky=W)
    rateEntry.insert(0, productDetails["cost_price"] if not toUpdate else productDetails["rate"])

    Label(parent, text="Quantity").grid(row=1, column=2, padx=5, pady=(5, 10), sticky=W)
    quantityEntry = Spinbox(parent, 
                            bd=globals.defaultEntryBorderWidth, 
                            font=globals.appFontNormal, 
                            from_=1, 
                            to=10000,
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
        if not quantity:
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

        productDetails["rate"] = str(rate)
        productDetails["quantity"] = str(quantity)

        addProductToPurchaseEntry(productDetails)

    def addProductToPurchaseEntry(productDetails):
        parent.config(bg=globals.defaultBgColor) if toUpdate else None
        if globals.PURCHASE_DETAILS["products"].get(productDetails["id"]) and not toUpdate:
            messagebox.showinfo("Purchase Entry System", f"'{productDetails['product_name']}' is already added!\nIf you want to update, please click update button.")
            return True

        globals.PURCHASE_DETAILS["products"][productDetails["id"]] = {"product_name": productDetails["product_name"],
                                                                "stock":productDetails["stock"],
                                                                "unit":productDetails["unit"],
                                                                "quantity":productDetails["quantity"],
                                                                "marked_price":productDetails["marked_price"],
                                                                "rate":productDetails["rate"]}
        clearProductDetails()
        createPurchaseDetailsTable(globals.purchaseDetailsFrame)

    ctaBtn = Button(parent,
        text="Add Product" if not toUpdate else "Update",
        bg=globals.appGreen,
        fg=globals.appWhite,
        width=10,
        command=validateProductDetails)
    ctaBtn.grid(row=1, column=4, pady=(5, 10), padx=5)

    makeColumnResponsive(parent)


def loadVendorDetails(parent, vendorDetails):
    try:
        log.info(f"Loading vendor -> {vendorDetails}")
        # destroy childrens of globals.rateQtyFrame
        # before loading details of another product
        for child in parent.winfo_children():
            child.destroy()

        Label(parent, text="Name").grid(row=1, column=0, padx=5, pady=10)
        vendorNameEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        vendorNameEntry.grid(row=1, column=1, padx=5, pady=10)
        vendorNameEntry.insert(0, vendorDetails["vendor_name"] if vendorDetails.get("vendor_name") else "")
        vendorNameEntry.config(state=DISABLED)

        Label(parent, text="VAT/PAN number").grid(row=1, column=2, padx=5, pady=10)
        vatNumberEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        vatNumberEntry.grid(row=1, column=3, padx=5, pady=10)
        vatNumberEntry.insert(0, vendorDetails["vat_number"] if vendorDetails.get("vat_number") else "")
        vatNumberEntry.config(state=DISABLED)
        
        Label(parent, text="Phone").grid(row=2, column=0, padx=5, pady=10)
        phEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        phEntry.grid(row=2, column=1, padx=5, pady=10)
        phEntry.insert(0, vendorDetails["phone_number"] if vendorDetails.get("phone_number") else "")
        phEntry.config(state=DISABLED)

        Label(parent, text="Telephone").grid(row=2, column=2, padx=5, pady=10)
        telEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        telEntry.grid(row=2, column=3, padx=5, pady=10)
        telEntry.insert(0, vendorDetails["telephone"] if vendorDetails.get("telephone") else "")
        telEntry.config(state=DISABLED)

        Label(parent, text="Address").grid(row=3, column=0, padx=5, pady=10)
        addressEntry = Entry(parent, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        addressEntry.grid(row=3, column=1, padx=5, pady=10)
        addressEntry.insert(0, vendorDetails["address"] if vendorDetails.get("address") else "")
        addressEntry.config(state=DISABLED)

        def addToPurchaseDetails():
            vendorData = {"vendor_id": vendorDetails["id"],
                        "vendor_name": vendorDetails["vendor_name"],
                        "vat_number": vendorDetails["vat_number"],
                        "phone_number": vendorDetails["phone_number"],
                        "telephone": vendorDetails["telephone"],
                        "address": vendorDetails["address"]}
            
            globals.PURCHASE_DETAILS["vendor"] = vendorData
            clearVendorDetails()
            createPurchaseDetailsTable(globals.purchaseDetailsFrame)

        cta = "Add Vendor" if not globals.PURCHASE_DETAILS["vendor"] else "Update Vendor"
        Button(parent,
            text=cta,
            bg=globals.appGreen,
            fg=globals.appWhite,
            width=12,
            command=addToPurchaseDetails).grid(row=3, column=3, padx=5, pady=10)

        makeColumnResponsive(parent)
    except Exception as e:
        log.exception(f"While loading vendor details -> {e}")


def createPurchaseDetailsTableHeader(parent):
    Label(parent, text="S No.", width=4, font=globals.appFontSmallBold).grid(row=1, column=0, sticky=W)
    Label(parent, text="Particulars", font=globals.appFontSmallBold).grid(row=1, column=1, sticky=W)
    Label(parent, text="QTY", width=4, font=globals.appFontSmallBold).grid(row=1, column=2, sticky=W)
    Label(parent, text="Rate", width=6, font=globals.appFontSmallBold).grid(row=1, column=3, sticky=W)
    Label(parent, text="Amount", font=globals.appFontSmallBold).grid(row=1, column=4, sticky=W)
    makeColumnResponsive(parent)


def createPurchaseDetailsTableBody(parent):
    if not globals.PURCHASE_DETAILS.get("products"):
        Label(parent, text="Please add products!").grid(columnspan=5, pady=10)
        return True
    for index, record in enumerate(globals.PURCHASE_DETAILS.get("products").items()):
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
                "stock":globals.PURCHASE_DETAILS.get("products")[id].get("stock"),
                "unit":globals.PURCHASE_DETAILS.get("products")[id].get("unit"),
                "quantity":details["quantity"],
                "marked_price":globals.PURCHASE_DETAILS.get("products")[id].get("marked_price"),
                "rate":details["rate"],
            }
            loadProductDetails(globals.rateQtyFrame, data, toUpdate=True)
        
        Button(parent, text="update", width=6, bg="#47B5FF", command=lambda id=record[0], details=record[1]: proceedToUpdate(id, details)).grid(row=index+2, column=5, pady=5, padx=(0,2), sticky=W)
        Button(parent, text="delete", width=6, bg="red", command=lambda id=record[0]: deleteProductFromCart(id)).grid(row=index+2, column=6, pady=5, padx=(2,0), sticky=W)
        
    makeColumnResponsive(parent)


def deleteProductFromCart(id):
    globals.PURCHASE_DETAILS.get("products").pop(id)
    createPurchaseDetailsTable(globals.purchaseDetailsFrame)


def createPurchaseDetailsTableFooter(parent):
    baseIndex = len(globals.PURCHASE_DETAILS.get("products")) + 6
    totalAmount = float(sum([float(record["rate"])*float(record["quantity"]) for record in globals.PURCHASE_DETAILS.get("products").values()]))
    # creating final entry
    globals.PURCHASE_DETAILS.get("final")["subtotal"] = totalAmount

    cashPayment = globals.PURCHASE_DETAILS.get("extra").get("cash_payment")
    cashPayment = float(cashPayment) if cashPayment else 0
    
    cashDiscount = globals.PURCHASE_DETAILS.get("extra").get("cash_discount")
    cashDiscount = float(cashDiscount) if cashDiscount else 0
    percentageDiscount = globals.PURCHASE_DETAILS.get("extra").get("p_discount")
    percentageDiscount = float(percentageDiscount) if percentageDiscount else 0
    extraDiscount = globals.PURCHASE_DETAILS.get("extra").get("extra_discount")
    extraDiscount = float(extraDiscount) if extraDiscount else 0

    discountByPercentage = float(totalAmount * (percentageDiscount/100))
    totalDiscountAmount = discountByPercentage + cashDiscount + extraDiscount
    globals.PURCHASE_DETAILS.get("final")["discount"] = totalDiscountAmount

    exciseDuty = globals.PURCHASE_DETAILS.get("extra").get("excise_duty")
    exciseDuty = float(exciseDuty) if exciseDuty else 0
    
    taxableAmount = float((totalAmount - totalDiscountAmount) + exciseDuty)

    vatPercentage = globals.PURCHASE_DETAILS.get("extra").get("vat")
    vatPercentage = float(vatPercentage) if vatPercentage else float(0)
    vatAmount = float(0)
    if vatPercentage:
        vatAmount = float(taxableAmount * (vatPercentage/100))
    globals.PURCHASE_DETAILS.get("final")["vat"] = vatAmount

    totalPayable = float(taxableAmount + vatAmount)
    globals.PURCHASE_DETAILS.get("final")["total"] = totalPayable

    Label(parent, text="Total:", font=globals.appFontSmallBold).grid(row=baseIndex,column=0, pady=(20, 0), sticky=W)
    Label(parent, text="Rs. {:,.2f}".format(totalAmount)).grid(row=baseIndex, column=1, pady=(20, 0), sticky=W)    

    if globals.PURCHASE_DETAILS.get("extra").get("p_discount"):
        Label(parent, text=f"Discount({globals.PURCHASE_DETAILS.get('extra').get('p_discount')}%):", font=globals.appFontSmallBold).grid(row=baseIndex+1, column=0, sticky=W)
        Label(parent, text="- Rs. {:,.2f}".format(discountByPercentage)).grid(row=baseIndex+1, column=1, sticky=W)
    
    if globals.PURCHASE_DETAILS.get("extra").get("cash_discount"):
        Label(parent, text=f"Cash Discount:", font=globals.appFontSmallBold).grid(row=baseIndex+2, column=0, sticky=W)
        Label(parent, text="- Rs. {:,.2f}".format(cashDiscount)).grid(row=baseIndex+2, column=1, sticky=W)
    
    if globals.PURCHASE_DETAILS.get("extra").get("extra_discount"):
        Label(parent, text=f"Extra Discount:", font=globals.appFontSmallBold).grid(row=baseIndex+3, column=0, sticky=W)
        Label(parent, text="- Rs. {:,.2f}".format(extraDiscount)).grid(row=baseIndex+3, column=1, sticky=W)
    
    if globals.PURCHASE_DETAILS.get("extra").get("excise_duty"):
        Label(parent, text=f"Excise Duty:", font=globals.appFontSmallBold).grid(row=baseIndex+4, column=0, sticky=W)
        Label(parent, text="Rs. {:,.2f}".format(exciseDuty)).grid(row=baseIndex+4, column=1, sticky=W)
    
    Label(parent, text=f"Taxable Amount:", font=globals.appFontSmallBold).grid(row=baseIndex+5, column=0, sticky=W)
    Label(parent, text="Rs. {:,.2f}".format(taxableAmount)).grid(row=baseIndex+5, column=1, sticky=W)
    
    if globals.PURCHASE_DETAILS.get("extra").get("vat"):
        Label(parent, text=f"VAT({globals.PURCHASE_DETAILS.get('extra').get('vat')}%):", font=globals.appFontSmallBold).grid(row=baseIndex+6, column=0, sticky=W)
        Label(parent, text="Rs. {:,.2f}".format(vatAmount)).grid(row=baseIndex+6, column=1, sticky=W)

    Label(parent, text="Grand Total:", font=globals.appFontSmallBold).grid(row=baseIndex+7, column=0, sticky=W)
    Label(parent, text="Rs. {:,.2f}".format(totalPayable)).grid(row=baseIndex+7, column=1, sticky=W)

    Label(parent, text="Cash Payment:", font=globals.appFontSmallBold).grid(row=baseIndex+7,column=2, sticky=W)
    Label(parent, text="Rs. {:,.2f}".format(cashPayment)).grid(row=baseIndex+7, column=3, sticky=W)    

    detailsCommands = LabelFrame(parent, borderwidth=0)
    detailsCommands.grid(row=baseIndex+8, column=0, columnspan=4, sticky=E, pady=5)

    def proceedToEntry():
        log.info(globals.PURCHASE_DETAILS)
        status = purchaseUtils.preprocess_purchase_details()
        if status:
            response = messagebox.askyesno("Purchase Entry System", "Are you sure?")
            if response:
                if globals.PURCHASE_DETAILS.get("id") is None:
                    entry_status = purchaseUtils.entry_purchase()
                    if not entry_status:
                        return False
                    else:
                        messagebox.showinfo("Purchase Entry System", "Purchase entry done successfully!\n\n- Products Added to inventory.\n- Stock updated.")
                        return True
                else:
                    update_status = purchaseUtils.update_purchase_entry()
                    if not update_status:
                        return False
                    else:
                        messagebox.showinfo("Purchase Entry System", "Purchase updated successfully!")
                        return True
            else:
                return False
        else:
            return False
    
    if globals.PURCHASE_DETAILS.get("id") is not None:
        Button(detailsCommands,
            text="Update Purchase Entry",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            width=20,
            command=proceedToEntry,
            state = DISABLED if not globals.PURCHASE_DETAILS else NORMAL
            ).pack(side="right", padx=3)

        clear = Button(detailsCommands,
                            text="Cancel Update",
                            bg=globals.appBlue,
                            fg=globals.appDarkGreen,
                            command=clearPurchaseEntryFrame)
        clear.pack(side="right", padx=3)
    else:
        Button(detailsCommands,
            text="Add Purchase Entry",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            width=20,
            command=proceedToEntry,
            state = DISABLED if not globals.PURCHASE_DETAILS else NORMAL
            ).pack(side="right", padx=3)

        clear = Button(detailsCommands,
                            text="Clear All",
                            bg=globals.appBlue,
                            fg=globals.appDarkGreen,
                            command=clearPurchaseEntryFrame)
        clear.pack(side="right", padx=3)

    makeColumnResponsive(parent)


def createPurchaseDetailsTableTop(parent):
    invoice_number = globals.PURCHASE_DETAILS.get("extra").get("invoice_number")
    date_of_purchase = globals.PURCHASE_DETAILS.get("extra").get("date_of_purchase")
    balance_amount = globals.PURCHASE_DETAILS.get("extra").get("balance_amount")
    balance_amount = float(balance_amount) if balance_amount else 0
    vendor_name = globals.PURCHASE_DETAILS.get("vendor").get("vendor_name")
    vat_number = globals.PURCHASE_DETAILS.get("vendor").get("vat_number")
    phone_number = globals.PURCHASE_DETAILS.get("vendor").get("phone_number")
    telephone = globals.PURCHASE_DETAILS.get("vendor").get("telephone")
    address = globals.PURCHASE_DETAILS.get("vendor").get("address")
    email = globals.PURCHASE_DETAILS.get("vendor").get("email")

    contacts = []
    if phone_number: contacts.append(phone_number) 
    if telephone: contacts.append(telephone)

    Label(parent, text="Vendor:", font=globals.appFontSmallBold).grid(row=0, column=0, pady=(5, 2), sticky=W)
    Label(parent, text=vendor_name if vendor_name else "********", wraplength=160, justify="left").grid(row=0, column=1, pady=(5, 2), sticky=W)
    
    Label(parent, text="VAT/PAN no:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=0, column=2, pady=(5, 2), sticky=W)
    Label(parent, text=vat_number if vat_number else "********", wraplength=160, justify="left").grid(row=0, column=3, pady=(5, 2), sticky=W)
    
    Label(parent, text="Contacts:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=1, column=0, pady=2, sticky=W)
    Label(parent, text=f"{', '.join(contacts)}" if contacts else "********", wraplength=160, justify="left").grid(row=1, column=1, pady=2, sticky=W)

    Label(parent, text="Address:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=1, column=2, pady=2, sticky=W)
    Label(parent, text=address if address else "**********", wraplength=160, justify="left").grid(row=1, column=3, pady=2, sticky=W)
    
    Label(parent, text="Date(dd/mm/yyyy):", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=2, column=0, pady=(7, 2), sticky=W)
    Label(parent, text=date_of_purchase if date_of_purchase else "**********", wraplength=160, justify="left").grid(row=2, column=1, pady=(7, 2), sticky=W)
    
    Label(parent, text="Invoice number:", font=globals.appFontSmallBold).grid(row=3, column=0, pady=(2, 5), sticky=W)
    Label(parent, text=f"#{invoice_number}" if invoice_number else "#********", wraplength=160, justify="left").grid(row=3, column=1, pady=(2, 5), sticky=W)

    Label(parent, text="Balance Amount:", font=globals.appFontSmallBold).grid(row=3, column=2, pady=(2, 5), sticky=W)
    Label(parent, text="Rs. {:,.2f}".format(balance_amount), wraplength=160, justify="left").grid(row=3, column=3, pady=(2, 5), sticky=W)
    
    makeColumnResponsive(parent)


def createPurchaseDetailsTable(parent):
    globals.purchaseDetailsTable.destroy() if globals.purchaseDetailsTable else None
    globals.purchaseDetailsTable = Frame(parent)
    globals.purchaseDetailsTable.pack(fill="both")

    createPurchaseDetailsTableTop(globals.purchaseDetailsTable)

    purchaseDetailsHeaderBodyMain = LabelFrame(globals.purchaseDetailsTable, text="Products")
    purchaseDetailsHeaderBodyMain.grid(row=4, columnspan=4, sticky="wens")

    canvas = Canvas(purchaseDetailsHeaderBodyMain, bg="blue", height=150)
    
    purchaseDetailsHeaderBody = Frame(canvas)
    purchaseDetailsHeaderBody.pack(fill="both", padx=5, pady=5)
    
    canvasScrollVertical = Scrollbar(purchaseDetailsHeaderBodyMain, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=canvasScrollVertical.set)
    canvasScrollHorizontal = Scrollbar(purchaseDetailsHeaderBodyMain, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=canvasScrollHorizontal.set)

    canvasScrollVertical.pack(side="right", fill="y")
    canvasScrollHorizontal.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    canvasframe = canvas.create_window(0,0, window=purchaseDetailsHeaderBody, anchor='nw')

    def frameWidth(event):
        if event.width > purchaseDetailsHeaderBody.winfo_width():
            canvas.itemconfig(canvasframe, width=event.width-4)
        if event.height > purchaseDetailsHeaderBody.winfo_height():
            canvas.itemconfig(canvasframe, height=event.height-4)

    def OnFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    canvas.bind('<Configure>', lambda e: frameWidth(e))
    purchaseDetailsHeaderBody.bind('<Configure>', lambda e: OnFrameConfigure(e))

    def _bound_to_mousewheel(event):
       canvas.bind_all("<MouseWheel>",_on_mousewheel)

    def _unbound_to_mousewheel(event):
       canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(event):
       canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    purchaseDetailsHeaderBody.bind('<Enter>',_bound_to_mousewheel)
    purchaseDetailsHeaderBody.bind('<Leave>',_unbound_to_mousewheel)

    createPurchaseDetailsTableHeader(purchaseDetailsHeaderBody)
    createPurchaseDetailsTableBody(purchaseDetailsHeaderBody)

    createPurchaseDetailsTableFooter(globals.purchaseDetailsTable)
    
    makeColumnResponsive(globals.purchaseDetailsTable)


def createVendorDetailsArea(parent):
    vendorDetailsFrame = Frame(parent)
    vendorDetailsFrame.pack(fill="x", pady=10)

    Label(vendorDetailsFrame, text="Search Vendor by", font=("TKDefault", 12)).grid(row=0, column=0, padx=(5, 1), pady=(5,10), sticky="w")
    globals.purchaseVendorNameEntry = AutocompleteEntry(vendorDetailsFrame,
                                    font=globals.appFontNormal, 
                                    completevalues=[record["vendor_name"] if record.get("vendor_name") else "" for record in globals.VENDORS_LIST])
    globals.purchaseVendorNameEntry.grid(row=0, column=2, padx=(2, 5), pady=(5,10), sticky="w")
    globals.purchaseVendorNameEntry.bind("<Return>", lambda x: proceedToLoadVendorDetails())


    def setCompleteValues():
        if globals.vendorsFilterOptionsMap.get(globals.purchaseVendorfilterOption.get()):
            column_name = globals.vendorsFilterOptionsMap.get(globals.purchaseVendorfilterOption.get())
            completevalues = [record[column_name] if record[column_name] else "" for record in globals.VENDORS_LIST]
            globals.purchaseVendorNameEntry.config(completevalues=set(completevalues))
    
    globals.purchaseVendorfilterOption = StringVar()
    globals.purchaseVendorfilterOption.set("Vendor Name")
    filters = list(globals.vendorsFilterOptionsMap.keys())
    filter = OptionMenu(vendorDetailsFrame, globals.purchaseVendorfilterOption, *filters, command=lambda x: setCompleteValues())
    filter.grid(row=0, column=1, padx=(1, 2), sticky="w", pady=(5,10))

    globals.namePhFrame = LabelFrame(vendorDetailsFrame, text="Vendor Details")
    globals.namePhFrame.grid(row=1, column=0, columnspan=5, sticky="nswe", pady=10)

    Label(globals.namePhFrame, text="Please search and load vendor details.").pack()

    def proceedToLoadVendorDetails():
        if globals.purchaseVendorNameEntry.get():
            status = False
            if globals.vendorsFilterOptionsMap.get(globals.purchaseVendorfilterOption.get()):
                toEval = f"get_vendor({globals.vendorsFilterOptionsMap.get(globals.purchaseVendorfilterOption.get())}='{globals.purchaseVendorNameEntry.get()}')"
                status, vendorDetails = eval(toEval)
            
            if status:
                loadVendorDetails(globals.namePhFrame, vendorDetails)
            else:
                for child in globals.namePhFrame.winfo_children():
                    child.destroy()
                Label(globals.namePhFrame, text="Vendor does not exist.").pack(pady=5)
                Button(globals.namePhFrame,
                    text="Add New Vendor",
                    bg=globals.appBlue,
                    fg=globals.appDarkGreen,
                    width=20,
                    command=lambda: addVendorsWindow.createAddVendorWindow()).pack(pady=5)
        else:
            globals.purchaseVendorNameEntry.focus()

    loadNamePhButton = Button(vendorDetailsFrame,
                        text="Load Details",
                        bg=globals.appBlue,
                        fg=globals.appDarkGreen,
                        width=10,
                        command=lambda: proceedToLoadVendorDetails())
    loadNamePhButton.grid(row=0, column=3, pady=(5,10), sticky="e")

    Button(vendorDetailsFrame,
        text="Clear",
        bg=globals.appBlue,
        fg=globals.appDarkGreen,
        width=10,
        command=clearVendorDetails).grid(row=0, column=4, pady=(5,10), sticky="e")
    
    makeColumnResponsive(vendorDetailsFrame)


def createProductDetailsArea(parent):
    productDetailsFrame = Frame(parent)
    productDetailsFrame.pack(fill="x", pady=10)

    Label(productDetailsFrame, text="Search Product by name", font=("TKDefault", 12)).grid(row=0, column=0, padx=5, pady=5)
    globals.purchaseProductNameEntry = AutocompleteEntry(productDetailsFrame,
                                    font=globals.appFontNormal, 
                                    completevalues=[record["product_name"] for record in globals.PRODUCTS_LIST])
    globals.purchaseProductNameEntry.grid(row=0, column=1, padx=5, pady=5)
    globals.purchaseProductNameEntry.bind("<Return>", lambda x: proceedToLoadProductDetails(globals.purchaseProductNameEntry.get()))

    globals.rateQtyFrame = LabelFrame(productDetailsFrame, text="Product Details")
    globals.rateQtyFrame.grid(row=1, column=0, columnspan=4, sticky="nswe")

    Label(globals.rateQtyFrame, text="Please search and load product details.").pack()

    def proceedToLoadProductDetails(name):
        if name:
            status, productDetails = get_product(name=name)
            if status:
                loadProductDetails(globals.rateQtyFrame, productDetails)
            else:
                for child in globals.rateQtyFrame.winfo_children():
                    child.destroy()
                Label(globals.rateQtyFrame, text="Product does not exist.").pack(pady=5)
                Button(globals.rateQtyFrame,
                    text="Add product",
                    bg=globals.appBlue,
                    fg=globals.appDarkGreen,
                    width=20,
                    command=lambda: addProductsWindow.createAddProductWindow()).pack(pady=5)
                return True
        else:
            globals.purchaseProductNameEntry.focus()
        return True

    loadRateQtyButton = Button(productDetailsFrame,
                        text="Load Details",
                        bg=globals.appBlue,
                        fg=globals.appDarkGreen,
                        width=10,
                        command=lambda: proceedToLoadProductDetails(globals.purchaseProductNameEntry.get()))
    loadRateQtyButton.grid(row=0, column=2, pady=5)


    Button(productDetailsFrame,
        text="Clear",
        bg=globals.appBlue,
        fg=globals.appDarkGreen,
        width=10,
        command=clearProductDetails).grid(row=0, column=3, pady=5)
    
    makeColumnResponsive(productDetailsFrame)


def createExtraDetailsArea(parent):
    extraDetails = LabelFrame(parent, text="Extra Details")
    extraDetails.pack(fill="x", pady=15)

    invoice_number = globals.PURCHASE_DETAILS.get("extra").get("invoice_number")
    invoice_number = invoice_number if invoice_number else ""

    date_of_purchase = globals.PURCHASE_DETAILS.get("extra").get("date_of_purchase")
    date_of_purchase = date_of_purchase if date_of_purchase else ""

    excise_duty = globals.PURCHASE_DETAILS.get("extra").get("excise_duty")
    excise_duty = excise_duty if excise_duty else ""

    cash_discount = globals.PURCHASE_DETAILS.get("extra").get("cash_discount")
    cash_discount = cash_discount if cash_discount else ""

    p_discount = globals.PURCHASE_DETAILS.get("extra").get("p_discount")
    p_discount = p_discount if p_discount else ""

    extra_discount = globals.PURCHASE_DETAILS.get("extra").get("extra_discount")
    extra_discount = extra_discount if extra_discount else ""

    vat = globals.PURCHASE_DETAILS.get("extra").get("vat")
    vat = vat if vat else ""

    cash_payment = globals.PURCHASE_DETAILS.get("extra").get("cash_payment")
    cash_payment = cash_payment if cash_payment else ""

    balance_amount = globals.PURCHASE_DETAILS.get("extra").get("balance_amount")
    balance_amount = balance_amount if balance_amount else ""

    extra_info = globals.PURCHASE_DETAILS.get("extra").get("extra_info")
    extra_info = extra_info if extra_info else ""

    Label(extraDetails, text="Invoice number").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    invoiceNumberEntry = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal, width=12)
    invoiceNumberEntry.grid(row=0, column=1, padx=5, pady=5, sticky=W)
    invoiceNumberEntry.insert(0, invoice_number)

    Label(extraDetails, text="Excuse Duty").grid(row=0, column=2, padx=5, pady=5, sticky=W)
    exciseDutyEntry = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal, width=12)
    exciseDutyEntry.grid(row=0, column=3, padx=5, pady=5, sticky=W)
    exciseDutyEntry.insert(0, excise_duty)

    Label(extraDetails, text="Date of Purchase").grid(row=0, column=4, padx=5, pady=5, sticky="nswe")
    fromDateEntry = DateEntry(extraDetails)
    fromDateEntry.grid(row=1, column=4, padx=5, pady=5, sticky="nswe")
    fromDateEntry.delete(0, END)
    fromDateEntry.insert(0,"Select date" if not date_of_purchase else date_of_purchase)

    Label(extraDetails, text="Cash Discount").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    cashDiscountEntry = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal, width=12)
    cashDiscountEntry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
    cashDiscountEntry.insert(0, cash_discount)

    Label(extraDetails, text="Percentage Discount").grid(row=1, column=2, padx=5, pady=5, sticky=W)
    percentageDiscountEntry = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal, width=12)
    percentageDiscountEntry.grid(row=1, column=3, padx=5, pady=5, sticky=W)
    percentageDiscountEntry.insert(0, p_discount)

    Label(extraDetails, text="Extra Discount").grid(row=2, column=0, padx=5, pady=5, sticky=W)
    extraDiscountEntry = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal, width=12)
    extraDiscountEntry.grid(row=2, column=1, padx=5, pady=5, sticky=W)
    extraDiscountEntry.insert(0, extra_discount)

    Label(extraDetails, text="VAT(%)").grid(row=2, column=2, padx=5, pady=5, sticky=W)
    vatEntry = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal, width=12)
    vatEntry.grid(row=2, column=3, padx=5, pady=5, sticky=W)
    vatEntry.insert(0, vat)

    Label(extraDetails, text="Cash Payment").grid(row=3, column=0, padx=5, pady=5, sticky=W)
    cashPaymentEntry = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal, width=12)
    cashPaymentEntry.grid(row=3, column=1, padx=5, pady=5, sticky=W)
    cashPaymentEntry.insert(0, cash_payment)

    Label(extraDetails, text="Balance Amount").grid(row=3, column=2, padx=5, pady=5, sticky=W)
    balanceAmountEntry = Entry(extraDetails, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal, width=12)
    balanceAmountEntry.grid(row=3, column=3, padx=5, pady=5, sticky=W)
    balanceAmountEntry.insert(0, balance_amount)

    def addExtraDetailsToBill():
        invoice_number = invoiceNumberEntry.get()
        excise_duty = exciseDutyEntry.get()
        cash_discount = cashDiscountEntry.get()
        p_discount = percentageDiscountEntry.get()
        extra_discount = extraDiscountEntry.get()
        vat = vatEntry.get()
        cash_payment = cashPaymentEntry.get()
        balance_amount = balanceAmountEntry.get()
        date_of_purchase = fromDateEntry.get()
        
        if not invoice_number:
            invoiceNumberEntry.focus()
            return False
        
        if not date_of_purchase:
            fromDateEntry.focus()
            return False

        date_of_purchase_meta = date_of_purchase.split("/")

        if len(date_of_purchase_meta)!=3:
            messagebox.showwarning("InaBi System", "Invalid Date.")
            return False
        
        for m in date_of_purchase_meta:
            if not m.isdigit():
                messagebox.showwarning("InaBi System", "Invalid Date.")
                return False
        
        if cash_payment and not isfloat(cash_payment):
            messagebox.showwarning("Invalid", "Cash Payment must be a number.")
            cashPaymentEntry.focus()
            return False

        if balance_amount and not isfloat(balance_amount):
            messagebox.showwarning("Invalid", "Balance Amount must be a number.")
            balanceAmountEntry.focus()
            return False

        if cash_discount and not isfloat(cash_discount):
            messagebox.showwarning("Invalid", "Discount must be a number.")
            cashDiscountEntry.focus()
            return False

        if extra_discount and not isfloat(extra_discount):
            messagebox.showwarning("Invalid", "Discount must be a number.")
            extraDiscountEntry.focus()
            return False

        if p_discount and not isfloat(p_discount):
            messagebox.showwarning("Invalid", "Discount percentage must be a number.")
            percentageDiscountEntry.focus()
            return False
        elif p_discount and (int(p_discount) > 100):
            messagebox.showwarning("Invalid", "Discount percentage must be less than 100.")
            percentageDiscountEntry.focus()
            return False
        
        if vat and not isfloat(vat):
            messagebox.showwarning("Invalid", "VAT percentage must be a number.")
            vatEntry.focus()
            return False
        elif vat and (int(vat) > 100):
            messagebox.showwarning("Invalid", "VAT percentage must be less than 100.")
            vatEntry.focus()
            return False

        user_year = int(date_of_purchase_meta[2])
        user_month = int(date_of_purchase_meta[1])
        if user_month > 12 or user_month < 1:
            messagebox.showwarning("InaBi System", "Invalid Date.")
            return False
        user_day = int(date_of_purchase_meta[0])
        if user_day > 32 or user_day < 1:
            messagebox.showwarning("InaBi System", "Invalid Date.")
            return False
            
        utc_timezone = timezone("UTC")

        todays_ne_datetime = nepali_datetime.datetime.now()
        user_selected_ne_datetime = todays_ne_datetime.replace(year=user_year, month=user_month, day=user_day)

        # check if user selected date is greater than today
        if user_selected_ne_datetime>todays_ne_datetime:
            messagebox.showwarning("InaBi System", "Please select date upto today only.")
            fromDateEntry.focus()
            return False

        user_selected_en_datetime = user_selected_ne_datetime.to_datetime_datetime()
        user_selected_utc_datetime = user_selected_en_datetime.astimezone(utc_timezone)
        
        globals.PURCHASE_DETAILS["extra"] = {"invoice_number": invoice_number,
                                            "excise_duty": excise_duty,
                                            "cash_discount": cash_discount,
                                            "p_discount": p_discount,
                                            "extra_discount": extra_discount,
                                            "vat": vat,
                                            "cash_payment": cash_payment,
                                            "balance_amount": balance_amount,
                                            "date_of_purchase":date_of_purchase,
                                            "date_of_purchase_utc":user_selected_utc_datetime}
        createPurchaseDetailsTable(globals.purchaseDetailsFrame)

    Button(extraDetails,
        text="Add to Entry",
        bg=globals.appGreen,
        fg=globals.appWhite,
        width=10,
        command=addExtraDetailsToBill).grid(row=3, column=4, rowspan=2, padx=5, pady=5, sticky="nswe")

    makeColumnResponsive(extraDetails)


def createDetailsArea(parent):
    detailsArea = Frame(parent)
    detailsArea.pack(side="left", fill="both", padx=(0,5), pady=10, expand=True)

    createVendorDetailsArea(detailsArea)
    createProductDetailsArea(detailsArea)
    createExtraDetailsArea(detailsArea)


def createPurchaseDetailsArea(parent):
    cartArea = Frame(parent)
    cartArea.pack(side="right", fill="both", padx=(5,0), pady=10, expand=True)

    Label(cartArea, text="Purchase Entry Details", font=globals.appFontNormalBold).pack(fill="x", pady=5)

    globals.purchaseDetailsFrame = LabelFrame(cartArea, borderwidth=2)
    globals.purchaseDetailsFrame.pack(fill="both")

    createPurchaseDetailsTable(globals.purchaseDetailsFrame)


def createPurchaseEntrySystemFrame(parent):
    globals.purchaseEntrySystemFrame = Frame(parent, borderwidth=1)
    globals.purchaseEntrySystemFrame.pack(fill="both", expand=True, padx=10, pady=10)

    detailsAndPurchaseEntryFrame = Frame(globals.purchaseEntrySystemFrame)
    detailsAndPurchaseEntryFrame.pack(fill="both", expand=True)

    createDetailsArea(detailsAndPurchaseEntryFrame)
    createPurchaseDetailsArea(detailsAndPurchaseEntryFrame)


def clearPurchaseEntryFrame(force=False):
        response = 1
        if not force:
            response = messagebox.askyesnocancel("Clear all", "Everything will reset.\nAre you sure?")
        if response==1:
            globals.PURCHASE_DETAILS.pop("id", 0)
            globals.PURCHASE_DETAILS["vendor"] = {}
            globals.PURCHASE_DETAILS["products"] = {}
            globals.PURCHASE_DETAILS["extra"] = {}
            globals.PURCHASE_DETAILS["final"] = {}
            dashboard.showFrame(globals.CURRENT_FRAME, True)


def openPurchaseEntrySystem(parent):
    try:
        createPurchaseEntrySystemFrame(parent)
    except Exception as e:
        log.exception(f"ERROR: while creating purchase system frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")