from config import STOP_LOSS_PERCENT, PARTIAL_PROFIT_PERCENT


def calculate_stop(entry_price):
    return entry_price * (1 - STOP_LOSS_PERCENT / 100)


def calculate_partial_profit(entry_price):
    return entry_price * (1 + PARTIAL_PROFIT_PERCENT / 100)


def evaluate_trade(entry_price, current_price):
    stop_price = calculate_stop(entry_price)
    partial_profit_price = calculate_partial_profit(entry_price)

    if current_price <= stop_price:
        return "STOP"

    if current_price >= partial_profit_price:
        return "PARTIAL_PROFIT"

    return "HOLD"
