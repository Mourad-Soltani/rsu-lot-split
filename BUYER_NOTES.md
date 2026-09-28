# Buyer notes — rsu-lot-split

Author: Mourad.Soltani

## Product

Single-purpose RSU lot matcher. Input grants/vests/sales. Output matched lots, remaining shares, ST vs LT gain.

## Who pays

- FAANG / late-stage employees with multi-year vest schedules
- Independent wealth advisors who still reconcile brokerage CSV by hand
- Indie founders who took early RSUs and now sell in blocks

## Price sketch

- $29 one-time desktop/CLI
- $9/mo hosted upload + PDF lot report
- $99/yr advisor seat (multi-client folders)

## Differentiation

Existing generic lot software is brokerage-bound or full tax suites. This is a 30-minute tool for one workflow.

## Risks

- Tax rules vary by country; product must stay labeled "not advice"
- Brokers already export 1099-B lots; buyers must feel faster/clearer than that CSV
- GitHub uniqueness was checked for "RSU tax lot tracker vesting" at build time (0 repos)

## Next 2 weeks

1. CSV import from E*TRADE / Fidelity / Carta exports
2. Wash-sale flag (US only, optional)
3. One-page PDF statement
