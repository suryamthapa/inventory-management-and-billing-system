# Window to add products in inventory.

import logging
from tkinter import *
from tkinter import messagebox
import frontend.config as globals
import frontend.frames.customers as customers
from frontend.utils.customers import saveCustomer, refreshCustomersList


log = logging.getLogger("frontend")


def createAddCustomerWindow():
    try:
        addCustomerWindow = Toplevel()
        addCustomerWindow.grab_set()
        addCustomerWindow.title("Add new customer")
        addCustomerWindow.resizable(0,0)
        addCustomerWindow.iconbitmap("./frontend/assets/images/favicon.ico")

        
        addCustomerFrame = LabelFrame(addCustomerWindow, text="Customer Details", borderwidth=1)
        addCustomerFrame.pack(fill="both", padx=10, pady=10, expand=True)

        individualCustomerVar = IntVar()
        checkBtn = Checkbutton(addCustomerFrame, text = "Individual Customer", variable = individualCustomerVar,
                        onvalue = 1, offvalue = 0, width = 20, justify="left")
        checkBtn.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        Label(addCustomerFrame, text="Full Name").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        customerNameEntry = Entry(addCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        customerNameEntry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        customerNameEntry.config(state=DISABLED)

        Label(addCustomerFrame, text="Company Name").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        companyNameEntry = Entry(addCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        companyNameEntry.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        Label(addCustomerFrame, text="Company Pan No").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        companyPanNoEntry = Entry(addCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        companyPanNoEntry.grid(row=2, column=3, padx=5, pady=5, sticky=W)

        def addIndividualCustomer():
            if individualCustomerVar.get()==1:
                customerNameEntry.config(state=NORMAL)
                companyNameEntry.config(state=DISABLED)
                companyPanNoEntry.config(state=DISABLED)
            if individualCustomerVar.get()==0:
                customerNameEntry.config(state=DISABLED)
                companyNameEntry.config(state=NORMAL)
                companyPanNoEntry.config(state=NORMAL)
        checkBtn.config(command=addIndividualCustomer)
        
        Label(addCustomerFrame, text="Phone number").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        phoneNumberEntry = Entry(addCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        phoneNumberEntry.grid(row=3, column=1, padx=5, pady=5, sticky=W)
        
        Label(addCustomerFrame, text="Telephone").grid(row=3, column=2, padx=5, pady=5, sticky=W)
        telephoneEntry = Entry(addCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        telephoneEntry.grid(row=3, column=3, padx=5, pady=5, sticky=W)

        Label(addCustomerFrame, text="Email").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        emailEntry = Entry(addCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        emailEntry.grid(row=4, column=1, padx=5, pady=5, sticky=W)

        Label(addCustomerFrame, text="Address").grid(row=4, column=2, padx=5, pady=5, sticky=W)
        addressEntry = Entry(addCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        addressEntry.grid(row=4, column=3, padx=5, pady=5, sticky=W)

        def validateCustomer(quitWindow=False):
            if not customerNameEntry.get() and individualCustomerVar.get():
                customerNameEntry.focus()
                return False
            
            if companyNameEntry.get() and not individualCustomerVar.get():
                if not companyPanNoEntry.get():
                    messagebox.showerror("Add customer", "Please add Pan No of the company.")
                    companyPanNoEntry.focus()
                    return False

            if companyPanNoEntry.get() and not individualCustomerVar.get():
                if not companyNameEntry.get():
                    messagebox.showerror("Add customer", "Please add the name of the company.")
                    companyNameEntry.focus()
                    return False

            if not phoneNumberEntry.get() and not telephoneEntry.get():
                messagebox.showerror("Add customer", "Please add phone number or telephone number.")
                phoneNumberEntry.focus()
                return False

            if phoneNumberEntry.get() and len(phoneNumberEntry.get()) != 10:
                messagebox.showwarning("Invalid", "Phone number must contain 10 digits.")
                phoneNumberEntry.focus()
                return False
            
            if not addressEntry.get():
                addressEntry.focus()
                return False
            
            data = {"full_name": customerNameEntry.get() if individualCustomerVar.get() and customerNameEntry.get() else None,
                    "company":companyNameEntry.get() if not individualCustomerVar.get() and companyNameEntry.get() else None,
                    "company_pan_no":companyPanNoEntry.get() if not individualCustomerVar.get() and companyPanNoEntry.get() else None,
                    "phone_number":phoneNumberEntry.get() if phoneNumberEntry.get() else None,
                    "telephone":telephoneEntry.get() if telephoneEntry.get() else None,
                    "email":emailEntry.get() if emailEntry.get() else None,
                    "address":addressEntry.get() if addressEntry.get() else None}
            status = saveCustomer(data)

            if status:
                # refreshing products list
                refreshCustomersList()
                if globals.CURRENT_FRAME=="customersFrame":
                    # refresh auto complete values in search entry as the query column
                    field = globals.customersFilterOptionsMap.get(globals.filterOption.get())
                    globals.queryEntry.config(completevalues=[record[field] if record.get(field) else "" for record in globals.CUSTOMERS_LIST])
                    # reload the inventory table
                    customers.handleSearchCustomer(globals.CURRENT_SEARCH_QUERY.get("customers"))
                if globals.CURRENT_FRAME=="billingSystemFrame":
                    # refresh auto complete values in customers search entry in billing frame
                    field = globals.customersFilterOptionsMap.get(globals.billingCustomerfilterOption.get())
                    globals.billingCustomerNameEntry.config(completevalues=[record[field] if record.get(field) else "" for record in globals.CUSTOMERS_LIST])
            else:
                return False

            if quitWindow:
                addCustomerWindow.destroy()
                return True
            return True

        Button(addCustomerWindow,
            text="Save and quit",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : validateCustomer(quitWindow=True),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)
        
        Button(addCustomerWindow,
            text="Save",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=validateCustomer,
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        addCustomerWindow.update()
        # bring to the center of screen
        x = int((globals.screen_width/2) - (addCustomerWindow.winfo_width()/2))
        y = int((globals.screen_height/2) - (addCustomerWindow.winfo_height()/2))
        addCustomerWindow.geometry(f'{addCustomerWindow.winfo_width()}x{addCustomerWindow.winfo_height()}+{x}+{y}')
    except Exception as e:
        log.error(f"ERROR: while creating Add Customers window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")