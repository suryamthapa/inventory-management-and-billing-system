""" 
Window for dashboard where user will be able to do different things
user will be able to access the dashboard only after entering valid liscence key in welcome screen
"""
# in-built module imports
import logging
import sys
import os
import datetime
from PIL import ImageTk
from PIL import Image as PILImage
from tkinter import *
from tkinter import messagebox

log = logging.getLogger("frontend")

try:
    # frontend imports
    import frontend.config as Settings
    from frontend.utils.frontend import exitParent, showCurrentTime, handle_buttons_on_activation
    from frontend.utils.app_configuration import has_trial_started, start_trial, is_trial_complete, is_machine_same
    from frontend.frames.inventory import openInventory
    from frontend.frames.home import openHome
    from frontend.frames.profile import openProfile
    from frontend.frames.settings import openSettings
    import frontend.frames.billing as billingSystem
    from frontend.frames.customers import openCustomers
    from frontend.frames.accounts import openAccounts
    from frontend.windows.lisence import createLicenseInformationWindow
    from frontend.windows.appUpdates import createAppUpdatesWindow
    # backend imports
    from backend.models import LisenceStatus
except Exception as e:
    log.error(f"Error occured while importing modules from dashboard -> {e}")
    messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")
    sys.exit("Import error")


def showFrame(frameName, refreshMode=False):
    alreadyOpen = True
    if Settings.CURRENT_FRAME!=frameName or refreshMode:
        alreadyOpen = False

    # Back to default color
    Settings.homeButton.configure(bg=Settings.appDarkGreen)
    Settings.profileButton.configure(bg=Settings.appDarkGreen)
    Settings.settingsButton.configure(bg=Settings.appDarkGreen)
    Settings.inventoryButton.configure(bg=Settings.appDarkGreen)
    Settings.billingSystemButton.configure(bg=Settings.appDarkGreen)
    Settings.customersButton.configure(bg=Settings.appDarkGreen)
    Settings.accountsButton.configure(bg=Settings.appDarkGreen)

    if not alreadyOpen:
        try:
            frame = eval(f"Settings.{Settings.CURRENT_FRAME}")
            if frame: eval(f"Settings.{Settings.CURRENT_FRAME}.destroy()")

            Settings.CURRENT_FRAME = frameName
            if frameName=="homeFrame":
                Settings.homeButton.configure(bg=Settings.appGreen)
                openHome(Settings.mainFrame)
            elif frameName=="profileFrame":
                Settings.profileButton.configure(bg=Settings.appGreen)
                openProfile(Settings.mainFrame)
            elif frameName=="inventoryFrame":
                Settings.inventoryButton.configure(bg=Settings.appGreen)
                openInventory(Settings.mainFrame)
            elif frameName=="settingsFrame":
                Settings.settingsButton.configure(bg=Settings.appGreen)
                openSettings(Settings.mainFrame)
            elif frameName=="billingSystemFrame":
                Settings.billingSystemButton.configure(bg=Settings.appGreen)
                billingSystem.openBillingSystem(Settings.mainFrame)
            elif frameName=="customersFrame":
                Settings.customersButton.configure(bg=Settings.appGreen)
                openCustomers(Settings.mainFrame)
            elif frameName=="accountsFrame":
                Settings.accountsButton.configure(bg=Settings.appGreen)
                openAccounts(Settings.mainFrame)
            log.info(f"OPENED: {frameName}")
        except Exception as e:
            log.error(f"{frameName} --> {e}")
    

