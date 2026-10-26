from config import (
    STOP_LOSS_PERCENT,
    PARTIAL_PROFIT_PERCENT,
    PROFIT_TARGET_PERCENT,
)

SIGNAL_COLORS = {
    "SELL": "RED",
    "HOLD": "GREEN",
    "BUY": "DARK_BLUE",
    "MOMENTUM": "YELLOW",
}


def percent_change(entry_price, current_price):
    if entry_price <= 0:
        raise ValueError("entry_price must be greater than zero")
    return ((current_price - entry_price) / entry_price) * 100


def stop_price(entry_price):
    return entry_price * (1 - STOP_LOSS_PERCENT / 100)


def partial_profit_price(entry_price):
    return entry_price * (1 + PARTIAL_PROFIT_PERCENT / 100)


def profit_target_price(entry_price):
    return entry_price * (1 + PROFIT_TARGET_PERCENT / 100)


def momentum_tier(change_percent):
    if change_percent >= 30:
        return 30
    if change_percent >= 20:
        return 20
    if change_percent >= 10:
        return 10
    return 0


def get_signal_color(signal):
    return SIGNAL_COLORS.get(signal, "GRAY")


def trade_decision(entry_price, current_price):
    """Long-only position management: BUY is an entry signal, SELL exits a long."""
    change = percent_change(entry_price, current_price)

    if current_price <= stop_price(entry_price):
        signal = "SELL"
        reason = "STOP_LOSS"
    elif change >= PROFIT_TARGET_PERCENT:
        signal = "SELL"
        reason = "PROFIT_TARGET"
    elif change >= PARTIAL_PROFIT_PERCENT:
        signal = "SELL"
        reason = "PROFIT_TAKING"
    else:
        signal = "HOLD"
        reason = "IN_POSITION"

    return {
        "signal": signal,
        "color": get_signal_color(signal),
        "reason": reason,
        "change_percent": round(change, 2),
        "stop_price": round(stop_price(entry_price), 4),
        "partial_profit_price": round(partial_profit_price(entry_price), 4),
        "profit_target_price": round(profit_target_price(entry_price), 4),
    }
