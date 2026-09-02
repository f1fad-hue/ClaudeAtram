# Monitoring system

Three scheduled jobs run every Sunday. They exist so nothing on the dashboard
quietly goes stale, and so that any error in the data, the math or the code is
found by the system rather than by the reader.

| # | Job | Sunday, PHT | Cron (UTC) | Routine ID |
|---|-----|-------------|------------|------------|
| 1 | Macro & correlated-sentiment relevance | 09:12 | `12 1 * * 0` | `trig_01UxqDnGKQh8QML6z2fziamx` |
| 2 | Source scrub & fact-check | 10:23 | `23 2 * * 0` | `trig_01QdvbeW9nq3kDzeUa93R2Ww` |
| 3 | Math, code & sanity audit | 11:37 | `37 3 * * 0` | `trig_01WrfrLEAfdpzEpJjM8enrgN` |

All three verified scheduled: `next_run_at` = 2026-09-06 (Sunday). If a routine
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
