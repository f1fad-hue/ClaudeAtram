# ATRAM Peso Macro Desk

A mobile-first macro and allocation dashboard for a peso investor in ATRAM unit
investment trust funds - eleven funds from the owner's 22-fund ATRAM list - built for a
ten-year horizon.

**Live:** https://claude.ai/code/artifact/307440fd-2952-4b4c-b55c-51725163be31

## The original four funds

| Code | Fund | Own stated target |
|---|---|---|
| `ATRPHMM` | ATRAM Peso Money Market Fund | Beat PH bank deposits, duration ≤ 1 year |
| `ATRQIAP` | ATRAM Nasdaq Equity Income Feeder Fund | JPM Nasdaq Equity Premium Income Active UCITS ETF · 75% Nasdaq-100 |
| `ATRASEQ` | ATRAM Asia Equity Opportunity Feeder Fund | JPMorgan Asia Equity Dividend Fund |
| `ATRGTEC` | ATRAM Global Technology Feeder Fund | Fidelity Funds – Global Technology · MSCI ACWI IT |

## Seven more from the 22-fund list

Every fund on the owner's list whose fees are confirmed - its trust fee on ATRAM's own
page or on two current listings that agree, and its target fund named with a published
charge (the standard set for US Equity Opportunity on 21 Oct 2026):

| Code | Fund | Own stated target |
|---|---|---|
| `ATRGLDV` | ATRAM Global Dividend Feeder Fund | Fidelity Funds – Global Dividend Fund |
| `ATRGHCP` | ATRAM Global Health Care Feeder Fund | Fidelity Funds – Global Healthcare Fund · MSCI ACWI Health Care |
| model `M_GINF` | ATRAM Global Infra Equity Feeder Fund | HSBC GIF – Global Infrastructure Equity |
| `14UF05P` | ATRAM Global Equity Opportunity Feeder Fund | Allianz Thematica |
| `20UF19P` | ATRAM Global Consumer Trends Feeder Fund | Invesco Global Consumer Trends Fund |
| `ATRAMIP` | ATRAM Asian Multi-Asset Income Feeder Fund | Schroder Asian Asset Income Fund |
| `14UF06` | ATRAM Global Allocation Feeder Fund | BlackRock Global Funds – Global Allocation Fund |

The other eleven are held out until their fees are confirmed, each with what is missing
(the page lists them): US Equity Opportunity, Global Bond Income, Global AI, Global
Multi-Asset Income, Global Capital Accumulation FoF, Global Equity High Income, Global
Natural Resources, Global Gold Equity, Global Financials, US Multi-Asset Income and Peso
Liquid. The ATRAM Long Term and Medium Term Peso Bond funds were removed from the list
and from every allocation on 21 Oct 2026, at the owner's instruction.

Each fund is measured against its own target, not a house benchmark.

## Result

Ten-year horizon, net of every fee layer, on J.P. Morgan's 2027 long-term capital
market assumptions. Market data as of 26 Oct 2026 (Philippine and Asian closes; US
series to 23 Oct). Weights in the universe's order: Money Market / Nasdaq Equity Income /
Asia Equity / Global Technology / Global Dividend / Global Health Care / Global Infra
Equity / Global Equity Opportunity / Global Consumer Trends / Asian Multi-Asset Income /
Global Allocation.

| | A · 10-year view | B · 1/3/5/10-year view | C · Nasdaq Income at 50% | D · Four funds, Nasdaq Income at 50% |
|---|---|---|---|---|
| Allocation (eleven funds, in the order above) | 5 / 30 / 0 / 20 / 0 / 0 / 20 / 0 / 0 / 25 / 0 | **10 / 35 / 0 / 10 / 0 / 15 / 30 / 0 / 0 / 0 / 0** | 5 / 50 / 0 / 5 / 0 / 0 / 35 / 0 / 0 / 5 / 0 | 25 / 50 / 5 / 20 / 0 / 0 / 0 / 0 / 0 / 0 / 0 |
| 10y net CAGR after all fees | 7.22% | 7.20% | **7.26%** | 7.07% |
| Expected max drawdown (10y) | −26.6% | **−26.1%** | −26.7% | −26.8% |
| Return per unit of drawdown | 0.271 | **0.276** | 0.272 | 0.264 |

All four rows are on the 1/3/5/10-year view. Every portfolio is built from four analyses -
the macro drivers, the market trend, the regional ranking and the volatility curve - each
read at **1, 3, 5 and 10 years** and weighted by the share of the ten-year holding it governs
(10 / 20 / 20 / 50%). **One rule chooses all four**, over the eleven funds within the
review's limits (at most 5 funds, 35% in any one, at least 5% peso cash; 322,725 mixes):
the best 10-year net CAGR after fees inside the drawdown budget, then the lowest drawdown
within 0.05pp of it. The engine re-chooses each at every update:
- **A, the 10-year view**: the rule on the four analyses read at 10 years alone (7.43% /
  −26.4% there): 5% money market, 30% Nasdaq Equity Income, 20% Global Technology, 20%
  Global Infra Equity, 25% Asian Multi-Asset Income.
- **B, the 1/3/5/10-year view**: the rule on all four horizons. Level with A at the model's
  precision (0.02pp a year less) for 0.5pp less drawdown (31 mixes inside the tie).
- **C** is B with Nasdaq Equity Income held at 50% (the pin is exempt from the 35% cap):
  0.06pp a year above B for 0.6pp more drawdown.
- **D** is C on four funds only - Nasdaq Equity Income at 50% with the Peso Money Market,
  Asia Equity and Global Technology (owner, 2026-10-23): 25 / 50 / 5 / 20, 0.19pp a year
  below C for 0.1pp more drawdown.

What moved them (v68): the drivers' rates and energy tilts now read each driver's path
across the four horizons rather than its 1-year reading held for ten years, so the hiking
cycle and the Gulf drag a ten-year return a fifth to a quarter as much as before; every forecast
rose about 0.3pp, Global Technology's most. The trend channel now scores the past year as
momentum and the past 3 and 5 years as reversal; after three strong years the two largely
cancel. The budget, −26.97%, is the original 20 / 30 / 25 / 25 baseline's drawdown less
2.83pp. US Equity Opportunity is held out until its trust fee is confirmed (at the listed
1.20% it would take 20% of A, 20% of B and 10% of C); Global Bond Income would move the
picks most (at its listed fee, 25-35% of A). The page states every figure here from the
engine; this table is a snapshot of it, and the review audit fails if it drifts.

## Layout

```
model/engine.py      the whole model - pure stdlib Python, no dependencies
model/data.json      generated payload, embedded into the page
dashboard.html       the published artifact
monitoring/          manual review runbook, claim register, changelog
```

## Running it

```
python3 model/engine.py           # audit report; exits 0 only if all checks pass
python3 model/engine.py --json    # regenerate model/data.json
python3 model/heldout_sens.py     # what US Equity Opportunity and Global Bond Income would do if admitted
```

Every figure on the page is computed by the engine. Change an input in the
`VERIFIED INPUTS` block and everything downstream recomputes.

## Keeping it current

There is no automation — the review is manual. `monitoring/README.md` is the
runbook, `monitoring/CLAIMS.md` the checklist of every figure and its source, and
`monitoring/CHANGELOG.md` the history including every bug found and fixed.

## Disclaimer

Portfolio analysis on eleven ATRAM funds over a 10-year horizon, not personal
financial advice.
Forecasts are modelled expectations, not guarantees. UITF investments are not
deposits and are not insured by the PDIC.
