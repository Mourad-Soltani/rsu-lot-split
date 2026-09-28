# Mourad.Soltani — rsu-lot-split CLI
"""Minimal CLI: JSON in, JSON summary out."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from .engine import Grant, Sale, Vest, compute_lots, summarize


def _d(value: str) -> date:
    return date.fromisoformat(value)


def load_payload(path: Path) -> tuple[list[Grant], list[Vest], list[Sale], str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    grants = [
        Grant(
            id=g["id"],
            shares=int(g["shares"]),
            grant_date=_d(g["grant_date"]),
            fmv_at_grant=Decimal(str(g["fmv_at_grant"])),
        )
        for g in data.get("grants", [])
    ]
    vests = [
        Vest(
            grant_id=v["grant_id"],
            shares=int(v["shares"]),
            vest_date=_d(v["vest_date"]),
            fmv_at_vest=Decimal(str(v["fmv_at_vest"])),
        )
        for v in data.get("vests", [])
    ]
    sales = [
        Sale(
            id=s["id"],
            shares=int(s["shares"]),
            sale_date=_d(s["sale_date"]),
            proceeds_per_share=Decimal(str(s["proceeds_per_share"])),
            lot_id=s.get("lot_id"),
        )
        for s in data.get("sales", [])
    ]
    method = data.get("method", "fifo")
    return grants, vests, sales, method


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rsu-lot-split", description="RSU tax-lot splitter — Mourad.Soltani")
    parser.add_argument("input", type=Path, help="JSON file with grants, vests, sales")
    args = parser.parse_args(argv)
    grants, vests, sales, method = load_payload(args.input)
    result = compute_lots(grants, vests, sales, method=method)  # type: ignore[arg-type]
    summary = summarize(result)
    payload = {
        "author": "Mourad.Soltani",
        "summary": {
            **summary,
            "st_gain": str(summary["st_gain"]),
            "lt_gain": str(summary["lt_gain"]),
        },
        "matches": [
            {
                "sale_id": m.sale_id,
                "lot_id": m.lot_id,
                "grant_id": m.grant_id,
                "shares": m.shares,
                "vest_date": m.vest_date.isoformat(),
                "sale_date": m.sale_date.isoformat(),
                "cost_basis": str(m.cost_basis),
                "proceeds": str(m.proceeds),
                "gain": str(m.gain),
                "holding": m.holding,
            }
            for m in result.matches
        ],
        "open_lots": [
            {
                "lot_id": lot.lot_id,
                "grant_id": lot.grant_id,
                "vest_date": lot.vest_date.isoformat(),
                "remaining": lot.remaining,
                "cost_per_share": str(lot.cost_per_share),
            }
            for lot in result.open_lots
        ],
    }
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if not result.warnings else 2


if __name__ == "__main__":
    raise SystemExit(main())
