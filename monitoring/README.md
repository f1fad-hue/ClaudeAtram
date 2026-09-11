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
9. Every figure quoted in a driver note, region note or fund note must equal the
   input it names. The page has contradicted itself on Brent twice; a general
   prose-vs-input guard now checks the named quantities on every run.

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

