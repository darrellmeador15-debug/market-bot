"""Candle classification and color rules for Market Bot.

Colors are intended to be used for both candle bodies and wicks:
- YELLOW: momentum candle (strong move, not yet the entry trigger)
- DARK_BLUE: confirmed BUY / entry candle
- GREEN: ordinary bullish candle / HOLD
- RED: bearish candle / SELL or downward move

Optional candle fields:
- momentum: bool, explicit momentum classification from the scanner
- change_percent: stock's percentage change for the session
- volume and average_volume: optional volume confirmation inputs
"""

MOMENTUM_CHANGE_PERCENT = 20.0
MOMENTUM_VOLUME_MULTIPLE = 2.0


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
    return is_green(candle) and candle["close"] > reference_high


def breakdown_confirmation(candle, reference_low):
    return is_red(candle) and candle["close"] < reference_low


def is_momentum_candle(candle):
    """Identify a momentum candle separately from the actual BUY trigger.

    An upstream scanner may explicitly set candle['momentum'].
    Otherwise, a session gain of at least 20% or volume at least 2x
    average volume can flag momentum. These are configurable defaults.
    """
    if candle.get("momentum") is True:
        return True

    change_percent = candle.get("change_percent")
    if change_percent is not None and change_percent >= MOMENTUM_CHANGE_PERCENT:
        return True

    volume = candle.get("volume")
    average_volume = candle.get("average_volume")
    if (
        volume is not None
        and average_volume is not None
        and average_volume > 0
        and volume >= MOMENTUM_VOLUME_MULTIPLE * average_volume
    ):
        return True

    return False


def _result(signal, color):
    # Apply the same color to the candle body and wick.
    return {
        "signal": signal,
        "color": color,
        "body_color": color,
        "wick_color": color,
    }


def candle_signal(candle, reference_high=None, reference_low=None):
    # A confirmed breakdown takes priority and stays RED.
    if reference_low is not None and breakdown_confirmation(candle, reference_low):
        return _result("SELL", "RED")

    # A confirmed breakout is the entry candle: DARK_BLUE, not yellow.
    if reference_high is not None and breakout_confirmation(candle, reference_high):
        return _result("BUY", "DARK_BLUE")

    # Yellow marks momentum building, before a confirmed entry.
    if is_green(candle) and is_momentum_candle(candle):
        return _result("MOMENTUM", "YELLOW")

    if is_red(candle):
        return _result("SELL", "RED")

    if is_green(candle):
        return _result("HOLD", "GREEN")

    return _result("HOLD", "GREEN")
