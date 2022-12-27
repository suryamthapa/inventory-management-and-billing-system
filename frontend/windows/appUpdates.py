from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import requests
from requests import ConnectionError
from functools import partial
import os
import subprocess
import tempfile
import threading
import logging
import queue
# frontend imports
import frontend.config as Settings
from frontend.utils.frontend import makeColumnResponsive
# backend imports
from backend.api.about_app import get_about_app


log = logging.getLogger("frontend")


def isFloat(x):
    try:
        float(x)
        return True
    except Exception as e:
        return False

q = queue.Queue()


def check_for_update(updateInfoLabel, installButton, installed_version):
    try:
        response = requests.get(Settings.version_info_link, timeout=10)
        if isFloat(installed_version) and isFloat(response.text.strip()):
            if float(installed_version) < float(response.text.strip()):
                updateInfoLabel.configure(text=f"Update Available - Version : {response.text.strip()}")
                installButton.configure(state="normal", 
                                        bg=Settings.appBlue,
                                        fg=Settings.appDarkGreen)
            if float(installed_version) == float(response.text.strip()):
                updateInfoLabel.configure(text=f"App is up-to-date!")
            else:
                updateInfoLabel.configure(text=f"Something is wrong!")
        else:
            updateInfoLabel.configure(text="Sorry, no update available for now!")
            installButton.configure(state="disabled", bg=Settings.defaultBgColor)
    except ConnectionError:
        updateInfoLabel.configure(text="Please check your internet connection and check for updates again!")
        installButton.configure(state="disabled", bg=Settings.defaultBgColor)
    except Exception as e:
        updateInfoLabel.configure(text="Cound not check for updates!")
        installButton.configure(state="disabled")
    finally:
        return True


def install_update(exe_path, updateAppWindow):
    try:
        updateAppWindow.event_generate('<<Done>>')
        subprocess.Popen(exe_path)
    except Exception as e:
        log.error(f"ERROR: While starting the executable installer for installing updates: {e}")
        messagebox.showerror("App Updates", "Some error occured while installing the update.\n\nPlease check logs or contact the developer.\n\nThank you!")


def createAppUpdatesWindow():
    try:
        status, message = get_about_app()
        if status:
            installed_version = message["app_version"] if message.get("app_version") else "N/A"
        else:
            installed_version = "N/A"
        
        updateAppWindow = Toplevel()
        updateAppWindow.grab_set()
        updateAppWindow.title("Update App")
        updateAppWindow.geometry(f"{380}x{200}")
        updateAppWindow.resizable(0,0)
        updateAppWindow.iconbitmap("./frontend/assets/images/favicon.ico")
        
        updateFrame = Frame(updateAppWindow)
        updateFrame.pack(fill="both", expand=True, padx=20, pady=20)

        def start_update_manager(installButton):
            installButton.configure(state="disabled", bg=Settings.defaultBgColor)
            progressFrame = Frame(updateFrame)
            progressFrame.grid(row=3, column=0, pady=10, padx=10)

            downloadInfoLabel = Label(progressFrame, text="Downloading the installer...please don't close the window.", anchor=W, wraplength=300)
            downloadInfoLabel.pack(fill="x", expand=True, pady=(0, 5))
            
            updateAppWindow.bind('<<Done>>', lambda event: updateAppWindow.destroy())
            
            def download(updateAppWindow, downloadInfoLabel):
                try:
                    log.info("START: Downloading the installer")
                    with requests.get(Settings.executable_installer_link, stream=True) as r:
                        r.raise_for_status()
                        fd, exe_path = tempfile.mkstemp(suffix = '.exe')
                        log.info(f"Full size: {int(r.headers.get('Content-Length'))}")
                        with open(exe_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=4096):
                                if chunk:
                                    f.write(chunk)
                        os.close(fd)
                    log.info("COMPLETED: Download")
                    downloadInfoLabel.configure(text="Complete. Launching the installer now...")
                    updateAppWindow.update_idletasks()
                    # updateAppWindow.after(10, lambda exe_path=exe_path, updateAppWindow=updateAppWindow: install_update(exe_path, updateAppWindow))
                    threading.Thread(target=install_update, args=(exe_path,updateAppWindow), daemon=True).start()
                except ConnectionError:
                    log.error(f"ERROR: While downloading the executable installer for installing updates: {e}")
                    messagebox.showerror("App Updates", "Cound not download the installer.\n\nPlease check your internet connection and try again.\n\nThank you!")
                except Exception as e:
                    log.error(f"ERROR: While downloading the executable installer for installing updates: {e}")
                    messagebox.showerror("App Updates", "Some error occured while downloading the updates.\n\nPlease check logs or contact the developer.\n\nThank you!")
                    
            updateAppWindow.update_idletasks()
            # updateAppWindow.after(1000, lambda: download(updateAppWindow, downloadInfoLabel))
            threading.Thread(target=download, args=(updateAppWindow, downloadInfoLabel), daemon=True).start()

        Label(updateFrame, text=f"Current Version : {installed_version}", justify="right").grid(row=0, column=0)

        updateInfoLabel = Label(updateFrame, text="Checking for updates...", wraplength=300)
        updateInfoLabel.grid(row=1, column=0, pady=10, padx=10)

        installButton = Button(updateFrame,
                        text="Download and Install",
                        state="disabled",
                        width=20)
        installButton.grid(row=2, column=0, pady=10, padx=10)
        installButton.configure(command= lambda: start_update_manager(installButton))

        makeColumnResponsive(updateFrame)
        updateAppWindow.update()
        updateInfoLabel.after(1000, lambda l=updateInfoLabel, b=installButton, i=installed_version: check_for_update(l, b, i))
        # bring to the center of screen
        x = int((Settings.screen_width/2) - (updateAppWindow.winfo_width()/2))
        y = int((Settings.screen_height/2) - (updateAppWindow.winfo_height()/2))
        updateAppWindow.geometry(f'{updateAppWindow.winfo_width()}x{updateAppWindow.winfo_height()}+{x}+{y}')
    except Exception as e:
        log.error(f"ERROR: while creating update window -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")