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
| Sep FOMC hike odds | 85.6% (11 Sep, after August CPI); 70% on 10 Sep after PPI; 58% a week earlier | P | CME FedWatch (verified via search result) | 2026-09-11 |
| US August CPI | headline 3.4% y/y unchanged, +0.4% m/m; core 2.4% y/y, +0.3% m/m (0.1pp above consensus); shelter 3.0% from 3.2%; gasoline +27.4% y/y | P | BLS release 2026-09-11 (verified via search result) | 2026-09-11 |
| July FOMC vote | 9–3 hold, 3 dissents for a hike | P | federalreserve.gov | 2026-09-05 |
| ECB deposit facility rate | **2.50%** — hiked +25bp on 10 Sep 2026; MRO 2.65%, MLF 2.90%, effective 16 Sep | P | ECB Governing Council decision 2026-09-10 (verified via search result) | 2026-09-11 |
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
| US 10-year Treasury yield | 4.96% (11 Sep close); 4.92% on 10 Sep was already a ten-year high | P | Treasury Yields Snapshot 2026-09-11 (verified via search result) | 2026-09-11 |
| US 2-year Treasury yield | 4.63% (11 Sep close) — **gap closed**; was 4.377% and marked STALE on 10 Sep | P | Treasury Yields Snapshot 2026-09-11 (verified via search result) | 2026-09-11 |
| US 30-year Treasury yield | 5.36% (11 Sep close) | P | Treasury Yields Snapshot 2026-09-11 (verified via search result) | 2026-09-11 |
| Fed Sep 15-16 hike probability | 58%, from 49.4% pre-payrolls | P | CME FedWatch | 2026-09-05 |
| **Euro area HICP (Aug 2026 flash)** | **3.3%**, from 2.9% Jul | P | Eurostat flash, 1 Sep | 2026-09-05 |
| Euro area energy inflation (Aug) | +14.3% y/y | P | Eurostat flash | 2026-09-05 |
| ECB Sep-10 expectation | +25bp to 2.50% — all 65 economists polled; 91% see it held to year end; shortest campaign since 2011 | P | Reuters poll 31 Aug–3 Sep | 2026-09-07 |
| PH core inflation (Jul 2026) | 4.2%, from 4.4% Jun | P | PSA / BusinessWorld | 2026-09-05 |
| Hormuz — **oil volume** (the measure that reaches this portfolio) | Gulf crude+products **15.5 mb/d** vs a **23.0 mb/d** pre-war baseline = **~67%, two-thirds**; trough was 5.5 mb/d in March; ~5.0 mb/d moves via dark crossings and ship-to-ship | P | Goldman Sachs (Struyven, Zhestkova Grigsby) 2026-08-28 via Bloomberg/Rigzone (verified via search result). Baseline is Goldman's OWN (15.5 + their stated 7.5 still-below), not borrowed from another source | 2026-09-12 |
| Hormuz — **vessel counts** (disputed, ~5x spread) | IMF PortWatch **6/day** (all transits) · Lloyd's List Intelligence **14/day** (cargo >10,000 dwt, 17–23 Aug) · US government **~30/day** (basis undisclosed) · JMIC 1 Sep advisory: "far below baseline" | P | PortWatch / Lloyd's / Al Jazeera 2026-09-03 "Why data doesn't match US claims" (all verified via search result) | 2026-09-12 |
| Hormuz baseline, vessel basis | ~85 transits/day pre-crisis (~93% drop) — **NOT a supply figure**; the ~85 counts all vessel types while the oil moves on a subset | P | IMF PortWatch | 2026-09-12 |
| Hormuz diplomacy | Iran + GCC foreign ministers and Iraq meet in Oman **Monday 14 Sep**; Iran and Oman have already agreed a temporary shipping lane and mine clearing | P | Al Jazeera 2026-09-11 (verified via search result). NOTE: one search summary put this on 15 Sep; the Monday after Friday 11 September 2026 is the **14th** | 2026-09-12 |
| **US nonfarm payrolls (Aug 2026)** | **+162,000** vs 53,000 consensus | P | bls.gov Employment Situation | 2026-09-05 |
| US nonfarm payrolls (Jul 2026) | −23,000 | P | bls.gov | 2026-09-05 |
| **PH CPI (Aug 2026)** | **6.1%**, from 6.2% Jul | P | psa.gov.ph | 2026-09-05 |
| PH CPI year-to-date average | 5.2% | P | psa.gov.ph | 2026-09-05 |
| US unemployment rate | 4.1% | P | bls.gov | 2026-09-05 |
| PH T-bill 91d / 182d / 364d | 5.138% / 5.517% / 5.717% | P | treasury.gov.ph auction results | 2026-09-05 |
| USD/PHP | 62.68 — **11 Sep close**, another record low; 62.775 intraday; prior record 62.625 on 8 Sep | P | Philippine business press (verified via search result) | 2026-09-11 |
| Brent crude | **$104.61 — a confirmed 11 Sep SETTLE**, −2.8% on the day, +8.7% on the week, above $100; passed $108 on 10 Sep, highest since 19 May | P | oil market reporting 2026-09-11 (verified via search result) — **gap closed**: the 10 Sep level had no confirmed settle and sources spread $102–108 | 2026-09-11 |
| Brent y/y change | +59.71% | D | derived from the $104.61 settle against a $65.50 year-ago base, itself implied by the last verified pair ($96.28 at +46.99%) | 2026-09-11 |
| Brent Q1 2026 close | $118 from $61 at year open | P | eia.gov Today in Energy | 2026-09-05 |
| IMF global growth 2026 / 2027 | 3.1% / 3.2% | P | IMF WEO April 2026 | 2026-09-05 |
| IMF US growth 2026 / 2027 | 2.4% / 2.0% | P | IMF WEO April 2026 | 2026-09-05 |
| IMF euro-area growth 2026 | 0.7% (from 1.1% in 2025) | P | IMF WEO April 2026 | 2026-09-05 |

