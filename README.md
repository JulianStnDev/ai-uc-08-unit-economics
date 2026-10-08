🇩🇪 [Deutsche Version](README_DE.md)

# UC8: Unit Economics, Pricing & Build-vs-Buy

> Status 2026-10-08: number inventory ([docs/INVENTUR.md](docs/INVENTUR.md)) and cost model ([evals/modell.md](evals/modell.md), worked example: [docs/RECHENWEG.md](docs/RECHENWEG.md)), all in German. Pricing and build-vs-buy to follow.

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

| Scenario | Approval / handover | With agent per ticket | Monthly saving | Tipping point handover rate |
|---|---|---|---|---|
| optimistic | 10 % / 15 % | 0.47 EUR | 30,641 EUR (86.7 %) | none |
| medium | 15 % / 30 % | 1.22 EUR | 23,125 EUR (65.4 %) | none (95 % > 85 % possible) |
| pessimistic | 20 % / 50 % | 2.59 EUR | 9,421 EUR (26.6 %) | 71 % |

![Saving per ticket over handover rate](docs/kipppunkt.svg)

Tokens cost 0.03 EUR per ticket, as much as 4 seconds of staff time. Handovers decide the saving: minutes per handover relative to minutes without the agent. Follow-up costs of wrong autonomous answers are not modelled ([docs/decisions.md](docs/decisions.md)).

## Cost & Latency
- Cost per 1000 requests: 1,223.49 EUR per 1,000 tickets with the agent (medium scenario, staff included), of which tokens 32.09 USD
- p95 latency: not applicable to a decision memo. Agent latency see UC7 (p95 39.7 s)
- Quality metric: tipping point of the handover rate 71 % in the pessimistic scenario, measured in the gold set 22 %
- UC8 cost so far: 0 USD (no API calls)

## Learnings
To follow.

## What I Would Do Differently
To follow.
