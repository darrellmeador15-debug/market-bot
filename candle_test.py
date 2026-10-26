from candle_rules import (
    is_red,
    is_green,
    is_bullish_recovery,
    has_two_bearish_pullbacks,
    breakout_confirmation,
    breakdown_confirmation,
    candle_signal,
)


def run_candle_tests():
    red = {"open": 10.00, "high": 10.05, "low": 9.70, "close": 9.80}
    green = {"open": 9.80, "high": 10.20, "low": 9.75, "close": 10.10}
    green_breakout = {"open": 10.10, "high": 10.40, "low": 10.05, "close": 10.30}
    red_breakdown = {"open": 9.80, "high": 9.90, "low": 9.40, "close": 9.50}
    momentum = {
        "open": 10.00, "high": 10.40, "low": 9.95, "close": 10.35,
        "change_percent": 22.0,
    }

    assert is_red(red)
    assert is_green(green)
    assert is_bullish_recovery(red, green)
    assert has_two_bearish_pullbacks([red, red, green])
    assert breakout_confirmation(green_breakout, 10.20)
    assert breakdown_confirmation(red_breakdown, 9.60)

    buy = candle_signal(green_breakout, reference_high=10.20)
    assert buy["signal"] == "BUY"
    assert buy["color"] == "DARK_BLUE"
    assert buy["body_color"] == "DARK_BLUE"
    assert buy["wick_color"] == "DARK_BLUE"

    short_or_sell = candle_signal(red_breakdown, reference_low=9.60)
    assert short_or_sell["signal"] == "SELL"
    assert short_or_sell["color"] == "RED"

    momentum_result = candle_signal(momentum)
    assert momentum_result["signal"] == "MOMENTUM"
    assert momentum_result["color"] == "YELLOW"

    sell = candle_signal(red)
    assert sell["signal"] == "SELL"
    assert sell["color"] == "RED"

    hold = candle_signal(green)
    assert hold["signal"] == "HOLD"
    assert hold["color"] == "GREEN"

    print("All candle tests passed.")
    print("MOMENTUM = YELLOW")
    print("BUY ENTRY = DARK_BLUE")
    print("HOLD / NORMAL UP = GREEN")
    print("SELL / DOWN = RED")


if __name__ == "__main__":
    run_candle_tests()
