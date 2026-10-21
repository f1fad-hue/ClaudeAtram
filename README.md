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

A and D add two more (A holds the bond fund; D holds both):

| Code | Fund | Own stated target |
|---|---|---|
| `ATRLTPB` (model label; Bloomberg PRUPIBA) | ATRAM Long Term Peso Bond Fund | PH government debt (up to 20% IG corporates), average portfolio life ≤ 7 years |
| `ATRGLDV` | ATRAM Global Dividend Feeder Fund | Fidelity Funds – Global Dividend Fund |

Each fund is measured against its own target, not a house benchmark.

## Result

Ten-year horizon, net of every fee layer, on J.P. Morgan's 2027 long-term capital
market assumptions. Market data as of 21 Oct 2026 (Philippine and Asian closes; US
series to 20 Oct).

| | A · Highest return | C · Nasdaq Income at 50% | D · Best worst case |
|---|---|---|---|
| Allocation (MM / Nasdaq Inc / Asia / Tech / LT Peso Bond / Global Dividend) | **5 / 25 / 0 / 35 / 35 / 0** | 20 / 50 / 20 / 10 / 0 / 0 | **5 / 35 / 0 / 20 / 35 / 5** |
| 10y net CAGR after all fees | **7.13%** | 6.78% | 6.91% |
| Expected max drawdown (10y) | −25.8% | −26.4% | **−21.8%** |
| Return per unit of drawdown | 0.276 | 0.257 | **0.317** |

**A and D are the two picks of a 21 Oct review of all 22 ATRAM funds**, on the same
search (at most 5 funds, 35% in any one, at least 5% peso cash):
- **A, highest return** (A since 21 Oct, replacing the 20 / 30 / 25 / 25 baseline):
  the best base-case 10-year net CAGR after fees inside the drawdown budget, then
  the lowest drawdown among the 19 mixes within 0.05pp of it. 7.67% / −25.4% in the
  review; over the budget (−27.3%) if bonds and tech fall together.
- **D, best worst case** (took the place of Portfolio B, retired on 21 Oct): the best
  worst-case return across six stress tests, inside the budget in every one. 7.38% /
  −21.5% in the review, 6.91% at worst against A's 6.87%.

Both weights are fixed; the page measures them on its own basis with the same fees,
tilts, drawdown rule and stress table. On it D returns 0.22pp a year less than A for
4.0pp less drawdown, and the best return per unit of drawdown of the three.

**C** holds Nasdaq Equity Income at 50% and chooses the other three original funds by
the page's rule: the best net CAGR inside the drawdown budget, then the lowest
drawdown within 0.05pp. The budget, −27.17%, is the original 20 / 30 / 25 / 25
baseline's drawdown less 2.83pp; that baseline is kept only as the budget's reference.
The page states every figure here from the engine; this table is a snapshot of it,
and the review audit fails if it drifts.

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

Portfolio analysis on six named funds (four in A, B and C; two more in D) over a
10-year horizon, not personal financial advice.
Forecasts are modelled expectations, not guarantees. UITF investments are not
deposits and are not insured by the PDIC.
