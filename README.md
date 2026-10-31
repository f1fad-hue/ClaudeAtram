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
market assumptions. Market data as of 30 Oct 2026 (Friday's closes in Manila, Seoul, Tokyo
and New York, Brent's December expiry, WTI, the VIX and the 2-, 10- and 30-year's official
closes; FedWatch at 29 Oct), reviewed 31 Oct. Weights in the universe's order: Money Market / Nasdaq Equity Income /
Asia Equity / Global Technology / Global Dividend / Global Health Care / Global Infra
Equity / Global Equity Opportunity / Global Consumer Trends / Asian Multi-Asset Income /
Global Allocation.

| | A · 10-year view | B · 3/5/10-year view | C · Nasdaq Income 50% |
|---|---|---|---|
| Allocation (eleven funds, in the order above) | 5 / 35 / 0 / 10 / 0 / 0 / 30 / 0 / 0 / 20 / 0 | **10 / 35 / 0 / 5 / 0 / 20 / 30 / 0 / 0 / 0 / 0** | 5 / 50 / 0 / 0 / 0 / 15 / 25 / 0 / 0 / 5 / 0 |
| 10y net CAGR after all fees | **7.30%** | 7.10% | 7.14% |
| Expected max drawdown (10y) | −24.9% | −24.9% | −24.9% |
| Return per unit of drawdown | **0.293** | 0.285 | 0.287 |

Each column is on its own horizon (owner, 28 Oct 2026, v80): A on the 10-year forecasts, B and
C on the 3/5/10-year. On one basis, the 3/5/10-year view, A returns 7.11% at −25.0% against B's
7.10% at −24.9%; on the 10-year view B returns 7.26% at −24.8%. Every portfolio is built from four analyses -
the macro drivers, the market trend, the regional ranking and the volatility curve - each
read at **3, 5 and 10 years** and weighted by the share of the ten-year holding it governs
(3Y years 1-3, 30%; 5Y years 4-5, 20%; 10Y years 6-10, 50%). **One rule chooses all three**, over the eleven funds within the review's
limits (at most 5 funds, 35% in any one, at least 5% peso cash; 322,725 mixes): **maximum
growth** - the highest 10-year net CAGR after all fund fees whose drawdown is inside the
budget, as computed and as shown; a shallower drawdown decides only between mixes that print
the same CAGR (since v77; until v76, the lowest drawdown within 0.05pp of the best). The
budget is **the Budget tab's band**, from the owner's **−25% base** (27 Oct 2026, v75): the
band leaves the base only when two month-end reviews in a row read another band and, for a
raise, both risk guards are clear. It is −25% today, in place of the derived −26.97% (the
original 20 / 30 / 25 / 25 baseline's drawdown less 2.83pp). The engine re-chooses each at
every update:
- **A, the 10-year view**: the rule on the four analyses read at 10 years alone (7.30% /
  −24.9% there): 5% money market, 35% Nasdaq Equity Income, 10% Global Technology, 30%
  Global Infra Equity, 20% Asian Multi-Asset Income. On the 3/5/10-year view it prints at
  the budget (−25.0%) and sits just past it before rounding.
- **B, the 3/5/10-year view**: the rule on all three horizons: 10% money market, 35%
  Nasdaq Equity Income, 5% Global Technology, 20% Global Health Care, 30% Global Infra
  Equity - the highest 3/5/10-year CAGR inside the budget, 0.01pp below A there for 0.1pp
  less drawdown. Maximum growth added 0.04pp a year to A and 0.05pp to B against the v76
  rule, for 0.4pp and 0.6pp more drawdown, both inside the budget.
- **C, Nasdaq Equity Income at 50%** (owner, 29 Oct 2026, v82: "Make portfolio C with 50%
  atram nasdaq equity income allocation based on 3, 5, 10yrs ... Use budget drawdown band for
  portfolio C"): B's rule, inputs and band budget with Nasdaq Equity Income held at 50% - the
  one fund exempt from the 35% cap - and the rest chosen over the other ten funds (8,289
  mixes, 3,551 inside the budget): 5% money market, 15% Global Health Care, 25% Global Infra
  Equity, 5% Asian Multi-Asset Income. 7.14% / −24.9% on the 3/5/10-year view (7.32% /
  −24.8% on the 10-year). It returns 0.04pp a year more than B at the same printed drawdown
  only because the pin is outside the cap: the drawdown model does not price one manager
  holding half the money, which is what the cap is for.

**The Budget tab** reads, on 1-5, whether the next three and five years justify moving the
25% budget - from the macro drivers, the volatility curve and the market trend at each
view - with bands for a step to 24%, 26% or 27%, guards that must also be clear, and what
each step does to A, B and C. On 30 Oct it reads 2.89: hold at 25%. Since v77 the band sets
the budget for A and B (owner, 28 Oct), and since v82 for C, through the same guards.

Portfolio C was first added on 2026-09-25, removed on 2026-10-28 (v76) and restored on
2026-10-29 (v82); its pinned search is separate from A's and B's, so neither change moved
them. Portfolio D - C on four funds only (Money Market, Nasdaq
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
fee, 25-35% of A). **The Asian Multi-Asset Income trust fee is disputed** (1.50% on ATRAM's
page, carried; 1.20% in its October 2025 KIID): at 1.20%, A would hold 35% of it and B 30%,
against 20% and none. The page states every figure here from the
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
