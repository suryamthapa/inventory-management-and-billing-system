from tkinter import *
from tkinter import messagebox
import time
import datetime
import pytz
from pytz import timezone
# frontend imports
import frontend.config as Settings
import frontend.windows.dashboard as dashboard
from frontend.utils import nepali_datetime
from core.nepali_datetime import date


def exitParent(parent):
    response = messagebox.askyesnocancel("Exit the app", "Are you sure?")
    if response==1:
        parent.destroy()


def makeResponsive(parent):
    n_columns, n_rows = parent.grid_size()
    for i in range(n_rows):
        Grid.rowconfigure(parent, i, weight=1)
    for i in range(n_columns):
        Grid.columnconfigure(parent, i, weight=1)


def makeColumnResponsive(parent):
    n_columns, n_rows = parent.grid_size()
    for i in range(n_columns):
        Grid.columnconfigure(parent, i, weight=1)


def makeRowResponsive(parent):
    n_columns, n_rows = parent.grid_size()
    for i in range(n_rows):
        Grid.rowconfigure(parent, i, weight=1)


def get_nepali_datetime_from_utc(utc_datetime, format="bs"):
    try:
        nepali_timezone = timezone("Asia/Kathmandu")
        utc = pytz.utc
        utc_datetime = utc_datetime.replace(tzinfo=utc)
        ne_datetime_ad = utc_datetime.astimezone(nepali_timezone)
        if format.lower()=="ad":
            return ne_datetime_ad, ""
        elif format.lower()=="bs":
            ne_datetime_bs = nepali_datetime.datetime.from_datetime_datetime(ne_datetime_ad)
            return ne_datetime_bs, ""
        else:
            return None, "Invalid format"
    except Exception as e:
        return None, e


def getCurrentTime():
    # get the current local time from the PC
    t = time.strftime('%I:%M:%S %p')
    # get todays date
    today = date.today()
    today = today.strftime("%B %d, %Y")
    return f"{today}, {t}"


def showCurrentTime(label):
    global PREVIOUS_TIME
    # get the current local time from the PC
    CURRENT_TIME = time.strftime('%I:%M:%S %p')
    # get todays date
    today = date.today()
    TODAY = today.strftime("%B %d, %Y")
    # if time string has changed, update it
    if CURRENT_TIME != Settings.PREVIOUS_TIME:
        Settings.PREVIOUS_TIME = CURRENT_TIME
        label.config(text=f"{TODAY}, {CURRENT_TIME}")
    # calls itself every 200 milliseconds
    # to update the time display as needed
    # could use >200 ms, but display gets jerky
    label.after(200, lambda: showCurrentTime(label))


def handle_buttons_on_activation(deactivation=False):
    buttonFrameMapping = {
        "inventoryFrame":"inventoryButton",
        "settingsFrame": "settingsButton",
        "profileFrame": "profileButton",
        "billingSystemFrame": "billingSystemButton",
        "customersFrame": "customersButton",
        "accountsFrame": "accountsButton",
        "homeFrame":"homeButton",
        "salesAndAnalyticsFrame":"salesAndAnalyticsButton"
    }
    in_version_two = ["salesAndAnalyticsFrame"]
    for frame in Settings.PREMIUM_FEATURES_FRAMES:
        if deactivation:
            eval(f"Settings.{buttonFrameMapping.get(frame)}").config(command=lambda: messagebox.showinfo("InaBi System", "This is the premium feature.\n\nTo use it: Please activate the app with a lisence key. Or please start the trial from home tab.\n\nThank you!"))
        else:
            if frame in in_version_two:
                eval(f"Settings.{buttonFrameMapping.get(frame)}").config(command=lambda : messagebox.showinfo("Sales and Analytics", "Feature comming soon in next update!\n\nYou will be able to view the sales and analytics of your company with the help of this feature.\n\nThank you!"))
            else:
                eval(f"Settings.{buttonFrameMapping.get(frame)}").config(command=lambda x=frame: dashboard.showFrame(x))

    