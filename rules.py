from config import (
    STOP_LOSS_PERCENT,
    PARTIAL_PROFIT_PERCENT,
)


SIGNAL_COLORS = {
    "SELL": "RED",
    "HOLD": "GREEN",
    "BUY": "YELLOW",
    "SHORT_SELL": "ORANGE",
}


def percent_change(entry_price, current_price):
    return ((current_price - entry_price) / entry_price) * 100


def stop_price(entry_price):
    return entry_price * (1 - STOP_LOSS_PERCENT / 100)


def partial_profit_price(entry_price):
    return entry_price * (1 + PARTIAL_PROFIT_PERCENT / 100)


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
    if current_price <= stop_price(entry_price):
        signal = "SELL"
    elif current_price >= partial_profit_price(entry_price):
        signal = "BUY"
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "color": get_signal_color(signal),
    }
