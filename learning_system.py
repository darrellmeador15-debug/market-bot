"""Persistent trade memory and guarded, human-approved strategy review.

This module never places broker orders or changes live strategy settings.
Run it in the same persistent environment as the bot; GitHub Actions runners
are temporary and are not an always-on trading host.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean


DEFAULT_MEMORY_PATH = Path("data/trade_memory.jsonl")


def record_event(event: dict, path: str | Path = DEFAULT_MEMORY_PATH) -> dict:
    """Append one JSON event to persistent local trade memory."""
    if not isinstance(event, dict) or not event:
        raise ValueError("event must be a non-empty dictionary")
    row = dict(event)
    row.setdefault("recorded_at", datetime.now(timezone.utc).isoformat())
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")
    return row


def load_memory(path: str | Path = DEFAULT_MEMORY_PATH) -> list[dict]:
    """Load recorded events; ignore no malformed rows silently."""
    source = Path(path)
    if not source.exists():
        return []
    rows = []
    with source.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in trade memory line {line_number}") from exc
    return rows


def summarize_trades(trades: list[dict]) -> dict:
    """Summarize closed trades containing a numeric pnl field."""
    closed = [t for t in trades if isinstance(t.get("pnl"), (int, float))]
    wins = [float(t["pnl"]) for t in closed if t["pnl"] > 0]
    losses = [float(t["pnl"]) for t in closed if t["pnl"] < 0]
    pnls = [float(t["pnl"]) for t in closed]
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    equity = peak = 0.0
    max_drawdown = 0.0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        max_drawdown = max(max_drawdown, peak - equity)
    return {
        "closed_trades": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_percent": round(100 * len(wins) / len(closed), 2) if closed else 0.0,
        "average_win": round(mean(wins), 4) if wins else 0.0,
        "average_loss": round(mean(losses), 4) if losses else 0.0,
        "realized_pnl": round(sum(pnls), 4),
        "profit_factor": round(gross_profit / gross_loss, 4) if gross_loss else (None if gross_profit == 0 else "undefined_no_losses"),
        "max_drawdown_from_trade_sequence": round(max_drawdown, 4),
    }


def analyze_setups(trades: list[dict], group_field: str = "setup") -> dict:
    """Compare recorded setup/regime groups without automatically changing rules."""
    groups = defaultdict(list)
    for trade in trades:
        if isinstance(trade.get("pnl"), (int, float)):
            groups[str(trade.get(group_field, "unknown"))].append(trade)
    return {
        key: summarize_trades(group)
        for key, group in sorted(groups.items())
    }


def propose_review(trades: list[dict], minimum_trades: int = 30) -> dict:
    """Return a review recommendation; this is not an automatic strategy update.

    The trade log should include market_regime/setup tags. Evidence is descriptive,
    not causal. Promotion requires a separate out-of-sample backtest and human approval.
    """
    stats = summarize_trades(trades)
    enough = stats["closed_trades"] >= minimum_trades
    groups = analyze_setups(trades)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "REVIEW_READY" if enough else "COLLECT_MORE_DATA",
        "closed_trades": stats["closed_trades"],
        "minimum_trades": minimum_trades,
        "overall": stats,
        "setup_comparison": groups,
        "next_steps": [
            "Tag each trade with setup, catalyst, and market_regime when known.",
            "Review performance separately for trending, choppy, and declining markets.",
            "Test any proposed rule change on historical data not used to create it.",
            "Require human approval before promoting a strategy change.",
            "Never enable live orders solely because a review passes.",
        ],
        "automatic_strategy_change": False,
        "live_orders_enabled": False,
    }


def rolling_review(memory_path: str | Path = DEFAULT_MEMORY_PATH) -> dict:
    """Build an analysis report from saved trade events."""
    events = load_memory(memory_path)
    closed_trades = [e for e in events if e.get("event") in {"TRADE_CLOSED", "SELL"} and isinstance(e.get("pnl"), (int, float))]
    return propose_review(closed_trades)
