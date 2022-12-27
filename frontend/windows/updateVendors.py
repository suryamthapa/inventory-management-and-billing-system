# Window to add products in inventory.
# inbuilt module imports
import logging
from tkinter import *
from tkinter import messagebox
# frontend imports
import frontend.config as globals
import frontend.frames.vendors as vendors
from frontend.utils.vendors import updateVendor, refreshVendorsList


log = logging.getLogger("frontend")


def createUpdateVendorWindow(vendorInfo):
    try:
        updateVendorWindow = Toplevel()
        updateVendorWindow.grab_set()
        updateVendorWindow.title("Update vendor")
        updateVendorWindow.resizable(0,0)
        updateVendorWindow.iconbitmap("./frontend/assets/images/favicon.ico")

        vendor_id = vendorInfo["id"] if vendorInfo and vendorInfo.get("id") else ""
        vendor_name = vendorInfo["vendor_name"] if vendorInfo and vendorInfo.get("vendor_name") else ""
        vendorVatNo = vendorInfo["vat_number"] if vendorInfo and vendorInfo.get("vat_number") else ""
        phone_number = vendorInfo["phone_number"] if vendorInfo and vendorInfo.get("phone_number") else ""
        telephone = vendorInfo["telephone"] if vendorInfo and vendorInfo.get("telephone") else ""
        email = vendorInfo["email"] if vendorInfo and vendorInfo.get("email") else ""
        address = vendorInfo["address"] if vendorInfo and vendorInfo.get("address") else ""

        updateVendorFrame = LabelFrame(updateVendorWindow, text="Vendor Details", borderwidth=1)
        updateVendorFrame.pack(fill="both", padx=10, pady=10, expand=True)

        Label(updateVendorFrame, text="Vendor Name").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        vendorNameEntry = Entry(updateVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        vendorNameEntry.grid(row=0, column=1, padx=5, pady=5, sticky=W)
        vendorNameEntry.insert(0, vendor_name)

        Label(updateVendorFrame, text="VAT/PAN No").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        vendorVatNoEntry = Entry(updateVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        vendorVatNoEntry.grid(row=0, column=3, padx=5, pady=5, sticky=W)
        vendorVatNoEntry.insert(0, vendorVatNo)
        
        Label(updateVendorFrame, text="Phone number").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        phoneNumberEntry = Entry(updateVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        phoneNumberEntry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        phoneNumberEntry.insert(0, phone_number)
        
        Label(updateVendorFrame, text="Telephone").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        telephoneEntry = Entry(updateVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        telephoneEntry.grid(row=1, column=3, padx=5, pady=5, sticky=W)
        telephoneEntry.insert(0, telephone)

        Label(updateVendorFrame, text="Email").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        emailEntry = Entry(updateVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        emailEntry.grid(row=2, column=1, padx=5, pady=5, sticky=W)
        emailEntry.insert(0, email)

        Label(updateVendorFrame, text="Address").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        addressEntry = Entry(updateVendorFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        addressEntry.grid(row=2, column=3, padx=5, pady=5, sticky=W)
        addressEntry.insert(0, address)
        
        def handleUpdate(id):
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

            details = {"vendor_name": vendorNameEntry.get() if vendorNameEntry.get() else None,
                    "vat_number":vendorVatNoEntry.get() if vendorVatNoEntry.get() else None,
                    "phone_number":phoneNumberEntry.get() if phoneNumberEntry.get() else None,
                    "telephone":telephoneEntry.get() if telephoneEntry.get() else None,
                    "email":emailEntry.get() if emailEntry.get() else None,
                    "address":addressEntry.get() if addressEntry.get() else None}
                    
            status = updateVendor(id, details)
            updateVendorWindow.destroy()
            if status:
                # refreshing products list
                refreshVendorsList()
                if globals.CURRENT_FRAME=="vendorsFrame":
                    # refresh auto complete values in search entry
                    field = globals.vendorsFilterOptionsMap.get(globals.filterOption.get())
                    globals.queryEntry.config(completevalues=[record[field] if record.get(field) else "" for record in globals.VENDORS_LIST])
                    # reload the inventory table
                    vendors.handleSearchVendor(globals.CURRENT_SEARCH_QUERY.get("vendors"))
                if globals.CURRENT_FRAME=="billingSystemFrame":
                    # refresh auto complete values in vendors search entry in billing frame
                    field = globals.vendorsFilterOptionsMap.get(globals.billingVendorfilterOption.get())
                    globals.billingProductNameEntry.config(completevalues=[record[field] if record.get(field) else "" for record in globals.VENDORS_LIST])

        Button(updateVendorWindow,
            text="Cancel",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : updateVendorWindow.destroy(),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        Button(updateVendorWindow,
            text="Update",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : handleUpdate(vendor_id),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        updateVendorWindow.update()
        # bring to the center of screen
        x = int((globals.screen_width/2) - (updateVendorWindow.winfo_width()/2))
        y = int((globals.screen_height/2) - (updateVendorWindow.winfo_height()/2))
        updateVendorWindow.geometry(f'{updateVendorWindow.winfo_width()}x{updateVendorWindow.winfo_height()}+{x}+{y}')
    except Exception as e:
        log.exception(f"ERROR: while creating Update Vendors window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")