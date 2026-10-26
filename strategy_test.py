from config import LONG_ONLY, SHORT_ENABLED, STOP_LOSS_PERCENT, PARTIAL_PROFIT_PERCENT, PROFIT_TARGET_PERCENT
from rules import momentum_tier, trade_decision
from strategy import evaluate_trade


def run_basic_tests():
    assert LONG_ONLY is True
    assert SHORT_ENABLED is False
    assert STOP_LOSS_PERCENT == 5.0
    assert PARTIAL_PROFIT_PERCENT == 10.0
    assert PROFIT_TARGET_PERCENT == 15.0

    tests = [
        ("10% momentum", momentum_tier(10), 10),
        ("20% momentum", momentum_tier(20), 20),
        ("30% momentum", momentum_tier(30), 30),
        ("Below momentum", momentum_tier(5), 0),
    ]
    for name, actual, expected in tests:
        if actual != expected:
            raise AssertionError(f"{name}: expected {expected}, got {actual}")

    entry = 10.00
    result = trade_decision(entry, 9.50)
    assert result["signal"] == "SELL"
    assert result["reason"] == "STOP_LOSS"
    assert result["color"] == "RED"

    result = trade_decision(entry, 10.50)
    assert result["signal"] == "HOLD"

    result = trade_decision(entry, 11.00)
    assert result["signal"] == "SELL"
    assert result["reason"] == "PROFIT_TAKING"

    result = trade_decision(entry, 11.50)
    assert result["signal"] == "SELL"
    assert result["reason"] == "PROFIT_TARGET"

    assert evaluate_trade(entry, 9.50) == "STOP"
    assert evaluate_trade(entry, 11.00) == "PROFIT_ZONE"
    assert evaluate_trade(entry, 11.50) == "TAKE_PROFIT"

    print("All long-only strategy tests passed.")
    print("No short-selling entries are enabled.")
    print("Stop loss: 5%; profit-taking starts at 10%; target: 15%.")


if __name__ == "__main__":
    run_basic_tests()
