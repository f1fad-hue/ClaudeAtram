# The review command

The owner's standing instruction for every review, kept here so a session can be told
"Run the ATRAM review in monitoring/REVIEW_COMMAND.md" and every change to it is versioned.
Updated 2026-11-12 (after v101): Portfolio C retired, so the command covers A, B and D; the
Report tab has its own step; periodic items, contract rolls and the runbook's evidence lessons
are named. The runbook (`README.md`) says how; this file says what.

```text
ATRAM review: bring the dashboard up to today, check every number on every tab, fix
what's wrong, clean up, and publish it to https://claude.ai/artifact/6z2thyg2HaHjFtcbjKhnUY
(code: f1fad-hue/ClaudeAtram, branch claude/android-portfolio-macro-dashboard-awmpce).
The portfolios are A, B and D (C was retired on 12 Nov 2026). I hold Nasdaq Equity Income.

Before you start
• Read the runbook (monitoring/README.md) and the newest changelog entry, and carry
  forward its "due before the next review" list.
• Test the primary sources and name any blocked: the exchanges (Cboe, CME FedWatch, ICE,
  PSE, KRX, JPX), the agencies (the US Treasury, the Fed, BLS, FRED, IMF PortWatch, the
  Bureau of the Treasury, PSA, BSP), uitf.com.ph, atram.com.ph and the target managers' sites.
• State the cut-off time (UTC) and which sessions had closed by then (New York, Manila,
  Tokyo, Seoul, the Brent and WTI settles, Treasuries), and any market holiday. If the work
  pauses, move the cut-off forward at most twice, then publish with the gaps named.
• Say which periodic items fall due: the weekly full fund check, a month-end band review,
  a quarter-end trend roll, and any contract roll or expiry (WTI, Brent, VIX futures).

Evidence rules (apply to everything below)
• Use a figure only if two independent sources agree and it adds up with the previous
  one (prior close + reported move = new close). Syndicated copies of one wire story,
  and rewrites of it, count as one source. Record any outlier as a dispute.
• If no two independent sources agree, or only one exists, keep the last confirmed figure
  and record the dispute; never pick one of the conflicting figures. A dispute is settled
  only when the primary source (the exchange, agency or manager) and one independent
  source agree. Re-try every open dispute and withheld session at each review.
• Re-quote a held reading as soon as two sources agree on the quantity carried, even if
  they disagree on a detail; record the detail as a dispute.
• A reason, a move or a date written beside a figure must belong to that figure's session.
• For a fund or target fund, the manager's own document (factsheet, KIID, prospectus)
  is the primary source; confirm it with a second (ATRAM's disclosure, uitf.com.ph or a
  fund database).
• If a held figure reaches its freshness limit, flag it and propose a fix, and list
  anything within two days of its limit. Never let a check fail quietly.
• If a site is blocked, name it and list what it left unverified. Don't fill gaps from memory.
• Cite sources as links in the report.

1. Market data and events (Macro, Volatility and Report tabs)
• Roll each market to its newest completed session: the S&P 500, Nasdaq and Dow; PSEi;
  KOSPI; Nikkei; the peso; Brent and WTI settles (front contract; watch expiries, rolls and
  the year-ago base); the VIX; the 2-, 10- and 30-year Treasury closes; FedWatch's odds for
  the next Fed meeting; the PH T-bill auction. Say which sessions were updated and which
  were held, and why.
• Add the economic releases and central-bank decisions since the last review (US, PH,
  euro area, Japan, Korea, China), including any released while you work; the valuation and
  earnings inputs (FactSet's weekly forward P/E and earnings season, the Nasdaq-100 and Asia
  forward P/E); a new IMF outlook when one is out; and the Gulf: Hormuz flows and transits
  (PortWatch, weekly), attacks, talks.
• Refresh the VIX futures curve if it is old, its front contract is near settlement, or the
  VIX has moved past the overtaken flag, and re-test it against VIX3M. Refresh anything else
  close to its freshness limit, or say why it's held.
• Update the event calendar: retire events that have passed or been released, add the
  next ones, each date confirmed by two sources.

2. The 22 ATRAM funds and their target funds (Funds tab)
• Every review: search ATRAM's notices and the target managers' notices for a fee change,
  merger, closure, manager change, target switch, share-class or mandate change, or new fund.
• Full check on the first review of each week, or whenever a notice turns up:
  ◦ ATRAM level: each fund's trust fee, read from ATRAM's own fund page.
  ◦ Target level: each feeder's target fund, share class and currency; the target's own
    charge for that class, its mandate and benchmark, and its top-10 holdings with as-of
    dates (the Look-through and Stock level sections; 60-day limit).
  ◦ Compare each feeder's 1-year peso return with its target's; a gap well beyond the
    fee stack means a fee or a target is wrong. If either return can't be found, record
    the test as not run.
• Check the long-run return assumptions each forecast starts from (the J.P. Morgan
  edition in use), that each matches its target's asset class and region, and that the
  peso translation stays inside its PPP bracket. Check the Side by side and Fee
  transparency tables against the slides.
• For each held-out fund, say what still blocks it, including any target fund not yet
  named. Re-run the held-out what-if for A, B and D and record its weights.

3. The four analyses at 3, 5 and 10 years (Macro and Volatility tabs)
• Macro drivers (seven scores now, their 3- and 5-year paths, neutral at 10), regional
  rankings (US, Europe, Asia, Philippines), market trend and volatility. Keep each score
  unless the evidence moves it, measured against the last published scores. When one
  moves, give the evidence and its effect on the headline gauge and on each fund's and
  portfolio's net 10-year CAGR and drawdown (say so when it moves only the gauge).
• Roll the trend window when a quarter closes and its returns are published. Check that
  the correlations (Correlated sentiment), the driver-to-fund tilts, each fund's volatility
  beta and drawdown coefficient, and the curve's tilt on each fund still follow from
  their inputs.
• Re-check a modelled assumption (the VIX long run, the variance risk premium, the
  drawdown calibration, peso volatility) only when its source updates; say if none did.

4. Drawdown budget band (Budget tab)
• Recompute the gauge: macro drivers + market trend at 3 and 5 years, weighted 60/40;
  the 10-year view is neutral by construction and shown as the anchor. Check its guards
  (two month-end reviews in the same band; geopolitics above 2.0 and the VIX at or
  under its long run before any raise). Record the month-end review when one is due.
• Report the budget in force and what each step (24% to 27%) does to A, B and D, and to
  B in a Hormuz closure.

5. Portfolios A, B and D (Portfolios tab)
• Re-run the selection under the current rules: the highest net CAGR after all fees
  inside the drawdown budget, a shallower drawdown breaking only exact ties.
  ◦ A and B: at most 5 funds, 35% in any one, at least 5% peso money market, 5% steps;
    A on the 10-year view, B on the 3/5/10-year view.
  ◦ D: Nasdaq Equity Income strictly the largest of two to five funds, each at least 5%,
    5% steps, no single-fund cap and no cash floor, on the 3/5/10-year view; the rule
    picks the number of funds, and each count's best is shown.
• Check the head-to-head tables, the lenses and "who wins where"; the stress scenarios
  against today's markets (for example the oil levels in the Hormuz escalation and
  disinflation restart rows); and re-run the what-ifs, the efficient-mix chart and the
  peso table.
• Ask me before changing any rule: the 25% base, the band and its guards, the limits,
  D's rule, the selection rule, the 3/5/10-year weights or the fund list.

6. Report tab
• Read the rationale report, the conclusion and the what-ifs against the other tabs, and
  the "Not in these numbers yet" calendar. Every source is a working https link, none is
  listed twice, and every dispute names its sources.

7. Error hunt (throughout)
• Debug, code-review and sanity-check the engine, the page, the audit, the held-out
  script and the docs. Look hardest at anything this update crosses: oil contract rolls,
  month- and quarter-ends, holidays, event dates, freshness limits, target-fund switches
  and share-class mismatches, inputs that roll by date, and sentences that quote a move,
  a reason or a date beside a figure.
• Confirm each check recalculates what it claims to; a check that only compares the
  page with itself proves nothing.
• Record each error in the changelog, then fix it.

8. Verify, clean up, publish
• All must pass: the engine checks, the independent audit, the phone-width page check
  and the planted-error (mutation) test, re-run after any later code change. Then open all
  six tabs and read them as a user would: wording, dates, and figures that contradict
  each other.
• House cleanup: retire inputs nothing reads, remove dead code and temp files, and make
  any hand-typed figure or date read its input.
• Commit and push, then publish to the same dashboard link and check the live copy.
  Update the changelog, the claims register (with a row for each target fund), the README
  and the runbook.

9. Report back, briefly
• Start with three lines: what changed for A, B and D; the budget in force; and what
  moved for Nasdaq Equity Income, the fund I hold.
• A table of A, B and D (weights, net CAGR, drawdown) with what changed and why, and D's
  number of funds, plus the drawdown band's reading and guards.
• Any target-fund change found (switch, share class, charge, merger, closure) and its
  effect on the fund's net CAGR.
• Blocked sources, what was held and why, disputes opened or settled, errors found and
  fixed, anything within two days of its limit, and what's due before the next review.
• Mark it "not personal financial advice."
```
