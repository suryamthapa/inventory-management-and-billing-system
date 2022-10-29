# license information windows and all
import datetime
import logging
from tkinter import *
from tkinter import messagebox
import frontend.config as globals
from frontend.utils.app_configuration import is_trial_complete
from frontend.utils.frontend import handle_buttons_on_activation
from frontend.utils.lisences import refreshLisenceInfo
import frontend.windows.dashboard as dashboard
# backend imports
from backend.models import LisenceStatus
from backend.api.lisences import add_lisence
from backend.api.about_app import add_update_app_configuration


log = logging.getLogger("frontend")


def createLicenseInformationWindow():
    try:
        licenseWindow = Toplevel()
        licenseWindow.grab_set()
        licenseWindow.title("License Information")
        licenseWindow.resizable(0,0)
        licenseWindow.iconbitmap("./frontend/assets/images/favicon.ico")
        
        statusFrame = Frame(licenseWindow)
        statusFrame.pack(anchor="w", padx=10, pady=(10, 0))
        Label(statusFrame, text="Status: ", font=globals.appFontNormalBold).pack(side="left")
        if globals.LISENCE_INFO.get("status")==LisenceStatus.expired: status = "Expired"
        elif globals.LISENCE_INFO.get("status")==LisenceStatus.active: status = "Active"
        elif globals.LISENCE_INFO.get("status")==LisenceStatus.not_activated_yet: status = "Not activated yet"
        else: status = "Could not find lisence status. Please contact the developer."
        statusLabel = Label(statusFrame, text=status)
        statusLabel.pack(side="left")

        if globals.LISENCE_INFO.get("status")!=LisenceStatus.not_activated_yet:
            expiryFrame = Frame(licenseWindow)
            expiryFrame.pack(anchor="w", padx=10)
            
            Label(expiryFrame,
                text=f"{'Expiry date' if globals.LISENCE_INFO.get('status')==LisenceStatus.active else 'Expired on'}: ", 
                font=globals.appFontNormalBold,
                anchor="w").pack(side="left")
            
            activated_on = globals.LISENCE_INFO.get("activated_on")
            expiryLabelText = f"{activated_on.year+1}-{activated_on.month}-{activated_on.day}"

            expiryLabel = Label(expiryFrame, text=expiryLabelText)
            expiryLabel.pack(side="left")

            currentLicenseFrame = Frame(licenseWindow)
            currentLicenseFrame.pack(anchor="w", padx=10)
            Label(currentLicenseFrame, text="Current License key: ", font=globals.appFontNormalBold).pack(side="left")
            statusLabel = Label(currentLicenseFrame, text=globals.LISENCE_INFO.get("lisence_key"))
            statusLabel.pack(padx=10)

        command = "Enter" if globals.LISENCE_INFO.get("status")==LisenceStatus.not_activated_yet else "Change"
        newLicenseFrame = Frame(licenseWindow)
        newLicenseFrame.pack(anchor="w", padx=10)
        Label(newLicenseFrame, text=f"{command} License Key: ", font=globals.appFontNormalBold).pack(side="left")
        newLicenseEntry = Entry(newLicenseFrame, width=40)
        newLicenseEntry.pack(padx=10, ipady=2, ipadx=2)
        newLicenseEntry.focus()

        buttonsWrapper = Frame(licenseWindow)
        buttonsWrapper.pack(fill="x")

        Button(buttonsWrapper,
            text="Close",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=licenseWindow.destroy,
            width=20).pack(side="left", ipadx=20, pady=20, padx=10)

        def activateLicense():
            if not newLicenseEntry.get():
                newLicenseEntry.focus()
                return False

            if len(newLicenseEntry.get())!=24:
                messagebox.showwarning("InaBi System", "Invalid Lisence Key!\n\nKey must contain 24 characters only!")
                newLicenseEntry.focus()
                return False
            
            if len(newLicenseEntry.get().split("-"))!=5:
                messagebox.showwarning("InaBi System", "Invalid Lisence Key!\n\nProbably missing a dash.")
                newLicenseEntry.focus()
                return False
            
            if str(globals.LISENCE_INFO.get("lisence_key")).lower()==str(newLicenseEntry.get()).lower():
                messagebox.showwarning("InaBi System", "Please enter a new lisence key!")
                newLicenseEntry.focus()
                return False

            if globals.LISENCE_INFO.get("status")==LisenceStatus.not_activated_yet:
                data = {"lisence_key": newLicenseEntry.get(), "duration": 1, "activated_on":datetime.datetime.now()}
                status, message = add_lisence(data)
                if status:
                    refreshLisenceInfo()
                    handle_buttons_on_activation(["inventoryFrame","billingSystemFrame","customersFrame","salesAndAnalyticsFrame"])
                    dashboard.showFrame(globals.CURRENT_FRAME, refreshMode=True)
                    licenseWindow.destroy()
                    messagebox.showinfo("Product activation", f"Activation successful!\n\nLisence Key: {status}\n\nThank you!")
                    status = is_trial_complete(forceComplete=True)
                    if not status:
                        messagebox.showerror("Product activation", f"App is activated however some error has occured!\nPlease check logs for errors!\n\nYou can close this dialogue and continue working!\n\nThank you!")
                    else:
                        # messagebox.showinfo("InaBi System", "Also the trial has been marked as completed.")
                        print("Trial complete status: ",is_trial_complete())
                    return True
                else:
                    messagebox.showerror("Product activation", f"Could not activate the app!\n\n{message}")
                    return False
                    

            if globals.LISENCE_INFO.get("status")==LisenceStatus.expired:
                data = {"lisence_key": newLicenseEntry.get(), "duration": 1, "activated_on":datetime.datetime.now()}
                status, message = add_lisence(data)
                if status:
                    refreshLisenceInfo()
                    handle_buttons_on_activation(["inventoryFrame","billingSystemFrame","customersFrame","salesAndAnalyticsFrame"])
                    dashboard.showFrame(globals.CURRENT_FRAME, refreshMode=True)
                    licenseWindow.destroy()
                    messagebox.showinfo("Product activation", f"Activation successful!\n\nLisence Key: {status}\n\nThank you!")
                    return True
                else:
                    messagebox.showerror("Product activation", f"Could not re-activate the app!\n\n{message}")
                    return False
                    

            if globals.LISENCE_INFO.get("status")==LisenceStatus.active:
                data = {"lisence_key": newLicenseEntry.get(), "duration": 1, "activated_on":datetime.datetime.now()}
                status, message = add_lisence(data)
                if status:
                    refreshLisenceInfo()
                    dashboard.showFrame(globals.CURRENT_FRAME, refreshMode=True)
                    licenseWindow.destroy()
                    messagebox.showinfo("Product activation", f"Lisence key updated successfully!\n\nLisence Key: {data['lisence_key']}.\n\nThank you!")
                    return True
                else:
                    messagebox.showerror("Product activation", f"Could not update the lisence key!\n\n{message}")
                    return False
            
            
            
            

        Button(buttonsWrapper,
            text="Activate",
            bg=globals.appBlue,
            fg=globals.appDarkGreen,
            command=activateLicense,
            width=20).pack(side="right", ipadx=20, pady=20, padx=10)

        licenseWindow.update()
        # bring to the center of screen
        x = int((globals.screen_width/2) - (licenseWindow.winfo_width()/2))
        y = int((globals.screen_height/2) - (licenseWindow.winfo_height()/2))
        licenseWindow.geometry(f'{licenseWindow.winfo_width()}x{licenseWindow.winfo_height()}+{x}+{y}')
    except Exception as e:
        log.error(f"ERROR: while creating lisence window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")