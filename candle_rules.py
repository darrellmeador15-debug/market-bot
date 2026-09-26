def is_red(candle):
    return candle["close"] < candle["open"]


def is_green(candle):
    return candle["close"] > candle["open"]


def is_bullish_recovery(previous_candle, current_candle):
    return (
        is_red(previous_candle)
        and is_green(current_candle)
        and current_candle["close"] > previous_candle["high"]
    )


def has_two_bearish_pullbacks(candles):
    bearish_count = sum(is_red(candle) for candle in candles)
    return bearish_count >= 2


def breakout_confirmation(candle, reference_high):
    return (
        is_green(candle)
        and candle["close"] > reference_high
    )


def breakdown_confirmation(candle, reference_low):
    return (
        is_red(candle)
        and candle["close"] < reference_low
    )


def candle_signal(candle, reference_high=None, reference_low=None):
    if reference_high is not None and breakout_confirmation(
        candle, reference_high
    ):
        return {
            "signal": "BUY",
            "color": "YELLOW",
        }

    if reference_low is not None and breakdown_confirmation(
        candle, reference_low
    ):
        return {
            "signal": "SHORT_SELL",
            "color": "ORANGE",
        }

    if is_red(candle):
        return {
            "signal": "SELL",
            "color": "RED",
        }

    if is_green(candle):
        return {
            "signal": "HOLD",
            "color": "GREEN",
        }

    return {
        "signal": "HOLD",
        "color": "GREEN",
    }
