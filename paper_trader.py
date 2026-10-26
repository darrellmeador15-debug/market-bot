"""Local long-only paper simulator. This module never sends broker orders."""
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path

from learning_system import DEFAULT_MEMORY_PATH, record_event


@dataclass
class Trade:
    symbol: str
    shares: int
    entry_price: float
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    pnl: Optional[float] = None


class PaperTrader:
    """Small, deterministic simulator for testing signals against supplied prices.

    The stop is a trigger, not a guaranteed fill price. This simple simulator fills
    at the supplied price when a stop is triggered; real gaps/slippage can be worse.
    """

    def __init__(self, starting_cash=10_000.0, stop_loss_percent=5.0,
                 profit_target_percent=15.0, max_position_fraction=0.20,\n                 memory_path=DEFAULT_MEMORY_PATH):
        if starting_cash <= 0:
            raise ValueError("starting_cash must be greater than zero")
        if not 0 < stop_loss_percent < 100:
            raise ValueError("stop_loss_percent must be between 0 and 100")
        if profit_target_percent <= 0:
            raise ValueError("profit_target_percent must be greater than zero")
        if not 0 < max_position_fraction <= 1:
            raise ValueError("max_position_fraction must be in (0, 1]")
        self.starting_cash = float(starting_cash)
        self.cash = float(starting_cash)
        self.stop_loss_percent = float(stop_loss_percent)
        self.profit_target_percent = float(profit_target_percent)
        self.max_position_fraction = float(max_position_fraction)
        self.position = None
        self.closed_trades = []
        self.ledger = []

    def buy(self, symbol, price, shares=None):
        if not isinstance(symbol, str) or not symbol.strip():
            raise ValueError("symbol is required")
        if price is None or price <= 0:
            raise ValueError("price must be greater than zero")
        if self.position is not None:
            return {"status": "rejected", "reason": "already_holding_position"}
        max_spend = self.cash * self.max_position_fraction
        affordable = int(min(max_spend, self.cash) // float(price))
        qty = affordable if shares is None else shares
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError("shares must be a positive whole number")
        cost = qty * float(price)
        if cost > self.cash or cost > max_spend:
            return {"status": "rejected", "reason": "position_limit_or_insufficient_cash"}
        self.cash -= cost
        self.position = Trade(symbol.strip().upper(), qty, float(price))
        event = {"event": "BUY", "symbol": self.position.symbol, "shares": qty,
                 "price": float(price), "cash_after": round(self.cash, 2)}
        self.ledger.append(event)
        return {"status": "filled_simulated", **event}

    def update_price(self, price):
        if price is None or price <= 0:
            raise ValueError("price must be greater than zero")
        if self.position is None:
            return {"status": "no_position"}
        entry = self.position.entry_price
        stop_price = entry * (1 - self.stop_loss_percent / 100)
        target_price = entry * (1 + self.profit_target_percent / 100)
        # Stop is checked first for conservative handling if a supplied price is
        # somehow beyond both thresholds between observations.
        if price <= stop_price:
            return self.sell(float(price), "STOP_LOSS")
        if price >= target_price:
            return self.sell(float(price), "PROFIT_TARGET")
        return {"status": "holding", "symbol": self.position.symbol,
                "shares": self.position.shares, "entry_price": entry,
                "current_price": float(price),
                "unrealized_pnl": round((float(price) - entry) * self.position.shares, 2),
                "stop_price": round(stop_price, 4),
                "target_price": round(target_price, 4)}

    def sell(self, price, reason="MANUAL_EXIT"):
        if price is None or price <= 0:
            raise ValueError("price must be greater than zero")
        if self.position is None:
            return {"status": "rejected", "reason": "no_open_position"}
        trade = self.position
        trade.exit_price = float(price)
        trade.exit_reason = str(reason)
        trade.pnl = round((trade.exit_price - trade.entry_price) * trade.shares, 2)
        self.cash += trade.exit_price * trade.shares
        self.closed_trades.append(asdict(trade))
        event = {"event": "SELL", "symbol": trade.symbol, "shares": trade.shares,
                 "price": trade.exit_price, "reason": trade.exit_reason,
                 "pnl": trade.pnl, "cash_after": round(self.cash, 2)}
        self.ledger.append(event)
        self.position = None
        return {"status": "filled_simulated", **event}

    def summary(self):
        wins = [t for t in self.closed_trades if t["pnl"] > 0]
        losses = [t for t in self.closed_trades if t["pnl"] < 0]
        total_pnl = round(sum(t["pnl"] for t in self.closed_trades), 2)
        return {
            "starting_cash": round(self.starting_cash, 2),
            "cash": round(self.cash, 2),
            "open_position": asdict(self.position) if self.position else None,
            "closed_trades": len(self.closed_trades),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate_percent": round(100 * len(wins) / len(self.closed_trades), 2)
                if self.closed_trades else 0.0,
            "realized_pnl": total_pnl,
            "ledger": list(self.ledger),
        }
