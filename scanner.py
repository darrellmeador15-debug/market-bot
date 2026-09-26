from config import (
    MIN_PRICE,
    MAX_PRICE,
    MIN_LIQUIDITY,
    MOMENTUM_LEVELS,
    EXCLUDE_CHINA_STOCKS,
)


def qualifies_price(price):
    return MIN_PRICE <= price <= MAX_PRICE


def qualifies_liquidity(volume):
    return volume >= MIN_LIQUIDITY


def qualifies_momentum(change_percent):
    return any(
        change_percent >= level
        for level in MOMENTUM_LEVELS
    )


def momentum_tier(change_percent):
    if change_percent >= 30:
        return 30

    if change_percent >= 20:
        return 20

    if change_percent >= 10:
        return 10

    return 0


def qualifies_country(country):
    if not EXCLUDE_CHINA_STOCKS:
        return True

    if country is None:
        return True

    return country.upper() not in {
        "CHINA",
        "CN",
        "HONG KONG",
        "HK",
    }


def scan_stock(
    price,
    volume,
    change_percent,
    country=None,
):
    price_ok = qualifies_price(price)
    liquidity_ok = qualifies_liquidity(volume)
    momentum_ok = qualifies_momentum(change_percent)
    country_ok = qualifies_country(country)

    return {
        "price_ok": price_ok,
        "liquidity_ok": liquidity_ok,
        "momentum_ok": momentum_ok,
        "country_ok": country_ok,
        "momentum_tier": momentum_tier(change_percent),
        "qualifies": (
            price_ok
            and liquidity_ok
            and momentum_ok
            and country_ok
        ),
    }


def scan_long_setup(
    price,
    volume,
    change_percent,
    country=None,
):
    result = scan_stock(
        price,
        volume,
        change_percent,
        country,
    )

    return result["qualifies"]


def scan_short_setup(
    price,
    volume,
    change_percent,
    country=None,
):
    result = scan_stock(
        price,
        volume,
        change_percent,
        country,
    )

    return (
        result["price_ok"]
        and result["liquidity_ok"]
        and result["country_ok"]
        and change_percent <= -10
    )


if __name__ == "__main__":
    print("Market Bot scanner ready.")
    print("Price range: $0.50 - $15.00")
    print("Minimum liquidity: 8,000,000")
    print("Momentum levels: 10%, 20%, 30%")
    print("China stocks excluded.")
    print("Long and short setups supported.")
