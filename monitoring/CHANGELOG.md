# Changelog

Newest first. Every error found gets recorded before it gets fixed.

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
