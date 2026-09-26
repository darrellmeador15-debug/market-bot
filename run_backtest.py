from backtest import backtest


def entry_signal(row):
    return row.get("entry_signal", False)


def exit_signal(row):
    return row.get("exit_signal", False)


def run_backtest(data):
    results = backtest(data, entry_signal, exit_signal)

    if results.empty:
        print("No trades found.")
        return results

    print(f"Trades: {len(results)}")
    print(f"Total P&L: {results['pnl_percent'].sum():.2f}%")
    print(
        f"Win rate: "
        f"{(results['pnl_percent'] > 0).mean() * 100:.2f}%"
    )

    return results


if __name__ == "__main__":
    print("Backtest engine ready.")
    print("Waiting for historical intraday data.")
