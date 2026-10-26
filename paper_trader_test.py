from paper_trader import PaperTrader
from learning_system import load_memory
import tempfile
from pathlib import Path


def run_tests():
    bot = PaperTrader(starting_cash=10_000, stop_loss_percent=5,
                      profit_target_percent=15, max_position_fraction=0.20)

    result = bot.buy("ABCD", 10, shares=100)
    assert result["status"] == "filled_simulated"
    assert bot.cash == 9_000
    assert bot.position.symbol == "ABCD"

    duplicate = bot.buy("WXYZ", 5, shares=10)
    assert duplicate["status"] == "rejected"
    assert duplicate["reason"] == "already_holding_position"

    hold = bot.update_price(10.50)
    assert hold["status"] == "holding"

    stop = bot.update_price(9.50)
    assert stop["status"] == "filled_simulated"
    assert stop["reason"] == "STOP_LOSS"
    assert stop["pnl"] == -50
    assert bot.position is None
    assert bot.cash == 9_950

    # The profit target is configurable, so test 10%, 15%, and 20% independently.
    for target in (10, 15, 20):
        sim = PaperTrader(starting_cash=1_000, profit_target_percent=target,
                          max_position_fraction=1.0)
        sim.buy("TEST", 10, shares=10)
        outcome = sim.update_price(10 * (1 + target / 100))
        assert outcome["status"] == "filled_simulated"
        assert outcome["reason"] == "PROFIT_TARGET"
        assert outcome["pnl"] == 10 * target / 100 * 10
        assert sim.position is None

    no_short = PaperTrader(starting_cash=1_000, max_position_fraction=1.0)
    assert no_short.sell(10)["status"] == "rejected"
    assert no_short.position is None

    too_large = PaperTrader(starting_cash=1_000, max_position_fraction=0.20)
    assert too_large.buy("BIG", 10, shares=21)["status"] == "rejected"
    assert too_large.cash == 1_000

    try:
        bot.buy("BAD", 0, shares=1)
        raise AssertionError("zero price should be rejected")
    except ValueError:
        pass

    summary = PaperTrader(starting_cash=1000, max_position_fraction=1.0)
    summary.buy("WIN", 10, shares=10)
    summary.sell(11, "TEST_WIN")
    stats = summary.summary()
    assert stats["closed_trades"] == 1
    assert stats["wins"] == 1
    assert stats["win_rate_percent"] == 100
    assert stats["realized_pnl"] == 10
    assert stats["cash"] == 1010

    with tempfile.TemporaryDirectory() as folder:
        memory_file = Path(folder) / "trade_memory.jsonl"
        persistent = PaperTrader(starting_cash=1000, max_position_fraction=1.0,
                                 memory_path=memory_file)
        persistent.buy("MEM", 10, shares=10)
        persistent.sell(11, "MEMORY_TEST")
        saved = load_memory(memory_file)
        assert [row["event"] for row in saved] == ["BUY", "SELL"]
        assert saved[-1]["pnl"] == 10

    print("All paper-trader tests passed.")


if __name__ == "__main__":
    run_tests()
