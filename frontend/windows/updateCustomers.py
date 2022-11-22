# Window to add products in inventory.
# inbuilt module imports
import logging
from tkinter import *
from tkinter import messagebox
# frontend imports
import frontend.config as globals
import frontend.frames.customers as customers
from frontend.utils.customers import updateCustomer, refreshCustomersList


log = logging.getLogger("frontend")


def createUpdateCustomerWindow(customerInfo):
    try:
        updateCustomerWindow = Toplevel()
        updateCustomerWindow.grab_set()
        updateCustomerWindow.title("Update customer")
        updateCustomerWindow.resizable(0,0)
        updateCustomerWindow.iconbitmap("./frontend/assets/images/favicon.ico")

        customer_id = customerInfo["id"] if customerInfo and customerInfo["id"] else ""
        full_name = customerInfo["full_name"] if customerInfo and customerInfo["full_name"] else ""
        company = customerInfo["company"] if customerInfo and customerInfo["company"] else ""
        companyPanNo = customerInfo["company_pan_no"] if customerInfo and customerInfo["company_pan_no"] else ""
        phone_number = customerInfo["phone_number"] if customerInfo and customerInfo["phone_number"] else ""
        telephone = customerInfo["telephone"] if customerInfo and customerInfo["telephone"] else ""
        email = customerInfo["email"] if customerInfo and customerInfo["email"] else ""
        address = customerInfo["address"] if customerInfo and customerInfo["address"] else ""

        updateCustomerFrame = LabelFrame(updateCustomerWindow, text="Customer Details", borderwidth=1)
        updateCustomerFrame.pack(fill="both", padx=10, pady=10, expand=True)

        individualCustomerVar = IntVar()
        if full_name:
            individualCustomerVar.set(1)

        checkBtn = Checkbutton(updateCustomerFrame, text = "Individual Customer", variable = individualCustomerVar,
                        onvalue = 1, offvalue = 0, width = 20, justify="left")
        checkBtn.grid(row=0, column=0, padx=5, pady=5, sticky=W)

        Label(updateCustomerFrame, text="Full Name", justify="left").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        customerNameEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        customerNameEntry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        customerNameEntry.insert(0, full_name)
        customerNameEntry.config(state=NORMAL if full_name else DISABLED)

        Label(updateCustomerFrame, text="Company").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        companyNameEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        companyNameEntry.grid(row=2, column=1, padx=5, pady=5, sticky=W)
        companyNameEntry.insert(0, company)
        companyNameEntry.config(state=NORMAL if not full_name else DISABLED)

        Label(updateCustomerFrame, text="Company Pan No").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        companyPanNoEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        companyPanNoEntry.grid(row=2, column=3, padx=5, pady=5, sticky=W)
        companyPanNoEntry.insert(0, companyPanNo)
        companyPanNoEntry.config(state=NORMAL if not full_name else DISABLED)

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
        
        Label(updateCustomerFrame, text="Phone number").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        phoneNumberEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        phoneNumberEntry.grid(row=3, column=1, padx=5, pady=5, sticky=W)
        phoneNumberEntry.insert(0, phone_number)
        
        Label(updateCustomerFrame, text="Telephone").grid(row=3, column=2, padx=5, pady=5, sticky=W)
        telephoneEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        telephoneEntry.grid(row=3, column=3, padx=5, pady=5, sticky=W)
        telephoneEntry.insert(0, telephone)

        Label(updateCustomerFrame, text="Email").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        emailEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        emailEntry.grid(row=4, column=1, padx=5, pady=5, sticky=W)
        emailEntry.insert(0, email)

        Label(updateCustomerFrame, text="Address").grid(row=4, column=2, padx=5, pady=5, sticky=W)
        addressEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        addressEntry.grid(row=4, column=3, padx=5, pady=5, sticky=W)
        addressEntry.insert(0, address)
        
        def handleUpdate(id):
            if not customerNameEntry.get() and individualCustomerVar.get():
                customerNameEntry.focus()
                return False

            if companyNameEntry.get() and not individualCustomerVar.get():
                if not companyPanNoEntry.get():
                    messagebox.showerror("Update customer", "Please add Pan No of the company.")
                    companyPanNoEntry.focus()
                    return False

            if companyPanNoEntry.get() and not individualCustomerVar.get():
                if not companyNameEntry.get():
                    messagebox.showerror("Update customer", "Please add the name of the company.")
                    companyNameEntry.focus()
                    return False
            
            if not phoneNumberEntry.get() and not telephoneEntry.get():
                messagebox.showerror("Update customer", "Please add phone number or telephone number.")
                phoneNumberEntry.focus()
                return False

            if phoneNumberEntry.get() and len(phoneNumberEntry.get()) != 10:
                messagebox.showwarning("Invalid", "Phone number must contain 10 digits.")
                phoneNumberEntry.focus()
                return False
            
            if not addressEntry.get():
                addressEntry.focus()
                return False

            details = {"full_name": customerNameEntry.get() if individualCustomerVar.get() and customerNameEntry.get() else None,
                    "company":companyNameEntry.get() if not individualCustomerVar.get() and companyNameEntry.get() else None,
                    "company_pan_no":companyPanNoEntry.get() if not individualCustomerVar.get() and companyPanNoEntry.get() else None,
                    "phone_number":phoneNumberEntry.get() if phoneNumberEntry.get() else None,
                    "telephone":telephoneEntry.get() if telephoneEntry.get() else None,
                    "email":emailEntry.get() if emailEntry.get() else None,
                    "address":addressEntry.get() if addressEntry.get() else None}
                    
            status = updateCustomer(id, details)
            updateCustomerWindow.destroy()
            if status:
                # refreshing products list
                refreshCustomersList()
                if globals.CURRENT_FRAME=="customersFrame":
                    # refresh auto complete values in search entry
                    field = globals.customersFilterOptionsMap.get(globals.filterOption.get())
                    globals.queryEntry.config(completevalues=[record[field] if record.get(field) else "" for record in globals.CUSTOMERS_LIST])
                    # reload the inventory table
                    customers.handleSearchCustomer(globals.CURRENT_SEARCH_QUERY.get("customers"))
                if globals.CURRENT_FRAME=="billingSystemFrame":
                    # refresh auto complete values in customers search entry in billing frame
                    field = globals.customersFilterOptionsMap.get(globals.billingCustomerfilterOption.get())
                    globals.billingProductNameEntry.config(completevalues=[record[field] if record.get(field) else "" for record in globals.CUSTOMERS_LIST])

        Button(updateCustomerWindow,
            text="Cancel",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : updateCustomerWindow.destroy(),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        Button(updateCustomerWindow,
            text="Update",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : handleUpdate(customer_id),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        updateCustomerWindow.update()
        # bring to the center of screen
        x = int((globals.screen_width/2) - (updateCustomerWindow.winfo_width()/2))
        y = int((globals.screen_height/2) - (updateCustomerWindow.winfo_height()/2))
        updateCustomerWindow.geometry(f'{updateCustomerWindow.winfo_width()}x{updateCustomerWindow.winfo_height()}+{x}+{y}')
    except Exception as e:
        log.error(f"ERROR: while creating Update Customers window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")