def createSidebar(container):
    Settings.sidebar = Frame(container, borderwidth=0)
    Settings.sidebar.pack(side="left", fill="y")

    branding = Frame(Settings.sidebar, borderwidth=0)
    branding.grid(row=0, pady=15)

    global companyLogo
    companyLogo = PILImage.open(os.path.join(Settings.CURRENT_WORKING_DIRECTORY, "frontend","assets","images","logo.png"))
    companyLogo = companyLogo.resize((60,60))
    companyLogo = ImageTk.PhotoImage(companyLogo)
    Label(branding, image=companyLogo).grid(row=0, column=0)
    company_name = Settings.CURRENT_SETTINGS.get("company_profile").get("company_name") if Settings.CURRENT_SETTINGS.get("company_profile") else ""
    Settings.sidebarBrandName = Label(branding, text=company_name, width=20, wraplength=160)
    Settings.sidebarBrandName.grid(row=1, column=0)

    optionsColor = "#DFF6FF"
    options = Frame(Settings.sidebar, bg=Settings.appDarkGreen, borderwidth=0)
    options.grid(row=1, sticky="ns")
    optionsWidth = 19
    optionsPadY = 10

    Settings.homeButton = Button(options, 
        text="Home",
        width=optionsWidth, 
        bg=Settings.appDarkGreen, 
        fg=optionsColor,
        command=lambda : showFrame("homeFrame"))
    Settings.homeButton.grid(row=0, column=0, pady=optionsPadY)

    Settings.profileButton = Button(options, 
        text="Company Profile", 
        width=optionsWidth, 
        bg=Settings.appDarkGreen, 
        fg=optionsColor,
        command=lambda : showFrame("profileFrame"))
    Settings.profileButton.grid(row=1, column=0, pady=optionsPadY)

    Settings.inventoryButton = Button(options, 
        text="Inventory", 
        width=optionsWidth, 
        bg=Settings.appDarkGreen, 
        fg=optionsColor,
        command=lambda : showFrame("inventoryFrame"))
    Settings.inventoryButton.grid(row=2, column=0, pady=optionsPadY)

    Settings.customersButton = Button(options, 
        text="Customers", 
        width=optionsWidth, 
        bg=Settings.appDarkGreen, 
        fg=optionsColor,
        command=lambda : showFrame("customersFrame"))
    Settings.customersButton.grid(row=3, column=0, pady=optionsPadY)

    Settings.accountsButton = Button(options, 
        text="Accounts", 
        width=optionsWidth, 
        bg=Settings.appDarkGreen, 
        fg=optionsColor,
        command=lambda : showFrame("accountsFrame"))
    Settings.accountsButton.grid(row=4, column=0, pady=optionsPadY)

    Settings.billingSystemButton = Button(options, 
        text="Billing System", 
        width=optionsWidth, 
        bg=Settings.appDarkGreen, 
        fg=optionsColor,
        command=lambda : showFrame("billingSystemFrame"))
    Settings.billingSystemButton.grid(row=5, column=0, pady=optionsPadY)

    Settings.salesAndAnalyticsButton = Button(options, 
        text="Sales and Analytics", 
        width=optionsWidth, 
        bg=Settings.appDarkGreen, 
        fg=optionsColor,
        command=lambda : messagebox.showinfo("Sales and Analytics", "Feature comming soon in next update!\n\nYou will be able to view the sales and analytics of your company with the help of this feature.\n\nThank you!"))
    Settings.salesAndAnalyticsButton.grid(row=6, column=0, pady=optionsPadY)

    Settings.settingsButton = Button(options, 
        text="Settings", 
        width=optionsWidth, 
        bg=Settings.appDarkGreen, 
        fg=optionsColor,
        command=lambda : showFrame("settingsFrame"))
    Settings.settingsButton.grid(row=7, column=0, pady=optionsPadY)

    Settings.updateButton = Button(options, 
        text="Check Updates",
        width=optionsWidth, 
        bg=Settings.appDarkGreen, 
        fg=optionsColor,
        command=createAppUpdatesWindow)
    Settings.updateButton.grid(row=8, column=0, pady=optionsPadY)

    Settings.exitButton = Button(options, 
        text="Exit", width=optionsWidth,
        bg=Settings.appDarkGreen,
        fg=optionsColor,
        command=lambda: exitParent(Settings.app))
    Settings.exitButton.grid(row=9, column=0, pady=optionsPadY)

    # Making the options frame expand to the height of screen
    Grid.rowconfigure(Settings.sidebar, 1, weight=1)
    Grid.columnconfigure(Settings.sidebar, 0, weight=1)


