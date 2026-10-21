# Peso Four-Fund Macro Desk

A mobile-first macro and allocation dashboard for a peso investor in ATRAM unit
investment trust funds - the four original funds and two more from a review of all
22 - built for a ten-year horizon.

**Live:** https://claude.ai/code/artifact/307440fd-2952-4b4c-b55c-51725163be31

## The four funds

| Code | Fund | Own stated target |
|---|---|---|
| `ATRPHMM` | ATRAM Peso Money Market Fund | Beat PH bank deposits, duration ≤ 1 year |
| `ATRQIAP` | ATRAM Nasdaq Equity Income Feeder Fund | JPM Nasdaq Equity Premium Income Active UCITS ETF · 75% Nasdaq-100 |
| `ATRASEQ` | ATRAM Asia Equity Opportunity Feeder Fund | JPMorgan Asia Equity Dividend Fund |
| `ATRGTEC` | ATRAM Global Technology Feeder Fund | Fidelity Funds – Global Technology · MSCI ACWI IT |

Two more from the review complete the six the engine chooses over:

| Code | Fund | Own stated target |
|---|---|---|
| `ATRLTPB` (model label; Bloomberg PRUPIBA) | ATRAM Long Term Peso Bond Fund | PH government debt (up to 20% IG corporates), average portfolio life ≤ 7 years |
| `ATRGLDV` | ATRAM Global Dividend Feeder Fund | Fidelity Funds – Global Dividend Fund |

Each fund is measured against its own target, not a house benchmark.

## Result

Ten-year horizon, net of every fee layer, on J.P. Morgan's 2027 long-term capital
market assumptions. Market data as of 21 Oct 2026 (Philippine and Asian closes; US
series to 20 Oct).

| | A · Long-run view | B · Macro view | C · Nasdaq Income at 50% |
|---|---|---|---|
| Allocation (MM / Nasdaq Inc / Asia / Tech / LT Peso Bond / Global Dividend) | **5 / 25 / 0 / 35 / 35 / 0** | **5 / 20 / 5 / 35 / 35 / 0** | 5 / 50 / 0 / 20 / 25 / 0 |
| 10y net CAGR after all fees | **7.13%** | 7.12% | 7.08% |
| Expected max drawdown (10y) | −25.8% | −25.7% | **−25.6%** |
| Return per unit of drawdown | 0.276 | **0.277** | **0.277** |

All three rows are on the macro view. **One rule chooses all three**, over the six
funds within the review's limits (at most 5 funds, 35% in any one, at least 5% peso
cash; 8,775 mixes): the best 10-year net CAGR after fees inside the drawdown budget,
then the lowest drawdown within 0.05pp of it. The engine re-chooses each at every
update:
- **A, the long-run view**: the rule on the long-run return assumptions alone (7.67% /
  −25.4% there), with no cycle view. It is the same mix the 21 Oct review of all 22
  ATRAM funds found over the 13 it kept after screening, and the page says so only
  while that holds.
- **B, the macro view**: the rule on the macro-adjusted returns - the regional
  ranking and the market trend, each at 3, 6 and 12 months against the 10-year
  anchor, the volatility curve, and the drivers' rates and energy tilts. On them B
  returns 0.01pp a year less than A for 0.1pp less drawdown (9 mixes inside the tie).
  Its 5% satellite sits on the tie's edge: it was Global Dividend until the money
  market's fee was corrected on 21 Oct, which moved the band by 0.004pp.
- **C** is B with Nasdaq Equity Income held at 50% (the pin is exempt from the 35%
  cap): 0.04pp a year below B for 0.1pp less drawdown.

The budget, −27.17%, is the original 20 / 30 / 25 / 25 baseline's drawdown less
2.83pp; that baseline is kept only as the budget's reference. The list is now 24
funds; US Equity Opportunity is held out until its trust fee is confirmed (at the
listed 1.20% it would take 30% of A and of B and 25% of C). The page states every figure
here from the engine; this table is a snapshot of it, and the review audit fails if
it drifts.

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

Portfolio analysis on six named funds (A and C hold four each, B five) over a
10-year horizon, not personal financial advice.
Forecasts are modelled expectations, not guarantees. UITF investments are not
deposits and are not insured by the PDIC.
