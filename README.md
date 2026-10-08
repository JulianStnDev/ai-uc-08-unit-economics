🇩🇪 [Deutsche Version](README_DE.md)

# UC8: Unit Economics, Pricing & Build-vs-Buy

> Status 2026-10-08: number inventory ([docs/INVENTUR.md](docs/INVENTUR.md)) and cost model ([evals/modell.md](evals/modell.md), worked example: [docs/RECHENWEG.md](docs/RECHENWEG.md)), all in German. Pricing: [evals/pricing.md](evals/pricing.md), worked example [docs/RECHENWEG_PRICING.md](docs/RECHENWEG_PRICING.md). Build-vs-buy to follow.

## Problem
The support agent from UC4/UC7 runs as a web demo on Cloud Run. The product question behind it is still open: **What does a support ticket cost with the agent, compared with a ticket handled entirely by a human?** And from that: how could it be priced, and does building it pay off compared with buying a product?

This repo is a decision memo, not product code. It builds on the measured data from UC4, UC6 and UC7.

## PM Decision
Open. The first step was a number inventory: which numbers already exist, with which source, and which are missing for the calculation?

## Architecture Sketch
```
UC4 gold set (45 runs) ─┐
UC6 gold set (45 runs) ─┼─▶ scripts/inventur.py ──▶ data/inventur.csv ──▶ docs/INVENTUR.md
UC7 Neon log ───────────┤      (read-only,           (value, unit, model,
Cloud Monitoring ───────┘       no API cost)          source, commit, date)
```

## Evaluation Results
Number inventory, details in [docs/INVENTUR.md](docs/INVENTUR.md):

| Metric | Value | Source |
|---|---|---|
| Agent cost per ticket, median / p95 | 0.0264 / 0.0422 USD | 45 gold set runs, deployed version (UC6) |
| Final answer (Haiku) per ticket with recommendation, median | 0.0047 USD | 5 live runs |
| Judge (Sonnet 5) per verdict, median | 0.0190 USD | 5 live verdicts, 20 % sample |
| Gold set runs without any human | 29 of 45 (64 %) | UC6 gold set |
| Real customer tickets in production | 0 | Neon: all 13 runs are test runs |

Cost model (10,000 tickets per month, human only 8 min × 0.4420 EUR/min = 3.54 EUR per ticket):

| Scenario | Approval / handover (minutes factor 1.0 / 1.1 / 1.3, rework 5 / 14 / 20 %) | With agent per ticket | Monthly saving | Tipping point handover rate |
|---|---|---|---|---|
| optimistic | 10 % / 15 % | 0.74 EUR | 27,989 EUR (79.2 %) | none |
| medium | 15 % / 30 % | 1.60 EUR | 19,342 EUR (54.7 %) | none (87 % > 85 % possible) |
| pessimistic | 20 % / 50 % | 2.89 EUR | 6,415 EUR (18.1 %) | 66 % |

![Saving per ticket over handover rate](docs/kipppunkt.svg)

Minutes per handover = minutes without the agent × 1.0 / 1.1 / 1.3. Rework: share of autonomous tickets that a human still has to rework, justified in [docs/NACHARBEIT.md](docs/NACHARBEIT.md) (deployed agent in the gold set: 4 of 29 autonomous runs with a wrong core message = 14 %, 3 of them systematic in T04). Computing the deadline inside the tool would save about 1,546 EUR per month at 10,000 tickets (open option, [docs/decisions.md](docs/decisions.md)).

Tokens cost 0.03 EUR per ticket, as much as 4 seconds of staff time. The saving moves most with minutes without the agent, staff cost and the handover rate:

![Tornado: sensitivity of the saving per ticket](docs/tornado.svg)

Pricing from the vendor's view (10,000 tickets per customer and month). Floor = our full cost + 20 %, ceiling = the customer keeps 50 % of the saving:

| Customer type | per seat (month) | per ticket | per resolved ticket | Corridor per month |
|---|---|---|---|---|
| low-cost (5 min) | 140 … 942 EUR | 0.09 … 0.59 EUR | 0.14 … 0.95 EUR | 876 … 5,890 EUR |
| medium (8 min) | 88 … 982 EUR | 0.09 … 0.98 EUR | 0.14 … 1.58 EUR | 876 … 9,821 EUR |
| expensive (14.4 min) | 49 … 1,012 EUR | 0.09 … 1.82 EUR | 0.14 … 2.92 EUR | 876 … 18,209 EUR |

![Price corridor per customer type](docs/korridor.svg)

Intercom Fin (0.99 USD per outcome, checked on intercom.com) sits at 52 % of our per-resolution corridor for the medium customer. Decided: **450 EUR per month + 0.75 EUR per resolved ticket** (no handover, not reopened within 7 days). For the medium customer that is an 85.8 % margin, and the customer keeps 73.9 % of the saving. Loss only below a 3.7 % resolution rate ([docs/decisions.md](docs/decisions.md)). With per-seat billing, a 30 % headcount cut in year two costs the vendor 30 % of revenue although ticket volume stays the same.

## Cost & Latency
- Cost per 1000 requests: 1,601.85 EUR per 1,000 tickets with the agent (medium scenario, staff included), of which tokens 32.09 USD
- p95 latency: not applicable to a decision memo. Agent latency see UC7 (p95 39.7 s)
- Quality metric: tipping point of the handover rate 66 % in the pessimistic scenario, measured in the gold set 22 %
- UC8 cost so far: 0 USD (no API calls)

## Learnings
To follow.

## What I Would Do Differently
To follow.
