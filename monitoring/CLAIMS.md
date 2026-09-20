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
| Fed funds target range | **3.75–4.00%** — raised 25bp on 16 Sep 2026, first increase since 2023 | P | federalreserve.gov FOMC statement 2026-07-29 | 2026-09-05 |
| Fed dot plot, Sep 2026 | Median end-2026 policy rate **4.1%** — one more hike. 12 of 18 participants at 4.125%, 4 at 4.375%; 16 of 18 see at least one more | P | FOMC Summary of Economic Projections, 16 Sep 2026 (verified via search result) | 2026-09-17 |
| Next-move odds | October **50.9%**; cumulative at least one more by December **88.5%** | P | CME FedWatch, 17 Sep (verified via search result) | 2026-09-17 |
| 16 Sep session | S&P 7,551.81 (−0.45%) · Dow 51,461.90 (−1.21%) · Nasdaq 25,978.42 (−0.01%) — all three reversed intraday gains after Warsh spoke; VIX 16.93 | P | market reporting 2026-09-16 (verified via search result) | 2026-09-17 |
| **18 Sep session (carried)** | **S&P 7,650.50 (+0.17%) · Nasdaq 26,522.55 (+0.39%) · Dow 51,682.64 (−0.18%, −95.40 pts)** on triple witching, ~$7tn expiry. Week: S&P −0.1%, Nasdaq +0.7%, Dow −1.7% — third straight losing week, worst since March. Chain: 51,682.64 + 95.40 = 51,778.04 prior, and 95.40/51,778.04 = 0.18% ✓ | P | CNBC / TheStreet 18 Sep (verified via search result) | 2026-09-19 |
| VIX chain, 14–16 Sep | 17.10 → **17.20** → 16.93. The 16.93/−0.27/−1.57% triple was withheld on 16 Sep because it could not chain off 17.10; it was real but **mis-dated to the 15th**. The missing 17.20 close on the 15th makes all three reconcile exactly | P | market reporting (verified via search result) | 2026-09-17 |
| US August CPI | headline 3.4% y/y unchanged, +0.4% m/m; core 2.4% y/y, +0.3% m/m (0.1pp above consensus); shelter 3.0% from 3.2%; gasoline +27.4% y/y | P | BLS release 2026-09-11 (verified via search result) | 2026-09-11 |
| September FOMC vote | **Unanimous** to hike (July was 9–3 to hold, with 3 dissenting for a hike) | P | federalreserve.gov | 2026-09-05 |
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
| US 10-year Treasury yield | **4.94% (18 Sep close)**, easing back from 5.016% on the 16th. The intraday peak is 5.04% on 15 Sep — **that** is the figure "highest since 2007" belongs to, and the page attached it to the previous close until 2026-09-19 | P | US Treasury yield reporting, 18 Sep (verified via search result) | 2026-09-19 |
| US 2-year Treasury yield | 4.63% (11 Sep close) — **gap closed**; was 4.377% and marked STALE on 10 Sep | P | Treasury Yields Snapshot 2026-09-11 (verified via search result) | 2026-09-11 |
| US 30-year Treasury yield | 5.36% (11 Sep close) | P | Treasury Yields Snapshot 2026-09-11 (verified via search result) | 2026-09-11 |
| Fed Sep 15-16 hike probability | 58%, from 49.4% pre-payrolls | P | CME FedWatch | 2026-09-05 |
| **Euro area HICP (Aug 2026 flash)** | **3.3%**, from 2.9% Jul | P | Eurostat flash, 1 Sep | 2026-09-05 |
| Euro area energy inflation (Aug) | +14.3% y/y | P | Eurostat flash | 2026-09-05 |
| ECB Sep-10 expectation | +25bp to 2.50% — all 65 economists polled; 91% see it held to year end; shortest campaign since 2011 | P | Reuters poll 31 Aug–3 Sep | 2026-09-07 |
| PH core inflation (Jul 2026) | 4.2%, from 4.4% Jun | P | PSA / BusinessWorld | 2026-09-05 |
| Hormuz — **oil volume** (the measure that reaches this portfolio) | Gulf crude+products **15.5 mb/d** vs a **23.0 mb/d** pre-war baseline = **~67%, two-thirds**; trough was 5.5 mb/d in March; ~5.0 mb/d moves via dark crossings and ship-to-ship | P | Goldman Sachs (Struyven, Zhestkova Grigsby) 2026-08-28 via Bloomberg/Rigzone (verified via search result). Baseline is Goldman's OWN (15.5 + their stated 7.5 still-below), not borrowed from another source | 2026-09-12 |
| Hormuz — **vessel counts** (disputed, ~5x spread) | IMF PortWatch **8/day on 13 Sep** (all transits, baseline 85/day measured 28 Feb 2025–27 Feb 2026) · Lloyd's List Intelligence **14/day** (cargo >10,000 dwt, 17–23 Aug) · US government **~30/day** (basis undisclosed) · JMIC 1 Sep advisory: "far below baseline" | P | PortWatch / Lloyd's / Al Jazeera (all verified via search result) — **the PortWatch reading was 6/day dated 6 Sep and sat here fourteen days**; it now carries its own date and a check bounds the lag against PortWatch's weekly Tuesday cadence | 2026-09-20 |
| Hormuz — **queue off berth** | **369 (18 Sep) · 357 (19 Sep) · 376 (20 Sep)** — AIS-visible vessels holding position away from berth in the Hormuz and Gulf watch box, excluding ships within 25 km of a working port. Oscillating, not draining: the first two points alone read as a drawdown and the third contradicts it | P | Straits Daily Brief (verified via search result) — **supersedes a 436 from 30 August on an undisclosed basis**, which is dropped rather than compared against: two vessel counts on unknown bases are not a trend | 2026-09-20 |
| Hormuz baseline, vessel basis | ~85 transits/day pre-crisis (~93% drop) — **NOT a supply figure**; the ~85 counts all vessel types while the oil moves on a subset | P | IMF PortWatch | 2026-09-12 |
| JEPQ look-through | **RE-VERIFIED 2026-09-20, unchanged.** 31 July 2026 is still the most recent published JEPQ fact sheet; all ten top holdings and weights match what the model carries. The 51-day age is JPM's publication lag, not model staleness — but the 60-day look-through check will fail around 29 Sep if the August sheet is not out | P | am.jpmorgan.com JEPQ fact sheet (verified via search result) | 2026-09-20 |
| BoJ decision | **DELIVERED 18 Sep: +25bp to 1.25%**, the highest since 1995, on a **7–2** vote (Asada and Sato dissenting). Three months from the previous move against six before it | P | BoJ Statement on Monetary Policy, 18 Sep; CNBC | 2026-09-19 |
| BoJ market reaction | **The yen FELL** — USD/JPY closed 156.86, +0.58%, a two-week low for the yen — because two dissents cast doubt on the pace of further tightening. A hike that weakens the currency prices the END of a cycle, not improving carry | P | Bloomberg / Reuters 18 Sep | 2026-09-19 |
| Japan core CPI (Aug 2026) | **1.7%**, from 1.8% in July and below a 1.8% consensus — released hours before the decision. Ex fresh food *and* fuel: 1.9% | P | Reuters, 18 Sep | 2026-09-19 |
| FOMC expected outcome | 25bp hike taking the target range to **3.75–4.00%**; ~85–86% priced at Friday's close | P | CME FedWatch / week-ahead previews (verified via search result) | 2026-09-14 |
| Hormuz diplomacy | **POSTPONED.** The 14 Sep Oman meeting, at which Iran was to unveil the temporary shipping lane agreed with Muscat, was called off on the day "in the interests of consensus" per Oman's FM Badr Albusaidi — no new date | P | Bloomberg / Oman FM statement 2026-09-14 (verified via search result) | 2026-09-14 |
| Saudi East–West (Petroline) pipeline | **SHUT 11 Sep** after drone strikes launched from Iraq; satellite imagery shows fire damage at a pumping station. 1,200 km to Yanbu on the Red Sea; ~5.0 mb/d was being rerouted through it **specifically to bypass Hormuz**; design capacity 7 mb/d. **Strike date disputed** — one account dates the pumping-station hit 10 Sep, another says "last Thursday" (the 11th) from an 18 Sep story. The shutdown date is corroborated and nothing downstream depends on the strike date, so the dispute is recorded rather than resolved by picking | P | CNBC 2026-09-11 / Al Jazeera 2026-09-12,14 / Wikipedia East–West Crude Oil Pipeline (verified via search result) | 2026-09-20 |
| Petroline **repair**, which this model had no view of at all | Aramco bypassing the damaged section, targeting **50% of capacity within days** and **full in ~6 weeks** (Bloomberg, 16 Sep); regional officials cited by AP on **18 Sep** put repairs at **3–5 weeks** with only partial flows meanwhile. These are INTENTIONS and ESTIMATES, not deliveries | P | Bloomberg 2026-09-16 / ENR (verified via search result) — until 2026-09-20 the notes said only "still shut", which carried an implied permanence the reporting does not support | 2026-09-20 |
| Yanbu | **No Saudi crude has left since 11 Sep.** Stocks below **15 million barrels**, a **4–7 day** buffer; term cargoes to European refiners being cancelled or deferred. Kpler puts the export loss at **2.5–2.7 mb/d** | P | ENR / Kpler via discoveryalert (verified via search result) — **cross-check**: 2.5–2.7 is about half the 5.0 mb/d the line was carrying, consistent with the ~50% Aramco is targeting, and a check now asserts that agreement | 2026-09-20 |
| Gulf flow reading is now dated | Goldman's 15.5 mb/d "two-thirds" is measured **28 Aug**, before the pipeline was hit. A material part of what it measured ran through the line now shut. No post-shutdown figure published; none invented | D | stated limitation | 2026-09-14 |
| 14 Sep session | **NOT USED.** One search summary returned S&P 7,657 / Nasdaq 26,333.04 / Dow 52,573.29 / VIX 15.84 as Monday's close — every figure identical to **Friday 11 Sep**, and contradicted by same-day reporting that Monday was falling on oil and AI names. Mislabelled; discarded | — | trade-date vs publication-date check | 2026-09-14 |
| **US nonfarm payrolls (Aug 2026)** | **+162,000** vs 53,000 consensus | P | bls.gov Employment Situation | 2026-09-05 |
| US nonfarm payrolls (Jul 2026) | −23,000 | P | bls.gov | 2026-09-05 |
| **PH CPI (Aug 2026)** | **6.1%**, from 6.2% Jul — fourth consecutive deceleration, a five-month low. **Re-verified 2026-09-20** against PSA and three Philippine outlets after one search summary put inflation at "6.2% as of mid-September"; that figure is July's, or a dated article. 6.1% stands | P | psa.gov.ph, DZRH/Rappler/BusinessWorld 4–5 Sep | 2026-09-20 |
| PH CPI **composition** (Aug 2026) | Food and non-alcoholic beverages **4.6%** from 5.2% — this is what drove the deceleration. **RICE 19.4% from 17.1%**, +2.3pp in a month. Jan–Aug average 5.2% | P | psa.gov.ph (verified via search result) — the peso note argued against a fifth deceleration on the oil price alone; the staple re-accelerating is the more concrete risk and was not carried until now | 2026-09-20 |
| PH CPI year-to-date average | 5.2% | P | psa.gov.ph | 2026-09-05 |
| US unemployment rate | 4.1% | P | bls.gov | 2026-09-05 |
| PH T-bill 91d / 182d / 364d | 5.138% / 5.517% / 5.717% | P | treasury.gov.ph auction results | 2026-09-05 |
| USD/PHP | **62.749 — 18 Sep close**, −1.9 centavos from 62.73 on the 17th. The peso came OFF its record: 62.86 on 14 Sep is the weakest close, 62.925 on the 15th the weakest intraday. Spot and the record are now separate inputs | P | Manila Times 18 Sep; GMA News 14 Sep; BusinessWorld 16 Sep | 2026-09-19 |
| USD/PHP record count | **24**, as of the 62.68 print on 11 Sep — not 23. BusinessWorld counted 62.625 (8 Sep) as the 23rd and 62.68 as the 24th; this model had the count attached to the level below it from launch until 2026-09-19. 62.86 is at least one more, but no source states its ordinal and an ordinal cannot be derived from a price | P | BusinessWorld / headtopics record tally | 2026-09-19 |
| PH 10-year government bond yield | ~7.50% (18 Sep) — what the peso's recovery off 62.86 cost domestically | P | Manila Times, 18 Sep | 2026-09-19 |
| Brent crude | **$103.87 — 18 Sep settle**, −0.9% on the day and −1.0% on the week, 4.5% off the $108.75 four-month high set 15 Sep. Prior settle $104.82, implied by the published move | P | CNBC oil prices, 18 Sep (verified via search result) | 2026-09-19 |
| WTI crude | **$100.30 — 18 Sep settle**, −1.6% on the day, flat on the week | P | CNBC oil prices, 18 Sep | 2026-09-19 |
| Brent y/y change | +58.58% | D | derived from the $103.87 settle against a $65.50 year-ago base, itself implied by the last verified pair ($96.28 at +46.99%) | 2026-09-19 |
| Brent Q1 2026 close | $118 from $61 at year open | P | eia.gov Today in Energy | 2026-09-05 |
| IMF global growth 2026 / 2027 | 3.1% / 3.2% | P | IMF WEO April 2026 | 2026-09-05 |
| IMF US growth 2026 / 2027 | 2.4% / 2.0% | P | IMF WEO April 2026 | 2026-09-05 |
| IMF euro-area growth 2026 | 0.7% (from 1.1% in 2025) | P | IMF WEO April 2026 | 2026-09-05 |

