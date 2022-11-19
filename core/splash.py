import os
import tkinter
import logging
from tkinter import *
from tkinter import messagebox
import time
import importlib.util
from core.loggers import setup_logger


def check_if_module_exists(name):
     mod = importlib.util.find_spec(name)
     if not mod:
        return False
     return True


def ensure_modules():
    modules = ["ttkwidgets", "alembic", "PIL", "reportlab", "frontend", "backend", "core", "nepali_datetime", "pytz"]
    for module in modules:
        value = check_if_module_exists(module)
        if not value:
            return False, f"Can not find module -> {module}"
    return True, "INITIALIZED: modules and dependencies"


def initialize_app(parent, bgColor, fgColor, font):
    Label(parent, text="Opening the interface...", bg=bgColor, fg=fgColor, font=font).grid(row=7, column=0, padx=10, pady=2, sticky=W)

    parent.update()
    time.sleep(1)
    parent.destroy()

    import frontend.windows.dashboard as dashboard
    from frontend.config import app
    dashboard.openDashboard(app)
    app.mainloop()
    
    
def folders_files_initialization():
    try:
        # ensure log files
        if not os.path.exists("logs"):
            os.mkdir("logs")
            open("./logs/backend.log", "w").close()
            open("./logs/frontend.log", "w").close()
        if not os.path.exists("./logs/backend.log"):
            open("./logs/backend.log", "w").close()
        if not os.path.exists("./logs/frontend.log"):
            open("./logs/frontend.log", "w").close()

        setup_logger('backend', "./logs/backend.log")
        setup_logger('frontend', "./logs/frontend.log")

        # ensure bills folder
        if not os.path.exists("bills"):
            os.mkdir("bills")

        # ensure bills folder
        if not os.path.exists("ledgers"):
            os.mkdir("ledgers")

        if not os.path.exists("migrations"):
            raise Exception("NOT FOUND: migrations folder") 
            
        if not os.path.exists("alembic.ini"):
            raise Exception("NOT FOUND: alembic.ini file") 
        
        if not os.path.exists("frontend"):
            raise Exception("NOT FOUND: frontend folder for assets") 

        return True, "INITIALIZED: Log files and essential folders"
    except Exception as e:
        return False, f"Could not initialize files and folders.\n\n{e}"


def createSplashScreen(parent, bgColor, fgColor, font):
    if not isCreated:
        status, message = folders_files_initialization()
        Label(parent, text=message, bg=bgColor, fg=fgColor, font=font).grid(row=2, column=0, padx=10, pady=2, sticky=W)
        parent.update()
        if not status:
            messagebox.showerror("Inventory Management and Billing System", f"{message}\n\nPlease contact the developer.\n\nThank you!")
            parent.destroy()
            return False
        
        status, message = ensure_modules()
        Label(parent, text=message, bg=bgColor, fg=fgColor, font=font).grid(row=3, column=0, padx=10, pady=2, sticky=W)
        parent.update()
        if not status:
            messagebox.showerror("Inventory Management and Billing System", f"{message}\n\nPlease contact the developer.\n\nThank you!")
            parent.destroy()
            return False
        
        from core.initialization import database_initialization, initialize_app_configuration
        status, message = database_initialization()
        Label(parent, text=message, bg=bgColor, fg=fgColor, font=font).grid(row=4, column=0, padx=10, pady=2, sticky=W)
        parent.update()
        if not status:
            messagebox.showerror("Inventory Management and Billing System", f"{message}\n\nPlease contact the developer.\n\nThank you!")
            parent.destroy()
            return False

        status, message = initialize_app_configuration()
        Label(parent, text=message, bg=bgColor, fg=fgColor, font=font).grid(row=5, column=0, padx=10, pady=2, sticky=W)
        parent.update()
        if not status:
            messagebox.showerror("Inventory Management and Billing System", f"{message}\n\nPlease contact the developer.\n\nThank you!")
            parent.destroy()
            return False

        initialize_app(parent, bgColor, fgColor, font)


# colors
appWhite = "#DFF6FF"
appBlue = "#47B5FF"
appGreen = "#256D85"
appDarkGreen = "#06283D"
font = ("Helvetica", 9)
fontBold = ("Helvetica-Bold", 10)
isCreated = False

splashScreen = Tk()
splashScreen.geometry(f"{380}x{180}")
splashScreen.overrideredirect(True)

screen_width = splashScreen.winfo_screenwidth()
screen_height = splashScreen.winfo_screenheight()

splashScreen.config(bg=appDarkGreen)
splashScreen.update()
x = int((screen_width/2) - (splashScreen.winfo_width()/2))
y = int((screen_height/2) - (splashScreen.winfo_height()/2))
splashScreen.geometry(f'{splashScreen.winfo_width()}x{splashScreen.winfo_height()}+{x}+{y}')

Label(splashScreen, text="Inventory Management and Billing System, By Datakhoj.", bg=appDarkGreen, fg=appWhite, font=fontBold).grid(row=0, column=0, padx=10, pady=2, sticky=W)

mainLabel = Label(splashScreen, text="INITIALIZING APPLICATION ...", bg=appDarkGreen, fg=appWhite, font=font)
mainLabel.grid(row=1, column=0, padx=10, pady=2, sticky=W)

mainLabel.after(1000, lambda: createSplashScreen(splashScreen, appDarkGreen, appWhite, font))