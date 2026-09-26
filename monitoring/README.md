# Review runbook

**There is no automation. This is a manual runbook.**

Both Sunday routines were deleted on 2026-09-03 at the owner's request — the
review is now done by hand. Nothing re-runs on a schedule, nothing republishes
the artifact on its own, and no figure on the page refreshes itself. The page
carries an as-of date; once that date is more than a week old, treat every
forward-looking number as a forecast built on stale inputs.

This file is what to do when you sit down to review it. `CLAIMS.md` is the
checklist of every figure and where it came from. `CHANGELOG.md` is the history,
including every bug found so far and how it was fixed — read it before changing
anything, because several of the traps are subtle and already documented.

## The review, in order

**1. Refresh the macro inputs** — the `VERIFIED INPUTS` block in
`model/engine.py`. Policy rates (Fed, ECB, BSP), prices (US CPI from BLS, PH CPI
from PSA, Brent), the VIX complex (spot plus the four observable futures — LEVELS only; the
maturities are derived from the settlement calendar, do not type them), the PH
T-bill curve and USD/PHP. Primary sources only. If one is unreachable, leave the
prior value and mark it stale — never guess.

**2. Re-score and re-optimise.** Seven drivers and four regions across
3M / 6M / 12M / 10Y, then the gauge. Drivers and regions are researched on 1–10;
both the headline gauge and the regional rankings are reported on 1–5. The optimised portfolio is built from four
inputs — the broad gauge, the correlated per-sleeve transmission, the **volatility
gap** (horizon-blended implied vol minus the LONG-RUN 19.5 every base return already
assumes, same horizon weights as the regional blend) and the regional rankings. Two of those are derived rather than judged: the
regional tilt is `(score − 3.0) × 0.675` on the reported 1–5 scale (identical to
the old `(score − 5.5) × 0.30` on the 1–10 research scale), and each fund's volatility tilt is
`gap × sensitivity`, where the sensitivities in `VOL_SENS` are structural properties
of how each sleeve is built. Change a sensitivity only if the fund's structure changes,
not because you have a view on the market. Never change a score without rewriting
its rationale to cite the new evidence. Re-run the optimiser; weights stay
multiples of 5, sum to 100, and hold all four funds at 5% or more. There is **no
single-fund cap** since 2026-09-24 (the owner's decision; it was 50% from 9 Sep):
the drawdown budget is what limits concentration, and the page publishes what the
old 50% cap would have chosen beside the actual choice. Reinstating a cap means
a max-weight filter back in `enumerate_portfolios` and `_best_without` in
`engine.py`, plus the page passages that describe the choice.

**3. Re-verify the claims** in `CLAIMS.md`, marking each VERIFIED / CHANGED /
STALE / UNREACHABLE with the date. Do not promote a claim from "verified via
search result" to "verified at primary source" unless you actually opened the
document.

**4. Audit before publishing.** Run the engine — every check must pass, and never
loosen one to get green. A check can encode a false assumption; one did, and the
fix is recorded in the changelog. Confirm the published page and the engine still
agree figure for figure. Cross-check the figures written into the page's prose
against the payload. Render at 412px and look at it.

**5. Publish, then push** — or better, push first. The repo is the source of
truth; the artifact is a rendering of it.

## Invariants — a job must never break these

1. All four funds appear in both portfolios, always. Never drop one.
2. Every allocation weight ends in **5 or 0** and each portfolio sums to **100**.
3. Every figure on the page comes from `model/engine.py`. If a model OUTPUT is
   typed into `dashboard.html` by hand, it is a bug — move it into the payload and
   render it. `checklist.js` enforces this two ways: C1 requires every hard-typed
   figure to be a rounding of some payload number, and C2 is a ratchet freezing the
   count of hard-typed figures at 41 (all inputs and constants, no outputs). C1
   alone is not enough — it cannot catch a wrong figure whose value coincides with
   an unrelated model number, which is exactly how a stale −40% drawdown survived.
   Raise the ratchet only with a reason.
4. `python3 model/engine.py` exits 0 with all sanity checks passing *before*
   anything is republished.
5. Only primary sources. The issuing institution's own publication, never an
   aggregator or a secondary quote of it.
6. An unverifiable number is **labelled on the page as an estimate**, never
   quietly presented as fact.
7. Light theme, mobile-first, bottom tab bar. Do not redesign it.
8. Anything the calendar determines is **derived, never typed**. VIX futures
   maturities come from the settlement rule and `VIX_QUOTE_DATE`; typing them
   is how the time axis silently drifted three days off its own prices.
9. Every number in a driver, region or fund note must be a rounding of a published
   input — not just the named quantities. The verifier enforces this; it is how a
   stale "closed 4.92%" and a "$106 oil" survived guards that only looked near the
   word "Brent". A model assumption stated only in prose is not published: if a
   number moves the model, it goes in the inputs.
10. State a disruption on the measure that reaches the portfolio. Hormuz was
   published as a "~93% shutdown" from vessel counts while oil flows were at
   two-thirds of pre-war — a claim the model's own Brent input contradicted. Where
   sources disagree, publish the range, not the most dramatic number.
11. Never pair one source's current reading with another source's baseline. Goldman's
   15.5 mb/d against a 20.0 mb/d baseline from a different measure gave 22% where
   the source said a third. Keep a source's own pair together.
12. Reference data (fund fact sheets, holdings, sector splits) must carry a real
   date — day precision, not "2026" — and be within 60 days of `REVIEW_DATE`. The
   JEPQ table sat on a 73-day-old sheet with Tesla in a top ten it had already left.
13. `AS_OF` is the market data date; `REVIEW_DATE` is when a human last worked the
   page. They are not the same on a weekend, and reference data retrieved during a
   review is legitimately newer than the market snapshot.
17. A market print that will not CHAIN is not a print. Every close must reproduce
   the next day's published move; where three reported figures for one session are
   mutually inconsistent, publish none of them and say the series lags. The
   arithmetic chain also settles disputed DATES - a move off a confirmed close can
   only belong to the next trading session.
19. Renaming or removing a payload field IS a page change - the page reads fields by
   name, and no data-level check can see the break. Grep `dashboard.html` for the
   field name BEFORE the rename. Three page breaks in four days came this way.
20. An input named for a pending event must be renamed when that event resolves.
   `fed_hike_odds_sep` outliving the September FOMC asserted that a decided meeting
   was still open. Catalysts leave the list when they happen; so do their inputs.
   The rename is only half of it: GREP THE PROSE that reads the field. The report
   tab still said "FedWatch puts the 16 September hike at 50.9%" after the field
   had correctly become `fed_hike_odds_oct`, so the number was right and the
   sentence was a lie.
21. A prose check that asks "does this quote match SOME published input" is not a
   staleness check. "Brent at $109" passed for nine days because $109 is within a
   dollar of the dated four-month high, while spot was $103.87. Scope by CONTEXT,
   not by loosening or tightening tolerance: an undated present-tense quote must be
   spot; only a quote sitting beside a date may cite a dated input. Dateness
   attaches to the QUOTE, not to its sentence - one sentence holding both a current
   level and a dated high will otherwise exempt both. And do not key the pattern on
   a benchmark's name: "$106 oil" names nothing and drifted underneath a regex that
   required the word "Brent".
22. A superlative is a claim about WHICH number, not just how big. "Its highest
   since 2007" was rendered from `ust_10y_prev` - correct only while the previous
   close and the intraday peak coincided, which ended the day they diverged. If a
   figure carries a superlative, bind it to the input that owns the superlative,
   and DATE it: `brent_high` had its date typed into prose and was wrong by five
   days from the moment the high moved.
23. A stale input ages SILENTLY when everything paired with it ages too. The VIX
   strip and its spot are quoted together, so every internal consistency check kept
   passing while the pair drifted 15 days from the market. Two things fix that, and
   both are needed: an EXPIRY derived from the data's own structure (one 30-day
   roll window, because past that the front contract has settled), and an
   INDEPENDENT reading that the model never sees - VIX3M measured the error at
   -4.97% and gave its sign, which disclosure alone never did.
