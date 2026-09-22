from trade_journal import Trade, Journal


def test_option_pnl():
    t = Trade(date="2026-09-22", symbol="SOFI", side="long",
              qty=2, entry=0.50, exit=0.11, type="option")
    assert round(t.pnl, 2) == round((0.11 - 0.50) * 2 * 100, 2)


def test_pdt_count():
    j = Journal()
    j.add(Trade(date="2026-09-22", symbol="SOFI", side="long", day_trade=True))
    j.add(Trade(date="2026-09-21", symbol="AAPL", side="long", day_trade=True))
    j.add(Trade(date="2026-09-10", symbol="MSFT", side="long", day_trade=True))
    assert j.day_trades_used(today="2026-09-22") == 2
    assert "one left" in (j.pdt_warning(today="2026-09-22") or "")


def test_win_rate():
    j = Journal()
    j.add(Trade(date="2026-09-22", symbol="A", side="long", qty=1, entry=10, exit=12))
    j.add(Trade(date="2026-09-22", symbol="B", side="long", qty=1, entry=10, exit=9))
    assert j.win_rate == 50.0
