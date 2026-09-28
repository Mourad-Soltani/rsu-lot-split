# One-to-one outreach templates

Do not send bulk or purchased lists. Use only after a real conversation or a personal reply.

Author: Mourad.Soltani

## Template A — equity-comp Slack / Discord peer

Subject: tiny RSU lot tool if you still reconcile sales by hand

Hi {name},

I built a small FIFO / specific-ID matcher for RSU vests vs sales. You drop grants, vest FMVs, and sale blocks in JSON and get cost basis plus ST/LT.

Not tax advice — just the lot math I kept redoing in a sheet.

If you want it: {repo_url}

— Mourad.Soltani

## Template B — advisor who mentioned Carta / 1099-B cleanup

Subject: RSU lot split for {client_count} vest schedules

{name},

You said the painful part is matching partial sales across vest tranches.

rsu-lot-split does that matching and prints remaining lots. CLI today, CSV import next.

Happy to walk through one anonymized client file on a 15-minute call.

Repo: {repo_url}

— Mourad.Soltani

## Template C — reply to someone who posted “how do I pick lots for RSU sale”

{name} — if you still need this: FIFO vs specific-ID matcher here {repo_url}. Input is vest date + FMV and sale date + proceeds. It flags ST/LT. I am the author (Mourad.Soltani). Glad to adjust the JSON shape to your broker export.
