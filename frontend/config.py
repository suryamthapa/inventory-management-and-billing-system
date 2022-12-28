from tkinter import *
from tkinter.font import Font
from tkinter import font
import os
import logging
from frontend.utils.lisences import getLisenceInfo
from frontend.utils.products import refreshProductsList
from frontend.utils.customers import refreshCustomersList
import frontend.utils.purchase as purchaseUtils
import frontend.utils.vendors as vendorUtils
from frontend.utils.settings import getSettings
from frontend.utils.sales import refreshTotalSales
log = logging.getLogger("frontend")

try:
    from core.appConfigurations import version_info_link, executable_installer_link
except Exception as e:
    log.exception(f"ERROR: {e}")
    version_info_link = ""
    executable_installer_link = ""

version_info_link = "https://raw.githubusercontent.com/datakhoj/InaBi-System-Public/main/versionInfo.txt" if not version_info_link else version_info_link
executable_installer_link = "https://github.com/datakhoj/InaBi-System-Public/blob/main/Inventory%20Management%20and%20Billing%20System.exe?raw=true" if not executable_installer_link else executable_installer_link

DATE_TIME_TYPE = "NEPALI"
PREMIUM_FEATURES_FRAMES = ["inventoryFrame",
                            "billingSystemFrame",
                            "customersFrame",
                            "salesAndAnalyticsFrame", 
                            "accountsFrame", 
                            "purchaseEntrySystemFrame",
                            "purchaseViewFrame"
                        ]
# constants
CURRENT_WORKING_DIRECTORY = os.getcwd()
CURRENT_SETTINGS = getSettings()
LISENCE_INFO = getLisenceInfo()

# Settings
CURRENCY_LIST = ["NPR", "INR", "USD"]
UNITS_LIST = ["PCS", "KGS", "GRAMS", "METER", "BAGS"]

# global variables
PREVIOUS_TIME = ''
CURRENT_FRAME = "homeFrame"

# customers info
CUSTOMERS_LIST = None
refreshCustomersList()

# customers info
VENDORS_LIST = None
vendorUtils.refreshVendorsList()

# products info
PRODUCTS_LIST = None
refreshProductsList()

# purchase info
PURCHASE_LIST = None
purchaseUtils.refreshPurchasesList()

# pagination and search queries
PAGINATION_PAGE = 1
PAGINATION_PAGE_LIMIT = 11
CURRENT_SEARCH_QUERY = {
    "customers":{},
    "products":{},
    "accounts":{},
    "vendors":{},
    "purchases":{}
}
BILL_DETAILS = {
    "customer":{},
    "products":{},
    "extra":{},
    "final":{}
}
PURCHASE_DETAILS = {
    "vendor":{},
    "products":{},
    "extra":{},
    "final":{}
}
CURRENT_LEDGER_ACCOUNT = {
    "customer":{},
    "account":{},
    "from":"",
    "to":"",
    "summary":{
            "dr_amount":0.00,
            "cr_amount":0.00,
            "account_balance":0.00
        }
}

TOTAL_SALES = {}
refreshTotalSales()

# global buttons
homeButton = None
profileButton = None
inventoryButton = None
customersButton = None
vendorsButton = None
accountsButton = None
purchaseButton = None
settingsButton = None
billingSystemButton = None
purchaseEntrySystemButton = None
purchaseViewButton = None
salesAndAnalyticsButton = None
exitButton = None
paginationBackButton = None
paginationForwardButton = None

buttonFrameMapping = {
        "homeFrame":"homeButton",
        "profileFrame": "profileButton",
        "customersFrame": "customersButton",
        "accountsFrame": "accountsButton",
        "vendorsFrame": "vendorsButton",
        "purchaseEntrySystemFrame":"purchaseEntrySystemButton",
        "purchaseViewFrame":"purchaseViewButton",
        "inventoryFrame":"inventoryButton",
        "billingSystemFrame": "billingSystemButton",
        "salesAndAnalyticsFrame":"salesAndAnalyticsButton",
        "settingsFrame": "settingsButton",
    }

