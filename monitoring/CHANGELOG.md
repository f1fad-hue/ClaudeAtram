# Changelog

Newest first. Every error found gets recorded before it gets fixed.

## 2026-10-27 — v73: review of v72; rolled to Tuesday 27 Oct; KOSPI corrected; A, B, C and D unchanged

At the owner's instruction: debug, code-review and sanity-check; re-research, fact-check
and re-verify the data and math, funds, ETFs, stocks and fees, net 10-year CAGR and
drawdown, the market trend, macro, volatility and regional analyses at 3, 5 and 10
years, and the A-D selections from the 22-fund list; house cleanup.

**Rolled (each cross-checked, each chaining from its previous close):**
- **Peso, 27 Oct**: 64.17, 22 centavos weaker, the first close past 64 and a record for
  a sixth session (Rappler and the Manila Times on BAP data). Year-to-date loss 8.38%.
- **PSEi, 27 Oct**: +2.13% to 5,761.19, its best day since 1 Sep (BusinessWorld; Inquirer).
- **KOSPI, 27 Oct**: +3.09% to 5,638.34, a sidecar on program buying, as Anthropic's IPO
  filing revived the AI trade before SK Hynix reports (Asia Business Daily; Seoul
  Economic Daily; MoneyToday). **Nikkei**: +1.73% to 63,268.32 (TradingKey; CNBC).
- **VIX, 26 Oct**: 18.39, −5.45% (Yahoo's history, Investing.com, Cboe; AD HOC's 18.30
  is the one outlier).
- **Brent and WTI, 26 Oct**: $115.81 (−$0.91) and $101.76 (−$1.51) as Saudi Arabia's
  defence minister, with Turkish and Pakistani officials, met Iran's president; the four
  agreed to keep talking (CNBC; Reuters via Yahoo and Investing.com; Al Jazeera).

**Held:** the 10-year at its 23 Oct official close (FRED and the Fed's H.15 have not
published 26 Oct; the secondary prints run 4.986-5.00%); the VIX futures curve at the
20 Oct settlements (no later strip found); FedWatch at its 26 Oct read; Brent's year-ago
base at 23 Oct 2025 ($65.99), now exactly at its three-day bound - 24 Oct 2025's $65.94
has one source - so the next roll must re-anchor to 27 Oct 2025. No driver, region,
trend or volatility score moved: no new 3- or 5-year evidence, and a rebound session
after a sell-off is not a regime. A, B, C and D, every fund's net return and drawdown,
and every what-if are identical to v72.

**Errors found and fixed:**
- **The 26 Oct KOSPI was the wrong one of two prints** (v69-v72): 5,469.59 (−80.71,
  TokenPost) was carried and the exchange figure, 5,469.47 (−80.83, −1.46%; Korea
  Exchange data via UPI, Asia Business Daily, JoongAng), was set aside as "a feed
  value". Both chain from 5,550.30, so the arithmetic could not choose; the source had
  to, and the wrong one was trusted.
- **"Planned" was a report**: the Asia note said SK Hynix rose "ahead of its planned
  16tn-won special dividend"; the company says it is reviewing shareholder returns and
  has decided nothing. It now says so.
- **A fund figure traced by coincidence**: the 75 in Nasdaq Equity Income's "75%
  Nasdaq-100" benchmark had no input, and from this roll the audit's ±0.5 tolerance
  matched it to Brent's +75.5% y/y, silencing its warning. Verified (ATRAM's fund page,
  uitf.com.ph, the fact sheet) and made an input.
- **A Brent sentence the oil checks misread**: "Brent settled $0.91 lower at $115.81"
  put the change where the checks read the level; caught by two engine checks before
  publishing and reworded.

**House cleanup:** nine CLAIMS rows rolled (USD/PHP, PSEi, the peso's YTD loss, Brent,
WTI, Brent y/y, Nikkei, KOSPI, VIX); two 23 Oct VIX intraday inputs no longer quoted
removed; the README's data line dated.

**Checks:** engine 233/233; independent audit 416/416 (2 standing warnings, both fund
fee notes); page validator 24/24 on the published copy (version 73, payload identical to `model/data.json`); mutations 44/44 caught.

## 2026-10-27 — v72: review of v71; US equities rolled to Monday 26 Oct; A, B, C and D unchanged

At the owner's instruction: debug, code-review and sanity-check; re-research, fact-check
and re-verify the data and math, funds, ETFs, stocks and fees, net 10-year CAGR and
drawdown, market trend, macro, volatility, regional rankings and the A-D selections from
the 22-fund list; house cleanup.

**Rolled (cross-checked):**
- **US equities, 26 Oct** (CNBC's close report, TheStreet, Yahoo): S&P 7,676.77 (+0.70%),
  Nasdaq 26,169.38 (+0.82%), Dow 52,361.58 (+0.28%), as Anthropic's IPO filing lifted
  the AI trade after two weekly losses. All three chain to the cent off 23 Oct.
- **FedWatch, 26 Oct** (FXStreet citing the tool; a futures calculation on CME's method;
  CNBC): an October hike at 9.4% (from 7.2%), a December hike at 79.7% (from 80.5%).
- **Gulf, 26 Oct**: the Houthis claimed new strikes on the East-West pipeline's pumping
  stations and Riyadh's airport; the coalition said it destroyed five missile-storage
  tunnels in Yemen (Reuters); Saudi, Turkish and Pakistani officials held talks in Tehran.

**Held, not guessed:** the 26 Oct VIX close (published figures run from about 18.2 to
19.5, and Cboe's own page contradicts itself), the Brent and WTI settles (only intraday
prints, $114-115 and $101-102), and the 10-year close (only intraday, about 4.98%). Each
stays at its 23 Oct value until the closes agree.

**Re-verified, unchanged:** the peso's 26 Oct close of 63.95 is both the day's high and
its close (Manila Bulletin on BAP data, the Manila Times, Philstar) - a Manila Times
line calling it an intraday record is the same print; the PSEi's 5,641.18; FactSet's
23 Oct figures (29.5% blended growth, 83% beating, 18.7x forward); the Nasdaq Equity
Income target's 0.35% TER (justETF, HL, finanzen); the 1.50% trust fee on the A PHP
classes. A, B, C and D, every fund's net return and every what-if are identical to v71:
index levels do not feed the return model, and no driver or region score moved on one
session.

**Errors found and fixed:**
- **A duplicated dict key, silently resolved** (introduced and caught in this pass): the
  new 23 Oct December baseline went in above the old 22 Oct one under the same name, and
  Python kept the later, so the Monetary note printed the 22nd's 90.0% as the 23rd's. The
  22 Oct reading now has its own name, and a new engine check parses every dict literal
  in the engine and fails on any key typed twice (none in v71).
- **A session move read as another day's**: the volatility note's "the Dow fell 1.23%"
  read the live `dow_chg_pct`, which a roll would have turned into Monday's +0.28% with
  the word "fell" still in front of it. The 23 Oct moves are now their own inputs.
- **"a 8.07% loss"**: the article now follows the number as read aloud.
- **A heading branch that could never run**: the driver heading searched the 10-year
  view, which is neutral by construction, for "near neutral", so its "still below"
  branch was dead; it now searches only the views before the anchor.
- **Missing CLAIMS row**: the 23 Oct session was never registered (v67-v71); it is now,
  beside 26 Oct.

**Checks:** engine 233/233 (one added: no duplicated dict keys); independent audit
414/414 (3 standing warnings); page validator 24/24 on the published copy (version 72, payload identical to `model/data.json`); mutations 44/44 caught.

## 2026-10-27 — v71: every portfolio on 3, 5 and 10-year forecasts

At the owner's instruction: "Update all portfolio based on macroeconomic drivers deep
analysis, market trend deep analysis, regional rankings deep analysis and volatility deep
analysis of 3, 5 and 10yrs forecast. Do the best and recommended approach to reach max
growth 10yrs cagr minus fund fees forecast while controlling the drawdown to minimum to all
portfolios. Do house cleanup." Market data unchanged (26 Oct; US to 23 Oct).

**The three horizons, analysis by analysis** (weights: each view's share of the ten years -
3Y years 1-3 30%, 5Y years 4-5 20%, 10Y years 6-10 50%):
- **Macro drivers**: each driver's 3-year reading is its expected average over years 1-3
  and its 5-year reading over years 4-5, researched year by year: the Fed's September
  medians (4.1% at the end of 2026 and 2027, 3.9% in 2028, 3.6% in 2029, 3.2% long run),
  BSP's inflation path (6.1% / 6.0% / 3.3% for 2026-2028), five-year and 5y5y breakevens,
  the IMF's growth path, long-term EPS forecasts against their record, the CAPE, and the
  Brent curve for December 2027 ($86.46-87.82) and 2029 ($72.32). Monetary 3.5 / 5.0,
  Inflation 3.75 / 5.25, Growth 4.5 / 5.25, Earnings 6.5 / 5.5, Valuation 6.5 / 5.5,
  Volatility 4.5 / 5.5, Geopolitics 3.0 / 5.0; the gauge reads 2.29 now, 2.62 at 3Y, 2.90
  at 5Y, 3.00 at 10Y. Each step sits between the one before it and neutral, by check.
- **Regional ranking**: 3-year / 5-year scores US 5.5 / 6.25, Europe 3.75 / 4.5, Asia
  6.5 / 7.0, Philippines 5.25 / 5.75; 10-year anchors unchanged. Blends (1-5): Asia 3.60,
  US 3.29, Philippines 2.99, Europe 2.46.
- **Market trend**: two scored views. The past year is momentum for year 1 ahead, the past
  3 and 5 years reversal for years 2-5, and each view takes them by the share of its own
  years in each window: 3Y = 3 + ⅓ z(1Y) − ⅔ × 0.5 z(3Y, 5Y); 5Y = 3 − 0.5 z(3Y, 5Y); 10Y
  neutral. The shares are derived from the year windows in the engine, not typed.
- **Volatility**: the curve at 3Y, 5Y and 10Y (19.24 / 19.34 / 19.42%), read on forward vol
  over each view's own years (19.24 / 19.49 / 19.50%).

**The portfolios:** A 5 / 30 / 0 / 20 / 0 / 0 / 20 / 0 / 0 / 25 at 7.23% / −26.6%
(unchanged); **B 5 / 35 / 0 / 5 / 0 / 25 / 30 at 7.23% / −26.3%** (was 10% cash, 10%
Global Technology, 20% Health Care and 25% Infra at 7.19% / −26.0%); C 5 / 50 / 0 / 5 / 0 /
0 / 35 / 0 / 0 / 5 at 7.26% / −26.7%; D 25 / 50 / 5 / 20 at 7.07% / −26.8%. All inside the
−26.97% budget.

**What the regrouping alone does, and what the evidence does.** The trend and volatility
channels are invariant to the regrouping (the trend blend is 3 + 0.1 z(1Y) − 0.2 z(3Y, 5Y)
either way; the forward variances average to the 10-year implied however the years are cut),
so their tilts did not move. Averaged over years 1-5, the year-by-year readings land within
0.15 of v70's five-year readings. What moved B is Monetary: the Fed path above neutral
through 2028 and near it in 2029 gives a ten-year average of 4.80 against 4.75, so the
rates drag shrinks (×0.467 from ×0.50). Rerun with Monetary held at 4.75, the rule picks
10 / 35 / 0 / 10 / 0 / 15 / 30 at 7.20% / −26.1%. B is a near-tie the rule settles, not a
conviction call.

**Errors found and fixed in the rebuild:**
- **One year's input reused for another**: the 3-year notes gave the Fed's median as 4.1%
  "at the end of 2026 and 2027" from the 2026 input alone; traceability passed because the
  number existed. Cross-checked (FRED's FEDTARMD, the FRED blog, MUFG's 4.125% median dot),
  the 2027 median is also 4.1%; it is now its own input (`fed_sep_2027`), and the prose
  joins the two years only while the inputs agree.
- **The Fed's projection path had no listed source on the page**: FRED's FEDTARMD series
  and the FRED blog's September SEP note are added to the sources.
- **Two dated Brent forward quotes failed the Brent prose checks**: December 2027 Brent
  ($86.46 and $87.82, two tables) is now a published input the checks know, dated "on 22
  Oct" beside the figure.
- **The page's trend and driver tables read v70 keys** (`T.view`, `w_mom`, `w_rev`, the
  first horizon taken as the 5-year one) that a third horizon breaks; both now loop over
  the published views, and the driver heading names the first horizon near neutral.

**House cleanup:** the 5/10-year wording replaced in the engine, page, README, CLAIMS and
runbook; the held-out fund results re-run on the new engine (unchanged: US Equity
Opportunity at 1.20% would take 20% of A, 25% of B and 10% of C); a mutant added for the
trend shares (the 3-year view left on v70's 1/5 momentum split).

**Checks:** engine 232/232; independent audit 414/414 (3 standing warnings); page validator
24/24 on the published copy (version 71, payload identical to `model/data.json`); mutations 44/44 caught (one added: the 3-year trend view on v70's split).

## 2026-10-27 — v70: every portfolio on 5 and 10-year forecasts

At the owner's instruction: "Update all portfolio based on macroeconomic drivers deep
analysis, market trend deep analysis, regional rankings deep analysis and volatility deep
analysis of 5 and 10yrs forecast. Do the best and recommended approach to reach max growth
10yrs cagr minus fund fees forecast while controlling the drawdown to minimum to all
portfolios. Do house cleanup." Market data unchanged (26 Oct; US to 23 Oct).

**The two horizons, analysis by analysis** (weights: each view's share of the ten years,
5Y years 1-5 and 10Y years 6-10, half each):
- **Macro drivers**: each driver's 5-year reading is its expected average over years 1-5,
  from medium-term evidence - the Fed's September projections (3.9% at end-2028, 3.6% at
  end-2029, 3.2% long run), five-year breakevens (2.37-2.48%), the IMF's October growth
  path, BSP's 2028 inflation forecast (3.3%), long-term EPS forecasts against their record,
  the CAPE and the Brent curve. Monetary 4.0, Inflation 4.5, Growth 4.75, Earnings 6.0,
  Valuation 6.0, Volatility 5.0, Geopolitics 3.75; the gauge reads 2.29 now, 2.72 at 5Y.
- **Regional ranking**: 5-year scores US 5.75, Europe 4.0, Asia 6.75, Philippines 5.5,
  10-year anchors unchanged.
- **Market trend**: one 5-year score, momentum for its first year and reversal for its
  other four (3 + 0.2 z(1Y) − 0.8 × 0.5 z(3Y, 5Y)); the 10-year anchor neutral.
- **Volatility**: the curve at 5Y and 10Y (19.34 / 19.42%), read on forward vol.

**The portfolios:** A 5 / 30 / 0 / 20 / 0 / 0 / 20 / 0 / 0 / 25 at 7.22% / −26.6%
(unchanged); **B 10 / 35 / 0 / 10 / 0 / 20 / 25 at 7.19% / −26.0%** (was 15% Health Care,
30% Infra, 7.20% / −26.1%); C 5 / 50 / 0 / 5 / 0 / 0 / 35 / 0 / 0 / 5 at 7.25% / −26.7%;
D 25 / 50 / 5 / 20 at 7.06% / −26.8%. All inside the −26.97% budget.

**What the regrouping alone does, and what the evidence does.** Collapsing 1, 3 and 5 years
into one 5-year average reproduces the v69 blend exactly - the trend tilts and the
volatility ramp do not move, and could not. What moved the portfolios is where the
five-year evidence differs from the v69 paths' own 5-year averages: the US 5.75 against
5.9 (the CAPE at 40.7, a Fed above its long run until 2029), Geopolitics 3.75 against 3.3
(a Brent curve near $72 for December 2029), Valuation 6.0 against 7.2.

**Errors found and fixed in the rebuild:**
- **A check that assumed four horizons**: "the horizon blend's long bucket is the mandate
  horizon" required exactly four weights; it now requires the published weights to be the
  horizons themselves, ending on the mandate.
- **A check that a 50/50 split cannot pass**: the audit's "the anchor dominates" took the
  largest weight, which ties at half; it now asks the anchor for at least half.
- **Dated forward oil prices read as undated spot**: the Europe note's December 2029 Brent
  level sat 45 characters from its date; the note now dates the curve first, and the
  forward curve is a published input the Brent checks know.

**House cleanup:** the 1/3/5/10-year wording removed from the engine, page, README and
CLAIMS; the driver table shows the reading now beside its 5- and 10-year readings; the
held-out fund results re-run (US Equity Opportunity at 1.20% would now take 25% of B).

**Checks:** engine 231/231; independent audit 408/408 (3 standing warnings; fewer checks
than v69 because there are fewer horizons to re-derive); page validator 24/24 on the
published copy (version 70, payload identical to `model/data.json`); mutations 43/43 caught
(the driver-path and horizon-weight mutants moved to the 5- and 10-year keys).

## 2026-10-26 — v69: rolled to Monday 26 Oct; review of v68; A, B, C and D unchanged

At the owner's instruction: debug, code-review and sanity-check; re-research and
re-verify the data and math, funds and fees, net 10-year CAGR and drawdown, market
trend, macro, volatility, regional rankings and the selections from the 22-fund list;
house cleanup.

**A, B, C and D are unchanged:** A 7.22% / −26.6% (7.43% / −26.4% on its 10-year view),
B 7.20% / −26.1%, C 7.26% / −26.7%, D 7.07% / −26.8%, all inside the −26.97% budget.
Every driver and regional score is held, and nothing rolled feeds a fund return: the
trend windows end at 30 Sep and the vol curve stays on the 20 Oct strip.

**Rolled:** US closes to Friday 23 Oct (S&P 7623.68, −0.52%; Nasdaq 25955.34, −0.21%; Dow
52215.16, −1.23%; VIX 19.45, +2.21%; 10-year 5.00% on the par curve, 2-year 4.69%,
30-year 5.33%; Brent $116.72, +3.1%, the highest close since 29 April; WTI $103.27);
Asia and Manila to Monday 26 Oct (KOSPI 5469.59, −1.45%; Nikkei 62189.65, −0.80%;
PSEi 5641.18, −1.53%; the peso a record 63.95); the 26 Oct T-bill auction (91-day
6.624%, +63.2bp, the first after BSP's 50bp hike). FactSet's 23 Oct earnings count (83%
beating, Q3 growth 29.5%) and the S&P's forward P/E (18.7×, below its five- and ten-year
averages) enter the earnings and valuation notes. FedWatch stays at 23 Oct's 7.2% /
80.5%: the 26 Oct readings found disagree (79.7% to 81.0% for December).

**Errors found and fixed:**
- **Brent's year-on-year was measured a week off its anniversary.** The one-week bound
  let v67-v68 compare 22 Oct 2026 with 15 Oct 2025 ($61.91) when 22 Oct 2025 was $62.59:
  +82.8% published against +80.8%. The base is now the exact anniversary (23 Oct 2025,
  $65.99, the day the Rosneft and Lukoil sanctions lifted Brent 5.4%), the bound is
  three days, and the three settles reported for it ($65.85, $65.97, $65.99) are kept.
- **The trend section said every 3- and 5-year return ran to 30 Sep.** Health care's run
  to 31 Aug, global technology's to 6 Oct and 1 Sep, and the ACWI table shows no date.
  Each sleeve now carries `trail_date`, the page prints them, and a check bounds their age.
- **v68 left two retired horizons in prose**: the Philippines note's "the 12-month and
  ten-year horizons stay neutral" (now "the 3-, 5- and 10-year"), and the driver-table
  heading "Hostile for a year, near neutral by 5Y", typed, now read from the gauge path.
  Its note's "a hiking cycle that ends by year four" overstated the Monetary path (5.0 at
  five years, not neutral) and now says the tightening is expected to fade.
- **A note that would have printed a fall as a gain.** The volatility note's "reversed
  into a {latest KOSPI move} gain" would have read "−1.45% gain" on this roll; the 23 Oct
  move is a dated input of its own (`kospi_23oct_chg_pct`), as lesson 97 asks.
- **A past catalyst.** The 26 Oct T-bill auction left the catalyst list once it happened;
  US third-quarter GDP and September PCE (29 Oct) joined it.

**House cleanup:** five inputs no longer quoted anywhere removed
(`fed_hike_odds_oct_postcpi`, `vix_22oct_intraday_high`, `wti_nov_final`,
`kospi_21oct_chg_pct`, and the 22 Oct S&P and Nasdaq moves); the BSP's 17 Dec meeting is
quoted again in the Philippines note rather than left as an orphan.

**Checks:** engine 231/231 (new: every dated trailing return on or before the as-of and
under 75 days old; the Brent year-ago bound at three days); independent audit 420/420 (3
standing warnings); page validator 24/24 on the published copy (version 69, payload
identical to `model/data.json`); mutations 43/43 caught.

## 2026-10-26 — v68: every portfolio on 1, 3, 5 and 10-year forecasts

At the owner's instruction: "Update all portfolio based on macroeconomic drivers deep
analysis, market trend deep analysis, regional rankings deep analysis and volatility deep
analysis of 1, 3, 5 and 10yrs forecast. Do the best and recommended approach to reach max
growth 10yrs cagr minus fund fees forecast while controlling the drawdown to minimum to
all portfolios", and "do house cleanup also". Market data unchanged (23 Oct; US to 22 Oct).

**The four horizons, analysis by analysis:**
- **Weights are arithmetic now, not judgement**: each view's share of the ten years it
  governs - 1Y 10% (year 1), 3Y 20% (years 2-3), 5Y 20% (years 4-5), 10Y 50% (6-10).
- **Regional ranking**: 1-year scores are the old 3-, 6- and 12-month views across the year;
  3- and 5-year scores are new, between them and the unchanged 10-year anchors (US 5.0 /
  6.0 / 6.25 / 6.5; Europe 3.0 / 3.75 / 4.25 / 4.5; Asia 5.5 / 6.75 / 7.0 / 7.0;
  Philippines 5.25 / 5.5 / 5.5 / 5.5), each note closing with its reasoning.
- **Macro drivers**: each of the seven has a 1/3/5/10-year path (`DRIVER_PATH`), its
  1-year point the researched score and every path neutral at ten years. The gauge reads
  2.29 / 2.68 / 2.89 / 3.00 across them.
- **Market trend**: the past year as MOMENTUM (3 + z); the past 3 and 5 years, annualised,
  as REVERSAL (3 − 0.5z); 10 years neutral. Trailing returns sourced for all five markets.
- **Volatility**: the curve at 1Y / 3Y / 5Y / 10Y (18.87 / 19.24 / 19.34 / 19.42%), and the
  channel reads each horizon's FORWARD vol over its own years.
- **A is chosen on the 10-year view** (`net_10y`: the analyses at 10 years alone), B on all
  four horizons, C and D on them with Nasdaq Equity Income at 50%.

**The portfolios:** A 5 / 30 / 0 / 20 / 0 / 0 / 20 / 0 / 0 / 25 / 0 at 7.22% / −26.6%
(7.43% / −26.4% on its own view); B 10 / 35 / 0 / 10 / 0 / 15 / 30 at **7.20% / −26.1%**;
C 5 / 50 / 0 / 5 / 0 / 0 / 35 / 0 / 0 / 5 at 7.26% / −26.7%; D 25 / 50 / 5 / 20 at 7.07% /
−26.8%. All inside the −26.97% budget. Were (v67) 6.91 / 6.88 / 6.95 / 6.80%.

**Errors found and fixed:**
- **The rates and energy tilts held a 1-year reading for ten years.** The regional and
  volatility channels averaged their horizons; the drivers' tilts took today's Monetary 2.0
  and Geopolitics 1.5 as permanent. On the ten-year path they read 4.75 and 4.40: rates
  ×0.50 (was ×2.333), energy ×0.367 (was ×1.333). The largest single reason every forecast
  rose about 0.3pp; Global Technology's rates drag went from −0.93pp to −0.20pp.
- **The vol blend would have counted year 1 four times.** The implied figure at 3, 5 and 10
  years is the average from today, so pairing it with weights for years 2-3, 4-5 and 6-10
  re-counts year 1 inside each. It now reads forward vol; the ramp is −0.08 (was −0.45).
- **The held-out fund results were from the old engine.** US Equity Opportunity and Global
  Bond Income were re-run (`model/heldout_sens.py`, A on the 10-year view): at 1.20% US
  Equity Opportunity would take 20% of A, 20% of B and 10% of C (was 10 / 25 / 10).
- **A disputed trailing return.** Schwab's 30 Sep page puts Global Technology at 37.6% and
  22.0% a year over 3 and 5 years, but its one-year 45.0% is 7.6pp above what the monthly
  series compounds to (37.43%). Three trackers agree on 31.4% and 18.8%; Schwab's pair runs
  as `trend_alt` beside Asia's disputed quarter, and nothing moves.
- **The Europe and Philippines notes named retired horizons** ("Held, 3M at 2.25", "6M and
  longer held", "Near horizons held"); reworded.

**House cleanup:** the superseded horizon-weight history (the 2026-09-08 reweighting) cut
from the engine to one line pointing here; dead branches in the trend note's Asia sentence
removed; the README result table, CLAIMS register and disclaimer brought up to the eleven
funds and four horizons.

**Checks:** engine 230/230 (seven new: driver paths, horizon gauges, the 10-year column,
forward vols, the trend's four horizons, the weights' derivation, the 10-year vol ramp);
independent audit 418/418 (3 standing warnings), re-deriving every new figure from typed
sources; page validator 24/24 on the published copy (new: the driver table at four
horizons); mutations 43/43 caught (seven new). One old mutant, Asian Multi-Asset Income
borrowing Asia's full trend tilt, had become a no-op - half of −0.01 rounds to −0.01 - and
now drifts the tilt instead, so it can never pass by rounding.

## 2026-10-23 — v67: rolled to Friday 23 Oct; A, B, C and D unchanged

At the owner's instruction: debug, code-review and sanity-check; re-research and
re-verify the data and math, funds and fees, net 10-year CAGR and drawdown, market
trend, macro, volatility, regional rankings and the selections from the 22-fund list;
house cleanup.

**A, B, C and D are unchanged:** A 7.21% / −26.4% long-run (6.91% / −26.6% macro), B
6.88% / −26.0%, C 6.95% / −26.8%, D 6.80% / −26.4%. Nothing rolled feeds a fund return:
the drivers and regions that do are held, and the trend windows end at 30 Sep.

**Errors found and fixed:**
- **The Report described three portfolios after D joined.** "A, B and C come from one
  rule..." and the cash section ("C 5%") left D out; both now name it (D holds 20% cash).
- **Notes that print a move from the latest input would have flipped its sign.** The Asia,
  earnings and volatility notes printed the KOSPI's and Nikkei's latest moves as "fell
  X%"; rolled to Friday's +0.30% KOSPI they would have read "fell 0.3%". The 22 Oct moves
  are now dated inputs of their own (`kospi_22oct_chg_pct`, `nikkei_22oct_chg_pct`,
  `psei_22oct_chg_pct`, `kospi_21oct_chg_pct`), and the 23 Oct ones are worded as gains
  or losses from the data.
- **A backwards sentence caught in proofreading:** the first draft of the monetary note
  had the 10-year falling "to 5.13% on the 21st - from 4.96%". Fixed before the engine
  ran; the redraft then failed the check that the note lists at least three dated closes
  matching the series, and now lists them day by day.
- **"0.3%"** for a move published at 2dp: now formatted as 0.30%.

**Rolled:**
- **Peso 63.615 (23 Oct)**, 9.5 centavos weaker, a record close after a record 63.62
  intraday (Manila Times, Filipino Times, BAP data); 7.58% loss of purchasing power this
  year. Remolona: BSP intervenes only a little, to limit inflationary swings.
- **PSEi 5,728.63 (−0.88%)** on the hike and the peso (Inquirer, Bloomberg).
- **KOSPI 5,550.30 (+0.30%)**, a 4% intraday fall reversed as SK Hynix rose 4.42% on
  halting Solidigm's IPO review; **Nikkei 62,693.16 (−0.34%)**.
- **10-year 4.96% (22 Oct, par curve)**, −17bp (StockMarketWatch's table; 24/7 Wall St
  citing Treasury's curve) - held back on 23 Oct on market quotes; 2-year 4.65%, 30-year
  5.29%.
- **FedWatch (23 Oct, tool-cited):** October 7.2%, December 80.5%, from 16% and 90%.
- **As-of date 23 Oct** (PH/Asia Friday close; US series at Thursday 22 Oct).

**Verified, unchanged:** Brent $113.17 and the VIX 19.03 (22 Oct); the US closes of the
22nd; the held-out fees. Iran's claim of seven tankers hit is unconfirmed and disputed
by Washington, so the geopolitics note keeps the confirmed 22 Oct facts.

**Not carried:** the 23 Oct US session (trading when this was built). **Next roll:**
Brent's year-ago base (15 Oct 2025) is at its one-week bound against the 22 Oct settle;
the 23 Oct settle needs a newer base.

**House cleanup:** the orphaned `kospi_20oct_close` and `ust_10y_mkt_22oct` and the
superseded `fed_dec_post_selloff_reads` removed. The v66 mutation run never finished
cleanly - the first crashed when a rebuild rewrote the payload it was reading, the
second was stopped once this roll began editing the engine it copies - so the full set,
D's three included, runs on this build.

## 2026-10-23 — v66: Portfolio D (four funds), and all four portfolios head to head

At the owner's instruction: "Make a portfolio D compose 50% atram nasdaq equity income
with atram global tech, atram asia equity and atram peso money market based [on the]
macroeconomics drivers ..., regional rankings ..., volatility ... and market trend
analysis of 3, 6, and 12 months with 10yrs horizon", and then: "Make all portfolios
to be versus".

**Portfolio D: 20 Money Market / 50 Nasdaq Equity Income / 20 Asia / 10 Global
Technology, 6.80% / −26.4%** (long-run 6.91%; vol 13.12%; ret/DD 0.258). C's pin,
C's rule and C's macro inputs, over those four funds only: 43 mixes under the limits,
18 inside the budget, 2 in the tie - the other is 25 / 50 / 5 / 20 at 6.85% / −27.0%,
and D is the shallower. It is the mix C held from v59 to v62, before Global Health Care
joined the search. Against C: 0.15pp a year less for 0.4pp less drawdown. D's search
is C's loop restricted to the four funds, so nothing is measured twice and D can never
beat C (a check holds both).

How D holds up: unchanged under a flat volatility view and the lower Asia trend figure;
with the rates and oil tilts off, Asia's fee higher or the market trend off, it moves to
25 / 50 / 5 / 20; without Asia's re-rating, to 30 / 50 / 0 / 20 (6.75%). Its worst
shortfall against the best four-fund mix under any one alternative is 0.20pp (no Asia
re-rating).

**All four, versus.** The Portfolios tab now opens on A vs B vs C vs D: four donuts in
two rows, one table of who holds what, and a head-to-head table with the best figure in
each row marked - net CAGR, long-run CAGR, drawdown, volatility, return per drawdown,
P1M after ten years and the three stress drawdowns. A "who wins where" card names the
leader on each measure and sets every pair against every other. The strategic-vs-macro
lens covers all four. C and D keep their own sections, without repeating their donuts.

**Checks:** engine 223 (D's limits, its four funds, its rule pick, its re-derivation,
its what-ifs, subset of C); audit 389 (an independent walk over D's four funds rebuilds
D, its tie and its six what-ifs; the README table has a D column; D's CLAIMS row);
validator 23 (four donuts in two rows; the A-B-C-D tables fit a phone; D's own row);
mutations 36 (D holding a fifth fund, D's weights drifting, a D what-if typed).

**Retired with it:** the audit and validator checks that required "nothing left of
Portfolio D" - written for the old review-pick D (retired in v59), now replaced by
checks that the new D is what it claims and that nothing of the old one returned; the
A-to-B legend and the A-vs-B-only headline table and delta card.

## 2026-10-23 — v65: the AI sell-off rolled in; volatility cut to 2.5; allocations unchanged

At the owner's instruction: debug, code-review and sanity-check; re-research and
re-verify the data and math, funds and fees, net 10-year CAGR and drawdown, market
trend, macro, volatility, regional rankings and the selections from the 22-fund list;
house cleanup.

**A, B and C are unchanged:** A 7.21% / −26.4% long-run (6.91% / −26.6% macro), B
6.88% / −26.0%, C 6.95% / −26.8%. Nothing that moves fund returns changed: the
monetary and geopolitics scores, the two that feed the rates and energy tilts, are
held, and the trend windows end at 30 Sep. The held-out sensitivities re-run to the
same weights.

**Errors found and fixed:**
- **The peso's streak count was disputed.** v64 called 22 Oct "its fourth record close
  in a row" (BusinessWorld); Tribune counts the third, because 20 Oct's 63.09 tied the
  19th's. The page now gives no count.
- **"The Fed pricing has barely moved"** was true of the 22 Oct morning read and false by
  that evening: after the Treasury rally, December read 76-80% against the 90% carried.
  The note now says when the 90% was read and records the later range as not carried.
- **A claim with no guard.** Global Allocation's fee note says "none holds it" - true
  today, false the day a roll put it in a pick. A new engine check (217) holds it to the
  picks, and the 1.50% re-run behind it is now in `model/heldout_sens.py`, not only in a
  scratch script.
- **An orphaned input and a stale toll.** The 22 Oct Asian-session Brent move (+1.7%)
  lost its last quote when the settle was carried and is removed. The Dammam airport
  toll was 1 dead; the civil aviation authority raised it to 2 (four dead, ten injured
  across the two sites).

**Rolled to 22 Oct (US):**
- **S&P 7,663.43 (−1.21%), its worst day since July; Nasdaq 26,008.86 (−2.60%); Dow
  52,867.98 (+0.02%)** - Meta's spending plans and Lam Research's guidance sent chip
  stocks down more than 6%. All three chain to the cent.
- **VIX 19.03 (+14.09%)**, intraday 20.30 (Cboe, Yahoo, Volatility Therapy; 16.68 + 2.35).
  Investing.com's 18.84 is not carried: its same-day table has the 10-year at 5.065%.
- **Brent $113.17 (+$4.35, +4.0%)**, the highest close since 4 May, as Aramco evacuated
  Dhahran. WTI $99.47 (+2.39%), a chain within December, so its
  prior is now typed. Brent +82.8% y/y; its 15 Oct 2025 base is at the one-week bound and
  must be re-anchored next roll (DTN implies 22 Oct 2025 at $62.59, one source).
- **Gulf:** four dead and ten injured in Saudi Arabia on 22 Oct; Aramco's first full
  Dhahran evacuation since July.

**Scores:** Volatility & risk appetite **cut 2.75 → 2.5**, undoing the 21 Oct raise,
which rested on a VIX that has since jumped 14%; not lower, as it is still under its
19.5 long run and its 22.31 high of 16 Oct. Gauge 2.30 → 2.29. Every other driver and
region held; their notes now carry the sell-off, the oil break and the Gulf strikes.

**Verified, unchanged:** held-out fees (US Equity Opportunity, Global AI, Global Bond
Income: no new confirmed fee); Nasdaq Equity Income's look-through (31 Aug, still the
latest JPMorgan sheet); Global Technology's (a 30 Sep sheet is listed, but two reads
disagree on its date and country table, so the 31 Aug sheet stays, valid to 30 Oct).

**Not carried:** the 10-year for 22 Oct (market quotes near 4.96%, about −17bp, the
biggest one-day fall since March 2023; no par curve yet); FedWatch on the 23rd (after
the as-of date); the 23 Oct PH, Korea and Japan closes (not published when this was
built).

## 2026-10-22 — v64: review, fact-check and roll; allocations unchanged

At the owner's instruction: debug, code-review and sanity-check; re-research and
re-verify the data and math, funds, ETFs and fees, net 10-year CAGR and drawdown,
market trend, macro, volatility, regional rankings and allocations; house cleanup.

**A, B and C are unchanged:** A 7.21% / −26.4% long-run (6.91% / −26.6% macro), B
6.88% / −26.0%, C 6.95% / −26.8%. Every change below was re-run through the search.

**Errors found and fixed:**
- **Equity Opportunity's trend (MSCI ACWI) was on one source.** The 2026 quarters were
  ETFreplay's ETF figures (−2.21 / 14.17 / 1.14), a table that also printed a Q4 2026
  that cannot exist yet, and up to 1pp off the index. Their cross-check compared
  quarters ending 30 Sep with an iShares year-to-date figure running to 20 Oct, so it
  checked nothing. Now the index's own quarters: Q1 −3.20%, Q2 +14.93% (Aristotle
  Capital; 11.25% for the half), Q3 +1.6% (Maseco, Goldstone; 13.0% year to date, which
  the four compound to). The audit checks both totals. The trend tilt moves 0.08 →
  0.09, Global Technology's by +0.01pp through the shared z-scores; B's feasible count
  is 198,762 (was 198,748).
- **Health Care's trend cited a cross-check that disagrees with everything else.**
  AAII's "20.7% to 31 Aug" is replaced by iShares' own NAV returns to 30 Sep (−1.96%
  September, 5.93% YTD, 16.81% one year); the PortfoliosLab months give −2.03%, 5.79%
  and 16.98%, within 0.2pp. A new audit check holds them there.
- **The fee standard was read two ways.** Global AI is held out because its listings
  disagree; Global Allocation was admitted at 1.20% while DragonFi lists 1.50%. Re-run
  at 1.50%: A, B and C unchanged, since none holds it at either fee. Recorded in its fee
  note and CLAIMS row; the fund stays at the 1.20% two listings agree on.
- **A stale comment** called the 20 Oct 10-year "PROVISIONAL until FRED publishes it"
  after it had been confirmed; the Fed's H.15 now has it at 5.12.

**Rolled:**
- **Peso 63.52 (22 Oct)**, 15.9 centavos weaker, a fourth straight record close after a
  record 63.545 intraday (BusinessWorld, Manila Bulletin, Manila Times). Withheld in v61
  while only Tribune's "shortly after the announcement" figure existed. YTD loss of
  purchasing power 7.45% (was 7.21%). The record count stays 24 as of 11 Sep:
  BusinessWorld calls the 22 Oct close the 35th record of 2026, GMA the 30th.
- **Treasuries to 21 Oct** on the par curve (Forbes): 10-year 5.13% (+1bp), 2-year
  4.81%, 30-year 5.42%; FRED's T10Y2Y of 0.32 is 5.13 − 4.81. Held back in v61 on
  market quotes alone.

**Verified, unchanged:** J.P. Morgan's 2027 US investment-grade 6.1% and global
aggregate 5.3% (its own press release); the six funds repriced to 1.50% on 14 Sep
(Global Technology, Equity Opportunity, Infra, Consumer Trends, Financials, Health
Care); Global Allocation not among them.

**Not carried:** the US session of 22 Oct (still trading when this was built), so the
S&P, VIX and Brent stay at 21 Oct.

**House cleanup:** the unused `product` import, `PIN_UNIV` and the dead `slide_note`
payload field removed; stale comments rewritten; the page's `FA` alias replaced by
`FALL`, the one list of all funds; the `ust_10y_mkt_21oct` and `usdphp_withheld_22oct`
holding fields retired with the points they held.

## 2026-10-22 — v63: A, B and C chosen from the 22-fund ATRAM list

At the owner's instruction: "Update portfolio A from 22 atram list and maximum growth
10yrs net cagr with minimum drawdown. Update portfolio b and c from 22 atram list based
on macroeconomic drivers ... market trend ... regional rankings ... volatility ... of 3,
6, and 12 months with 10yrs horizon." C keeps Nasdaq Equity Income at 50%, and A stays
on the 10-year long-run returns (owner, the same day).

**The universe, from five funds to eleven.** Every fund on the list is searched once its
fees are confirmed: its trust fee on ATRAM's own page or on two current listings that
agree, and its target fund named with a published charge. That is the standard the
owner set for US Equity Opportunity on 21 Oct, applied to every fund.
- **Added (six):** Global Health Care, Global Infra Equity, Global Equity Opportunity,
  Global Consumer Trends, Asian Multi-Asset Income and Global Allocation. All are built
  by `build_fund()` like the others.
- **Held out (eleven), each with what is missing (`list22_held_out`):** US Equity
  Opportunity, Global Bond Income, Global AI, Global Multi-Asset Income, Global Capital
  Accumulation, Equity High Income, Natural Resources, Gold Equity, Global Financials,
  US Multi-Asset Income and Peso Liquid.

**The picks** (macro view; A chosen on the long-run view):

| | Mix | Forecast | Was (v62) |
|---|---|---|---|
| **A** | 5 MM / 35 Nasdaq Income / 5 Global Tech / 20 Health Care / 35 Infra | 7.21% / −26.4% long-run (6.91% / −26.6% macro) | 6.97% / −26.3% long-run |
| **B** | 5 MM / 35 Nasdaq Income / 15 Asia / 35 Health Care / 10 Infra | 6.88% / −26.0% | 6.77% / −26.3% |
| **C** | 5 MM / 50 Nasdaq Income / 10 Asia / 35 Health Care | 6.95% / −26.8% | 6.80% / −26.4% |

Health Care and Infra do the diversifying work: 0.56-0.64 correlated with the two US-tech
sleeves, against 0.88 between those two. Global Technology falls to 5% of A and none of
B or C.

**How each added fund is built** (CLAIMS.md has one row per fund):
- **Fees:** published trust fees and target-fund charges. Asian Multi-Asset Income's
  target charge is an estimate, Schroders' class A figure.
- **Gross:** sector and theme funds are built on J.P. Morgan's 2027 global equity
  figure with no premium, since the LTCMA publishes regions, not sectors. The two
  multi-asset funds are blended from their legs on the LTCMA's 2027 bond figures
  (global aggregate 5.3%, US investment-grade 6.1% as a proxy for Asian credit).
- **Correlations:** from the 21 Oct review's factor model, now in the engine.
  It reproduces the typed five-fund block within 0.01.
- **Market trend:** two new series, global health care (IXJ) and global equity (MSCI
  ACWI). The multi-asset funds carry their equity market's trend, and their regional
  tilt, at their equity share. Global Infra Equity and Global Consumer Trends have no
  sourced series and carry none.
- **Estimates:** volatility betas, rates and energy sensitivities, regional mixes,
  drawdown-k adjustments and stress shocks, all on the funds' mandates and recorded.

**The search, rewritten.** The old universe was every point of a 21^(n-1) grid,
filtered. That is fine at five funds and impossible at eleven, about 30 million points.
- **Engine:** generates the 322,725 limit-respecting mixes directly (the money market
  plus up to four funds) and measures each with the same arithmetic as `summarise()`.
  The six what-ifs, the frontier and the best ratio come out of the same single pass.
  The build takes about 11 seconds.
- **Tie-break:** the rule's order gained a third key, the lower true drawdown, for
  mixes that print the same drawdown and CAGR.
- **Audit:** re-derives everything with its own depth-first search (22 seconds) and
  rebuilds every added correlation pair from the published factor loadings.

**What the held-out funds would do** (`model/heldout_sens.py`, now in the repo):
- **US Equity Opportunity at its listed 1.20%:** 10% of A, 25% of B, 10% of C.
- **US Equity Opportunity at 1.50%:** none of A, 5% of B, 5% of C.
- **Global Bond Income at its listed 0.90%:** 35% / 25% / 10% if its target charges the
  0.69% institutional rate; 30% of A and none of B or C at the 1.59% retail rate.

The page shows both.

**Found on the way**
- **A count check that hung the engine.** v62's second count of the universe walked
  every grid point; over eleven funds that is 8^11. It is now a dynamic programme.
- **"Global Technology: the deepest drawdown"** stopped being true when Global Consumer
  Trends joined at −80.3%. The Report's heading and bullet now state the rank from the
  data. The engine check now asserts only the claim still typed, "the most
  rate-sensitive".
- **Fixed widths everywhere:**
  - the CLAIMS check compared six weights;
  - number words stopped at "six" and "eight";
  - the validator expected three trend markets;
  - the page had six colours.
  All are now derived from the universe. The page has eleven colour slots.
- **Tables that would not fit a phone at eleven columns:** the transmission table and
  the added-funds table are now a row per fund. The correlation matrix is the full
  11 × 11, compact.
- **What-if weights printed as eleven slash-separated numbers** now name the holdings.
- **A's donut** showed its macro-view figure under a "Long-run view" label. A's own
  10-year long-run figure is now printed beneath it.
- **A mutant that would have gone blind.** Global Dividend's regional score is now read
  from its published mix, so typing `gdiv_mix` wrong would have passed. A check now
  requires the two copies to agree.
- **Mutations:** 34, all caught. m20 is now derived from the real weights; m31-m34
  cover the held-out register, equity shares, factor-model pairs and borrowed trends.
- **The Asia re-rating what-if:** with eleven funds, B's and C's forecasts rise
  without the credit (6.89% and 7.00% against 6.88% and 6.95%). The rule takes the
  shallowest mix inside the tie, and the credit changes which mixes are in it.

Engine 216/216, audit 376/376, validator 22/22 on the published copy, mutations 34/34.
Runbook: step 2b (re-check the held-out funds); invariant 1 extended; lessons 86-90.
Not personal advice.

## 2026-10-22 — v62: the four-fund optimiser retired

At the owner's instruction ("Retire the four fund optimi[ser]"). The internal
four-fund optimum, the old Portfolio B, had been off the page since v56, kept "for
its checks". **Nothing the page shows changes**: A, B and C are 25/30/0/25/20,
30/35/10/25/0 and 20/50/20/10/0 at 6.72%, 6.77% and 6.80%, as in v61.

**Removed.** From the engine: the four-fund enumeration and its feasible set, the
four-fund B and pinned C, the strict-maximum disclosure, the 50%-cap
counterfactual, the Global Technology stub and the tech-sleeve gap, the four-fund
what-ifs and frontier, the four-fund best ratio, and the 5% per-fund floor that
only that rule used. From the payload (about 8.7KB): `optimized`, `pinned`,
`best_ratio`, `stub`, `tech_gap`, `min_sleeve`, `cap_counterfactual`, `what_if`,
`frontier` and `dd_model.optimized_k`. The engine run takes under a second.

**Kept.** The 20/30/25/25 baseline, off the page, as the budget's reference: the
−27.17% budget is its macro drawdown less 2.83pp. A new check rebuilds the budget
from the printed baseline.

**Moved to what the page shows.** The checks on shared machinery now test A, B and
C instead of the four-fund optimum. These cover the zero-shock scenario row, every
scenario and headline drawdown rebuilt from its printed row and published k, each
k as the ex-cash average of its funds, the peso figures, the budget on the column
each pick was chosen on, the what-if helper rebuilding the live B and C, and
diversification. New checks:
- the universe count rebuilt a second way (2,065 mixes);
- every universe frontier point efficient, and B on it;
- the best ratio rebuilt;
- the Asia fee column against its published stress.

The Report's typed Global Technology claims are now tested across all five funds.
Engine 213/213 (was 227), audit 289/289 (was 306), and the mutation set has 30
entries. m2, m5, m6 and m8 were replaced by universe equivalents, and m29 and m30
were added.

**Found on the way**
- **The page's Asia fee stress was typed.** The What-ifs sentence reads
  `universe.what_if.asia_fee_hi.stress_pp`, but only the four-fund what-ifs carried
  it, so the page has shown a typed "0.25pp" fallback since v56. The universe
  what-if now publishes it, and the audit ties it to the column.
- **A number that traced by coincidence.** The bull-case row's "$65" oil passed the
  every-number-traces check only because a 65% weight sat in the four-fund
  frontier. It is now an input (`brent_disinflation`).
- **Two what-if conventions.** The retired helper re-derived the budget on each
  alternative column. The universe what-ifs the page shows hold it at the live
  27.17%, which is also how A is chosen. On 22 Oct the convention decides three of
  the six B answers (vol flat, drags neutral, no re-rating), because 21 mixes sit
  in B's 0.05pp band. The page's convention is kept and now stated in the engine.
- **A new mutant was a no-op.** The first m5 moved 5pp into cash from "the largest
  fund other than the pin". On 22 Oct that fund was cash itself, so the harness
  reported MISSED for a check that works (lesson 80 again). It now never draws from
  cash or the pin, and asserts the mutant differs.
- Three checks were dropped, not moved:
  - "B beats the baseline on return per drawdown" was a fact, not an invariant.
  - "B trails the baseline past the tie only when the baseline breaks the budget":
    the baseline always breaks the budget by construction, so it reduced to the
    budget itself.
  - The disputed Asia quarter's effect on B and C: the page states it from the
    data.
- README: "the same mix the old four-fund C held" dropped. Runbook: step 2 states
  the one budget; lesson 39 names `WHAT_IF_UNIV`; a "100." that rendered as a list
  item was re-wrapped; lessons 83-85 added. CLAIMS: the drawdown k, budget,
  selection rule, floor, cap, frontier and Asia re-rating rows updated. The k row
  had read "A, C and D".

Not personal advice.

## 2026-10-22 — v61: rolled to 22 Oct; BSP's jumbo hike; Gulf escalation; allocations unchanged

Rolled to the Philippine and Asian close of Thursday 22 Oct and the US close of
Wednesday 21 Oct. **A, B and C do not move** (25/30/0/25/20, 30/35/10/25/0,
20/50/20/10/0 at 6.72%, 6.77%, 6.80%): every driver and region score was held, so
no fund forecast changed.

**Rolled (two or more sources unless noted)**
- **BSP +50bp to 5.50%** on 22 Oct, a fourth straight hike and the first half-point
  since February 2023, against a poll in which 20 of 22 expected 25bp; corridor
  5.00-6.00%; next meeting 17 Dec. The BSP catalyst is replaced by the 26 Oct T-bill
  auction, the first after the hike. The Bank of Korea held at 3.00%.
- US, 21 Oct: S&P 7,757.17 (+0.58%, a third straight gain), Nasdaq 26,702.86
  (+1.05%), Dow 52,856.09 (+0.69%); VIX **16.68** (−3.64%), a third close below the
  long run; Brent **$108.82** (+3 cents; Investing.com's 110.15 was intraday); WTI
  **December $97.15** (−0.68%), the front month since November expired at $101.79.
- Asia, 22 Oct: KOSPI **5,533.77** (−3.52%) as chips sold (SK Hynix −5.48%, Samsung
  −4.02%); Nikkei **62,907.84** (−2.65%; a Reuters-based headline's −2.40% does not
  reproduce); PSEi **5,779.73** (−0.72%), ending a five-session rally.
- FedWatch: October hike **16%**, December **90%** (FXStreet 22 Oct 09:12 GMT citing
  the tool), replacing the 16 Oct pair as its five-day bound expired.
- Geopolitics: the US ordered diplomats out of Saudi Arabia after Houthi strikes
  killed three; the New York Times reports US and Israeli strike plans for after the
  midterms. **Held at 1.5** (volume still near 14 mb/d; 1.0 kept for full closure).
  Volatility **held at 2.75** (VIX lower, but Asia sold off and the Gulf escalated).

**Not carried, recorded:** the 22 Oct peso close (63.52 "shortly after the
announcement" vs a 63.545 record intraday; the 21 Oct 63.361 stays); the 10-year for
21 Oct (market quotes ~5.13%, no par curve yet); a 21 Oct VIX futures strip (only a
single-source front-month 18.35), so the vol curve stays at the 20 Oct settlements.

**Errors found and fixed**
- **A date check pointed the wrong way.** The 22-fund review check required the
  review to be dated on or after the as-of date, so it failed the moment the data
  rolled past the day it was run. It now requires the review not to post-date the
  data and to be within 14 days.
- **False precision on the page:** the Report printed FedWatch as "16.0%" and "90.0%";
  odds now print at the reading's own precision.
- **A December WTI prior was a session price.** The $98.28 carried for December on 20
  Oct does not chain to the 21 Oct report ("fell 67 cents to $97.15"); the prior is
  now implied across the roll, as the model's rule says.
- **Stale runbook rules:** "hold all four funds at 5% or more", "no single-fund cap"
  and invariant 1 ("all four funds appear in both portfolios") described the
  pre-v56 model. Rewritten for the one rule over the universe.
- **The page title counted funds** ("Peso Four-Fund Macro Desk", over five funds). It
  is now "ATRAM Peso Macro Desk", which does not go stale when the list changes.

**Confirmed:** Global Dividend's Y-Acc-USD OCF of 1.04% (Investing.com, Cbonds,
Endowus). The money market's interest-rate note is now bound to BSP's rate.

**House cleanup:** the four-fund optimiser (off the page, ~8.6KB of payload, read by
24 engine checks) is kept for now and flagged; retiring it means re-pointing those
checks at the universe and is a change of its own.

Verification: engine 227/227, audit 306/306, validator 22/22 on the published copy,
mutation harness 28/28.

## 2026-10-21 — v60: the list count stated as 22 from 24

The owner confirmed the list: 22 funds, down from 24, with the ATRAM Long Term and
Medium Term Peso Bond funds removed. The page now says "down from 24", and an engine
check requires the arithmetic (22 + the two removed = 24) instead of the looser
"more than the original review's 22". No figure moves. Engine 227/227, audit
304/304, validator 22/22 on the published copy.

## 2026-10-21 — v59: the peso bond funds removed; nothing left of Portfolio D

At the owner's instruction: "Remove from the lists and portfolio allocations the atram
long term and medium term peso bond", and "No more portfolio d".

**The universe is five funds**: Peso Money Market, Nasdaq Equity Income, Asia Equity,
Global Technology and Global Dividend (2,065 mixes within the review's limits). The
same rule re-chose all three:

| | Weights (MM / NQ Inc / Asia / Tech / Gl Div) | Macro view | With the bond fund (v58) |
|---|---|---|---|
| **A** (long-run) | 25 / 30 / 0 / 25 / 20 | 6.72% / −26.4%, 0.255 | 7.13% / −25.8% |
| **B** (macro) | 30 / 35 / 10 / 25 / 0 | 6.77% / −26.3%, 0.257 | 7.12% / −25.7% |
| **C** (NQ Inc 50%) | 20 / 50 / 20 / 10 / 0 | 6.80% / −26.4%, 0.258 | 7.08% / −25.6% |

The bond fund earned 6.16% at 5.8% volatility; without it the drawdown budget is met
with 20-30% cash instead, which costs about 0.35pp a year. C is now the same mix as
the internal four-fund pin: Global Dividend does not enter it.

- **Engine:** the Long Term Peso Bond's spec, inputs (the PH curve, fee, mandate,
  volatility estimate), correlation row, volatility sensitivity, stress shocks,
  look-through, its what-if and its five checks are gone, as is the review's
  best-worst-case record that held 35% of it. The four-fund what-ifs no longer carry
  A and D re-measurements (the universe what-ifs do). The Medium Term Peso Bond was
  never in the engine; it is gone from the review model's list.
- **No more Portfolio D:** the page had shown only A, B and C since v55, but the payload
  key was still `portfolio_d` and the code still said D throughout. Now `portfolio_b`,
  `universe` (was `six`), `b_k` (was `d_k`), `useq_w_b_*` (was `useq_w_d_*`); engine
  names `PB_W`, `UNIV`, `CORR_U`, `ADD_FUNDS`; page ids `donutB`, `pblede`, `pbnote`,
  `pbtab`, `addfunds`. The audit fails if the key, a D label or a D id comes back.
- **The review model, re-run without either bond fund** (its 11 screened funds, money
  market 0.58%, and the page's −27.17% budget - it had carried −27.27%, a budget from
  before the 2027 roll): its long-run pick is 15 MM / 35 Nasdaq Inc / 15 Global Tech /
  10 Global Dividend / 25 **Global Health Care** at 7.06% / −26.3%. Global Health Care
  is not one of this page's funds, so A cannot match it; the page says so. US Equity
  Opportunity at 1.20%: 25% of A, 20% of B, 15% of C; at 1.50%: none of A, 10% of B, 5%
  of C. The list is 22 funds.
- **Page:** the Report's cash section is now "Cash, the only buffer"; the bond what-if,
  the bond slide, its role, look-through and build-up row, and the "35% of B sits in
  one Philippine bond fund" warning are gone; fund counts ("five funds", "2,065
  portfolios") are read from the payload rather than typed "six". Fixed on the way:
  Global Dividend's correlations were read from matrix row 5, which no longer exists
  (now by id); the trend note's Asia clause checked only B's forecast and read "B's 10%
  and C's 20% ... is"; the US Equity Opportunity sentence could print "none of A and
  10% of B".
- **Sources:** four that only supported the bond fund are removed (290 remain).
- **Checks:** engine 227 (bond checks out; a check that no bond fund is left); audit
  G2/G4 rewritten for any fund count (304); validator rows 3, 13, 16, 17 and 22 read
  the fund count from the payload and fail on a bond slide or a D key; mutation
  harness 28/28 (new: the `portfolio_d` key back, a bond fund back in the ids, the bond
  what-if back, A claiming the review's mix).

Research since v57: no new closes (US markets still open at 19:00 UTC). Brent traded
near $110 on the 21st and the 10-year near 5.09% intraday; neither is carried.

## 2026-10-21 — v58: Nasdaq Equity Income's unit class stated

The owner confirmed the holding is the **A PHP unit class** of ATRAM Nasdaq Equity
Income. That is the class the model already priced (1.50% trust fee incl. distribution
fee + 0.35% target-fund TER), so no figure moves; the fee note and the claims row now
name the class, and the D classes' 0.50% is recorded as not held. Engine 231/231, audit
309/309, validator 22/22 on the published copy.

## 2026-10-21 — Scrub v57: money-market fee corrected, Hormuz volume and the curve rolled, B moves on the tie's edge

A full debug, review and fact-check pass at the owner's request. US markets were still
open (17:00 UTC), so the roll is to the 20 Oct US close and the 21 Oct Asian close.

**Errors found and fixed**
- **Money-market fee stale for years (data).** ATRPHMM carried 0.71% "all-in" from a
  superseded KIIDS (trustee ~0.70%). The current KIIDS has 0.57% trustee + 0.01% other
  as a share of average daily NAV; uitf.com.ph and GCash list the trust fee at 0.50%
  p.a. Now 0.58%, carried as components like Asia Equity's. Every portfolio holds 5% of
  it, so every forecast rises about 0.01pp.
- **B moved on the tie's edge (consequence, not a defect).** The fee lifted 5 / 25 / 0 /
  35 / 30 / 5 to 7.138% raw, so the 0.05pp band now starts at 7.088% and v56's B (5 / 20
  / 0 / 35 / 35 / 5, 7.084%) falls 0.004pp outside it. The rule now picks **5 / 20 / 5 /
  35 / 35 / 0 — 7.12% / −25.7%**, 5% Asia Equity in place of 5% Global Dividend. A
  (7.13% / −25.8%) is unchanged; C is unchanged in weights, 7.08% / −25.6%.
- **An engine check asserted a fact about the inputs (runbook 74, again).** "Both Hormuz
  measures are published" required a 20-50% volume loss; Kpler's new week puts it at
  18% and the check failed on a true input. It now requires both measures as fractions
  of their own baselines, and quoted.
- **Page text that was true by luck:** the trend note said "none of A, B or C holds
  Asia Equity" (B now does; the reason is read from the weights); "0.276 → 0.277, 0%
  better" (a gain under 1% now gets a decimal); "C ... with 0.1pp less drawdown: the
  price of holding half the portfolio in one fund" (the clause now follows the signs);
  the US Equity Opportunity sentence used B's 1.50%-fee weight for C; "35% in any one
  and 5% cash" read the floor as a share (now "at least 5%"); the Report's rule steps
  read the tie from the retired four-fund key; "The oil price follows the first
  [volume]" is false now that volume recovered and Brent did not.
- **CLAIMS misattribution (v56):** the 24-fund row credited US Equity Opportunity's B
  and C shares to "the engine's six-fund rule"; they come from the review model with
  the page's tilts, since the engine does not model that fund.
- **A mutation went silent:** m22 typed B's vol-flat weights as 5 / 25 / 0 / 35 / 35 / 0,
  which the fee correction made the TRUE answer, so it mutated nothing. It is now
  derived from the real weights.

**Rolled (cross-checked, two or more sources)**
- US 2-year **4.79%** and 30-year **5.42%** on the 20 Oct Treasury par curve (were 16 Oct
  session readings, 4.715% and 5.434%); FRED's T10Y2Y 0.33 agrees. Both now carry the
  10-year's official-close basis. The 10-year's 20 Oct **5.12%** is confirmed (two
  par-curve republications, the 23 Sep rule) and no longer provisional.
- Hormuz on volume: Kpler, week to 18 Oct, **about 14 mb/d through the Strait with Gulf
  of Oman transfers, 82% of pre-war (preliminary)**; the Gulf's exports by every route
  above 24 mb/d against 23.3. Not like-for-like with the 9.4 mb/d crude-only week to
  14 Oct, so no trend is drawn. **Geopolitics held at 1.5**: one preliminary week,
  Bloomberg has October to date still below pre-war, attacks continue, the deal is
  stalled, and Brent sits within 1% of its five-month high.
- BSP: BusinessWorld's poll, 20 of 22 expect +25bp to 5.25% on 22 Oct, two +50bp.
- The review model re-run with the corrected fee on its own 13-fund pool: A unchanged
  (7.68%, 14 in the tie). US Equity Opportunity at 1.20%: 30% of A, **30% of B** (was
  25%), 25% of C; at 1.50%: **15% of A** (was 5%), none of B or C. Searched over all 22
  with nothing screened, the review model would add 15% Global AI (fee unverified, a
  near-duplicate of Global Technology), which the review screened out.

**Confirmed unchanged:** Brent $108.79 (20 Oct), VIX 17.31 and VIX3M 18.99, S&P
7,712.57, peso 63.361 (record), PSEi 5,821.51, Nikkei 64,621.24, KOSPI 5,735.66, PH CPI
7.2% (core 4.7%), ECB 2.50% and BoJ 1.25% (holds expected), Nasdaq Equity Income 1.50% +
0.35% (JEPQ UCITS), Global Technology 1.50% + 1.04% (also 1.04% for Y-Acc-USD), Global
Dividend 1.50%, Long Term Peso Bond 1.00%.

**Not carried, recorded:** the PH 5-year for 20 Oct — Manila Bulletin 7.678%, the
Treasury's table (as reported) 7.768%, the day's July 2031 bond at 7.830%. The 15 Oct
curve stays until two sources agree. FedWatch stays at its 16 Oct reading: newer
figures (December ~90%, October under 20%) come from one secondary source each.

**House cleanup:** the dead "D only" tag code and set, a duplicate of `six_feasible`
inside the what-if builder, and ~20 engine comments and check names that still said
"Portfolio D" (the payload was byte-identical before and after). The engine printout now
lists the six-fund what-ifs.

Verification: engine 231/231, audit 309/309, validator 22/22 on the published copy,
mutation harness 26/26 (one added: the money-market fee reverting).

## 2026-10-21 — A, B and C chosen by one rule over six funds; B and C on the macro view

At the owner's instruction: "make portofolio b and c based on macro economics drivers
deep analysis, market trend deep analysis, volatility deep analysis, regional rankings
deep analysis of 3, 6, and 12months with horizon of 10yrs. Make the portfolio a, b and c
to max growth 10yrs net cagr with minimum drawdown."

A and B had been fixed weights carried over from the 22-fund review's own model, and C
was chosen over the four original funds only. Now the engine chooses all three, by the
page's one rule (the best 10-year net CAGR after fees inside the −27.17% budget, then
the lowest drawdown within 0.05pp), over every 5%-step mix of the six funds within the
review's limits: at most 5 funds, 35% in any one (C's pin exempt), at least 5% peso cash
(8,775 mixes).

| | Column | Weights (MM / NQ Inc / Asia / Tech / LT Bond / Gl Div) | Macro view | Feasible / in tie |
|---|---|---|---|---|
| **A** | long-run (`net_base`) | 5 / 25 / 0 / 35 / 35 / 0 (unchanged; the review's pick) | 7.13% / −25.8%, 0.276 | 7,197 / 4 |
| **B** | macro (`net_macro`) | **5 / 20 / 0 / 35 / 35 / 5** (was 5 / 35 / 0 / 20 / 35 / 5) | **7.08% / −25.3%**, 0.280 (was 6.91% / −21.8%) | 7,102 / 12 |
| **C** | macro, Nasdaq Inc at 50% | **5 / 50 / 0 / 20 / 25 / 0** (was 20 / 50 / 20 / 10) | **7.07% / −25.6%**, 0.276 (was 6.78% / −26.4%) | 394 / 3 |

B's macro view is the regional ranking and the market trend, each at 3, 6 and 12 months
blended against the 10-year anchor, the volatility curve, and the seven drivers' rates
and energy tilts - the inputs the Macro and Volatility tabs already show. B gives up
the old pick's stress-test objective (best worst case), which the instruction does not
ask for, and gains 0.17pp a year at 3.5pp more drawdown, still inside the budget.

- **Engine:** `six_grid`, `six_ok`, `six_feasible` and three `pick` calls replace the
  fixed weights; new payload `portfolio_c` and `six` (limits, enumeration size, tie,
  the six-fund macro frontier, and `what_if` with B and C RE-CHOSEN and A re-measured
  on every alternative column, the weaker-bond case included). `portfolio_a` and
  `portfolio_d` gain `column`, `band_n` and `n_feasible`; `portfolio_a.is_review_pick`
  publishes whether A is still the review's mix. C's drawdown coefficient now comes
  from its six-fund weights (1.68158, was the four-fund pin's 1.68125). Engine checks
  231 (from 229): the review's-limits check now covers C, and two are new - each pick
  being the rule's pick on its own column, and every six-fund what-if. The two checks
  that still named "Portfolio D" now say B.
- **Page:** "A vs B · one rule, two views"; the lede, rule steps, feasible-set chart
  (now 8,775 six-fund mixes), C's section, Report what-ifs (now B and C re-chosen,
  with the weight order stated once), trend note and the Funds tab's weights read the
  new payload. Fixed on the way: the frontier sentence read "C ... on it" with no
  verb; the "maximise return alone" corner still described one fund at 35% when the
  cap makes it a mix; section 4 of the Report still promised "the A–B gap" in Global
  Technology, which both now hold at 35%; Global Technology's role still read "held
  small"; the bond note still said "the review that picked B".
- **Docs:** README result table and text; CLAIMS rows for A, B, C and the selection
  rule (the review-only row for B is marked superseded); runbook invariant 78.
- **Checks:** audit section G4 re-derives the enumeration, all three picks (feasible
  counts and tie bands included), C's figures and k, the six-fund frontier and every
  six-fund what-if from the payload alone; the CLAIMS check now requires portfolio
  weights in order, not merely present. Validator rows 16, 17 and 22 test the new
  meanings. Six new mutations (C typed back to the four-fund pin, B on the wrong
  column, a six-fund what-if typed, C's k off the old pin, B's band count, a frontier
  point dropped), all caught.

US Equity Opportunity stays out until its trust fee is confirmed: in this rule it would
take 30% of A, 25% of B and 25% of C at the listed 1.20%, and 5% of A, none of B or C,
at 1.50%.

Verification: engine 231/231, audit 309/309, validator 22/22 on the published copy
(v56, payload identical to the repo), mutation harness 25/25.

## 2026-10-21 — Portfolio D relabelled Portfolio B

At the owner's instruction ("change the label of portfolio d to portfolio b now"): the
review's best-worst-case pick, shown as D since it took the retired four-fund B's place,
is now labelled **B** everywhere on the page. Weights and figures are unchanged:
5 / 35 / 0 / 20 / 35 / 5 at 6.91% / −21.8%.

- **Page:** the A-vs-B donuts, the A / B / C table (now in that order), the headline,
  lens, stress and peso tables, the frontier mark, the Report ("Why B"), the trend note,
  the Volatility tab's portfolio k, and each Funds slide's "Weight in A / B / C".
- **Engine:** the bond fund's correlation note ("the review that picked B") and the
  printout; the payload key stays `portfolio_d`, and the internal four-fund optimum
  stays `optimized`, off the page.
- **Docs:** README's result table is A / B / C; the claims rows are relabelled.
- **Checks:** the validator's label row now requires "Portfolio B" and no "Portfolio D".
  Its first version matched "Portfolio B" case-sensitively, but the page prints the
  donut eyebrow in capitals, so the check failed on a true page; the same blind spot
  meant the previous version's "no Portfolio B" test could not have seen "PORTFOLIO B"
  either. Both directions are case-insensitive now. The audit checks the label in the
  page source and README.

Verification: engine 229/229, audit 296/296 (the claims check now also reads A's row),
validator 22/22 on the published copy, mutation harness 19/19.

## 2026-10-21 — The review list is now 24 funds; A and D held until the one fund that would change them has a confirmed fee

Market data unchanged (21 Oct). The owner sent an updated list of 24 ATRAM funds: the
22 plus **ATRAM US Equity Opportunity** (target: Franklin U.S. Opportunities) and
**ATRAM US Multi-Asset Income** (target: Allianz Income and Growth). Both were added to
the review model and both picks re-run on the same search.

- **US Multi-Asset Income** makes neither pick: 5.64% net after 3.06% of fees.
- **US Equity Opportunity** enters both, and how far depends on its trust fee:

| Its trust fee / target charge | A | D (worst case) |
|---|---|---|
| 1.20% listed / 0.85% clean class | 30% (with 5% Medium Term Peso Bond) | 30% (7.11%) |
| 1.50%, Global Technology's fee since 14 Sep / 0.85% | 5% | 15% (7.05%) |
| 1.20% / 1.81% retail class | 0% — A unchanged | 5% (6.96%) |
| 1.50% / 1.81% | 0% — A unchanged | 0% — a 5% satellite moves inside the tie (6.93%) |

The only fee found, 1.20%, is on a uitf.com.ph page about 17 months old; the share class
the feeder holds is not published. A pick that moves this much on one unconfirmed fee is
not a pick to publish. **At the owner's choice, A and D are held** and the page says why
(a note under the A-vs-D lede, bound to the recorded figures). The engine records the
re-run (`review_list_n`, `useq_*`) and checks it is consistent and that neither held
portfolio contains the unconfirmed fund. Seven sources added.

Next step, when the fund's fact sheet confirms the fee: add US Equity Opportunity (and,
for A at the listed fee, the Medium Term Peso Bond) to the engine and apply the rule.

## 2026-10-21 — Portfolio B retired and D in its place; Portfolio A is now the 22-fund review's highest-return pick

Market data unchanged (21 Oct). At the owner's instruction: "Remove portfolio b and
replace it by portfolio d. Update portfolio A using the 22 fund review pick with max
10yrs net cagr growth minus the fund fees with minimum drawdown."

| | Weights (MM / Nasdaq Inc / Asia / Tech / LT Peso Bond / Global Dividend) | Net 10Y CAGR | Drawdown | Return / DD |
|---|---|---|---|---|
| **A, highest return** (new) | **5 / 25 / 0 / 35 / 35 / 0** | 7.13% | −25.8% | 0.276 |
| C, Nasdaq Income 50% | 20 / 50 / 20 / 10 / 0 / 0 | 6.78% | −26.4% | 0.257 |
| **D, best worst case** (in B's place) | 5 / 35 / 0 / 20 / 35 / 5 | 6.91% | −21.8% | 0.317 |
| *A until today: 20 / 30 / 25 / 25* | | *6.93%* | *−30.0%* | *0.231* |
| *B until today: 20 / 60 / 10 / 10* | | *6.81%* | *−26.5%* | *0.257* |

### 1. How A was chosen

The 22-fund review's own search, re-run today on the corrected inputs (the Global
Dividend fee at 1.50%): about a million mixes of up to 5 funds, at most 35% in any
one, at least 5% peso cash. The rule the owner named: the best base-case 10-year net
CAGR after fees inside the drawdown budget; then, among the 19 mixes within 0.05pp of
it, the lowest drawdown. It did not move from the review's first run: **5% Peso Money
Market / 35% Long Term Peso Bond / 25% Nasdaq Equity Income / 35% Global
Technology**, 7.67% / −25.4% on the review's basis. Like D it is FIXED here and
measured on the page's basis: 7.13% / −25.8%, inside the −27.17% budget.

**Disclosed, not hidden:** A goes OVER the budget (−27.3%) in one of the review's six
stress tests, bonds and tech falling together; D stays inside in all six. A's worst
case is 6.87% against D's 6.91%.

### 2. What changed on the page

- **Portfolios:** A and D side by side where A and B were, one A / C / D table,
  C below. Headline forecast, strategic-vs-macro lens, stress table and peso table
  are A against D. The frontier now marks A, C and D: A and D, from all 22 funds,
  both sit above the four-fund line.
- **Report:** rewritten as "Why D", against A. Every what-if now re-measures A and D
  on its alternative column (they are fixed, so a what-if moves their forecast, not
  their weights) and re-chooses C. New what-if: **the bond fund's own estimates**
  (7.0% gross and 7.5% volatility, the review's case) — A 6.89% / −26.4%, D 6.67% /
  −22.4%. The Global Technology stub and the 50%-cap counterfactual, which described
  B, are gone from the page.
- **Funds:** each slide states the fund's weight in A, C and D; the "D only" tag is
  gone, since A holds the Long Term Peso Bond too.
- **The drawdown budget does not move.** It is still the original 20 / 30 / 25 / 25
  baseline's drawdown less 2.83pp (−27.17%); that baseline is kept only as the
  budget's reference. Measuring the budget from the new A would make it depend on
  the portfolio it is used to judge. Runbook invariant 77.
- The engine still derives the four-fund optimum (B) internally: C is chosen by the
  same rule on the same feasible set, and the checks re-apply it. Nothing on the page
  shows it.

### 3. Found while doing it

- **D's review pick on corrected inputs.** With the Global Dividend fee at 1.50%, the
  review's best-worst-case rule now puts D's 5% in Global Health Care instead of
  Global Dividend (worst case 6.92% against 6.91%, base 7.38% / −21.5% for both —
  inside the tie). D is kept as approved; the swap is offered to the owner, not made.
- **The trend note** said what B and C would hold without the trend; it now gives A's
  and D's re-measured forecasts and C's weights.
- A first validator draft wrote `\b` as a backspace character into its own regex; the
  check that "Portfolio B" is gone could never have failed. Caught on its first run.

### 4. Verification

Engine 228/228 (five new: A and D inside the review's limits, A re-derives, A's
grind-on row, the two picks order as their rules say, every what-if carries A and D).
Audit 295/295 with a new section re-deriving A, every what-if for A and D, and the
weaker-bond case. Validator 22/22, its portfolio rows rewritten for A, C and D and
requiring that no "Portfolio B" remains. Mutation harness 19/19 (two new: A's weights
drift, a D what-if typed).

## 2026-10-21 — The Funds tab shows all six funds; three errors in the Global Dividend fund fixed

Market data unchanged (21 Oct). At the owner's request the Funds tab now covers
every ATRAM fund a portfolio holds: the four of A, B and C, then the Long Term Peso
Bond and Global Dividend funds that Portfolio D adds, each marked "D only".

### 1. What the tab gained

- Six fund slides (was four), each with its return build-up, fees, target and
  Portfolio D weight; the heading and lede count the funds from the payload.
- The side-by-side, fee, look-through and stock-level sections list all six.
- **Long Term Peso Bond** look-through: the fund publishes no holdings, so the PH
  government curve it is priced off is shown (2Y 7.055% · 5Y 7.679% · 10Y 8.016%,
  15 Oct, ADB), with its benchmark, the BPI Philippine Government Bond Index.
- **Global Dividend** look-through: the target fund's top 10 at 30 Sep 2026 (TSMC
  4.0%, Deutsche Boerse, Unilever and Roche 3.4% ...) and its largest countries.

### 2. Errors found, recorded before they were fixed

1. **The fund code was invented.** ATRAM's code for the Global Dividend Feeder Fund
   is **ATRGLDV** (its fund page); the model carried `ATRGDIV`. Renamed everywhere.
   The Long Term Peso Bond has no ATRAM code confirmed, so its slide now prints its
   Bloomberg ticker (PRUPIBA) rather than the model's label `ATRLTPB` as if it
   were ATRAM's.
2. **The trust fee was 0.30pp low.** ATRAM's own page lists 1.50% p.a. including
   distribution fee, and uitf.com.ph has 1.50% for the USD class. The model carried
   1.20% as an ESTIMATE. Now PUBLISHED 1.50%; uitf.com.ph's PHP-class page still
   shows 1.10%, the level before the feeder increases. The page's Method & limits
   now counts one fee estimate, not two.
3. **The regional mix was a guess, and a wrong one.** US 50 / Europe 38 / Asia 12
   was typed as an estimate; the target fund's 30 Sep factsheet puts Germany, France
   and Switzerland alone at 29.7%, and an older listing has the US at 21%. The mix is
   now DERIVED from the country weights (US 24.5 / Europe 60.2 / Asia 15.3), checked
   against them, and published.

**Effect:** Global Dividend net 6.64% → 6.22% (fee −0.30, regional tilt −0.12).
**Portfolio D 6.93% → 6.91%**, drawdown −21.8% unchanged, return per drawdown
0.318 → 0.317 — still 0.10pp above B at 4.7pp less drawdown. The 21 Oct review's
own figures (7.38% / −21.5%) were computed on the 1.20% estimate and are quoted as
recorded.

A first draft of the Global Dividend slide called it "the least US-tech-heavy
equity on this tab" — false beside an Asia fund with no US tech. It now states the
correlations (0.69 / 0.61) against Asia Equity's (0.74 / 0.66), compared in the data.

### 3. Verification

Engine 223/223 (three new: all six look-throughs present, the mix reproduces its
country weights, and the two new look-throughs' freshness). Audit 287/287. Validator
22/22, its fund row now requiring six slides and six rows in every fund table.
Mutation harness 17/17 (two new: the mix back to the guess, the fee back to 1.20).

## 2026-10-21 — Roll to Wednesday 21 Oct and the J.P. Morgan 2027 assumptions: the budget now costs B real return, D leads on this page's own basis, and nine errors fixed

Market data as of 21 Oct (Philippine and Asian closes; US series carry Tuesday 20
Oct, their latest close). Review date 21 Oct. Every fund now runs on J.P. Morgan's
2027 long-term capital market assumptions.

| | Weights | Net 10Y CAGR | Drawdown | Return / DD |
|---|---|---|---|---|
| A, baseline | 20 / 30 / 25 / 25 | 6.93% | −30.0% | 0.231 |
| B, optimised | **20 / 60 / 10 / 10** (was 25 / 15 / 55 / 5) | 6.81% | −26.5% | 0.257 |
| C, Nasdaq Income 50% | **20 / 50 / 20 / 10** (was 20 / 50 / 25 / 5) | 6.78% | −26.4% | 0.257 |
| D, 22-fund review pick | 5 / 35 / 0 / 20 + 35 LT Peso Bond + 5 Global Dividend | 6.93% | −21.8% | 0.318 |

### 1. The 2027 assumptions, applied to every fund together

- US large cap 7.5% (from 6.7%), EM equity 7.1% (from 7.8%), global equity 7.5%
  (from 7.0%). The edition is an input (`ltcma_edition`), every gross note names it,
  and the 2026 figures are kept as `_prev`.
- Effect: Nasdaq Equity Income gross 9.36% (was 8.74%), Global Technology 11.80%
  (was 11.00%), Asia Equity 9.60% (was 10.30%). Global Technology is now the
  highest-return sleeve, and the baseline holds 25% of it.
- **B trails the baseline by 0.12pp, outside the 0.05pp tie**, for a drawdown 3.5pp
  shallower. The baseline is outside the budget; B is the best the budget allows.
- **D now returns 6.93% at −21.8%**: 0.12pp above B at 4.7pp less drawdown, level
  with the baseline at 8.2pp less. Its weights are unchanged; the page now measures
  them on the same edition the review used, and says so from the data.

### 2. Errors found, recorded before they were fixed

1. **A fact written as an invariant.** The engine check "B gives up no more CAGR to
   the baseline than the tie band", and the same rule in the audit and validator,
   failed on the 2027 roll — on a fact, not a defect. All three now state the rule
   that is true: B may trail past the tie only when the baseline breaks the budget.
   Runbook invariant 74.
2. **"Inside the tie" was typed, twice.** `#vsbase` and the Report lede said "inside
   the tie" whenever B trailed A, at any size. Both are now banded on the tie, and
   the Headline card no longer says the baseline's tech weight "costs drawdown
   without buying return" when it buys 0.12pp. The validator reads both sentences.
3. **The volatility tilt was taken from the unrounded ramp.** −0.454 gave Global
   Technology +0.06 while the page printed −0.45 × −0.122 = +0.05. The ramp is now
   rounded to its published 2dp first; the engine check used Python's banker's
   `round()` where every tilt uses half-up `rnd()`, and the audit allowed 0.011 of
   slack. Both are now exact. Runbook invariant 76; mutation m14.
4. **Asia's ten-year anchor counted the base twice.** Its note cited J.P. Morgan's EM
   assumption "the highest of any equity block" — which IS the Asia fund's base
   return. Anchor 7.5 → 7.0 on the 1–10 research scale, the reason removed; the US
   anchor, which never cited it, holds at 6.5 although its base rose 0.8pp. Runbook
   invariant 75.
5. **D's correlation note was typed** ("0.05–0.14", "about 0.35"). The review recorded
   0.37. Both figures are now bound to `CORR_D` and `pd_review_stress_corr`. Mutation m15.
6. **D's note read the bond fund as `weights[4]`** — position, not identity. It is now
   found by id.
7. **D's note typed the edition** ("measured on J.P. Morgan's 2026 assumptions …
   the 2027 edition the review used is not yet rolled in"), stale the moment this
   roll landed. It compares `pd_review_ltcma` with `ltcma_edition` and is worded
   from the comparison.
8. **"One fee estimate left" and "four named funds" were typed in the markup** after
   D brought a second estimate (the Global Dividend trust fee) and two more funds.
   Both are now counted from the payload ("Two fee estimates", "six").
9. **Small defects:** the Volatility tab printed "The latest close is 0.0% above the
   curve's own spot" at a fresh quote; the Funds slides printed "(-15)" with a hyphen
   for a minus; the Report printed "a 11% gain". A −0.0 volatility tilt is now 0.0.
   D's added funds carry no market-trend tilt, and the page now says so.

### 3. Market roll

- **VIX 20 Oct RESOLVED at 17.31** (−6.13%) by three sources. The single source's
  17.60 that was withheld on the 20th was wrong.
- **Volatility curve re-quoted** at the 20 Oct Cboe settlements, Nov 18.49 · Dec
  18.70; the October contract settled on the 21st. January was not found as a
  settlement and is not carried. Against the 20 Oct VIX3M of 18.99 the curve reads
  −3.66% (the 5 Oct strip it replaces: −4.66%). Blended 19.05, 0.45 below the long run.
- **10-year:** 19 Oct confirmed at 5.15 by two more par-curve sources; 20 Oct 5.12
  carried as PROVISIONAL.
- **FedWatch:** still the 16 Oct pair (14.9% October, 88.9% by December), now AT its
  5-day bound. The next roll fails unless a dated reading of the tool is found.
- **Peso** a record 63.361 (intraday 63.373); YTD loss of purchasing power 7.21%.
  **PSEi** 5,821.51, a fifth straight gain.
- **KOSPI** +3.29% to 5,735.66, 18.1% below 2 Oct; **Nikkei** +0.85% to 64,621.24.
- **Geopolitics:** on 21 Oct Iran's speaker Ghalibaf said Tehran would not trust
  Washington until its conditions for reopening the Strait were met; CENTCOM called
  the mine claims false. Brent rose about 1.5% in Asian trading from the $108.79 settle.
- Look-throughs: no 30 Sep fact sheet found for JEPQ or Fidelity Global Technology;
  31 Aug stays (51 days, inside the 60-day bound).

### 4. Scores

- **Volatility & risk appetite 2.5 → 2.75**: the reason for the last cut — the VIX above
  the long run on spot — has reversed for two closes, on a re-quoted curve.
- **Asia 10Y anchor 7.5 → 7.0** (error 4). Every other driver and region held.
- Gauge 2.29 → 2.30.

### 5. House cleanup, a shorter page

- C's own A/B/C table removed: the A–D table in D's section carries every row.
- Catalysts cut to one or two sentences each; the five-week-old postponed Oman talks
  retired (the mechanism stays).
- Driver and region summaries no longer print a 1–10 score beside a 1–5 tile
  ("Held at 2.0" beside 1.44); the research score stays in each note.
- Words per tab at 412px: Report 1,379 → 1,278, Portfolios 827 → 779, Macro 870 → 855.

### 6. Verification

- Engine 220/220. Audit 285/285 against the v50 payload, 0 warnings. Validator 22/22
  on the published copy. Mutation harness 15/15 caught, two new (m14, m15).

## 2026-10-21 — Add Portfolio D: the 22-fund review pick, measured on this page's basis

Market data unchanged: still the Tuesday 20 Oct closes, review date 20 Oct. This
change adds a portfolio; it does not roll the markets.

| | Weights | Net 10Y CAGR | Drawdown | Return / DD |
|---|---|---|---|---|
| A, baseline | 20 / 30 / 25 / 25 | 6.74% | −30.1% | 0.224 |
| B, optimised | 25 / 15 / 55 / 5 | 6.76% | −26.3% | 0.257 |
| C, Nasdaq Income 50% | 20 / 50 / 25 / 5 | 6.54% | −25.6% | 0.255 |
| **D, 22-fund review pick** | **5 / 35 / 0 / 20 + 35 LT Peso Bond + 5 Global Dividend** | **6.53%** | **−22.1%** | **0.295** |

D returns the same as C (inside the 0.05pp tie) with a drawdown 3.5pp shallower.
It also has the best return per unit of drawdown of the four, and the shallowest
drawdown in every stress row: Hormuz −40.7% against C's −46.7%, Hawkish −31.7%
against −36.0%.

### 1. What D is

**Where the weights come from:** the owner's 21 Oct review of all 22 ATRAM funds.
- Basis: J.P. Morgan's 2027 assumptions (published 19 Oct).
- Rule: the best worst-case CAGR across six stress tests, staying inside the
  −27.27% drawdown budget in every one.
- Result: 7.38% / −21.5%, 6.91% at worst.

**The weights are FIXED here, not re-optimised.** The page measures them as it
measures A, B and C:
- the same fees, FX drift, tilts, drawdown rule and stress table;
- the J.P. Morgan 2026 assumptions every other fund here still runs on.

The page quotes both numbers, each with its basis.

**The two added funds are built by `build_fund()`, for D only:**
- **ATRAM Long Term Peso Bond Fund (35%)**
  - Fee: 1.00% trust fee (DragonFi).
  - Mandate: average portfolio life ≤ 7 years.
  - Gross: 7.68%, the PH curve's 5-year point at the 15 Oct close (ADB).
  - Volatility: 5.8%, an estimate.
  - Macro tilt: −0.52. Net 6.16% on the macro view.
- **ATRAM Global Dividend Feeder Fund (5%)**
  - Target: Fidelity Funds – Global Dividend.
  - Fees: 1.04% target OCF (Y-Acc-USD, published) plus 1.20% trust fee (an
    estimate).
  - Gross: J.P. Morgan global equity 7.0% − 0.3% dividend drag.
  - Net 6.15% on the macro view.

### 2. Engine changes

- **Optional universe:** `port_vol / port_ret / port_k / port_dd / summarise /
  run_scenarios` now take an optional universe, so D is computed by the same code
  as A, B and C. Called without one, they are unchanged: A, B and C, every
  what-if and all 211 earlier checks reproduce exactly.
- **Six-fund correlation matrix `CORR_D`:** the four-fund block is unchanged. The
  new pairs come from the review's factor model, which reproduces the four-fund
  pairs (0.88 / 0.66 / 0.74) exactly.
- **Stress shocks:** the five stress rows carry shocks for the two added funds.
  These are estimates and are recorded in CLAIMS.
- **Ten new engine checks (211 → 221):**
  - D's weights are on the 5% grid.
  - `CORR_D` extends `CORR`: same block, symmetric, unit diagonal, positive definite.
  - D's CAGR re-derives from its six funds.
  - D sits inside the budget.
  - D's grind-on row reproduces D.
  - The added funds' fees add up.
  - The PH curve is upward-sloping and dated within 14 days of the as-of date.
  - The bond fund's gross is the curve's 5-year point, and its volatility the
    stated estimate.
  - The review is quoted as recorded, with its drawdown inside the same budget.

### 3. Errors found while adding it, all fixed

1. **D's table overflowed a phone screen** (four columns with full peso values);
   D's column was cut off. Shortened to A–D headers and short labels, with peso
   values in millions. The validator now checks that the table fits its container.
2. **A missing full stop** between the bond fund's mandate and its fee note.
3. **The recorded review drawdown was an orphan input:** the page read it through
   a generic loop. It is now used by a real check: the review's own drawdown must
   sit inside the same budget.

**The review that picked D first corrected its own model** (all recorded in the
owner-facing reply):
- FX coupling did not match this engine.
- Its three correlations were off (0.85 / 0.70 / 0.62).
- Bonds and tech had no rate link.
- The bond fund was priced off the 10-year yield and not its ≤7-year average life.
- The Global Dividend target fee used the UK fund's class.
- Drawdowns were tested only on the raw value.
- The search skipped 9 funds untested.
- Two macro tilts were typed by hand.
- The local check ignored the cash limit.
- One stress matrix was not positive definite.

### 4. Not yet done, and flagged

- **This page is on J.P. Morgan's 2026 assumptions.** The 2027 edition (US large
  cap 7.5%, EM 7.1%) makes the Asia note's "EM equity at 7.8%, the highest of any
  equity block" stale. Rolling it in would change B and C, so it is left for the
  owner's decision.
- **The October VIX future settles today (21 Oct).** The next market roll must
  re-quote the strip or drop October.
- **The 16 Oct FedWatch reading** reaches its 5-day bound with that roll.
- **Unverified inputs:** the Global Dividend trust fee, and the bond fund's own
  yield and duration. Check them on the funds' fact sheets.

### 5. Verification

- **Engine:** 221 / 221 checks.
- **Independent audit:** 278 checks, 0 failures, 0 warnings. A new G2 section
  re-derives D's funds, matrix and both views from the payload, and README and
  CLAIMS rows are checked for D.
- **Validator:** 22 rows; the new row 22 checks D's donut, payload weights, budget
  and the A–D table's fit.
- **Mutation harness:** 13 of 13 caught, including D's weights drifting and the
  bond fund priced off the 10-year.
- **Sources:** 6 added, 259 in all.

Not personal advice.

## 2026-10-20 — Roll to Tuesday 20 Oct: a record peso, Asia's selling resumes, a volatility curve that now reads low, and five errors fixed

All markets are Tuesday 20 Oct closes, except the VIX (19 Oct; 20 Oct withheld)
and the 10-year (19 Oct, provisional). The review date is 20 Oct.

| | Weights | Net 10Y CAGR | Drawdown | Return / DD |
|---|---|---|---|---|
| A, baseline | 20 / 30 / 25 / 25 | 6.74% | −30.1% | 0.224 |
| B, optimised | **25 / 15 / 55 / 5** | 6.76% | −26.3% | 0.257 |
| C, Nasdaq Income 50% | **20 / 50 / 25 / 5** | 6.54% | −25.6% | 0.255 |

Every score held, so no allocation or forecast moved. The gauge is **2.29**.

### 1. Data, 19–20 Oct

- **Equities, 20 Oct**: S&P 7,712.57 (+0.28%), Nasdaq 26,424.82 (−0.02%), Dow
  52,495.88 (+1.02%) on industrial earnings beats, money rotating from tech into
  value; on 19 Oct S&P 7,690.73, Nasdaq 26,430.89, Dow 51,966.03.
- **10-year**: 16 Oct RESOLVED at 5.09% (Fed H.15, FRED). **19 Oct 5.15%,
  provisional** on the Treasury par curve. 20 Oct has only market quotes (5.12%)
  and is not carried.
- **Fed odds**: the 16 Oct FedWatch reading (October 14.9%, December 88.9%) is
  still the latest dated one. Secondary reads on 19–20 Oct agree on the shape,
  not the decimals, and are not carried.
- **VIX**: **18.44 (−7.75%) on 19 Oct**, back below the long-run 19.5. 20 Oct is
  withheld: one source has 17.60. VIX3M 19.60 on 19 Oct.
- **Oil**: Brent 109.55 (19 Oct), then **108.79 (−0.7%) on 20 Oct**, off a
  $111.99 session high, on the Qatar–Pakistan proposal; y/y +75.72%. **November
  WTI expired on 20 Oct at $101.79**; December, the front month from 21 Oct,
  settled at $98.28.
- **Asia**: KOSPI +1.76% to 5,768.01 (19 Oct), then **−3.73% to 5,552.74** (20
  Oct), the lowest close since 7 April and 20.7% below 2 Oct; Nikkei 64,916.70
  then 64,075.42 (−1.30%). **China's Q3 GDP grew 4.5%** against 4.4% expected, on
  exports; September retail sales grew 1.1%.
- **Philippines**: the **peso closed at a record 63.09 on 19 and 20 Oct** (YTD
  loss 6.82%); PSEi 5,806.17, a fourth straight gain. The 19 Oct auction lifted
  bills to **5.992% / 6.229% / 6.444%**, a ninth straight weekly rise; BSP is
  expected to hike to 5.25% on 22 Oct.
- **Hormuz**: the IRGC claims a mined supertanker (17 Oct). On 19 Oct the Houthis
  claimed strikes on Saudi airports and Aramco sites; Riyadh has not confirmed
  them. Kpler counts at least 18 vessels fired on in two weeks. On 20 Oct a
  Qatar–Pakistan compromise was reported and disputed. PortWatch has 4 transits on
  18 Oct. No newer Kpler volume reading than 9.4 mb/d (week to 14 Oct).
- **Funds and fees**: no change found. No fee notice from ATRAM; JEPQ UCITS ongoing
  charges still 0.35%. The 31 Aug look-throughs are 50 days old, inside the 60-day
  bound.

### 2. Scores

Every driver and region held. Volatility stays at **2.5**: the VIX is back under
the long run, but for one session only, and Asia is still selling. Asia's 3M stays
at **4.0** after last week's cut, though the KOSPI fell to a new low for the move.

### 3. The volatility curve now reads low

Re-anchored to the 19 Oct spot, the 5 Oct strip gives 18.19 at three months against
a VIX3M of 19.60: **−7.19%**, inside the ±10% bound but past half of it (−3.04% on
15 Oct). So the model's implied vol and forecast drawdowns run **shallow**. The
superseded 2 Oct board now reads −2.51%: the market has risen to where that board
was. Saxo's 20 Oct brief (October 18.67, November 18.75) points the same way, but
it is one source and covers two contracts, so it is not carried. The latest close
is 18.8% above the strip's spot, under the 20% flag.

**The October contract settles on 21 Oct**, and the "no contract on the strip has
settled" check will fail at the next review by design. That review must re-quote
the strip or drop October. The 16 Oct FedWatch reading reaches its 5-day bound on
the 21st too.

### 4. Errors found and fixed

1. **The page typed the overtaken threshold** ("Past 20%") beside a check holding
   its own 0.20. It is now one engine constant, `STRIP_OVERTAKEN_PCT`, which the
   check uses and the page reads.
2. **The page called a −7.19% gap "a touch shallow".** The wording was signed by
   the residual but not sized. The ±10% bound is now an engine constant
   (`VIX3M_BOUND_PCT`) that the page reads. Past half the bound, the page now says
   the drawdowns run shallow and names the bound.
3. **An unused binding** (`p_vc :=`) in the strip-flag check, left by the last
   roll. Removed.
4. **A new input with no reader** (`wti_next_contract`) was caught by the audit's
   orphan check and removed. The comment already names the contract.
5. **A draft source description would have printed " - +"**, the malformed sign
   the validator rejects. The new insertion guard caught it before it reached the
   page.

Recorded and not carried:

- **KOSPI and Nikkei**: AP's KOSPI 5,539.05 ("−4%") was a pre-close figure, and a
  KuCoin flash's 5,553.08 misses its own points. Investing.com's Nikkei 64,699.50
  for 19 Oct was an intraday snapshot.
- **VIX**: a 17.72 "−2.27" print for 19 Oct was intraday.
- **Philippines**: Context.ph's "364-day 5.278%" is the 35-day cash-management
  bill. A PSEi "+14.98" misses 5,782.70.
- **Brent**: $105.76 is a quote after the news, not a settle.
- **Misdated source**: CNBC's live page dated 19 Oct describes 20 Oct's session.

### 5. Verification

- Engine **212 / 212** checks; one new check covers the withheld VIX session.
  Independent audit: **260 checks, 0 failures, 0 warnings**. Validator: 21 rows,
  all passing on the published copy. Mutation harness: 11 of 11 caught.
- **25 sources added** (253 in all, unique, https). Three existing entries (FRED
  VXVCLS, Investing.com VIX history, Fed H.15) were re-described, not duplicated.
- Every reported move reproduces from the previous close: S&P, Nasdaq (a cent off
  on 19 Oct's points, the prior close's rounding), Dow, Brent, WTI, VIX, KOSPI,
  Nikkei, PSEi, peso and T-bills.

Not personal advice.

## 2026-10-17 — Roll to Friday 16 Oct: a VIX spike past the carried curve, hot producer prices, Brent at a five-month high, and seven errors fixed

All markets are Friday 16 Oct closes; the review date is 17 Oct.

| | Weights | Net 10Y CAGR | Drawdown | Return / DD |
|---|---|---|---|---|
| A, baseline | 20 / 30 / 25 / 25 | 6.74% | −30.1% | 0.224 |
| B, optimised | **25 / 15 / 55 / 5** | 6.76% | −26.3% | 0.257 |
| C, Nasdaq Income 50% | **20 / 50 / 25 / 5** | 6.54% | −25.6% | 0.255 |

No allocation or forecast moved: the two scores that changed (inflation and
volatility) feed the gauge, not the fund tilts. The gauge is **2.29** (was 2.32).

### 1. Data, 15–16 Oct

- **US producer prices (15 Oct)**: +1.3% m/m in September, the largest since
  March 2022, 6.3% y/y, against about 0.5% expected; core +0.5% / 5.0%.
  **Retail sales** +0.8% against 0.3% (August revised to +1.3%; ex-gas +0.2%).
- **Fed odds** fell anyway: October 14.9% on 16 Oct (from 31.6% after the CPI),
  December 88.9%. Chair Warsh gave no signal.
- **10-year**: 14 Oct's 5.19% CONFIRMED by FRED; 15 Oct 5.10%. 16 Oct has only
  market quotes (5.085%) and is not carried. 2-year 4.715%, 30-year 5.434%.
- **Equities, 16 Oct**: S&P 7,659.44 (−1.09%), Nasdaq 26,140.03 (−2.14%), Dow
  52,002.41 — the worst week for the S&P and Nasdaq since June, on AI-debt fears.
- **VIX**: 16.46 (15 Oct), then **19.99 (+21.45%) on 16 Oct**, intraday 22.31.
- **Oil**: Brent 105.92 (15 Oct) then **109.86 (+3.7%), the highest settle since
  19 May**; WTI 97.97 then 101.41. Brent y/y +77.45% on a base moved one day closer
  to the anniversary (61.91, 15 Oct 2025).
- **Asia, 16 Oct**: KOSPI 5,668.05 (+2.05%), still 19.1% below 2 Oct; Nikkei
  65,324.29 (+1.39%). **Peso** 62.985 after a record intraday 63.23; **PSEi**
  5,782.70 (+2.11%).
- **Euro area**: September inflation confirmed at 3.8% (core 2.5%). ECB on 29 Oct
  added to the catalysts; the 16 Oct HICP item retired.
- **Hormuz**: tankers attacked off Al Jubayl, Saudi Arabia; the IRGC says the
  Strait is "closed". On volume, Kpler had crude through Hormuz at **9.4 mb/d** in
  the week to 14 Oct (about 70% of pre-war), up from 8.5.
- **Funds**: no 30 Sep factsheet from J.P. Morgan (JEPQ) or Fidelity yet; the
  31 Aug look-throughs stand at 47 days, inside the 60-day bound.

### 2. Scores

Inflation **2.25 → 2.0** (the PPI confirmed the CPI; Brent at a five-month
high). Volatility **2.75 → 2.5** (VIX above the long-run 19.5 on spot).
Geopolitics **held at 1.5**: the attacks spread, but the volume measure the note
goes by improved. Monetary held at 2.0 (a December hike is still ~89% priced).
Every region held.

### 3. The volatility curve, overtaken

Friday's VIX (19.99) is **28.8% above the 5 Oct strip's own spot** and above its
December future (18.55). The strip still held on 15 Oct — re-anchored it reads
17.93 against that day's VIX3M of 18.49 (−3.04%), and Cboe's October future
settled 17.42 against the strip's 17.46 — but no 16 Oct settlements or VIX3M were
found. The strip stays in the forecasts, and the page now **flags it as overtaken**
whenever the latest close is more than 20% from the curve's spot. A re-quoted
curve near the long run is the Report's "volatility curve" case (B to 20 / 30 /
45 / 5 at 6.78%, inside the tie).

### 4. Errors found and fixed

1. **A check guarded a market fact, not a defect.** "The December future is above
   the latest VIX close" failed the moment the VIX spiked. The page's wording had
   been signed by the data since 15 Oct, so the claim it guarded no longer existed.
   It is replaced by a check that the strip is flagged when the market has moved
   more than 20% from it.
2. **The drawdown calibration was typed into the page and never checked.** k = 1.65,
   the −20% / −33% anchors and their σ and µ, the 0.50 drift coefficient, the
   √(T/5) scaling, κ = 1.5 and the cash sleeve's 100bp / 0.5y floor are now engine
   data the page reads, and a new check confirms k reproduces both anchors (20.1 and
   33.1 against 20 and 33).
3. **Two fee notes quoted figures with no input** (Asia Equity's 1.17% trustee and
   0.01% auditor fees; Fidelity's 0.80% AMC) — the audit's two standing warnings.
   The components are now fields, the notes are built from them, and a check
   requires itemised parts to sum to the fee. The audit runs with no warnings.
4. **The Report would have printed "0.00% below the $109.86 it reached on 16
   October"** once Brent set a new high. It now says "its highest settle since
   19 May".
5. **The settle high moved and had to be re-anchored**: $109.86 (16 Oct) replaces
   November's $108.75, which is kept as the prior, and a new check requires a moved
   high to be above an older, lower prior.
6. **The VIX intraday high (18.17, 10 Sep) no longer bracketed the closes** once
   the VIX closed at 19.99. Moved to 22.31 (16 Oct).
7. **Dead page code**: a no-op string replace and two redundant aliases in the
   gauge sub-line, left by the last roll.

### 5. Verification

- Engine **211 / 211** (three new checks). Independent audit **257 checks, 0
  failures, 0 warnings**. Validator 21 rows, all passing on the published copy.
  Mutation harness 11 of 11 caught.
- **18 sources added** (228 in all, unique, https); one existing entry
  (thetrading.tools) re-described rather than duplicated.
- Every reported move reproduces from the previous close: S&P, Nasdaq (a cent
  off on points, the prior close's rounding), Dow, Brent, WTI, VIX, KOSPI, Nikkei,
  PSEi, peso. AP's week-to-date points land on 9 Oct for the second time.

Not personal advice.

## 2026-10-15 — Roll to Thursday 15 Oct: a stale Global Technology fee, a hot CPI, Asia's crash, a concise page, and fifteen errors fixed

Asian and Philippine data are Thursday 15 Oct closes; US series carry their latest
close, Wednesday 14 Oct (the page says so beside the as-of date).

| | Weights | Net 10Y CAGR | Drawdown | Return / DD |
|---|---|---|---|---|
| A, baseline | 20 / 30 / 25 / 25 | 6.74% (was 6.84%) | −30.1% | 0.224 |
| B, optimised | **25 / 15 / 55 / 5** | 6.76% (was 6.81%) | −26.3% | 0.257 |
| C, Nasdaq Income 50% | **20 / 50 / 25 / 5** | 6.54% (was 6.57%) | −25.6% | 0.255 |

Neither allocation moved. B is now 0.02pp **above** the baseline, inside the tie;
most of A's fall is the fee correction below (Global Technology is 25% of A, 5% of
B). The gauge is **2.32** (was 2.36).

### 1. Fees: the Global Technology trust fee was a month stale

ATRAM raised the ATRGTEC trust fee **from 1.15% to 1.50% on 14 Sep 2026** (A unit
class), with five other feeders moving 1.20% → 1.50%, under an amended Declaration
of Trust; ATRAM's own fund page lists 1.50%. The model carried 1.15%, marked
"verified", for a month. Corrected: the fund's all-in fee is 2.54% and its net
forecast 7.59% (was 7.96% before this roll). Asia Equity Opportunity is not on the
list; Nasdaq Equity Income was already 1.50%. The fee now carries its previous
value and effective date, and the Funds tab states the change.

Knock-on: the Report's typed heading "Global Technology: the highest return, the
smallest weight" became false — Asia Equity (7.64%) now forecasts above it. The
heading is now "the deepest drawdown, the smallest weight", the rank is computed
on the page, and the engine check asserts only the claims still typed.

Every other fee re-checked: Nasdaq Equity Income 1.50% + 0.35% TER (ATRAM page,
DragonFi); Peso Money Market 0.71% all-in (KIIDS); Asia Equity 1.18% + the 1.55%
estimate (the one estimate left, unchanged); Fidelity W-Acc-GBP OCF 1.04%.

### 2. Data, 12–15 Oct

- **US September CPI (14 Oct)**: 3.7% y/y (+0.6% m/m) against a 3.6% Dow Jones
  consensus; core 2.6% (+0.3%) against 2.5%. Gasoline +34.2% y/y. The page had
  quoted a 3.7% consensus — Admiral Markets' preview, not the survey the print
  was measured against.
- **Fed odds**: October 31.6% late on 14 Oct (from 22%; ~50% intraday), December
  89.7%.
- **10-year**: 9 Oct 5.24% CONFIRMED by FRED; 13 Oct 5.21%; 14 Oct 5.19%
  provisional (par curve). 12 Oct had no close (Columbus Day). 2-year 4.808%,
  30-year 5.517% (14 Oct readings).
- **Equities, 14 Oct**: S&P 7,718.94 (−1.11%, worst since July), Nasdaq 26,692.87
  (−1.88%), Dow 51,621.48. AP's week-to-date points put 9 Oct's Dow at 51,654.95,
  six cents below the 51,655.01 carried then.
- **Asia, 15 Oct**: KOSPI 5,554.22 (−7.57%, circuit breaker), 20.7% below 2 Oct;
  Nikkei 64,425.95 (−4.9%). TSMC Q3 profit NT$763.06bn, +68.7%, above consensus.
- **Peso**: record close 63.06 (15 Oct), the first past 63; intraday 63.15. PSEi
  5,663.17. T-bills 5.845 / 6.171 / 6.351% (12 Oct auction).
- **Oil**: Brent 106.65 / 105.69 / 106.06 (12–14 Oct), +70.0% y/y on a re-anchored
  base (62.39, 14 Oct 2025). WTI 95.09.
- **VIX**: 15.21 / 15.27 / 16.87 (12–14 Oct, +10.48% on the CPI). The 5 Oct strip
  is still the curve (10 days old; no fresher settlements found).
- **Hormuz**: a container ship sunk (13 Oct), more than 20 vessels attacked in
  October, Aramco's Dhahran headquarters hit; Kpler crude through Hormuz 8.5 mb/d
  (week to 12 Oct); PortWatch 2 transits (11 Oct).

### 3. Scores

Inflation **2.5 → 2.25** (the print it was held for came in hot on both measures).
Volatility **3.0 → 2.75** (VIX +10.48%, Korean circuit breaker). Geopolitics
**1.75 → 1.5** (ships sinking, Aramco struck, talks stalled). US 3M **4.25 → 4.0**.
Asia 3M **5.0 → 4.0**, 6M **5.5 → 5.0**: the buyers left, not the earnings; 12M
and the ten-year anchor held. Monetary, growth, earnings, valuation, Europe and the
Philippines held. Every driver and region note was rewritten shorter.

### 4. The page, made concise

Visible words per tab: Macro 1,419 → 871, Volatility 1,000 → 399, Portfolios
1,273 → 597, Report 1,779 → 1,373, Funds 1,273 → 1,061 (mostly the four slides).
Page height at 412px falls by 12% (Funds) to 48% (Volatility).

Method detail — the curve construction, the drawdown calibration, the trend
formula and sources, the strategic lens, the scenario assumptions and "why
not maximise return" — moved into collapsed "how" panels; nothing was deleted
that a check reads. Fees moved above the look-through on the Funds tab.

### 5. Errors found and fixed

1. **The peso table printed "+-5,435" in the gain colour** whenever B ended below
   A: the Δ column hard-coded "+" and green. Now signed by value; the validator has
   a new row rejecting malformed signs, NaN or "undefined" anywhere on the page with
   every collapsible open (it fails on the previous commit).
2. **Global Technology's trust fee**, above.
3. **The Report's "highest return" heading**, above.
4. **"~72% US · ~16% Asia · ~12% Europe by index weight"** was typed into the
   look-through with no source. Replaced by the fund's own published country split;
   the note's "less American than its benchmark" went with it.
5. **"Distributes ~9% p.a."** was typed with no model input. Replaced by the TER
   from the payload.
6. **Numbers typed into markup** — 10.5×, 52% / 28%, 0.88 (twice), 1.55% / 1.50%,
   BSP 5.00% — are now bound to the payload.
7. **The gauge sub-line was typed** ("volatility has stepped back but not stood
   down") and went false the day volatility was cut. Now named from the scores.
8. **The volatility chart labelled the curve's 5 Oct spot "spot VIX"** beside a
   tile showing the 14 Oct close. Now "curve spot 15.52 (5 Oct)".
9. **The gap column printed a hyphen** ("-0.53") where every other figure uses a
   minus sign; two tiles hard-coded "+" (latent). All signed by value.
10. **A check pinned stale prose**: "Hormuz is quoted on oil volume" required
    Goldman's 28 Aug 15.5 mb/d in the note, seven weeks after newer readings. It now
    reads the newest dated measure (Kpler, week to 12 Oct); the Report's Hormuz line
    moved with it.
11. **The FX drift bracket paired August PH CPI with US headline** after both
    September prints existed. Now month-matched: 7.2 − 3.7 = 3.5pp.
12. **The stub sentence said Global Technology "costs nothing in expected
    return"** while its 5% floor cost 0.4pp of drawdown. It now states both, and
    that the minimum weight, not the forecast, keeps it in.
13. **The trend windows end 30 Sep and the page did not say so** while the KOSPI
    was 20.7% below its 2 Oct close. The page now flags any move after the window.
14. **The conclusion said B "raises" or "lowers" the CAGR** for differences inside
    the tie. Inside the tie it now says the forecasts are level.
15. **The 25 Sep correction note** sat atop the Report three weeks on, with a
    payload record nothing else used. Retired; the history is here.

### 6. House cleanup

- **98 inputs and 6 derived fields removed** that nothing read — not the engine,
  not the page, not a note (superseded payrolls, PMIs, August CPI components,
  chip-stock moves, earlier Hormuz flows). Payload 111.5 KB → 103.7 KB.
- Dead page code removed (the correction note, a guard for a missing element).
- Look-through notes shortened.
- **36 sources added** for this roll (210 in all, every one https and unique); two
  existing entries (Fed H.15, Investing.com VIX) re-described rather than duplicated.

### 7. Verification

- Engine **208 / 208**. Independent audit **253 checks, 0 failures**, 2 standing
  warnings. Validator **21 rows**, all passing on the published copy (the viewport
  row needs the host). No JavaScript errors; no horizontal scroll at 412px.
- Mutation harness: **11 of 11** caught.
- B's optimum stays flat: the strict maximum, 25 / 10 / 60 / 5, is 0.05pp higher
  for 0.7pp more drawdown. With the fee correction alone and no rescoring, that gap
  rounds to 0.06pp and the rule takes it — the knife-edge is recorded in CLAIMS.

Not personal advice.

## 2026-10-10 — Roll to Friday 9 Oct: a mis-dated volatility curve caught and re-quoted, the trend channel put on realised risk, and thirteen errors fixed

The market snapshot rolls to **Friday 9 Oct**; the review date is 10 Oct.

- **A, baseline**: 20 / 30 / 25 / 25, at 6.84% and −30.1%.
- **B, optimised**: **25 / 15 / 55 / 5**, at 6.81% and −26.3%. It is still 0.03pp
  below the baseline, inside the tie, with a drawdown 3.8pp shallower.
- **C, Nasdaq Income at 50%**: **20 / 50 / 25 / 5**, at 6.57% and −25.6%.
- The gauge is **2.36**; the drivers are unchanged.

Neither allocation moved. The forecasts moved slightly, mostly through the
re-quoted volatility curve, which lowers every fund's volatility and its
volatility tilt.

### 1. The volatility curve was wrong for its date

**What the curve was.** Since 3 Oct the curve had been built on a futures board
labelled "as of 2 October": Oct 18.65, Nov 19.21, Dec 19.35, Jan 20.38.

**What the test found.** It was tested against the market's 3-month index,
VIX3M, re-anchored to that day's spot:

- on 1 Oct it read −0.3%;
- on 6 Oct it read **+4.4%**;
- on 7 Oct it read **+4.16%**.

It fitted the market of the day before its own date.

**Why the old check missed it.** The only VIX3M reading available then was dated
1 Oct, a day before the strip it was testing.

**What explains it.** The VIX fell 6.6% on 2 Oct. Either the board was a 1 Oct
snapshot labelled 2 Oct, or the futures fell about a point that day. Either way,
it priced the wrong market for five days.

**Fixed.**

- **Re-quoted** to the 5 Oct Cboe settlements: Oct 17.46, Nov 18.14, Dec 18.55,
  Jan 19.33. They read −0.87% against VIX3M on 7 Oct and −0.6% on 6 Oct.
- **A new check** requires the VIX3M reading to be dated on or after the strip it
  tests.
- **The comparison now shifts the curve forward in time**, by the days since its
  quote date, not only in level. Until now only the spot was moved.
- **The superseded board is kept** and measured on the same test, so the page
  states its +4.16% error rather than describing it.

**Effect.** Horizon vols fall to 17.58 / 18.42 / 18.92 / 19.44%. The blend falls
to 18.97, against the long-run 19.5. The volatility tilts move to −0.11pp for
Nasdaq Equity Income and +0.06pp for Global Technology.

### 2. The trend channel scored realised returns against implied risk

Each trend z-score divided a trailing return by **implied** volatility. Implied
vol carries the 3.5-point premium options charge over delivered volatility, so
every z was shrunk by about 18%.

**Fixed.** The divisor is now the realised-equivalent level the model already
publishes: 19.44 − 3.5 = 15.94, times each market's beta. The tilts rise to
+0.12 (Nasdaq-100), +0.15 (Asia ex Japan) and +0.16 (global tech). Global tech's
six-month score now reaches the 5.0 cap.

**Neither portfolio's weights move.** The trend lifts B's forecast by 0.11pp and
C's by 0.10pp.

### 3. A check asserted what the data no longer supported

The engine checked that Asia's disputed second quarter "does not move Portfolio B
or C". On the 10 Oct inputs it does move B, to 25 / 15 / 50 / 10 at 6.82%, which
is 0.01pp from B and inside a five-portfolio band.

Asserting invariance on a flat optimum invites someone to loosen the check. It is
replaced by a bound: the disputed input may move neither forecast by more than
the 0.05pp tie. The page now states the move and its size, and the audit
re-derives both.

### 4. Data rolled to 9 Oct, each figure chained to its prior

- **US equities:**
  - 7 Oct: S&P 7,801.77, Dow −0.66%.
  - 8 Oct: S&P 7,765.36; Nasdaq 27,193.34 (−1.25%).
  - 9 Oct: **S&P 7,811.54, Nasdaq 27,366.17, Dow 51,655.01**.
  - Every close chains to the cent. The S&P's record close is still 7,818.93
    (6 Oct).
- **10-year:**
  - **6 Oct resolved at 5.27** now that FRED has published it; 7 Oct 5.28;
    8 Oct 5.22.
  - **9 Oct 5.24 is provisional** (Treasury par curve; FRED publishes on 13 Oct).
  - Intraday **5.365% on 7 Oct**, the highest since April 2002 but still short of
    that year's 5.379%.
  - The 10-year auction cleared at **5.3%**, the highest since November 2000,
    with 80.3% to indirect bidders.
  - The 30-year reached a high of 5.733%.
- **FOMC minutes:** every participant backed the September hike, and most saw
  another by year-end as appropriate.
- **FedWatch:** still carried at 6 Oct (21.6% / 86.2%). The 9 Oct readings
  (16–18%) came with no dated December figure.
- **VIX:** 15.08, then 15.41, then **14.84**.
- **Brent:**
  - **$104.28** (8 Oct, +4%, on tanker attacks and Hurricane Isaias), then
    **$104.72** (9 Oct).
  - **7 Oct withheld:** the reported moves imply about 100.2, against a 101.90
    print in a daily table.
  - The year-ago base is re-anchored to the exact anniversary, $65.22, giving
    **+60.56%**.
- **WTI:** 88.28, then 91.49, then **91.85**.
- **Peso:**
  - A **record-weak close of 62.90 on 8 Oct**, then **62.801** on 9 Oct.
  - The 62.925 intraday trough of 15 Sep stands.
  - YTD loss of purchasing power: 6.39%.
- **PSEi:** a **2026 low of 5,610.39** on 8 Oct, then **5,700.99** on 9 Oct.
- **Nikkei:** **69,030.92** (9 Oct, −0.02%). A daily table's 68,520.50 for 8 Oct
  is not carried, because Nikkei's own published move contradicts it.
- **KOSPI:** **6,625.93** (8 Oct, −2.62%); Korea was shut on 9 Oct.
- **Samsung's preliminary Q3:** **107.4tn won**, a record, against a 106.1tn
  consensus. **TSMC's September revenue:** +54.6% y/y.
- **Michigan sentiment:** **46.3**, near its record low. Five-year inflation
  expectations rose to **3.5%**.
- **US September CPI:** due 14 Oct with a **3.7%** consensus; now a catalyst.
- **Geopolitics:**
  - At least **12 tankers attacked** in the week to 5 Oct, including one off
    Qatar with casualties.
  - The President pledged **no US strike on Iran before the 3 Nov midterms**.
  - PortWatch counted **4 transits**; the queue was **206**.
- **France:** the OAT–Bund spread is at **~140bp**.

### 5. Scores

- **Europe 3M cut 2.5 → 2.25.** French fiscal stress (a ~140bp spread, a 5.4%
  deficit) has joined the energy shock.
- **Every driver is held**, each with its rationale rewritten to the evidence:
  - Monetary: the minutes said what the dots had, and yields ended below their
    peak.
  - Inflation: expectations worsened, but no print arrived; 14 Oct is the test.
  - Growth: sentiment is near its record low, while activity is still in
    expansion.
  - Earnings: Samsung beat narrowly, and the market sold the news.
  - Geopolitics: attacks spread inside the Gulf, while a US strike is off the
    table until 3 Nov.
- The gauge is unchanged at 2.36.

### 6. Funds and stocks

- **Global Technology look-through, upgraded from sector weights to stocks.** It
  now uses Fidelity's 31 Aug factsheet: TSMC 9.1, Microsoft 6.9, Apple 5.4 and six
  more. The note had said no top-10 list was reachable.
  - The tenth holding, 2.1%, is unnamed in the reachable text and is left out
    rather than guessed.
  - The fund is 53.5% US, against its benchmark's 72%. Re-weighting the regional
    score on it is OPEN, because the full country table is not reachable.
- **JEPQ:** 31 Aug is still JPMorgan's latest sheet; re-checked on 10 Oct.
- **The Asia target's holdings:** the newest list is from April, so the gap
  stays declared.

### 7. Errors found, recorded, fixed

1. **The "2 Oct" VIX strip priced 1 Oct's market** (section 1).
2. **The VIX3M comparison shifted the curve in level only,** not in time.
3. **The VIX3M check accepted a reading dated before the strip.**
4. **Trend z-scores used implied volatility** (section 2).
5. **The Report's "provisional" label was hard-wired** to the 23 Sep market print
   (5.104%). It would have printed that beside the 9 Oct close. A provisional
   point now names its own basis, and a check refuses a basis that is a figure.
6. **An invariance check could not survive a flat optimum** (section 3).
7. **The Global Technology look-through note was outdated:** it said no holdings
   list was reachable, and its sector table was dated by when it was read.
8. **The JEPQ note's "checked" date was a week stale.**
9. **"98 positions" would have traced by coincidence** to JPMorgan's 98% crude
   figure. It now has its own input.
10. **A check used the literal 1.22** where the named beta constant now exists.
11. **The trend note's "none of them over the last three" was ambiguous.**
    Reworded.
12. **The top-level README's result table had no check.** The audit now compares
    it with the payload (new section I2).
13. **The volatility lede quoted a provisional close without saying so.** It now
    carries the same flag as the Report.

Caught before commit, not shipped:

- a note sentence ("5.60% on the 9th") that the 10-year listing check read as a
  10-year close;
- an unverified estimate of my own in CLAIMS, removed.

### 8. Verification

- **Engine:** 208/208 checks.
- **Independent audit:** 247 checks, 0 failures. It has a new README-drift
  section, a VIX3M date rule, and the time-shifted VIX3M re-derivation.
- **Mutation tests:** 11 of 11 caught. Three are new: a VIX3M reading dated
  before the strip, trend sigma moved back onto implied volatility, and B's CAGR
  drifting.
- **Validator:** 19/20 locally; the viewport row passes only on the published
  copy.

## 2026-10-07 — Roll to Tuesday 6 Oct, a market-trend channel, one selection rule for every portfolio, and fourteen errors fixed

The market snapshot rolls to **Tuesday 6 Oct**; the review date is 7 Oct. The owner
asked for three portfolios on a ten-year horizon:

- a baseline;
- an optimised portfolio built on macro sentiment, volatility, **market trend** and
  regional rankings at 3, 6 and 12 months with the 10-year anchor;
- a donut with Nasdaq Equity Income at 50%.

All three are to be picked by "the best and recommended approach to reach max growth
... while controlling the drawdown to minimum". The results:

- **A, baseline**: 20 / 30 / 25 / 25, at 6.84% and −30.2%.
- **B, optimised**: **25 / 15 / 55 / 5**, at 6.81% and −26.4%. It was
  25 / 10 / 60 / 5; **the rule change moved it, not the data**.
- **C**: **20 / 50 / 25 / 5**, at 6.60% and −25.7%, unchanged.
- The gauge is **2.36**.

### 1. One selection rule for every portfolio (owner's instruction)

The 2026-09-29 finding is closed. B took the strict maximum while C took the
lowest drawdown within 0.05pp of its best, so a difference below the model's
precision decided B.

**What changed in the engine.** One function, `pick()`, now chooses every
portfolio: the best CAGR in budget, then the lowest drawdown within 0.05pp. It
chooses:

- B and C;
- the 50%-cap counterfactual;
- the Global Technology stub's counterfactual;
- every what-if, each of which now reports C as well as B.

**The strict maximum stays visible.** It is published beside B as
`optimized.strict`: 25 / 10 / 60 / 5 at 6.86% and −27.1%, so 0.05pp more return
for 0.7pp more drawdown.

**Consequence, stated on the page.** B now forecasts **0.03pp less than the
baseline**: 6.81% against 6.84%, inside the tie. Its drawdown is 3.8pp shallower,
and return per drawdown improves 0.226 → 0.258. Under the strict rule B was 0.02pp
ahead, so the baseline was never meaningfully behind on return. Four passages typed
"better on both axes" or assumed a positive edge:

- the improvement card;
- the "Why not simply maximise return?" paragraph;
- the rationale lede;
- the both-lenses note.

Each is now generated from the numbers.

### 2. A market-trend channel at 3 / 6 / 12 months

**What is measured.** For each equity sleeve, its market's trailing returns to
**30 Sep**:

- the Nasdaq-100, through QQQ;
- MSCI AC Asia ex Japan;
- global technology, through IXN.

**How it is scored.** Each window becomes a z-score against the sleeve's own
long-run drift and volatility. That score maps to 3 + z on 1–5 and is blended
with the regional weights. **The 10Y score is held at 3.0**, because momentum
fades within about a year and partly reverses (Moskowitz, Ooi and Pedersen,
2012). The tilt is (blend − 3) × 0.30, an assumption recorded as one.

**The tilts.** They are +0.10, +0.12 and +0.13pp. **Without the channel neither B
nor C moves**; it lifts B's forecast by 0.09pp and C's by 0.08pp.

**One input is disputed.** Asia's Q2 is +27.7% in Schroders' figure but 25.73%
for AAXJ. It is re-run on the lower figure as `trend_alt`, and neither portfolio
moves.

**Sources are all new.** There are 13 of them. Every quarter is compounded in
code from its months where they are given. The Nasdaq-100's Q2 and Q3 agree with
the index factsheet within 0.01pp.

**Shared betas.** The three market betas (1.22 / 1.05 / 1.30) are now named
constants. The fund volatilities and the trend channel both use them.

**Where it shows.** The page gains a "Market trend" section and a sixth row in
the transmission table. The rationale report gains a "What would change this
view" bullet for it.

### 3. Data rolled to 6 Oct, each figure chained to its prior

- **US equities, 6 Oct:**
  - S&P **7,818.93 (+0.58%), a record** above its August high;
  - Nasdaq **27,599.79 (+0.45%), a record**;
  - Dow **51,521.28 (+0.49%)**.
  - 5 Oct and 6 Oct each chain to the cent.
- **10-year:**
  - 5 Oct **5.31%** (FRED DGS10).
  - **2 Oct resolved at 5.28**: Monday's "+3bp" only fits 5.28.
  - **6 Oct not carried**, because only market-basis quotes exist.
  - **Intraday peak 5.349% on 5 Oct, the highest since April 2002.**
  - The 30-year high moved to 5.69%, also on 5 Oct.
- **FedWatch (6 Oct):** October **21.6%**, December **86.2%**.
- **ISM services:** **54.9**, with prices paid **74.0**.
- **PH CPI (Sep):** **7.2%** against a 6.7% poll; core 4.7%; bottom 30% of
  households 9.0%.
- **PH T-bills (5 Oct):** 5.667 / 5.971 / 6.214%.
- **Peso (6 Oct):** **62.771**, a 6.34% loss this year.
- **PSEi:** 5,743.21 on 5 Oct, then **5,677.12** on 6 Oct.
- **Brent:**
  - **$100.32** (5 Oct, −1.9%).
  - **$100.58** (6 Oct), *recovered*. No settlement story exists; two 7 Oct
    quotes both measure from it. A new check requires two witnesses for any
    recovered settle.
  - Up 55.87% y/y.
- **WTI:** $89.43 (5 Oct). 6 Oct is not carried: two implied settles a cent
  apart.
- **VIX:** 15.52 (5 Oct, +1.4%), then **15.01** (6 Oct, −3.29%).
- **Nikkei:** **70,683.98**, the first close above 70,000 since 1 July.
- **KOSPI:** **6,941.39** (−0.89%).
- **Energy:**
  - Saudi November price to Asia **$5 below**, a six-year low.
  - Petroline at **5.8 mb/d**.
  - A G7 release of **100m barrels** is planned.
- **Hormuz security:**
  - UKMTO: **9 attacks in October by the 6th** against 18 in all of September.
  - The queue off berth is back up to **242**.

### 4. Scores

- **Inflation trajectory 2.75 → 2.5**, on the Philippine print and US services
  prices.
- **Valuation support 8.25 → 8.0**, on records set on a 2002-high discount rate.
- **Philippines 3M and 6M 5.5 → 5.0**: September CPI was the test this note had
  named, and it failed.
- Every other driver and region is held, each with its rationale rewritten to the
  6 Oct evidence. The gauge goes 2.38 → 2.36.

### 5. Errors found, recorded, fixed

1. **The real yield used August CPI** for two days after September's 7.2% was out,
   and the page typed the month ("against August inflation"). Fixed: the payload
   carries the CPI and its month.
2. **The peso slide** typed "August inflation printed 6.1%, a fourth consecutive
   slowdown". It is now a template on the payload.
3. **December FedWatch odds** in the US note had no date. Fixed.
4. **A coincidental trace.** "The poorest 30% of households" traced to an
   unrelated 30. It now has its own input, `ph_cpi_bottom_hh_pct`.
5. **The stub counterfactual tested only the raw drawdown.** FEASIBLE tests both
   the raw and the published one, so the stub could have been measured against a
   portfolio that *prints* over budget. Both are tested now.
6. **The stub counterfactual used the strict maximum.** That compared the stub
   against a rule B no longer uses. Fixed by the rule change.
7. **The 6 Oct inputs had no entries in the sources list.** The page's
   "every number traces to one of these" was false for them. 24 sources are added, and
   FRED's entry now names 2 and 5 Oct.
8. **The top-level README's result table** still showed the 2 Sep build: a 5-year
   horizon, 15 / 45 / 35 / 5, 7.31%. It is replaced with the current three
   portfolios.
9. **The engine's report** printed driver research scores at one decimal (1.75
   showed as "1.8"). This is the defect invariant 56 fixed on the page.
10. **The improvement card** would have printed "+−0.03pp" under "Better on both
    axes at once" once B's edge turned negative. The heading, sign and sentence
    are now conditioned on the data.
11. **"The winner is the one that beats the baseline on both sides at once"** was
    typed in markup and false under the new rule. It is now computed.
12. **The rationale lede** said "a thin return edge" for a negative edge. Now
    conditioned.
13. **Two "1-year" figures** from searches (Nasdaq-100 +34.38%, IXN +58.08%) could
    not be twelve months to 30 Sep on their own monthly series. Not used, and
    recorded in CLAIMS.
14. **Fourteen CLAIMS rows** still carried 2 Oct values the payload had moved past;
    the independent audit flagged each one. All are rolled to 6 Oct with their
    chains.

### 6. Verification

- **Engine:** 205/205 checks.
- **Independent audit:** 237 checks, 0 failures. It has a new section, B1,
  which re-derives every trend figure from the published months. Its section G
  re-derives the one rule for B, C, the strict alternative, the cap
  counterfactual, the stub and all six what-ifs (with C).
- **Mutation tests:** eight deliberate faults, all eight caught.
- **Validator:** two new requirements, the third donut and the trend analysis, so
  it now has 20 rows. They pass 19/20 locally; the 20th, the viewport, is added
  by the host.

## 2026-10-03 — Roll to Friday 2 Oct: fresh VIX curve, Brent across its roll, Monetary up and Growth down, and nine errors fixed

The market snapshot rolls to **Friday 2 Oct**; the review date is 3 Oct. The
allocations do not move:

- B stays **25 / 10 / 60 / 5** (6.78%, −27.2%).
- C stays **20 / 50 / 25 / 5** (6.52%, −25.8%).
- The baseline is 6.76%, −30.3%. The gauge is **2.38**.

### 0. The verification harness was lost and rebuilt

The container was reset between reviews and the scratch harness (independent
audit, requirement validator, dump tool) went with it. The session transcript had
been compacted, so the sources could not be recovered. All three were rebuilt
from scratch:

- **The audit** reads only `model/data.json` and refuses to run if the page's
  embedded payload differs. It re-derives:
  - every fund net from its components;
  - the gauge and the regional blends;
  - the volatility curve, by re-integration;
  - every chain;
  - the full enumeration, feasible set, optimum, near-tie band, Portfolio C, the
    cap counterfactual, all four what-ifs and the efficient frontier.
- **It traces every number in every note to an input** and lists the pairings,
  so a coincidental trace is visible.
- **It fails on any input added since the last commit that nothing reads.**
- **It was proven first against the last committed version:** 173 checks, 0
  failures, matching the old audit's clean result.
- **On the rolled data it runs 182 checks, 0 failures.** Its one warning is a fee
  component quoted from the fund documents.

The validator passes 17/18 locally; the 18th, the viewport tag, is added only by
the host.

### 1. Data rolled to 2 Oct, each figure chained to its prior

- **US equities:**
  - 2 Oct: S&P **7,722.72 (+0.73%)**, Nasdaq **27,190.86 (+1.19%), a record**,
    Dow **51,176.96 (+0.49%)**.
  - The three sessions before are in CLAIMS, every one to the cent.
- **Yields, official closes:**
  - 29 Sep **5.26**, 30 Sep **5.29**, 1 Oct **5.24**.
  - 28 Sep's provisional 5.24 is confirmed by FRED.
  - **2 Oct is withheld**: the candidates are 5.27 and 5.28, and neither is the
    Treasury's own figure.
  - **Intraday peak 5.342% on 1 Oct, the highest since April 2002.**
  - 30-year high 5.632% (30 Sep).
- **Fed odds:** after September payrolls (+29k against 84k, unemployment 4.2%),
  FedWatch has October at **17%**, from 73% on 23 Sep, and December at **66.2%**.
- **Inflation:**
  - August PCE: headline **3.4%** and core **3.0%**, against 3.7% and 3.3%
    expected, partly on a BEA methodology change.
  - Euro-area September flash: **3.8%**, with energy at 18.8%.
  - BSP projects Philippine September CPI at **6.4–7.4%**.
- **VIX:**
  - 28 Sep is **resolved at 16.07**: the next session's −0.2% chains only from it.
  - Then 16.04, 16.34, 16.39 and **15.31 (−6.59%)** on 2 Oct.
- **Brent:**
  - **The front month rolled on 30 Sep**, November to December.
  - 2 Oct settle **$102.25** (December); +0.11% on the week, like for like.
  - **WTI** $91.11.
- **Philippines:** peso **62.535**; PSEi **5,629.03**, a fifth straight loss and a
  2026 low.
- **Asia:**
  - Nikkei **68,309.46**.
  - KOSPI **7,003.74**; Samsung +2.79%, SK Hynix +3.21%.
  - Tankan for large manufacturers **+24**.
- **Hormuz:**
  - Goldman's own Gulf export series is back at **23.3 mb/d**, against its 23.0
    pre-war level.
  - JPMorgan has crude at 98% of pre-war, products at 58%.
  - The queue is down to **147** vessels.

### 2. Expiring inputs re-anchored before their bounds failed

- **VIX futures curve.**
  - Re-quoted: Oct 18.65 · Nov 19.21 · Dec 19.35 · Jan 20.38 (2 Oct). The 4 Sep
    curve was one day from its 30-day stop.
  - One source, so it was tested against VIX3M, which it never saw: **18.54
    against 18.58, −0.22%.**
  - The blend moves 18.88 → **19.40**, so the vol tilts shrink to −0.02pp
    (Nasdaq Equity Income) and +0.01pp (Global Technology).
- **Brent y/y base.** Now **$64.53 (3 Oct 2025)**, one day off the anniversary
  and like for like: December was the front month on both dates.
- **FedWatch.** Re-sourced from the tool itself (CNBC citing it, 2 Oct).
- **JEPQ holdings.**
  - Refreshed to the **31 August** fact sheet; the July sheet had reached 64
    days against the 60-day bound.
  - Tesla in, Lam Research out.
  - The July sector weight is dropped rather than shown beside August rows.

### 3. Scores

- **Monetary policy 1.75 → 2.0**, half of the 23 Sep cut. Both tests the note
  named came in soft and October odds fell to 17%. Only half comes back because
  the long end did not follow.
- **Growth momentum 4.25 → 4.0.** The 23 Sep raise is reversed, as the catalyst
  list said a weak payrolls print would do.
- **Held:** the other five drivers and all four regions.
  - Geopolitics is held because the volume facts improved and the security facts
    worsened, in the same week.

The Monetary raise moves the rates scale from ×2.5 to ×2.333 and lifts every
equity fund's net. **Neither portfolio moves.**

### 4. Errors found and fixed

1. **The page printed January as December.** `vix_fut_dec` was the strip's last
   contract by position, which became January when January joined. The page
   printed "December future 20.38" and "prices 20.38 by December". It is now
   selected by label: 19.35.
2. **Scores shown at the wrong precision.** The Report printed Geopolitics &
   energy as "scored 1.8", and the driver cards printed research scores of
   1.75, 2.75 and 8.25 as 1.8, 2.8 and 8.3. Scores now print at the precision
   they are set.
3. **A Brent comparison across a contract roll.** "Below the $108.75 high" set
   December against November's settle high. `brent_off_high_pct` is now derived
   only within one contract; otherwise the page names the contract the high
   belongs to.
4. **A stale superlative typed into the page.** The Report read "its highest
   since 2007" while the peak moved to a 2002 high. It is now bound to
   `ust_10y_peak_since`.
5. **A mislabelled source.** The sources list called the JEPQ sheet "30 June
   2026" while the look-through used 31 July.
6. **A typed figure in a scenario.** "Hawkish repricing" said the Fed "hikes into
   a 4.1% unemployment rate". It is now bound to the input (4.2%).
7. **A fund note on the previous auction.** The Peso Money Market gross-return
   note quoted the **21 Sep** auction a week after the 28 Sep rates were rolled
   in. It traced only because `ph_tbill_prev` held the old rates. It is now
   bound to the live auction.
8. **Coincidental traces.** The Europe note's "up from 0.7%" (April's IMF figure)
   and the Monetary note's "16 of 18" matched unrelated inputs. Both now have
   their own input: `imf_ea_2026_apr`, and `fed_dots_any_more`, derived.
9. **CLAIMS rows stale before this roll:**
   - worst-case peso values: ₱744k / ₱711k against the page's ₱728k / ₱697k;
   - horizon vols: the old curve's figures;
   - the energy scale: ×1.333 since the 29 Sep raise made it ×1.25;
   - the vessel-count drop: "~93%" where PortWatch's 1 against 85 is 99%;
   - the Asia fund's gap note said only 2023 holdings were reachable, where an
     aggregator now shows 30 April 2026. That is still past the 60-day bound,
     so it stays a gap.

New engine checks:

- every Brent roll must carry the new contract's prior, and only rolls may;
- the curve's spot must be the carried close on its own quote date;
- the latest VIX close may equal the curve's date, never precede it.

The engine passes 193/193.

### 5. Open

- **Portfolio B's selection rule is still the owner's call.** Four portfolios sit
  within 0.05pp of its 6.78%. C's rule would give 25 / 15 / 55 / 5 at 6.73% /
  −26.5%.
- **Philippine September CPI on 6 Oct.** BSP's range sits above August's 6.1%.
  The PH region and the Inflation driver are held until the print.
- **The 2 Oct 10-year** needs a Treasury figure to resolve between 5.27 and 5.28.
- **The euro-area flash** is final on 16 Oct.
- **The harness** lives outside the repo by design. It was lost once; committing
  it is the owner's choice.

## 2026-09-29 — Roll to Monday 28 Sep, Geopolitics raised on volume, and Portfolio B's optimum found not sharp

The market snapshot rolls to **Monday 28 Sep**; the review date is 29 Sep. The
allocations do not move:

- B stays **25 / 10 / 60 / 5** (6.76%, −27.1%).
- C stays **20 / 50 / 25 / 5** (6.46%, −25.7%).
- The baseline is 6.72%, −30.1%.
- The gauge is **2.38**.

### 1. Data rolled to 28 Sep, each figure chained to its prior

- **US equities:**
  - S&P **7,683.69 (−0.77%)**.
  - Nasdaq **26,820.38 (−0.92%)**.
  - Dow **51,481.51 (−0.67%, −347.11)**, which chains to the cent.
- **US yields:**
  - 10-year **5.24%**. This is the official close but **provisional**: only one
    par-curve source has it. Only the latest point may be provisional.
  - The intraday peak moved to **5.25%**; the 24 Sep 5.223% is kept, dated.
  - 30-year **5.57%**, its highest since 2004. 2-year **4.93%**.
- **Brent** settled at **$105.28, +0.92%** (+0.96, chained both ways), after trading
  as high as **$108.83** on the rejection headline. It sits 3.19% below the $108.75
  settle high and is +58.15% y/y.
- **WTI** settled at **$92.60, +0.21%**.
- **Philippines:**
  - Peso **62.545**, 8 centavos weaker; 6.00% YTD loss.
  - PSEi **5,788.87, −0.64%**.
  - T-bills **5.535 / 5.862 / 6.115%**, +10.4 / +4.1 / +7.2bp.
- **Asia:**
  - Nikkei **65,877.62, −0.73%**, after touching 67,035.
  - KOSPI **6,889.74, −2.70%** on its return from Chuseok, with Samsung −5.43% and
    SK Hynix −5.05%.
- **Hormuz queue:** **262 and 233** on the 27th and 28th, the lowest in the series.
  It is published as a range, not scored.
- **FedWatch:**
  - Two secondary reads disagree, **64.2% and 72.3%**. They are recorded as a dated
    range; neither is the tool itself.
  - The 23 Sep 73.0 is at its five-day bound.
- **VIX 28 Sep withheld.**
  - 16.07 (+8.07%) and 16.30 (+9.62%) both reproduce from 14.87, and each has one
    source. That is the situation that published a wrong close on 25 Sep.
  - 14.87 (25 Sep) stays the latest carried close. The note says Monday was up
    either way.

### 2. Geopolitics & energy raised 1.5 → 1.75

The note says to score the Strait on volume. The volume data turned:

- Middle East crude exports hit **12.8 mb/d** in September, the most since the war
  began (Kpler).
- Hormuz flows are running toward **7.4 mb/d** under escort.
- Saudi exports are **5.3–6.0 mb/d**, up from 2.4–3.4 in August.
- The East–West pipeline resumed exports at **~3.5 mb/d** on 28 Sep.

The 26 Sep draft was withdrawn when Trump rejected Iran's plan. On 28 Sep the market
tested that headline: Brent traded to $108.83 and settled only +0.92%.

The score stops at 1.75 because:

- regional exports are still ~6 mb/d below February's 18.8;
- the Strait is escorted, not open;
- there is no deal.

Both portfolios were re-optimised on the new score, and neither moves.

### 3. Errors found and fixed

- **An untraceable intraday high.** The Geopolitics note's "$108.23 intraday on
  24 Sep" had no input behind it. The engine carried one "session high" field, which
  the 28 Sep roll overwrote with $108.83. The audit's trace check caught it.
  - Session highs are now a dated record, `brent_session_highs`.
  - A check requires each one to sit on a series date and at or above that day's
    settle.
- **Brent's reported moves lived only in prose.** They are now an input,
  `brent_reported_moves` (23, 24, 25 and 28 Sep).
  - A check requires every one to reproduce from the previous settle.
  - A second check requires the latest settle to carry one.
- **Saudi August exports were overstated.** The range read 3.1–3.4 mb/d, but
  Kpler's own August figure is **2.446**. It now reads **2.4–3.4**.
- **The 30-year high check rejected a true reading.** It required the high to be
  strictly **above** the reading, so it failed the day the reading *was* the high.
  It is now `>=`, and it still fails a reading above the high.
- **The KOSPI had no chain check.** Its point and percent moves are now both
  reproduced from the pre-holiday close.
- **Stale CLAIMS rows.** Brent, Brent y/y, USD/PHP, the 2-year and the 10-year still
  read 25 Sep; the audit failed all five. The Asia re-rating row still quoted the
  what-if as 40/15/5/40 at 6.32%; on the rolled data it is **25/30/25/20 at 6.33%**.

### 4. Finding: Portfolio B's optimum is not sharp, and B and C use different rules

- **B** takes the single best CAGR inside the budget.
- **C** takes the lowest drawdown within 0.05pp of its best, because a difference
  smaller than the model's own rounding is not worth more drawdown.

Applied to B's own candidates:

- **five** portfolios sit within 0.05pp of B's 6.76%;
- C's rule would pick **25 / 15 / 55 / 5 at 6.71% / −26.3%**;
- that gives up 0.05pp of return for 0.8pp less drawdown.

Every what-if is flat too. Without the Asia re-rating credit, **22** portfolios sit
within 0.05pp of the optimum.

Both results are true under their stated rules. So this is a design inconsistency,
not a false statement, and the choice of rule is the owner's. The page now
publishes the band beside B (Portfolio tab) and beside the Asia what-if (Report). An
engine check requires the band function to reproduce Portfolio C from C's own
candidates. **B is not changed** pending that decision.

### 5. Bounds at their edge on the next roll

- **Brent y/y base:** 22 Sep 2025 is six days off the anniversary today. A 29 Sep
  settle is seven days off, the last that passes; from 30 Sep it fails, so a base
  nearer 30 Sep–2 Oct 2025 must be sourced first.
- **FedWatch 73.0:** it is five days old. Re-source it from the tool or retire it.
- **VIX strip:** it is 25 days old. The hard stop fires at 30, about 4 Oct.
- **10-year 28 Sep:** provisional, and needs a second par-curve source.

## 2026-09-28 — Staleness sweep: stale IMF, euro inflation and payrolls, coincidental traces, and the weekend's rejection

The market snapshot is still Friday 25 Sep; this pass swept every claim by age, then
re-checked the week-old ones. The allocations do not move: B stays **25 / 10 / 60 / 5**
and C stays **20 / 50 / 25 / 5**.

### 1. Stale inputs found and corrected

- **The 25 Sep VIX close published in v41 was wrong.**
  - v41 had **14.85 (−5.24%)**, from one unattributed search summary. Three sources
    give **14.87, −0.80 / −5.11%**, day range 14.68–15.94: Portfolio Terminal,
    PC Thematic and Zacks.
  - Both pairs reproduce from Thursday's 15.67, so the chain check could not tell
    them apart. It tests consistency, not truth. The number of agreeing sources and
    the points descriptor settled it.
- **IMF.** The engine, the Europe note and the Report carried the **April** WEO for
  2½ months after the **July update** superseded it.
  - Global 3.1 / 3.2 → **3.0 / 3.4**.
  - US 2.4 / 2.0 → **2.3 / 2.2**.
  - Euro area 0.7 → **0.9** (2027: 1.2).
  - Advanced economies 1.8 / 1.7 → **1.7 / 1.8**.
  - The Report's "0.7%" was typed into the HTML, where no check could see it. It is
    now bound to the payload.
- **Euro-area August inflation.** The engine held the 3.3% flash; the final (17 Sep)
  was **3.2%**. The note's "excluding energy 2.2%" had no input behind it and is
  replaced by Eurostat's energy contribution (+1.29pp).
- **US payrolls.**
  - July's first print (−23k) was kept for three weeks after the 4 Sep revision to
    **+21k**.
  - An unsourced "12-month average 31,000", equal to June's revised figure and read
    by nothing, was removed.
- **Register rows with impossible provenance.**
  - The Fed funds row cited the 29 Jul statement and a 5 Sep verification for a
    16 Sep hike.
  - The "September FOMC vote" row was stamped verified before the vote.
  - Both are now sourced to 16 Sep (12–0).
- **Refreshed with their sources:**
  - Nasdaq-100 forward P/E, 22.4× as of 25 Sep. A 25× July reading was a different
    date and basis.
  - PH core inflation (August, 4.1%).
  - BSP: no meeting since 27 Aug; the next is 22 Oct, now a catalyst.
  - Hormuz queue, extended to 26 Sep (357–443, oscillating). The "one daily snapshot
    time" claim was false: the briefs stamp different hours.

### 2. Figures that traced only by coincidence

The trace check matched a prose number to *any* input with the same value, so a
dozen figures passed while pairing with unrelated fields:

| Figure in the note | What it matched |
|---|---|
| fuel oil +52% | Asia EPS growth |
| core "from 2.5%" | the ECB rate |
| shelter "from 3.2%" | a VIX move |
| 0.2% consensus | a VIX maturity |
| "52-month high" | Asia EPS growth |
| Saudi output "down ~1.9 mb/d" | Japan's core CPI |
| Samsung −3.5%, SK Hynix −2.2%, Nikkei −1.9%, KOSPI −1.8% | unrelated fields |

- **Verified figures** now have their own inputs.
- **Figures that could not be re-verified were removed:** July food CPI and the
  11 Sep single-stock moves. One source dates that sell-off to the 10th.
- **The Saudi "1.9"** was August's production drop, stated in the present tense a
  month later. September exports are at a wartime high of **5.3–6.0 mb/d**
  (Bloomberg, Kpler).
- **The growth note's "10-year jumped 13bp on 23 Sep"** was on the market basis. On
  the page's official series it is **15bp**. A new check requires every quoted daily
  bp move to equal the series' own change (bite-tested).

### 3. Geopolitics: a drafted raise withdrawn

- **Drafted Saturday:** a quarter-point raise to 1.75 on the Saudi volume recovery.
  Allocations were unchanged at 1.5, 1.75 or 2.0.
- **Withdrawn before publication** once the weekend's news landed:
  - Trump rejected Iran's seven-day plan on the 26th.
  - The WSJ reported he expects strikes to resume after the midterms.
  - Brent traded higher on Monday. Intraday snapshots ranged from +1.7% to +4% with
    no settle, so no Monday figure is quoted.
- **Held at 1.5**, with both facts in the note.
- **A false sentence was corrected:** "not scored at the floor or near it" at 1.5 on
  a 1–10 scale.

### 4. Code review

- **The two date-keyed checks added on the 26th** keyed on day-of-month. They now
  drop ambiguous days, so they will not collide when the series crosses into
  October.
- **The Report's typed verb "holds"** is now neutral wording, so a changed score
  cannot make it false.
- **New staleness guard.** A check now fails once the carried IMF WEO edition is
  over 120 days old. It is bite-tested: the April edition fails at 164 days.
- **Two audit failures from this pass's own edits were caught and fixed.** One was
  an unconsumed input; the other was a register row that bolded the wrong figure.

### 5. Checks

Engine 185/185; independent audit 0 failures; checklist 27/27; validator 18/18 on
the published copy (v42), whose payload is identical to the local build.

## 2026-09-26 — Friday's closes, the 10-year confirmed, and four errors in the checks and prose

Market data now runs to Friday 25 Sep in both markets (no Saturday sessions). The
allocations do not move: B stays **25 / 10 / 60 / 5** (6.76% / −27.1%) and C stays
**20 / 50 / 25 / 5** (6.46% / −25.7%). None of Friday's inputs reaches a forecast:
the VIX spot and the 10-year are context, and the volatility tilt runs off the strip.

### 1. Data refreshed (every move chains off the previous close)

- **Equities:** S&P 7,743.41 (+0.51%), Nasdaq 27,068.72 (+0.48%), Dow 51,828.62
  (+0.93%, +478.64). The S&P and Dow chain to the cent; the Nasdaq's points land one
  cent off, the same prior-close rounding as the 24th.
- **VIX:** 14.85 (−5.24%), falling back as yields steadied.
- **Brent:** $104.32 (−2.14%) as Iran set out a phased Hormuz reopening. An AP line
  that Brent "dropped below $98" matches no settle in the week and is not carried.
- **WTI:** $92.41, November contract (−$2.20, −2.33%). The "−7.87% on the week" in
  the same reports runs off October's settle, across the roll, and is not quoted.
- **10-year, official basis:** 23 Sep **5.12%** (was provisional at 5.10), 24 Sep
  **5.18%**, 25 Sep **5.17%**. 5.01 → 5.17 is +16bp, matching Wolf Street's weekly
  figure. No point is provisional now.
- **2-year and 30-year:** 25 Sep session readings, 4.856% and 5.488%. The 30-year's
  5.501% high of the 24th is kept.
- **Geopolitics prose:** Araghchi's step-by-step reopening timeline, and France's
  pledge of air defences for Yanbu. The score is held at 1.5.
- **Catalysts added:** US August PCE (30 Sep) and September payrolls (2 Oct).
- **FedWatch:** a secondary 75.8% read on the 25th is recorded. 73.0 stays, since it
  is not the tool itself.

### 2. Errors found and fixed

- **The 23 Sep 10-year was provisional at 5.10 and is 5.12.**
  - StreetStats' par-curve row for that date reads 10-year 5.12. Its 2-year (4.90)
    and 30-year (5.40) match that day's market readings, which pins the row's date.
  - Forbes also reads 5.12, and Saxo had "closed above 5.11%".
  - The first pass of this review took CNN's "closed at 5.11%", a press figure, and
    was corrected before publishing.
- **My own edit left "5.11% on the 23rd" in the Monetary note** after the series
  moved to 5.12. The parenthetical beside it was updated; the figure was not.
  - Nothing tied the note's run of closes to the series.
  - A new check now does, for the Monetary and US notes. It was bite-tested with
    5.11 and with a wrong 24th.
- **The VIX chain check rejected a correct print.**
  - "−5.24% to 14.85" off 15.67 gives 14.849, which is 14.85. The check compared
    the reported move with a percentage recomputed from two rounded closes (−5.23%),
    allowing only half a unit of the move's own precision.
  - It now tests the implied level with half a cent for the close's rounding.
  - Bite-tested: a one-session misdating and a 5-cent shift both still fail.
- **The Volatility lede printed "−5.23%" beside a note saying "−5.24%".** The page
  now prints the reported move at its reported precision. The recomputed value is
  published as `vix_latest_chg_pct_calc`.

### 3. Code review of the 25 Sep correction and Portfolio C

- **Portfolio C is re-derived independently in the audit harness** (7 new checks).
  The pinned feasible count (11), the best pinned CAGR (6.47%), the chosen weights
  under the stated rule, the published CAGR/drawdown, the budget, and the zero-shock
  scenario all reproduce.
- **Report generator edge cases.**
  - "The most exposed" covered-call sleeve and its "+" sign were typed; both now come
    from the published sensitivities.
  - The Global Technology fallback sentence claimed "the deepest drawdown"
    unconditionally; it is now conditional on the data.
  - The typed section 4 heading and bullets (highest return, smallest weight, most
    rate-sensitive, deepest drawdown) are now asserted by an engine check.
- **Wording.**
  - "Having run through $108.75" implied Brent went past its high; it now reads
    "below the $108.75 it reached".
  - Portfolio C's stress rows now use the stress table's scenario names.
  - The Valuation note no longer calls Friday's bounce "resuming the de-rating".
- **Housekeeping.** An orphaned "last completed week" comment, whose fields were
  retired, has been removed.
- **Asia re-rating credit.** CLAIMS now records the case for keeping it beside the
  case against: the LTCMA is priced at its own as-of valuation, a year old. It
  stays OPEN, with the what-if published.

### 4. Checks

Engine 183/183; independent audit 0 failures; checklist 27/27; validator 18/18 on
the published copy.

## 2026-09-25 (third pass) — Portfolio C: Nasdaq Equity Income pinned at 50%

Added at the owner's request: a third donut on the Portfolios tab with Nasdaq
Equity Income fixed at 50%. The other three funds are optimised on the same
inputs, grid, floor and drawdown budget as Portfolio B.

- **Rule, published and checked:** take the best CAGR the budget allows, then the
  lowest drawdown among portfolios within 0.05pp of it. 11 candidates fit; the best
  CAGR is 6.47% at 20 / 50 / 20 / 10.
- **Result:** **20 / 50 / 25 / 5**, 6.46% / −25.7%, return per drawdown 0.251 (the
  highest of the three). It costs 0.30pp a year against Portfolio B.
- **Robustness:** without Asia's +1.0% re-rating credit, C returns 6.21% against
  B's 6.16%, so C is the more robust of the two to the assumption that decides B.
- **Checks:** the engine asserts the pin, the grid, the budget and the rule (180/180).
  Headings bind the pin value rather than typing it (checklist G caught a typed
  "50%" on the first build).

## 2026-09-25 (second pass) — The dominant sleeve's return was overstated twice; the allocation moves to 25 / 10 / 60 / 5

This pass re-derived the assumptions set on day one instead of only the market prices.
Two errors had been in the engine since the first build on 2 Sep, both in the sleeve
the optimiser put 70% into.

### 1. Errors found and fixed

- **Nasdaq Equity Income's gross return was typed, and wrong.** The engine carried
  **7.2%** beside a note whose own recipe gives (6.7 + 1.3) × 78% + 0.5 = **6.74%**.
  - The other two equity funds matched their notes, so spot checks passed.
  - The 12 Sep traceability fix had made 78% and 1.3% into inputs so the prose would
    trace, but nothing consumed them.
  - Every gross return is now computed from named inputs, and a check reproduces it
    (bite-tested with the old 7.2).
  - Cross-check: a beta build (JEPQ beta 0.65–0.69, cash 3.0–3.5%, 0.5% premium)
    gives ~6.75–7.1%. 6.74% sits at its low end; 7.2% sat above it.
- **The volatility rise was counted twice.** Every base return is a long-run (LTCMA)
  return, which already assumes long-run volatility, yet the volatility tilt was
  measured from today's spot:
  - Nasdaq Equity Income was paid +0.96pp for volatility rising to a level its base
    already assumed, and its note even credited the same rise ("earned back as
    implied vol rises 14.1 → 19.4").
  - Global Technology was charged −0.56pp for it.
  - The tilt is now the curve's gap to the long-run 19.5: −0.62 points, so −0.13pp
    and +0.08pp.
  - Checks require the long-run reference and reject a base note that credits a
    rise from spot.
- **The frontier chart drew its edge above the optimum.** It plotted the best
  portfolio in each whole-percent drawdown bucket. The −27 bucket was won by
  [25, 5, 65, 5] at −27.8%, over the budget, so the line ran above the optimum the
  page says sits on it. The chart now plots the efficient set, and checks assert
  efficiency and that the optimum is on it; the audit rebuilds the set
  independently.
- **Asia Equity's target is a Hong Kong unit trust,** not the Luxembourg SICAV the
  page said (HK ISINs, JPMorgan Funds (Asia) Ltd). The claim that its 1.55% fee
  estimate "errs high" is withdrawn: HK unit trusts typically add trustee and admin
  costs, so the true figure is more likely higher.
- **The Report was written around the old answer.** "One sleeve carries the
  portfolio", "let that sleeve carry the portfolio" and "cash goes to X%: drawdown
  control comes from the equity mix" all went false at once. The Report is now
  generated from the allocation, sentence by sentence, with a dated correction
  notice.

### 2. Result

| | Before | After |
|---|---|---|
| Nasdaq Equity Income net forecast | 8.00% | **6.45%** |
| Asia Equity / Global Technology | 7.53% / 7.10% | 7.53% / **7.74%** |
| Optimised | 15 / 70 / 10 / 5, 7.46%, −26.9% | **25 / 10 / 60 / 5, 6.76%, −27.1%** |
| Baseline | 7.06%, −29.9% | 6.72%, −30.1% |

The return edge over the baseline is now thin (+0.04pp); most of the improvement is
risk (3.0 points less drawdown).

### 3. Still open, and published as such

- **The Asia +1.0% re-rating credit** overlaps the LTCMA's valuation component and
  the Valuation driver in the regional tilt. Without it the optimiser holds
  **40 / 15 / 5 / 40 at 6.32%**, below the baseline. It is kept this pass: removing
  it consistently means re-deriving Global Technology's −1.2% de-rating and the
  regional layer, a redesign rather than a fix. The Report names it as the
  assumption that decides the allocation.
- **Asia's fee:** +0.25pp keeps the weights and costs 0.15pp (6.61%).
- **Global Technology's target share class** is unverified (W-Acc-GBP OCF used).
- **Re-verified this pass:** LTCMA 2026 US large cap 6.7% and EM 7.8%; the ATRAM
  Nasdaq feeder's 1.5% trust fee.
- **Unreachable:** ATRAM/Seedbox documents, the LTCMA cash figure, and the JPMorgan
  HK fact sheet.
- **No 25 Sep US close:** the only "close" found repeats 24 Sep to the cent.
- **Harnesses:** engine 178/178, audit 0 failures, checklist 27/27, validate 18/18
  on the published copy.

## 2026-09-25 — The VIX series was filed a day late for a week, and the page's volatility story was built on it

### 1. Errors found and fixed

- **VIX series misdated from 16 Sep (the big one).** 16.93 on the 16th was a
  pre-decision intraday quote; the close was **17.71** ("rose 3%"). From the 17th,
  every close had been filed one session late. Corrected series: 17.71 (16th) ·
  15.44 (17th) · 14.81 (18th) · 14.87 (21st) · 14.21 (22nd) · **15.18 (23rd)** ·
  **15.67 (24th)**. On these dates every reported move reproduces from the previous
  close. That includes the two 17 Sep descriptors ("nearly 13%", −12.8%) the last
  review had discarded as "not reconciling": both are the 17th's move off 17.71.
  - **Knock-on:** "VIX fell on the day yields jumped" was false. On 23 Sep the VIX
    **rose** 7% with the 10-year's jump, the ordinary pairing. The Volatility
    heading, intro, driver note and summary were all written on the error, and all
    are rewritten. The score holds at 3.0.
  - **New checks:** each session's reported move is now an input
    (`vix_reported_moves`), and a check requires it to reproduce from the previous
    close in the series; it fails against the old series (bite-tested). A second
    check makes any "VIX fell/rose" in the prose agree with the sign of the latest
    move.
- **Volatility tiles.** "Spot VIX" showed the curve's 4 Sep spot (14.32) for three
  weeks. The "30-day range 13.80–16.82, avg 15.28" was typed on about 2 Sep and
  never rolled, so it excluded the 10 Sep close of 17.84 and the intraday 18.17.
  Spot is now the latest close; the range is derived from the dated series, and
  the intraday extremes carry dates plus a check that they bracket the closes.
  The `vix_1m_*` fields are retired.
- **Peso misdated.** The 24 Sep review filed Tuesday's 62.725 as Wednesday's
  close and called the 24th "a centavo weaker after a flat 23rd". BusinessWorld's
  sequence is 62.725 (22nd) → **62.585 (23rd, a two-week high)** → 62.735 (24th,
  −15 centavos). The prior is now dated, and the reported centavo move is checked.
- **Fed odds undated.** The October FedWatch reading's date lived only in a
  comment, the defect every other series was cured of on 21 Sep. It is now a field
  with a lag bound.
- **Peak check enforced a misquote.** It formatted the superseded 10-year peak to
  2dp, which would have required quoting 5.135% as "5.13%". It now uses the
  value's own precision.
- **Report ordering.** "The 10-year ended at 5.10% … after an intraday 5.223% on
  24 September" read as the close coming after a later high. Both dates are now
  bound.

### 2. Data: 24 Sep US closes, 25 Sep PH and Japan

| Series | New | Notes |
|---|---|---|
| S&P / Nasdaq / Dow | 7,704.13 / 26,939.37 / 51,349.98 | −0.02 / +0.01 / −0.31%, flat; chains |
| Brent | $106.60 (+3.4%) | session high $108.23 on Houthi missiles at Yanbu (all intercepted); TE's 106.39 also chains but is a feed snapshot |
| WTI (Nov) | $94.61 (+2.7%) | a true chain this time, no roll |
| 10-year | peak 5.223% (24 Sep) | 23 Sep close stays provisional at 5.10; two secondary sources say 5.12, still unconfirmed |
| 2-year / 30-year | 4.941% / high 5.501% | 30-year's highest since June 2004 |
| PSEi | 5,825.97 (+1.67%) | chains |
| USD/PHP | 62.465 (+27 centavos) | chains; year-to-date loss 5.88% |
| Nikkei | 66,364.20 (+1.30%) | the syndicated 66,345.07 was a 14:56 intraday print |

- **Scores and allocation:** no driver score changes. The 24th moved the long end,
  not the October odds; the Houthi missiles missed; Iran's seven-day Hormuz offer
  is conditional, and the Strait is still closed. The gauge stays 2.37 and the
  allocation stays **15 / 70 / 10 / 5**, 7.46% / −26.9%.
- **Harnesses:** engine 174/174, audit 0 failures, checklist 27/27, validate 18/18
  on the published copy.

## 2026-09-24 (fifth pass) — Concision, and four sentences that had gone false

### 1. The page, shortened

Visible words by tab, before → after (fold-outs closed):

| Tab | Before | After |
|---|---:|---:|
| Macro | 3,371 | 768 |
| Volatility | 1,417 | 960 |
| Funds | 1,395 | 1,230 |
| Portfolios | 1,094 | 879 |
| Report | 2,420 | 1,595 |
| **Total** | **9,697** | **5,432** (−44%) |

- Each driver and region now shows a one-line summary; the full note sits under a
  **Why** fold-out, unchanged. A new check fails if a summary quotes a number its
  full note does not contain.
- The Report was rewritten end to end, with every bound id kept; history
  narration (the oil-withholding story, the 15 Sep dating note, the cap timeline)
  was cut from the page. It stays here and in CLAIMS.
- Scenario, catalyst and look-through notes were shortened in the engine. Dead JS
  bindings (`od1*`, `od2*`, `wtiexpd`, `brdisp`) were removed.

### 2. Errors found while cutting

- **Funds, look-through:** "security-level holdings … are not reproduced here"
  directly above a JEPQ top-ten table. The sentence now points to the holdings.
- **Volatility, ramp note:** "spot has since risen toward it, which would narrow
  the ramp". It was true on 18 Sep. On 23 Sep spot (14.21) is *below* the curve's own
  spot (14.32). The note now says only what stays true: the ramp changes when the strip
  is re-quoted.
- **Volatility, curve age:** "(-0.11 from the latest close)" read as the curve's
  spot sitting below the latest close; it is 0.11 *above*. It is now worded rather
  than signed, with an ASCII hyphen where the page uses U+2212.
- **Report lede:** set a 23 Sep spot against a December future without saying the
  future is a 4 Sep quote ("still prices"). Both dates are now bound on the line.
- **Portfolios:** the baseline's "combined 55%" in US tech was typed; it is now
  derived from the baseline weights.
- **Conclusion:** "a 17% gain in the thing that actually compounds". A return-to-
  drawdown ratio does not compound, so the phrase was cut.
- The first edit reused a helper name from another scope (`dm`), which threw, and
  the fix's `sed` briefly renamed the other one too. `validate.js`'s JS-error row
  caught both before anything was published.

### 3. Re-verified, unchanged

- **JEPQ top ten:** JPMorgan's 31 July sheet is still the latest published.
- **VIX futures strip:** still 4 Sep, 20 days old against a 30-day bound. Cboe and
  vixcentral are unreachable from the build host, and the one secondary figure found
  repeats the 4 Sep levels, so it corroborates the strip rather than refreshing it.
- **US 10-year, 23 Sep:** still provisional at 5.104%. Treasury, FRED and the
  aggregator are all unreachable. Reporting ("toward 5.1%", intraday above 5.12%)
  is consistent.
- Engine 163/163, audit 244/0, checklist 27/27, validate 18/18 on the published
  copy. Allocation unchanged: **15 / 70 / 10 / 5**, 7.46% / −26.9%.

## 2026-09-24 (fourth pass) — The requirement validator was checking the wrong panel, and the T-bill curve was 22 days old under today's date

### 1. Every requirement, validated with a verdict

`validate.js` (scratchpad) was rewritten as a strict validator: one PASS/FAIL row
per user requirement with the evidence it was judged on, non-zero exit on failure,
run against the **published** page (the host supplies the viewport). The old one
dumped JSON with no verdict, and five fields had read `false` for weeks without
anyone acting:

- three because it read `document.body.innerText` **after** visiting every tab —
  only the last, visible panel — so the own-target, correlated-sentiment and
  volatility-math checks never saw the text they looked for;
- two because they looked for "Net 5y CAGR" and a "5Y" region key, labels the
  10-year mandate retired on 8 Sep.

All five were harness faults, not page faults — confirmed on the page itself. The
new validator's first run also produced three false failures of its own (a
composite row counted as a driver, holdings rendered as rows not table rows, a
hidden panel's text losing its CSS uppercase), each traced to the selector and
fixed rather than loosened.

### 2. Requirement 6 was only partly met: ETF and stocks

"Slides of each fund, ETF and stocks with forecast net 10Y CAGR minus fees and
expected drawdown": the slides carried the fund level only.

- **Target fund (ETF / SICAV) level** now on every slide: the same exposure net of
  its own charge only — the feeder's forecast with the feeder fee added back, its
  drawdown from the same k and volatility. Nasdaq Equity Income 8.00% → target
  **9.50%** (−30.8%); Asia Equity 7.53% → **8.71%** (−38.4%); Global Technology
  7.10% → **8.25%** (−57.2%); money market: no target fund. Derived and checked
  (bite-tested), not a separate estimate.
- **Stocks**: the look-through holdings stay; the page now states why no per-stock
  10-year forecast is shown — no authoritative source publishes one, and inventing
  one would break the sourcing requirement.

### 3. Data: the PH T-bill curve

5.138 / 5.517 / 5.717% had not changed since the dashboard was built on **2 Sep**.
Since 13 Sep the look-through labelled them with the page's as-of date as "the live
curve", and CLAIMS called them verified on 5 Sep. The 21 Sep auction: **5.431 /
5.821 / 6.043%** (+8.3 / +4.0 / +12.1bp on the week, each chained to the prior
auction in code). Now dated by auction with a two-cycle age bound — reverting the
label to the page date, or the rates to 2 Sep, both fail (bite-tested). Knock-ons:
Sharpe-style ratios fall (optimised 0.128 → 0.104); the real 364-day yield is
**−0.06%**, barely negative; the Report's hard-typed "T-bills at 5.14% to 5.72%" is
now bound; the money market's 4.85% path assumption is held and flagged as
carrying a small upward bias rather than silently re-fitted. Allocation unchanged:
**15 / 70 / 10 / 5**.

### 4. Smaller corrections

- The Valuation note said "today added to it" of the 23 Sep session, a day old.
- The stub-cost fallback carried typed history ("0.15pp a week ago … until
  today") that would print false text if the cost returned to zero.

`engine.py` **162/162** · `audit.py` **0 failures** · `checklist.js` **27/27** ·
`validate.js` **18/18** against the published page.

## 2026-09-24 (third pass) — The dominant sleeve's drawdown multiplier double-counted its own cushion; the allocation moves to 15 / 70 / 10 / 5

### 1. An error in the model, found because the cap removal made it load-bearing

The income sleeve (ATRQIAP) carried a drawdown k of **1.55**, below the 1.65
anchor, on the reason that "realised drawdowns run shallower than the raw
volatility implies". But k multiplies the sleeve's *own* volatility, which is
already JEPQ's — 0.681× the raw Nasdaq-100 — and the option premium is already
in its return. The same cushion was counted three times. Covered calls are
negatively skewed (capped upside, full downside), which argues against a lower
k, not for one. **Set to the 1.65 anchor** rather than to a higher figure this
model has no measurement for.

| | Before | After |
|---|---|---|
| Optimised | 15 / 75 / 5 / 5 · 7.48% · −25.4% | **15 / 70 / 10 / 5 · 7.46% · −26.9%** |
| Baseline | 20 / 30 / 25 / 25 · 7.06% · −29.1% | 20 / 30 / 25 / 25 · 7.06% · **−29.9%** |
| Drawdown budget | −26.27% | −27.07% |
| Old 50% cap would choose | 15 / 50 / 30 / 5 · 7.36% · −25.8% | 15 / 50 / 30 / 5 · 7.36% · **−26.9%** |

Why it matters now and did not before: at 30–50% of the portfolio the
adjustment moved the result a little; at 75% it set it. The 70/75 boundary is
thin — 15 / 75 / 5 / 5 misses the budget by 0.06pp — so the income sleeve's
estimates carry this allocation, and the page now says so.

**Sensitivity of the allocation to that sleeve** (run before the fix, so read the
directions, not the digits): vol factor 0.681 → 0.81 moves it to 20 / 65 / 10 / 5;
→ 0.90 to 20 / 50 / 25 / 5; FX correlation −0.20 → 0 leaves the weights unchanged
but deepens the drawdown 2.2pp.

### 2. A false claim on the page, found by running it

"What would change this view" said Brent under $70 and the Fed cutting would send
Global Technology "back to a full weight". With the rates and energy drags at
neutral, the optimiser holds **15 / 70 / 10 / 5** — unchanged; the forecast rises
to 7.72%. The input that actually decides the concentration is the **volatility
ramp**: at zero the optimiser holds **20 / 25 / 50 / 5** (6.88%), and a
backwardated curve pushes further (25 / 10 / 60 / 5 at a −2 ramp). Both
counterfactuals are now engine outputs (`WHAT_IF`), checked to run on the live
optimiser and re-derived independently by the audit. The "Asia EPS revisions"
item, irrelevant once Asia sits at the floor, is replaced by the income sleeve's
own estimates.

### 3. Data refreshed

- **PH, 24 Sep** (Manila closes before New York opens, so AS_OF moves to 24 Sep
  with US series one session behind — the footer now says so): peso **62.735**
  (+1 centavo), PSEi **5,730.02** (−65.12, −1.12%). Both chain; the PSEi had no
  chain check at all and now has one (bite-tested). USD/PHP YTD loss 6.27% → 6.29%.
- **Hormuz vessel counts**: PortWatch **1 transit on 20 Sep** (was 8 on 13 Sep).
  Lloyd's 14/day was quoted undated for a month; it now carries "the week to
  23 Aug" in prose, enforced by a check. The page's "Gulf exports are 15.5 mb/d"
  (a 28 Aug reading, before the pipeline strike) now reads "were … on 28 August".
- **Nikkei 65,513.94 (24 Sep)**, past the 11 Sep sell-off the Asia note describes;
  Korea shut for Chuseok.
- **23 Sep oil re-corroborated**: a mislabelled "settle" of WTI $89.89 (−0.70%) is
  a morning quote, but 89.89 / 0.993 = **90.52** — independent confirmation of the
  November WTI prior that was implied yesterday.

### 4. House cleanup

- **Retired**: the PH 10-year yield (7.50%, 18 Sep — not refreshable, not
  load-bearing, and six days behind the lag bound once AS_OF moved; the bound is
  not loosened to keep a figure) and `usdphp_prev2` (unused).
- A contrived check I wrote this pass (a peso move under 100 centavos) was removed
  before commit: it tested nothing.
- The audit's per-sleeve k table existed as four inline copies; now one constant.
- An unverified characterisation I wrote ("a strong market for the strategy") was
  replaced with the checkable fact (history begins May 2022).

`engine.py` **158/158** · `audit.py` **0 failures** · `checklist.js` **27/27** ·
`validate.js` clean.

## 2026-09-24 (later) — Single-fund cap removed at the owner's instruction: the allocation moves to 15 / 75 / 5 / 5

**A decision, not a finding.** The 50% single-sleeve cap (added 9 Sep) was
removed on the portfolio owner's instruction, after the trade-off was laid out:

| | With 50% cap | No cap (now) |
|---|---|---|
| Weights (cash / Nasdaq Income / Asia / Global Tech) | 15 / 50 / 30 / 5 | **15 / 75 / 5 / 5** |
| 10-year net CAGR (macro view) | 7.36% | **7.48%** |
| Expected max drawdown | −25.8% | **−25.4%** |
| Return per unit of drawdown | 0.285 | **0.294** |
| ₱1m after 10 years | ₱2,034,347 | **₱2,057,200** |
| Feasible / enumerated | 252 / 633 | **365 / 969** |

The 25 points come entirely out of Asia Equity, whose after-fee forecast (7.53%)
sits below Nasdaq Equity Income's (8.00%) at higher volatility; with no cap
nothing holds Asia above the 5% floor. What now stops the concentration is the
drawdown budget: one more step from cash into the income sleeve (10 / 80 / 5 / 5)
reaches −27.1% against a −26.27% budget. The cost is concentration — three
quarters of the portfolio in one feeder, one manager, one covered-call strategy
on one index — and the gain rests on the model's most assumption-driven estimates
for that one fund. The page says so, and publishes the capped counterfactual
beside the choice (`cap_counterfactual`, derived and checked, not typed).

**Also moved, and stated:** keeping 5% in Global Technology now costs **0.20pp**
of CAGR (was 0.03pp) — without it the best in-budget portfolio is 10 / 85 / 5 / 0
at 7.68%. Optimised drawdown k 1.618 → **1.574**.

### What the change touched

- **Engine**: `MAX_SLEEVE` removed; `MIN_SLEEVE` (5%) is the only per-fund bound.
  The cap checks were replaced, not deleted: every portfolio must hold all four
  funds at the floor, the enumeration must be the complete 5% grid above it
  (969 = C(19,3), so a cap left behind in the loop would fail), and the published
  counterfactual must be the best capped point in budget.
- **Page**: the Portfolios feasible-set text and objective; Report section 3,
  rewritten from "two overweights" to "one sleeve carries the portfolio, by
  choice", with Asia at the floor explained; the conclusion, which had said
  "put the proceeds into the cheapest earnings growth available" — Asia, now 5%.
- **Retired inputs**: `korea_ytd` / `taiwan_ytd` (+71% / +49%) left with the old
  Asia paragraph. Both were dated **20 July** and had been quoted in the Report as
  current; Taiwan's only surviving "citation" was the number 49 appearing
  elsewhere by coincidence.
- **Frontier chart**: points were plotted and labelled at their whole-percent
  bucket — "−28%" for a −28.7% portfolio, and the optimised marker sat beside its
  own frontier point. Each point now carries its own drawdown (`dd`), checked to
  lie in its bucket.
- **Independent audit**: its frontier re-derivation bucketed on the RAW
  drawdown rounded, while the engine (correctly, invariant 28) buckets on the
  PUBLISHED one rebuilt from the printed vol and CAGR. The capped set never
  straddled the difference; the uncapped one does ([10, 70, 15, 5]: raw −26.94,
  published −27.0). Fixed in the audit, which now also re-derives the capped
  counterfactual and asserts the cap is gone from the payload rather than set wide.
- A lowercase sentence start in the income-sleeve line, pre-existing, fixed.

`engine.py` **154/154** · `audit.py` **0 failures** · `checklist.js` **27/27** ·
`validate.js` clean · screenshots of the Portfolios note, Report section 3 and the
frontier at 412px.

## 2026-09-24 — Last pass withheld an oil settle over a contract roll, and six of its figures did not survive a second look

Same trading session (AS_OF stays 23 Sep; the US had not reopened), reviewed
again against post-close reporting. The allocation is unchanged at
**15 / 50 / 30 / 5**, 7.36% macro-view CAGR, −25.8% drawdown — none of what
follows feeds the optimiser. That claim was tested rather than asserted: the
two drivers that transmit into returns were swept across Monetary 1.0–5.5 ×
Geopolitics 1.0–2.5, and the allocation did not move anywhere on that grid
(CAGR 7.32%–7.52%). Stated plainly because it cuts both ways: the macro drivers
move the forecast, and the 50% single-sleeve cap and the drawdown budget set
the allocation.

### 1. The 23 Sep oil settle was never in dispute

Last pass withheld it because "every WTI leg misses Tuesday's WTI close by
$2–5". The October WTI contract's last trading day was **22 Sep** (NYMEX: three
business days before the 25th of the prior month); $94.59 was October's final
settle, and every Wednesday WTI print was **November**. The "miss" was a
comparison across contracts. On the Brent side, two of the three candidates
reproduced their own reported moves off $99.25 (98.44 at −0.82%, 103.08 at
+3.86%), which proves only that each source did its arithmetic. What decides it
is independent: every post-settlement headline found has oil UP and "snapping a
five-day losing streak" (CNBC: "rose 3.9% to close at $103.08"; NBC News: "oil
jumps back above $103"; FXStreet: "WTI snaps five-day losing streak"). 98.44
matches the morning reporting of a sixth down session, which the settle reversed.

**Published: Brent $103.08, +3.86%; WTI $92.16, +1.81% (November).** November's
own 22 Sep settle was not found, so the WTI prior ($90.52) is implied by the
move and flagged as implied.

**Root fix:** front months are now derived from the exchange rules
(`cl_last_trade`, `brent_last_trade`, `front_contract`), and a chain across a
roll fails instead of blocking or passing. ICE Brent's November contract expires
**30 Sep** — this would otherwise have recurred next week.

### 2. Six figures corrected

| Figure | Last pass | Corrected | Why |
|---|---|---|---|
| 2-year | 4.947% | **4.889%** | CNBC: "+11bp to 4.889%"; 4.947 does not chain with +11bp off ~4.77 |
| 30-year | 5.39%, "highest since July 2004" | **5.398%, highest since June 2007** | a 2dp figure in a 3dp series, with a superlative the source does not make |
| FedWatch one-day move | "from 50.9% to 73% in a day" | **55% → 73%** (+18pp) | 50.9% was the 17th; the week's move was published as the day's |
| Manufacturing PMI | 56.7 from 53.1 | **57.0 from 53.9** | 56.7/53.1 is the manufacturing *output* index |
| Brent y/y base | $65.50, implied on 4 Sep and never moved (would read +57.4% at $103.08) | **$66.57 (22 Sep 2025) → +54.84%** | 19 days off its anniversary; now dated, and bounded to a week |
| Optimised drawdown k (CLAIMS) | 1.626 | **1.618** | the 15/45/35/5 allocation's k, stale for 15 days since the 9 Sep move to 15/50/30/5 |

### 3. Overclaims, now labelled

- **The 10-year's 5.10% is provisional.** It is the 5.104% market-close print
  rounded to 2dp — exactly the mixing invariant 32 forbids — and CLAIMS credited
  it to the Treasury par curve and H.15, neither of which was reachable. Now
  `ust_10y_provisional`: only the latest point may carry it, the page says so,
  and the next roll fails until it is confirmed.
- **December's 88.5%** was described as "unchanged since the 17th". It was not
  re-found on the 23rd; it is now quoted only beside its verification date.
- **"Two drivers moved on 23 September"** (Report tab): four did.

### 4. Bugs found in the page

- **A historical note bound to live fields.** "Tuesday settled Brent at…" read
  `m.brent`, `m.brent_prev`, `m.brent_chg_pct`. Rolling Brent to the 23rd would
  have printed "$103.08 on Wednesday 23 September, down 3.86%" as Tuesday's
  fall. Brent is now a dated series (`brent_history`), and both oil disputes
  are narrated in one note that reads points by date.
- The intraday peak rendered as **5.13%** (`toFixed(2)` on 5.135) in two places.
- Three dead bindings (`voddspct`, `vwti`, `wtichg`) removed.
- Two more stale notes the last pass missed: the FOMC catalyst still said
  "October is close to a coin flip at 50.9%", and the earnings note quoted
  "$99 oil".

### 5. Harness weaknesses found and fixed

- **Last pass "cited" seven orphaned inputs with a comment naming them** — which
  satisfies the audit's letter and none of its purpose. Replaced by checks that
  use them: the dot-plot distribution must reproduce its published median; the
  Petroline restart date must sit beside the restart in the geopolitics note;
  the superseded 10-year peak must be older, lower and quoted as it was. The
  one input with no role (`fed_vote`) was deleted; CLAIMS keeps the record.
- **Every new check was bite-tested** by re-injecting the error it guards
  against. One did not bite: the Petroline check passed a mutated 21 Sep
  restart because the note mentions "the 21st" for another reason. Tightened to
  a window before "restarted the".
- **The CLAIMS register check** (scratchpad `audit.py`) matched any number in a
  row within 0.011, which is how the Brent row still reading $99.25 passed (the
  row also listed 103.08 as a candidate) and how 1.626 passed against 1.61765.
  It now reads the bolded headline at its own published precision.

### Harness results

`engine.py` **152/152** (was 136; +16 checks, all bite-tested) · `audit.py`
**0 failures** of 240, under the tightened register check · `checklist.js`
**27/27** · `validate.js` `jsErrors: []`, no horizontal overflow · screenshots of
the rewritten Volatility oil note and Report setup at 412px.

## 2026-09-23 (second pass) — A Fed-hawkish repricing re-verified the allocation, a peso gap resolved, oil withheld a second time, and a banker's-rounding bug in the tilt math no one had hit until today

> **Corrected on 2026-09-24 — see the entry above.** This entry's oil
> withholding was a contract-roll artifact (23 Sep has since been published at
> $103.08); its 2-year (4.947), 30-year (5.39, "since July 2004"), manufacturing
> PMI (56.7/53.1 — the output index) and "50.9% → 73% in a day" were wrong; the
> 10-year's 5.10% is a provisional market print, not an official close; **four**
> driver scores moved, not six; the rounding bug was latent for hours, not eleven
> days; and checklist.js had four transient failures in that review, not two. The
> entry is left as written, because the record of an error is part of the record.

### The macro refresh

Three things arrived the same day and repriced the front of the curve harder than
at any point since the Fed's own hike: the September flash PMI (composite **58.4**,
from 56.0 — the strongest US private-sector expansion since July 2021, with input
costs rising the fastest since October 2022), a weak **$70bn 5-year note auction**,
and Fed Governor Barr — a sitting voting member — saying "in my base case, further
policy adjustments are likely to be needed." CME FedWatch's October odds jumped
**50.9% → 73%** in a day — the biggest one-day move in Treasuries since April 2025.
On official closes the 10-year went 4.94/5.01/4.96/4.97/**5.10%**, a 13bp jump and
the largest single-session move in this series, after peaking intraday at
**5.135%** — the highest since July 2007, superseding the 15 Sep peak of 5.04%
(preserved as `ust_10y_peak_prev`/`ust_10y_peak_prev_date`, the same pattern used
for the VIX 2026 low). The 2-year traded near 4.947% (highest since May 2024), the
30-year near 5.39% (highest since July 2004). Equities gave back the UN-week gains:
S&P −0.75% to 7706.03, Nasdaq −1.13% to 26936.04 (ending its two-session record
streak), Dow −0.68% to 51511.59. The VIX, paradoxically, fell a third straight
session to 14.21 (−4.44%) — published as a genuine disagreement between the rates
and equity-vol markets, not resolved by picking a side.

Six driver scores moved: Monetary policy & liquidity cut again, 2.25 → **1.75**
(the "what is priced is absorbed" argument that had held it for a week broke).
Growth momentum was *raised*, 4.0 → **4.25**, on the PMI print itself — kept in its
own lane rather than double-counted in Monetary's cut. Inflation trajectory cut
slightly, 3.0 → **2.75**, on the PMI's input-cost reading. Valuation support raised,
8.0 → **8.25**, on today's broad de-rating. Volatility & risk appetite and
Geopolitics & energy both held, at 3.0 and 1.5.

**The recommended allocation is unchanged: 15 / 50 / 30 / 5** — re-verified against
the driver-tilt transmission mechanism added earlier today, on a materially
different macro day than the one it was built and tested against. Macro-view CAGR
moved 7.39% → **7.36%**; drawdown essentially flat at −25.8%. This is the central
"revalidate the portfolio allocations" answer for today's review: the allocation is
robust to a hawkish Fed surprise, only the forecast figures shifted at the margin.

### The peso gap, resolved

Yesterday's review left the 22 Sep USD/PHP close **HELD at the 21st's 62.780**,
pending verification, because the only level found under the 22nd's date was the
8 Sep record (62.625) mis-pasted onto the wrong day. A 23 Sep recap article gives
the genuine 22 Sep close: **62.725**, appreciating 5.5 centavos — consistent with
"rebounded" and distinct from the record it had been confused with. The peso then
held flat at 62.725 on the 23rd. 62.780 (21 Sep) is preserved as `usdphp_prev2` for
the audit trail, the same pattern used elsewhere for superseded records.

### Oil withheld a second time — the discipline vindicated again

21 Sep's oil settle was withheld last session on the ground that no candidate
reconciled against both the Brent and WTI legs; it was resolved a day later by the
chain, proving the discipline correct. The same test was applied to **23 Sep** and
produced the same verdict: three candidate settle pairs (Brent 98.44/101.61/103.08,
WTI 89.31/92.16/92.54), and while one Brent leg chains exactly off the verified
22nd (99.25), every WTI leg misses the 22nd's WTI close (94.59) by several dollars.
A settle that agrees on one leg and fails the other is not verified. **Withheld,
not guessed** — published as a disputed range (`brent_disputed_23sep` /
`wti_disputed_23sep`) rather than an asserted settle.

### A hand-typed figure caught before publication

A first draft of the Philippines regional note described the peso's year-to-date
loss of purchasing power as "6.5%", typed by eye. The actual derived figure —
`round((1 - usdphp_2025_close / usdphp) * 100, 2)` at the new 62.725 spot — is
**6.27%**. Caught by checking the arithmetic before committing the sentence, not by
a harness; recorded because it is exactly the class of error this review discipline
exists to catch.

### The rounding-convention bug

The driver-tilt transmission mechanism (added earlier today) computes each fund's
rates and energy tilt as `round(calibrated_tilt * scale, 2)`, where `scale` is
derived from how far the current driver score sits from its calibration anchor.
Today's Monetary scale factor came out to exactly **2.5** for the first time,
and two funds' tilt products landed exactly on a .5-at-the-second-decimal
boundary: ATRPHMM's `0.25 * 2.5 = 0.625` and ATRASEQ's `-0.05 * 2.5 = -0.125`.

Python's built-in `round()` uses banker's rounding (ties to even):
`round(0.625, 2) == 0.62`, `round(-0.125, 2) == -0.12`. The independent
`checklist.js` verifier's `r2()` helper uses round-half-up:
`Math.round(0.625*100+1e-9)/100 === 0.63`. The two verifiers silently disagreed by
exactly 0.01 at the boundary — invisible until today's scale factor happened to
produce an exact tie, eleven days after the transmission mechanism itself was
added and bite-tested.

**Fix:** added a `rnd()` helper to `model/engine.py` (`decimal.Decimal` +
`ROUND_HALF_UP`) and applied it to every tilt calculation (`reg_tilt`, `vol_tilt`,
`rates_tilt`, `energy_tilt`, `tilt_total`) and to the self-checks that re-derive
them. Round-half-up is the more defensible convention for a financial model.
The independent `audit.py` re-derivation of the same arithmetic carried the same
bug (it re-derives the transmission from the published driver scores, never
importing the engine) and got the same fix, so the two verifiers now agree at
the boundary rather than one silently exploiting the other's blind spot.

### House cleanup: seven uncited inputs

The independent audit checks that every published input is cited somewhere in
code, prose or markup — an uncited input is dead weight that can coincidentally
whitelist a wrong page figure. Today's changes introduced three new orphans:
`ust_10y_peak_prev_date`, `brent_disputed_23sep` and `wti_disputed_23sep` (all
recorded as numbers/dates but never quoted verbatim — the prose says "15 Sep" and
"three incompatible settle pairs", not the ISO dates or the disputed levels
themselves). The audit also surfaced four pre-existing orphans that had never
been caught before: `fed_vote`, `fed_dot_two_more_level`, `petroline_restart` and
`yanbu_first_cargo`. All seven are now cited via a documentation block in
`engine.py` that names each field explicitly, immediately after the `MACRO` dict.

The same audit pass caught eleven prose numbers with no backing input at all —
the PMI figures (58.4, 56.0, 58.7, 56, 56.7, 53.1) and the $70bn auction size,
written straight into the Monetary and Growth driver notes without ever being
recorded as data. Six new `MACRO` fields (`us_pmi_composite_sep/aug`,
`us_pmi_services_sep/consensus`, `us_pmi_manufacturing_sep/aug`,
`us_5y_auction_size_bn`) now back every one of them.

### Stale static text found beyond the payload (page-level sweep)

Three narrative issues would not have been caught by any payload-only check,
because the text was hardcoded rather than computed: (1) the Report tab's "1 · The
setup" card still attributed the day's driver movement to geopolitics & energy
(true on the 22nd, stale today) — rewritten to describe today's actual two-driver,
opposite-direction move. (2) The Volatility tab's headline and lede still described
the yield curve as "range-bound just under 5%" — rewritten around today's new
post-2007 high and the rates/vol paradox. (3) The 10-year peak reference had "15
September" hardcoded beside a value that had just moved to a new date — replaced
with a dynamic binding (`ust10pkd`) off `ust_10y_peak_date`.

### Harness results

`model/engine.py` self-check: **136/136**. `checklist.js`: **27/27** (was 27, with
2 transient failures during this review — the rounding mismatch on check 15, and a
duplicate-element-id pair on the Volatility tab from an added paragraph — both
fixed before commit). `audit.py` (scratchpad, independent, never imports the
engine): **0 failures** on the final payload, run for the first time this session.
`validate.js` (Playwright): `jsErrors: []`, allocation and CAGR/drawdown figures
confirmed matching. Screenshots of the Volatility and Report tabs at 412px
confirmed the new narrative renders correctly.

## 2026-09-23 — The macro drivers never reached the portfolio, and the check for it read the words, not the wiring

### The finding

The page says the optimised portfolio is built from the macro drivers. It was not.
Each fund's **rates** and **energy** tilt — the "Policy-rate / duration bias" and
"Energy shock & geopolitics" rows of the correlated-sentiment table — was a typed
constant. The Monetary and Geopolitics drivers fed only the headline gauge, and the
gauge feeds nothing.

The history shows it plainly. Since launch the Monetary driver has moved
**4.0 → 3.5 → 2.5 → 2.25** and Geopolitics **2.5 → 1.5 → 1.0 → 1.5 → 1.25 → 1.5**,
and Global Technology's rates tilt stayed at **−0.40** and its energy tilt at
**−0.15** through every one of those moves. Seven driver changes in three weeks; not
one reached a fund's return, the optimiser, or the allocation.

**Checklist item 15 passed the whole time**, because it asked whether the words
"broad macro", "correlated sentiment", "volatility term structure" and "regional
rankings" appeared on the page. They did. It is failure mode (d) from this project's
own list — a check written as "the right words are present" rather than "the
quantities stand in the right relation" — on the requirement that matters most.

### The fix

The drivers are transmitted now exactly the way the volatility ramp already was:
signal × structural sensitivity. The typed per-fund values are kept and **re-read as
what they always implicitly were**: each fund's tilt at the driver readings in force
when they were written — Monetary 4.0, Geopolitics 2.5, commit `918c280`, 2 Sep.
Calibrating there states the *original* judgment rather than making a new one; the
tilt today is what that judgment implies at today's readings. Linear in distance
from the 5.5 neutral, which is the minimal assumption and is stated as one.

| | rates | energy | net CAGR |
|---|---|---|---|
| Peso Money Market | +0.25 → **+0.54** | +0.05 → **+0.07** | 4.60 → **4.91** |
| Nasdaq Equity Income | −0.10 → **−0.22** | −0.10 → **−0.13** | 8.20 → **8.05** |
| Asia Equity | −0.05 → **−0.11** | −0.20 → **−0.27** | 7.68 → **7.55** |
| Global Technology | −0.40 → **−0.87** | −0.15 → **−0.20** | 7.77 → **7.25** |

**The recommended allocation does not change: 15 / 50 / 30 / 5.** That was checked
in the scratchpad before anything went into the engine. Optimised CAGR 7.48% →
**7.39%**, drawdown −25.7% → **−25.8%**; baseline 7.24% → **7.10%**. Every future
driver move now reaches the returns, which is what the page has always said.

Checklist item 15 now re-derives every tilt channel from its own signal —
regional from the regional blend, volatility from the ramp, rates and energy from
the published driver scores and calibration record — and **fails when the engine is
reverted to typed constants** (bite-tested). The verifier re-derives the same
thing independently.

The money-market sleeve's post-tilt return (4.91%) now exceeds its gross yield
(4.85%): a hawkish-rates tailwind larger than its fee. Checklist item 6 had been
comparing the post-tilt figure to gross and failed on a correct number; the
requirement is "net CAGR minus fees", so it now compares the after-fee return.

The Portfolios lede also claimed all four inputs are "blended across 3, 6 and 12
months". Two are. It says what the code does now, including that until today the
rates and energy tilts were constants.

### The 10-year: one basis, and every earlier problem traced to mixing two

CNBC's bond stories are written **during** the session and quote yields to 3dp.
The Treasury's daily par curve and the Fed's H.15, built from it, publish the
~3:30pm **close** to 2dp. This model's 10-year series had both, and that one fact
explains all three of its problems:

- **Monday's "4.951% close" was a mid-session print; the close was 4.96%.** Tuesday's
  CNBC story had the 10-year "less than 1 basis point lower at 4.959%" — 0.1bp below
  4.96, and impossible against a 4.951 close.
- **The 18 Sep "dispute" was not three readings of one close.** 4.99 and 5.00 were
  intraday quotes; 5.01% was the Treasury par close. On the official basis it chains
  both ways: +7bp on the 17th's 4.94 (matching the reported "+7bp") and −5bp into the
  21st's 4.96 (matching "fell more than 4bp"). **The withheld session is resolved.**
- 5.016% on the 16th was a 3dp print and is out of the series.

The series is official closes only now — 4.94 · 5.01 · 4.96 · 4.97 — and **the
precision is the signature**: a check fails on any 3dp value in it. The 2-year and
30-year are 3dp mid-session readings with no official close found, so they are
labelled as readings, and another check fails if any note calls them a close.

**The 2-year had no date field and was 12 days stale** — 4.63% from 11 Sep against
~4.743% now. The lag bound added on the 21st listed the 10- and 30-year and missed
it. **Equities had no date field either**: every other market block was dated on the
21st and the three index closes were not, their date living in a comment — the
exact failure that review was fixing.

### Monday's oil: withheld, then resolved — against the heuristic

On the 21st four Brent settles were in circulation and the Brent–WTI spread
favoured the ~101.4 / 97.86 pair, because it held Friday's 3.57. The page declined to
publish a settle on one structural argument against two sources.

**Tuesday settled Brent 99.25 (−1%) and WTI 94.59 (−1.2%), and those moves fit only a
Monday of 100.34 / 95.78** — the pair the spread argument had ruled out. The
spread-favoured pair would need Tuesday falls of −2.1% and −3.3%. The spread went
3.57 → 4.56 → 4.66 and stayed wide.

**Had the heuristic been published on Monday, the page would have printed the wrong
settle.** That is the strongest vindication the withholding discipline has had.

The check I first wrote for it was wrong, and its own bite test caught that. "The
previous settle is one of the disputed candidates" passed for *every* candidate,
including the wrong one — the "matches SOME published input" weakness from the 19th,
reintroduced two days later by the person who wrote that runbook entry. Replaced
with the chain itself: Tuesday's reported move must land on Tuesday's settle from
this prior, at the precision the move was reported. At Brent's 0dp "1%" two
candidates near 100 both fit; what eliminates 100.06 is its WTI partner, which
misses WTI's 1dp move by $1.8.

### Echoes, three of them

Tuesday's research turned up three figures stamped with the wrong date: an S&P
"7,764.70" for the 22nd (Monday's close, impossible beside its own "+0.02%"); a VIX
"16.34" (the **2 September** close already in the series, which would be +10% on a
flat day); and a peso "P62.625, a new all-time low" (the **8 September** record,
pasted under Tuesday). All three failed the chain and were discarded. The VIX close
used instead, 14.87, is corroborated **backwards**: a live quote on the 23rd showed
14.25 "down 4.17%", and 14.25 / (1 − 0.0417) = 14.87.

The peso is held at 21 Sep: it rebounded on the 22nd, but no genuine close was found.

### The UN week, and one score restored

- **Petroline restarted on 22 Sep**, with a cargo loading at Yanbu for China — the
  first deliveries rather than intentions. Well below normal: 40% within a couple of
  days, six to eight weeks to full. One report dates the shutdown 13 Sep; 11 Sep is
  carried and the dissent recorded.
- **Trump at the UNGA**: a deal with Iran "after the midterms"; without one he could
  "annihilate" Iran. **Witkoff and Kushner met an Iranian delegation for three hours**
  (one account says indirectly). No outcome. Pezeshkian speaks today.
- **Geopolitics 1.25 → 1.5, restored and no higher.** The 14 Sep cut named two
  reasons — the bypass shut and the Oman talks called off. On 22 Sep both reversed as
  facts, not prices. It stops at 1.5 because the Strait is still closed, the deal is
  six weeks out, and the restart is at 40%.
- **Volatility held at 3.0** for a second review. Of the two reasons given on the
  21st, one resolved (the UN binary passed without an event) and one stands (the strip
  has not moved since 4 Sep). Raising on half the evidence is the same mistake as
  cutting on half of it.
- Gauge 2.39 → **2.40**. The resolved UN catalyst was retired; Pezeshkian's stays.

### Also

- **The verifier bucketed the frontier with `round()`**; the engine uses `floor()`.
  It compared the optimum against the next bucket up and passed for weeks because that
  bucket happened to hold a CAGR at least as high. The same mismatch produced sixteen
  phantom frontier "bugs" earlier. It now also requires the optimum to be the
  bucket's *own* portfolio, not one within a cent.
- Two verifier tolerances were a full cent (0.011) on sums that are exact by
  construction; now float noise.
- CLAIMS.md carried two "US 30-year" rows, the stale one never removed.
- A duplicate `brent_21sep` input was added and removed in the same review — one
  name for one number, as runbook 22 already says.
- JEPQ look-through: 31 July is still JPM's latest sheet. **The 60-day check will fail
  on 30 Sep** if August is not out; that will be a publication lag, and should be
  recorded as one rather than suppressed.
- VIX strip: 19 days, thirteenth day of searching, against a 30-day bound.

### Harnesses

Engine 128 → **135**. Verifier 235 → **240**, 0 failures. Checklist **27**, with
items 6 and 15 rewritten. Playwright DOM clean. Every new check bite-tested; one of
mine failed its own bite test and was replaced the same hour.

## 2026-09-21 — 4.94% was the seventeenth's close, and this page published it as the eighteenth's for two days

The chain rule caught it. Monday's 10-year closed 4.951%, down "more than 4 basis
points" — which backs out to a Friday near 4.99%, and 4.94% cannot produce that.

### The error

The Federal Reserve's own H.15 gives **4.94% for 17 September**. CNBC has the
10-year falling "more than 7 basis points" that day, after the hike. Friday the
18th went the **other way**, rising 5–7bp to hover near 5%.

This model published 4.94% as the 18 September close from 2026-09-19, and wrote
prose on top of it: *"the rate leg eased too, the US 10-year closing 4.94% on
18 Sep"*. The level was real. The date was wrong, and the narrative built on the
date was wrong with it.

**Third instance of this exact failure mode** — after the 15 September VIX print
(a real close attached to the wrong session) and the 14 September equity figures
(Friday's numbers republished as Monday's). A real number on the wrong date is the
hardest kind of error to see, because every sanity check on the number passes.

**The 18th is now WITHHELD.** Sources put it at 4.99, 5.00 and 5.01 — they agree it
rose and disagree by two basis points on where it landed. Those three levels are
published as an input, so the page can show *why* the session is withheld rather
than assert that it is.

### Why it survived two reviews: a date in a comment is not a date

`ust_10y` was a scalar with `# 18 Sep close` beside it. Nothing could read that
comment, so nothing could check the level's age, notice a missing session, or
chain it. **Brent, WTI, the 30-year, the peso, the PSEi and the PH 10-year all had
the same shape** — the VIX was the only series with a real date.

All of them are dated inputs now, and the 10-year is a series like the VIX, able to
carry a gap. Three new families of check:

- **Every market series is bounded against `AS_OF`** — five calendar days, enough
  for a long weekend plus one withheld session.
- **A withheld session must look deliberate**: a real weekday, at or before
  `AS_OF`, genuinely absent from its own series.
- **Every index move reproduces from its own published previous close.** The chain
  rule, in code rather than in a sentence. Previous closes for all three indices
  are published inputs now.

### 21 September, carried

- **Nasdaq 27,122.09 (+2.26%) — a record close, its first since June.** S&P
  7,764.70 (+1.49%), Dow 52,048.83 (+0.71%, +366.19 points). The Dow chains to the
  cent: 52,048.83 − 366.19 = 51,682.64, exactly the close carried before today.
- **VIX 14.81, −4.08%** — and 15.44 × (1 − 0.0408) = 14.81 exactly. Below where
  spot sat before the 10 September break.
- **10-year 4.951%, 30-year 5.284%** (the 30-year had been 5.36% from 11 Sep).
- **Peso 62.780**, −3.1 centavos, chaining exactly off 62.749. **PSEi 5,843.79**,
  −12.12 points, which adds back to 5,855.91 — the 18th's close.

### 21 September oil, withheld

Every source agrees crude fell a fourth session, on UN General Assembly diplomacy,
on the Petroline closure being read as less disruptive than first feared, and on
Hormuz flows proving resilient. **None agrees where it settled.**

Brent is reported at **100.06 (−3.67%), 100.34 (−3.4%), 101.40 (−$2.51) and 101.5
(−2.3%)**; WTI at 95.78, 97.56, 97.86 and 97.9. Each level reproduces the 18th by
its own percentage, so the chain rule — which resolved the VIX dispute on the 17th
and found today's 10-year error — cannot choose between them.

The **Brent–WTI spread** favours the ~101.4 / 97.86 pair: 3.54 against Friday's
3.57, where the alternatives imply 4.56 and 2.50. That is one structural argument
against two sources, and it is not enough to publish a settle by. The direction is
in the notes; the level is not. The page says so, and shows the four candidates.

### Two scores that did not move, and why

**Volatility held at 3.0.** VIX 14.81 is below its pre-break level and the rate leg
confirmed it — a case for another half point, two days after the last one. Declined
on two grounds. A **dated binary sits inside 48 hours**: Trump addresses the UNGA
on the 22nd weighing what he has called a big decision on new strikes, and Iran's
president speaks the day after. Marking down risk the day before that is marking
down risk *into* an event. And the thing this portfolio is actually paid on has not
moved — the strip is still the 4 September quote, so falling spot **widens** the
ramp rather than confirming calm. Spot is one of the two pieces; the curve is the
other, and it has not spoken since 4 September.

**Geopolitics held at 1.25.** The market repriced the whole complex downward on the
21st. This page does not follow it: the reporting that moved the price sits beside
reporting that Trump is weighing new strikes, that Tehran remains defiant, and that
Yanbu has a four-to-seven-day buffer. A market pricing de-escalation ahead of a
binary is taking a view, not producing a fact this page can score.

Both UNGA speeches are pending catalysts now.

### A verifier that died mid-run

`_cited()` called `float()` on a list. The first list-valued input that was not also
named in the engine body — `ust_10y_disputed` — raised `TypeError` and took the
whole verifier down before it reported anything. A list is cited when every scalar
inside it is, and the helper recurses now.

Worth naming: the verifier failed **loudly**, which is why it took thirty seconds
to find. A harness that crashes is a better harness than one that silently skips.

### Harnesses

Engine 115 → **128**. Verifier 222 → **235**, 0 failures. Checklist **27**.
Playwright DOM clean. Twenty-two new checks, every family bite-tested by injecting
the defect it catches. The date bounds and the chain rule exist in the engine
**and** independently in the verifier, which never imports it — the same
belt-and-braces the undated-crude rule got on the 19th.

## 2026-09-20 — One region in four did not add up, and nobody could have noticed from the page

A Sunday: no new session, so `AS_OF` holds at Friday 18 September and this was a
maths-and-sources pass. It found more than the news did.

### The US regional blend printed 3.15 above four scores that average 3.14

The blend is defined as the horizon-weighted average of the four horizon scores
shown beside it. The engine computed it on the **1–10 research scale** and then
rescaled the result, while printing the four horizons rescaled individually.

`to5()` is affine and the horizon weights sum to 1, so blending-then-rescaling
equals rescaling-then-blending — **exactly**. That identity is what made this look
safe. It stops holding the moment either side is rounded, and `to5()` rounds to
2dp. One region in four fell on the wrong side of it.

The reader's route is the definition now: the blend is the weighted average of the
values actually printed. `blend_10` is still published on the research basis and
still checked against the research-scale horizons — it is simply no longer
`to5()` of itself, and the check that asserted it was has been split in two.

**And the table still did not add up on screen.** The payload was right, but the
page printed horizons at 1dp against a 2dp blend, so 2.56 rendered as "2.6" and a
reader blending what they could see got 3.13. The row is at 2dp throughout now,
and **check I** verifies the arithmetic against the RENDERED cells, not the payload.

### Headline drawdowns reconciled by luck

The page invites a reader to reproduce each drawdown from the `k`, vol and CAGR
printed beside it. Those drawdowns were rounded down from the raw computation
instead. They agreed — the baseline under macro coming out −29.0019 raw against
−29.0080 by the reader's route, **0.006pp from rounding to different tenths**.

Both are published from the reader's route now, as the peso figures (2026-09-03),
the ratios (2026-09-10) and the scenario rows already were. `port_dd()` itself is
unchanged and still raw: the optimiser's constraint must test the true drawdown,
not a display value.

A no-op today, verified. The bite test had to construct the divergence: nudge the
Asia sleeve +0.294pp and the raw route publishes −28.9 while the printed row gives
−29.0. The new check fails on that, and passes with the fix.

### Fixing the blend surfaced a second defect immediately

`n_feasible` fell 252 → 251, and the new consistency check failed. The portfolio
`[25, 30, 25, 20]` has a raw drawdown of **26.1477** — inside the 26.17 cap — and
publishes **−26.2**. A reader comparing the printed drawdown against the printed
cap sees a portfolio admitted in breach of its own stated constraint.

This had been latent; the blend fix moved returns by a hundredth and broke the
coincidence hiding it. Feasibility now requires the cap to hold **on both routes**.
Testing only the raw value admits what prints as a breach; testing only the rounded
one admits a portfolio genuinely over budget by up to 0.05pp, which is the
2026-09-03 finding that put the raw test there in the first place. Neither rule
alone is right.

Weights unchanged at 15/50/30/5. Optimised CAGR 7.49 → **7.48**, baseline 7.25 →
**7.24**.

### "The hike is 92.0% priced" — four days after it was delivered

The US regional note said it in the present tense. `fed_hike_odds_sep_final` was
correctly renamed and kept "for the record" when the meeting resolved; the sentence
reading it was not touched. That is runbook 20's other half, and it is now a check:
any sentence quoting a resolved meeting's odds must name the meeting's date, and
the input must describe a meeting that has actually happened.

The check is narrow and says so in its own comment — it fires only where the value
is quoted, and cannot police tense in general. Pretending otherwise would be the
"right words are present" check this project has been caught writing before.

### A weekday typed beside a date said Saturday on a Sunday

`REVIEW_DATE`'s comment. A weekday written next to a date is a second copy of that
date that nobody maintains. Both weekdays are derived now, and two checks assert
what the comment used to claim: `AS_OF` must be a trading weekday, and the review
date must not precede it. A duplicate ordering check three hundred lines apart was
removed rather than left to drift.

### Hormuz: a count fourteen days stale, and a queue that is not a trend

**IMF PortWatch transits: 6 → 8**, and the 6 was dated **6 September**. PortWatch
publishes weekly on Tuesdays, so some lag is structural — but the reading carried
no date, so nothing could tell structural lag from neglect. Both the reading and
its date are inputs now, with a bound derived from the cadence: two publication
cycles, because at more than that a publication has been missed.

**The vessel queue is a series, not a number.** It was 436 from 30 August, on an
undisclosed basis, and had sat for three weeks. The replacement is three points on
one stated methodology — AIS-visible, holding off berth, excluding ships within
25 km of a working port: **369 (18th), 357 (19th), 376 (20th)**. The first two
alone read as a drawdown; the third says it is oscillating. A check requires three
points before any note calls a direction.

The old 436 is **dropped, not compared against**. Its basis is unknown, so setting
it beside a figure with a stated basis is the mixed-basis error this model already
made once with Goldman's flow reading. The verifier caught the numeral sitting in
prose with nothing to trace to.

### Petroline has a repair timetable, and the notes did not know

They said "still shut", which carries an implied permanence the reporting does not
support. Aramco is bypassing the damaged section, targeting **50% of capacity
within days** and full in **about six weeks**; regional officials put repairs at
**three to five weeks** with only partial flows meanwhile.

Against that, the downside is worse than the notes had: **no Saudi crude has left
Yanbu since 11 September**, stocks there are below **15 million barrels** — a
**four-to-seven-day** buffer — and term cargoes to European refiners are being
cancelled or deferred.

A dated path back is genuinely better than none; a four-day buffer is genuinely
worse. **Geopolitics held at 1.25.** They do not net to a score change and
manufacturing one would be noise.

Kpler's independent Yanbu export loss of **2.5–2.7 mb/d** is about half the 5.0
mb/d the line was carrying — what a line running at the targeted half would cost.
A check asserts that agreement, so if either number moves the note reconciling them
fails rather than quietly becoming wrong.

**The strike date is disputed** and recorded as such: one account dates the
pumping-station hit 10 Sep, another says "last Thursday" — the 11th — from an
18 September story. The shutdown is corroborated and nothing downstream depends on
the strike date, so it is not resolved by picking.

### Re-verified, unchanged

- **PH August CPI 6.1%** — re-checked against PSA and three Philippine outlets
  after one search summary put inflation at "6.2% as of mid-September". That is
  July's figure. 6.1% stands.
- **JEPQ look-through** — 31 July 2026 is still the latest published fact sheet
  and all ten weights match. The 51-day age is JPM's publication lag, not model
  staleness; the 60-day check will fail around 29 Sep if the August sheet is late.
- **BSP forecasts** — 6.1% for 2026 and 5.4% for 2027 both confirmed.
- Portfolio arithmetic re-derived from scratch against the payload alone: all four
  metric sets, all 633 enumerated portfolios, all 29 frontier buckets, the
  correlation matrix (symmetric, unit-diagonal, PSD, min eigenvalue 0.110), the
  drawdown calibration (S&P −20.075 vs −20 observed, NDX −33.100 vs −33), every
  fund's fee stack, FX translation and volatility. Zero mismatches.

### New, and material

**Rice.** August's deceleration came from food falling to 4.6% from 5.2% — while
**rice accelerated to 19.4% from 17.1%**, +2.3pp in a month. The peso note argued
against a fifth deceleration on the oil price alone. A staple re-accelerating like
that is the more concrete risk, and the model was not carrying it.

### Harnesses

Engine 103 → **115**. Verifier 218 → **222**, 0 failures. Checklist 26 → **27**.
Playwright DOM clean.

Twelve new checks. Every one bite-tested by injecting the defect it is meant to
catch — and for the two reconcilability checks the injection had to be
*constructed*, because the defect they guard is invisible until the numbers move.

## 2026-09-19 — The peso came off its record, and three notes quoted a Brent price that was five days dead

A week of resolutions: the Fed hiked, the Bank of Japan hiked, triple witching cleared,
and volatility went back inside the range it broke. Most of what this review found is
the wreckage those resolutions left in prose that was written for the week before.

### "Brent at $109" survived nine days of checks because the check was scoped wrong

Three notes — the Philippines regional note, the inflation driver and the PH CPI
catalyst — said *"Brent at $109 works directly against"* in the present tense while
Brent settled **$103.87**. The prose-vs-input scan passed them every day, because it
asked whether a quoted level matched **some** published Brent input, and $109 is within
tolerance of the dated four-month high of $108.75.

That scoping was deliberate once: it was added so a note could legitimately cite a
dated session high beside the current level. The defect is that it never distinguished
the two cases. A quote only earns the dated inputs by being dated.

The new check separates them, and getting it right took three attempts, each of which
failed its own bite test:

1. **First version** treated a bare year as a date, so *"BSP's own 2027 forecast is
   5.4% — and Brent at $109"* read as dated. A forecast year does not date a price.
2. **Second version** tested whole sentences. One sentence holding both a current
   level and a dated high exempted **both**. Dateness attaches to the quote, not the
   sentence — the check now looks in a 45-character window around each quote.
3. **Third version** still required the literal word "Brent", so the earnings note's
   *"$106 oil"* — no benchmark named — was invisible. Now three patterns cover it.

All four sites bite-tested by re-injection. Catalyst and postponed prose were also
outside the scanned set entirely, which is why the catalyst kept its own private copy
of the stale figure; they are inside it now.

### The peso came off its record and the model carried the record as if it were spot

`usdphp` was **62.68**, the 11 Sep close, described as *"another record low"*. By this
review it was neither current nor the record:

- **62.86** on 14 Sep is the weakest **close** on record (the sixth record of September)
- **62.925** on 15 Sep is the weakest **intraday** print
- **62.749** on 18 Sep is where it actually is, down 1.9 centavos from 62.73

Spot and the record are separate inputs now. Conflating a dated record with a moving
level is what produced the error: the record only ever moves one way, spot does not.

**And the record count was off by one.** BusinessWorld counted 62.625 (8 Sep) as the
23rd record of 2026 and 62.68 (11 Sep) as the **24th**; this model had 23 attached to
the level above it, from launch. 62.86 is at least one more, but no source states its
ordinal and an ordinal cannot be derived from a price, so nothing is asserted.

**The source entry was also describing a figure the model had stopped using.** It read
*"the peso has since printed a FIFTH record of P62.59 on 4 September, **which is the
figure this model uses**"* — while the model used 62.68. Replaced with the three
sources actually behind the inputs.

### "Its highest since 2007" was printed against the wrong number, on the page

The volatility tab said the 10-year *"closed 4.94% after touching **5.02%**, its
highest since 2007"*. The element was fed `ust_10y_prev` — the previous close — while
the intraday peak the superlative belongs to is **5.04%**. It was right only while the
previous close and the peak coincided, and they stopped coinciding on the 18th.

Two duplicate inputs were feeding this confusion: `ust_10y_peak` and
`ust_10y_intraday`, same value, same date, different names. One name now.

The same defect had a second instance: the report tab dated the Brent four-month high
*"on 10 September"* when it belongs to the **15th**. `brent_high_date` is an input now
— a dated figure whose date lives only in prose is a figure whose date is not
maintained.

### The first heading on the page was a hard-typed number, one tenth wrong

`<h2>A 2.7 market: strong earnings, hostile policy</h2>` sat above a gauge reading
**2.39**. Neither C1 nor C2 could see it: both scan only elements carrying
`class="num"`, and a figure written straight into an `<h2>` carries nothing. C1 would
not have flagged it even if it had scanned — 2.7 traces, because it is also the CPI
food print.

**New check G**: a heading either carries no number, or gets it from an element with an
id. Bite-tested by re-injection.

### What the stale VIX strip costs is now measured, not disclosed

The strip has not been re-quoted since 4 September — **15 days**, the ninth consecutive
day of searching without a fresh one. Until now that was disclosed and left there. A
stale strip ages silently, because the spot paired with it ages in lockstep and every
internal consistency check still passes.

**VIX3M is a free test.** It is a market-published constant-maturity 3-month implied
vol, and it is not an input to the bootstrap. Re-anchor this curve to the spot of the
VIX3M observation date, integrate to three months, and it reads **17.68** against a
published **18.60** — **−4.97%**. Same t=0, same strip, so the residual is the strip's
age and nothing else.

The sign matters and is now stated on the page: this model's implied volatility is
**low** against the market's, so its forecast drawdowns are if anything a touch
shallow.

Two new checks bound it. The residual itself, at ±10% — derived, not picked: moving
every future 10% moves the residual 6.7 points, so the band passes a correct curve,
fails a strip priced 10% too low (−11.7%) and fails a flat curve (−14.8%). And a hard
stop once the strip passes **one 30-day roll window**, because past that the front
contract it was quoted against has settled and the curve describes contracts that no
longer exist. The bound is `VIX_FWD_WINDOW_D`, the same constant the maturities are
derived from.

### The page claimed the curve had moved. It had not.

*"Move the curve and that number moves with it; this week it moved, and the sleeve's
edge grew."* The ramp is `blend − curve spot`, and both legs come from the 4 Sep
curve, so the ramp cannot move until the strip is re-quoted. What moved was delivered
volatility, toward the curve rather than the curve toward it.

### October odds were printed as September odds

The report tab: *"FedWatch puts **the 16 September hike** at 50.9%"*. The September
hike happened on the 16th. 50.9% is `fed_hike_odds_oct`. The field was correctly
renamed when the meeting resolved; the prose that read it was not.

### Resolved and carried forward

- **BoJ hiked 18 Sep, +25bp to 1.25%** — highest since 1995, **7–2** (Asada and Sato
  dissenting), three months from the last move against six before it. **The yen FELL**,
  USD/JPY 156.86, a two-week low: a hike that weakens the currency prices the end of a
  cycle, not improving carry. The board tightened into core CPI that had **slowed** to
  1.7% from 1.8% hours earlier, on a demand gauge at 1.9%.
- The resolved BoJ catalyst was removed from the pending list.
- **18 Sep session**: S&P 7,650.50 (+0.17%), Nasdaq 26,522.55 (+0.39%), Dow 51,682.64
  (−0.18%). Week: −0.1% / +0.7% / −1.7%, the Dow's third straight losing week and worst
  since March. Chain verified: 51,682.64 + 95.40 = 51,778.04, and 95.40/51,778.04 =
  0.18% ✓.
- **Brent $103.87**, WTI **$100.30**, 10-year **4.94%**.
- The 15 September VIX note on the page still said the close was withheld. It was
  resolved on the 17th as a **dating** error, not a level dispute; the page now says so.
- The `vix_spot` commentary still read *"has since fallen BACK toward the 2026 low …
  which widens the gap to the futures curve"*. It did the opposite.

### A sentence read "from one market close, , and the strip has not been re-quoted"

Two `<b>` elements printed the curve's quote date and **both carried `id="vquoted"`**.
`getElementById` returns the first match, so the second was never filled and rendered
as nothing between two commas.

Nothing could see it. The payload was right, the setter reported success, no JS error
was thrown, and every data-level check passed. It was found by looking at the rendered
page.

**Checks H and H2**: no duplicate element id anywhere on the page, and no element the
renderer targets may render empty. Both bite-tested by restoring the duplicate.

### Scores

**Volatility & risk appetite 2.5 → 3.0.** What earns it is structural, not price: the
three dated events holding a premium in the front of the curve — the Fed hike, the BoJ
hike, a triple-witching expiry — all cleared without a volatility event. Geopolitics
was deliberately **not** raised beside it: crude easing 4.5% off a peak is a price, and
the Petroline bypass is still shut.

Gauge 2.37 → **2.39**. Weights unchanged at 15/50/30/5.

### Harnesses

Engine 100 → **103**. Verifier 212 → **218**, 0 failures. Checklist 23 → **26**.
Playwright DOM clean, no JS errors.

**Twelve new checks, every one bite-tested by injecting the defect it is meant to
catch** —
and three of them failed their first bite test and had to be rewritten before they bit.
Both the undated-crude rule and the strip-age bound exist in the engine *and*
independently in the verifier, which never imports the engine; the verifier also
re-derives the VIX3M residual on its own 200,000-point Riemann sum. Catalyst and
postponed prose were outside the verifier's prose scan too, and are inside it now.

## 2026-09-17 — The Fed moved, and yesterday's withheld print turns out to have been mis-dated

The FOMC hiked. Yesterday's decision to withhold a VIX close that would not chain is
resolved, and it resolved in favour of the discipline rather than against it.

### The Fed raised to 3.75-4.00%, unanimously

First increase since 2023, and the three July dissenters carried the whole committee.
Warsh: the Fed had "removed a dose of accommodation" and would deliver a "timelier
return" to 2%. The dot plot is the harder part — median end-2026 policy rate **4.1%**,
with **12 of 18** participants at 4.125% and another **4 at 4.375%**, so 16 of 18 see
at least one more hike this year and a quarter see two. October is close to a coin
flip at 50.9%; cumulative odds of at least one more by December are 88.5%.

The 10-year closed **5.016%**, back above 5%. Equities reversed intraday gains once
Warsh spoke: S&P 7,551.81, Dow 51,461.90 (−1.21%), Nasdaq 25,978.42. Brent settled
**$105.83**, off the $108.75 high.

Monetary policy cut 2.5 → 2.25; gauge 2.39 → 2.37. Weights unchanged at 15/50/30/5.

### The withheld VIX print was real — and mis-dated

Yesterday this model refused to publish a 15 September close reported as *"16.93,
down 0.27 points or −1.57%"*, because those three figures could not chain off a
corroborated 17.10 prior.

They were correct figures. They belong to **16 September**. The missing link is a
**17.20** close on the 15th, against which −0.27 and −1.57% both reconcile exactly.
The chain now reads 17.10 → 17.20 → 16.93 and closes without a residual.

This is the clearest vindication the chain rule has had. Publishing those numbers
yesterday would have put a real close on the wrong day and broken the series; the
rule caught a **dating** error, not a value error, which is the harder of the two to
see. Both closes are now carried.

### The September-odds field outlived its meeting

`fed_hike_odds_sep` described a decision that has happened. An input named for a
pending event that has since resolved is worse than a stale number — it asserts the
past is still open. Replaced with `fed_hike_odds_oct` and a cumulative December
figure, the check that reads the FedWatch sentence repointed, and the FOMC catalyst
rolled from 16 September to 28 October.

Same class as the postponed Oman talks on the 14th: **a catalyst list is only honest
if entries leave it when they resolve.**

### The page broke again, the same way

Renaming that field and `ust_10y_intraday` left three `toFixed()` calls on
`undefined`. Engine 100/100 and verifier all-green while the page threw on load —
`validate.js` caught it.

**Third time in four days.** The pattern is now unmistakable and worth stating as a
rule rather than an observation: *every* rename or removal of a payload field is a
page change, because the page reads the payload by name. The data-level harnesses
cannot see it by construction. The runbook now says to grep the page for a field
name before renaming it, not after.

### Also

- Catalysts went out of date order when the FOMC entry was rolled to October — caught
  by the ordering check, which exists precisely because a list that looks sorted is
  not the same as one that is.
- Four prose figures went stale behind the input changes ($104.61, $96, +66.0%,
  +7.95%) and were caught by prose traceability rather than by eye.

**Checks: engine 100, independent verifier 212, requirements checklist 23/23.**

## 2026-09-16 — The strip rolled, a refactor that deleted four inputs, and a VIX close that would not chain

FOMC day, and the day the September VIX contract settles. The expiry guard written
on Monday fired on schedule, which is the first time a check here has caught
something before it became a defect rather than after.

### The strip is rolled

The September contract settled today and is dropped: a settled contract is not a
forward price. The three that remain are still 4 September quotes — a sixth day of
searching produced nothing but the same levels beside a spot near 14.9, which dates
them rather than confirming them. Dropping the front contract moves the horizon blend
by 0.04 and changes **no** fund's volatility tilt, so the roll is safe; the curve now
runs on 3 contracts and 4 knots, and the page says so.

### Market inputs refreshed

The 10-year closed **5.00%** on 15 September after touching **5.04%** — its highest
since 2007. Brent settled **$108.75** (+66.0% y/y), WTI $105.83, and equities have
fallen in six of the last seven sessions. FOMC odds 92%. Volatility & risk appetite
cut 3.0 → 2.5 and growth 4.5 → 4.0; gauge 2.44 → 2.39. Weights unchanged.

### A VIX close that would not chain

The 15 September close was reported as *"16.93, down 0.27 points or −1.57%"*. Those
three cannot all be true against a 17.10 prior: −0.27 gives 16.83 and −1.58%, while
16.93 is −0.17 and −0.99%; for −1.57% to land on 16.93 the prior would have to be
17.20. **No close is published for the 15th.**

The 14th, by contrast, is solid — and by arithmetic rather than by counting sources.
One outlet dated the +7.95% move to the 15th, but 15.84 (a confirmed 11 September
close) × 1.0795 = 17.10, and the session after Friday the 11th is Monday the 14th.
The chain settles the date.

### The VIX fields were refactored into a series — and the refactor deleted four inputs

`vix_latest` / `vix_next_close` / `vix_prev_close` / `vix_prev` / `vix_spike` had
grown around a single two-day episode and did not generalise: adding two more closes
would have needed another pair of fields. They are now one `vix_history` list with
everything derived from it, so the move percentage is computed rather than asserted
and cannot disagree with the levels.

**The replacement range ran past its intended end and silently deleted
`spx_close`, `wti_settle`, `brent_wk_pct` and the equity levels.** Nothing caught it
directly: the "every published input is cited" check finds *orphaned* inputs, not
*removed* ones. What surfaced it was the prose that cited them failing traceability —
a check built for a different purpose catching this one sideways. Restored.

Three new checks on the series itself: every close on a weekday, dates in order with
no duplicates, and the published move reproducing from the last two closes. The
verifier re-derives the whole chain rather than just the last pair.

### A lag that is now stated rather than silent

Withholding the 15th leaves the VIX series one session behind `AS_OF`. That is the
right outcome, but a *silent* lag is not: a check now reports the gap in its own name
and fails beyond five sessions. A series that quietly stops tracking is the failure
mode this is for.

### The page broke and the engine could not see it

Removing those fields left four `toFixed()` calls on `undefined` in the volatility
lede. **All 100 engine checks and all 212 verifier checks passed** while the page threw
a JS error on load — both harnesses read the payload, and the payload was fine.

`validate.js` caught it. This is the second time in three days that a page-level
failure was invisible to the data-level checks (the catalyst block on the 14th was
the first), and it is the same lesson from the other direction: **the payload being
correct says nothing about the page working.** The lede is rewritten around the
current picture rather than patched.

### Also

- `$105` was still being quoted as the *current* Brent level in three notes. It passed
  the traceability guard by matching the prior settle at $104.61 — traceable, and
  wrong for what the sentence claims. A figure can be sourced and still be the wrong
  figure for its sentence.
- One of my own edits duplicated "a four-month high" inside a sentence. Caught by
  reading the rendered output rather than by any check.

**Checks: engine 97 → 100, independent verifier 209 → 212, requirements checklist 23/23.**

## 2026-09-14 (second pass) — The Hormuz bypass was shut, and both harnesses carried the same wrong constant

Research turned up two developments that matter more than anything in the code, and
the code review found a tolerance that was wrong in *both* the engine and the
supposedly independent verifier.

### The bypass is shut

Drone strikes launched from Iraq on 10-11 September hit Saudi Arabia's **East-West
(Petroline) pipeline** and Riyadh closed it on the 11th; satellite imagery shows fire
damage at a pumping station. That 1,200 km line to Yanbu on the Red Sea was moving
roughly **5.0 mb/d specifically to route around the Strait**.

This undercuts the offset this model was leaning on. Goldman's "two-thirds of pre-war"
reading — 15.5 mb/d against a 23.0 mb/d baseline, published here two days ago — is
dated **28 August**, and a material part of what it measured ran through the line
that is now shut. No post-shutdown flow figure has been published, so none is
invented: the flow reading now carries its own as-of date and the note says plainly
that two-thirds is the last measured level and is **stale in a knowable direction**.

### The diplomacy was called off

The Oman meeting at which Iran was to unveil the temporary shipping lane agreed with
Muscat was postponed on the day, "in the interests of consensus", with no new date.
Last week's note said this model was not pricing that diplomacy. That was right.

It is no longer a dated catalyst, but it is **not dropped either** — a new
`POSTPONED` block carries it, because "the thing that was going to settle this did
not happen" is information, and silently removing the row would read as though the
meeting had gone ahead.

Geopolitics & energy cut **1.5 → 1.25**. Still not at the floor, for the same reason
as before: the stress table models full closure and Brent above $130. Gauge 2.46 → 2.44.

### Monday's close: mislabelled data, discarded

One search returned S&P 7,657 / Nasdaq 26,333.04 / Dow 52,573.29 / VIX 15.84 as
Monday's close. Every one of those is **Friday's** figure to the decimal, and
same-day reporting had Monday *falling* on oil and AI names. A day cannot be both
+0.9% and lower. Discarded, and recorded in CLAIMS as discarded. Market inputs stay
at Friday's close.

### A hand-picked tolerance, wrong in both harnesses

Cutting a driver to 1.25 broke the check that the weighted composite of the reported
1-5 scores equals the headline gauge. The error was **0.0065** against a hand-picked
tolerance of **0.006**.

The score was not the problem. Each reported score is `to5()` rounded to 2dp and the
weights sum to 1, so the composite carries up to 0.005 of rounding, and the gauge
itself rounds for another 0.005: the **derived** bound is 0.010. The 0.006 had been
passing only because the scores happened to round favourably.

Worse, the independent verifier carried **the same 0.006** and failed the same way on
the same day. Both sides wrong in the same direction is exactly what an independent
verifier exists to prevent — and it did not, because the constant had been *copied*
rather than re-derived. Both are now derived from publication precision.

This is the second time a hand-picked tolerance has been the defect rather than the
check (the first was 0.0614 against a hand-picked 0.06 on 2026-09-06).

### A tolerance left behind by a precision change

Yesterday `port_k` moved from 3dp to 5dp. The check that the portfolio k equals the
ex-cash weighted average still allowed **0.006** — roughly **1200x** looser than a 5dp
figure warrants, and it would have passed a materially wrong average. Now derived
from the published precision, and verified to bite on a 0.001 perturbation that the
old tolerance swallowed. The tech-gap check had the opposite problem, 0.006 where
three 2dp figures propagate to 0.015 — too tight is a defect too, it just waits
longer to fire.

**The rule these three share:** a tolerance is only as good as the precision it was
derived from, and it must move when that precision moves. A copied constant does
neither.

**Checks: engine 97, independent verifier 209, requirements checklist 23/23.**

## 2026-09-14 — A contract that expires on Wednesday, and a tolerance that policed itself

Monday. No 14 September market data was reported yet when this ran, so the market
inputs stand at Friday's close; `REVIEW_DATE` moves to today, `AS_OF` stays at
2026-09-11. Research corrected one date, and the code review found three defects
plus two flaws in checks I wrote during the same pass.

### The front VIX contract settles on Wednesday and nothing knew

The strip's September contract settles **16 September**. Maturities are measured to
the centre of the 30-day window each contract prices, so the front maturity stays
*positive* until 1 October — which means the existing "maturities are positive and
strictly increasing" check would not have fired for another fortnight, while the
bootstrap interpolated through a contract that had stopped trading.

Now checked against `REVIEW_DATE`, so it fires the day a contract expires. Verified
by moving the review date to Thursday: both the expiry guard and the days-to-front
check fail.

### The BoJ catalyst was on the wrong day

Listed as 17 September. The Bank of Japan meets **17-18** and the decision lands on
the **18th**. The FOMC entry was right (15-16, decision the 16th) — the error was
dating one two-day meeting from its start and the other from its decision.

### Scenario drawdowns did not reconcile, for the third time

Two of the ten stress rows were 0.1 out from their own printed cagr and vol. This is
the same defect as the peso figures (2026-09-03) and `ret_per_dd` (2026-09-11): a
published figure computed from raw values while its inputs print rounded. Each time
it was fixed where it was found rather than everywhere the pattern occurs.

The substantive cause here was different, though, and worth separating: the
**published `port_k` was lossy**. At 3dp, the AI-capex row reconstructs to −42.34
from the exact coefficient and −42.35 from the published 1.618 — which print as
−42.3 and −42.4. Published at 5dp now. Rounding the scenario inputs as well is a
consistency fix, not a caught bug, and it is recorded as such.

### The stub counterfactual could have dropped a second fund

`_best_without(3)` forces Global Technology to zero and re-optimises. It required
non-zero sleeves to be at least 5% — but permitted *other* sleeves to be zero too,
so a two-fund portfolio like [50, 50, 0, 0] was reachable. The stub's "cost" would
then be measured against something the objective forbids, which is precisely the
error the concentration-cap guard beside it was added to prevent.

It is not binding today — the answer is [15, 50, 35, 0], holding all three — so this
is a latent bug closed by reasoning rather than by a failing test, and it is recorded
that way rather than dressed up as a catch.

### Two checks I wrote in this same pass were wrong

**A check that compared the engine to itself.** The new scenario-reconstruction check
computed `round(port_k(OPT_W), 5)` locally instead of reading the published value —
so it could not detect the payload publishing a lossier figure, the one thing it
existed to catch.

**A tolerance that policed itself.** Having fixed that, the check still would not
fire. It used a bound derived from half a unit in the last published place of each
input, propagated through the drawdown formula. That bound is correct and useless:
as `k` is published less precisely its error term grows, so the tolerance grows in
lockstep with the error it is meant to police. Three bite tests passed in a row
before this became obvious.

The honest question was never "is the error inside a bound I derived" but "does a
reader reconstructing from the published row land on the printed number". That is
now asserted directly, with no tolerance to get wrong — and it fails immediately at
3dp and 2dp.

This is the fourth first-run-green check in a week. Yesterday's note said a check
written as "the right words are present" rarely holds while one written as "the
quantities stand in the right relation" usually does. Today adds the sharper
version: **a tolerance derived from the same quantity it is checking cannot detect a
defect in that quantity.** When the check and the thing checked share a parameter,
the check is a tautology wearing arithmetic.

### The catalyst block had been missing from the page for three days

The worst find of the pass, and it was found by eye rather than by any check.

The **"Not in these numbers yet"** block — the pending-catalyst list added on
10 September — was deleted from the markup by the conciseness edit on the 11th. That
edit replaced the whole "Keeping this current" section, and the catalyst card sat
inside the replaced range. Three days, three reviews, and nothing caught it:

- The payload still carried all four catalysts.
- The engine still checked they were in date order and still pending.
- The verifier still re-derived them independently.
- `validate.js` reported **no JS errors** — because the renderer opens with
  `if (!host || !D.catalysts) return;`, so a missing mount point is a silent no-op.

Every check validated the data. None validated that the data reached the screen. The
defensive guard I wrote to make the renderer robust is exactly what hid its absence.

Restored, and **check F** added: every payload collection the page is meant to render
must actually appear in the DOM — exact counts for lists (catalysts, sources, fund
slides), at-least counts for charts that legitimately draw extra marks. Verified by
deleting the mount point again.

Two of the five selectors were wrong on the first run, and both were mine rather than
the page's: the driver list has 7 drivers plus a weighted-composite row, and the
frontier draws 42 circles for 29 points because it marks both portfolios. Checked
before filing.

**Checks: engine 95 → 97, independent verifier 209, requirements checklist 22 → 23.**

## 2026-09-13 — Stale reference data, and a magic number that turned out to be right

Sunday. No market data since Friday's close, so this was a scrub of the things that
do not move with the tape — and most of what it found had been sitting there for
weeks.

### The 2026 VIX low moved on 4 September and the model did not notice

The page carried **14.18 (17 August)** as the year's low, which is what it was when
the model adopted it. On **4 September the index slid to 13.80** just before the
payrolls release, then rebounded to close 14.32. The low had been superseded for nine
days. Both are now carried — the August print is still cited historically, but it is
no longer the low — and the source entry that called 14.18 "the complacency baseline
this model measures the ramp against" is corrected: the ramp is measured against the
curve, not against either low.

The same research also re-dated the one-month high: two accounts put the spike peak
at **16.82 on 2 September**, not 16.80 on the 1st. That is coherent with the 2 Sep
*close* of 16.34 being the spike; a 1 Sep intraday high above a higher 2 Sep close
was not.

### A magic number, finally sourced — and it was right

`vol_beta` for the covered-call sleeve was `1.22 * 0.68`. The **0.68** had been an
unsourced constant since launch, flagged as undocumented on 10 September and never
resolved. J.P. Morgan's own JEPQ fact sheet (31 July 2026) publishes a
since-inception annualised standard deviation of **13.9%** against the Nasdaq-100's
**20.4%** — a ratio of **0.681**.

So the constant was right to two decimals, and had been for months. That is worth
being clear about: being correct is not the same as being *sourced*, and an unsourced
number that happens to be right is still a number nobody can check. It is now derived
from the two published figures, both are in the payload, and the independent verifier
reads them from there rather than hard-coding its own copy — it had been carrying the
same `1.22 * 0.68` on its side, so the two agreed with each other and with nothing
else.

The other two vol betas (Asia 1.05 × 0.92, Global Tech 1.30) remain **assumptions**
and are now labelled as such in the code and in CLAIMS.md. Fidelity publishes a 3-year
annualised volatility of 17.23% for the Global Technology fund, which implies a ~1.30
beta only if S&P realised vol over that window was ~13.3% — plausible, unverified, and
not the same quantity, since this beta applies to forward implied vol. Recorded as a
cross-check, not a confirmation.

### Look-through data was a month and a half stale

The JEPQ table was on the **30 June** fact sheet, 73 days old. On the 31 July sheet,
**Tesla has left the top ten and Broadcom has entered**, and six of the ten weights
had moved. The existing check only asked whether the weights summed to a plausible
30-60%, which a stale-but-coherent table passes comfortably.

Fidelity's sector breakdown had moved too — every weight, and the residual line
changed from "Managed funds 0.94%" to "Cash and equivalents 0.47%".

Both refreshed. New checks: look-through data must be within 60 days of the review
(one monthly publication lag and no more), and weight-ranked rows must descend.

### Three date problems underneath that

- The money-market look-through was dated **"2026-08"** while carrying *today's*
  T-bill yields — and it carried them as a hand-typed copy of `MACRO`'s values with
  nothing tying the two together. Now derived from the same inputs and dated properly.
- The Fidelity entry was dated **"2026"**. A year is not a date and cannot be checked
  for staleness. It is now the retrieval date, with the note saying so explicitly:
  Fidelity's page does not publish its own snapshot date at the source reachable from
  here, so the figures are its latest month-end, not a 13 September position.
- Fixing those exposed a conflation the model had lived with from the start.
  **`AS_OF` and the review date are different things.** `AS_OF` is the market data
  date — the last trading session every price comes from. On a weekend review,
  reference data retrieved during the review is legitimately *newer* than the market
  snapshot; the first version of the freshness check called that "stale by −2 days".
  `REVIEW_DATE` now exists alongside `AS_OF`, both appear in the footer, and a check
  asserts the review is never before the market date.

### Two of my own checks were wrong before the data was

- The ordering check flagged the money-market rows as out of order. They are a yield
  **curve**, ordered by tenor: 5.138 / 5.517 / 5.717 ascends correctly. Scoped to
  weight-ranked kinds.
- C1 scanned only static markup, so figures hard-typed into the page's own JavaScript
  prose maps were invisible — the money-market bullet carried a `"Live curve: 91d
  5.14% · 182d 5.52% · 364d 5.72%"` copy of the T-bill inputs. Derived now, and C1
  extended to scan those maps.

C1's extension also confirmed yesterday's finding again. Injecting a wrong `4.11%`
into that bullet, **C1 passed** — 4.11 coincides with something among ~400 payload
numbers — and **C2's ratchet caught it**. Value-matching cannot catch a wrong figure
whose value collides; only the ratchet stops one being introduced.

### One thing I checked and did not file

The Asia fund's slide appeared to show "~72% US · ~16% Asia · ~12% Europe", which
would be the Global Tech index mix on the wrong card. It was not: reading the slides
individually shows each has its own bullets. The apparent overlap was an artifact of
`innerText` concatenating across sibling cards in my query, not a rendering bug.

**Checks: engine 88 → 95, independent verifier 209, requirements checklist 22/22.**
Six new checks verified to bite.

## 2026-09-12 — The page's central geopolitical claim was contradicted by its own oil price

Saturday, markets closed, so the 11 September inputs are complete for the week.
Research closed the last two open gaps and turned up a substantive error in the
driver that carries the portfolio's largest macro risk.

### "A ~93% shutdown" was the wrong measure

The geopolitics note read the Hormuz disruption off **vessel counts** — 6 transits a
day against a ~85 baseline — and called it *"a ~93% shutdown"*. Two things are wrong
with that.

**The vessel counts themselves disagree by about five times.** IMF PortWatch logs 6 a
day across all transits; Lloyd's List Intelligence logs 14, counting only cargo
vessels over 10,000 dwt; the US government claims around 30. Al Jazeera ran a piece
on 3 September specifically about the gap between US-claimed transits and ship-tracker
data. This model published one of those numbers as settled fact.

**More importantly, vessel count is not supply.** Goldman puts Gulf crude and product
exports at 15.5 mb/d against a ~23 mb/d pre-war baseline — about two-thirds, up from
a 5.5 mb/d trough in March — with roughly 5 mb/d moving through dark crossings and
ship-to-ship transfers. That is about a **third** of supply lost, not 93%.

The tell was internal, and it had been sitting on the page for days: **$105 oil is
not what a 93% shutdown prices.** The model's own Brent input contradicted its own
geopolitics narrative, and nothing was comparing them.

Both measures are now published and both appear on the page, with the point stated
plainly: they measure different things and the oil price follows the volume one. The
score is **held at 1.5 rather than raised** on the flows recovery, because that
recovery is already in the $104.61 price — crediting the driver for it would count
the same good news twice.

Four checks added, three verified to bite.

### A mixed baseline inside the fix

The first version of the correction paired Goldman's 15.5 mb/d with a 20.0 mb/d
baseline taken from a different source measuring Hormuz transit alone. That gives a
22% loss — which flatly contradicts Goldman's own "two-thirds" headline. Their note
says exports are 15-16 mb/d and "still 7 to 8 mb/d below pre-conflict", so their
baseline is ~23, and 15.5/23.0 = 67%.

Caught because the percentage is **derived rather than typed**: printing it showed 22%
where the source said a third. Two measures of the same strait are not
interchangeable just because both are quoted in mb/d. The baseline is now tied to the
source's own pair by a check.

### Gaps closed

- **The 11 September VIX close is confirmed: 15.84, −11.21%.** Yesterday only a midday
  −12.50% was available. The close also corroborates the 10 Sep figure arithmetically:
  15.84 / (1 − 0.1121) = 17.84, against one outlet that printed "near 17.89".
- **Iran and the GCC meet in Oman on Monday 14 September** — now a catalyst, and the
  single largest swing factor for the energy driver. One search summary dated it the
  15th; the Monday after Friday 11 September 2026 is the **14th**.
- The VIX futures strip still has no fresh quote. Third day open, still recorded open.

### Prose traceability — the hole flagged yesterday, now closed

checklist.js C1 scans only the static page markup, so numbers written into the
**payload's own notes** were never checked. That is how the monetary note kept
asserting the 10-year "closed 4.92%" after the input moved to 4.96%, and the earnings
note kept "$106 oil" against a $104.61 settle — the Brent guard missed the second
because it only looks within 20 characters of the word "Brent".

The verifier now requires every number in every driver, region and fund note to be a
rounding of some payload quantity. It flagged 15 on its first run. Two were the stale
figures above. The rest were **model assumptions living only in prose with no
published counterpart** — the 78% covered-call upside capture, the 1.3pp NDX growth
premium, the 5.25% pre-lengthening short-rate assumption, the Nikkei and KOSPI closes,
Lloyd's 10,000 dwt threshold. All are now inputs, which is where a number that moves
the model belongs.

Exclusions are stated rather than fudged: calendar years are labels, tenors like
"364d" are identifiers, and index names that contain a number ("S&P 500") are names.

### A check that passed while its subject vanished

The bite test caught one of the new checks failing to fail. "The disputed vessel
counts are all published" tested that three strings appear in the note — so collapsing
all three counts to the same number passed it, while the disagreement the check exists
to record had disappeared. It now asserts the counts are distinct and the spread is
at least threefold.

That is the third time a first-run-green check has turned out not to bite. The
pattern is consistent enough to name: **a check written as "the right words are
present" almost never holds; one written as "the quantities stand in the right
relation" usually does.**

**Checks: engine 82 → 88, independent verifier 208 → 209, requirements checklist
22/22.**

## 2026-09-11 (second pass) — The breakout reversed, and a driver was scored below its own stress row

Full checklist run plus a research pass to close the three gaps recorded this
morning. All 22 requirements pass. Two of the three gaps are closed with confirmed
figures, and the volatility call published earlier today needed correcting within
hours.

### The correction

This morning's page was headlined **"The calm broke — from the spot side"**, on the
10 September VIX close of 17.84. The very next session reversed most of it: the
S&P 500 rose 0.86% to 7,656.98, its first gain in five; WTI settled down 2.4% at
$100.05; Brent settled down 2.8%; and the VIX was **−12.50% at midday** on news that
Tehran will meet Gulf states in Oman about the Strait.

So the range break did not hold. The headline is now **"A range break that did not
hold"**, and the driver note says plainly that this model has twice mistaken a single
session for a regime change and is not doing it a third time. No confirmed 11 Sep VIX
close was found, so none is carried — the reversal is recorded as the intraday move
it verifiably was.

### A driver scored below the worst case on its own page

Geopolitics & energy was at **1.0, the floor of the research scale**, with a note
saying the driver had "no room left to worsen". On the same page, the Hormuz row of
the stress table models full Strait closure and Brent above $130 against a settle of
$104.61 — a strictly worse state. Both cannot be true.

Raised to 1.5, and the inconsistency is now machine-checked: no driver may sit at the
scale floor while the page models a state worse than the one it describes. The
closure level is published as an input so the scenario and every note citing it
cannot drift apart. Verified to bite.

### Gaps closed

- **Brent now has a confirmed settle** — $104.61 on 11 Sep, −2.8% on the day, +8.7%
  on the week, still above $100. This morning's figure was a timestamped intraday
  print because sources spread $102–108 with no settle confirmed.
- **The 2-year Treasury yield is no longer stale** — 4.63% on 11 Sep against the
  4.377% carried since 7 Sep, a 25bp move. The 10-year is 4.96% and the 30-year 5.36%.
- **The VIX futures strip still has no fresh quote.** Every source found still echoes
  the 4 September levels beside a spot near 14.9. The curve stays on its quote date;
  the gap remains open and is recorded as open.

### A new check, and a flaw in it found by its own bite test

The verifier now asserts that **every published input is cited somewhere** — in code,
in prose, or in the page markup. This is the inverse of checklist C1: C1 says every
figure on the page traces to an input, this says every input reaches the page.

It matters more than housekeeping. An uncited input is a number sitting in the
payload that can whitelist a *wrong* page figure by coincidence — which is exactly how
a stale −40% drawdown passed C1 yesterday, by matching an unrelated frontier weight.
Fewer unused numbers means a stricter C1.

It immediately found eight orphans, most created by yesterday's conciseness pass:
`ust_10y_wk_high`, `ust_2y`, `ust_30y`, `ea_hicp_2027`, `ph_core_jul`,
`bsp_infl_2027`, `brent_wk`, `ltcma_6040plus`. Five were dropped as no longer earning
their place; three were freshly researched and are now cited in the notes.

**The first version of this check was broken, and its own bite test caught it.** A
probe input of 1234.56 was reported as cited. The cause: the check generated an
"abbreviated thousands" candidate as `value/1000` rounded, which for anything between
1000 and 9999 produces the token **"1"** — and "1" matches somewhere in any document.
Worse, that bug had made the check pass on the eight real orphans above, so its first
green run was false. Fixed by only generating that candidate when it is a distinctive
token, and requiring every candidate to be at least two characters.

Two lessons, both already in this file in other forms: a check is not verified until
you have watched it fail, and a check that passes on its first run deserves more
suspicion than one that fails.

### Also

- The US note still said the 10-year "closed 4.92%" after the input moved to 4.96%.
  Payload prose is not covered by C1, which only scans static page markup — noted as
  a remaining hole rather than papered over.
- `checklist.js` requirement 6 was still labelled "net 5y CAGR" three days after the
  mandate went to ten years. The check itself was correct; only its name was stale.

**Checks: engine 81 → 82, independent verifier 207 → 208, requirements checklist
22/22.** Both new checks verified to bite.

## 2026-09-11 (editing pass) — Made the page concise, and found three stale figures doing it

Asked to make the page concise. It is **28% shorter** — 54,333 to 39,062 characters
of rendered text, 30.2 to 22.7 phone screens — with no requirement dropped: still
81/81 engine checks, 207 verifier checks and the full requirements checklist.

### What was cut

- **Driver and region notes, 10,845 → 4,937 chars.** These had accumulated a running
  commentary on the model's own past mistakes — "this model said last week…",
  "previously MARKED DOWN from 6.05…", "the previous read was wrong in an instructive
  way". That history is real and worth keeping, but its home is this file, not a
  driver tile on a phone. The notes now lead with the judgement and the two or three
  numbers behind it.
- **The on-page review runbook, ~1,100px.** It duplicated `monitoring/README.md`,
  was an operator's checklist rather than anything a reader of the portfolio needs,
  and had itself gone stale (it still described the VIX bootstrap as "spot plus the
  two nearest futures"; it has used four contracts since 8 September). Replaced by
  the one paragraph that matters: nothing refreshes itself, the header carries the
  as-of date, and the procedure lives in the repo.
- **The sources list, ~2,650px** — nearly three phone screens. All 37 sources and
  every link are still there, now behind a `<details>` summary showing the count.
- The drawdown-model card, the report's setup and conclusion sections, the peso note
  and the fee-provenance note, all trimmed without losing a claim.

### Three stale figures found while editing

Reading the page closely for length is a different pass from checking it for
correctness, and it turned up three things three days of audits had missed:

1. **Global Technology's drawdown was printed as −40%** against a modelled **−57.6%**.
   Hard-typed, and 17 points wrong.
2. **"Bootstrapped piecewise from the three observable points"** — the curve has used
   five knots (spot plus four futures) since 8 September.
3. **"Spot fell back toward its 2026 low while the curve held"** — last week's story,
   printed in the week spot broke out to 17.84.

All three now render from the payload.

### The check that should have caught them, and did not

`checklist.js` carried a check named "no stale hard-typed figures found this pass".
It was a **denylist of specific strings from past incidents** — `16.44`, `0.23pp`,
`out of 969`, and so on. A denylist can only catch a figure that has already been
found stale once. It passed clean on all three of the above, because they were new.
This is the same failure mode as the targeted prose guards on 9 September: a list of
yesterday's mistakes is not a detector.

Replaced with the positive form of runbook invariant 3, in two parts:

- **C1 — traceability.** Every hard-typed number in the static markup must be a
  rounding of some payload number. Getting to zero violations required publishing
  `regional_tilt_per_pt` and a derived `real_yield` block, which were the last two
  page figures with no payload counterpart.
- **C2 — ratchet.** C1 has a limit worth stating plainly: it cannot catch a figure
  whose *wrong* value happens to coincide with an unrelated model number. The −40%
  is exactly that case — 40.0 appears in the payload as a frontier weight — so C1
  alone would not have caught it either. C2 freezes the count of hard-typed figures
  at 41, all of them inputs and constants. A new hard-typed figure cannot be added
  without tripping it. Verified by reinstating the −40%: C1 passes, C2 fails.

That pairing is the actual lesson. The first check tells you a figure came from
nowhere; only the second stops a wrong one being typed in the first place.

## 2026-09-11 (research + audit) — The calm broke, and the curve did not move with it

Search was available again after being down for all of 10 September, so this was a
full input refresh as well as an audit. Nearly every macro input moved, the broad
gauge fell 2.65 → 2.43, and the optimised weights did not change at all.

### What actually happened in the market

- **The ECB hiked.** Deposit rate +25bp to **2.50%** on 10 Sep, MRO 2.65%, MLF
  2.90%, effective 16 Sep — the second and final move of its shortest campaign
  since 2011, taken explicitly because the energy shock will hold inflation above
  target for an extended period.
- **August CPI printed on 11 Sep.** Headline **3.4%** unchanged and in line; core
  **2.4%** y/y, better than the 2.5% this model carried; but core rose 0.3% m/m
  against a 0.2% consensus, headline 0.4% m/m with gasoline contributing over a
  third, gasoline **+27.4%** y/y and fuel oil **+52%**. Disinflation intact
  underneath, energy eating it in real time.
- **September FOMC went from a coin-flip to near-certainty.** CME FedWatch
  **58% → 70% → 85.6%** across 4, 10 and 11 September. The US 10-year closed
  **4.92%**, a ten-year high.
- **Brent went through $108** on 10 Sep, highest since 19 May, **+61.6% y/y**
  against +47% a week ago. Saudi output fell ~1.9 mb/d after Houthi strikes; US
  CENTCOM confirmed five Iranian tankers destroyed; tanker rates at record highs.
- **The peso set another record low**, 62.68 on 11 Sep, 62.775 intraday.
- **The VIX broke out.** Closed **17.84** on 10 Sep, +8.38%, after touching 18.17 —
  ending a 28-session range of 14 to 17.

### The judgement call this pass turned on

For three weeks the central claim on this page was that the market was priced for
calm it did not expect to keep: spot near its 2026 low while the curve priced 19+
by December. **That gap has now closed from the spot side.** The obvious move was
to re-anchor the volatility curve on 17.84 and re-run everything.

That would have been wrong, and the model does not do it. The futures strip has
not been re-quoted since 4 September. Every source found on 11 September still
echoes the same four contract levels — 16.57 / 18.41 / 19.08 / 19.26 — *alongside
a spot of about 14.9*, which dates those quotes rather than confirming them.
Splicing a 10 September spot onto a 4 September strip does not produce a newer
term structure; it produces a front-month backwardation that no market printed,
and that artefact would flow straight through the vol ramp into every fund's tilt
and into the optimiser.

So the curve keeps its own spot of 14.32, paired with the strip it was bootstrapped
from and with the `VIX_QUOTE_DATE` introduced yesterday. The latest observation is
published as a separate, separately-dated field, the 3.52-point divergence is stated
on the page rather than buried, and the news is carried by the volatility **driver
score**, which is a judgement, rather than by the curve, which is an arithmetic
object requiring a consistent snapshot. Six checks enforce the separation, including
one that fails if the curve's t=0 is ever silently replaced by the latest spot.

### Scores

Gauge **2.65 → 2.43** (1–5). Geopolitics & energy cut to the **floor** of its scale;
monetary policy 3.5 → 2.5; growth 5.5 → 4.5; earnings 7.5 → 7.0; volatility &
risk appetite 3.5 → 3.0. Valuation support was the one improvement, 7.5 → 8.0 —
the same earnings got cheaper. Regions: US 5.5/5.5/6.0/6.5 → 4.5/5.0/5.5/6.5,
Europe 3.0/3.5/4.0/4.5 → 2.5/3.0/3.5/4.5, Asia 6.0/6.5/7.0/7.5 → 5.0/5.5/6.5/7.5,
Philippines 6.0/6.0/5.5/5.5 → flat 5.5. Every ten-year anchor held; all the cuts
are at horizons under a year, which is what a terms-of-trade shock should do to a
ten-year mandate.

Two notes now record calls that went against this model rather than quietly
dropping them: the Asia note says plainly that last week's read of the early-September
bounce was too generous at the near horizon, and the volatility note says that being
right about the repricing a week later by a different route is **not** the same as
having been right when it first made the call and retracted it.

### Result

Optimised weights are **unchanged at 15 / 50 / 30 / 5** despite every input moving.
Net CAGR 7.58% → 7.49%, drawdown −25.6% → −25.7%, baseline 7.33% → 7.25%. The
allocation is not sensitive to a week of bad news, which is worth more as evidence
than a reshuffle would have been.

### Defects found and fixed

1. **A guard that had stopped biting.** The scenario rows now interpolate the hike
   odds from the input, so the check that "prose matches the input" passed with the
   input reverted to 58 — the prose moved with it. A presence test was no better,
   because the notes legitimately carry the figure's history ("up from 58% a week
   ago"), which satisfies a presence check with a stale number. The guard now reads
   the FedWatch sentence in the monetary-policy note — the one place the live figure
   is asserted by hand — and requires the first percentage in it to be the input.
   Verified to bite.
2. **The Brent guard was too narrow in the other direction.** Written on 10 Sep to
   require every quoted Brent figure to equal spot, it rejected the true statements
   "passed $108 on 10 Sep" and "at $106 rather than $96". The rule should be that a
   quoted figure matches *some published input*, not that it matches spot, so the
   dated high and the prior level are now published and the guard accepts any of the
   three. Same scoping lesson as the $130 counterfactual, in the opposite direction.
3. **The odds check's number format was hard-coded.** It rendered the input with
   `:.0f`, which matched "58%" but not "85.6%", so refreshing the input failed a
   check that was testing the formatter rather than the prose.
4. **`brent_yoy` was a typed constant** beside a typed `brent`. They were consistent
   only because someone kept them so. The y/y is now derived from the level and a
   published year-ago base, so the two cannot drift apart.
5. Stale page narrative: the volatility panel headline and lede, the rationale-report
   lede, the `#volpara` term-structure paragraph and the whole "what changed this
   week" block all still described the calm holding. Rewritten, and every figure in
   them now renders from the payload rather than being typed.

### Honest limits on this pass

- **Brent has no confirmed settle.** Intraday sources on 10 Sep spread $102 to $108.
  The level is carried as a timestamped print ($105.82, 11 Sep 09:15 ET) rather than
  presented as a close, and CLAIMS.md records the spread.
- **One outlet printed two different VIX closes for 10 Sep** — 17.84 (+8.38%) and
  17.47 (+6.14%). Both imply the same 16.46 prior close. 17.84 is carried, confirmed
  by a second independent search, and the discrepancy is recorded rather than hidden.
- **The 2-year Treasury yield is stale.** No 10 Sep print was found; it is marked
  STALE in CLAIMS.md rather than rolled forward on the 10-year's move.
- **Hormuz transits** are 6 on PortWatch's latest published day, reported via search
  rather than read at PortWatch. A separate non-PortWatch estimate put traffic nearer
  10/day on 10 Sep; both are recorded.
- 14.53 surfaced again as a "7 September" VIX print. 7 September 2026 was **Labor
  Day** and US markets were closed, so there is no such close — the same figure this
  model discarded on 2026-09-08 when it was labelled 5 September, which was a
  Saturday. Discarded again.

**Checks: engine 76 → 81, independent verifier 197 → 207, requirements checklist
21/21.** All six new checks verified to bite by injecting the defect they target.

## 2026-09-10 (audit) — A time axis three days off its own prices, and a peso figure that meant something else

**No research was possible this pass.** `WebSearch` was unavailable for every
query attempted and direct fetches are blocked by the egress proxy, so not one
input was refreshed and `AS_OF` stays at 2026-09-09. Everything below is math,
code and internal-consistency work, which needs no network. Six defects.

### 1. The VIX futures maturities were measured from a Sunday

The strip's four maturities were hard-typed constants. Backing each one out
against the contract settlement rule — a VIX future settles the Wednesday 30 days
before the third Friday of the following month, and prices the 30-day window
centred 15 days later — gives an implied base date of **6 September 2026 for all
four**. That is a Sunday. It is neither the quote date (Friday 4 September, the
close every level on the strip comes from) nor `AS_OF` (9 September).

So the forward-variance integration was running a 4 September curve off a
6 September origin: the time axis had drifted away from the prices sitting on it,
and would have drifted further every time `AS_OF` moved without anyone noticing,
because nothing checked a typed constant.

The effect was small — the horizon blend moves 18.93 → 18.92, the ramp 4.613 →
4.595, and one fund's volatility tilt by 0.01pp — but the mechanism was broken,
and 3M implied vol did move 17.43 → 17.35. Maturities are now **derived** from
`vix_settlement()` and a new `VIX_QUOTE_DATE`, so the base date is provably the
quote date. `MACRO["vix_futs_levels"]` carries levels and contract months only;
there is nothing left to type wrongly.

Six checks added. The strong one lives in the independent verifier, which
re-derives the settlement calendar from scratch and asserts that **every
published maturity implies the same base date and that it is the quote date** —
the check that would have caught this the day it was introduced. The engine-side
checks (quote date is a weekday, quote date is not after `AS_OF`, settlements
land on Wednesdays 30 days before a third Friday) are tripwires against
re-hardcoding rather than independent verification, and are described that way.

### 2. "Value at expected trough" was not the trough

The peso illustration printed ₱744,000 under the label *Value at expected
trough*, computed as the drawdown applied to the opening ₱1,000,000. But the same
page defines drawdown as the expected 10-year maximum, **peak to trough**. Those
two statements cannot both hold: at 7.58% for ten years the modelled peak is
about ₱2.08M, so a peak-to-trough drawdown of 25.6% arriving late in the mandate
troughs near ₱1.54M, not ₱744k — a factor of two apart.

The number is worth printing; it is the worst case for money invested *today*,
before any growth cushion exists, which is the number that matters to someone
deciding now. The label asserted the other reading. Renamed to
`worst_1m_from_open`, relabelled on the page as "Worst case for money invested
today", and the note now states explicitly that it is deliberately not the low
point of the modelled path and why.

### 3. Two published ratios could not be reconciled from the published figures

`ret_per_dd` and `sharpe_like` were computed from raw values while `cagr`,
`vol` and `maxdd` printed rounded. A reader dividing the printed 7.33 by the
printed 28.9 got 0.254 against a printed 0.253; two of the four portfolios
failed to reconcile.

This is the *same defect* fixed on 2026-09-03 for the peso figures, whose whole
point was that a reader who multiplies out the displayed CAGR should get the
displayed peso number. That fix was applied to `terminal_1m` and missed the two
ratios three lines above it in the same function. Both now build from the
published figures.

The verifier had a check for this and it passed anyway: its tolerance was 0.002
and the error was 0.001. That is the second time a tolerance has been the bug
rather than the check. Tightened to 6e-4 — the last published digit — and a
matching check added for `sharpe_like`, which reconciled only by luck.

### 4. The page contradicted itself on Brent, twice

Brent was quoted three ways at once: `$95` in the growth-momentum driver against
an input of `$96.28`; `+40% y/y` in the US and Europe region notes while the
geopolitics driver on the same page said the year-on-year had *"WIDENED to +47.0%
from +40.3% a week ago"*. The Europe note was a full week behind — it carried the
superseded pair (`+40%` from `+32%`) that the geopolitics note describes as last
week's. A reader comparing the US note to the Asia note saw two different numbers
for one input.

Fixed, and generalised. The three prose guards added on 2026-09-09 were
deliberately targeted at specific strings; targeted guards do not catch the next
instance of the same class. There is now a **general prose-vs-input scan**: every
driver note, region note and fund note is scanned for the named quantities and
each quote must match the input it names.

Worth recording how the guard first failed. Scoped to include scenario
descriptions, it flagged `"Brent to $130+ from $96"` — the Hormuz closure
counterfactual, which is correct prose. The fix was to scope the guard to notes
describing the *current* market, not to widen the tolerance until $130 passed;
a guard loose enough to accept $130 would never catch a $95. Scenario rows keep
their own anchor check.

### 5. `FX_DRIFT` did not match the derivation printed beside it

`FX_DRIFT = 2.0` carried the comment *"PPP-implied PHP depreciation vs USD
(PH ~3.9% infl vs US ~2.4%)"*. That differential is 1.5, not 2.0. The constant
adds directly to the gross return of three of the four sleeves, and neither the
number nor its stated justification was checked.

The constant is left at 2.0 — it is defensible for a ten-year mandate, sitting
between long-run relative PPP (1.5pp) and the current print differential (6.1
less 3.4 = 2.7pp), and moving a lever this large on judgement alone during a pass
with no research would have been worse than leaving it. What is fixed is the
dishonesty: the comment now states the actual reasoning, the two anchors are
named constants, and a check asserts `1.5 <= FX_DRIFT <= 2.7` from the model's
own inflation inputs. If PH inflation converges past 2.0pp above the US, the
check fails and says so.

### 6. The independent verifier audited a stale payload

The verifier reads only `model/data.json`, deliberately, so the engine cannot
mark its own homework. Nothing forced that file to be current. After the engine
changed above, the verifier ran clean — 184 checks, zero failures — against the
*previous* payload, because `--json` prints to stdout and the redirect into
`model/data.json` had been skipped.

A verifier that can silently audit superseded numbers is worse than no verifier,
because it produces false confidence. It now asserts, before anything else, that
`model/data.json` is byte-identical to the payload embedded in `dashboard.html`.
It also no longer depends on the working directory, having died twice on that.

### Also

- `macro_tilt["regional"]` was set on all four funds and read nowhere. It
  shadowed the live `region` field and had already silently diverged from it on
  the money-market sleeve (`None` against `"PHILIPPINES"`). Removed. The
  2026-09-09 dead-code sweep looked for unused constants, functions and
  parameters, and did not look for unused dict keys.
- The runbook had drifted from the model it describes: the regional tilt formula
  was still the pre-rescale `(score − 5.5) × 0.30`, the horizon table still said
  `5Y`, and it still described the VIX complex as "spot plus the two nearest
  futures" when the bootstrap has used four contracts since 2026-09-08. Two
  near-identical "how to run it" sections merged into one.
- The egress note assumed `WebSearch` as the fallback when `WebFetch` is blocked.
  Both were unavailable today. The runbook now says what to do when there is no
  research channel at all: refresh nothing, move no dates, and say so.
- The payload field `sp_vol_5y` had held the **ten-year** implied vol since the
  mandate lengthened on 8 September. The value was right and every consumer used
  it correctly, but a field whose name contradicts its contents is how a correct
  number eventually gets used wrongly. Renamed `sp_vol_lt`, after the constant it
  publishes rather than after a horizon.
- Added a **pending-catalyst block** to the page, listing scheduled events dated
  after `AS_OF` that no number on the page accounts for — today the ECB decision
  (10 Sep), US August CPI (11 Sep) and the FOMC (16 Sep), all three of which hit
  inputs currently doing real work. Two checks assert the list is in date order
  and that every entry is genuinely still pending, so the page cannot describe a
  passed event in the future tense.

### On `AS_OF`

It stays at **2026-09-09** even though this pass ran on the 10th. No input was
refreshed, so moving it would assert a currency the data does not have. The
as-of date describes when the numbers were verified, not when someone last
looked at the file.

**Checks: engine 65 → 76, independent verifier 184 → 197, requirements checklist
21/21.** All eight new checks were verified to bite by injecting the defect they
target and confirming the failure.

## 2026-09-09 (audit) — The stress table was on a different horizon from the rest of the page

Validation-only pass: no new research, no input changes. Three defects found by
looking where nothing was looking. One is serious.

### 1. Scenario drawdowns were never horizon-scaled

When the mandate moved to ten years on 7 September, `DD_HORIZON_SCALAR` was
applied in `build_fund()` and in `port_dd()` — but **not in `run_scenarios()`**.
For two days the stress table published drawdowns on the *five-year* calibration
while every other drawdown on the page was on the ten-year one, understating the
tail by a factor of 1.414.

The tell was sitting in plain sight: the **"Grind-on base case"** row is defined
as zero shock and a 1.0 volatility multiplier — *"the modelled path"* — so it
must reproduce the headline portfolio exactly. CAGR matched (7.58%), volatility
matched (13.54%), and drawdown read **−18.1% against a headline −25.6%**. The
same portfolio, described two ways, on one page.

| Scenario (optimised) | Published | Corrected |
|---|---|---|
| Hormuz escalation | −33.5% | **−47.4%** |
| Hawkish repricing | −25.7% | **−36.3%** |
| AI capex digestion | −29.9% | **−42.2%** |
| Disinflation restart | −12.5% | **−17.7%** |
| Grind-on base case | −18.1% | **−25.6%** |

Fixed, and **three checks added**: both zero-shock rows must reproduce their
headline row on all three figures, and every scenario drawdown must reproduce
from the published coefficients including the scalar. All three verified to bite
by reverting the fix. The independent verifier gained a whole scenario block —
it had never re-derived the stress engine at all.

### 2. The "Hawkish repricing" scenario contradicted the driver on the same page

Its description said *"two hikes are priced for Sep-16 and Dec"*. The
monetary-policy driver was corrected on 5 September to say the opposite —
*"still one move, not the two this model previously asserted, since the December
hike has slipped to January 2027"*. The correction was applied in one place and
not the other, and nothing compared them.

Rewritten to say what the row actually is: a **tail**, modelling the market
coming round to the dissenters, explicitly against a base case of roughly one
hike at 58%. Also fixed *"The 3 July dissents"* → *"The three July dissenters"*
(it read as a date; the FOMC was 28–29 July), and the Brent anchor now
interpolates `MACRO["brent"]` instead of carrying a typed \$95.

**Three targeted regression guards added** — no scenario may assert a hike count
the macro block doesn't price; the Brent anchor and the September odds quoted in
prose must match the inputs. Two verified to bite by injecting the old text.

### 3. One constant published three times

The 1–5 neutral appeared as `gauge_neutral`, `driver_scale.neutral` and the
regional `NEUTRAL_5`. Three copies of one number with nothing tying them
together. Now asserted equal in both harnesses.

### What was checked and found sound

Worth recording, because "no finding" is a result:

- **The efficient frontier is correct.** All 30 buckets independently reproduced;
  every point is the max-CAGR portfolio in its bucket and respects the cap.
  My first re-derivation reported **16 mismatches** — all phantom, because I
  bucketed with `round()` on unrounded drawdowns where the engine uses
  `floor()` on rounded ones. The bucketing rule is part of the claim, and I
  nearly filed sixteen false bugs by not reproducing it exactly. The check now
  in the verifier encodes the rule explicitly.
- `best_ratio`, the look-through tables, the source list, fee arithmetic and the
  peso reconciliation all re-derived clean.
- Dead-code sweep: no unused constants, no uncalled functions, no orphaned
  parameters. Three payload keys the page never reads (`acwi_it_mix`, `fx`,
  and the now-tied `gauge_neutral`) are engine- and verifier-side inputs, not
  clutter. `tilt_regional` / `tilt_rates` / `tilt_energy` appeared unused by a
  naive scan but are read through dynamic string keys — checked before reporting.

**Verification:** engine **57 → 65** checks. Independent verifier **171 → 184**,
0 failures. Checklist 21/21. Repo 8 tracked files.

## 2026-09-09 (later) — Driver sentiments moved to 1–5; the page is now one scale throughout

Requested change, and the last one needed: the seven driver scores were the only
1–10 surface left. Gauge and regional rankings had already moved.

Handled exactly as the regions were on 5 September. The drivers stay
**researched on 1–10** — that is the granularity the evidence supports, and every
driver note is written against it ("held below 6", "held at 1.5 rather than cut
further"). Rewriting sourced prose onto five points would destroy information and
risk drift. So the score is rescaled once, at the reported value, and **each note
now carries its research-scale score** the way the region rationales already do.

| Driver | Reported | Researched |
|---|---|---|
| Monetary policy & liquidity | **2.11** | 3.5 |
| Inflation trajectory | **1.89** | 3.0 |
| Growth momentum | **3.00** | 5.5 |
| Corporate earnings | **3.89** | 7.5 |
| Valuation support | **3.89** | 7.5 |
| Volatility & risk appetite | **2.11** | 3.5 |
| Geopolitics & energy | **1.22** | 1.5 |

One property worth stating because it makes the page self-consistent rather than
merely relabelled: `to5` is **affine** and the driver weights sum to 1, so
blending-then-rescaling and rescaling-then-blending give the same number. The
weighted composite of the *reported* scores therefore **is** the headline gauge,
2.65. Both the engine and the independent verifier now assert that rather than
assuming it.

Also changed: bars fill against 5 rather than 10; the neutral hairline moves from
55% to 60% of the track (3.0 of 5, where it was 5.5 of 10) — Growth momentum at
exactly 3.00 lands on it, which is a free visual check; and the colour thresholds
are the old 1–10 breaks (6.5 / 4.5) carried across **by the same map**, so no
driver changes colour as a result of the rescale.

### A hand-typed rescale was wrong, and now there is a guard

Rewriting the report prose, I typed `to5(4.0)` as **2.44**. It is **2.33**. Caught
by re-deriving every figure I had just written rather than trusting the typing —
and the honest lesson is that this is the fourth time a hard-typed derived figure
has gone wrong on this page.

So the checklist gained a guard that parses the rendered prose for every
"reported (researched)" pair and asserts the pair actually satisfies `to5`.
**Verified to bite**: reintroducing 2.44 makes it fail, restoring 2.33 makes it
pass. A check that has never been seen to fail is not evidence of anything.

**Verification:** engine **53 → 57** checks. Independent verifier **171 checks,
0 failures** — it failed first, correctly, because it was still reading `score`
as the research value; it now re-derives both scales and the affine property
independently. Checklist **20 → 21**, all passing. Repo 8 tracked files.

## 2026-09-09 — Two fee errors, and an optimiser with no diversification constraint

The most consequential review so far. Chasing the two target-fund fee estimates
to primary sources changed the recommended allocation, and the change exposed a
missing constraint that had been hidden by luck.

### 1. The Asia fee estimate was wrong by ~0.75pp a year

`ATRASEQ`'s target-fund ongoing charge carried **0.80%** — an unanchored guess
the register had honestly flagged as "not located". J.P. Morgan publishes a
**1.50% management fee** for the JPMorgan Asia Equity Dividend Fund. An ongoing
charge cannot be *below* the management fee, so 0.80% was not merely uncertain,
it was **impossible**.

Corrected to **1.55%** (published 1.50% plus ~0.05% operating costs). Still an
estimate — the OCF for the exact share class ATRAM's feeder buys is not
published — but now anchored on a published figure and erring high rather than
low. All-in stack **1.98% → 2.73%**, the highest on the sheet.

Consequence: Asia Equity's forecast net CAGR falls **8.54% → 7.79%** and the
sleeve drops **from first to third**. Its macro case is unchanged and still the
strongest — this is a cost finding, not a change of view — but it was being
overweighted partly on a return that a fee error had inflated.

### 2. The Global Tech estimate is no longer an estimate

Fidelity **publishes** the Global Technology Fund's OCF: **1.04%** for the
W-Acc-GBP class (AMC 0.80% + operating costs) — the same class this model
already cites for the fund's realised five-year return. Promoted from a 0.95%
estimate to a verified figure. The JEPQ UCITS TER of 0.35% was re-confirmed
across three independent sources and stands.

One fee estimate now remains on the page, down from two.

### 3. The optimiser had no diversification constraint — and nobody could tell

With Asia's return corrected, the optimiser immediately proposed **15 / 75 / 5 / 5**
— 75% in a single fund. A "four-fund portfolio" that is one fund plus three stubs,
and flatly against the argument the report itself makes ("it is the same bet,
twice"). **The page argued the principle; the code never encoded it.**

It had never bound before, because the drawdown budget happened to do the job by
accident. That is the worst kind of missing constraint: invisible until the day
it matters.

Added an explicit **50% single-sleeve cap**, stated on the page as part of the
objective rather than applied silently, with three checks asserting it (both
portfolios respect it, the enumerated set respects it, and the stub
counterfactual obeys the same cap so its "cost" is measured against something
the objective would actually allow). It is not reverse-engineered to reproduce
the old answer — the previous optimum was 45%, comfortably inside it.

Enumerated set **969 → 633** portfolios; feasible **252**.

### 4. A check that encoded a contingent fact as a law

`the Global Tech stub cost is derived, and the stub is genuinely dearer` asserted
`cost > 0`. That stopped being true today: the counterfactual is drawn from a
*different* feasible set, so its best point can be better, equal or worse than
the chosen one. **The stub is now free** — it cost 0.15pp a week ago, and the fee
corrections closed the gap.

Same failure mode as the "vol term structure is monotone rising" invariant on
4 September: a fact that was true when written, written in as a law. The check now
asserts the arithmetic identity and reports the sign as a finding. The page's
"That option is not free" claim — true yesterday, false today — is replaced by
text that states whichever way the sign falls, and says plainly that it changed.

### 5. Result

| | Before | After |
|---|---|---|
| Baseline | 7.54% / −28.8% | **7.33% / −28.9%** |
| Optimised | **15/45/35/5**, 7.82% / −25.8% | **15/50/30/5**, 7.58% / −25.6% |
| Return per drawdown | 0.262 → 0.304 | **0.253 → 0.296** |

Returns fall because the fees are real and were understated. The optimised
portfolio still beats the baseline on both axes, and by a slightly wider relative
margin (17% vs 15%).

### 6. Also

- Peso **62.625**, the 23rd record-low close of 2026 — and a dating check:
  a wire story dated the 9th reports the **8th's** close. Trade date is now
  recorded against publication date, with the prior session (62.586, not a
  record) noted so the sequence is auditable.
- The rationale's hard-typed allocation figures (45%, 35%, 5%) and the "Why
  15 / 45 / 35 / 5" heading now render from the payload — they would have gone
  stale the moment the weights moved, which is exactly what happened today.

**Verification:** engine **50 → 53** checks. Independent verifier **167 checks,
0 failures** — it disagreed with the engine on the feasible-set size until it was
taught the cap *from the payload*, which is the behaviour that makes it worth
having. Checklist 20/20. Repo 8 tracked files; harness 44KB.

## 2026-09-08 — Review: the horizon blend was never reweighted, and the published cap was looser than the enforced one

Research and audit pass. Two model defects found, two relevance gaps closed, one
input refreshed. No claim was found to be factually wrong this week — the two I
had flagged as single-sourced both corroborated.

### 1. The horizon blend was carried onto a doubled mandate unchanged

`HZ_W` was `3M 15 / 6M 25 / 12M 30 / long 30`, unchanged when the mandate moved
from five years to ten on 7 September. Two things were wrong with it:

- **The comment above it claimed the blend "keeps the long anchor dominant."
  It did not.** 70% of the weight sat on horizons under a year against 30% on
  the anchor. The comment described an intent the numbers contradicted, and
  nothing checked it — the same class of defect as the drawdown formula on
  5 September: prose asserting something the code did not do.
- Whatever the right near-term weight is for a five-year mandate, it is not also
  right for a ten-year one. Doubling the holding period without touching the
  weights silently doubles how much a three-month signal counts per year held.

Now **`3M 10 / 6M 15 / 12M 25 / 10Y 50`** — near-term signals keep half the
weight, the anchor genuinely dominates, and **three new checks assert it**
(weights sum to 1; the mandate bucket carries ≥50%; no sub-year bucket outweighs
it) rather than trusting a comment.

Effect: regional blends rise toward their long anchors (Asia 3.61 → 3.70,
US 3.20 → 3.28), and the volatility ramp widens **+4.38 → +4.61** because the
long-horizon vol point now carries half the blend against spot. Optimised CAGR
**7.76% → 7.82%**, return-per-drawdown **0.300 → 0.304**. Weights hold at
15/45/35/5.

### 2. The published drawdown cap was looser than the enforced one

`dd_cap` was published as `round(DD_CAP, 1)` = **26.0** while the optimiser
enforced **25.97**. Consequences:

- An independent re-derivation from the published payload got **370** feasible
  portfolios where the engine got 368. The verifier caught this; it is the
  reason it exists.
- Worse, **the engine's own budget check read the published cap**, so it could
  not bite: it would have passed a chosen portfolio breaching the real budget by
  up to 0.03pp.

Compounding it, `horizon_scalar` was published to 4dp, leaving a 2.5e-04 error
in every drawdown — enough on its own to flip portfolios sitting on the boundary.

Both now published at the precision they are enforced at, the budget check reads
the enforced cap, and **two new checks assert that the published cap and scalar
*are* the enforced ones**. A published constraint that differs from the applied
constraint is worse than no published constraint.

### 3. Relevance: the macro read was one-sided on the driver that matters most

Monetary policy carries the largest driver weight (20%) and the note presented
the hawkish case as settled. It is not. Goldman's Jan Hatzius argues market
pricing for the funds rate is **still too hawkish**, calls a September hike
"very unlikely" on softer retail sales and cooling inflation, and expects
3.50–3.75% held through 2026 with cuts pushed to 2027. Sources also differ on
the September odds — 58% post-payrolls against ~30% in the Goldman piece.

Score **held at 3.5**, deliberately: the tightening that has already *happened*
is not in dispute (ECB hikes 10 Sep, BSP three moves, 2-year at a 20-month high).
But the note now carries the dissent and flags this as the driver most likely to
move on the 11 Sep CPI and 16 Sep FOMC.

### 4. Relevance: a new demand-side channel, cutting both ways

China has cut crude imports and refinery runs enough to moderate the price
surge — Brent is above $96 after +9.3% on the week, a smaller move than a ~93%
Hormuz shutdown alone implies, and that gap *is* the Chinese demand cut. Added
to both the energy driver and the Asia rationale, with its two-sidedness stated:
it caps the input-cost tax on every net importer in this portfolio, while being
the clearest read yet on the Chinese demand weakness that would hurt Asian
earnings. Iran's new threatened restricted zone inside the Gulf is recorded too.

### 5. Corroborated, refreshed, and swept

- **Peso confirmed and moved**: 62.59 on 4 Sep verified at two outlets (Manila
  Bulletin, Tribune — "fifth record low in six sessions"). It has since printed
  **62.625 on 8 Sep, the 23rd record-low close of 2026**. The rationale now also
  states *why* — dollar strength and the oil import bill, not a domestic
  solvency signal — because that is what justifies still holding the sleeve.
- **VIX complacency corroborated independently**: the contango regime was on its
  **92nd day** as of 18 August (VIX 15.84 vs VIX3M 19.27). This is the thesis's
  central claim and it now has support beyond the single strip quote.
- Brent +9.3% on the week and the 30-year at 5.233% added.
- **Four stale mandate references** left inside the regional rationales after
  the horizon change ("the 5-year anchor holds at 6.5", "the 12M and 5Y anchors")
  — found by sweeping the payload's prose fields for horizon strings, not just
  the page's. Genuine five-year *facts* (the Fidelity fund's realised 5y return,
  the NDX 5y average P/E) were left alone.
- The horizon blend weights were typed into the page prose in two places; both
  now render from the payload.

**Verification:** engine **45 → 50** checks. Independent verifier **163 checks,
0 failures**. Checklist 20/20. Repo at 8 tracked files; harness 44KB.

## 2026-09-08 — Mandate horizon moved 5 years → 10 years

Requested change. It is not a relabel: the horizon is load-bearing in three
places, and pretending otherwise would have published numbers that no longer
mean what they say.

### The horizon is now one constant

`HORIZON_Y = 10.0` in the engine, `HY` / `HYL` in the page — both derived from
the payload. Previously "5" was spelled out in a dozen places across the engine,
the page prose, the page's JavaScript, the verifier and the checklist, which is
why this change touched so much. It should not have to be hunted down again:
the long volatility point, the horizon blend's long bucket, every regional score
key, the peso compounding, the drawdown scaling and every visible label now all
derive from that one number. **Six new engine checks assert exactly that** — that
the vol curve's last point, the blend's long bucket and every region's long score
really are the mandate horizon, and that peso terminal value compounds over it.

### What actually changed in the maths

**1. Expected drawdown is not horizon-invariant.** The `k·σ − 0.50µ` calibration
reproduces S&P −20% and NDX −33%, and those are **rolling five-year medians**.
A ten-year window gives the path twice as long to find its worst peak-to-trough,
so the anchors cannot simply be relabelled. Expected maximum drawdown of a
diffusion scales with σ√T, so the whole calibrated bracket is scaled by

```
√(T / T_calib) = √(10 / 5) = 1.4142
```

which turns the anchors into ~−28% (S&P) and ~−47% (NDX) — plausible for
ten-year windows, and **derived** from the five-year calibration rather than
re-fitted by eye to ten-year medians this model has not verified at a primary
source. The drift term scales with the same factor because it is an annualised
rate offsetting the same window; scaling only the volatility term would quietly
assume drift stops helping as the horizon lengthens. The scalar is published on
the page and in the payload, so the printed formula still reproduces every
printed drawdown — the five drawdown-reproduction checks failed the moment the
scalar was introduced without it, which is the check doing its job.

The money-market floor is deliberately **not** scaled: a 100bp shock on a
half-year duration book is the same size at five years or ten.

**2. The optimiser's budget had to scale too.** The objective was "at least
2.0pp below the baseline's drawdown". With drawdowns ~41% deeper, a flat 2.0pp
would have quietly *loosened* the constraint. It scales with the drawdowns it
constrains: **2.83pp**, so the objective means what it meant before.

**3. One return assumption was genuinely a five-year average.** The peso money
market's gross was a "5y average PH short-rate path" at **5.25%**. The elevated
front end is a 1–3 year feature, so over a decade far more of the path sits at
the ~4.50% neutral rate. Cut to **4.85%**. Every other return input is a
long-horizon capital-market assumption (JPM LTCMA is a 10–15 year framework) and
is, if anything, better suited to the longer mandate than the shorter one.

**Left alone deliberately** — genuine five-year facts, not mandate references:
the Fidelity target fund's realised 15.20% five-year return, the NDX five-year
average forward P/E of 24.7×, and the rolling-five-year calibration medians
themselves.

### Result

| | 5-year mandate | 10-year mandate |
|---|---|---|
| Baseline | 7.57% / −20.3% | **7.49% / −28.8%** |
| Optimised | 7.82% / −18.2% | **7.76% / −25.8%** |
| Return per drawdown | 0.374 → 0.431 | **0.260 → 0.300** |
| ₱1,000,000 becomes | ₱2.11m at 10y | **₱2,111,426** |

Weights hold at **15/45/35/5**. CAGRs dip slightly on the money-market cut;
drawdowns deepen by the √2 scalar. Return-per-drawdown falls in level — a longer
window simply contains more drawdown — but the optimised portfolio's *relative*
advantage over the baseline widens, 15% → 15.4%.

**Verification:** engine **39 → 45** checks. Independent verifier **162 checks,
0 failures** — its own horizon now reads from the payload rather than assuming
five years, which is what surfaced the five stale assumptions inside it
(terminal compounding, the DD recomputation, the feasible-set count, the
optimality proof and the budget). Checklist 20/20, with its horizon assertions
and stale-figure guard both keyed to the payload.

## 2026-09-07 — Deep scrub: the volatility read was wrong, and correcting it moved the model

Full research pass against live sources. Four factual errors found in inputs this
model had presented as verified, one of them load-bearing. Correcting them
materially improved the optimised portfolio's forecast, which is the point of
checking.

### 1. The central volatility claim was wrong — and wrong in the flattering direction

Last week's page led with "the calm was priced, and it has started to break":
spot VIX 16.44 on 2 Sep, +10.2% on the day, off a 2026 low of 14.13 set 28 Aug.
Almost none of that survived contact with the sources.

| Claim | Published | Verified |
|---|---|---|
| Spot VIX | 16.44 (2 Sep) | **14.32** (4 Sep close) |
| 2026 low | 14.13 on 28 Aug | **14.18 on 17 Aug** |
| Sep future | 17.92 | **16.57** |
| Dec future | 20.38 | **19.26** |

The VIX did spike to **16.34** on 2 Sep on the Hormuz strikes — then gave the
entire move back: 15.20 on 3 Sep, 14.32 at Friday's close, within 0.14 of the
2026 low. The thesis was not merely stale, it was **inverted**: the complacency
did not break, it re-asserted itself while a shooting war ran in the Strait of
Hormuz.

One aggregator reported a "5 September close of 14.53". **5 September 2026 was a
Saturday.** There is no such close, and the figure was discarded — a weekday
check is now part of accepting any market print.

### 2. The bootstrap was interpolating across a gap it no longer had to

The curve was built from two observable futures (Sep, Dec) with a five-month
linear guess between them. Four contracts are quoted — Sep 16.57, Oct 18.41,
Nov 19.08, Dec 19.26 — so the bootstrap now interpolates through all of them.
The knots are data, not constants, so adding the next contract is an input
change rather than a code change.

### 3. What that does to the portfolio

This is the whole reason the volatility channel was wired into the optimiser on
5 September. Spot fell toward its low while the curve held, so:

```
ramp = 18.68% blended implied − 14.32 spot = +4.36 vol points   (was +2.87)
```

Every sleeve's tilt moved with it, with nobody re-typing a number. The
covered-call sleeve's volatility tilt goes **+0.60 → +0.92pp**, Global
Technology's **−0.35 → −0.53pp**. Consequences:

- **The two US-tech sleeves have swapped places.** Nasdaq Equity Income now
  forecasts **8.21%** net against Global Technology's **7.92%** — it wins on
  return *and* on risk (16.0% vol vs 24.7%). The report's "for a forecast net
  CAGR only 0.22pp lower" is now false in the other direction; the page states
  the dominance instead, rendered from the funds.
- **Optimised forecast rises 7.66% → 7.82%**, drawdown improves −18.4% → −18.2%,
  return-per-drawdown **0.415 → 0.431** (a 15% gain over baseline, was 13%).
  Weights hold at **15/45/35/5** — the budget still binds there.
- **The Global Tech stub costs more now: 0.08pp → 0.15pp.** Stated, not buried.

### 4. Three more corrections

- **Hormuz throughput was measured against the wrong baseline.** The page cited
  ~5 transits "against a 10-day average of 14" — but that average was itself
  already collapsed. Against the **~85/day pre-crisis baseline**, the 6 transits
  PortWatch logged on 30 Aug are a **~93% shutdown**, with 436 vessels holding.
  The conflict is also now direct rather than proxy.
- **Brent +40.3% → +46.99% y/y**, $94.86 → **$96.28**. The shock is still widening.
- **Peso 62.565 → 62.59**, a *fifth* consecutive record low, not a fourth.
  10-year 4.76% → **4.784%** (4.818% intraweek, highest since Nov 2023);
  2-year **4.377%**, highest since Jan 2025.

### 5. Scores that moved, and why

- **Volatility & risk appetite 4.0 → 3.5.** Cut *because* the previous read was
  wrong: absorbing a live Hormuz conflict without repricing vol is more
  complacency, not less.
- **Asia 3M 5.5 → 6.0.** Last week's cut assumed the 2 Sep selloff was a
  persistent energy de-rating. It reversed in three sessions on AI and memory
  demand — SK Hynix ~+7% on the week, Nikkei +1.26% to 65,021, KOSPI back in
  bull-market territory. The selloff was macro, the earnings never moved.
- **ECB confirmed and strengthened:** all 65 economists in the 31 Aug–3 Sep
  Reuters poll see +25bp to 2.50% on 10 Sep, 91% see it held to year end —
  the shortest hiking campaign since 2011.

Gauge **2.68 → 2.65**.

### 6. A check fired, and the tolerance was the bug

`optimized drawdown reproduces from its published k` failed at a real gap of
**0.0614** against a hand-picked `< 0.06`. The check was right and the tolerance
was wrong: it ignored the rounding each published input contributes through the
formula. Both the engine and the independent verifier now **derive** the bound —
display rounding (0.05) plus each input's propagated contribution — rather than
carrying a round number that would drift into meaninglessness. A magic constant
is how a check gets quietly loosened until it stops biting.

Also fixed: the monetary-policy driver note still ended with a stale "US 10-year
4.76%" after its opening sentence had been updated to 4.784% — caught by widening
the checklist's stale-figure guard to every figure corrected this week, which is
now how that guard is maintained. (The guard excludes the sources list, where
descriptions legitimately quote older articles verbatim.) Also: a duplicated row
in the verifier's claim-register map, and the last hard-typed figures in the prose (the conclusion's six numbers, the Hormuz
scenario, the Asia horizons, the ramp arithmetic, the VIX stat card's 2026 low)
are now rendered from the payload.

**Verification:** engine **39/39**. Independent verifier **160 checks, 0
failures**, with the forward-variance curve re-integrated from the payload's own
futures strip on a 200,000-step grid using its own knots. Claim register updated
and now **20 rows machine-checked**. All 16 checklist items plus 4 build-health
checks: **20/20**.

## 2026-09-05 — Audit: the published drawdown formula did not reproduce the published drawdowns

Full revalidation pass. Four defects found, all four rectified. The first is the
serious one.

### 1. The drawdown card published a formula that was wrong for three of four funds

The Volatility tab stated expected drawdown as `1.65 × σ − 0.50 × µ` and said the
coefficients were calibrated against the S&P and Nasdaq medians. True as far as it
went — but the engine has always applied a **per-fund adjustment** to that
coefficient, and nothing on the page said so:

| Sleeve | k actually used |
|---|---|
| Peso Money Market | 1.65 (floored separately anyway) |
| Nasdaq Equity Income | **1.55** |
| Asia Equity | **1.70** |
| Global Technology | **1.80** |

A reader checking the arithmetic would have found it failed. Global Technology's
−40.8% is −37.1% under the formula as printed. Worse, it reaches the headline: the
portfolio coefficients are 1.675 (baseline) and 1.626 (optimised), so the stated
formula gives **−20.2% → −18.8%** where the page prints **−20.5% → −18.4%**. The
improvement the whole report turns on would have read 1.4pp instead of 2.1pp.

The adjustments themselves are defensible — left tails genuinely are not the same
shape across a covered-call fund, an EM index and concentrated long-duration
growth — so the fix is disclosure, not deletion. Each `k` is now published with the
reason it differs from the anchor, the portfolio coefficients are printed, and
**six new checks assert that every drawdown on the page reproduces from the `k`
printed beside it.** No number changed; the page now supports the numbers it prints.

This is the failure mode worth naming: the engine's own checks all passed, because
they verified the code against itself. Nothing checked the code against the page's
*claim* about the code.

### 2. The cost of the Global Technology stub was understated by 2.7x

The report says keeping a 5% stub rather than cutting to zero costs "roughly
0.03pp of portfolio CAGR". Re-derived against the optimiser's own objective — max
CAGR subject to the drawdown cap — the best portfolio that drops the sleeve
entirely (10/65/25/0) returns **7.74%** against 7.66%. The stub costs **0.08pp**.
The 0.03 was correct for an earlier set of tilts and was never re-derived.

Now computed in the engine and rendered from the payload, with the counterfactual
allocation named so the reader can check the claim rather than take it. The
recommendation is unchanged — it is a deliberate purchase of optionality — but it
is now priced honestly.

### 3. A stale sleeve-comparison figure

"…for a forecast net CAGR only **0.23pp** lower" — the actual gap between Global
Technology (8.10%) and Nasdaq Equity Income (7.88%) is **0.22pp**. Now rendered
from the two funds it describes.

### 4. The peso-cash section still argued from July's inflation print

The report claimed "with July inflation at 6.2%, the real yield is roughly −1pp"
while the Philippines region rationale on the same page had already been updated to
August's 6.1% and said the gap "narrowed … to roughly −0.4pp". The page contradicted
itself. Corrected to the August print and stated as the range it actually is:
**−0.95pp at the 91-day bill to −0.40pp at the 364-day**, with the improvement from
July made explicit. The Global-Tech-adjacent money-market slide note carried the
same stale July figure and is fixed too.

### 5. The claim register itself had drifted — eleven rows

`monitoring/CLAIMS.md` exists to catch exactly this class of problem, and it had
the problem. Eleven rows no longer matched the model they certify:

| Row | Register said | Model says |
|---|---|---|
| BSP target RRP rate | 4.75% | **5.00%** |
| BSP last move | +25bp (June) | **+25bp on 27 Aug, third consecutive** |
| Spot VIX | 14.13 | **16.44** (14.13 is the 30-day low) |
| Horizon vol 3M/6M/12M/5Y | 17.94 / 19.10 / 19.54 / 19.55 | **18.27 / 19.25 / 19.62 / 19.57** |
| Brent crude | $91.28 | **$94.86** |
| Brent y/y | +32.02% | **+40.33%** |
| PHP depreciation drift | 1.5% p.a. | **2.0% p.a.** |
| Regional tilt sensitivity | 0.30pp above 5.5 | **0.675pp above 3.0** |
| Drawdown model | 1.65σ − 0.50µ | **per-sleeve k, 1.55–1.80** |
| Header + assumptions preamble | "Job 2 walks this file each Sunday" | no automation since 3 Sep |

All corrected, and rows added for the volatility ramp, the per-sleeve and portfolio
drawdown coefficients, the reporting scales, and the volatility sensitivities.

The structural fix matters more than the corrections: **the register is now
machine-checked.** The independent verifier parses `CLAIMS.md` and asserts eighteen
of its rows against `model/data.json` on every run. A register that certifies stale
figures is worse than no register — it converts drift into false assurance.

### Also

- The driver-bar caption said the bars "run 1–10"; they fill in proportion to the
  score from zero. Caption now describes the encoding accurately.
- Removed a check written this session that could not fail (`… or True`) and
  replaced it with one that re-derives the portfolio coefficient as the ex-cash
  weighted average.

**Verification:** engine **29 → 39** checks. The independent verifier — which reads
only `data.json` and never imports the engine — gained the drawdown-reproduction,
derived-figure and claim-register blocks and now runs **159 checks, 0 failures**. Volatility
integration re-done on a 20,000-step grid, portfolio algebra recomputed with an
explicit double loop, correlation matrix re-tested for positive-definiteness by
Cholesky, and the 969-portfolio enumeration re-counted from scratch — all agree.
All 16 original checklist items re-verified against the rendered page at 412px,
plus 4 build-health checks: **20/20**.

**House cleanup:** repo stays at 8 tracked files with nothing stray. The review
harness in the scratchpad went from 5.1MB of accumulated one-offs to 40KB — six
near-identical screenshot scripts collapsed into one parameterised `shot.js`, and
the stale payload snapshots, duplicated page copies and old PNGs deleted. What
remains is the three things worth re-running (`audit.py`, `validate.js`,
`checklist.js`) plus a README saying how. `model/__pycache__` removed.

## 2026-09-05 — Regional rankings moved to the same 1–5 scale

Follow-up to the gauge change below: the four regional rankings now report on
**1–5** as well, so every sentiment number on the page reads against one scale.

This one had a trap the gauge did not. Regional scores are not display-only —
they drive each fund's return tilt through `(score − neutral) × coefficient`.
Rescaling the scores without rescaling the coefficient would have silently moved
every allocation. So the coefficient was restated in 1–5 units:

```
0.675pp per 1–5 point  ==  0.30pp per 1–10 point   (0.30 × 9/4)
neutral 3.0            ==  neutral 5.5
```

Verified rather than asserted: the full payload was diffed before and after.
**Every weight, CAGR, drawdown, volatility, tilt, scenario and frontier point is
byte-identical.** The only fields that changed are the four reported regional
scores (`5.70 → 3.09`, `5.95 → 3.20`, `6.80 → 3.58`, `5.84 → 3.15`).

- Heatmap shading anchors rescaled from the research scale, not re-picked by eye
  (`2.5 → 1.67`, span `6 → 2.67`), so the colour breaks land in the same places.
- Each region's "why" note is sourced prose written against 1–10 ("the 5-year
  anchor holds at 6.5", "Neutral, 5.5"). Rewriting those would have risked drift
  in researched text, so each note now carries a one-line header stating its
  research-scale blend and that the horizon figures inside it are on that scale.
- The Asia paragraph in the report quoted `5.5 / 6.5 / 7.0 / 7.5`; now
  `3.0 / 3.44 / 3.67 / 3.89`, rescaled rather than restated.
- Fund detail "Regional score … / 10" → "… / 5".

**Checks:** engine 25 → **29**. The verifier's regional block now re-derives the
blend on the research scale, confirms every reported score is the exact rescale
of it, and — the check that actually matters — confirms each fund's tilt equals
what the old 1–10 formula would have produced. **0 failures.**

## 2026-09-05 — Headline macro gauge moved to a 1–5 scale

Requested change: report the overall macro-driver sentiment gauge on **1–5**
rather than 1–10.

The seven drivers keep their **1–10** scores — that is the granularity the
underlying evidence supports, and every driver note is written against it
("held below 6", "held at 1.5 rather than cut further"). Rescoring them onto
five points would have destroyed real information and risked drift in the
sourced rationales. Instead the composite is rescaled once, at the headline:

```
gauge_5 = 1 + (gauge_10 − 1) × 4/9      # 1→1,  5.5→3.0,  10→5
```

Endpoints map to endpoints, so the driver-scale neutral of 5.5 lands exactly on
the 1–5 neutral of 3.0 — the dial's neutral is a real midpoint, not an
approximation. Today: **4.78 / 10 → 2.68 / 5**, displayed as **2.7**.

Changed with it:

- Dial geometry rebuilt for a 1–5 sweep: the four state bands become
  `1–2 / 2–3 / 3–4 / 4–5`, ticks every 0.5 with integer majors, labels at
  1 / 3 / 5.
- Verdict thresholds rescaled from the driver scale, not re-invented:
  `3.5 → 2.11`, `5.5 → 3.00`, `7.5 → 3.89`. The reading is unchanged —
  *Neutral, tilted cautious*.
- Header chip, `/10` suffix, section heading and the rationale prose all follow.
  The rationale's "rather than a 3 or an 8" is now "rather than a 1.9 or a 4.1",
  those being the same two anchors rescaled.
- The driver card's composite row shows both numbers (`4.78 / 10 → 2.7`) so the
  two scales can never be silently confused.
- The one place a driver-scale figure still appears in prose (inflation cut
  3.5 → 3.0) is now explicitly labelled as the 1–10 driver scale.

Regional scores stay 1–10 throughout: they feed the fund tilts through
`(score − 5.5) × 0.30`, so rescaling them would have moved allocations. It did
not, and no weight, CAGR or drawdown changed.

**Checks:** engine 22 → **25** (headline in 1–5, composite in 1–10, the rescale
is exact, and the neutral maps to the neutral). The independent verifier's
`gauge = Σ(weight × score)` check was pointing at the headline field and so
failed on the new payload — correctly. It now re-derives both numbers and the
rescale separately: **0 failures**.

## 2026-09-05 — Volatility analysis now actually drives the optimiser

The optimised portfolio was described as being built on macro sentiment,
correlated sentiment and regional rankings. Volatility was analysed in depth on
its own tab — a forward-variance integration across 3M / 6M / 12M / 5Y — but
**it never fed the allocation.** Each fund's volatility tilt was a hard-coded
constant (`vol_path: +0.60`, `-0.35`, and so on) sitting in the fund definitions.
The regional tilt was properly derived as `(score − 5.5) × 0.30`; the volatility
tilt was simply typed in.

That is now fixed. The channel is:

**ramp = horizon-blended implied vol − spot VIX**, using the same
`3M 15% / 6M 25% / 12M 30% / 5Y 30%` weights as the regional blend. Today:
`19.31% − 16.44 = +2.87 vol points` — how much repricing the option market is
still pointing at.

Each sleeve then earns or pays that ramp through a structural sensitivity, in pp
of 5-year CAGR per vol point:

| Sleeve | Sensitivity | Why |
|---|---|---|
| Nasdaq Equity Income | **+0.210** | writes calls on ~78% of a Nasdaq-100 book at ~1.22× market vol; premium scales with implied vol |
| Global Technology | **−0.122** | highest vol beta (1.30) and longest-duration equity; a higher vol regime lifts the discount rate on distant cash flows |
| Asia Equity | **0.000** | effects cancel — higher discount rate against an already-compressed 10.5× multiple and a duration-shortening dividend tilt |
| Peso Money Market | **+0.035** | cash gains marginally as risk-off keeps the front end bid |

These are properties of how each fund is built, not views on the market, and the
sensitivities should change only if a fund's structure changes.

**The output is unchanged.** The derived tilts reproduce the previous hand-set
values exactly (+0.10 / +0.60 / 0.00 / −0.35), so allocations stay at
**20/30/25/25** and **15/45/35/5** and forecasts stay at **7.50% / −20.5%** and
**7.66% / −18.4%**. That was deliberate: the mechanism becomes genuine without an
unexplained jump in the answer. What changes is that **the weights will now move
when the volatility curve moves** — previously they could not.

### Surfaced on the page

- The Portfolios tab now names all four inputs the optimised portfolio is built
  from, rather than the vague "takes the macro read seriously".
- A new card in the Volatility tab shows the ramp arithmetic and the per-sleeve
  sensitivity table, so a reader can see the curve turn into an allocation.
- The correlated-sentiment transmission row is now labelled from live data
  (`Volatility ramp 16.4 → 19.3`) instead of a typed string that would go stale.
- The rationale no longer calls the +0.60pp tilt "an estimate" — it shows the
  ramp, the sensitivity and their product.

### Three new sanity checks (19 -> 22)

- the ramp equals blended implied vol minus spot
- every volatility tilt is derived from the ramp, not hand-set
- the covered-call sleeve is the only one paid by a rising ramp

Validation: engine **22/22**, independent re-derivation **0 failures**, all
sixteen original requirements **16/16 PASS** plus four build-health checks.

## 2026-09-05 — Review: two releases landed, three defects fixed

Full manual review: macro refresh, fact-check, independent maths audit, code
review, cleanup, and validation of all sixteen original requirements. As-of
2026-09-03 -> 2026-09-05.

### New data — two scheduled releases since the last review

**US August payrolls (BLS, 4 Sep): +162,000 against a 53,000 consensus**,
unemployment steady at 4.1%, versus a 31,000 twelve-month average. This retires
the −23k July print the model had been treating as evidence of a cracking labour
market — it was noise, not trend. Growth momentum raised **5.0 -> 5.5**, and the
US near-horizon score **5.0 -> 5.5**.

**PH August CPI (PSA, 4 Sep): 6.1%**, easing from 6.2% — a fourth consecutive
monthly slowdown and a five-month low, inside BSP's own 5.5–6.5% range. Against
364-day T-bills at 5.72% the real-yield gap narrows from about −1pp to −0.4pp, so
the money market sleeve is losing purchasing power far more slowly. Philippines
3M and 6M raised **5.5 -> 6.0**; the 12M and 5Y anchors held at 5.5 because the
year-to-date average is still 5.2%.

Fed odds refreshed: **58%** for the 15–16 Sep FOMC, up from 49.4% the day before
on the payrolls beat — and *down* from the 66% recorded on 3 Sep, a reminder that
a point-in-time probability is not a standing fact.

### Defects found and fixed

1. **Duplicate source URL.** Adding an August PSA row created a second entry on
   the same `psa.gov.ph/price-indices/cpi-ir` URL as the July row. Merged into one
   row covering the series. Caught by the audit's duplicate check.

2. **Two stale corner-solution figures.** The "why not simply maximise return?"
   passage quoted the min-drawdown portfolio at 5.42% / −2.0%; the Philippines
   rescore moved it to 5.47% / −1.9%. **Fixed structurally rather than by hand:**
   both corner solutions now render from the payload at load time, so they cannot
   drift again. This is the first real bite taken out of the standing
   "53 hard-coded prose figures" risk.

3. **The gauge dial and the prose disagreed.** The dial and header showed
   **4.8** (one decimal) while the rationale said **4.78**. For a composite of
   seven subjective half-point judgements, two decimals is false precision anyway.
   Prose now reads 4.8, matching the dial. The validator was tightened to compare
   on displayed precision, so this class of mismatch is caught in future.

### Effect on the portfolio: none

Gauge **4.78** (unchanged on net — the growth upgrade offset the earlier
inflation cut). Both allocations hold at **20/30/25/25** and **15/45/35/5**.
Forecasts nudge to **7.50% / −20.5%** and **7.66% / −18.4%**; return per unit of
drawdown **0.366 -> 0.415**, a 13% gain.

### Validation

All **sixteen original requirements** re-validated against the rendered page:
**16/16 PASS**, plus three build-health checks. Engine **19/19**. Independent
re-derivation (reads only `data.json`, never imports the engine): **0 failures**.
Sources 31 -> 33, all https, no duplicates. Palette still passes colour-vision
validation. `__pycache__` removed; tree clean; 8 tracked files.

### Still pending

US August CPI publishes **11 September** and the FOMC decides **16 September**;
the ECB decides **10 September**. All three will move the inflation and policy
reads. Worth a re-run after each.

## 2026-09-03 — Manual review: two factual errors corrected

Full review run by hand: macro refresh, source fact-check, independent maths
audit, code review and cleanup. As-of moved 2026-09-02 -> 2026-09-03.

### Error 1 — the page overstated how much Fed tightening was priced

Both the US regional rationale and the monetary-policy driver note claimed **"the
market now prices TWO hikes (Sep-16 and Dec), not a hold"**, and the report
repeated it as "two more Fed hikes rather than a hold". That was wrong.

CME FedWatch puts the 16 September hike at roughly **66%** — one move. A December
hike *was* fully priced about a week ago but has since **slipped to January 2027**.
Two hikes is a house view (Barclays), not market pricing. The claim made the
hawkish read look more certain than the market actually is, in a portfolio whose
biggest single call is cutting long-duration tech because of that hawkishness.
Corrected in the engine and in the report prose.

### Error 2 — "core CPI 2.5% is the one clean anchor" no longer held

The model leaned on contained US core CPI as the offsetting good news in an
otherwise hostile inflation picture. But **PCE — the measure the Fed actually
targets — is running 3.7% over twelve months and 4.1% annualised over six**,
which is precisely what Chair Warsh cited at Jackson Hole to justify a hawkish
turn. Leaning on core CPI while ignoring PCE was cherry-picking the friendlier
gauge. The inflation driver is cut **3.5 -> 3.0** and the rationale now leads
with PCE.

### New verified data

| Input | Value | Source |
|---|---|---|
| Euro area HICP, Aug flash | **3.3%**, up from 2.9% | Eurostat, 1 Sep |
| Euro area energy inflation | **+14.3%** y/y, from 10.3% | Eurostat |
| ECB 10 Sep expectation | +25bp to 2.50%, then done | Reuters poll |
| US PCE | 3.7% / 4.1% ann. | via CNBC Jackson Hole |
| US 10-year | 4.76% | market data |
| PH core inflation, Jul | 4.2%, from 4.4% | PSA |
| Hormuz transits | ~5 vessels vs 14 10-day avg | Bloomberg |

Sources 26 -> 31, all https, no duplicates.

### Effect on the portfolio: none

Gauge **4.78 -> 4.70**. Both allocations unchanged at **20/30/25/25** and
**15/45/35/5**; forecasts unchanged at 7.48% / -20.5% and 7.64% / -18.5%.

Worth being explicit about why: the seven drivers feed the **gauge only**. Fund
tilts come from the regional scores and the volatility, rate and energy channels,
none of which moved materially in one day. A driver rescore is a change to the
summary judgement, not to the allocation mechanism. That separation is by design
— but it does mean the gauge can drift without the weights responding, which a
reader should understand.

### Audit — clean

Independent re-derivation (reads only `model/data.json`, never imports the
engine): **0 failures, 0 warnings.** Volatility integration re-derived at 200,000
steps; drawdown calibration still -20.2% S&P / -33.1% NDX; correlation matrix
positive semi-definite; 969 portfolios enumerated independently with matching
count and confirmed optimum; gauge, blends and every regional tilt re-derived;
fee arithmetic exact. Engine **19/19**.

**31 prose figures cross-checked against the payload — zero stale**, including
confirmation that no "two hikes" claim survives anywhere.

Page renders clean at 412px: no JS errors, no SVG label outside its viewBox, no
horizontal scroll, light theme holds, 31 sources linked. Palette still passes
colour-vision validation under `--pairs all`.

### House cleanup

`model/__pycache__` removed; working tree clean; 8 tracked files.

## 2026-09-03 — Automation deleted; review is now manual

At the owner's request, both Sunday routines were deleted:

- `trig_01UxqDnGKQh8QML6z2fziamx` — Sun 6am, macro relevance + source fact-check
- `trig_01WrfrLEAfdpzEpJjM8enrgN` — Sun 4pm, math, code and sanity audit

Verified afterwards: **zero ATRAM routines remain active.** Eight spent one-shot
check-ins survive with `enabled=false` and `ended_reason=run_once_fired`; they
cannot fire and the default routines view hides fired one-shots, so they are
invisible clutter rather than live automation.

Three routines belonging to a **different project** (`ClaudeBinance`, Sundays at
06:00 and 16:00 UTC) were deliberately **not** touched — they are outside this
repo's scope and deleting them on an ambiguous instruction would have been
destructive.

### The page was claiming automation it no longer had

Deleting the routines made the dashboard's own Report tab false: it still said
"Two jobs, every Sunday" and described runs that would never happen. This is the
same class of error as the stale "three jobs" section found earlier today — the
page describing a maintenance regime that had changed underneath it.

Rewritten as **"Reviewed by hand"**: a four-step runbook in the order the review
should actually be done — refresh inputs, re-score and re-optimise, re-verify
claims, audit before publishing — with an explicit statement that there is no
automated refresh and that figures older than a week should be read as forecasts
on stale inputs. The renderer's "↻ … · weekly" suffix was removed with it.

One more stale promise, at source: the Asia Equity look-through gap note read
"Sunday job 2 retries weekly". Now "retry at each manual review".

A grep for `Sunday`, `auto run`, `weekly` and `↻` across the page and engine
returns nothing. `monitoring/README.md` is now a manual runbook rather than an
automation spec, and the root README matches.

Verified after the change: engine 19/19, page renders clean at 412px with no JS
errors, no SVG overflow and no horizontal scroll, 26 sources intact.

## 2026-09-03 — Audit: three real bugs found and fixed

Full adversarial audit run by hand rather than by firing the routine. Every
figure was re-derived from first principles by a script that reads only
`model/data.json` — it never imports the engine's own functions, so the engine
cannot mark its own homework. 120+ independent assertions.

### Bug 1 — peso figures did not reconcile with the page's own CAGR

`summarise()` compounded the RAW return while the page displayed the ROUNDED
one, so a reader multiplying out the printed CAGR could not reproduce the printed
peso value. The optimised portfolio showed 7.64% and P1,445,237, but
1,000,000 x 1.0764^5 = P1,445,002 — a **P235 gap with no visible explanation**,
and P462 on the trough row. On a page whose footer promises "all figures
computed from the published model engine", a figure the reader cannot check is
a defect. Terminal and trough are now compounded from the displayed values, so
the arithmetic ties out exactly.

### Bug 2 — the optimiser admitted portfolios over its own drawdown budget

Feasibility tested `round(d, 1) <= DD_CAP`, so a portfolio with a true drawdown
of −18.5099% displayed as −18.5% and was admitted against an 18.5% cap. Four
portfolios were inside the feasible set that should not have been, exceeding the
budget by up to 0.017pp. **The winner was unaffected** — 15/45/35/5 is still the
max-CAGR point under either test, verified independently — but a constraint that
says "<=" must actually mean it. Now tested on the true value.

### Bug 3 — dead code

`IDX`, a fund-id-to-index map, was built on every run and never read. Removed.

### Regression checks added (16 -> 19)

- peso figures reconcile with the displayed CAGR and drawdown
- no chosen portfolio exceeds the drawdown budget
- the optimum really is the max-CAGR point inside the budget

### What was checked and found correct

- **Volatility integration.** All four horizons re-derived with a 200,000-step
  Riemann sum against the engine's 4,000 — agreement to <0.02pp. Realised-equivalent,
  1-sigma and 2-sigma moves all consistent.
- **Drawdown calibration.** Still reproduces −20.2% for the S&P 500 and −33.1%
  for the Nasdaq-100 on their historical sigma/mu.
- **Correlation matrix.** Symmetric, unit diagonal, all |rho| <= 1, and positive
  semi-definite by Cholesky.
- **Portfolio variance.** Quadratic form re-derived for both portfolios; matches.
- **Optimiser.** 969 portfolios enumerated independently — count matches exactly,
  and the chosen point is confirmed optimal inside the budget.
- **Frontier.** Drawdowns strictly increasing, every point 5%-granular and summing
  to 100, optimised portfolio sits on the edge.
- **Gauge and regions.** Composite, all four horizon blends, the ACWI-IT mix
  weighting and every regional tilt re-derived from scratch; all match.
- **Fees.** gross − fees = net, and the four tilt components sum to the total,
  for all four funds.
- **39 hard-coded prose figures** cross-checked against the payload. **Zero stale.**
- **Plausibility.** Money market drawdown cash-like at −0.5%, no fund CAGR above
  15% or below 0, portfolio CAGR does not exceed its best component, portfolio
  drawdown shallower than its worst.
- **Page.** JS parses, no runtime errors, no SVG label outside its viewBox, no
  horizontal scroll at 412px, light theme holds, 26 https sources.
- **Palette.** Still passes colour-vision validation under `--pairs all`.

### Standing risk, not a bug

53 numeric literals live in the page's authored prose rather than coming from the
engine. All 39 checkable ones are currently correct, but this is structurally how
the "17 automated checks" error got in last time. The prose-vs-payload cross-check
above is now part of the audit and should be re-run every week.

## 2026-09-03 — Consolidated to two jobs; house cleanup

The three-job schedule is now two. The old "source scrub & fact-check" job
(11am, `trig_01QdvbeW9nq3kDzeUa93R2Ww`) is **deleted**; its work is folded into
the 6am job as Phase C.

| # | Job | Sunday PHT | Cron (UTC) | Model |
|---|---|---|---|---|
| 1 | Macro relevance + source fact-check | 06:03 | `3 22 * * 6` | Sonnet 5 |
| 2 | Math, code and sanity audit | 16:11 | `11 8 * * 0` | Opus 5 |

### Why

Two reasons, both evidenced by this week's failures.

**Rate limit.** The account limit is a five-hour rolling window and three
research-heavy sessions do not fit in one. Six runs were attempted on 2026-09-02
and exactly one produced usable output; every failure was the limit, not the
jobs. Two jobs ~10 hours apart give each its own window with room to spare.

**Duplicated research.** The macro refresh and the fact-check were both
re-reading the same central-bank and fund-manager sources. Merging them removes
a whole pass over the same material.

Job 1 now runs in four phases — macro refresh, re-score and re-optimise, source
fact-check, then validate/publish — pushing after each. Job 2 audits job 1's
output and has an explicit new step: confirm job 1 actually pushed rather than
only republishing.

### House cleanup

- Deleted the redundant 11am routine.
- Removed `model/__pycache__/` (untracked build residue).
- Rewrote `monitoring/README.md` and the root `README.md` for the two-job
  system; removed the stale three-job schedule tables.
- Fixed a routine name that had been stored HTML-escaped (`&amp;`).
- Repo is now 8 tracked files: the engine, its generated payload, the page, and
  four docs. Nothing else.

### Left alone deliberately

Three unrelated routines on this account belong to a different project
(`ClaudeBinance`) and were not touched. They fire Sundays at 06:02, 11:06 and
16:05 UTC. Job 2 fires at 08:11 UTC, which sits between two of them — if
rate-limit failures recur on Sundays, that interleaving is the first suspect.

## 2026-09-03 — Jobs 2 and 3 smoke test: both lost their work

Fired together at 23:27 UTC on 2026-09-02, after the rate-limit window reset.

| Job | Model | Outcome | Pushed | Republished |
|---|---|---|---|---|
| 2 source scrub | Sonnet 5 | stalled 23:39, resumed ~06:10, **completed** 06:17 | **no** | no |
| 3 math & code audit | Opus 5 | **failed** 23:40 on the five-hour limit | no | no |

Job 3 died 13 minutes in. Job 2 sat frozen on the limit for ~6.5 hours, resumed
when the window reset, and finished — its usage moved from $5.93/72,343 output
tokens to $7.39/77,459, so it did real work after resuming. It then pushed
nothing. Its container is gone and, unlike job 1, there is no published artifact
to recover it from: that research is simply lost.

**No damage, though.** The repo/page drift check passes (payloads deep-equal),
16/16 engine checks pass, the branch is clean at `3096b53`, and the artifact is
untouched. That is the push-before-republish ordering working as intended — a
run that dies now leaves nothing behind, instead of job 1's failure mode where
the page moved ahead of the repo.

### The finding that matters

**Job 2 ran with the hardened brief and still did not push.** That brief already
said, in capitals, that a republish without a matching commit is a failed run and
that the report must state the pushed SHA. Instruction-only enforcement is not
enough when the commit is the LAST step of a long run: the run may never reach
its last step.

Root cause is structural, not motivational. So all three briefs are rewritten
again around **commit early, commit often**:

- first push must land within 15 minutes, before the work is finished;
- push after every phase, or every few claims, not once at the end;
- explicit statement that there may be no end of run, because the five-hour
  limit stalls or kills a session without warning.

A run that dies half-way should now leave half its work safely on the branch.

### Tally for the day

Six job runs attempted, one produced usable output (job 1's Opus run), and even
that needed hand recovery. Every failure traces to the same five-hour rate-limit
window rather than to the jobs themselves. Three research jobs do not fit in one
window on any model. The Sunday schedule spaces them five hours apart, which is
the configuration that has never actually been tried — every manual test has
crammed them together.

## 2026-09-02 — Job 1 run on Opus: good work, but it never pushed

Job 1 was fired alone at 18:26 UTC on `claude-opus-5` (session
`cse_013jknbydkPpk617yZm6eHi9`). It ran ~15 minutes, completed, and republished
the artifact at 18:37:59Z. **It pushed nothing to the branch.** The live page
moved to a new macro vintage while the repo stayed at `c650455`, so the engine
in git no longer reproduced the published page — a direct violation of the
invariant that every figure on the page comes from `model/engine.py`.

Its research was good and is now recovered into the repo. What it found:

| Input | Was | Now |
|---|---|---|
| BSP policy rate | 4.75% | **5.00%** (3 hikes since April, +75bp) |
| PH CPI | — | **6.2% Jul**, 6.4% Jun — well above target |
| BSP inflation forecast | — | 6.1% (2026), 5.4% (2027) |
| USD/PHP | — | **62.565**, an all-time low |
| Brent | $91.28 | **$94.86** (+40.3% y/y) |
| VIX spot | 14.13 | **16.44** |
| ECB | hiked June | **held at 2.25%** on 23 July |
| Gauge | 5.3 | **4.78** |
| Sources | 21 | **26** |

Every regional score was cut (US 6.23→5.88, Europe 4.38→3.88, Asia 7.22→6.80,
PH 6.05→5.50), geopolitics went 2.5→1.5 on the Iran tanker strikes, and the FX
drift assumption rose 1.5%→2.0% on the peso's new low. **Both allocations held:
baseline 20/30/25/25 and optimised 15/45/35/5.** Forecasts rose to 7.48% /
−20.5% and 7.64% / −18.5%.

### Recovery

`model/engine.py` was reconstructed from the published payload and now
reproduces the live artifact's data block **exactly** (verified by deep
equality). `dashboard.html` was recovered from the live page so job 1's
narrative edits survive. No republish was needed — the live page was already
correct; it was the repo that was behind.

### Real bug found, in our own code

Reconstruction failed the sanity check `vol term structure is monotone rising`
on data that was correct. **The check encoded a false invariant.** Horizon
volatility is not monotone in T: it converges toward the long-run anchor, so
when the last liquid future sits above that anchor (Dec 20.38 vs anchor 19.5)
the 12M window can average above the 5Y window — which is exactly what happened
once spot VIX rose to 16.44 (12M 19.62 vs 5Y 19.57). The original build only
passed because spot was low enough to make the curve incidentally monotone.

Replaced with two correct invariants: horizon vol must **converge toward the
anchor** (`|σ5Y − anchor| ≤ |σ3M − anchor|`), and every horizon must sit in a
sane 10–40% band. Now 16/16 checks pass.

### Process fix

Job 1 republished a page whose engine failed a sanity check, and skipped its
push. Both routine briefs have been rewritten so that **commit and push happen
BEFORE the republish**, and the job must state the pushed commit SHA in its
report. A republish without a matching pushed commit is now defined as a failed
run.

## 2026-09-02 — Smoke test of all three routines: ABORTED on rate limit

All three routines were fired manually at 12:18 UTC to prove the monitoring
system works end to end. **All three failed**, none of them for a reason to do
with the jobs themselves.

| Job | Session | Ran for | Outcome |
|---|---|---|---|
| 1 macro relevance | `cse_01XLyRLZHRT6HW7cubaZumzp` | ~4m25s | failed — session limit |
| 2 source scrub | `cse_01Le4o3RQUuuZHeGSvhrRdtZ` | ~3m56s | failed — session limit |
| 3 math & code audit | `cse_01RW4B5qisvro9583iCvCPeZ` | ~3m31s | failed — session limit |

Every one reported `You've hit your session limit · resets 5:10pm (UTC)` with
`rate_limit_info.status = rejected` on the five-hour window. Firing three
research-heavy sessions concurrently, on top of this session's own work,
exhausted the shared five-hour budget within about four minutes.

**Nothing was committed and nothing was republished.** `origin/claude/android-
portfolio-macro-dashboard-awmpce` stayed at `6e9c697`, no `Smoke test` sections
were written to this file, and the artifact was untouched. The concurrency
mitigations (rebase-before-push, job 1 owning the republish, separate changelog
headings) were therefore never exercised — the run died before any job reached
the write stage.

### What this does and does not prove

- **Proved:** the routines fire, mint sessions, and start work. All three
  reached RUNNING and began their briefs.
- **Not proved:** that any job completes, commits, republishes, or that the
  conflict handling works. That still needs a clean run.

### Actions taken

1. Model for all three routines changed from the inherited `claude-sonnet-5`
   to **`claude-opus-5`** at the user's request. Schedules unchanged.
2. Do **not** fire all three at once again. On the real Sunday schedule they are
   70 minutes apart, which is well clear of the limit. If they must be tested
   manually, fire one, let it finish, then fire the next.

## 2026-09-02 — Checklist audit (run 2)

Full re-validation of every requirement against the live page and the engine.
22 DOM assertions run headlessly at 412px; 15 engine sanity checks. All pass.

### Errors found and rectified

1. **The three Sunday routines had no schedule and would never have fired.**
   They were created with the parameter named `cron` when the API expects
   `cron_expression`; the field was silently dropped and all three were stored
   as poke-only routines with `next_run_at = 0001-01-01T00:00:00Z`. Detected by
   listing the account's triggers and noticing the ATRAM three were missing from
   a `recurring: true` filter. Fixed with `update_trigger`; all three now show
   `next_run_at = 2026-09-06` (Sunday) at 01:12 / 02:23 / 03:37 UTC — 09:12 /
   10:23 / 11:37 PHT.
2. **Inconsistent decimal precision inside a single look-through column.**
   The renderer used `v.toFixed(v < 10 ? 1 : 2)`, so the Global Technology
   sector list showed `65.30%` next to `7.3%`. Replaced with a per-list `dp`
   field carried in the engine, so every figure in one column is formatted alike.
3. **Requirement gap: no stock-level detail on the fund slides.** The brief asked
   for funds, ETFs *and stocks*; the page had funds and ETFs plus index-level
   exposure only. Added a stock-level look-through section (see below).

### Added

- `LOOKTHROUGH` block in the engine, with three new sanity checks covering it.
- Verified top-10 equity holdings for the Nasdaq Equity Income sleeve
  (J.P. Morgan JEPQ factsheet, 30 June 2026): NVIDIA 6.7%, Apple 5.8%, Micron
  5.6%, Alphabet C 5.0%, Microsoft 3.9%, AMD 3.9%, Amazon 3.7%, Lam Research
  2.9%, Tesla 2.4%, Meta 2.4%. Sector tilt IT 50.9% / Comm Svcs 10.2% /
  Cons Disc 9.2%.
- Verified sector composition for Global Technology (Fidelity factsheet,
  LU1033663649): Technology 65.30%, Consumer Discretionary 11.73%, Industrials
  10.74%, Telecoms 7.33%, Real Estate 2.73%, Energy 1.43%, Managed funds 0.94%.
- Money market sleeve shown as its instrument curve rather than shares.

### Recorded as a gap, not filled

- **Asia Equity holdings are unverified.** The JPMorgan Asia Equity Dividend
  Fund's current positions could not be confirmed from any reachable primary
  source; the most recent published holdings found were from 2023 and are too
  stale to show. The page states this explicitly with a "not published" chip
  rather than substituting index constituents. Sunday job 2 retries weekly.
- **Fidelity does not publish a current top-10 at a reachable source**, so that
  sleeve shows sector composition only. Also retried weekly.

## 2026-09-02 — Initial build

- Built `model/engine.py`: volatility term structure by forward-variance
  integration, seven-driver macro gauge, four-region ranking across
  3M/6M/12M/5Y, per-fund return build-up net of all fees, drawdown model,
  full enumeration of the 969 five-percent-granular allocations, scenario grid.
- Baseline portfolio (5-year horizon, no cycle view): **20 / 30 / 25 / 25**
  → 6.98% strategic CAGR, −20.8% expected max drawdown.
- Optimised portfolio (macro-adjusted, drawdown-budgeted): **15 / 45 / 35 / 5**
  → 7.31% CAGR, −18.6% expected max drawdown, return-per-drawdown 0.393.
- Macro gauge: **5.3 / 10**.
- All 12 engine sanity checks pass.
- Chart palette validated for colour-vision safety under `--pairs all`.
- Published to https://claude.ai/code/artifact/307440fd-2952-4b4c-b55c-51725163be31
- Registered the three Sunday routines.

### Known limitations recorded at build time

- `atram.com.ph`, `uitf.com.ph`, `fred.stlouisfed.org`, `bworldonline.com` and
  most primary-source domains are blocked by this environment's egress proxy.
  All figures were therefore verified through `WebSearch` results quoting those
  primary sources, not by direct fetch of the source documents. Job 2 should
  retry direct fetches each week.
- Two target-fund ongoing charges (JPM Asia Equity Dividend, Fidelity Global
  Technology) are estimates at 0.80% and 0.95%. Both are labelled "part est."
  on the page's fee table.
