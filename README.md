# Market Bot

Long-only stock scanner and strategy-testing project. The current code includes signal rules, historical-data helpers, strategy tests, and a local simulated paper-trading engine.

## Safety and current status

- **Local simulator only:** `paper_trader.py` simulates buys and sells using prices supplied to it. It does not send orders to Schwab, Thinkorswim, or Robinhood.
- **No short selling:** the simulator only opens long positions.
- **No live orders:** live trading is disabled by default. No broker order execution has been implemented.
- **No guarantee of returns:** passing tests verifies software behavior, not profitability or a 90% win rate.
- **Stop orders can slip:** the simulator's stop trigger is not a guarantee that a real order would fill at the stop price.

## Local paper simulator

The simulator keeps a cash balance, permits one open long position at a time, enforces a configurable maximum position fraction, and records simulated entries and exits. Its default exit settings are a 5% stop and 15% profit target. Change `profit_target_percent` to test 10%, 15%, or 20% exit plans separately.

Run locally:

```bash
python paper_trader_test.py
```

The tests cover simulated buying and selling, stop/target exits, cash accounting, duplicate-entry prevention, position limits, and long-only behavior. GitHub Actions runs these tests on pushes.

## Data and broker connections still needed

- A verified market-data source and approved credentials are needed before the bot can scan current live prices. The Schwab Trader API offers market-data features when the relevant API access is approved.
- This repository does not yet implement Schwab OAuth, a streaming feed, a full stock-universe scanner, news ingestion, or a broker execution adapter.
- Schwab API paper simulation is not the same as Thinkorswim paperMoney. Use this local simulator for automated recorded practice and use Thinkorswim paperMoney separately for manual chart/order practice.
- A Robinhood version should be a separate broker adapter and configuration, with its own authorization and safeguards. It should first use the same local simulation approach; no Robinhood stock-order connection is implemented here.

## Strategy goals

- Focus on stocks priced $0.50–$15, with early-momentum setups, volume, catalyst/news data, and price action.
- Exclude China/Hong Kong listings when reliable country data is available; unknown country data must not silently pass the exclusion filter.
- Test the user's preferred 6:00 a.m.–12:00 p.m. and 3:00–6:00 p.m. Eastern windows, with special attention to 6:00–9:00 a.m.
- Evaluate 7-, 15-, and 30-day results with trade count, win rate, average win/loss, realized P&L, drawdown, and realistic slippage/fees before considering live execution.