def createTopBar(container):
    Settings.topBar = Frame(container, bg="#256D85")
    Settings.topBar.pack(side="top", fill="x")

    appStatus = ""
    if Settings.LISENCE_INFO.get("status") == LisenceStatus.not_activated_yet:
        appStatus = "Inactive"
    elif Settings.LISENCE_INFO.get("status") == LisenceStatus.active:
        appStatus = "Active"
    elif Settings.LISENCE_INFO.get("status") == LisenceStatus.expired:
        appStatus = "Expired"

    Settings.appStatusLabel = Label(Settings.topBar, text=f"Status: {appStatus}", font=Settings.appFontBigBold, fg="#DFF6FF", bg="#256D85")
    Settings.appStatusLabel.grid(row=0, column=0, sticky="w", pady=22, padx=20)

    timeLabel = Label(Settings.topBar, font=Settings.appFontBigBold, fg="#DFF6FF", bg="#256D85")
    timeLabel.grid(row=0, column=0, sticky="e", pady=22, padx=20)

    Grid.columnconfigure(Settings.topBar, 0, weight=1)
    Grid.rowconfigure(Settings.topBar, 0, weight=1)

    showCurrentTime(timeLabel)


def openDashboard(container):
    try:
        if not is_machine_same():
            messagebox.showerror("Inabi System", "The application does not belong to this machine. In case of any inconvenience, please contact the developers. \n\nDevelopers Info:\nDatakhoj Private Limited\nPhone: (+977) 9862585910\nEmail: datakhoj.ai@gmail.com\n\nThank you!")
            container.destroy()
            return False

        log.info("FOUND: Machine is same.")
        createSidebar(container)

        Settings.board = Frame(container, borderwidth=1, width=500, height=500)
        Settings.board.pack(side="right", fill="both", expand=True)
        
        createTopBar(Settings.board)

        Settings.mainFrame = Frame(Settings.board)
        Settings.mainFrame.pack(side="bottom", fill="both", expand=True)
        showFrame(Settings.CURRENT_FRAME, refreshMode=True)
        
        if is_trial_complete():
            log.info("COMPLETE: Trial")
            if Settings.LISENCE_INFO.get("status") == LisenceStatus.active:
                log.info("Lisence is active")
                messagebox.showinfo("InaBi System", "Welcome to Inventory Management and Billing System, by Datakhoj Private Limited!")
            elif Settings.LISENCE_INFO.get("status") is None:
                log.error("Exception may have occured while updating lisence key to expired.")
                handle_buttons_on_activation(deactivation=True)
                messagebox.showerror("InaBi System", "Could not check lisence status.\n\nPlease contact the developer.\n\nThank you!")
            else:
                log.info("Lisence is expired or not registered yet")
                handle_buttons_on_activation(deactivation=True)
                log.info("Premium features disabled.")
                msg_trial_completed = "Your trial for 7 days has already completed.\n\nTo keep using the app, you need to activate it.\n\nClick Yes to activate."
                msg_lisence_expired = "Your lisence key has been expired.\n\nTo continue using the features, you will have to reactivate the app with a new lisence key.\n\nClick Yes to enter a new lisence key."
                message = msg_trial_completed if Settings.LISENCE_INFO.get("status")==LisenceStatus.not_activated_yet else msg_lisence_expired
                response = messagebox.askyesnocancel("InaBi System", message)
                if response==1:
                    createLicenseInformationWindow()
        else:
            log.info("INCOMPLETE: Trial")
            status, trial_begin_on = has_trial_started()
            if status:
                trial_day = int((datetime.datetime.now()-trial_begin_on).days)+1
                log.info(f"Trial has already been started -> Day {trial_day}")
                trial_day = f"day {trial_day}" if trial_day!=7 else "the last day"
                messagebox.showinfo("InaBi System", f"Welcome to {trial_day} of your trial.")
            else:
                log.info("Trial has not started yet")
                response = messagebox.askyesnocancel("InaBi System", "Welcome to Inventory Management and Billing System, by Datakhoj Private Limited.\n\nWe are offering you a free trial of 7 days so that you can use all of our premium features!\n\nClick Yes to proceed.")
                if response!=1:
                    handle_buttons_on_activation(deactivation=True)
                else:
                    status, message = start_trial()
                    if status:
                        log.info("STARTING: Trial for 7 days")
                        messagebox.showinfo("Inabi System", "Congrats!\n\nYour free trial for 7 days has been started!")
                        showFrame(Settings.CURRENT_FRAME, refreshMode=True)
                    else:
                        messagebox.showerror("Inabi System", f"Something went wrong!\n\n{message}.")
    except Exception as e:
        log.error(f"ERROR: while creating dashboard -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")