47. EDITING A SENTENCE IS NOT EDITING ITS NUMBERS. Confirming the 23 Sep 10-year
   at 5.12 changed the parenthetical beside it and left "5.11% on the 23rd" standing;
   nothing tied the note's run of closes to the series. Every "X.XX% on the Nth" in
   the Monetary and US notes is now checked against the series by date, and the
   Report's typed Global Technology claims are asserted against the payload.
46. ONE MOVE, ONE NUMBER ON THE PAGE. The Volatility lede recomputed the VIX move
   from two rounded closes (-5.23%) beside a note quoting the source (-5.24%). Where
   a reported figure exists the page prints it, at its reported precision; the
   recomputed one is published under its own name for the audit.
45. A CHECK'S TOLERANCE MUST INCLUDE THE ROUNDING OF ITS OWN INPUTS. The VIX
   reported-move check recomputed a percentage from two 2dp closes and held it to
   the move's own precision, so it rejected a correct "-5.24% to 14.85" (15.67 x
   0.9476 = 14.849). Test on the implied level, as the index chains do, and allow
   the carried close's half-cent - a misdated close still misses by dollars.
44. A PLOT'S BUCKETS ARE NOT ITS CLAIM. The frontier was the best portfolio in each
   whole-percent drawdown bucket, so a point just over the budget could win the
   optimum's bucket and draw the "edge" above a portfolio the page says sits on it.
   Build the chart from the property the prose asserts (here, efficiency), and check
   that property rather than the construction.
