# Home frame
# Here, if user has not entered liscence key, he/she will have to enter here.
# If activated he/she will be able to enter the system
# If not activated he/she wont be able to pass through this window.
import logging
import tkinter
from tkinter import *
from tkinter import messagebox
import frontend.config as globals
from frontend.windows.updateProducts import createUpdateProductWindow
from frontend.windows.lisence import createLicenseInformationWindow
from frontend.utils.frontend import makeColumnResponsive
from frontend.utils.app_configuration import start_trial, is_trial_complete, has_trial_started
from frontend.utils.frontend import handle_buttons_on_activation
import frontend.windows.dashboard as dashboard
# backend imports
from backend.models import LisenceStatus


log = logging.getLogger("frontend")


def createInventoryInfo(parent):
    totalProductsFrame = Frame(parent)
    totalProductsFrame.pack(anchor="w", padx=10, pady=(10, 0))
    Label(totalProductsFrame, text="Total Products: ", font=globals.appFontNormalBold).pack(side="left")
    totalProductsLabel = Label(totalProductsFrame, text=len(globals.PRODUCTS_LIST), font=globals.appFontNormalBold)
    totalProductsLabel.pack(side="left")

    outOfStockFrame = LabelFrame(parent, text="Out of stock")
    outOfStockFrame.pack(padx=10, pady=(20, 0), fill="x")

    canvas = Canvas(outOfStockFrame, bg="blue")

    outOfStockInfoHeaderBody = Frame(canvas)
    outOfStockInfoHeaderBody.pack(fill="x", padx=5, pady=5)

    canvasScrollVertical = Scrollbar(outOfStockFrame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=canvasScrollVertical.set)
    canvasScrollHorizontal = Scrollbar(outOfStockFrame, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=canvasScrollHorizontal.set)

    canvasScrollVertical.pack(side="right", fill="y")
    canvasScrollHorizontal.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    canvasframe = canvas.create_window(0,0, window=outOfStockInfoHeaderBody, anchor='nw')

    def frameWidth(event):
        if event.width > outOfStockInfoHeaderBody.winfo_width():
            canvas.itemconfig(canvasframe, width=event.width-4)
        if event.height > outOfStockInfoHeaderBody.winfo_height():
            canvas.itemconfig(canvasframe, height=event.height-4)

    def OnFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    canvas.bind('<Configure>', lambda e: frameWidth(e))
    outOfStockInfoHeaderBody.bind('<Configure>', lambda e: OnFrameConfigure(e))

    def _bound_to_mousewheel(event):
       canvas.bind_all("<MouseWheel>",_on_mousewheel)

    def _unbound_to_mousewheel(event):
       canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(event):
       canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    outOfStockInfoHeaderBody.bind('<Enter>',_bound_to_mousewheel)
    outOfStockInfoHeaderBody.bind('<Leave>',_unbound_to_mousewheel)

    # headers
    Label(outOfStockInfoHeaderBody, text="ID").grid(row=0, column=0, pady=5, padx=5, sticky=W)
    Label(outOfStockInfoHeaderBody, text="Product Name").grid(row=0, column=1, pady=5, padx=5, sticky=W)
    makeColumnResponsive(outOfStockInfoHeaderBody)

    records = [item for item in globals.PRODUCTS_LIST if item["stock"]==0]
    if len(records)!=0:
        for index, record in enumerate(records):
            bg = "white" if (index+1)%2==0 else globals.appWhite
            Label(outOfStockInfoHeaderBody, text=record["id"], bg=bg).grid(row=index+1, column=0, pady=5, padx=5, sticky=W)
            Label(outOfStockInfoHeaderBody, text=record["product_name"], bg=bg).grid(row=index+1, column=1, pady=5, padx=5, sticky=W)
            Button(outOfStockInfoHeaderBody,
                        text="Add Stock",
                        bg=globals.appBlue,
                        fg=globals.appDarkGreen,
                        width=10,
                        command=lambda productDetails=record: createUpdateProductWindow(productDetails)).grid(row=index+1, column=2, pady=5, padx=5, sticky=W)
    else:
        Label(outOfStockInfoHeaderBody, text="No product out of stock!", fg=globals.appDarkGreen).grid(row=1, columnspan=3, pady=5, sticky="nswe")
    
    makeColumnResponsive(outOfStockInfoHeaderBody)
    

