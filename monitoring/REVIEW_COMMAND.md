# The review command

The owner's standing instruction for every review, kept here so a session can be told
"Run the ATRAM review in monitoring/REVIEW_COMMAND.md" and every change to it is versioned.
The runbook (`monitoring/README.md`) says how; this file says what.

**Rewritten 2026-11-24 (v132)** at the owner's request ("Update this command prompt to cover everything
in programming, pages and tabs"). It now covers:
- the code: each file, the commands that check it, and a code-review checklist (step 9);
- the dividend payouts (step 3);
- C's current rules: the income funds, no main fund, and at most 110 less the owner's age in stocks;
- all five tabs and their thirty sections, each mapped to its step.

Earlier changes (v101-v131: C retired, restored, then re-set as the income portfolio; the 1-5 scales;
the band and its spans; the payout rows; the concise fold) are in `monitoring/CHANGELOG.md`.

```text
ATRAM review: bring the dashboard up to today, check every number on every tab and the
code that makes it, fix what's wrong, clean up, keep it concise, and publish it to
https://claude.ai/artifact/6z2thyg2HaHjFtcbjKhnUY
(code: f1fad-hue/ClaudeAtram, branch claude/android-portfolio-macro-dashboard-awmpce).
The portfolios are A, B, C and D. C is my dividend-income portfolio. I hold Nasdaq Equity Income.

Before you start
• Read the runbook (monitoring/README.md) and the newest changelog entry, and carry
  forward its "due before the next review" list.
• Test the primary sources and name any that are blocked:
  ◦ the exchanges: Cboe, CME FedWatch, ICE, PSE, KRX, JPX;
  ◦ the agencies: the US Treasury, the Fed, BLS, FRED, IMF PortWatch, the Bureau of the
    Treasury, PSA, BSP;
  ◦ uitf.com.ph, atram.com.ph and the target managers' sites.
• State the cut-off time (UTC) and any market holiday. Say which sessions had closed by
  then: New York, Manila, Tokyo, Seoul, the Brent and WTI settles, Treasuries. If the work
  pauses, move the cut-off forward at most twice, then publish with the gaps named.
• Say which periodic items fall due:
  ◦ the weekly full fund check, on the first review of each week;
  ◦ a month-end band review;
  ◦ a quarter-end trend roll;
  ◦ any contract roll or expiry (WTI, Brent, VIX futures);
  ◦ C's age cap, which steps down one point on my birthday (30 Dec).

Evidence rules (apply to everything below)
• Use a figure only if two independent sources agree and it adds up with the previous one
  (prior close + reported move = new close). Syndicated copies of one wire story, and
  rewrites of it, count as one source. Record any outlier as a dispute.
• If no two independent sources agree, or only one exists, keep the last confirmed figure
  and record the dispute. Never pick one of the conflicting figures.
  ◦ A dispute is settled only when the primary source (the exchange, agency or manager)
    and one independent source agree.
  ◦ Re-try every open dispute and withheld session at each review.
• Re-quote a held reading as soon as two sources agree on the quantity carried, even if
  they disagree on a detail; record the detail as a dispute.
• A reason, a move or a date written beside a figure must belong to that figure's session.
• For a fund or target fund, the manager's own document (factsheet, KIID, prospectus) is
  the primary source. Confirm it with a second: ATRAM's disclosure, uitf.com.ph or a fund
  database.
• If a held figure reaches its freshness limit, flag it and propose a fix. List anything
  within two days of its limit. Never let a check fail quietly.
• If a site is blocked, name it and list what it left unverified. Don't fill gaps from memory.
• Cite sources as links in the report.

1. Market data and events (Macro and Report tabs)
• Roll each market to its newest completed session:
  ◦ the S&P 500, Nasdaq and Dow;
  ◦ the PSEi, KOSPI and Nikkei;
  ◦ the peso;
  ◦ the Brent and WTI settles: the front contract; watch expiries, rolls and the year-ago base;
  ◦ the VIX;
  ◦ the 2-, 10- and 30-year Treasury closes;
  ◦ FedWatch's odds for the next Fed meeting;
  ◦ the PH T-bill auction.
  Say which sessions were updated and which were held, and why.
• Add the economic releases and central-bank decisions since the last review, including any
  released while you work: US, PH, euro area, Japan, Korea, China.
• Add the valuation and earnings inputs: FactSet's weekly forward P/E and earnings season,
  and the Nasdaq-100 and Asia forward P/E.
• Add a new IMF outlook when one is out.
• Add the Gulf: Hormuz flows and transits (PortWatch, weekly), attacks and talks.
• Refresh the VIX futures curve if any of these hold: it is old, its front contract is near
  settlement, or the VIX has moved past the overtaken flag. Re-test it against VIX3M.
• Refresh anything else close to its freshness limit, or say why it's held.
• Update the event calendar:
  ◦ Retire events that have passed or been released.
  ◦ Add the next ones: at least everything due before the next Fed, BSP, ECB and BoJ
    decisions (jobs, CPI and PCE prints, OPEC+ meetings, Philippine inflation). Confirm
    each date with two sources.
  ◦ A US release or the Fed is past once a US session on or after its date is carried.
    Everything else is past once the data date reaches it. The engine and the audit share
    this rule.
• News after the cut-off (a weekend, or while you work) goes in its note, marked as after the
  close and in no price yet.
  ◦ A score moves on it only if the evidence is decisive.
  ◦ Otherwise the note says, in words, what would move it, not a typed score.
• Words that depend on a level must follow the data: "in correction", "a record",
  "overtaken", "the lowest since". Rewrite any relative date ("Friday", "the week's fall")
  that a roll has made ambiguous.

2. The 22 ATRAM funds and their target funds (Funds tab)
• Every review: search ATRAM's notices and the target managers' notices for any of these:
  a fee change, merger, closure, manager change, target switch, share-class or mandate
  change, or new fund.
• Full check on the first review of each week, or whenever a notice turns up:
  ◦ ATRAM level: each fund's trust fee, read from ATRAM's own fund page.
  ◦ Target level, for each feeder:
    - its target fund, share class and currency;
    - the target's own charge for that class, its mandate and its benchmark;
    - its top-10 holdings with as-of dates (the Look-through and Stock level sections;
      60-day limit).
  ◦ Compare each feeder's 1-year peso return with its target's. A gap well beyond the fee
    stack means a fee or a target is wrong. If either return can't be found, record the
    test as not run.
• Each fund's net 10-year CAGR and drawdown must follow from its inputs:
  ◦ the long-run return assumption (the J.P. Morgan edition in use), matched to the target's
    asset class and region;
  ◦ the fee stack (ATRAM's trust fee plus the target's charge);
  ◦ the four analyses' tilts;
  ◦ the volatility model.
  The peso translation must stay inside its PPP bracket. Check the Side by side and Fee
  transparency tables against the slides.
• For each held-out fund, say what still blocks it, including any target fund not yet
  named. Re-run model/heldout_sens.py for A, B and D and record its weights. C holds only
  its five named funds; a held-out income fund joins it only once admitted.

3. Dividend payouts (Portfolios tab: C's "What each fund pays", the payout card, the
   headline rows)
• The payers are:
  ◦ monthly: Nasdaq Equity Income;
  ◦ quarterly: Asia Equity, Global Dividend and Asian Multi-Asset Income.
  Every other fund pays nothing out, and the money market's interest stays in its unit price.
• In the weekly check, re-confirm each payer still pays and how often: ATRAM's distribution
  notices and a broker's income-paying list, two sources for "pays".
  ◦ A fund that stops paying leaves C's set.
  ◦ An admitted fund that starts paying joins it.
  Both are my call, so ask.
• Read each payer's rates. Until ATRAM's own distribution tables can be read, each rate is
  its target fund's, from two sources, to one decimal.
  ◦ Last 12 months: its trailing-12-month yield. Check that the funds on no income-paying
    list still pay nothing.
  ◦ The year before: its payout yield for the last full year (2025 until the 2026 figures
    publish), read the same way. Replace an ASSUMED rate (Asian Multi-Asset Income's 2025)
    as soon as its record is found.
  ◦ Next 12 months: its latest payout rate, annualised; the manager's notice first, a data
    site second. This is a forecast, not a promise: a covered-call fund's income moves with
    volatility, and a set rate can be cut.
• Recompute every portfolio's payout by hand for at least one portfolio, and check:
  ◦ the yield is the sum of weight × rate;
  ◦ the pesos on ₱1,000,000, and the same net of ATRAM's trust fee;
  ◦ the monthly and quarterly payments;
  ◦ the share held in funds that pay nothing, and the share resting on an assumed rate;
  ◦ the versus table (next 12 months against the last 12) and the 2025 row.
• A payout is inside each fund's net CAGR, never added to it. Say so wherever a payout is
  shown.
• Re-date the payout record only when its rates are re-read.

4. The four analyses at 6 months and 1, 3, 5 and 10 years (Macro, Budget and Portfolios tabs)
• Every score is on 1-5, with 3 neutral: the drivers from v119, the regions from v120.
  Moves are judged on that scale, and no 1-10 figure is published.
• The four analyses:
  ◦ Regional rankings: US, Europe, Asia and the Philippines, each with a researched year-1
    reading; years 2-3 are implied.
  ◦ Macro sentiment: seven driver scores now, plus their year-1, 3-year and 5-year paths;
    neutral at 10 years.
  ◦ Market trend: the quarters, z-scores and reversal.
  ◦ Market valuation: the valuation driver's path. It tilts years 1-5 only, weighted
    10/20/20 of the ten years, and is neutral at 10, where the long-run base prices it.
• Volatility tilts no forecast. It sets each fund's volatility and expected drawdown, and
  the VIX guards a raise.
• Keep each score unless the evidence moves it, measured against the last published scores.
  When one moves, give the evidence and its effect on:
  ◦ the headline gauge;
  ◦ each fund's and each portfolio's net 10-year CAGR and drawdown.
  Say so when it moves only the gauge.
• Roll the trend window when a quarter closes and its returns are published.
• Check that each of these still follows from its inputs:
  ◦ the correlations (Correlated sentiment);
  ◦ the driver-to-fund tilts;
  ◦ each fund's volatility beta and drawdown coefficient ("How each drawdown is estimated");
  ◦ each fund's valuation tilt.
  Check that "the four analyses, year by year" table matches the blends the forecasts use.
• Re-check a modelled assumption only when its source updates, and say if none did: the
  VIX long run, the variance risk premium, the drawdown calibration, peso volatility.

5. The drawdown budget band at 6 months, 1, 3, 5 and 10 years (Budget tab)
• Recompute the gauge from three inputs: the macro drivers (without valuation), market trend
  and market valuation.
  ◦ Spans and weights: months 1-6, months 7-12, years 2-3 and years 4-5, weighted
    10/10/40/40.
  ◦ Years 6-10 are shown as the anchor and not weighted: neutral by construction, what the
    25% base stands for.
• Re-read the valuation evidence: the forward P/E for the S&P, Nasdaq-100, Asia and Europe;
  the CAPE; ten-year return forecasts.
• Re-research each driver's readings and say which moved. Months 7-12 are implied.
  ◦ Year 1, the year ahead: Fed and SOFR futures, the Philadelphia Fed survey, FOMC
    projections, the EIA's STEO, the IMF, 2027 earnings.
  ◦ Six months, the half-year ahead: FedWatch's next meetings, BSP's next decision, the
    latest inflation prints, the STEO's quarterly path, the VIX curve, forward multiples.
  Re-date each span's reading date when you re-read it, even if nothing moved.
• Check the guards before any raise:
  ◦ two month-end reviews in the same band;
  ◦ geopolitics above its 1.44 floor;
  ◦ the VIX at or under its long run.
  Record the month-end review when one is due.
• Report the budget in force. The band runs from 20% to 30%, one point a step; it holds at
  25% from 2.80 to 3.20 and moves one step per 0.15 of the reading.
• Report what each step does to A, B, C and D, and to B in a Hormuz closure. The band's
  budget is every portfolio's budget.

6. Portfolios A, B, C and D (Portfolios tab)
• Re-run the selection under the current rules: the highest net CAGR after all fees inside
  the drawdown budget. A shallower drawdown breaks only exact ties.
  ◦ A and B: at most 5 funds, at most 35% in any one, at least 5% in the peso money market,
    5% steps. A is chosen on the 10-year view; B on the 1/3/5/10-year view, weighted
    10/20/20/50.
  ◦ C: two to five of its five funds, on the 1/3/5/10-year view:
    - Peso Money Market (a cash buffer, not required), Nasdaq Equity Income, Asia Equity,
      Global Dividend and Asian Multi-Asset Income;
    - each at least 5%, in 5% steps;
    - no main fund and no single-fund cap;
    - at most (110 − my age)% in stocks. The age is taken on the review date. Asian
      Multi-Asset Income counts as half stocks and the money market as none.
    The rule picks the number of funds, and each count's best is shown. Report C's stock
    share against its cap, and say when the cap rather than the budget binds.
  ◦ D: Nasdaq Equity Income strictly the largest of two to five funds, on the 1/3/5/10-year
    view:
    - each at least 5%, in 5% steps;
    - no single-fund cap and no cash floor.
    The rule picks the number of funds, and each count's best is shown.
• Flag any pick in a near-tie: more than one mix printing the best CAGR, or a runner-up
  within 0.01pp. Say what would flip it, and say plainly when a change of mix is a tie-break,
  not a view.
• Check and re-run:
  ◦ the head-to-head tables, the lenses and "who wins where";
  ◦ the stress scenarios against today's markets (for example the oil levels in the Hormuz
    escalation and disinflation-restart rows);
  ◦ the what-ifs, the feasible set and frontier, and the peso table;
  ◦ the number of mixes searched and the number inside the budget.
• Ask me before changing any rule or assumption:
  ◦ the 25% base, the band, its 2.80-3.20 hold, its 0.15 steps and its guards;
  ◦ the budget gauge's spans (months 1-6 and 7-12, years 2-3 and 4-5) and their
    10/10/40/40 weights;
  ◦ the selection rule, the limits, D's rule and the fund list;
  ◦ C's fund set, its 110 − age rule and how a fund's stock share is counted;
  ◦ the 1/3/5/10-year weights, and the valuation tilt applying to years 1-5 only;
  ◦ the 1-5 scales;
  ◦ the payout basis: target-fund yields, the year-before and next-12-month readings, any
    assumed rate, and the net-of-trust-fee line.

7. Report tab
• Read the rationale report, the conclusion and the what-ifs against the other tabs.
• Check the setup's live figures against the Macro tab: the Fed's range, the odds, the
  10-year, Brent, BSP, the ECB, the BoJ, the IMF, Asia's earnings and multiple, the gauge,
  geopolitics and volatility.
• Check the "Not in these numbers yet" calendar, and "Method & limits": fee estimates,
  correlations, and the footer's data and review dates.
• Every source is a working https link and none is listed twice. Every dispute names its
  sources.

8. Error hunt (throughout)
• Debug, code-review and sanity-check the engine, the page, the audit, the held-out script
  and the docs.
• Look hardest at anything this update crosses:
  ◦ oil contract rolls, month- and quarter-ends, holidays, event dates, freshness limits;
  ◦ target-fund switches and share-class mismatches;
  ◦ inputs that roll by date;
  ◦ sentences that quote a move, a reason or a date beside a figure;
  ◦ birthdays (C's cap).
• Confirm each check recalculates what it claims to. A check that only compares the page
  with itself proves nothing.
• Record each error in the changelog, then fix it.

9. The code (programming)
• Files, and what each does:
  ◦ model/engine.py: every input (markets, funds, payouts, the owner's birth date as
    OWNER_BIRTH); the scores, the forecasts, the searches for A-D and the payload; its own
    checks. `python3 model/engine.py` runs the checks; `--json` prints the payload.
  ◦ model/heldout_sens.py: the held-out and disputed-fee re-runs (about 70 s). It self-checks
    the figures it has recorded; re-date heldout_run_date when it is re-run.
  ◦ monitoring/harness/rebuild.sh: writes model/data.json and embeds it in dashboard.html.
  ◦ monitoring/harness/audit.py: an independent re-implementation. From the inputs and the
    payload it re-derives the picks, the payouts, the budget, the dates, the register and
    the text rules.
  ◦ monitoring/harness/validate.js: renders the page at phone width with Playwright. It
    checks that every section is filled, nothing overflows, and no paragraph over 90 words
    shows; `--live` checks the published copy.
  ◦ monitoring/harness/mutate.py: plants errors (mutants) in the engine and the page. Every
    one must be caught (`-j 4`, about 15 minutes).
  ◦ dashboard.html: the page. Its script renders the payload; the concise fold runs last.
• Code-review checklist:
  ◦ Every input is read by name, and every number in a note traces to an input. No figure
    or date is typed by hand where an input exists, and inputs nothing reads are retired.
  ◦ Date-keyed notes gain an entry for each new date, and retired dates and keys are removed.
    These are the US, Asia and PH reasons and summaries, the peso, the PSEi and the VIX.
  ◦ Rolling series (Brent, the VIX) append; they never overwrite. Across a WTI roll the
    prior is implied by the move.
  ◦ Shared rules are written once in the engine and again, independently, in the audit: the
    event "past" rule, half-up rounding, the selection rule, the age cap, the payout sums.
  ◦ Printed figures round half-up. A difference is taken from the printed values, so the
    page adds up.
  ◦ Conditional wording follows its data: "in correction" only at 10% or more below the
    record; "OVERTAKEN" with its flag; the cap's next step on the next birthday.
  ◦ The page shows no "undefined", "NaN" or empty cell, and no duplicate id. The fold keeps
    the first sentence and leaves tables whole. Light and dark both read.
  ◦ Privacy: the owner's birth date stays in engine.py. No personal detail goes in the page,
    the payload or a commit. Secret-scan the staged diff.

10. Verify, clean up, publish
• Run in this order, and all must pass:
  ◦ `python3 model/engine.py`;
  ◦ `sh monitoring/harness/rebuild.sh`;
  ◦ `python3 monitoring/harness/audit.py`;
  ◦ `node monitoring/harness/validate.js $PWD/dashboard.html`;
  ◦ `python3 monitoring/harness/mutate.py -j 4`, re-run after any later code change.
• Then open all five tabs and read them as a user would, looking for wording, dates and
  figures that contradict each other.
• House cleanup: retire inputs nothing reads; remove dead code and temp files; make any
  hand-typed figure or date read its input.
• Keep it concise. Each section leads with its figures and a one-line takeaway, and the rest
  folds under "More". The page folds any paragraph over 60 words, and the page check fails
  one that shows more than 90. Write a new note so its first sentence is the point.
• Commit and push, then publish to the same dashboard link and check the live copy
  (`validate.js --live`, and the embedded payload matches model/data.json).
• Update the changelog, the claims register (with a row for each target fund), the README
  and the runbook.

11. Report back, briefly
• Start with three lines:
  ◦ what changed for A, B, C and D;
  ◦ the budget in force;
  ◦ what moved for Nasdaq Equity Income, the fund I hold.
• A table of A, B, C and D: weights, net CAGR and drawdown, what changed and why. Add C's
  and D's number of funds, C's stock share against its age cap, and the drawdown band's
  reading and guards.
• Each portfolio's payout: the last 12 months against the next 12, with the share resting
  on an assumed rate.
• Any target-fund change found (switch, share class, charge, merger, closure) and its effect
  on the fund's net CAGR.
• Then list:
  ◦ blocked sources;
  ◦ what was held, and why;
  ◦ disputes opened or settled;
  ◦ errors found and fixed;
  ◦ anything within two days of its limit;
  ◦ what's due before the next review.
• Mark it "not personal financial advice."
```