43. COUNT EACH EFFECT ONCE, AGAINST THE SAME REFERENCE. Every base return here is a
   long-run return, which already assumes long-run volatility; the volatility tilt was
   measured from today's spot, so the rise to the long-run level was counted in the
   base and again in the tilt (+0.96pp to one sleeve, -0.56pp to another). A tilt is
   a deviation, and it must be a deviation from what the base already contains. The
   same test, applied to Asia's re-rating credit, is still open (see CLAIMS).
42. A NUMBER BESIDE ITS OWN RECIPE MUST BE COMPUTED FROM IT. The Nasdaq Equity
   Income gross return was typed as 7.2% for 23 days beside a note whose arithmetic
   gives 6.74%. The traceability fix of 12 Sep made the recipe's numbers into inputs
   so the prose would trace - and never connected them to the calculation. An input
   nothing consumes is decoration. Every gross return is now computed from named
   inputs, a check reproduces it, and the dangerous case (the sleeve that decides the
   allocation) is the one to re-derive first each review, not the market prices.
41. A HARNESS THAT PRINTS WITHOUT A VERDICT IS NOT A CHECK. `validate.js` dumped
   JSON, and five of its fields read `false` for weeks - three because it read
   `document.body.innerText` after visiting every tab (only the last, visible
   panel), two because they looked for "5y"/"5Y" labels the 10-year mandate no
   longer prints. Nothing failed, so nothing was fixed. Every harness states
   PASS/FAIL per requirement and exits non-zero on failure; and requirement 1 is
   validated against the PUBLISHED copy, because the host supplies the viewport.
40. A DATE MUST BELONG TO THE NUMBER IT LABELS. The T-bill look-through was
   labelled with the page's as-of date on the theory that it was "the live curve";
   it was never refreshed after 2 Sep, so the label made a 22-day-old curve look
   current. Date a figure by its own observation (the auction, the fact sheet, the
   close), bound its age against its own cadence, and never borrow a date.
