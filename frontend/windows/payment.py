# Window to add products in inventory.
import logging
from tkinter import *
from tkinter import messagebox
import frontend.config as globals
from frontend.utils.bills import make_payment_and_add_bill_entry


log = logging.getLogger("frontend")


def createPaymentWindow(forUpdate=False):
    try:
        paymentWindow = Toplevel()
        paymentWindow.grab_set()
        paymentWindow.title("Payment")
        paymentWindow.resizable(0,0)
        paymentWindow.iconbitmap("./frontend/assets/images/favicon.ico")

        Label(paymentWindow, text=f"Total Payable Amount(Rs): {globals.BILL_DETAILS['final']['total']:,.2f}",
            font=globals.appFontNormalBold).grid(row=0, columnspan=2, pady=(20, 5), padx=10)

        Label(paymentWindow, text="Paid Amount(Rs)", font=globals.appFontNormal).grid(row=1, column=0, pady=(10, 20), padx=10)
        paymentEntry = Entry(paymentWindow)
        paymentEntry.grid(row=1, column=1, pady=(10, 20), padx=10)
        paymentEntry.focus()
        paymentEntry.insert(0, float(globals.BILL_DETAILS['final']['total']))

        def validatePayment(withoutPayment=False):
            if not withoutPayment:
                try:
                    float(paymentEntry.get())
                except:
                    messagebox.showwarning("Payment", "Must be a number.")
                    return False
            if float(paymentEntry.get().isdigit())>float(globals.BILL_DETAILS['final']['total']):
                messagebox.showwarning("Payment", "Amount greater than actual payable amount.")
                return False
            paidAmount = float(paymentEntry.get()) if not withoutPayment else float(0)
            make_payment_and_add_bill_entry(paidAmount)
            paymentWindow.destroy()

        proceedBtn = Button(paymentWindow,
            text="Proceed without payment",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=lambda : validatePayment(withoutPayment=True),
            width=25)
        proceedBtn.grid(row=2, column=0, pady=(5, 20), padx=10)
        
        proceedBtn = Button(paymentWindow,
            text="Make Payment and Print bill",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=validatePayment,
            width=25)
        proceedBtn.grid(row=2, column=1, pady=(5, 20), padx=10)

        paymentEntry.bind('<Return>', validatePayment)
        paymentWindow.update()
        # bring to the center of screen
        x = int((globals.screen_width/2) - (paymentWindow.winfo_width()/2))
        y = int((globals.screen_height/2) - (paymentWindow.winfo_height()/2))
        paymentWindow.geometry(f'{paymentWindow.winfo_width()}x{paymentWindow.winfo_height()}+{x}+{y}')
    except Exception as e:
        log.exception(f"ERROR: while creating Bill Payment window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")