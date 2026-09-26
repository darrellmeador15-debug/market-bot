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

    if trade_decision(entry, 9.90) != "HOLD":
        raise AssertionError("Expected HOLD")

    if trade_decision(entry, 10.80) != "PARTIAL_PROFIT":
        raise AssertionError("Expected PARTIAL_PROFIT")

    if trade_decision(entry, 8.90) != "STOP":
        raise AssertionError("Expected STOP")

    print("All strategy tests passed.")


if __name__ == "__main__":
    run_basic_tests()