39. "WHAT WOULD CHANGE THIS VIEW" IS A COUNTERFACTUAL THE ENGINE CAN RUN - SO RUN IT.
   The Report said that Brent under $70 and the Fed cutting would send Global
   Technology "back to a full weight". Re-running the optimiser with the rates and
   energy drags at neutral left the allocation exactly where it was; the input that
   actually decides the concentration - the volatility ramp - was listed as a
   footnote. Every trigger on that list is now an engine counterfactual
   (`WHAT_IF`), checked to use the live optimiser and re-derived by the audit.
38. A RISK ADJUSTMENT APPLIES TO THE QUANTITY IT WAS REASONED ABOUT. The income
   sleeve's drawdown k was cut 1.65 -> 1.55 because its drawdowns "run shallower than
   the RAW volatility implies" - but k multiplies its own volatility, already 0.681x
   the raw index, and the option premium is already in its return. One cushion,
   counted three times. It was harmless at 30% of the portfolio and set the
   allocation at 75%: an assumption's error grows with the weight riding on it, so
   when a sleeve becomes dominant, re-read every adjustment attached to it.
37. A REGISTER CHECK READS THE HEADLINE, AT THE HEADLINE'S OWN PRECISION. The
   CLAIMS check matched ANY number in a row within 0.011. A Brent row still reading
   "$99.25" passed on 2026-09-23 because the same row listed 103.08 as a disputed
   candidate, and an optimised drawdown k of "1.626" - the 15/45/35/5 allocation's -
   passed against the model's 1.61765 for fifteen days, from the 9 Sep move to
   15/50/30/5. A register figure matches only
   when the model value rounds to it at the register's published precision, and
   where a row bolds its headline, only the headline counts.
36. HISTORY BINDS TO DATED POINTS, NEVER TO ROLLING FIELDS. The page's account of
   the 21 Sep oil dispute ("Tuesday settled Brent at...") was bound to `brent`,
   `brent_prev` and `brent_chg_pct` - the LIVE fields. The next roll would have
   printed Wednesday's +3.86% settle, dated Wednesday, as Tuesday's fall. Any input
   that a narrative quotes after it has stopped being current belongs in a dated
   series (`brent_history`, like `vix_history` and `ust_10y_history`) and is read by
   date. The same goes for a FIXED BASE under a rolling ratio: Brent's "y/y" was
   measured against a base implied on 4 Sep and never moved, 19 days off its
   anniversary by the 23rd. A base carries its date, and a check bounds the drift.
35. A SETTLE CHAINS ONLY TO THE PREVIOUS SETTLE OF THE SAME CONTRACT. On 2026-09-23
   the October WTI contract expired, and every later WTI print was November; the
   first pass compared them with October's final settle, found a $2-5 "miss", and
   withheld a settle that was never in dispute. Front months are set by the exchange
   calendar (NYMEX CL: 3 business days before the 25th of the prior month; ICE Brent:
   last business day of the second month prior), so they are DERIVED (invariant 8)
   and a chain across a roll fails. And a candidate that reproduces its OWN reported
   percentage proves only that its arithmetic was done - on the 23rd two Brent prints
   did. What picks between them is independent evidence: the post-settlement
   direction ("snapped a five-day losing streak").
34. TWO VERIFIERS THAT ROUND DIFFERENTLY WILL EVENTUALLY DISAGREE ABOUT A NUMBER
   THAT IS OTHERWISE CORRECT. The driver-tilt transmission multiplies a typed
   constant by a scale factor derived from a driver score; on 2026-09-23 that
   scale hit exactly 2.5 for the first time, and two funds' tilt products landed
   exactly on a .5-at-the-2dp boundary (0.25*2.5=0.625, -0.05*2.5=-0.125). Python's
   `round()` rounds half-to-even (0.625->0.62); the independent checklist's `r2()`
   rounds half-up (0.625->0.63). Both are "correct" roundings of a correct number,
   and they silently disagreed by 0.01 at the boundary - latent from the moment the
   transmission was added that morning, and invisible until the afternoon's driver
   move happened to produce an exact tie. Pick ONE convention
   (round-half-up is the more defensible one for a financial model) and use it
   EVERYWHERE two things must agree bit-for-bit on a rounded value: the engine, the
   independent audit's re-derivation of the same arithmetic, and any verifier that
   checks it. A tolerance does not fix this - the disagreement is exactly 0.01, not
   noise - the rounding function itself has to match.
