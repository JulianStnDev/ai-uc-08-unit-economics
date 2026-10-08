🇩🇪 [Deutsche Version](README_DE.md)

# UC8: Unit Economics, Pricing & Build-vs-Buy

> Status 2026-10-08: number inventory done ([docs/INVENTUR.md](docs/INVENTUR.md), German), cost model still open.

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

The largest gaps: minutes per approval and per handover, minutes per ticket without the agent, and the real ticket mix.

## Cost & Latency
- Cost per 1000 requests: open (follows from the cost model)
- p95 latency: not applicable to a decision memo. Agent latency see UC7 (p95 39.7 s)
- Quality metric: open
- UC8 cost so far: 0 USD (no API calls)

## Learnings
To follow.

## What I Would Do Differently
To follow.
