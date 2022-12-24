# Window to add products in inventory.

import logging
from tkinter import *
from tkinter import messagebox
import frontend.config as globals
import frontend.frames.vendors as vendors
from frontend.utils.vendors import saveVendor, refreshVendorsList


log = logging.getLogger("frontend")


def createAddVendorWindow():
    try:
        addVendorWindow = Toplevel()
        addVendorWindow.grab_set()
        addVendorWindow.title("Add new vendor")
        addVendorWindow.resizable(0,0)
        addVendorWindow.iconbitmap("./frontend/assets/images/favicon.ico")

        addVendorFrame = LabelFrame(addVendorWindow, text="Vendor Details", borderwidth=1)
        addVendorFrame.pack(fill="both", padx=10, pady=10, expand=True)

        Label(addVendorFrame, text="Vendor Name").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        vendorNameEntry = Entry(addVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        vendorNameEntry.grid(row=0, column=1, padx=5, pady=5, sticky=W)

        Label(addVendorFrame, text="VAT/PAN No").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        vendorVatNoEntry = Entry(addVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        vendorVatNoEntry.grid(row=0, column=3, padx=5, pady=5, sticky=W)
        
        Label(addVendorFrame, text="Phone number").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        phoneNumberEntry = Entry(addVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        phoneNumberEntry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        
        Label(addVendorFrame, text="Telephone").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        telephoneEntry = Entry(addVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        telephoneEntry.grid(row=1, column=3, padx=5, pady=5, sticky=W)

        Label(addVendorFrame, text="Email").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        emailEntry = Entry(addVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        emailEntry.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        Label(addVendorFrame, text="Address").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        addressEntry = Entry(addVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        addressEntry.grid(row=2, column=3, padx=5, pady=5, sticky=W)

        def validateVendor(quitWindow=False):
            if not vendorNameEntry.get():
                vendorNameEntry.focus()
                return False

            if not vendorVatNoEntry.get():
                vendorVatNoEntry.focus()
                return False

            if not phoneNumberEntry.get() and not telephoneEntry.get():
                messagebox.showerror("Add vendor", "Please add phone number or telephone number.")
                phoneNumberEntry.focus()
                return False

            if phoneNumberEntry.get() and len(phoneNumberEntry.get()) != 10:
                messagebox.showwarning("Invalid", "Phone number must contain 10 digits.")
                phoneNumberEntry.focus()
                return False
            
            if not addressEntry.get():
                addressEntry.focus()
                return False
            
            data = {"vendor_name": vendorNameEntry.get() if vendorNameEntry.get() else None,
                    "vat_number":vendorVatNoEntry.get() if vendorVatNoEntry.get() else None,
                    "phone_number":phoneNumberEntry.get() if phoneNumberEntry.get() else None,
                    "telephone":telephoneEntry.get() if telephoneEntry.get() else None,
                    "email":emailEntry.get() if emailEntry.get() else None,
                    "address":addressEntry.get() if addressEntry.get() else None}
            status = saveVendor(data)

            if status:
                # refreshing products list
                refreshVendorsList()
                if globals.CURRENT_FRAME=="vendorsFrame":
                    # refresh auto complete values in search entry as the query column
                    field = globals.vendorsFilterOptionsMap.get(globals.filterOption.get())
                    globals.queryEntry.config(completevalues=[record[field] if record.get(field) else "" for record in globals.VENDORS_LIST])
                    # reload the inventory table
                    vendors.handleSearchVendor(globals.CURRENT_SEARCH_QUERY.get("vendors"))
                if globals.CURRENT_FRAME=="billingSystemFrame":
                    # refresh auto complete values in vendors search entry in billing frame
                    field = globals.vendorsFilterOptionsMap.get(globals.billingVendorfilterOption.get())
                    globals.billingVendorNameEntry.config(completevalues=[record[field] if record.get(field) else "" for record in globals.VENDORS_LIST])
            else:
                return False

            if quitWindow:
                addVendorWindow.destroy()
                return True
            return True

        Button(addVendorWindow,
            text="Save and quit",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : validateVendor(quitWindow=True),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)
        
        Button(addVendorWindow,
            text="Save",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=validateVendor,
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        addVendorWindow.update()
        # bring to the center of screen
        x = int((globals.screen_width/2) - (addVendorWindow.winfo_width()/2))
        y = int((globals.screen_height/2) - (addVendorWindow.winfo_height()/2))
        addVendorWindow.geometry(f'{addVendorWindow.winfo_width()}x{addVendorWindow.winfo_height()}+{x}+{y}')
    except Exception as e:
        log.error(f"ERROR: while creating Add Vendors window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")