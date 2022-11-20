# Window to add products in inventory.

import logging
from pytz import timezone
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
# frontend imports
from frontend.utils import nepali_datetime
import frontend.config as globals
import frontend.frames.accounts as accountsFrame
from frontend.utils.accounts import updateAccount
from frontend.utils.frontend import makeColumnResponsive
from frontend.utils.tkNepaliCalendar import DateEntry
# backend imports
from backend.models import AccountType


log = logging.getLogger("frontend")


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def createUpdateAccountWindow(customerInfo, accountInfo):
    try:
        updateAccountWindow = Toplevel()
        updateAccountWindow.grab_set()
        updateAccountWindow.title("Update Transaction")
        updateAccountWindow.resizable(0,0)
        updateAccountWindow.iconbitmap("./frontend/assets/images/favicon.ico")

        customer_id = customerInfo["id"] if customerInfo and customerInfo["id"] else ""
        if not customer_id:
            raise ValueError("Customer Id not found in customerInfo.")

        name = customerInfo["full_name"] if customerInfo and customerInfo["full_name"] else ""
        company = customerInfo["company"] if customerInfo and customerInfo["company"] else ""
        company_pan_no = customerInfo["company_pan_no"] if customerInfo and customerInfo["company_pan_no"] else ""
        phone_num = customerInfo["phone_number"] if customerInfo and customerInfo["phone_number"] else ""
        telephone = customerInfo["telephone"] if customerInfo and customerInfo["telephone"] else ""
        email = customerInfo["email"] if customerInfo and customerInfo["email"] else ""
        address = customerInfo["address"] if customerInfo and customerInfo["address"] else ""

        account_id = accountInfo["id"] if accountInfo.get("id") else ""
        if not account_id:
            raise ValueError("Account Id not found in accountInfo.")
        date = accountInfo["date"] if accountInfo.get("date") else ""
        bill_id = accountInfo["bill_id"] if accountInfo.get("bill_id") else ""
        type = accountInfo["type"] if accountInfo.get("type") else ""
        description = accountInfo["description"] if accountInfo.get("description") else ""
        amount = accountInfo["amount"] if accountInfo.get("amount") else ""

        customerDetailsFrame = Frame(updateAccountWindow)
        customerDetailsFrame.pack(fill="both", padx=10, pady=5, expand=True)

        contacts = []
        if phone_num: contacts.append(phone_num) 
        if telephone: contacts.append(telephone)

        Label(customerDetailsFrame, text="Customer:", font=globals.appFontSmallBold).grid(row=0, column=0, pady=(10, 5), sticky=W)
        if name:
            Label(customerDetailsFrame, text=name, wraplength=160, justify="left").grid(row=0, column=1, pady=(10, 5), sticky=W)
        elif company:
            Label(customerDetailsFrame, text=company, wraplength=160, justify="left").grid(row=0, column=1, pady=(10, 5), sticky=W)
        else:
            Label(customerDetailsFrame, text="********", wraplength=160, justify="left").grid(row=0, column=1, pady=(10, 5), sticky=W)
        
        if company:
            Label(customerDetailsFrame, text="PAN no:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=0, column=2, pady=(10, 5), sticky=W)
            Label(customerDetailsFrame, text=company_pan_no if company_pan_no else "**********", wraplength=160, justify="left").grid(row=0, column=3, pady=(10, 5), sticky=W)
        elif name:
            Label(customerDetailsFrame, text="Address:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=0, column=2, pady=(10, 5), sticky=W)
            Label(customerDetailsFrame, text=address if address else "**********", wraplength=160, justify="left").grid(row=0, column=3, pady=(10, 5), sticky=W)
        
        Label(customerDetailsFrame, text="Contacts:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=1, column=0, pady=(5, 10), sticky=W)
        Label(customerDetailsFrame, text=f"{', '.join(contacts)}" if contacts else "********", wraplength=160, justify="left").grid(row=1, column=1, pady=(5, 10), sticky=W)

        if company:
            Label(customerDetailsFrame, text="Address:", font=globals.appFontSmallBold, wraplength=160, justify="left").grid(row=1, column=2, pady=(5, 10), sticky=W)
            Label(customerDetailsFrame, text=address if address else "**********", wraplength=160, justify="left").grid(row=1, column=3, pady=(5, 10), sticky=W)
        
        makeColumnResponsive(customerDetailsFrame)

        updateAccountFrame = LabelFrame(updateAccountWindow, text="Transaction Details", borderwidth=1)
        updateAccountFrame.pack(fill="both", padx=10, pady=10, expand=True)
        
        Label(updateAccountFrame, text="Date ").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        dateEntry = DateEntry(updateAccountFrame)
        dateEntry.grid(row=0, column=1, sticky="w", padx=(2,5))
        dateEntry.delete(0, END)
        dateEntry.insert(0, date)
        if bill_id:
            dateEntry.configure(state="disabled")

        desctiptionsList = ["Cash Deposit", "Bank Deposit"]
        desctiptionsList = [description] + desctiptionsList
        descriptionVar = StringVar()

        Label(updateAccountFrame, text="Description").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        descriptionEntry = ttk.Combobox(updateAccountFrame, textvariable=descriptionVar, values=desctiptionsList)
        descriptionEntry.current(0)
        descriptionEntry.grid(row=0, column=3, padx=5, pady=5, sticky=W)
        if bill_id:
            descriptionEntry.configure(state="disabled")

        Label(updateAccountFrame, text="Type").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        typesList = ["debit", "credit"]
        typeOption = StringVar()
        typeOption.set(typesList[1] if not type else type)
        typeEntry = OptionMenu(updateAccountFrame, typeOption, *typesList)
        typeEntry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        if bill_id:
            typeEntry.configure(state="disabled")

        Label(updateAccountFrame, text="Amount").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        amountEntry = Entry(updateAccountFrame, bd=globals.defaultEntryBorderWidth)
        amountEntry.grid(row=1, column=3, padx=5, pady=5, sticky=W)
        amountEntry.insert(0, amount)

        makeColumnResponsive(updateAccountFrame )

        def validateAccount():
            date = dateEntry.get()
            if not date:
                dateEntry.focus()
                return False

            date_meta = date.split("/")
            # check if there are three sections separated by /
            if len(date_meta)!=3:
                messagebox.showwarning("InaBi System", "Please select or enter a valid date.")
                return False
            # check if every section is a number
            for m in date_meta:
                if not m.isdigit():
                    messagebox.showwarning("InaBi System", "Please select or enter a valid date.")
                    return False

            if not descriptionVar.get():
                messagebox.showerror("Add Account", "Please select or enter the description.")
                descriptionEntry.focus()
                return False

            if not typeOption.get():
                messagebox.showerror("Add Account", "Please select the type of transaction.")
                typeEntry.focus()
                return False

            if not amountEntry.get():
                amountEntry.focus()
                return False
            
            if not isfloat(amountEntry.get()):
                messagebox.showerror("Add Account", "Amount should be a number.")
                typeEntry.focus()
                return False
            
            user_year = int(date_meta[2])
            user_month = int(date_meta[1])
            user_day = int(date_meta[0])

            utc_timezone = timezone("UTC")

            todays_ne_datetime = nepali_datetime.datetime.now()
            user_selected_ne_datetime = todays_ne_datetime.replace(year=user_year, month=user_month, day=user_day)
            
            # check if user selected date is greater than today
            if user_selected_ne_datetime>todays_ne_datetime:
                messagebox.showwarning("InaBi System", "Please select date upto today only.")
                dateEntry.focus()
                return False
            
            user_selected_en_datetime = user_selected_ne_datetime.to_datetime_datetime()
            user_selected_utc_datetime = user_selected_en_datetime.astimezone(utc_timezone)

            data = {"transaction_date": user_selected_utc_datetime,
                    "customer_id": customer_id,
                    "type": AccountType.credit if typeOption.get()=="credit" else AccountType.debit,
                    "description": descriptionVar.get(),
                    "amount": amountEntry.get()}
            status = updateAccount(account_id, data)
            updateAccountWindow.destroy()

            if status:
                if globals.CURRENT_FRAME=="accountsFrame":
                    # reload the accounts table
                    accountsFrame.handleSearchAccount(column=globals.CURRENT_SEARCH_QUERY["account"]["column"], 
                                                    query=globals.CURRENT_SEARCH_QUERY["account"]["query"], 
                                                    from_=globals.CURRENT_LEDGER_ACCOUNT["from"], 
                                                    to=globals.CURRENT_LEDGER_ACCOUNT["to"])
            return True

        Button(updateAccountWindow,
            text="Cancel",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : updateAccountWindow.destroy(),
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)
        
        Button(updateAccountWindow,
            text="Update",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=validateAccount,
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        updateAccountWindow.update()
        # bring to the center of screen
        x = int((globals.screen_width/2) - (updateAccountWindow.winfo_width()/2))
        y = int((globals.screen_height/2) - (updateAccountWindow.winfo_height()/2))
        updateAccountWindow.geometry(f'{updateAccountWindow.winfo_width()}x{updateAccountWindow.winfo_height()}+{x}+{y}')
    except Exception as e:
        log.error(f"ERROR: while creating Add Accounts window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")