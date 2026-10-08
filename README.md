🇩🇪 [Deutsche Version](README_DE.md)

# UC8: Unit Economics, Pricing & Build-vs-Buy

> A decision memo, not product code. Every number comes from measured runs (UC4, UC6, UC7) and an assumptions table with sources ([data/annahmen.csv](data/annahmen.csv)). Cost: 0 USD, no API calls.

## Problem
FocusFlow has a working support agent as a prototype (UC7). Three questions are open: What does a ticket cost with the agent compared with a ticket a human handles alone? How much could you charge for it if you sold the agent? And should FocusFlow run it itself or buy one?

## Three Steps

**1. Cost: Tokens are 2 % of the cost per ticket – handoffs drive the business case.**
With the agent a ticket costs 1.60 EUR instead of 3.54 EUR (human only, 8 min). Tokens are 0.03 EUR of that. 73 % is handoffs to humans. Whether the agent pays off depends on the handoff rate, not on the model price. In the gold set it is 22 %. The agent only becomes more expensive than a human alone in the pessimistic scenario, and even there only above 66 % handoffs.

![Saving per ticket over handoff rate](docs/kipppunkt.svg)

**2. Price: 450 EUR per month + 0.75 EUR per resolved ticket.**
"Resolved" means: no handoff and not reopened within 7 days. At 10,000 tickets per month that gives an 85.8 % margin. The medium customer keeps 73.9 % of the saving. The price is below Fin (0.89 EUR per outcome). Per-seat billing is rejected: if the customer cuts 30 % of headcount, the vendor loses 30 % of revenue.

![Price corridor per customer type](docs/korridor.svg)

**3. Build vs. buy: Build pays off above ~5,000 tickets/month – driven by one unsourced assumption.**
Running it yourself beats our product from 5,085 tickets per month and Fin from 3,456. Past build cost is sunk and not counted. The tipping point depends on the ongoing maintenance effort, an assumption without a source: at 21 h per month it is 1,875 tickets, at 100 h it is 12,440.

![Run it yourself vs. buy](docs/build_buy_differenz.svg)

## Decision
**FocusFlow runs the agent itself (A).** Only future costs count. At 10,000 tickets per month A costs 18,846 EUR, our product 20,996 EUR, Fin 23,578 EUR. The data stays under FocusFlow's control: it goes to the model provider and its own host (Frankfurt), not additionally to a SaaS vendor.

**Decide again if** the full cost of A is above C's offer three months in a row, or the maintenance effort stays above 45 h per month. Measured every month for this: person-days per maintenance task, daily rate, operating cost and tokens ([docs/decisions.md](docs/decisions.md)).

## Assumptions That Carry the Result

| Assumption | Range | Effect | Source |
|---|---|---|---|
| Minutes per ticket without the agent | 5 / 8 / 14.4 min | saving 1.15 to 3.61 EUR per ticket | industry figures, partly secondary sources |
| Staff cost per minute | 0.37 / 0.44 / 0.75 EUR | saving 1.61 to 3.30 EUR per ticket | Entgeltatlas, Destatis (to verify in the original) |
| Handoff rate | 15 / 30 / 50 % | saving 2.44 to 1.26 EUR per ticket | gold set 22 %, but billing tickets only |
| Maintenance effort for A | 21 / 45 / 100 h per month | build-vs-buy tipping point 1,875 to 12,440 tickets | none, own assumption |

![Tornado: sensitivity of the saving per ticket](docs/tornado.svg)

## Cost & Latency
- Cost per 1000 requests: 1,601.85 EUR per 1,000 tickets with the agent (medium scenario, staff included), of which tokens 32.09 USD
- p95 latency: 39.7 s per agent run (UC7, Cloud Run)
- Quality metric: 4 of 29 autonomous gold set runs with a wrong core message (14 %), counted as rework

## What I Would Do Differently
- **Measure the big levers first.** The three strongest assumptions (minutes without the agent, staff cost, maintenance effort) are not measured. 20 approvals and handoffs timed with a stopwatch and time tracking in UC4 to UC7 would have been worth more than any extra decimal on tokens.
- **Get the real ticket mix earlier.** The gold set contains only billing and subscription tickets, the handoff rate in real traffic is unknown.
- **Leave sunk costs out from the start.** The first version counted the past build time (312 EUR/month).
- **Define terms up front.** Markup (profit / cost) and margin (profit / revenue) were mixed at first.

Details (German): [Inventory](docs/INVENTUR.md) · [Cost model](evals/modell.md) · [Pricing](evals/pricing.md) · [Build vs. buy](evals/build_buy.md) · Worked examples [cost](docs/RECHENWEG.md), [price](docs/RECHENWEG_PRICING.md), [build vs. buy](docs/RECHENWEG_BUILD_BUY.md) · [Rework](docs/NACHARBEIT.md) · [Decisions](docs/decisions.md)
