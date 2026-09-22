"""Core trade-journal logic: trades, P&L, PDT day-trade counting."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
import csv


@dataclass
class Trade:
    date: str  # YYYY-MM-DD
    symbol: str
    side: str  # long / short
    qty: float = 1.0
    entry: float = 0.0
    exit: float = 0.0
    fees: float = 0.0
    type: str = "equity"  # equity | option
    notes: str = ""
    day_trade: bool = False  # opened and closed same session

    @property
    def multiplier(self) -> float:
        return 100.0 if self.type == "option" else 1.0

    @property
    def pnl(self) -> float:
        gross = (self.exit - self.entry) * self.qty * self.multiplier
        if self.side == "short":
            gross = -gross
        return gross - self.fees

    @property
    def return_pct(self) -> float:
        cost = self.entry * self.qty * self.multiplier
        if cost == 0:
            return 0.0
        return self.pnl / cost * 100


@dataclass
class Journal:
    trades: list = field(default_factory=list)

    def add(self, trade: Trade) -> None:
        self.trades.append(trade)

    @classmethod
    def from_csv(cls, path: str) -> "Journal":
        j = cls()
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                j.add(Trade(
                    date=row["date"],
                    symbol=row["symbol"],
                    side=row.get("side", "long"),
                    qty=float(row.get("qty", 1)),
                    entry=float(row.get("entry", 0)),
                    exit=float(row.get("exit", 0)),
                    fees=float(row.get("fees", 0)),
                    type=row.get("type", "equity"),
                    notes=row.get("notes", ""),
                    day_trade=row.get("day_trade", "").lower() in ("1", "true", "yes"),
                ))
        return j

    def to_csv(self, path: str) -> None:
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "date", "symbol", "side", "qty", "entry", "exit",
                "fees", "type", "notes", "day_trade"])
            w.writeheader()
            for t in self.trades:
                w.writerow({
                    "date": t.date, "symbol": t.symbol, "side": t.side,
                    "qty": t.qty, "entry": t.entry, "exit": t.exit,
                    "fees": t.fees, "type": t.type, "notes": t.notes,
                    "day_trade": int(t.day_trade),
                })

    @property
    def total_pnl(self) -> float:
        return sum(t.pnl for t in self.trades)

    @property
    def win_rate(self) -> float:
        if not self.trades:
            return 0.0
        wins = sum(1 for t in self.trades if t.pnl > 0)
        return wins / len(self.trades) * 100

    def day_trades_used(self, today: str | None = None) -> int:
        """Count day trades in the rolling 5-business-day window.

        Simplified: counts day trades dated within the last 5 calendar days
        including `today`. Good enough for a personal journal; your broker
        is the source of truth.
        """
        today_d = datetime.strptime(today, "%Y-%m-%d").date() if today else date.today()
        count = 0
        for t in self.trades:
            if not t.day_trade:
                continue
            try:
                d = datetime.strptime(t.date, "%Y-%m-%d").date()
            except ValueError:
                continue
            if 0 <= (today_d - d).days <= 4:
                count += 1
        return count

    def pdt_warning(self, today: str | None = None) -> str | None:
        used = self.day_trades_used(today)
        if used >= 3:
            return f"PDT LOCK RISK: {used}/3 day trades used — do not day trade."
        if used == 2:
            return f"Caution: {used}/3 day trades used — one left."
        return None

    def by_symbol(self) -> dict:
        out: dict = {}
        for t in self.trades:
            out.setdefault(t.symbol, {"trades": 0, "pnl": 0.0})
            out[t.symbol]["trades"] += 1
            out[t.symbol]["pnl"] += t.pnl
        return out
