#!/usr/bin/env python3
"""CLI for the smart trade journal."""
import argparse
from trade_journal import Journal, Trade


def cmd_add(args):
    j = Journal.from_csv(args.csv) if args.csv else Journal()
    j.add(Trade(
        date=args.date, symbol=args.symbol.upper(), side=args.side,
        qty=args.qty, entry=args.entry, exit=args.exit or 0.0,
        fees=args.fees, type=args.type, notes=args.notes or "",
        day_trade=args.day_trade,
    ))
    out = args.csv or "trades.csv"
    j.to_csv(out)
    print(f"logged {args.symbol.upper()} -> {out}")


def cmd_summary(args):
    j = Journal.from_csv(args.csv)
    print(f"trades:    {len(j.trades)}")
    print(f"total P&L: ${j.total_pnl:,.2f}")
    print(f"win rate:  {j.win_rate:.1f}%")
    warn = j.pdt_warning()
    if warn:
        print(f"! {warn}")
    print("\nby symbol:")
    for sym, s in sorted(j.by_symbol().items()):
        print(f"  {sym:8} {s['trades']:3} trades  ${s['pnl']:10,.2f}")


def cmd_report(args):
    from html import escape
    j = Journal.from_csv(args.csv)
    rows = "\n".join(
        f"<tr><td>{escape(t.date)}</td><td>{escape(t.symbol)}</td>"
        f"<td>{escape(t.side)}</td><td>{t.qty:g}</td>"
        f"<td>${t.entry:,.2f}</td><td>${t.exit:,.2f}</td>"
        f"<td>${t.pnl:,.2f}</td><td>{escape(t.notes)}</td></tr>"
        for t in j.trades
    )
    warn = j.pdt_warning() or ""
    html = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Trade Journal Report</title>
<style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:6px 10px;font-size:14px}}
.warn{{background:#fff3cd;border:1px solid #ffc107;padding:10px;border-radius:6px}}</style>
</head><body>
<h1>Trade Journal Report</h1>
<p>Total P&L: <b>${j.total_pnl:,.2f}</b> · Win rate: <b>{j.win_rate:.1f}%</b> · Trades: <b>{len(j.trades)}</b></p>
{f'<div class="warn">{escape(warn)}</div>' if warn else ''}
<table><tr><th>Date</th><th>Symbol</th><th>Side</th><th>Qty</th><th>Entry</th><th>Exit</th><th>P&L</th><th>Notes</th></tr>
{rows}</table></body></html>"""
    with open(args.out, "w") as f:
        f.write(html)
    print(f"wrote {args.out}")


def main():
    p = argparse.ArgumentParser(prog="journal")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--date", required=True)
    a.add_argument("--symbol", required=True)
    a.add_argument("--side", default="long", choices=["long", "short"])
    a.add_argument("--qty", type=float, default=1)
    a.add_argument("--entry", type=float, required=True)
    a.add_argument("--exit", type=float, default=0.0)
    a.add_argument("--fees", type=float, default=0.0)
    a.add_argument("--type", default="equity", choices=["equity", "option"])
    a.add_argument("--notes", default="")
    a.add_argument("--day-trade", action="store_true")
    a.add_argument("--csv", default="")
    a.set_defaults(fn=cmd_add)

    s = sub.add_parser("summary")
    s.add_argument("--csv", required=True)
    s.set_defaults(fn=cmd_summary)

    r = sub.add_parser("report")
    r.add_argument("--csv", required=True)
    r.add_argument("--out", default="report.html")
    r.set_defaults(fn=cmd_report)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
