from decimal import Decimal, InvalidOperation

import config
import quotes
from errors import InputError


def validate_amount(text):
    """Return the amount as a Decimal, or raise InputError with a clear message."""
    try:
        amount = Decimal(str(text).strip())
    except InvalidOperation:
        raise InputError("Enter the amount as a number, for example 500.")
    if not amount.is_finite():
        raise InputError("Enter the amount as a number, for example 500.")
    if amount.as_tuple().exponent < -2:
        raise InputError("Use at most two decimal places.")
    if amount < config.MIN_TRANSACTION or amount > config.MAX_TRANSACTION:
        raise InputError(f"The amount must be between {config.MIN_TRANSACTION:,} and {config.MAX_TRANSACTION:,}.")
    return amount


def validate_currency(code):
    """Return the code in capitals, or raise InputError."""
    clean = str(code).strip().upper()
    if clean not in config.CURRENCIES:
        raise InputError("Choose one of: " + ", ".join(config.CURRENCIES) + ".")
    return clean


def validate_money(text, label):
    """Return a Decimal that is not negative and has at most two decimal places."""
    try:
        value = Decimal(str(text).strip())
    except InvalidOperation:
        raise InputError(f"Enter the {label} as a number, for example 250.00.")
    if not value.is_finite():
        raise InputError(f"Enter the {label} as a number, for example 250.00.")
    if value.as_tuple().exponent < -2:
        raise InputError(f"Use at most two decimal places for the {label}.")
    if value < 0:
        raise InputError(f"The {label} cannot be negative.")
    if value > config.MAX_QUOTE_INPUT:
        raise InputError(f"The {label} is too large.")
    return value


def validate_plan_id(value, plans):
    """Return the chosen plan dictionary, or raise InputError."""
    try:
        plan_id = int(str(value).strip())
    except ValueError:
        raise InputError("Choose an investment type.")
    for plan in plans:
        if plan["plan_id"] == plan_id:
            return plan
    raise InputError("Choose an investment type.")


def validate_quote_inputs(plan, lump_sum, monthly):
    """Raise InputError listing every rule the chosen plan breaks."""
    reasons = quotes.check_eligibility(plan, lump_sum, monthly)
    if reasons:
        raise InputError(" ".join(reasons))