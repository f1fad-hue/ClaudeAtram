# Changelog

Newest first. Every error found gets recorded before it gets fixed.

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
