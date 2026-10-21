# Peso Four-Fund Macro Desk

A mobile-first macro and allocation dashboard for a peso investor in ATRAM unit
investment trust funds - the four original funds and Global Dividend, from a review of
the ATRAM list - built for a ten-year horizon.

**Live:** https://claude.ai/code/artifact/307440fd-2952-4b4c-b55c-51725163be31

## The four funds

| Code | Fund | Own stated target |
|---|---|---|
| `ATRPHMM` | ATRAM Peso Money Market Fund | Beat PH bank deposits, duration ≤ 1 year |
| `ATRQIAP` | ATRAM Nasdaq Equity Income Feeder Fund | JPM Nasdaq Equity Premium Income Active UCITS ETF · 75% Nasdaq-100 |
| `ATRASEQ` | ATRAM Asia Equity Opportunity Feeder Fund | JPMorgan Asia Equity Dividend Fund |
| `ATRGTEC` | ATRAM Global Technology Feeder Fund | Fidelity Funds – Global Technology · MSCI ACWI IT |

One more from the review completes the five the engine chooses over:

| Code | Fund | Own stated target |
|---|---|---|
| `ATRGLDV` | ATRAM Global Dividend Feeder Fund | Fidelity Funds – Global Dividend Fund |

The ATRAM Long Term and Medium Term Peso Bond funds were removed from the list and
from every allocation on 21 Oct 2026, at the owner's instruction.

Each fund is measured against its own target, not a house benchmark.

## Result

Ten-year horizon, net of every fee layer, on J.P. Morgan's 2027 long-term capital
market assumptions. Market data as of 21 Oct 2026 (Philippine and Asian closes; US
series to 20 Oct).

| | A · Long-run view | B · Macro view | C · Nasdaq Income at 50% |
|---|---|---|---|
| Allocation (MM / Nasdaq Inc / Asia / Tech / Global Dividend) | **25 / 30 / 0 / 25 / 20** | **30 / 35 / 10 / 25 / 0** | 20 / 50 / 20 / 10 / 0 |
| 10y net CAGR after all fees | 6.72% | 6.77% | **6.80%** |
| Expected max drawdown (10y) | −26.4% | **−26.3%** | −26.4% |
| Return per unit of drawdown | 0.255 | 0.257 | **0.258** |

All three rows are on the macro view. **One rule chooses all three**, over the five
funds within the review's limits (at most 5 funds, 35% in any one, at least 5% peso
cash; 2,065 mixes): the best 10-year net CAGR after fees inside the drawdown budget,
then the lowest drawdown within 0.05pp of it. The engine re-chooses each at every
update:
- **A, the long-run view**: the rule on the long-run return assumptions alone (6.97% /
  −26.3% there), with no cycle view.
- **B, the macro view**: the rule on the macro-adjusted returns - the regional
  ranking and the market trend, each at 3, 6 and 12 months against the 10-year
  anchor, the volatility curve, and the drivers' rates and energy tilts. On them B
  returns 0.05pp a year more than A for 0.1pp less drawdown (21 mixes inside the tie).
- **C** is B with Nasdaq Equity Income held at 50% (the pin is exempt from the 35%
  cap): 0.03pp a year above B for 0.1pp more drawdown. It is the same mix the old
  four-fund C held: Global Dividend does not enter it.

Without the bond fund, cash is the only sleeve that does not fall with equities, so
the budget is met by holding 20-30% of it; the forecasts are about 0.35pp a year below
the bond-fund versions (7.08-7.13%). The budget, −27.17%, is the original 20 / 30 /
25 / 25 baseline's drawdown less 2.83pp; that baseline is kept only as the budget's
reference. The list is now 22 funds, down from 24 with the two peso bond funds removed. Over it, the review's own long-run pick holds
25% Global Health Care, a fund this page does not model, so A differs from it. US
Equity Opportunity is held out until its trust fee is confirmed (at the listed 1.20%
it would take 25% of A, 20% of B and 15% of C). The page states every figure here
from the engine; this table is a snapshot of it, and the review audit fails if it
drifts.

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
```

Every figure on the page is computed by the engine. Change an input in the
`VERIFIED INPUTS` block and everything downstream recomputes.

## Keeping it current

There is no automation — the review is manual. `monitoring/README.md` is the
runbook, `monitoring/CLAIMS.md` the checklist of every figure and its source, and
`monitoring/CHANGELOG.md` the history including every bug found and fixed.

## Disclaimer

Portfolio analysis on five named funds (A, B and C hold four each) over a
10-year horizon, not personal financial advice.
Forecasts are modelled expectations, not guarantees. UITF investments are not
deposits and are not insured by the PDIC.
