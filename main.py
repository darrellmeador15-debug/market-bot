from scanner import scan_stock
from strategy import evaluate_trade


def analyze_stock(price, volume, change_percent, entry_price=None):
    scan = scan_stock(price, volume, change_percent)

    result = {
        "scan": scan,
        "trade": None,
    }

    if entry_price is not None:
        result["trade"] = evaluate_trade(entry_price, price)

    return result


if __name__ == "__main__":
    print("Market Bot is ready for testing.")