def createSalesInfo(parent):
    totalProductsSoldFrame = Frame(parent)
    totalProductsSoldFrame.pack(anchor="w", padx=10, pady=(10, 0))
    Label(totalProductsSoldFrame, text="Total Products Sold Today: ", font=globals.appFontNormalBold).pack(side="left")
    totalProductsSoldLabel = Label(totalProductsSoldFrame, text=len(globals.TOTAL_SALES), font=globals.appFontNormalBold)
    totalProductsSoldLabel.pack(side="left")

    detailsFrame = LabelFrame(parent, text="Details")
    detailsFrame.pack(padx=10, pady=(20, 0), fill="x")
    
    canvas = Canvas(detailsFrame, bg="blue")

    salesInfoHeaderBody = Frame(canvas)
    salesInfoHeaderBody.pack(fill="x", padx=5, pady=5)

    def frameWidth(event):
        if event.width > salesInfoHeaderBody.winfo_width():
            canvas.itemconfig(canvasframe, width=event.width-4)
        if event.height > salesInfoHeaderBody.winfo_height():
            canvas.itemconfig(canvasframe, height=event.height-4)

    def OnFrameConfigure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    canvas.bind('<Configure>', lambda e: frameWidth(e))
    salesInfoHeaderBody.bind('<Configure>', lambda e: OnFrameConfigure(e))

    canvasScrollVertical = Scrollbar(detailsFrame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=canvasScrollVertical.set)
    canvasScrollHorizontal = Scrollbar(detailsFrame, orient="horizontal", command=canvas.xview)
    canvas.configure(xscrollcommand=canvasScrollHorizontal.set)

    canvasScrollVertical.pack(side="right", fill="y")
    canvasScrollHorizontal.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
    canvasframe = canvas.create_window(0,0, window=salesInfoHeaderBody, anchor='nw')

    def _bound_to_mousewheel(event):
       canvas.bind_all("<MouseWheel>",_on_mousewheel)

    def _unbound_to_mousewheel(event):
       canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(event):
       canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    salesInfoHeaderBody.bind('<Enter>',_bound_to_mousewheel)
    salesInfoHeaderBody.bind('<Leave>',_unbound_to_mousewheel)

    # headers
    Label(salesInfoHeaderBody, text="Product Name").grid(row=0, column=0, pady=5, padx=5, sticky=W)
    Label(salesInfoHeaderBody, text="QTY").grid(row=0, column=1, pady=5, padx=5, sticky=W)
    Label(salesInfoHeaderBody, text="Unit").grid(row=0, column=2, pady=5, padx=5, sticky=W)
    makeColumnResponsive(salesInfoHeaderBody)

    if len(globals.TOTAL_SALES)!=0:
        for index, record in enumerate(globals.TOTAL_SALES.items()):
            bg = "white" if (index+1)%2==0 else globals.appWhite
            Label(salesInfoHeaderBody, text=record[0], bg=bg).grid(row=index+1, column=0, pady=5, padx=5, sticky=W)
            Label(salesInfoHeaderBody, text=record[1]["quantity"], bg=bg).grid(row=index+1, column=1, pady=5, padx=5, sticky=W)
            Label(salesInfoHeaderBody, text=record[1]["unit"], bg=bg).grid(row=index+1, column=2, pady=5, padx=5, sticky=W)
    else:
        Label(salesInfoHeaderBody, text="No products sold!", fg=globals.appDarkGreen).grid(row=1, columnspan=3, pady=5, sticky="nswe")
    

def createHomeFrame(parent):
    globals.homeFrame = Frame(parent, borderwidth=1)
    globals.homeFrame.pack(fill="both", expand=True, padx=10)

    globals.defaultBgColor = globals.homeFrame.cget("bg")

    newFont = globals.appFontBigBold
    newFont.configure(size=15)
    Label(globals.homeFrame, text="Welcome to Inventory management and Billing system!", font=globals.appFontBigBold).pack(side="top", fill="x", pady=10)
    
    InventoryInfoWrapper = Frame(globals.homeFrame)
    InventoryInfoWrapper.pack(fill="both", expand=True)

    inventoryInfoFrame = LabelFrame(InventoryInfoWrapper, text="Inventory")
    inventoryInfoFrame.pack(side="left", fill="both", expand=True, padx=20)
    createInventoryInfo(inventoryInfoFrame)
    
    salesInfoFrame = LabelFrame(InventoryInfoWrapper, text="Sales")
    salesInfoFrame.pack(side="left", fill="both", expand=True, padx=20)
    createSalesInfo(salesInfoFrame)

    aboutButton = Button(globals.homeFrame, 
                        text="About app",
                        bg=globals.appBlue,
                        fg=globals.appDarkGreen,
                        command=lambda: messagebox.showinfo("About app", "Inventory Management and Billing System\n\nVersion: 1.0\n\nDeveloper Info:\nCompany: Datakhoj Private Limited\nPhone: (+977) 9862585910\nEmail: datakhoj.ai@gmail.com\n\nThank you!"))
    aboutButton.pack(side="right", ipadx=20, pady=20, padx=10)

    licenseButton = Button(globals.homeFrame, 
                        text="Product License", 
                        bg=globals.appBlue, 
                        fg=globals.appDarkGreen,
                        command=createLicenseInformationWindow)
    licenseButton.pack(side="right", ipadx=20, pady=20, padx=10)

    def startTrial():
        response = messagebox.askyesnocancel("Inabi System", "You are getting 7 days of free trial.\n\nClick Yes to proceed.")
        if response!=1:
            return False
        else:
            status, message = start_trial()
            if status:
                handle_buttons_on_activation()
                messagebox.showinfo("Inabi System", "Congrats!\n\nYour free trial for 7 days has been started!")
                dashboard.showFrame(globals.CURRENT_FRAME, refreshMode=True)
            else:
                messagebox.showerror("Inabi System", f"Something went wrong!\n\n{message}.")        
    hasTrialStarted, message = has_trial_started()
    if globals.LISENCE_INFO.get("status")==LisenceStatus.not_activated_yet and not (is_trial_complete() or hasTrialStarted):
        trialButton = Button(globals.homeFrame, 
                            text="Start Trial", 
                            bg=globals.appBlue, 
                            fg=globals.appDarkGreen,
                            command=startTrial)
        trialButton.pack(side="right", ipadx=20, pady=20, padx=10)

def openHome(parent):
    try:
        createHomeFrame(parent)
    except Exception as e:
        log.error(f"ERROR: while creating home frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")