33. A REQUIREMENT IS CHECKED ON ITS MECHANISM, NOT ITS WORDING. Checklist item 15
   ("optimised from macro + correlated sentiment + volatility + regional") asked
   whether those words appeared on the page, and passed for three weeks while no
   macro driver reached any fund: the rates and energy tilts were typed constants.
   For every requirement that says "X is built from Y", the check must perturb or
   re-derive Y and show X move. If a check would pass on a page whose code does
   nothing, it is testing the copywriting.
32. WHEN A SERIES MIXES TWO KINDS OF NUMBER, EVERY SYMPTOM LOOKS LIKE A DIFFERENT
   BUG. The 10-year's wrong date, its "disputed" session and its intraday-as-close
   error were one defect: CNBC mid-session prints (3dp) mixed with official closes
   (2dp). State the basis of every series, keep one basis per series, and use the
   precision as a tripwire.
31. A HEURISTIC THAT CANNOT BE CHECKED IS NOT EVIDENCE. The Brent-WTI spread
   "favoured" the wrong Monday settle; the next session's chain found the right
   one. Withholding cost one day of a stale number. Publishing on the heuristic
   would have cost a wrong one. And a check of the form "value is one of the
   candidates" is the runbook-21 weakness again - it passes the wrong candidate.
30. A DATE IN A COMMENT IS NOT A DATE. `ust_10y` was a scalar with `# 18 Sep
   close` beside it; the comment was WRONG for two days and nothing could read it
   to find out. Every market input carries its own date field now, every one is
   bounded against AS_OF, and any series that can have a gap is a SERIES, not a
   scalar. The same applies to a weekday typed beside a date (runbook 20 region).
29. THE CHAIN RULE BELONGS IN CODE, not in a sentence. "A print that will not
   reproduce the next session's published move is not a print" has now caught a
   value dispute (15 Sep VIX), a dating error in that dispute (17 Sep), and a
   dating error nobody had questioned (the 10-year, 21 Sep). Publish the PREVIOUS
   close as an input so the chain is checkable rather than asserted. And a real
   number on the wrong date is the hardest error to see, because every sanity
   check on the NUMBER passes.
28. EVERY PUBLISHED FIGURE IS COMPUTED FROM THE FIGURES PUBLISHED BESIDE IT, not
   from the raw values behind them. This has now been the defect five times. An
   exact algebraic identity does NOT exempt a step: to5() is affine and the
   horizon weights sum to 1, so blending then rescaling equals rescaling then
   blending - until either side is rounded, and to5() rounds to 2dp. That printed
   a US regional blend of 3.15 above four scores averaging 3.14. And agreement
   today is not the same as correctness: the headline drawdowns matched the
   reader's route by 0.006pp of luck. When a bite test cannot fail on live data,
   CONSTRUCT the divergence and prove the check fires on it.
26. The rule reaches the SCREEN, not just the payload. The regional row was right
   in the payload and still did not add up rendered, because the horizons printed
   at 1dp against a 2dp blend. Check the arithmetic against the DOM cells.
27. When two rules each admit what the other rejects, apply BOTH. Feasibility on
   the raw drawdown admits a portfolio that PRINTS as over budget; feasibility on
   the rounded one admits a portfolio genuinely over budget by up to 0.05pp. The
   cap must hold as computed AND as shown. A fix that surfaces a second defect the
   same day usually means the first was hiding it, not causing it.
