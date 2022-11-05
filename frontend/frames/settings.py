# App settings
import logging
from tkinter import *
from tkinter import messagebox
import frontend.config as globals
from frontend.utils.settings import refreshCurrentSettings
from backend.api.settings import add_update_setting


log = logging.getLogger("frontend")


def createSettingsFrame(parent):
    askForPayment = int(globals.CURRENT_SETTINGS.get("ask_for_payment")) if globals.CURRENT_SETTINGS.get("ask_for_payment") else 0
    askForDiscount = int(globals.CURRENT_SETTINGS.get("ask_for_discount")) if globals.CURRENT_SETTINGS.get("ask_for_discount") else 0
    askForVat = int(globals.CURRENT_SETTINGS.get("ask_for_vat")) if globals.CURRENT_SETTINGS.get("ask_for_vat") else 0
    askForTax = int(globals.CURRENT_SETTINGS.get("ask_for_tax")) if globals.CURRENT_SETTINGS.get("ask_for_tax") else 0
    defaultVat = int(globals.CURRENT_SETTINGS.get("default_vat")) if globals.CURRENT_SETTINGS.get("default_vat") else 0
    defaultTax = int(globals.CURRENT_SETTINGS.get("default_tax")) if globals.CURRENT_SETTINGS.get("default_tax") else 0
    defaultDiscount = int(globals.CURRENT_SETTINGS.get("default_discount")) if globals.CURRENT_SETTINGS.get("default_discount") else 0

    globals.settingsFrame = Frame(parent, borderwidth=1)
    globals.settingsFrame.pack(fill="both", expand=True, padx=10)

    # billing settings
    billSettingsFrame = LabelFrame(globals.settingsFrame, text="Billing system configurations")
    billSettingsFrame.pack(padx=10, pady=10)

    askForPaymentVar = IntVar()
    askForPaymentVar.set(askForPayment)
    askForDiscountVar = IntVar()
    askForDiscountVar.set(askForDiscount)
    askForVatVar = IntVar()
    askForVatVar.set(askForVat)
    askForTaxVar = IntVar()
    askForTaxVar.set(askForTax)
    Checkbutton(billSettingsFrame, text = "Ask for payment", variable = askForPaymentVar,
                    onvalue = 1, offvalue = 0, width = 20).grid(row=0, column=0, columnspan=2, pady=2, sticky=W)
    Checkbutton(billSettingsFrame, text = "Ask for Discount", variable = askForDiscountVar, 
                    onvalue = 1, offvalue = 0, width = 20).grid(row=1, column=0, columnspan=2, pady=2, sticky=W)
    Checkbutton(billSettingsFrame, text = "Ask for VAT", variable = askForVatVar, 
                    onvalue = 1, offvalue = 0, width = 20).grid(row=2, column=0, columnspan=2, pady=2, sticky=W)
    Checkbutton(billSettingsFrame, text = "Ask for Tax", variable = askForTaxVar, 
                    onvalue = 1, offvalue = 0, width = 20).grid(row=3, column=0, columnspan=2, pady=2, sticky=W)

    Label(billSettingsFrame, text="Default VAT(%)").grid(row=4, column=0, pady=2, padx=3, sticky=W)
    defaultVatEntry = Entry(billSettingsFrame)
    defaultVatEntry.grid(row=4, column=1, pady=2, padx=3, sticky=W)
    defaultVatEntry.insert(0, defaultVat)

    Label(billSettingsFrame, text="Default discount(%)").grid(row=5, column=0, pady=2, padx=3, sticky=W)
    defaultDiscountEntry = Entry(billSettingsFrame)
    defaultDiscountEntry.grid(row=5, column=1, pady=2, sticky=W)
    defaultDiscountEntry.insert(0, defaultDiscount)

    Label(billSettingsFrame, text="Default tax(%)").grid(row=6, column=0, pady=2, padx=3, sticky=W)
    defaultTaxEntry = Entry(billSettingsFrame)
    defaultTaxEntry.grid(row=6, column=1, pady=2, sticky=W)
    defaultTaxEntry.insert(0, defaultTax)

    # system settings
    systemSettingsFrame = LabelFrame(globals.settingsFrame, text="System")
    systemSettingsFrame.pack(padx=5, pady=5)

    def saveSettings():
        settings = {}
        if askForPaymentVar.get()!=askForPayment:
            settings["ask_for_payment"] = askForPaymentVar.get()
        if askForDiscountVar.get()!=askForDiscount:
            settings["ask_for_discount"] = askForDiscountVar.get()
        if askForVatVar.get()!=askForVat:
            settings["ask_for_vat"] = askForVatVar.get()
        if askForTaxVar.get()!=askForTax:
            settings["ask_for_tax"] = askForTaxVar.get()
        if defaultVatEntry.get()!=defaultVat:
            settings["default_vat"] = defaultVatEntry.get()
        if defaultDiscountEntry.get()!=defaultDiscount:
            settings["default_discount"] = defaultDiscountEntry.get()
        if defaultTaxEntry.get()!=defaultTax:
            settings["default_tax"] = defaultTaxEntry.get()

        if settings.get("ask_for_discount"):
            settings["default_discount"] = 0
        if settings.get("ask_for_vat"):
            settings["default_vat"] = 0
        if settings.get("ask_for_tax"):
            settings["default_tax"] = 0
        
        if not settings:
            messagebox.showinfo("Settings", "No setting has been changed.")
            return None
        
        status, message = add_update_setting(data=settings)
        if status:
            refreshCurrentSettings()
            messagebox.showinfo("Settings", message)
        else:
            messagebox.showerror("Settings", message)
   
    saveButton = Button(globals.settingsFrame, 
                        text="Save",
                        bg=globals.appBlue,
                        fg=globals.appDarkGreen,
                        width=20,
                        command=saveSettings)
    saveButton.pack(side="right", ipadx=20, pady=50, padx=20)

def openSettings(parent):
    try:
        createSettingsFrame(parent)
    except Exception as e:
        log.error(f"ERROR: while creating home frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")