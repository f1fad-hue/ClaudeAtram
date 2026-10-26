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
1Y / 3Y / 5Y / 10Y (since v68; 3M / 6M / 12M / 10Y before), then the gauge. Each
driver's score is its 1-year reading; its 3- and 5-year points live in `DRIVER_PATH`
and are re-judged whenever the 1-year score moves far enough to change the path.
Drivers and regions are researched on 1–10; both the headline gauge and the regional
rankings are reported on 1–5. The horizon weights are each view's share of the ten
years (10 / 20 / 20 / 50) and are not to be tuned. Every portfolio is built from the
same inputs — the drivers' rates and energy tilts (read on each driver's ten-year
path), the **volatility gap** (the curve's FORWARD vol over each horizon's years,
weighted, minus the LONG-RUN 19.5 every base return already assumes), the regional
rankings and the **market trend**: each equity sleeve's market over the past year
(momentum) and the past 3 and 5 years annualised (reversal), z-scored against its own
long-run drift and volatility, with the 10Y score held neutral. A reads them at 10
years alone; B, C and D at all four. Refresh `TREND_INPUTS` (quarters and
`trail_ann`) and `TREND_END` at each month-end; a check fails once the window is a
month stale. Every
quarter must reproduce from its months where months are given, and a "1-year"
figure from a search is never used unless the months behind it reproduce it.
Every portfolio — A, B, C and every what-if — is
chosen by the one function `pick()`: the best CAGR in budget, then the lowest
drawdown within 0.05pp of it. Three of the inputs are derived rather than judged: the
regional tilt is `(score − 3.0) × 0.675` on the reported 1–5 scale (identical to
the old `(score − 5.5) × 0.30` on the 1–10 research scale), and each fund's volatility tilt is
`gap × sensitivity`, where the sensitivities in `VOL_SENS` are structural properties
of how each sleeve is built. Change a sensitivity only if the fund's structure changes,
not because you have a view on the market. Never change a score without rewriting
its rationale to cite the new evidence. Re-run the engine: it re-chooses A, B and C
by the one rule over the whole universe (eleven funds from the owner's 22-fund list
since 2026-10-22) within the review's limits - at most 5 funds, at most 35% in any one (C's Nasdaq Equity Income
pin excepted), at least 5% in the money market - on the 5% grid, each
summing to 100. A fund may be held at 0%. Every pick, and every what-if, sits inside ONE
drawdown budget: the 20/30/25/25 reference baseline's macro drawdown less 2.83pp.
The baseline stays in the payload, off the page, so the budget can be re-derived;
do not replace it with a current pick, or the budget would depend on the portfolio
it judges. (The internal four-fund optimiser that ran beside the picks was retired
on 2026-10-22, v62.)

**2b. Re-check the 22-fund list's held-out funds** (`list22_held_out`). A fund enters
the search once its fees are confirmed - its trust fee on ATRAM's own page or on two
current listings that agree, and its target fund named with a published charge - and
not before. When one is confirmed, build it like the others (`ADD_FUNDS`, its factor
loadings, its vol sensitivity, its shocks in every scenario row, its look-through) and
remove it from the held-out list; the check that every one of the 22 is searched or
held out, never both, fails until both are done. Re-run `model/heldout_sens.py` for US Equity
Opportunity and Global Bond Income when their fees move, and update `useq_w_*` /
`gbi_w_*`.

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

1. A, B and C are chosen by the one rule over the whole universe; none is set by
   hand. A fund at 0% is allowed. A fund removed from the list (the two peso bond
   funds, 2026-10-21) never comes back without the owner's instruction. Every fund
   on the 22-fund list is either searched or held out with its reason (v63).
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
100. A TOLERANCE IS SIZED TO THE SERIES, NOT TO THE CALENDAR. A year-ago base "within a
   week" is harmless for a series that drifts and wrong for one that jumped 5.4% in a day:
   Brent's y/y was 2pp high for two releases while every check passed. Ask what the
   series can do inside the bound before choosing the bound.
99. A READING IS NOT A FORECAST UNTIL IT SAYS HOW LONG IT LASTS. The rates and energy
   tilts took a Monetary score of 2.0 as if it held for ten years, beside regional and
   volatility channels that had always averaged their horizons. The inconsistency took
   0.73pp a year off Global Technology's forecast through its rates tilt alone, and no check
   could see it, because each channel was right on its own terms. Give every signal a path.
