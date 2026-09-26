from rules import momentum_tier, trade_decision


def run_basic_tests():
    tests = [
        ("10% momentum", momentum_tier(10), 10),
        ("20% momentum", momentum_tier(20), 20),
        ("30% momentum", momentum_tier(30), 30),
        ("Below momentum", momentum_tier(5), 0),
    ]

    for name, actual, expected in tests:
        if actual != expected:
            raise AssertionError(
                f"{name}: expected {expected}, got {actual}"
            )

    entry = 10.00

    result = trade_decision(entry, 9.90)
    assert result["signal"] == "HOLD"
    assert result["color"] == "GREEN"

    result = trade_decision(entry, 10.80)
    assert result["signal"] == "BUY"
    assert result["color"] == "YELLOW"

    result = trade_decision(entry, 8.90)
    assert result["signal"] == "SELL"
    assert result["color"] == "RED"

    print("All strategy tests passed.")
    print("SELL = RED")
    print("HOLD = GREEN")
    print("BUY = YELLOW")
    print("SHORT SELL = ORANGE")


if __name__ == "__main__":
    run_basic_tests()