## Every section, and the step that covers it (v132)

Five tabs, thirty sections. A review that skips a row has not covered the page; the page check confirms each
renders.

| Tab | Section | Step |
|---|---|---|
| Macro | Overall driver gauge (the headline and its verdict) | 4 |
| Macro | Driver breakdown (seven scores, notes, summaries) | 1, 4 |
| Macro | Drivers now / 3Y / 5Y / 10Y (paths, ten-year averages, the gauge at each) | 4 |
| Macro | Regional ranking 1Y / 3Y / 5Y / 10Y | 4 |
| Macro | Market trend 1Y / 3Y / 5Y / 10Y (quarters, z-scores, reversal) | 4 |
| Macro | Correlated sentiment (the correlation matrix and how each driver lands) | 4 |
| Funds | Fund slides (the eleven funds' jobs) | 2 |
| Funds | Side by side | 2 |
| Funds | Fee transparency (feeder and target layers) | 2 |
| Funds | Look-through (regions and sectors underneath) | 2 |
| Funds | Stock level (top holdings, dated, 60-day limit) | 2 |
| Portfolios | A vs B vs C vs D: the donuts, weights, the four analyses year by year, adding funds | 4, 6 |
| Portfolios | Portfolio C: the lede (its stock share and age cap), what each fund pays and its sources, each count's best | 3, 6 |
| Portfolios | Portfolio D: each count's best, the number of funds | 6 |
| Portfolios | Headline forecast: the A-D table with its payout rows, the payout card (next vs last 12 months; fund by fund and 2025 folded), who wins where | 3, 6 |
| Portfolios | Feasible set (the frontier, the best pure ratio, the extremes) | 6 |
| Portfolios | Stress test | 6 |
| Portfolios | In pesos (₱1,000,000 over ten years) | 6 |
| Portfolios | How each drawdown is estimated (volatility term structure, betas, k, the cash floor) | 4, 6 |
| Budget | The reading and the budget in force | 5 |
| Budget | What each view says (6M, 7-12M, 2-3Y, 4-5Y, the 10Y anchor) | 5 |
| Budget | The research by span (drivers, valuation, trend) | 4, 5 |
| Budget | The bands and the guards | 5 |
| Budget | What each step buys (A to D at 20% to 30%) | 5, 6 |
| Budget | Why (the rule and its history) | 5 |
| Report | Rationale report | 7 |
| Report | The setup, volatility, where the weight goes, Global Technology, cash, C | 1, 7 |
| Report | Keeping this current (the calendar, anything postponed) | 1, 7 |
| Report | Sources | 7 |
| Report | Method & limits | 7 |