## Volatility complex

| Claim | Value | Kind | Source | Last verified |
|---|---|---|---|---|
| Spot VIX | 14.32 (4 Sep close - the last trading day; 5 Sep was a Saturday) | P | Cboe | 2026-09-07 |
| VIX 2026 low | **13.80 — 4 Sep intraday**, just before the payrolls release, then rebounded to close 14.32 | P | market reporting (verified via search result) — **CORRECTED**: 14.18 on 17 Aug was the year's low when this model adopted it, and was superseded on 4 Sep without the model noticing for nine days | 2026-09-13 |
| VIX August low | 14.18 (17 Aug intraday) — the 2026 low *until* 4 Sep, still cited historically | P | CNBC 2026-08-17 | 2026-09-13 |
| VIX 1-month high | 16.82 (2 Sep intraday); the 2 Sep **close** was 16.34 | P | market reporting (verified via search result). Previously carried as 16.80 on 1 Sep; two accounts put the peak on the 2nd, which is coherent with that session's close being the spike | 2026-09-13 |
| Asia Equity vol beta | 1.05 × 0.92 = 0.966 | **E** | ASSUMPTION — Asia Pacific ex-Japan vol ~1.05× the S&P, times ~0.92 for the dividend tilt. Neither leg sourced to a manager document; no published pair found to anchor it | 2026-09-13 |
| Global Technology vol beta | 1.30 | **E** | ASSUMPTION. Cross-check only: Fidelity publishes 3y annualised volatility of 17.23% (USD I Acc, Jun 2026), which implies ~1.30 beta only if S&P realised vol over that window was ~13.3% — plausible, unverified, and not the same quantity (this beta applies to forward implied vol) | 2026-09-13 |
| Covered-call vol factor | JEPQ since-inception annualised σ **13.9%** vs Nasdaq-100 **20.4%** → factor **0.681**; published beta 0.81 | P | J.P. Morgan JEPQ fact sheet, 31 Jul 2026 (verified via search result) — replaces an unsourced 0.68 carried in `vol_beta` since launch | 2026-09-13 |
| VIX Hormuz spike | 16.34 (2 Sep close), retraced to 15.20 then 14.32 | P | market reports | 2026-09-07 |
| 11 Sep session (reversal) | S&P +0.86% to 7,656.98 — first gain in five sessions; WTI settled $100.05, −2.4%; **VIX closed 15.84, −11.21%** — gap closed, and the −11.21% from 15.84 implies a 17.84 prior close, independently corroborating the 10 Sep figure against one outlet that printed "near 17.89"; Nikkei 64,011, KOSPI 6,910 | P | market reporting 2026-09-11/12 (verified via search result) | 2026-09-12 |
| Hormuz diplomacy | Tehran to meet Gulf states in Oman on the Strait (11 Sep) — the reason oil settled down 2.8% | P | oil market reporting 2026-09-11 (verified via search result) | 2026-09-11 |
| Brent full-closure scenario level | $130 | E | the stress row's modelled level, published so the scenario and every note citing it cannot drift | 2026-09-11 |
| VIX latest close | **15.44 on 18 Sep**, +0.13% — back inside the range it broke. Series: 17.10 (14th) · 17.20 (15th) · 16.93 (16th) · 15.42 (17th) · 15.44 (18th) | P | market reporting, corroborated across sessions | 2026-09-19 |
| VIX episode high | **17.84 on 10 Sep**, +8.38%, intraday 18.17 — the break of a 28-session 14–17 range. One outlet also printed 17.47/+6.14% for the same session; both imply the same 16.46 prior close, so 17.84 is carried and the discrepancy recorded | P | two independent searches agreeing | 2026-09-11 |
| 17–18 Sep VIX descriptors | **LEVELS carried, descriptors DISCARDED.** 15.42 and 15.44 are both corroborated, but the reported moves ("nearly 13%", −12.8%) do not chain off a triple-corroborated 16.93 — both would need a ~17.7 prior. The moves are therefore DERIVED (−8.92%, +0.13%) rather than quoted | P/D | arithmetic chain rule | 2026-09-19 |
| VIX futures strip is NOT re-quoted | curve still on its 4 Sep quote date — **15 days**, ninth consecutive day of searching without a fresh strip | — | every source found still echoes the same 4 Sep levels; the curve stays on 4 Sep and the 1.12-point spot divergence is published. **Now bounded rather than merely disclosed**: a check fails once the strip passes one 30-day roll window, because at that point the front contract it was quoted against has settled | 2026-09-19 |
| Cost of that staleness, MEASURED | **−4.97%** | D | re-anchor the bootstrapped curve to the spot of the VIX3M observation date (15.84, 11 Sep), integrate to 3 months, and it reads 17.68 against a published VIX3M of 18.60. Same t=0, same strip, so the residual is the strip's age and nothing else. The sign matters: this model's implied vol is LOW against the market's, so its forecast drawdowns are if anything a touch shallow | 2026-09-19 |
| VIX3M (independent check) | 18.60 with VIX 15.84, 11 Sep close; published IVTS 0.8516 reproduces exactly from the pair | P | thetrading.tools VIX term structure — used ONLY to test the bootstrap, never as an input to it | 2026-09-19 |
| VIX 30-day range / average | 14.18–16.80 / 15.28 | P | Cboe | 2026-09-07 |
| VIX futures strip (levels) | Sep 16.57 · Oct 18.41 · Nov 19.08 · Dec 19.26 | P | VIX term-structure data (verified via search result, not at Cboe directly) | 2026-09-07 |
| VIX quote date | 2026-09-04 (Friday close) | P | the date every VIX level above is quoted at; asserted to be a weekday and not after AS_OF | 2026-09-10 |
| VIX futures maturities | 0.0740 · 0.1699 · 0.2466 · 0.3233 yr | D | derived from the contract settlement rule (Wednesday 30d before the following month's third Friday, plus a 15d window centre) off the quote date; independently re-derived by the verifier | 2026-09-10 |
| Expected PHP depreciation (FX_DRIFT) | 2.0%/yr | E | between long-run relative PPP (3.9 − 2.4 = 1.5pp) and the current print differential (6.1 − 3.4 = 2.7pp); bracket asserted from the model's own inflation inputs | 2026-09-10 |
| Worst-case peso value, ₱1m | ₱744,000 optimised · ₱711,000 baseline | D | the expected max drawdown applied to the OPENING value — the worst case for money invested today, deliberately NOT the low point of the modelled path | 2026-09-10 |
| Long-run VIX anchor | 19.5 | E | historical VIX mean 1990–2025 | 2026-09-05 |
| Variance risk premium | 3.5 vol points | E | implied minus realised, long-run | 2026-09-05 |
| Horizon vol 3M/6M/12M/10Y | 17.20 / 18.26 / 18.82 / 19.43% | D | engine, forward-variance integration over 3 observable contracts (Sep settled 16 Sep and was dropped), maturities derived from the VIX settlement calendar off the 4 Sep quote date. The 3M leg is now cross-checked against VIX3M — see "Cost of that staleness" below | 2026-09-19 |
| Volatility ramp (blend − spot) | 18.88% − 14.32 = +4.56 vol pts | D | engine. **Unchanged this week and deliberately so**: both legs come from the 4 Sep curve, so the ramp cannot move until the strip is re-quoted. The page said "this week it moved" until 2026-09-19; it did not | 2026-09-19 |

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
| **Reader-reproducibility rule** | **every published figure is computed from the figures published beside it**, not from the raw values behind them | Extended 2026-09-20 to the three places it still was not. (1) The **regional blend** was blended on the 1–10 research scale then rescaled, printing a US blend of 3.15 above four reported scores averaging 3.14 — to5() is affine so the two routes agree exactly, until either is rounded, and to5() rounds to 2dp. (2) The **headline drawdowns** were rounded down from the raw value; they matched the reader's route only by luck, the baseline under macro landing 0.006pp from a different tenth. (3) The regional table **displayed** horizons at 1dp against a 2dp blend, so the row did not add up on screen even once the payload did. Earlier instances: peso figures (2026-09-03), ratios (2026-09-10), scenario drawdowns |
| **Feasibility is tested on BOTH routes** | a portfolio is feasible only if it respects the drawdown cap **as computed and as shown** | Each rule alone admits what the other rejects. Raw-only admitted `[25, 30, 25, 20]` at 26.1477 against a 26.17 cap, which PRINTS −26.2 — a reader comparing it to the printed cap reads a breach. Rounded-only admits one genuinely over budget by up to 0.05pp (the 2026-09-03 finding). Surfaced 2026-09-20 when the regional-blend fix moved returns a hundredth and broke the coincidence hiding it |
| Reporting scales | **everything the reader sees is 1–5** — gauge, regional rankings and (from 2026-09-09) the seven driver scores. All three are *researched* on 1–10, the granularity the evidence supports and the scale every note is written against; each note carries its research-scale score | one endpoint-preserving rescale throughout: 1→1, 5.5→3.0 neutral, 10→5. The map is affine and the driver weights sum to 1, so the weighted composite of the reported driver scores **is** the headline gauge — asserted, not assumed |
| Volatility tilt sensitivity | +0.035 ATRPHMM · +0.210 ATRQIAP · 0.000 ATRASEQ · −0.122 ATRGTEC, per vol point of ramp | structural, not a view |
| Horizon blend weights | 3M 10% · 6M 15% · 12M 25% · 10Y 50% | **reweighted 2026-09-08**: the old 15/25/30/30 put 70% on sub-year horizons while its own comment claimed the anchor was dominant, and it was never revisited when the mandate doubled |
| Drawdown budget for the optimiser | baseline max DD less 2.83pp (= 2.0pp at the 5y calibration, scaled by √(T/5)) | holding it flat would have quietly loosened the objective. The cap is published at the precision it is enforced at — it was rounded until 2026-09-08 |
| Single-sleeve concentration cap | 50% | **added 2026-09-09.** Until then the objective had no diversification constraint; it never bound until the Asia fee correction, at which point the optimiser proposed 75% in one fund |