# global labels
appStatusLabel = None
sidebarBrandName = None
profileBrandName = None
paginationPageInfo = None

# global entries
queryEntry = None
billingProductNameEntry = None
billingCustomerNameEntry = None
purchaseProductNameEntry = None
purchaseVendorNameEntry = None

# global listbox
progressbar = None
billPreviewBox = None

# global frames
topBar = None
mainFrame = None
homeFrame = None

inventoryFrame = None
tableTop = None
inventoryTable = None

profileFrame = None
settingsFrame = None

billingSystemFrame = None
billDetailsFrame = None
billDetailsTable = None

purchaseEntrySystemFrame = None
purchaseDetailsFrame = None
purchaseDetailsTable = None

purchaseViewFrame = None
purchaseViewTable = None

# global canvas
tableCanvas = None

# to load name and phone number of customer
namePhFrame = None
# to load rate and quantity of product
rateQtyFrame = None

customersFrame = None
customersTable = None

vendorsFrame = None
vendorsTable = None

customersFilterOptionsMap = {
            "Individual Name": "full_name",
            "Company Name": "company",
            "Company PAN no": "company_pan_no",
            "Phone Number": "phone_number",
            "Telephone": "telephone",
            "Email": "email"
        }
vendorsFilterOptionsMap = {
            "Vendor Name": "vendor_name",
            "Vat Number": "vat_number",
            "Phone Number": "phone_number",
            "Telephone": "telephone",
            "Email": "email"
        }
purchaseFilterOptionsMap = {
            "Invoice Number": "invoice_number",
            "Vendor VAT/PAN Number": "vat_number",
            "Vendor Name": "vendor_name",
            "Vendor Telephone": "telephone",
            "Vendor Phone Number": "phone_number",
            "Vendor Email": "email"
        }
productsFilterOptionsMap = {
            "Product name": "product_name"
        }
filterOption = None
billingCustomerfilterOption = None
purchaseVendorfilterOption = None

accountsFrame = None
accountsTable = None
ledgerDetailsMainFrame = None
ledgerDetailsArea = None
ledgerDetailsFrame = None
accountCustomerDetailsFrame=None
ledgerDetailsTable = None

salesAndAnalyticsFrame = None

# colors
appWhite = "#DFF6FF"
appBlue = "#47B5FF"
appGreen = "#256D85"
appDarkGreen = "#06283D"

# app configurations
app = Tk()
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
app.geometry(f"{1200}x{720}")
app.title("Inventory Management and Billing System")
app.state("zoomed")
app.iconbitmap("./frontend/assets/images/favicon.ico")
app.configure(bg=appWhite)

defaultBgColor = None

# fonts
appFontSmall = Font(family="Helvetica", size=9, weight="normal", slant="roman", underline=0, overstrike=0)
appFontSmallBold = Font(family="Helvetica", size=9, weight="bold", slant="roman", underline=0, overstrike=0)

appFontNormal = Font(family="Helvetica", size=12, weight="normal", slant="roman", underline=0, overstrike=0)
appFontNormalBold = Font(family="Helvetica", size=12, weight="bold", slant="roman", underline=0, overstrike=0)

appFontMedium = Font(family="Helvetica", size=15, weight="normal", slant="roman", underline=0, overstrike=0)
appFontMediumBold = Font(family="Helvetica", size=15, weight="bold", slant="roman", underline=0, overstrike=0)

appFontBig = Font(family="Helvetica", size=18, weight="normal", slant="roman", underline=0, overstrike=0)
appFontBigBold = Font(family="Helvetica", size=18, weight="bold", slant="roman", underline=0, overstrike=0)

# Creating a Font object of "TkDefaultFont"
defaultFont = font.nametofont("TkDefaultFont")
# Overriding default-font with custom settings
# i.e changing font-family, size and weight
defaultFont.configure(family="Helvetica",
                    size=10,
                    weight=font.NORMAL)


# app defaults
defaultEntryBorderWidth = 2

# app.mainloop()