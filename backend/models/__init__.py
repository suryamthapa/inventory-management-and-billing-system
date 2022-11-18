import enum

class LisenceStatus(enum.Enum):
    expired = 0
    active = 1
    not_activated_yet = 2

class AccountType(enum.Enum):
    debit = 0
    credit = 1