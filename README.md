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
market assumptions. Market data as of 28 Oct 2026 (the peso, PSEi and KOSPI closes; US
equities, the VIX and Brent to 27 Oct; WTI, the Nikkei and the 10-year Treasury to the
session before, where the next prints are not yet confirmed). Weights in the universe's order: Money Market / Nasdaq Equity Income /
Asia Equity / Global Technology / Global Dividend / Global Health Care / Global Infra
Equity / Global Equity Opportunity / Global Consumer Trends / Asian Multi-Asset Income /
Global Allocation.

| | A · 10-year view | B · 3/5/10-year view |
|---|---|---|
| Allocation (eleven funds, in the order above) | 5 / 30 / 0 / 15 / 0 / 0 / 20 / 0 / 0 / 30 / 0 | **5 / 35 / 0 / 10 / 0 / 0 / 25 / 0 / 0 / 25 / 0** |
| 10y net CAGR after all fees | **7.07%** | 7.05% |
| Expected max drawdown (10y) | −24.6% | **−24.3%** |
| Return per unit of drawdown | 0.287 | **0.290** |

Both columns are on the 3/5/10-year view. Every portfolio is built from four analyses -
the macro drivers, the market trend, the regional ranking and the volatility curve - each
read at **3, 5 and 10 years** and weighted by the share of the ten-year holding it governs
(3Y years 1-3, 30%; 5Y years 4-5, 20%; 10Y years 6-10, 50%). **One rule chooses both**, over the eleven funds within the review's
limits (at most 5 funds, 35% in any one, at least 5% peso cash; 322,725 mixes): the best
10-year net CAGR after fees inside the drawdown budget, then the lowest drawdown within
0.05pp of it. The budget is **−25%, the owner's from 27 Oct 2026** (v75), in place of the
derived −26.97% (the original 20 / 30 / 25 / 25 baseline's drawdown less 2.83pp). The
engine re-chooses each at every update:
- **A, the 10-year view**: the rule on the four analyses read at 10 years alone (7.26% /
  −24.5% there): 5% money market, 30% Nasdaq Equity Income, 15% Global Technology, 20%
  Global Infra Equity, 30% Asian Multi-Asset Income.
- **B, the 3/5/10-year view**: the rule on all three horizons: 5% money market, 35%
  Nasdaq Equity Income, 10% Global Technology, 25% Global Infra Equity, 25% Asian
  Multi-Asset Income. Level with A at the model's precision for 0.3pp less drawdown (49
  mixes inside the tie).

**The Budget tab** reads, on 1-5, whether the next three and five years justify moving the
25% budget - from the macro drivers, the volatility curve and the market trend at each
view - with bands for a step to 24%, 26% or 27%, guards that must also be clear, and what
each step does to A and B. On 28 Oct it reads 2.89: hold at 25%. It is advisory; the
budget never moves by itself.

Portfolio C - B with Nasdaq Equity Income held at 50%, the pin exempt from the 35% cap,
added on 2026-09-25 - was removed at the owner's request on 2026-10-28 (v76). At removal it
held 5 / 50 / 10 Global Health Care / 25 Global Infra Equity / 10 Asian Multi-Asset Income at
7.09% / −24.3%. Removing it changed neither A nor B: they come out of a different search,
and nothing else read its result. Portfolio D - C on four funds only (Money Market, Nasdaq
Equity Income, Asia Equity and Global Technology), added on 2026-10-23 - was removed on
2026-10-27 (v74), for the same reason changing nothing else.

What moved them (v71): each analysis is now researched year by year - years 1-3, then
years 4-5 - from the Fed's projected rates (4.1% at the end of 2026 and 2027, 3.9% in 2028,
3.6% in 2029), BSP's inflation path, five-year inflation pricing, the IMF's growth path,
the cyclically adjusted P/E of 40.7 and the oil curve for 2027 and 2029. Averaged over the
five years the readings land within 0.15 of v70's. B moves 5pp from cash into Global Infra
Equity and 5pp from Global Technology into Global Health Care (7.23% against 7.19%, for
0.3pp more drawdown). The rates drag drives it: Monetary's ten-year average rises to 4.80
from 4.75, and with it held at 4.75, B would keep 10% in cash and 10% in Global
Technology. A and C kept their weights. (Those were the picks under the derived −26.97% budget;
v75 moved all three to the owner's 25%; C was retired in v76.) US Equity Opportunity is
held out until its trust fee is confirmed (at the listed 1.20% it would take 20% of A and
20% of B, at the 25% budget); Global Bond Income would move the picks most (at its listed
fee, 30-35% of A). The page states every figure here from the
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
