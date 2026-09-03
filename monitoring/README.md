# Monitoring system

Two scheduled jobs run every Sunday. They exist so nothing on the dashboard
quietly goes stale, and so that any error in the data, the math or the code is
found by the system rather than by the reader.

| # | Job | Sunday, PHT | Cron (UTC) | Model | Routine ID |
|---|-----|-------------|------------|-------|------------|
| 1 | Macro relevance + source fact-check | 06:03 | `3 22 * * 6` | Sonnet 5 | `trig_01UxqDnGKQh8QML6z2fziamx` |
| 2 | Math, code and sanity audit | 16:11 | `11 8 * * 0` | Opus 5 | `trig_01WrfrLEAfdpzEpJjM8enrgN` |

**Job 1's cron day is Saturday, not Sunday, and that is correct.** Cron is
evaluated in UTC. Sunday 06:00 PHT is Saturday 22:00 UTC, so `* * 6`. Job 2 is
afternoon PHT and stays on Sunday UTC. After any edit, check `next_run_at` — it
is the only reliable proof the day is right. A routine showing `next_run_at` of
`0001-01-01T00:00:00Z` has **no schedule** and will never fire: the field is
`cron_expression`, not `cron`, and an unrecognised field is dropped silently.

## Why two jobs, not three

Until 2026-09-03 this was three jobs at 5-hour spacing: macro relevance, source
fact-check, then audit. That failed repeatedly. The account's rate limit is a
five-hour rolling window, and three research-heavy sessions cannot fit in one —
six runs were attempted on 2026-09-02 and exactly one produced usable output.

The macro refresh and the fact-check were also doing the same research twice:
both had to re-read the same central-bank and fund-manager sources. Merging them
into one 6am job removed the duplication, and the ~10 hour gap to the 4pm audit
means each job now gets its own rate-limit window with room to spare.

Job 1 gathers and updates. Job 2 audits what job 1 did. Do not add a third.

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

## Caveats on fired sessions

- The routines carry no MCP connector grants, so fired sessions have Bash, git,
  WebSearch and the Artifact tool but **not** the GitHub MCP tools. Push with
  `git push -u origin <branch>`, not the GitHub API.
- **Do not fire both jobs at once to test them.** Every manual test that ran them
  concurrently exhausted the rate-limit window and lost the work. Fire one, let
  it finish, then fire the other — or just let the schedule do it.
- This account also runs three unrelated routines for a different project
  (`ClaudeBinance`) at 06:02, 11:06 and 16:05 UTC on Sundays. Job 2 fires at
  08:11 UTC, which lands between two of them; if rate-limit failures recur on
  Sundays, that interleaving is the first thing to look at.
