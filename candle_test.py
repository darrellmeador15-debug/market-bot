from candle_rules import (
    is_red,
    is_green,
    is_bullish_recovery,
    has_two_bearish_pullbacks,
    breakout_confirmation,
)


def run_candle_tests():
    red = {
        "open": 10.00,
        "high": 10.05,
        "low": 9.70,
        "close": 9.80,
    }

    green = {
        "open": 9.80,
        "high": 10.20,
        "low": 9.75,
        "close": 10.10,
    }

    green_breakout = {
        "open": 10.10,
        "high": 10.40,
        "low": 10.05,
        "close": 10.30,
    }

    assert is_red(red)
    assert is_green(green)
    assert is_bullish_recovery
