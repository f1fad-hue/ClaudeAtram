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

Portfolio D adds two more, held in D only:

| Code | Fund | Own stated target |
|---|---|---|
| `ATRLTPB` | ATRAM Long Term Peso Bond Fund | PH government debt (up to 20% IG corporates), average portfolio life ≤ 7 years |
| `ATRGDIV` | ATRAM Global Dividend Feeder Fund | Fidelity Funds – Global Dividend Fund |

Each fund is measured against its own target, not a house benchmark.

## Result

Ten-year horizon, net of every fee layer. Market data as of 20 Oct 2026.

| | A · Baseline | B · Optimised | C · Nasdaq Income at 50% |
|---|---|---|---|
| Allocation (MM / Nasdaq Inc / Asia / Tech) | 20 / 30 / 25 / 25 | **25 / 15 / 55 / 5** | **20 / 50 / 25 / 5** |
| 10y net CAGR after all fees | 6.74% | **6.76%** | 6.54% |
| Expected max drawdown (10y) | −30.1% | **−26.3%** | −25.6% |
| Return per unit of drawdown | 0.224 | **0.257** | 0.255 |

B and C are chosen by one rule: the best net CAGR the drawdown budget allows
(the baseline's drawdown less 2.83pp), then the lowest drawdown among portfolios
within 0.05pp of it. B is built from macro sentiment, the correlated per-sleeve
transmission, the volatility curve, the regional rankings and the market trend, each
at 3 / 6 / 12 months against the 10-year anchor. Almost all of B's improvement on the
baseline is drawdown: the forecasts are level at the model's precision (0.02pp apart,
inside the 0.05pp tie) and B's drawdown is 3.8pp shallower. The page states this, and every figure here, from
the engine; this table is a snapshot of it, and the review audit fails if it drifts.

### Portfolio D · the 22-fund review pick (added 21 Oct 2026)

| | D |
|---|---|
| D · Allocation (MM / Nasdaq Inc / Asia / Tech / LT Peso Bond / Global Dividend) | **5 / 35 / 0 / 20 / 35 / 5** |
| D · 10y net CAGR after all fees | 6.53% |
| D · Expected max drawdown (10y) | −22.1% |
| D · Return per unit of drawdown | 0.295 |

D's weights are fixed. They come from a 21 Oct review of all 22 ATRAM funds on
J.P. Morgan's 2027 assumptions: the best worst-case return across six stress tests,
inside the drawdown budget in every one (7.38% / −21.5% there, 6.91% at worst).
Measured here on the page's own basis, the same as A, B and C, it returns 6.53%
(level with C) at a drawdown 3.5pp shallower.

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
