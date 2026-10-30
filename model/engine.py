#!/usr/bin/env python3
"""
ATRAM 4-Fund Portfolio Engine
=============================
Deterministic, auditable model. Pure stdlib (no numpy) so it runs anywhere.

Everything below is derived from the VERIFIED INPUTS block, which cites the
authoritative source for each number. Change an input -> every downstream
figure recomputes. No hard-coded outputs.

Run:  python3 engine.py            -> human-readable audit report
      python3 engine.py --json     -> machine-readable payload for the dashboard
"""
import datetime as _dt
import json, math, re, sys
from decimal import Decimal, ROUND_HALF_UP
from itertools import combinations

# Two different dates, which this model had been conflating. AS_OF is the market
# data date - the last trading session every price, yield and level comes from.
# REVIEW_DATE is when a human last worked through the page. On a weekend review they
# differ, and reference data retrieved during the review is legitimately NEWER than
# the market snapshot: a look-through read today is not "stale by -2 days".
# NO WEEKDAY IS TYPED HERE. The comment on REVIEW_DATE said "(Saturday)" on a
# Sunday, because a weekday written beside a date is a second copy of the date
# that nobody updates. Both weekdays are derived and checked below instead.
AS_OF = "2026-10-30"        # newest completed session carried (Friday's closes in Seoul
                            # and Tokyo, after the BoJ held; Thursday's in New York and
                            # Manila, Brent's settle, the VIX and the 10-year, after US GDP,
                            # September PCE and the ECB's hold. WTI at 28 Oct, its 29 Oct
                            # settle in dispute; the 2-year at 27 Oct and the 30-year at
                            # 26 Oct; Manila's 30 Oct closes not yet in two sources)
REVIEW_DATE = "2026-10-30"  # when this review was worked through

# ----------------------------------------------------------------------------
# INVESTMENT HORIZON
# The mandate horizon. Every horizon-dependent quantity below derives from this
# constant rather than hard-coding a number of years, because on 8 Sep the
# horizon moved 5 -> 10 and the previous build had "5" spelled out in a dozen
# places. Changing this one line moves the long volatility point, the horizon
# blend's long bucket, the peso compounding, the drawdown scaling and every
# label that names the horizon.
# ----------------------------------------------------------------------------
HORIZON_Y = 10.0
HZ_LABEL = f"{HORIZON_Y:.0f}Y"          # "10Y"
DD_CALIB_Y = 5.0                        # the window the -20%/-33% medians describe

# ----------------------------------------------------------------------------
# 1. VERIFIED INPUTS  (source-cited; see SOURCES dict at bottom)
# ----------------------------------------------------------------------------

MACRO = {
    # THE FED MOVED. 16 September 2026: +25bp to 3.75-4.00%, the first increase
    # since 2023, and UNANIMOUS - the three July dissenters got the whole committee.
    # The "Hawkish repricing" stress row was written when a second hike returning to
    # the 2026 strip was the tail; the dot plot now has it as the median.
    "fed_funds_lower": 3.75,
    "fed_funds_upper": 4.00,
    "fed_dot_2026": 4.1,          # median end-2026 policy rate, i.e. one more hike
    "fed_dots_one_more": 12,      # of 18, at 4.125%
    "fed_dots_two_more": 4,       # of 18, at 4.375%
    "fed_dots_participants": 18,
    "fed_dot_one_more_level": 4.125,   # midpoint the 12 project
    "fed_dot_two_more_level": 4.375,   # midpoint the 4 project
    # SEPTEMBER CPI (BLS, 14 Oct): headline +0.6% m/m, 3.7% y/y from 3.4%, against
    # a 3.6% Dow Jones consensus; core +0.3% m/m (0.2% expected), 2.6% y/y from 2.4%
    # (2.5% expected). Gasoline +9.1% m/m and +34.2% y/y - over half the monthly
    # rise; energy +20.4% y/y; shelter 3.2% from 3.0%; food 2.5% from 2.7%;
    # airline fares +22% y/y (CNBC, CBS, CNN, Fox Business citing BLS).
    # The page had quoted a 3.7% consensus for this print - Admiral Markets'
    # preview figure, not the Dow Jones survey most reports measured it against.
    "us_cpi_headline": 3.7, "us_cpi_headline_prev": 3.4,
    "us_cpi_headline_consensus": 3.6, "us_cpi_core_consensus": 2.5,
    # Every figure the inflation note quotes is an input. Until 2026-09-26 five of
    # them were not, and "traced" only by coincidence - the July priors (2.5, 3.2)
    # to the ECB rate and a VIX move, fuel oil's +52% to Asia's EPS growth, the
    # 0.2% consensus to a VIX future's maturity. July's food rate (3.0%) could not
    # be re-verified and is no longer quoted.
    "us_cpi_core": 2.6, "us_cpi_core_prev": 2.4,   # Sep (14 Oct) / Aug (11 Sep)
    "us_cpi_core_mom": 0.3, "us_cpi_core_mom_consensus": 0.2,
    "us_cpi_headline_mom": 0.6,
    "us_cpi_shelter": 3.2, "us_cpi_shelter_prev": 3.0,
    "us_cpi_food": 2.5, "us_cpi_energy_yoy": 20.4,
    "us_cpi_gasoline_yoy": 34.2, "us_cpi_gasoline_mom": 9.1,
    "us_cpi_airfare_yoy": 22,
    "us_pce_12m": 3.7,
    # AUGUST PCE (BEA, 30 Sep): headline +0.3% m/m and 3.4% y/y against 3.7%
    # expected, core +0.2% and 3.0% against 0.3% and 3.3%. The July headline was
    # REVISED DOWN to 3.4% - the 3.7% carried above as us_pce_12m is July's first
    # print, kept for the record and no longer quoted as current. Part of the
    # improvement is the BEA's annual methodology overhaul (software, legal
    # services, portfolio fees), not prices cooling, and the notes say so.
    "us_pce_aug": 3.4, "us_pce_aug_consensus": 3.7, "us_pce_jul_rev": 3.4,
    "us_core_pce_aug": 3.0,
    "us_pce_mom_aug": 0.3, "us_core_pce_mom_aug": 0.2,
    # SEPTEMBER PCE (BEA, 29 Oct; Econoday, Xinhua): headline +0.5% m/m and 3.6% y/y, core
    # +0.3% and 3.1%, core in line with the 3.1% consensus; real spending flat and the
    # saving rate down to 3.8%, the lowest in almost four years.
    "us_pce_sep": 3.6, "us_core_pce_sep": 3.1, "us_core_pce_sep_consensus": 3.1,
    "us_pce_mom_sep": 0.5, "us_core_pce_mom_sep": 0.3, "us_saving_rate_sep": 3.8,
    # US THIRD-QUARTER GDP, advance (BEA, 29 Oct; NAW; Advisor Perspectives): 3.4% at an
    # annual rate against 3.1% expected (WSJ survey) and 2.2% in the second quarter, on
    # inventories, equipment and consumer and government spending, less exports.
    "us_gdp_q3": 3.4, "us_gdp_q3_consensus": 3.1, "us_gdp_q2": 2.2,
    # A DATING ERROR THAT WAS PUBLISHED FOR TWO DAYS. 4.94 was carried as the
    # 18 September close and it is the SEVENTEENTH's - the Fed's own H.15 gives
    # 4.94 for 17 Sep, and CNBC has the 10-year falling "more than 7 basis points"
    # that day after the hike. Friday the 18th went the OTHER way, rising 5-7bp to
    # hover near 5%, and the notes built "the rate leg eased too" on top of the
    # wrong day. Caught on 2026-09-21 by the chain: Monday's close of 4.951, down
    # "more than 4 basis points", backs out to a Friday near 4.99 - which 4.94
    # cannot produce. Third instance of this failure mode after the 15 Sep VIX
    # print and the 14 Sep equity figures: a real number on the wrong date.
    #
    # ONE BASIS: OFFICIAL CLOSES ONLY. Rebuilt 2026-09-23, because every problem
    # this series has had traces to mixing two kinds of number. CNBC's bond stories
    # are written DURING the session and quote yields to 3dp; the Treasury's daily
    # par curve and the Fed's H.15 (which is built from it) publish the ~3:30pm
    # close to 2dp. The series had both. So:
    #  - "4.951% on 21 Sep" was a CNBC mid-session print presented as a close. The
    #    official close was 4.96. Proven by the chain: Tuesday's CNBC story put the
    #    10-year "less than 1 basis point lower at 4.959%" - 0.1bp below 4.96, and
    #    impossible against a 4.951 close.
    #  - the 18 Sep "dispute" (4.99 / 5.00 / 5.01) was not three readings of one
    #    close; it was intraday quotes set beside the official close. On the
    #    official basis it is 5.01 - which is +7bp on the 17th's 4.94, matching the
    #    reported "+7bp", and -5bp into the 21st's 4.96, matching "fell more than
    #    4bp". It chains both ways. The withheld session is RESOLVED.
    #  - 5.016 on the 16th was a 3dp CNBC print, so it is not in this series.
    # The precision is the signature, and a check now enforces it: a 3dp value in
    # this series is an intraday quote that has leaked in.
    "ust_10y_basis": "official close: Treasury daily par curve / Fed H.15, 2dp",
    "ust_10y_history": [
        ("2026-09-17", 4.94),    # Federal Reserve H.15
        ("2026-09-18", 5.01),    # Treasury par yield "finished Friday at 5.01%"
        ("2026-09-21", 4.96),    # FRED DGS10; CNBC's 4.951 was mid-session
        ("2026-09-22", 4.97),    # settled slightly higher; CNBC's 4.959 was mid-session
        ("2026-09-23", 5.12),    # CONFIRMED 2026-09-26 - see below
        ("2026-09-24", 5.18),    # FRED DGS10; the intraday peak that day was 5.223
        ("2026-09-25", 5.17),    # Treasury par curve (Advisor Perspectives, Wolf Street)
        ("2026-09-28", 5.24),    # CONFIRMED 2026-10-03: FRED DGS10 agrees with StreetStats
        ("2026-09-29", 5.26),    # FRED DGS10; CNBC's 5.253 was mid-session
        ("2026-09-30", 5.29),    # FRED DGS10; CNBC's 5.298 was mid-session
        ("2026-10-01", 5.24),    # StreetStats par curve (2-year 4.78, 30-year 5.61)
        # 2 OCT RESOLVED 2026-10-07 at 5.28: FRED DGS10 has 5.28, and Monday's 5.31
        # was reported "+3 basis points", which only 5.28 gives. The rival 5.27 was
        # Trading Economics' market quote. The dispute record is kept below.
        ("2026-10-02", 5.28),
        ("2026-10-05", 5.31),    # FRED DGS10; par curve 2-year 4.84, 30-year 5.66
        # 6 OCT RESOLVED 2026-10-10: FRED DGS10 now has 5.27 - the figure the market
        # quotes gave, but carried only now that an official source has it.
        ("2026-10-06", 5.27),
        ("2026-10-07", 5.28),    # FRED DGS10; intraday 5.365% before the 10-year auction
        ("2026-10-08", 5.22),    # FRED DGS10; Treasury par curve 5.22, 2-year 4.75
        # 9 Oct CONFIRMED 2026-10-15: FRED DGS10 and H.15 both have 5.24.
        ("2026-10-09", 5.24),
        # 12 Oct: Columbus Day - the bond market was shut, so there is no close.
        ("2026-10-13", 5.21),    # FRED DGS10 / H.15; 2-year 4.79 (T10Y2Y 0.42)
        # 14 Oct CONFIRMED 2026-10-17 by FRED DGS10 / H.15 at 5.19. After the CPI it
        # ran from ~5.19 to ~5.33 within half an hour, then reversed as stocks fell.
        ("2026-10-14", 5.19),
        ("2026-10-15", 5.10),    # FRED DGS10 / H.15; Treasury par curve 2-year 4.77, 30-year 5.43
        # 16 Oct RESOLVED 2026-10-20: the Fed's H.15 of 19 Oct and FRED DGS10 have
        # 5.09. The market quotes had been 5.081-5.098 (MND, CNBC, Investing).
        ("2026-10-16", 5.09),
        # 19 Oct CONFIRMED 2026-10-21 on the par curve by two more sources: Vantage
        # ("5.15% daily par yield on 19 October") and Forecasts.org (5.15), beside
        # Forbes and Stock Market Watch. CNBC's market basis 5.146%.
        ("2026-10-19", 5.15),
        # 20 Oct: Treasury par curve 5.12, "down 3 basis points" (Forbes' Treasury-
        # rates page) - chains off 5.15; Investing.com's market close 5.133. The Fed's
        # H.15 now has the 20th at 5.12 (2-year 4.79, 30-year 5.42).
        ("2026-10-20", 5.12),
        # 21 Oct: 5.13, +1bp (Forbes' Treasury-rates page, the par curve; Trading
        # Economics 5.13 on the market basis). FRED's T10Y2Y for the 21st is 0.32, which
        # is 5.13 less the par curve's 4.81 2-year - so the official spread pins it too.
        ("2026-10-21", 5.13),
        # 22 Oct: 4.96, -17bp, on the par curve (StockMarketWatch's table, "official U.S.
        # Treasury data"; 24/7 Wall St: "Treasury's official par yield curve shows the
        # 10-year closing at 4.96%, down from 5.13%"). Market basis: CNBC 4.972% late,
        # the biggest one-day fall since 10 Mar 2023; Trading Economics 4.96; MND 4.966.
        ("2026-10-22", 4.96),
        # 23 Oct: 5.00, +4bp, on the par curve - two republications of the Treasury's
        # table (ETF Trends' "Treasury Yields Snapshot" and a second curve table: 3-month
        # 4.22, 2-year 4.69, 10-year 5.00, 30-year 5.33). Market basis 4.988 (Investing.com;
        # Reuters "about 4.99%"); CNBC: "back to 5%" on the week.
        ("2026-10-23", 5.00),
        # 26 Oct OFFICIAL: 5.00 (FRED DGS10, from the Fed's H.15 release of 27 Oct, whose
        # table runs to the 26th), unchanged; the market basis had it near 4.99.
        ("2026-10-26", 5.00),
        # 27 Oct: 4.99, -1bp, on the par curve (Forbes' Treasury-rates page; StockMarketWatch's
        # table, "official U.S. Treasury data"); market close 4.993% (Investing.com, Portfolio
        # Terminal). FRED's T10Y2Y for the 27th is 0.29 = 4.99 - 4.70. MND's 5.019 is not carried.
        ("2026-10-27", 4.99),
        # 28 Oct: 5.05, +6bp, after the Fed held - the first official close above 5% since
        # the 21st (the par curve as JOLT Journal reprints it; Forbes' Treasury-rates page has
        # the 29th "down 7 basis points", which lands here). Held in v83, when only market
        # quotes were reachable (Investing.com 5.015, CNBC 5.02 intraday).
        ("2026-10-28", 5.05),
        # 29 Oct: 4.98, -7bp, after the GDP beat and September PCE (Forbes' Treasury-rates
        # page; the par curve via JOLT Journal); ^TNX's 4.989 is the market close.
        ("2026-10-29", 4.98),
    ],
    # 23 Sep is the 5.104% market-close print (CNBC, Wolf Street: "+13.7bp to
    # 5.104") rounded to 2dp, NOT a Treasury par-curve / H.15 figure: neither was
    # reachable from the review environment. On this series' own basis that is
    # exactly the mixing the 3dp tripwire exists to stop, so the point is marked
    # provisional rather than passed off as official. CNBC's own prior reference
    # (5.104 - 0.137 = 4.967) rounds to the official 4.97, so the two bases agree
    # to within a basis point here - but "agree" is a finding for the next review
    # to make, not an assumption. A check allows only the LATEST point to be
    # provisional: the next session's roll fails until this one is confirmed.
    # CONFIRMED 2026-09-26, and it was NOT the rounded print: the official close
    # was 5.12, two basis points above the 5.10 carried provisionally. StreetStats'
    # par-curve table dated 23 Sep gives 10-year 5.12 - and its 2-year (4.90) and
    # 30-year (5.40) on the same row match that day's market readings (4.889,
    # 5.398), which pins the table to the right date; Forbes' Treasury-rates page
    # for the 23rd also reads 5.12, and Saxo had it "closed above 5.11%". CNN's
    # "closed at 5.11%" is a press figure, not the par curve; it is kept in the
    # dispute record with the provisional 5.10. The week then chains on one basis:
    # 5.01 on the 18th to 5.17 on the 25th is +16bp, which is exactly Wolf Street's
    # "rose by 16 basis points during the week, to 5.17%". The 24th's 5.18 is the
    # 3:30pm official close; CNBC's market close that day was ~5.16 (its Friday
    # story has the 10-year "rising less than 1bp to 5.163%") - the two bases differ
    # by two basis points on the day, and in DIRECTION on Friday (-1bp official,
    # +<1bp market). The series carries one basis, so the prose says "little
    # changed" for Friday and quotes no direction.
    # 28 Sep: StreetStats' par-curve row gives 10-year 5.24 (2-year 4.94, 30-year
    # 5.56); Yahoo's close-of-day story also has 5.24. CNBC's market basis had it
    # "roughly 9.5bp to 5.25%", intraday "tops 5.25%" (Seeking Alpha). One par-curve
    # source is one source, so the point is PROVISIONAL until a second confirms it.
    # CONFIRMED 2026-10-03: FRED DGS10 also has 5.24 for the 28th, so the point is
    # no longer provisional.
    # 2 OCT WITHHELD. Two candidates for the official close - 5.27 (Trading
    # Economics, "+0.03") and 5.28 (a par-curve table: 2-year 4.83 plus a 0.45 spread)
    # - and neither is the Treasury's own release. CNBC's market basis had the
    # 10-year "almost 5 basis points" higher at 5.281% after an early fall on the
    # weak payrolls. The VIX rule: a close two sources disagree on is not carried.
    # 20 OCT CONFIRMED 2026-10-21: two republications of the Treasury par curve
    # (YourBestSavings and Forbes' Treasury-rates page) both read 5.12, and Mortgage
    # News Daily's market close was 5.123 - the 23 Sep rule (two par-curve sources).
    "ust_10y_provisional": [],
    # 21 Oct was held back on 22 Oct on market quotes alone (Trading Economics 5.13,
    # Investing.com 5.127, CNBC intraday 5.109); carried from 2026-10-22 on the par curve.
    # 22 Oct was held back on 23 Oct on market quotes alone; carried from 2026-10-23 on
    # the par curve. Investing.com's 22 Oct table (5.065) is wrong on any basis.
    "ust_10y_provisional_basis": "Treasury par curve; FRED H.15 pending",
    "ust_10y_disputed_23sep": [5.10, 5.11, 5.12],
    # 6 Oct was NOT CARRIED on 7 Oct: only market-basis quotes existed (Trading
    # Economics and the CBOE ^TNX at 5.27; CNBC 5.286% mid-session). RESOLVED
    # 2026-10-10 at 5.27 when FRED DGS10 published it. The market quote is kept.
    "ust_10y_withheld": [],
    "ust_10y_disputed_2oct": [5.27, 5.28],
    # The three figures that made 18 Sep look disputed, kept as the record of a
    # mixed-basis error rather than deleted: two were intraday market quotes.
    "ust_10y_disputed": [4.99, 5.00, 5.01],
    # ONE name for the intraday peak, and it MOVED again on 23 Sep - the close
    # itself (5.10) now exceeds the OLD peak (5.04, 15 Sep), and the new intraday
    # high (5.135, "highest since July 2007") is well clear of it. The prior
    # record is kept, dated, rather than overwritten - the same pattern used for
    # the VIX 2026 low when IT moved and got missed for nine days.
    # MOVED AGAIN on 24 Sep: CNBC "surged more than 10bp to 5.223%, levels not
    # reached since June 2007" late in the session (Saxo: "as high as 5.22%").
    # The 24 Sep close (5.18) is now carried beside it. The peak did NOT move on the
    # 25th: CNBC's Friday story dates the post-2007 high to Thursday.
    # MOVED AGAIN on 28 Sep: "tops 5.25%" (Seeking Alpha / Helious), CNBC "roughly
    # 9.5bp to 5.25%, the highest since 2007". 5.25 is a floor on the day's high,
    # not its exact print, and the prose says "above 5.25%" accordingly.
    # MOVED AGAIN on 1 Oct: CNBC "hit an intraday high of 5.342% to reach its
    # highest level going back to April 3, 2002, before easing 5 basis points to
    # 5.243%". The superlative changed with it - 2002, not 2007 - and the prose
    # says so. The 28 Sep floor of 5.25 is kept as the prior record.
    # MOVED AGAIN on 5 Oct: "jumped to 5.349%, its highest level since April 3,
    # 2002" (CNBC), after the ISM services report; 1 Oct's 5.342% is the prior.
    # MOVED AGAIN on 7 Oct: 5.365% before the 10-year auction (MarketScreener /
    # Quartz; CNBC 5.35%, NBC "as high as 5.36%"), still below the 5.379% of
    # 3 April 2002, so the superlative stays "since April 2002". The auction then
    # cleared at 5.3%, the highest 10-year auction yield since November 2000, with
    # indirect bidders taking 80.3%.
    "ust_10y_peak": 5.365, "ust_10y_peak_date": "2026-10-07",
    # The superlative is DATA, not markup: the Report typed "its highest since 2007"
    # beside a field that moved past the 2007 peak on 1 Oct.
    "ust_10y_peak_since": "April 2002",
    "ust_10y_peak_prev": 5.349, "ust_10y_peak_prev_date": "2026-10-05",
    # The 2-year had NO date field and was 12 days stale - 4.63 from 11 Sep, when
    # the actual level had risen 11bp - because the lag check added on 21 Sep
    # listed the 10-year and 30-year and missed it. These two are CNBC session
    # readings (3dp), labelled as such; no official close was found for either,
    # and the prose calls them readings, not closes.
    # CORRECTED on the 23 Sep re-verification: the first pass carried 4.947 for
    # the 2-year - which does not chain with CNBC's own "+11bp" off a ~4.77 prior -
    # and 5.39 for the 30-year, a 2dp figure in a 3dp series, with a superlative
    # ("since July 2004") the source does not make. CNBC's end-of-session story:
    # 2-year "jumped more than 11bp to 4.889%, highest since May 2024"; 30-year
    # "gained more than 9bp to 5.398%, highest since June 2007".
    # 24 Sep (CNBC): 2-year "rose more than 4bp to 4.941%" - 4.889 + 0.052, it
    # chains. The 30-year was "last about 10bp higher, hitting a high of 5.501%, a
    # level not seen since June 2004"; "about" is not a reading, so the carried
    # level stays the 23 Sep 5.398 and the session HIGH is carried as its own dated
    # field rather than passed off as a close.
    # 25 Sep (CNBC, "little changed to end a volatile week"): 2-year "down more
    # than 3bp at 4.856%", 30-year "higher by more than 2bp at 5.488%". Neither
    # chains to the prior reading here, and neither is expected to: both ends are
    # mid-session quotes (the 2-year's implies a ~4.89 Thursday close, not the
    # 4.941 read DURING Thursday). The Treasury par curve has Friday's 2-year at
    # 4.81 and 30-year at 5.50 (20-year 5.55, highest since June 2004) - a
    # different basis, recorded in CLAIMS and not mixed in here.
    # 28 Sep (CNBC): 2-year "rose roughly 8bp to 4.93%", 30-year "advanced 8bp to
    # 5.57%, a level not touched since 2004". The 30-year's reading IS the session
    # high as far as any source says, so the high moves with it.
    # 2 Oct (CNBC, after the payrolls): 2-year "higher by 5 basis points at
    # 4.839%", 30-year "added 2 basis points at 5.629%". The 30-year's high is the
    # 30 Sep reading of 5.632% (CNBC), "around its highest level since 2002"; on
    # 29 Sep it had "surpassed 5.61%" intraday (5.623% at one point).
    # 6 Oct (CNBC, "Treasury yields slide as surge to multiyear highs cools"):
    # 2-year "down more than 3 basis points at 4.80%", 30-year "down less than 1
    # basis point at 5.659%". The 30-year's HIGH moved on 5 Oct: it "rose at least
    # 7 basis points to 5.7%", a level not seen since late May 2002 (Bloomberg),
    # 5.69% in another report - carried at the 2dp figure, 5.69.
    # 9 Oct (CNBC, "Treasury yields steady as traders wrap up volatile week"):
    # 2-year "more than 3 basis points higher at 4.789%" (par 8 Oct 4.75 + 3.9bp),
    # 30-year "fell less than 1 basis point to 5.60%". The 30-year HIGH moved on
    # 7 Oct to 5.733% (MarketScreener / Quartz; NBC 5.73%), the highest since 2002.
    # 14 Oct (CNBC afternoon): 2-year "up slightly at 4.808%", after its highest
    # since 29 Sep on the CPI; 30-year down about 4bp at 5.517%. StreetStats' table
    # (4.86 / 5.56) is undated within the day and not carried.
    # 16 Oct (CNBC, "yields waver as traders wrap up volatile week"): 2-year "down
    # more than 3 basis points at 4.715%", 30-year "rose less than 1 basis point to
    # 5.434%"; the 10-year 5.085%. Par curve 15 Oct: 4.77 / 5.10 / 5.43.
    # 20 Oct, TREASURY PAR CURVE (YourBestSavings / Forbes republications, 2026-10-21):
    # 2-year 4.79%, 30-year 5.42% (-6bp; Trading Economics' OTC quote 5.43%); FRED's
    # T10Y2Y for the 20th is 0.33, which is 5.12 - 4.79. From here the 2-year and
    # 30-year are carried on the same official-close basis as the 10-year.
    # 21 Oct, par curve (Forbes): 2-year 4.81%, 30-year 5.42%; T10Y2Y 0.32 = 5.13 - 4.81.
    # 22 Oct, par curve (StockMarketWatch's table): 2-year 4.65% (-16bp), 30-year 5.29%
    # (-13bp); CNBC's market closes 4.659% and 5.296% agree within a basis point.
    # 23 Oct, par curve (the same two republications): 2-year 4.69% (+4bp), 30-year
    # 5.33% (+4bp).
    # 26 Oct, par curve (StockMarketWatch's table; Forbes): 2-year 4.68% (-1bp), 30-year
    # 5.31% (-2bp); 5.00 - 4.68 = 0.32 on the 10-year's own 26 Oct close. CNBC's
    # mid-session 4.716% / 5.299% are not carried.
    # 27 Oct, par curve (StockMarketWatch's table): 2-year 4.70% (+2bp); FRED's T10Y2Y 0.29
    # is 4.99 - 4.70. Its 30-year 5.30% has no second source, so the 30-year stays at 26 Oct.
    "ust_2y": 4.70, "ust_2y_date": "2026-10-27",
    "ust_10y_intraday_14oct": 5.33,   # ~30 minutes after the CPI (Quartz, CNBC)
    "ust_30y": 5.31, "ust_30y_date": "2026-10-26",
    "ust_30y_high": 5.733, "ust_30y_high_date": "2026-10-07",  # highest since 2002
    "ust_curve_basis": "Treasury par curve closes (from 20 Oct; mid-session readings before)",

    # The September meeting is DECIDED, so these now describe the NEXT move rather
    # than a meeting that has happened. Carrying a "September odds" field past the
    # September decision would be an input describing the past as if it were pending.
    # The prose quotes DELTAS, and a delta is only auditable if both ends are
    # published inputs. Two deltas, two baselines: the ONE-DAY move is off the 22nd
    # (55%, CNBC: "increased from 55% on Tuesday, an 18-percentage-point increase"),
    # and the move since the decision is off the first post-meeting reading (50.9%,
    # 17 Sep). The first pass published "jumped from 50.9% to 73% in a day" - the
    # WEEK's move described as the day's, which is the 4.94%-dated-the-18th error
    # in a different field.
    # DATED. Its date lived only in this comment, the defect every other market
    # series was cured of on 21 Sep; the Fed odds were missed. A secondary read on
    # 24 Sep put October at 73.5% and a desk note at "70%" - consistent with no
    # material change, and neither is FedWatch itself, so 73.0 stays, dated.
    # 26 Sep: a secondary page citing FedWatch "as of 25 Sep" reads 75.8% - the
    # same direction, a couple of points firmer, and still not the tool itself.
    # Held at 73.0 on the same rule; the 5-day bound on its date still passes.
    # 28 Sep: secondary reads disagree - 72.3% ("CME FedWatch as of 28 Sep", via a
    # tracker) and 64.2% (a weekly note, "from 57.6% a week earlier"). Recorded as a
    # range; neither is the tool, and 73.0 (23 Sep) is at its 5-day bound today.
    # 2 OCT, AFTER THE PAYROLLS (CNBC citing FedWatch): "only a 17% chance that
    # the Fed increases rates by a quarter percentage point" in October. The week-
    # earlier column of the same tool had HOLD at 35.8%, i.e. a hike at 64.2% -
    # which corroborates the 28 Sep weekly note's 64.2% and settles that disputed
    # range at its low end. December: 66.2% for a hike by then (FedWatch, 2 Oct).
    # 6 OCT (Benzinga citing CME FedWatch): October 21.6%, December 86.2% - the
    # December meeting firmed back toward where it stood before the payrolls.
    # 14 OCT, AFTER THE CPI: about 22% before the release, ~50% at 9:21am ET (CME's
    # own FedWatch account: "jumped to 50% post-CPI, from 22% a day ago"), 41.5% at
    # midday, then 31.6% October and 89.7% December at 7:23pm ET (FXStreet via
    # FinanceFeeds). Forbes' 2:45pm read (66% hold) and a 33.8% late print agree
    # within three points; Reuters' factbox has December at 89.5%. The latest
    # dated pair is carried; the intraday peak is kept beside it.
    # 15-16 OCT: the PPI (+1.3% m/m) did NOT lift the odds - energy did the work -
    # and Chair Warsh gave no signal on the 16th. CME FedWatch: 85.1% hold for
    # October, i.e. 14.9% for a hike, and 88.9% for a hike by December (Invezz,
    # 16 Oct); Schwab had October at 17% "from around 45% Wednesday"; CNBC "more
    # than 80%" hold. Goldman reads a pause in October and a final hike in December.
    # 19-20 OCT: no reading of the tool itself was reachable. Secondary reads agree
    # on the shape and not the decimals - October hold 82.8-85.1% (a hike at
    # ~15-17%; Forbes "about 15%" on the 19th), December 82.8% to 94% by source
    # and hour. None is carried; the 16 Oct pair stays, dated, inside its 5-day bound.
    # 21 OCT: secondary reads again agree on the shape - October hold 82.8-83.9%,
    # December 90-94% - and none is the tool.
    # 22 OCT, 09:12 GMT (FXStreet citing CME FedWatch): "about an 84% chance" of a hold
    # next week, i.e. 16% for a hike, and 90% for a hike in December. Other reads that
    # day span 13-16% (October) and 86-91.5% (December, fattail.ai's cumulative); the
    # dated, tool-cited pair is carried and the 16 Oct pair becomes its baseline.
    # 23 OCT (FXStreet citing the CME FedWatch Tool): a 92.8% chance of a hold next week,
    # i.e. 7.2% for a hike - Yahoo has the same 7.2% - and 80.5% for a hike by December.
    # The 22 Oct pair (16% / 90%) is its baseline; that read was before the Treasury rally.
    # 26 OCT (FXStreet citing the CME FedWatch Tool, 05:32 GMT): a 90.6% chance of a
    # hold on the 28th, i.e. 9.4% for a hike, and 79.7% for a hike in December. A
    # futures calculation on CME's method that morning had 90.0% / 10.0%, and CNBC's
    # close report "a 90% likelihood" of a hold; the tool-cited pair is carried. The
    # 23 Oct pair (7.2% / 80.5%) is its baseline. Polymarket and Kalshi (about 7% on the
    # 25th) are not the tool and are not carried.
    # 27 OCT, near the close (Kiplinger's live page citing the CME FedWatch Tool: a 92.8%
    # chance of a hold, from 90.6% earlier in the day; Forbes about 93% at 4:30pm ET):
    # 7.2% for an October hike. December reads that day run from 71% to above 80% across
    # outlets that do not say when they read the tool, so the 26 Oct 79.7% stays, dated.
    # 28 OCT, THE OCTOBER MEETING DECIDED: a hold at 3.75-4.00%, 10-2, Governor Cook and
    # Cleveland's Hammack preferring a quarter-point hike (the Fed's statement; CNBC; Fox
    # Business). The statement has inflation "elevated". It was priced: FedWatch had a
    # 92.8% hold on the eve (7.2% for a hike). The October odds fields are RETIRED with
    # the meeting, as September's were on 17 Sep - an "October odds" input surviving the
    # October decision would describe the past as pending (runbook 20); the readings
    # stay in CLAIMS. The next move is December's.
    "fed_oct_decision_date": "2026-10-28",
    "fed_oct_votes_hold": 10, "fed_oct_votes_hike": 2,
    # December, after the decision (28 Oct): "CME's FedWatch tool is currently
    # projecting an 85% likelihood" of a hike (ABC News); "85% probability" (Kiplinger);
    # Finimize 86.0% and Yahoo 84% at 1:27pm ET are other reads of the same afternoon.
    # The baseline is the tool-cited 79.7% of 26 Oct; the 27 Oct reads were untimed.
    # Carried at the sources' own precision (v81): "85%", not "85.0%" - a decimal no source
    # gave (CNBC's 85.7% is a different read of the same afternoon).
    # 29 Oct, after GDP and September PCE: 79.6% (Fox Business and IBTimes, citing the tool,
    # "down from 84.2%" the day before - another read of the 28th's afternoon than the 85%
    # carried). FXStreet's 74.9% and FXEmpire's ~83% are other hours of the same day.
    "fed_hike_odds_dec": 79.6,   # a hike by the 9 Dec meeting (FedWatch)
    "fed_hike_odds_dec_date": "2026-10-29",
    "fed_hike_odds_dec_prev": 85, "fed_hike_odds_dec_prev_date": "2026-10-28",
    # The 22 Oct evening reads (TheStreet 76%, Reuters about 80%) were recorded as a range
    # in v65 and are superseded by the 23 Oct tool read.
    # A settled reading of a DECIDED meeting. Kept for the record, and registered
    # in RESOLVED_ODDS below so prose quoting it has to say which meeting and when:
    # the US regional note said "the hike is 92.0% priced" in the present tense for
    # five days after the hike had been delivered.
    "fed_hike_odds_sep_final": 92.0,
    "fed_hike_odds_sep_date": "2026-09-16",
    "ecb_sep_delivered": 2.50,
    # SEPTEMBER PAYROLLS (BLS, 2 Oct): +29k against an 84k consensus; unemployment
    # 4.2% from 4.1%. August REVISED to +133k from +162k, July to -10k from +21k
    # (60k fewer in total). The first prints are kept, named as such.
    "us_payrolls_jul_rev2": -10_000,
    "us_ism_mfg_sep": 54.5, "us_ism_mfg_consensus": 54.9,   # 1 Oct
    # ISM SERVICES, September (5 Oct): 54.9 from 55.4, a slight miss; prices paid
    # 74.0 from 72.6, employment 50.1. Consensus is reported as 55.0 and 55.2 in
    # different places, so no consensus is carried.
    "us_ism_svc_sep": 54.9,
    # Michigan sentiment, October preliminary (9 Oct): 46.3 from 48.1 against 48.0
    # expected, near May's record low of 44.8; year-ahead inflation expectations
    # 4.7% from 4.6%, five-year 3.5% from 3.4%.
    # SEPTEMBER RETAIL SALES and PPI (15 Oct): sales +0.8% against 0.3% expected,
    # August revised to +1.3%; gas stations +6.4%, ex-gas only +0.2%. PPI final
    # demand +1.3% m/m - the largest since March 2022 - and 6.3% y/y, against about
    # 0.5% expected (sources differ, 0.5-0.6); core +0.5% m/m, 5.0% y/y; energy
    # goods +10.8% (CNBC, CNN, US News / Reuters).
    "us_retail_sep": 0.8, "us_retail_sep_consensus": 0.3, "us_retail_aug_rev": 1.3,
    "us_retail_exgas_sep": 0.2,
    "us_ppi_sep_mom": 1.3, "us_ppi_sep_yoy": 6.3, "us_ppi_core_mom": 0.5, "us_ppi_core_yoy": 5.0,
    "us_umich_oct": 46.3,
    "us_umich_record_low": 44.8,
    "us_umich_infl_1y": 4.7,
    "us_umich_infl_5y": 3.5, "us_umich_infl_5y_prev": 3.4,
    # FRANCE. The 10-year OAT-Bund spread reached about 140bp, last seen in the
    # euro debt crisis (Rothschild, UBS), with the 2026 deficit now expected at
    # 5.4% of GDP against a 5.0% target.
    "fr_oat_spread_bp": 140, "fr_deficit_2026": 5.4, "fr_deficit_target": 5.0,
    # 14 Oct: 135.5bp (OAT 4.81%, Bund 3.45%; Ideal Investisseur), as the Assembly
    # opened the budget on 13 Oct; Allianz Trade sees 120-150bp to year-end.
    "fr_oat_spread_14oct": 135.5,
    "us_unemployment": 4.2,
    # S&P Global flash PMI, September 2026 (released 23 Sep), vs the August finals.
    # The headline Manufacturing PMI, 57.0 from 53.9 (a 52-month high). The first
    # pass carried 56.7 from 53.1 under this name - that is the Manufacturing
    # OUTPUT index, a different series in the same release.
    "us_pmi_manufacturing_high_months": 52,   # "a 52-month high" (S&P Global)
    "us_5y_auction_size_bn": 70,   # weak-demand 5-year note auction, 23 Sep
    "ecb_depo": 2.50,          # HIKED 10 Sep 2026 (+25bp); MRO 2.65, MLF 2.90, effective 16 Sep
    # HELD 29 Oct (the ECB's statement; Euronews): all three rates unchanged, no commitment
    # on the path; Lagarde announced she will step down early, in February.
    "ecb_oct_decision_date": "2026-10-29",
    "ecb_depo_prev": 2.25,
    # FINAL, 17 Sep: 3.2%, revised down from the 3.3% flash of 1 Sep that this
    # model carried for three weeks. Energy 14.3% y/y, contributing +1.29pp. The
    # note's "excluding energy was 2.2%" had no input behind it - it traced only
    # because an unrelated 2.2 (SK Hynix -2.2%) sat elsewhere in the prose - and
    # is replaced by the energy contribution Eurostat actually publishes.
    # SEPTEMBER FLASH (Eurostat, 2 Oct): 3.8% against 3.6% expected, the highest
    # since 2023; energy 18.8% from 14.3%, services 3.2% from 3.0%. A flash, so it
    # is named as one until the 16 Oct final.
    "ea_hicp_sep_flash": 3.8,
    "ea_hicp_sep_final": 3.8, "ea_core_sep": 2.5,   # Eurostat, 16 Oct: final = flash "ea_hicp_sep_consensus": 3.6, "ea_energy_sep_flash": 18.8,
    "ea_hicp_aug": 3.2,
    "ea_hicp_2026": 3.0,
    "ea_hicp_2028": 2.0,
    # BANK OF JAPAN - hiked 18 Sep, and the yen FELL. This matters to the Asia
    # sleeve in the opposite direction to the obvious one: a hike that weakens the
    # currency is the market saying the cycle is nearly done, not that carry has
    # improved. Three months from the previous move against six before it, so the
    # pace quickened even as the board split.
    "boj_rate": 1.25,          # 18 Sep, +25bp - highest since 1995
    "boj_rate_prev": 1.00,
    "boj_vote_for": 7, "boj_vote_against": 2,   # Asada and Sato dissented
    "boj_gap_months": 3, "boj_gap_months_prev": 6,
    "usdjpy": 158.48,           # 14 Oct (Trading Economics)
    # HELD 30 Oct at 1.25%, 8-1, Takata for 1.5%, the board saying its 2% target is met and
    # flagging a hike as soon as December (FXStreet / ING; Maaal).
    "boj_oct_decision_date": "2026-10-30",
    "boj_oct_vote_hold": 8, "boj_oct_vote_hike": 1, "boj_oct_dissent_rate": 1.5,
    # BoJ Tankan, Q3 (1 Oct): large manufacturers +24 from +22 (25 expected), a
    # sixth straight rise and the highest in eight years, on AI-related demand.
    "jp_tankan_large_mfg": 24, "jp_tankan_large_mfg_prev": 22,
    # CHINA Q3 (NBS, 19 Oct): GDP +4.5% y/y against 4.4% expected (Reuters poll),
    # up from 4.3% in Q2, +1.2% q/q - the bottom of the 4.5-5% target. Exports did
    # the work; September retail sales rose only 1.1% and property and fixed-asset
    # investment fell (Reuters via US News, China Daily, Anadolu).
    "china_gdp_q3": 4.5, "china_gdp_q3_consensus": 4.4, "china_gdp_q2": 4.3,
    "china_retail_sep": 1.1,
    # 22 OCT, BSP DECIDED (BusinessWorld, Rappler, Tribune, astig.ph): the Monetary
    # Board raised the target RRP rate 50bp to 5.50%, its fourth straight hike and
    # the first half-point since February 2023, where 20 of 22 analysts in
    # BusinessWorld's poll had expected 25bp; the overnight deposit and lending rates
    # rose to 5.00% and 6.00%. Governor Remolona: "We're not hiking the policy rate to
    # defend the peso"; more is possible at the 17 Dec meeting. H1 GDP growth was 2.6%.
    "bsp_rrp": 5.50, "bsp_rrp_prev": 5.00, "bsp_hike_bp": 50,
    "bsp_decision_date": "2026-10-22", "bsp_next_meeting": "2026-12-17",
    "bsp_odf": 5.00, "bsp_olf": 6.00,
    "ph_gdp_h1": 2.6,
    "bsp_hikes_since_apr": 4,
    # BANK OF KOREA held its base rate at 3.00% on 22 Oct, pausing its tightening
    # (Aju Press, TradingKey).
    "bok_rate": 3.00, "bok_decision_date": "2026-10-22",
    # The headline decelerated for a fourth month, but the largest single food
    # component went the other way and hard. The peso sleeve's real-carry argument
    # rests on a FIFTH deceleration; a staple re-accelerating 2.3pp in one month is
    # the most concrete thing working against it, and the note had only the oil
    # price to point at.
    # BSP's month-ahead range for SEPTEMBER (30 Sep): 6.4-7.4%, from August's 6.1%
    # - weather-hit food, pump prices and the weaker peso. A FORECAST; the PSA
    # print is due 6 Oct, and nothing is scored on it before then.
    # PH SEPTEMBER CPI (PSA, 6 Oct): 7.2%, inside BSP's range and above a 6.7%
    # poll median - matching April's 7.2%, the three-year high. Core 4.7% from
    # 4.1%, the highest since October 2023. Food 6.7% from 4.6%, transport 14.6%
    # from 13.5%, housing and utilities 8.4% from 7.9%; the bottom 30% of
    # households saw 9.0%.
    "ph_cpi_sep": 7.2, "ph_cpi_sep_poll": 6.7, "ph_cpi_apr": 7.2,
    "ph_core_cpi_sep": 4.7,
    "ph_food_cpi_sep": 6.7,
    "ph_cpi_bottom30_sep": 9.0, "ph_cpi_bottom_hh_pct": 30,   # PSA's bottom-30% series
    "bsp_infl_2027": 5.4,
    # The peso came OFF its record and this model did not notice for five days.
    # Until 2026-09-19 it carried the 11 Sep close of 62.68 and described it as
    # "another record low"; by then 62.86 (14 Sep) was the record and the peso had
    # recovered to 62.749. Spot and the record are separate inputs now, because
    # conflating a dated record with a moving level is what produced the error:
    # the record only ever moves one way, spot does not.
    # Trade date is checked against publication date - a wire story dated the 15th
    # reports the 14th's close.
    # 21 Sep's "HELD" placeholder is now resolved: the 22 Sep figure that had been
    # missing turned up in a 23 Sep recap - the peso APPRECIATED 5.5 centavos to
    # 62.725 on the 22nd on US-Iran talk optimism (BusinessWorld), which is what
    # the discarded "62.625" should have looked like and did not - a weakening
    # claim on a session that strengthened. 23 Sep: flat, "matched its previous
    # session's close" - two independent radar.ph/Manila Times pieces agree.
    # 25 Sep: +27 centavos to 62.465 from 62.735, the first gain in two sessions
    # (radar.ph). Chains exactly: 62.735 - 0.270 = 62.465.
    # THE 24 SEP PRIOR WAS MISDATED. The last review carried 62.725 as the 23 Sep
    # close and called the 24th "a centavo weaker after a flat 23rd". BusinessWorld's
    # own sequence is 62.78 (21 Sep) -> 62.725 (22nd, +5.5 centavos) -> 62.585 (23rd,
    # a two-week high, +14 centavos) -> 62.735 (24th, -15 centavos); its 24 Sep
    # story says so in terms ("fell by 15 centavos ... from Wednesday's two-week high
    # of P62.585"). 62.725 was TUESDAY's close. The Manila Times called the 23rd
    # "flat", which is the reading the last review took; BusinessWorld and radar.ph
    # chain through all four sessions and it does not, so 62.585 is carried.
    # 28 Sep: "weakened by eight centavos to close at P62.545 ... from P62.465 on
    # Friday" (BAP data via Tribune / headtopics); 62.465 + 0.080 = 62.545.
    # 29 Sep 62.565 (+2 centavos), 30 Sep 62.64 (+7.5), 1 Oct 62.775 (+13.5, a
    # fourth straight loss), 2 Oct 62.535 (-24, "snapping its four-session losing
    # streak") - radar.ph each day; every step chains to the half-centavo.
    # 5 Oct 62.621 (+8.6 centavos, radar.ph); 6 Oct "slid by 15 centavos to end at
    # P62.771 ... from its P62.621 finish on Monday" (BusinessWorld, BAP data).
    # One 6 Oct report repeated Monday's 62.621 as Tuesday's close; BusinessWorld's
    # chain settles it.
    # 7 Oct 62.75 (Tribune, "settled at P62.750"); 8 Oct "slid by 15 centavos to
    # end at P62.90 ... a new record-low finish, eclipsing the P62.86 logged on
    # Sept. 14" (BusinessWorld, BAP data; radar.ph the same); 9 Oct 62.801
    # (radar.ph, "a 10-centavo gain" - 9.9 centavos to the tenth). BusinessWorld:
    # the 15 Sep intraday 62.925 is still the weakest the peso has traded.
    # 13 Oct 62.80; 14 Oct "7 centavos weaker" at 62.87 (BusinessWorld, BAP data;
    # radar.ph 62.870); 15 Oct 63.06, the first close past 63 and a record, after
    # an intraday low of 63.15 (Manila Bulletin, Tribune, BusinessWorld).
    # 16 Oct 62.985, a 7.5-centavo rebound, after an intraday 63.23 - the weakest
    # print on record (Manila Times, radar.ph).
    # 19 Oct 63.09, 10.5 centavos weaker and a record close, past the 63.06 of the
    # 15th, on the hot US inflation data (Tribune, radar.ph, astig.ph). 20 Oct
    # 63.09 again, unchanged - a record close for a second day - after trading
    # 62.98-63.11 (Manila Times).
    # 21 Oct 63.361, 27.1 centavos (0.43%) weaker - a record close - after an
    # intraday 63.373, the weakest print on record, on dollar strength and oil
    # (Tribune, radar.ph). 63.09 + 0.271 = 63.361.
    # 22 Oct 63.52, 15.9 centavos weaker - a record close for a fourth straight
    # session - after opening at 63.31 and trading 63.30-63.545, on the BSP's 50bp
    # hike and Gulf risk (BusinessWorld, Manila Bulletin, Manila Times).
    # 63.361 + 0.159 = 63.52.
    # 23 Oct 63.615, 9.5 centavos weaker, another record close, after opening at 63.35
    # and touching 63.62 - the weakest print on record (Manila Times; Filipino Times,
    # citing BAP data). 63.52 + 0.095 = 63.615. Remolona the same day: the hike was not
    # to defend the peso; BSP intervenes a little, to limit inflationary swings (Tribune).
    # 26 Oct 63.95, 33.5 centavos weaker, a record close, after opening at 63.535;
    # weighted average 63.859 (BusinessWorld, Philstar, Manila Bulletin, BAP data) on
    # oil and the Gulf. 63.615 + 0.335 = 63.95.
    # 27 Oct 64.17, 22 centavos weaker - the first close past 64, a record for a sixth
    # straight session - after opening at 63.95 and touching 64.20 (Rappler, BAP data;
    # the Manila Times has the range 63.90-64.20). 63.95 + 0.22 = 64.17. Remolona: BSP
    # will not defend a level and intervenes only to cushion excessive moves (Rappler).
    # 28 Oct 64.025, 14.5 centavos STRONGER, ending the run of record closes, after
    # opening at 64.08 and trading to 63.94 (Philstar; Tribune, BAP data). 64.17 - 0.145
    # = 64.025. A Manila Bulletin figure of 63.92 for the 27th (via astig.ph) is against
    # Philstar, Inquirer, Bombo Radyo and Tribune's chain, and is not carried.
    # 29 Oct 63.85, 17.5 centavos stronger, after opening at 63.88 and trading 63.80-63.91,
    # on the President's reassurance, the Fed's hold and cheaper oil (BusinessWorld, BAP
    # data; GMA; Philstar). 64.025 - 0.175 = 63.85. Friday's 63.74 is in one aggregator only.
    "usdphp": 63.85,           # 29 Oct
    "usdphp_date": "2026-10-29",
    "usdphp_prev": 64.025,     # 28 Oct close
    "usdphp_prev_date": "2026-10-28",
    "usdphp_chg": -0.175,
    "usdphp_record": 64.17,        # 27 Oct close - the weakest close on record
    "usdphp_record_date": "2026-10-27",
    "usdphp_record_prev": 63.95, "usdphp_record_prev_date": "2026-10-26",
    # The weakest print on record is the 27 Oct intraday 64.20 (Rappler; the Manila
    # Times' range tops at the same 64.2).
    "usdphp_record_intraday": 64.20,
    "usdphp_record_intraday_date": "2026-10-27",
    # 24, not 23. BusinessWorld counted 62.625 (8 Sep) as the 23rd record of 2026
    # and 62.68 (11 Sep) as the 24th; this model had the count attached to the
    # level below it from launch until 2026-09-19. It is carried as-of the 11 Sep
    # print because that is the last record published with a running YTD count.
    # 62.86 is at least one more, but no source states its ordinal and an ordinal
    # cannot be derived from a price, so it is not asserted. The 22 Oct close is
    # BusinessWorld's 35th record of the year and GMA's 30th; the two disagree, so
    # neither replaces the 11 Sep count. (26 Oct: Philstar's "37th", which chains with
    # BusinessWorld's count, still against GMA's - not carried.)
    "usdphp_records_2026": 24,
    "usdphp_sept_records": 6,      # 14 Sep was the sixth record of the month
    "usdphp_2025_close": 58.79,    # 29 Dec 2025 - the YTD base, move DERIVED below
    # 25 Sep: +95.95 (+1.67%), the first gain after a run of losses that took the
    # index to a 10-month low on the 24th. 5730.02 + 95.95 = 5825.97 exactly.
    # 28 Sep: -37.10 (-0.64%) to 5788.87 (Tribune); 5825.97 - 37.10 = 5788.87.
    # 29 Sep 5738.40 (-50.47), 30 Sep 5679.48 (-58.92), 1 Oct 5629.47 (-50.01, a
    # 2026 low), 2 Oct 5629.03 (-0.44, -0.01%), a fifth straight loss (radar.ph).
    # 5 Oct +114.18 (+2.03%) to 5743.21, snapping a five-session slide; 6 Oct
    # -66.09 (-1.15%) to 5677.12 as September inflation surprised (Inquirer).
    # 7 Oct +59.57 (+1.05%) to 5736.69 (Tribune); 8 Oct -126.30 (-2.20%) to
    # 5610.39, a new 2026 low, on the record-low peso and oil (radar.ph, Manila
    # Bulletin); 9 Oct +90.60 (+1.61%) to 5700.99 (radar.ph, InsiderPH, Yahoo).
    # 13 Oct 5701.54; 14 Oct -84.31 (-1.48%) to 5617.23 (BusinessWorld); 15 Oct
    # +45.94 (+0.82%) to 5663.17 on bargain hunting (Manila Bulletin, Inquirer).
    # 16 Oct +119.53 (+2.11%) to 5782.70 on an MSCI warning on Indonesia and lower
    # yields (Manila Bulletin; Manila Times has +119.47, which misses 5663.17).
    # 19 Oct +15.20 (+0.26%) to 5797.90, a third straight gain, after an intraday
    # 5830.19 (Tribune; one report +14.98, which misses 5782.70). 20 Oct +8.27
    # (+0.14%) to 5806.17 as investors waited on the BSP (Inquirer, Manila Times).
    # 21 Oct +15.34 (+0.26%) to 5821.51, a fifth straight gain, on foreign buying
    # (Tribune, radar.ph, BusinessWorld). A Manila Times page dated the 21st carries
    # the 20th's 5806.17.
    # 22 Oct -41.78 (-0.72%) to 5779.73, ending the five-session rally on profit-
    # taking before the BSP decision (Inquirer; Investing.com range 5743.29-5805.52).
    # 5821.51 - 41.78 = 5779.73.
    # 23 Oct: -51.10 (-0.88%) to 5728.63 (Inquirer; Bloomberg PCOMP), on the BSP's hike
    # and the weaker peso; down 54.07 (0.94%) on the week. 5779.73 - 51.10 = 5728.63.
    # 26 Oct: -87.45 (-1.53%) to 5641.18, the lowest close in almost two weeks, on the
    # BSP's hike and the peso (BusinessWorld; Trading Economics). 5728.63 - 87.45 =
    # 5641.18. The all-shares index fell 1.01% to 3161.12.
    # 27 Oct: +120.01 (+2.13%) to 5761.19, its best day since 1 Sep, on bargain hunting
    # after the 26th's fall, as the peso passed 64 (BusinessWorld; Inquirer). 5641.18 +
    # 120.01 = 5761.19. The all-shares index rose 1.67% to 3213.96.
    # 28 Oct: -107.64 (-1.87%) to 5653.55 on inflation fears, with energy costs and the
    # peso past 64 (Inquirer; Tribune). 5761.19 - 107.64 = 5653.55. Only Mining and Oil
    # rose; Services fell 2.95%.
    # 29 Oct: +52.03 (+0.92%) to 5705.58, back above 5,700 on bargain hunting as the peso
    # recovered, on thin trade (Inquirer; BusinessWorld). 5653.55 + 52.03 = 5705.58. The
    # 30 Oct close (Trading Economics 5680.35) is in one source and not carried.
    "psei": 5705.58, "psei_chg_pts": 52.03, "psei_chg_pct": 0.92,
    "psei_date": "2026-10-29",
    "psei_prev": 5653.55,
    "psei_28oct_chg_pct": -1.87,
    "psei_2026_low": 5610.39, "psei_2026_low_date": "2026-10-08",
    # PH T-BILLS, 21 Sep auction (BusinessWorld / BusinessMirror). CORRECTED
    # 2026-09-24: 5.138 / 5.517 / 5.717 had been here since the build on 2 Sep,
    # never refreshed, and since 13 Sep the look-through stamped them with the
    # page's own as-of date as "the live curve" - 22 days and ~30bp stale on every
    # tenor by the time it was caught. The rates now carry their AUCTION date, the
    # previous auction for the chain, and a bound on age against the weekly cadence.
    # 28 Sep auction (BusinessMirror, Context.ph): 5.535 (+10.4bp), 5.862 (+4.1bp),
    # 6.115 (+7.2bp) - "mostly slightly higher for the sixth straight week"; every
    # move chains off the 21 Sep rates below.
    # 5 Oct auction (BusinessMirror): 5.667 (+13.2bp), 5.971 (+10.9bp), 6.214
    # (+9.9bp) - "investors sought higher returns on inflation bet", a day before
    # the CPI print. Seventh straight weekly rise in the 364-day.
    # 12 Oct auction (BusinessWorld, BusinessMirror): 5.845 (+17.8bp), 6.171
    # (+20.0bp), 6.351 (+13.7bp), partially awarded at P39.9bn of P45bn on BSP
    # hike bets.
    # 19 Oct auction: 5.992 (+14.7bp) and 6.229 (+5.8bp) (BusinessWorld,
    # BusinessMirror, Context.ph); 364-day 6.444 (Business Recorder; +9.3bp off
    # 6.351). Partially awarded, P44.23bn of P45bn - a ninth straight weekly rise
    # and the highest since November 2023 (RCBC). Context.ph's "364-day 5.278%" is
    # the 35-day cash-management bill and is not carried.
    # 26 Oct auction, the first after BSP's 50bp hike (BusinessWorld, two pieces): 91-day
    # 6.624 (+63.2bp, full P20bn), 182-day 6.43 (+20.1bp, P11.88bn of P15bn), 364-day
    # 6.583 (+13.9bp, P5.8bn of P10bn); P47.68bn raised against a P55bn plan. ONE SOURCE,
    # but its prior-week rates are exactly the 19 Oct record below, and every move chains.
    "ph_tbill_91": 6.624, "ph_tbill_182": 6.43, "ph_tbill_364": 6.583,
    "ph_tbill_prev": [5.992, 6.229, 6.444],       # 19 Oct auction
    "ph_tbill_chg_bp": [63.2, 20.1, 13.9],        # as reported
    "ph_tbill_date": "2026-10-26",
    "ph_tbill_cadence_d": 7,                      # BTr auctions T-bills weekly
    # THE PESO BOND FUNDS WERE REMOVED 2026-10-21 (owner: "remove from the lists and
    # portfolio allocations the atram long term and medium term peso bond"). Their
    # inputs - the PH government curve that priced the Long Term Peso Bond, its fee,
    # mandate and volatility estimate - went with them.
    # ATRAM Global Dividend Feeder Fund -> Fidelity Funds - Global Dividend Fund
    # (KIID; BusinessWorld 21 Jul 2026). ATRAM's own code is ATRGLDV (its fund
    # page); the model carried a placeholder, ATRGDIV, until 2026-10-21. Target OCF
    # 1.04%, PUBLISHED by Fidelity for the Y-Acc-USD class; the class the feeder
    # holds is not published.
    # TRUST FEE 1.20 -> 1.50 (2026-10-21), PUBLISHED: ATRAM's fund page for the PHP
    # class lists "Trust Fee (incl Distribution Fee, if any) 1.50% p.a.", and
    # uitf.com.ph has 1.50% for the USD class. uitf.com.ph's PHP-class page still
    # shows 1.10%, the level before the feeder increases. The 1.20% carried since
    # the fund was added was an estimate, made when no schedule had been found.
    "gdiv_trust_fee": 1.50, "gdiv_target_ocf": 1.04, "gdiv_div_drag": 0.3,
    # JPM LTCMA global equity, 2027 edition (2026 edition: 7.0%).
    "ltcma_global_eq": 7.5, "ltcma_global_eq_prev": 7.0,
    # JPM LTCMA 2027 fixed income (press release, 19 Oct 2026): global aggregate bonds
    # 5.3%, "the highest in two decades"; US investment-grade credit 6.1%. The bond legs
    # of the two multi-asset funds are built on them (2026-10-22). No 2027 figure for
    # Asian credit was found; US investment grade stands in for it, flagged as a proxy.
    "ltcma_global_agg": 5.3, "ltcma_us_ig": 6.1,
    # THE 22-FUND LIST, SEARCHED (owner, 2026-10-22: "Update portfolio A from 22 atram
    # list"). A fund enters the universe once its fees are confirmed - its trust fee on
    # ATRAM's own page or on two current listings that agree, and its target fund named
    # with a published charge - the standard the owner set for US Equity Opportunity on
    # 2026-10-21. The rest are held out, each with what is missing, and re-checked on
    # every roll. Eleven in, eleven out.
    "list22_held_out": [
        ["US Equity Opportunity", "trust fee not confirmed: only uitf.com.ph's 1.20% listing, about 17 months old (owner's hold, 2026-10-21)"],
        ["Global Bond Income", "trust fee on one listing only (uitf.com.ph, 0.90%); target named only in a 2020 disclosure (PIMCO GIS Diversified Income), whose charge runs 0.69-1.59% by class"],
        ["Global AI", "trust fee listings disagree (1.20% and 1.50%); target fund not named in any document found"],
        ["Global Multi-Asset Income", "trust fee listings disagree (1.15%, 1.19%, 1.25%)"],
        ["Global Capital Accumulation FoF", "trust fee on one listing only (0.90%, USD class)"],
        ["Global Equity High Income", "no fee or target fund found"],
        ["Global Natural Resources", "no fee or target fund found"],
        ["Global Gold Equity", "launched 2026; target fund not named in any document found"],
        ["Global Financials", "current 1.50% trust fee on one secondary source; target and its charge last published in 2020"],
        ["US Multi-Asset Income", "trust fee on one listing only (1.50%, USD class)"],
        ["Peso Liquid", "no current fee found; the same job as the money market"],
    ],
    # THE 21 OCT REVIEW of the ATRAM list on the JPM 2027 assumptions. Its best-worst-
    # case pick (the old B, 35% in the Long Term Peso Bond) went with the bond funds;
    # what remains is the review's date, scope and search limits.
    "pd_review_date": "2026-10-21", "pd_review_n_funds": 22, "pd_review_n_scen": 6,
    "pd_review_ltcma": 2027,         # the J.P. Morgan edition the review ran on
    # The review's search, shared by both picks: at most 5 funds, at most 35% in any
    # one, at least 5% in peso cash, on the 5% grid.
    "pd_review_max_funds": 5, "pd_review_max_w": 35, "pd_review_min_cash": 5,
    # THE REVIEW'S HIGHEST-RETURN PICK, the reference A is compared with: the best
    # base-case net CAGR inside the budget, then the lowest drawdown within the tie.
    # RE-RUN 2026-10-21 WITHOUT EITHER PESO BOND FUND (owner), with the money market
    # at 0.58% and on the page's -27.17% budget (the review model had carried -27.27%,
    # a budget from before the 2027 roll), over the 11 funds the review kept after
    # screening less the two bond funds. It holds 25% Global Health Care, a fund this
    # page does not model, so A - chosen over this page's five - cannot match it.
    # 58 in the tie; worst case 6.55% (on the 2026 assumptions); -28.0% if bonds and
    # tech fall together. With the bonds it was 5 / 25 / 0 / 35 / 35 / 0 at 7.68%.
    "pa_review_date": "2026-10-21", "pa_review_cagr": 7.06, "pa_review_dd": 26.3,
    "pa_review_band_n": 58, "pa_review_worst": 6.55, "pa_review_stress_dd": 28.0,
    "pa_review_pool_n": 11,
    "pa_review_mix": [["Peso Money Market", 15], ["Nasdaq Equity Income", 35],
                      ["Global Technology", 15], ["Global Dividend", 10],
                      ["Global Health Care", 25]],
    # THE LIST (owner, 2026-10-21): 24 funds with ATRAM US Equity Opportunity and US
    # Multi-Asset Income added, then 22 with the Long Term and Medium Term Peso Bond
    # funds removed. US Equity Opportunity's weight turns on its trust fee, not
    # confirmed: uitf.com.ph lists 1.20% on a page about 17 months old, and ATRAM moved
    # its sister feeders to 1.50% on 14 Sep. It is HELD OUT at the owner's choice.
    # RE-RUN 2026-10-28 UNDER THE MAXIMUM-GROWTH RULE AT THE BAND'S 25% (v77;
    # model/heldout_sens.py: the fund built by build_fund(), its pairs from the factor
    # model, the rule re-run over the eleven funds plus it): at 1.20%, 20% of A and 20% of
    # B; at 1.50%, 15% of A and none of B. (Under the 0.05pp tie of v75-v76: 20 / 20 and
    # 0 / 0; at the derived 26.97% to v74, A / B / the since-retired C: 20 / 25 / 10 and
    # 20 / 0 / 5.)
    # GLOBAL BOND INCOME, the held-out fund that would move the picks most, the same way:
    # at its listed 0.90% trust fee with the target's institutional 0.69% charge, 35% of
    # A and 35% of B; with the retail 1.59%, 25% of A and 20% of B (v75-v76: 35 / 35 and
    # 30 / 0; at 26.97%, A / B / C: 35 / 35 / 25 and 25 / 20 / 10). Its gross is the LTCMA's investment-grade
    # credit figure - an assumption for a fund whose target is not confirmed.
    # These are RESULTS OF A RUN, so they carry the run's budget: heldout_run_cap must be
    # the live budget, or the check fails and the script must be re-run (v75: the budget
    # moved to 25% and these sat at their 26.97% values until the review caught it).
    "review_list_n": 22, "review_list_prev_n": 24, "review_list_date": "2026-10-21",
    "review_list_removed": ["Long Term Peso Bond", "Medium Term Peso Bond"],
    # Other share classes' charges quoted beside two target funds' (v83: typed in the notes
    # until now, the audit's two standing "figure without its own input" warnings).
    "ghcp_target_iacc_ter": 0.89,   # Fidelity Global Healthcare, I-Acc class
    "geo_target_at_ter": 1.95,      # Allianz Thematica, retail AT class (Citywire)
    "useq_trust_listed": 1.20, "useq_trust_peer": 1.50,
    "useq_ocf_clean": 0.85, "useq_ocf_retail": 1.81,
    "useq_w_a_listed": 20, "useq_w_b_listed": 20, "useq_w_a_peer": 15, "useq_w_b_peer": 0,
    # RE-RUN 2026-10-30 on the 30 Oct inputs (v84): every weight below came back identical.
    # Portfolio C, restored v82, re-run 2026-10-29 (heldout_sens, the same rule and budget, the
    # pin kept): US Equity Opportunity takes none of C at either fee; Global Bond Income 25% at
    # the institutional charge and none at the retail one; at the disputed 1.20% Asian Multi-Asset
    # Income fee C holds the 5% it holds at 1.50%. A's and B's re-ran to the figures carried.
    "useq_w_c_listed": 0, "useq_w_c_peer": 0, "gbi_w_c_low": 25, "gbi_w_c_high": 0, "amip_w_c_alt": 5,
    "gbi_trust_listed": 0.90, "gbi_target_low": 0.69, "gbi_target_high": 1.59,
    "gbi_w_a_low": 35, "gbi_w_b_low": 35,
    "gbi_w_a_high": 25, "gbi_w_b_high": 20,
    "heldout_run_cap": 25.0, "heldout_run_tie": 0.0, "heldout_run_date": "2026-10-30",
    # ASIAN MULTI-ASSET INCOME'S DISPUTED TRUST FEE (v75 CLAIMS; on the page from v77): ATRAM's
    # page has 1.50%, carried; the October 2025 KIID and uitf.com.ph 1.20%. Re-run 2026-10-28
    # (heldout_sens.run_refee) under the maximum-growth rule at 25%: the fund's net rises
    # 0.30pp, and A holds 35% of it (7.39% on its 10-year view), B 30% (7.18%) - against 20%
    # and none at 1.50%. Results of a run, at the run's budget and rule above.
    "amip_trust_alt": 1.20, "amip_w_a_alt": 35, "amip_w_b_alt": 30,
    # BRENT NOW CARRIES ITS OWN DATE, which it never had - the date lived in this
    # comment, so nothing could check the level's age or say a session was missing.
    # That is the same gap the 10-year had, and the 10-year's cost two days of a
    # wrong number.
    # 21 SEPTEMBER WAS WITHHELD, AND TUESDAY RESOLVED IT - AGAINST THE HEURISTIC.
    # Four Monday settles were in circulation (100.06, 100.34, 101.40, 101.5), each
    # chaining off the 18th by its own percentage. The Brent-WTI spread favoured
    # the ~101.4 / 97.86 pair, because it held Friday's 3.57; this model declined to
    # publish on one structural argument against two sources. Tuesday settled
    # Brent 99.25 (-1%) and WTI 94.59 (-1.2%), and those moves only fit a Monday of
    # 100.34 / 95.78 - the spread-favoured pair would need Tuesday falls of -2.1%
    # and -3.3%. The spread did not hold: it went 3.57 -> 4.56 -> 4.66 and STAYED
    # wide. Had the heuristic been published on Monday, it would have published the
    # wrong settle. Monday is now carried, recovered by the chain from the next day.
    # BRENT IS A DATED SERIES NOW, like the VIX and the 10-year. brent, brent_date,
    # brent_prev and brent_prev_date are DERIVED from its last two points below.
    # Until 2026-09-23 they were four typed scalars, and the page bound a HISTORICAL
    # paragraph ("Tuesday settled Brent at...") to the live ones - the next roll
    # would have printed Wednesday's settle, dated Wednesday, as Tuesday's.
    "brent_history": [
        ("2026-09-18", 103.87),  # CNBC, -0.9%
        ("2026-09-21", 100.34),  # recovered by the chain from the 22nd - see below
        ("2026-09-22", 99.25),   # -1.09%, fifth straight down session
        ("2026-09-23", 103.08),  # +3.86%, snapping the five-session losing streak
        # 24 Sep. CNBC: "gained 3.4% to close at $106.60", after a session high of
        # $108.23 when Houthi missiles were fired at Yanbu and Taif (all six were
        # intercepted). Trading Economics carried 106.39 (+3.21%) - it also chains
        # off 103.08, so the arithmetic cannot pick; the settlement report can, and
        # the TE figure is a feed snapshot, not a settle. Recorded in CLAIMS.
        ("2026-09-24", 106.60),
        # 25 Sep. CNBC: "declined 2.14% to settle at $104.32" as Iran asked the US
        # to return to the June memorandum; 106.60 x 0.9786 = 104.32. Feed quotes
        # of $105.70 (-0.85%) and $104.47 (-2.00%) were intraday. An AP line that
        # Brent "dropped below $98" matches no settle in the week and is not
        # carried.
        ("2026-09-25", 104.32),
        # 28 Sep: "gained 96 cents to close at $105.28 ... after climbing as high as
        # $108.83" on Trump's rejection of Iran's plan (Reuters via Rigzone/CNBC;
        # investingLive "settled up 0.9%"). 104.32 + 0.96 = 105.28.
        ("2026-09-28", 105.28),
        # 29 Sep: "closed down $2.69, or 2.6%, at $102.59" as Saudi Arabia restored
        # about half the East-West pipeline's flow (Reuters via Rigzone/Yahoo).
        ("2026-09-29", 102.59),
        # 30 Sep: NOVEMBER'S LAST TRADING DAY. It "expired at $103.50", +0.9%;
        # December settled +1.9% at $98.03 the same day, $5.47 below it.
        ("2026-09-30", 103.50),
        # FROM 1 OCT THE FRONT MONTH IS DECEMBER. "December Brent settled at $102.31,
        # up 4.37% or $4.28" after Chinese refiners halted fuel exports and a third
        # US carrier was reported heading to the region: 98.03 + 4.28 = 102.31. The
        # move is off DECEMBER's own 30 Sep settle, not November's expiry - see
        # brent_roll_priors.
        ("2026-10-01", 102.31),
        # 2 Oct: "settled at US$102.25, down just US$0.06, or 0.06%" (EnergyNow,
        # Reuters); Reuters' like-for-like front-month weekly change was +0.11%.
        ("2026-10-02", 102.25),
        # 5 Oct: "Brent for December settlement dipped 1.9% to settle at $100.32" as
        # Saudi Aramco cut its Asian price to a six-year low (Bloomberg).
        ("2026-10-05", 100.32),
        # 6 Oct: RECOVERED, not reported. No settlement story was found; one
        # summary gives "front-month settle 100.58", and both 7 Oct quotes measure
        # their moves from it (101.50 "+0.92"; 101.51 "+0.93"). Carried on that
        # corroboration - see brent_recovered - with no reported move.
        ("2026-10-06", 100.58),
        # 7 OCT WITHHELD: CNBC has 8 Oct "gained 4% to close at $104.28" and
        # Bloomberg "4.1%", which put 7 Oct at 100.27 / 100.17 - "closed near $100"
        # (Bloomberg) - while a daily table shows 101.90 (+1.31%), likely a
        # post-settlement print after The Atlantic's report on Iran strike options.
        # 8 Oct: $104.28 (CNBC; Bloomberg "settle above $104", the highest since
        # September) on Iran's tanker attacks and Hurricane Isaias.
        ("2026-10-08", 104.28),
        # 9 Oct: "ended at US$104.72 a barrel, gaining 44 cents, or 0.42%"
        # (Business Recorder; Yahoo the same close and move): 104.28 + 0.44.
        ("2026-10-09", 104.72),
        # 12 Oct: "rose 1.8% to $106.65" (TheStreet); 13 Oct "settled 0.90% lower
        # ... at $105.69" (FNN, Investing.com) - which also re-confirms the 12th;
        # 14 Oct "added 37 cents to close at $106.06" (CNBC, Newsquawk) after the
        # Houthi strike on Aramco's Dhahran headquarters.
        ("2026-10-12", 106.65),
        ("2026-10-13", 105.69),
        ("2026-10-14", 106.06),
        # 15 Oct: "settled down 14 cents, or 0.13%, at $105.92" (Reuters via Yahoo;
        # CNBC; Investing.com) as the US weighed easing shadow-fleet sanctions.
        # 16 Oct: "settled $3.94, or 3.7%, higher at $109.86, the highest since
        # May 19" (Reuters via Detroit News / Investing.com) on Hormuz attacks and
        # Ukraine's threat to Russian refineries. 105.92 + 3.94 = 109.86.
        ("2026-10-15", 105.92),
        ("2026-10-16", 109.86),
        # 19 Oct: "-0.3%" to $109.55 (Reuters; PFL, Investing.com), after topping
        # $110 on the Houthi claims against Saudi airports and Aramco.
        # 20 Oct: December "fell 0.7% to settle at $108.79", off a session high of
        # $111.99, a five-month high (CNBC; Pomegra has the $109.55 prior), on the
        # Qatar-Pakistan proposal. A $105.76 quote after the news is not a settle.
        ("2026-10-19", 109.55),
        ("2026-10-20", 108.79),
        # 21 Oct: December "ended the session up three cents at $108.82" (Reuters via
        # FN News; CNBC "added 3 cents to close at $108.82"; Yahoo BZ=F 108.82).
        # Investing.com's 110.15 is an intraday table value and is not carried.
        ("2026-10-21", 108.82),
        # 22 Oct: "rose $4.35, or 4.0 percent, to settle at $113.17", its highest close
        # since 4 May (Reuters via AsiaOne, Yahoo, MarineLink), as Aramco evacuated its
        # Dhahran headquarters. 108.82 + 4.35 = 113.17. One report says "since May 18";
        # most say 4 May.
        ("2026-10-22", 113.17),
        # 23 Oct: "settled at $116.72 a barrel, up $3.55, or 3.1%, the highest close since
        # April 29", +6.2% on the week, a third weekly gain (CNBC; Rio Times; BigGo), as the
        # Houthi strikes went on and a new US strike on Iran was floated. 113.17 + 3.55 =
        # 116.72. Investing.com's 111.70 is its series after rolling to January.
        ("2026-10-23", 116.72),
        # 26 Oct: "lost 91 cents to close at $115.81" after briefly topping $117, as the
        # Saudi defence minister met Iran's president in Tehran (CNBC); Reuters "down 0.8%"
        # (via Yahoo, Investing.com). 116.72 - 0.91 = 115.81. December, as on the 23rd.
        ("2026-10-26", 115.81),
        # 27 Oct: "lost 1.7% to close at $113.88" (CNBC); "drops US$1.93 a barrel" on the
        # Iran talks (The Nation). 115.81 - 1.93 = 113.88. Investing.com's 110.93 is
        # another contract. December expires on 30 Oct: the next roll crosses to January,
        # about $4.6 lower (Mitrade), and needs January's own prior.
        ("2026-10-27", 113.88),
        # 28 Oct: "Brent for December advanced 1.3% to settle at $115.32" (CNBC; Rigzone the
        # same), on the Wall Street Journal's report that the US told Gulf states to prepare for
        # strikes on Iran after the midterms. 113.88 + 1.44 = 115.32; 1.44 / 113.88 is +1.26%.
        # Still December, which expires on the 30th. Held in v79-v80 on CNBC alone.
        ("2026-10-28", 115.32),
        # 29 Oct: "fell 44 cents to close at $114.88" (CNBC), and Reuters' next-morning
        # December quote, "+$1.20 ... to $116.08" (Gulf Today), lands on the same settle.
        # 115.32 - 0.44 = 114.88. The move was reported in cents and is carried in cents
        # (brent_reported_pts), not as a percentage. Investing.com's 110.80 and
        # World Oil Monitor's 109.71 are January, which takes over as front month on 2 Nov.
        ("2026-10-29", 114.88),
    ],
    # ACROSS A ROLL the reported move is off the NEW contract's prior settle, which
    # is not in the front-month series. Carried here, dated by the session it is the
    # prior FOR, so the chain check uses the right base instead of failing or being
    # waived. (WTI's 22 Sep roll was handled by implying the prior; here a published
    # December settle exists, so it is typed and checked.)
    "brent_roll_priors": {"2026-10-01": 98.03},
    # Reuters' like-for-like front-month weekly change to 2 Oct (December vs
    # December), the honest week-on-week figure across the roll.
    # A settle with no reported move of its own, recovered from the NEXT session's
    # quotes: each [level, points change] must land on it. The 21 Sep settle was
    # recovered the same way from the 22nd's move; this makes the method a check.
    "brent_recovered": {"2026-10-06": [[101.50, 0.92], [101.51, 0.93]]},
    # EVERY SESSION'S REPORTED MOVE, like the VIX's. A single brent_chg_reported
    # field held only the latest, so the moment it rolled, the notes' historical
    # moves (+3.4% on the 24th, -2.14% on the 25th) lost their input and would have
    # traced only by coincidence. Now each is an input and each must reproduce from
    # the previous settle in the series. (2026-09-29)
    "brent_reported_moves": {"2026-09-23": 3.86, "2026-09-24": 3.4,
                             "2026-09-25": -2.14, "2026-09-28": 0.92,
                             "2026-09-29": -2.6, "2026-09-30": 0.9,
                             "2026-10-01": 4.37, "2026-10-02": -0.06,
                             "2026-10-05": -1.9, "2026-10-09": 0.42,
                             "2026-10-12": 1.8, "2026-10-13": -0.90,
                             "2026-10-14": 0.35, "2026-10-15": -0.13,
                             "2026-10-16": 3.7, "2026-10-19": -0.3,
                             "2026-10-20": -0.7, "2026-10-21": 0.03,
                             "2026-10-22": 4.0, "2026-10-23": 3.1,
                             "2026-10-26": -0.8, "2026-10-27": -1.7,
                             "2026-10-28": 1.3},
    # A MOVE REPORTED IN CENTS (v84) is carried in cents, not turned into a percentage no
    # source printed: CNBC's 29 Oct "fell 44 cents". Each must land on the settle exactly.
    "brent_reported_pts": {"2026-10-29": -0.44},
    # 28 Sep: $108.83 intraday on the rejection - ABOVE the $108.75 SETTLE high of
    # 15 Sep (verified 2026-09-29: "Brent finished up $3.07 at $108.75 ... highest
    # close since May 19"), so the settle high stands and this is an intraday one.
    # A DATED RECORD, like the moves: rolling a single field to the 28th took the
    # 24 Sep $108.23 the geopolitics note still quotes off the inputs (the audit's
    # trace caught it on 2026-09-29). The latest entry is the current session high.
    "brent_session_highs": {"2026-09-24": 108.23, "2026-09-28": 108.83,
                            "2026-10-20": 111.99},
    # 23 SEP - WITHHELD ON THE FIRST PASS, RESOLVED ON THE SECOND. Three pairs were
    # in circulation, and TWO Brent legs chained off the 22nd by their own reported
    # moves: 98.44 at -0.82% and 103.08 at +3.86%. A candidate that reproduces its
    # own percentage proves only that the arithmetic was done; it cannot pick between
    # two. What picks is DIRECTION: every post-settlement headline has oil UP and
    # "snapping a five-day losing streak" (CNBC: "rose 3.9% to close at $103.08"),
    # which 98.44 cannot be - it matches the morning reporting of a sixth down
    # session, which the settle reversed.
    # The WTI legs that "missed the 22nd by $2-5" missed nothing. The October WTI
    # contract's last trading day was 22 Sep (3 business days before the 25th), so
    # 94.59 was October's final settle and every Wednesday print was NOVEMBER. The
    # first pass chained across a contract roll, found a gap, and read it as a
    # dispute. The roll dates are now derived from the exchange rules below, and a
    # chain across a roll fails instead of passing or blocking silently.
    "brent_withheld": ["2026-10-07"],
    "brent_disputed_7oct": [100.17, 100.27, 101.90],
    "brent_disputed_23sep": [98.44, 101.61, 103.08],
    "wti_disputed_23sep": [89.31, 92.16, 92.54],
    # 27 Oct, held in v76-v77 on three prints of one source each (CNBC 99.90,
    # Macrotrends 99.82, Investing.com 100.16). RESOLVED in v78: DTN's settle report
    # repeats CNBC's 99.90 with its points (-$1.86), so it is carried below.
    "wti_disputed_27oct": [99.82, 99.90, 100.16],
    # The four Monday candidates, kept as the record of the dispute - and of the
    # heuristic that picked the wrong one.
    "brent_disputed": [100.06, 100.34, 101.40, 101.50],
    # (The recovered Monday settle is brent_prev below - one name for one number.
    # A separate "brent_21sep" with the same value was added and removed in the
    # same review: two inputs for one quantity is how ust_10y_peak and
    # ust_10y_intraday drifted apart.)
    # MOVED 2026-10-17: 16 Oct's $109.86 is the highest settle since 19 May, on the
    # December contract - past November's $108.75 of 15 Sep.
    # MOVED 2026-10-23: 22 Oct's $113.17, the highest close since 4 May, on December.
    # MOVED 2026-10-26: 23 Oct's $116.72, the highest close since 29 April, on December.
    "brent_high": 116.72,
    "brent_high_since": "29 April",
    "brent_high_prev": 113.17, "brent_high_prev_date": "2026-10-22",
    # DATED, because the page hard-typed "on 10 September" against it and was wrong
    # by five days from the moment the high moved. A dated figure whose date lives
    # only in prose is a figure whose date is not maintained.
    "brent_high_date": "2026-10-23",
    "brent_closure": 130.0,    # the Hormuz full-closure level the stress row models;
                               # published so the scenario and the notes citing it
                               # cannot drift apart
    "brent_disinflation": 65.0,  # the level the bull-case row has oil mean-revert to.
                                 # Typed in that row's prose until v62, where it "traced"
                                 # only by coinciding with a 65% four-fund weight.
    # Year-ago base. brent_yoy is DERIVED from it below rather than typed, so the
    # level and the change can never drift apart the way the quoted figures did on
    # 2026-09-10. RE-ANCHORED 2026-09-24: the base had been $65.50, implied by the
    # 4 Sep pair ($96.28 at +46.99%) and never moved since - so by the 23rd the
    # "y/y" was measured against a date 19 days off the anniversary, overstating it
    # (+57.4% instead of +54.8%). Now CNBC's verified 22 Sep 2025 settle, one day
    # off, and DATED so a check can bound the drift: a week, then re-anchor.
    # RE-ANCHORED 2026-10-03, before the week bound failed: CNBC's 5 Oct 2025 story
    # has Brent "closed up 42 cents, or 0.7%, at $64.53" on Friday 3 Oct 2025 - one
    # day off the anniversary of 2 Oct, and LIKE FOR LIKE: on both dates the front
    # month was the December contract (November 2025 also expired on 30 Sep).
    # RE-ANCHORED 2026-10-10 to the exact anniversary: on 9 Oct 2025 "the December
    # Brent contract ended the session down $1.03 at $65.22" (Sprague; Reuters
    # "settling 1.6% lower") on the Gaza ceasefire - December then as now.
    # RE-ANCHORED 2026-10-15: on 15 Oct 2025 December Brent "fell 0.77% to settle
    # at $61.91", down 48 cents and $1.41 over two sessions (Dow Jones Data Talk),
    # which puts 14 Oct 2025 at $62.39 and 13 Oct at $63.32 - December then as now.
    # RE-ANCHORED 2026-10-17 to 15 Oct 2025, the settle Dow Jones reports directly
    # ($61.91, -0.77%), one day off the anniversary of 16 Oct.
    # AT ITS BOUND on 2026-10-23: against the 22 Oct settle it is seven days off. DTN
    # has 23 Oct 2025 at $65.97, +$3.38, which puts 22 Oct 2025 at $62.59 - one source,
    # by subtraction. The next roll must re-anchor or fail the week bound.
    # RE-ANCHORED 2026-10-26 to the EXACT anniversary, and the bound TIGHTENED to three
    # days. On 23 Oct 2025 Brent "rose $3.40, or 5.4%, to settle at $65.99" on the US
    # sanctions on Rosneft and Lukoil (Reuters via Yahoo, the Globe and Mail); DTN has
    # $65.97 and MEES $65.85, but MEES's own 22 Oct $62.59 plus Reuters' $3.40 is $65.99.
    # AT ITS BOUND on 2026-10-27: against the 26 Oct settle it is three days off (26 Oct
    # 2025 was a Sunday). 24 Oct 2025's $65.94 has one source (newsonair) and is not
    # carried; it would move the y/y by 0.1pp. The next roll must re-anchor to 27 Oct
    # 2025 or fail the bound.
    # RE-ANCHORED 2026-10-28 to the EXACT anniversary of the 27 Oct settle: on 27 Oct 2025
    # December Brent "settled down 32 cents at $65.62" as OPEC+ output plans outweighed
    # US-China trade hopes (Sprague Energy; Reuters via Investing.com / Oil and Gas 360).
    # 65.94 - 0.32 = 65.62, which also chains the single-source 24 Oct. EIA's spot 65.52
    # is a different basis.
    # The week bound let v67 compare 22 Oct 2026 with 15 Oct 2025 ($61.91) when 22 Oct
    # 2025 was $62.59: +82.8% y/y published against +80.8% on the anniversary. A base
    # one week off is fine for a slow series and wrong for one that moved 5.4% in a day.
    "brent_yr_ago": 65.62,
    "brent_yr_ago_date": "2025-10-27",
    "brent_yr_ago_disputed": [65.52, 65.62],   # EIA spot against the futures settle
    # HORMUZ. Two different things get measured here and they do not agree, so both
    # are carried. VESSEL COUNTS differ ~5x across sources because they count
    # different things; OIL VOLUME is what actually reaches this portfolio, through
    # the Brent price. Until 2026-09-12 this model published only the vessel count
    # and called it a "~93% shutdown", which described a supply collapse its own
    # Brent input contradicted.
    # PortWatch publishes WEEKLY, on Tuesdays, so this reading is structurally a
    # few days behind and carrying it undated let it go fourteen days stale: 6 was
    # the 6 September count and was still here on the 19th. Both the reading and
    # its date are inputs now, and a check bounds the gap.
    "hormuz_transits": 4,          # IMF PortWatch, all transits (2 on 11 Oct, 4 on 4 Oct)
    "hormuz_transits_date": "2026-10-18",   # latest published day, 20 Oct (Straits Daily Brief)
    "hormuz_transits_cadence_d": 7,   # weekly Tuesday publication
    "hormuz_baseline": 85,         # pre-crisis transits/day, SAME PortWatch basis
                                   # (measured 28 Feb 2025 - 27 Feb 2026)
    "hormuz_lloyds": 14,           # Lloyd's List Intelligence, 17-23 Aug
    "hormuz_lloyds_asof": "2026-08-23",  # dated: the note quoted it undated for a month
    "hormuz_lloyds_dwt": 10000,    # Lloyd's counts only cargo vessels above this
    "hormuz_us_claim": 30,         # US government claim; basis undisclosed
    # Goldman's OWN pair, kept together. Mixing their 15.5 with a 20.0 baseline taken
    # from a different (Hormuz-transit-only) source gave a 22% loss, which flatly
    # contradicts Goldman's own "two-thirds of pre-war" headline. Their note says
    # exports are 15-16 mb/d and "still 7 to 8 mb/d below pre-conflict", so their
    # baseline is ~23, and 15.5/23.0 = 67% - two-thirds, as stated. Two measures of
    # the same strait are not interchangeable just because both are in mb/d.
    "hormuz_flow_now": 15.5,       # mb/d Gulf crude+products, Goldman 28 Aug (15-16)
    "hormuz_flow_gap": 7.5,        # mb/d still below pre-conflict, Goldman (7-8)
    "hormuz_flow_prewar": 23.0,    # mb/d, = 15.5 + 7.5, Goldman's implied baseline
    "hormuz_flow_trough": 5.5,     # mb/d, March trough (5-6)
    # The flow reading's OWN date. It matters more than usual now: Goldman's
    # two-thirds was measured on 28 August, and on 11 September drone strikes
    # launched from Iraq hit Saudi Arabia's East-West (Petroline) pipeline, which
    # Riyadh then shut. That pipeline was carrying roughly 5 mb/d to the Red Sea
    # port of Yanbu specifically to BYPASS Hormuz - so a material part of the
    # recovery Goldman measured has since been taken out, and the 15.5 figure is
    # stale in a knowable direction. No post-shutdown flow number has been
    # published, so none is invented here.
    "hormuz_flow_asof": "2026-08-28",
    # GOLDMAN'S OWN SERIES, RE-READ (29-30 Sep, Bloomberg/gCaptain): Persian Gulf oil
    # exports, dark flows included, "recovered to 23.3 mb/d over the last week, a
    # level in line with the 2025 average" - against the 23.0 pre-war baseline their
    # 28 Aug note implied. JPMorgan, separately: Middle East CRUDE exports 17.5 mb/d,
    # 98% of pre-war, but PRODUCTS only 58%. Carried as their own fields; the 28 Aug
    # pair above is the prior reading and stays as the record.
    "me_crude_jpm_pct": 98,
    "petroline_bypass": 5.0,       # mb/d rerouted via the pipeline before the strike
    "petroline_capacity": 7.0,     # mb/d design capacity after expansion
    "petroline_km": 1200,          # east-west across the peninsula to Yanbu
    # The STRIKE and the SHUTDOWN are different days and the model's notes had been
    # conflating them. Accounts also disagree on the strike: one dates the pumping
    # station hit 10 Sep, another says "last Thursday" (the 11th) from a 18 Sep
    # story. The shutdown is corroborated; the strike date is recorded as disputed
    # rather than silently picked, because nothing downstream depends on it.
    "petroline_struck": "2026-09-10",
    "petroline_struck_disputed": True,
    # REPAIR, which the model had no view of at all - so "still shut" was carrying
    # an implied permanence the reporting does not support. Aramco is bypassing the
    # damaged section, targeting half capacity within days and full in about six
    # weeks (16 Sep); regional officials cited by AP on 18 Sep put repairs at three
    # to five weeks with only partial flows during the work. Both are INTENTIONS
    # and ESTIMATES, not deliveries: no Saudi crude had left Yanbu since 11 Sep.
    "petroline_repair_wk_lo": 3, "petroline_repair_wk_hi": 5,
    "petroline_full_wk": 6,
    "petroline_target_pct": 50,
    # Kpler's independent read, and a check on the 5.0 carried above: it puts the
    # Yanbu export loss at 2.5-2.7 mb/d, which is about half of 5.0 - consistent
    # with a line running at the ~50% Aramco is targeting.
    "yanbu_loss_lo": 2.5, "yanbu_loss_hi": 2.7,
    "yanbu_stocks_mb": 15,         # below this by 18 Sep
    # RESTARTED 22 Sep (three sources briefed on it, via Reuters). Running "well
    # below normal throughput": a couple of days to reach 40%, and six to eight
    # weeks to full - a longer tail than Aramco's own six-week target of the 16th.
    # One cargo was scheduled to load at Yanbu that day, for China. These are the
    # first DELIVERIES rather than intentions: the pipe is moving oil again.
    # The same report dates the shutdown 13 Sep; 11 Sep is carried because it is
    # the contemporaneous report and matches Yanbu going dry that day. Recorded,
    # not resolved by picking.
    "petroline_restart": "2026-09-22",
    "petroline_restart_pct": 40,   # within "a couple of days" of restart
    "petroline_full_wk_lo": 6, "petroline_full_wk_hi": 8,
    "yanbu_first_cargo": "2026-09-22",
    "yanbu_buffer_d_lo": 4, "yanbu_buffer_d_hi": 7,
    "hormuz_dark": 5.0,            # mb/d moving via dark crossings / STS transfers
    # SAUDI CRUDE EXPORTS, the newest VOLUME reading (2026-09-26). Two trackers,
    # one direction: Bloomberg tanker-tracking has September heading for 5.28
    # mb/d, Kpler (via CNBC, 25 Sep) 6.0 - both the highest since the war began,
    # rerouted through Hormuz on the US-escorted channel off Oman. August was 3.1
    # (Kpler, via AzerTac) to 3.4 (CNBC). The growth note had carried "Saudi
    # output is still down ~1.9 mb/d" - August's PRODUCTION drop (6.2 mb/d, -23%
    # m/m), undated and in the present tense a month on; its 1.9 traced only to an
    # unrelated Japanese CPI figure.
    # 28 Sep (Reuters, Kpler): Saudi on track for ~5.4 mb/d in September - inside
    # the range - but AUGUST at 2.446 mb/d, below the 3.1-3.4 carried; the August
    # range is widened to the sources rather than one picked.
    "saudi_exports_sep_hi": 6.0,
    "saudi_exports_aug_lo": 2.4, "saudi_exports_aug_hi": 3.4,
    # THE REGION'S VOLUME, the newest and broadest reading (Reuters/Kpler, 27-28
    # Sep): Saudi, UAE, Iraq, Oman, Qatar, Kuwait and Iran together exported 12.8
    # mb/d in September, the most since the war began, against 18.8 in February;
    # exports via Hormuz ~7.4 mb/d. And the pipeline: exports via the East-West
    # line resumed on 28 Sep at ~3.5 mb/d (Bloomberg), half its 7.0 capacity.
    "me_exports_feb": 18.8,
    "petroline_flow_28sep": 3.5,
    # MONDAY 28 SEP, INTRADAY ONLY - after Washington rejected Iran's seven-day
    # plan on the 26th, Brent traded higher, but the snapshots disagree (+1.74% to
    # $106.14 in one, +4% to ~$108.48 in another) and neither is a settle. So no
    # level or move from Monday is quoted or carried: the note says only that
    # Brent traded higher. See CLAIMS.
    # THE WEEK'S ESCALATION, as facts: Rubio told Iran's UN delegation on Monday
    # 28 Sep to leave New York (it flew to Doha early on the 29th; Iran says it left
    # on schedule); a tanker was hit by an "unknown projectile" in the Strait on
    # 2 Oct (UKMTO: small fire, blackout, no casualties), after strikes on 29 Sep and
    # 1 Oct; a third US carrier group was reported heading to the region (WSJ,
    # 1 Oct). And the other side: Washington sent a counter-proposal through Qatar,
    # which Araghchi put to Iran's cabinet.
    "tanker_struck_date": "2026-10-02",
    # CHINA halted gasoline, diesel and jet fuel exports beyond Hong Kong and Macau
    # "until further notice" (1 Oct) - a PRODUCTS shock for Asian importers, the
    # Philippines among them, separate from crude volume.
    "china_fuel_export_halt_date": "2026-10-01",
    # US SPR: DOE offered the LAST 40 million barrels of the 172m-barrel release
    # (bids due 6 Oct; exchange, not sale), leaving the reserve under 284 million
    # barrels, the lowest since 1982.
    "spr_final_tranche_mb": 40,
    # 5-6 OCT. Saudi Aramco cut November Arab Light to Asia to $5 BELOW the
    # regional benchmark, from $2 below - a six-year low, where traders expected a
    # rise: producers racing for market share as Hormuz flows return. The energy
    # minister put East-West pipeline flows at 5.8 mb/d (6 Oct), from ~3.5 on
    # 28 Sep. The G7 plans a 100-million-barrel crude-and-diesel release. And
    # against all of it: UKMTO logged nine attacks in the Strait in October by
    # the 6th - half September's whole-month total - and on 5 Oct the IRGC
    # turned a tanker back off Khasab under threat of attack. Qatar is working
    # with China to restart talks; Iran's president called talks with the US
    # "meaningless".
    "saudi_osp_asia_nov": -5.0, "saudi_osp_asia_oct": -2.0,
    "ukmto_attacks_oct": 9, "ukmto_attacks_sep": 18,
    # 7-9 OCT. Reuters counted at least 12 tankers attacked between 28 Sep and
    # 5 Oct, the most intense week of the war; a chemical tanker was hit off Qatar
    # on 7 Oct with crew casualties (UKMTO), and another struck and set on fire
    # east of Fujairah on 8 Oct. Hurricane Isaias shut in more than 70% of US Gulf
    # crude output by 9 Oct. The President said on 8 Oct the US would not strike
    # Iran before the 3 Nov midterms, after The Atlantic reported the White House
    # had asked for strike options; on 9 Oct he called talks "productive". China
    # resumed refined-fuel exports after its Golden Week halt.
    "tankers_attacked_week": 12, "tankers_attacked_week_end": "2026-10-05",
    # 12-15 OCT. The Singapore-flagged container ship GFS Pride sank after a
    # projectile strike on 13 Oct (crew of 21 evacuated); GFS Giselle was hit on
    # the 14th. Reuters: more than 20 vessels, mostly tankers, attacked in October
    # by the 14th. Houthi missiles hit Saudi Aramco's Dhahran headquarters on the
    # night of 13 Oct. Kpler: crude through Hormuz 8.5 mb/d in the week to 12 Oct,
    # nearly 40% below pre-war. IEA (10 Oct): Hormuz flows rose 3.7 mb/d to 10.9
    # mb/d in September. Iran called the US reply to its ceasefire plan
    # "insufficient" (11 Oct).
    "vessels_attacked_oct_min": 20, "vessels_attacked_oct_date": "2026-10-14",
    "container_ship_sunk_date": "2026-10-13",
    "aramco_hq_struck_date": "2026-10-13",
    # 16 Oct (CNBC citing Kpler): Hormuz shipments 9.4 mb/d in the week to Wednesday
    # 14 Oct, "about 70% of the average before the Iran war"; Middle East shipments
    # including the bypass pipelines ~14 mb/d, nearly 20% below. Up from 8.5 mb/d
    # (week to 12 Oct, "nearly 40% below"). A "68% cut" in one weekly review could
    # not be traced to any source and is not carried.
    # 21 Oct (Kpler via Bloomberg, Seeking Alpha / TradingView, The National, WSJ):
    # in the week to 18 Oct, oil through Hormuz INCLUDING Gulf of Oman transfers was
    # about 14 mb/d, 82% of pre-war (preliminary); the Gulf's exports by every route
    # were above 24 mb/d against 23.3 pre-war. Bloomberg: the October-to-date average
    # is still below pre-war. NOT like-for-like with the 9.4 mb/d crude-only reading
    # of the week to 14 Oct, which is kept as the previous point, not a trend.
    "hormuz_crude_kpler": 14, "hormuz_crude_kpler_week": "2026-10-18",
    "hormuz_crude_kpler_prev": 9.4, "hormuz_crude_kpler_prev_week": "2026-10-14",
    "gulf_exports_kpler": 24, "gulf_exports_prewar": 23.3,
    # 16-17 Oct: two tankers attacked 68-78 nm northeast of Al Jubayl, Saudi
    # Arabia (UKMTO; one by an RPG from a small boat); the IRGC says the Strait is
    # "closed" and a supertanker hit a mine, CENTCOM that traffic continues. Iran
    # sent a seven-day reopening plan via Qatar. The US is weighing easing
    # sanctions on "shadow fleet" tankers to cut freight costs (Reuters, 15 Oct).
    "jubayl_attacks_date": "2026-10-16",
    # 17-20 OCT. The IRGC says a supertanker carrying more than 2m barrels hit a
    # naval mine south of the Strait and exploded (17 Oct; vessel unnamed, nothing
    # independent). On 19 Oct the Houthis claimed strikes on Riyadh and Abha
    # airports, Aramco at Yanbu, Shaybah and Saudi naval forces - unconfirmed by
    # Riyadh - and Saudi Arabia postponed next week's investment conference. Kpler:
    # at least 18 vessels fired on in two weeks (CNBC, 20 Oct). On 20 Oct Qatar and
    # Pakistan put a compromise to both sides (Al-Araby; Israel's Channel 12 says
    # the US approved and Iran gave preliminary consent); a diplomat told Bloomberg
    # a deal is not close. Lavrov was in Tehran on the 19th. The US waived the new
    # Russia sanctions and tariffs on 16 Oct for a 60-day review.
    "tanker_mine_claim_date": "2026-10-17",
    "houthi_saudi_claims_date": "2026-10-19",
    "vessels_fired_on_2wk": 18,
    "us_iran_proposal_date": "2026-10-20",
    # 21 Oct: Iran's speaker Ghalibaf said Tehran would not trust Washington until
    # its conditions for reopening the Strait were met; CENTCOM called the IRGC's
    # mine claims false. Brent rose about 1.5% in Asian trading (CNBC, AA).
    "us_iran_stall_date": "2026-10-21",
    # 22 Oct: the US ordered non-emergency diplomats and families out of Saudi Arabia
    # after Houthi strikes - an attack on King Fahd International Airport in Dammam
    # killed one and injured eight, and a drone on an Aramco-run field killed two
    # (Reuters via NewsNation, ThePrint, Haaretz). The New York Times reports US and
    # Israeli plans for renewed strikes on Iran after the midterms (CNBC); indirect
    # talks continue.
    # UPDATED 2026-10-23: the Saudi civil aviation authority raised the airport toll
    # to two dead, eight injured; the energy ministry has two contractors, a Filipino
    # and a Nepali, killed by drone debris at the Shaybah field - four dead and ten
    # injured in all (Arab News; Dawn). Aramco then ordered the first full evacuation
    # of its Dhahran headquarters since fighting resumed in July (Reuters via Detroit
    # News, Business Recorder). The 22 Oct Asian-session Brent move (+1.7%) is gone
    # from the notes now that the day's settle is carried, and from the inputs.
    "us_saudi_departure_date": "2026-10-22",
    "dammam_attack_dead": 2, "dammam_attack_injured": 8, "aramco_field_dead": 2,
    "iea_hormuz_sep": 10.9, "iea_hormuz_sep_chg": 3.7,
    # BusinessWorld poll (20 Oct, "Inflation risks to keep BSP hawkish"): 20 of 22
    # analysts expect +25bp to 5.25% on 22 Oct, the other two +50bp.
    "bsp_poll_hike": 20, "bsp_poll_n": 22,
    "hormuz_kpler_pct_of_prewar": 82,       # Kpler's own figure, week to 18 Oct
    "hormuz_crude_kpler_below_pct": 18,     # = 100 - 82, the loss the page quotes
    "isaias_gulf_shutin_pct": 70,
    # THE QUEUE, on a stated basis and as a SERIES. 436 was a 30 August reading on
    # an undisclosed basis and sat here for three weeks. These three are one
    # source, one methodology, one daily snapshot time: AIS-visible vessels holding
    # position away from berth in the Hormuz and Gulf watch box, excluding ships
    # within 25 km of a working port. Three points, because two would have let this
    # note call 369 -> 357 a drawdown; 376 the next day says it is oscillating.
    # EXTENDED 2026-09-26 from the same brief: 401 (21st), 443 (22nd), 407 (25th),
    # 422 (26th). "One daily snapshot time" above was NOT true: the briefs stamp
    # their counts at different hours (11:49 UTC on the 21st, 02:49 UTC on the
    # 25th), so these are intraday snapshots and only the RANGE carries meaning.
    "hormuz_queue": [("2026-09-18", 369), ("2026-09-19", 357), ("2026-09-20", 376),
                     ("2026-09-21", 401), ("2026-09-22", 443), ("2026-09-25", 407),
                     ("2026-09-26", 422), ("2026-09-27", 262), ("2026-09-28", 233),
                     ("2026-10-02", 147), ("2026-10-06", 242),
                     ("2026-10-07", 206)],   # 02:50 UTC each
    # That reading is now OUT OF DATE and was carried too long: through 2026-09-18
    # this comment still said the VIX had "fallen BACK toward the 2026 low", which
    # widened the gap to the futures curve. It did the opposite. Spot ran to 17.20
    # on 15 Sep and settled 15.44 on the 18th, so realised volatility has spent a
    # fortnight CLOSING the gap to the strip from below.
    # 5 Sep 2026 was a SATURDAY. One aggregator reported a "5 Sep close of 14.53";
    # there is no such close, and it was discarded. Friday 4 Sep is the last print
    # that belongs to the curve's quote date.
    # THE CURVE'S t=0. This is the spot that belongs to VIX_QUOTE_DATE, and it must
    # stay paired with the futures strip below: the bootstrap integrates forward
    # variance from spot through the strip, so a spot from one date and a strip
    # from another is not a term structure, it is two half-curves glued together.
    # RE-QUOTED 2026-10-03, the day before the 4 Sep strip hit its 30-day stop: the
    # curve is now the 2 Oct close, so its spot is 2 Oct's 15.31 - the same number
    # as the latest close, legitimately, because the strip and the spot are one
    # market close again. The check that guarded against silent replacement now
    # tests the stronger thing: the curve's spot is the close ON its quote date.
    # RE-QUOTED 2026-10-10 to the 5 Oct settlements - see vix_futs_levels.
    # RE-QUOTED 2026-10-21 to the 20 Oct settlements - see vix_futs_levels.
    "vix_spot": 17.31,         # 20 Oct close (Tuesday) - the curve's own spot
    # AN INDEPENDENT READ ON THE SAME SHAPE. VIX3M is a market-published constant-
    # maturity 3-month implied vol - it is not an input to the bootstrap, so the
    # ratio it implies is a free test of whether the forward-variance integration
    # produces a term structure the market would recognise. Both legs are from one
    # source on one date, and the published IVTS reproduces from them exactly
    # (15.84 / 18.60 = 0.8516), which is why the pair is trusted.
    # RE-READ 2026-10-03: VIX3M 18.58, published with a VIX3M/VIX ratio of 1.13 -
    # which reproduces from 18.58 / 16.39, the 1 OCT close, not from 2 Oct's 15.31.
    # The pair is trusted on the same test as the 11 Sep one (18.60 / 15.84, kept
    # in CLAIMS): its published ratio reproduces from its own two legs. So it is
    # dated 1 Oct, the date its spot belongs to.
    # RE-READ 2026-10-10: FRED's VXVCLS has VIX3M 17.72 on 7 Oct, with the VIX at
    # 15.08 that day. An observation AFTER the strip's quote date, which the old
    # pair was not: 18.58 / 16.39 was 1 Oct, a day BEFORE the 2 Oct strip, and a
    # check cannot test a curve against a market it predates.
    # RE-READ 2026-10-17: thetrading.tools has VIX3M 18.49 with the VIX at 16.46 on
    # 15 Oct (ratio 0.8902, day 133 of contango). Cboe's 15 Oct settlements carry
    # the October future at 17.42, against the strip's 17.46 - the front of the
    # 5 Oct strip still held on the 15th. None found for 16 Oct.
    # RE-READ 2026-10-20: FRED's VXVCLS has VIX3M 19.60 on 19 Oct, with the VIX at
    # 18.44 - the 5 Oct strip read -7.19% against it.
    # RE-READ 2026-10-21: thetrading.tools has VIX3M 18.99 with the VIX at 17.31 at
    # the 20 Oct close (IVTS 0.9115 = 17.31 / 18.99) - the same close as the
    # re-quoted strip below.
    "vix3m": 18.99, "vix3m_spot": 17.31, "vix3m_date": "2026-10-20",
    # SPOT HISTORY, newest last. This replaced a sprawl of one-off fields -
    # vix_latest / vix_next_close / vix_prev_close / vix_prev / vix_spike - that had
    # grown around a single two-day episode and did not generalise: adding the
    # 14-15 Sep closes would have needed another pair of them. One list, everything
    # else derived from it. Each close is a CONFIRMED session close; the chain is
    # self-checking because each day's percentage move must reproduce the next
    # day's level. (Refactor 2026-09-16.)
    "vix_history": [
        ("2026-09-02", 16.34),   # Hormuz spike close
        ("2026-09-03", 15.20),
        ("2026-09-04", 14.32),   # the curve's quote date
        ("2026-09-09", 16.46),
        ("2026-09-10", 17.84),   # broke a 28-session 14-17 range
        ("2026-09-11", 15.84),
        # 14 Sep is solid: 15.84 x 1.0795 = 17.10, and the session after Friday the
        # 11th is Monday the 14th. One outlet dated that same +7.95% move to the
        # 15th; the arithmetic chain off a confirmed close settles it.
        ("2026-09-14", 17.10),   # +7.95%
        # 15 and 16 Sep were WITHHELD on 2026-09-16 because the figures reported for
        # the 15th - "16.93, down 0.27 or -1.57%" - could not chain off a 17.10
        # prior. They were real; they were mis-dated. Those figures belong to the
        # 16th, and the missing link is a 17.20 close on the 15th, against which
        # -0.27 and -1.57% both reconcile exactly. The chain discipline held: the
        # numbers were not published until they could be made to add up.
        ("2026-09-15", 17.20),
        # 16 SEP ONWARD WAS MISDATED, AND IT CHANGED THE STORY. Corrected 2026-09-25.
        # 16.93 ("-0.27, -1.57%") was a PRE-DECISION intraday quote, not the close:
        # the index "rose 3% to 17.71" on Fed day. From the 17th every close had been
        # filed one session late - 15.44 under the 18th, 14.81 under the 21st, 14.87
        # under the 22nd, 14.21 under the 23rd - which is why the two 17 Sep
        # descriptors ("nearly 13%", "-12.8%") "did not reconcile": both are the
        # 17th's move off 17.71, and they reproduce it exactly. On the right dates
        # EVERY reported move chains off the previous close:
        #   17.20 x 1.0297 = 17.71   (16th, "rose 3%")
        #   17.71 x 0.8718 = 15.44   (17th, "-12.8%")
        #   15.44 x 0.9592 = 14.81   (18th, "-4.08%"; ALFRED/VIXCLS has 14.81 on the 18th)
        #   14.81 x 1.0041 = 14.87   (21st, "+0.41%")
        #   14.87 x 0.9556 = 14.21   (22nd, "-4.44%", a 21-session low)
        #   14.21 x 1.0683 = 15.18   (23rd, "rose 7%")
        #   15.18 + 0.49   = 15.67   (24th, "+0.49, +3.23%")
        # The page's "VIX fell on the day yields jumped" was the misdating talking:
        # on 23 Sep the VIX ROSE 6.8% with the 10-year's jump, the ordinary pairing.
        ("2026-09-16", 17.71),   # +2.97%, Fed day
        ("2026-09-17", 15.44),   # -12.82%, post-Fed relief rally (one report: 15.42)
        ("2026-09-18", 14.81),   # -4.08%, triple witching
        ("2026-09-21", 14.87),   # +0.41%
        ("2026-09-22", 14.21),   # -4.44%, a 21-session low
        ("2026-09-23", 15.18),   # +6.83%, with the 10-year's biggest jump since April 2025
        ("2026-09-24", 15.67),   # +3.23%
        # CORRECTED 2026-09-28 from 14.85 / -5.24%, which came from ONE unattributed
        # search summary and was published in v41. Three sources give 14.87,
        # "-0.80, -5.11%", day range 14.68-15.94 (Portfolio Terminal, PC Thematic,
        # Zacks): 15.67 - 0.80 = 14.87. Both pairs reproduce from 15.67, so the
        # chain check could not pick; the count and the points descriptor did.
        ("2026-09-25", 14.87),   # -0.80 / -5.11%
        # 28 SEP RESOLVED 2026-10-03, by the NEXT session: Zacks' 29 Sep recap has the
        # index "up 8.1% to 16.07", and Tuesday's "down 0.2% to 16.04" chains off 16.07
        # (16.07 x 0.998 = 16.04) but not off the rival 16.30, from which 16.04 would
        # be -1.6%. Two sources plus the chain, against one.
        ("2026-09-28", 16.07),   # +1.20 / +8.07%
        ("2026-09-29", 16.04),   # -0.2% (Zacks)
        ("2026-09-30", 16.34),   # +1.9% (Zacks); thetrading.tools 16.3
        ("2026-10-01", 16.39),   # +0.3% (Zacks)
        # 2 Oct: "down 6.59% (-1.08)" to 15.31 - 16.39 - 1.08 = 15.31. A substack
        # brief printed -6.53%, which does not reproduce from 16.39 and is not carried.
        ("2026-10-02", 15.31),
        ("2026-10-05", 15.52),   # +1.4% (Zacks)
        ("2026-10-06", 15.01),   # -0.51 / -3.29% (Zacks)
        ("2026-10-07", 15.08),   # +0.47% (Investing.com historical)
        ("2026-10-08", 15.41),   # +2.19% (Investing.com; StreetStats 15.41 from 15.08)
        # 9 Oct: "14.84, down 0.57 (-3.70%)" (Cboe, Yahoo, Investing.com). Vista's
        # weekly recap had 14.82 / -0.59 off the same 15.41; three sources to one.
        ("2026-10-09", 14.84),
        ("2026-10-12", 15.21),   # +2.49% (FRED VIXCLS, Investing.com)
        ("2026-10-13", 15.27),   # FRED VIXCLS; +0.39% derived from the two closes
        ("2026-10-14", 16.87),   # +1.60 / +10.48% on the CPI (Yahoo, Investing.com)
        ("2026-10-15", 16.46),   # FRED VIXCLS, thetrading.tools; -2.43% derived
        # 16 Oct: "+3.53 (+21.45%)" to 19.99 (Investing.com, Yahoo), intraday 22.31,
        # above 22 for the first time in four months (CNBC) on the AI sell-off.
        ("2026-10-16", 19.99),
        # 19 Oct: 18.44, -7.75%, range 17.39-18.93 (Investing.com historical,
        # Bloomberg 4:15pm; The Daily Macro Brief). A 17.72 "-2.27" print was
        # intraday.
        ("2026-10-19", 18.44),
        # 20 Oct RESOLVED 2026-10-21: 17.31, -6.13% (CappNotes' Closing Look, PC
        # Thematic, Cboe's own spot 17.31). 18.44 x (1 - 0.0613) = 17.31. The single
        # market summary's 17.60 was WRONG - withholding it was right.
        ("2026-10-20", 17.31),
        # 21 Oct 16.68, -0.63 (-3.64%) (Bloomberg VIX:IND at 4:15pm; Yahoo; PC
        # Thematic). Cboe's page shows 16.68 with a 0.00% change field, a display slip.
        ("2026-10-21", 16.68),
        # 22 Oct 19.03, +2.35 (+14.09%) (Cboe's own page; Yahoo, stamped 4:31pm;
        # Volatility Therapy). 16.68 + 2.35 = 19.03. Investing.com's 18.84 is not
        # carried: the same table has the 10-year at 5.065% on a day every other source
        # has it near 4.96%. Intraday high 20.30 (Investrade).
        ("2026-10-22", 19.03),
        # 23 Oct 19.45, +0.42 (+2.21%) (Yahoo, stamped 3:15pm CDT; Investing.com: open
        # 19.18, range 18.87-20.66; Saxo). 19.03 + 0.42 = 19.45. A Nordfx line with 19.0
        # (+14%) is the 22nd's move.
        ("2026-10-23", 19.45),
        # 26 Oct 18.39, -1.06 (-5.45%) (Yahoo's history, open 19.66, range 17.79-19.84;
        # Investing.com; Cboe's own spot 18.39). 19.45 - 1.06 = 18.39. AD HOC News' 18.30
        # (-5.9%) is the one outlier and is not carried; the v72 pass withheld this
        # close the same evening, when the figures still ran from 18.2 to 19.5.
        ("2026-10-26", 18.39),
        # 27 Oct 17.52, -0.87 (-4.7%) (Cboe's own spot 17.52; AD HOC News, the same close
        # and prior). 18.39 - 0.87 = 17.52. Doug's Daily Diary has 17.51 (-4.79%), a cent
        # apart, and is kept as disputed, not carried.
        ("2026-10-27", 17.52),
        # 28 Oct 16.91, -0.61 (-3.48%), after the Fed held (Cboe's own spot; Yahoo Finance's
        # close; CNBC, prior 17.52; PC Thematic "cooled to 16.91, from 17.52"). 17.52 - 0.61 =
        # 16.91. One recap's 16.83 is not carried; Investing.com's 17.32 and Bloomberg's 17.41
        # are intraday snapshots (13:32 ET for Bloomberg).
        ("2026-10-28", 16.91),
        # 29 Oct 17.20, +0.29 (+1.71%), as Alphabet's quarter hit tech (AD HOC News, range
        # 16.21-17.36; Investing.com's table; PC Thematic "ticked up to 17.20 from 16.91";
        # CappNotes). 16.91 + 0.29 = 17.20.
        ("2026-10-29", 17.20),
    ],
    # EACH SESSION'S REPORTED MOVE, at the precision it was reported. The series
    # above was self-checking only in a comment ("each day's percentage move must
    # reproduce the next day's level"), and nothing enforced it - which is how 16.93
    # sat in the 16th and every later close sat one session late for a week, with
    # the two descriptors that would have exposed it filed as "not reconciling". A
    # reported move is now an input, and a check requires it to reproduce from the
    # previous close in the series. Integers are moves reported to 0dp ("rose 3%").
    "vix_reported_moves": {
        "2026-09-14": 7.95, "2026-09-16": 3, "2026-09-17": -12.8,
        "2026-09-18": -4.08, "2026-09-21": 0.41, "2026-09-22": -4.44,
        "2026-09-23": 7, "2026-09-24": 3.23, "2026-09-25": -5.11,
        "2026-09-28": 8.07, "2026-09-29": -0.2, "2026-09-30": 1.9,
        "2026-10-01": 0.3, "2026-10-02": -6.59,
        "2026-10-05": 1.4, "2026-10-06": -3.29,
        "2026-10-07": 0.47, "2026-10-08": 2.19, "2026-10-09": -3.70,
        "2026-10-12": 2.49, "2026-10-13": 0.39, "2026-10-14": 10.48,
        "2026-10-15": -2.43, "2026-10-16": 21.45, "2026-10-19": -7.75,
        "2026-10-20": -6.13,
        "2026-10-21": -3.64, "2026-10-22": 14.09, "2026-10-23": 2.21,
        "2026-10-26": -5.45, "2026-10-27": -4.7, "2026-10-28": -3.48,
        "2026-10-29": 1.71,
    },
    # 28 Sep WITHHELD: two reports, 16.07 ("+1.20, +8.07%") and 16.30 ("+1.43,
    # +9.62%), and BOTH reproduce from 14.87 - the chain cannot choose, and one
    # source each is the situation that published a wrong close on 25 Sep. Up on
    # the day either way; not carried until a third source settles it.
    # 20 Oct was withheld on 2026-10-20 (one source, 17.60) and RESOLVED on the 21st
    # at 17.31 by three; the record keeps both.
    "vix_withheld": [],
    "vix_disputed_20oct": [17.31, 17.60],
    "vix_disputed_22oct": [18.84, 19.03],   # Investing.com's table against three sources
    "vix_disputed_26oct": [18.30, 18.39],   # AD HOC News against three sources
    "vix_disputed_27oct": [17.51, 17.52],   # Doug's Daily Diary against Cboe
    "vix_disputed_28oct": [16.83, 16.91],   # one recap against Cboe, Yahoo, CNBC and PC Thematic
    "vix_disputed_28sep": [16.07, 16.30],   # the record of the resolved dispute
    # MOVED 2026-10-17: 22.31 intraday on 16 Oct (The Weekly Debrief; CNBC "above
    # 22 for the first time in four months"), past 10 Sep's 18.17.
    "vix_latest_high": 22.31,
    "vix_latest_high_date": "2026-10-16",
    # Session context. These were accidentally deleted on 2026-09-16 when the VIX
    # block above was refactored - the replaced range ran past its intended end and
    # swallowed them. Nothing caught it, because the "every published input is
    # cited" check finds orphaned inputs, not REMOVED ones; the prose that cited
    # them is what failed. Restored with the 15 Sep session.
    # EQUITIES NOW CARRY A DATE. On 2026-09-21 every other market series got a
    # date field and a lag bound, and these three did not - their date was in the
    # comment above them, which is the exact failure that review was fixing.
    # 23 Sep. The Dow chains to the cent again: 51863.69 - 352.10 = 51511.59.
    # The two-record Nasdaq streak broke here: hot PMI + hawkish Barr + a weak 5y
    # auction sent the 10-year to a new post-2007 high, and duration assets sold
    # off across the board for the first time since the Fed hike itself.
    # 24 Sep (AP): flat after several turns - S&P -1.90 to 7704.13, Nasdaq +3.34 to
    # 26939.37, Dow -161.61 to 51349.98. The Dow chains to the cent; the Nasdaq's
    # points land one cent off (26936.04 + 3.34 = 26939.38), inside the rounding of
    # the prior close, and its percentage chains. Saxo's Dow of 51355.15 does not
    # reproduce its own -0.31% and is not carried.
    # 25 Sep (AP): up together - S&P +39.28 to 7743.41, Nasdaq +129.34 to
    # 27068.72, Dow +478.64 to 51828.62. AP rounds the percentages to 1dp; CNBC
    # reports S&P +0.51% and Dow +0.93%, the same as the points over the prior close
    # give, and the Nasdaq's +0.48% is those points. Every one chains. The
    # S&P and Dow land to the cent; the Nasdaq's points land one cent off again
    # (26939.37 + 129.34 = 27068.71), the same rounding in the prior close.
    # 28 Sep (CNBC close): Dow -347.11 (-0.67%) to 51481.51, S&P -0.77% to 7683.69,
    # Nasdaq -0.92% to 26820.38 - "weighed down by a jump in Treasury yields". The
    # Dow chains to the cent (51828.62 - 347.11); the other two chain at 2dp.
    # 29 Sep: S&P -12.85 to 7670.84, Nasdaq -22.84 to 26797.54, Dow -131.59 to
    # 51349.92 - every one to the cent. (Zacks/CNBC printed the S&P at "-0.16%";
    # 12.85 / 7683.69 is -0.167%, so the points are carried and the move derived.)
    # 30 Sep (AP): S&P -19.30 to 7651.54, Nasdaq +63.52 to 26861.06, Dow -443.87 to
    # 50906.05 - each to the cent. 1 Oct: S&P +0.19% to 7666.45, Nasdaq +0.04% to
    # 26871.60, Dow +20.51 to 50926.56.
    # 2 Oct (AP): S&P +56.27 to 7722.72, Nasdaq +319.27 to 27190.86 - a RECORD
    # close - and Dow +250.40 to 51176.96, after the weak payrolls cut the odds of
    # an October hike. The S&P and Dow chain to the cent; the Nasdaq's points land
    # a cent off (26871.60 + 319.27 = 27190.87), the prior close's rounding again.
    # 24/7 Wall St printed the S&P at 7722.57; it does not reproduce AP's points.
    # 5 Oct (AP): S&P +51.23 to 7773.95, its first close above 7,800 intraday
    # aside; Nasdaq +286.45 to a record 27477.31; Dow +90.94 to 51267.90.
    # 6 Oct (AP, CNBC): S&P +44.98 (+0.58%) to 7818.93, a RECORD close above its
    # August high; Nasdaq +122.48 (+0.45%) to a record 27599.79; Dow +253.38
    # (+0.49%) to 51521.28. Every one chains to the cent.
    # 7 Oct (AP): S&P -0.2%, Dow -0.7%, Nasdaq -0.2% as the 10-year hit a 2002
    # high; the 8 Oct points put the closes at 7801.77, 51179.87 and 27538.69.
    # 8 Oct (AP): S&P -36.41 (-0.47%) to 7765.36, Nasdaq -345.35 (-1.25%) to
    # 27193.34 on a tech sell-off, Dow +51.77 to 51231.64.
    # 9 Oct (TheStreet, Yahoo): S&P +46.18 (+0.59%) to 7811.54, Nasdaq +172.83
    # (+0.64%) to 27366.17, Dow +423.37 (+0.83%) to 51655.01. Each chains to the
    # cent. The S&P's record close is still 7818.93 (6 Oct).
    # 9 Oct's Dow was 51654.95 on AP's basis: Monday's +195.60 to 51850.55 and the
    # week-to-date -33.47 both land there, six cents off the 51655.01 carried.
    # 12 Oct (AP): S&P -4.30 to 7807.24, Nasdaq -120.27 to 27245.90, Dow +195.60
    # to 51850.55. 13 Oct (AP): S&P -1.79 to 7805.45, Nasdaq -41.52 to 27204.38,
    # Dow -180.45 to 51670.10. 14 Oct (AP): S&P -86.51 (-1.1%) to 7718.94, the
    # worst day since July, Nasdaq -511.51 (-1.9%) to 26692.87, Dow to 51621.48
    # (week-to-date -33.47), on the CPI and a chip sell-off (SOX -4.3%).
    # 15 Oct (AP): S&P +25.12 to 7744.06, Nasdaq +20.16 to 26713.03, Dow +556.21 to
    # 52177.69; the week-to-date points (S&P -67.48, Nasdaq -653.14, Dow +522.74)
    # land on 9 Oct again. 16 Oct (AP): S&P -84.62 (-1.1%) to 7659.44, Nasdaq
    # -572.99 (-2.1%) to 26140.03, Dow -175.28 (-0.3%) to 52002.41 - the worst week
    # for the S&P and Nasdaq since June. The Nasdaq's points land a cent off
    # (26713.03 - 572.99 = 26140.04), the prior close's rounding.
    # 19 Oct (Anadolu): S&P +31.29 (+0.41%) to 7690.73, Nasdaq +290.85 (+1.11%) to
    # 26430.89, Dow -36.38 (-0.07%) to 51966.03, as AI stocks rebounded. The
    # Nasdaq's points again land a cent off (26140.03 + 290.85 = 26430.88).
    # 20 Oct (CNBC, Yahoo's summary): S&P +21.84 (+0.28%) to 7712.57, Nasdaq -6.07
    # (-0.02%) to 26424.82, Dow +529.85 (+1.02%) to 52495.88 on industrial
    # earnings beats; money rotated from tech into value.
    # 21 Oct (AP via KVUE, CNBC): S&P +44.60 (+0.58%) to 7757.17, a third straight
    # gain; Nasdaq +278.04 (+1.05%) to 26702.86; Dow +360.21 (+0.69%) to 52856.09, as
    # SpaceX and Tesla led tech higher. A moomoo recap quoting +0.28% / -0.02% is the
    # 20th's session.
    # 22 Oct (AP via ABC News; CNBC): S&P -93.74 (-1.21%) to 7663.43, its worst day
    # since July; Nasdaq -694.00 (-2.60%) to 26008.86; Dow +11.89 (+0.02%) to
    # 52867.98, after Meta's spending outlook and Lam Research's guidance sent chip
    # stocks down more than 6%. All three chain to the cent.
    # 23 Oct (AP via Yahoo, "How major US stock indexes fared"; TV News Check; Dean FI):
    # S&P -39.75 (-0.52%) to 7623.68; Nasdaq -53.52 (-0.21%) to 25955.34; Dow -652.82
    # (-1.23%) to 52215.16, as oil topped $100 for WTI; energy the only clear gainer, and
    # the Philadelphia semiconductor index +0.44% after the 22nd's sell-off. All three
    # chain to the cent.
    # 26 Oct (CNBC's close report; TheStreet; Yahoo): S&P +53.09 (+0.70%) to 7676.77;
    # Nasdaq +214.04 (+0.82%) to 26169.38; Dow +146.42 (+0.28%) to 52361.58, as
    # Anthropic's IPO filing lifted the AI trade after back-to-back weekly losses for the
    # S&P and the Nasdaq, with the Fed on the 28th and 163 S&P companies reporting this
    # week. All three chain to the cent off the 23 Oct closes.
    # 27 Oct (TheStreet; TradingKey): S&P +45.83 (+0.60%) to 7722.60; Nasdaq +308.43
    # (+1.18%) to 26477.81; Dow +15.99 (+0.03%) to 52377.57, chip stocks extending the
    # rally on the eve of the Fed's decision as oil slid. All three chain to the cent off
    # the 26 Oct closes. A 24/7 Wall St. 7732.80 is an intraday print.
    # 28 Oct (CNBC's close report; AP via KRMG; Brownfield for the Dow): S&P +21.38
    # (+0.28%) to 7743.98; Nasdaq +72.04 (+0.27%) to 26549.85; Dow +97.53 (+0.19%) to
    # 52475.10 - a third straight gain for all three, the Fed holding at 2pm. All three
    # chain to the cent off the 27 Oct closes. Reuters-based 7739.58 was mid-session.
    # 29 Oct (AP via WTOP and KVUE; TheStreet): S&P -23.59 (-0.30%) to 7720.39, its first
    # fall in four sessions; Nasdaq -365.13 (-1.38%) to 26184.72; Dow -132.54 (-0.25%) to
    # 52342.56 - Alphabet's quarter (a revenue miss and negative free cash flow on its AI
    # spending) took the largest one-day bite out of its market value on record. All three
    # chain to the cent off the 28 Oct closes. AP rounds the moves to 0.3%, 1.4%, 0.3%.
    "equity_date": "2026-10-29",
    "spx_close": 7720.39, "spx_chg_pct": -0.30, "spx_chg_pts": -23.59,
    "nasdaq_close": 26184.72, "nasdaq_chg_pct": -1.38, "nasdaq_chg_pts": -365.13,
    "dow_close": 52342.56, "dow_chg_pct": -0.25, "dow_chg_pts": -132.54,
    "spx_record_close": 7818.93, "spx_record_date": "2026-10-06",
    # Previous closes, published so the CHAIN is checkable in code rather than
    # asserted in a sentence. This is the discipline that caught the 10-year's
    # dating error today and the VIX's on 17 Sep: a print that will not reproduce
    # the next session's published move is not a print.
    "spx_prev": 7743.98, "nasdaq_prev": 26549.85, "dow_prev": 52475.10,
    # WTI rolled on 22 Sep: October's final settle was 94.59, and from the 23rd the
    # front month is NOVEMBER. Its +1.81% is a move off November's own 22 Sep settle,
    # which no source found reports - so that prior is IMPLIED from the move, not
    # typed, and a check refuses to call a cross-roll pair a chain.
    # 24 Sep: November again, so this IS a chain - off November's own 23 Sep settle.
    # CNBC: "climbed 2.7% to settle at $94.61"; 92.16 x 1.0266 = 94.61.
    # 25 Sep: November again. "Settled Friday at $92.41, down $2.20" (EnergyNow);
    # CNBC: "dropping 2.33% to settle at $92.41". 94.61 - 2.20 = 92.41 to the cent,
    # and -2.20 / 94.61 = -2.33%: the reported move and the points agree. The
    # "-7.87% on the week" in the same reports runs off 100.30 - OCTOBER's 18 Sep
    # settle - so it crosses the 22 Sep roll and is not quoted here.
    # 28 Sep: November again, "rose 0.2% to $92.60" (investingLive); 92.60 - 92.41
    # = +0.19, i.e. +0.21% - the 2dp move is derived from the two settles.
    # 29 Sep -3.22 to 89.38; 30 Sep +1.04 to 90.42; 1 Oct "+$2.45, or 2.7%" to
    # 92.87; 2 Oct "US$91.11 ... falling US$1.76, or 1.90%, from Thursday's $92.87"
    # as DOE offered the SPR's last 40m barrels. November is still the front month
    # (last trade 20 Oct), so every step is one contract.
    # 5 Oct: "Monday's settlement of US$89.43" (EnergyNow), "fell 1.8%"
    # (Bloomberg); 89.43 / 91.11 = -1.84%. 6 Oct is NOT carried: two 7 Oct quotes
    # imply 89.44 and 89.43 - flat on the day either way, but a cent apart.
    # 6 Oct 89.44 and 7 Oct 88.28 (-1.30%, a daily table); 8 Oct "advanced 3.6% to
    # settle at $91.49" (CNBC: 88.28 x 1.0364); 9 Oct "rose 36 cents, or 0.39%, to
    # US$91.85" (Business Recorder): 91.49 + 0.36.
    # 13 Oct "up 0.43% at $94.14" (FNN, Investing.com); 14 Oct "settles USD 0.95
    # higher at 95.09" (Newsquawk; +1.01%, a three-week high). November is still
    # the front month (last trade 20 Oct).
    # 15 Oct "rose about 3% to close at $97.97" (CNBC); 16 Oct "closed $3.44, or
    # 3.5%, higher at $101.41", the highest since 17 Sep (Reuters). 97.97 + 3.44.
    # 19 Oct +2.25 (+2.2%) to 103.66; 20 Oct, its LAST TRADING DAY, November
    # "closed at $101.79 per barrel and expired" (CNBC), -1.80% off 103.66. From
    # 21 Oct the front month is December, which settled at $98.28 (-0.26) - a
    # $3.51 backwardation across the roll. The next roll needs December's own prior.
    # 21 Oct, DECEMBER now the front month: "fell 67 cents to settle at $97.15"
    # (CNBC; Reuters via FN News), -0.68%. Across the roll the prior is implied from
    # the move (97.82); the $98.28 and $98.21 quoted for December on the 20th were
    # session prices, not that day's settle, and are not carried.
    # 22 Oct: "rose $2.32, or 2.4 percent, to settle at $99.47" (Reuters via AsiaOne,
    # MarineLink). 97.15 + 2.32 = 99.47; 2.32 / 97.15 is +2.39%.
    # 23 Oct: "closes up $3.80, or 3.8%; settles at $103.27" (MarketScreener; Investing.com
    # +3.82%; CNBC). 99.47 + 3.80 = 103.27; 3.80 / 99.47 is +3.82%.
    # 26 Oct: "fell $1.51 to settle at $101.76" (CNBC; Reuters via Yahoo). 103.27 - 1.51
    # = 101.76; 1.51 / 103.27 is -1.46%.
    # 27 Oct: "fell $1.86, or 1.83%, to settle at $99.90" (DTN; CNBC $99.90, -1.83%).
    # 101.76 - 1.86 = 99.90; 1.86 / 101.76 is -1.83%.
    # 28 Oct: "gained 2.9% to settle at $102.78" (CNBC; Rigzone the same). 99.90 + 2.88 =
    # 102.78; 2.88 / 99.90 is +2.88%, the reported 2.9% to 1dp. December again - one contract.
    "wti_settle": 102.78, "wti_chg_pct": 2.88,
    "wti_date": "2026-10-28", "wti_contract": "2026-12",
    "wti_prev": 99.90,             # December's own 27 Oct settle - within one contract
    "wti_prev_date": "2026-10-27",
    "wti_expired_contract": "2026-11",
    # The 2026 low MOVED and this model did not notice for nine days. 14.18 on
    # 17 Aug was widely reported as the year's low at the time, and was carried as
    # such; on 4 Sep the index slid to 13.80 just before the payrolls release and
    # then rebounded to close 14.32. Both are kept - the August print is still cited
    # historically, but it is no longer the low.
    "vix_2026_low": 13.80,     # 4 Sep intraday, before the payrolls print
    "vix_2026_low_date": "2026-09-04",
    # RETIRED 2026-09-25: vix_1m_avg 15.28, vix_1m_low 13.80, vix_1m_high 16.82.
    # A "30-day range" typed on ~2 Sep and never rolled: the Volatility tab printed
    # "13.80-16.82" for three weeks while the index closed at 17.84 and traded to
    # 18.17 on 10 Sep - a range that excluded its own high. Undated statistics over
    # a moving window are a clock nobody winds. The tile now derives its range from
    # vix_history and the two dated intraday extremes.
    # VIX futures strip. Effective centre = expiry + 15 days, because a VIX future
    # settles on 30-day forward implied vol; that centre is the t at which the
    # contract's level is the forward vol, and it is what the bootstrap interpolates
    # between. Four contracts are observable, so the curve no longer has to guess
    # across a five-month gap between Sep and Dec.
    # Levels only. The MATURITIES are derived below from the contract settlement
    # rule and VIX_QUOTE_DATE - see the note there for why they are no longer typed.
    # ROLLED 2026-09-16: the September contract settles today, and a settled
    # contract is not a forward price. Dropped rather than carried - the expiry
    # guard added on 14 Sep fires the moment it settles, which is what it was for.
    # The three that remain are still 4 September quotes and still stale; that is
    # disclosed rather than fixed, because no fresher strip has been found in
    # FOURTEEN consecutive days of looking - 20 days of age against a 30-day bound
    # on 2026-09-24 (Cboe and vixcentral are unreachable from the build host; the
    # one secondary figure found repeats the 4 Sep levels). Dropping the front contract moves the horizon blend by 0.04
    # and changes no fund's volatility tilt.
    # As of 2026-09-19 the cost of that staleness is MEASURED, not guessed: against
    # VIX3M on 11 Sep, re-anchored to the same spot, this curve reads 4.97% LOW.
    # The direction matters - the model's implied vol, and therefore its forecast
    # drawdowns, are marginally understated rather than overstated. Two checks now
    # bound it: the residual itself, and a hard stop when the strip passes one
    # roll window.
    # RE-QUOTED 2026-10-03 - the first fresh strip in 29 days of looking: Oct 18.65,
    # Nov 19.21, Dec 19.35, Jan 20.38 (Investing.com's VIX futures board, "as of
    # 2 October", via search). ONE source, so it is tested against something it
    # never saw: re-anchored to the VIX3M date's spot, its 3-month vol reads
    # within a quarter of a percent of the published VIX3M (see VIX3M_RESID). A
    # TradingView snapshot of the October contract at 20.40, undated, also lands
    # inside the 10% band - so VIX3M cannot tell the two apart, and the dated
    # reading is carried. January joins the strip, so the bootstrap reaches 0.34y.
    # RE-QUOTED 2026-10-10 - AND THE 2 OCT STRIP WAS WRONG FOR ITS DATE. Tested
    # against VIX3M on 6 and 7 Oct, re-anchored to each day's spot, the "2 Oct"
    # strip read 4.2-4.4% HIGH; it matched only the 1 Oct VIX3M (-0.3%) - the one
    # pair the old check had, dated a day before the strip. VIX fell 6.6% on 2 Oct,
    # so either the board was a 1 Oct snapshot labelled 2 Oct or the futures fell
    # about a point that day; either way it priced the wrong market. The 5 Oct
    # Cboe settlements (thetrading.tools): Oct 17.46, Nov 18.14, Dec 18.55, Jan
    # 19.33. Tested the same way they read -0.6% (6 Oct) and -0.9% (7 Oct); a
    # second source's 7 Oct settlements (Oct 17.33, Nov 17.65) sit just below them,
    # as the VIX did. An undated TradingView snapshot (Nov 20.70, Dec 20.65) is not
    # carried.
    # RE-QUOTED 2026-10-21 - the October contract settles today, so the 5 Oct strip
    # could not run past it. The 20 Oct Cboe settlements (thetrading.tools, the
    # 5 Oct strip's source): Nov 18.4881, Dec 18.6965 - October 17.2209 has settled
    # and is dropped. January was not found as a settlement (Cboe's board shows
    # 19.52 beside an intraday 17.34 spot, undated) and is not carried, so the curve
    # mean-reverts to the long run beyond December. Saxo's 19 Oct November 18.75
    # sits beside it, as the VIX did. Tested against the same close's VIX3M.
    "vix_futs_levels": [("Nov", 2026, 11, 18.49), ("Dec", 2026, 12, 18.70)],
    "vix_fut_sep": 18.49,
    "vix_fut_dec": 18.70,
    # The superseded board, kept so its error is MEASURED on the page rather than
    # described: the same VIX3M test is run on it below. Now the 5 Oct strip.
    "vix_futs_prev_levels": [("Oct", 2026, 10, 17.46), ("Nov", 2026, 11, 18.14),
                             ("Dec", 2026, 12, 18.55), ("Jan", 2027, 1, 19.33)],
    "vix_futs_prev_date": "2026-10-05",
    "vix_longrun": 19.5,
    "variance_risk_premium": 3.5,
    # IMF WEO UPDATE, JULY 2026 (8 Jul). Until 2026-09-26 these were the APRIL
    # figures, labelled April in CLAIMS and last verified on 5 Sep - two and a half
    # months after the July update superseded them. Every one moved: global
    # 3.1/3.2 -> 3.0/3.4, US 2.4/2.0 -> 2.3/2.2, euro area 0.7 -> 0.9 (2027 1.2),
    # advanced 1.8/1.7 -> 1.7/1.8. The Europe note built "growth of just 0.7%" on
    # the stale one, and the Report typed it into its HTML where no check could see.
    "imf_weo_vintage": "2026-07-08",
    "imf_global_2026": 3.0,
    "imf_global_2027": 3.4,
    "imf_ea_2026": 0.9,
    # The APRIL figure the Europe note says the July update rose from. It traced
    # only by coincidence (to unrelated 0.7s) until 2026-10-03; now its own input.
    "imf_ea_2027": 1.2,
    "imf_emde_2026": 3.8,
    # FactSet Earnings Insight, 23 Oct: forward 12-month P/E 18.7 for the S&P 500, below
    # its five-year (19.8) and ten-year (19.1) averages and the 19.0 of 30 Sep; 24% of
    # the index reported, 83% beating EPS estimates by 2.1% in aggregate (five-year
    # average 7.5%); Q3 blended growth 29.5%, from 29.2%; health care the one sector
    # with earnings down on a year.
    "spx_fwd_pe": 18.7, "spx_fwd_pe_5y": 19.8, "spx_fwd_pe_10y": 19.1, "spx_fwd_pe_q3end": 19.0,
    "factset_reported_pct": 24, "factset_beat_pct": 83, "factset_surprise_pct": 2.1,
    "factset_surprise_5y": 7.5, "factset_q3_growth": 29.5, "factset_q3_growth_prev": 29.2,
    # THE FIVE-YEAR EVIDENCE (2026-10-27), for the 5-year driver and regional readings.
    # Fed September SEP medians (FRED's FEDTARMD; TD Economics): 3.9% at end-2028, 3.6%
    # at end-2029, longer run 3.2% (some tables 3.25%). Five-year breakevens 2.37% on
    # 6 Oct (MacroMicro) and 2.48% on 23 Oct (FRED via commentary), 5y5y 2.20% on 23 Oct.
    # IMF October WEO: world 3.1% (2026), 3.4% (2027); Philippines 3.4% and 5.1%
    # (Philstar; Manila Bulletin). BSP after its 22 Oct hike: inflation 6.1% (2026), 6.0%
    # (2027), 3.3% (2028) (Philstar, Rappler, GMA). Shiller CAPE 40.7 in October
    # (Macroradar 40.71, thetrading.tools 40.7; GuruFocus 40.19 on 1 Oct), record 44.2
    # (Dec 1999), long-run median about 16.6. Long-term S&P EPS growth forecast 16.7%,
    # against 22.3% forecast and 9.5% realised a year since 1992 (Klement; Finimize) -
    # one analyst's figures. Brent December 2029 $72.32 and December 2030 $69.16 on
    # 15 Oct, front month $105.92 (CME settlements via Baratelli Institute; "low-$70s by
    # 2030", Commodity Board).
    # The end-2027 median, 4.1% (v71, for the 3-year view): FRED's FEDTARMD and the FRED
    # blog's SEP note, MUFG's 4.125% median dot; its own input, not the 2026 one reused.
    # The feeder's stated benchmark, 75% Nasdaq-100 Index (ATRAM's fund page for the A PHP
    # class; uitf.com.ph's A and D USD listings; the fact sheet). Its own input from v73:
    # until then the 75 in the fund's note traced only by landing within rounding of an
    # unrelated number (Brent's 75.5% y/y).
    "atrqiap_bench_ndx_pct": 75,
    "fed_sep_2027": 4.1, "fed_sep_2028": 3.9, "fed_sep_2029": 3.6, "fed_sep_longrun": 3.2,
    "be_5y_6oct": 2.37, "be_5y": 2.48, "be_5y5y": 2.20,
    "imf_world_2026": 3.1, "imf_world_2027": 3.4, "imf_ph_2026": 3.4, "imf_ph_2027": 5.1,
    "bsp_cpi_2026": 6.1, "bsp_cpi_2027": 6.0, "bsp_cpi_2028": 3.3,
    "cape": 40.7, "cape_high": 44.2, "cape_median": 16.6,
    "ltg_eps": 16.7, "ltg_hist_fcst": 22.3, "ltg_hist_real": 9.5,
    "brent_dec2029": 72.32, "brent_dec2030": 69.16, "brent_front_15oct": 105.92,
    # December 2027 Brent, for the 3-year view (2026-10-27): $87.82 on a 22 Oct quote
    # (Farmbucks, intraday) and $86.46 on an undated table (Oilprice) - two quotes $1.36
    # apart, so carried as a range, not a settle.
    "brent_dec2027_lo": 86.46, "brent_dec2027_hi": 87.82,
    # Two newer NDX forward multiples disagree with each other - MacroMicro 20.50 for
    # October, Siblis 23.26 for September - so neither replaces the last verified 22.4.
    "ndx_fwd_pe_disputed": [20.50, 23.26],
    "ndx_fwd_pe": 22.4,
    "ndx_fwd_pe_10y": 22.9,
    "ndx_fwd_pe_5y": 24.7,
    "sxxp_fwd_pe": 15.37,
    "asia_fwd_pe": 10.5,
    "asia_eps_2026": 52.5,
    "asia_eps_2027": 27.5,
    # 11 Sep closes - the sell-off the Asia note describes. The note also carried
    # Nikkei -1.9%, KOSPI -1.8%, Samsung -3.5% and SK Hynix -2.2% with no inputs
    # behind them (they traced to unrelated 1.9 / 2.2 figures); on 2026-09-26 none
    # could be re-verified, and one source dates the leg down to the 10th, so the
    # percentages were dropped and the sell-off is dated 10-11 Sep.
    "nikkei": 64011, "kospi": 6910,
    # 24 Sep: the Nikkei reopened from the 23 Sep equinox holiday +0.76% at 65,513.94
    # (TradingKey close). Corroborated by construction: Trading Economics' intraday
    # +0.99% at 65,665 implies the same prior close (~65,020) - two reports agreeing
    # on the base they moved from. Korea was shut for Chuseok, so the KOSPI has no
    # newer print than the one above.
    # 25 Sep: +1.30% to 66,364.20, a fifth straight gain (Business Standard). A
    # widely syndicated 66,345.07 (+831.08, +1.27%) was stamped 14:56 - before the
    # 15:30 close - and its own points miss the 24 Sep base by 0.05: an intraday
    # print. 65,513.94 x 1.0130 = 66,365; the close chains to its percentage.
    # 28 Sep: -486.58 (-0.73%) to 65,877.62 after touching 67,035 (News On Japan);
    # 66,364.20 - 486.58 = 65,877.62, which also re-confirms Friday's close.
    # 30 Sep: +1.94% (+1,270-odd) to 66,753.72, its highest close since 19 Aug; 1 Oct:
    # +2,203.00 (+3.30%) to 68,956.72 on Micron's forecast, the highest since 17 Aug;
    # 2 Oct: -647.26 (-0.94%) to 68,309.46 on profit-taking before the US payrolls
    # (Xinhua/Kyodo). 66,753.72 + 2,203.00 = 68,956.72 and 68,956.72 - 647.26 =
    # 68,309.46. A rival 66,866.47 for 30 Sep does not reproduce 1 Oct's points.
    # 5 Oct +1,637.40 (+2.40%) to 69,946.86; 6 Oct +737.12 (+1.05%) to 70,683.98,
    # the first close above 70,000 since 1 July (Kyodo / Edge). Both chain.
    # 7 Oct 70035.71 (-0.92%); 9 Oct 69030.92, -11.19 (-0.02%), after recovering
    # most of a near-900-point fall as SoftBank slid (Nikkei Inc., FRED, Il Sole).
    # The 8 Oct close is the one Nikkei's own move implies, 69042.11; a daily table
    # had 68520.50 (-2.16%), which Friday's published move does not reproduce.
    # 14 Oct 67744.29, a fifth straight fall; 15 Oct -3318.34 (-4.9%) to 64425.95,
    # the third-largest points fall on record, as Advantest and Tokyo Electron led
    # an AI and rate sell-off (Nikkei Inc., Japan Times).
    # 16 Oct +898.34 (+1.39%) to 65324.29 (Yahoo historical; Reuters via ad-hoc
    # news). Investing.com and Trading Economics' 65,619 (+1.66-1.85%) was a feed
    # snapshot and does not reproduce the points.
    # 19 Oct -407.59 (-0.62%) to 64916.70, after a 1,400-point intraday fall to
    # 63831.78 (uCapital, BBN Times, News On Japan); 20 Oct -841.28 (-1.30%) to
    # 64075.42 on AI-investment worries and oil (AP).
    # 21 Oct +545.82 (+0.85%) to 64621.24 as AI stocks led a rebound (AP; Il Sole 24
    # Ore / Radiocor). Investing.com's 64,696.00 (+0.97%) is a feed value.
    # 22 Oct -1713.40 (-2.65%) to 62907.84 on AI and chip selling with Brent back
    # above $110 (TradingKey, TradingView). A Reuters-based Investing.com headline has
    # -2.40%, which does not reproduce from 64621.24; the 2.65% does, exactly.
    # 23 Oct: -214.68 (-0.34%) to 62693.16 (Reuters; Nikkei's index page), tech off its
    # lows; 62907.84 - 214.68 = 62693.16. Investing.com's "-0.25%" was a pre-close print.
    # 26 Oct: -503.51 (-0.80%) to 62189.65, a third straight fall, on chip selling
    # (TokenPost; TradingKey 62189.60). 62693.16 - 503.51 = 62189.65.
    # 27 Oct: +1078.72 (+1.73%) to 63268.37 as chip and AI stocks rallied, SoftBank +5%
    # (Yahoo historical; AD HOC News; CNBC's live blog +1.73%). 62189.65 + 1078.72 =
    # 63268.37. v76-v77 CARRIED 63268.32 (+1078.67), five hundredths low: the 1.73% chain
    # check passes either way, so only re-reading the points caught it. Investing.com's
    # "+1.78%" headline does not reproduce from 62189.65; the 1.73% does.
    # 28 Oct: +685.82 (+1.08%) to 63954.19, Kioxia leading chips after SK hynix's quarter
    # (Jiji; AD HOC News "686 points higher"; Il Sole 24 Ore +1.08%). 63268.37 + 685.82 =
    # 63954.19 - which also confirms the corrected 27 Oct close. Held in v76-v77 among four
    # prints (63954.14, Yahoo's 64000.18, Investing.com's 64232 kept as the record).
    "nikkei_disputed_28oct": [63954.14, 63954.19, 64000.18, 64232.0],
    # 29 Oct: +705.28 (+1.10%) to 64659.47, a third straight gain on chip and AI shares
    # before the BoJ (Nikkei Indexes' own close; FRED NIKKEI225; News on Japan). 63954.19 +
    # 705.28 = 64659.47. v83 RECORDED 64594.00 (+639.81, Reuters via Investing.com) as
    # verified: a pre-close print, never carried, and wrong (runbook 119).
    # 30 Oct: -1369.36 (-2.12%) to 63290.11 as the AI sell-off reached Tokyo after
    # Alphabet's quarter and the BoJ held (Japan Daily Sun; News on Japan; CNBC -2.12%).
    # 64659.47 - 1369.36 = 63290.11. Trading Economics' 63154 (-2.33%) does not chain.
    "nikkei_disputed_29oct": [64594.0, 64659.47],
    "nikkei_disputed_30oct": [63154.0, 63290.11],
    "nikkei_latest": 63290.11, "nikkei_latest_chg_pct": -2.12, "nikkei_latest_chg_pts": -1369.36,
    "nikkei_latest_date": "2026-10-30",
    "nikkei_latest_prev": 64659.47,
    "nikkei_29oct_chg_pct": 1.10,
    # KOREA REOPENED from Chuseok on 28 Sep: KOSPI -191.18 (-2.70%) to 6,889.74 from
    # 7,080.92 on the 23rd; Samsung Electronics -5.43%, SK Hynix -5.05%; foreigners
    # net sold 3.24tn won (Korea Times, Seoul Economic Daily, IBTimes).
    # 29 Sep -0.27% to 6,870.81. 2 Oct: +32.39 (+0.46%) to 7,003.74, back above
    # 7,000 as Samsung (+2.79%) and SK Hynix (+3.21%) rebounded late on Micron's
    # results (Seoul Economic Daily, SBS).
    # Korea shut 5 Oct (National Foundation Day, observed). 6 Oct: -62.35 (-0.89%)
    # to 6,941.39 as foreigners sold chips ahead of earnings; Samsung -1.45%, SK
    # Hynix -3.69% (Seoul Economic Daily).
    # 7 Oct -137.49 (-1.98%) to 6803.90 (Yonhap); 8 Oct -177.97 (-2.62%) to
    # 6625.93, a third straight fall on oil and US rate fears (Korea Exchange via
    # JoongAng). Korea was shut on 9 Oct (Hangeul Day). Samsung's preliminary Q3
    # operating profit (8 Oct) was 107.4tn won, the first above 100tn, against a
    # 106.1tn consensus; TSMC's September revenue was +54.6% on a year earlier.
    # 14 Oct -26.54 (-0.44%) to 6008.81, a sixth straight loss (Asia Business
    # Daily, Seoul Economic Daily); 15 Oct -454.59 (-7.57%) to 5554.22 after a
    # circuit breaker halted trading, the lowest close since 7 April and 20.7%
    # below the 7003.74 of 2 Oct - a bear market in seven sessions. Foreigners net
    # sold 3.62tn won; SK Hynix and Samsung each fell about 10% on rate and AI
    # funding fears, after China's CXMT flagged a new DRAM design on 12 Oct.
    # 16 Oct +113.83 (+2.05%) to 5668.05 after touching 5809.94; foreigners net
    # buyers for the first time in nine sessions (Aju Press). Indonesia fell 11%
    # and tripped a circuit breaker on an MSCI downgrade warning.
    # 19 Oct +99.96 (+1.76%) to 5768.01 after opening more than 3% lower;
    # institutions bought, foreigners and retail sold (Seoul Economic Daily, SBS,
    # JoongAng). 20 Oct -215.27 (-3.73%) to 5552.74, the lowest close since 7
    # April, as foreigners and institutions sold (Seoul Economic Daily citing KRX;
    # KED Global). AP's 5539.05 ("-4%") was a pre-close figure; a KuCoin flash's
    # 5553.08 misses its own points. The index is down 17% in October, the worst
    # of the major markets.
    # 21 Oct +182.92 (+3.29%) to 5735.66 as chip stocks rallied after the US earnings
    # rebound (AP via WSLS; TokenPost "closes 3.29% higher").
    # 22 Oct -201.89 (-3.52%) to 5533.77, below the 20 Oct close, as the Bank of Korea
    # paused and chips sold - SK Hynix -5.48%, Samsung Electronics -4.02% (Aju Press,
    # TradingKey). 5735.66 - 201.89 = 5533.77.
    # 23 Oct: +16.53 (+0.30%) to 5550.30 after opening -2.36% at 5403.17 and touching
    # 5305.98 - a 4% intraday fall reversed - as SK Hynix rose 4.42% on halting
    # Solidigm's IPO review; Samsung +0.47% to 215,500 won; foreigners net sellers
    # (KED Global, Korea JoongAng Daily, Asia Business Daily). 5533.77 + 16.53 = 5550.30.
    # 26 Oct CORRECTED 2026-10-27: -80.83 (-1.46%) to 5469.47, a seven-month low, as
    # foreigners net sold 695.5bn won (Asia Business Daily; UPI citing Korea Exchange
    # data; Korea JoongAng Daily; Businesskorea). 5550.30 - 80.83 = 5469.47. v69-v72
    # carried TokenPost's 5469.59 (-80.71) and set the exchange figure aside as "a feed
    # value": both reproduce from 5550.30, so the chain could not choose, and the one
    # with the exchange behind it was the one dropped. Samsung Electronics -1.16%.
    # 27 Oct: +168.87 (+3.09%) to 5638.34 after a 4.9% intraday rise that triggered a
    # sidecar on program buying, as Anthropic's IPO filing revived the AI trade before
    # SK Hynix reports on the 28th (Asia Business Daily; Seoul Economic Daily;
    # MoneyToday). 5469.47 + 168.87 = 5638.34. A report that SK Hynix is weighing a
    # special dividend of about 16tn won is NOT a decision: the company says it is
    # reviewing shareholder returns and has decided nothing (MoneyToday).
    # 28 Oct: +374.10 (+6.63%) to 6012.44, after touching 6032.28, as SK hynix's record
    # quarter lifted the chipmakers and foreigners and institutions bought more than 1.7tn
    # won (Newsis; SBS Biz; Newspim; LCNews). 5638.34 + 374.10 = 6012.44. A 6023.73
    # (+6.8%) in one English report does not reproduce the exchange's points.
    # SK hynix (company release, 28 Oct; investingLive): third-quarter operating profit
    # 83.33tn won, +632% on a year and above the ~77tn expected, on revenue of 104.6tn,
    # and about 100tn won of shareholder returns planned for 2026 - 30tn or more in
    # dividends, 60tn or more in buybacks. It settles the 27 Oct dividend report.
    # 29 Oct: -74.78 (-1.24%) to 5937.66, back below 6,000 as Samsung fell more than 4% on
    # its detailed quarter (Seoul Economic Daily; SBS). 6012.44 - 74.78 = 5937.66.
    # 30 Oct: -206.92 (-3.48%) to 5730.74 after Alphabet's quarter revived the AI-spending
    # fear; a sell-side sidecar triggered at 10:05 and foreigners sold 1.6tn won (Seoul
    # Economic Daily; Korea Times). 5937.66 - 206.92 = 5730.74.
    "kospi_latest": 5730.74, "kospi_latest_chg_pts": -206.92, "kospi_latest_chg_pct": -3.48,
    "kospi_latest_date": "2026-10-30", "kospi_latest_prev": 5937.66,
    "kospi_29oct_chg_pct": -1.24, "kospi_28oct_chg_pct": 6.63,
    "skhynix_q3_op_tn": 83.33, "skhynix_q3_op_yoy": 632, "skhynix_returns_2026_tn": 100,
    "kospi_2oct": 7003.74,
    # TSMC Q3 (15 Oct): net income NT$763.06bn, +68.7% y/y, against NT$746.34bn
    # expected (LSEG); a sixth straight record quarter.
    "tsmc_q3_ni_bn": 763.06, "tsmc_q3_ni_yoy": 68.7, "tsmc_q3_consensus_bn": 746.34,
    "samsung_q3_op_tn": 107.4, "samsung_q3_consensus_tn": 106.1,
    # JPM LTCMA, ROLLED 2026-10-21 to the 2027 edition (published 19 Oct 2026): US
    # large cap 7.5% (+80bp on resilient profits), EM equity 7.1% (down as the AI and
    # capex tailwinds normalise) - developed markets above emerging for the first
    # time in the series. Every fund here moves to it together. The 2026 edition's
    # figures are kept as the record.
    "ltcma_edition": 2027, "ltcma_date": "2026-10-19",
    "ltcma_us_eq": 7.5, "ltcma_us_eq_prev": 6.7,
    "ndx_growth_premium": 1.3,     # NDX total return over US large cap in the build-up
    "qiap_capture": 78,            # covered-call upside capture, % of the NDX
    # EVERY COMPONENT OF EVERY GROSS RETURN IS AN INPUT, AND THE GROSS IS COMPUTED
    # FROM THEM. Until 2026-09-25 the three equity gross returns were typed beside a
    # note giving their recipe, and nothing checked one against the other. Two
    # happened to agree. The Nasdaq Equity Income figure did not: its note builds
    # 8.0% x 78% + 0.5% = 6.74%, and the engine carried 7.2% from the first build
    # on 2 Sep - 0.46pp of return, in the sleeve the optimiser put 70% into. The
    # 12 Sep traceability fix had made 78% and 1.3% inputs so the prose would
    # trace, but never wired them into the calculation: decorative inputs.
    "qiap_premium_lr": 0.5,        # option premium harvest at LONG-RUN implied vol, %/yr (E)
    "asia_target_mgmt_fee": 1.50,  # JPMAM's published management fee for the HK unit trust
    "asia_rerating": 1.0,          # re-rating credit in the Asia base, %/yr (E) - see CLAIMS
    "asia_div_drag": 0.5,          # dividend tilt's lower growth capture, %/yr (E)
    "tech_growth_premium": 3.5,    # tech earnings-growth premium over US large cap, %/yr (E)
    "tech_derating": 1.2,          # tech multiple de-rating drag, %/yr (E)
    "phmm_gross_prev": 5.25,       # the PH short-rate assumption before the mandate lengthened
    "ltcma_em_eq": 7.1, "ltcma_em_eq_prev": 7.8,
}

# ----------------------------------------------------------------------------
# 1a. CRUDE CONTRACT ROLLS - derived, not typed
#     A settle only chains to the previous settle OF THE SAME CONTRACT. On
#     2026-09-23 the first pass compared November WTI prints against October's
#     final settle (the October contract expired on the 22nd), found a $2-5 gap,
#     and withheld a settle that was never in dispute. Which contract is the front
#     month on a given day is set by the exchange calendar, so - like the VIX
#     maturities below - it is derived here and never typed. Business days are
#     weekdays; exchange holidays are not modelled, which can move a last trading
#     day by one session around a holiday and is stated rather than hidden.
# ----------------------------------------------------------------------------
def _bizdays_before(d, n):
    while n:
        d -= _dt.timedelta(days=1)
        if d.weekday() < 5:
            n -= 1
    return d


def cl_last_trade(y, m):
    """NYMEX WTI (CL), delivery month (y, m): trading ends 3 business days before
    the 25th of the prior month, or 4 if the 25th is not a business day."""
    py, pm = (y - 1, 12) if m == 1 else (y, m - 1)
    d25 = _dt.date(py, pm, 25)
    return _bizdays_before(d25, 3 if d25.weekday() < 5 else 4)


def brent_last_trade(y, m):
    """ICE Brent, delivery month (y, m): trading ends on the last business day of
    the second month before delivery."""
    py, pm = (y, m - 2) if m > 2 else (y - 1, m + 10)
    d = _dt.date(py + (pm == 12), pm % 12 + 1, 1) - _dt.timedelta(days=1)
    while d.weekday() >= 5:
        d -= _dt.timedelta(days=1)
    return d


def front_contract(iso, last_trade):
    """The delivery month ('YYYY-MM') that is front month on date iso."""
    d = _dt.date.fromisoformat(iso)
    y, m = d.year, d.month
    while last_trade(y, m) < d:
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return f"{y}-{m:02d}"


# ----------------------------------------------------------------------------
# 1b. VIX FUTURES MATURITIES - derived, not typed
#     The strip's levels are quoted at a market close; its MATURITIES are a
#     function of the calendar. They used to be four hard-typed constants, and on
#     2026-09-10 an audit backed all four out to an implied base date of
#     6 September 2026 - a SUNDAY, matching neither the quote date (4 Sep, the
#     Friday close every level here comes from) nor AS_OF. Nothing checked them,
#     so the time axis had drifted away from the prices sitting on it, and would
#     have drifted further every time AS_OF moved.
#
#     They are now derived. A VIX future settles on the Wednesday 30 days before
#     the third Friday of the month AFTER the contract month; on that date it
#     pays out on 30-day forward implied vol, so the t at which the contract's
#     level IS the forward vol is the settlement date plus 15 days - the centre
#     of the 30-day window it prices. Maturities are measured from the QUOTE
#     DATE, not from AS_OF: the whole curve, spot included, is one market close,
#     and measuring a 4 Sep curve from a 9 Sep origin would misdate every point.
# ----------------------------------------------------------------------------

VIX_QUOTE_DATE = "2026-10-20"   # Tuesday close - the date every VIX level here is from
VIX_FWD_WINDOW_D = 30           # a VIX future pays on 30-day forward implied vol

def _third_friday(y, m):
    return [_dt.date(y, m, d) for d in range(15, 22)
            if _dt.date(y, m, d).weekday() == 4][0]

def vix_settlement(y, m):
    """Settlement date of the VIX future for contract month (y, m)."""
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return _third_friday(ny, nm) - _dt.timedelta(days=VIX_FWD_WINDOW_D)

def vix_maturity(y, m, quote=None):
    """Years from the quote date to the centre of the contract's 30-day window."""
    q = _dt.date.fromisoformat(quote or VIX_QUOTE_DATE)
    centre = vix_settlement(y, m) + _dt.timedelta(days=VIX_FWD_WINDOW_D // 2)
    return (centre - q).days / 365.0

# Everything about the latest spot derives from the history list - nothing is typed
# twice. The percentage move is computed, not asserted, so the chain cannot disagree
# with itself the way separate `latest` and `prev_close` fields could.
_VH = MACRO["vix_history"]
MACRO["vix_latest_date"], MACRO["vix_latest"] = _VH[-1]
MACRO["vix_prev_date"], MACRO["vix_prev_close"] = _VH[-2]
# The move the PAGE prints is the REPORTED one, at the precision it was reported.
# Until 2026-09-26 it was recomputed from the two rounded closes, which is not the
# same number: on 25 Sep the Volatility lede printed "-5.23%" from 14.85 / 15.67
# while the driver note beside it, and the source, said -5.24%. Two figures for one
# move on one page. (That pair was itself wrong - see vix_history: 14.87, -5.11% -
# but the rule stands whatever the data.) The recomputed value is kept,
# under its own name, for the audit; the chain check below ties the two together.
_vrep = MACRO["vix_reported_moves"][MACRO["vix_latest_date"]]
MACRO["vix_latest_chg_pct_calc"] = round(
    (MACRO["vix_latest"] / MACRO["vix_prev_close"] - 1) * 100, 2)
MACRO["vix_latest_chg_pct"] = float(_vrep)
MACRO["vix_latest_chg_dp"] = 0 if isinstance(_vrep, int) else len(repr(_vrep).split(".")[1])
MACRO["vix_episode_high"] = max(v for _, v in _VH)
# The episode high has a DATE, and the page needed it: without one the prose called
# 17.84 a mid-week peak when it belongs to 10 Sep, a week before the week described.
# A superlative without its date drifts the moment the window moves.
MACRO["vix_episode_high_date"] = max(_VH, key=lambda r: r[1])[0]
MACRO["vix_episode_low_date"] = min(_VH, key=lambda r: r[1])[0]

# The 10-year's headline level, its prior and its move, all DERIVED from the
# series. ust_10y was a scalar with its date in a comment, and the comment was
# wrong for two days. A series cannot carry a date it does not have.
_UH = MACRO["ust_10y_history"]
MACRO["ust_10y_date"], MACRO["ust_10y"] = _UH[-1]
MACRO["ust_10y_prev_date"], MACRO["ust_10y_prev"] = _UH[-2]
MACRO["ust_10y_chg_bp"] = round((MACRO["ust_10y"] - MACRO["ust_10y_prev"]) * 100, 1)

_BH = MACRO["brent_history"]
MACRO["brent_date"], MACRO["brent"] = _BH[-1]
MACRO["brent_prev_date"], MACRO["brent_prev"] = _BH[-2]
# November WTI's 22 Sep settle, implied by its reported move - see wti_contract.
# Implied ONLY when no published prior was entered; a check requires that to
# coincide exactly with a contract roll.
MACRO["wti_expired_last_trade"] = cl_last_trade(
    *map(int, MACRO["wti_expired_contract"].split("-"))).isoformat()
MACRO["wti_prev_implied"] = "wti_prev" not in MACRO
if MACRO["wti_prev_implied"]:
    MACRO["wti_prev"] = round(MACRO["wti_settle"] / (1 + MACRO["wti_chg_pct"] / 100), 2)
MACRO["brent_yoy"] = round((MACRO["brent"] / MACRO["brent_yr_ago"] - 1) * 100, 2)
# On the week: against the settle seven calendar days earlier, same contract or None.
_wk = (_dt.date.fromisoformat(MACRO["brent_date"]) - _dt.timedelta(days=7)).isoformat()
MACRO["brent_wk_chg_pct"] = (round((MACRO["brent"] / dict(MACRO["brent_history"])[_wk] - 1) * 100, 1)
                             if _wk in dict(MACRO["brent_history"]) else None)
# "16 of 18 dot-plot participants" - the 16 is the one-more and two-more groups
# together, derived so the note's count has its own input rather than tracing to
# whatever else happens to equal 16.
MACRO["fed_dots_any_more"] = MACRO["fed_dots_one_more"] + MACRO["fed_dots_two_more"]
# How far spot sits below the four-month high, and the day's move, both DERIVED so
# the notes quoting them cannot drift from the levels they come from.
# NOT ACROSS A ROLL. The $108.75 settle high of 15 Sep is November's; December,
# front month since 1 Oct, traded $5.47 below November on the day it took over.
# "X% below the high" between two contracts measures the roll, not the market -
# the same reason WTI's cross-roll weekly change is not quoted. Derived only when
# the high and the latest settle are the same contract, else None, and the page
# says which contract the high belongs to.
MACRO["brent_high_contract"] = front_contract(MACRO["brent_high_date"], brent_last_trade)
MACRO["brent_contract"] = front_contract(MACRO["brent_date"], brent_last_trade)
MACRO["brent_off_high_pct"] = (round((1 - MACRO["brent"] / MACRO["brent_high"]) * 100, 2)
                               if MACRO["brent_high_contract"] == MACRO["brent_contract"] else None)
MACRO["brent_chg_pct"] = round((MACRO["brent"] / MACRO["brent_prev"] - 1) * 100, 2)
# None when the latest settle was RECOVERED rather than reported (see
# brent_recovered); the checks then require the recovery instead.
MACRO["brent_chg_reported"] = MACRO["brent_reported_moves"].get(MACRO["brent_date"])
MACRO["brent_session_high_date"], MACRO["brent_session_high"] = max(
    MACRO["brent_session_highs"].items())
# The peso's year-to-date loss of VALUE, which is what a peso holder experiences:
# 1 - base/spot, not spot/base - 1. Both conventions are in circulation and they
# differ by half a point at this level, so the one that reaches the portfolio is
# the one computed, and it is computed rather than typed.
MACRO["usdphp_ytd_pct"] = round(
    (1 - MACRO["usdphp_2025_close"] / MACRO["usdphp"]) * 100, 2)
MACRO["kospi_off_2oct_pct"] = round((1 - MACRO["kospi_latest"] / MACRO["kospi_2oct"]) * 100, 1)
MACRO["spx_off_record_pct"] = round((1 - MACRO["spx_close"] / MACRO["spx_record_close"]) * 100, 1)
MACRO["brent_chg_pts"] = round(MACRO["brent"] - MACRO["brent_prev"], 2)
MACRO["usdphp_chg_ctvo"] = round((MACRO["usdphp"] - MACRO["usdphp_prev"]) * 100, 1)
# The vessel-count drop the geopolitics note quotes in order to correct it. Derived
# rather than typed so the figure and the counts it comes from cannot drift apart -
# and so the note's own arithmetic is auditable rather than asserted.
MACRO["hormuz_vessel_drop_pct"] = round(
    (1 - MACRO["hormuz_transits"] / MACRO["hormuz_baseline"]) * 100, 0)
# The queue's latest reading and its range, derived from the series so the note
# cannot quote a level the series does not contain, nor call three noisy points a
# trend. Ordered and de-duplicated by the checks below.
_HQ = MACRO["hormuz_queue"]
MACRO["hormuz_queue_date"], MACRO["hormuz_queue_now"] = _HQ[-1]
# How stale the PortWatch reading is at this review, against its own publication
# cadence. Derived, so it cannot be described as fresh once it is not.
MACRO["hormuz_transits_age_d"] = (
    _dt.date.fromisoformat(REVIEW_DATE)
    - _dt.date.fromisoformat(MACRO["hormuz_transits_date"])).days

MACRO["vix_futs"] = [(lbl, round(vix_maturity(y, m), 4), lvl)
                     for lbl, y, m, lvl in MACRO["vix_futs_levels"]]
# BY LABEL, not by position. "vix_fut_dec" was the strip's LAST contract, which
# was December until January joined on 2026-10-03 - and the page then printed
# January's 20.38 as "December future" and "prices 20.38 by December". The front
# contract keeps its historical name (vix_fut_sep) and is still the first.
MACRO["vix_fut_sep"] = MACRO["vix_futs"][0][2]
MACRO["vix_fut_dec"] = next(lvl for lbl, _, lvl in MACRO["vix_futs"] if lbl == "Dec")

# ----------------------------------------------------------------------------
# 1c. PENDING CATALYSTS
#     Scheduled events that land AFTER the as-of date and are therefore NOT in
#     any number on this page. They are listed so a reader knows what the model
#     cannot know yet, and checked so the page can never describe an event in the
#     future tense once its date has passed - the failure mode that has produced
#     four stale-figure defects in this changelog.
# ----------------------------------------------------------------------------

# Postponed with no new date, so it is NOT a dated catalyst. Recorded here rather
# than dropped, because "the thing that was going to resolve this did not happen" is
# itself information the page should carry. (2026-09-14.)
# Emptied 2026-10-21: the Oman talks called off on 14 Sep were superseded by the
# UN meeting of 22 Sep and then the Qatar-Pakistan channel; five weeks on, the entry
# described history, not a pending event. The mechanism stays for the next one.
POSTPONED = []

# 29-30 Oct (v84): US GDP and September PCE, the ECB's hold and the BoJ's hold happened
# and moved into the notes; October payrolls joins.
CATALYSTS = [
    ("2026-11-03", "US midterm elections",
     "The date the Hormuz standoff works to: the US pledged on 8 Oct not to strike Iran "
     "before it, and on 28 Oct reportedly told Gulf states to prepare for strikes after "
     "it. Full closure, the stress table's worst row, is what this date can bring back."),
    ("2026-11-06", "US October jobs report",
     "The first payrolls since the Fed held with two votes for a hike, and the test of a "
     "consumer whose real spending was flat in September."),
]
# WHICH CLOCK DECIDES THAT A CATALYST HAS HAPPENED (2026-10-28). AS_OF is the newest
# session carried, often Asia's, a day ahead of New York's. A US event is past once a US
# session ON OR AFTER its date is carried, so it is read against the US equity date;
# every other catalyst against AS_OF.
CATALYST_CLOCK = {"US October jobs report": "equity_date"}

# ----------------------------------------------------------------------------
# 2. VOLATILITY TERM STRUCTURE
#    Piecewise forward-variance curve bootstrapped from the observable VIX
#    complex, then mean-reverted to the long-run anchor.
#      sigma(0->T) = sqrt( (1/T) * integral_0^T sigma_f(t)^2 dt )
# ----------------------------------------------------------------------------

KAPPA = 1.5   # OU mean-reversion speed on vol beyond the last liquid future

def _seg_var(s_a, s_b, dt):
    """Integral of a linearly-interpolated vol segment's variance.
    For sigma(t) = a + b t, mean of sigma^2 = (a^2 + a*b_end + b_end^2)/3."""
    return (s_a * s_a + s_a * s_b + s_b * s_b) / 3.0 * dt

# Knots: spot at t=0, then each observable future at its effective centre.
VOL_KNOTS = [(0.0, MACRO["vix_spot"])] + [(t, v) for _, t, v in MACRO["vix_futs"]]

def fwd_vol(t):
    """Forward 30-day implied vol (annualised, %) at time t years from now.

    Piecewise-linear through every observable point on the strip, then
    OU mean-reversion toward the long-run anchor past the last liquid contract.
    """
    if t <= 0:
        return VOL_KNOTS[0][1]
    for (ta, va), (tb, vb) in zip(VOL_KNOTS, VOL_KNOTS[1:]):
        if t <= tb:
            return va + (vb - va) * (t - ta) / (tb - ta)
    t_last, v_last = VOL_KNOTS[-1]
    vinf = MACRO["vix_longrun"]
    return vinf + (v_last - vinf) * math.exp(-KAPPA * (t - t_last))

def _fwd_vol_on(knots, t):
    """fwd_vol against an arbitrary knot set - used to re-anchor the curve to a
    different t=0 without mutating the published one."""
    if t <= 0:
        return knots[0][1]
    for (ta, va), (tb, vb) in zip(knots, knots[1:]):
        if t <= tb:
            return va + (vb - va) * (t - ta) / (tb - ta)
    t_last, v_last = knots[-1]
    vinf = MACRO["vix_longrun"]
    return vinf + (v_last - vinf) * math.exp(-KAPPA * (t - t_last))

def _horizon_vol_on(knots, T, n=4000):
    h, acc = T / n, 0.0
    for i in range(n):
        acc += _seg_var(_fwd_vol_on(knots, i * h), _fwd_vol_on(knots, (i + 1) * h), h)
    return math.sqrt(acc / T)

def horizon_vol(T, n=4000):
    """Annualised implied vol for a 0->T horizon via forward-variance integration."""
    return _horizon_vol_on(VOL_KNOTS, T, n)

# THE FORECAST HORIZONS (owner, 2026-10-27: "macroeconomic drivers ..., market trend ...,
# regional rankings ... and volatility deep analysis of 3, 5 and 10yrs forecast"). 5 and
# 10 years in v70; 1, 3, 5 and 10 in v68-v69; 3, 6 and 12 months plus the 10-year anchor
# until v67. Each view covers the years since the one before it: the 3-year view years
# 1-3, the 5-year view years 4-5, the 10-year view years 6-10.
HZ_KEYS = ("3Y", "5Y", HZ_LABEL)
HORIZONS = [("3Y", 3.0), ("5Y", 5.0), (HZ_LABEL, HORIZON_Y)]
VOL_TS = []
_prev = (0.0, 0.0)
for lbl, T in HORIZONS:
    iv = horizon_vol(T)
    # THE FORWARD VOL OF THE YEARS THIS VIEW GOVERNS (2026-10-26): the 3-year point is
    # the average over years 0-3, so years 2-3 alone are what is left once year 1 is
    # taken out of the variance. Built from the PRINTED implied figures, so a reader
    # reproduces it from the table.
    _ivr = round(iv, 2)
    fwd = math.sqrt((T * _ivr ** 2 - _prev[0] * _prev[1] ** 2) / (T - _prev[0]))
    VOL_TS.append({
        "label": lbl, "years": T, "from_years": _prev[0],
        "implied": _ivr, "forward": round(fwd, 2),
        "realised": round(iv - MACRO["variance_risk_premium"], 2),
        # 1-sigma and 2-sigma S&P-equivalent move over the horizon
        "move_1sd": round(iv * math.sqrt(T), 2),
        "move_2sd": round(2 * iv * math.sqrt(T), 2),
    })
    _prev = (T, _ivr)
SP_VOL_LT = next(v["implied"] for v in VOL_TS if v["label"] == HZ_LABEL)

# What the stale strip costs, measured rather than asserted. Re-anchor the curve to
# the spot of the VIX3M observation date, integrate to 0.25y, and compare with the
# market's own 3-month index. Same t=0, same strip, so the residual is the strip's
# age and nothing else. It is NEGATIVE, which means this model's implied vol sits
# below the market's - so its forecast drawdowns are, if anything, a touch small.
# RE-ANCHORED IN TIME AS WELL AS LEVEL (2026-10-10): each future's maturity is
# shortened by the days from the strip's quote date to the VIX3M date, so the
# comparison prices the same calendar window the published index does. Until
# then only the spot was moved, and the VIX3M pair predated the strip.
_V3M_EL = (_dt.date.fromisoformat(MACRO["vix3m_date"])
           - _dt.date.fromisoformat(VIX_QUOTE_DATE)).days / 365.0
VIX3M_MODEL = _horizon_vol_on([(0.0, MACRO["vix3m_spot"])]
                              + [(t - _V3M_EL, v) for t, v in VOL_KNOTS[1:] if t - _V3M_EL > 0], 0.25)
VIX3M_RESID = round((VIX3M_MODEL / MACRO["vix3m"] - 1) * 100, 2)
# THE TWO TOLERANCES THE PAGE QUOTES, as data (2026-10-20). Each was a literal in
# its check and typed again into the page's wording ("Past 20%"), so the check and
# the sentence describing it could drift apart - the defect the drawdown anchors
# had until 17 Oct. The page now reads both from vol_channel.
VIX3M_BOUND_PCT = 10.0       # |VIX3M_RESID| beyond this rejects the strip
STRIP_OVERTAKEN_PCT = 20.0   # a latest close this far from the strip's spot flags it
# The superseded 2 Oct board on the same test, same VIX3M date and spot.
_PREV_EL = (_dt.date.fromisoformat(MACRO["vix3m_date"])
            - _dt.date.fromisoformat(MACRO["vix_futs_prev_date"])).days / 365.0
_PREV_KN = [(vix_maturity(y, m, MACRO["vix_futs_prev_date"]) - _PREV_EL, lvl)
            for _, y, m, lvl in MACRO["vix_futs_prev_levels"]]
VIX3M_PREV_RESID = round((_horizon_vol_on([(0.0, MACRO["vix3m_spot"])]
                                          + [(t, v) for t, v in _PREV_KN if t > 0], 0.25)
                          / MACRO["vix3m"] - 1) * 100, 2)

# ----------------------------------------------------------------------------
# 3. REGIONAL MACRO-DRIVER SCORES
#    Researched and scored on 1-10 (the granularity the evidence supports, and the
#    scale every "why" note below is written against), then REPORTED on 1-5 using
#    the same endpoint-preserving rescale as the headline gauge: 1->1, 5.5->3.0,
#    10->5. The fund tilt coefficient is restated in 1-5 units so the rescale moves
#    no allocation: 0.30 per 1-10 point == 0.675 per 1-5 point.
#    Each score is an evidence-weighted judgement over the seven drivers in
#    DRIVERS below, blended across horizons by HZ_W.
#
#    HORIZON BLEND WEIGHTS: each view's share of the ten-year holding (below). The
#    judgement weights they replaced (3M 10 / 6M 15 / 12M 25 / 10Y 50 from 2026-09-08,
#    and 15/25/30/30 before) are in monitoring/CHANGELOG.md.
# ----------------------------------------------------------------------------

# EACH VIEW'S WEIGHT IS THE SHARE OF THE TEN-YEAR HOLDING IT GOVERNS (since 2026-10-26):
# the 3-year view years 1-3 (30%), the 5-year view years 4-5 (20%), the 10-year view
# years 6-10 (50%). A ten-year CAGR is
# (to first order) the average of its annual returns, so a view that holds for k of the
# ten years moves it by k/10 of its annual effect. The weights are DERIVED from the
# horizons, not chosen, and a check holds them there. (5 and 10 years carried 50 / 50 in
# v70; 1, 3, 5 and 10 carried 10 / 20 / 20 / 50 in v68-v69; the 3M/6M/12M/10Y split of
# 10/15/25/50 was a judgement.)
_HZ_YEARS = dict(HORIZONS)
HZ_W = {h: round((_HZ_YEARS[h] - (_HZ_YEARS[HZ_KEYS[i - 1]] if i else 0.0)) / HORIZON_Y, 2)
        for i, h in enumerate(HZ_KEYS)}

# ----------------------------------------------------------------------------
# 3b. VOLATILITY RAMP - the optimiser's volatility channel
#     Until 2026-09-05 each fund's volatility tilt was a hand-set constant: the
#     term structure was computed and displayed, but never actually fed the
#     allocation. It does now. The ramp is how far the horizon-blended implied
#     vol sits ABOVE spot - i.e. how much repricing the option market is still
#     pointing at - using the same horizon weights as the regional blend.
# ----------------------------------------------------------------------------
# READ ON FORWARD VOL (2026-10-26). Each horizon's weight is the share of the ten years
# it governs, so it is paired with the vol of THOSE years - the curve's forward vol over
# them - not with the 0-to-T average, which would count year 1 again inside the 3-, 5-
# and 10-year points. Over the four segments the forwards' variance averages back to the
# 10-year implied variance exactly; the blend of vols sits a hair below it.
VOL_BLEND = sum(v["forward"] * HZ_W[v["label"]] for v in VOL_TS)
# MEASURED FROM THE LONG-RUN LEVEL, NOT FROM SPOT. Corrected 2026-09-25. Every
# fund's base return is a long-run (LTCMA) return, and a long-run return already
# assumes average volatility - the 19.5 long-run VIX this model's own curve
# converges to. Measuring the ramp from TODAY's low spot credited the covered-call
# sleeve (+0.96pp) and charged Global Technology (-0.56pp) for volatility rising to
# a level both bases already assume: the rise was counted in the base and again in
# the tilt. The tilt is now the deviation of the horizon-blended curve from the
# long-run level - what the cycle view adds to, or takes from, a no-view base.
# ROUNDED TO THE PUBLISHED 2dp before any tilt is taken from it (2026-10-21): the
# unrounded -0.454 gave Global Technology +0.06 where the printed -0.45 x -0.122
# gives +0.05, so the page's own figures did not reproduce its tilt.
VOL_RAMP  = round(VOL_BLEND - MACRO["vix_longrun"], 2)
# The ramp the 10-year view alone reads: years 6-10 of the curve (Portfolio A's column).
VOL_RAMP_10 = round(VOL_TS[-1]["forward"] - MACRO["vix_longrun"], 2)
VOL_RAMP_REF = "long-run"

# Per-fund sensitivity, in pp of net CAGR per point of vol ramp. These are
# structural properties of each sleeve, not judgements about the current market:
#   ATRQIAP  +0.210  writes calls on ~78% of a Nasdaq-100 book whose own vol is
#                    ~1.22x the market; premium scales with implied vol, so a curve
#                    ABOVE the long-run level its base assumes is extra income, and
#                    one below it is less.
#   ATRGTEC  -0.122  highest vol beta (1.30) and the longest-duration equity
#                    here; a higher vol regime lifts the discount rate on distant
#                    cash flows and compresses the multiple.
#   ATRASEQ   0.000  the two effects cancel - a higher discount rate hurts, but
#                    at 10.5x forward the multiple is already compressed and the
#                    dividend tilt shortens effective duration.
#   ATRPHMM  +0.035  cash gains marginally as risk-off keeps the front end bid.
VOL_SENS = {"ATRPHMM": 0.035, "ATRQIAP": 0.210, "ATRASEQ": 0.000, "ATRGTEC": -0.122,
            # Global Dividend: no volatility channel is claimed
            "ATRGLDV": 0.000,
            # The six added 2026-10-22: none is built on selling or buying volatility,
            # and none is claimed - the channel is structural, not a view.
            "ATRGHCP": 0.000, "M_GINF": 0.000, "M_GEO": 0.000, "M_GCT": 0.000,
            "ATRAMIP": 0.000, "M_GALL": 0.000}



def to5(v10):
    """Linear rescale of a 1-10 research score onto 1-5. 1->1, 5.5->3.0, 10->5."""
    return round(1 + (v10 - 1) * 4 / 9, 2)


def rnd(x, ndigits=2):
    """Round-half-up (ties away from zero) to ndigits, unlike Python's built-in
    round() which rounds half-to-even. The driver-tilt scale factors (2.5,
    1.333...) can land a product exactly on a .5-at-the-next-digit boundary
    (e.g. 0.25*2.5=0.625, -0.05*2.5=-0.125), where banker's rounding silently
    diverges from the round-half-up convention every other verifier in this
    project assumes. Used for every tilt calculation so engine.py and the
    independent checklist/audit verifiers agree at the boundary."""
    q = Decimal(1).scaleb(-ndigits)
    return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))


NEUTRAL_5 = 3.0                 # the 1-5 neutral (= 5.5 on the 1-10 research scale)

# Each equity market's volatility relative to the S&P, used twice: by the fund
# volatilities below (where each sleeve then applies its own structure factor) and
# by the trend channel, which measures the MARKET. All three are assumptions, and
# CLAIMS.md records them as estimates.
NDX_SP_BETA = 1.22     # Nasdaq-100
ASIA_SP_BETA = 1.05    # Asia Pacific ex-Japan / Asia ex-Japan
TECH_SP_BETA = 1.30    # concentrated global technology
# Added 2026-10-22 with the 22-fund universe, ASSUMPTIONS like the three above:
HC_SP_BETA = 0.85      # global health care (S&P Global 1200 Health Care)
ACWI_SP_BETA = 1.00    # global equity (MSCI ACWI), a little below the S&P's long-run vol

# ----------------------------------------------------------------------------
# 3c. MARKET TREND - 1-year momentum, 3- and 5-year reversal, the trend channel
#     Added 2026-10-07 at the portfolio owner's instruction: the optimised
#     portfolios are to be built on market trend analysis as well as macro
#     sentiment, volatility and the regional rankings, at 3, 6 and 12 months
#     with the 10-year horizon.
#
#     WHAT IS MEASURED. Each equity sleeve's MARKET - the index its target fund
#     is run against, or the closest liquid proxy for it - over the three
#     trailing windows ending at the last completed month-end. Not the feeder's
#     own NAV: the question is which way the market is moving, and a manager's
#     stock selection is not a market trend.
#
#     HOW IT IS SCORED. A raw return means nothing until it is set against what
#     this model already expects of that market and how much the market moves.
#     Each window's return becomes a z-score against the sleeve's own long-run
#     drift and volatility:
#         z_h = (ln(1 + R_h) - h * ln(1 + mu)) / (sigma * sqrt(h))
#     so a +28% half-year counts for less in a 24%-vol market than in a 20%-vol
#     one, and a market that simply did what its long-run return says scores
#     neutral. It is mapped onto the same 1-5 scale as every other score here:
#     3 + z, clipped to [1, 5], so two standard deviations either way hits the
#     bound.
#
#     THE THREE HORIZONS (2026-10-27; 5/10 years in v70, 1/3/5/10 in v68-v69, 3, 6
#     and 12 months before). The evidence says a trend means different things at
#     different distances, and each view is scored by the years it covers:
#       MOMENTUM, YEAR 1. Time-series momentum - a market's own trailing 12 months
#            predicting its next 12 - is one of the best-documented effects in
#            finance, and it fades within about a year (Moskowitz, Ooi and Pedersen,
#            2012). Signal: z of the trailing four quarters.
#       REVERSAL, YEARS 2-5. The same study finds it partly reverses in years two to
#            five, and long-horizon losers outrun winners over the next three to five
#            years (De Bondt and Thaler, 1985). Signal: the mean z of the trailing 3-
#            and 5-year annualised returns, at half momentum's weight because reversal
#            is the weaker and less consistent effect.
#       NOTHING AFTER YEAR 5: over that distance a trend carries no signal this
#            model can defend, so the 10-year view is neutral.
#     A view's score is 3 + (its years of momentum / its years) x z(1y) - (its years
#     of reversal / its years) x 0.5 x z(3y, 5y): the 3-year view (years 1-3) is a
#     third momentum and two-thirds reversal, the 5-year view (years 4-5) all
#     reversal, the 10-year view (years 6-10) neither. The shares are DERIVED from the
#     horizons. The blend uses the same HZ_W weights as the regional rankings.
#
#     HOW MUCH IT IS WORTH. TREND_TILT_PER_PT is an ASSUMPTION, recorded as one.
#     The highest blend the scheme can produce is 4.0 (both trend views at the 5.0
#     bound, the anchor at 3.0). That is taken as worth about +3pp of return across
#     the ten-year mandate - 0.30pp a year - so 0.30 per point.
#     Under half the regional coefficient on purpose: momentum lasts a year and
#     reversal is uncertain, priced here into a ten-year forecast.
#     The "trend_off" what-if re-runs the optimiser without it, so its effect on
#     the allocation is published rather than asserted.
#
#     WHAT IT OVERLAPS. The regional rankings include a Valuation driver, and a
#     rally makes a market dearer: that lowers the regional score while it raises
#     this one. The two are allowed to pull against each other - that is the
#     value-against-momentum tension, not a double count.
#
#     The peso sleeve has no trend tilt. Its "trend" is the rate path, which the
#     rates channel already carries.
# ----------------------------------------------------------------------------
TREND_END = "2026-09-30"          # the last completed month-end before AS_OF
TREND_TILT_PER_PT = 0.30
TREND_ANCHOR = NEUTRAL_5          # the 10Y trend score: neutral, by the evidence above
TREND_Q = ("2025Q4", "2026Q1", "2026Q2", "2026Q3")      # oldest first
TREND_H = (("1Y", 4, 1.00),)     # momentum signal: label, quarters, years
TREND_LONG = (("3Y", 3.0), ("5Y", 5.0))   # reversal signals: label, years (annualised inputs)
TREND_REVERSAL = 0.5             # reversal's weight per unit of z, against momentum's 1.0
TREND_MOM_YEARS = (0.0, 1.0)     # the years momentum governs
TREND_REV_YEARS = (1.0, 5.0)     # the years reversal governs; nothing after
def _overlap(a, b, lo, hi):
    return max(0.0, min(b, hi) - max(a, lo))
# For each horizon, the share of the years it covers that momentum and reversal govern:
# DERIVED from the horizons (3Y: 1/3 and 2/3; 5Y: 0 and 1; 10Y: 0 and 0).
TREND_W = {}
_a = 0.0
for _h, _T in HORIZONS:
    TREND_W[_h] = {"mom": round(_overlap(_a, _T, *TREND_MOM_YEARS) / (_T - _a), 4),
                   "rev": round(_overlap(_a, _T, *TREND_REV_YEARS) / (_T - _a), 4)}
    _a = _T
TREND_VIEWS = tuple(h for h in HZ_KEYS if TREND_W[h]["mom"] or TREND_W[h]["rev"])
# The month-end the trailing 3- and 5-year returns are sought to. Each sleeve's own
# figures carry their own dates (trail_date): until 2026-10-26 the page said all five
# ran to this date, when health care's run to 31 Aug and the ACWI table shows none.
TREND_LONG_END = "2026-09-30"
TREND_INPUTS = {
    "ATRQIAP": {
        "market": "Nasdaq-100", "proxy": "Invesco QQQ, total return",
        "mu": MACRO["ltcma_us_eq"] + MACRO["ndx_growth_premium"], "beta": NDX_SP_BETA,
        # Monthly total returns, compounded to quarters. They reproduce the index
        # provider's own quarters to within a basis point (the factsheet is a
        # PRICE index, QQQ a total return net of its fee), and the 2025 months
        # compound to the 20.77% calendar-year return published beside them.
        "monthly": {"2025Q4": [4.78, -1.56, -0.67], "2026Q1": [1.23, -2.34, -4.84],
                    "2026Q2": [15.69, 10.57, -0.15], "2026Q3": [-6.57, 4.18, 3.32]},
        "cross_check": {"2026Q2": 27.74, "2026Q3": 0.58},
        "source": "PortfoliosLab, QQQ monthly total returns; Nasdaq-100 factsheet "
                  "(30 Sep 2026) for the Q2 and Q3 cross-check",
        # Annualised NAV total returns to 30 Sep 2026, the one source dated to the month-
        # end; PortfoliosLab (26.61%, 14.54%) and FinanceCharts (26.35%, 15.87%), undated,
        # sit 1.4-1.8pp lower on 3 years.
        "trail_ann": {"3Y": 28.0, "5Y": 16.3},
        "trail_source": "AAII ETF Evaluator, QQQ at NAV to 30 Sep 2026",
        "trail_date": {"3Y": "2026-09-30", "5Y": "2026-09-30"},
    },
    "ATRASEQ": {
        "market": "MSCI AC Asia ex Japan",
        "proxy": "the index in USD; the target fund's Asia Pacific ex-Japan benchmark also "
                 "holds Australia, which no monthly series reachable here isolates",
        "mu": MACRO["ltcma_em_eq"] + MACRO["asia_rerating"], "beta": ASIA_SP_BETA,
        # Quarters where a quarterly review states one; Q3 from its months, which
        # Schroders' Q3 review describes as "a slight decline" - what they compound
        # to. The September month is from a single source; its sensitivity is
        # measured below (TREND_ALT) rather than assumed small.
        "quarterly": {"2025Q4": 4.3, "2026Q1": -1.13, "2026Q2": 27.7},
        "monthly": {"2026Q3": [-3.18, 3.3, -0.25]},
        "cross_check": {},
        "source": "Schroders quarterly markets reviews (Q4 2025 +4.3%, Q2 2026 +27.7%) "
                  "and monthly reviews (Aug 2026 +3.3%); Shikhara CIO's Desk (Q1 2026 "
                  "-1.13%, Jul 2026 -3.18%); MSCI index factsheet (Sep 2026 -0.25%)",
        # The index ETF's (AAXJ) standardised returns to 30 Sep 2026; iShares' own table,
        # dated 19 Oct, reads 24.8% and 8.65%. An ETF's return is net of its fee, so the
        # index itself ran a little higher.
        "trail_ann": {"3Y": 24.8, "5Y": 8.6},
        "trail_source": "ETF Research Center, AAXJ standardised performance to 30 Sep 2026; "
                        "iShares AAXJ performance table (19 Oct 2026)",
        "trail_date": {"3Y": "2026-09-30", "5Y": "2026-09-30"},
    },
    "ATRGTEC": {
        "market": "Global technology, S&P Global 1200 IT",
        "proxy": "iShares Global Tech ETF (IXN), total return",
        "mu": MACRO["ltcma_us_eq"] + MACRO["tech_growth_premium"] - MACRO["tech_derating"],
        "beta": TECH_SP_BETA,
        # The target fund's benchmark is MSCI ACWI IT; IXN tracks the S&P Global
        # 1200 IT, the closest proxy with a published monthly series. The Jan-Aug
        # 2026 months compound to the 28.22% year-to-date published with them.
        "monthly": {"2025Q4": [7.11, -5.47, 1.39], "2026Q1": [2.03, -0.35, -6.36],
                    "2026Q2": [20.29, 19.58, 0.60], "2026Q3": [-8.17, 1.35, 4.4]},
        "cross_check": {},
        "source": "PortfoliosLab, IXN monthly total returns (September 2026 from a "
                  "second performance tracker)",
        # THE ONE TRAILING INPUT SOURCES DISAGREE ON. Schwab's page dated 30 Sep reads
        # 37.6% and 22.0%, but its one-year 45.0% is 7.6pp above what the monthly series
        # above compounds to (37.43%), so it is not on this channel's basis; it is run as
        # the alternative (TREND_ALT). The figures used agree across three trackers.
        "trail_ann": {"3Y": 31.4, "5Y": 18.8},
        "trail_source": "Yahoo Finance trailing returns (3-year 31.38% to 6 Oct 2026, 5-year "
                        "18.79% to 1 Sep); PortfoliosLab (31.25%, 18.78%) and MyPlanIQ (5-year "
                        "18.85% to 24 Aug) agree",
        "trail_date": {"3Y": "2026-10-06", "5Y": "2026-09-01"},
    },
    # ---- added 2026-10-22 with the 22-fund universe ----
    "ATRGHCP": {
        "market": "Global health care, S&P Global 1200 Health Care",
        "proxy": "iShares Global Healthcare ETF (IXJ), total return; the target fund's "
                 "benchmark is MSCI ACWI Health Care, which no monthly series reachable here gives",
        "mu": MACRO["ltcma_global_eq"], "beta": HC_SP_BETA,
        # The Q4 2025 months compound to +10.6%: BlackRock has global health care up "more
        # than 10%" in the quarter, leading every sector. iShares' own NAV returns to 30 Sep
        # 2026 - September -1.96%, year-to-date 5.93%, one year 16.81% - against these
        # months' -2.03%, 5.79% and 16.98%: within 0.2pp, the gap between price and NAV.
        # (AAII's "20.7% year-to-date to 31 Aug" agrees with no other source and is not used.)
        "monthly": {"2025Q4": [2.85, 8.30, -0.73], "2026Q1": [1.41, 2.98, -8.03],
                    "2026Q2": [-0.65, 1.69, 5.03], "2026Q3": [1.91, 3.97, -2.03]},
        "cross_check": {},
        "source": "PortfoliosLab, IXJ monthly total returns; BlackRock (Q4 2025) and iShares' "
                  "NAV returns to 30 Sep 2026 as cross-checks",
        # A month earlier than the others: no source reached gives the 30 Sep figures.
        "trail_ann": {"3Y": 8.6, "5Y": 4.8},
        "trail_source": "AAII, IXJ annualised NAV returns to 31 Aug 2026; Yahoo Finance "
                        "(8.58%, 4.80% to 21 Sep) agrees",
        "trail_date": {"3Y": "2026-08-31", "5Y": "2026-08-31"},
    },
    "M_GEO": {
        "market": "Global equity, MSCI ACWI",
        "proxy": "the index in USD; the target fund, Allianz Thematica, is a thematic "
                 "global equity fund run against MSCI ACWI",
        "mu": MACRO["ltcma_global_eq"], "beta": ACWI_SP_BETA,
        # The index's own quarters, all four (2026-10-22). Aristotle Capital: Q4 2025 +3.29%
        # (Maseco +3.4%), Q1 2026 -3.20%, Q2 +14.93% with 11.25% for the half - which
        # -3.20% and +14.93% compound to. Q3 +1.6% and 13.0% for the year to date (Maseco,
        # Goldstone): 11.25% and 1.6% compound to 13.03%. Until 2026-10-22 the 2026
        # quarters were the ETF's from ETFreplay (-2.21 / 14.17 / 1.14), one source whose
        # table also printed a Q4 2026 that cannot exist yet, and up to 1pp off the index.
        "quarterly": {"2025Q4": 3.29, "2026Q1": -3.20, "2026Q2": 14.93, "2026Q3": 1.6},
        "cross_check": {},
        "source": "Aristotle Capital quarterly commentaries (Q4 2025 - Q2 2026, MSCI ACWI); "
                  "Maseco and Goldstone Q3 2026 market reviews",
        # The index ETF (ACWI); the cached page does not show its as-of date, and Yahoo
        # Finance and Dividend.com agree within 0.5pp.
        "trail_ann": {"3Y": 21.75, "5Y": 11.62},
        "trail_source": "iShares MSCI ACWI ETF performance table; Yahoo Finance and "
                        "Dividend.com agree",
        "trail_date": {"3Y": None, "5Y": None},    # the cached table shows no as-of date
    },
}
# The inputs sources disagree on materially: AAXJ, the ETF on the same Asia index,
# published 25.73% for the quarter Schroders puts at 27.7%; and Schwab's 30 Sep page has
# Global Technology's 3- and 5-year returns at 37.6% and 22.0%. The trend is re-run on
# both alternatives at once and the allocation checked against it.
TREND_ALT = {"ATRASEQ": {"2026Q2": 25.73}, "ATRGTEC": {"3Y": 37.6, "5Y": 22.0}}

def _compound(xs):
    p = 1.0
    for x in xs:
        p *= 1 + x / 100
    return (p - 1) * 100

def trend_build(fid, override=None):
    """The published trend record for one sleeve, built on the reader's route:
    every figure from the PRINTED (rounded) figures before it."""
    t = TREND_INPUTS[fid]
    q = {}
    for k in TREND_Q:
        if k in t.get("monthly", {}):
            q[k] = round(_compound(t["monthly"][k]), 2)
        else:
            q[k] = t["quarterly"][k]
    trail = dict(t["trail_ann"])
    for k, v in (override or {}).items():
        if k in TREND_Q:
            q[k] = v
        else:
            assert k in trail, k
            trail[k] = v
    # REALISED, NOT IMPLIED (corrected 2026-10-10). A trailing return is a realised
    # outcome, so its z-score divides by realised volatility: the 10Y implied level
    # less the variance risk premium this model already publishes. Dividing by
    # implied vol, as the first version did, shrank every z by ~18% - the premium
    # options charge over delivered volatility, counted as if it were risk.
    mu = round(t["mu"], 2)
    sigma = round(t["beta"] * (SP_VOL_LT - MACRO["variance_risk_premium"]), 2)
    ret, z, score = {}, {}, {}
    for lbl, nq, yrs in TREND_H:
        ret[lbl] = round(_compound([q[k] for k in TREND_Q[-nq:]]), 2)
        z[lbl] = round((math.log(1 + ret[lbl] / 100) - yrs * math.log(1 + mu / 100))
                       / (sigma / 100 * math.sqrt(yrs)), 2)
    # The 3- and 5-year returns are ANNUALISED, so h * ln(1 + mu) on the cumulative
    # return becomes sqrt(h) * (ln(1 + R) - ln(1 + mu)) / sigma - the same z.
    for lbl, yrs in TREND_LONG:
        ret[lbl] = trail[lbl]
        z[lbl] = round(math.sqrt(yrs) * (math.log(1 + ret[lbl] / 100) - math.log(1 + mu / 100))
                       / (sigma / 100), 2)
    z_rev = round(sum(z[l] for l, _ in TREND_LONG) / len(TREND_LONG), 2)
    for h in HZ_KEYS:
        w = TREND_W[h]
        score[h] = (round(min(5.0, max(1.0, 3.0 + w["mom"] * z[TREND_H[0][0]]
                                       - w["rev"] * TREND_REVERSAL * z_rev)), 2)
                    if h in TREND_VIEWS else TREND_ANCHOR)
    blend = round(sum(score[h] * w for h, w in HZ_W.items()), 2)
    return {"market": t["market"], "proxy": t["proxy"], "source": t["source"],
            "mu": mu, "beta": t["beta"], "sigma": sigma,
            "quarters": q, "monthly": t.get("monthly", {}), "cross_check": t["cross_check"],
            "trail_source": t["trail_source"], "trail_date": t["trail_date"],
            "ret": ret, "z": z, "z_rev": z_rev, "score": score, "blend": blend,
            "tilt": rnd((blend - TREND_ANCHOR) * TREND_TILT_PER_PT)}

TREND = {fid: trend_build(fid) for fid in TREND_INPUTS}
TREND_ALT_BUILT = {fid: trend_build(fid, ov) for fid, ov in TREND_ALT.items()}

# THE 3-, 5- AND 10-YEAR SCORES (2026-10-27). The 3-year score is each region's outlook
# averaged over years 1-3, the 5-year score over years 4-5, each researched from the
# year-by-year evidence (the Fed's own rate path, inflation pricing and BSP's forecasts by
# year, the IMF's growth path, cyclically adjusted valuations and the Brent curve by
# contract year) weighed against the cycle now. The 10-year anchor is unchanged. Each
# region's note closes with the reasoning for its 3- and 5-year scores.
def _a_an(x):
    """The article a number takes when read aloud: an 8.07%, an 11%, an 18%; a 7.2%."""
    w = str(x).split(".")[0].lstrip("-")
    return "an" if w.startswith("8") or w in ("11", "18") else "a"

def _fed_26_27():
    """The Fed's end-2026 and end-2027 medians in one phrase, joined only while they agree."""
    a, b = MACRO["fed_dot_2026"], MACRO["fed_sep_2027"]
    return f"{a}% at the end of 2026 and 2027" if a == b else f"{a}% at the end of 2026 and {b}% at the end of 2027"

# The day of a dated input, "29 Oct" (v84): a note's date moves with the value it dates.
def _dday(k):
    d_ = _dt.date.fromisoformat(MACRO[k])
    return f"{d_.day} {d_:%b}"
_u10 = dict(MACRO["ust_10y_history"])

REGIONS = {
    "US": {
        "3Y": 5.5, "5Y": 6.25, HZ_LABEL: 6.5,
        "why": (f"Held. On {_dday('equity_date')} the S&P fell {abs(MACRO['spx_chg_pct']):.2f}% to {MACRO['spx_close']:.2f}, its "
                f"first fall in four sessions, the Nasdaq {abs(MACRO['nasdaq_chg_pct']):.2f}% to {MACRO['nasdaq_close']:.2f} and the "
                f"Dow {abs(MACRO['dow_chg_pct']):.2f}% to {MACRO['dow_close']:.2f}, as Alphabet's quarter revived the question of what "
                "the AI build-out earns. The economy is not the problem: GDP grew at a "
                f"{MACRO['us_gdp_q3']}% annual rate in the third quarter against {MACRO['us_gdp_q3_consensus']}% expected, but "
                f"September core PCE was {MACRO['us_core_pce_sep']}% on the year and producer prices rose 1.3% in the month; "
                f"{MACRO['fed_oct_votes_hike']} Fed voters wanted a hike on 28 Oct, FedWatch has one by December at "
                f"{MACRO['fed_hike_odds_dec']}% on {_dday('fed_hike_odds_dec_date')}, and the 10-year closed at "
                f"{MACRO['ust_10y']:.2f}% on {_dday('ust_10y_date')}. FactSet has {MACRO['factset_beat_pct']}% of reporting "
                f"companies beating estimates and the index on {MACRO['spx_fwd_pe']}x forward earnings, below its five- and "
                "ten-year averages. The consumer is the weak point: Michigan sentiment at 46.3, retail sales 0.8% in "
                f"September, the saving rate down to {MACRO['us_saving_rate_sep']}%. The anchor holds at 6.5 on two structural "
                "points: the US is a net energy EXPORTER, a relative tailwind with "
                f"Brent +{MACRO['brent_yoy']:.1f}% y/y, and NDX at 22.4x forward on its last verified reading sat "
                "below its 10y and 5y averages. J.P. Morgan's "
                f"{MACRO['ltcma_edition']} assumptions lift US large caps to "
                f"{MACRO['ltcma_us_eq']}% from {MACRO['ltcma_us_eq_prev']}%; that is already "
                "in every US fund's base return, so it does not move the anchor as well. "
                "THREE YEARS: 5.5, a point below the 6.5 anchor. The Fed's own path keeps "
                f"policy above its {MACRO['fed_sep_longrun']}% long-run rate through all three - "
                f"{_fed_26_27()}, {MACRO['fed_sep_2028']}% at end-2028 - "
                f"and the cyclically adjusted P/E is {MACRO['cape']}, against a {MACRO['cape_high']} record "
                f"and a {MACRO['cape_median']} long-run median: a valuation that has historically cost "
                "the next years' returns, whatever the forward multiple says. Against them, earnings "
                "growing at a record pace and the energy-exporter edge. FIVE YEARS (years 4-5): "
                f"6.25, as policy reaches neutral ({MACRO['fed_sep_2029']}% at end-2029) and the "
                "AI spending has either paid or been digested. Most houses' decade forecasts "
                "favour non-US over US equities on the same valuation."),
    },
    "EUROPE": {
        "3Y": 3.75, "5Y": 4.5, HZ_LABEL: 4.5,
        "why": f"Held. The ECB held its deposit rate at {MACRO['ecb_depo']:.2f}% on {_dday('ecb_oct_decision_date')}, after the 10 Sep hike, with September inflation confirmed at 3.8% (energy 18.8%, core 2.5%), and made no commitment on December; Lagarde said she will step down early, in February. The 10-year OAT-Bund spread eased to 135.5bp on 14 Oct from about 140bp as the Assembly took up a budget meant to cut the deficit to 5.0% of GDP from 5.4%. Europe is the largest net energy importer here, facing Brent +" f"{MACRO['brent_yoy']:.1f}% y/y against IMF growth of 0.9%; the offset is real - at 15.4x forward it is the cheapest large market after Asia. "
                 "THREE YEARS: 3.75. The largest energy importer pays the most while oil stays "
                 f"high - December 2027 Brent was quoted at ${MACRO['brent_dec2027_hi']} on 22 Oct (another "
                 f"table has ${MACRO['brent_dec2027_lo']}) - "
                 "and growth starts at 0.9% under an ECB that hiked into it; a 15.4x market is the "
                 "offset. FIVE YEARS (years 4-5): 4.5, at the anchor, as the shock fades - on 15 Oct "
                 f"the Brent curve settled near ${MACRO['brent_dec2029']} for December 2029 and "
                 f"${MACRO['brent_dec2030']} for December 2030.",
    },
    "ASIA": {
        # TEN-YEAR ANCHOR 7.5 -> 7.0 (2026-10-21): half its case was the base return.
        # It cited J.P. Morgan's EM equity assumption, which IS the Asia fund's base,
        # so the same number was counted in the base and again in the tilt.
        "3Y": 6.5, "5Y": 7.0, HZ_LABEL: 7.0,
        "why": ("Held; the ten-year anchor at 7.0 since 21 Oct. The AI trade turned on Asia's chipmakers: on "
                f"{_dday('kospi_latest_date')} the KOSPI fell {abs(MACRO['kospi_latest_chg_pct']):.2f}% to "
                f"{MACRO['kospi_latest']:,.2f} and the Nikkei {abs(MACRO['nikkei_latest_chg_pct']):.2f}% to "
                f"{MACRO['nikkei_latest']:,.2f} after Alphabet's quarter, and the BoJ held at {MACRO['boj_rate']:.2f}% with a "
                f"hike flagged for December. On the 29th the KOSPI had slipped {abs(MACRO['kospi_29oct_chg_pct']):.2f}% as "
                f"Samsung fell on its detailed quarter, while the Nikkei rose {MACRO['nikkei_29oct_chg_pct']:.2f}%; on the "
                f"28th the KOSPI jumped {MACRO['kospi_28oct_chg_pct']:.2f}% as SK hynix reported a record quarter - operating "
                f"profit of {MACRO['skhynix_q3_op_tn']:.1f}tn won, up {MACRO['skhynix_q3_op_yoy']}% on a year - and about "
                f"{MACRO['skhynix_returns_2026_tn']}tn won of shareholder returns for 2026. The KOSPI is "
                f"{MACRO['kospi_off_2oct_pct']}% below its 7003.74 close of 2 Oct. China grew 4.5% in the third quarter "
                "against 4.4% expected, on exports. The earnings did not break: TSMC's third-quarter profit rose 68.7% to a "
                "record, and Samsung's quarter was a record 107.4tn won. Oil is the importers' "
                f"problem, Brent at ${MACRO['brent']:.2f}, with the yen near 158.48. The anchor was cut "
                "because half its case was the base return: it cited J.P. Morgan's EM "
                "equity assumption as the highest of any equity block, but that assumption "
                "is the Asia fund's base, so it was counted twice - and the "
                f"{MACRO['ltcma_edition']} edition cuts it to {MACRO['ltcma_em_eq']}% from "
                f"{MACRO['ltcma_em_eq_prev']}%, below US large caps. What remains is "
                "valuation: 10.5x forward before the fall against consensus EPS growth of "
                "~52% and ~28% is a two-decade-wide discount. THREE YEARS: 6.5, half a point "
                "below the 7.0 anchor - the October selling and an importer's oil bill weigh "
                "on the first years. FIVE YEARS (years 4-5): 7.0, at the anchor, as earnings "
                "that grew into a discounted multiple re-rate it."),
    },
    "PHILIPPINES": {
        "3Y": 5.25, "5Y": 5.75, HZ_LABEL: 5.5,
        "why": ("Held. BSP raised its policy rate 50bp to 5.50% on 22 Oct, "
                "twice the 25bp that 20 of 22 analysts expected - its fourth straight hike "
                "and the first half-point since February 2023 - and the 26 Oct auction repriced "
                "to it: 91-day bills jumped 63.2bp to 6.624%, 182-day bills 20.1bp to 6.43% and "
                "364-day bills 13.9bp to 6.583%, the two longer tenors under-awarded. The peso, "
                f"after a record {MACRO['usdphp_record']:.2f} on 27 Oct, recovered to {MACRO['usdphp']} on "
                f"{_dday('usdphp_date')}, {abs(MACRO['usdphp_chg_ctvo']):g} centavos "
                f"{'stronger' if MACRO['usdphp_chg_ctvo'] < 0 else 'weaker'} on the day, as the President signalled "
                f"support and the Fed held - still {_a_an(MACRO['usdphp_ytd_pct'])} {MACRO['usdphp_ytd_pct']}% loss of "
                "purchasing power against the dollar this year. Governor Remolona left the 17 Dec meeting open, and says "
                "BSP will not defend a level and intervenes only to cushion excessive moves. The PSEi rose "
                f"{MACRO['psei_chg_pct']:.2f}% to {MACRO['psei']:.2f} on {_dday('psei_date')}, after falling "
                f"{abs(MACRO['psei_28oct_chg_pct']):.2f}% on the 28th on inflation fears; its 2026 low is "
                f"{MACRO['psei_2026_low']}, on 8 Oct. September inflation was 7.2%, core 4.7%: against it every tenor's real "
                "yield is still below zero, though the gap closed by up to 63bp in one auction. This sleeve's job - zero "
                "duration risk and high nominal carry - is unimpaired. Its purchasing "
                f"power is not. THREE YEARS: 5.25. BSP sees inflation at {MACRO['bsp_cpi_2026']}% this "
                f"year and {MACRO['bsp_cpi_2027']}% next, then {MACRO['bsp_cpi_2028']}% in 2028, inside its "
                "2-4% target, while the IMF has growth recovering to "
                f"{MACRO['imf_ph_2027']}% in 2027 from {MACRO['imf_ph_2026']}%: the real carry is about "
                "nil for two of the three years. FIVE YEARS (years 4-5): 5.75, a little above "
                "neutral, as a policy rate set against 6% inflation meets inflation back near 3%."),
    },
}
# to5() is affine and HZ_W sums to 1, so blending then rescaling equals rescaling
# then blending - EXACTLY. It stops being true the moment either side is rounded,
# and to5() rounds to 2dp. Blending on the research scale and rescaling the result
# printed a US blend of 3.15 while a reader blending the four REPORTED scores with
# the printed horizon weights got 3.14. One region in four failed to reconcile, on
# the page, for as long as anyone had been looking.
# The reader's route is now the definition: the blend is the horizon-weighted
# average of the values actually printed. blend_10 is still published on the
# research basis for audit, and is still checked against the research-scale
# horizons - it is simply no longer to5() of itself.  (Audit 2026-09-20.)
for r in REGIONS.values():
    r["blend_10"] = round(sum(r[h] * w for h, w in HZ_W.items()), 2)
    for h in HZ_KEYS:
        r[h + "_10"] = r[h]      # research basis, kept so the rescale stays auditable
        r[h] = to5(r[h])         # reported value, 1-5
    r["blend"] = round(sum(r[h] * w for h, w in HZ_W.items()), 2)

# ----------------------------------------------------------------------------
# 4. BROAD MACRO GAUGE (1-5) - weighted composite of seven drivers
#    Drivers are researched and scored on a 1-10 scale (that is the granularity the
#    underlying evidence supports). The HEADLINE gauge is reported 1-5: endpoints map
#    to endpoints, so the 1-10 neutral of 5.5 lands exactly on the 1-5 neutral of 3.0.
# ----------------------------------------------------------------------------

DRIVERS = [
    ("Monetary policy & liquidity", 0.2, 2.0,
     f"HELD at 2.0. The Fed held at {MACRO['fed_funds_lower']:.2f}-{MACRO['fed_funds_upper']:.2f}% on 28 Oct, "
     f"{MACRO['fed_oct_votes_hold']}-{MACRO['fed_oct_votes_hike']}, Governor Cook and Cleveland's Hammack for a hike, and "
     "the statement calls inflation elevated. September's core PCE then rose "
     f"{MACRO['us_core_pce_mom_sep']}% on the month and {MACRO['us_core_pce_sep']}% on the year, headline "
     f"{MACRO['us_pce_mom_sep']}% and {MACRO['us_pce_sep']}%, and FedWatch has a hike by the 9 Dec meeting at "
     f"{MACRO['fed_hike_odds_dec']}% on {_dday('fed_hike_odds_dec_date')}, from {MACRO['fed_hike_odds_dec_prev']}% on the "
     f"28th. On official closes the 10-year was {_u10['2026-10-27']:.2f}% on the 27th, {_u10['2026-10-28']:.2f}% on the "
     f"28th and {MACRO['ust_10y']:.2f}% on the 29th, with the 2-year last at {MACRO['ust_2y']:.2f}% ({_dday('ust_2y_date')}) "
     f"and the 30-year at {MACRO['ust_30y']:.2f}% ({_dday('ust_30y_date')}) - all below the 7 Oct intraday high of 5.365%, "
     "above the 5 Oct peak of 5.349% and the highest since April 2002. "
     f"The ECB held at {MACRO['ecb_depo']:.2f}% on 29 Oct and the BoJ, a day later, at {MACRO['boj_rate']:.2f}%, "
     f"{MACRO['boj_oct_vote_hold']}-{MACRO['boj_oct_vote_hike']} with a vote for {MACRO['boj_oct_dissent_rate']}% and a "
     "hike flagged for December. Manila repriced to BSP's 50bp hike to 5.50%: at the 26 Oct auction 91-day bills "
     "jumped 63.2bp to 6.624%, 182-day bills 20.1bp to 6.43% and 364-day bills 13.9bp to 6.583%. Held: the hold "
     "and a firm core were both in the December-hike path the score assumed."),
    ("Inflation trajectory", 0.15, 2.0,
     f"HELD at 2.0. September PCE prices rose {MACRO['us_pce_mom_sep']}% on the month and {MACRO['us_pce_sep']}% on "
     f"the year, from {MACRO['us_pce_aug']}% in August; core rose {MACRO['us_core_pce_mom_sep']}% and "
     f"{MACRO['us_core_pce_sep']}%, from {MACRO['us_core_pce_aug']}%, in line with forecasts. That followed September "
     "PPI up 1.3%, the largest monthly rise since March 2022, and 6.3% on the year (core 0.5% and 5.0%), and CPI of "
     f"3.7% (core 2.6%). Brent settled at ${MACRO['brent']:.2f} on {_dday('brent_date')}, "
     f"{'up' if MACRO['brent_chg_pts'] > 0 else 'down'} ${abs(MACRO['brent_chg_pts']):.2f}, below the "
     f"${MACRO['brent_high']} of the 23rd, its highest close since 29 April, and {abs(MACRO['brent_wk_chg_pct'])}% "
     f"{'higher' if MACRO['brent_wk_chg_pct'] > 0 else 'lower'} on the week, and {MACRO['brent_yoy']:.1f}% above the "
     f"${MACRO['brent_yr_ago']:.2f} of a year earlier; December WTI settled at ${MACRO['wti_settle']:.2f} on "
     f"{_dday('wti_date')}. The euro area is at 3.8% (core 2.5%) and the Philippines at 7.2%. Held: core is firming, "
     "not running away, and most of the jump is energy passing through, not yet wages."),
    ("Growth momentum", 0.15, 4.0,
     f"HELD at 4.0. US GDP grew at a {MACRO['us_gdp_q3']}% annual rate in the third quarter, against "
     f"{MACRO['us_gdp_q3_consensus']}% expected and {MACRO['us_gdp_q2']}% in the second, on inventories, equipment and "
     "consumer and government spending - but September's real spending was flat and the saving rate fell to "
     f"{MACRO['us_saving_rate_sep']}%, the lowest in almost four years. China grew 4.5% on the year against 4.4% "
     "expected, on exports; its September retail sales rose only 1.1%. Michigan sentiment, at 46.3 in October's "
     "first read, is near May's record low of 44.8; ISM services (54.9) and manufacturing (54.5) stayed in expansion "
     "in September. Philippine growth was 2.6% in the first half. Held: a beat built on inventories, with a stretched "
     "consumer behind it, is not a turn in the cycle."),
    ("Corporate earnings", 0.2, 7.0,
     "HELD at 7.0, still the strongest pillar; the market is pricing the financing, not the profits. FactSet's "
     f"23 Oct count has {MACRO['factset_reported_pct']}% of the S&P reported and {MACRO['factset_beat_pct']}% beating "
     f"estimates - by {MACRO['factset_surprise_pct']}% in aggregate, against a {MACRO['factset_surprise_5y']}% "
     f"five-year average - with third-quarter growth blended at {MACRO['factset_q3_growth']}%, from "
     f"{MACRO['factset_q3_growth_prev']}%; health care is the one sector with earnings down on a year. On 29 Oct "
     "Alphabet took the largest one-day fall in market value in its history after a revenue miss and negative free "
     f"cash flow on its AI spending, and the Nasdaq fell {abs(MACRO['nasdaq_chg_pct']):.2f}%; on the 30th the KOSPI "
     f"fell {abs(MACRO['kospi_latest_chg_pct']):.2f}% and the Nikkei {abs(MACRO['nikkei_latest_chg_pct']):.2f}%. The "
     f"suppliers' numbers are records: SK hynix's third-quarter operating profit was {MACRO['skhynix_q3_op_tn']:.1f}tn "
     f"won, up {MACRO['skhynix_q3_op_yoy']}% on a year, with about {MACRO['skhynix_returns_2026_tn']}tn won of "
     "shareholder returns planned for 2026; TSMC's net income rose 68.7% to NT$763.06bn, above the NT$746.34bn "
     "expected; Samsung's quarter was a record 107.4tn won. Asia ex-Japan EPS of ~+52% (2026) and ~+28% (2027) "
     "stands. Held: the profits keep coming; what is being questioned is the return on the spending that buys them."),
    ("Valuation support", 0.1, 8.0,
     f"HELD at 8.0: FactSet had the S&P on {MACRO['spx_fwd_pe']}x forward earnings on 23 Oct, below its five-year "
     f"({MACRO['spx_fwd_pe_5y']}x) and ten-year ({MACRO['spx_fwd_pe_10y']}x) averages and the "
     f"{MACRO['spx_fwd_pe_q3end']:.1f}x of 30 Sep. The S&P closed at {MACRO['spx_close']:.2f} on {_dday('equity_date')}, "
     f"{MACRO['spx_off_record_pct']}% below its 7818.93 record of 6 Oct. Asia was on 10.5x forward before its October "
     f"fall and is cheaper on the same earnings: the KOSPI closed at {MACRO['kospi_latest']:,.2f} on "
     f"{_dday('kospi_latest_date')}, {MACRO['kospi_off_2oct_pct']}% below its 2 Oct close. NDX at 22.4x forward on its "
     "last verified reading sat below its 10y (22.9x) and 5y (24.7x) averages - two newer readings disagree "
     f"({MACRO['ndx_fwd_pe_disputed'][0]:.1f}x and {MACRO['ndx_fwd_pe_disputed'][1]:.1f}x) and are not carried; Europe "
     "is at 15.4x. Held: cheaper than its averages on the one multiple re-verified, and the rest only cheaper since."),
    # RAISED 2.5 -> 2.75 (2026-10-21); HELD 2026-10-22 as the VIX eased again but
    # Asia sold off and the Gulf escalated. CUT 2.75 -> 2.5 (2026-10-23): the VIX's
    # 14% jump on the AI sell-off undid the calm the raise rested on. HELD since.
    ("Volatility & risk appetite", 0.1, 2.5,
     f"HELD at 2.5. The VIX rose {MACRO['vix_latest_chg_pct']}% to {MACRO['vix_latest']:.2f} on "
     f"{_dday('vix_latest_date')} as Alphabet's quarter hit tech, after three falls into the Fed's hold "
     f"({abs(MACRO['vix_reported_moves']['2026-10-28'])}% on the 28th, {abs(MACRO['vix_reported_moves']['2026-10-27'])}% "
     f"on the 27th) - still under the long-run {MACRO['vix_longrun']} and well off its {MACRO['vix_latest_high']} high "
     f"of 16 Oct. Asia took the shock on the 30th: the KOSPI fell {abs(MACRO['kospi_latest_chg_pct']):.2f}%, tripping a "
     f"sell-side sidecar, and the Nikkei {abs(MACRO['nikkei_latest_chg_pct']):.2f}%. No full futures strip after the "
     "20 Oct settlements has been reached, so the curve stays quoted there - November "
     f"{MACRO['vix_fut_sep']} and December {MACRO['vix_fut_dec']}, above that day's spot, the ordinary upward slope - "
     f"and mean-reverts to the long run beyond. Tested against that day's VIX3M of {MACRO['vix3m']} it gives "
     f"{VIX3M_MODEL:.2f} at three months, {abs(VIX3M_RESID):.2f}% {'below' if VIX3M_RESID < 0 else 'above'}, inside "
     f"the {VIX3M_BOUND_PCT:.0f}% bound; the 5 Oct strip it replaced read {abs(VIX3M_PREV_RESID):.2f}% "
     f"{'below' if VIX3M_PREV_RESID < 0 else 'above'} on the same test. On forward vol the curve sits at "
     f"{VOL_BLEND:.2f}, {abs(VOL_RAMP):.2f} {'below' if VOL_RAMP < 0 else 'above'} the long run. Held: one up day "
     "after three down is not a regime, and the Asian sell-off is an earnings question, not a volatility one."),
    ("Geopolitics & energy", 0.1, 1.5,
     "HELD at 1.5; the threat widened again, and the barrels have not yet shrunk. On 30 Oct Iran's Revolutionary "
     "Guard claimed that tankers leaving the Strait by unauthorised routes had struck mines and caught fire; US Central "
     "Command said it had cleared mines from the main transit routes and called the claim false, and UKMTO reported "
     "explosives attached to a tanker off Khasab, Oman (CNBC; AP; Gulf News). On the 28th the US had reportedly told "
     "Gulf states to prepare for a short, intense campaign against Iran after the 3 November midterms (the Wall "
     "Street Journal, via CNBC), and the Houthis claim new attacks on Saudi airports and oil facilities while Qatari "
     f"mediators are in Tehran. Brent settled at ${MACRO['brent']:.2f} on {_dday('brent_date')}, below the "
     f"${MACRO['brent_high']} of the 23rd, its highest close since 29 April. Read it on VOLUME, the measure this note "
     "goes by: Kpler had oil through Hormuz, with Gulf of Oman transfers, at about 14 mb/d in the week to 18 Oct, 82% "
     "of pre-war on preliminary figures, and the Gulf's exports by every route above 24 mb/d against 23.3 pre-war; no "
     "later week has been published. On 22 Sep Saudi Arabia restarted the 1200 km East-West pipeline that bypasses "
     "the Strait, and the export volumes since bear out that it runs. Vessel counts disagree and are not supply: IMF PortWatch counted 4 transits on 18 Oct against an "
     "85 baseline, a 95% drop; Lloyd's List Intelligence 14 a day in the week to 23 Aug, counting only cargo over "
     "10000 dwt; the US government around 30, on a basis it does not state. Held, not cut: mines claimed are not "
     "mines confirmed, and 1.0 is kept for full closure with Brent above $130 - strictly worse, and nearer than it was."),
]
GAUGE_10 = round(sum(w * s for _, w, s, _ in DRIVERS), 2)

# THE DRIVERS AT 3, 5 AND 10 YEARS (2026-10-27). Each score above is the reading NOW:
# the evidence in its note is about the cycle in force. The 3-year reading is the
# driver's expected average over years 1-3 and the 5-year reading over years 4-5, each
# researched from the year-by-year evidence its "why" names. Every driver is neutral at
# ten years: a cycle's extremes do not last a decade, and the funds' base returns are
# long-run assumptions that already carry the average cycle, so a 10-year reading away
# from neutral would count it twice. A check holds each path moving from the reading now
# toward neutral, never past it.
DRIVER_NEUTRAL_10 = 5.5
DRIVER_PATH = {
    "Monetary policy & liquidity": {"3Y": 3.5, "5Y": 5.0,
        "why": f"The Fed's own September path keeps its rate above the {MACRO['fed_sep_longrun']}% it "
               f"calls neutral for three years - {_fed_26_27()}, "
               f"{MACRO['fed_sep_2028']}% in 2028 - and BSP, hiking now, only hints at easing in 2027: 3.5 "
               f"for years 1-3. Then {MACRO['fed_sep_2029']}% in 2029, close to neutral: 5.0 for years 4-5."},
    "Inflation trajectory": {"3Y": 3.75, "5Y": 5.25,
        "why": f"BSP sees {MACRO['bsp_cpi_2026']}% this year and {MACRO['bsp_cpi_2027']}% in 2027 before "
               f"{MACRO['bsp_cpi_2028']}% in 2028, and the US prices {MACRO['be_5y_6oct']}-{MACRO['be_5y']}% a year "
               "over five years (October breakevens): 3.75 for years 1-3. The market puts the five "
               f"after at about {MACRO['be_5y5y']}%, near target: 5.25 for years 4-5."},
    "Growth momentum": {"3Y": 4.5, "5Y": 5.25,
        "why": f"The IMF has the world at {MACRO['imf_world_2026']}% this year and {MACRO['imf_world_2027']}% "
               f"next and the Philippines recovering to {MACRO['imf_ph_2027']}% in 2027 but below its "
               "potential, with a hiking cycle and an energy shock in train: 4.5 for years 1-3, "
               "5.25 for years 4-5 as policy turns."},
    "Corporate earnings": {"3Y": 6.5, "5Y": 5.5,
        "why": f"Analysts' long-term S&P growth forecast is {MACRO['ltg_eps']}%, in the top tenth this "
               f"century, and this quarter is growing at {MACRO['factset_q3_growth']}%: 6.5 for years 1-3. "
               f"But since 1992 they forecast {MACRO['ltg_hist_fcst']}% a year and got "
               f"{MACRO['ltg_hist_real']}%: neutral by years 4-5 as margins revert."},
    "Valuation support": {"3Y": 6.5, "5Y": 5.5,
        "why": "Asia at 10.5x and Europe at 15.4x are cheap, and the S&P's forward multiple is "
               f"below its averages, but on ten-year earnings the S&P is on {MACRO['cape']}, near the "
               f"{MACRO['cape_high']} record: 6.5 for years 1-3, neutral for years 4-5, where the "
               "base returns already price the starting multiple."},
    "Volatility & risk appetite": {"3Y": 4.5, "5Y": 5.5,
        "why": "The VIX curve's own 3-year implied volatility is a little under the long run, "
               "while the hiking cycle and the Gulf keep risk appetite below neutral: 4.5 for "
               "years 1-3, neutral for years 4-5."},
    "Geopolitics & energy": {"3Y": 3.0, "5Y": 5.0,
        "why": "The oil market prices the shock out slowly: December 2027 Brent was quoted at "
               f"${MACRO['brent_dec2027_hi']} on 22 Oct (another table has ${MACRO['brent_dec2027_lo']}), still far above pre-war - 3.0 for "
               f"years 1-3. December 2029 settled at ${MACRO['brent_dec2029']} and December 2030 at "
               f"${MACRO['brent_dec2030']} on 15 Oct, against ${MACRO['brent_front_15oct']} for the front "
               "month: 5.0 for years 4-5, a premium still above pre-war."},
}
for _n, _, _s, _ in DRIVERS:
    DRIVER_PATH[_n][HZ_LABEL] = DRIVER_NEUTRAL_10
# Each driver's path averaged over the ten years (the reading its tilts take), and the
# gauge at each horizon - the headline GAUGE stays the reading now.
DRIVER_BLEND_10 = {n: round(sum(DRIVER_PATH[n][h] * w for h, w in HZ_W.items()), 2)
                   for n, _, _, _ in DRIVERS}
GAUGE_PATH_10 = {h: round(sum(w * DRIVER_PATH[n][h] for n, w, _, _ in DRIVERS), 2)
                 for h in HZ_KEYS}

# ONE-LINE SUMMARIES, shown by default; the full note sits one tap behind each.
# A check requires every number in a summary to appear in its full note, so a
# summary cannot drift from the reasoning it abbreviates.
SUMMARY = {
    "Monetary policy & liquidity": f"Held: September core PCE ran {MACRO['us_core_pce_sep']}% on the year after the Fed held, and FedWatch has a December hike at {MACRO['fed_hike_odds_dec']}% on {_dday('fed_hike_odds_dec_date')}; the ECB and the BoJ held too.",
    "Inflation trajectory": f"Held: September PCE prices rose {MACRO['us_pce_sep']}% on the year, core {MACRO['us_core_pce_sep']}%; Brent settled at ${MACRO['brent']:.2f} on {_dday('brent_date')}, +{MACRO['brent_yoy']:.1f}% y/y.",
    "Growth momentum": f"Held: US GDP grew at a {MACRO['us_gdp_q3']}% annual rate in the third quarter against {MACRO['us_gdp_q3_consensus']}% expected, on inventories, while September's real spending was flat.",
    "Corporate earnings": f"Held, the strongest pillar: {MACRO['factset_beat_pct']}% of reporting S&P companies beat (FactSet, 23 Oct), but Alphabet's AI spending took the Nasdaq down {abs(MACRO['nasdaq_chg_pct']):.2f}% on 29 Oct.",
    "Valuation support": f"Held: the S&P is on {MACRO['spx_fwd_pe']}x forward earnings, below its five- and ten-year averages; the KOSPI is {MACRO['kospi_off_2oct_pct']}% below its 2 Oct close.",
    "Volatility & risk appetite": f"Held: the VIX rose {MACRO['vix_latest_chg_pct']}% to {MACRO['vix_latest']:.2f} on {_dday('vix_latest_date')}, still under its long-run {MACRO['vix_longrun']}, before Seoul and Tokyo sold off on the 30th.",
    "Geopolitics & energy": f"Held: on 30 Oct Iran claimed tankers had struck mines in Hormuz, which US Central Command called false; Brent settled at ${MACRO['brent']:.2f} on {_dday('brent_date')}, flows near 14 mb/d.",
    "US": f"Held: the S&P fell {abs(MACRO['spx_chg_pct']):.2f}% to {MACRO['spx_close']:.2f} on {_dday('equity_date')} on Alphabet's quarter, after GDP beat at {MACRO['us_gdp_q3']}%; FedWatch has a December hike at {MACRO['fed_hike_odds_dec']}% on {_dday('fed_hike_odds_dec_date')}.",
    "EUROPE": f"Held: the ECB kept its deposit rate at {MACRO['ecb_depo']:.2f}% on {_dday('ecb_oct_decision_date')} with inflation at 3.8%, and Lagarde will leave early.",
    "ASIA": f"Held: the KOSPI fell {abs(MACRO['kospi_latest_chg_pct']):.2f}% to {MACRO['kospi_latest']:,.2f} and the Nikkei {abs(MACRO['nikkei_latest_chg_pct']):.2f}% to {MACRO['nikkei_latest']:,.2f} on {_dday('kospi_latest_date')} on the AI-spending scare; the BoJ held at {MACRO['boj_rate']:.2f}%.",
    "PHILIPPINES": f"Held: the peso recovered to {MACRO['usdphp']} on {_dday('usdphp_date')} from its {MACRO['usdphp_record']:.2f} record and the PSEi rose {MACRO['psei_chg_pct']:.2f}%; 91-day bills are at 6.624% after BSP's 50bp hike.",
}

GAUGE = to5(GAUGE_10)          # headline, 1-5
GAUGE_NEUTRAL = NEUTRAL_5
# The gauge at each horizon on the reported scale, and blended on the reader's route.
GAUGE_PATH = {h: to5(v) for h, v in GAUGE_PATH_10.items()}
GAUGE_BLEND = round(sum(GAUGE_PATH[h] * w for h, w in HZ_W.items()), 2)

# ----------------------------------------------------------------------------
# 5. FUNDS - verified structure, fees, and the return build-up
# ----------------------------------------------------------------------------

# Expected PHP depreciation against the USD, %/yr, applied to every unhedged
# sleeve - so this constant moves three of the four funds and deserves a stated
# derivation. It used to carry the comment "PPP-implied (PH ~3.9% infl vs US
# ~2.4%)", which computes to 1.5, not 2.0; the number and its own justification
# disagreed and nothing checked either. (Audit 2026-09-10.)
#
# What it actually is: a 10-year blend between the two differentials this model
# already carries. Relative PPP says expected depreciation IS the inflation
# differential. At the long-run anchors that is ~3.9% PH (BSP's 2-4% target band,
# upper half) less ~2.4% US = ~1.5pp. On the CURRENT prints it is 6.1% less 3.4%
# = ~2.7pp. A ten-year mandate spends its first years nearer the second number
# and the rest nearer the first, so the constant sits between them rather than at
# either end. The check below asserts exactly that bracket, so if PH inflation
# converges past 2.0pp above the US - or the long-run anchors move above it -
# this stops being defensible and says so.
FX_DRIFT = 2.0
# Published volatility figures behind the covered-call sleeve's vol beta.
# Source: J.P. Morgan JEPQ fact sheet, 31 July 2026 (since-inception annualised).
JEPQ_VOL = 13.9         # JEPQ annualised standard deviation, %
NDX_VOL  = 20.4         # Nasdaq-100 annualised standard deviation, same window, %
JEPQ_BETA = 0.81        # 5-year monthly beta vs the index, published

FX_PPP_PH_LR = 3.9      # long-run PH inflation anchor (BSP 2-4% band, upper half)
FX_PPP_US_LR = 2.4      # long-run US inflation anchor
FX_VOL   = 6.0          # USD/PHP annualised vol, %
FX_CORR  = -0.20        # peso weakens in risk-off -> cushions PHP-denominated USD assets

FUNDS = [
    {
        "id": "ATRPHMM", "name": "ATRAM Peso Money Market Fund",
        "short": "Peso Money Market", "ccy": "PHP", "region": "PHILIPPINES",
        "target": "Own mandate: outperform PH bank deposits, average portfolio duration <= 1 year",
        "target_verified": True,
        # CORRECTED 2026-10-21: 0.71% came from a superseded KIIDS (trustee ~0.70%).
        # The current KIIDS has 0.57% trustee + 0.01% other, as a share of average
        # daily NAV; uitf.com.ph and GCash list the trust fee at 0.50% p.a. The KIIDS
        # figure is the higher and is what the fund actually bore, so it is used.
        "fee_feeder": 0.58, "fee_target": 0.00,
        "fee_parts": [["trustee", 0.57], ["other", 0.01]],
        "fee_feeder_prev": 0.71,
        "fee_note": "{parts} as a share of average daily NAV (KIIDS; the listed trust fee is 0.50% p.a.), was 0.71% on a superseded KIIDS",
        "gross_usd": None,                 # PHP asset - no FX translation
        "gross_local": 4.85,
        # Bound to the auction inputs 2026-10-03. It quoted the 21 Sep auction a week
        # after the 28 Sep rates were rolled in - the figures traced, but to the
        # PREVIOUS auction (ph_tbill_prev), which is the coincidence the trace now lists.
        "gross_note": f"10y average PH short-rate path. Anchored on the PH bill curve - 91d {MACRO['ph_tbill_91']}%, 182d {MACRO['ph_tbill_182']}%, 364d {MACRO['ph_tbill_364']}% at the {_dt.date.fromisoformat(MACRO['ph_tbill_date']).day} {_dt.date.fromisoformat(MACRO['ph_tbill_date']):%b} auction, higher across the curve than when this assumption was set on 2 Sep - with BSP at {MACRO['bsp_rrp']:.2f}% after a fourth consecutive hike (a half-point on 22 Oct), reverting toward a ~4.50% neutral policy rate by year 3-5. Held at 4.85% and flagged rather than re-fitted: the rise sits in the part of the path that reverts within a few years, which lifts a ten-year average by roughly a tenth of a point, a little more after the half-point - inside this assumption's precision, but a known upward bias until it is re-fitted. CUT from 5.25% when the mandate lengthened to 10 years: the elevated front end is a 1-3 year feature, so over a decade far more of the path sits at neutral and the average falls toward it.",
        "vol_beta": 0.021, "fx_exposed": False,
        "macro_tilt": {"rates": +0.25, "energy": +0.05},
        "dd_k_adj": 0.0, "cash_like": True,
        "dd_k_why": "Not applicable - the cash sleeve is floored by a rate shock, not by the equity formula.",
    },
    {
        "id": "ATRQIAP", "name": "ATRAM Nasdaq Equity Income Feeder Fund",
        "short": "Nasdaq Equity Income", "ccy": "PHP (unhedged)", "region": "US",
        "target": "Target fund: JPMorgan Nasdaq Equity Premium Income Active UCITS ETF "
                  f"(IE000U9J8HX9). Stated benchmark: {MACRO['atrqiap_bench_ndx_pct']}% Nasdaq-100 Index.",
        "target_verified": True,
        "fee_feeder": 1.50, "fee_target": 0.35,
        # THE CLASS HELD (owner, 2026-10-21): the A PHP unit class - 1.50% trust fee incl.
        # distribution fee on ATRAM's fund page and uitf.com.ph. The D classes list 0.50%
        # and are not what this portfolio holds.
        "fee_note": "1.50% ATRAM trust fee incl. distribution fee, A PHP unit class (the class held) + 0.35% target-fund TER (both verified)",
        # COMPUTED (was a typed 7.2 that its own recipe did not produce). The premium
        # is the harvest at LONG-RUN implied vol: the base is a no-view return, and
        # "earned back as implied vol rises 14.3 -> 19.4" - the old wording - was the
        # same rise the volatility tilt pays for. It is counted there, once.
        "gross_usd": round((MACRO["ltcma_us_eq"] + MACRO["ndx_growth_premium"])
                           * MACRO["qiap_capture"] / 100 + MACRO["qiap_premium_lr"], 2),
        "gross_note": (f"NDX long-run total return of {MACRO['ltcma_us_eq'] + MACRO['ndx_growth_premium']:.1f}% "
                       f"(JPM LTCMA {MACRO['ltcma_edition']} US large cap {MACRO['ltcma_us_eq']}%, was {MACRO['ltcma_us_eq_prev']}%, + {MACRO['ndx_growth_premium']}% NDX "
                       f"growth premium, valuation neutral at 22.4x vs 22.9x 10y avg), times "
                       f"~{MACRO['qiap_capture']}% covered-call upside capture, plus "
                       f"~{MACRO['qiap_premium_lr']}%/yr of option premium at long-run implied vol."),
        # NDX vol relative to the S&P (1.22, assumption) times the covered-call
        # vol factor, which is no longer a magic number: J.P. Morgan's own fact
        # sheet (31 Jul 2026) puts JEPQ since-inception annualised standard
        # deviation at 13.9% against the Nasdaq-100's 20.4%, i.e. 0.681. The 0.68
        # carried here for months happened to be right to two decimals, but it was
        # unsourced; it is now derived from two published figures.
        "vol_beta": NDX_SP_BETA * (JEPQ_VOL / NDX_VOL), "fx_exposed": True,
        "macro_tilt": {"rates": -0.10, "energy": -0.10},
        # WAS -0.10 until 2026-09-24, on the reason that "realised drawdowns run
        # shallower than the raw volatility implies". But k multiplies THIS sleeve's
        # volatility, which is already JEPQ's own (0.681x the Nasdaq-100) - the
        # premium's cushion is in sigma, and the premium itself is in the return, so
        # the cut counted it a third time. The shape argument runs the other way:
        # capped upside with near-full downside is NEGATIVELY skewed, which if
        # anything raises drawdown per unit of volatility. Set to the anchor rather
        # than to a higher figure this model has no measurement for. It mattered
        # little at 30-50% of the portfolio; at 75% it set the allocation.
        "dd_k_adj": 0.0, "cash_like": False,
        "dd_k_why": "At the 1.65 anchor: the premium's cushion is already in this sleeve's volatility (0.681x the Nasdaq-100) and its return; capped upside with full downside is negatively skewed, which argues against a lower k, not for one.",
    },
    {
        "id": "ATRASEQ", "name": "ATRAM Asia Equity Opportunity Feeder Fund",
        "short": "Asia Equity", "ccy": "PHP (unhedged)", "region": "ASIA",
        "target": "Target fund: JPMorgan Asia Equity Dividend Fund (Asia Pacific ex-Japan). "
                  "Feeder launched 08 Dec 2016.",
        "target_verified": True,
        # RAISED 0.80 -> 1.55 on 2026-09-09. The 0.80% carried since launch was an
        # unanchored guess. J.P. Morgan publishes a MANAGEMENT FEE of 1.50% p.a. for
        # this fund, so the ongoing charge cannot be 0.80% - it is at least the
        # management fee. 1.55% = the published 1.50% plus ~0.05% operating costs.
        # Still an ESTIMATE, because the exact OCF for the share class ATRAM's feeder
        # buys is not published; but it is now anchored on a published figure.
        # CORRECTED 2026-09-25: this said the estimate "errs HIGH". It cannot know
        # that. The target is a HONG KONG unit trust (HK ISINs, JPMorgan Funds (Asia)
        # Ltd), and HK unit trusts typically add trustee and administration costs to
        # the management fee, so the true OCF is more likely ABOVE 1.55% than below.
        # COMPONENTS AS DATA (2026-10-15 review): the note quoted 1.17% and 0.01%
        # that existed nowhere else, so the audit could not tie them to the fee.
        # The note is now built from these parts, and a check requires them to sum
        # to fee_feeder.
        "fee_feeder": 1.18, "fee_target": 1.55,
        "fee_parts": [["trustee", 1.17], ["auditor", 0.01]],
        "fee_note": "{parts} (verified KIIDS) + ~1.55% estimated target-fund OCF "
                    "(ESTIMATE, anchored on JPMAM's published 1.50% management fee for "
                    "this Hong Kong unit trust; exact share-class OCF not published, and "
                    "trustee/admin costs may put it higher)",
        "gross_usd": round(MACRO["ltcma_em_eq"] + MACRO["asia_rerating"] - MACRO["asia_div_drag"], 2),
        "gross_note": (f"JPM LTCMA {MACRO['ltcma_edition']} EM equity {MACRO['ltcma_em_eq']}% (was {MACRO['ltcma_em_eq_prev']}%) + ~{MACRO['asia_rerating']}% "
                       f"re-rating from a 10.5x forward multiple against ~52%/~28% EPS growth, less "
                       f"~{MACRO['asia_div_drag']}% for the dividend tilt's lower growth capture."),
        # ASSUMPTION, not a published figure: Asia Pacific ex-Japan vol at ~1.05x
        # the S&P, times ~0.92 for the dividend tilt's lower beta. Neither leg is
        # sourced to a manager document, and CLAIMS.md records it as an estimate.
        # Unlike the covered-call factor next door, no published pair was found to
        # anchor it. (Reviewed 2026-09-13.)
        "vol_beta": ASIA_SP_BETA * 0.92, "fx_exposed": True,
        "macro_tilt": {"rates": -0.05, "energy": -0.20},
        "asia_rerating_share": 1.0,     # the whole fund carries the re-rating credit
        "dd_k_adj": +0.05, "cash_like": False,
        "dd_k_why": "Above 1.65: Asian equity drawdowns carry more crash kurtosis and liquidity gapping than a developed-market index.",
    },
    {
        "id": "ATRGTEC", "name": "ATRAM Global Technology Feeder Fund",
        "short": "Global Technology", "ccy": "PHP (unhedged)", "region": "GLOBAL_TECH",
        "target": "Target fund: Fidelity Funds - Global Technology Fund. Benchmark: "
                  "MSCI ACWI Information Technology. Target-fund 5y annualised: 15.20% "
                  "(W GBP class, to 20 Aug 2026).",
        "target_verified": True,
        # PROMOTED from a 0.95% estimate to Fidelity's PUBLISHED 1.04% OCF for the
        # W-Acc-GBP class (AMC 0.80% + operating costs), the same class this model
        # already cites for the fund's realised 5-year return. (Verified 2026-09-09.)
        # FEEDER FEE RAISED 1.15% -> 1.50% FROM 14 SEP 2026 (A unit class), with five
        # other ATRAM feeders at 1.20% -> 1.50%, under an amended Declaration of
        # Trust; ATRAM's fund page now lists 1.50%. This model carried 1.15% for a
        # month after the change. Caught 2026-10-15. Asia Equity Opportunity is not
        # on the list; Nasdaq Equity Income was already at 1.50%.
        "fee_feeder": 1.50, "fee_target": 1.04,
        "fee_feeder_prev": 1.15, "fee_feeder_from": "2026-09-14",
        "target_amc": 0.80,   # Fidelity's annual management charge inside the 1.04% OCF
        "fee_note": "1.50% ATRAM trust fee from 14 Sep 2026, up from 1.15% (published) "
                    "+ 1.04% target-fund OCF (PUBLISHED by Fidelity for the W-Acc-GBP "
                    "and Y-Acc-USD classes, AMC {amc:.2f}%)",
        "gross_usd": round(MACRO["ltcma_us_eq"] + MACRO["tech_growth_premium"] - MACRO["tech_derating"], 2),
        "gross_note": (f"US large cap {MACRO['ltcma_us_eq']}% (JPM LTCMA {MACRO['ltcma_edition']}; was {MACRO['ltcma_us_eq_prev']}%) + {MACRO['tech_growth_premium']}% "
                       f"tech earnings-growth premium - {MACRO['tech_derating']}% multiple de-rating drag. "
                       f"Deliberately well BELOW the target fund's realised 15.20% 5y, which was earned "
                       f"inside an AI capex boom and is not a forecast."),
        # ASSUMPTION: concentrated global tech at ~1.30x the S&P. Cross-check
        # rather than confirmation - Fidelity publishes a 3-year annualised
        # volatility of 17.23% for this fund (USD I Acc, Jun 2026), which implies
        # a ~1.30 beta only if S&P REALISED vol over that window was ~13.3%. That
        # is plausible but unverified here, and the two are not the same quantity:
        # this beta is applied to FORWARD implied vol, not trailing realised.
        # Recorded as an estimate. (Reviewed 2026-09-13.)
        "vol_beta": TECH_SP_BETA, "fx_exposed": True,
        "macro_tilt": {"rates": -0.40, "energy": -0.15},
        "dd_k_adj": +0.15, "cash_like": False,
        "dd_k_why": "Well above 1.65: concentrated long-duration growth has the fattest left tail on the sheet - the 2022 de-rating took the sector far past what 1.65 sigma predicts.",
    },
]

for _f in FUNDS:
    if "fee_parts" in _f:
        _f["fee_note"] = _f["fee_note"].replace("{parts}", " + ".join(
            f"{v:.2f}% {k}" for k, v in _f["fee_parts"]))
    if "target_amc" in _f:
        _f["fee_note"] = _f["fee_note"].format(amc=_f["target_amc"])

# MSCI ACWI IT regional decomposition, used to score the Global Tech sleeve
ACWI_IT_MIX = {"US": 0.72, "ASIA": 0.16, "EUROPE": 0.12}
# The Global Dividend sleeve, DERIVED 2026-10-21 from the
# target fund's country weights. It was an ESTIMATE of US 50 / Europe 38 / Asia 12;
# the fund's 30 Sep 2026 factsheet has Germany 11.2, France 9.6, Switzerland 8.9,
# Japan 7.4, Spain 5.9, Taiwan 4.0, Netherlands 3.1, South Korea 1.8. Its US and UK
# weights are not in the text reachable here; they are taken from an older listing
# of the same fund (DFO: US 21.16, UK 13.31; the UK OEIC sister, 6 Oct: 21.7 / 14.1).
# The mix is the identified 86.4% renormalised; Japan joins Asia, as in the ACWI IT
# mix above.
GDIV_GEO = {"US": [("USA", 21.16)],
            "EUROPE": [("Germany", 11.2), ("France", 9.6), ("Switzerland", 8.9),
                       ("Spain", 5.9), ("Netherlands", 3.1), ("UK", 13.31)],
            "ASIA": [("Japan", 7.4), ("Taiwan", 4.0), ("South Korea", 1.8)]}
_GG = {r: sum(v for _, v in xs) for r, xs in GDIV_GEO.items()}
GDIV_MIX = {"US": round(_GG["US"] / sum(_GG.values()), 3),
            "EUROPE": round(_GG["EUROPE"] / sum(_GG.values()), 3)}
GDIV_MIX["ASIA"] = round(1 - GDIV_MIX["US"] - GDIV_MIX["EUROPE"], 3)
# The six funds added 2026-10-22. ESTIMATES: each target's benchmark split by region,
# rounded (MSCI ACWI Health Care is roughly two-thirds US; listed infrastructure about
# half; a thematic or consumer global fund about three-fifths), not the funds' own
# published country weights, which were not reachable for these six. Japan joins
# Asia, as in the two mixes above. Recorded in CLAIMS.md as estimates.
REGION_MIX = {
    "GLOBAL_TECH": ACWI_IT_MIX, "GLOBAL_DIV": GDIV_MIX,
    "GLOBAL_HC": {"US": 0.66, "EUROPE": 0.25, "ASIA": 0.09},
    "GLOBAL_INFRA": {"US": 0.50, "EUROPE": 0.33, "ASIA": 0.17},
    "GLOBAL_EQ_OPP": {"US": 0.60, "EUROPE": 0.15, "ASIA": 0.25},
    "GLOBAL_CONS": {"US": 0.62, "EUROPE": 0.13, "ASIA": 0.25},
    "GLOBAL_ALLOC": {"US": 0.60, "EUROPE": 0.20, "ASIA": 0.20},
}

REGIONAL_TILT_PER_PT = 0.675    # % of net CAGR per point of 1-5 macro score above neutral
NEUTRAL = NEUTRAL_5             # 0.675 = 0.30 per 1-10 point x 9/4, so tilts are unchanged

# ---- The Monetary and Geopolitics drivers, TRANSMITTED -----------------------
# Until 2026-09-23 they were not. Each fund's rates and energy tilt was a typed
# constant, and the Monetary and Geopolitics drivers - scored separately, above -
# fed only the headline gauge, which itself feeds nothing. Since launch the
# Monetary driver has moved 4.0 -> 3.5 -> 2.5 -> 2.25 and Geopolitics 2.5 -> 1.5
# -> 1.0 -> 1.5 -> 1.25 -> 1.5, and Global Tech's rates tilt stayed at -0.40 and
# its energy tilt at -0.15 through every one of those moves. The page said the
# optimiser was built from the macro drivers; it was built from constants that
# happened to have been written the same day the drivers first were.
#
# They are transmitted now the same way the volatility ramp is: signal times a
# structural sensitivity. The typed per-fund values in FUNDS are kept, and
# RE-READ as what they always implicitly were - each fund's tilt at the driver
# readings in force when they were written (commit 918c280, 2 Sep: Monetary 4.0,
# Geopolitics 2.5). Calibrating there states the ORIGINAL judgment rather than
# making a new one; the tilt today is what that judgment implies at today's
# readings. Linear in distance from the 5.5 neutral, the minimal assumption.
# The recommended allocation does not change - it was checked before this went
# in - but every fund's forecast does, and every future driver move now reaches
# the returns and the optimiser, which is what the page has always claimed.
#
# READ ACROSS THE HORIZONS (since 2026-10-26). Until v67 the tilt took each driver's
# current reading as though it held for all ten years, while the regional and
# volatility channels already averaged their horizons. A Monetary reading of 2.0 that
# is expected to average 3.5 over three years and 5.0 over the next two does not drag
# a ten-year return as one held for the decade would. The reading is the driver's path averaged over the ten
# years with the HZ_W weights (DRIVER_BLEND_10); the 10-year view alone (Portfolio A's
# column) reads the 10-year point, which is neutral, so it carries no rates or energy
# tilt.
TILT_CAL = {"monetary": 4.0, "geopolitics": 2.5,
            "date": "2026-09-02", "commit": "918c280"}
MON_BLEND = DRIVER_BLEND_10["Monetary policy & liquidity"]
GEO_BLEND = DRIVER_BLEND_10["Geopolitics & energy"]
assert TILT_CAL["monetary"] != DRIVER_NEUTRAL_10 and TILT_CAL["geopolitics"] != DRIVER_NEUTRAL_10, \
    "a calibration reading at neutral carries no information about sensitivity"
def _drv_scale(reading, cal):
    return (reading - DRIVER_NEUTRAL_10) / (cal - DRIVER_NEUTRAL_10)
RATES_SCALE = _drv_scale(MON_BLEND, TILT_CAL["monetary"])
ENERGY_SCALE = _drv_scale(GEO_BLEND, TILT_CAL["geopolitics"])
RATES_SCALE_10 = _drv_scale(DRIVER_PATH["Monetary policy & liquidity"][HZ_LABEL], TILT_CAL["monetary"]) + 0.0
ENERGY_SCALE_10 = _drv_scale(DRIVER_PATH["Geopolitics & energy"][HZ_LABEL], TILT_CAL["geopolitics"]) + 0.0

def regional_score(region_key, h="blend"):
    """The fund's regional score: the horizon blend, or one horizon's score."""
    if region_key in REGION_MIX:
        return sum(REGIONS[r][h] * w for r, w in REGION_MIX[region_key].items())
    return REGIONS[region_key][h]

# ---- Per-fund return, volatility and drawdown -------------------------------

DD_K = 1.65      # calibrated: 1.65*sigma - 0.5*mu reproduces the observed median
DD_MU = 0.50     # rolling-5y max drawdown of the S&P 500 (~-20%) and NDX (~-33%)
# The two anchors as data: (sigma, mu, median rolling-5y max drawdown), all in %.
# Typed into the page until 2026-10-17 and never checked; a check below now
# requires DD_K and DD_MU to reproduce both within half a point.
DD_CALIB = {"S&P 500": (15.5, 11.0, 20.0), "Nasdaq-100": (24.0, 13.0, 33.0)}
MM_SHOCK_BP, MM_DURATION_Y = 100, 0.5   # the cash sleeve's rate-shock floor

# Expected maximum drawdown is NOT horizon-invariant: a longer window gives the
# path more time to find its worst peak-to-trough, so the same fund carries a
# deeper expected drawdown over 10 years than over 5. The calibration anchors
# above are rolling-FIVE-year medians, so lengthening the mandate cannot just
# relabel them.
#
# For a diffusion, expected maximum drawdown scales with sigma*sqrt(T), so the
# whole calibrated quantity scales by sqrt(T / T_calib). At a 10-year horizon
# that is sqrt(2) = 1.414, which turns the S&P anchor into ~-28% and the NDX
# anchor into ~-47% - both plausible for rolling 10-year windows, and both
# DERIVED from the 5-year calibration rather than re-fitted by eye to numbers
# this model has not verified at a primary source.
#
# The drift term scales with the same factor because it is an annualised rate
# offsetting the same window; scaling only the volatility term would quietly
# assume drift stops helping as the horizon lengthens.
DD_HORIZON_SCALAR = math.sqrt(HORIZON_Y / DD_CALIB_Y)

def combine_fx(sig_asset):
    """Total PHP-denominated vol for an unhedged USD asset."""
    return math.sqrt(sig_asset**2 + FX_VOL**2 + 2 * FX_CORR * sig_asset * FX_VOL)

def build_fund(f):
    fee = f["fee_feeder"] + f["fee_target"]
    if f["fx_exposed"]:
        gross_php = f["gross_usd"] + FX_DRIFT
    else:
        gross_php = f["gross_local"]
    base_net = gross_php - fee

    sig_asset = f["vol_beta"] * SP_VOL_LT
    sig = sig_asset if not f["fx_exposed"] else combine_fx(sig_asset)

    # macro overlay
    t = f["macro_tilt"]
    rs = regional_score(f["region"])
    # Every component rounded to the 2dp it is PUBLISHED at, and the total built
    # from those, so the transmission table's column adds up on the page.
    # A MULTI-ASSET FUND'S equity share carries the regional and trend tilts, which
    # score equity markets; its bond leg carries the rates and energy tilts with the
    # rest of the fund (2026-10-22). 1.0 for every equity fund, which leaves them
    # exactly as before.
    share = f.get("equity_share", 1.0)
    reg_tilt = rnd((rs - NEUTRAL) * REGIONAL_TILT_PER_PT * share if share != 1.0
                   else (rs - NEUTRAL) * REGIONAL_TILT_PER_PT)
    vol_tilt = rnd(VOL_RAMP * VOL_SENS[f["id"]]) + 0.0   # derived, not hand-set; + 0.0 drops a -0.0
    rates_tilt = rnd(t["rates"] * RATES_SCALE)     # derived from the Monetary driver
    energy_tilt = rnd(t["energy"] * ENERGY_SCALE)  # derived from Geopolitics & energy
    # The market whose 1/3/5-year trend the fund carries: its own by default, or another
    # fund's (a multi-asset fund's equity market); None where no series was sourced.
    mkt = f.get("trend_market", f["id"])
    trend_tilt = (rnd(TREND[mkt]["tilt"] * share) + 0.0 if mkt in TREND and share != 1.0
                  else TREND[mkt]["tilt"] if mkt in TREND else 0.0)   # 1/3/5-year market trend
    tilt_total = rnd(reg_tilt + vol_tilt + rates_tilt + energy_tilt + trend_tilt)
    macro_net = base_net + tilt_total
    # THE 10-YEAR VIEW ALONE (2026-10-26), Portfolio A's column: the same channels read
    # at the 10-year horizon only - the regional score's 10-year anchor, the volatility
    # curve's years 6-10, the drivers' 10-year readings and the trend's neutral anchor.
    rs10 = regional_score(f["region"], HZ_LABEL)
    reg10 = rnd((rs10 - NEUTRAL) * REGIONAL_TILT_PER_PT * share if share != 1.0
                else (rs10 - NEUTRAL) * REGIONAL_TILT_PER_PT) + 0.0
    vol10 = rnd(VOL_RAMP_10 * VOL_SENS[f["id"]]) + 0.0
    rates10 = rnd(t["rates"] * RATES_SCALE_10) + 0.0
    energy10 = rnd(t["energy"] * ENERGY_SCALE_10) + 0.0
    tilt10 = rnd(reg10 + vol10 + rates10 + energy10)
    net10 = base_net + tilt10

    k = DD_K + f["dd_k_adj"]
    def dd(mu):
        raw = (k * sig - DD_MU * mu) * DD_HORIZON_SCALAR
        if f["cash_like"]:
            # Money market: bounded by a MM_SHOCK_BP parallel shock on ~MM_DURATION_Y
            # less one year of carry - it cannot behave like an equity fund. This
            # floor is NOT horizon-scaled: a rate shock on a half-year duration
            # book is the same size whether you hold it 5 years or 10.
            return max(0.5, min(raw, 0.9))
        return max(raw, 0.0)

    return {
        **{q: f[q] for q in ("id", "name", "short", "ccy", "region", "target",
                             "target_verified", "fee_note", "gross_note")},
        # The code the page prints. It is the id unless the id is only this model's
        # label - ATRLTPB has no ATRAM code confirmed, so its slide shows Bloomberg's.
        "code": f.get("code", f["id"]),
        "fee_feeder": f["fee_feeder"], "fee_target": f["fee_target"],
        "fee_feeder_prev": f.get("fee_feeder_prev"), "fee_feeder_from": f.get("fee_feeder_from"),
        "fee_parts": f.get("fee_parts"), "target_amc": f.get("target_amc"),
        "fee_total": round(fee, 2),
        "gross_php": round(gross_php, 2),
        "fx_drift": FX_DRIFT if f["fx_exposed"] else 0.0,
        "net_base": round(base_net, 2),
        "regional_score": round(rs, 2),
        "tilt_regional": round(reg_tilt, 2),
        "tilt_vol": vol_tilt, "tilt_rates": rates_tilt, "tilt_energy": energy_tilt,
        "tilt_trend": trend_tilt,
        "equity_share": share, "trend_market": mkt if mkt in TREND else None,
        # the regional mix the score is read from (None for a single-region fund), so the
        # independent audit re-derives the score instead of trusting it
        "region_mix": REGION_MIX.get(f["region"]),
        "asia_rerating_share": f.get("asia_rerating_share", 0.0),
        "role": f.get("role"), "exposure": f.get("exposure"),
        "tilt_rates_cal": t["rates"], "tilt_energy_cal": t["energy"],
        "tilt_total": round(tilt_total, 2),
        "net_macro": round(macro_net, 2),
        "regional_score_10y": round(rs10, 2), "tilt_regional_10y": reg10,
        "tilt_vol_10y": vol10, "tilt_rates_10y": rates10, "tilt_energy_10y": energy10,
        "tilt_total_10y": round(tilt10, 2), "net_10y": round(net10, 2),
        "vol": round(sig, 2), "vol_beta": f["vol_beta"],
        "dd_k": round(k, 2), "dd_k_why": f["dd_k_why"],
        "dd_base": round(-dd(base_net), 1),
        "dd_macro": round(-dd(macro_net), 1),
        "dd_10y": round(-dd(net10), 1),
        # THE TARGET FUND ITSELF (the ETF / SICAV each feeder buys): the same
        # exposure, in pesos, net of its OWN charge only - i.e. the sleeve's
        # return with the feeder's fee added back. Derived, not a separate
        # estimate; the gap to net_macro is exactly what the feeder layer costs.
        # None for the money market, whose "target" is its own mandate.
        "target_net_macro": None if f["cash_like"] else round(macro_net + f["fee_feeder"], 2),
        "target_dd_macro": None if f["cash_like"] else round(-dd(macro_net + f["fee_feeder"]), 1),
    }

F = [build_fund(f) for f in FUNDS]

# ---- The funds beyond the original four ----------------------------------------
# Global Dividend from the 21 Oct review of the ATRAM list, and six more from the
# owner's 22-fund list (2026-10-22). Every one is built by build_fund() - the same
# fees, FX drift, tilts and drawdown rule as the original four - so A and B are
# measured on one basis. The Long Term Peso Bond that sat beside Global Dividend was
# removed on 2026-10-21 at the owner's instruction.
ADD_FUNDS = [
    {
        "id": "ATRGLDV", "name": "ATRAM Global Dividend Feeder Fund",
        "short": "Global Dividend", "ccy": "PHP (unhedged)", "region": "GLOBAL_DIV",
        "target": "Target fund: Fidelity Funds - Global Dividend Fund.",
        "target_verified": True,
        "fee_feeder": MACRO["gdiv_trust_fee"], "fee_target": MACRO["gdiv_target_ocf"],
        "fee_note": (f"{MACRO['gdiv_trust_fee']:.2f}% ATRAM trust fee incl. distribution fee "
                     f"(PUBLISHED on ATRAM's fund page) + {MACRO['gdiv_target_ocf']:.2f}% target-fund OCF "
                     f"(PUBLISHED by Fidelity for the Y-Acc-USD class; the class the feeder "
                     f"holds is not published)"),
        "gross_usd": round(MACRO["ltcma_global_eq"] - MACRO["gdiv_div_drag"], 2),
        "gross_note": (f"JPM LTCMA {MACRO['ltcma_edition']} global equity {MACRO['ltcma_global_eq']}% "
                       f"(was {MACRO['ltcma_global_eq_prev']}%) less ~{MACRO['gdiv_div_drag']}% for "
                       f"the dividend tilt's lower growth capture."),
        "vol_beta": 0.80, "fx_exposed": True,      # ASSUMPTION: quality-dividend equity at ~0.80x the S&P
        "macro_tilt": {"rates": -0.08, "energy": 0.0},
        "dd_k_adj": 0.0, "cash_like": False,
        "dd_k_why": "At the 1.65 anchor: a diversified dividend portfolio's left tail is the market's.",
    },
    # ---- THE SIX ADDED 2026-10-22, from the owner's 22-fund list ----
    # Each passed the list's fee standard (MACRO["list22_held_out"] has the eleven that
    # did not). Built by build_fund() like every other sleeve. What is ESTIMATED is
    # named in each note and in CLAIMS.md: the volatility betas, the rates and energy
    # sensitivities, the regional mixes and the drawdown-k adjustments are judgments on
    # the funds' mandates, as they were for Global Dividend. SECTOR AND THEME FUNDS CARRY
    # NO SECTOR PREMIUM: J.P. Morgan's LTCMA publishes regional assumptions, not sector
    # ones, so each is built on global equity and differs from the others through its
    # fees, volatility, correlations and macro tilts. (Global Technology's premium is
    # this model's own named input, kept as it was.)
    {
        "id": "ATRGHCP", "name": "ATRAM Global Health Care Feeder Fund",
        "short": "Global Health Care", "ccy": "PHP (unhedged)", "region": "GLOBAL_HC",
        "target": "Target fund: Fidelity Funds - Global Healthcare Fund (the feeder's KIID, "
                  "target information as of 27 Feb 2026). Benchmark: MSCI ACWI Health Care.",
        "target_verified": True,
        "fee_feeder": 1.50, "fee_target": 1.05,
        "fee_feeder_prev": 1.20, "fee_feeder_from": "2026-09-14",
        "fee_note": "1.50% ATRAM trust fee incl. distribution fee from 14 Sep 2026, up from 1.20% "
                    "(ATRAM's fund page and uitf.com.ph) + 1.05% target-fund TER (PUBLISHED on the "
                    f"feeder's fact sheet; Fidelity's I-Acc class shows {MACRO['ghcp_target_iacc_ter']:.2f}%)",
        "gross_usd": MACRO["ltcma_global_eq"],
        "gross_note": (f"JPM LTCMA {MACRO['ltcma_edition']} global equity {MACRO['ltcma_global_eq']}%, "
                       f"with no sector premium: the LTCMA publishes regional, not sector, assumptions."),
        "vol_beta": HC_SP_BETA, "fx_exposed": True,       # ASSUMPTION: health care at ~0.85x the S&P
        "macro_tilt": {"rates": -0.05, "energy": 0.0},
        "dd_k_adj": 0.0, "cash_like": False,
        "dd_k_why": "At the 1.65 anchor: a defensive sector, but a single-sector book; its left tail is taken as the market's.",
        "role": "Defensive equity — health care, two-thirds US",
        "exposure": ["Fidelity Funds — Global Healthcare Fund (Luxembourg SICAV)",
                     "Benchmark: MSCI ACWI Health Care",
                     "Pharmaceuticals, biotech, devices and insurers; largest holdings Eli Lilly and AbbVie (Aug 2026)"],
    },
    {
        "id": "M_GINF", "code": "code not confirmed", "name": "ATRAM Global Infra Equity Feeder Fund",
        "short": "Global Infra Equity", "ccy": "PHP (unhedged)", "region": "GLOBAL_INFRA",
        "target": "Target fund: HSBC Global Investment Funds - Global Infrastructure Equity "
                  "(since March 2025, replacing UBS (Lux) Infrastructure Equity).",
        "target_verified": True,
        "fee_feeder": 1.50, "fee_target": 0.80,
        "fee_feeder_prev": 1.20, "fee_feeder_from": "2026-09-14",
        "fee_note": "1.50% ATRAM trust fee from 14 Sep 2026, up from 1.20% (uitf.com.ph A PHP units; "
                    "the 14 Sep repricing) + 0.80% target-fund TER (PUBLISHED on the feeder's fact sheet)",
        "gross_usd": MACRO["ltcma_global_eq"],
        "gross_note": (f"JPM LTCMA {MACRO['ltcma_edition']} global equity {MACRO['ltcma_global_eq']}%, "
                       f"with no sector premium: the LTCMA publishes no listed-infrastructure line."),
        "vol_beta": 0.85, "fx_exposed": True,             # ASSUMPTION: listed infrastructure ~0.85x
        "macro_tilt": {"rates": -0.20, "energy": +0.05},  # bond-like; pipelines gain from energy
        "dd_k_adj": 0.0, "cash_like": False,
        "dd_k_why": "At the 1.65 anchor: regulated, contracted cash flows; no fatter tail than the market's is claimed.",
        "role": "Real-asset equity — utilities, pipelines, towers",
        "exposure": ["HSBC GIF — Global Infrastructure Equity (Luxembourg SICAV)",
                     "Listed infrastructure: utilities, energy pipelines, transport, communications towers",
                     "Target since March 2025 (was UBS (Lux) Infrastructure Equity)"],
    },
    {
        "id": "M_GEO", "code": "14UF05P", "name": "ATRAM Global Equity Opportunity Feeder Fund",
        "short": "Global Equity Opportunity", "ccy": "PHP (unhedged)", "region": "GLOBAL_EQ_OPP",
        "target": "Target fund: Allianz Global Investors Fund - Allianz Thematica (since April 2021). "
                  "A thematic global equity fund.",
        "target_verified": True,
        "fee_feeder": 1.50, "fee_target": 1.00,
        "fee_feeder_prev": 1.20, "fee_feeder_from": "2026-09-14",
        "fee_note": "1.50% ATRAM trust fee from 14 Sep 2026, up from 1.20% (ATRAM's fund page, "
                    "uitf.com.ph PHP class) + 1.00% target-fund TER (PUBLISHED in the feeder's KIID, "
                    f"31 Mar 2026; Allianz's retail AT class lists {MACRO['geo_target_at_ter']:.2f}%)",
        "gross_usd": MACRO["ltcma_global_eq"],
        "gross_note": (f"JPM LTCMA {MACRO['ltcma_edition']} global equity {MACRO['ltcma_global_eq']}%, "
                       f"with no theme premium."),
        "vol_beta": ACWI_SP_BETA * 1.15, "fx_exposed": True,   # ASSUMPTION: thematic, ~1.15x the market
        "macro_tilt": {"rates": -0.20, "energy": -0.10},
        "dd_k_adj": +0.05, "cash_like": False,
        "dd_k_why": "A little above 1.65: thematic growth with a mid-cap tilt gaps further than the broad market.",
        "role": "Thematic global equity — long-run themes",
        "exposure": ["Allianz Global Investors Fund — Allianz Thematica (Luxembourg SICAV)",
                     "Global equities picked by structural theme",
                     "Target since April 2021 (was Fidelity Global Thematic Opportunities)"],
    },
    {
        "id": "M_GCT", "code": "20UF19P", "name": "ATRAM Global Consumer Trends Feeder Fund",
        "short": "Global Consumer Trends", "ccy": "PHP (unhedged)", "region": "GLOBAL_CONS",
        "target": "Target fund: Invesco Global Consumer Trends Fund.",
        "target_verified": True,
        "fee_feeder": 1.50, "fee_target": 0.97,
        "fee_feeder_prev": 1.20, "fee_feeder_from": "2026-09-14",
        "fee_note": "1.50% ATRAM trust fee from 14 Sep 2026, up from 1.20% (ATRAM's fund page) + "
                    "0.97% target-fund TER (PUBLISHED in the feeder's later KIID; an earlier one had 1.04%)",
        "gross_usd": MACRO["ltcma_global_eq"],
        "gross_note": (f"JPM LTCMA {MACRO['ltcma_edition']} global equity {MACRO['ltcma_global_eq']}%, "
                       f"with no sector premium."),
        "vol_beta": 1.75, "fx_exposed": True,             # ASSUMPTION: concentrated consumer growth
        "macro_tilt": {"rates": -0.25, "energy": -0.15},
        "dd_k_adj": +0.15, "cash_like": False,
        "dd_k_why": "Well above 1.65: a concentrated consumer-growth book; its 2022 fall ran far past what 1.65 sigma predicts.",
        "role": "Consumer growth — the most volatile fund here",
        "exposure": ["Invesco Global Consumer Trends Fund (Luxembourg SICAV)",
                     "Consumer discretionary, e-commerce and leisure, global",
                     "Concentrated growth book"],
    },
    {
        "id": "ATRAMIP", "name": "ATRAM Asian Multi-Asset Income Feeder Fund",
        "short": "Asian Multi-Asset Income", "ccy": "PHP (unhedged)", "region": "ASIA",
        "target": "Target fund: Schroder Asian Asset Income Fund (named at launch, Sep 2022). "
                  "Benchmark: 50% MSCI AC Asia Pacific ex Japan + 50% Bloomberg EM Asia.",
        "target_verified": True,
        "fee_feeder": 1.50, "fee_target": 1.54,
        "fee_note": "1.50% ATRAM trust fee incl. distribution fee (ATRAM's fund page; DragonFi) + "
                    "~1.54% target-fund charge (ESTIMATE: Schroders' published class A figure, Mar 2025; "
                    "the class the feeder holds is not published). DISPUTED: the October 2025 KIID and "
                    f"uitf.com.ph list a {MACRO['amip_trust_alt']:.2f}% trust fee; at it, A would hold "
                    f"{MACRO['amip_w_a_alt']}% of this fund and B {MACRO['amip_w_b_alt']}%, and C the {MACRO['amip_w_c_alt']}% it holds at 1.50%",
        # Half the page's Asia equity sleeve, half Asian credit. No 2027 LTCMA figure for
        # Asian credit was found, so US investment grade stands in for it.
        "gross_usd": round(0.5 * (MACRO["ltcma_em_eq"] + MACRO["asia_rerating"] - MACRO["asia_div_drag"])
                           + 0.5 * MACRO["ltcma_us_ig"], 2),
        "gross_note": (f"Half equity, half bonds, as its benchmark: the Asia equity build (JPM LTCMA "
                       f"{MACRO['ltcma_edition']} EM equity {MACRO['ltcma_em_eq']}% + {MACRO['asia_rerating']}% re-rating "
                       f"- {MACRO['asia_div_drag']}% dividend drag) and {MACRO['ltcma_us_ig']}% for Asian credit "
                       f"(the LTCMA's US investment-grade figure, a proxy)."),
        "vol_beta": 0.48, "fx_exposed": True,             # ASSUMPTION: a 50/50 Asian book
        "macro_tilt": {"rates": -0.10, "energy": -0.15},  # Asia imports its oil
        "dd_k_adj": 0.0, "cash_like": False,
        "dd_k_why": "At the 1.65 anchor: the bond half damps the Asian equity tail.",
        "equity_share": 0.5, "trend_market": "ATRASEQ", "asia_rerating_share": 0.5,
        "role": "Asian income — half equity, half credit",
        "exposure": ["Schroder Asian Asset Income Fund (Hong Kong unit trust)",
                     "Asia Pacific ex-Japan dividend equities and Asian USD credit, about half each",
                     "Benchmark 50% MSCI AC Asia Pacific ex Japan / 50% Bloomberg EM Asia"],
    },
    {
        "id": "M_GALL", "code": "14UF06", "name": "ATRAM Global Allocation Feeder Fund",
        "short": "Global Allocation", "ccy": "PHP (unhedged)", "region": "GLOBAL_ALLOC",
        "target": "Target fund: BlackRock Global Funds - Global Allocation Fund (A2 USD).",
        "target_verified": True,
        "fee_feeder": 1.20, "fee_target": 1.13,
        "fee_note": "1.20% ATRAM trust fee (uitf.com.ph PHP and USD classes and the feeder's fact sheet; "
                    "DragonFi lists 1.50%, and the fund is not among the six repriced on 14 Sep; at "
                    "1.50% A, B and C are unchanged, as none holds it) + "
                    "1.13% target-fund TER (PUBLISHED on the feeder's fact sheet)",
        "gross_usd": round(0.6 * MACRO["ltcma_global_eq"] + 0.4 * MACRO["ltcma_global_agg"], 2),
        "gross_note": (f"Three-fifths global equity ({MACRO['ltcma_global_eq']}%) and two-fifths global "
                       f"bonds ({MACRO['ltcma_global_agg']}%, JPM LTCMA {MACRO['ltcma_edition']} global aggregate)."),
        "vol_beta": 0.55, "fx_exposed": True,             # ASSUMPTION: a 60/40 global book
        "macro_tilt": {"rates": -0.10, "energy": -0.05},
        "dd_k_adj": 0.0, "cash_like": False,
        "dd_k_why": "At the 1.65 anchor: a balanced book; its bond share is already in its volatility.",
        "equity_share": 0.6, "trend_market": "M_GEO",
        "role": "Balanced — global stocks and bonds, managed",
        "exposure": ["BlackRock Global Funds — Global Allocation Fund (Luxembourg SICAV)",
                     "About 60% global equities, 40% bonds and cash, moved by the manager",
                     "The most diversified single fund on the list"],
    },
]
F_ADD = [build_fund(f) for f in ADD_FUNDS]
_ADD_IX = {f["id"]: i for i, f in enumerate(ADD_FUNDS)}

# ---- Correlation matrix -----------------------------------------------------
# Order: ATRPHMM, ATRQIAP, ATRASEQ, ATRGTEC
CORR = [
    [1.00, 0.00, 0.00, 0.00],
    [0.00, 1.00, 0.66, 0.88],
    [0.00, 0.66, 1.00, 0.74],
    [0.00, 0.88, 0.74, 1.00],
]
CORR_NOTE = ("Money market is treated as uncorrelated to the equity sleeves. "
             "Nasdaq Equity Income / Global Technology at 0.88 is the binding "
             "constraint - both are US mega-cap-tech engines, so holding both "
             "at size buys far less diversification than it appears to.")

# The typed five-fund block: the four-fund matrix above unchanged, plus Global Dividend,
# whose pairs came from the 21 Oct review's factor model (its fit reproduces the 0.88 /
# 0.66 / 0.74 above). Order: MM, Nasdaq Income, Asia, Tech, Global Dividend.
CORR_5 = [r + [x] for r, x in zip(CORR, (0.00, 0.61, 0.59, 0.69))] + [
    [0.00, 0.61, 0.59, 0.69, 1.00],
]

# THE FACTOR MODEL BEHIND EVERY PAIR OUTSIDE THAT BLOCK (2026-10-22). Eleven funds make
# 55 pairs; typing them would be 55 numbers nobody could check. They come instead from
# the 21 Oct review's factor model, whose fit reproduces the typed block above to two
# decimals (a check below holds it to that): each fund's USD return loads on six factors
# - G global equity, GW growth, EM emerging markets, CY cyclicals and commodities, RG
# global rates (duration), RP peso rates - plus its own idiosyncratic part, so that its
# volatility is exactly the one build_fund() gives it; every unhedged fund then carries
# the same peso coupling (FX_CORR with its own return) that combine_fx() applies. The
# loadings are ESTIMATES, recorded in CLAIMS.md. The typed block is kept as published.
FACTORS = ("G", "GW", "EM", "CY", "RG", "RP")
FACTOR_LOADINGS = {
    "ATRPHMM": {"RP": 0.2},
    "ATRQIAP": {"G": 12.0, "GW": 7.5, "RG": 3.0},
    "ATRASEQ": {"G": 12.9, "GW": 6.1, "EM": 11.3, "CY": 3.0, "RG": 1.0},
    "ATRGTEC": {"G": 21.7, "GW": 11.9, "RG": 5.0},
    "ATRGLDV": {"G": 13.5, "GW": -2.0, "CY": 4.0, "RG": 2.0},
    "ATRGHCP": {"G": 12.0, "RG": 3.0},
    "M_GINF": {"G": 11.0, "CY": 3.0, "RG": 6.0},
    "M_GEO": {"G": 18.0, "GW": 7.0, "CY": 3.0, "RG": 3.0},
    "M_GCT": {"G": 19.0, "GW": 13.0, "CY": 6.0, "RG": 4.0},
    "ATRAMIP": {"G": 5.5, "EM": 4.5, "RG": 2.5},
    "M_GALL": {"G": 9.0, "GW": 1.5, "RG": 3.0},
}

def factor_corr(specs):
    """Peso-terms correlations from the factor model, for the specs given."""
    rows = []
    for f in specs:
        s = f["vol_beta"] * SP_VOL_LT                      # the asset's own volatility
        L = [FACTOR_LOADINGS[f["id"]].get(k, 0.0) for k in FACTORS]
        sq = sum(x * x for x in L)
        if sq > s * s:                                     # factors may not exceed the total
            k_ = math.sqrt((s * s - 1e-6) / sq); L = [x * k_ for x in L]; sq = s * s - 1e-6
        u = 1.0 if f["fx_exposed"] else 0.0
        rows.append((L, s * s - sq, u, FX_CORR * FX_VOL * s * u))
    n = len(rows)
    cov = [[sum(a * b for a, b in zip(rows[i][0], rows[j][0])) + (rows[i][1] if i == j else 0.0)
            + rows[j][2] * rows[i][3] + rows[i][2] * rows[j][3] + rows[i][2] * rows[j][2] * FX_VOL ** 2
            for j in range(n)] for i in range(n)]
    sd = [math.sqrt(cov[i][i]) for i in range(n)]
    return [[cov[i][j] / (sd[i] * sd[j]) for j in range(n)] for i in range(n)]

_ALL_SPECS = FUNDS + ADD_FUNDS
_FC = factor_corr(_ALL_SPECS)
_NU = len(_ALL_SPECS)
# Published at two decimals, like the typed block; the typed block wins inside itself.
CORR_U = [[(CORR_5[i][j] if i < 5 and j < 5 else (1.0 if i == j else round(_FC[i][j], 2)))
           for j in range(_NU)] for i in range(_NU)]
# BOUND to the matrix: the ranges are read from it, never typed.
_IDX = {f["id"]: i for i, f in enumerate(_ALL_SPECS)}
_GDIV_EQ = CORR_U[_IDX["ATRGLDV"]][1:4]
_ADD_EQ = [CORR_U[i][j] for i in range(5, _NU) for j in range(1, _NU) if j != i]
CORR_U_NOTE = (f"Global Dividend moves with the other equity sleeves "
               f"({min(_GDIV_EQ):.2f}-{max(_GDIV_EQ):.2f}): a different style of equity, "
               f"not a hedge. The six added from the 22-fund list run "
               f"{min(_ADD_EQ):.2f}-{max(_ADD_EQ):.2f} with the other funds, from a factor model "
               f"fitted to the original block. With the peso bond funds removed, the money "
               f"market is the only sleeve that does not fall with equities.")

# Every portfolio function takes an optional UNIVERSE - (funds built, fund specs,
# correlation). The default is the four original funds, which the budget's reference
# baseline is measured on; every pick passes the eleven-fund UNIV.
def _univ(u):
    return u if u is not None else (F, FUNDS, CORR)

def port_vol(w, u=None):
    Fs, _, C = _univ(u)
    s = [w[i] * Fs[i]["vol"] for i in range(len(w))]
    v = 0.0
    for i in range(len(w)):
        for j in range(len(w)):
            v += s[i] * s[j] * C[i][j]
    return math.sqrt(v)

def port_ret(w, key, u=None):
    Fs, _, _ = _univ(u)
    return sum(w[i] * Fs[i][key] for i in range(len(w)))

def port_k(w, u=None):
    """Weight-averaged drawdown coefficient, ex-cash (cash contributes no equity DD)."""
    _, FS, _ = _univ(u)
    eq = sum(w[i] for i in range(len(w)) if not FS[i]["cash_like"])
    if eq <= 0:
        return DD_K
    return DD_K + sum(w[i] * FS[i]["dd_k_adj"] for i in range(len(w))
                      if not FS[i]["cash_like"]) / eq

def port_dd(w, key, u=None):
    mu = port_ret(w, key, u)
    return -max((port_k(w, u) * port_vol(w, u) - DD_MU * mu) * DD_HORIZON_SCALAR, 0.0)

def summarise(w, key, u=None):
    r, v, d = port_ret(w, key, u), port_vol(w, u), port_dd(w, key, u)
    # The peso illustration is computed from the ROUNDED figures the page shows,
    # not the raw ones, so a reader who multiplies out the displayed CAGR gets
    # exactly the peso number printed beside it. Using the raw values instead
    # left a ~P235 gap that nobody could reconcile. (Audit 2026-09-03.)
    # Every published RATIO is built from the published (rounded) inputs for the
    # same reason: ret_per_dd used raw r and raw d while cagr and maxdd printed
    # rounded, so a reader dividing 7.33 by 28.9 got 0.254 against a printed
    # 0.253 - two of the four portfolios failed to reconcile. The 2026-09-03 fix
    # was applied to the peso figures and missed the ratios three lines above
    # them. (Audit 2026-09-10.)
    # The PUBLISHED drawdown is rebuilt from the published cagr and vol, not
    # rounded down from the raw one. The two agreed today - but only by luck of
    # where the numbers fell: the baseline under macro came out -29.0019 raw
    # against -29.0080 by the reader's route, 0.006pp from rounding to different
    # tenths. The page invites the reader to reproduce the drawdown from the k,
    # vol and CAGR printed beside it, so that route is the one that defines the
    # number. This is the same fix already applied to the peso figures (2026-09-03)
    # and the ratios (2026-09-10), and the scenario rows have always worked this
    # way; the headline rows were the last place the raw value still surfaced.
    # port_dd() itself is UNCHANGED and still raw - the optimiser's constraint must
    # test the true drawdown, not a display value.  (Audit 2026-09-20.)
    r_d, v_d = round(r, 2), round(v, 2)
    d_d = round(-max((port_k(w, u) * v_d - DD_MU * r_d) * DD_HORIZON_SCALAR, 0.0), 1)
    return {
        "weights": [round(x * 100, 1) for x in w],
        "cagr": r_d, "vol": v_d, "maxdd": d_d,
        "ret_per_dd": round(r_d / abs(d_d), 3) if d_d else None,
        "sharpe_like": round((r_d - MACRO["ph_tbill_364"]) / v_d, 3),
        "terminal_1m": round(1_000_000 * (1 + r_d / 100) ** HORIZON_Y),
        # The drawdown applied to the OPENING peso value. Read it as "the worst
        # this is expected to look for money invested today", before any growth
        # cushion has been built - which is the number that matters to someone
        # deciding now. It is deliberately NOT the trough of the modelled path:
        # drawdown is defined peak-to-trough, and a drawdown arriving late in a
        # 10-year mandate starts from a peak well above P1,000,000. The page
        # used to label this "Value at expected trough", which asserted the
        # second reading while computing the first. (Audit 2026-09-10.)
        "worst_1m_from_open": round(1_000_000 * (1 + d_d / 100)),
    }

# ----------------------------------------------------------------------------
# 5b. STOCK-LEVEL LOOK-THROUGH
#     Published holdings of the target funds. Only what a manager actually
#     discloses goes here; where a target fund does not publish current
#     holdings, that is recorded as a gap rather than filled with a guess.
# ----------------------------------------------------------------------------

_GDIV_T3 = round(sum(v for _, v in GDIV_GEO["EUROPE"][:3]), 1)
_GDIV_US = round(GDIV_GEO["US"][0][1], 1)
LOOKTHROUGH = {
    "ATRPHMM": {
        "dp": 3,
        "kind": "instruments",
        # Dated by the AUCTION, not by AS_OF. The 2026-09-13 fix replaced a wrong
        # "2026-08" label with AS_OF on the theory that these were the live curve;
        # they were not refreshed again, so AS_OF made a 2 Sep curve look current
        # for eleven days. A date must belong to the number it labels.
        "as_of": MACRO["ph_tbill_date"],
        "note": "A money market fund holds paper, not shares: the T-bill curve is "
                "its look-through.",
        "rows": [["91-day T-bill", MACRO["ph_tbill_91"]],
                 ["182-day T-bill", MACRO["ph_tbill_182"]],
                 ["364-day T-bill", MACRO["ph_tbill_364"]]],
        "unit": "% yield",
        "source": "Bureau of the Treasury PH auction results",
    },
    "ATRQIAP": {
        "dp": 1,
        "kind": "stocks",
        # REFRESHED 2026-10-03 to the 31 August factsheet: the 31 July sheet had
        # reached 64 days against the 60-day bound. Tesla enters at 2.1% and Lam
        # Research leaves; Micron moves up to fifth. The sector weight is DROPPED,
        # not carried over: the July sheet's 47.7% Information Technology was not
        # re-read for August, and a July figure beside August rows would be a
        # mixed-date table. (The 2dp "September" list in circulation is the same
        # data at the same $42.21bn of assets - an August sheet re-labelled - and
        # is not carried.)
        "as_of": "2026-08-31",
        "note": "Top 10 of the strategy, from the US-listed JEPQ factsheet; the "
                "feeder holds the UCITS sister fund, which runs the same strategy. "
                "Still the latest sheet found (checked 2026-10-23).",
        "rows": [["NVIDIA", 7.3], ["Apple", 6.4], ["Microsoft", 5.3],
                 ["Alphabet Class C", 4.8], ["Micron Technology", 4.6],
                 ["Amazon", 4.0], ["Advanced Micro Devices", 3.1],
                 ["Meta Platforms", 2.4], ["Broadcom", 2.1], ["Tesla", 2.1]],
        "unit": "% of fund",
        "source": "J.P. Morgan Asset Management JEPQ factsheet, 31 August 2026",
    },
    "ATRASEQ": {
        "dp": 1,
        "kind": "gap",
        "as_of": None,
        # RETRIED 2026-10-03, and the note was wrong about the gap's size: an
        # aggregator now shows a 30 April 2026 top 10 (TSMC 9.65%, Samsung pref
        # 5.32%, Tencent 4.64% ...), not only 2023 data. It is still five months
        # old - past the 60-day bound every look-through is held to - and not from
        # JPMorgan itself, so it is described, not shown.
        "note": "No current holdings from a primary source. The newest list found "
                "is an aggregator's from 30 April 2026, past the 60-day limit, so it "
                "is not shown. The mandate is verified: at least 70% in "
                "dividend-paying Asia Pacific ex-Japan equities.",
        "rows": [],
        "unit": None,
        "source": "gap recorded rather than filled - retry at each manual review",
    },
    "ATRGTEC": {
        "dp": 1,
        "kind": "stocks",
        # UPGRADED 2026-10-10 from sector weights to the stocks themselves. The
        # note here said Fidelity published "no current top-10 list at a source
        # reachable from here"; its 31 August 2026 factsheet (Singapore edition,
        # 98 positions) now is. Nine holdings are shown, not ten: the sheet's text
        # drops the NAME of a 2.1% position between Oracle and Netflix, and a
        # holding is not guessed. The ICB sector table shown until today was dated
        # by when it was read (13 Sep), because its page carried no date; these
        # GICS sectors and the geography come from the dated sheet.
        # CHECKED 2026-10-23: a 30 Sep sheet is listed (95 positions; TSMC 9.6,
        # Microsoft 7.1, Apple 5.7), but two reads of it disagree on its date and its
        # country table, so it is not carried. The 31 Aug sheet stays, inside the
        # 60-day bound until 30 Oct.
        "as_of": "2026-08-31",
        # "Less American than its benchmark" was cut 2026-10-15: the benchmark's
        # country weights are not an input, and the ~72% US figure the page typed
        # for them had no source.
        "note": "From Fidelity's 31 August 2026 factsheet (98 positions). The "
                "tenth holding, a 2.1% position, is not named in the text "
                "reachable here, so it is left out rather than guessed.",
        "rows": [["Taiwan Semiconductor", 9.1], ["Microsoft", 6.9], ["Apple", 5.4],
                 ["Alphabet", 4.4], ["Amazon", 3.8], ["ASML", 3.6],
                 ["Texas Instruments", 3.6], ["Oracle", 2.2], ["Netflix", 2.0]],
        "unit": "% of fund",
        "sectors": [["Information Technology", 65.7], ["Communication Services", 13.5],
                    ["Consumer Discretionary", 7.4]],
        "geo": [["USA", 53.5], ["Taiwan", 10.8], ["Netherlands", 8.6]],
        "unnamed_pct": 2.1, "positions": 98,
        "source": "Fidelity Funds - Global Technology Fund factsheet, 31 August 2026 "
                  "(Fidelity International, Singapore edition)",
    },
    # ---- the fund beyond the original four (2026-10-21) ----
    "ATRGLDV": {
        "dp": 1,
        "kind": "stocks",
        # The target fund's 30 Sep 2026 factsheet (Singapore edition). The UK OEIC
        # run by the same manager shows the same names at 31 Aug (TSMC 3.7, Roche
        # 3.6, Deutsche Boerse 3.5, Unilever 3.3, Vinci 3.2) - a cross-check, not
        # the source.
        "as_of": "2026-09-30",
        # Bound to GDIV_GEO, not typed: the comparison is computed, published beside
        # the note so the figure traces, and worded from it.
        "geo_top3_pct": _GDIV_T3, "geo_us_pct": _GDIV_US,
        "note": ("Top 10 of Fidelity Funds - Global Dividend Fund (US$21.4bn), the "
                 "feeder's target. Germany, France and Switzerland together "
                 f"({_GDIV_T3:.1f}%) {'outweigh' if _GDIV_T3 > _GDIV_US else 'trail'} the US "
                 f"({_GDIV_US:.1f}%, from an older listing)."),
        "rows": [["Taiwan Semiconductor", 4.0], ["Deutsche Boerse", 3.4], ["Unilever", 3.4],
                 ["Roche", 3.4], ["Vinci", 3.1], ["Novartis", 2.8],
                 ["Texas Instruments", 2.8], ["CME Group", 2.8], ["Legrand", 2.7],
                 ["Shin-Etsu Chemical", 2.7]],
        "unit": "% of fund",
        "geo": [["Germany", 11.2], ["France", 9.6], ["Switzerland", 8.9]],
        "source": "Fidelity Funds - Global Dividend Fund factsheet, 30 September 2026 "
                  "(Fidelity International, Singapore edition)",
    },
    # ---- the six added from the 22-fund list (2026-10-22): declared gaps ----
    # Each target is named and its charge sourced, but no current top-10 table was
    # reachable for any of them, so none is typed from memory.
    "ATRGHCP": {"kind": "gap", "as_of": "2026-08-31",
                "top2": [["Eli Lilly", 8.7], ["AbbVie", 7.4]], "positions": 41,
                "note": "Fidelity Funds - Global Healthcare Fund. Its 31 Aug 2026 Singapore factsheet "
                        "lists Eli Lilly (8.7%) and AbbVie (7.4%) as the largest of 41 positions; the "
                        "full top 10 was not legible in the text reached.",
                "source": "Fidelity Funds - Global Healthcare Fund factsheet, 31 August 2026 (Singapore edition), partial"},
    "M_GINF": {"kind": "gap",
               "note": "HSBC GIF Global Infrastructure Equity. No holdings table was reachable.",
               "source": "ATRAM Global Infra Equity Feeder Fund fact sheet (target change, March 2025)"},
    "M_GEO": {"kind": "gap",
              "note": "Allianz Thematica. No holdings table was reachable.",
              "source": "ATRAM Global Equity Opportunity Feeder Fund KIID, 31 March 2026"},
    "M_GCT": {"kind": "gap",
              "note": "Invesco Global Consumer Trends Fund. No holdings table was reachable.",
              "source": "ATRAM Global Consumer Trends Feeder Fund KIID"},
    "ATRAMIP": {"kind": "gap",
                "alloc": [["equities", 50.17], ["bonds", 38.85], ["cash", 5.89]],
                "note": "Schroder Asian Asset Income Fund: 50.17% equities, 38.85% bonds and 5.89% cash "
                        "on an undated aggregator page; no holdings table was reachable.",
                "source": "Investing.com holdings page (undated); BusinessWorld, 6 Sep 2022 (the target)"},
    "M_GALL": {"kind": "gap",
               "note": "BlackRock Global Funds - Global Allocation Fund. No holdings table was reachable.",
               "source": "ATRAM Global Allocation Feeder Fund fact sheet"},
}

# ----------------------------------------------------------------------------
# 6. PORTFOLIOS
# ----------------------------------------------------------------------------

# --- The budget's reference: the original no-view baseline -------------------
# A 20% liquidity buffer and the three equity engines held near-equally. It was
# Portfolio A until 2026-10-21, when the owner replaced A with the 22-fund review's
# highest-return pick (PA_W below). It stays here as the REFERENCE the drawdown
# budget is measured from, so the budget means what it meant: replacing it with
# the new A would make the budget depend on the portfolio it is used to judge.
BASELINE_W = [0.20, 0.30, 0.25, 0.25]
BASE = summarise(BASELINE_W, "net_base")
BASE_UNDER_MACRO = summarise(BASELINE_W, "net_macro")

# --- The drawdown budget ----------------------------------------------------
# Objective: the user asked for maximum net CAGR with drawdown held to a
# minimum. A pure max-return solve just buys the highest-return sleeve; a pure
# min-DD solve just buys cash. The defensible reading is: cut the reference's
# drawdown by a hard, stated amount and take the best return inside that:
#   maxDD <= baseline maxDD - 2.0pp  (a hard, stated improvement)
# 2.0pp was the stated improvement at the 5-year calibration. Drawdowns are
# ~41% deeper at a 10-year horizon, so holding the budget at a flat 2.0pp would
# quietly LOOSEN the objective. It is scaled by the same factor as the drawdowns
# it constrains, so the constraint means what it meant before.
DD_BUDGET_IMPROVEMENT = round(2.0 * DD_HORIZON_SCALAR, 2)
DD_CAP_DERIVED = abs(BASE_UNDER_MACRO["maxdd"]) - DD_BUDGET_IMPROVEMENT
# THE OWNER'S 25% IS THE BASE FROM v75 (2026-10-27: "Apply the 25% drawdown to all
# portfolios"), after a sweep of the rule from 18% to 32% found the trade-off of
# Portfolio C (retired in v76) bending there: below 25% each point of drawdown accepted
# earned about 0.11pp a year, above it about 0.07pp. Until v74 the budget was the
# derivation above (-26.97% on 26 Oct); it stays published beside it as the reference it
# replaced, and it is the ceiling the gauge may raise the budget towards, never past.
# FROM v77 THE BAND SETS THE BUDGET (owner, 2026-10-28: "Use the budget drawdown band to
# portfolio A and B"): DD_CAP is the gauge's recommended step - the base while the
# reading sits in the hold band, or a guard is not clear; the band's step once two
# month-end reviews in a row read it and, for a raise, both risk guards are clear.
DD_BUDGET_OWNER = 25.0
DD_BUDGET_OWNER_DATE = "2026-10-27"
DD_BUDGET_BAND_DATE = "2026-10-28"

# ----------------------------------------------------------------------------
# THE DRAWDOWN BUDGET GAUGE (owner, 2026-10-27: "a best recommended gauge 1 to 5 when to
# increase the drawdown of the portfolio based on macro sentiments, volatility, market
# trends of 3, 5 and 10yrs"). FROM v77 IT SETS THE BUDGET (owner, 2026-10-28: "Use the budget
# drawdown band to portfolio A and B"): DD_CAP is the recommended step below, which leaves
# the owner's 25% base only when the guards allow it. It reads, at each view, three things
# this model already publishes on 1-5, 3 neutral:
#   MACRO  the driver gauge at that horizon (GAUGE_PATH) - the seven drivers' path;
#   VOL    the forward implied volatility of the years the view covers against the
#          long-run level every base return assumes: 3 - (forward / long-run - 1) / step,
#          one point per DDG_VOL_STEP (10%) of the long-run level, clipped to 1-5. The
#          step is an ASSUMPTION, stated as one;
#   TREND  the market-trend score at that horizon, averaged over the trend markets.
# A view's reading is the mean of the three. THE GAUGE READS THE 3- AND 5-YEAR VIEWS ONLY,
# weighted by the years of the first five each covers (3/5 and 2/5): the 10-year view is
# neutral by construction for the drivers and the trend, and its volatility years sit at
# the long run, so it carries no timing information - it is what the fixed budget
# itself stands for. Weighted in, it would pin the gauge between 2 and 4 and make the
# outer bands unreachable. It is shown beside the other two, not hidden.
# The reading maps to a step of the budget (DDG_BANDS); a step away from 25% is acted on
# only when two consecutive month-end reviews read the same band, and a RAISE also needs
# both risk guards clear: the Geopolitics & energy reading above 2.0 (1-10) - the Hormuz
# tail the stress grid prices - and the VIX at or below its long run. The ceiling is 27%,
# the derived budget the owner's figure replaced; the floor 24%.
DDG_VOL_STEP = 0.10
DDG_VIEWS = tuple(h for h in HZ_KEYS if h != HZ_LABEL)
DDG_W = {h: round((_HZ_YEARS[h] - (_HZ_YEARS[DDG_VIEWS[i - 1]] if i else 0.0))
                  / _HZ_YEARS[DDG_VIEWS[-1]], 2) for i, h in enumerate(DDG_VIEWS)}
DDG_BANDS = [  # [lo, hi) on the 1-5 reading, the budget it points to, the action
    (1.0, 2.5, 24.0, "Tighten to 24%"),
    (2.5, 3.5, 25.0, "Hold at 25%"),
    (3.5, 4.25, 26.0, "Raise to 26%"),
    (4.25, 5.0001, 27.0, "Raise to 27%"),
]
DDG_GEO_FLOOR = 2.0
DDG_REVIEWS_NEEDED = 2
# Month-end readings on record, oldest first: (date, reading). The first is due at the
# 31 Oct roll; until two share a band, no step is taken.
DDG_REVIEWS = []
_VOL_FWD = {v["label"]: v["forward"] for v in VOL_TS}

def _ddg_vol(h):
    return round(min(5.0, max(1.0, 3.0 - (_VOL_FWD[h] / MACRO["vix_longrun"] - 1) / DDG_VOL_STEP)), 2)

def _ddg_trend(h):
    return round(sum(TREND[f]["score"][h] for f in TREND) / len(TREND), 2)

DDG_PARTS = {h: {"macro": GAUGE_PATH[h], "vol": _ddg_vol(h), "trend": _ddg_trend(h),
                 "vol_forward": _VOL_FWD[h]} for h in HZ_KEYS}
for _h in HZ_KEYS:
    _p = DDG_PARTS[_h]
    _p["reading"] = round((_p["macro"] + _p["vol"] + _p["trend"]) / 3, 2)
DDG_VALUE = round(sum(DDG_PARTS[h]["reading"] * DDG_W[h] for h in DDG_VIEWS), 2)
DDG_BAND = next(b for b in DDG_BANDS if b[0] <= DDG_VALUE < b[1])
_geo_now = next(s_ for n_, _, s_, _ in DRIVERS if n_.startswith("Geopolitics"))
DDG_GUARDS = [
    {"name": "persistence", "ok": (len(DDG_REVIEWS) >= DDG_REVIEWS_NEEDED and all(
        next(b for b in DDG_BANDS if b[0] <= v_ < b[1]) == DDG_BAND
        for _, v_ in DDG_REVIEWS[-DDG_REVIEWS_NEEDED:])),
     "reviews": len(DDG_REVIEWS), "needed": DDG_REVIEWS_NEEDED, "applies_to": "any step"},
    {"name": "geopolitics", "ok": _geo_now > DDG_GEO_FLOOR, "reading": _geo_now,
     "floor": DDG_GEO_FLOOR, "applies_to": "raise"},
    {"name": "vix", "ok": MACRO["vix_latest"] <= MACRO["vix_longrun"], "reading": MACRO["vix_latest"],
     "longrun": MACRO["vix_longrun"], "applies_to": "raise"},
]
_raise = DDG_BAND[2] > DD_BUDGET_OWNER
_step_ok = all(g_["ok"] for g_ in DDG_GUARDS
               if g_["applies_to"] == "any step" or (g_["applies_to"] == "raise" and _raise))
DDG_RECOMMENDED = DDG_BAND[2] if (DDG_BAND[2] != DD_BUDGET_OWNER and _step_ok) else DD_BUDGET_OWNER
DDG_BLOCKED_BY = [g_["name"] for g_ in DDG_GUARDS if DDG_BAND[2] != DD_BUDGET_OWNER and not g_["ok"]
                  and (g_["applies_to"] == "any step" or _raise)]

DD_CAP = DDG_RECOMMENDED

# ONE SELECTION RULE FOR EVERY PORTFOLIO - unified 2026-10-07 at the owner's
# instruction ("the best and recommended approach to reach max growth ... while
# controlling the drawdown to minimum"). From then until v76 it took the best CAGR the
# budget allows and, among the portfolios within 0.05pp of it, the one with the LOWEST
# drawdown: a return difference below the model's precision was not worth more drawdown.
# MAXIMUM GROWTH FROM v77 (owner, 2026-10-28: "the best and recommended approach to
# reach maximum growth 10yrs cagr minus fund fees ... Use the budget drawdown band"):
# the drawdown is held by the band's budget, so the rule takes the HIGHEST net CAGR the
# budget allows; a shallower drawdown decides only between mixes that print the same
# CAGR (then the lower true drawdown, then the mix generated first).
# On the v76 inputs at 25% it adds 0.04pp a year to A and 0.05pp to B for 0.4pp and
# 0.6pp more drawdown - the size of the tolerance it replaces, inside the budget.
PIN_TIE_PP = 0.0

# The rule itself is _Pick, below with the search: it streams every mix once.

# PORTFOLIO C, RESTORED (owner, 2026-10-29: "Make portfolio C with 50% atram nasdaq equity
# income allocation based on 3, 5, 10yrs volatility, market trend, macroeconomic sentiments
# and regional rankings deep analysis from the 22 atram lists. Use budget drawdown band for
# portfolio C."). Retired in v76 (2026-10-28), it was the owner's pinned variant from
# 2026-09-25 to v75. It comes back on the v77 rule: Nasdaq Equity Income held at exactly 50%,
# the rest chosen around it - maximum growth, the highest net CAGR after fees on the
# 3/5/10-year view (B's column) whose drawdown is inside the band's budget, as computed and
# as shown - over the same eleven funds and the same limits, the pin the one exemption from
# the 35% cap. Its own pass over the pinned set; A and B read nothing of it.
PIN_W = 0.50

# ONE RULE FOR A AND B, OVER ONE UNIVERSE (2026-10-21, at the owner's instruction:
# "make the portfolio a, b and c to max growth 10yrs net cagr with minimum drawdown",
# with B and C "based on macro economics drivers, market trend, volatility, regional
# rankings ... of 3, 6, and 12 months with horizon of 10yrs"). Every pick is the page's
# one rule - the best net CAGR the drawdown budget allows, then the lowest drawdown
# within the tie - over every fund on the owner's 22-fund list whose fees are
# confirmed (eleven since 2026-10-22; five from 21 Oct, when the peso bond funds left,
# and six before), under the review's limits: at most 5 funds, 35% in any one, at
# least 5% peso cash. What differs is the COLUMN the rule reads:
#   A  net_10y    the four analyses read at the 10-year horizon alone (2026-10-26; the
#                 long-run assumptions with no view, net_base, until v67)
#   B  net_macro  the four analyses at every horizon - the regional ranking, the
#                 market trend and the drivers' rates and energy tilts at 3, 5 and 10
#                 years (5 and 10 in v70; 1, 3, 5 and 10 in v68-v69), and the
#                 volatility curve over the same years
# (C, B with Nasdaq Equity Income held at 50%, was retired in v76; D, C over four funds,
# in v74.)
# Until v56 A and B were FIXED weights from the review; the engine now chooses both
# itself, on every roll. Whether A matches the review's own long-run pick is
# published (portfolio_a.is_review_pick), never assumed: the review's pick (25% Global
# Health Care) is not the engine's, now with every fund in it modelled.
# The four-fund optimiser that ran beside them off the page, kept only for its own
# checks, was retired on 2026-10-22 (v62); the baseline above is all that is left of it.
UNIV = (F + F_ADD, FUNDS + ADD_FUNDS, CORR_U)
UNIV_IDS = [f["id"] for f in UNIV[1]]
FRONTIER_SPACING = 0.9     # a frontier point every 0.9pp of drawdown
UNIV_MAX_FUNDS = MACRO["pd_review_max_funds"]
UNIV_MAX_W = MACRO["pd_review_max_w"] / 100
UNIV_MIN_CASH = MACRO["pd_review_min_cash"] / 100

# WHAT WOULD CHANGE THIS VIEW - computed, not asserted. The page's list said that
# "Brent below $70 and the Fed cutting" would send Global Technology "back to a full
# weight"; re-running the optimiser showed the allocation does not move at all. Each
# counterfactual here is the SAME rule on an alternative return column, inside the
# SAME drawdown budget (DD_CAP), so the only thing that differs is the input named.
for _f in F + F_ADD:
    _f["net_novol"] = round(_f["net_macro"] - _f["tilt_vol"], 2)       # flat VIX curve
    _f["net_neutral"] = round(_f["net_macro"] - _f["tilt_rates"]
                              - _f["tilt_energy"], 2)                  # drags at neutral
    _f["net_notrend"] = round(_f["net_macro"] - _f["tilt_trend"], 2)   # no trend channel
    # Asia's trend on the alternative source for its one disputed quarter, for every fund
    # that carries Asia's trend (a multi-asset fund at its equity share)
    _m = _f["trend_market"]
    _f["net_trend_alt"] = round(_f["net_macro"] - _f["tilt_trend"]
                                + ((TREND_ALT_BUILT[_m]["tilt"] if _f["equity_share"] == 1.0
                                    else rnd(TREND_ALT_BUILT[_m]["tilt"] * _f["equity_share"]) + 0.0)
                                   if _m in TREND_ALT_BUILT else _f["tilt_trend"]), 2)

# THE TWO ASSUMPTIONS THE 2026-09-25 CORRECTION LEFT CARRYING THE RESULT, tested
# the same way: the Asia base's +1.0% re-rating credit (which overlaps both the
# LTCMA's own valuation component and the Valuation driver in the regional tilt),
# and its ESTIMATED target-fund charge (a Hong Kong unit trust whose trustee and
# admin costs may put the OCF above the 1.55% carried). A result that one
# assumption can overturn is published with that assumption named.
ASIA_FEE_STRESS = 0.25
# (The 2026-09-25 correction record that fed a Report note was retired on
# 2026-10-15 with the note; the correction itself is in monitoring/CHANGELOG.md.)
for _f in F + F_ADD:
    _aseq = _f["id"] == "ATRASEQ"
    # Every fund that carries the credit loses it, at its share (2026-10-22: the Asian
    # multi-asset fund's equity half carries it too).
    _f["net_asia_norerate"] = round(_f["net_macro"] - MACRO["asia_rerating"] * _f["asia_rerating_share"], 2)
    _f["net_asia_fee_hi"] = round(_f["net_macro"] - (ASIA_FEE_STRESS if _aseq else 0.0), 2)
# The alternative columns the universe what-ifs are run on.
_WI_COL = {"vol_flat": "net_novol", "drags_neutral": "net_neutral",
           "asia_no_rerating": "net_asia_norerate", "asia_fee_hi": "net_asia_fee_hi",
           "trend_off": "net_notrend", "trend_alt": "net_trend_alt"}
# EACH PORTFOLIO ON ITS OWN HORIZON (owner, 2026-10-28: "Update portfolio A to 10yrs
# horizon and portfolio B to 3, 5, 10yrs horizons"). A is chosen on the 10-year column,
# so its what-ifs are measured there too: the same change applied to the 10-year view.
# That view carries no rates, energy or trend tilt and the curve's years 6-10, so four
# of the six leave A where it is by construction - which is the finding, not a gap.
for _f in F + F_ADD:
    _f["net10_novol"] = round(_f["net_10y"] - _f["tilt_vol_10y"], 2)
    _f["net10_neutral"] = round(_f["net_10y"] - _f["tilt_rates_10y"] - _f["tilt_energy_10y"], 2)
    _f["net10_notrend"] = _f["net_10y"]          # the 10-year trend anchor is neutral
    _f["net10_trend_alt"] = _f["net_10y"]
    _f["net10_asia_norerate"] = round(_f["net_10y"] - MACRO["asia_rerating"] * _f["asia_rerating_share"], 2)
    _f["net10_asia_fee_hi"] = round(_f["net_10y"] - (ASIA_FEE_STRESS if _f["id"] == "ATRASEQ" else 0.0), 2)
_WI_COL10 = {k: "net10_" + v[4:] for k, v in _WI_COL.items()}

# ---- THE SEARCH (rewritten 2026-10-22 for the eleven-fund universe) ----------
# Until v62 the universe was every point of a 21^(n-1) grid, filtered - fine for five
# funds, impossible for eleven. The limit-respecting mixes are generated directly
# instead: the money market (5-35%) plus up to four other funds, each 5-35%, on the 5%
# grid, summing to 100 - the same set, in a fixed order.
# Each mix is measured by the SAME ARITHMETIC as port_ret / port_vol / port_k /
# summarise(), term for term in index order, so a pick re-measured by summarise()
# lands on exactly the figures the search saw. Feasible means inside the budget as
# computed AND as shown: the raw drawdown alone admits a mix that PRINTS over the cap
# ([25, 30, 25, 20] at 26.1477 raw against a 26.17 cap printed -26.2, 2026-09-20); the
# printed one alone admits one up to 0.05pp genuinely over it (2026-09-03).
# THE RULE'S ORDER, now total: the lowest published drawdown, then the higher published
# CAGR, then the lower TRUE drawdown, then the mix generated first. The third key was
# added with the search: two mixes can print the same drawdown and CAGR, and the one
# that is genuinely shallower should win, not whichever the loop met first.
_UN = len(UNIV_IDS)
_UF, _US, _UC = UNIV
_VOL = [f["vol"] for f in _UF]
_ADJ = [f["dd_k_adj"] for f in _US]
_CASH = [f["cash_like"] for f in _US]
_MAXU, _CASHU = round(UNIV_MAX_W * 20), round(UNIV_MIN_CASH * 20)
_IQ, _PINU = UNIV_IDS.index("ATRQIAP"), round(PIN_W * 20)

def _comps(total, parts, lo, hi):
    """Every way to split `total` units into `parts` ordered parts, each in [lo, hi]."""
    if parts == 1:
        if lo <= total <= hi:
            yield (total,)
        return
    for x in range(lo, min(hi, total - lo * (parts - 1)) + 1):
        for rest in _comps(total - x, parts - 1, lo, hi):
            yield (x,) + rest

def univ_mixes(pinned=False):
    """Every limit-respecting mix as (indices, units) - units of 5%, indices ascending.
    pinned: Portfolio C's set - Nasdaq Equity Income fixed at the pin, the rest as usual."""
    others = [i for i in range(1, _UN) if not (pinned and i == _IQ)]
    free = UNIV_MAX_FUNDS - 1 - (1 if pinned else 0)        # funds beside cash (and the pin)
    rest = 20 - (_PINU if pinned else 0)
    for k in range(0, free + 1):
        for sup in combinations(others, k):
            idx = tuple(sorted((0,) + sup + ((_IQ,) if pinned else ())))
            for comp in _comps(rest, k + 1, 1, _MAXU):
                if comp[0] < _CASHU:
                    continue
                if not pinned:
                    yield idx, comp
                    continue
                it = iter(comp)
                yield idx, tuple(_PINU if i == _IQ else next(it) for i in idx)

def _measure(idx, units, cols):
    """Raw and published figures for one mix on each column, by summarise()'s arithmetic."""
    w = [u / 20 for u in units]
    sv = [w[a] * _VOL[i] for a, i in enumerate(idx)]
    v = 0.0
    for a, i in enumerate(idx):
        for b, j in enumerate(idx):
            v += sv[a] * sv[b] * _UC[i][j]
    v = math.sqrt(v)
    eq = 0
    for a, i in enumerate(idx):
        if not _CASH[i]:
            eq += w[a]
    if eq <= 0:
        k = DD_K
    else:
        ka = 0
        for a, i in enumerate(idx):
            if not _CASH[i]:
                ka += w[a] * _ADJ[i]
        k = DD_K + ka / eq
    v_d = round(v, 2)
    out = []
    for col in cols:
        mu = 0
        for a, i in enumerate(idx):
            mu += w[a] * _UF[i][col]
        raw = -max((k * v - DD_MU * mu) * DD_HORIZON_SCALAR, 0.0)
        r_d = round(mu, 2)
        d_d = round(-max((k * v_d - DD_MU * r_d) * DD_HORIZON_SCALAR, 0.0), 1)
        out.append((r_d, d_d, raw))
    return out

def _key(m):
    """The rule's total order on a measured mix (r_d, d_d, raw, seq, idx, units)."""
    return (abs(m[1]), -m[0], abs(m[2]), m[3])

class _Pick:
    """The rule, streamed: the best feasible CAGR, and every feasible mix within the tie.
    The cap is the live budget unless an alternative is named (the budget gauge's steps)."""
    def __init__(self, cap=None):
        self.best, self.band, self.n = -1e9, [], 0
        self.cap = DD_CAP if cap is None else cap
    def add(self, m):
        r_d, d_d, raw = m[0], m[1], m[2]
        if abs(raw) > self.cap + 1e-9 or abs(d_d) > self.cap + 1e-9:
            return
        self.n += 1
        if r_d > self.best:
            self.best = r_d
            self.band = [x for x in self.band if x[0] >= r_d - PIN_TIE_PP - 1e-9]
        if r_d >= self.best - PIN_TIE_PP - 1e-9:
            self.band.append(m)
    def result(self):
        band = [x for x in self.band if x[0] >= self.best - PIN_TIE_PP - 1e-9]
        win = min(band, key=_key)
        return [u / 20 for u in _full_units(win[4], win[5])], band, win

def _full_units(idx, units):
    """The mix as a full weight-unit vector over the universe."""
    u = [0] * _UN
    for i, x in zip(idx, units):
        u[i] = x
    return u

_WI_KEYS = list(_WI_COL)
# "live" is the macro column again, sent down the what-if path: a check requires it to
# return the published B, so the what-ifs are proved to answer the same question.
_WI_COL["live"] = "net_macro"; _WI_COL10["live"] = "net_10y"; _WI_KEYS.append("live")
_COLS_U = ["net_10y", "net_macro"] + [_WI_COL[k] for k in _WI_KEYS]
# PORTFOLIO D, RETIRED (owner, 2026-10-27: "Remove portfolio D"). From v66 to v73 it was
# the since-retired C's pinned set restricted to four funds - Money Market, Nasdaq Equity
# Income, Asia Equity, Global Technology - and came out of C's loop; removing it changes no other
# pick, because nothing else read its result. A check holds it gone.
_PK = {"a": _Pick(), "b": _Pick(), "c": _Pick()}
_PK.update({("b", k): _Pick() for k in _WI_KEYS})
_PK.update({("c", k): _Pick() for k in _WI_KEYS})   # C re-chosen on each what-if, like B
# The budget gauge's alternative steps (2026-10-27), chosen by the same rule in the same
# pass: what A and B would hold if the budget moved to each - every band's step but the
# one in force.
DDG_STEPS = tuple(sorted({b[2] for b in DDG_BANDS} - {DD_CAP}))
_PKX = {(x, c): _Pick(c) for x in "abc" for c in DDG_STEPS}
_FRONT_BUCKET, _BEST_RATIO_M, UNIV_N_TOTAL = {}, None, 0
for _seq, (_idx, _u) in enumerate(univ_mixes()):
    _ms = _measure(_idx, _u, _COLS_U)
    UNIV_N_TOTAL += 1
    _a = _ms[0] + (_seq, _idx, _u); _b = _ms[1] + (_seq, _idx, _u)
    _PK["a"].add(_a); _PK["b"].add(_b)
    for _c in DDG_STEPS:
        _PKX[("a", _c)].add(_a); _PKX[("b", _c)].add(_b)
    for _k, _m in zip(_WI_KEYS, _ms[2:]):
        _PK[("b", _k)].add(_m + (_seq, _idx, _u))
    # the macro frontier and the best pure ratio, over every limit-respecting mix
    _cur = _FRONT_BUCKET.get(abs(_b[1]))
    if _cur is None or _key(_b) < _key(_cur):
        _FRONT_BUCKET[abs(_b[1])] = _b
    if _b[1]:
        _rt = round(_b[0] / abs(_b[1]), 3)
        if (_BEST_RATIO_M is None or _rt > _BEST_RATIO_M[0]
                or (_rt == _BEST_RATIO_M[0] and _key(_b) < _key(_BEST_RATIO_M[1]))):
            _BEST_RATIO_M = (_rt, _b)

# PORTFOLIO C's own pass (v82): every pinned mix, measured by the same arithmetic, chosen by
# the same rule on the 3/5/10-year column (index 1), at the live budget, at every gauge step
# and on every what-if column.
UNIV_N_PINNED = 0
for _seq, (_idx, _u) in enumerate(univ_mixes(pinned=True)):
    _ms = _measure(_idx, _u, _COLS_U)
    UNIV_N_PINNED += 1
    _cm = _ms[1] + (_seq, _idx, _u)
    _PK["c"].add(_cm)
    for _c in DDG_STEPS:
        _PKX[("c", _c)].add(_cm)
    for _k, _m in zip(_WI_KEYS, _ms[2:]):
        _PK[("c", _k)].add(_m + (_seq, _idx, _u))

PA_W, PA_BAND, _ = _PK["a"].result()
PB_W, PB_BAND, _ = _PK["b"].result()        # Portfolio B
PC_W, PC_BAND, _ = _PK["c"].result()        # Portfolio C, Nasdaq Equity Income at 50%
PA_BAND_N, PB_BAND_N, PC_BAND_N = len(PA_BAND), len(PB_BAND), len(PC_BAND)
UNIV_N_FEAS = {x: _PK[x].n for x in "abc"}
UNIV_BEST = {x: _PK[x].best for x in "abc"}
PA, PA_BASE = summarise(PA_W, "net_macro", UNIV), summarise(PA_W, "net_base", UNIV)
# Each on the 10-year view alone too: A's own column, and the second lens for B.
PA_10, PB_10 = (summarise(w, "net_10y", UNIV) for w in (PA_W, PB_W))
PB, PB_BASE = summarise(PB_W, "net_macro", UNIV), summarise(PB_W, "net_base", UNIV)
PC, PC_BASE, PC_10 = (summarise(PC_W, c_, UNIV) for c_ in ("net_macro", "net_base", "net_10y"))
# Whether the engine's A is the mix the 22-fund review found. Published, not asserted:
# a later roll may move one and not the other, and the page says so when it does.
PA_IS_REVIEW = (dict(MACRO["pa_review_mix"])
                == {f["short"]: round(w * 100) for f, w in zip(UNIV[1], PA_W) if round(w * 100)})
# The review's holdings in funds this page does not model, if any.
PA_REVIEW_OUTSIDE = [x for x in MACRO["pa_review_mix"] if x[0] not in [f["short"] for f in UNIV[1]]]

# The universe's macro frontier and the best pure ratio, for the Portfolios chart and
# the "why not simply maximise return" note - the same set B is chosen from. The
# frontier is every bucket's best mix (by the rule's order) that beats every shallower
# bucket on CAGR, thinned to FRONTIER_SPACING with B always kept.
_univ_par, _best_u = [], -1e9
for _dd in sorted(_FRONT_BUCKET):
    _m = _FRONT_BUCKET[_dd]
    if _m[0] > _best_u + 1e-9:
        _univ_par.append(_m); _best_u = _m[0]
UNIV_FRONTIER, _last_u = [], None
_PBU = [round(x * 20) for x in PB_W]
for _m in _univ_par:
    _w = _full_units(_m[4], _m[5])
    if _last_u is None or abs(_m[1]) >= _last_u + FRONTIER_SPACING or _w == _PBU:
        UNIV_FRONTIER.append({"maxdd": abs(_m[1]), "dd": _m[1], "cagr": _m[0],
                              "weights": [x * 5.0 for x in _w]}); _last_u = abs(_m[1])
_brw = [x / 20 for x in _full_units(_BEST_RATIO_M[1][4], _BEST_RATIO_M[1][5])]
UNIV_BEST_RATIO = (_brw, summarise(_brw, "net_macro", UNIV))

# THE UNIVERSE WHAT-IFS (2026-10-21): B RE-CHOSEN by the rule on each alternative
# column, A re-measured on it (A is chosen on the 10-year column, which reads none of the
# near-horizon inputs these change). All six come out of the one search above.
def _wi_entry(k):
    b = _PK[("b", k)].result(); c = _PK[("c", k)].result()
    a = summarise(PA_W, _WI_COL10[k], UNIV)   # A on its own (10-year) view, v80
    return {"b": {"weights": [round(x * 100) for x in b[0]], "cagr": b[2][0], "maxdd": b[2][1]},
            "c": {"weights": [round(x * 100) for x in c[0]], "cagr": c[2][0], "maxdd": c[2][1]},
            "a": {"cagr": a["cagr"], "maxdd": a["maxdd"]}}
WHAT_IF_UNIV = {k: _wi_entry(k) for k in _WI_KEYS if k != "live"}


def _alt_entry(cap):
    out = {}
    for x in "abc":
        if cap == DD_CAP:
            w_, n_, best = {"a": PA_W, "b": PB_W, "c": PC_W}[x], _PK[x].n, _PK[x].best
        else:
            w_, _band, _ = _PKX[(x, cap)].result(); n_, best = _PKX[(x, cap)].n, _PKX[(x, cap)].best
        col_ = "net_10y" if x == "a" else "net_macro"      # each on its own horizon (v80)
        m_ = summarise(w_, col_, UNIV)
        out[x] = {"weights": [round(v * 100) for v in w_], "cagr": m_["cagr"], "maxdd": m_["maxdd"],
                  "vol": m_["vol"], "ret_per_dd": m_["ret_per_dd"], "n_feasible": n_, "best": best,
                  "hormuz_dd": next(r for r in run_scenarios(w_, col_, UNIV)
                                    if r["name"].startswith("Hormuz"))["maxdd"]}
    return out
def ddg_alt():
    """A, B and C at each step, measured when the payload is built (the stress grid comes later)."""
    return {c: _alt_entry(c) for c in sorted(set(DDG_STEPS) | {DD_CAP})}
# The stress size the page quotes. Until v62 only the four-fund what-ifs carried it,
# so the page's sentence fell back to a typed "0.25pp" that nothing tied to this input.
WHAT_IF_UNIV["asia_fee_hi"]["stress_pp"] = ASIA_FEE_STRESS

# ----------------------------------------------------------------------------
# 7. SCENARIO / STRESS GRID
# ----------------------------------------------------------------------------
# Each scenario is an additive shock (pp, annualised over 5y) per fund and a
# vol multiplier, keyed to a live, named risk in the current macro picture.
# Global Dividend carries shocks too (ESTIMATES, 2026-10-21): about half the
# Nasdaq sleeve's hit in each equity row.
SCENARIOS = [
    ("Hormuz escalation", "Already partly running since the late-August tanker strikes. "
     f"This row models the tail: full Strait closure and Brent to ${MACRO['brent_closure']:.0f}+ from "
     f"${MACRO['brent']:.0f}. Global CPI re-accelerates, the Fed is forced to hike, and "
     "multiples compress hardest at the long end.",
     {"ATRPHMM": +0.5, "ATRQIAP": -4.5, "ATRASEQ": -6.5, "ATRGTEC": -7.5, "ATRGLDV": -3.0,
     "ATRGHCP": -2.0, "M_GINF": -2.0, "M_GEO": -5.0, "M_GCT": -6.5, "ATRAMIP": -3.0, "M_GALL": -2.5}, 1.60),
    ("Hawkish repricing", "A second hike on top of the one the dot plot already has "
     f"(median {MACRO['fed_dot_2026']}% for end-2026) - {MACRO['fed_dots_two_more']} of "
     # Bound to the input 2026-10-03: "a 4.1% unemployment rate" was typed, and
     # went stale the day September's report moved it to 4.2%.
     f"{MACRO['fed_dots_participants']} participants see it. The Fed hikes into a "
     f"{MACRO['us_unemployment']}% unemployment rate; duration-heavy growth de-rates.",
     {"ATRPHMM": +0.8, "ATRQIAP": -2.5, "ATRASEQ": -2.0, "ATRGTEC": -5.0, "ATRGLDV": -1.5,
     "ATRGHCP": -1.0, "M_GINF": -2.5, "M_GEO": -3.5, "M_GCT": -4.5, "ATRAMIP": -1.5, "M_GALL": -2.0}, 1.30),
    ("AI capex digestion", "Semis order book rolls over; the 52% Asia EPS "
     "estimate is cut. Hits the AI supply chain and mega-cap tech together.",
     {"ATRPHMM": 0.0, "ATRQIAP": -3.5, "ATRASEQ": -5.5, "ATRGTEC": -8.0, "ATRGLDV": -1.0,
     "ATRGHCP": 0.0, "M_GINF": -0.5, "M_GEO": -3.5, "M_GCT": -3.0, "ATRAMIP": -2.5, "M_GALL": -1.5}, 1.45),
    ("Disinflation restart", f"Oil mean-reverts to ${MACRO['brent_disinflation']:.0f}, headline CPI falls to 2%, "
     "Fed cuts. The bull case: multiples expand, vol collapses.",
     {"ATRPHMM": -0.9, "ATRQIAP": +2.5, "ATRASEQ": +3.5, "ATRGTEC": +4.5, "ATRGLDV": +1.5,
     "ATRGHCP": +1.0, "M_GINF": +2.0, "M_GEO": +3.5, "M_GCT": +4.5, "ATRAMIP": +2.0, "M_GALL": +2.0}, 0.80),
    ("Grind-on base case", "Vol drifts up to the 19-20 the futures curve already "
     "prices, earnings hold, no policy accident. The modelled path.",
     {"ATRPHMM": 0.0, "ATRQIAP": 0.0, "ATRASEQ": 0.0, "ATRGTEC": 0.0, "ATRGLDV": 0.0,
     "ATRGHCP": 0.0, "M_GINF": 0.0, "M_GEO": 0.0, "M_GCT": 0.0, "ATRAMIP": 0.0, "M_GALL": 0.0}, 1.00),
]

def run_scenarios(w, key, u=None):
    Fs, _, C = _univ(u)
    n = len(w)
    rows = []
    for name, desc, shock, volmul in SCENARIOS:
        r = sum(w[i] * (Fs[i][key] + shock[Fs[i]["id"]]) for i in range(n))
        s = [w[i] * Fs[i]["vol"] * volmul for i in range(n)]
        v = math.sqrt(sum(s[i] * s[j] * C[i][j] for i in range(n) for j in range(n)))
        # The horizon scalar belongs here exactly as it does in port_dd(). It was
        # MISSING from 2026-09-07, when the mandate moved to 10 years, until the
        # 2026-09-09 audit: every other drawdown on the page was scaled and these
        # were not, so the stress table understated the tail by a factor of 1.414
        # while sitting next to headline figures that did not. The "Grind-on base
        # case" row - zero shock, 1.0 vol multiplier - is the tell: it must
        # reproduce the headline portfolio exactly, and it did not.
        # Built from the ROUNDED cagr and vol, for the same reason summarise() is:
        # a reader dividing out the printed row must land on the printed drawdown.
        # Computed from raw r and v, two of the ten rows were 0.1 out from their own
        # printed inputs. This is the THIRD place this defect has appeared - the
        # peso figures on 2026-09-03, ret_per_dd on 2026-09-11, and here - each time
        # because the fix was applied where it was found rather than everywhere the
        # pattern occurs. (Audit 2026-09-14.)
        r_d, v_d = round(r, 2), round(v, 2)
        d = -max((port_k(w, u) * v_d - DD_MU * r_d) * DD_HORIZON_SCALAR, 0.0)
        rows.append({"name": name, "desc": desc, "cagr": r_d,
                     "vol": v_d, "maxdd": round(d, 1)})
    return rows

# ----------------------------------------------------------------------------
# 8. SOURCES
# ----------------------------------------------------------------------------
SOURCES = [
    ("Rigzone", "Oil rises with Iran attack report - Brent +1.3% to $115.32, WTI +2.9% to $102.78, 28 Oct 2026",
     "https://www.rigzone.com/news/oil_rises_with_iran_attack_report_israeli_election_in_focus-28-oct-2026-184958-article"),
    ("CNBC", "Oil prices rise as U.S. reportedly tells Gulf countries to prepare for Iran strikes after midterm elections (citing the Wall Street Journal), 28 Oct 2026",
     "https://www.cnbc.com/2026/10/28/oil-price-today-wti-brent-hormuz.html"),
    ("The Hill", "Oil prices climb as Trump, Pentagon mull fresh strikes on Iran, 28 Oct 2026",
     "https://thehill.com/policy/energy-environment/6136014-oil-gas-prices-surge-reports-fresh-iran-strikes-white-house/"),
    ("The National", "Oil prices up due to Houthi strikes and US threat to renew Iran war, 28 Oct 2026",
     "https://thenationalnews.com/business/energy/2026/10/28/oil-prices-up-due-to-houthi-strikes-and-us-threat-to-renew-iran-war"),
    ("Federal Reserve", "Federal Reserve issues FOMC statement - target range held at 3.75-4.00%, Cook and Hammack for a hike, 28 Oct 2026",
     "https://www.federalreserve.gov/newsevents/pressreleases/monetary20261028a.htm"),
    ("CNBC", "Fed holds rates steady, 10-2, two officials for a hike, 28 Oct 2026",
     "https://www.cnbc.com/2026/10/28/fed-interest-rate-decision-october-2026.html"),
    ("CNBC", "Stock market news for 28 Oct 2026 - S&P +0.28% to 7,743.98, Nasdaq +0.27% to 26,549.85, Dow +0.19% to 52,475.10",
     "https://www.cnbc.com/2026/10/27/stock-market-today-live-updates.html"),
    ("Associated Press via KRMG", "How major US stock indexes fared Wednesday 10/28/2026 - S&P +21.38, Nasdaq +72.04, Dow +97.53",
     "https://krmg.com/2026/10/28/how-major-us-stock-indexes-fared-wednesday-10-28-2026/"),
    ("ABC News", "Federal Reserve holds interest rates steady as midterm elections loom - FedWatch 85% for a December hike, 28 Oct 2026",
     "https://abcnews.com/Business/federal-reserve-set-issue-interest-rate-decision-midterm/story?id=137599228"),
    ("Kiplinger", "October Fed meeting live - 85% priced for a December hike, 28 Oct 2026",
     "https://www.kiplinger.com/investing/live/fed-meeting-updates-and-commentary-october-2026"),
    ("DTN", "WTI near $100 ahead of Hormuz diplomacy and the Fed - December WTI -$1.86 (-1.83%) to settle at $99.90, 27 Oct 2026",
     "https://www.dtnpf.com/agriculture/web/ag/news/world-policy/article/2026/10/27/wti-100-ahead-hormuz-diplomacy-fed"),
    ("AD HOC News", "Nikkei 225 closes 686 points higher as Kioxia leads chips - 63,954.19, 28 Oct 2026",
     "https://www.ad-hoc-news.de/boerse/news/marktberichte/nikkei-225-closes-686-points-higher-as-kioxia-leads-chips/70425452"),
    ("Il Sole 24 Ore", "Tokyo: the Nikkei closes up 1.08%, the Wall Street effect boosts tech, 28 Oct 2026",
     "https://en.ilsole24ore.com/art/tokyo-stock-exchange-nikkei-closes-up-108-per-cent-wall-street-effect-boosts-tech-sector-AJ5waXwB"),
    ("AD HOC News", "Nikkei 225 gains 1.7 percent as the AI rally extends - 63,268.37 (+1,078.72), 27 Oct 2026",
     "https://www.ad-hoc-news.de/boerse/news/marktberichte/nikkei-225-gains-1-7-percent-as-ai-rally-extends-after-close/70422671"),
    ("CNBC", "Oil today, 27 Oct 2026 - Brent -1.7% to settle at $113.88, WTI $99.90, on Iran diplomacy",
     "https://www.cnbc.com/2026/10/27/oil-today-iran-us-crude-wti-brent-trump.html"),
    ("The Nation (Thailand)", "Brent drops US$1.93 a barrel on October 27 amid Iran talks",
     "https://www.nationthailand.com/news/world/40072812"),
    ("Sprague Energy", "27 Oct 2025 - December Brent settled down 32 cents at $65.62, WTI $61.31 (the year-ago base)",
     "https://www.spragueenergy.com/framework-agreed-to-avoid-100-u-s-tariffs-on-chinese-goods/"),
    ("Oil and Gas 360 / Investing.com (Reuters)", "Oil settles lower as OPEC plans to increase oil output - Brent $65.62, 27 Oct 2025",
     "https://www.oilandgas360.com/oil-settles-lower-as-opec-plans-to-increase-oil-output/"),
    ("The Philippine Star", "Peso rebounds 14.5 cents to P64.025 vs dollar, 28 Oct 2026",
     "https://www.philstar.com/business/2026/10/28/2566343/peso-rebounds-145-cents-p64025-vs-dollar"),
    ("Daily Tribune", "Peso rebounds, but stays above P64; PSEi slumps - 64.025 and 5,653.55, 28 Oct 2026",
     "https://tribune.net.ph/2026/10/28/peso-rebounds-but-stays-above-p64-psei-slumps"),
    ("Philippine Daily Inquirer", "Inflation fears drag PSEi down 1.87% - 5,653.55, 28 Oct 2026",
     "https://business.inquirer.net/618558/inflation-fears-drag-psei-down-1-87"),
    ("Newsis", "KOSPI closes 6.63% higher - 6,012.44 (+374.10), 28 Oct 2026",
     "https://www.newsis.com/view/NISI20261028_0021508701"),
    ("SBS Biz", "KOSPI back above 6,000 after ten sessions, +6.63% to 6,012.44, 28 Oct 2026",
     "https://biz.sbs.co.kr/article/20000342741"),
    ("SK hynix", "SK hynix announces 3Q26 financial results - operating profit KRW 83.3tn, ~KRW 100tn of 2026 shareholder returns",
     "https://news.skhynix.com/en/q3-2026-business-results/"),
    ("investingLive", "SK Hynix Q3 operating profit beats at 83tn won, unveils 100tn won shareholder payout plan",
     "https://investinglive.com/stocks/sk-hynix-q3-operating-profit-beats-at-83tn-won-unveils-100tn-won-shareholder-payout-plan/"),
    # ---- added 2026-10-10, the 7-9 Oct roll ----
    ("KTVB / Associated Press", "How major US stock indexes fared Wednesday 10/7/2026 - S&P -0.2%, Dow -0.7%, Nasdaq -0.2%",
     "https://www.ktvb.com/article/syndication/associatedpress/how-major-us-stock-indexes-fared-wednesday-1072026/616-452f0082-36eb-4068-ac36-10d6db740e41"),
    ("La Nacion / Associated Press", "How major US stock indexes fared Thursday 10/8/2026 - S&P 7765.36 (-36.41), Nasdaq 27193.34 (-345.35), Dow 51231.64 (+51.77)",
     "https://www.lanacion.com.ar/usa/how-major-us-stock-indexes-fared-thursday-1082026-nid08102026/"),
    ("TheStreet", "Stock market today, 9 Oct 2026 - S&P 7811.54 (+46.18), Nasdaq 27366.17 (+172.83), Dow 51655.01 (+423.37)",
     "https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-oct-09-2026"),
    ("CNBC", "10-year Treasury yield backs off from 24-year high after solid bond auction - 5.3% auction, 80.3% indirect, 7 Oct 2026",
     "https://www.cnbc.com/2026/10/07/treasury-yields-auction-fomc-minutes.html"),
    ("MarketScreener", "US 10-year yield backs away from 24-year high after note sale - intraday 5.365%, 30-year 5.733%, 7 Oct 2026",
     "https://www.marketscreener.com/news/us-10-year-yield-back-away-from-24-year-high-after-treasury-note-sale-ce785ddedd8ef224"),
    ("CNBC", "Treasury yields steady as traders wrap up volatile week - 2-year 4.789%, 30-year 5.60%, 9 Oct 2026",
     "https://www.cnbc.com/2026/10/09/us-treasurys-bond-yields-midterms.html"),
    ("ETF Trends / Advisor Perspectives", "Treasury yields snapshot, 9 Oct 2026 - 10-year 5.24% on the Treasury par curve (provisional here until FRED)",
     "https://www.etftrends.com/fixed-income-content-hub/treasury-yields-snapshot-october-9-2026/"),
    ("Federal Reserve", "Minutes of the FOMC, 15-16 September 2026, released 7 Oct 2026",
     "https://www.federalreserve.gov/newsevents/pressreleases/monetary20261007a.htm"),
    ("Bloomberg", "Fed minutes show officials all backed September hike; most see another by year-end, 7 Oct 2026",
     "https://www.bloomberg.com/news/articles/2026-10-07/fed-minutes-show-hawkish-unity-behind-september-rate-hike"),
    ("CNBC", "Oil prices jump as Iran steps up tanker attacks, hurricane threatens US Gulf production - Brent $104.28 (+4%), WTI $91.49 (+3.6%), 8 Oct 2026",
     "https://www.cnbc.com/2026/10/08/oil-prices-today-brent-wti-hormuz.html"),
    ("Business Recorder / Reuters", "Oil prices settle higher - Brent $104.72 (+0.44), WTI $91.85 (+0.36), Isaias shuts over 70% of US Gulf output, 9 Oct 2026",
     "https://brecorder.com/news/40443543/oil-prices-settle-higher"),
    ("Yahoo Finance / Bloomberg", "Oil edges higher on Iran strike options report and storm impact - Brent closed near $100, 7 Oct 2026 (the withheld session)",
     "https://finance.yahoo.com/energy/articles/oil-edges-higher-iran-strike-220255409.html"),
    ("Sprague Energy", "The crude market reacts to the Israel-Hamas ceasefire - December Brent $65.22 on 9 Oct 2025, the year-ago base",
     "https://www.spragueenergy.com/the-crude-market-reacts-to-the-israel-and-hamas-ceasefire-agreement/"),
    ("BusinessWorld", "Peso plunges to new all-time-low close - P62.90 from P62.75, past P62.86 of 14 Sep; 62.925 intraday still the trough, 8 Oct 2026",
     "https://bworldonline.com/banking-finance/2026/10/08/785623/peso-plunges-to-new-all-time-low-close-on-contagion-oil-supply-fears/"),
    ("radar.ph", "Peso rebounds from new low as PSEi gains 90 points - P62.801, PSEi 5700.99, 9 Oct 2026",
     "https://radar.ph/peso-rebounds-from-new-low-as-psei-gains-90-points-october-9-2026/"),
    ("radar.ph", "Peso plummets to new historic low - P62.90; PSEi -126.30 to 5610.39, 8 Oct 2026",
     "https://radar.ph/breaking-peso-plummets-to-new-historic-low-october-8-2026/"),
    ("Tribune", "PSEi rebounds 1.05% after inflation-driven selloff - 5736.69, peso P62.750, 7 Oct 2026",
     "https://tribune.net.ph/2026/10/07/psei-rebounds-105-after-inflation-driven-selloff"),
    ("Il Sole 24 Ore", "Tokyo: the Nikkei closes down 0.02% at 69,030.92, 9 Oct 2026",
     "https://en.ilsole24ore.com/art/tokyo-stock-exchange-nikkei-index-closes-up-002-per-cent-AJg9qMeB"),
    ("Korea JoongAng Daily", "Kospi closes down 2.62% to 6,625.93, a third day of losses on inflation worries, 8 Oct 2026",
     "https://www.koreajoongangdaily.com/business/kospi-closes-down-262-to-continue-slide-to-third-day-on-inflation-worries/12911756"),
    ("Seoul Economic Daily", "Samsung Electronics Q3 operating profit tops 100 trillion won for the first time - 107.4tn, 8 Oct 2026",
     "https://en.sedaily.com/finance/2026/10/08/samsung-electronics-posts-record-107-trillion-won-quarterly"),
    ("TSMC", "September 2026 revenue report - NT$511.86bn, +54.6% y/y",
     "https://pr.tsmc.com/english/news/3343"),
    ("FXStreet / University of Michigan", "Consumer sentiment 46.3 in October (preliminary); 1-year inflation expectations 4.7%, 5-year 3.5%, 9 Oct 2026",
     "https://www.fxstreet.com/news/uom-consumer-sentiment-index-expected-to-decline-in-october-amid-high-oil-prices-202610091000"),
    ("Admiral Markets", "US CPI September 2026 preview - release 14 Oct, 3.7% headline consensus",
     "https://admiralmarkets.com/analytics/traders-blog/us-cpi-preview-september-2026-forecasts-and-the-core-cpi-outlook"),
    ("Rothschild & Co", "France: fiscal pressure - OAT-Bund spread near 140bp, 2026 deficit 5.4%, October 2026",
     "https://www.rothschildandco.com/en-us/newsroom/insights/2026/10/wm-strategy-blog-france-fiscal-pressure/"),
    ("Al Hurra / Reuters", "Tanker attacks spread inside the Gulf as Hormuz traffic hits a two-month low - at least 12 tankers attacked 28 Sep-5 Oct",
     "https://alhurra.com/en/45443"),
    ("Al Jazeera / UKMTO", "Tanker hit by multiple projectiles off the north coast of Qatar, casualties reported, 7 Oct 2026",
     "https://www.aljazeera.com/news/2026/10/8/tanker-hit-by-multiple-projectiles-off-north-coast-of-qatar-ukmto-says"),
    ("NBC News", "Trump's pledge not to strike Iran before the midterms fails to soothe oil markets, 8 Oct 2026",
     "https://www.nbcnews.com/business/energy/oil-prices-stocks-trump-iran-rcna602248"),
    ("Straits Daily Brief", "Strait of Hormuz status, 7 Oct 2026 - 206 vessels holding position; PortWatch 4 transits on 4 Oct",
     "https://straits.live/briefs/2026-10-07"),
    ("FRED (St. Louis Fed)", "VXVCLS - Cboe 3-month volatility index: 17.72 on 7 Oct 2026, the VIX3M test of the re-quoted curve; 19.60 on 19 Oct",
     "https://fred.stlouisfed.org/series/VXVCLS"),
    ("Investing.com", "CBOE Volatility Index historical data - 15.08 (7 Oct), 15.41 (8 Oct), 14.84 (9 Oct), 15.21 (12 Oct, +2.49%), 16.87 (14 Oct, +10.48%), 19.99 (16 Oct), 18.44 (19 Oct, -7.75%)",
     "https://www.investing.com/indices/volatility-s-p-500-historical-data"),
    # ---- added 2026-10-07, the 5-6 Oct roll ----
    ("Philippine Statistics Authority", "Summary Inflation Report, September 2026 - headline 7.2%, core 4.7%, food 6.7%, transport 14.6%, bottom 30% of households 9.0%",
     "https://psa.gov.ph/content/summary-inflation-report-consumer-price-index-2018100-september-2026"),
    ("BusinessWorld", "Philippine inflation heats up to 3-year high - 7.2% in September against a 6.7% poll median, 6 Oct 2026",
     "https://bworldonline.com/top-stories/2026/10/06/784925/philippine-inflation-heats-up-to-3-year-high/"),
    ("BusinessWorld", "Peso sinks as euro zone woes, inflation fears dent sentiment - P62.771 from P62.621, 6 Oct 2026",
     "https://bworldonline.com/banking-finance/2026/10/06/785004/peso-sinks-as-euro-zone-woes-inflation-fears-dent-sentiment/"),
    ("radar.ph", "Peso resets gains as PSEi gains 114 points - PSEi 5,743.21, peso P62.621, 5 Oct 2026",
     "https://radar.ph/peso-resets-gains-as-psei-gains-114-points-october-5-2026/"),
    ("Philippine Daily Inquirer", "Inflation jump drags PSEi down to 5,677 - 5,677.12, -66.09 (-1.15%), 6 Oct 2026",
     "https://business.inquirer.net/614535/inflation-jump-drags-psei-down-to-5677"),
    ("BusinessMirror", "Investors sought higher returns on inflation bet - T-bills 5.667% / 5.971% / 6.214%, 5 Oct 2026 auction",
     "https://businessmirror.com.ph/2026/10/05/investors-sought-higher-returns-on-inflation-bet/"),
    ("CNBC", "10-year Treasury yield rises to fresh 2002 high to start the week - 5.349%, 5 Oct 2026",
     "https://www.cnbc.com/2026/10/05/treasury-yields-bonds-fed-rates.html"),
    ("CNBC", "Treasury yields slide as surge to multiyear highs cools - 2-year 4.80%, 30-year 5.659%, 6 Oct 2026",
     "https://www.cnbc.com/2026/10/06/treasury-yields-fed-fomc-minutes.html"),
    ("Bloomberg", "Treasury yields hit 24-year highs as long bonds extend selloff - 30-year near 5.7%, 5 Oct 2026",
     "https://www.bloomberg.com/news/articles/2026-10-05/treasuries-slump-pushes-long-end-yields-to-fresh-24-year-highs"),
    ("Benzinga / CME FedWatch", "October Fed hike odds fall to 21.6%; December 86.2%, 6 Oct 2026",
     "https://www.benzinga.com/markets/economic-data/26/10/62185721/jim-cramer-says-interest-rates-can-fall-too-as-october-fed-hike-odds-fall-to-21-6-heres-what-traders-are-betting-on"),
    ("ISM via PR Newswire", "Services PMI at 54.9%, September 2026 - prices 74.0%, from 55.4% and 72.6% in August",
     "https://www.morningstar.com/news/pr-newswire/20261005la62389/services-pmi-at-549-september-2026-ism-services-pmi-report"),
    ("Mankato Free Press / AP", "How major US stock indexes fared Tuesday 10/6/2026 - S&P 7818.93 (record), Nasdaq 27599.79 (record), Dow 51521.28",
     "https://www.mankatofreepress.com/news/business/how-major-us-stock-indexes-fared-tuesday-10-6-2026/article_f884ef77-b48c-5fa7-9f66-ff8a954a52cb.html"),
    ("Yahoo Finance / Zacks", "Stock Market News for Oct 6, 2026 - VIX up 1.4% to 15.52 (5 Oct session)",
     "https://finance.yahoo.com/markets/stocks/articles/stock-market-news-oct-6-054400913.html"),
    ("Yahoo Finance / Zacks", "Stock Market News for Oct 7, 2026 - VIX down 3.29% to 15.01 (6 Oct session)",
     "https://finance.yahoo.com/markets/stocks/articles/stock-market-news-oct-7-074400333.html"),
    ("Rigzone / Bloomberg", "Oil slides on Saudi price cut - Brent December settled $100.32, -1.9%, 5 Oct 2026",
     "https://www.rigzone.com/news/oil_slides_on_saudi_price_cut-05-oct-2026-184777-article"),
    ("Bloomberg", "Saudis cut flagship oil price to Asia to lowest in six years - November Arab Light $5 below, from $2 below",
     "https://www.bloomberg.com/news/articles/2026-10-05/saudis-cut-flagship-oil-price-to-asia-to-lowest-in-six-years"),
    ("Fortune", "Current price of oil as of 7 Oct 2026 - Brent $101.51, +93 cents (recovers the 6 Oct settle of $100.58)",
     "https://fortune.com/article/price-of-oil-10-07-2026/"),
    ("EnergyNow", "Oil slides more than 2% as recovering Gulf exports and emergency stock release ease supply fears - WTI settled $89.43 on 5 Oct; G7 100m-barrel release",
     "https://energynow.com/2026/10/oil-slides-more-than-2-as-recovering-gulf-exports-and-emergency-stock-release-ease-supply-fears/"),
    ("Bloomberg", "Key Saudi pipeline flows at 5.8 million barrels, minister says, 6 Oct 2026",
     "https://www.bloomberg.com/news/articles/2026-10-06/key-saudi-pipeline-flows-at-5-8-million-barrels-minister-says"),
    ("Bloomberg", "Iran increases tanker attacks in Hormuz as oil shipments near pre-war levels - UKMTO: nine attacks in October by the 6th, 18 in September",
     "https://www.bloomberg.com/news/articles/2026-10-06/iran-ramps-up-ship-attacks-in-hormuz-as-oil-and-gas-flows-climb"),
    ("Gulf News", "Iran's president says talks with the US 'meaningless', 6 Oct 2026",
     "https://gulfnews.com/world/mena/us-iran-war-tehran-rejects-military-solution-saudi-led-coalition-backs-yemen-offensive-against-houthis-1.500698388"),
    ("Straits Daily Brief", "Strait of Hormuz status, 6 Oct 2026 - 242 vessels holding position; IRGC turned a tanker back off Khasab on 5 Oct",
     "https://straits.live/briefs/2026-10-06"),
    ("Edge Consultancy", "Asia market wrap 6 October 2026 - Nikkei 70,683.98, its first close above 70,000 since 1 July",
     "https://edgeconsultancykw.com/asia-market-wrap-6-october-2026/"),
    ("Seoul Economic Daily", "KOSPI closes down 0.89% at 6,941.39 - Samsung -1.45%, SK Hynix -3.69%, 6 Oct 2026",
     "https://en.sedaily.com/finance/2026/10/06/kospi-closes-down-089-percent-at-694139"),
    # ---- added 2026-10-07, the market-trend channel ----
    ("PortfoliosLab", "Invesco QQQ monthly total returns, 2025-2026 (Nasdaq-100 trend; 2025 compounds to 20.77%)",
     "https://portfolioslab.com/symbol/QQQ"),
    ("PortfoliosLab", "iShares Global Tech ETF (IXN) monthly total returns, 2025-2026 (global technology trend)",
     "https://portfolioslab.com/symbol/IXN"),
    ("Nasdaq", "Nasdaq-100 index factsheet, 30 Sep 2026 - Q2 +27.74%, Q3 +0.58% (trend cross-check)",
     "https://indexes.nasdaqomx.com/docs/FS_XNDX.pdf"),
    ("Schroders", "Quarterly markets review Q4 2025 - MSCI AC Asia ex Japan +4.3% in US dollars",
     "https://www.schroders.com/en/global/individual/insights/quarterly-markets-review---q4-2025/"),
    ("Schroders", "Quarterly markets review Q2 2026 - MSCI Asia ex Japan +27.7% in US dollars",
     "https://www.schroders.com/en/global/individual/insights/quarterly-markets-review---q2-2026/"),
    ("Schroders", "Monthly markets review August 2026 - MSCI AC Asia ex Japan +3.3%",
     "https://www.schroders.com/en-us/us/institutional/insights/monthly-markets-review---august-2026/"),
    ("Schroders", "Monthly markets review July 2026 - MSCI AC Asia ex Japan -3.2% in US dollars",
     "https://www.schroders.com/en/global/individual/insights/monthly-markets-review---july-2026/"),
    ("Schroders", "Quarterly markets review Q3 2026 - MSCI AC Asia ex Japan 'a slight decline' in the quarter",
     "https://www.schroders.com/en-gb/uk/intermediary/insights/quarterly-markets-review---q3-2026/"),
    ("Shikhara", "From the CIO's Desk, Asia Quarterly Q1 2026 - MSCI AC Asia ex Japan -1.13% in USD",
     "https://shikhara.com/from-the-cios-desk-asia-quarterly-q1-2026/"),
    ("Shikhara", "From the CIO's Desk, Asia Insights July 2026 - MSCI AC Asia ex Japan -3.18% in USD",
     "https://shikhara.com/from-the-cios-desk-asia-insights-july-2026/"),
    ("MSCI", "MSCI AC Asia ex Japan Index factsheet (USD), 30 Sep 2026 - one month -0.25%",
     "https://www.msci.com/documents/10199/255599/msci-ac-asia-ex-japan-index-usd-net.pdf"),
    ("BlackRock iShares", "iShares MSCI All Country Asia ex Japan ETF (AAXJ) - 3-month 25.73%, the trend's alternative Asia figure",
     "https://www.ishares.com/us/products/239601/ishares-msci-all-country-asia-ex-japan-etf"),
    ("Moskowitz, Ooi and Pedersen", "Time series momentum, Journal of Financial Economics 104(2), 2012 - trends persist about a year, then partly reverse",
     "https://doi.org/10.1016/j.jfineco.2011.11.003"),
    # ---- added 2026-10-03, the 2 Oct roll ----
    ("CNBC", "September 2026 jobs report - payrolls +29k vs 84k consensus, unemployment 4.2%, August revised to +133k, July to -10k",
     "https://www.cnbc.com/2026/10/02/jobs-report-september-2026.html"),
    ("CNBC", "Traders see little chance of an October hike - CME FedWatch 17% after the payrolls, 2 Oct 2026",
     "https://www.cnbc.com/2026/10/02/fed-rate-hike-odds-decline-after-september-jobs-report.html"),
    ("CNBC", "Treasury yields fall from multiyear highs - 10-year intraday 5.342%, highest since 3 April 2002, 1 Oct 2026",
     "https://www.cnbc.com/2026/10/01/us-treasury-bond-yield.html"),
    ("CNBC", "10-year Treasury yield ticks higher despite weak jobs report - 10-year 5.281%, 2-year 4.839%, 30-year 5.629%, 2 Oct 2026",
     "https://www.cnbc.com/2026/10/02/treasury-yields-bonds-nonfarm-payrolls.html"),
    ("CNBC", "10-year yield higher as traders look past inflation data - 30-year 5.632%, 30 Sep 2026",
     "https://www.cnbc.com/2026/09/30/treasury-yields-bonds-selloff.html"),
    ("FRED (St. Louis Fed)", "DGS10 - 10-year constant maturity: 5.24 (28 Sep), 5.26 (29 Sep), 5.29 (30 Sep), 5.28 (2 Oct), 5.31 (5 Oct), 5.27 (6 Oct), 5.28 (7 Oct), 5.22 (8 Oct) 2026",
     "https://fred.stlouisfed.org/series/DGS10"),
    ("FRED (St. Louis Fed)", "FEDTARMD - FOMC projections, median federal funds rate: 4.1 for 2026 and 2027, 3.9 for 2028, 3.6 for 2029 (September 2026 SEP)",
     "https://fred.stlouisfed.org/series/FEDTARMD"),
    ("FRED Blog", "FOMC Summary of Economic Projections, September 2026 - the median at 4.1% through 2027, 3.9% by end-2028",
     "https://fredblog.stlouisfed.org/2026/09/fomc-summary-of-economic-projections-september-2026/"),
    ("Yahoo Finance / BEA", "August 2026 PCE - headline 3.4% y/y vs 3.7% expected, core 3.0% vs 3.3%",
     "https://finance.yahoo.com/economy/policy/articles/u-core-pce-inflation-rises-132052964.html"),
    ("Eurostat", "Euro area annual inflation up to 3.8% - September 2026 flash, energy 18.8%",
     "https://ec.europa.eu/eurostat/web/products-euro-indicators/w/2-02102026-ap"),
    ("The Japan Times", "Tankan Q3 2026 - large manufacturers +24 from +22, sixth straight rise",
     "https://www.japantimes.co.jp/business/2026/10/01/companies/tankan-better-sentiment/"),
    ("WTOP / Associated Press", "How major US stock indexes fared Friday 10/2/2026 - S&P 7722.72, Nasdaq 27190.86 (record), Dow 51176.96",
     "https://wtop.com/news/2026/10/how-major-us-stock-indexes-fared-friday-10-2-2026"),
    ("Yahoo Finance / Zacks", "Stock Market News for Sep 30, 2026 - VIX down 0.2% to 16.04 (29 Sep session)",
     "https://sg.finance.yahoo.com/news/stock-market-news-sep-30-071000168.html"),
    ("Investing.com", "S&P 500 VIX futures contracts board - Oct 18.65, Nov 19.21, Dec 19.35, Jan 20.38, 2 Oct 2026",
     "https://www.investing.com/indices/us-spx-vix-futures-contracts"),
    ("Yahoo Finance / Reuters", "Oil prices settle down on signs Middle East exports recovering - Brent $102.59, WTI $89.38, 29 Sep 2026",
     "https://finance.yahoo.com/energy/articles/oil-prices-rise-second-session-003313319.html"),
    ("Tokenpost / Reuters", "Brent crude settles at $102.31 after 4.4% gain - December contract, 1 Oct 2026",
     "https://www.tokenpost.com/news/investing/26265"),
    ("EnergyNow", "Oil ends volatile week mixed - Brent $102.25, WTI $91.11, SPR's final 40m barrels, 2 Oct 2026",
     "https://energynow.com/2026/10/oil-ends-volatile-week-mixed-as-emergency-reserve-release-knocks-wti-lower-but-brent-holds-above-102/"),
    ("CNBC", "OPEC+ opts for modest hike - Brent closed $64.53 on 3 Oct 2025, the year-ago base",
     "https://www.cnbc.com/2025/10/05/opec-raises-oil-production-again-with-modest-a-hike-from-november.html"),
    ("gCaptain / Bloomberg", "JPMorgan and Goldman see Mideast oil flows near pre-war levels - Goldman 23.3 mb/d, JPM crude 17.5 mb/d (98%), products 58%",
     "https://gcaptain.com/jpmorgan-and-goldman-see-mideast-oil-flows-near-pre-war-levels/"),
    ("ABC News / AP", "Rubio orders visiting Iranian UN delegation to leave NYC ahead of schedule, 30 Sep 2026",
     "https://abcnews.com/US/wireStory/rubio-orders-visiting-iranian-delegation-leave-nyc-ahead-136908428"),
    ("Straits Daily Brief", "Strait of Hormuz status, 2 Oct 2026 - 147 vessels holding position; PortWatch 1 transit on 27 Sep",
     "https://straits.live/briefs/2026-10-02"),
    ("radar.ph", "Peso rebounds sharply as PSEi holds near 5,600 - P62.535, PSEi 5,629.03, 2 Oct 2026",
     "https://radar.ph/peso-rebounds-sharply-as-psei-holds-near-5600-october-2-2026/"),
    ("Tribune", "BSP sees September inflation rising to within 6.4 to 7.4%, 30 Sep 2026",
     "https://tribune.net.ph/2026/09/30/bsp-sees-september-inflation-rising-to-within-64-to-74-2"),
    ("Seoul Economic Daily", "KOSPI reclaims 7,000 as Samsung Electronics rebounds late - 7,003.74, 2 Oct 2026",
     "https://en.sedaily.com/finance/2026/10/02/kospi-reclaims-7000-as-samsung-electronics-rebounds-late"),
    ("Xinhua", "Tokyo stocks end lower on profit-taking - Nikkei 68,309.46, 2 Oct 2026",
     "https://english.news.cn/asiapacific/20261002/15332f987dcb40cba0dc62de276864ef/c.html"),
    ("Federal Reserve", "FOMC statement, 29 July 2026 - target range 3.50-3.75%",
     "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm"),
    ("US BLS", "Consumer Price Index, July 2026 - headline +3.4% y/y, core +2.5% y/y",
     "https://www.bls.gov/news.release/cpi.nr0.htm"),
    ("European Central Bank", "Monetary policy decision, 11 June 2026 - deposit rate 2.25%",
     "https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260611~4d41bd5e83.en.html"),
    ("Bangko Sentral ng Pilipinas", "Key rates - RRP 5.00% after the 27 August 2026 hike, a third consecutive move and +75bp cumulative since April",
     "https://www.bsp.gov.ph/SitePages/Statistics/KeyRates.aspx"),
    ("US BLS", "Employment Situation, August 2026 - nonfarm payrolls +162,000 against a "
     "53,000 consensus; unemployment rate steady at 4.1%",
     "https://www.bls.gov/news.release/empsit.nr0.htm"),
    ("CNBC", "US payrolls rose 162,000 in August, much more than expected; unemployment "
     "at 4.1%; Fed hike odds for September rose to ~58% from 49.4%",
     "https://www.cnbc.com/2026/09/04/jobs-report-august-2026.html"),
    ("Eurostat", "Flash estimate, 1 September 2026 - euro area annual inflation 3.3% in "
     "August, up from 2.9% in July, energy +14.3% y/y",
     "https://ec.europa.eu/eurostat/web/products-euro-indicators/w/2-01092026-ap"),
    ("CME Group / FedWatch", "Fed funds futures - 58% implied probability of a 25bp hike "
     "at the 15-16 September 2026 FOMC, up from 49.4% before the August payrolls beat; "
     "the second hike has slipped to January 2027",
     "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"),
    ("CNBC", "Jackson Hole roundup - Chair Warsh cites PCE at 3.7% over 12 months and 4.1% "
     "annualised over 6, lifting September hike odds",
     "https://www.cnbc.com/2026/08/31/jackson-hole-fed-chair-kevin-warsh-hawkish-rate-hikes-analysts.html"),
    ("Reuters (via Investing.com)", "Economist poll - ECB to raise a second time in September "
     "to 2.50%, then done; shortest hiking campaign in 15 years",
     "https://www.investing.com/news/economy-news/ecb-to-raise-rates-a-second-time-in-september-but-then-done-say-economists-reuters-poll-4887563"),
    ("Bloomberg", "Oil market news, 3 September 2026 - Hormuz commodity transits ~5 vessels "
     "against a 10-day average of 14. NOTE: that 10-day average was itself already "
     "collapsed; this model now states throughput against the ~85/day pre-crisis baseline",
     "https://www.bloomberg.com/news/articles/2026-09-02/latest-oil-market-news-and-analysis-for-sept-3"),
    ("Philippine Statistics Authority", "Consumer Price Index series - headline inflation "
     "6.1% y/y in August 2026, easing from 6.2% in July and 6.4% in June; a fourth "
     "consecutive monthly slowdown and a five-month low, year-to-date average 5.2%. "
     "The deceleration came from food, 4.6% from 5.2%, while RICE accelerated to "
     "19.4% from 17.1%",
     "https://psa.gov.ph/price-indices/cpi-ir"),
    ("European Central Bank", "Monetary policy decision, 23 July 2026 - deposit rate HELD at 2.25% after the June hike",
     "https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260723~29f24d99bc.en.html"),
    ("BSP Monetary Policy Report", "February 2026 economic outlook and inflation path",
     "https://www.bsp.gov.ph/Price%20Stability/MonetaryPolicyReport/FullReport-February2026.pdf"),
    ("CNBC", "VIX hits 14.18 on 17 August, reported at the time as the 2026 low. It was, until 4 September, when the index slid to 13.80 before the payrolls print. The volatility tilt is measured from the long-run level, not from either low",
     "https://www.cnbc.com/2026/08/17/stock-market-volatility-vix-wall-street.html"),
    ("Reuters (via KFGO)", "ECB to raise a second time on 10 Sep then stop - all 65 economists polled 31 Aug-3 Sep forecast 2.50%, 91% see it held to year end",
     "https://kfgo.com/2026/09/03/ecb-to-raise-rates-a-second-time-in-september-but-then-done-say-economists-reuters-poll/"),
    ("Bloomberg", "Economists see a final ECB hike next week, splitting with market pricing",
     "https://www.bloomberg.com/news/articles/2026-09-04/economists-see-final-ecb-hike-next-week-in-split-with-markets"),
    ("Wikipedia (chronology, secondary)", "2026-2028 world oil market chronology - Hormuz escalation timeline, cross-checked against the primary reports cited here",
     "https://en.wikipedia.org/wiki/2026%E2%80%932028_world_oil_market_chronology"),
        ("Bureau of the Treasury PH", "T-bill auction results, 21 September 2026 - 91d 5.431% (+8.3bp), 182d 5.821% (+4.0bp), 364d 6.043% (+12.1bp), as reported by BusinessWorld and BusinessMirror",
     "https://www.treasury.gov.ph/?cat=13"),
    ("IMF", "World Economic Outlook Update, July 2026 - 'Global Economy in Crosscurrents of War and "
     "Technology': global 3.0% (2026) / 3.4% (2027), US 2.3% / 2.2%, euro area 0.9% / 1.2%, "
     "advanced economies 1.7% / 1.8%, EMDEs 3.8% / 4.5%",
     "https://www.imf.org/en/publications/weo/issues/2026/07/08/world-economic-outlook-update-july-2026"),
    ("Cboe", "VIX index and VIX futures term structure",
     "https://www.cboe.com/tradable-products/vix/"),
    ("US EIA", "Crude oil and petroleum product prices, Q1 2026",
     "https://www.eia.gov/todayinenergy/detail.php?id=67424"),
    ("Military Times", "US launches new barrage of strikes on Iran around the Strait of Hormuz, 1 September 2026 - roughly 100 targets",
     "https://www.militarytimes.com/news/your-military/2026/09/01/us-launches-new-barrage-of-strikes-on-iran-around-strait-of-hormuz/"),
    ("Axios", "US strikes Iranian oil tankers for the first time, 2 September 2026 - new 'tanker for tanker' retaliation policy",
     "https://www.axios.com/2026/09/02/iran-tankers-hormuz-attacks-oil"),
    ("The Manila Times", "Peso closes weaker at P62.749 to the dollar, 18 September 2026 - down 1.9 centavos from P62.73, with PH 10-year yields around 7.50%. This is the level the model carries",
     "https://www.manilatimes.net/2026/09/18/business/peso-closes-weaker-at-p627491/2428119"),
    ("GMA News", "Peso closes at a fresh record low of P62.86 to the dollar, 14 September 2026 - the sixth record of the month, from P62.68 on the 11th. The record and the current level are separate inputs; this is the record",
     "https://www.gmanetwork.com/news/money/economy/1002326/peso-closes-at-fresh-record-low-of-p62-86-to-us-dollar/story/"),
    ("BusinessWorld", "Peso rebounds after hitting the P62.90 range, 16 September 2026 - closed P62.835 on the 15th with an intraday trough of P62.925, the weakest print on record",
     "https://bworldonline.com/banking-finance/2026/09/16/777421/peso-rebounds-after-hitting-p62-90-range/"),
    ("Federal Reserve", "H.15 Selected Interest Rates (Daily) - the 10-year closed 4.94% on 17 September 2026 (once published here as the EIGHTEENTH's close); 5.24 on 9 Oct and 5.21 on 13 Oct (14 Oct release); 5.09 on 16 Oct (19 Oct release)",
     "https://www.federalreserve.gov/releases/h15/"),
    ("CNBC", "Treasury yields ease as global borrowing costs tumble, 21 September 2026 - the 10-year fell more than 4bp to 4.951% and the 30-year to 5.284%, after the 10-year hit a 19-year high of 5.041% the previous week",
     "https://www.cnbc.com/2026/09/21/treasury-yields-government-bonds.html"),
    ("CNBC", "Stock market news for 21 September 2026 - S&P 500 +1.49% to 7,764.70, Nasdaq +2.26% to 27,122.09 (a record close, its first since June), Dow +366.19 points (+0.71%) to 52,048.83",
     "https://www.cnbc.com/2026/09/20/stock-market-today-live-updates.html"),
    ("CNBC", "US crude tumbles back below $100 after Trump says he is open to talking to Iran at the UN, 21 September 2026 - a fourth session of losses; the Petroline closure read as less disruptive than feared and Hormuz flows resilient. The SETTLE is disputed and is not carried",
     "https://www.cnbc.com/2026/09/21/iran-us-oil-prices-crude-saudi-arabia-.html"),
    ("CNBC", "Iranian President Pezeshkian to head to New York for the UN meeting as Trump warns of no-deal consequences, 21 September 2026 - Trump addresses the UNGA on the 22nd weighing a 'big decision' on new strikes; Pezeshkian speaks the day after",
     "https://www.cnbc.com/2026/09/21/us-iran-war-trump-hormuz.html"),
    ("radar.ph", "Peso slips further as PSEi extends decline to a second session, 21 September 2026 - the peso lost 3.1 centavos to P62.78; the PSEi shed 12.12 points (0.21%) to 5,843.79",
     "https://radar.ph/peso-slips-further-as-psei-extends-decline-to-second-session-september-21-2026/"),
    ("IMF PortWatch", "Strait of Hormuz daily transit calls - 1 transit on 20 September 2026 (8 on 13 September) against a pre-crisis baseline of 85/day, via the Straits Daily Brief (baseline measured 28 Feb 2025 to 27 Feb 2026). Published weekly on Tuesdays, so the reading is structurally a few days behind",
     "https://portwatch.imf.org/pages/cc317ba850e34c4dadbead6f7b336fb1"),
    ("TradingKey", "Nikkei 225 closes up 0.76% at 65,513.94 on its return from holiday; "
     "South Korean markets closed (Chuseok), 24 September 2026",
     "https://www.tradingkey.com/analysis/stocks/more/262184314-japan-south-korea-stocks-kospi-nikkei-softbank-kioxia-tradingkey"),
    ("Straits Daily Brief", "Strait of Hormuz status, 18-20 September 2026 - AIS-visible vessels holding position away from berth in the Hormuz and Gulf watch box, excluding ships within 25 km of a working port: 369, 357 and 376",
     "https://straits.live/briefs/2026-09-20"),
    ("Bloomberg", "Saudi Arabia seeks to resume half of its key oil pipeline within days, 16 September 2026 - Aramco bypassing the damaged section, targeting full capacity in about six weeks",
     "https://www.bloomberg.com/news/articles/2026-09-16/saudis-seek-to-resume-half-of-key-oil-pipeline-within-days"),
    ("Engineering News-Record", "Saudi Aramco works to bypass damage on the East-West pipeline - regional officials cited on 18 September put repairs at three to five weeks with only partial flows meanwhile; no Saudi crude had left Yanbu since 11 September; Yanbu stocks below 15 million barrels, a four-to-seven-day buffer; Kpler puts the Yanbu export loss at 2.5-2.7 mb/d",
     "https://www.enr.com/articles/63668-saudi-aramco-works-to-bypass-damage-on-critical-east-west-oil-pipeline"),
    ("Bank of Japan", "Statement on Monetary Policy, 18 September 2026 - policy rate raised 25bp to 1.25%, the highest since 1995, on a 7-2 vote with Asada and Sato dissenting",
     "https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k260918a.pdf"),
    ("CNBC", "Bank of Japan raises rates to a 31-year high, 18 September 2026 - and the yen FELL, the split vote casting doubt on the pace of further tightening",
     "https://www.cnbc.com/2026/09/18/japan-raises-rates-30-year-high-yen-jgb.html"),
    ("Reuters", "Japan core CPI rose 1.7% y/y in August 2026, released 18 September - below the 1.8% consensus and down from 1.8% in July; ex fresh food and fuel 1.9%",
     "https://www.investing.com/news/economic-indicators/japans-august-core-consumer-prices-rise-17-yryr-4906565"),
    ("CNBC", "Stock market close, 18 September 2026 - S&P 500 7,650.50 (+0.17%), Nasdaq 26,522.55 (+0.39%), Dow 51,682.64 (-0.18%, -95.40 points) on triple witching",
     "https://www.cnbc.com/2026/09/17/stock-market-today-live-updates.html"),
    ("CNBC", "Oil prices, 18 September 2026 - Brent settled $103.87 (-0.9%), WTI $100.30 (-1.6%); Brent lost nearly 1% on the week, WTI finished flat",
     "https://www.cnbc.com/2026/09/18/oil-prices-today-brent-wti-saudi-arabia-houthi.html"),
    ("thetrading.tools", "VIX term structure - the 20 Oct 2026 Cboe settlements carried from 21 Oct (Nov 18.4881, Dec 18.6965; October 17.2209 settles 21 Oct), VIX3M 18.99 with VIX 17.31 (ratio 0.9115); before them the 5 Oct settlements (Oct 17.46, Nov 18.14, Dec 18.55, Jan 19.33)",
     "https://www.thetrading.tools/vix-term-structure"),
    ("J.P. Morgan Asset Management", "2026 Long-Term Capital Market Assumptions - US equity 6.7%, EM equity 7.8%",
     "https://am.jpmorgan.com/us/en/asset-management/adv/about-us/media/press-releases/jp-morgan-releases-2026-long-term-capital-market-assumptions/"),
    ("J.P. Morgan Asset Management", "Nasdaq Equity Premium Income Active UCITS ETF (IE000U9J8HX9) factsheet - 0.35% TER",
     "https://am.jpmorgan.com/content/dam/jpm-am-aem/asiapacific/sg/en/literature/fact-sheet/factsheet-jpmorgan-nasdaq-equity-premium-income-active-ucits-etf.pdf"),
    ("Fidelity International", "Fidelity Funds - Global Technology Fund factsheet, 31 August 2026 (Singapore) - top holdings TSMC 9.1%, Microsoft 6.9%, Apple 5.4%; GICS IT 65.7%; USA 53.5%, Taiwan 10.8% - the stock-level look-through since 10 Oct",
     "https://www.fidelityinternational.com/legal/documents/SG-en/hffs.SG-en.SG.G-TEC.pdf"),
    ("ATRAM Trust Corporation", "Fund pages and KIIDS - fees, target funds, benchmarks",
     "https://www.atram.com.ph/funds/selector"),
    ("UITF.com.ph (TOAP)", "Official Philippine UITF daily NAVpu portal",
     "https://www.uitf.com.ph/"),
    ("BusinessWorld", "ATRAM launches Nasdaq income feeder fund - 1.50% fee, 75% NDX benchmark",
     "https://bworldonline.com/banking-finance/2026/04/29/746186/atram-launches-nasdaq-income-feeder-fund/"),
    ("Philippine Star", "ATRAM launches Nasdaq feeder fund",
     "https://www.philstar.com/business/2026/04/29/2524247/atram-launches-nasdaq-feeder-fund"),
    ("J.P. Morgan Asset Management", "JEPQ factsheet, 31 August 2026 - top-10 holdings used for the stock-level look-through",
     "https://am.jpmorgan.com/content/dam/jpm-am-aem/americas/us/en/literature/fact-sheet/etfs/FS-JEPQ.PDF"),
    ("Fidelity International", "Global Technology Fund W-Acc-GBP (LU1033663649) portfolio - ICB sector composition, the look-through until 10 Oct",
     "https://www.fidelity.co.uk/factsheet-data/factsheet/LU1033663649-fid-funds-global-tech-fd-w-acc-gbp/portfolio"),
    ("Morningstar", "JPMorgan Nasdaq Equity Premium Income - strategy and risk analysis",
     "https://www.morningstar.com/etfs/xnas/jepq/quote"),
    ("Siblis Research / STOXX", "STOXX Europe 600 P/E - trailing 19.67, forward 15.37",
     "https://siblisresearch.com/data/europe-pe-ratio/"),
    ("J.P. Morgan Private Bank", "2026 Asia Mid-Year Outlook - Asia ex-Japan 10.5x forward",
     "https://privatebank.jpmorgan.com/apac/en/insights/markets-and-investing/asf/2026-asia-mid-year-outlook"),
    ("S&P Global", "US Flash Composite PMI, September 2026 - 58.4 from 56.0, strongest since "
     "July 2021; services 58.7 (56.0 consensus); manufacturing PMI 57.0 from 53.9, a 52-month "
     "high (manufacturing output index 56.7); input prices highest since October 2022",
     "https://www.pmi.spglobal.com/Public/Home/PressRelease/7c2acaf676064c92bab19610524887d3"),
    ("Federal Reserve", "Governor Michael Barr remarks, 23 September 2026 - 'in my base case, "
     "further policy adjustments are likely to be needed'",
     "https://wolfstreet.com/2026/09/23/bond-bloodbath-treasury-10-year-yield-spikes-13-basis-points-breaks-out-hits-5-10-after-hot-pmis-with-inflation-written-all-over/"),
    ("CNBC", "10-year Treasury yield rockets to 19-year high, 23 September 2026 - 10-year "
     "+13bp to 5.104% (market print; intraday peak 5.135%), 2-year +11bp to 4.889% "
     "(highest since May 2024), 30-year +9bp to 5.398% (highest since June 2007)",
     "https://www.cnbc.com/2026/09/23/treasury-yields-oil-inflation-fed.html"),
    ("CNBC", "Market sees next Fed hike in October, following Barr comments and hot "
     "inflation reading, 23 September 2026 - CME FedWatch October odds 73%, from 55% "
     "on Tuesday",
     "https://www.cnbc.com/2026/09/23/market-sees-next-fed-hike-in-october-following-barr-comments-hot-inflation.html"),
    ("CNN", "10-year Treasury yield hits 5.1% for first time in 19 years, 23 September 2026",
     "https://www.cnn.com/2026/09/23/investing/us-bond-market-fed"),
    ("Yahoo Finance / Reuters", "US stock market close, 23 September 2026 - S&P 500 "
     "-0.75% to 7,706.03, Nasdaq -1.13% to 26,936.04, Dow -0.68% (-352.10pts) to 51,511.59",
     "https://finance.yahoo.com/markets/live/stock-market-today-wednesday-september-23-dow-sp-500-nasdaq-080556640.html"),
    ("BusinessWorld", "Peso appreciates 5.5 centavos to P62.725 on US-Iran talk optimism, "
     "22 September 2026",
     "https://bworldonline.com/banking-finance/2026/09/23/780530/peso-rebounds-on-hopes-for-us-iran-talks/"),
    ("radar.ph", "Peso holds steady as PSEi falls for fourth straight session, "
     "23 September 2026 - peso flat at P62.725, PSEi -19.42pts to 5,795.14",
     "https://radar.ph/peso-holds-steady-as-psei-falls-for-fourth-straight-session-september-23-2026/"),
    ("CNBC", "Iran's president blames US, Israel for global instability in defiant UN "
     "speech, 23 September 2026",
     "https://www.cnbc.com/2026/09/23/iran-united-nations-trump-israel.html"),
    ("Reuters / Hydrocarbon Processing", "Saudi Arabia's East-West pipeline restart status, "
     "23 September 2026 - targeting 4mb/d of 7mb/d capacity, 40% within days, full restart "
     "6-8 weeks; ~14mb loaded onto 7 VLCCs at Ras Tanura on 20 September",
     "https://www.hydrocarbonprocessing.com/news/2026/09/saudi-arabia-restarts-east-west-oil-pipeline/"),
    ("CNBC", "Oil prices rise, snap five day losing streak as Iran vows it will not "
     "surrender, 23 September 2026 - Brent +3.9% to $103.08, WTI (November) +1.8% to $92.16",
     "https://www.cnbc.com/2026/09/23/iran-us-talks-crude-oil-un-wti.html"),
    ("MarketScreener / Dow Jones", "October WTI crude contract closes down $1.19, or 1.2%, "
     "settles at $94.59 - the expiring contract's final settle, 22 September 2026",
     "https://www.marketscreener.com/news/october-wti-crude-oil-contract-closes-down-1-19-or-1-2-settles-at-94-59-per-barrel-november-br-ce785ad8d08af725"),
    ("NBC News", "Treasury yields surge to near 20-year high as oil jumps back above $103 "
     "per barrel, 23 September 2026 - sharpest one-day 10-year jump since 9 April 2025",
     "https://www.nbcnews.com/business/energy/treasury-yields-oil-stocks-rcna599398"),
    ("CNBC", "Oil prices dip as Iraq increases exports, 22 September 2025 - Brent settled "
     "$66.57, the year-ago base for Brent's y/y change",
     "https://www.cnbc.com/amp/2025/09/22/oil-is-little-changed-as-russia-mideast-concerns-offset-by-oversupply-worry.html"),
    ("CNBC", "10-year Treasury yield is little changed to end a volatile week, 25 September "
     "2026 - 10-year +<1bp to 5.163% after Thursday's post-June-2007 high; 30-year +2bp to "
     "5.488%; 2-year -3bp to 4.856%",
     "https://www.cnbc.com/2026/09/25/treasury-yields-bonds-debt.html"),
    ("Advisor Perspectives (dshort)", "Treasury Yields Snapshot, 25 September 2026 - "
     "10-year finished at 5.17%, 2-year at 4.81% (Treasury par curve)",
     "https://www.advisorperspectives.com/dshort/updates/2026/09/25/treasury-yields-snapshot-september-25-2026"),
    ("Wolf Street", "Long-Term Treasury Yields Rise to 5.5%, 25 September 2026 - 10-year +16bp "
     "on the week to 5.17%; 20-year 5.55%, highest since June 2004; 30-year 5.50%",
     "https://wolfstreet.com/2026/09/25/long-term-treasury-yields-rise-to-5-5-mortgage-rates-to-7-5-as-bond-market-grapples-with-a-complex-reality/"),
    ("StreetStats", "US Treasury par yield curve - 23 September 2026 row: 10-year 5.12%, "
     "2-year 4.90%, 30-year 5.40%",
     "https://streetstats.finance/rates/treasuries"),
    ("CNBC", "U.S. crude oil falls nearly 8% for the week after Tehran and Washington hold "
     "talks at the U.N., 25 September 2026 - Brent -2.14% to $104.32",
     "https://www.cnbc.com/2026/09/25/oil-falls-as-potential-diplomatic-solution-to-iran-conflict-arises.html"),
    ("EnergyNow", "Oil ends week lower as US-Iran truce hopes hit WTI, 25 September 2026 - "
     "WTI (November) settled $92.41, down $2.20",
     "https://energynow.com/2026/09/oil-ends-week-lower-as-u-s-iran-truce-hopes-hit-wti-while-middle-east-supply-risks-keep-brent-above-100/"),
    ("CNBC", "Iran offers to reopen Strait of Hormuz within 7 days and restart nuclear "
     "talks, 25 September 2026",
     "https://www.cnbc.com/2026/09/25/us-iran-trump-hormuz-.html"),
    ("CNBC", "Saudi Arabia crude oil exports hit highest level since Iran war began despite "
     "pipeline outage, 25 September 2026 - 6 million b/d in September per Kpler, via a "
     "US-escorted channel along Oman's coast; August 3.4 million b/d",
     "https://www.cnbc.com/2026/09/25/saudi-arabia-oil-iran-war-pipeline-strait-hormuz-red-sea-houthis.html"),
    ("Bloomberg", "Saudis' Gulf oil surge drives exports to highest since war began, "
     "24 September 2026 - September heading for 5.28 million b/d",
     "https://www.bloomberg.com/news/articles/2026-09-24/saudis-gulf-oil-surge-drives-exports-to-highest-since-war-began"),
    ("Straits Daily Brief", "Strait of Hormuz status, 21-26 September 2026 - vessels holding "
     "position away from berth: 401, 443, 407, 422; PortWatch's latest transit reading still "
     "1 on 20 September",
     "https://straits.live/briefs/2026-09-26"),
    ("Eurostat", "Annual inflation up to 3.2% in the euro area, 17 September 2026 - final "
     "August HICP, revised from the 3.3% flash; energy 14.3%, contributing +1.29pp",
     "https://ec.europa.eu/eurostat/web/products-euro-indicators/w/2-17092026-ap"),
    ("Euronews", "Saudi Arabia reports fresh Houthi attacks as France offers military "
     "support to protect Yanbu, 25 September 2026",
     "https://www.euronews.com/2026/09/25/saudi-arabia-reports-fresh-houthi-attacks-as-france-offers-military-support-to-protect-yan"),
    ("CNBC", "Stock market news for Sept. 25, 2026 - S&P 500 +0.51% to 7,743.41, Dow "
     "+478.64 (+0.93%) to 51,828.62, Nasdaq +0.5% to 27,068.72; WTI -2.33% to $92.41",
     "https://www.cnbc.com/2026/09/24/stock-market-today-live-updates.html"),
    ("BEA / BLS", "Release schedules - Personal Income and Outlays, August 2026, on "
     "30 September; Employment Situation, September 2026, on 2 October",
     "https://www.bls.gov/schedule/news_release/current_year.asp"),
    # ---- added 2026-10-15, the 12-15 Oct roll ----
    ("CNBC", "CPI inflation report, September 2026 - headline 3.7% y/y (+0.6% m/m) vs 3.6% expected; core 2.6% (+0.3%)",
     "https://www.cnbc.com/2026/10/14/cpi-inflation-report-september-2026.html"),
    ("CBS News", "September CPI report shows inflation accelerated to 3.7% as energy costs soared - gasoline +9.1% m/m",
     "https://www.cbsnews.com/news/september-cpi-report-inflation-energy-costs/"),
    ("Fox Business", "September CPI: shelter 3.2% y/y, food 2.5%, gasoline +34.2% (BLS release summary)",
     "https://foxbusiness.com/economy/cpi-inflation-september-2026"),
    ("ABC News / Associated Press", "How major US stock indexes fared Wednesday 10/14/2026 - S&P 7718.94 (-86.51), Nasdaq 26692.87 (-511.51); week-to-date Dow -33.47",
     "https://abcnews.com/Business/wireStory/major-us-stock-indexes-fared-wednesday-10142026-137270020"),
    ("WTOP / Associated Press", "How major US stock indexes fared Monday 10/12/2026 - S&P 7807.24, Nasdaq 27245.90, Dow 51850.55 (+195.60)",
     "https://wtop.com/national/2026/10/how-major-us-stock-indexes-fared-monday-10-12-2026"),
    ("KVUE / Associated Press", "How major US stock indexes fared Tuesday 10/13/2026 - S&P 7805.45 (-1.79), Nasdaq 27204.38 (-41.52), Dow 51670.10 (-180.45)",
     "https://www.kvue.com/article/syndication/associatedpress/how-major-us-stock-indexes-fared-tuesday-10132026/616-79e921f9-f51b-49be-8ffb-40f942bd73c3"),
    ("CNBC", "Oil, 14 Oct 2026 - Brent settled $106.06 (+37 cents) after the IEA warning and the Houthi strike on Aramco",
     "https://www.cnbc.com/2026/10/14/oil-rises-amid-growing-tensions-between-saudis-and-iran-backed-houthis.html"),
    ("FNN (Financial News)", "[Oil prices] Brent settles down 0.9% at $105.69; WTI rises 0.43% to $94.14, 13 Oct 2026",
     "https://en.fnnews.com/news/202610140452085589"),
    ("Newsquawk", "Crude wrap: WTI (X6) settles USD 0.95 higher at 95.09/bbl; Brent (Z6) USD 0.37 higher at 106.06/bbl",
     "https://www.newsquawk.com/headlines/crude-wrap-wti-x6-settles-usd-095-higher-at-9509bbl-brent-z6-settles-usd-037-higher-at-10606bbl"),
    ("TheStreet", "Stock market today, 12 Oct 2026 - S&P moderates; Brent +1.8% to $106.65",
     "https://www.thestreet.com/stock-market-today/stock-market-today-oct-12-2026-dow-futures-climb-as-wall-street-gears-up-for-busy-week"),
    ("TradingView / Dow Jones Newswires", "Data Talk, 15 Oct 2025 - front-month ICE Brent fell 0.77% to settle at $61.91, down $1.41 over two sessions (the y/y base)",
     "https://it.tradingview.com/news/DJN_DN20251015007406%3A0-front-month-ice-brent-crude-fell-0-77-to-settle-at-61-91-data-talk"),
    ("FRED", "CBOE Volatility Index: VIXCLS - 15.21 (12 Oct), 15.27 (13 Oct)",
     "https://fred.stlouisfed.org/series/vixcls"),
    ("StockMarketWatch", "Treasury par yield curve, 14 Oct 2026 - 10-year 5.19%, -2bp",
     "https://stockmarketwatch.com/bonds"),
    ("CNBC", "10-year Treasury yield dips as traders look ahead to Thursday's reports - 2-year 4.808%, 30-year 5.517%, 14 Oct",
     "https://www.cnbc.com/2026/10/14/us-treasury-yields-cpi-inflation-report.html"),
    ("FinanceFeeds", "Fed rate hike in October? Odds after the 3.7% CPI - FedWatch 31.6% October, 89.7% December (FXStreet, 7:23pm ET 14 Oct)",
     "https://financefeeds.com/will-the-fed-hike-on-28-october-what-the-odds-did-after-a-3-7-cpi/"),
    ("Manila Bulletin", "Peso crashes past P63:$1, hits weakest-ever close of 63.06, 15 Oct 2026",
     "https://mb.com.ph/2026/10/15/peso-crashes-past-631-hits-weakest-ever-close"),
    ("BusinessWorld", "Peso extends slide before US consumer inflation data - closes at P62.87, 14 Oct 2026",
     "https://bworldonline.com/banking-finance/2026/10/14/786942/peso-extends-slide-before-us-consumer-inflation-data/"),
    ("Manila Bulletin", "PSEi snaps two-day slide after holding 5,600 support: +45.94 to 5,663.17, 15 Oct 2026",
     "https://mb.com.ph/2026/10/15/psei-snaps-two-day-slide-after-holding-5600-support"),
    ("BusinessWorld", "PSEi plunges to 5,600 level as sell-off continues: -84.31 to 5,617.23, 14 Oct 2026",
     "https://bworldonline.com/stock-market/2026/10/14/786880/psei-plunges-to-5600-level-as-sell-off-continues/"),
    ("BusinessWorld", "BTr partially awards T-bills as yields climb on rate hike bets - 5.845 / 6.171 / 6.351%, 12 Oct 2026",
     "https://bworldonline.com/banking-finance/2026/10/12/786345/btr-partially-awards-t-bills-as-yields-climb-on-rate-hike-bets/"),
    ("The Asia Business Daily", "KOSPI closes down more than 7% as circuit breaker is triggered - 5,554.22, 15 Oct 2026",
     "https://www.asiae.co.kr/en/article/2026101515453239955"),
    ("Seoul Economic Daily", "KOSPI closes down 0.44% at 6,008.81, 14 Oct 2026",
     "https://en.sedaily.com/finance/2026/10/14/kospi-closes-down-044-percent-at-600881"),
    ("The Japan Times", "Nikkei 225 falls 5% on rate and AI concerns - 64,425.95, 15 Oct 2026",
     "https://www.japantimes.co.jp/business/2026/10/15/nagata-nikkei-decline/"),
    ("TSMC (SEC Form 6-K)", "Third-quarter 2026 results - net income NT$763.06bn, +68.7% y/y; revenue NT$1,494.24bn",
     "https://www.sec.gov/Archives/edgar/data/0001046179/000104617926000726/a3q26e_withguidancexfinal.htm"),
    ("CNBC", "Nvidia, SK Hynix, ASML, SoftBank: global tech rout on AI funding worries, 15 Oct 2026",
     "https://www.cnbc.com/2026/10/15/sk-hynix-samsung-softbank-stocks-asia-tech-rout-ai-funding-worries.html"),
    ("gCaptain", "Containership sinks as Hormuz attacks spiral out of control - GFS Pride, 13 Oct 2026",
     "https://gcaptain.com/containership-sinks-as-hormuz-attacks-spiral-out-of-control/"),
    ("CNBC", "Container ship sinks in Strait of Hormuz as Iran steps up attacks, 14 Oct 2026",
     "https://www.cnbc.com/2026/10/14/container-ship-sinks-strait-hormuz-as-iran-war-attacks.html"),
    ("Investing.com (Reuters)", "Container ship sinks in Strait of Hormuz amid Iran attacks - Kpler: Hormuz crude 8.5 mb/d in the week to 12 Oct",
     "https://in.investing.com/news/economy-news/container-ship-sinks-in-strait-of-hormuz-amid-iran-attacks-5633558"),
    ("France 24", "Blasts rock Riyadh as Houthis vow to continue striking Saudi airports, oil facilities - Aramco building hit, 14 Oct 2026",
     "https://www.france24.com/en/middle-east/20261014-live-saudi-arabia-reports-aramco-building-hit-and-four-wounded-in-houthi-missile-attacks"),
    ("IEA", "Oil Market Report - October 2026: Hormuz flows +3.7 mb/d to 10.9 mb/d in September",
     "https://www.iea.org/reports/oil-market-report-october-2026"),
    ("CBS News", "Iran calls U.S. response 'insufficient' amid stalled talks to end the war",
     "https://www.cbsnews.com/live-updates/iran-war-trump-us-elections-saudi-arabia-yemen-houthis/"),
    ("ATRAM Trust Corporation", "ATRAM Global Technology Feeder Fund (A PHP unit class) - trust fee 1.50% p.a.",
     "https://www.atram.com.ph/funds/uitf-funds/details?fund=ATRGTEC"),
    ("Poor Pinoy Investor", "ATRAM feeder fund fees increasing 14 September 2026 - Global Technology 1.15% to 1.50%; five others 1.20% to 1.50%",
     "https://poorpinoyinvestor.com/atram-feeder-fund-fee-increase-2026/"),
    ("Ideal Investisseur", "OAT / Bund spread: 135.5bp as of 14 Oct 2026 (OAT 4.81%, Bund 3.45%)",
     "https://www.ideal-investisseur.fr/en/markets/oat-bund-spread.html"),
    ("Inquirer", "Consensus builds for further BSP rate increases - a fourth hike expected on 22 Oct",
     "https://business.inquirer.net/615592/consensus-builds-for-further-bsp-rate-increases"),
    ("FXStreet", "Japanese yen: BoJ hawkishness supports JPY against US dollar - MUFG, 15 Oct 2026",
     "https://www.fxstreet.com/news/japanese-yen-boj-hawkishness-supports-jpy-against-us-dollar-mufg-202610150745"),
    # ---- added 2026-10-17, the 15-16 Oct roll ----
    ("WTOP / Associated Press", "How major US stock indexes fared Thursday 10/15/2026 - S&P 7744.06 (+25.12), Nasdaq 26713.03 (+20.16), Dow 52177.69 (+556.21)",
     "https://wtop.com/news/2026/10/how-major-us-stock-indexes-fared-thursday-10-15-2026"),
    ("ABC News / Associated Press", "How major US stock indexes fared Friday 10/16/2026 - S&P 7659.44 (-84.62), Nasdaq 26140.03 (-572.99), Dow 52002.41 (-175.28)",
     "https://abcnews.com/Business/wireStory/major-us-stock-indexes-fared-friday-10162026-137331951"),
    ("CNBC", "September producer price index and retail sales - PPI +1.3% m/m, retail sales +0.8%",
     "https://www.cnbc.com/2026/10/15/september-producer-price-index-retail-sales-data.html"),
    ("US News / Reuters", "US producer prices post largest gain in 4-1/2 years; expensive gasoline boosts retail sales, 15 Oct 2026",
     "https://money.usnews.com/investing/news/articles/2026-10-15/us-producer-prices-post-largest-increase-in-4-1-2-years-in-september"),
    ("Yahoo Finance / Reuters", "Brent oil slips as US weighs easing sanctions on global shadow fleet - settled $105.92 (-0.13%), 15 Oct 2026",
     "https://finance.yahoo.com/energy/articles/oil-prices-fall-investors-weigh-012948990.html"),
    ("Investing.com / Reuters", "Oil touches $110 a barrel for first time since May - Brent settled $109.86 (+3.7%), WTI $101.41 (+3.5%), 16 Oct 2026",
     "https://www.investing.com/news/commodities-news/oil-edges-down-as-investors-weigh-possible-us-sanctions-on-shadow-fleet-4952926"),
    ("CNBC", "Brent oil touches $110 as Iran escalates Hormuz attacks - Kpler: Hormuz shipments 9.4 mb/d in the week to 14 Oct, ~70% of pre-war",
     "https://www.cnbc.com/2026/10/16/oil-price-today-iran-strait-hormuz-ukraine-russia.html"),
    ("CNBC", "Wall Street's fear gauge is ripping; traders see it going even higher - VIX above 22 intraday, 16 Oct 2026",
     "https://www.cnbc.com/2026/10/16/wall-streets-fear-gauge-is-ripping-traders-see-it-going-even-higher.html"),
    ("CNBC", "U.S. Treasury yields waver as traders wrap up volatile week - 10-year 5.085%, 2-year 4.715%, 30-year 5.434%, 16 Oct",
     "https://www.cnbc.com/2026/10/16/us-treasury-yields-investors-hot-inflation-data-.html"),
    ("Invezz", "Fed rate-hold odds jump to 85% even as Warsh offers no clues - CME FedWatch 85.1% hold, December hike 88.9%, 16 Oct 2026",
     "https://invezz.com/news/2026/10/16/fed-rate-hold-odds-jump-to-85-even-as-warsh-offers-no-clues-on-policy-path/"),
    ("The Manila Times", "Peso rebounds from record low, closes at P62.985:$1 after an intraday P63.23, 16 Oct 2026",
     "https://www.manilatimes.net/2026/10/16/business/peso-rebounds-from-record-low-closes-at-p629851/2447280"),
    ("Manila Bulletin", "PSEi surges as MSCI Indonesia warning, lower yields lift sentiment: +119.53 to 5,782.70, 16 Oct 2026",
     "https://mb.com.ph/2026/10/16/psei-surges-as-msci-indonesia-warning-lower-yields-lift-sentiment"),
    ("Aju Press", "Foreigners end eight-day sell-off as KOSPI, Nikkei rebound - KOSPI +113.83 to 5,668.05, 16 Oct 2026",
     "https://www.ajupress.com/view/20261016153219133"),
    ("Vantage Markets", "Nikkei 225 rises after a 4.90% drop - close 65,324.29 (+898.34), 16 Oct 2026",
     "https://www.vantagemarkets.com/market-news/nikkei-225-rises-after-4-90-percent-drop-october-16-2026/"),
    ("Eurostat", "Annual inflation up to 3.8% in the euro area - September 2026 final, 16 October 2026",
     "https://ec.europa.eu/eurostat/web/products-euro-indicators/w/2-16102026-ap"),
    ("ANI / UKMTO", "Tanker struck by unknown projectile near Al Jubail in Saudi Arabia, 16-17 Oct 2026",
     "https://aninews.in/news/world/europe/tanker-struck-by-unknown-projectile-near-al-jubail-in-saudi-arabia-ukmto20261017130404/"),
    ("Meduza / Reuters", "US weighs easing sanctions on shadow fleet tankers, 15 Oct 2026",
     "https://meduza.io/en/news/2026/10/15/us-weighs-easing-sanctions-on-shadow-fleet-tankers"),
    ("Admiral Markets", "ECB meeting October 2026: dates (28-29 October) and what markets watch",
     "https://admiralmarkets.com/analytics/traders-blog/ecb-meeting-october-2026"),
    # ---- added 2026-10-20, the 19-20 Oct roll ----
    ("Anadolu Agency", "US stocks close Monday mixed as tech shares rise: S&P 7690.73 (+31.29), Nasdaq 26430.89 (+290.85), Dow 51966.03 (-36.38), 19 Oct 2026",
     "https://aa.com.tr/en/economy/us-stocks-close-monday-mixed-as-tech-shares-raise/4093958"),
    ("CNBC", "Dow jumps 500 points as earnings optimism steadies market: Dow 52495.88 (+529.85), S&P 7712.57 (+0.28%), Nasdaq 26424.82 (-0.02%), 20 Oct 2026",
     "https://www.cnbc.com/2026/10/19/stock-market-today-live-updates.html"),
    ("CNBC", "Oil prices fall as traders hope for diplomatic progress in Middle East - Brent settled $108.79 (-0.7%), session high $111.99; November WTI expired at $101.79, December $98.28, 20 Oct 2026",
     "https://www.cnbc.com/2026/10/20/oil-price-wti-brent-crude.html"),
    ("Rigzone / Bloomberg", "Oil slips as Iran talks fuel volatility - a diplomat disputes reports that a US-Iran deal is close, 20 Oct 2026",
     "https://www.rigzone.com/news/oil_slips_as_iran_talks_fuel_volatility-20-oct-2026-184889-article"),
    ("CNBC", "Brent oil tops $109 after Houthi militants claim attacks on Saudi airports and Aramco facilities, 19 Oct 2026",
     "https://www.cnbc.com/2026/10/18/oil-price-today-ukraine-russia-iran-strait-hormuz.html"),
    ("Al Arabiya", "Tanker explodes after hitting mine in Strait of Hormuz: Iran's IRGC - supertanker with more than 2m barrels, unnamed, 17 Oct 2026",
     "https://english.alarabiya.net/News/middle-east/2026/10/17/tanker-explodes-after-hitting-mine-in-strait-of-hormuz-iran-s-irgc"),
    ("The New Arab", "Exclusive: mediators submit new peace proposal to Iran, US - the Qatar-Pakistan compromise, 20 Oct 2026",
     "https://www.newarab.com/news/exclusive-mediators-submit-new-peace-proposal-iran-us"),
    ("CNBC", "Trump waives broad new Russia sanctions and tariffs before they take effect - a 60-day review, 16-17 Oct 2026",
     "https://www.cnbc.com/2026/10/17/trump-waives-russia-related-sanctions-tariffs-before-they-take-effect-.html"),
    ("Straits Daily Brief", "Strait of Hormuz status, 20 Oct 2026 - IMF PortWatch 4 transits on 18 Oct against an 85/day baseline",
     "https://straits.live/briefs/2026-10-20"),
    ("Forbes Advisor", "Treasury rates today - 10-year par yield 5.15% on 19 Oct 2026, 5.12% on 20 Oct (down 3 basis points) and 5.13% on 21 Oct, with the 2-year 4.81% and 30-year 5.42%; 4.99% on 27 Oct (down 1bp)",
     "https://www.forbes.com/advisor/investing/treasury-rates/"),
    ("CNBC", "Treasury yields move higher as investors assess the US inflation backdrop - 10-year 5.146%, 19 Oct 2026",
     "https://www.cnbc.com/2026/10/19/bonds-treasurys-us-yields.html"),
    ("Trading Economics", "US 10-year Treasury note yield: 5.12% on 20 Oct 2026, down 2bp (market basis)",
     "https://tradingeconomics.com/united-states/government-bond-yield"),
    ("Forbes", "What to look for from the Fed's October meeting - markets firmly expect a December hike, about 15% for October, 19 Oct 2026",
     "https://www.forbes.com/sites/simonmoore/2026/10/19/what-to-look-for-from-the-feds-october-meeting/"),
    ("The Daily Macro Brief", "VIX 18.44, VIX3M (VXV) 19.60, ratio 0.94 - the 19 Oct close, 20 Oct 2026",
     "https://dn12448583.substack.com/p/the-daily-macro-brief-october-20"),
    ("Saxo", "The front end drains, the tails do not - options brief: October VIX future 18.67, November 18.75, spot 18.44, 20 Oct 2026",
     "https://home.saxo/en-gb/content/articles/options/the-front-end-drains-the-tails-do-not---options-brief---20-october-2026-20102026"),
    ("Daily Tribune", "Peso sets another record low, stocks gain: P63.09 to the dollar; PSEi up 15.20 to 5,797.90, 19 Oct 2026",
     "https://tribune.net.ph/2026/10/19/peso-sets-another-record-low-stocks-gain"),
    ("The Manila Times", "Peso closes at record-low P63.09 for second straight day, 20 Oct 2026",
     "https://www.manilatimes.net/2026/10/20/business/peso-closes-at-record-low-p6309-for-second-straight-day/2449446"),
    ("Philippine Daily Inquirer", "PSEi clears 5,800 as bargain hunting lifts stocks: up 8.27 to 5,806.17, 20 Oct 2026",
     "https://business.inquirer.net/616826/psei-clears-5800-as-bargain-hunting-lifts-stocks"),
    ("BusinessWorld", "Yields on short-term bills climb - 91-day 5.992% (+14.7bp), 182-day 6.229% (+5.8bp), 19 Oct 2026",
     "https://bworldonline.com/banking-finance/2026/10/19/787915/yields-on-short-term-bills-climb/"),
    ("Business Recorder / Reuters", "Philippines awards $861mn of T-bill and cash-management bill offers - 364-day 6.444%, 19 Oct 2026",
     "https://www.brecorder.com/news/40444916/philippines-awards-861mn-worth-of-t-bill-cash-management-bill-offers"),
    ("Seoul Economic Daily", "KOSPI closes up 1.76% at 5,768.01, 19 Oct 2026",
     "https://en.sedaily.com/finance/2026/10/19/kospi-closes-up-176-percent-at-576801"),
    ("Seoul Economic Daily", "KOSPI closes down 3.73% at 5,552.74 (-215.27, Korea Exchange), 20 Oct 2026",
     "https://en.sedaily.com/finance/2026/10/20/kospi-closes-down-373-percent-at-555274"),
    ("uCapital", "Nikkei 225 falls 0.62% to 64,916.70 at the Tokyo close, 19 Oct 2026",
     "https://ucapital.com/en/news/markets/nikkei-225-tokyo-close-oct-19-2026-6ad5bcb64bc7e3d4606f0be5"),
    ("Gulf Today / Associated Press", "Asian shares mostly decline after AI stocks lead a rebound on Wall Street - Nikkei down 1.3% to 64,075.42, 20 Oct 2026",
     "https://www.gulftoday.ae/business/2026/10/20/asian-shares-mostly-decline-after-ai-stocks-lead-a-rebound-on-wall-street"),
    ("US News / Reuters", "China's economic growth picks up in the third quarter, beating expectations - 4.5% against 4.4%, 19 Oct 2026",
     "https://money.usnews.com/investing/news/articles/2026-10-18/chinas-economic-growth-picks-up-in-third-quarter-beating-expectations"),
    # ---- added 2026-10-21, the two funds beyond the original four ----
    ("Fidelity", "Fidelity Funds - Global Dividend Fund Y-Acc-USD: ongoing charge 1.04%",
     "https://www.fidelity.co.uk/factsheet-data/factsheet/LU0605515963USD-fidelity-funds---global-dividend-fund-y-acc-usd/charges-and-key-documents"),
    ("Seedbox / ATRAM", "ATRAM Global Dividend Feeder Fund KIIDS: target fund Fidelity Funds - Global Dividend Fund",
     "https://file.seedbox.ph/ATRAM%20GLOBAL%20DIVIDEND%20FEEDER%20FUND%20KIIDS_Jan_2021.pdf"),
    ("BusinessWorld", "ATRAM offers global feeder funds via PERA: the Global Dividend feeders invest in the Fidelity Global Dividend Fund, 21 Jul 2026",
     "https://bworldonline.com/banking-finance/2026/07/21/764648/atram-offers-global-feeder-funds-via-pera/"),
    ("PR Newswire / J.P. Morgan", "J.P. Morgan 2027 Long-Term Capital Market Assumptions: 60/40 at 7.0%; US large cap 7.5%, global equities 7.5%, emerging markets 7.1%, global aggregate bonds 5.3%, 19 Oct 2026",
     "https://www.prnewswire.com/news-releases/jp-morgan-releases-2027-longterm-capital-market-assumptions-projecting-7-0-return-for-6040-portfolio-over-10-15-years-302912421.html"),
    # ---- added 2026-10-21, the 21 Oct roll ----
    ("Daily Tribune", "Peso plunges to fresh record low as PSEi extends recovery: P63.361, 27.1 centavos weaker; PSEi up 15.34 to 5,821.51, 21 Oct 2026",
     "https://tribune.net.ph/2026/10/21/peso-plunges-to-fresh-record-low-as-psei-extends-recovery"),
    ("Radar PH", "Peso tumbles to all-time low again: P63.361 close, P63.373 intraday; PSEi up for a fifth session, 21 Oct 2026",
     "https://radar.ph/peso-tumbles-to-all-time-low-again-october-21-2026/"),
    ("BusinessWorld", "Stocks climb further as market eyes BSP decision, 21 Oct 2026",
     "https://bworldonline.com/stock-market/2026/10/21/788381/stocks-climb-further-as-market-eyes-bsp-decision/"),
    ("WSLS / Associated Press", "Asian shares are mixed, with Kospi up 3% after US stocks rally on strong earnings - KOSPI 5,735.66, Nikkei 64,621.24, 21 Oct 2026",
     "https://www.wsls.com/business/2026/10/21/asian-shares-are-mixed-with-kospi-up-3-after-us-stocks-rally-on-strong-earnings/"),
    ("Il Sole 24 Ore", "Tokyo: Nikkei up 0.85% at the close, shares lead the rebound, 21 Oct 2026",
     "https://en.ilsole24ore.com/art/tokyo-stock-exchange-nikkei-up-085-per-cent-at-close-shares-lead-the-rebound-AJ4ojypB"),
    ("CappNotes", "Closing Look, Tuesday 20 October 2026 - VIX 17.31",
     "https://cappnotes.substack.com/p/closing-look-tuesday-october-20-2026"),
    ("PC Thematic", "Daily market report, 20 Oct 2026 - VIX 17.31",
     "https://pcthematic.substack.com/p/daily-market-report-october-20-2026"),
    ("Vantage Markets", "US 10-year Treasury yield: 5.15% daily par yield on 19 October, 20 Oct 2026",
     "https://www.vantagemarkets.com/market-news/us-10-year-treasury-yield-cpi-reaction-october-20-2026/"),
    ("Forecasts.org", "10-year Treasury constant maturity, daily: 5.15 on 19 Oct 2026",
     "https://www.forecasts.org/10yrT.htm"),
    ("Anadolu Agency", "Oil rises as Iran tensions, US crude stock draw fuel supply concerns - Ghalibaf: no trust in Washington until Iran's conditions for reopening the Strait are met, 21 Oct 2026",
     "https://www.aa.com.tr/en/energy/oil/oil-rises-as-iran-tensions-us-crude-stock-draw-fuel-supply-concerns/60411"),
    ("IBTimes Australia", "Iran says mines set tankers ablaze in the Strait of Hormuz as the US military calls Tehran's claims false, Oct 2026",
     "https://www.ibtimes.com.au/iran-claims-mines-stopped-tankers-strait-hormuz-1877113"),
    # ---- added 2026-10-21, the two D funds on the Funds tab ----
    ("ATRAM", "ATRAM Global Dividend Feeder Fund (PHP Unit Class), fund code ATRGLDV: trust fee incl. distribution fee 1.50% p.a.; KIIDS July 2026",
     "https://www.atram.com.ph/funds/uitf-funds/details?fund=ATRGLDV"),
    ("uitf.com.ph", "ATRAM Global Dividend Feeder Fund (USD Unit Class): trust fee structure 1.50% p.a.",
     "https://uitf.com.ph/daily_navpu_details.php?fund_id=544&bank_id=31"),
    ("Fidelity International", "Fidelity Funds - Global Dividend Fund factsheet, 30 Sep 2026: US$21.4bn; top 10 TSMC 4.0%, Deutsche Boerse 3.4%, Unilever 3.4%, Roche 3.4%, Vinci 3.1% ...; Germany 11.2%, France 9.6%, Switzerland 8.9%, Japan 7.4%",
     "https://www.fidelityinternational.com/legal/documents/SG-en/hffs.SG-en.SG.G-GDMUS.pdf"),
    ("DFO Fairsheets", "Fidelity Funds - Global Dividend Fund: U.S.A. 21.16%, United Kingdom 13.31% (older listing)",
     "https://dfo.sg/fairsheets/funds/fidelity-funds-global-dividend-fund"),
    ("Trustnet", "Fidelity Global Dividend W Inc (UK OEIC, same manager), factsheet 6 Oct 2026: USA 21.7%, UK 14.1%; holdings at 31 Aug",
     "https://www2.trustnet.com/Factsheets/FundFactsheetPDF.aspx?fundCode=0OF2E&univ=O"),
    # ---- added 2026-10-21, the 24-fund list ----
    ("uitf.com.ph", "ATRAM US Equity Opportunity Feeder Fund (PHP Unit Class): trust fee 1.20% p.a. (page about 17 months old); benchmark MSCI USA Growth; inception 27 May 2025; NAVPU 126.02 on 18 Oct 2026",
     "https://uitf.com.ph/daily_navpu_details.php?fund_id=550&bank_id=31"),
    ("Seedbox / ATRAM", "ATRAM US Equity Opportunity Feeder Fund KIIDS, Feb 2021: target fund Franklin Templeton Investment Funds - Franklin U.S. Opportunities Fund",
     "https://file.seedbox.ph/ATRAM%20US%20EQUITY%20OPPORTUNITY%20FEEDER%20FUND%20KIIDS_Feb_2021.pdf"),
    ("Finect", "Franklin U.S. Opportunities Fund I(acc)USD: ongoing charges 0.85% (management 0.70%)",
     "https://www.finect.com/fondos-inversion/LU0195948665-Franklin_us_opportunities_iaccusd"),
    ("Franklin Templeton", "Franklin U.S. Opportunities Fund C(acc)USD factsheet, 30 Sep 2026: NVIDIA 10.37%, Microsoft 5.30%, Amazon 4.42% (top issuers at 31 Aug)",
     "https://www.franklintempletonoffshore.com/download/en-os/factsheet/21a1951a-931c-48fc-9d2b-5750d38f3542/Factsheet-FranklinUSOpportunitiesFund-C(acc)USD-4913-F--NRC-en-OS.PDF"),
    ("uitf.com.ph", "ATRAM US Multi-Asset Income Feeder Fund (A USD Unit Class): trust fee 1.50% p.a.; benchmark 50% MSCI USA High Dividend Yield / 25% Bloomberg US HY Very Liquid / 25% Bloomberg US Aggregate",
     "https://www.uitf.com.ph/home/daily_navpu_details.php?fund_id=624&bank_id=31"),
    ("Seedbox / ATRAM", "ATRAM US Multi-Asset Income Feeder Fund KIIDS, Dec 2020: target fund Allianz Income and Growth",
     "https://file.seedbox.ph/ATRAM%20US%20MULTI-ASSET%20INCOME%20FEEDER%20FUND%20KIIDS_Dec%202020.PDF"),
    ("Finect", "Allianz Income and Growth AM USD: ongoing charges 1.56% (management 1.50%); a third each in equities, high yield and convertibles",
     "https://www.finect.com/fondos-inversion/LU0820561818-Allianz_income_and_growth_am_usd"),
    # ---- added 2026-10-21, the v57 scrub ----
    ("Bloomberg", "Middle East oil flows near prewar levels defy Hormuz attacks - Kpler: Gulf crude and condensate a high of 24.6 mb/d in the week to 18 Oct; October to date still below prewar, 21 Oct 2026",
     "https://www.bloomberg.com/news/articles/2026-10-21/middle-east-oil-flows-near-prewar-levels-defy-hormuz-attacks"),
    ("Seeking Alpha / TradingView", "Middle East oil flows now surpass levels before the US-Iran war, Kpler says - Hormuz incl. Gulf of Oman transfers ~14 mb/d, 82% of prewar; all routes >24 vs 23.3 mb/d, 21 Oct 2026",
     "https://www.tradingview.com/news/seekingalpha:313ed4e49094b:0-middle-east-oil-flows-now-surpass-levels-before-u-s-iran-war-kpler-says/"),
    ("The National", "Non-Iran Middle East oil exports recover to prewar levels with Hormuz alternatives, 21 Oct 2026",
     "https://www.thenationalnews.com/business/energy/2026/10/21/non-iran-middle-east-oil-exports-recover-to-prewar-levels-with-hormuz-alternatives/"),
    ("YourBestSavings (US Treasury par curve)", "Treasury yields today, 20 Oct 2026 - 2-year 4.79%, 10-year 5.12%, 30-year 5.42% on the daily par curve",
     "https://yourbestsavings.com/treasury-yields/"),
    ("FRED (St. Louis Fed)", "T10Y2Y - 10-year minus 2-year Treasury constant maturity: 0.33 on 20 Oct 2026, 0.32 on 21 Oct",
     "https://fred.stlouisfed.org/series/T10Y2Y"),
    ("uitf.com.ph", "ATRAM Peso Money Market Fund (A Unit Class) - trust fee structure 0.50% p.a.",
     "https://www.uitf.com.ph/daily_navpu_details.php?fund_id=203"),
    ("GCash Help Centre", "GFunds fees - ATRAM Peso Money Market Fund trust fee 0.50%",
     "https://help.gcash.com/hc/en-us/articles/30841717008025-GFunds-fees"),
    ("Seedbox / ATRAM Trust", "ATRAM Peso Money Market Fund KIIDS - trustee 0.57%, other 0.01% of average daily NAV",
     "https://file.seedbox.ph/ATRAM_Peso_Money_Market_Fund_KIIDS.pdf"),
    ("Fidelity International", "Global Technology Fund Y-Acc-USD factsheet, 30 Jun 2026 - OCF 1.04% (30.04.25), AMC 0.80%",
     "https://www.fidelityinternational.com/FILPS/Documents/en/current/mf.en.gb.LU1560650563.pdf"),
    ("BusinessWorld", "Inflation risks to keep BSP hawkish - poll: 20 of 22 analysts expect +25bp to 5.25% on 22 Oct, two +50bp, 20 Oct 2026",
     "https://bworldonline.com/top-stories/2026/10/20/788200/inflation-risks-to-keep-bsp-hawkish/"),
    # ---- added 2026-10-22, the 21-22 Oct roll ----
    ("AP via KVUE", "How major US stock indexes fared Wednesday 10/21/2026 - S&P 7757.17 (+0.6%), Nasdaq +1.1%, Dow +0.7%",
     "https://www.kvue.com/article/syndication/associatedpress/how-major-us-stock-indexes-fared-wednesday-10212026/616-7b5f5e36-88da-4c68-b7a1-1ed8d1bc2cb5"),
    ("CNBC", "S&P 500 notches 3-day win streak, Nasdaq jumps 1% as SpaceX and Tesla rally - S&P 7757.17, Nasdaq 26702.86, Dow 52856.09 (+360.21), 21 Oct 2026",
     "https://www.cnbc.com/2026/10/20/stock-market-today-live-updates.html"),
    ("Bloomberg", "Cboe Volatility Index (VIX:IND) - 16.68, -0.63 (-3.64%) at the 21 Oct 2026 close",
     "https://www.bloomberg.com/quote/VIX:IND"),
    ("PC Thematic", "Daily market report, 21 Oct 2026 - VIX cooled to 16.68 from 17.31",
     "https://pcthematic.substack.com/p/daily-market-report-october-21-2026"),
    ("CNBC", "Oil price today: WTI, Brent rise on Middle East worries - Brent +3 cents to $108.82, WTI -67 cents to $97.15, 21 Oct 2026",
     "https://www.cnbc.com/2026/10/21/oil-price-today-wti-brent-rise-on-middle-east-worries.html"),
    ("FN News / Reuters", "Oil prices end mixed; Brent at $108.82, WTI at $97.15, 21 Oct 2026",
     "https://en.fnnews.com/news/202610220446553314"),
    ("BusinessWorld", "Philippine central bank hikes key rate by 50 bps amid inflation woes - RRP 5.50%, 22 Oct 2026",
     "https://bworldonline.com/top-stories/2026/10/22/788621/philippine-central-bank-hikes-key-rate-by-50-bps-amid-inflation-woes/"),
    ("Rappler", "Bangko Sentral raises interest rates to 5.50% as inflation, peso woes mount - overnight deposit 5.00%, lending 6.00%, 22 Oct 2026",
     "https://www.rappler.com/business/bangko-sentral-pilipinas-monetary-policy-interest-rates-october-2026/"),
    ("Daily Tribune", "BSP delivers jumbo 50-basis-point rate hike - peso at P63.52 shortly after the announcement, 22 Oct 2026",
     "https://tribune.net.ph/2026/10/22/bsp-delivers-jumbo-50-basis-point-rate-hike"),
    ("Inquirer", "PSEi snaps 5-day rally on profit-taking - -41.78 (-0.72%) to 5779.73; peso record low P63.545, 22 Oct 2026",
     "https://business.inquirer.net/617332/psei-snaps-5-day-rally-on-profit-taking"),
    ("BusinessWorld", "Peso closes at record low for fourth straight day - P63.52, 15.9 centavos weaker, 22 Oct 2026",
     "https://bworldonline.com/top-stories/2026/10/22/788742/peso-closes-at-record-low-for-fourth-straight-day/"),
    ("Manila Bulletin", "Peso falls to historic low of 63.52 despite surprise BSP rate hike - opened 63.31, range 63.30-63.545, 22 Oct 2026",
     "https://mb.com.ph/2026/10/22/peso-falls-to-historic-low-of-6352-despite-surprise-bsp-rate-hike"),
    ("Manila Times", "Peso sinks to another record low, P63.52, 22 Oct 2026",
     "https://www.manilatimes.net/2026/10/22/business/peso-sinks-to-another-record-low-p6352/2451534"),
    ("Aju Press", "KOSPI wipes out prior gains as BOK pauses rate hikes - -201.89 (-3.52%); SK Hynix -5.48%, Samsung -4.02%, 22 Oct 2026",
     "https://www.ajupress.com/view/20261022153542644"),
    ("TradingKey", "Japan and South Korea stocks slump; KOSPI -3.52% to 5533.77, Nikkei -2.65% to 62907.84, 22 Oct 2026",
     "https://www.tradingkey.com/analysis/stocks/more/262231586-japan-south-korea-stocks-kospi-nikkei-softbank-sk-hynix-samsung-kioxia-tradingkey"),
    ("FXStreet", "US Dollar Index falls to near 101.50 due to Fed rate pause bets - CME FedWatch ~84% hold for October, 90% for a December hike, 22 Oct 2026",
     "https://www.fxstreet.com/news/united-states-dollar-index-falls-to-near-10150-due-to-fed-rate-pause-bets-202610220912"),
    ("NewsNation / Reuters", "US orders diplomats to leave Saudi Arabia after Houthi strikes - Dammam airport attack kills one, injures eight, 22 Oct 2026",
     "https://www.newsnationnow.com/world/us-orders-diplomats-leave-saudi-arabia/"),
    ("CNBC", "US pulls diplomats from Saudi Arabia as it reportedly readies Iran strikes after midterms (New York Times), 22 Oct 2026",
     "https://www.cnbc.com/2026/10/22/us-iran-trump-hormuz-.html"),
    ("ThePrint / Reuters", "US orders diplomats to depart Saudi Arabia amid Houthi strikes; drone on an Aramco field kills two, 22 Oct 2026",
     "https://theprint.in/world/us-orders-diplomats-to-depart-saudi-arabia-amid-houthi-strikes-1-dead-in-airport-attack/3078403/"),
    ("Nation Thailand", "Brent rises to US$110.11 a barrel on 22 Oct as US orders some diplomats out of Saudi Arabia",
     "https://www.nationthailand.com/news/world/40072588"),
    ("Endowus", "Fidelity Global Dividend Fund (LU0605515963, Y-Acc-USD) - fund fees 1.04% p.a.",
     "https://endowus.com/investment-funds-list/fidelity-global-dividend-fund-LU0605515963"),
    # ---- added 2026-10-22, the 22-fund list searched (v63) ----
    ("ATRAM Trust", "ATRAM Global Health Care Feeder Fund (ATRGHCP) - trust fee incl. distribution fee 1.50% p.a.",
     "https://www.atram.com.ph/funds/uitf-funds/details?fund=ATRGHCP"),
    ("uitf.com.ph", "ATRAM Global Health Care Feeder Fund - daily NAVpu, trust fee 1.50% p.a., benchmark MSCI ACWI Health Care",
     "https://www.uitf.com.ph/daily_navpu_details.php?fund_id=435"),
    ("investa.ph / ATRAM", "ATRAM Global Health Care Feeder Fund fact sheet - target Fidelity Funds Global Healthcare, TER 1.05%",
     "https://storage.investa.ph/files/Fund/52/PDF/52_FundFactSheet_1763395696.pdf"),
    ("Fidelity International", "Fidelity Funds - Global Healthcare Fund factsheet, 31 Aug 2026 (Singapore) - Eli Lilly 8.7%, AbbVie 7.4%, 41 positions",
     "https://www.fidelityinternational.com/legal/documents/SG-en/hffs.SG-en.SG.G-HCR.pdf"),
    ("uitf.com.ph", "ATRAM Global Infra Equity Feeder Fund (A PHP units) - trust fee 1.50% p.a.",
     "https://www.uitf.com.ph/daily_navpu_details.php?fund_id=434"),
    ("Seedbox / ATRAM", "ATRAM Global Infra Equity Feeder Fund fact sheet - target changed to HSBC GIF Global Infrastructure Equity, March 2025; TER 0.80%",
     "https://file.seedbox.ph/ATRAM_GLOBAL_INFRA_EQUITY_FEEDER_FUND_KIIDS.pdf"),
    ("ATRAM Trust", "ATRAM Global Equity Opportunity Feeder Fund (PHP unit class) - trust fee 1.50% p.a.",
     "https://www.atram.com.ph/funds/uitf-funds/details?fund=14UF05P"),
    ("Seedbox / ATRAM", "ATRAM Global Equity Opportunity Feeder Fund KIID - target Allianz Thematica since April 2021; target TER 1.00% (31 Mar 2026)",
     "https://file.seedbox.ph/ATRAM_GLOBAL_EQUITY_OPPORTUNITY_FEEDER_FUND_KIIDS.pdf"),
    ("Citywire", "Allianz Global Investors Fund - Allianz Thematica AT USD - ongoing charge 1.95%",
     "https://citywire.com/selector/fund/allianz-global-investors-fund-allianz-thematica/c579592"),
    ("ATRAM Trust", "ATRAM Global Consumer Trends Feeder Fund - trust fee 1.50% p.a.",
     "https://www.atram.com.ph/funds/uitf-funds/details?fund=20UF19P"),
    ("investa.ph / ATRAM", "ATRAM Global Consumer Trends Feeder Fund fact sheet - target Invesco Global Consumer Trends, TER 0.97%",
     "https://storage.investa.ph/files/Fund/50/PDF/50_FundFactSheet_1763395688.pdf"),
    ("ATRAM Trust", "ATRAM Asian Multi-Asset Income Feeder Fund (ATRAMIP) - trust fee 1.50% p.a.; benchmark 50% MSCI AC APxJ / 50% Bloomberg EM Asia",
     "https://www.atram.com.ph/funds/uitf-funds/details?fund=ATRAMIP"),
    ("BusinessWorld", "ATRAM Trust launches new fund - the Asian multi-asset income feeder, target Schroder Asian Asset Income Fund, Sep 2022",
     "https://bworldonline.com/banking-finance/2022/09/06/472618/atram-trust-launches-new-fund/"),
    ("Schroders", "Schroder Asian Asset Income Fund - Product Key Facts (class A USD ongoing charges)",
     "https://api.schroders.com/document-store/HKUT-Asian-Asset-Income-Fund-PKFSAPAC-HKEN.pdf"),
    ("uitf.com.ph", "ATRAM Global Allocation Feeder Fund (PHP unit class) - trust fee 1.20% p.a.",
     "https://www.uitf.com.ph/home/daily_navpu_details.php?fund_id=433&bank_id=31"),
    ("investa.ph / ATRAM", "ATRAM Global Allocation Feeder Fund fact sheet - target BGF Global Allocation A2 USD, TER 1.13%",
     "https://storage.investa.ph/files/Fund/40/PDF/40_FundFactSheet_1767270656.pdf"),
    ("J.P. Morgan Asset Management", "2027 Long-Term Capital Market Assumptions press release - global aggregate bonds 5.3%, US investment-grade credit 6.1%, US large cap 7.5%",
     "https://am.jpmorgan.com/us/en/asset-management/adv/about-us/media/press-releases/jp-morgan-releases-2027-long-term-capital-market-assumptions/"),
    ("PortfoliosLab", "iShares Global Healthcare ETF (IXJ) - monthly total returns, Oct 2025 - Sep 2026",
     "https://portfolioslab.com/symbol/IXJ"),
    ("BlackRock", "Healthcare making a comeback? - global health care up more than 10% in Q4 2025",
     "https://www.blackrock.com/au/insights/ishares/2026-comeback-year-for-healthcare"),
    ("Aristotle Capital", "4Q 2025 commentary - MSCI ACWI +3.29% (net, USD) in the quarter",
     "https://www.aristotlecap.com/wp-content/uploads/2026/01/GE-Adv-Commentary-2025-12.pdf"),
    ("Aristotle Capital", "1Q 2026 commentary - MSCI ACWI -3.20% in the quarter",
     "https://www.aristotlecap.com/wp-content/uploads/2026/04/GE-Adv-Commentary-2026_03.pdf"),
    ("Aristotle Capital", "2Q 2026 commentary - MSCI ACWI +14.93% in the quarter, 11.25% year to date",
     "https://www.aristotlecap.com/wp-content/uploads/2026/07/GE-Adv-Commentary-2026_06.pdf"),
    ("Maseco", "Q3 2026 global market review - MSCI ACWI +1.6% in the quarter, 13.0% year to date",
     "https://masecoasia.com/q3-2026-global-market-review-and-perspective/"),
    ("Goldstone Financial Group", "Q3 2026 market recap - MSCI ACWI +1.6% in Q3, +13.0% year to date",
     "https://www.goldstonefinancialgroup.com/q3-2026-market-review/"),
    ("iShares", "iShares Global Healthcare ETF (IXJ) - NAV returns to 30 Sep 2026: 1 month -1.96%, YTD 5.93%, 1 year 16.81%",
     "https://www.ishares.com/us/products/239744/ishares-global-healthcare-etf"),
    ("uitf.com.ph", "ATRAM Global Bond Income Feeder Fund - trust fee 0.90% p.a. (held out: one listing)",
     "https://www.uitf.com.ph/daily_navpu_details.php?fund_id=364"),
    ("uitf.com.ph", "ATRAM US Equity Opportunity Feeder Fund (USD unit class) - trust fee 1.20% p.a. (held out: stale listing)",
     "https://www.uitf.com.ph/daily_navpu_details.php?fund_id=260"),
    ("Yahoo Finance", "CBOE Volatility Index (^VIX) - 16.91, -0.61 (-3.48%) at the 28 Oct 2026 close",
     "https://finance.yahoo.com/quote/%5EVIX/"),
    ("CNBC", "CBOE Market Volatility Index (.VIX) - last 16.91, previous close 17.52, 28 Oct 2026",
     "https://www.cnbc.com/quotes/.VIX"),
    ("PC Thematic", "Daily market report, 28 Oct 2026 - VIX cooled to 16.91 from 17.52",
     "https://pcthematic.substack.com/p/daily-market-report-october-28-2026"),
    ("Associated Press via WTOP", "How major US stock indexes fared Thursday 10/29/2026 - S&P -23.59 to 7720.39, Nasdaq -365.13 to 26184.72, Dow -132.54 to 52342.56",
     "https://wtop.com/national/2026/10/how-major-us-stock-indexes-fared-thursday-10-29-2026/"),
    ("TheStreet", "Stock market today, 29 Oct 2026 - S&P 500 falls after Alphabet and Microsoft issue divergent earnings",
     "https://www.thestreet.com/stock-market-today/stock-market-today-dow-jones-sp-500-nasdaq-updates-oct-29-2026"),
    ("Yahoo Finance", "Alphabet loses $475 billion in market value, the biggest drop in its history, 29 Oct 2026",
     "https://finance.yahoo.com/markets/article/alphabet-heads-for-a-500-billion-drop-in-market-value-the-biggest-in-its-history-134824763.html"),
    ("Bureau of Economic Analysis", "GDP (advance estimate), third quarter 2026 - real GDP +3.4% at an annual rate, 29 Oct 2026",
     "https://www.bea.gov/news/2026/gdp-advance-estimate-3rd-quarter-2026"),
    ("NAW", "First estimate: 3Q US GDP growth accelerated to 3.4%, from 2.2%",
     "https://www.naw.org/mdm/news/first-estimate-3q-u-s-gdp-growth-accelerated-to-3-4/"),
    ("Bureau of Economic Analysis", "Personal income and outlays, September 2026 - PCE prices +0.5% m/m, 3.6% y/y; core +0.3%, 3.1%",
     "https://www.bea.gov/news/2026/personal-income-and-outlays-september-2026"),
    ("Xinhua", "US inflation accelerates in September on higher energy prices - saving rate 3.8%, 30 Oct 2026",
     "https://english.news.cn/20261030/380498ce182143719fe19189f4065b3d/c.html"),
    ("Fox Business", "Fed's preferred inflation gauge rose in September as third-quarter GDP beats expectations - FedWatch 79.6% for a December hike",
     "https://www.foxbusiness.com/economy/september-2026-pce-inflation"),
    ("IBTimes", "September's inflation was in line with expectations; odds of a rate hike dropped but remain high - 79.6% from 84.2%",
     "https://www.ibtimes.com/septembers-inflation-was-line-expectations-odds-rate-hike-dropped-remain-high-3809143"),
    ("European Central Bank", "Monetary policy decisions, 29 Oct 2026 - the three key rates unchanged, deposit facility 2.50%",
     "https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp261029~9a493adf17.en.html"),
    ("Euronews", "ECB holds rates at 2.5% as Lagarde announces early exit, 29 Oct 2026",
     "https://www.euronews.com/2026/10/29/ecb-holds-rates-at-25-as-lagarde-announces-early-exit-with-inflation-near-double-the-targe"),
    ("FXStreet / ING", "Japanese yen: weakness to persist despite a hawkish BoJ - held at 1.25%, 8-1, Takata for 1.5%, 30 Oct 2026",
     "https://www.fxstreet.com/news/japanese-yen-weakness-against-us-dollar-to-persist-despite-hawkish-boj-ing-202610301248"),
    ("Maaal", "Bank of Japan keeps interest rates unchanged and declares its inflation target met, 30 Oct 2026",
     "https://maaal.com/en/news/details/bank-of-japan-keeps-inter-b/"),
    ("Nikkei Indexes", "Nikkei Stock Average - 29 Oct 2026 close 64,659.47, +705.28 (+1.10%)",
     "https://indexes.nikkei.co.jp/en/nkave/index/profile"),
    ("News on Japan", "Japan stocks rise for a third day as the Nikkei reclaims 64,000 - 64,659.47, 29 Oct 2026",
     "https://newsonjapan.com/article/151176.php"),
    ("News on Japan", "Japan stocks plunge 1,369 points as the AI selloff hits Tokyo - 63,290.11, 30 Oct 2026",
     "https://newsonjapan.com/article/151189.php"),
    ("Japan Daily Sun", "Nikkei 225 drops 1,369.36 points (-2.12%) to 63,290.11 amid the AI selloff, 30 Oct 2026",
     "https://japandailysun.com/business/japan-stocks-plunge-1369-points-as-ai-selloff-hits-tokyo-financial-markets"),
    ("Seoul Economic Daily", "KOSPI falls 1.24% to close at 5,937.66, 29 Oct 2026",
     "https://en.sedaily.com/finance/2026/10/29/kospi-falls-124-percent-to-close-at-593766"),
    ("SBS", "KOSPI falls 1.2% below 6,000 again; Samsung Electronics plunges over 4%, 29 Oct 2026",
     "https://news.sbs.co.kr/english/article.do?news_id=N1008821474"),
    ("Seoul Economic Daily", "KOSPI closes down 3.48% at 5,730.74, 30 Oct 2026",
     "https://en.sedaily.com/finance/2026/10/30/kospi-closes-down-348-percent-at-573074"),
    ("Korea Times", "KOSPI falls 3.48% as US tech earnings fuel AI investment concerns, 30 Oct 2026",
     "https://www.koreatimes.co.kr/economy/others/20261030/kospi-falls-348-as-us-tech-earnings-fuel-ai-investment-concerns"),
    ("Philippine Daily Inquirer", "PSEi rebounds to 5,705 on bargain hunting, up 52.03 (0.92%), 29 Oct 2026",
     "https://business.inquirer.net/618703/psei-rebounds-to-5705-on-bargain-hunting"),
    ("BusinessWorld", "Philippine stocks rise as peso extends recovery - PSEi 5,705.58, 29 Oct 2026",
     "https://bworldonline.com/stock-market/2026/10/29/790161/philippine-stocks-rise-as-peso-extends-recovery/"),
    ("BusinessWorld", "Peso strengthens further as Fed pauses rate hike cycle - P63.85 from P64.025, 29 Oct 2026",
     "https://bworldonline.com/banking-finance/2026/10/29/790244/peso-strengthens-further-as-fed-pauses-rate-hike-cycle/"),
    ("GMA News", "Peso rebounds to P63.85:$1 after two days above the 64 level, 29 Oct 2026",
     "https://www.gmanetwork.com/news/money/economy/1007622/peso-rebounds-to-p63-85-1-after-two-days-above-64-level/story/"),
    ("AD HOC News", "VIX closes at 17.20 after a volatile session, up 0.29 (1.71%), 29 Oct 2026",
     "https://www.ad-hoc-news.de/boerse/news/marktberichte/vix-closes-at-17-20-after-volatile-session/70430489"),
    ("PC Thematic", "Daily market report, 29 Oct 2026 - VIX ticked up to 17.20 from 16.91",
     "https://pcthematic.substack.com/p/daily-market-report-october-29-2026"),
    ("JOLT Journal", "Treasury yields on 29 Oct 2026: 10-year at 4.98% on the par curve, from 5.05% on the 28th",
     "https://www.joltjournal.com/finance/treasury-yields-october-29-2026/"),
    ("CNBC", "Oil price today, 29 Oct 2026 - Brent fell 44 cents to close at $114.88",
     "https://www.cnbc.com/2026/10/29/oil-price-today-wti-brent.html"),
    ("Gulf Today / Reuters", "Oil prices rise, Brent reaches $116.08 - December +$1.20 at 0323 GMT, 30 Oct 2026",
     "https://www.gulftoday.ae/business/2026/10/30/oil-prices-rise-brent-reaches-11608-pb"),
    ("CNBC", "Iran claims four tankers struck mines in Hormuz as strike fears grow after the midterms, 30 Oct 2026",
     "https://www.cnbc.com/2026/10/30/iran-trump-hormuz-oil-middle-east-.html"),
    ("Las Vegas Review-Journal / AP", "Mideast developments: Iran says 3 oil tankers struck mines; Central Command calls the claim false, 30 Oct 2026",
     "https://www.reviewjournal.com/news/politics-and-government/3-oil-tankers-struck-mines-in-the-strait-of-hormuz-iran-says-3906664/"),
    ("Gulf News", "Hormuz tensions rise as Iran reports tanker incidents; UKMTO confirms an incident off Oman, 30 Oct 2026",
     "https://gulfnews.com/world/mena/middle-east-war-iran-claims-tankers-hit-mines-in-strait-of-hormuz-ukmto-confirms-strike-off-oman-fired-us-general-reportedly-admitted-iran-leaks-1.500729137"),
    ("Finance Calendar", "US Employment Situation (non-farm payrolls), October 2026 - release 6 Nov 2026",
     "https://www.financecalendar.com/event/us-employment-situation-non-farm-payrolls-october-2026/"),
]

# ----------------------------------------------------------------------------
# 9. OUTPUT
# ----------------------------------------------------------------------------

def payload():
    return {
        "as_of": AS_OF, "macro": MACRO, "vol_ts": VOL_TS,
        # Named for the constant it publishes, not for a horizon. It was
        # "sp_vol_5y" until 2026-09-10 and had held the TEN-year implied vol
        # since the mandate lengthened - a field whose name contradicted its
        # contents is exactly how a correct number gets used wrongly.
        "sp_vol_lt": SP_VOL_LT,
        "regions": {k: {**v, "summary": SUMMARY[k]} for k, v in REGIONS.items()},
        "hz_weights": HZ_W,
        "vol_channel": {"blend": round(VOL_BLEND, 2), "spot": MACRO["vix_spot"],
                        "longrun": MACRO["vix_longrun"], "ramp_ref": VOL_RAMP_REF,
                        "quote_date": VIX_QUOTE_DATE,
                        "latest": MACRO["vix_latest"],
                        "latest_date": MACRO["vix_latest_date"],
                        "latest_gap": round(MACRO["vix_latest"] - MACRO["vix_spot"], 2),
                        "ramp": round(VOL_RAMP, 2), "sens": VOL_SENS,
                        "ramp_10y": VOL_RAMP_10, "basis": "forward",
                        "kappa": KAPPA, "vrp": MACRO["variance_risk_premium"],
                        # How far the latest close has moved from the curve's own
                        # spot. Past 20% the strip is flagged on the page as
                        # overtaken by the market (added 2026-10-17, when the VIX
                        # closed 28.8% above the 5 Oct strip's spot).
                        "spot_move_pct": round((MACRO["vix_latest"] / MACRO["vix_spot"] - 1) * 100, 1),
                        "overtaken": abs(MACRO["vix_latest"] / MACRO["vix_spot"] - 1)
                                     > STRIP_OVERTAKEN_PCT / 100,
                        "overtaken_pct": STRIP_OVERTAKEN_PCT,
                        "vix3m_bound_pct": VIX3M_BOUND_PCT,
                        # The independent market read, and the measured cost of the
                        # strip's age. Published so the page can state the gap
                        # rather than the reader having to infer it.
                        "vix3m": MACRO["vix3m"], "vix3m_date": MACRO["vix3m_date"],
                        "vix3m_model": round(VIX3M_MODEL, 2),
                        "vix3m_resid": VIX3M_RESID,
                        "vix3m_prev_strip_resid": VIX3M_PREV_RESID,
                        "prev_strip_date": MACRO["vix_futs_prev_date"],
                        "strip_age_d": (_dt.date.fromisoformat(REVIEW_DATE)
                                        - _dt.date.fromisoformat(VIX_QUOTE_DATE)).days},
        # Each driver is RESEARCHED on 1-10 (score_10) - the granularity the evidence
        # supports, and the scale every note below is written against - and REPORTED on
        # 1-5 (score) by the same endpoint-preserving rescale used for the gauge and the
        # regional rankings. Since to5() is affine and the weights sum to 1, the weighted
        # composite of the REPORTED scores is exactly the headline gauge; the check block
        # asserts that rather than assuming it.
        "drivers": [{"name": n, "weight": w,
                     "score": to5(s), "score_10": s, "note": t, "summary": SUMMARY[n],
                     # the 3/5/10-year path on the research scale, its reasoning, and
                     # its ten-year average - the reading the rates and energy tilts take
                     "path": {h: DRIVER_PATH[n][h] for h in HZ_KEYS},
                     "path_5": {h: to5(DRIVER_PATH[n][h]) for h in HZ_KEYS},
                     "blend_5": round(sum(to5(DRIVER_PATH[n][h]) * w for h, w in HZ_W.items()), 2),
                     "path_why": DRIVER_PATH[n]["why"], "blend_10": DRIVER_BLEND_10[n]}
                    for n, w, s, t in DRIVERS],
        "driver_scale": {"research_max": 10, "reported_max": 5,
                         "neutral": NEUTRAL_5, "neutral_10": 5.5},
        "gauge": GAUGE, "gauge_10": GAUGE_10, "gauge_neutral": GAUGE_NEUTRAL,
        "gauge_path": GAUGE_PATH, "gauge_path_10": GAUGE_PATH_10, "gauge_blend": GAUGE_BLEND,
        "funds": F, "corr": CORR, "corr_note": CORR_NOTE,
        "lookthrough": LOOKTHROUGH,
        "acwi_it_mix": ACWI_IT_MIX, "gdiv_mix": GDIV_MIX,
        # The covered-call sleeve's vol factor, published so it is auditable rather
        # than a constant folded into vol_beta.
        "jepq_vol": JEPQ_VOL, "ndx_vol": NDX_VOL, "jepq_beta": JEPQ_BETA,
        "cc_vol_factor": round(JEPQ_VOL / NDX_VOL, 4),
        "fx": {"drift": FX_DRIFT, "vol": FX_VOL, "corr": FX_CORR,
               "ppp_lr": round(FX_PPP_PH_LR - FX_PPP_US_LR, 2),
               "ppp_now": round(MACRO["ph_cpi_sep"] - MACRO["us_cpi_headline"], 2)},
        "vix_quote_date": VIX_QUOTE_DATE,
        "review_date": REVIEW_DATE,
        # Published so the page never has to type them: the regional tilt coefficient
        # and the peso sleeve's real yield were the last two hard-typed figures in the
        # static markup with no payload counterpart. (Audit 2026-09-11.)
        "regional_tilt_per_pt": REGIONAL_TILT_PER_PT,
        # The market-trend channel: every figure from window returns to tilt, on
        # the reader's route, plus the one disputed input re-run on its alternative.
        "trend": {"end": TREND_END, "tilt_per_pt": TREND_TILT_PER_PT,
                  "vol_basis": round(SP_VOL_LT - MACRO["variance_risk_premium"], 2),
                  "vrp": MACRO["variance_risk_premium"],
                  "anchor": TREND_ANCHOR, "quarters": list(TREND_Q),
                  "horizons": [{"label": l, "quarters": n, "years": y} for l, n, y in TREND_H],
                  "long": [{"label": l, "years": y} for l, y in TREND_LONG],
                  "reversal": TREND_REVERSAL, "long_end": TREND_LONG_END,
                  "views": list(TREND_VIEWS), "w": TREND_W,
                  "mom_years": list(TREND_MOM_YEARS), "rev_years": list(TREND_REV_YEARS),
                  "sleeves": TREND, "alt": TREND_ALT, "alt_built": TREND_ALT_BUILT},
        # The calibration record for the driver transmission, published so the
        # page-level and independent harnesses can re-derive every rates and energy
        # tilt from the driver scores without importing this file.
        "driver_tilt_cal": {**TILT_CAL, "neutral_10": DRIVER_NEUTRAL_10,
                            "reading": "blend_10",
                            "monetary_blend": MON_BLEND, "geopolitics_blend": GEO_BLEND,
                            "rates_scale": round(RATES_SCALE, 6),
                            "energy_scale": round(ENERGY_SCALE, 6),
                            "rates_scale_10y": round(RATES_SCALE_10, 6),
                            "energy_scale_10y": round(ENERGY_SCALE_10, 6)},
        # On the LATEST print. It read August's 6.1% for two days after September's
        # 7.2% was out, and the page typed the month - "against August inflation".
        # (The PPP differential above stays on August: it needs the US figure for
        # the same month, and US September CPI is not out.)
        "real_yield": {
            "cpi": MACRO["ph_cpi_sep"], "month": "September",
            "t91": round(MACRO["ph_tbill_91"] - MACRO["ph_cpi_sep"], 2),
            "t364": round(MACRO["ph_tbill_364"] - MACRO["ph_cpi_sep"], 2),
        },
        "catalysts": [{"date": d, "what": w, "why": y} for d, w, y in CATALYSTS],
        "postponed": [{"what": w, "why": y} for w, y in POSTPONED],
        "dd_model": {"k": DD_K, "mu_coef": DD_MU,
                     "calib": {k_: list(v_) for k_, v_ in DD_CALIB.items()},
                     "mm_shock_bp": MM_SHOCK_BP, "mm_duration_y": MM_DURATION_Y,
                     "horizon_y": HORIZON_Y, "calib_y": DD_CALIB_Y,
                     # 4dp left a 2.5e-04 error in every drawdown - enough to
                     # flip portfolios sitting on the budget boundary.
                     "horizon_scalar": round(DD_HORIZON_SCALAR, 9),
                     # 5dp, not 3. At 3dp the published k is LOSSY enough to move a
                     # reconstructed scenario drawdown by a rounding step: the AI
                     # capex row reproduces as -42.34 from the exact k and -42.35
                     # from 1.618, which print as -42.3 and -42.4. The page shows it
                     # formatted; the payload should not throw the precision away.
                     "baseline_k": round(port_k(BASELINE_W), 5),
                     # the two portfolios the page shows (v76)
                     "a_k": round(port_k(PA_W, UNIV), 5), "b_k": round(port_k(PB_W, UNIV), 5),
                     "c_k": round(port_k(PC_W, UNIV), 5),
                     "note": "1.65 is the calibration anchor, not the coefficient every sleeve "
                             "uses. Each fund carries a declared adjustment for the shape of its "
                             "own left tail; the portfolio coefficient is the weighted average "
                             "across the equity sleeves. The whole quantity is then scaled by "
                             "sqrt(horizon / calibration window), because expected maximum "
                             "drawdown grows with the square root of the horizon - the -20% and "
                             "-33% anchors are rolling FIVE-year medians and cannot simply be "
                             "relabelled for a longer mandate."},
        # The drawdown budget's reference (off the page): DD_CAP is its macro drawdown
        # less DD_BUDGET_IMPROVEMENT, so a reader can re-derive the budget from it.
        "baseline": {"weights": [round(x*100) for x in BASELINE_W],
                     "base": BASE, "under_macro": BASE_UNDER_MACRO,
                     "scenarios": run_scenarios(BASELINE_W, "net_macro")},
        "portfolio_a": {"weights": [round(x * 100) for x in PA_W], "ids": UNIV_IDS,
                        "macro": PA, "base": PA_BASE, "ten": PA_10, "column": "net_10y",
                        "band_n": PA_BAND_N, "n_feasible": UNIV_N_FEAS["a"],
                        "is_review_pick": PA_IS_REVIEW, "review_outside": PA_REVIEW_OUTSIDE,
                        "scenarios": run_scenarios(PA_W, "net_10y", UNIV),   # its own horizon (v80)
                        "dd_cap": round(DD_CAP, 2),
                        # inside the budget on the 3/5/10-year view AS COMPUTED AND AS SHOWN
                        # (v77: the printed figure alone called A inside at -25.0% while its true
                        # drawdown there was 25.0035%)
                        "in_budget": abs(PA["maxdd"]) <= DD_CAP + 1e-9
                                     and abs(port_dd(PA_W, "net_macro", UNIV)) <= DD_CAP + 1e-9,
                        "review": {k[10:]: MACRO[k] for k in MACRO if k.startswith("pa_review_")}},
        "dd_budget": {"cap": DD_CAP, "source": "band", "base": DD_BUDGET_OWNER, "base_source": "owner",
                      "date": DD_BUDGET_OWNER_DATE, "band_date": DD_BUDGET_BAND_DATE,
                      "derived_ref": round(DD_CAP_DERIVED, 2), "improvement": DD_BUDGET_IMPROVEMENT},
        "dd_gauge": {"value": DDG_VALUE, "views": list(DDG_VIEWS), "w": DDG_W,
                     "parts": DDG_PARTS, "vol_step": DDG_VOL_STEP, "longrun": MACRO["vix_longrun"],
                     "bands": [{"lo": b[0], "hi": min(b[1], 5.0), "cap": b[2], "action": b[3]}
                               for b in DDG_BANDS],
                     "band": {"lo": DDG_BAND[0], "hi": min(DDG_BAND[1], 5.0), "cap": DDG_BAND[2],
                              "action": DDG_BAND[3]},
                     "guards": DDG_GUARDS, "recommended_cap": DDG_RECOMMENDED,
                     "blocked_by": DDG_BLOCKED_BY, "reviews": DDG_REVIEWS,
                     "alt": {f"{c:.0f}": v for c, v in ddg_alt().items()}},
        "universe": {"limits": {"max_funds": UNIV_MAX_FUNDS, "max_w": round(UNIV_MAX_W * 100),
                           "min_cash": round(UNIV_MIN_CASH * 100)},
                "n_total": UNIV_N_TOTAL,
                "n_list": len(UNIV_IDS) + len(MACRO["list22_held_out"]),
                "held_out": [{"short": a, "why": b} for a, b in MACRO["list22_held_out"]],
                "tie_pp": PIN_TIE_PP, "frontier": UNIV_FRONTIER,
                "best_ratio": {"weights": UNIV_BEST_RATIO[1]["weights"], **UNIV_BEST_RATIO[1]},
                "what_if": WHAT_IF_UNIV},
        "portfolio_b": {"weights": [round(x * 100) for x in PB_W], "ids": UNIV_IDS,
                        "column": "net_macro", "band_n": PB_BAND_N,
                        "n_feasible": UNIV_N_FEAS["b"],
                        "shorts": [f["short"] for f in UNIV[1]],
                        "funds": F_ADD, "macro": PB, "base": PB_BASE, "ten": PB_10,
                        "scenarios": run_scenarios(PB_W, "net_macro", UNIV),
                        "corr": CORR_U, "corr_note": CORR_U_NOTE,
                        # the factor model behind every pair outside the typed block, so the
                        # audit rebuilds those pairs rather than reading them
                        "factors": {"names": list(FACTORS), "loadings": FACTOR_LOADINGS,
                                    "fx_corr": FX_CORR, "fx_vol": FX_VOL, "typed_block": 5},
                        "dd_cap": round(DD_CAP, 2),
                        "in_budget": abs(PB["maxdd"]) <= DD_CAP + 1e-9
                                     and abs(port_dd(PB_W, "net_macro", UNIV)) <= DD_CAP + 1e-9,
                        "review": {k[10:]: MACRO[k] for k in MACRO if k.startswith("pd_review_")}},
        # PORTFOLIO C (restored v82): Nasdaq Equity Income held at 50%, the rest by the same
        # rule on the 3/5/10-year view, inside the same band budget.
        "portfolio_c": {"weights": [round(x * 100) for x in PC_W], "ids": UNIV_IDS,
                        "macro": PC, "base": PC_BASE, "ten": PC_10, "column": "net_macro",
                        "fund": "ATRQIAP", "pin_pct": round(PIN_W * 100),
                        "band_n": PC_BAND_N, "n_feasible": UNIV_N_FEAS["c"], "n_total": UNIV_N_PINNED,
                        "scenarios": run_scenarios(PC_W, "net_macro", UNIV),
                        "dd_cap": round(DD_CAP, 2),
                        "in_budget": abs(PC["maxdd"]) <= DD_CAP + 1e-9
                                     and abs(port_dd(PC_W, "net_macro", UNIV)) <= DD_CAP + 1e-9},
        "sources": [{"org": o, "what": w, "url": u} for o, w, u in SOURCES],
    }

def report():
    p = payload()
    L = []
    A = L.append
    A(f"ATRAM PORTFOLIO ENGINE - audit report  (as of {AS_OF})")
    A("=" * 78)
    A("\n[1] VOLATILITY TERM STRUCTURE (forward-variance integration of the VIX complex)")
    A(f"    spot VIX {MACRO['vix_spot']}  |  front fut ({MACRO['vix_futs'][0][0]}) {MACRO['vix_fut_sep']}  |  "
      f"Dec fut {MACRO['vix_fut_dec']}  |  long-run anchor {MACRO['vix_longrun']}")
    A(f"    {'H':<5}{'implied':>10}{'forward':>10}{'realised':>10}{'1sd move':>11}{'2sd move':>11}")
    for v in p["vol_ts"]:
        A(f"    {v['label']:<5}{v['implied']:>9.2f}%{v['forward']:>9.2f}%{v['realised']:>9.2f}%"
          f"{v['move_1sd']:>10.2f}%{v['move_2sd']:>10.2f}%")
    A(f"    forward-vol blend {p['vol_channel']['blend']}  ramp {p['vol_channel']['ramp']:+.2f}"
      f"  (10-year view: years 6-10 ramp {p['vol_channel']['ramp_10y']:+.2f})")
    A("\n[2] REGIONAL MACRO-DRIVER RANKING (1-5, neutral 3.0)")
    A(f"    {'region':<14}" + "".join(f"{h:>6}" for h in HZ_KEYS) + f"{'blend':>8}")
    for k, v in sorted(p["regions"].items(), key=lambda t: -t[1]["blend"]):
        A(f"    {k:<14}" + "".join(f"{v[h]:>6}" for h in HZ_KEYS) + f"{v['blend']:>8}")
    tr = p["trend"]
    A(f"\n[2b] MARKET TREND (to {tr['end']}; z vs long-run drift and vol; view = 3 + mom share x z(1Y) "
      f"- rev share x {TREND_REVERSAL} z(3Y,5Y): " + ", ".join(f"{h} {TREND_W[h]['mom']}/{TREND_W[h]['rev']}"
                                                             for h in HZ_KEYS) + ")")
    A(f"    {'sleeve':<10}{'1Y':>8}{'3Y pa':>8}{'5Y pa':>8}   {'z 1Y/3Y/5Y':<18}{'z rev':>6}"
      + "".join(f"{h:>7}" for h in TREND_VIEWS) + f"{'blend':>7}{'tilt':>7}")
    for k, v in tr["sleeves"].items():
        A(f"    {k:<10}{v['ret']['1Y']:>7.2f}%{v['ret']['3Y']:>7.2f}%{v['ret']['5Y']:>7.2f}%   "
          f"{'/'.join(f'{v[chr(122)][h]:+.2f}' for h in ('1Y', '3Y', '5Y')):<18}"
          f"{v['z_rev']:>+6.2f}" + "".join(f"{v['score'][h]:>7.2f}" for h in TREND_VIEWS)
          + f"{v['blend']:>7.2f}{v['tilt']:>+7.2f}")
    A("\n[3] BROAD MACRO GAUGE (drivers reported 1-5, researched 1-10)")
    for d in p["drivers"]:
        A(f"    {d['name']:<30} w={d['weight']:.2f}  "
          f"score={d['score']:.2f} / 5   ({d['score_10']:g} / 10)")
    A(f"    {'COMPOSITE (research scale)':<30}            {p['gauge_10']} / 10")
    A(f"    {'HEADLINE GAUGE':<30}            {p['gauge']} / 5"
      f"   (neutral {p['gauge_neutral']})")
    A(f"    {'driver path (1-10)':<30}" + "".join(f"{h:>6}" for h in HZ_KEYS) + f"{'blend':>8}")
    for d in p["drivers"]:
        A(f"    {d['name']:<30}" + "".join(f"{d['path'][h]:>6g}" for h in HZ_KEYS) + f"{d['blend_10']:>8}")
    A(f"    {'GAUGE (1-5)':<30}" + "".join(f"{p['gauge_path'][h]:>6}" for h in HZ_KEYS)
      + f"{p['gauge_blend']:>8}")
    A(f"    rates scale {p['driver_tilt_cal']['rates_scale']:.4f} (Monetary {MON_BLEND} blended), "
      f"energy scale {p['driver_tilt_cal']['energy_scale']:.4f} (Geopolitics {GEO_BLEND} blended)")
    A(f"\n[4] FUNDS - net {HZ_LABEL} CAGR after ALL fees, and expected max drawdown")
    A(f"    {'fund':<22}{'fee':>7}{'gross':>8}{'base':>8}{'tilt':>7}{'macro':>8}"
      f"{'vol':>8}{'DD base':>9}{'DD macro':>10}")
    for f in p["funds"] + p["portfolio_b"]["funds"]:
        A(f"    {f['short']:<22}{f['fee_total']:>6.2f}%{f['gross_php']:>7.2f}%"
          f"{f['net_base']:>7.2f}%{f['tilt_total']:>+7.2f}{f['net_macro']:>7.2f}%"
          f"{f['vol']:>7.2f}%{f['dd_base']:>8.1f}%{f['dd_macro']:>9.1f}%")
    A(f"\n[5] PORTFOLIOS   (order: {' / '.join(p['portfolio_b']['shorts'])})")
    b, o = p["baseline"], p["portfolio_b"]
    A(f"    BASELINE  weights {b['weights']}   (the budget's reference, four original funds; off the page)")
    A(f"      strategic view : CAGR {b['base']['cagr']}%  vol {b['base']['vol']}%  "
      f"maxDD {b['base']['maxdd']}%  ret/DD {b['base']['ret_per_dd']}")
    A(f"      macro view     : CAGR {b['under_macro']['cagr']}%  vol {b['under_macro']['vol']}%  "
      f"maxDD {b['under_macro']['maxdd']}%  ret/DD {b['under_macro']['ret_per_dd']}")
    A(f"    DD budget {o['dd_cap']}% (the band's step from the owner's {DD_BUDGET_OWNER:.0f}% base of {DD_BUDGET_OWNER_DATE}); the derivation it replaced "
      f"|{b['under_macro']['maxdd']}| - {DD_BUDGET_IMPROVEMENT} = {round(DD_CAP_DERIVED, 2)}%; "
      f"budget gauge {DDG_VALUE} -> {DDG_BAND[3]}, recommended {DDG_RECOMMENDED:.0f}%; "
      f"rule: best CAGR in budget, then lowest DD within {p['universe']['tie_pp']:.2f}pp; "
      f"{p['universe']['n_total']} mixes under the limits")
    for lab, key, rule in (("PORTFOLIO A", "portfolio_a", "the 10-year view"), ("PORTFOLIO B", "portfolio_b", "the 3/5/10-year view"),
                           ("PORTFOLIO C", "portfolio_c", "the 3/5/10-year view, Nasdaq Equity Income at 50%")):
        pq = p[key]
        A(f"    {lab} weights {pq['weights']}   (the rule on {rule}; {pq['n_feasible']} feasible, {pq['band_n']} in band)")
        if "ten" in pq:
            A(f"      10-year view   : CAGR {pq['ten']['cagr']}%  vol {pq['ten']['vol']}%  "
              f"maxDD {pq['ten']['maxdd']}%  ret/DD {pq['ten']['ret_per_dd']}")
        A(f"      macro view     : CAGR {pq['macro']['cagr']}%  vol {pq['macro']['vol']}%  "
          f"maxDD {pq['macro']['maxdd']}%  ret/DD {pq['macro']['ret_per_dd']}")
        A(f"      strategic view : CAGR {pq['base']['cagr']}%  vol {pq['base']['vol']}%  "
          f"maxDD {pq['base']['maxdd']}%  ret/DD {pq['base']['ret_per_dd']}")
    for k, v in p["universe"]["what_if"].items():
        A(f"    what-if {k:<17}: B {v['b']['weights']} {v['b']['cagr']}%   "
          f"A {v['a']['cagr']}% / {v['a']['maxdd']}%")
    br = p["universe"]["best_ratio"]
    A(f"    best pure ret/DD  : {br['weights']}  CAGR {br['cagr']}%  "
      f"maxDD {br['maxdd']}%  ratio {br['ret_per_dd']}")
    A("\n[6] SCENARIOS (Portfolio B)")
    for s in o["scenarios"]:
        A(f"    {s['name']:<24} CAGR {s['cagr']:>6.2f}%   vol {s['vol']:>5.2f}%   maxDD {s['maxdd']:>6.1f}%")
    A("\n[7] SANITY CHECKS")
    checks = []
    checks.append(("the budget's reference holds the four original funds on the 5% grid, summing to 100",
                   sum(b["weights"]) == 100 and len(b["weights"]) == 4
                   and all(x > 0 and x % 5 == 0 for x in b["weights"])))
    # NOTE: horizon vol is NOT necessarily monotone in T. It converges toward the
    # long-run anchor, and when the last liquid future sits ABOVE that anchor the
    # 1Y window can average above the 5Y window. The correct invariant is
    # convergence, not monotonicity. (Bug found 2026-09-02: the old monotone
    # assertion failed the moment spot VIX rose to 16.44, on data that was right.)
    anchor = MACRO["vix_longrun"]
    checks.append(("horizon vol converges toward the long-run anchor",
                   abs(p["vol_ts"][-1]["implied"] - anchor)
                   <= abs(p["vol_ts"][0]["implied"] - anchor) + 1e-9))
    checks.append(("every horizon vol is in a sane 10-40% band",
                   all(10 <= v["implied"] <= 40 for v in p["vol_ts"])))
    checks.append(("headline gauge within 1-5", 1 <= p["gauge"] <= 5))
    checks.append(("driver composite within 1-10", 1 <= p["gauge_10"] <= 10))
    checks.append(("gauge rescale 1-10 -> 1-5 is exact",
                   abs(p["gauge"] - (1 + (p["gauge_10"] - 1) * 4 / 9)) <= 0.005))
    checks.append(("the 1-10 neutral 5.5 maps to the 1-5 neutral",
                   abs(to5(5.5) - p["gauge_neutral"]) < 1e-9))
    # The 1-5 neutral appears in three payload fields (gauge_neutral,
    # driver_scale.neutral, and implicitly the regional NEUTRAL). Three copies of
    # one constant is a drift risk with no upside, so tie them together rather
    # than trusting them to stay equal. (Audit 2026-09-09.)
    checks.append(("every published 1-5 neutral is the same number",
                   p["driver_scale"]["neutral"] == p["gauge_neutral"] == NEUTRAL_5))
    checks.append(("the driver research neutral is the 1-10 neutral",
                   abs(p["driver_scale"]["neutral_10"] - 5.5) < 1e-9))
    # Driver scale. The last 1-10 surface on the page moved to 1-5 on 2026-09-09;
    # these assert the reported scores really are the research scores rescaled, and
    # that the composite of the reported scores IS the headline gauge (true because
    # to5 is affine and the weights sum to 1 - asserted, not assumed).
    # Prose-vs-payload regression guards. These are TARGETED, not general
    # contradiction detection: they encode the two specific ways the scenario
    # descriptions drifted from the macro block. On 2026-09-09 the "Hawkish
    # repricing" row still said two hikes were priced, three days after the
    # monetary-policy driver on the same page was corrected to one.
    _prose = " ".join(x["desc"] for x in
                      p["portfolio_b"]["scenarios"] + p["baseline"]["scenarios"])
    checks.append(("no scenario asserts a hike count the macro block does not price",
                   "two hikes are priced" not in _prose
                   and "two hikes priced" not in _prose))
    checks.append(("the Brent anchor quoted in scenario prose matches the input",
                   f"${MACRO['brent']:.0f}" in _prose))
    # The September hike odds. This must test HAND-WRITTEN prose: the scenario rows
    # now interpolate the input directly, so checking them proved nothing - the
    # 2026-09-11 bite test passed with the input reverted to 58, because the prose
    # had moved with it. A bare presence test is no better, because the notes also
    # carry the figure's own history ("up from 58% a week ago"), which would satisfy
    # a presence check with a stale number. So this reads the FedWatch sentence in
    # the monetary-policy driver note - the one place the live figure is asserted -
    # and requires the first percentage in it to be the input.
    # Tracks the NEXT decision, not one that has happened. The field this read was
    # renamed on 2026-09-17 when the September meeting decided: an input called
    # "September odds" surviving past the September meeting would describe the past
    # as though it were still pending.
    _odds = MACRO["fed_hike_odds_dec"]   # the next meeting since 28 Oct (October decided)
    _mon = next(d[3] for d in DRIVERS if d[0].startswith("Monetary"))
    _m = re.search(r"FedWatch[^.]*?(\d+(?:\.\d+)?)%", _mon)
    checks.append(("the live hike odds asserted in the monetary note match the input",
                   _m is not None and abs(float(_m.group(1)) - _odds) < 0.05))

    # GENERAL prose-vs-input guard, replacing what used to be one-off string
    # checks. A handful of inputs get quoted by name all over the notes; when one
    # moves, every note that quotes it has to move too. On 2026-09-10 Brent was
    # being quoted three different ways on one page - "$95" in the growth driver
    # against an input of $96.28, and "+40% y/y" in the US and Europe notes while
    # the geopolitics driver on the same page said the y/y had "WIDENED to +47.0%
    # from +40.3% a week ago". Two notes carried the superseded number and the
    # page contradicted itself. This scans every note for the named quantities
    # and requires each quote to round to the input it names.
    # Scope: prose that describes the CURRENT market. Scenario descriptions are
    # excluded by construction - "Brent to $130+ from $96" is a counterfactual,
    # not a quote of the input, and the scenario rows keep their own anchor check
    # above. Scoping this correctly is the point: loosening the tolerance until
    # $130 passed would have made the guard useless for its actual job.
    # Catalyst text is on the page and carries the same quotes, so it is scanned
    # with the rest. It was outside this join until 2026-09-19, which is why the
    # catalyst note kept its own private copy of the stale "$109" for nine days.
    _notes_all = ([d[3] for d in DRIVERS] + [r["why"] for r in REGIONS.values()]
                  + [f["gross_note"] for f in FUNDS] + [f["fee_note"] for f in FUNDS]
                  + [c[2] for c in CATALYSTS] + [p[1] for p in POSTPONED])
    _all_prose = " ".join(_notes_all)
    # A quoted Brent figure must match SOME published Brent input, not only spot:
    # the notes legitimately cite the dated session high ($108 on 10 Sep) beside
    # the current level ($105.82). Requiring every quote to equal spot would have
    # forced the true statement out of the prose to satisfy the check - the same
    # scoping mistake the scenario counterfactual exposed on 2026-09-10.
    _brent_ok = [MACRO["brent"], MACRO["brent_high"], MACRO["brent_prev"],
                 MACRO["brent_closure"], MACRO["brent_session_high"],
                 # the dated forward curve the 5-year readings cite (2026-10-27)
                 MACRO["brent_dec2029"], MACRO["brent_dec2030"], MACRO["brent_front_15oct"],
                 MACRO["brent_dec2027_lo"], MACRO["brent_dec2027_hi"]]
    _quoted = [
        (r"Brent[^.]{0,20}?\$(\d+(?:\.\d+)?)", _brent_ok, 1.0, "Brent level"),
        (r"Brent \+(\d+(?:\.\d+)?)%", [MACRO["brent_yoy"]], 1.0, "Brent y/y"),
    ]
    for pat, wants, tol, lab in _quoted:
        found = [float(x) for x in re.findall(pat, _all_prose)]
        checks.append((f"every {lab} quoted in prose matches a published input",
                       bool(found) and all(any(abs(v - w) <= tol for w in wants)
                                           for v in found)))

    # ...but "matches SOME published input" is too weak on its own, and it stayed
    # too weak for nine days. Three notes said "Brent at $109 works directly
    # against" in the present tense while spot was $103.87; $109 is within
    # tolerance of the dated four-month HIGH, so the check above passed every day
    # the sentence was wrong. A quote only earns the dated inputs by being dated.
    # Sentences carrying a date, or the "$130" closure counterfactual, may cite a
    # dated or hypothetical level; an undated present-tense quote must be spot.
    # A DATE here means a day pinned to a month ("15 Sep", "2 September"), not a
    # bare year: the first version of this check accepted any 19xx/20xx token, so
    # "BSP's own 2027 forecast is 5.4% - and Brent at $109" read as dated and the
    # injected staleness passed. A forecast year does not date a price.
    _DATED = re.compile(r"\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
                        r"[a-z]*\b", re.I)
    # Dateness attaches to the QUOTE, not the sentence. The first version tested
    # whole sentences, so one sentence holding both a current level and a dated
    # high ("$104 oil ... the $108.75 peak of 15 Sep") exempted BOTH - and a
    # re-injected stale $106 passed. A date earns only the quote it sits beside.
    # Not only quotes that say "Brent", either: the earnings note said "$106 oil"
    # with no benchmark named, under a pattern that required the word.
    _OILQ = re.compile(r"Brent[^.;]{0,20}?\$(\d+(?:\.\d+)?)"
                       r"|\$(\d{2,3}(?:\.\d+)?)(?= oil\b)"
                       r"|oil (?:price )?(?:at|near|around) \$(\d{2,3}(?:\.\d+)?)")
    _DATE_WINDOW = 45     # chars either side of the quote a date may sit in
    _undated = []
    for _q in _OILQ.finditer(_all_prose):
        _v = float(next(g for g in _q.groups() if g))
        if abs(_v - MACRO["brent_closure"]) <= 1.0:
            continue              # the full-closure counterfactual, not a quote
        _ctx = _all_prose[max(0, _q.start() - _DATE_WINDOW):_q.end() + _DATE_WINDOW]
        if _DATED.search(_ctx):
            continue              # dated quotes may cite a dated input
        _undated.append(_v)
    checks.append(("every UNDATED crude level in prose is the current spot",
                   all(abs(v - MACRO["brent"]) <= 1.0 for v in _undated)))

    # Look-through freshness and ordering. The JEPQ table sat on the 30 June fact
    # sheet until 2026-09-13 - 73 days stale - by which point Tesla had left the top
    # ten and Broadcom had entered, and six of the ten weights had moved. The
    # existing check only asked whether the weights summed to a plausible 30-60%,
    # which a stale-but-coherent table passes. Fund fact sheets are monthly, so 60
    # days allows one publication lag and no more.
    def _lt_date(t):
        """Normalise a YYYY / YYYY-MM / YYYY-MM-DD as-of to the end of its period."""
        parts = t.split("-")
        if len(parts) == 3:
            return _dt.date.fromisoformat(t)
        if len(parts) == 2:
            y, m = int(parts[0]), int(parts[1])
            ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
            return _dt.date(ny, nm, 1) - _dt.timedelta(days=1)
        return _dt.date(int(parts[0]), 12, 31)

    _LT_MAX_AGE_D = 60
    _asof_d = _dt.date.fromisoformat(REVIEW_DATE)
    for _k, _v in LOOKTHROUGH.items():
        if not _v.get("as_of"):
            continue
        _age = (_asof_d - _lt_date(_v["as_of"])).days
        checks.append((f"{_k} look-through is within {_LT_MAX_AGE_D} days of the as-of date",
                       0 <= _age <= _LT_MAX_AGE_D))
    # Weight-ranked kinds only. A yield curve is ordered by TENOR, and the money
    # market rows (5.138 / 5.517 / 5.717) ascend correctly - the first version of
    # this check called that a defect.
    checks.append(("weight-ranked look-through rows descend",
                   all(all(v["rows"][i][1] >= v["rows"][i + 1][1]
                           for i in range(len(v["rows"]) - 1))
                       for v in LOOKTHROUGH.values()
                       if v.get("rows") and v["kind"] in ("stocks", "sectors"))))

    # The covered-call vol factor must be the published ratio, not a typed constant.
    _q = next(f for f in FUNDS if f["id"] == "ATRQIAP")
    checks.append(("the covered-call vol factor is the published JEPQ/NDX ratio",
                   abs(_q["vol_beta"] / NDX_SP_BETA - JEPQ_VOL / NDX_VOL) < 1e-9))
    checks.append(("the published JEPQ vol is below the index it is written on",
                   JEPQ_VOL < NDX_VOL and 0.5 < JEPQ_VOL / NDX_VOL < 0.85))

    # The Hormuz disruption must be stated on the measure that reaches this
    # portfolio. Until 2026-09-12 the page published a vessel-count drop
    # (6 of ~85) as "a ~93% shutdown", which describes a supply collapse that the
    # model's own Brent input contradicts: Goldman puts Gulf flows at ~2/3 of
    # pre-war. These assert the volume measure is published, that it is the one
    # quoted, and that the vessel counts are published as the disputed range they
    # are rather than as a single settled number.
    _geo_note = next(d[3] for d in DRIVERS if d[0].startswith("Geopolitics"))
    # ON THE NEWEST VOLUME READING (2026-10-15). This tested for Goldman's 28 Aug
    # 15.5 mb/d, so the note had to keep quoting a seven-week-old figure to pass -
    # a check pinning stale prose in place. It now reads the latest dated measure.
    _flow_loss = MACRO["hormuz_crude_kpler_below_pct"] / 100
    checks.append(("Hormuz is quoted on oil volume, not vessel count alone",
                   "mb/d" in _geo_note and str(MACRO["hormuz_crude_kpler"]) in _geo_note))
    # Not just "all three strings appear": with the counts collapsed to one number
    # that passes trivially while the disagreement it exists to record has vanished.
    # The point is that the sources DISAGREE, so assert the spread. (Bite test,
    # 2026-09-12.)
    _counts = [MACRO["hormuz_transits"], MACRO["hormuz_lloyds"], MACRO["hormuz_us_claim"]]
    checks.append(("the vessel counts are published as a disputed range, not one number",
                   len(set(_counts)) == 3 and max(_counts) >= 3 * min(_counts)))
    # NOT a string check on "93% shutdown": the note now quotes that phrase in order
    # to correct it, and a literal search cannot tell an assertion from a retraction -
    # the same trap as the $130 counterfactual on 2026-09-10. What is actually
    # required is that both measures are published, so a reader can see how far apart
    # they are, and that the two disagree by enough to be worth stating.
    # REVISED 2026-10-21: this asserted a 20-50% volume loss - a FACT about the inputs
    # written as an invariant (runbook 74). Kpler's week to 18 Oct put the loss at 18%
    # and the check failed on a true input. What it exists to require is that both
    # measures are published as fractions of their own baselines, and quoted.
    _vessel_loss = 1 - MACRO["hormuz_transits"] / MACRO["hormuz_baseline"]
    checks.append(("both the vessel-count and volume measures are published",
                   0 < _flow_loss < 1 and 0 < _vessel_loss < 1
                   and MACRO["hormuz_crude_kpler_below_pct"] == 100 - MACRO["hormuz_kpler_pct_of_prewar"]
                   and f"{100 - MACRO['hormuz_crude_kpler_below_pct']}% of pre-war" in _geo_note))
    checks.append(("the two Hormuz measures are far enough apart to require both",
                   _vessel_loss - _flow_loss > 0.3))
    checks.append(("the Gulf flow baseline is the source's own, not a borrowed one",
                   abs(MACRO["hormuz_flow_now"] + MACRO["hormuz_flow_gap"]
                       - MACRO["hormuz_flow_prewar"]) < 1e-9
                   and 0.64 < MACRO["hormuz_flow_now"] / MACRO["hormuz_flow_prewar"] < 0.70))
    checks.append(("the flows trough is below the current reading",
                   MACRO["hormuz_flow_trough"] < MACRO["hormuz_flow_now"]
                   < MACRO["hormuz_flow_prewar"]))

    # A driver cannot sit at the floor of its scale while the page models a state
    # strictly worse than the one it describes. On 2026-09-11 geopolitics & energy was
    # scored 1.0 - "no room left to worsen" - beside a Hormuz row modelling full
    # closure and Brent above $130 against a settle of $104.61. Both cannot be true.
    _geo = next(d for d in DRIVERS if d[0].startswith("Geopolitics"))
    checks.append(("no driver sits at the scale floor while a worse state is modelled",
                   _geo[2] > 1.0 and MACRO["brent_closure"] > MACRO["brent"]))

    # ---- the volatility time axis ------------------------------------------
    # Every maturity on the strip must reproduce from the contract settlement
    # rule and the quote date. Until 2026-09-10 they were four typed constants
    # that backed out to an implied base date of Sunday 6 September - neither the
    # quote date nor AS_OF - and nothing was checking them.
    # THE TWO HEADLINE DATES THEMSELVES. Neither was checked: AS_OF is the last
    # completed trading session, so it cannot land on a weekend, and REVIEW_DATE is
    # when a human worked through the page, so it cannot precede the data it was
    # reviewing. The weekday used to be typed in a comment beside REVIEW_DATE and
    # said "Saturday" on a Sunday - a second copy of a date that nobody maintains.
    _asof = _dt.date.fromisoformat(AS_OF)
    _revd = _dt.date.fromisoformat(REVIEW_DATE)
    checks.append((f"the as-of date is a trading weekday ({_asof:%A})",
                   _asof.weekday() < 5))

    # A PROBABILITY FOR A MEETING THAT HAS HAPPENED must be quoted with the meeting
    # it belongs to. "the hike is 92.0% priced" read as pending for five days after
    # the hike was delivered, because the input was correctly kept "for the record"
    # and the sentence reading it was not updated. Renaming a field is half the fix;
    # the prose that reads it is the other half (runbook 20).
    # This is a narrow guard, and says so: it fires only where the VALUE is quoted.
    # It cannot police tense in general, and pretending otherwise would be the
    # "right words are present" check this project has been caught writing before.
    RESOLVED_ODDS = [("fed_hike_odds_sep_final", "fed_hike_odds_sep_date")]
    for _vk, _dk in RESOLVED_ODDS:
        _d = _dt.date.fromisoformat(MACRO[_dk])
        checks.append((f"{_vk} describes a meeting that has actually happened",
                       _d <= _asof))
        _needle = f"{MACRO[_vk]:.1f}%"
        _day = f"{_d.day} {_d:%b}"
        _hits = [s for s in re.split(r"(?<=[.;])\s+", _all_prose) if _needle in s]
        checks.append((f"every sentence quoting {_needle} names its meeting date "
                       f"({_day})",
                       all(_day in s or f"{_d.day} {_d:%B}" in s for s in _hits)))

    # The target-fund level is the SAME exposure with the feeder's fee added back,
    # and its drawdown comes out of the same formula - nothing else may differ.
    checks.append(("every target fund's forecast is its feeder's plus the feeder fee, "
                   "and its drawdown reproduces from the same k and vol",
                   all(f2["target_net_macro"] is None if f2["id"] == "ATRPHMM" else
                       abs(f2["target_net_macro"] - f2["net_macro"] - f2["fee_feeder"]) < 0.0051
                       and f2["target_dd_macro"] >= f2["dd_macro"]   # the fee deepens the feeder's
                       and abs(-(f2["dd_k"] * f2["vol"] - DD_MU * f2["target_net_macro"])
                               * DD_HORIZON_SCALAR - f2["target_dd_macro"]) < 0.08
                       for f2 in F)))
    # Every summary number must be stated in the full note it abbreviates.
    _NUMRE = re.compile(r"\d+(?:\.\d+)?")
    _full = {**{d[0]: d[3] for d in DRIVERS}, **{k: v["why"] for k, v in REGIONS.items()}}
    _own = {d[0]: (f"{d[2]}", f"{d[2]:.2f}", f"{d[2]:.1f}") for d in DRIVERS}   # a driver's own score
    _drift = [(k, n) for k, t in SUMMARY.items() for n in _NUMRE.findall(t)
              if not re.fullmatch(r"(19|20)\d\d", n) and n not in _full[k]
              and n not in _own.get(k, ())]
    checks.append((f"every summary's figures are stated in its full note ({_drift or 'all'})",
                   not _drift and set(SUMMARY) == set(_full)))
    # PH T-BILLS: each tenor's reported move reproduces from the previous auction,
    # and the auction is no older than two weekly cycles at review.
    _tb = [MACRO["ph_tbill_91"], MACRO["ph_tbill_182"], MACRO["ph_tbill_364"]]
    checks.append(("every T-bill tenor's reported move reproduces from the prior auction",
                   all(abs((_tb[i] - MACRO["ph_tbill_prev"][i]) * 100 - MACRO["ph_tbill_chg_bp"][i])
                       <= 0.05 + 1e-9 for i in range(3))))
    _tba = (_revd - _dt.date.fromisoformat(MACRO["ph_tbill_date"])).days
    checks.append((f"the T-bill auction is within two weekly cycles ({_tba}d of "
                   f"{2 * MACRO['ph_tbill_cadence_d']}d)",
                   0 <= _tba <= 2 * MACRO["ph_tbill_cadence_d"]))
    checks.append(("the T-bill look-through is dated by its auction, not by the page",
                   LOOKTHROUGH["ATRPHMM"]["as_of"] == MACRO["ph_tbill_date"]))
    # HORMUZ COUNTS. The transit reading sat undated and went fourteen days stale.
    # PortWatch publishes weekly, so one cadence of lag is structural and two means
    # a publication was missed - the bound is derived from the cadence, not chosen.
    _hd = _dt.date.fromisoformat(MACRO["hormuz_transits_date"])
    _hc = MACRO["hormuz_transits_cadence_d"]
    checks.append(("the transit reading is not dated after the review",
                   _hd <= _revd))
    checks.append((f"the transit reading is within two publication cycles "
                   f"({MACRO['hormuz_transits_age_d']}d of {2 * _hc}d)",
                   MACRO["hormuz_transits_age_d"] <= 2 * _hc))
    # The queue is a SERIES now, for the reason the note gives: two points out of
    # three read as a drawdown that the third contradicts.
    _hqd = [d for d, _ in MACRO["hormuz_queue"]]
    checks.append(("the vessel queue is in date order with no repeats",
                   _hqd == sorted(set(_hqd)) and len(_hqd) == len(set(_hqd))))
    checks.append(("no vessel-queue reading is dated after the review",
                   all(_dt.date.fromisoformat(d) <= _revd for d in _hqd)))
    checks.append(("the queue needs 3+ points before any note calls a direction",
                   len(MACRO["hormuz_queue"]) >= 3))
    # Kpler's Yanbu loss against the model's own pre-strike throughput: a line
    # running at the targeted half should cost about half of what it carried.
    # Independent numbers that agree are worth asserting; if they stop agreeing,
    # one of them has moved and the note that reconciles them is wrong.
    _ymid = (MACRO["yanbu_loss_lo"] + MACRO["yanbu_loss_hi"]) / 2
    _half = MACRO["petroline_bypass"] * MACRO["petroline_target_pct"] / 100
    checks.append((f"Kpler's Yanbu loss is about half the pre-strike throughput "
                   f"({_ymid:.2f} vs {_half:.2f} mb/d)", abs(_ymid - _half) <= 0.5))
    # (the review-date-vs-as-of ordering is already asserted below, beside the
    # catalyst checks - not duplicated here)
    # THE IMF VINTAGE IS A CLOCK. The April WEO sat here for 2.5 months after the
    # July update superseded it, because nothing knew which edition was carried.
    # The WEO appears every ~3 months (Jan/Apr/Jul/Oct); 120 days past the carried
    # edition means a newer one exists and has not been read.
    _imf_age = (_asof - _dt.date.fromisoformat(MACRO["imf_weo_vintage"])).days
    checks.append((f"the IMF WEO edition carried is current ({_imf_age}d old, bound 120d)",
                   0 <= _imf_age <= 120))
    # A US catalyst is read against the last US session carried (CATALYST_CLOCK).
    _cat_clock = lambda n: (_dt.date.fromisoformat(MACRO[CATALYST_CLOCK[n]]) if n in CATALYST_CLOCK
                            else _asof)
    checks.append(("every pending catalyst is dated after the last session of its own market carried",
                   all(_dt.date.fromisoformat(d) > _cat_clock(n) for d, n, _ in CATALYSTS)
                   and set(CATALYST_CLOCK) <= {n for _, n, _ in CATALYSTS}
                   and all(MACRO[k] <= AS_OF for k in CATALYST_CLOCK.values())))
    checks.append(("catalysts are listed in date order",
                   [d for d, _, _ in CATALYSTS] == sorted(d for d, _, _ in CATALYSTS)))

    checks.append((f"the review date is not before the market as-of date "
                   f"({_revd:%A} {REVIEW_DATE} vs {_asof:%A} {AS_OF})",
                   _revd >= _asof))
    _q = _dt.date.fromisoformat(VIX_QUOTE_DATE)
    checks.append(("the VIX quote date is a trading weekday", _q.weekday() < 5))
    # The latest observed spot may be the curve's own close (a same-day strip, as
    # from 2026-10-03) or newer; never OLDER - a curve quoted after the latest close
    # would be pricing a session the series has not recorded.
    _vl = _dt.date.fromisoformat(MACRO["vix_latest_date"])
    checks.append(("the latest VIX observation is a weekday", _vl.weekday() < 5))
    checks.append(("the latest VIX observation is not older than the curve quote",
                   _vl >= _q))
    # The spot series may legitimately lag AS_OF when a session's close cannot be
    # confirmed - on 2026-09-16 the 15 Sep print was withheld because three reported
    # figures for it were mutually inconsistent. A lag is acceptable; a SILENT lag is
    # not, so it is surfaced and bounded. More than a few sessions behind means the
    # series has quietly stopped tracking.
    _vix_lag = (_dt.date.fromisoformat(AS_OF)
                - _dt.date.fromisoformat(MACRO["vix_latest_date"])).days
    checks.append((f"the VIX series lags the as-of date by {_vix_lag} day(s)",
                   0 <= _vix_lag <= 5))
    # THE SAME BOUND, ON EVERY MARKET SERIES. Only the VIX had one. Brent, WTI and
    # the 10-year carried their dates in comments, so nothing could see them age -
    # and the 10-year's comment was WRONG for two days, saying 18 Sep over a level
    # that belongs to the 17th. A date a check cannot read is not a date.
    # Five calendar days covers a long weekend plus one withheld session; past that
    # the series has quietly stopped tracking rather than deliberately paused.
    for _lbl, _dk in (("Brent", "brent_date"), ("WTI", "wti_date"),
                      ("the 10-year", "ust_10y_date"), ("the 30-year", "ust_30y_date"),
                      ("the 2-year", "ust_2y_date"), ("equities", "equity_date"),
                      ("the peso", "usdphp_date"), ("the PSEi", "psei_date"),
                      ("the Nikkei", "nikkei_latest_date")):
        _sd = _dt.date.fromisoformat(MACRO[_dk])
        _lag = (_asof - _sd).days
        checks.append((f"{_lbl} is dated and lags the as-of date by {_lag} day(s)",
                       0 <= _lag <= 5))
    # EVERY INDEX MOVE REPRODUCES FROM ITS OWN PREVIOUS CLOSE. The chain rule, in
    # code. The percentage is published to 2dp, so the bound is half a unit of that
    # on the implied level - derived from the publication precision, not chosen.
    for _lbl, _c, _p, _pc in (("S&P", "spx_close", "spx_prev", "spx_chg_pct"),
                              ("Nasdaq", "nasdaq_close", "nasdaq_prev", "nasdaq_chg_pct"),
                              ("Dow", "dow_close", "dow_prev", "dow_chg_pct")):
        _implied = MACRO[_p] * (1 + MACRO[_pc] / 100)
        checks.append((f"the {_lbl}'s move reproduces from its own previous close "
                       f"({_implied:,.2f} vs {MACRO[_c]:,.2f})",
                       abs(_implied - MACRO[_c]) <= MACRO[_p] * 0.00005 + 0.01))
    # Oil gets the same chain - but ONLY WITHIN ONE CONTRACT. The first pass on
    # 2026-09-23 chained November WTI prints against October's final settle, found
    # a $2-5 gap and withheld a settle that was never disputed. The front month on
    # each date is derived from the exchange calendar (section 1a).
    _wti_front = front_contract(MACRO["wti_date"], cl_last_trade)
    _wti_prev_front = front_contract(MACRO["wti_prev_date"], cl_last_trade)
    checks.append((f"WTI is quoted on the front-month contract for its date ({_wti_front})",
                   MACRO["wti_contract"] == _wti_front))
    _wti_rolled = _wti_prev_front != _wti_front
    checks.append(("a WTI roll is declared exactly when the calendar says one happened",
                   _wti_rolled == (MACRO["wti_expired_contract"] == _wti_prev_front)
                   and (not _wti_rolled or cl_last_trade(
                       *map(int, MACRO["wti_expired_contract"].split("-")))
                       == _dt.date.fromisoformat(MACRO["wti_prev_date"]))))
    # Across a roll the prior is IMPLIED by the reported move (so a chain check
    # would be circular); within one contract it must be a published settle, and
    # then the move has to reproduce from it at its reported (2dp) precision.
    checks.append(("WTI's prior is implied exactly when it crosses a roll",
                   MACRO["wti_prev_implied"] == _wti_rolled))
    checks.append(("WTI's reported move reproduces from its own contract's prior",
                   _wti_rolled or abs(MACRO["wti_prev"] * (1 + MACRO["wti_chg_pct"] / 100)
                                      - MACRO["wti_settle"])
                   <= MACRO["wti_prev"] * 0.00005 + 0.01))
    _bfront = [front_contract(d, brent_last_trade)
               for d in (MACRO["brent_prev_date"], MACRO["brent_date"])]
    checks.append((f"Brent's latest pair is one contract ({_bfront[1]}), so it can chain",
                   _bfront[0] == _bfront[1]))
    # NOT "is one of the candidates" - that passed for every candidate, the wrong
    # ones included, and was caught by its own bite test the day it was written.
    # The question is whether the REPORTED move lands on the settle from this prior,
    # at the precision the move was reported - derived from the figure itself (a
    # 0dp "fell 1%" allows half a percent, a 2dp "+3.86%" half a basis point).
    _bdp = len(repr(MACRO["brent_chg_reported"]).split(".")[1]) \
        if isinstance(MACRO["brent_chg_reported"], float) else 0
    checks.append(("Brent's reported move reproduces from its own previous settle "
                   "(or the settle is recovered)",
                   MACRO["brent_chg_reported"] is None
                   or abs(MACRO["brent_prev"] * (1 + MACRO["brent_chg_reported"] / 100)
                          - MACRO["brent"])
                   <= MACRO["brent_prev"] * 0.5 * 10 ** -_bdp / 100 + 0.01))
    # A RECOVERED settle earns its place only if EVERY next-session quote lands on
    # it - level less its own points change - to the cent; one quote is not two.
    checks.append(("every recovered Brent settle is reproduced by two or more next-session quotes",
                   all(d in dict(MACRO["brent_history"]) and len(qs) >= 2
                       and all(abs(lv - pt - dict(MACRO["brent_history"])[d]) <= 0.005 + 1e-9
                               for lv, pt in qs)
                       for d, qs in MACRO["brent_recovered"].items())))
    _bd = [d for d, _ in MACRO["brent_history"]]
    checks.append(("the Brent series is weekdays, in date order, no duplicates, "
                   "none after the as-of date",
                   _bd == sorted(set(_bd))
                   and all(_dt.date.fromisoformat(d).weekday() < 5 for d in _bd)
                   and _bd[-1] <= AS_OF))
    # A fixed year-ago base read against a moving settle stops being "year on
    # year" as the anniversary drifts. THREE DAYS since 2026-10-26 (a week before): the
    # week let a 5.4% one-day jump fall between the base and the anniversary.
    _anniv = _dt.date.fromisoformat(MACRO["brent_date"]).replace(year=_dt.date.fromisoformat(
        MACRO["brent_date"]).year - 1)
    checks.append(("Brent's year-ago base is within three days of the anniversary",
                   abs((_anniv - _dt.date.fromisoformat(MACRO["brent_yr_ago_date"])).days)
                   <= 3))
    # A dispute record is only a record if it contains the settle that resolved it.
    for _dk, _ck in (("2026-09-21", "brent_disputed"), ("2026-09-23", "brent_disputed_23sep")):
        checks.append((f"the {_dk} Brent dispute record contains the settle that resolved it",
                       dict(MACRO["brent_history"]).get(_dk) in MACRO[_ck]))
    checks.append(("the 23 Sep 10-year dispute record contains the official close that resolved it",
                   dict(MACRO["ust_10y_history"]).get("2026-09-23") in MACRO["ust_10y_disputed_23sep"]))
    checks.append(("the 23 Sep WTI candidates are all one contract, the one that settled",
                   MACRO["wti_date"] != "2026-09-23"
                   or MACRO["wti_settle"] in MACRO["wti_disputed_23sep"]))
    # The PSEi had no chain check at all: its move was stated in a comment. Both the
    # point and the percentage move must reproduce from the published prior close,
    # at the precision each is published (2dp).
    # THE PESO CHAINS, and its prior is DATED. The last review filed Tuesday's close
    # as Wednesday's and called the 24th "a centavo weaker after a flat 23rd"; with a
    # date on the prior and the reported centavo move checked, that cannot recur
    # silently.
    checks.append(("the peso's reported move reproduces from its dated prior close",
                   MACRO["usdphp_prev_date"] < MACRO["usdphp_date"]
                   and abs((MACRO["usdphp"] - MACRO["usdphp_prev"]) - MACRO["usdphp_chg"]) < 0.0005))
    # EVERY REPORTED BRENT MOVE reproduces from the previous settle in the series,
    # on the level, at the move's own precision - the VIX rule, now for Brent.
    _bh = MACRO["brent_history"]
    _bprev = {d: v for (_, v), (d, _) in zip(_bh, _bh[1:])}
    # Across a roll the move is off the NEW contract's own prior settle. A session
    # whose front month differs from the previous session's MUST have that prior
    # recorded, and only such a session may - so a roll can neither be chained
    # through silently nor used to excuse an ordinary day's mismatch.
    _brolls = {d for (pd, _), (d, _) in zip(_bh, _bh[1:])
               if front_contract(pd, brent_last_trade) != front_contract(d, brent_last_trade)}
    checks.append(("every Brent roll in the series has its new contract's prior, and only rolls do",
                   set(MACRO["brent_roll_priors"]) == _brolls))
    _bprev.update({d: v for d, v in MACRO["brent_roll_priors"].items() if d in _bprev})
    _bcur = dict(_bh)
    def _bmove_ok(d, pct):
        _dp = 0 if isinstance(pct, int) else len(repr(pct).split(".")[1])
        return d in _bprev and (abs(_bprev[d] * (1 + pct / 100) - _bcur[d])
                                <= _bprev[d] * 0.5 * 10 ** -_dp / 100 + 0.005 + 1e-9)
    checks.append(("every reported Brent move reproduces from the previous settle in the series",
                   all(_bmove_ok(d, p) for d, p in MACRO["brent_reported_moves"].items())))
    checks.append(("every Brent move reported in cents lands on its settle to the cent, and no session has both",
                   all(d in _bprev and abs(_bprev[d] + pt - _bcur[d]) <= 0.005 + 1e-9
                       for d, pt in MACRO["brent_reported_pts"].items())
                   and not set(MACRO["brent_reported_pts"]) & set(MACRO["brent_reported_moves"])))
    checks.append(("every Brent session high is on a series date and at/above that day's settle",
                   all(d in _bcur and _bcur[d] <= h and d <= AS_OF
                       for d, h in MACRO["brent_session_highs"].items())))
    checks.append(("the latest Brent settle carries a reported move (percent or cents) or a recovery",
                   (MACRO["brent_date"] in MACRO["brent_reported_moves"]
                    or MACRO["brent_date"] in MACRO["brent_reported_pts"])
                   != (MACRO["brent_date"] in MACRO["brent_recovered"])))
    checks.append(("the KOSPI's point and percent moves reproduce from its prior close",
                   abs(MACRO["kospi_latest_prev"] + MACRO["kospi_latest_chg_pts"]
                       - MACRO["kospi_latest"]) < 0.005
                   and abs(MACRO["kospi_latest_chg_pts"] / MACRO["kospi_latest_prev"] * 100
                           - MACRO["kospi_latest_chg_pct"]) <= 0.005 + 1e-9))
    # THE POINTS CHAIN, wherever a source prints points (v78). The percent chain's bound
    # is half a unit of the published 2dp - about 3 points on the Nikkei - so it passed the
    # 27 Oct close that v76-v77 carried five hundredths low (63268.32). Points are printed
    # to the cent, so their chain is exact, and it is what catches that error:
    # 63268.32 + 685.82 is the 63954.14 one source printed for the 28th. The KOSPI, the
    # PSEi and the Dow carried points already; the S&P, the Nasdaq and the Nikkei now do.
    for _lbl, _c, _p, _pt in (("S&P", "spx_close", "spx_prev", "spx_chg_pts"),
                              ("Nasdaq", "nasdaq_close", "nasdaq_prev", "nasdaq_chg_pts"),
                              ("Nikkei", "nikkei_latest", "nikkei_latest_prev", "nikkei_latest_chg_pts")):
        checks.append((f"the {_lbl}'s point move chains to the cent from its prior close",
                       abs(MACRO[_p] + MACRO[_pt] - MACRO[_c]) < 0.005))
    checks.append(("the Nikkei's move reproduces from its own previous close",
                   abs(MACRO["nikkei_latest_prev"] * (1 + MACRO["nikkei_latest_chg_pct"] / 100)
                       - MACRO["nikkei_latest"]) <= MACRO["nikkei_latest_prev"] * 0.00005 + 0.01))
    # Session highs are dated and sit where a high must: at or above that day's
    # carried level, and never after the as-of date.
    checks.append(("Brent's session high is dated in the series and at/above that day's settle",
                   MACRO["brent_session_high_date"] in dict(MACRO["brent_history"])
                   and dict(MACRO["brent_history"])[MACRO["brent_session_high_date"]]
                   <= MACRO["brent_session_high"]
                   and MACRO["brent_session_high_date"] <= AS_OF))
    # The high may predate the latest reading (24 Sep's 5.501 against Friday's
    # 5.488); what it may not be is BELOW it - a reading above the carried high
    # means the high moved and nobody rolled it.
    # "At or above": when the reading IS the new high (28 Sep, 5.57) the two are
    # equal; a reading ABOVE the carried high still fails.
    checks.append(("the 30-year's session high is dated, not after the as-of date, and at or above the reading",
                   MACRO["ust_30y_high_date"] <= AS_OF
                   and MACRO["ust_30y_high"] >= MACRO["ust_30y"]))
    checks.append(("the next-meeting (December) FedWatch reading is dated, after its baseline, within 5 days",
                   MACRO["fed_hike_odds_dec_prev_date"] < MACRO["fed_hike_odds_dec_date"] <= AS_OF
                   and (_asof - _dt.date.fromisoformat(MACRO["fed_hike_odds_dec_date"])).days <= 5))
    # A DECIDED MEETING LEAVES NO LIVE ODDS BEHIND (v79): no input still names the
    # October odds, and the decision is dated on or before the as-of and the US session
    # carried, with its vote adding up to the twelve voters.
    checks.append(("the October meeting is recorded as decided: no October odds input left, the vote adds to 12, dated by the US session",
                   not any(k.startswith("fed_hike_odds_oct") for k in MACRO)
                   and MACRO["fed_oct_votes_hold"] + MACRO["fed_oct_votes_hike"] == 12
                   and MACRO["fed_oct_decision_date"] <= MACRO["equity_date"] <= AS_OF))
    checks.append(("the PSEi's point and percent moves reproduce from its prior close",
                   abs(MACRO["psei_prev"] + MACRO["psei_chg_pts"] - MACRO["psei"]) < 0.005
                   and abs(MACRO["psei_chg_pts"] / MACRO["psei_prev"] * 100
                           - MACRO["psei_chg_pct"]) <= 0.005 + 1e-9))
    checks.append(("the Dow's point move reproduces from the two closes",
                   abs((MACRO["dow_close"] - MACRO["dow_prev"])
                       - MACRO["dow_chg_pts"]) < 0.005))

    # ONE BASIS IN THE 10-YEAR SERIES. Official closes publish to 2dp; CNBC's
    # mid-session prints run to 3dp. Both had been in this series, which is how a
    # mid-session 4.951 got published as Monday's close and how an intraday quote
    # beside an official close looked like a three-way dispute over Friday's.
    # A value with a third decimal is an intraday quote that has leaked in.
    checks.append(("every 10-year close is on the official 2dp basis",
                   "official close" in MACRO["ust_10y_basis"]
                   and all(round(v, 2) == v for _, v in MACRO["ust_10y_history"])))
    # PROVISIONAL is allowed for the LATEST point only - it is what keeps a market
    # print from quietly becoming an official close. The next session's roll moves
    # it off the end and fails this until the reviewer confirms it and clears the
    # flag. Any note that calls the series "official closes" while quoting the
    # provisional point has to say so.
    _uhd = [d for d, _ in MACRO["ust_10y_history"]]
    checks.append(("only the latest 10-year point may be provisional",
                   all(d == _uhd[-1] for d in MACRO["ust_10y_provisional"])))
    _prov_txt = f"{MACRO['ust_10y']:.2f}%"
    checks.append(("a provisional 10-year point names the basis it is provisional on, not a figure",
                   not MACRO["ust_10y_provisional"]
                   or (MACRO.get("ust_10y_provisional_basis")
                       and not re.search(r"\d\.\d", MACRO["ust_10y_provisional_basis"]))))
    checks.append(("no note passes a provisional 10-year point off as an official close",
                   not MACRO["ust_10y_provisional"]
                   or all("provisional" in t for t in _notes_all
                          if "official close" in t and _prov_txt in t)))
    # DAY FORMS a note may use for a dated input: "17th", "17 Sep", "17 September".
    def _dayforms(iso):
        _d = _dt.date.fromisoformat(iso)
        _sfx = "th" if 11 <= _d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(_d.day % 10, "th")
        return (f"{_d.day}{_sfx}", f"{_d.day} {_d:%b}", f"{_d.day} {_d:%B}")
    # NO KEY IS TYPED TWICE IN ONE DICT. Python keeps the later of two equal keys and says
    # nothing: v72's first pass added a 23 Oct December baseline above the 22 Oct one under
    # the same name, and the note printed the 22nd's 90.0% as the 23rd's. Every dict
    # literal in this file is parsed and its constant keys counted.
    import ast as _ast
    _dupkeys = []
    for _n in _ast.walk(_ast.parse(open(__file__, encoding="utf-8").read())):
        if isinstance(_n, _ast.Dict):
            _ks = [k.value for k in _n.keys if isinstance(k, _ast.Constant)]
            _dupkeys += [(_n.lineno, k) for k in sorted({k for k in _ks if _ks.count(k) > 1})]
    checks.append((f"no dict literal in the engine types a key twice ({len(_dupkeys)} found)",
                   not _dupkeys))
    # FEDWATCH HAS TWO BASELINES and each delta must use its own. The first pass
    # printed "jumped from 50.9% to 73% in a day": the week's move as the day's.
    checks.append(("the FedWatch readings are dated in order, none after the as-of date",
                   MACRO["fed_hike_odds_dec_prev_date"] < MACRO["fed_hike_odds_dec_date"] <= AS_OF))
    _oneday = [m for t in _notes_all
               for m in re.finditer(r"from (\d+(?:\.\d+)?)% to (\d+(?:\.\d+)?)% in a day", t)]
    checks.append(("every 'in a day' FedWatch move is quoted off the previous session",
                   all(abs(float(m.group(1)) - MACRO["fed_hike_odds_dec_prev"]) < 0.05
                       and abs(float(m.group(2)) - MACRO["fed_hike_odds_dec"]) < 0.05
                       for m in _oneday)))
    # A reading not re-found on the review date may be quoted, but only with its date.
    _decq = f"{MACRO['fed_hike_odds_dec']}%"
    # A whole-number figure is matched as a whole token (v81): "85%" is inside "18.85%".
    _decre = re.compile(r"(?<![\d.])" + re.escape(_decq))
    checks.append(("the December odds are quoted only beside the date they were verified",
                   all(any(f in sent for f in _dayforms(MACRO["fed_hike_odds_dec_date"]))
                       for t in _notes_all for sent in re.split(r"(?<=[.;])\s", t)
                       if _decre.search(sent))))
    # A DAILY CLOSE QUOTED WITH A DATE CARRIES ITS OWN DATE (v83). The valuation note said
    # "The S&P closed at 7743.98 on the 27th" from v79 to v82: the level rolled to the 28th
    # and the typed ordinal did not. In every note and summary, a sentence that quotes one of
    # these closes and names any day must name the close's own day among them.
    _dayre = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)\b|\b(\d{1,2}) (?:Sep|Oct|Nov|September|October|November)\b")
    _closes = [(k, d) for k, d in (("spx_close", "equity_date"), ("nasdaq_close", "equity_date"),
               ("dow_close", "equity_date"), ("nikkei_latest", "nikkei_latest_date"),
               ("kospi_latest", "kospi_latest_date"), ("psei", "psei_date"), ("usdphp", "usdphp_date"),
               ("brent", "brent_date"), ("wti_settle", "wti_date"), ("vix_latest", "vix_latest_date"))]
    _bad_days = []
    for t in _notes_all + list(SUMMARY.values()):
        for sent in re.split(r"(?<=[.;])\s", t):
            days = {int(a or b) for a, b in _dayre.findall(sent)}
            if not days: continue
            for k, dk in _closes:
                v = MACRO[k]
                forms = {f"{v:.2f}", f"{v:,.2f}", f"{v}", f"{v:,}"}
                if any(re.search(r"(?<![\d.,])" + re.escape(f_) + r"(?![\d])", sent) for f_ in forms) \
                        and _dt.date.fromisoformat(MACRO[dk]).day not in days:
                    _bad_days.append((k, sent[:80]))
    checks.append((f"every daily close quoted beside a date is quoted beside its own ({len(_bad_days)} not)",
                   not _bad_days))
    # THE DOT PLOT'S OWN INPUTS MUST REPRODUCE ITS MEDIAN: participants not in the
    # one- or two-more groups sit at today's midpoint, and each group is a whole
    # number of 25bp steps above it.
    _fmid = (MACRO["fed_funds_lower"] + MACRO["fed_funds_upper"]) / 2
    _dots = sorted([_fmid] * (MACRO["fed_dots_participants"] - MACRO["fed_dots_one_more"]
                              - MACRO["fed_dots_two_more"])
                   + [MACRO["fed_dot_one_more_level"]] * MACRO["fed_dots_one_more"]
                   + [MACRO["fed_dot_two_more_level"]] * MACRO["fed_dots_two_more"])
    _dmed = (_dots[len(_dots) // 2 - 1] + _dots[len(_dots) // 2]) / 2
    # THE DRAWDOWN CALIBRATION REPRODUCES ITS OWN ANCHORS. Stated on the page for a
    # month and never asserted: k*sigma - mu_coef*mu must land within half a point of
    # each published median, or k is not calibrated to what the page says it is.
    checks.append(("the drawdown k reproduces both calibration anchors (" + ", ".join(
                       f"{n_} {DD_K * sg_ - DD_MU * mu_:.1f} vs {dd_:.0f}"
                       for n_, (sg_, mu_, dd_) in DD_CALIB.items()) + ")",
                   all(abs(DD_K * sg_ - DD_MU * mu_ - dd_) <= 0.5
                       for sg_, mu_, dd_ in DD_CALIB.values())))
    # A SETTLE HIGH ONLY MOVES UP. When it moves, the old one is kept as the prior,
    # which must be older and lower - otherwise the "highest since" claim is wrong.
    checks.append(("the Brent settle high moved up from an older, lower prior",
                   MACRO["brent_high_prev_date"] < MACRO["brent_high_date"]
                   and MACRO["brent_high_prev"] < MACRO["brent_high"]
                   and MACRO["brent_high"] >= max(v for d_, v in MACRO["brent_history"]
                                                  if front_contract(d_, brent_last_trade)
                                                  == MACRO["brent_contract"])))
    checks.append(("every itemised fee sums to the fee it itemises",
                   all(abs(sum(v for _, v in f_["fee_parts"]) - f_["fee_feeder"]) < 1e-9
                       for f_ in FUNDS if "fee_parts" in f_)))
    checks.append(("the dot-plot distribution reproduces its published median",
                   abs(MACRO["fed_dot_one_more_level"] - _fmid - 0.25) < 1e-9
                   and abs(MACRO["fed_dot_two_more_level"] - _fmid - 0.50) < 1e-9
                   and round(_dmed, 1) == MACRO["fed_dot_2026"]))
    # DATED EVENTS STAY BOUND TO THE PROSE THAT NARRATES THEM.
    # The date must sit BESIDE the restart, not anywhere in the note: the first
    # version passed a mutated 21 Sep restart because the note mentions "the 21st"
    # for an unrelated reason further on.
    _geo_note = next(d[3] for d in DRIVERS if d[0].startswith("Geopolitics"))
    _ri = _geo_note.find("restarted the")
    checks.append(("the Petroline restart and first Yanbu cargo are in order and "
                   "narrated on the date they carry",
                   MACRO["petroline_restart"] <= MACRO["yanbu_first_cargo"] <= AS_OF
                   and _ri > 0 and any(f in _geo_note[max(0, _ri - 120):_ri]
                                       for f in _dayforms(MACRO["petroline_restart"]))))
    # Every vessel count the geopolitics note quotes carries its own date: Lloyd's
    # 14/day (week to 23 Aug) sat undated for a month beside a 13 Sep PortWatch figure,
    # and a "fivefold disagreement" between readings a month apart is partly just time.
    _li = _geo_note.find("Lloyd's")
    checks.append(("the Lloyd's vessel count is quoted beside its own date",
                   _li > 0 and any(f in _geo_note[_li:_li + 90]
                                   for f in _dayforms(MACRO["hormuz_lloyds_asof"]))))
    _mon_note = next(d[3] for d in DRIVERS if d[0].startswith("Monetary"))
    # THE NOTE'S 10-YEAR RUN IS THE SERIES, DATE BY DATE. Added 2026-09-26 after the
    # 23rd was confirmed at 5.12 and the note went on saying "5.11% on the 23rd":
    # the parenthetical beside it was edited, the figure was not, and nothing tied
    # the sentence to ust_10y_history. Every "X.XX% on the Nth" in this note that
    # names a day in the series must carry that day's close.
    # Day-of-month keys (the prose names days that way); a day number that occurs
    # twice in the series - it will once the series crosses a month end - is
    # ambiguous and is dropped rather than guessed. Shared with the bp check below.
    _days = [_dt.date.fromisoformat(d).day for d, _ in MACRO["ust_10y_history"]]
    _uniq = {x for x in _days if _days.count(x) == 1}
    _uh_by_day = {_dt.date.fromisoformat(d).day: v for d, v in MACRO["ust_10y_history"]
                  if _dt.date.fromisoformat(d).day in _uniq}
    _mon_run = (re.findall(r"(\d\.\d\d)% on the (\d+)(?:st|nd|rd|th)", _mon_note)
                + re.findall(r"(\d\.\d\d)% on (\d+) Sep", REGIONS["US"]["why"]))
    # A DAILY BASIS-POINT MOVE IS A DIFFERENCE OF TWO CLOSES IN THE SERIES. The
    # growth note said the 10-year "jumped 13bp on 23 Sep" - the market-close
    # basis - while the page's own official series has 4.97 -> 5.12, i.e. 15bp.
    # Any "Nbp on DD Sep" in a note, for a day the series holds, must be that
    # day's change on the series' basis.
    _uh = MACRO["ust_10y_history"]
    _uh_chg = {_dt.date.fromisoformat(d).day: round((v - pv) * 100)
               for (_, pv), (d, v) in zip(_uh, _uh[1:])
               if _dt.date.fromisoformat(d).day in _uniq}
    _bp_claims = [(int(bp), int(dd)) for t in _notes_all
                  for bp, dd in re.findall(r"(\d+)bp on (\d+) Sep", t)]
    checks.append(("every daily 10-year bp move quoted in a note is the series' own change",
                   all(_uh_chg.get(dd, bp) == bp for bp, dd in _bp_claims)))
    checks.append(("every 10-year close the Monetary and US notes list matches the series on its date",
                   len(_mon_run) >= 3 and all(abs(float(v) - _uh_by_day[int(dd)]) < 1e-9
                                              for v, dd in _mon_run if int(dd) in _uh_by_day)))
    checks.append(("the superseded 10-year peak is older and lower, and quoted as it was",
                   MACRO["ust_10y_peak_prev_date"] < MACRO["ust_10y_peak_date"]
                   and MACRO["ust_10y_peak_prev"] < MACRO["ust_10y_peak"]
                   # Quoted at its OWN precision: formatting to 2dp would demand
                   # "5.13%" for a 5.135% print - a misquote the check would enforce.
                   and f"{_dayforms(MACRO['ust_10y_peak_prev_date'])[1]} peak of "
                       f"{MACRO['ust_10y_peak_prev']}%" in _mon_note))
    # The 2-year and 30-year are MID-SESSION readings, and are labelled so. The
    # label is only worth something if the prose honours it: a sentence saying
    # the 2-year "closed" at a mid-session print is the exact error that put
    # 4.951 into the 10-year series as Monday's close.
    _mid = "mid-session" in MACRO["ust_curve_basis"]
    checks.append(("no note calls a mid-session 2-year or 30-year reading a close",
                   not _mid or not re.search(r"(2|30)-year (?:closed|close[sd]? at|settled)",
                                             _all_prose)))

    # A WITHHELD SESSION IS A DELIBERATE ACT and has to look like one: it must name
    # a real trading day, at or before the as-of date, that the series does not
    # contain. Otherwise "withheld" drifts into a list nobody maintains.
    for _lbl, _wk, _series in (
            ("VIX", "vix_withheld", [d for d, _ in MACRO["vix_history"]]),
            ("the 10-year", "ust_10y_withheld", [d for d, _ in MACRO["ust_10y_history"]]),
            ("Brent", "brent_withheld", [d for d, _ in MACRO["brent_history"]])):
        for _w in MACRO.get(_wk, []):
            _wd = _dt.date.fromisoformat(_w)
            checks.append((f"{_lbl}'s withheld session {_w} is a weekday "
                           f"at/before the as-of date, and absent from the series",
                           _wd.weekday() < 5 and _wd <= _asof and _w not in _series))

    checks.append(("every VIX close in the series is on a weekday",
                   all(_dt.date.fromisoformat(d).weekday() < 5
                       for d, _ in MACRO["vix_history"])))
    checks.append(("the VIX series is in date order with no duplicates",
                   [d for d, _ in MACRO["vix_history"]]
                   == sorted({d for d, _ in MACRO["vix_history"]})))
    checks.append(("the latest VIX observation is not after the as-of date",
                   _vl <= _dt.date.fromisoformat(AS_OF)))
    # THE VIX'S DIRECTION IS A CLAIM, and the prose made it wrong for three reviews:
    # "fell on the day yields jumped" was a series filed one session late. Any note
    # that says the VIX fell or rose must agree with the sign of the latest move.
    _vdir = re.findall(r"VIX (fell|rose|fall|rise|falling|rising)\b", _all_prose + " "
                       + " ".join(SUMMARY.values()))
    _vup = MACRO["vix_latest_chg_pct"] > 0
    checks.append(("every 'VIX fell/rose' in prose agrees with the latest move's sign",
                   all((w.startswith("r") == _vup) for w in _vdir)))
    # WAS "the December future is above the latest VIX close". The page's wording
    # has been signed by the data since 2026-10-15, so the claim it guarded is gone;
    # on 16 Oct the market crossed it (VIX 19.99 against a December future of 18.55)
    # and the check would have failed on a fact, not a defect. It now guards what
    # matters instead: a strip the market has moved far from is flagged, not hidden.
    _smove = abs(MACRO["vix_latest"] / MACRO["vix_spot"] - 1)
    checks.append((f"a strip the market has moved >{STRIP_OVERTAKEN_PCT:.0f}% from is flagged "
                   f"({_smove * 100:.1f}%)",
                   p["vol_channel"]["overtaken"] == (_smove > STRIP_OVERTAKEN_PCT / 100)))
    # A misdated or intraday value shows up first as an outlier move. 40% is beyond
    # any 2026 session and inside a genuine shock day (Aug 2024 closed +65%).
    _vh = MACRO["vix_history"]
    checks.append(("no VIX close-to-close move in the series exceeds 40% (misdating tripwire)",
                   all(abs(b / a - 1) < 0.40 for (_, a), (_, b) in zip(_vh, _vh[1:]))))
    _vprev = dict(zip([d for d, _ in _vh[1:]], [v for _, v in _vh[:-1]]))
    _vcur = dict(_vh)
    # ON THE LEVEL, not the percentage - the same form as the index chains above.
    # Both closes are rounded to 2dp, so a percentage recomputed from them carries
    # that rounding too; the first version compared it against the reported move
    # at the move's own precision alone, and on 2026-09-26 rejected an internally
    # consistent print: "-5.24% to 14.85" off 15.67 is 14.849, which IS 14.85 - but
    # 14.85 / 15.67 recomputes to -5.23%. (That print later proved to be the wrong
    # close - 14.87 - which is the point: a chain check tests consistency, not
    # truth; the source count settles truth.) The bound is half a unit of the reported move on
    # the implied level plus half a cent for the carried close's own rounding. A
    # misdated close still misses by dollars, not fractions of a cent.
    def _vmove_ok(d, pct):
        _dp = 0 if isinstance(pct, int) else len(repr(pct).split(".")[1])
        return d in _vprev and (abs(_vprev[d] * (1 + pct / 100) - _vcur[d])
                                <= _vprev[d] * 0.5 * 10 ** -_dp / 100 + 0.005 + 1e-9)
    checks.append(("every reported VIX move reproduces from the previous close in the series",
                   all(_vmove_ok(d, pct) for d, pct in MACRO["vix_reported_moves"].items())))
    checks.append(("the latest VIX close carries a reported move (the chain reaches today)",
                   MACRO["vix_latest_date"] in MACRO["vix_reported_moves"]))
    # The Volatility tile prints the intraday extremes beside the range of closes
    # since the series starts, so both must fall inside that window and bracket it.
    _vcl = [v for _, v in _vh]
    checks.append(("the VIX intraday extremes are dated inside the series and bracket its closes",
                   _vh[0][0] <= MACRO["vix_2026_low_date"] <= MACRO["vix_latest_date"]
                   and _vh[0][0] <= MACRO["vix_latest_high_date"] <= MACRO["vix_latest_date"]
                   and MACRO["vix_2026_low"] <= min(_vcl) and MACRO["vix_latest_high"] >= max(_vcl)))
    checks.append(("the latest VIX move reproduces from its own prior close",
                   abs(MACRO["vix_prev_close"] * (1 + MACRO["vix_latest_chg_pct"] / 100)
                       - MACRO["vix_latest"]) < 0.02))
    # FREE CORROBORATION OF THE BOOTSTRAP, and a measurement of what the stale
    # strip costs. VIX3M is a market-published constant-maturity 3-month implied
    # vol; it is not an input here, so comparing it to the model's sigma(0->0.25)
    # tests the forward-variance integration against something it never saw.
    # The two are seven days apart, so the comparison RE-ANCHORS the curve to the
    # spot of the VIX3M date rather than budgeting a tolerance for the mismatch:
    # same t=0, same strip, one number each. The first version compared ratios at
    # different spots inside a 0.10 band and bit on nothing.
    # The bound is one full mis-quote of the strip. Moving every future 10% moves
    # this residual 6.7 points, so +/-10% passes a correct curve, fails a strip
    # priced 10% too low (-11.7%), and fails a flat curve (-14.8%).
    checks.append((f"the bootstrapped 3M vol tracks VIX3M at the same spot "
                   f"({VIX3M_MODEL:.2f} vs {MACRO['vix3m']:.2f}, {VIX3M_RESID:+.2f}%)",
                   abs(VIX3M_RESID) <= VIX3M_BOUND_PCT))
    # A TEST MUST NOT PREDATE WHAT IT TESTS. The 2 Oct strip was checked against a
    # 1 Oct VIX3M - the only pair then available - and matched it to 0.3% while
    # missing 6-7 Oct by over 4%: it fitted the market of the day BEFORE its own
    # date. (Found 2026-10-10.) The VIX3M reading must be on or after the strip's
    # quote date, and on a date the spot series carries at the stated level.
    checks.append(("the VIX3M check is dated on/after the strip it tests, at a carried close",
                   MACRO["vix3m_date"] >= VIX_QUOTE_DATE
                   and dict(MACRO["vix_history"]).get(MACRO["vix3m_date"]) == MACRO["vix3m_spot"]))
    # Was "spot != latest", which guarded a 4 Sep curve against having its t=0
    # swapped for a newer close. With a same-day strip the two are EQUAL by right,
    # so the test is now the one that was always meant: the curve's spot is the
    # carried close on the strip's own quote date.
    checks.append(("the curve's spot is the carried close on the strip's own quote date",
                   VOL_KNOTS[0][1] == MACRO["vix_spot"]
                   and dict(MACRO["vix_history"]).get(VIX_QUOTE_DATE) == MACRO["vix_spot"]))
    checks.append(("the VIX quote date is not after the model as-of date",
                   _q <= _dt.date.fromisoformat(AS_OF)))
    # The strip has an EXPIRY, and nothing said so. It has not been re-quoted since
    # 4 Sep - fifteen days at this review, after nine consecutive days of failing to
    # find a fresh one - and a stale strip ages silently because the spot paired
    # with it ages in lockstep, so every internal consistency check still passes.
    # The bound is one roll window, the same 30 days the contracts themselves are
    # defined on: past that, the front contract this strip was quoted against has
    # settled and been replaced, so the curve describes a set of contracts that no
    # longer exists. Derived from VIX_FWD_WINDOW_D rather than chosen.
    checks.append((f"the VIX strip is younger than one roll window "
                   f"({(_dt.date.fromisoformat(REVIEW_DATE) - _q).days}d of "
                   f"{VIX_FWD_WINDOW_D}d)",
                   (_dt.date.fromisoformat(REVIEW_DATE) - _q).days < VIX_FWD_WINDOW_D))
    checks.append(("every VIX future settles on a Wednesday",
                   all(vix_settlement(y, m).weekday() == 2
                       for _, y, m, _ in MACRO["vix_futs_levels"])))
    checks.append(("every VIX settlement is 30 days before a third Friday",
                   all((vix_settlement(y, m) + _dt.timedelta(days=30)).weekday() == 4
                       and 15 <= (vix_settlement(y, m)
                                  + _dt.timedelta(days=30)).day <= 21
                       for _, y, m, _ in MACRO["vix_futs_levels"])))
    checks.append(("every published maturity reproduces from the settlement rule",
                   all(abs(t - vix_maturity(y, m)) < 5e-5
                       for (_, t, _), (_, y, m, _)
                       in zip(MACRO["vix_futs"], MACRO["vix_futs_levels"]))))
    # A settled contract is not on the curve. The September contract settles
    # 16 September and nothing in this model knew that: maturities are measured to
    # the 30-day window CENTRE, so the front maturity stays positive until 1 October
    # and the existing positivity check would not fire for another two weeks - by
    # which point the bootstrap would have been interpolating through a contract
    # that stopped trading. Checked against REVIEW_DATE, so it fires the day the
    # contract expires rather than a fortnight later. (Audit 2026-09-14.)
    _rev = _dt.date.fromisoformat(REVIEW_DATE)
    _settled = [lbl for lbl, y, m, _ in MACRO["vix_futs_levels"]
                if vix_settlement(y, m) <= _rev]
    checks.append(("no contract on the strip has already settled",
                   not _settled))
    _days_to_front = (vix_settlement(*MACRO["vix_futs_levels"][0][1:3]) - _rev).days
    checks.append((f"front contract has {_days_to_front} days to settlement",
                   _days_to_front > 0))

    checks.append(("maturities are positive and strictly increasing",
                   all(t > 0 for _, t, _ in MACRO["vix_futs"])
                   and all(a[1] < b[1] for a, b
                           in zip(MACRO["vix_futs"], MACRO["vix_futs"][1:]))))

    # ---- the FX drift bracket ----------------------------------------------
    # FX_DRIFT moves three of the four sleeves, so it must stay inside the two
    # inflation differentials this model already carries: the long-run PPP anchor
    # below it and the current print above it. Its old comment claimed a pure PPP
    # derivation that computed to 1.5 against a constant of 2.0.
    _ppp_lr = FX_PPP_PH_LR - FX_PPP_US_LR
    # Month-matched: September PH (7.2) against September US (3.7). Until
    # 2026-10-15 it paired August with August, the latest month both had.
    _ppp_now = MACRO["ph_cpi_sep"] - MACRO["us_cpi_headline"]
    checks.append((f"FX drift sits between long-run PPP ({_ppp_lr:.1f}) and the "
                   f"current differential ({_ppp_now:.1f})",
                   _ppp_lr <= FX_DRIFT <= _ppp_now))

    # The zero-shock scenario is an identity, not an approximation: no shock and a
    # 1.0 volatility multiplier is the modelled path, so it must reproduce the
    # headline row of the portfolio it describes - CAGR, vol AND drawdown. Only
    # the drawdown ever disagreed, and nothing was checking it. (Audit 2026-09-09.)
    # Each portfolio's zero-shock row is its OWN headline (v80): A's on the 10-year view.
    _own = lambda q: q["ten"] if q["column"] == "net_10y" else q["macro"]
    for lab, port, scens in [("baseline", p["baseline"]["under_macro"], p["baseline"]["scenarios"])] + [
            (f"Portfolio {x.upper()}", _own(p[f"portfolio_{x}"]), p[f"portfolio_{x}"]["scenarios"])
            for x in "abc"]:
        base_row = next((x for x in scens if x["name"].startswith("Grind")), None)
        checks.append((f"{lab} zero-shock scenario reproduces the headline row",
                       base_row is not None
                       and abs(base_row["cagr"] - port["cagr"]) < 0.011
                       and abs(base_row["vol"] - port["vol"]) < 0.011
                       and abs(base_row["maxdd"] - port["maxdd"]) < 0.06))
    # and every scenario drawdown must carry the same horizon scaling as the rest
    # Every scenario row must reproduce from ITS OWN printed figures and the
    # published k - the guarantee check B makes for the fund table.
    #
    # This began as a derived-tolerance bound: half a unit in the last published
    # place of each input, propagated through d = (k*v - 0.50*r)*scalar. That bound
    # is correct and useless. As k is published less precisely its error term grows,
    # so the tolerance grows in lockstep with the error it is meant to police - the
    # check can never fail on precision, which is exactly what it was added to
    # catch. Three bite tests passed in a row before that became obvious.
    #
    # The honest question is not "is the error inside a bound I derived" but "does a
    # reader reconstructing from the published row land on the printed number". That
    # is asserted directly, with no tolerance to get wrong. (Audit 2026-09-14.)
    checks.append(("every scenario drawdown of A and B reproduces from its own printed row",
                   all(round(-max((p["dd_model"][f"{x_}_k"] * x["vol"] - DD_MU * x["cagr"])
                                  * DD_HORIZON_SCALAR, 0.0), 1) == x["maxdd"]
                       for x_ in "abc" for x in p[f"portfolio_{x_}"]["scenarios"])))
    # THE SAME QUESTION, asked of the four headline rows. It was only ever asked of
    # the scenarios, and the headline rows reached the reader's answer by luck: the
    # baseline under macro came out -29.0019 raw against -29.0080 by the reader's
    # route, 0.006pp from rounding to different tenths.  (Audit 2026-09-20.)
    _hd_rows = [(p["baseline"]["base"], p["dd_model"]["baseline_k"]),
                (p["baseline"]["under_macro"], p["dd_model"]["baseline_k"])] + [
               (p[f"portfolio_{x_}"][r_], p["dd_model"][f"{x_}_k"]) for x_ in "abc" for r_ in ("base", "macro")]
    checks.append(("every headline drawdown reproduces from its own printed row",
                   all(round(-max((_k * x["vol"] - DD_MU * x["cagr"])
                                  * DD_HORIZON_SCALAR, 0.0), 1) == x["maxdd"]
                       for x, _k in _hd_rows)))
    checks.append(("every driver score is reported in 1-5",
                   all(1 <= d["score"] <= 5 for d in p["drivers"])))
    checks.append(("every driver rescale 1-10 -> 1-5 is exact",
                   all(abs(d["score"] - to5(d["score_10"])) < 1e-9 for d in p["drivers"])))
    # Tolerance DERIVED, not picked. Each reported score is to5() rounded to 2dp
    # (+-0.005) and the weights sum to 1, so the composite carries up to 0.005 of
    # rounding; the gauge itself rounds at 2dp for another 0.005. Bound = 0.010.
    # The hand-picked 0.006 that stood here passed only because the scores happened
    # to round favourably - it failed the moment a driver moved to 1.25, on an error
    # of 0.0065 that is well inside what the published precision permits. Second
    # time a hand-picked tolerance has been the defect rather than the check.
    _comp_bound = sum(d["weight"] for d in p["drivers"]) * 0.005 + 0.005
    checks.append(("the weighted composite of the reported driver scores is the gauge",
                   abs(sum(d["weight"] * d["score"] for d in p["drivers"]) - p["gauge"])
                   <= _comp_bound))
    checks.append(("driver weights still sum to 1 after the rescale",
                   abs(sum(d["weight"] for d in p["drivers"]) - 1.0) < 1e-9))
    checks.append(("every regional score is reported in 1-5",
                   all(1 <= v[h] <= 5 for v in p["regions"].values()
                       for h in HZ_KEYS + ("blend",))))
    # The four HORIZON scores are to5() of their research values. The BLEND is not,
    # and deliberately so since 2026-09-20: it is the horizon-weighted average of
    # the printed scores, because that is the arithmetic a reader does. Asserting
    # to5(blend_10) here would re-impose the route that printed 3.15 over a page
    # showing 3.14.
    checks.append(("every regional rescale 1-10 -> 1-5 is exact",
                   all(abs(v[h] - to5(v[h + "_10"])) < 1e-9
                       for v in p["regions"].values()
                       for h in HZ_KEYS)))
    checks.append(("every regional blend reproduces from the scores printed beside it",
                   all(v["blend"] == round(sum(v[h] * w for h, w in HZ_W.items()), 2)
                       for v in p["regions"].values())))
    checks.append(("regional blend is horizon-weighted on the research scale",
                   all(abs(v["blend_10"] - sum(v[h + "_10"] * w
                                               for h, w in HZ_W.items())) < 0.006
                       for v in p["regions"].values())))
    checks.append(("the 1-5 tilt coefficient equals the 1-10 one rescaled",
                   abs(REGIONAL_TILT_PER_PT - 0.30 * 9 / 4) < 1e-9))
    # Horizon consistency. On 8 Sep the mandate moved 5y -> 10y; these assert the
    # horizon is one number everywhere rather than a label that drifted from the
    # maths behind it.
    dm = p["dd_model"]
    checks.append(("the volatility term structure's long point is the mandate horizon",
                   p["vol_ts"][-1]["label"] == HZ_LABEL
                   and abs(p["vol_ts"][-1]["years"] - HORIZON_Y) < 1e-9))
    checks.append(("the horizon blend's long bucket is the mandate horizon",
                   HZ_LABEL in p["hz_weights"] and list(p["hz_weights"]) == list(HZ_KEYS)
                   and list(HZ_KEYS)[-1] == HZ_LABEL))
    checks.append(("horizon blend weights sum to 1",
                   abs(sum(p["hz_weights"].values()) - 1.0) < 1e-9))
    # Asserted, not commented: a long mandate must not be run off near-term signal.
    checks.append(("the mandate-horizon bucket carries at least half the blend",
                   p["hz_weights"][HZ_LABEL] >= 0.50 - 1e-9))
    checks.append(("no single sub-year bucket outweighs the mandate horizon",
                   all(v <= p["hz_weights"][HZ_LABEL] + 1e-9
                       for k, v in p["hz_weights"].items() if k != HZ_LABEL)))
    # THE UNIVERSE IS THE COMPLETE GRID UNDER THE LIMITS, counted a second way: each
    # fund 0..max_w in 5% steps, cash at least min_cash, the units summing to 20. A
    # limit left behind in the filter, or one dropped from it, changes the count.
    # Counted by dynamic programme over (units used, funds held), fund by fund - not by
    # walking the grid, which over eleven funds is 8^11 points (it hung the first run
    # of v63, 2026-10-22).
    _lim = p["universe"]["limits"]; _mx = _lim["max_w"] // 5
    _dp = {(0, 0): 1}
    for _i in range(len(UNIV_IDS)):
        _lo = _lim["min_cash"] // 5 if _i == 0 else 0
        _nx = {}
        for (_t, _h), _c in _dp.items():
            for _x in range(_lo, _mx + 1):
                if _t + _x <= 20 and _h + (1 if _x else 0) <= _lim["max_funds"]:
                    _key_ = (_t + _x, _h + (1 if _x else 0))
                    _nx[_key_] = _nx.get(_key_, 0) + _c
        _dp = _nx
    _cnt = sum(_c for (_t, _h), _c in _dp.items() if _t == 20)
    checks.append((f"the universe enumeration is the complete 5% grid under the limits ({_cnt} mixes)",
                   p["universe"]["n_total"] == _cnt))
    # Every frontier point is efficient: no limit-respecting mix has at least its
    # CAGR at no more drawdown. And B is ON it, as the chart draws it.
    # (each drawdown bucket's best CAGR dominates every mix in it, so the buckets stand
    # in for all 322,000-odd mixes)
    _allp = [(m[0], abs(m[1])) for m in _FRONT_BUCKET.values()]
    checks.append(("every universe frontier point is efficient (no mix beats it on both axes)",
                   all(not any(c >= f["cagr"] + 1e-9 and d <= abs(f["dd"]) + 1e-9 for c, d in _allp)
                       for f in p["universe"]["frontier"])))
    checks.append(("Portfolio B is a frontier point",
                   any([round(x) for x in f["weights"]] == p["portfolio_b"]["weights"]
                       for f in p["universe"]["frontier"])))
    _br = p["universe"]["best_ratio"]
    checks.append(("the universe's best pure ratio is the highest ret/DD of any limit-respecting mix",
                   _br["ret_per_dd"] == _BEST_RATIO_M[0]
                   and _br["ret_per_dd"] == round(_br["cagr"] / abs(_br["maxdd"]), 3)
                   and all(m[0] / abs(m[1]) <= _br["ret_per_dd"] + 0.0005 for m in _FRONT_BUCKET.values() if m[1])))
    # THE REPORT'S SECTION 4 IS TYPED, so its claims are asserted here: the heading
    # "Global Technology: the deepest drawdown, the smallest weight" and the bullets
    # "the most rate-sensitive holding" and "the deepest expected drawdown on the
    # sheet". "The highest return" was in the heading until 2026-10-15, when the
    # 1.15% -> 1.50% trust-fee correction put Asia Equity's net forecast above it;
    # the page now states the rank from the data instead of typing it.
    # (The "smallest weight" claim left the heading with the four-fund optimum it
    # described, v62. "The deepest drawdown" left it on 2026-10-22, when Global Consumer
    # Trends joined the universe deeper still: the page now states the rank from the
    # data. The claim still typed - the most rate-sensitive - is tested across all funds.)
    _five = p["funds"] + p["portfolio_b"]["funds"]
    _gt = next(f for f in _five if f["id"] == "ATRGTEC")
    checks.append(("the Report's typed Global Technology claim still holds across every fund "
                   "(the most rate-sensitive)",
                   all(_gt["tilt_rates"] <= f["tilt_rates"] for f in _five)))
    # The what-if helper must BE the rule: on the live column it has to return the
    # published B, or its counterfactuals answer a different question.
    _live = _wi_entry("live")
    checks.append(("the what-if helper reproduces the published B on live inputs",
                   _live["b"]["weights"] == p["portfolio_b"]["weights"]
                   and _live["a"]["cagr"] == p["portfolio_a"]["ten"]["cagr"]))
    checks.append(("each what-if column differs from the live one by exactly the tilt it removes",
                   all(abs(f2["net_macro"] - f2["net_novol"] - f2["tilt_vol"]) < 0.0051
                       and abs(f2["net_macro"] - f2["net_neutral"] - f2["tilt_rates"]
                               - f2["tilt_energy"]) < 0.0051
                   and abs(f2["net_macro"] - f2["net_notrend"] - f2["tilt_trend"]) < 0.0051
                   and abs(f2["net_macro"] - f2["net_asia_fee_hi"]
                           - (p["universe"]["what_if"]["asia_fee_hi"]["stress_pp"]
                              if f2["id"] == "ATRASEQ" else 0.0)) < 0.0051
                   for f2 in p["funds"] + p["portfolio_b"]["funds"])))
    checks.append(("every region is scored at the mandate horizon",
                   all(HZ_LABEL in v for v in p["regions"].values())))
    checks.append(("the drawdown horizon scalar is sqrt(horizon / calibration window)",
                   abs(dm["horizon_scalar"] - math.sqrt(dm["horizon_y"] / dm["calib_y"]))
                   < 5e-5))
    checks.append(("the drawdown scalar is >1 for a horizon longer than the calibration",
                   (dm["horizon_scalar"] > 1) == (dm["horizon_y"] > dm["calib_y"])))
    checks.append(("peso terminal value compounds over the mandate horizon",
                   all(abs(1_000_000 * (1 + p[f"portfolio_{x_}"]["macro"]["cagr"] / 100) ** HORIZON_Y
                           - p[f"portfolio_{x_}"]["macro"]["terminal_1m"]) < 1.0 for x_ in "abc")))
    # The drawdown card publishes a formula. These assert the formula, using the
    # coefficients the page prints, reproduces the drawdowns the page prints -
    # the audit that was missing when 1.65 was shown as if it applied to every
    # sleeve while three of four actually used a different k. (Audit 2026-09-05.)
    # Tolerance is DERIVED, not guessed: the check reads the page's rounded values,
    # so the bound is the drawdown's own display rounding (1dp -> 0.05) plus the
    # error each rounded input contributes through the formula. Picking a round
    # number here is how a check gets quietly loosened until it stops biting -
    # this one fired on 7 Sep at a real 0.0614 and the bound below is why.
    def dd_tol(k, mu_coef, vol_dp=0.005, k_dp=0.0, ret_dp=0.005):
        hs = p["dd_model"]["horizon_scalar"]
        return 0.05 + (k * vol_dp + k_dp + mu_coef * ret_dp) * hs
    for fd in p["funds"]:
        if fd["id"] == "ATRPHMM":
            continue
        pred = ((fd["dd_k"] * fd["vol"] - p["dd_model"]["mu_coef"] * fd["net_macro"])
                * p["dd_model"]["horizon_scalar"])
        checks.append((f"{fd['id']} drawdown reproduces from its published k",
                       abs(-pred - fd["dd_macro"])
                       <= dd_tol(fd["dd_k"], p["dd_model"]["mu_coef"])))
    checks.append(("every fund's drawdown coefficient carries a stated reason",
                   all(len(fd.get("dd_k_why", "")) > 30 for fd in p["funds"])))
    for lab, mm, kk in [("baseline", p["baseline"]["under_macro"], p["dd_model"]["baseline_k"])] + [
            (f"Portfolio {x_.upper()}", p[f"portfolio_{x_}"]["macro"], p["dd_model"][f"{x_}_k"]) for x_ in "abc"]:
        pred = ((kk * mm["vol"] - p["dd_model"]["mu_coef"] * mm["cagr"])
                * p["dd_model"]["horizon_scalar"])
        # portfolio k is published to 3dp, so it contributes vol * 0.0005
        checks.append((f"{lab} drawdown reproduces from its published k",
                       abs(-pred - mm["maxdd"])
                       <= dd_tol(kk, p["dd_model"]["mu_coef"],
                                 k_dp=mm["vol"] * 0.0005)))
    for lab, w, kkey in [("baseline", BASELINE_W, "baseline_k")] + [
            (f"Portfolio {x_.upper()}", [x / 100 for x in p[f"portfolio_{x_}"]["weights"]], f"{x_}_k") for x_ in "abc"]:
        eq = [(w[i], _five[i]["dd_k"]) for i in range(len(w))
              if not UNIV[1][i]["cash_like"]]
        avg = sum(x * kx for x, kx in eq) / sum(x for x, _ in eq)
        # Bound derived from how precisely k is PUBLISHED, which changed on
        # 2026-09-14 from 3dp to 5dp. The 0.006 that stood here was set when the
        # figure printed at 3dp and was left behind by that change - against a 5dp
        # value it is roughly 1200x looser than the arithmetic warrants, so it would
        # have passed a materially wrong weighted average. A tolerance is only as
        # good as the precision it was derived from, and it must move with it.
        _k_pub = p["dd_model"][kkey]
        _k_dec = len(repr(float(_k_pub)).split(".")[1].rstrip("0")) if "." in repr(float(_k_pub)) else 0
        checks.append((f"{lab} portfolio k is the ex-cash weighted average of the sleeve k's",
                       abs(avg - _k_pub) <= 0.5 * 10 ** (-_k_dec) + 1e-12))
    checks.append(("every fund net CAGR is below its gross", 
                   all(f["net_base"] < f["gross_php"] for f in p["funds"])))
    lt = p["lookthrough"]
    checks.append((f"look-through recorded for all {len(UNIV_IDS)} funds, Global Dividend included",
                   set(lt) == {f["id"] for f in FUNDS + ADD_FUNDS}))
    checks.append(("the Global Dividend mix is the target fund's country weights, renormalised",
                   abs(sum(GDIV_MIX.values()) - 1) < 1e-9
                   and all(abs(GDIV_MIX[r] - _GG[r] / sum(_GG.values())) < 0.0015 for r in _GG)
                   and LOOKTHROUGH["ATRGLDV"]["geo"] == [list(x) for x in GDIV_GEO["EUROPE"][:3]]))
    checks.append(("look-through gaps are declared, not fabricated",
                   all(v["kind"] == "gap" or v["rows"] for v in lt.values())))
    checks.append(("JEPQ top-10 weights are plausible (sum 30-60%)",
                   30 <= sum(r[1] for r in lt["ATRQIAP"]["rows"]) <= 60))
    # regression: peso figures must be reproducible from the displayed numbers
    def _ties(m):
        return (abs(1_000_000 * (1 + m["cagr"] / 100) ** HORIZON_Y - m["terminal_1m"]) < 1.0
                and abs(1_000_000 * (1 + m["maxdd"] / 100)
                        - m["worst_1m_from_open"]) < 1.0)
    vc = p["vol_channel"]
    checks.append(("the volatility tilt's reference is the long-run level every base assumes",
                   vc["ramp_ref"] == "long-run"
                   and abs(vc["blend"] - vc["longrun"] - vc["ramp"]) < 0.011))
    checks.append(("every volatility tilt is derived from the ramp, not hand-set",
                   all(abs(f2["tilt_vol"] - rnd(vc["ramp"] * vc["sens"][f2["id"]])) < 1e-9
                       for f2 in p["funds"])))
    # THE DRIVERS REACH THE RETURNS. The check that was missing for three weeks
    # is not "are the tilts plausible" - constant tilts are perfectly plausible -
    # but "does a driver score MOVE them". Each tilt must reproduce from its
    # calibration anchor and the driver score as PUBLISHED in the drivers list, so
    # editing a driver without the tilts following, or reverting a tilt to a typed
    # constant, both fail here.
    # Since 2026-10-26 the reading is each driver's horizon path averaged with the
    # published horizon weights, re-derived here from the published path.
    _dp = {d["name"]: round(sum(d["path"][h] * w for h, w in p["hz_weights"].items()), 2)
           for d in p["drivers"]}
    def _toward(seq, neu):
        """Each step moves toward neutral or holds, and never crosses it."""
        return all(min(x, neu) <= y <= max(x, neu) for x, y in zip(seq, seq[1:]))
    checks.append(("every driver's path moves from its reading now toward neutral, ends neutral, and averages as published",
                   all(_toward([d["score_10"]] + [d["path"][h] for h in HZ_KEYS], DRIVER_NEUTRAL_10)
                       and d["path"][HZ_LABEL] == DRIVER_NEUTRAL_10
                       and list(d["path"]) == list(HZ_KEYS) and _dp[d["name"]] == d["blend_10"]
                       and all(1 <= v <= 10 for v in d["path"].values()) and d["path_why"]
                       for d in p["drivers"])))
    checks.append(("the gauge at each horizon is the weighted composite of the driver path, moving from the headline toward neutral",
                   all(abs(p["gauge_path_10"][h] - sum(d["weight"] * d["path"][h] for d in p["drivers"])) < 0.006
                       and p["gauge_path"][h] == to5(p["gauge_path_10"][h]) for h in HZ_KEYS)
                   and _toward([p["gauge"]] + [p["gauge_path"][h] for h in HZ_KEYS], NEUTRAL_5)
                   and p["gauge_blend"] == round(sum(p["gauge_path"][h] * w for h, w in p["hz_weights"].items()), 2)))
    _rs = (_dp["Monetary policy & liquidity"] - DRIVER_NEUTRAL_10) / (TILT_CAL["monetary"] - DRIVER_NEUTRAL_10)
    _es = (_dp["Geopolitics & energy"] - DRIVER_NEUTRAL_10) / (TILT_CAL["geopolitics"] - DRIVER_NEUTRAL_10)
    checks.append(("every rates tilt is transmitted from the Monetary driver",
                   all(f2["tilt_rates"] == rnd(f2["tilt_rates_cal"] * _rs) for f2 in p["funds"])))
    checks.append(("every energy tilt is transmitted from the Geopolitics driver",
                   all(f2["tilt_energy"] == rnd(f2["tilt_energy_cal"] * _es) for f2 in p["funds"])))
    # THE 10-YEAR VIEW (2026-10-26), Portfolio A's column, re-derived from the published
    # 10-year scores: each region's anchor, the curve's years 6-10, the drivers' 10-year
    # readings (neutral, so no rates or energy tilt) and no trend.
    _all_f = p["funds"] + p["portfolio_b"]["funds"]
    def _rs10(f2):
        mix = f2["region_mix"] or {f2["region"]: 1.0}
        return sum(p["regions"][r][HZ_LABEL] * w for r, w in mix.items())
    checks.append(("every fund's 10-year column re-derives from the 10-year scores",
                   all(abs(f2["regional_score_10y"] - round(_rs10(f2), 2)) < 1e-9
                       and f2["tilt_regional_10y"] == rnd((_rs10(f2) - NEUTRAL) * REGIONAL_TILT_PER_PT
                                                          * (f2["equity_share"] if f2["equity_share"] != 1.0 else 1.0)) + 0.0
                       and f2["tilt_vol_10y"] == rnd(vc["ramp_10y"] * vc["sens"][f2["id"]]) + 0.0
                       and f2["tilt_rates_10y"] == 0.0 and f2["tilt_energy_10y"] == 0.0
                       and f2["tilt_total_10y"] == rnd(f2["tilt_regional_10y"] + f2["tilt_vol_10y"])
                       and abs(f2["net_10y"] - round(f2["net_base"] + f2["tilt_total_10y"], 2)) < 0.006
                       for f2 in _all_f)))
    checks.append(("the 10-year view's vol ramp is the curve's years 6-10 against the long run",
                   vc["ramp_10y"] == round(p["vol_ts"][-1]["forward"] - vc["longrun"], 2)))
    # THE FORWARD VOLS reproduce from the printed implied column, segment by segment,
    # and the blend the vol channel reads is their horizon-weighted average.
    _fw_ok, _pv = True, (0.0, 0.0)
    for v in p["vol_ts"]:
        _fw = math.sqrt((v["years"] * v["implied"] ** 2 - _pv[0] * _pv[1] ** 2) / (v["years"] - _pv[0]))
        _fw_ok = _fw_ok and abs(v["forward"] - _fw) < 0.006 and v["from_years"] == _pv[0]
        _pv = (v["years"], v["implied"])
    checks.append(("every forward vol reproduces from the printed implied curve, and the blend is their weighted average",
                   _fw_ok and abs(vc["blend"] - sum(v["forward"] * p["hz_weights"][v["label"]]
                                                    for v in p["vol_ts"])) < 0.006))
    # THE TREND'S FOUR HORIZONS: 1-year momentum on the quarters, 3- and 5-year reversal
    # on the annualised trailing returns, the anchor at neutral - all from printed figures.
    _tr = p["trend"]
    def _trend_ok(v):
        ok = True
        for h in _tr["long"]:
            l, y = h["label"], h["years"]
            zz = round(math.sqrt(y) * (math.log(1 + v["ret"][l] / 100) - math.log(1 + v["mu"] / 100))
                       / (v["sigma"] / 100), 2)
            ok = ok and v["z"][l] == zz
        zr = round(sum(v["z"][h["label"]] for h in _tr["long"]) / len(_tr["long"]), 2)
        ok = ok and v["z_rev"] == zr
        for h in HZ_KEYS:
            w = _tr["w"][h]
            want = (round(min(5.0, max(1.0, 3.0 + w["mom"] * v["z"]["1Y"] - w["rev"] * _tr["reversal"] * zr)), 2)
                    if h in _tr["views"] else _tr["anchor"])
            ok = ok and v["score"][h] == want
        ok = ok and v["score"][HZ_LABEL] == _tr["anchor"] and list(v["score"]) == list(HZ_KEYS)
        return ok and v["blend"] == round(sum(v["score"][h] * w for h, w in p["hz_weights"].items()), 2)
    checks.append(("every trend view is scored by its years of momentum and reversal, neutral at 10, from its printed returns",
                   all(_trend_ok(v) for v in list(_tr["sleeves"].values()) + list(_tr["alt_built"].values()))
                   and all(set(v["ret"]) == {"1Y", "3Y", "5Y"} for v in _tr["sleeves"].values())))
    _tds = [d_ for v in _tr["sleeves"].values() for d_ in v["trail_date"].values() if d_]
    checks.append(("every dated trailing return is on or before the as-of date and under 75 days old",
                   all(set(v["trail_date"]) == {"3Y", "5Y"} for v in _tr["sleeves"].values())
                   and all(0 <= (_dt.date.fromisoformat(AS_OF) - _dt.date.fromisoformat(d_)).days <= 75
                           for d_ in _tds)))
    checks.append(("the trend's momentum and reversal shares are the years each view covers: 3Y 1/3 and 2/3, 5Y all reversal, 10Y neither",
                   _tr["w"] == {"3Y": {"mom": 0.3333, "rev": 0.6667}, "5Y": {"mom": 0.0, "rev": 1.0},
                                HZ_LABEL: {"mom": 0.0, "rev": 0.0}} and _tr["views"] == ["3Y", "5Y"]))
    checks.append(("the horizon weights are each view's share of the ten years and sum to 1",
                   p["hz_weights"] == {"3Y": 0.3, "5Y": 0.2, HZ_LABEL: 0.5}
                   and abs(sum(p["hz_weights"].values()) - 1) < 1e-9))
    checks.append(("every fund's tilt column adds up to its published total",
                   all(rnd(f2["tilt_regional"] + f2["tilt_vol"] + f2["tilt_rates"]
                             + f2["tilt_energy"] + f2["tilt_trend"]) == f2["tilt_total"]
                       for f2 in p["funds"])))
    # ---- the market-trend channel (added 2026-10-07) ----
    _tr = p["trend"]
    _end = _dt.date.fromisoformat(_tr["end"])
    checks.append(("the trend window ends on the last month-end before the as-of date",
                   (_end + _dt.timedelta(days=1)).day == 1
                   and _end < _dt.date.fromisoformat(AS_OF)
                   and (_end + _dt.timedelta(days=1)).month == _dt.date.fromisoformat(AS_OF).month))
    def _cmp(xs):
        q_ = 1.0
        for x in xs: q_ *= 1 + x / 100
        return (q_ - 1) * 100
    checks.append(("every trend quarter reproduces from its months, where months are given",
                   all(abs(v["quarters"][k] - round(_cmp(m), 2)) < 1e-9
                       for v in _tr["sleeves"].values() for k, m in v["monthly"].items())))
    checks.append(("every trend quarter is within 0.05pp of the index provider's own figure",
                   all(abs(v["quarters"][k] - x) <= 0.05
                       for v in _tr["sleeves"].values() for k, x in v["cross_check"].items())))
    checks.append(("the QQQ 2025 months compound to the published calendar-year 20.77%",
                   abs(_cmp([2.16, -2.70, -7.59, 1.40, 9.18, 6.39, 2.42, 0.95, 5.38]
                            + TREND_INPUTS["ATRQIAP"]["monthly"]["2025Q4"]) - 20.77) < 0.01))
    checks.append(("the IXN Jan-Aug 2026 months compound to the published 28.22% year-to-date",
                   abs(_cmp(TREND_INPUTS["ATRGTEC"]["monthly"]["2026Q1"]
                            + TREND_INPUTS["ATRGTEC"]["monthly"]["2026Q2"]
                            + TREND_INPUTS["ATRGTEC"]["monthly"]["2026Q3"][:2]) - 28.22) < 0.01))
    _ok = True
    for fid, v in _tr["sleeves"].items():
        for h in _tr["horizons"]:
            r_ = round(_cmp([v["quarters"][k] for k in _tr["quarters"][-h["quarters"]:]]), 2)
            z_ = round((math.log(1 + r_ / 100) - h["years"] * math.log(1 + v["mu"] / 100))
                       / (v["sigma"] / 100 * math.sqrt(h["years"])), 2)
            _ok &= (r_ == v["ret"][h["label"]] and z_ == v["z"][h["label"]])
        _ok &= v["score"][HZ_LABEL] == _tr["anchor"] == NEUTRAL_5
        _ok &= v["blend"] == round(sum(v["score"][k] * w for k, w in p["hz_weights"].items()), 2)
        _ok &= v["tilt"] == rnd((v["blend"] - _tr["anchor"]) * _tr["tilt_per_pt"])
        _ok &= abs(v["sigma"] - round(v["beta"] * (p["sp_vol_lt"] - MACRO["variance_risk_premium"]), 2)) < 1e-9
    checks.append(("every trend return, z-score, score, blend and tilt reproduces from the printed figure before it",
                   _ok))
    checks.append(("the trend scheme can never move a sleeve by more than its stated full-signal 0.30pp",
                   all(abs(v["tilt"]) <= 0.30 + 1e-9 for v in _tr["sleeves"].values())))
    # Every fund, all eleven (2026-10-22): its trend market's tilt, at its equity share;
    # none where no series is sourced, and none for cash.
    _all11 = p["funds"] + p["portfolio_b"]["funds"]
    checks.append(("every fund's trend tilt is its market's published tilt at its equity share; cash carries none",
                   all(f2["tilt_trend"] == ((_tr["sleeves"][f2["trend_market"]]["tilt"] if f2["equity_share"] == 1.0
                                             else rnd(_tr["sleeves"][f2["trend_market"]]["tilt"] * f2["equity_share"]) + 0.0)
                                            if f2["trend_market"] else 0.0)
                       for f2 in _all11)
                   and "ATRPHMM" not in _tr["sleeves"]
                   and all(f2["trend_market"] in (None, *_tr["sleeves"]) for f2 in _all11)))
    checks.append(("each trend market's beta is the one its fund's volatility is built on",
                   abs(FUNDS[1]["vol_beta"] - TREND_INPUTS["ATRQIAP"]["beta"] * JEPQ_VOL / NDX_VOL) < 1e-12
                   and abs(FUNDS[2]["vol_beta"] - TREND_INPUTS["ATRASEQ"]["beta"] * 0.92) < 1e-12
                   and abs(FUNDS[3]["vol_beta"] - TREND_INPUTS["ATRGTEC"]["beta"]) < 1e-12
                   and abs(ADD_FUNDS[_ADD_IX["ATRGHCP"]]["vol_beta"] - TREND_INPUTS["ATRGHCP"]["beta"]) < 1e-12
                   and abs(ADD_FUNDS[_ADD_IX["M_GEO"]]["vol_beta"] - TREND_INPUTS["M_GEO"]["beta"] * 1.15) < 1e-12))
    checks.append(("the covered-call sleeve is the one most paid when the curve sits above long-run",
                   max(p["funds"], key=lambda f2: f2["tilt_vol"])["id"] == "ATRQIAP"
                   or vc["ramp"] <= 0))
    # EVERY GROSS RETURN REPRODUCES FROM ITS NAMED COMPONENTS, and every component
    # it uses is quoted in its own note. The typed-7.2 defect is exactly the case
    # this catches: a number that its documented recipe does not produce.
    _M = MACRO
    _recipes = {
        "ATRQIAP": ((_M["ltcma_us_eq"] + _M["ndx_growth_premium"]) * _M["qiap_capture"] / 100
                    + _M["qiap_premium_lr"],
                    [_M["qiap_capture"], _M["qiap_premium_lr"], _M["ltcma_us_eq"], _M["ndx_growth_premium"]]),
        "ATRASEQ": (_M["ltcma_em_eq"] + _M["asia_rerating"] - _M["asia_div_drag"],
                    [_M["ltcma_em_eq"], _M["asia_rerating"], _M["asia_div_drag"]]),
        "ATRGTEC": (_M["ltcma_us_eq"] + _M["tech_growth_premium"] - _M["tech_derating"],
                    [_M["ltcma_us_eq"], _M["tech_growth_premium"], _M["tech_derating"]]),
        # the six added 2026-10-22: global equity with no sector premium, and the two
        # multi-asset blends from their legs
        **{k: (_M["ltcma_global_eq"], [_M["ltcma_global_eq"]]) for k in ("ATRGHCP", "M_GINF", "M_GEO", "M_GCT")},
        "ATRAMIP": (0.5 * (_M["ltcma_em_eq"] + _M["asia_rerating"] - _M["asia_div_drag"]) + 0.5 * _M["ltcma_us_ig"],
                    [_M["ltcma_em_eq"], _M["asia_rerating"], _M["asia_div_drag"], _M["ltcma_us_ig"]]),
        "M_GALL": (0.6 * _M["ltcma_global_eq"] + 0.4 * _M["ltcma_global_agg"],
                   [_M["ltcma_global_eq"], _M["ltcma_global_agg"]]),
    }
    _fsrc = {f2["id"]: f2 for f2 in FUNDS + ADD_FUNDS}
    checks.append(("every equity gross return reproduces from its named components",
                   all(abs(_fsrc[k]["gross_usd"] - v) < 0.005 for k, (v, _) in _recipes.items())))
    checks.append(("every component of a gross return is quoted in that fund's note",
                   all(all(f"{c}%" in _fsrc[k]["gross_note"] for c in comps)
                       for k, (_, comps) in _recipes.items())))
    checks.append(("no base return credits volatility rising from spot (counted once, in the tilt)",
                   not any(re.search(r"implied vol rises|as vol rises|->\s*19", f2["gross_note"])
                           for f2 in FUNDS)))
    checks.append(("peso figures reconcile with the displayed CAGR and drawdown",
                   _ties(p["baseline"]["under_macro"])
                   and all(_ties(p[f"portfolio_{x_}"][r_]) for x_ in "abc" for r_ in ("macro", "base"))))
    # regression: no feasible portfolio may exceed the stated drawdown budget
    cap = p["portfolio_b"]["dd_cap"]
    # Each pick on the column it was CHOSEN on, by the raw route: A on the 10-year view
    # since v68 (this read the long-run column, A's before then, until v77), B on the macro
    # view. On another column a pick may sit outside; the page says so from in_budget.
    checks.append(("no pick exceeds the drawdown budget on the column it was chosen on",
                   abs(port_dd(PA_W, "net_10y", UNIV)) <= DD_CAP + 1e-9
                   and abs(port_dd(PB_W, "net_macro", UNIV)) <= DD_CAP + 1e-9
                   and abs(port_dd(PC_W, "net_macro", UNIV)) <= DD_CAP + 1e-9))
    # FEASIBILITY MUST MEAN THE SAME THING ON BOTH ROUTES. The constraint is tested
    # on the true drawdown, deliberately; the page prints the reader-reproducible
    # one. Nothing had been asserting that a portfolio admitted by the first is not
    # shown breaching the cap by the second. They agree today, but only because the
    # two routes happen to land the same side of every boundary - the same
    # coincidence that let the headline rows reconcile by luck.
    checks.append(("every feasible portfolio respects the cap on the PUBLISHED "
                   "drawdown too",
                   all(abs(m[1]) <= DD_CAP + 1e-9 and abs(m[2]) <= DD_CAP + 1e-9
                       for x in _PK for m in _PK[x].band)))
    # The published cap must BE the enforced cap. Publishing a rounded, looser
    # figure made this very check unable to bite: it read the published 26.0
    # while the optimiser enforced 25.97. (Audit 2026-09-08.)
    checks.append(("the published drawdown cap is the one actually enforced, the same for A, B and C",
                   abs(cap - DD_CAP) < 5e-9
                   and p["portfolio_a"]["dd_cap"] == p["portfolio_b"]["dd_cap"] == p["portfolio_c"]["dd_cap"]))
    # THE OWNER'S BUDGET (v75): 25%, enforced on every pick; the derivation it replaced is
    # published beside it, and a reader can still rebuild that from the reference baseline.
    checks.append(("the budget is the band's recommended step from the owner's 25% base, the one enforced, dated",
                   cap == p["dd_budget"]["cap"] == p["dd_gauge"]["recommended_cap"] == DDG_RECOMMENDED
                   and p["dd_budget"]["base"] == 25.0 == DD_BUDGET_OWNER and p["dd_budget"]["source"] == "band"
                   and p["dd_budget"]["date"] <= p["dd_budget"]["band_date"] <= AS_OF))
    # MAXIMUM GROWTH (v77): each pick is the highest net CAGR its budget allows - nothing
    # feasible prints a higher CAGR on its column.
    checks.append(("A and B are the highest net CAGR the budget allows on their own column (no tie tolerance)",
                   PIN_TIE_PP == 0.0 == p["universe"]["tie_pp"]
                   and _PK["a"].best == p["portfolio_a"]["ten"]["cagr"] and _PK["b"].best == p["portfolio_b"]["macro"]["cagr"]))
    checks.append(("the derived reference it replaced is the baseline's macro drawdown less the stated improvement",
                   abs(p["dd_budget"]["derived_ref"] - round(abs(p["baseline"]["under_macro"]["maxdd"])
                                                              - DD_BUDGET_IMPROVEMENT, 2)) < 5e-9
                   and abs(DD_BUDGET_IMPROVEMENT - round(2.0 * p["dd_model"]["horizon_scalar"], 2)) < 5e-9))
    # THE BUDGET GAUGE (v75): every part re-derived from the published inputs it reads.
    _dg = p["dd_gauge"]
    checks.append(("the budget gauge's parts are the published driver gauge, forward vol and trend scores at each view",
                   all(_dg["parts"][h]["macro"] == p["gauge_path"][h]
                       and _dg["parts"][h]["trend"] == round(sum(v["score"][h] for v in p["trend"]["sleeves"].values())
                                                             / len(p["trend"]["sleeves"]), 2)
                       and _dg["parts"][h]["vol"] == round(min(5.0, max(1.0, 3.0 - (
                           next(v["forward"] for v in p["vol_ts"] if v["label"] == h) / p["macro"]["vix_longrun"] - 1)
                           / _dg["vol_step"])), 2)
                       and _dg["parts"][h]["reading"] == round((_dg["parts"][h]["macro"] + _dg["parts"][h]["vol"]
                                                               + _dg["parts"][h]["trend"]) / 3, 2)
                       for h in HZ_KEYS)))
    checks.append(("the budget gauge reads the 3- and 5-year views by their share of the first five years, the 10-year anchor shown but not weighted",
                   _dg["views"] == ["3Y", "5Y"] and _dg["w"] == {"3Y": 0.6, "5Y": 0.4}
                   and _dg["value"] == round(sum(_dg["parts"][h]["reading"] * _dg["w"][h] for h in _dg["views"]), 2)
                   and 1.0 <= _dg["value"] <= 5.0 and HZ_LABEL in _dg["parts"]))
    _bands = _dg["bands"]
    checks.append(("the gauge's bands tile 1-5 without a gap, step 1pp from 24% to 27%, and hold at the owner's 25%",
                   _bands[0]["lo"] == 1.0 and _bands[-1]["hi"] == 5.0
                   and all(a["hi"] == b["lo"] for a, b in zip(_bands, _bands[1:]))
                   and [b["cap"] for b in _bands] == [24.0, 25.0, 26.0, 27.0]
                   and any(b["cap"] == p["dd_budget"]["base"] and b["lo"] <= 3.0 < b["hi"] for b in _bands)
                   and _dg["band"]["lo"] <= _dg["value"] < _dg["band"]["hi"] + (1e-9 if _dg["band"]["hi"] == 5.0 else 0)))
    # runbook 107: a weighted view that is neutral by construction pins the gauge inside
    # its outer bands. Drive the weighted views to 1 and to 5, the 10-year held where it is.
    _ext = lambda v: round(sum((v if h != HZ_LABEL else _dg["parts"][h]["reading"]) * w
                               for h, w in _dg["w"].items()), 2)
    checks.append(("every band of the gauge is reachable: the weighted views at 1 and at 5 cross the 24% and 27% bands",
                   _ext(1.0) < _bands[0]["hi"] and _ext(5.0) >= _bands[-1]["lo"]))
    _gd = {g["name"]: g for g in _dg["guards"]}
    _rz = _dg["band"]["cap"] > p["dd_budget"]["base"]
    _okstep = all(g["ok"] for g in _dg["guards"] if g["applies_to"] == "any step" or (_rz and g["applies_to"] == "raise"))
    checks.append(("the recommendation follows the band only when every guard that applies is clear, never past 27% or the derived reference",
                   _gd["geopolitics"]["ok"] == (_gd["geopolitics"]["reading"] > _gd["geopolitics"]["floor"])
                   and _gd["vix"]["ok"] == (p["macro"]["vix_latest"] <= p["macro"]["vix_longrun"])
                   and _gd["persistence"]["ok"] == (_gd["persistence"]["reviews"] >= _gd["persistence"]["needed"]
                                                    and _gd["persistence"]["ok"])
                   and _dg["recommended_cap"] == (_dg["band"]["cap"] if _okstep else p["dd_budget"]["base"])
                   and _dg["recommended_cap"] <= 27.0 <= p["dd_budget"]["derived_ref"] + 0.05))
    _alt = _dg["alt"]
    checks.append(("the gauge's step in force is the published A, B and C, and each step's picks sit inside their own cap",
                   all(_alt[f"{DD_CAP:.0f}"][x]["weights"] == p[f"portfolio_{x}"]["weights"] for x in "abc")
                   and all(abs(_alt[c][x]["maxdd"]) <= float(c) + 1e-9 for c in _alt for x in "abc")
                   and all(set(_alt[c]) == {"a", "b", "c"} for c in _alt)
                   and all(_alt[c]["c"]["weights"][UNIV_IDS.index("ATRQIAP")] == p["portfolio_c"]["pin_pct"] for c in _alt)))
    # EACH ON ITS OWN HORIZON (v80): the step in force reports A on its 10-year view and B
    # on the 3/5/10-year view, and so do A's what-ifs - and on the 10-year view the four
    # near-horizon what-ifs (volatility, drags, trend twice) cannot move A at all.
    _wiu = p["universe"]["what_if"]
    checks.append(("A and B are reported on their own horizons: the step in force and A's what-ifs on the 10-year view, B's on 3/5/10",
                   _alt[f"{DD_CAP:.0f}"]["a"]["cagr"] == p["portfolio_a"]["ten"]["cagr"]
                   and _alt[f"{DD_CAP:.0f}"]["a"]["maxdd"] == p["portfolio_a"]["ten"]["maxdd"]
                   and _alt[f"{DD_CAP:.0f}"]["b"]["cagr"] == p["portfolio_b"]["macro"]["cagr"]
                   and _alt[f"{DD_CAP:.0f}"]["c"]["cagr"] == p["portfolio_c"]["macro"]["cagr"]
                   and all(_wiu[k]["a"]["cagr"] == p["portfolio_a"]["ten"]["cagr"]
                           for k in ("vol_flat", "drags_neutral", "trend_off", "trend_alt")
                           if all(abs(f2["tilt_vol_10y"]) < 1e-9 for f2 in p["funds"] + p["portfolio_b"]["funds"]) or k != "vol_flat")))
    checks.append(("a looser step never lowers the best return the rule can reach",
                   all(_alt[a][x]["best"] <= _alt[b][x]["best"] + 1e-9
                       for x in "abc" for a, b in zip(sorted(_alt, key=float), sorted(_alt, key=float)[1:]))))
    checks.append(("the published horizon scalar reproduces the enforced one",
                   abs(p["dd_model"]["horizon_scalar"] - DD_HORIZON_SCALAR) < 5e-9))
    # PORTFOLIO B (chosen by the rule since v56). The checks are about measurement:
    # the grid, the matrix it is measured with, the budget, and that every figure
    # re-derives from the funds' own inputs.
    _pb = p["portfolio_b"]; _bw = _pb["weights"]
    _nu = len(UNIV_IDS)
    checks.append((f"Portfolio B: {_nu} weights on the 5% grid summing to 100",
                   len(_bw) == _nu and sum(_bw) == 100 and all(x % 5 == 0 for x in _bw)))
    _cd = CORR_U
    checks.append((f"the {_nu}-fund correlation extends the four-fund one: same block, symmetric, unit diagonal, positive definite",
                   all(_cd[i][j] == CORR[i][j] for i in range(4) for j in range(4))
                   and len(_cd) == _nu and all(len(r) == _nu for r in _cd)
                   and all(_cd[i][j] == _cd[j][i] for i in range(_nu) for j in range(_nu))
                   and all(_cd[i][i] == 1.0 for i in range(_nu)) and _chol_pd(_cd)))
    _bmu = sum(w / 100 * f["net_macro"] for w, f in zip(_bw, p["funds"] + _pb["funds"]))
    checks.append((f"Portfolio B's CAGR re-derives from its {_nu} funds ({_bmu:.2f} vs {_pb['macro']['cagr']})",
                   abs(_bmu - _pb["macro"]["cagr"]) < 0.005))
    checks.append((f"Portfolio B sits inside the drawdown budget ({_pb['macro']['maxdd']}% vs -{DD_CAP:.2f}%)",
                   _pb["in_budget"] and abs(_pb["macro"]["maxdd"]) <= DD_CAP + 1e-9))
    _fg = _pb["funds"][0]
    checks.append(("Global Dividend's fee is its trust fee plus its target fund's",
                   abs(_fg["fee_total"] - MACRO["gdiv_trust_fee"] - MACRO["gdiv_target_ocf"]) < 1e-9))
    checks.append(("no peso bond fund is left in the universe (removed 2026-10-21)",
                   not any("Bond" in f["name"] for f in UNIV[1])))
    # THE 22-FUND LIST (2026-10-22): every fund either searched or held out with its
    # reason, none both; and the factor model behind the added pairs reproduces the
    # typed block it was fitted to, to the two decimals both are published at.
    _ho = [x["short"] for x in p["universe"]["held_out"]]
    checks.append(("the 22-fund list is fully accounted for: searched or held out with a reason, never both",
                   p["universe"]["n_list"] == MACRO["review_list_n"] == 22
                   and not set(_ho) & set(p["portfolio_b"]["shorts"])
                   and len(set(_ho)) == len(_ho)
                   and all(len(x["why"]) > 20 for x in p["universe"]["held_out"])
                   and "US Equity Opportunity" in _ho))
    checks.append(("the factor model reproduces the typed five-fund block within 0.01",
                   all(abs(_FC[i][j] - CORR_5[i][j]) <= 0.01 + 1e-9 for i in range(5) for j in range(5))))
    # PORTFOLIO A: the highest 10-year net CAGR inside the drawdown budget (v77 rule).
    _pa = p["portfolio_a"]; _aw = _pa["weights"]
    _cons = lambda w: (len(w) == _nu and sum(w) == 100 and all(x % 5 == 0 for x in w)
                       and sum(1 for x in w if x) <= MACRO["pd_review_max_funds"]
                       and max(w) <= MACRO["pd_review_max_w"]
                       and w[0] >= MACRO["pd_review_min_cash"])
    # A FEE NOTE THAT SAYS NO PICK HOLDS THE FUND is a claim about the picks, and the
    # picks move on every roll. Global Allocation's carries one (its 1.50% re-run,
    # 2026-10-22); if a later roll put it in A or B, the note would go false
    # silently. (2026-10-23)
    _held_none = [UNIV_IDS.index(f["id"]) for f in UNIV[1]
                  if re.search(r"(none|neither) holds it", f.get("fee_note", ""))]
    checks.append(("a fee note that says no portfolio holds its fund is still true",
                   bool(_held_none) and all(PA_W[i] == 0 and PB_W[i] == 0 and PC_W[i] == 0 for i in _held_none)))
    checks.append(("Portfolios A and B obey the review's limits: 5% grid, at most "
                   f"{MACRO['pd_review_max_funds']} funds, {MACRO['pd_review_max_w']}% in any one, "
                   f"{MACRO['pd_review_min_cash']}% cash",
                   _cons(_aw) and _cons(_bw)))
    # THE ONE RULE, RE-CHECKED ON EACH PICK'S OWN SET: nothing feasible beats it by
    # more than the tie, and nothing inside the tie has a shallower drawdown.
    # The pick re-measured by summarise() must land on the figures the search saw.
    def _rule_ok(x, w):
        best = _PK[x].best; mine = summarise([v / 100 for v in w],
            "net_10y" if x == "a" else "net_macro", UNIV)   # C on B's column
        band = [m for m in _PK[x].band if m[0] >= best - PIN_TIE_PP - 1e-9]
        return (mine["cagr"] >= best - PIN_TIE_PP - 1e-9 and abs(mine["maxdd"]) <= DD_CAP + 1e-9
                and not any(abs(m[1]) < abs(mine["maxdd"]) - 1e-9 for m in band)
                and any(_full_units(m[4], m[5]) == [v // 5 for v in w] and m[0] == mine["cagr"]
                        and m[1] == mine["maxdd"] for m in band))
    checks.append(("A and B are each the rule's pick on their own column: A the 10-year view, B the 3/5/10-year blend",
                   _rule_ok("a", _aw) and _rule_ok("b", _bw)))
    # PORTFOLIO D RETIRED (owner, 2026-10-27): no key, no search, no what-if entry, no
    # coefficient - the way the four-fund optimiser was held gone from v62.
    checks.append(("Portfolio D is retired: no portfolio_d key, no D in any what-if, no d_k",
                   "portfolio_d" not in p and "d_k" not in p["dd_model"] and set(_PK) & {"d"} == set()
                   and all("d" not in v for v in p["universe"]["what_if"].values())))
    # PORTFOLIO C RESTORED (owner, 2026-10-29; retired v76-v81). Nasdaq Equity Income held at
    # exactly 50% - the one exemption from the 35% cap - and every other limit kept; chosen by
    # the same maximum-growth rule on the 3/5/10-year view inside the same band budget, over
    # its own pinned set, which is every limit-respecting mix with the pin and nothing else.
    _pc = p["portfolio_c"]; _cw = _pc["weights"]; _ip = UNIV_IDS.index(_pc["fund"])
    _cons_c = lambda w: (len(w) == _nu and sum(w) == 100 and all(x % 5 == 0 for x in w)
                         and sum(1 for x in w if x) <= MACRO["pd_review_max_funds"]
                         and max(x for i, x in enumerate(w) if i != _ip) <= MACRO["pd_review_max_w"]
                         and w[0] >= MACRO["pd_review_min_cash"] and w[_ip] == _pc["pin_pct"])
    _pins = list(univ_mixes(pinned=True))
    checks.append(("Portfolio C holds Nasdaq Equity Income at exactly 50%, every other limit kept, the pin the one exemption",
                   _pc["pin_pct"] == 50 == round(PIN_W * 100) and _pc["fund"] == "ATRQIAP" and _cons_c(_cw)
                   and _pc["column"] == "net_macro"))
    checks.append(("C's pinned set is every limit-respecting mix with the pin, each one exactly once",
                   len(_pins) == _pc["n_total"] == len(set(_pins))
                   and all(dict(zip(i_, u_)).get(_ip) == _PINU and sum(u_) == 20 and u_[0] >= _CASHU
                           and len(i_) <= UNIV_MAX_FUNDS and all(x <= _MAXU for j_, x in zip(i_, u_) if j_ != _ip)
                           for i_, u_ in _pins)))
    checks.append(("Portfolio C is the highest 3/5/10-year net CAGR the budget allows with the pin, inside it on both routes",
                   _PK["c"].best == _pc["macro"]["cagr"] and _rule_ok("c", _cw)
                   and _pc["in_budget"] and abs(_pc["macro"]["maxdd"]) <= DD_CAP + 1e-9
                   and abs(port_dd(PC_W, "net_macro", UNIV)) <= DD_CAP + 1e-9
                   and _pc["dd_cap"] == p["portfolio_b"]["dd_cap"] == round(DD_CAP, 2)))
    checks.append(("every universe what-if re-chooses B and C and re-measures A",
                   all({"a", "b", "c"} <= set(v) and len(v["b"]["weights"]) == _nu and len(v["c"]["weights"]) == _nu
                       and v["c"]["weights"][_ip] == _pc["pin_pct"]
                       for v in p["universe"]["what_if"].values())
                   and _wi_entry("live")["c"]["weights"] == _cw))
    _cmu = sum(w / 100 * f["net_macro"] for w, f in zip(_cw, p["funds"] + _pb["funds"]))
    checks.append((f"Portfolio C's CAGR re-derives from its funds ({_cmu:.2f} vs {_pc['macro']['cagr']})",
                   abs(_cmu - _pc["macro"]["cagr"]) < 0.005))
    _amu = sum(w / 100 * f["net_macro"] for w, f in zip(_aw, p["funds"] + _pb["funds"]))
    checks.append((f"Portfolio A's CAGR re-derives from its funds ({_amu:.2f} vs {_pa['macro']['cagr']})",
                   abs(_amu - _pa["macro"]["cagr"]) < 0.005))
    # THE 22-FUND REVIEW RECORD (21 Oct) holds together. Its name said "the two picks
    # order as their rules say: A the higher base case, the best-worst-case pick the
    # better worst case" from the D era to v77, while the body compared no two picks -
    # a check's name is a claim too (lesson 110), so it now says what the body tests.
    checks.append(("the 22-fund review record holds together: one date, under two weeks old, its A inside the budget it ran at, its stress drawdown no milder than its base",
                   MACRO["pa_review_date"] == MACRO["pd_review_date"] <= AS_OF
                   and (_dt.date.fromisoformat(AS_OF) - _dt.date.fromisoformat(MACRO["pd_review_date"])).days <= 14
                   and MACRO["pa_review_dd"] <= DD_CAP_DERIVED + 1e-9 and MACRO["pa_review_band_n"] >= 1
                   and MACRO["pa_review_stress_dd"] >= MACRO["pa_review_dd"]
                   and 0 < MACRO["pa_review_pool_n"] <= MACRO["pd_review_n_funds"]))
    # The 24-fund re-run is recorded, not applied: the held picks hold none of the new
    # fund, and the recorded weights fall as its assumed fee rises.
    checks.append(("the review list's re-run is recorded consistently and the universe excludes the unconfirmed fund",
                   MACRO["review_list_n"] + len(MACRO["review_list_removed"]) == MACRO["review_list_prev_n"]
                   and MACRO["review_list_date"] >= MACRO["pd_review_date"]
                   and MACRO["useq_trust_listed"] < MACRO["useq_trust_peer"]
                   and MACRO["useq_ocf_clean"] < MACRO["useq_ocf_retail"]
                   and MACRO["useq_w_a_listed"] >= MACRO["useq_w_a_peer"] >= 0
                   and MACRO["useq_w_b_listed"] >= MACRO["useq_w_b_peer"] >= 0
                   and MACRO["useq_w_c_listed"] >= MACRO["useq_w_c_peer"] >= 0
                   and MACRO["gbi_target_low"] < MACRO["gbi_target_high"]
                   and all(MACRO[f"gbi_w_{x}_low"] >= MACRO[f"gbi_w_{x}_high"] >= 0 for x in "abc")
                   and sum(x[1] for x in MACRO["pa_review_mix"]) == 100
                   and "ATRUSEQ" not in p["portfolio_b"]["ids"]))
    checks.append(("the held-out funds' what-if weights were run at the live drawdown budget and rule, on or before today",
                   MACRO["heldout_run_cap"] == p["dd_budget"]["cap"] and MACRO["heldout_run_tie"] == PIN_TIE_PP
                   and AS_OF <= MACRO["heldout_run_date"] <= REVIEW_DATE   # run in this review, not after it
                   # the disputed-fee re-run (same run, same budget and rule): a lower fee than the
                   # one carried, weights inside the limits, and the note on the page quoting them
                   and MACRO["amip_trust_alt"] < next(f["fee_feeder"] for f in UNIV[1] if f["id"] == "ATRAMIP")
                   and all(0 <= MACRO[k] <= MACRO["pd_review_max_w"] for k in ("amip_w_a_alt", "amip_w_b_alt", "amip_w_c_alt"))
                   and f"A would hold {MACRO['amip_w_a_alt']}% of this fund and B {MACRO['amip_w_b_alt']}%"
                       in next(f["fee_note"] for f in UNIV[1] if f["id"] == "ATRAMIP")))
    checks.append(("portfolio vol < weighted-average vol for A, B and C (diversification works)",
                   all(p[f"portfolio_{x_}"]["macro"]["vol"]
                       < sum(w / 100 * f["vol"] for w, f in zip(p[f"portfolio_{x_}"]["weights"], _five))
                       for x_ in "abc")))
    for name, ok in checks:
        A(f"    [{'PASS' if ok else 'FAIL'}] {name}")
    A(f"\n    {sum(1 for _, ok in checks if ok)}/{len(checks)} checks passed")
    return "\n".join(L), all(ok for _, ok in checks)

def _chol_pd(M):
    """True if M is positive definite (Cholesky succeeds)."""
    n = len(M); L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            sm = M[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                if sm <= 0:
                    return False
                L[i][i] = math.sqrt(sm)
            else:
                L[i][j] = sm / L[j][j]
    return True

if __name__ == "__main__":
    if "--json" in sys.argv:
        print(json.dumps(payload(), indent=1))
    else:
        txt, ok = report()
        print(txt)
        sys.exit(0 if ok else 1)
