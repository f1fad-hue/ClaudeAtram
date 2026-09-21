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
ramp** (horizon-blended implied vol minus spot, same horizon weights as the regional
blend) and the regional rankings. Two of those are derived rather than judged: the
regional tilt is `(score − 3.0) × 0.675` on the reported 1–5 scale (identical to
the old `(score − 5.5) × 0.30` on the 1–10 research scale), and each fund's volatility tilt is
`ramp × sensitivity`, where the sensitivities in `VOL_SENS` are structural properties
of how each sleeve is built. Change a sensitivity only if the fund's structure changes,
not because you have a view on the market. Never change a score without rewriting
its rationale to cite the new evidence. Re-run the optimiser; weights stay
multiples of 5, sum to 100, and hold all four funds.

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