## Volatility complex

| Claim | Value | Kind | Source | Last verified |
|---|---|---|---|---|
| Spot VIX | 14.32 (4 Sep close - the last trading day; 5 Sep was a Saturday) | P | Cboe | 2026-09-07 |
| VIX 2026 low | 14.18 (17 Aug) | P | CNBC / Cboe | 2026-09-07 |
| VIX Hormuz spike | 16.34 (2 Sep close), retraced to 15.20 then 14.32 | P | market reports | 2026-09-07 |
| 11 Sep session (reversal) | S&P +0.86% to 7,656.98 — first gain in five sessions; WTI settled $100.05, −2.4%; **VIX closed 15.84, −11.21%** — gap closed, and the −11.21% from 15.84 implies a 17.84 prior close, independently corroborating the 10 Sep figure against one outlet that printed "near 17.89"; Nikkei 64,011, KOSPI 6,910 | P | market reporting 2026-09-11/12 (verified via search result) | 2026-09-12 |
| Hormuz diplomacy | Tehran to meet Gulf states in Oman on the Strait (11 Sep) — the reason oil settled down 2.8% | P | oil market reporting 2026-09-11 (verified via search result) | 2026-09-11 |
| Brent full-closure scenario level | $130 | E | the stress row's modelled level, published so the scenario and every note citing it cannot drift | 2026-09-11 |
| VIX latest close | **17.84 on 10 Sep**, +8.38%, high 18.17 — broke a 28-session 14–17 range | P | market reports, two independent searches agreeing; one outlet also printed 17.47/+6.14% for the same session, and both imply the same 16.46 prior close, so the close is carried as 17.84 and the discrepancy is recorded rather than hidden | 2026-09-11 |
| VIX futures strip is NOT re-quoted | curve still on its 4 Sep quote date | — | every source found on 11 Sep echoes the same four 4 Sep levels beside a spot near 14.9, which dates those quotes rather than confirming them; the curve is therefore left on 4 Sep and the 3.52-point spot divergence is published | 2026-09-11 |
| VIX 30-day range / average | 14.18–16.80 / 15.28 | P | Cboe | 2026-09-07 |
| VIX futures strip (levels) | Sep 16.57 · Oct 18.41 · Nov 19.08 · Dec 19.26 | P | VIX term-structure data (verified via search result, not at Cboe directly) | 2026-09-07 |
| VIX quote date | 2026-09-04 (Friday close) | P | the date every VIX level above is quoted at; asserted to be a weekday and not after AS_OF | 2026-09-10 |
| VIX futures maturities | 0.0740 · 0.1699 · 0.2466 · 0.3233 yr | D | derived from the contract settlement rule (Wednesday 30d before the following month's third Friday, plus a 15d window centre) off the quote date; independently re-derived by the verifier | 2026-09-10 |
| Expected PHP depreciation (FX_DRIFT) | 2.0%/yr | E | between long-run relative PPP (3.9 − 2.4 = 1.5pp) and the current print differential (6.1 − 3.4 = 2.7pp); bracket asserted from the model's own inflation inputs | 2026-09-10 |
| Worst-case peso value, ₱1m | ₱744,000 optimised · ₱711,000 baseline | D | the expected max drawdown applied to the OPENING value — the worst case for money invested today, deliberately NOT the low point of the modelled path | 2026-09-10 |
| Long-run VIX anchor | 19.5 | E | historical VIX mean 1990–2025 | 2026-09-05 |
| Variance risk premium | 3.5 vol points | E | implied minus realised, long-run | 2026-09-05 |
| Horizon vol 3M/6M/12M/10Y | 17.35 / 18.33 / 18.86 / 19.43% | D | engine, forward-variance integration over 4 observable contracts, maturities derived from the VIX settlement calendar off the 4 Sep quote date | 2026-09-10 |
| Volatility ramp (blend − spot) | 18.93% − 14.32 = +4.61 vol pts | D | engine | 2026-09-08 |

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
| Target-fund TER (JEPQ UCITS) | 0.35% | P | JPMAM factsheet — re-confirmed across justETF, Morningstar and Cbonds | 2026-09-09 |
| Underlying distribution yield | ~9% p.a. | P | JPMAM / justETF | 2026-09-05 |
| ATRASEQ trustee + auditor fee | 1.17% + 0.01% | P | ATRAM KIIDS | 2026-09-05 |
| ATRASEQ target fund | JPMorgan Asia Equity Dividend Fund | P | ATRAM KIIDS | 2026-09-05 |
| ATRASEQ inception | 08 Dec 2016 | P | ATRAM / uitf.com.ph | 2026-09-05 |
| **ATRASEQ target-fund OCF** | **1.55%** | **E** | anchored on JPMAM's **published 1.50% management fee** for the JPMorgan Asia Equity Dividend Fund; exact share-class OCF still not published, so this errs high. Raised from an unanchored 0.80% on 2026-09-09 | 2026-09-09 |
| ATRGTEC management fee | 1.15% p.a. | P | ATRAM KIIDS | 2026-09-05 |
| ATRGTEC target fund | Fidelity Funds – Global Technology Fund | P | ATRAM KIIDS | 2026-09-05 |
| ATRGTEC benchmark | MSCI ACWI Information Technology | P | Fidelity factsheet | 2026-09-05 |
| Fidelity Global Technology 5y annualised | 15.20% (W GBP, to 20 Aug 2026) | P | Fidelity / platform data | 2026-09-05 |
| ATRGTEC target-fund OCF | **1.04%** | **P** | Fidelity published OCF, W-Acc-GBP class (AMC 0.80% + operating costs), as of 30.04.25 — **promoted from a 0.95% estimate** | 2026-09-09 |

## Modelled assumptions (not published figures)

These are the model's own judgements. They are not claims about the world and
cannot be "verified" — but each one should be re-examined at every manual review,
and the arithmetic that uses them re-derived independently.

| Assumption | Value | Rationale |
|---|---|---|
| PHP depreciation drift vs USD | 2.0% p.a. | PPP: PH inflation ~3.9% vs US ~2.4% |
| USD/PHP volatility | 6.0% | long-run realised |
| FX/equity correlation | −0.20 | peso weakens in risk-off, cushioning PHP holders |
| Drawdown model | (k·σ − 0.50µ) · √(T/5), anchor k = 1.65 | bracket calibrated to S&P 500 ≈ −20% and NDX ≈ −33% rolling **5y** medians; scaled to the mandate horizon because expected max drawdown grows with √T |
| Mandate horizon | 10 years (was 5 until 2026-09-08) | one constant `HORIZON_Y` drives the long vol point, the blend's long bucket, peso compounding, drawdown scaling and every label |
| Drawdown horizon scalar | √(10/5) = 1.4142 | derived from the 5y calibration, not re-fitted to unverified 10y medians |
| Scenario drawdowns | same `(k·σ − 0.50µ)·√(T/5)` as everything else | **the scalar was missing from `run_scenarios` between 2026-09-07 and 2026-09-09**, so the stress table sat next to headline figures on a different horizon scaling |
| Per-sleeve drawdown k | 1.65 cash · 1.55 ATRQIAP · 1.70 ATRASEQ · 1.80 ATRGTEC | left tails differ in shape; each adjustment is published on the page with its reason |
| Portfolio drawdown k | 1.675 baseline · 1.626 optimised | ex-cash weighted average of the sleeve coefficients (before the horizon scalar) |
| Correlation ATRQIAP↔ATRGTEC | 0.88 | both US mega-cap tech engines |
| Correlation ATRQIAP↔ATRASEQ | 0.66 | |
| Correlation ATRASEQ↔ATRGTEC | 0.74 | Asia semis in the global tech complex |
| Money market vs equities | 0.00 | |
| Regional tilt sensitivity | 0.675pp of CAGR per 1–5 macro score point above the 3.0 neutral (= 0.30pp per 1–10 point) | |
| Reporting scales | **everything the reader sees is 1–5** — gauge, regional rankings and (from 2026-09-09) the seven driver scores. All three are *researched* on 1–10, the granularity the evidence supports and the scale every note is written against; each note carries its research-scale score | one endpoint-preserving rescale throughout: 1→1, 5.5→3.0 neutral, 10→5. The map is affine and the driver weights sum to 1, so the weighted composite of the reported driver scores **is** the headline gauge — asserted, not assumed |
| Volatility tilt sensitivity | +0.035 ATRPHMM · +0.210 ATRQIAP · 0.000 ATRASEQ · −0.122 ATRGTEC, per vol point of ramp | structural, not a view |
| Horizon blend weights | 3M 10% · 6M 15% · 12M 25% · 10Y 50% | **reweighted 2026-09-08**: the old 15/25/30/30 put 70% on sub-year horizons while its own comment claimed the anchor was dominant, and it was never revisited when the mandate doubled |
| Drawdown budget for the optimiser | baseline max DD less 2.83pp (= 2.0pp at the 5y calibration, scaled by √(T/5)) | holding it flat would have quietly loosened the objective. The cap is published at the precision it is enforced at — it was rounded until 2026-09-08 |
| Single-sleeve concentration cap | 50% | **added 2026-09-09.** Until then the objective had no diversification constraint; it never bound until the Asia fee correction, at which point the optimiser proposed 75% in one fund |
