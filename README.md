# Smart Trade Journal

A lightweight trading journal for day/swing traders. Log trades, track P&L,
count PDT day-trades, and generate a clean HTML report — no database needed.

## Why

Most retail journals are either spreadsheets or bloated SaaS. This is a
single-file-friendly Python toolkit you can run locally and own your data.

## Quick start

```bash
pip install -r requirements.txt

# add a trade
python cli.py add --symbol SOFI --side long --qty 2 --entry 0.50 --exit 0.11 \
  --type option --notes "broke stop, cut fast"

# show summary
python cli.py summary --csv example_trades.csv

# build HTML report
python cli.py report --csv my_trades.csv --out report.html
```

## PDT tracking

US pattern-day-trader rule: max 3 day trades in any rolling 5 business days
under $25k. `trade_journal.py` counts day trades (open+close same session)
and warns when you're at 2.

## Data format

CSV columns: `date,symbol,side,qty,entry,exit,fees,type,notes`
