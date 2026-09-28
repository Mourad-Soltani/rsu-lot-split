# Mourad.Soltani — rsu-lot-split engine
"""FIFO / specific-id lot matching for RSU vests and sales."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Literal

Method = Literal["fifo", "specific"]
CENTS = Decimal("0.01")


def _money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(CENTS, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Grant:
    id: str
    shares: int
    grant_date: date
    fmv_at_grant: Decimal


@dataclass(frozen=True)
class Vest:
    grant_id: str
    shares: int
    vest_date: date
    fmv_at_vest: Decimal


@dataclass(frozen=True)
class Sale:
    id: str
    shares: int
    sale_date: date
    proceeds_per_share: Decimal
    lot_id: str | None = None  # used by specific-id method


@dataclass
class OpenLot:
    lot_id: str
    grant_id: str
    vest_date: date
    remaining: int
    cost_per_share: Decimal


@dataclass
class MatchedLot:
    sale_id: str
    lot_id: str
    grant_id: str
    shares: int
    vest_date: date
    sale_date: date
    cost_basis: Decimal
    proceeds: Decimal
    gain: Decimal
    holding: Literal["ST", "LT"]


@dataclass
class Result:
    matches: list[MatchedLot] = field(default_factory=list)
    open_lots: list[OpenLot] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _holding(vest_date: date, sale_date: date) -> Literal["ST", "LT"]:
    # US equity: long-term after more than one year.
    return "LT" if sale_date > vest_date.replace(year=vest_date.year + 1) else "ST"


def compute_lots(
    grants: Iterable[Grant],
    vests: Iterable[Vest],
    sales: Iterable[Sale],
    method: Method = "fifo",
) -> Result:
    grant_map = {g.id: g for g in grants}
    result = Result()

    lots: list[OpenLot] = []
    vest_index = 0
    for vest in sorted(vests, key=lambda v: (v.vest_date, v.grant_id)):
        if vest.grant_id not in grant_map:
            result.warnings.append(f"Unknown grant_id on vest: {vest.grant_id}")
            continue
        if vest.shares <= 0:
            result.warnings.append(f"Non-positive vest shares for {vest.grant_id}")
            continue
        vest_index += 1
        lots.append(
            OpenLot(
                lot_id=f"{vest.grant_id}-V{vest_index}",
                grant_id=vest.grant_id,
                vest_date=vest.vest_date,
                remaining=vest.shares,
                cost_per_share=_money(vest.fmv_at_vest),
            )
        )

    remaining_sales = sorted(sales, key=lambda s: (s.sale_date, s.id))
    for sale in remaining_sales:
        need = sale.shares
        if need <= 0:
            result.warnings.append(f"Non-positive sale shares: {sale.id}")
            continue
        pps = _money(sale.proceeds_per_share)

        def pick_indices() -> list[int]:
            if method == "specific" and sale.lot_id:
                return [i for i, lot in enumerate(lots) if lot.lot_id == sale.lot_id and lot.remaining > 0]
            return [i for i, lot in enumerate(lots) if lot.remaining > 0]

        while need > 0:
            idxs = pick_indices()
            if not idxs:
                result.warnings.append(f"Oversold {need} shares on sale {sale.id}")
                break
            i = idxs[0]
            lot = lots[i]
            take = min(need, lot.remaining)
            cost = _money(lot.cost_per_share * take)
            proceeds = _money(pps * take)
            result.matches.append(
                MatchedLot(
                    sale_id=sale.id,
                    lot_id=lot.lot_id,
                    grant_id=lot.grant_id,
                    shares=take,
                    vest_date=lot.vest_date,
                    sale_date=sale.sale_date,
                    cost_basis=cost,
                    proceeds=proceeds,
                    gain=_money(proceeds - cost),
                    holding=_holding(lot.vest_date, sale.sale_date),
                )
            )
            lot.remaining -= take
            need -= take

    result.open_lots = [lot for lot in lots if lot.remaining > 0]
    return result


def summarize(result: Result) -> dict:
    st = sum((m.gain for m in result.matches if m.holding == "ST"), Decimal("0.00"))
    lt = sum((m.gain for m in result.matches if m.holding == "LT"), Decimal("0.00"))
    open_shares = sum(lot.remaining for lot in result.open_lots)
    return {
        "matched_sales": len({m.sale_id for m in result.matches}),
        "matched_shares": sum(m.shares for m in result.matches),
        "open_shares": open_shares,
        "st_gain": _money(st),
        "lt_gain": _money(lt),
        "warnings": list(result.warnings),
    }
