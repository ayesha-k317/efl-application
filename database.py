import sqlite3
from decimal import Decimal
from pathlib import Path

import config
from errors import RateUnavailableError

BASE_DIR = Path(__file__).parent

def get_connection(db_file=None):
    """Open a connection to the SQLite database."""
    connection = sqlite3.connect(db_file or config.DB_FILE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def init_db(db_file=None):
    """Create the tables from schema.sql and add the starting data."""
    script = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    connection = get_connection(db_file)
    connection.executescript(script)
    seed_reference_data(connection)
    connection.commit()
    connection.close()

def seed_reference_data(connection):
    """Insert currencies, sample rates, plans, tax rules and the demo user."""
    for code in config.CURRENCIES:
        name, symbol = config.CURRENCY_NAMES[code]
        connection.execute(
            "INSERT OR IGNORE INTO currency (currency_code, name, symbol) VALUES (?, ?, ?)",
            (code, name, symbol),
        )
        has_rate = connection.execute(
            "SELECT 1 FROM exchange_rate WHERE currency_code = ?", (code,)
        ).fetchone()
        if has_rate is None:
            connection.execute(
                "INSERT INTO exchange_rate (currency_code, rate_to_usd, source) VALUES (?, ?, 'sample')",
                (code, float(config.SAMPLE_RATES_TO_USD[code])),
            )
    for plan in config.PLANS:
        connection.execute(
            "INSERT OR IGNORE INTO investment_plan VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            plan,
        )
    has_rules = connection.execute("SELECT 1 FROM tax_rule").fetchone()
    if has_rules is None:
        connection.executemany(
            "INSERT INTO tax_rule (plan_id, profit_above, tax_rate_pct) VALUES (?, ?, ?)",
            config.TAX_RULES,
        )
    connection.execute(
        "INSERT OR IGNORE INTO user (user_id, name, email, password_hash) VALUES (?, 'Demo user', 'demo@efl.test', 'not-set')",
        (config.DEMO_USER_ID,),
    )

def get_rate_to_usd(currency_code, db_file=None):
    """Return the newest rate for this currency as a Decimal."""
    connection = get_connection(db_file)
    try:
        row = connection.execute(
            "SELECT rate_to_usd FROM exchange_rate WHERE currency_code = ? ORDER BY fetched_at DESC, rate_id DESC LIMIT 1",
            (currency_code,),
        ).fetchone()
    finally:
        connection.close()                                              # Release the file
    if row is None:                                                     # No rate stored for this currency
        raise RateUnavailableError("No exchange rate is available for " + str(currency_code) + ".")  # Stop with a clear error; the route turns it into a message
    return Decimal(str(row["rate_to_usd"]))                             # str() first, so Decimal gets 1.3 and not 1.3000000000000000444

def list_currencies(db_file=None):                                      # The currencies to show in the drop-down lists
    """Return the active currencies as a list of dictionaries."""       # Docstring
    connection = get_connection(db_file)                                # Open the database
    try:                                                                # Always close the connection
        rows = connection.execute(                                      # Start a SELECT statement
            "SELECT currency_code, name, symbol FROM currency WHERE is_active = 1 ORDER BY currency_code"  # Only active currencies, in code order
        ).fetchall()                                                    # fetchall gives every row
    finally:                                                            # Runs whether or not an error happened
        connection.close()                                              # Release the file
    return [{"code": r["currency_code"], "name": r["name"], "symbol": r["symbol"]} for r in rows]  # Turn each row into a plain dictionary Flask can send as JSON

def save_transaction(user_id, transaction, db_file=None):               # Store one finished conversion and return its id
    """Insert a conversion transaction and return its id."""            # Docstring
    connection = get_connection(db_file)                                # Open the database
    try:                                                                # Always close the connection
        cursor = connection.execute(                                    # Start an INSERT statement
            "INSERT INTO conversion_transaction (user_id, from_currency, to_currency, amount, rate_used, fee_percent, fee_usd, converted_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",  # Eight columns, eight ? marks
            (                                                           # The eight values, in the same order
                user_id,                                                # Who converted
                transaction["from_currency"],                           # Currency sold
                transaction["to_currency"],                             # Currency bought
                float(transaction["amount"]),                           # SQLite stores REAL, so Decimal becomes float
                float(transaction["rate_used"]),                        # The rate we used
                float(transaction["fee_percent"]),                      # Band percentage
                float(transaction["fee_usd"]),                          # Fee in US dollars
                float(transaction["converted_amount"]),                 # What the user receives
            ),                                                          # End of the values
        )                                                               # End of the INSERT
        connection.commit()                                             # Save permanently
        return cursor.lastrowid                                         # The auto number SQLite gave the new row
    finally:                                                            # Runs even after the return above
        connection.close()                                              # Release the file