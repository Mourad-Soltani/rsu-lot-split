# Mourad.Soltani — health tests
from datetime import date
from decimal import Decimal

from rsu_lot_split.engine import Grant, Sale, Vest, compute_lots, summarize


def test_fifo_short_and_long_term():
    grants = [Grant("G1", 100, date(2023, 1, 15), Decimal("10"))]
    vests = [
        Vest("G1", 50, date(2024, 1, 15), Decimal("20.00")),
        Vest("G1", 50, date(2025, 1, 15), Decimal("30.00")),
    ]
    sales = [Sale("S1", 60, date(2025, 3, 1), Decimal("40.00"))]
    result = compute_lots(grants, vests, sales, method="fifo")
    assert sum(m.shares for m in result.matches) == 60
    assert result.matches[0].holding == "LT"
    assert result.matches[1].holding == "ST"
    assert result.matches[0].shares == 50
    assert result.matches[1].shares == 10
    assert result.open_lots[0].remaining == 40
    summary = summarize(result)
    assert summary["open_shares"] == 40
    assert summary["st_gain"] == Decimal("100.00")  # 10 * (40-30)
    assert summary["lt_gain"] == Decimal("1000.00")  # 50 * (40-20)


def test_specific_id_picks_named_lot():
    grants = [Grant("G1", 20, date(2024, 1, 1), Decimal("5"))]
    vests = [
        Vest("G1", 10, date(2024, 6, 1), Decimal("8")),
        Vest("G1", 10, date(2024, 12, 1), Decimal("12")),
    ]
    # First vest becomes G1-V1, second G1-V2
    sales = [Sale("S1", 5, date(2025, 1, 1), Decimal("15"), lot_id="G1-V2")]
    result = compute_lots(grants, vests, sales, method="specific")
    assert len(result.matches) == 1
    assert result.matches[0].lot_id == "G1-V2"
    assert result.matches[0].cost_basis == Decimal("60.00")


def test_oversell_warns():
    grants = [Grant("G1", 10, date(2024, 1, 1), Decimal("1"))]
    vests = [Vest("G1", 10, date(2024, 6, 1), Decimal("2"))]
    sales = [Sale("S1", 12, date(2024, 7, 1), Decimal("3"))]
    result = compute_lots(grants, vests, sales)
    assert result.warnings
    assert sum(m.shares for m in result.matches) == 10
