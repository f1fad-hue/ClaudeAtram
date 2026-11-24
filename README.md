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
market assumptions. Market data as of 24 Nov 2026 (reviewed 24 Nov, 08:30 UTC): Seoul and Tokyo at their 24 Nov closes (the KOSPI
5,006.03, +6.32%, back above 5,000; the Nikkei 58,644.63, +3.91%, its first session since the holiday); New York, the VIX,
oil and the peso at 23 Nov, when Nvidia's board reinstated Jensen Huang (the S&P 500 7,237.17, +4.73%, out of correction;
the Nasdaq 24,089.56, +6.51%, its best day since April 2025; the VIX 26.62, -25.83%; Brent $89.37, -3.46%, its lowest close
since August; WTI's January contract $80.17; the peso 63.845); Manila at 23 Nov (the PSEi 5,353.07, +0.87%; 24 Nov's
close not yet reported) and the 23 Nov T-bill auction (91-day 6.584%); Treasuries at 20 Nov (the official 23 Nov curve
not yet published). Not personal financial advice.

| | A · 10-year view | B · 1/3/5/10-year view | C · dividend income | D · Nasdaq Income-led |
|---|---|---|---|---|
| Allocation (eleven funds, in the order above) | 5 / 35 / 0 / 10 / 0 / 0 / 25 / 0 / 0 / 25 / 0 | **5 / 35 / 0 / 10 / 0 / 0 / 25 / 0 / 0 / 25 / 0** | 30 / 65 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 5 / 0 | 0 / 50 / 0 / 0 / 0 / 15 / 15 / 0 / 0 / 20 / 0 |
| 10y net total-return CAGR after all fees | **7.24%** | 7.13% | 6.61% | 7.19% |
| Expected max drawdown (10y) | −24.9% | −24.9% | **−20.9%** | −24.9% |
| Return per unit of drawdown | 0.291 | 0.286 | **0.316** | 0.289 |
| Payout yield, trailing 12 months (est.) | 5.49% | 5.49% | 7.71% | 6.90% |
| Payout a year on ₱1,000,000 (est.; net of ATRAM's trust fee) | ₱54,900 (₱45,900) | ₱54,900 (₱45,900) | ₱77,100 (₱66,600) | ₱69,000 (₱58,500) |
| Payout yield, next 12 months (forecast at the latest rates) | 5.84% | 5.84% | 8.36% | 7.40% |
| Payout, next vs last 12 months | +0.35pp (₱58,400) | +0.35pp (₱58,400) | +0.65pp (₱83,600) | +0.50pp (₱74,000) |
| Payout yield, 2025, for reference (est.) | 5.18% | 5.18% | 7.13% | 6.45% |

Each column is on its own horizon (owner, 28 Oct 2026, v80): A on the 10-year forecasts, B, C and D
on the 1/3/5/10-year. **Portfolio C (v125, owner, 23 Nov 2026)** is the dividend-income portfolio -
two to five of the four ATRAM funds that pay income to their unitholders (Nasdaq Equity Income monthly;
Asia Equity Opportunity, Global Dividend and Asian Multi-Asset Income quarterly) and Peso Money Market as
an allowed cash buffer, each at least 5%, no main fund and no single-fund cap - chosen by B's rule on B's
view - and, from v131 (owner, 23 Nov 2026), at most 110 less the owner's age in stocks (68% at 42, 67% from 30 Dec,
recomputed on each birthday): 65% Nasdaq Equity Income, 30% Peso Money Market and 5% Asian Multi-Asset Income, 67.5% in
stocks, at 6.61% / −20.9%, 0.52pp a year below B (65% / 35% Nasdaq / Asian Multi-Asset at 7.07% / −25.0% before the cap).
The cap, not the drawdown budget, now binds: C's mix is the same at every budget step from 21% to 30%. Payouts count inside each fund's net total-return CAGR, not on top.
**The payout rows (v126, owner, 23 Nov 2026)** are estimates: no ATRAM fund's own payout rate was found, so each
paying fund is read at its target fund's trailing-12-month distribution yield (Nasdaq Equity Income ~11.4% monthly; Asian
Multi-Asset Income ~6.0%, Asia Equity Opportunity ~2.7% and Global Dividend ~2.3% quarterly), and the bracket assumes ATRAM
pays it net of its trust fee. A payout is part of the return, not added to it.
**The year-before rows (v129)** set each portfolio's payout over the last 12 months against 2025's, read the same way
from each target: Nasdaq Equity Income ~10.5% in 2025 (Parqet 10.45%; justETF's 9.63% disputed) against ~11.4% now;
Asian Multi-Asset Income's 2025 rate was not found and is ASSUMED at its target's set 6% a year, which every portfolio
holds (A and B 25%, D 20%, C 5%). v127's 1-year return rows were retired: the owner asked for last year's payout, not last year's return.
**The next-12-month rows (v130)** are a forecast at each payer's latest payout rate, annualised: Nasdaq Equity Income ~12.4%
(J.P. Morgan's 12.37% for September; DivvyDiary 12.88% after November's payout), Asian Multi-Asset Income its target's set
6% a year. They hold only if the rates do; a covered-call fund's income moves with volatility.
From 17 Nov (v111) to v124 C was the owner's three funds, Nasdaq Equity Income-led with Peso Money Market and
Global Technology (70 / 25 / 5 at 6.94% / −24.8% on 23 Nov); an earlier C, Nasdaq Equity Income pinned at
50%, was retired on 12 Nov 2026 (v101). **A and B are the same mix since v107**: the rule picks on B's view
what it picks on A's, 7.13% / −24.9% on the 1/3/5/10-year view and 7.24% / −24.9% on the 10-year
(v117: 25% Global Infra Equity and 25% Asian Multi-Asset Income, from 30% and 20%, as the re-quoted VIX curve's
higher long-run volatility, 19.96 from 19.42, deepens every fund's expected drawdown and the budget binds tighter).
Every portfolio is built from four analyses (owner, 16 Nov 2026, v107) - the regional ranking,
macro sentiment (the drivers' rates and energy tilts), the market trend and market valuation.
**A** reads them at 10 years alone, where macro, trend and valuation are neutral by construction
and valuation is already priced in the long-run assumptions. **B, C and D** read them at **1, 3, 5
and 10 years**, weighted by the years each covers: year 1 10%, years 2-3 20%, years 4-5 20%,
years 6-10 50%. Year 1 is researched on its own for every analysis - the regional rankings'
from 16 Nov 2026 (v108): US 2.78, Europe 2.00, Asia 3.22, Philippines 2.67 on 1-5, each 0.22 under
its three-year score (5.0, 3.25, 6.0 and 4.75 on the 1-10 scale they were researched on until v119) - and years 2-3 are what each three-year reading (the average of years 1-3)
leaves once year 1 is taken out, so no year counts twice and the blends, forecasts and picks are
unchanged by the split. The Portfolios tab's table "The four analyses, year by year" shows every
reading A, B and D take.
Valuation tilts years 1-5 only: its 1-5 blend, 3.132, sits 0.132 above neutral, which at the
regional rate (0.675pp a point) adds 0.09pp to every equity fund, 0.05pp to Global Allocation and
0.04pp to Asian Multi-Asset Income (0.05pp until v119, when the drivers moved to 1-5 and the
rounding of Valuation's 3-year reading tipped it under the edge).
**The macro drivers are scored on 1-5, 3 neutral, from v119** (owner, 21 Nov 2026: "Macroeconomics
drivers update it 1-5 guauge. No more 1-10."): every score, path point, six-month and year-1
reading, the guard's floor (1.44) and the tilts' calibration (2.33 and 1.67) is on 1-5, carried
across from 1-10 by the fixed map 1 → 1, 5.5 → 3, 10 → 5 at 2dp. **The regional rankings followed in
v120** (owner, 21 Nov 2026: "Regional driver update them to 1-5 gauge"): US 3.00 / 3.33 / 3.44 at 3, 5
and 10 years, Europe 2.22 / 2.56 / 2.56, Asia 3.44 / 3.67 / 3.67, Philippines 2.89 / 3.11 / 3.00, the
same blends (3.29 / 2.46 / 3.60 / 2.99) and no forecast or pick moved. Nothing on the page is on 1-10. The volatility curve no longer tilts any return (it moved them -0.02 to +0.01pp);
it sets each fund's volatility and so its expected drawdown, and the VIX guards a raise of the
budget. The Volatility tab was removed; its drawdown model is on the Portfolios tab.
**One rule chooses all three**, over the eleven funds within the review's
limits (at most 5 funds, 35% in any one, at least 5% peso cash; 322,725 mixes): **maximum
growth** - the highest 10-year net total-return CAGR after all fund fees whose drawdown is inside the
budget, as computed and as shown; a shallower drawdown decides only between mixes that print
the same CAGR (since v77; until v76, the lowest drawdown within 0.05pp of the best). The
budget is **the Budget tab's band**, from the owner's **−25% base** (27 Oct 2026, v75), for A,
B and D alike: the band leaves the base only when two month-end reviews in a row read another
band and, for a raise, both risk guards are clear. It is −25% today, in place of the derived
−26.97% (the original 20 / 30 / 25 / 25 baseline's drawdown less 2.83pp). The engine re-chooses
each at every update:
- **A, the 10-year view**: the rule on the four analyses read at 10 years alone (7.24% /
  −24.9% there): 5% money market, 35% Nasdaq Equity Income, 10% Global Technology, 25%
  Global Infra Equity, 25% Asian Multi-Asset Income (30% and 20% until v116).
- **B, the 1/3/5/10-year view**: the rule on all four horizons, now A's mix: 5% money market,
  35% Nasdaq Equity Income, 10% Global Technology, 25% Global Infra Equity, 25% Asian Multi-Asset
  Income - 7.13% / −24.9% (150,902 of the 322,725 inside the budget; 7.14% until v119).
  Until v106 it held 10% money market, 35% Nasdaq Equity Income, 5% Global Technology, 20% Global
  Health Care and 30% Global Infra Equity for 7.10%; the valuation tilt lifts the equity funds
  more than the multi-asset fund, and Asian Multi-Asset Income replaces Global Health Care.
- **D, Nasdaq Equity Income-led** (owner, 7 Nov 2026, v96; re-set 12 Nov 2026, v99: "Update
  portfolio D as the atram nasdaq equity income as main fund with best and recommended number of
  allocations in a portfolio based on the macroeconomic sentiment, market trend, volatility,
  regional rankings deep analysis of 3, 5, 10yrs and with in the drawdown band"; on the four
  analyses at 1, 3, 5 and 10 years from v107): B's rule, inputs and band budget over every mix
  with Nasdaq Equity Income as the largest holding of two to five funds, each at least 5%, with
  **no single-fund cap and no cash floor** (the owner's choice of 7 Nov). The rule picks the
  number of funds (174,390 mixes, 30,274 inside the budget): **four** - 50% Nasdaq Equity Income,
  20% Asian Multi-Asset Income, 15% Global Health Care, 15% Global Infra Equity (v119; 10% and 20%
  in v117-v118, when Asian Multi-Asset Income's valuation tilt was 0.05pp, and 15% and 15% until
  v116). 7.19% / −24.9% on the 1/3/5/10-year view (7.28% / −24.8% on the 10-year), 0.06pp above B,
  by giving up the cap and the cash floor. Each count's best: two funds 7.07% / −25.0%, three
  7.16% / −24.9%, four 7.19% / −24.9%, five 7.19% / −25.0% (four and five tie; the shallower
  drawdown decides). It holds no peso cash, and all four funds are unhedged; across the band's
  steps it runs from 6.70% / −20.0% (20%) through 7.10% / −24.0% (24%) and 7.28% / −25.9% (26%)
  to 7.60% / −29.8% (30%).

**The Budget tab** reads, on 1-5, whether the next five years justify moving the 25% budget -
months 1-6 (10%), months 7-12 (10%), years 2-3 (40%) and years 4-5 (40%) (owner, 17 Nov 2026, v112:
"6months, 1yr, 3yrs, 5yrs and 10yrs"; year 1 whole at 20% from 15 Nov), with the ten-year view shown
beside them as the anchor and not weighted (neutral by construction, it is what the 25% base stands
for, and it sets A's forecasts). Months 1-6 are researched on their own; months 7-12 are what year 1
leaves once they are taken out, so the halves average back to year 1 and the split moves the reading
only when the research moves year 1. On 20 Nov (v117) months 1-6 read 3.53 and months 7-12 3.13 (the
gauge 2.93, hold at 25%, as on year 1 whole; 3.51 and 3.11 on 17 Nov; years 2-3 2.82 from v119, when the drivers
moved to 1-5, from 2.83) - from three parts over each span: the macro drivers other than valuation, the
market trend and market valuation (its own part from 16 Nov 2026, so it counts once; volatility
left the reading on 3 Nov 2026 and stays as the guard on a raise), with
bands for a step anywhere from 20% to 30%, one point at a time (owner, 16 Nov 2026; 24-27%
until then) - hold at 25% from 2.80 to 3.20 and one point for every 0.15 of the reading beyond
it (v109, owner 16 Nov 2026, fitted to where the gauge can actually go: stylized extremes read
about 2.0 to 3.7, which 0.30 steps and a 2.50-3.50 hold turned into 23-26% only; now 20-29%), guards that must also be clear, and what each step does to A, B, C and D. Year 1 is researched on its own (the section "The year ahead" gives each
driver's reading and its evidence); years 2-3 are what the 3-year reading leaves once year 1
is taken out, so no year counts twice and no pick moves. On 16 Nov it reads 2.93 (year 1 3.32,
years 2-3 2.83, years 4-5 2.83): hold at 25%, as at October's month-end (restated on the
three-part rule), the first review on record. Since v77 the band sets
the budget for A and B (owner, 28 Oct), since v96 for D and since v111 for C, through the same guards.

The earlier Portfolio C - Nasdaq Equity Income held at exactly 50%, the one exemption from the 35% cap, the
rest by B's rule - was first added on 2026-09-25, removed on 2026-10-28 (v76), restored on
2026-10-29 (v82) and **retired on 2026-11-12 (v101)** at the owner's request ("Remove and clean up
the portfolio C"). Its pinned search was separate from A's, B's and D's, so no other pick moved:
at its retirement it held 5% money market, 50% Nasdaq Equity Income, 20% Global Health Care, 20%
Global Infra Equity and 5% Asian Multi-Asset Income for 7.14% / −24.9%. An earlier Portfolio D -
C on four funds only (Money Market, Nasdaq Equity Income, Asia Equity and Global Technology),
added on 2026-10-23 - was removed on 2026-10-27 (v74), for the same reason changing nothing else.

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
held out until its trust fee is confirmed (at the listed 1.20% it would take 15% of A and
15% of B, at the 25% budget); Global Bond Income would move the picks most (at its 1.00%
trust fee, confirmed in v113, 20-35% of A). **The Asian Multi-Asset Income trust fee is disputed** (1.50% on ATRAM's
page, carried; 1.20% in its October 2025 KIID): at 1.20%, A would hold 35% of it against 25%
now, and B 25%, as now (`model/heldout_sens.py`, v119). The page states every figure here from the
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
