# The review command

The owner's standing instruction for every review, kept here so a session can be told
"Run the ATRAM review in monitoring/REVIEW_COMMAND.md" and every change to it is versioned.
Updated 2026-11-12 (after v101): Portfolio C retired, so the command covers A, B and D; the
Report tab has its own step; periodic items, contract rolls and the runbook's evidence lessons
are named. Updated 2026-11-15 (v103): the Budget tab reads 1, 3, 5 and 10 years. Updated 2026-11-16 (v105):
the budget band runs 20% to 30%. Updated 2026-11-16 (v107): the Volatility tab is removed (its drawdown
model is on the Portfolios tab); the four analyses are the regional ranking, macro sentiment, market trend
and market valuation, A on 10 years and B and D on 1, 3, 5 and 10; the gauge reads 1, 3 and 5 years.
Updated 2026-11-16 (v108): every analysis, the regional rankings included, has a researched year-1 reading.
Updated 2026-11-16 (v109): the band holds at 25% from 2.80 to 3.20 and steps one point per 0.15.
Updated 2026-11-17 (v110): five tabs, not six. Updated 2026-11-17 (v111): Portfolio C is back as the owner's
three funds, so the command covers A, B, C and D. Updated 2026-11-17 (v112): the gauge reads months 1-6
and 7-12, years 2-3 and 4-5 (10/10/40/40), with the 10-year view as its unweighted anchor. Updated 2026-11-22 (v122): the
drivers and the regional rankings are scored on 1-5 (v119-v120), so the geopolitics guard's floor is 1.44; news after the
cut-off, near-tie picks and the calendar's US clock have their own rules; every section on the five tabs is named, with
the step that covers it (the map after the command), and the page check confirms every section renders. Updated
2026-11-23 (v125): Portfolio C is the dividend-income portfolio; the weekly fund check re-confirms each income fund's
payout schedule. Updated 2026-11-23 (v126): every portfolio shows its trailing-12-month payout, estimated
from the target funds' yields. Updated 2026-11-23 (v129): beside it, each portfolio's payout the year before (v127's 1-year return retired). Updated 2026-11-23 (v128): every tab
leads with figures and takeaways; long notes fold under "More". The runbook
(`README.md`) says how; this file says what.

```text
ATRAM review: bring the dashboard up to today, check every number on every tab, fix
what's wrong, clean up, and publish it to https://claude.ai/artifact/6z2thyg2HaHjFtcbjKhnUY
(code: f1fad-hue/ClaudeAtram, branch claude/android-portfolio-macro-dashboard-awmpce).
The portfolios are A, B, C and D (C, from 23 Nov 2026, is my dividend-income portfolio: two to five
of the ATRAM funds that pay income, with Peso Money Market as a cash buffer). I hold Nasdaq Equity Income.

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

1. Market data and events (Macro and Report tabs)
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
  next ones - at least everything due before the next Fed, BSP, ECB and BoJ decisions (jobs, CPI and
  PCE prints, OPEC+ meetings, Philippine inflation) - each date confirmed by two sources. A US release
  or the Fed is past once a US session on or after its date is carried; everything else, once the data
  date reaches it (one rule, shared by the engine and the audit).
• News after the cut-off (a weekend, or while you work) goes in its note marked as after the close and
  in no price yet. A score moves on it only if the evidence is decisive; otherwise the note says what
  would move it, in words, not a typed score.

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
  ◦ Portfolio C's income funds (v125): re-confirm that each still pays income and how
    often (ATRAM's distribution notices, a broker's income-paying list), two sources for
    "pays"; a fund that stops paying leaves C's set, and an admitted fund that starts paying
    joins it - both are the owner's call, so ask.
  ◦ Payouts (v126): re-read each paying fund's trailing-12-month yield (its target fund's,
    until ATRAM's own distribution tables can be read; two sources, one decimal) and
    check that the funds on no income-paying list still pay nothing. Every portfolio's
    income on the Portfolios tab is derived from these.
  ◦ The year before (v129): each payer's payout yield for the prior full year (2025 until
    the 2026 figures publish), read the same way as this year's; replace any ASSUMED rate
    (Asian Multi-Asset Income's) as soon as its record is found.
• Check the long-run return assumptions each forecast starts from (the J.P. Morgan
  edition in use), that each matches its target's asset class and region, and that the
  peso translation stays inside its PPP bracket. Check the Side by side and Fee
  transparency tables against the slides.
• For each held-out fund, say what still blocks it, including any target fund not yet
  named. Re-run the held-out what-if for A, B and D and record its weights (C holds only its five named funds;
  a held-out income fund joins it only once admitted).

3. The four analyses at 1, 3, 5 and 10 years (Macro, Funds and Portfolios tabs)
• Every score is on 1-5, 3 neutral (the drivers from v119, the regions from v120); moves are
  judged on that scale, and no 1-10 figure is published.
• Regional rankings (US, Europe, Asia, Philippines; each with a researched year-1 reading
  from v108, years 2-3 implied), macro sentiment (seven driver scores
  now, their year-1, 3- and 5-year paths, neutral at 10), market trend and market valuation
  (the valuation driver's path; it tilts years 1-5 only, weighted 10/20/20 of the ten years, and
  is neutral at 10, where the long-run base prices it). Volatility tilts no forecast: it sets each
  fund's volatility and expected drawdown, and the VIX guards a raise. Keep each score
  unless the evidence moves it, measured against the last published scores. When one
  moves, give the evidence and its effect on the headline gauge and on each fund's and
  portfolio's net 10-year CAGR and drawdown (say so when it moves only the gauge).
• Roll the trend window when a quarter closes and its returns are published. Check that
  the correlations (Correlated sentiment), the driver-to-fund tilts, each fund's volatility
  beta and drawdown coefficient (Portfolios tab, "How each drawdown is estimated"), and the
  valuation tilt on each fund still follow from their inputs, and that the Portfolios tab's
  "four analyses, year by year" table matches the blends the forecasts use.
• Re-check a modelled assumption (the VIX long run, the variance risk premium, the
  drawdown calibration, peso volatility) only when its source updates; say if none did.

4. Drawdown budget band (Budget tab)
• Recompute the gauge: macro drivers (without valuation) + market trend + market valuation
  over months 1-6, months 7-12, years 2-3 and years 4-5, weighted 10/10/40/40 (owner, 17 Nov
  2026: 6 months, 1, 3, 5 and 10 years); years 6-10 are shown as the anchor and not weighted
  (neutral by construction, what the 25% base stands for). Re-read the valuation evidence (forward P/E for the
  S&P, Nasdaq-100, Asia and Europe; the CAPE; ten-year return forecasts).
  Re-research each driver's year-1 reading (the year-ahead forecasts: Fed and SOFR futures,
  the Philadelphia Fed survey, FOMC projections, the EIA's STEO, the IMF, 2027 earnings)
  and its six-month reading (the half-year ahead: FedWatch's next meetings, BSP's next
  decision, the latest inflation prints, the STEO's quarterly path, the VIX curve, forward
  multiples), and say which moved; months 7-12 are implied. Check its guards
  (two month-end reviews in the same band; geopolitics above its 1.44 floor and the VIX at or
  under its long run before any raise). Record the month-end review when one is due.
• Report the budget in force and what each step (20% to 30%, one point a step; owner,
  16 Nov 2026; hold 2.80-3.20 and 0.15 of the reading a step, v109) does to A, B, C and D, and to B in a Hormuz closure. The band's budget is every
  portfolio's budget (owner, 16 Nov 2026: "All portfolio still use the budget drawdown band").

5. Portfolios A, B, C and D (Portfolios tab)
• Re-run the selection under the current rules: the highest net CAGR after all fees
  inside the drawdown budget, a shallower drawdown breaking only exact ties.
  ◦ A and B: at most 5 funds, 35% in any one, at least 5% peso money market, 5% steps;
    A on the 10-year view, B on the 1/3/5/10-year view.
  ◦ D: Nasdaq Equity Income strictly the largest of two to five funds, each at least 5%,
    5% steps, no single-fund cap and no cash floor, on the 1/3/5/10-year view; the rule
    picks the number of funds, and each count's best is shown.
  ◦ C: exactly Peso Money Market, Nasdaq Equity Income (strictly the largest) and Global
    Technology, each at least 5%, 5% steps, no single-fund cap, on the 1/3/5/10-year view;
    each Nasdaq weight's best is shown.
• Flag any pick that sits in a near-tie - more than one mix printing the best CAGR, or a runner-up
  within 0.01pp - say what would flip it, and say plainly when a change of mix is a tie-break, not a
  view (D, 21 Nov 2026: three mixes tied at 7.19%).
• Check the head-to-head tables, the lenses and "who wins where"; the stress scenarios
  against today's markets (for example the oil levels in the Hormuz escalation and
  disinflation restart rows); and re-run the what-ifs, the efficient-mix chart and the
  peso table.
• Ask me before changing any rule: the 25% base, the band and its guards, the limits,
  D's rule, the selection rule, the 1/3/5/10-year weights (10/20/20/50 by years covered), the
  valuation tilt's years 1-5 only, the band's 2.80-3.20 hold and 0.15 steps, the budget gauge's spans
  (months 1-6 and 7-12, years 2-3 and 4-5) and their 10/10/40/40 weights, the 1-5 scales, or the fund list.

6. Report tab
• Read the rationale report, the conclusion and the what-ifs against the other tabs; the
  setup's live figures (the Fed's range, the odds, the 10-year, Brent, BSP, the ECB, the BoJ,
  the IMF, Asia's earnings and multiple, the gauge, geopolitics and volatility) against the
  Macro tab; the "Not in these numbers yet" calendar; "Method & limits" (fee estimates,
  correlations, the footer's data and review dates). Every source is a working https link,
  none is listed twice, and every dispute names its sources.

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
  (every section on every tab renders, nothing left empty, no page-wide horizontal scroll)
  and the planted-error (mutation) test, re-run after any later code change. Then open all
  five tabs and read them as a user would: wording, dates, and figures that contradict
  each other.
• House cleanup: retire inputs nothing reads, remove dead code and temp files, and make
  any hand-typed figure or date read its input.
• Keep it concise (v128): each section leads with its figures and a one-line takeaway; the
  rest folds under "More" (the page does this to any paragraph over 60 words, and the page
  check fails one that shows more than 90). Write a new note so its first sentence is the
  point.
• Commit and push, then publish to the same dashboard link and check the live copy.
  Update the changelog, the claims register (with a row for each target fund), the README
  and the runbook.

9. Report back, briefly
• Start with three lines: what changed for A, B, C and D; the budget in force; and what
  moved for Nasdaq Equity Income, the fund I hold.
• A table of A, B, C and D (weights, net CAGR, drawdown) with what changed and why, and D's
  number of funds, plus the drawdown band's reading and guards.
• Any target-fund change found (switch, share class, charge, merger, closure) and its
  effect on the fund's net CAGR.
• Blocked sources, what was held and why, disputes opened or settled, errors found and
  fixed, anything within two days of its limit, and what's due before the next review.
• Mark it "not personal financial advice."
```

## Every section, and the step that covers it (v122)

Five tabs, thirty sections. A review that skips a row has not covered the page.

| Tab | Section | Step |
|---|---|---|
| Macro | Overall driver gauge (the headline and its verdict) | 3 |
| Macro | Driver breakdown (seven scores, notes, summaries) | 1, 3 |
| Macro | Drivers now / 3Y / 5Y / 10Y (paths, ten-year averages, the gauge at each) | 3 |
| Macro | Regional ranking 1Y / 2-3Y / 4-5Y / 6-10Y | 3 |
| Macro | Market trend 1Y / 3Y / 5Y / 10Y (quarters, z-scores, reversal) | 3 |
| Macro | Correlated sentiment (the correlation matrix and how each driver lands) | 3 |
| Funds | Fund slides (the eleven funds' jobs) | 2 |
| Funds | Side by side | 2 |
| Funds | Fee transparency (feeder and target layers) | 2 |
| Funds | Look-through (regions and sectors underneath) | 2 |
| Funds | Stock level (top holdings, dated, 60-day limit) | 2 |
| Portfolios | A vs B vs C vs D, and the four analyses year by year | 3, 5 |
| Portfolios | Portfolio C (what each fund pays and its sources; each count's best) | 4, 5 |
| Portfolios | Portfolio D (each count's best, the number of funds) | 5 |
| Portfolios | Headline forecast, lenses, who wins where | 5 |
| Portfolios | Income paid, the last 12 months against the year before (each portfolio, fund by fund) | 4, 5 |
| Portfolios | Feasible set (the frontier, the best pure ratio, the extremes) | 5 |
| Portfolios | Stress test | 5 |
| Portfolios | In pesos (P1,000,000 over ten years) | 5 |
| Portfolios | How each drawdown is estimated (volatility term structure, betas, k, the cash floor) | 3, 5 |
| Budget | The reading and the budget in force | 4 |
| Budget | What each view says (6M, 7-12M, 2-3Y, 4-5Y, the 10Y anchor) | 4 |
| Budget | The research by span (drivers, valuation, trend) | 4 |
| Budget | The bands and the guards | 4 |
| Budget | What each step buys (A to D at 20% to 30%) | 4 |
| Budget | Why (the rule and its history) | 4 |
| Report | Rationale report | 6 |
| Report | The setup, volatility, where the weight goes, Global Technology, cash, C | 6 |
| Report | Keeping this current (the calendar, anything postponed) | 1, 6 |
| Report | Sources | 6 |
| Report | Method & limits | 6 |
