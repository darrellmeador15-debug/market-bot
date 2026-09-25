import pandas as pd


def backtest(data, entry_signal, exit_signal):
    trades = []
    position = None

    for _, row in data.iterrows():
        if position is None and entry_signal(row):
            position = {
                "entry_price": row["close"],
                "entry_time": row["timestamp"],
            }

        elif position is not None and exit_signal(row):
            exit_price = row["close"]

            pnl_percent = (
                (exit_price - position["entry_price"])
                / position["entry_price"]
            ) * 100

            trades.append({
                "entry_time": position["entry_time"],
                "entry_price": position["entry_price"],
                "exit_time": row["timestamp"],
                "exit_price": exit_price,
                "pnl_percent": pnl_percent,
            })

            position = None

    return pd.DataFrame(trades)