98. A WEIGHT AND THE QUANTITY IT WEIGHTS MUST COVER THE SAME YEARS. Implied vol at three
   years is the average from today; a weight for years two and three applied to it counts
   year one again. When the weights became shares of the holding period, the vol channel
   had to move to forward vol with them.
97. A NOTE THAT PRINTS "THE LATEST MOVE" DOES NOT KNOW WHICH WAY IT WENT. "The KOSPI fell
   {latest_chg}%" was true for one session and would have printed "fell 0.3%" for a 0.3%
   gain the next. A move that a sentence describes in the past gets its own dated input;
   only a sentence written for either sign may read the latest one.
96. A NAME THAT COMES BACK NEEDS ITS OLD GUARDS REWRITTEN, NOT DELETED. "Nothing left of
   Portfolio D" guarded against the retired review pick for four versions; the owner's new
   four-fund D tripped it on day one. The guard was right about the old D and wrong about
   the name: it now checks that the new D is what it claims, and that the old one's fields
   have not come back with it.
95. A TIMESTAMP IS PART OF A PROBABILITY. "FedWatch had December at 90% on 22 Oct" was
   the 09:12 GMT read; by the close the Treasury rally had it near 76-80%. A quote
   that moves inside a day carries its hour, or the prose built on it ("has barely
   moved") goes false the same afternoon.
94. A CLAIM ABOUT THE PICKS NEEDS A CHECK ON THE PICKS. "None holds it" in a fee note
   is true only until the next roll changes A, B or C. Every sentence that describes
   the selection gets a check against the selection, or it is a guess with a date.
93. ONE STANDARD MEANS ONE READING OF IT. Global AI was held out because its
   listings disagree (1.20% and 1.50%); Global Allocation was let in at 1.20% with
   DragonFi listing 1.50%. Two of three agreeing is not "no disagreement". The
   resolution here was to measure it - at 1.50% no pick changes - and say so; where a
   disagreement would move a pick, the fund waits.
92. A CROSS-CHECK MUST COVER THE SAME PERIOD. ACWI's 2026 quarters "compounded to
   12.92% against iShares' 12.90% year to date to 20 October" - quarters ending 30 Sep
   against a figure running to 20 Oct. The match was luck, and it hid a single-source
   series up to 1pp off the index. Check like against like, or it checks nothing.
91. ONE SOURCE THAT DISAGREES WITH EVERY OTHER IS NOT A SECOND OPINION. AAII had IXJ
   up 20.7% to 31 Aug; the monthly series compounds to 8.0% for January-August, and
   iShares' own NAV has 5.93% to 30 Sep after a -1.96% September - which is where
   8.0% lands. A cross-check is two sources agreeing, not one source cited.
90. EVERY FIXED WIDTH IS A UNIVERSE SIZE WRITTEN DOWN. Going from five funds to
   eleven broke, one by one: a CLAIMS check comparing the first six weights, number
   words that stopped at "six" and "eight", a validator expecting exactly three trend
   markets, six colour slots, and a count check that walked 8^11 grid points and hung
   the engine. None was wrong for five funds. Read a fixed length as an assumption
   about the universe, and derive it from the universe instead.
89. NO PREMIUM THE SOURCE DOES NOT PUBLISH. J.P. Morgan's LTCMA gives regions, not
   sectors, so health care, infrastructure, themes and consumer funds are all built
   on global equity. That is consistent, not neutral: listed infrastructure on a 7.5%
   equity return is the assumption most likely to flatter it, and it holds 35% of A.
   Name the assumption beside the weight it carries.
88. A NEW FUND CAN FALSIFY AN OLD SUPERLATIVE. "Global Technology: the deepest
   drawdown" was a heading, true for five funds and false the day Global Consumer
   Trends joined at -80%. A superlative over a set is a claim about the set; compute
   it, or it goes stale on the first addition.
87. ONE STANDARD FOR EVERY FUND. The owner held US Equity Opportunity out until its
   fee was confirmed; applied to the whole list, the same rule holds out ten more.
   The fund that would move the picks most (Global Bond Income, 30-35% of A) is held
   out by it too, and is shown as a sensitivity rather than quietly admitted.
86. GENERATE WHAT THE LIMITS ALLOW; DO NOT FILTER A GRID. A 21^(n-1) grid filtered
   down to the limit-respecting mixes is fine at five funds and impossible at eleven
   (30 million points against 322,725 valid ones). Generate the valid set directly,
   measure it with the same arithmetic as the published summary, and keep a second,
   differently written generator in the audit.
85. A COUNTERFACTUAL SAYS WHAT IT HOLDS FIXED. The retired four-fund what-ifs
   re-derived the drawdown budget on each alternative column; the universe what-ifs
   the page shows hold it at the live 27.17%, as A is chosen. On 22 Oct the choice
   decided three of the six B answers (B's band held 21 mixes). Neither is wrong;
   an unstated one is. The engine comment now names the budget it holds.
84. A NUMBER CAN TRACE BY COINCIDENCE. The bull-case row's "$65" oil passed the
   every-number-traces check for weeks because a 65% weight sat in the four-fund
   frontier in the payload. Retiring the frontier exposed it. An assumed level in
   prose gets its own named input (`brent_disinflation`), never a lucky match.
83. CODE THAT NOTHING SHOWS STILL COSTS CHECKS, AND HIDES GAPS. The four-fund
   optimiser stayed "for its checks" after the page stopped showing it: about 25
   engine checks, an audit section and four mutations defended an answer no reader
   saw, while the page's Asia fee sentence read `stress_pp`, which only those hidden
   what-ifs carried, and fell back to a typed "0.25pp". When the page drops a
   result, retire the code, and move each check to the thing that is shown.
82. A DATE BOUND POINTS ONE WAY. "The review is dated on/after the as-of date" was
   true on the day the review ran and false the next morning, when the data rolled
   past it. A recorded analysis may not post-date the data it is read beside; it
   may be older, within a stated age. Write the bound as "not after, and within N".
81. A KEY OUTLIVES ITS LABEL. Portfolio D was relabelled B on the page in v55, but the
   payload key, the variables and the element ids kept saying D for four more
   versions, until the owner had to say "no more portfolio d". When a label changes,
   the key changes with it, and a check forbids the old one.
80. A MUTATION IS DERIVED FROM THE TRUTH, NOT TYPED BESIDE IT. m22 typed a wrong
   what-if answer; a fee correction then made that typed vector the right answer and
   the harness reported MISSED for a check that was working. A mutant is the real
   value moved, so it can never coincide with the real value.
79. A FEE IS DATED BY ITS DOCUMENT. The money market's 0.71% was "verified" against a
   KIIDS that had been superseded; the fund's trust fee had since fallen to 0.50%, and
   the model carried the old figure for years. Every fee names the document it came
   from, and a scrub re-reads the fund's current listing, not the note.
78. A PICK IS CHOSEN WHERE IT IS MEASURED. A and B were fixed weights carried over
   from the 22-fund review's own factor model and then measured on this page's basis,
   where the best-worst-case B gave up 0.22pp a year to A for an objective nobody
   had asked this page to pursue. Since v56 the engine chooses A, B and C itself, by
   one rule over the six funds within the review's limits, each on a NAMED column
   (`portfolio_*.column`): A on the long-run returns, B and C on the macro view. The
   review's agreement is published as a flag (`portfolio_a.is_review_pick`), not
   asserted, and audit G4 re-chooses all three and every six-fund what-if from the
   payload alone.
77. A BUDGET IS NOT MEASURED FROM THE PORTFOLIO IT JUDGES. When the owner replaced
   Portfolio A with the review's highest-return pick, the drawdown budget - "A's
   drawdown less 2.83pp" - would have moved with it, and a riskier A would have
   loosened the budget that judges A. The original 20 / 30 / 25 / 25 baseline stays
   in the engine as the budget's reference only, and the page says so.
76. A TILT IS TAKEN FROM THE FIGURE THE PAGE PRINTS. The volatility tilt was taken
   from the unrounded ramp (-0.454) while the page printed -0.45, so Global
   Technology showed +0.06 where the printed figures give +0.05. The ramp is rounded
   to its published precision before any tilt uses it, and the audit now checks the
   tilt exactly, with no tolerance to hide in.
75. A TILT MAY NOT CITE THE BASE IT TILTS. Asia's ten-year anchor was justified by
   J.P. Morgan's EM equity assumption - which IS the Asia fund's base return - so the
   same number lifted the base and again the regional tilt. When the 2027 edition
   cut EM to 7.1% the double count showed. A regional score argues from what the
   base does not already carry: valuation, energy exposure, policy.
74. A FACT ABOUT THE INPUTS IS NOT AN INVARIANT. "B gives up no more return to the
   baseline than the tie" held for three weeks because the inputs happened to make it
   true; on the 2027 roll the budget began to cost B 0.12pp and the check failed on a
   fact, not a defect. It now states the rule that is actually true - B may trail the
   baseline past the tie only when the baseline breaks the budget - and the page
   words "inside the tie" only when it is.
73. A PORTFOLIO PICKED ELSEWHERE IS MEASURED HERE, NOT RE-CHOSEN. D's weights come
   from a wider review on a different basis. Its two added funds are built by the
   same build_fund(), its risk by the same functions with the six-fund universe passed
   in, and the page quotes BOTH numbers - the review's and this page's - each with its
   basis, so neither can stand in for the other.
72. A TOLERANCE A SENTENCE QUOTES IS A TOLERANCE THE CHECK OWNS. "Past 20%" was
   typed into the page beside a check holding its own 0.20, and the VIX3M bound of
   10% lived only in its check while the page called the gap "a touch" whatever its
   size. Both bounds are engine constants the page reads, and wording about a gap
   is banded against its bound, not only signed: -7.19% is not "a touch".
71. A CALIBRATION IS DATA, AND IT MUST REPRODUCE ITS ANCHORS. k = 1.65 and the
   -20% / -33% medians it is calibrated to sat in the page's HTML for a month; no
   check asked whether k still produced them. They are engine data now, and a check
   recomputes both anchors from k on every run.
70. A FEE THE NOTE ITEMISES IS ITEMISED IN THE DATA. "1.17% trustee + 0.01%
   auditor" lived only in a sentence. Components are fields, the sentence is built
   from them, and the parts must sum to the fee.
69. A CHECK GUARDS A DEFECT, NOT A MARKET STATE. "The December future is above
   spot" was true for weeks and failed on a 21% VIX spike - a fact, not an error.
   Where the page's wording follows the data, the check should test the wording's
   honesty (here: a stale strip is flagged), not demand that the market cooperate.
68. A NUMBER TYPED INTO MARKUP IS A NUMBER NO CHECK CAN SEE. 10.5x, 52% / 28%,
   0.88, 1.55% / 1.50%, "~9% p.a." and "~72% US" sat in the page's HTML; two had no
   source at all. Every figure on the page now comes from the payload.
67. A TRAILING WINDOW SAYS WHERE IT ENDS. The trend windows end at a month-end;
   on 15 Oct the KOSPI was 20.7% below its 2 Oct close and nothing said the windows
   could not see it. The page now flags any move after the window's end.
66. A DELTA IS SIGNED BY ITS VALUE, NEVER BY ITS EXPECTED DIRECTION. The peso
   table hard-coded "+" and the gain colour and printed "+-5,435". The validator
   rejects malformed signs anywhere on the page, with every collapsible open.
65. A CHECK MUST NOT PIN STALE PROSE. "Hormuz is quoted on oil volume" demanded
   Goldman's 28 Aug figure in the note, so the note kept quoting it for seven
   weeks. A check tests the newest dated reading, not the one it was written for.
64. A FEE IS A DATED FACT. ATRAM repriced the Global Technology trust fee on
   14 Sep; the model carried the old "verified" 1.15% for a month. Every feeder fee
   is re-read from the manager's current fund page at each review, and a changed
   fee carries its previous value and effective date.
63. A SNAPSHOT OUTSIDE THE ENGINE NEEDS A CHECK OR IT ROTS. The top-level
   README's result table showed the 2 Sep build for a month before anyone looked.
   It is now compared with the payload by the review audit on every run.
62. A LABEL NAMES ITS OWN BASIS, NOT A NEIGHBOUR'S FIGURE. The Report's
   "provisional" tag printed the 23 Sep market print (5.104%) beside ANY
   provisional 10-year close - right once, then wrong the next time a point was
   provisional, which was 9 Oct. A provisional point now carries the basis it is
   provisional on, and a check refuses a basis that is a number.
61. A REALISED OUTCOME IS MEASURED AGAINST REALISED RISK. The trend channel's
   z-scores divided trailing returns by IMPLIED volatility, which carries the
   3.5-point premium options charge over delivered volatility - shrinking every
   z by ~18%. The model publishes the realised-equivalent level; that is the one a
   realised return is compared with.
60. A TEST MUST NOT PREDATE WHAT IT TESTS. The "2 Oct" VIX futures board was
   validated against the 1 Oct VIX3M - the only reading available - and matched it
   to 0.3%, while missing 6-7 Oct by over 4%: it priced the market of the day
   before its own date. The VIX3M reading must now be dated on or after the strip,
   and the comparison shifts the curve forward in time, not only in level.
59. A RETURN IS SCORED AGAINST WHAT WAS ALREADY EXPECTED, AND ONLY FROM ITS
   OWN PARTS. The trend channel z-scores each window against the sleeve's long-run
   drift and volatility, so a market that merely did what its base return says
   scores neutral. Two "1-year" figures surfaced in its research (Nasdaq-100
   +34.38%, global tech +58.08%) that their own monthly series show cannot be twelve
   months to the window end. A summary's period label is a claim; compound the
   months before using the total.
58. A SETTLE RECOVERED FROM THE NEXT SESSION NEEDS TWO WITNESSES. Brent's 6 Oct
   settle was never reported; it is carried because two 7 Oct quotes both measure
   their moves from it. A check now requires two or more next-session quotes for
   every recovered settle, and the page carries no move for that day. One quote is
   a guess with arithmetic attached.
57. ONE OBJECTIVE, ONE RULE. Two portfolios chosen to the same stated objective
   must be chosen by the same function. Every pick on the page now goes through
   `pick()`, and both harnesses re-apply it to each portfolio's own candidates. A
   rule change can move the headline comparison: under it B gives up 0.03pp of
   forecast return to the baseline, inside the tie, and the page says so in words
   generated from the numbers rather than "better on both axes" typed in markup.
56. A NUMBER IS SHOWN AT THE PRECISION IT IS SET. Geopolitics was scored 1.75 and the
   Report printed "1.8"; the driver cards showed 8.25 as 8.3. A rounded score is a
   different score. Format each value at its own precision, never at the
   template's.
55. POSITION IS NOT IDENTITY. `vix_fut_dec` was "the last contract on the strip".
   That was true for three weeks, then January joined and the page printed
   January's level as December's. Select by the name the prose uses, never by
   where the item happens to sit in a list.
54. A CONTRACT ROLL IS NOT A PRICE MOVE. Brent's front month went November to
   December on 30 Sep, and December was $5.47 cheaper the same day. A move across
   a roll is measured from the NEW contract's prior, which is recorded. A
   comparison across a roll, such as "below the high" or "on the week", is
   retired, or stated like for like, or the contract is named.
53. A BOUND THAT PASSES TODAY CAN FAIL ON THE NEXT ROLL. The Brent y/y base passed
   its one-week bound at six days (two sessions from failing), FedWatch its five-day
   bound at five (one session), the VIX strip its 30-day stop at 25. A check that passes says nothing about tomorrow, so
   every review lists the bounds within one roll of failing, with what must be
   sourced before then.
52. A HIGH IS A DATED RECORD, AND SO IS EVERY REPORTED MOVE. One "session high"
   field was overwritten by the next day's roll, which left "$108.23 on 24 Sep"
   in prose with nothing behind it. Brent's moves lived only in sentences. Both
   are now dated records, and each entry is checked against the series on its own
   date: a high at or above that day's settle, a move reproducing from the prior.
51. A SELECTION RULE IS PART OF THE RESULT. Portfolio C took the lowest drawdown
   within 0.05pp of its best return; Portfolio B took the strict maximum, and five
   portfolios sat inside that band. When a difference smaller than the model's
   rounding decides the answer, publish the band beside the answer. And when two
   answers on one page use different rules, say so and leave the choice to the
   owner. (The owner chose on 2026-10-07: see 57.)
50. A VALUE UPDATE IS NOT A VERIFICATION. The Fed funds row read "raised 25bp on
   16 Sep" while citing the 29 Jul statement and a 5 Sep verification - both before
   the event. The IMF rows said "April" for 2½ months after the July update, and
   July payrolls kept their first print for three weeks after the revision. When a
   figure changes, its source and date change in the same edit, and a sweep lists
   every row by age before each review.
49. A NUMBER THAT TRACES BY COINCIDENCE IS UNTRACED. "Excluding energy 2.2%", "fuel
   oil +52%", "Samsung -3.5%", "Saudi output down ~1.9 mb/d" and a dozen more passed
   the trace check because an unrelated input happened to hold the same value. The
   test is the pairing, not the match: every figure in a note has its own input,
   and a review lists each prose number beside the input it traced to.
48. A DRAFTED CALL IS NOT A PUBLISHED ONE. A quarter-point raise to Geopolitics was
   drafted on the volume data and withdrawn when the weekend's rejection of Iran's
   plan, and Monday's oil rally, landed. Record the draft and why it did not ship; do not quietly overwrite.
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
   (`WHAT_IF_UNIV` since v62), checked to reproduce B and C on the live column and
   re-derived by the audit.
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

