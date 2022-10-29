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
        updateCustomerWindow.title("Update product")
        updateCustomerWindow.resizable(0,0)
        updateCustomerWindow.iconbitmap("./frontend/assets/images/favicon.ico")

        customer_id = customerInfo["id"] if customerInfo and customerInfo["id"] else ""
        full_name = customerInfo["full_name"] if customerInfo and customerInfo["full_name"] else ""
        company = customerInfo["company"] if customerInfo and customerInfo["company"] else ""
        phone_number = customerInfo["phone_number"] if customerInfo and customerInfo["phone_number"] else ""
        telephone = customerInfo["telephone"] if customerInfo and customerInfo["telephone"] else ""
        email = customerInfo["email"] if customerInfo and customerInfo["email"] else ""
        address = customerInfo["address"] if customerInfo and customerInfo["address"] else ""

        updateCustomerFrame = LabelFrame(updateCustomerWindow, text="Customer Details", borderwidth=1)
        updateCustomerFrame.pack(fill="both", padx=10, pady=10, expand=True)

        Label(updateCustomerFrame, text="Full Name", justify="left").grid(row=0, column=0, padx=5, pady=5)
        customerNameEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        customerNameEntry.grid(row=0, column=1, padx=5, pady=5)
        customerNameEntry.insert(0, full_name)

        Label(updateCustomerFrame, text="Company").grid(row=0, column=2, padx=5, pady=5)
        companyNameEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        companyNameEntry.grid(row=0, column=3, padx=5, pady=5)
        companyNameEntry.insert(0, company)
        
        Label(updateCustomerFrame, text="Phone number").grid(row=1, column=0, padx=5, pady=5)
        phoneNumberEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        phoneNumberEntry.grid(row=1, column=1, padx=5, pady=5)
        phoneNumberEntry.insert(0, phone_number)
        
        Label(updateCustomerFrame, text="Telephone").grid(row=1, column=2, padx=5, pady=5)
        telephoneEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        telephoneEntry.grid(row=1, column=3, padx=5, pady=5)
        telephoneEntry.insert(0, telephone)

        Label(updateCustomerFrame, text="Email").grid(row=2, column=0, padx=5, pady=5)
        emailEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        emailEntry.grid(row=2, column=1, padx=5, pady=5)
        emailEntry.insert(0, email)

        Label(updateCustomerFrame, text="Address").grid(row=2, column=2, padx=5, pady=5)
        addressEntry = Entry(updateCustomerFrame, bd=globals.defaultEntryBorderWidth, font=globals.appFontNormal)
        addressEntry.grid(row=2, column=3, padx=5, pady=5)
        addressEntry.insert(0, address)
        
        def handleUpdate(id):
            if not customerNameEntry.get():
                customerNameEntry.focus()
                return False
            elif not phoneNumberEntry.get() and not telephoneEntry.get():
                messagebox.showerror("Add customer", "Please add phone number or telephone number.")
                phoneNumberEntry.focus()
                return False
            elif not addressEntry.get():
                addressEntry.focus()
                return False

            if len(phoneNumberEntry.get()) != 10:
                messagebox.showwarning("Invalid", "Phone number must contain 10 digits.")
                phoneNumberEntry.focus()
                return False

            details = {"full_name": customerNameEntry.get(),
                    "company":companyNameEntry.get(),
                    "phone_number":phoneNumberEntry.get(),
                    "telephone":telephoneEntry.get(),
                    "email":emailEntry.get(),
                    "address":addressEntry.get()}
                    
            updateCustomer(id, details)
            updateCustomerWindow.destroy()
            # refreshing products list
            refreshCustomersList()
            if globals.CURRENT_FRAME=="customersFrame":
                # refresh auto complete values in search entry
                globals.queryEntry.config(completevalues=[record["full_name"] for record in globals.CUSTOMERS_LIST])
                # reload the inventory table
                customers.handleSearchCustomer(globals.CURRENT_SEARCH_QUERY.get("customers"))
            if globals.CURRENT_FRAME=="billingSystemFrame":
                # refresh auto complete values in product search entry
                globals.billingProductNameEntry.config(completevalues=[record["full_name"] for record in globals.CUSTOMERS_LIST])

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