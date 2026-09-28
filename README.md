# rsu-lot-split

RSU vesting tax-lot splitter for cost basis and short/long-term holding.

Built by **Mourad.Soltani**.

## Why this exists

Equity-heavy employees and indie operators still track RSU lots in spreadsheets. This tool turns grants, vest events, and sales into FIFO or specific-ID matched lots with cost basis and ST/LT flags.

GitHub search at build time found no existing repository named or described as an RSU tax-lot tracker.

## Install

```bash
pip install -e ".[dev]"
```

## Usage

```bash
rsu-lot-split examples/sample.json
```

Input JSON keys: `grants`, `vests`, `sales`, optional `method` (`fifo` or `specific`).

For specific-ID matching, set `lot_id` on a sale to a generated lot id (`{grant}-V{n}`).

## Tests

```bash
pytest
```

## Scope (v0.1)

- FIFO and specific-ID matching
- Cost basis from vest FMV
- ST/LT split using more-than-one-year rule
- CLI JSON report
- Not tax advice. Confirm with a CPA for your jurisdiction.

## License

MIT — Mourad.Soltani
