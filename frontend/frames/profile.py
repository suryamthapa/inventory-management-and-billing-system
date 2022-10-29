# built-in module imports
import logging
from PIL import ImageTk
from PIL import Image as PILImage
from tkinter import messagebox
from tkinter import *
import os
# frontend imports
import frontend.config as Settings
import frontend.windows.dashboard as dashboard
# backend imports
from backend.api.settings import add_update_setting


log = logging.getLogger("frontend")


def createProfileFrame(parent):
    companyProfile = Settings.CURRENT_SETTINGS.get("company_profile") if Settings.CURRENT_SETTINGS.get("company_profile") else {}
    companyName = companyProfile.get("company_name") if companyProfile.get("company_name") else ""
    panNo = companyProfile.get("pan_no") if companyProfile.get("pan_no") else ""
    phoneNumber = companyProfile.get("phone_number") if companyProfile.get("phone_number") else ""
    telephone = companyProfile.get("telephone") if companyProfile.get("telephone") else ""
    primaryOwner = companyProfile.get("primary_owner") if companyProfile.get("primary_owner") else ""
    secondaryOwner = companyProfile.get("secondary_owner") if companyProfile.get("secondary_owner") else ""
    country = companyProfile.get("country") if companyProfile.get("country") else ""
    province = companyProfile.get("province") if companyProfile.get("province") else ""
    district = companyProfile.get("district") if companyProfile.get("district") else ""
    municipality = companyProfile.get("municipality") if companyProfile.get("municipality") else ""
    ward = companyProfile.get("ward") if companyProfile.get("ward") else ""
    toll = companyProfile.get("toll") if companyProfile.get("toll") else ""
    zipCode = companyProfile.get("zip_code") if companyProfile.get("zip_code") else ""
    
    Settings.profileFrame = Frame(parent, borderwidth=1)
    Settings.profileFrame.pack(fill="both", expand=True, padx=10)

    branding = Frame(Settings.profileFrame, borderwidth=0)
    branding.pack(fill="x", pady=10, expand=True)

    global companyLogo
    companyLogo = PILImage.open(os.path.join(Settings.CURRENT_WORKING_DIRECTORY, "frontend","assets","images","logo.png"))
    companyLogo = companyLogo.resize((120,120))
    companyLogo = ImageTk.PhotoImage(companyLogo)
    Label(branding, image=companyLogo).pack(pady=(0, 10))
    Settings.profileBrandName = Label(branding, text=companyName, width=20, wraplength=160, font=Settings.appFontNormalBold)
    Settings.profileBrandName.pack()

    generalInfoframe = Frame(Settings.profileFrame, borderwidth=0)
    generalInfoframe.pack(fill="x", pady=10)
    
    generalInfoframe1 = Frame(generalInfoframe, borderwidth=0)
    generalInfoframe1.pack(fill="x", pady=5)
    
    companyNameFrame = LabelFrame(generalInfoframe1, borderwidth=0)
    companyNameFrame.pack(side="left", fill="x", expand=True)
    Label(companyNameFrame, text="Company Name").grid(row=0, column=0, sticky=W)
    companyNameEntry = Entry(companyNameFrame, width=40, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    companyNameEntry.grid(row=0, column=1, padx=10, sticky=W)
    companyNameEntry.insert(0, companyName)
    
    panNoFrame = LabelFrame(generalInfoframe1, borderwidth=0)
    panNoFrame.pack(side="right", fill="x", expand=True)
    Label(panNoFrame, text="PAN No.").grid(row=0, column=0, sticky=W)
    panNoEntry = Entry(panNoFrame, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    panNoEntry.grid(row=0, column=1, padx=10, sticky=W)
    panNoEntry.insert(0, panNo)
    
    
    generalInfoframe2 = Frame(generalInfoframe, borderwidth=0)
    generalInfoframe2.pack(fill="x", pady=5)

    phoneNumberFrame = LabelFrame(generalInfoframe2, borderwidth=0)
    phoneNumberFrame.pack(side="left", fill="x", expand=True)
    Label(phoneNumberFrame, text="Phone Number").grid(row=0, column=0, sticky=W)
    phoneNumberEntry = Entry(phoneNumberFrame, width=40, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    phoneNumberEntry.grid(row=0, column=1, padx=10, sticky=W)
    phoneNumberEntry.insert(0, phoneNumber)
    
    telephoneFrame = LabelFrame(generalInfoframe2, borderwidth=0)
    telephoneFrame.pack(side="right", fill="x", expand=True)
    Label(telephoneFrame, text="Telephone").grid(row=0, column=0, sticky=W)
    telephoneEntry = Entry(telephoneFrame, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    telephoneEntry.grid(row=0, column=1, padx=10, sticky=W)
    telephoneEntry.insert(0, telephone)

    otherInfoWrapper = Frame(Settings.profileFrame)
    otherInfoWrapper.pack(fill="x", pady=10)

    addressInfoframe = LabelFrame(otherInfoWrapper, text="Address Info", borderwidth=1)
    addressInfoframe.pack(side="left", fill="x", padx=(0, 10), expand=True)

    Label(addressInfoframe, text="Country", justify="left").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    countryNameEntry = Entry(addressInfoframe, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    countryNameEntry.grid(row=0, column=1, padx=5, pady=5, sticky=W)
    countryNameEntry.insert(0, country)
    Label(addressInfoframe, text="Province").grid(row=0, column=2, padx=5, pady=5, sticky=W)
    provinceNameEntry = Entry(addressInfoframe, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    provinceNameEntry.grid(row=0, column=3, padx=5, pady=5, sticky=W)
    provinceNameEntry.insert(0, province)

    Label(addressInfoframe, text="Disctict").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    districtNameEntry = Entry(addressInfoframe, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    districtNameEntry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
    districtNameEntry.insert(0, district)
    Label(addressInfoframe, text="Municipality").grid(row=1, column=2, padx=5, pady=5, sticky=W)
    municipalityNameEntry = Entry(addressInfoframe, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    municipalityNameEntry.grid(row=1, column=3, padx=5, pady=5, sticky=W)
    municipalityNameEntry.insert(0, municipality)

    Label(addressInfoframe, text="Ward").grid(row=2, column=0, padx=5, pady=5, sticky=W)
    wardNoEntry = Entry(addressInfoframe, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    wardNoEntry.grid(row=2, column=1, padx=5, pady=5, sticky=W)
    wardNoEntry.insert(0, ward)
    Label(addressInfoframe, text="Toll").grid(row=2, column=2, padx=5, pady=5, sticky=W)
    tollNameEntry = Entry(addressInfoframe, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    tollNameEntry.grid(row=2, column=3, padx=5, pady=5, sticky=W)
    tollNameEntry.insert(0, toll)

    Label(addressInfoframe, text="Zip code").grid(row=3, column=0, padx=5, pady=5, sticky=W)
    zipCodeEntry = Entry(addressInfoframe, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal)
    zipCodeEntry.grid(row=3, column=1, padx=5, pady=5, sticky=W)
    zipCodeEntry.insert(0, zipCode)

    ownersInfoframe = LabelFrame(otherInfoWrapper, text="Owner Info", borderwidth=1, pady=5)
    ownersInfoframe.pack(side="left", fill="x", padx=(10,0), expand=True)

    Label(ownersInfoframe, text="Primary").grid(row=0, column=0, padx=5, pady=5, sticky=W)
    primaryOwnerNameEntry = Entry(ownersInfoframe, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal, width=30)
    primaryOwnerNameEntry.grid(row=0, column=1, pady=5, sticky=W)
    primaryOwnerNameEntry.insert(0, primaryOwner)
    Label(ownersInfoframe, text="Secondary").grid(row=1, column=0, padx=5, pady=5, sticky=W)
    secondaryOwnerNameEntry = Entry(ownersInfoframe, bd=Settings.defaultEntryBorderWidth, font=Settings.appFontNormal, width=30)
    secondaryOwnerNameEntry.grid(row=1, column=1, pady=5, sticky=W)
    secondaryOwnerNameEntry.insert(0, secondaryOwner)

    def saveProfileData():
        if companyName==companyNameEntry.get() and primaryOwner==primaryOwnerNameEntry.get() and \
                        secondaryOwner==secondaryOwnerNameEntry.get() and panNo==panNoEntry.get() and \
                        phoneNumber==phoneNumberEntry.get() and telephone==telephoneEntry.get() and \
                        country==countryNameEntry.get() and province==provinceNameEntry.get() and \
                        district==districtNameEntry.get() and municipality==municipalityNameEntry.get() and \
                        ward==wardNoEntry.get() and zipCode==zipCodeEntry.get():
            messagebox.showinfo("Company Profile", "No information has been changed.")
            return None
        companyProfile = {"company_name":companyNameEntry.get(),
                        "primary_owner":primaryOwnerNameEntry.get(),
                        "secondary_owner":secondaryOwnerNameEntry.get(),
                        "pan_no":panNoEntry.get(),
                        "phone_number":phoneNumberEntry.get(),
                        "telephone":telephoneEntry.get(),
                        "country":countryNameEntry.get(),
                        "province":provinceNameEntry.get(),
                        "district":districtNameEntry.get(),
                        "municipality":municipalityNameEntry.get(),
                        "ward":wardNoEntry.get(),
                        "toll":tollNameEntry.get(),
                        "zip_code":zipCodeEntry.get()}
        status, message = add_update_setting(data={"company_profile":str(companyProfile)})
        if status:
            # refresh brand names accross labels and constants
            Settings.CURRENT_SETTINGS["company_profile"] = companyProfile
            Settings.profileBrandName.config(text=companyNameEntry.get())
            Settings.sidebarBrandName.config(text=companyNameEntry.get())
            messagebox.showinfo("Company Profile", message)
            dashboard.showFrame("profileFrame", refreshMode=True)
        else:
            messagebox.showerror("Company Profile", message)

    saveButton = Button(Settings.profileFrame, 
                        text="Save",
                        bg=Settings.appBlue,
                        fg=Settings.appDarkGreen,
                        width=20,
                        command=saveProfileData)
    saveButton.pack(side="right", ipadx=20, pady=50, padx=20)


def openProfile(parent):
    try:
        createProfileFrame(parent)
    except Exception as e:
        log.error(f"ERROR: while creating home frame -> {e}")
        messagebox.showerror("InaBi System","Error occured!\n\nPlease check logs or contact the developer.\n\nThank you!")