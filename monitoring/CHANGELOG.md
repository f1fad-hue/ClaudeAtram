# Changelog

Newest first. Each Sunday job appends here. Every error found gets recorded
before it gets fixed.

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
