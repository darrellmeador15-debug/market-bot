# Market Bot

Long-only stock scanner and strategy-testing project. The current code includes signal rules, historical-data helpers, strategy tests, and a local simulated paper-trading engine.

## Scanner dashboard prototype

A first single-screen dashboard is available in `dashboard.py`. It includes:
- Momentum/gap candidate table and configurable ticker list.
- Top 5 two-minute up/down movers for the selected symbols.
- News headlines returned by Yahoo Finance for those symbols.
- Two intraday candlestick/volume charts.
- A clearly labelled volatility/volume-based pre-halt watch.

Run locally after installing requirements:

```bash
python -m pip install -r requirements.txt
streamlit run dashboard.py
```

**Current limitations:** this first dashboard scans only the symbols entered in its input field; it is not yet a complete market-wide scanner. Yahoo Finance data can be delayed, incomplete, or unavailable for some symbols. The pre-halt label is a heuristic, not an official exchange halt alert. An official halt/resumption feed, reliable real-time data provider, full stock universe, and news catalyst provider still need to be connected. No orders are sent from the dashboard.

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

## Latency measurement and free-data limits

- `latency_monitor.py` measures the local time spent processing an event and producing a decision, with median, p95, p99, and maximum results.
- This is **not** exchange-to-screen latency. True end-to-end delay requires a trustworthy provider event timestamp and a local receive timestamp; source coverage and timestamp semantics must be verified.
- The requested 4–6 millisecond target is a goal to measure, not a guarantee. Free feeds may be delayed, incomplete, rate-limited, or limited to one exchange.
- Before paper-trading signals are trusted, log source name, source timestamp, local receive time, alert time, missing/stale status, and symbol coverage. Never label a source real-time just because local processing is fast.
- Free/open-source software can be excellent, but it cannot manufacture missing exchange data, official halt notices, Level 2/order flow, or a complete catalyst feed.

Run the local latency utility tests with:

```bash
python latency_monitor_test.py
```

## Data and broker connections still needed

- A verified market-data source and approved credentials are needed before the bot can scan current live prices. The Schwab Trader API offers market-data features when the relevant API access is approved.
- This repository does not yet implement Schwab OAuth, a streaming feed, a full stock-universe scanner, official halt ingestion, or a broker execution adapter.
- Schwab API paper simulation is not the same as Thinkorswim paperMoney. Use this local simulator for automated recorded practice and use Thinkorswim paperMoney separately for manual chart/order practice. Direct API access to paperMoney is not assumed or promised.
- A Robinhood version should be a separate broker adapter and configuration, with its own authorization and safeguards. No Robinhood stock-order connection is implemented here.

## Strategy goals

- Focus on stocks priced $0.50–$15, with early-momentum setups, volume, catalyst/news data, and price action.
- Treat the 8-million threshold as traded volume, not float; float remains a separate field/filter.
- Exclude China/Hong Kong listings when reliable country data is available; unknown country data must not silently pass the exclusion filter.
- Test the user's preferred 6:00 a.m.–12:00 p.m. and 3:00–6:00 p.m. Eastern windows, with special attention to 6:00–9:00 a.m.
- Evaluate 7-, 15-, and 30-day results with trade count, win rate, average win/loss, realized P&L, drawdown, and realistic slippage/fees before considering live execution.

## Four-stage development and continuous learning plan

The bot's intended lifecycle is:

1. **Build and observe (initial target: 3 weeks):** connect an approved market-data source, scan the configured stock universe, simulate long-only entries/exits, and record every signal. Three weeks is a checkpoint, not a promise of readiness.
2. **Validate (typically several additional weeks):** test on unseen historical periods, include realistic fees/slippage, assess drawdown and losing streaks, and publish 7-, 15-, and 30-day scorecards. Do not rely on win rate alone.
3. **Thinkorswim paperMoney (after a separate integration/feasibility check):** test signals and order-management workflow in the platform's simulated environment. Keep testing for at least 4–8 weeks as a starting guideline, and longer if trade count or market conditions are insufficient.
4. **Real money only after explicit approval:** require stable out-of-sample results, adequate trade count, risk-limit checks, a kill switch, and verified broker order behavior. Start with small exposure. Passing software tests alone never authorizes live trading.

### Trade memory, strategy analysis, and controlled improvement

- `learning_system.py` adds persistent JSON Lines trade-event memory, summary metrics, setup-group comparisons, and a review report.
- `learning_system_test.py` checks storage, metrics, setup comparisons, insufficient-data status, and safety defaults.
- Record setup/catalyst and market-regime tags when available, so results can be compared across trending, choppy, and declining markets.
- The review system **does not automatically rewrite or promote trading rules**. Proposed changes must be tested against data not used to create them and approved by a human before promotion.
- GitHub Actions is for testing, not a continuous live-market process; persistent runtime/storage and a verified data feed remain to be configured.
- No system can promise 100% completion, constant improvement, or profits. Continuous evaluation is the goal; safe, measured changes matter more than changing rules every day.

Run the learning-system tests with:

```bash
python learning_system_test.py
```
