# Peso Four-Fund Macro Desk

A mobile-first macro and allocation dashboard for a peso investor holding four
ATRAM unit investment trust funds, built for a ten-year horizon.

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

Ten-year horizon, net of every fee layer. Market data as of 6 Oct 2026.

| | A · Baseline | B · Optimised | C · Nasdaq Income at 50% |
|---|---|---|---|
| Allocation (MM / Nasdaq Inc / Asia / Tech) | 20 / 30 / 25 / 25 | **25 / 15 / 55 / 5** | **20 / 50 / 25 / 5** |
| 10y net CAGR after all fees | 6.84% | **6.81%** | 6.60% |
| Expected max drawdown (10y) | −30.2% | **−26.4%** | −25.7% |
| Return per unit of drawdown | 0.226 | **0.258** | 0.257 |

B and C are chosen by one rule: the best net CAGR the drawdown budget allows
(the baseline's drawdown less 2.83pp), then the lowest drawdown among portfolios
within 0.05pp of it. B is built from macro sentiment, the correlated per-sleeve
transmission, the volatility curve, the regional rankings and the market trend, each
at 3 / 6 / 12 months against the 10-year anchor. Almost all of B's improvement on the
baseline is drawdown: it gives up 0.03pp of forecast return, inside the 0.05pp tie,
for a drawdown 3.8pp shallower. The page states this, and every figure here, from
the engine; this table is a snapshot of it.

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

Portfolio analysis on four named funds over a 10-year horizon, not personal
financial advice.
Forecasts are modelled expectations, not guarantees. UITF investments are not
deposits and are not insured by the PDIC.
