from config import (
    MIN_PRICE,
    MAX_PRICE,
    MIN_LIQUIDITY,
    MOMENTUM_LEVELS,
)


def qualifies_price(price):
    return MIN_PRICE <= price <= MAX_PRICE


def qualifies_liquidity(volume):
    return volume >= MIN_LIQUIDITY


def qualifies_momentum(change_percent):
    return any(change_percent >= level for level in MOMENTUM_LEVELS)


def scan_stock(price, volume, change_percent):
    return {
        "price_ok": qualifies_price(price),
        "liquidity_ok": qualifies_liquidity(volume),
        "momentum_ok": qualifies_momentum(change_percent),
    }
