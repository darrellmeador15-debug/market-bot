from config import (
    STOP_LOSS_PERCENT,
    PARTIAL_PROFIT_PERCENT,
    PROFIT_TARGET_PERCENT,
)


def calculate_stop(entry_price):
    return entry_price * (1 - STOP_LOSS_PERCENT / 100)


def calculate_partial_profit(entry_price):
    return entry_price * (1 + PARTIAL_PROFIT_PERCENT / 100)


def calculate_profit_target(entry_price):
    return entry_price * (1 + PROFIT_TARGET_PERCENT / 100)


def evaluate_trade(entry_price, current_price):
    """Manage an existing long position only; never generate a short entry."""
    if entry_price <= 0:
        raise ValueError("entry_price must be greater than zero")

    change_percent = ((current_price - entry_price) / entry_price) * 100

    if current_price <= calculate_stop(entry_price):
        return "STOP"

    if change_percent >= PROFIT_TARGET_PERCENT:
        return "TAKE_PROFIT"

    if change_percent >= PARTIAL_PROFIT_PERCENT:
        return "PROFIT_ZONE"

    return "HOLD"
