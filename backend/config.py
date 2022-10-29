import logging


class Settings:
    DATABASE_NAME = "imabs.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_NAME}"
    COMPANY_PROFILE_TABLE_NAME = "company_profile"
    APP_SETTINGS_TABLE_NAME = "app_settings"
    CUSTOMERS_TABLE_NAME = "customers"
    PRODUCTS_TABLE_NAME = "products"
    SALES_TABLE_NAME = "sales"
    LOG_PATH = "./logs/backend.log"
    PAGE_LIMIT = 11

