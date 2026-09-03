# Peso Four-Fund Macro Desk

A mobile-first macro and allocation dashboard for a peso investor holding four
ATRAM unit investment trust funds, built for a five-year horizon.

**Live:** https://claude.ai/code/artifact/307440fd-2952-4b4c-b55c-51725163be31

## The four funds

| Code | Fund | Own stated target |
|---|---|---|
| `ATRPHMM` | ATRAM Peso Money Market Fund | Beat PH bank deposits, duration ≤ 1 year |
| `ATRQIAP` | ATRAM Nasdaq Equity Income Feeder Fund | JPM Nasdaq Equity Premium Income Active UCITS ETF · 75% Nasdaq-100 |
| `ATRASEQ` | ATRAM Asia Equity Opportunity Feeder Fund | JPMorgan Asia Equity Dividend Fund |
| `ATRGTEC` | ATRAM Global Technology Feeder Fund | Fidelity Funds – Global Technology · MSCI ACWI IT |

Each fund is measured against its own target, not a house benchmark.

## Result

| | Baseline | Optimised |
|---|---|---|
| Allocation (MM / Nasdaq Inc / Asia / Tech) | 20 / 30 / 25 / 25 | **15 / 45 / 35 / 5** |
| 5y net CAGR after all fees | 7.17% | **7.31%** |
| Expected max drawdown | −20.7% | **−18.6%** |
| Return per unit of drawdown | 0.347 | **0.393** |

Better on both axes at once — the baseline carries two 0.88-correlated US tech
sleeves at a combined 55%, which costs drawdown without buying return.

## Layout

```
model/engine.py      the whole model - pure stdlib Python, no dependencies
model/data.json      generated payload, embedded into the page
dashboard.html       the published artifact
monitoring/          weekly job spec, claim register, changelog
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

Portfolio analysis on four named funds, not personal financial advice.
Forecasts are modelled expectations, not guarantees. UITF investments are not
deposits and are not insured by the PDIC.
