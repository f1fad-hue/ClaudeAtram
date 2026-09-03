# Monitoring system

Three scheduled jobs run every Sunday. They exist so nothing on the dashboard
quietly goes stale, and so that any error in the data, the math or the code is
found by the system rather than by the reader.

| # | Job | Sunday, PHT | Cron (UTC) | Routine ID |
|---|-----|-------------|------------|------------|
| 1 | Macro & correlated-sentiment relevance | 06:03 | `3 22 * * 6` | `trig_01UxqDnGKQh8QML6z2fziamx` |
| 2 | Source scrub & fact-check | 11:07 | `7 3 * * 0` | `trig_01QdvbeW9nq3kDzeUa93R2Ww` |
| 3 | Math, code & sanity audit | 16:11 | `11 8 * * 0` | `trig_01WrfrLEAfdpzEpJjM8enrgN` |

**Job 1's cron day is Saturday, not Sunday, and that is correct.** Cron is
evaluated in UTC. Sunday 06:00 PHT is Saturday 22:00 UTC, so `* * 6`. Jobs 2
and 3 are morning/afternoon PHT and stay on Sunday UTC. If you ever edit these,
check `next_run_at` afterwards — it is the only reliable proof the day is right.

The ~5 hour spacing is deliberate. The account's rate limit is a five-hour
rolling window; three research-heavy Opus sessions inside one window will
exhaust it, which is exactly what killed the 2026-09-02 smoke test. Keep the
jobs at least five hours apart and never fire them concurrently.

Jobs 1 and 2 run on **`claude-sonnet-5`**; job 3, the audit gate, runs on
**`claude-opus-5`** (set 2026-09-02). Routines created without
an explicit model inherit the environment default, which was Sonnet 5; the model
only applies to fires that create a new session, which all three do.

All three verified scheduled, next firing Sunday 2026-09-06 (job 1 at
`2026-09-05T22:03Z`, job 2 at `2026-09-06T03:07Z`, job 3 at `2026-09-06T08:11Z`).
If a routine
ever shows `next_run_at` of `0001-01-01T00:00:00Z` it has **no schedule** and
will never fire — the schedule field is `cron_expression`, not `cron`, and an
unrecognised field is dropped silently. Re-check this after any trigger edit.

Each fires a fresh Claude Code session in this environment with a complete
standalone brief. They run in order so that job 3 audits the work of jobs 1 and 2.

- **Live artifact:** https://claude.ai/code/artifact/307440fd-2952-4b4c-b55c-51725163be31
- **Branch:** `claude/android-portfolio-macro-dashboard-awmpce`

Jobs republish to the **same** artifact URL by passing it as the `url` parameter,
so the link the user holds never changes.

## Invariants — a job must never break these

1. All four funds appear in both portfolios, always. Never drop one.
2. Every allocation weight ends in **5 or 0** and each portfolio sums to **100**.
3. Every figure on the page comes from `model/engine.py`. If a number is typed
   into `dashboard.html` by hand, it is a bug — move it into the engine.
3a. **Commit early, commit often.** The first push must land within 15 minutes
   and work must be pushed after each phase, never batched into one final commit.
   The five-hour rate limit stalls or kills a run without warning, so a job may
   never reach its last step. On 2026-09-02 two jobs completed their research and
   lost all of it this way — one of them while running a brief that already
   demanded a push in capitals. Instruction alone does not fix a last-step
   failure; frequent pushes do.
3b. **Push BEFORE you republish, always.** The repo is the source of truth; the
   artifact is a rendering of it. Republishing without pushing leaves the engine
   unable to reproduce the live page, which happened on 2026-09-02 and had to be
   reverse-engineered out of the published payload. A republish with no matching
   pushed commit is a failed run, however good the research was.
4. `python3 model/engine.py` exits 0 with all sanity checks passing *before*
   anything is republished.
5. Only primary sources. The issuing institution's own publication, never an
   aggregator or a secondary quote of it.
6. An unverifiable number is **labelled on the page as an estimate**, never
   quietly presented as fact.
7. Light theme, mobile-first, bottom tab bar. Do not redesign it.

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

## Running the engine

```
python3 model/engine.py           # audit report + sanity checks (exit 0 = pass)
python3 model/engine.py --json    # payload consumed by dashboard.html
```

The engine has no third-party dependencies. Regenerate `model/data.json` and
re-embed it into `dashboard.html` (the `<script id="D">` block) after any change.

## Caveat on fired sessions

The routines were created without MCP connector grants, so the sessions they
fire have Bash, git, WebSearch and the Artifact tool, but **not** the GitHub
MCP tools. Push with `git push -u origin <branch>`, not the GitHub API.