25. A DUPLICATE ELEMENT ID renders the second one empty and nothing can see it.
   `getElementById` returns the first match, so the payload is right, the setter
   reports success, no JS error is thrown, and every data-level check passes while
   a sentence reads "from one market close, , and the strip has not been re-quoted".
   Two checks now: no duplicate id on the page, and no renderer target left empty.
   LOOK AT THE RENDERED PAGE every pass - this was found by reading a screenshot,
   not by a harness.
24. C1 and C2 only see elements carrying `class="num"`. A live figure written
   straight into a heading is invisible to both - "A 2.7 market" sat above a gauge
   reading 2.39 in the first heading on the page, and C1 would not have flagged it
   even if it had scanned, because 2.7 traces: it is also the CPI food print.
   Check G now requires a heading to carry no number or to read one from an id.
18. Refactoring a block of inputs can delete inputs. The "every published input is
   cited" check finds orphans, not removals. After any structural edit, diff the
   input keys before and after.
16. Derive every tolerance from the publication precision of the figures it
   compares, and re-derive it when that precision changes. A hand-picked constant
   has now been the defect twice, and a 0.006 left behind by a 3dp-to-5dp change
   was 1200x too loose. Never copy a tolerance into the verifier - re-derive it
   there, or both harnesses fail the same way on the same day.
15. Validate that data reaches the SCREEN, not just that it is correct in the
   payload. The catalyst block was deleted from the markup and went unnoticed for
   three days because every check validated the payload and the renderer's own
   `if (!host) return` guard swallowed the missing mount point. Defensive guards
   hide missing mount points; count rendered rows against payload rows.
14a. A tolerance derived from the same quantity it is checking cannot detect a
   defect in that quantity. Prefer "does the reader land on the printed number" to
   any propagated-error bound. And never let a check recompute a value the payload
   already publishes — that compares the engine to itself.
14. An unsourced constant that happens to be right is still unsourced. `vol_beta`
   carried 0.68 for months; J.P. Morgan publishes 13.9/20.4 = 0.681. Derive it from
   the published pair, and make the verifier read the same published figures rather
   than keeping its own copy of the constant.

## Authoritative source set

Central banks and statistical agencies: federalreserve.gov, bls.gov,
ecb.europa.eu, bsp.gov.ph, treasury.gov.ph, imf.org, eia.gov, cboe.com.
Fund managers' own documents: ATRAM (atram.com.ph), J.P. Morgan Asset
Management (am.jpmorgan.com), Fidelity International, and the TOAP UITF
portal (uitf.com.ph).

> Note: several of these domains are blocked by the network egress proxy in
> this environment. When `WebFetch` returns `EGRESS_BLOCKED`, fall back to
> `WebSearch`, and record in `CLAIMS.md` that the figure was verified via
> search result rather than a direct fetch of the primary document.
>
> Both channels can be down at once — on 2026-09-10 `WebSearch` was unavailable
> for every query and no research was possible at all. When that happens: do not
> refresh a single input. Leave every value at its prior figure, leave `AS_OF`
> where it is, say plainly in the report that the pass was validation-only, and
> do the math/code half of the review, which needs no network. A model whose
> inputs are honestly a week old is worth more than one carrying numbers that
> were guessed to look current.

## Running the engine

```
python3 model/engine.py                      # audit report + checks (exit 0 = pass)
python3 model/engine.py --json > model/data.json   # regenerate the payload
```

`--json` writes to **stdout**; it does not update `model/data.json` on its own.
That matters more than it looks: on 2026-09-10 the independent verifier — which
reads only `model/data.json` — passed 184 checks against a payload one engine-run
behind, because the redirect had been skipped. Both commands above, then re-embed
into `dashboard.html`'s `<script id="D">` block, in that order, every time. The
verifier now refuses to run unless `model/data.json` is byte-identical to the
payload the page carries, so this cannot pass silently again.

The engine has no third-party dependencies.

