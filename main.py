from scanner import scan_stock
from rules import trade_decision
from candle_rules import candle_signal


def analyze_stock(
    price,
    volume,
    change_percent,
    entry_price=None,
    candle=None,
    reference_high=None,
    reference_low=None,
):
    scan = scan_stock(
        price,
        volume,
        change_percent,
    )

    result = {
        "scan": scan,
        "trade": None,
        "candle": None,
    }

    if entry_price is not None:
        result["trade"] = trade_decision(
            entry_price,
            price,
        )

    if candle is not None:
        result["candle"] = candle_signal(
            candle,
            reference_high=reference_high,
            reference_low=reference_low,
        )

    return result


if __name__ == "__main__":
    print("Market Bot is ready for testing.")
    print("Candle colors:")
    print("MOMENTUM = YELLOW")
    print("BUY ENTRY = DARK_BLUE")
    print("HOLD / NORMAL UP = GREEN")
    print("SELL / DOWN = RED")
