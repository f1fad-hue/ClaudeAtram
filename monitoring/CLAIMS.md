# Claim register

Every numeric claim on the dashboard, its primary source, and when it was last
verified. There is no automated job: walk this file line by line during a manual
review and stamp each row `VERIFIED` / `CHANGED` / `STALE` / `UNREACHABLE`.

Rows marked **D** are re-checked mechanically — the independent verifier in the
review harness asserts them against `model/data.json`, because on 5 September an
audit found eleven rows here had drifted from the model they describe. A register
that goes stale is worse than none: it certifies figures that have moved.

Status legend: **P** = published primary figure · **E** = estimate, labelled as
such on the page · **D** = derived by `model/engine.py` from other rows.

## Monetary policy

| Claim | Value | Kind | Source | Last verified |
|---|---|---|---|---|
| Fed funds target range | 3.50–3.75% | P | federalreserve.gov FOMC statement 2026-07-29 | 2026-09-05 |
| July FOMC vote | 9–3 hold, 3 dissents for a hike | P | federalreserve.gov | 2026-09-05 |
| ECB deposit facility rate | 2.25% | P | ecb.europa.eu decision 2026-06-11 | 2026-09-05 |
| ECB June move | +25bp, first hike in 3 years | P | ecb.europa.eu | 2026-09-05 |
| Euro-area HICP projection | 3.0% / 2.3% / 2.0% (2026/27/28) | P | Eurosystem staff projections | 2026-09-05 |
| BSP target RRP rate | 5.00% | P | bsp.gov.ph key rates | 2026-09-05 |
| BSP last move | +25bp on 27 Aug 2026 — third consecutive, +75bp since April | P | bsp.gov.ph | 2026-09-05 |

## Prices, activity and rates

| Claim | Value | Kind | Source | Last verified |
|---|---|---|---|---|
| US CPI headline y/y (Jul 2026) | 3.4% | P | bls.gov CPI release | 2026-09-05 |
| US CPI core y/y (Jul 2026) | 2.5% | P | bls.gov | 2026-09-05 |
| **US PCE y/y / 6m annualised** | **3.7% / 4.1%** | P | cited by Chair Warsh, Jackson Hole (CNBC) | 2026-09-05 |
| US 10-year Treasury yield | 4.76% | P | market data, 3 Sep | 2026-09-05 |
| Fed Sep 15-16 hike probability | 58%, from 49.4% pre-payrolls | P | CME FedWatch | 2026-09-05 |
| **Euro area HICP (Aug 2026 flash)** | **3.3%**, from 2.9% Jul | P | Eurostat flash, 1 Sep | 2026-09-05 |
| Euro area energy inflation (Aug) | +14.3% y/y | P | Eurostat flash | 2026-09-05 |
| ECB Sep-10 expectation | +25bp to 2.50%, then done | P | Reuters economist poll | 2026-09-05 |
| PH core inflation (Jul 2026) | 4.2%, from 4.4% Jun | P | PSA / BusinessWorld | 2026-09-05 |
| Hormuz commodity transits | ~5 vessels vs 10-day avg 14 | P | Bloomberg, 3 Sep | 2026-09-05 |
| **US nonfarm payrolls (Aug 2026)** | **+162,000** vs 53,000 consensus | P | bls.gov Employment Situation | 2026-09-05 |
| US nonfarm payrolls (Jul 2026) | −23,000 | P | bls.gov | 2026-09-05 |
| **PH CPI (Aug 2026)** | **6.1%**, from 6.2% Jul | P | psa.gov.ph | 2026-09-05 |
| PH CPI year-to-date average | 5.2% | P | psa.gov.ph | 2026-09-05 |
| US unemployment rate | 4.1% | P | bls.gov | 2026-09-05 |
| PH T-bill 91d / 182d / 364d | 5.138% / 5.517% / 5.717% | P | treasury.gov.ph auction results | 2026-09-05 |
| Brent crude | $94.86 | P | EIA / market data | 2026-09-05 |
| Brent y/y change | +40.33% | P | market data | 2026-09-05 |
| Brent Q1 2026 close | $118 from $61 at year open | P | eia.gov Today in Energy | 2026-09-05 |
| IMF global growth 2026 / 2027 | 3.1% / 3.2% | P | IMF WEO April 2026 | 2026-09-05 |
| IMF US growth 2026 / 2027 | 2.4% / 2.0% | P | IMF WEO April 2026 | 2026-09-05 |
| IMF euro-area growth 2026 | 0.7% (from 1.1% in 2025) | P | IMF WEO April 2026 | 2026-09-05 |

## Volatility complex

| Claim | Value | Kind | Source | Last verified |
|---|---|---|---|---|
| Spot VIX | 16.44 (2 Sep close, +10.2% on the day) | P | Cboe | 2026-09-05 |
| VIX 2026 low | 14.13 (28 Aug) | P | Cboe | 2026-09-05 |
| VIX 30-day range / average | 14.13–18.43 / 15.28 | P | Cboe | 2026-09-05 |
| September VIX future | 17.92 | P | Cboe | 2026-09-05 |
| December VIX future | 20.38 | P | Cboe | 2026-09-05 |
| Long-run VIX anchor | 19.5 | E | historical VIX mean 1990–2025 | 2026-09-05 |
| Variance risk premium | 3.5 vol points | E | implied minus realised, long-run | 2026-09-05 |
| Horizon vol 3M/6M/12M/5Y | 18.27 / 19.25 / 19.62 / 19.57% | D | engine, forward-variance integration | 2026-09-05 |
| Volatility ramp (blend − spot) | 19.31% − 16.44 = +2.87 vol pts | D | engine | 2026-09-05 |

## Valuation and earnings

| Claim | Value | Kind | Source | Last verified |
|---|---|---|---|---|
| Nasdaq-100 forward P/E | 22.4× | P | market data | 2026-09-05 |
| Nasdaq-100 10y / 5y average forward P/E | 22.9× / 24.7× | P | market data | 2026-09-05 |
| STOXX Europe 600 forward P/E | 15.37× | P | Siblis Research / STOXX | 2026-09-05 |
| STOXX Europe 600 YTD (to Jul 2026) | +9.5% | P | STOXX | 2026-09-05 |
| MSCI AC Asia ex-Japan forward P/E | 10.5× | P | J.P. Morgan Asia Mid-Year Outlook 2026 | 2026-09-05 |
| Asia ex-Japan EPS growth 2026 / 2027 | ~52% / ~28% | P | J.P. Morgan Asia Mid-Year Outlook 2026 | 2026-09-05 |
| Korea / Taiwan YTD (to 20 Jul 2026) | +71% / +49% | P | market data | 2026-09-05 |
| JPM LTCMA 2026 US equity | 6.7% | P | am.jpmorgan.com LTCMA release | 2026-09-05 |
| JPM LTCMA 2026 EM equity (USD) | 7.8% | P | am.jpmorgan.com LTCMA release | 2026-09-05 |

## Fund structure and fees

| Claim | Value | Kind | Source | Last verified |
|---|---|---|---|---|
| ATRPHMM all-in fee | 0.71% of average daily NAV | P | ATRAM KIIDS | 2026-09-05 |
| ATRPHMM mandate | duration ≤ 1 year, beat bank deposits | P | ATRAM KIIDS | 2026-09-05 |
| ATRQIAP management fee | 1.50% p.a. | P | ATRAM / launch coverage | 2026-09-05 |
| ATRQIAP target fund | JPM Nasdaq Equity Premium Income Active UCITS ETF, IE000U9J8HX9 | P | ATRAM / JPMAM | 2026-09-05 |
| ATRQIAP stated benchmark | 75% Nasdaq-100 Index | P | ATRAM / launch coverage | 2026-09-05 |
| Target-fund TER (JEPQ UCITS) | 0.35% | P | JPMAM factsheet | 2026-09-05 |
| Underlying distribution yield | ~9% p.a. | P | JPMAM / justETF | 2026-09-05 |
| ATRASEQ trustee + auditor fee | 1.17% + 0.01% | P | ATRAM KIIDS | 2026-09-05 |
| ATRASEQ target fund | JPMorgan Asia Equity Dividend Fund | P | ATRAM KIIDS | 2026-09-05 |
| ATRASEQ inception | 08 Dec 2016 | P | ATRAM / uitf.com.ph | 2026-09-05 |
| **ATRASEQ target-fund OCF** | **0.80%** | **E** | **not located — promote when published** | 2026-09-05 |
| ATRGTEC management fee | 1.15% p.a. | P | ATRAM KIIDS | 2026-09-05 |
| ATRGTEC target fund | Fidelity Funds – Global Technology Fund | P | ATRAM KIIDS | 2026-09-05 |
| ATRGTEC benchmark | MSCI ACWI Information Technology | P | Fidelity factsheet | 2026-09-05 |
| Fidelity Global Technology 5y annualised | 15.20% (W GBP, to 20 Aug 2026) | P | Fidelity / platform data | 2026-09-05 |
| **ATRGTEC target-fund OCF** | **0.95%** | **E** | **not located — promote when published** | 2026-09-05 |

## Modelled assumptions (not published figures)

These are the model's own judgements. They are not claims about the world and
cannot be "verified" — but each one should be re-examined at every manual review,
and the arithmetic that uses them re-derived independently.

| Assumption | Value | Rationale |
|---|---|---|
| PHP depreciation drift vs USD | 2.0% p.a. | PPP: PH inflation ~3.9% vs US ~2.4% |
| USD/PHP volatility | 6.0% | long-run realised |
| FX/equity correlation | −0.20 | peso weakens in risk-off, cushioning PHP holders |
| Drawdown model | k·σ − 0.50µ, anchor k = 1.65 | calibrated to S&P 500 ≈ −20% and NDX ≈ −33% rolling 5y medians |
| Per-sleeve drawdown k | 1.65 cash · 1.55 ATRQIAP · 1.70 ATRASEQ · 1.80 ATRGTEC | left tails differ in shape; each adjustment is published on the page with its reason |
| Portfolio drawdown k | 1.675 baseline · 1.626 optimised | ex-cash weighted average of the sleeve coefficients |
| Correlation ATRQIAP↔ATRGTEC | 0.88 | both US mega-cap tech engines |
| Correlation ATRQIAP↔ATRASEQ | 0.66 | |
| Correlation ATRASEQ↔ATRGTEC | 0.74 | Asia semis in the global tech complex |
| Money market vs equities | 0.00 | |
| Regional tilt sensitivity | 0.675pp of CAGR per 1–5 macro score point above the 3.0 neutral (= 0.30pp per 1–10 point) | |
| Reporting scales | drivers and regions researched 1–10; gauge and regional rankings reported 1–5 | endpoint-preserving rescale, 5.5 → 3.0 |
| Volatility tilt sensitivity | +0.035 ATRPHMM · +0.210 ATRQIAP · 0.000 ATRASEQ · −0.122 ATRGTEC, per vol point of ramp | structural, not a view |
| Horizon blend weights | 3M 15% · 6M 25% · 12M 30% · 5Y 30% | 5-year mandate keeps the long end dominant |
| Drawdown budget for the optimiser | baseline max DD less 2.0pp | states the objective explicitly |
