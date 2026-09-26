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
from itertools import product

# Two different dates, which this model had been conflating. AS_OF is the market
# data date - the last trading session every price, yield and level comes from.
# REVIEW_DATE is when a human last worked through the page. On a weekend review they
# differ, and reference data retrieved during the review is legitimately NEWER than
# the market snapshot: a look-through read today is not "stale by -2 days".
# NO WEEKDAY IS TYPED HERE. The comment on REVIEW_DATE said "(Saturday)" on a
# Sunday, because a weekday written beside a date is a second copy of the date
# that nobody updates. Both weekdays are derived and checked below instead.
AS_OF = "2026-09-25"        # last completed trading session, PH and US both (Friday)
REVIEW_DATE = "2026-09-26"  # when this review was worked through

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
    "fed_funds_prev_upper": 3.75,
    "fed_dot_2026": 4.1,          # median end-2026 policy rate, i.e. one more hike
    "fed_dots_one_more": 12,      # of 18, at 4.125%
    "fed_dots_two_more": 4,       # of 18, at 4.375%
    "fed_dots_participants": 18,
    "fed_dot_one_more_level": 4.125,   # midpoint the 12 project
    "fed_dot_two_more_level": 4.375,   # midpoint the 4 project
    "us_cpi_headline": 3.4,
    "us_cpi_core": 2.4,        # Aug CPI, released 11 Sep (was 2.5 in July)
    "us_cpi_core_mom": 0.3,    # 0.1pp above consensus
    "us_cpi_headline_mom": 0.4,
    "us_cpi_shelter": 3.0,     # eased from 3.2
    "us_cpi_gasoline_yoy": 27.4,
    "us_pce_12m": 3.7, "us_pce_6m": 4.1,
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
    "ust_10y_provisional": [],
    "ust_10y_disputed_23sep": [5.10, 5.11, 5.12],
    "ust_10y_market_print": 5.104,   # CNBC / Wolf Street, 23 Sep, 3dp market basis
    "ust_10y_withheld": [],      # 18 Sep resolved on the official basis, see above
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
    "ust_10y_peak": 5.223, "ust_10y_peak_date": "2026-09-24",
    "ust_10y_peak_prev": 5.135, "ust_10y_peak_prev_date": "2026-09-23",
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
    "ust_2y": 4.856, "ust_2y_date": "2026-09-25",
    "ust_30y": 5.488, "ust_30y_date": "2026-09-25",
    "ust_30y_high": 5.501, "ust_30y_high_date": "2026-09-24",  # "since June 2004"
    "ust_curve_basis": "mid-session readings, not closes",

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
    "fed_hike_odds_oct": 73.0,   # CME FedWatch - Barr + hot PMI + weak 5y auction
    "fed_hike_odds_oct_date": "2026-09-23",
    "fed_hike_odds_oct_prev": 55.0, "fed_hike_odds_oct_prev_date": "2026-09-22",
    "fed_hike_odds_oct_first": 50.9, "fed_hike_odds_oct_first_date": "2026-09-17",
    "fed_hike_odds_dec": 88.5,   # cumulative, at least one more by December -
    "fed_hike_odds_dec_date": "2026-09-17",  # LAST VERIFIED here; not re-found on the 23rd
    # A settled reading of a DECIDED meeting. Kept for the record, and registered
    # in RESOLVED_ODDS below so prose quoting it has to say which meeting and when:
    # the US regional note said "the hike is 92.0% priced" in the present tense for
    # five days after the hike had been delivered.
    "fed_hike_odds_sep_final": 92.0,
    "fed_hike_odds_sep_date": "2026-09-16",
    "ecb_sep_delivered": 2.50,
    "us_payrolls_aug": 162_000, "us_payrolls_aug_consensus": 53_000,
    "us_payrolls_12m_avg": 31_000,
    "us_payrolls_jul": -23000,
    "us_unemployment": 4.1,
    # S&P Global flash PMI, September 2026 (released 23 Sep), vs the August finals.
    "us_pmi_composite_sep": 58.4, "us_pmi_composite_aug": 56.0,
    "us_pmi_services_sep": 58.7, "us_pmi_services_consensus": 56.0,
    # The headline Manufacturing PMI, 57.0 from 53.9 (a 52-month high). The first
    # pass carried 56.7 from 53.1 under this name - that is the Manufacturing
    # OUTPUT index, a different series in the same release.
    "us_pmi_manufacturing_sep": 57.0, "us_pmi_manufacturing_aug": 53.9,
    "us_5y_auction_size_bn": 70,   # weak-demand 5-year note auction, 23 Sep
    "ecb_depo": 2.50,          # HIKED 10 Sep 2026 (+25bp); MRO 2.65, MLF 2.90, effective 16 Sep
    "ecb_depo_prev": 2.25,
    "ecb_last_move_bp": 25,
    "ea_hicp_aug": 3.3, "ea_hicp_jul": 2.9, "ea_energy_aug": 14.3,
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
    "usdjpy": 156.86,          # 18 Sep close, +0.58% - a two-week low for the yen
    "jp_core_cpi": 1.7, "jp_core_cpi_prev": 1.8,   # Aug, released hours before
    "jp_core_core_cpi": 1.9,   # ex fresh food AND fuel - the BoJ's demand gauge
    "bsp_rrp": 5.0,
    "bsp_last_move_bp": 25,
    "bsp_hikes_since_apr": 3,
    "bsp_cum_bp": 75,
    "ph_cpi_aug": 6.1, "ph_cpi_ytd_avg": 5.2,
    # The headline decelerated for a fourth month, but the largest single food
    # component went the other way and hard. The peso sleeve's real-carry argument
    # rests on a FIFTH deceleration; a staple re-accelerating 2.3pp in one month is
    # the most concrete thing working against it, and the note had only the oil
    # price to point at.
    "ph_rice_cpi_aug": 19.4, "ph_rice_cpi_jul": 17.1,
    "ph_food_cpi_aug": 4.6, "ph_food_cpi_jul": 5.2,
    "ph_cpi_jul": 6.2,
    "ph_cpi_jun": 6.4,
    "bsp_infl_2026": 6.1,
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
    "usdphp": 62.465,          # 25 Sep
    "usdphp_date": "2026-09-25",
    "usdphp_prev": 62.735,     # 24 Sep close
    "usdphp_prev_date": "2026-09-24",
    "usdphp_chg": -0.270,      # as reported: "gained 27 centavos" (USD/PHP down)
    "usdphp_record": 62.86,        # 14 Sep close - the weakest close on record
    "usdphp_record_date": "2026-09-14",
    "usdphp_record_intraday": 62.925,  # 15 Sep intraday - weakest print on record
    # 24, not 23. BusinessWorld counted 62.625 (8 Sep) as the 23rd record of 2026
    # and 62.68 (11 Sep) as the 24th; this model had the count attached to the
    # level below it from launch until 2026-09-19. It is carried as-of the 11 Sep
    # print because that is the last record published with a running YTD count.
    # 62.86 is at least one more, but no source states its ordinal and an ordinal
    # cannot be derived from a price, so it is not asserted.
    "usdphp_records_2026": 24, "usdphp_records_asof": "2026-09-11",
    "usdphp_sept_records": 6,      # 14 Sep was the sixth record of the month
    "usdphp_2025_close": 58.79,    # 29 Dec 2025 - the YTD base, move DERIVED below
    # 25 Sep: +95.95 (+1.67%), the first gain after a run of losses that took the
    # index to a 10-month low on the 24th. 5730.02 + 95.95 = 5825.97 exactly.
    "psei": 5825.97, "psei_chg_pts": 95.95, "psei_chg_pct": 1.67,
    "psei_date": "2026-09-25",
    "psei_prev": 5730.02,
    # PH T-BILLS, 21 Sep auction (BusinessWorld / BusinessMirror). CORRECTED
    # 2026-09-24: 5.138 / 5.517 / 5.717 had been here since the build on 2 Sep,
    # never refreshed, and since 13 Sep the look-through stamped them with the
    # page's own as-of date as "the live curve" - 22 days and ~30bp stale on every
    # tenor by the time it was caught. The rates now carry their AUCTION date, the
    # previous auction for the chain, and a bound on age against the weekly cadence.
    "ph_tbill_91": 5.431, "ph_tbill_182": 5.821, "ph_tbill_364": 6.043,
    "ph_tbill_prev": [5.348, 5.781, 5.922],       # 14/15 Sep auction
    "ph_tbill_chg_bp": [8.3, 4.0, 12.1],          # as reported
    "ph_tbill_date": "2026-09-21",
    "ph_tbill_cadence_d": 7,                      # BTr auctions T-bills weekly
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
    ],
    "brent_chg_reported": -2.14,  # the source's own figure, 2dp (CNBC)
    "brent_session_high": 108.23, "brent_session_high_date": "2026-09-24",
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
    "brent_withheld": [],
    "brent_disputed_23sep": [98.44, 101.61, 103.08],
    "wti_disputed_23sep": [89.31, 92.16, 92.54],
    # The four Monday candidates, kept as the record of the dispute - and of the
    # heuristic that picked the wrong one.
    "brent_disputed": [100.06, 100.34, 101.40, 101.50],
    # (The recovered Monday settle is brent_prev below - one name for one number.
    # A separate "brent_21sep" with the same value was added and removed in the
    # same review: two inputs for one quantity is how ust_10y_peak and
    # ust_10y_intraday drifted apart.)
    "brent_high": 108.75,      # the four-month high
    # DATED, because the page hard-typed "on 10 September" against it and was wrong
    # by five days from the moment the high moved. A dated figure whose date lives
    # only in prose is a figure whose date is not maintained.
    "brent_high_date": "2026-09-15",
    "brent_closure": 130.0,    # the Hormuz full-closure level the stress row models;
                               # published so the scenario and the notes citing it
                               # cannot drift apart
    "brent_mom": 13.24,
    # Year-ago base. brent_yoy is DERIVED from it below rather than typed, so the
    # level and the change can never drift apart the way the quoted figures did on
    # 2026-09-10. RE-ANCHORED 2026-09-24: the base had been $65.50, implied by the
    # 4 Sep pair ($96.28 at +46.99%) and never moved since - so by the 23rd the
    # "y/y" was measured against a date 19 days off the anniversary, overstating it
    # (+57.4% instead of +54.8%). Now CNBC's verified 22 Sep 2025 settle, one day
    # off, and DATED so a check can bound the drift: a week, then re-anchor.
    "brent_yr_ago": 66.57,
    "brent_yr_ago_date": "2025-09-22",
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
    "hormuz_transits": 1,          # IMF PortWatch, all transits (was 8 on 13 Sep)
    "hormuz_transits_date": "2026-09-20",
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
    "petroline_bypass": 5.0,       # mb/d rerouted via the pipeline before the strike
    "petroline_capacity": 7.0,     # mb/d design capacity after expansion
    "petroline_km": 1200,          # east-west across the peninsula to Yanbu
    "petroline_shut": "2026-09-11",
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
    "yanbu_dry_since": "2026-09-11",
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
    # THE QUEUE, on a stated basis and as a SERIES. 436 was a 30 August reading on
    # an undisclosed basis and sat here for three weeks. These three are one
    # source, one methodology, one daily snapshot time: AIS-visible vessels holding
    # position away from berth in the Hormuz and Gulf watch box, excluding ships
    # within 25 km of a working port. Three points, because two would have let this
    # note call 369 -> 357 a drawdown; 376 the next day says it is oscillating.
    "hormuz_queue": [("2026-09-18", 369), ("2026-09-19", 357), ("2026-09-20", 376)],
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
    "vix_spot": 14.32,         # 4 Sep close (Friday) - the curve's own spot
    # AN INDEPENDENT READ ON THE SAME SHAPE. VIX3M is a market-published constant-
    # maturity 3-month implied vol - it is not an input to the bootstrap, so the
    # ratio it implies is a free test of whether the forward-variance integration
    # produces a term structure the market would recognise. Both legs are from one
    # source on one date, and the published IVTS reproduces from them exactly
    # (15.84 / 18.60 = 0.8516), which is why the pair is trusted.
    "vix3m": 18.60, "vix3m_spot": 15.84, "vix3m_date": "2026-09-11",
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
        ("2026-09-25", 14.85),   # -5.24%: 15.67 x 0.9476 = 14.85
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
        "2026-09-23": 7, "2026-09-24": 3.23, "2026-09-25": -5.24,
    },
    "vix_latest_high": 18.17,  # 10 Sep intraday, the highest print of the episode
    "vix_latest_high_date": "2026-09-10",
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
    "equity_date": "2026-09-25",
    "spx_close": 7743.41, "spx_chg_pct": 0.51,
    "nasdaq_close": 27068.72, "nasdaq_chg_pct": 0.48,
    "dow_close": 51828.62, "dow_chg_pct": 0.93, "dow_chg_pts": 478.64,
    # Previous closes, published so the CHAIN is checkable in code rather than
    # asserted in a sentence. This is the discipline that caught the 10-year's
    # dating error today and the VIX's on 17 Sep: a print that will not reproduce
    # the next session's published move is not a print.
    "spx_prev": 7704.13, "nasdaq_prev": 26939.37, "dow_prev": 51349.98,
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
    "wti_settle": 92.41, "wti_chg_pct": -2.33,    # 25 Sep, November contract
    "wti_date": "2026-09-25", "wti_contract": "2026-11",
    "wti_prev": 94.61, "wti_prev_date": "2026-09-24",
    "wti_expired_contract": "2026-10", "wti_expired_settle": 94.59,
    # The 2026 low MOVED and this model did not notice for nine days. 14.18 on
    # 17 Aug was widely reported as the year's low at the time, and was carried as
    # such; on 4 Sep the index slid to 13.80 just before the payrolls release and
    # then rebounded to close 14.32. Both are kept - the August print is still cited
    # historically, but it is no longer the low.
    "vix_2026_low": 13.80,     # 4 Sep intraday, before the payrolls print
    "vix_2026_low_date": "2026-09-04",
    "vix_aug_low": 14.18,      # 17 Aug intraday - the 2026 low UNTIL 4 Sep
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
    "vix_futs_levels": [("Oct", 2026, 10, 18.41),
                        ("Nov", 2026, 11, 19.08), ("Dec", 2026, 12, 19.26)],
    "vix_fut_sep": 16.57,
    "vix_fut_dec": 19.26,
    "vix_longrun": 19.5,
    "variance_risk_premium": 3.5,
    "imf_global_2026": 3.1,
    "imf_global_2027": 3.2,
    "imf_us_2026": 2.4,
    "imf_us_2027": 2.0,
    "imf_ea_2025": 1.1,
    "imf_ea_2026": 0.7,
    "imf_ae_2026": 1.8,
    "imf_ae_2027": 1.7,
    "ndx_fwd_pe": 22.4,
    "ndx_fwd_pe_10y": 22.9,
    "ndx_fwd_pe_5y": 24.7,
    "sxxp_fwd_pe": 15.37,
    "sxxp_ytd": 9.5,
    "asia_fwd_pe": 10.5,
    "asia_eps_2026": 52.5,
    "asia_eps_2027": 27.5,
    "nikkei": 64011, "kospi": 6910,   # 11 Sep closes - the sell-off the Asia note describes
    # 24 Sep: the Nikkei reopened from the 23 Sep equinox holiday +0.76% at 65,513.94
    # (TradingKey close). Corroborated by construction: Trading Economics' intraday
    # +0.99% at 65,665 implies the same prior close (~65,020) - two reports agreeing
    # on the base they moved from. Korea was shut for Chuseok, so the KOSPI has no
    # newer print than the one above.
    # 25 Sep: +1.30% to 66,364.20, a fifth straight gain (Business Standard). A
    # widely syndicated 66,345.07 (+831.08, +1.27%) was stamped 14:56 - before the
    # 15:30 close - and its own points miss the 24 Sep base by 0.05: an intraday
    # print. 65,513.94 x 1.0130 = 66,365; the close chains to its percentage.
    "nikkei_latest": 66364.20, "nikkei_latest_chg_pct": 1.30,
    "nikkei_latest_date": "2026-09-25",
    "nikkei_latest_prev": 65513.94,
    "ltcma_us_eq": 6.7,
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
    "asia_rerating": 1.0,          # re-rating credit in the Asia base, %/yr (E) - see CLAIMS
    "asia_div_drag": 0.5,          # dividend tilt's lower growth capture, %/yr (E)
    "tech_growth_premium": 3.5,    # tech earnings-growth premium over US large cap, %/yr (E)
    "tech_derating": 1.2,          # tech multiple de-rating drag, %/yr (E)
    "phmm_gross_prev": 5.25,       # the PH short-rate assumption before the mandate lengthened
    "ltcma_em_eq": 7.8,
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

VIX_QUOTE_DATE = "2026-09-04"   # Friday close - the date every VIX level here is from
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
# while the driver note beside it, and the source, said -5.24% (the true close was
# ~14.849). Two figures for one move on one page. The recomputed value is kept,
# under its own name, for the audit; the chain check below ties the two together.
_vrep = MACRO["vix_reported_moves"][MACRO["vix_latest_date"]]
MACRO["vix_latest_chg_pct_calc"] = round(
    (MACRO["vix_latest"] / MACRO["vix_prev_close"] - 1) * 100, 2)
MACRO["vix_latest_chg_pct"] = float(_vrep)
MACRO["vix_latest_chg_dp"] = 0 if isinstance(_vrep, int) else len(repr(_vrep).split(".")[1])
MACRO["vix_episode_high"] = max(v for _, v in _VH)
MACRO["vix_episode_low"] = min(v for _, v in _VH)
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
MACRO["fed_hike_odds_oct_chg_pp"] = round(MACRO["fed_hike_odds_oct"]
                                          - MACRO["fed_hike_odds_oct_prev"], 1)
# How far spot sits below the four-month high, and the day's move, both DERIVED so
# the notes quoting them cannot drift from the levels they come from.
MACRO["brent_off_high_pct"] = round((1 - MACRO["brent"] / MACRO["brent_high"]) * 100, 2)
MACRO["brent_chg_pct"] = round((MACRO["brent"] / MACRO["brent_prev"] - 1) * 100, 2)
# The peso's year-to-date loss of VALUE, which is what a peso holder experiences:
# 1 - base/spot, not spot/base - 1. Both conventions are in circulation and they
# differ by half a point at this level, so the one that reaches the portfolio is
# the one computed, and it is computed rather than typed.
MACRO["usdphp_ytd_pct"] = round(
    (1 - MACRO["usdphp_2025_close"] / MACRO["usdphp"]) * 100, 2)
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
MACRO["hormuz_queue_lo"] = min(v for _, v in _HQ)
MACRO["hormuz_queue_hi"] = max(v for _, v in _HQ)
# How stale the PortWatch reading is at this review, against its own publication
# cadence. Derived, so it cannot be described as fresh once it is not.
MACRO["hormuz_transits_age_d"] = (
    _dt.date.fromisoformat(REVIEW_DATE)
    - _dt.date.fromisoformat(MACRO["hormuz_transits_date"])).days
MACRO["hormuz_flow_drop_pct"] = round(
    (1 - MACRO["hormuz_flow_now"] / MACRO["hormuz_flow_prewar"]) * 100, 0)

MACRO["vix_futs"] = [(lbl, round(vix_maturity(y, m), 4), lvl)
                     for lbl, y, m, lvl in MACRO["vix_futs_levels"]]
MACRO["vix_fut_sep"] = MACRO["vix_futs"][0][2]
MACRO["vix_fut_dec"] = MACRO["vix_futs"][-1][2]

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
POSTPONED = [("Iran-GCC talks on the Strait, in Oman",
              "Called off on 14 September with no new date; Iran was to unveil the "
              "temporary shipping lane agreed with Muscat. US and Iranian delegations "
              "met at the UN on 22 September instead, and that meeting is what "
              "restored the energy driver.")]

CATALYSTS = [
    ("2026-09-30", "US August PCE inflation",
     "The Fed's own gauge, and the next hard number before October. July ran "
     "3.7% over 12 months; a hot August would firm the 73% October hike odds that "
     "the monetary driver and the near-horizon US scores are set against."),
    ("2026-10-02", "US September payrolls",
     "The growth driver was raised on August's +162k against a 53k consensus and "
     "the 58.4 PMI. A weak print is the quickest way to reverse that raise."),
    ("2026-10-06", "Philippine September CPI",
     "The peso sleeve's real carry needs PH inflation to keep slowing; August "
     "was the fourth slowdown in a row. Two things work against a fifth: Brent "
     "at $104.32 on 25 Sep, and rice inflation up to 19.4% from 17.1%."),
    ("2026-10-28", "FOMC decision",
     "October is priced at 73% after the 23 Sep repricing; at least one more "
     "hike by December was last verified at 88.5% on 17 Sep. The dot-plot median "
     "already has one more this year, so the question is timing."),
]

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

HORIZONS = [("3M", 0.25), ("6M", 0.50), ("12M", 1.00), (HZ_LABEL, HORIZON_Y)]
VOL_TS = []
for lbl, T in HORIZONS:
    iv = horizon_vol(T)
    VOL_TS.append({
        "label": lbl, "years": T,
        "implied": round(iv, 2),
        "realised": round(iv - MACRO["variance_risk_premium"], 2),
        # 1-sigma and 2-sigma S&P-equivalent move over the horizon
        "move_1sd": round(iv * math.sqrt(T), 2),
        "move_2sd": round(2 * iv * math.sqrt(T), 2),
    })
SP_VOL_LT = next(v["implied"] for v in VOL_TS if v["label"] == HZ_LABEL)

# What the stale strip costs, measured rather than asserted. Re-anchor the curve to
# the spot of the VIX3M observation date, integrate to 0.25y, and compare with the
# market's own 3-month index. Same t=0, same strip, so the residual is the strip's
# age and nothing else. It is NEGATIVE, which means this model's implied vol sits
# below the market's - so its forecast drawdowns are, if anything, a touch small.
VIX3M_MODEL = _horizon_vol_on([(0.0, MACRO["vix3m_spot"])] + VOL_KNOTS[1:], 0.25)
VIX3M_RESID = round((VIX3M_MODEL / MACRO["vix3m"] - 1) * 100, 2)

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
#    HORIZON BLEND WEIGHTS - reweighted 2026-09-08.
#    The old split was 3M 15 / 6M 25 / 12M 30 / long 30, carried over unchanged
#    when the mandate went from 5 years to 10. Two things were wrong with it:
#
#      1. The comment above it claimed the blend "keeps the long anchor
#         dominant". It did not. 70% of the weight sat on horizons under a year
#         against 30% on the anchor - the comment described an intent the
#         numbers contradicted, and nothing checked it.
#      2. Whatever the right near-term weight is for a FIVE-year mandate, it is
#         not also right for a TEN-year one. Doubling the holding period without
#         touching the weights silently doubles how much a 3-month signal counts
#         per year of mandate.
#
#    Now 3M 10 / 6M 15 / 12M 25 / long 50: near-term signals still get a vote
#    (half the weight), the anchor genuinely dominates, and the check below
#    asserts it rather than trusting a comment.
# ----------------------------------------------------------------------------

HZ_W = {"3M": 0.10, "6M": 0.15, "12M": 0.25, HZ_LABEL: 0.50}

# ----------------------------------------------------------------------------
# 3b. VOLATILITY RAMP - the optimiser's volatility channel
#     Until 2026-09-05 each fund's volatility tilt was a hand-set constant: the
#     term structure was computed and displayed, but never actually fed the
#     allocation. It does now. The ramp is how far the horizon-blended implied
#     vol sits ABOVE spot - i.e. how much repricing the option market is still
#     pointing at - using the same horizon weights as the regional blend.
# ----------------------------------------------------------------------------
VOL_BLEND = sum(v["implied"] * HZ_W[v["label"]] for v in VOL_TS)
# MEASURED FROM THE LONG-RUN LEVEL, NOT FROM SPOT. Corrected 2026-09-25. Every
# fund's base return is a long-run (LTCMA) return, and a long-run return already
# assumes average volatility - the 19.5 long-run VIX this model's own curve
# converges to. Measuring the ramp from TODAY's low spot credited the covered-call
# sleeve (+0.96pp) and charged Global Technology (-0.56pp) for volatility rising to
# a level both bases already assume: the rise was counted in the base and again in
# the tilt. The tilt is now the deviation of the horizon-blended curve from the
# long-run level - what the cycle view adds to, or takes from, a no-view base.
VOL_RAMP  = VOL_BLEND - MACRO["vix_longrun"]
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
VOL_SENS = {"ATRPHMM": 0.035, "ATRQIAP": 0.210, "ATRASEQ": 0.000, "ATRGTEC": -0.122}


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

REGIONS = {
    "US": {
        "3M": 4.25, "6M": 4.75, "12M": 5.5, HZ_LABEL: 6.5,
        "why": "Near horizons cut, ten-year anchor held. Growth is fine - August payrolls +162k against a 53k consensus, and the September composite PMI hit 58.4, the strongest since July 2021 - but the rate path has repriced hard. On official closes the 10-year went from 5.01% on 18 Sep to 5.17% on 25 Sep, and on the 24th it traded as high as 5.223%, the highest since June 2007; the 30-year hit 5.501% that day, its highest since June 2004. Friday was calmer - the 2-year read 4.856% and the 30-year 5.488%. The trigger on the 23rd: Fed Governor Barr said further hikes are 'likely to be needed', a $70bn 5-year auction met weak demand, and CME FedWatch's October odds jumped from 55% to 73% in a day. Equities have stalled rather than broken: after falling together on the 23rd and going flat on the 24th, the S&P closed 25 Sep at 7743.41 (+0.51%), the Nasdaq at 27068.72 (+0.48%) and the Dow at 51828.62 (+0.93%). August CPI was mixed - core 2.4% y/y but +0.3% on the month, gasoline +27.4% y/y. The anchor holds at 6.5 on two structural points: the US is a net energy EXPORTER, a relative tailwind against every other bloc here, and NDX at 22.4x forward still sits below its 10y and 5y averages.",
    },
    "EUROPE": {
        "3M": 2.5, "6M": 3.0, "12M": 3.5, HZ_LABEL: 4.5,
        "why": "The worst policy/growth mismatch in the world. The ECB hiked to 2.50% on 10 Sep - its second and final move - into IMF growth of just 0.7%, and did it explicitly because the energy shock will hold inflation above target for an extended period. August HICP was 3.3% with energy +14.3% y/y, but inflation excluding energy was 2.2%: essentially the whole overshoot is the oil price, and Europe is the largest net energy importer in the world facing Brent +56.7% y/y. The offset is real - at 15.4x forward it is the cheapest large market here, and the hiking cycle is now over by the ECB's own guidance.",
    },
    "ASIA": {
        "3M": 5.0, "6M": 5.5, "12M": 6.5, HZ_LABEL: 7.5,
        "why": "Near horizons cut; the early-September bounce did not hold. The region sold off again on 11 Sep - Nikkei -1.9% to 64,011, KOSPI -1.8% to 6,910, Samsung -3.5%, SK Hynix -2.2% - and this time it is a rate shock as well as an energy one. Japan has since recovered well past that level: the Nikkei closed 66,364.20 on 25 Sep, +1.30% for a fifth straight gain. Korea is shut for Chuseok, and this page carries no KOSPI print after 11 Sep. The BoJ delivered on 18 Sep, +25bp to 1.25% - the highest since 1995 - and the yen FELL, closing 156.86 per dollar, a two-week low. Read that carefully: a hike that weakens the currency is the market pricing the END of a cycle, not improving carry. The vote was 7-2, Asada and Sato dissenting, and August core CPI had slowed to 1.7% from 1.8% hours earlier, so the board tightened into decelerating headline inflation on the strength of a demand gauge at 1.9%. The gap from the previous move was three months against six before it: faster, and more contested. Korea, Taiwan and Japan are all large net oil importers. The ten-year anchor stays at 7.5: 10.5x forward against consensus EPS growth of ~52% and ~28% is a two-decade-wide discount, and JPM LTCMA puts EM equity at 7.8%, the highest of any equity block, on a framework that fits this mandate.",
    },
    "PHILIPPINES": {
        "3M": 5.5, "6M": 5.5, "12M": 5.5, HZ_LABEL: 5.5,
        "why": "Neutral across the curve. The nominal carry is intact and improving - BSP at 5.00% after three consecutive hikes, 364-day T-bills at 6.04% on the 21 Sep auction, up 12bp in a week as the Fed's hike fed through, with room for one more move - but the real carry is not. August inflation eased to 6.1% from 6.2%, a fourth consecutive deceleration and a five-month low, with the year to August averaging 5.2% - though BSP's own 2027 forecast is 5.4%. Oil, which had turned from the risk to the help, has turned back: two up days took Brent to $106.60 on 24 Sep, and after giving up 2.14% on the 25th it still settled at $104.32, 4.07% below its 15 Sep high - which matters most in a country that imports essentially all of its crude. The one that has not turned is inside the print: food inflation fell to 4.6% from 5.2%, which is what drove the deceleration, while RICE accelerated to 19.4% from 17.1%. A staple re-accelerating 2.3pp in a month is a harder thing for the headline to keep absorbing. The peso has come off its record: 62.465 on 25 Sep, 27 centavos stronger on the day, against the weakest close on record of 62.86 on 14 Sep and the weakest intraday print of 62.925 the next. That is still a 5.88% loss of purchasing power against the dollar this year. The PSEi rose 1.67% on 25 Sep to 5825.97, a first gain after a run of losses that had taken it to a 10-month low the day before. This sleeve's job is zero duration risk and high nominal carry; both are unimpaired. Its purchasing power is not.",
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
    for h in ("3M", "6M", "12M", HZ_LABEL):
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
    ("Monetary policy & liquidity", 0.2, 1.75,
     "HELD at 1.75 after the 23 Sep cut; the rest of the week extended the move "
     "without changing the path. What arrived on the 23rd: the S&P Global composite PMI hit 58.4 "
     "(from 56.0), the strongest US private-sector expansion since July 2021, with "
     "input costs rising the fastest since October 2022; a $70bn 5-year note "
     "auction met weak demand; and Fed Governor Barr - a sitting voting member - "
     "said 'in my base case, further policy adjustments are likely to be needed'. "
     "CME FedWatch put October at 73%, from 55% on the 22nd - an 18-point move in "
     "one session. It read 50.9% on the 17th. Cumulative odds of at least one more "
     "hike by December were last verified at 88.5% on the 17th; October alone "
     "cannot exceed the cumulative figure, so the two are consistent - but "
     "consistent is not re-verified. On official closes the 10-year went 4.94% on "
     "the 17th, 5.01% on the 18th, 4.96% on the 21st, 4.97% on the 22nd, 5.12% on "
     "the 23rd (the 5.104% market-close print, confirmed on the Treasury's par "
     "curve two basis points higher), 5.18% on the 24th and 5.17% on the 25th - 16bp "
     "on the week. On 24 Sep the selloff went longer and global: the 10-year "
     "traded as high as 5.223%, the highest since June 2007 (the 23 Sep peak of "
     "5.135% is superseded), and the 30-year hit 5.501%, its highest since June "
     "2004. Friday was calmer: the 10-year little changed, the 2-year read 4.856% "
     "and the 30-year 5.488%. The ECB finished its own "
     "cycle on 10 Sep at 2.50%; BSP is at 5.00% after three hikes; the BoJ joined "
     "on 18 Sep at 1.25%. Not cut again: the 24th moved the long end, not the "
     "October odds; the 25th moved neither; and 16 of 18 dot-plot participants already saw one more hike "
     "this year. What changed on the 23rd is HOW SOON, and that is in this score."),
    ("Inflation trajectory", 0.15, 2.75,
     "CUT a quarter point - two-sided is still the right frame, but the forward "
     "side just got louder. The core measure improved - August core CPI 2.4% y/y "
     "from 2.5%, shelter 3.0% from 3.2%, food 2.7% from 3.0%. Energy is eating that "
     "progress in real time: core rose 0.3% on the month against a 0.2% consensus, "
     "gasoline is +27.4% y/y and fuel oil +52%. What is new is forward-looking, not "
     "backward: the S&P Global composite PMI for September, released 23 Sep, "
     "reported input costs rising at their steepest pace since October 2022, "
     "driven by fuel, freight and wages together - a survey reading of pipeline "
     "pressure, months ahead of the CPI print it will eventually show up in. Euro "
     "HICP 3.3%. PH eased to 6.1%, a fourth straight deceleration - but Brent "
     "settled at $104.32 on 25 Sep, still +56.7% on a year earlier. That is still "
     "inside the range this score "
     "was set against - below the 15 Sep high - which is why the cut stops at a "
     "quarter point."),
    ("Growth momentum", 0.15, 4.25,
     "RAISED a quarter point on the hardest data point of the week: the S&P Global "
     "flash composite PMI for September hit 58.4, from 56.0, the strongest private-"
     "sector expansion since July 2021 - services led at 58.7 against a 56 "
     "consensus, and the manufacturing PMI jumped to 57.0 from 53.9, a 52-month "
     "high. August payrolls were "
     "already strong, +162k against a 53k consensus, unemployment 4.1%. This "
     "driver's own lane is whether the growth engine is intact under the shocks, "
     "not what the bond market did in reaction to the same print - that belongs to "
     "Monetary policy, which absorbed the hit: the PMI beat is exactly why the "
     "10-year jumped 13bp on 23 Sep and equities fell across the board. Read separately, the PMI print is unambiguous growth evidence; kept "
     "here rather than double-counted in the rate driver's cut. Saudi output is "
     "still down ~1.9 mb/d after Houthi strikes. The IMF's 3.1% global forecast was "
     "written against an oil price nearly forty dollars lower and a 10-year yield "
     "nowhere near 5.17%, a second tax on every long-duration cash flow here."),
    ("Corporate earnings", 0.2, 7.0,
     "Still the strongest pillar. Asia ex-Japan EPS of ~+52% (2026) and ~+28% (2027) "
     "is unrevised and the AI capex cycle keeps compounding through the semis supply "
     "chain. Trimmed because the margin assumption underneath those estimates is "
     "harder to hold at $104.32 oil than at $66.57, where it was a year ago - Brent "
     "settled 25 Sep 4.07% below its $108.75 peak of 15 Sep. "
     "The selling has hit the earnings engines directly - Samsung -3.5%, SK Hynix -2.2%."),
    ("Valuation support", 0.1, 8.25,
     "RAISED a quarter point on 23 Sep - the one driver the shock improves. The "
     "S&P, Nasdaq and Dow fell together that day as the 10-year jumped to a post-2007 high, "
     "resuming the de-rating a 1.9% Nikkei fall and a month of index declines had "
     "already started, against estimates that have not moved. They barely moved on "
     "24 Sep as the 10-year went higher still, and rose on 25 Sep (+0.51/+0.48/"
     "+0.93%) with it little changed - a bounce, not a re-rating. NDX 22.4x forward sits below both its 10y (22.9x) and 5y "
     "(24.7x) averages, Asia at 10.5x is a two-decade-wide discount, Europe 15.4x. "
     "A cheaper multiple on the same earnings is better compensation for the same "
     "risk."),
    ("Volatility & risk appetite", 0.1, 3.0,
     "HELD at 3.0 - and the puzzle the last two reviews held it on has dissolved. "
     "They read the index as falling through a rates selloff; that was a dating error in "
     "this page's own series, which had filed every close from 17 Sep one session "
     "late. On the right dates the index made a 21-session low of 14.21 on 22 Sep, "
     "then rose 7% to 15.18 on 23 Sep as the 10-year jumped, and 3.23% to 15.67 on "
     "24 Sep: the ordinary pairing, rates and equity volatility moving together. "
     "The pairing held on the way back: with the 10-year little changed and stocks "
     "up on 25 Sep, the index gave up 5.24% to 14.85. "
     "It is still a low level - under the 17.84 close of 10 Sep and below the "
     "long-run 19.5 - so it reads as neither complacency nor stress. What this "
     "driver does NOT carry is a claim that rising volatility pays the portfolio: "
     "every fund's base return already assumes long-run volatility, so only the "
     "curve's distance from 19.5 moves a forecast, and blended across horizons the "
     "4 September strip sits at 18.88 - just below it."),
    ("Geopolitics & energy", 0.1, 1.5,
     "HELD at 1.5, where it was restored on 22 Sep when both reasons for the cut to "
     "1.25 reversed as facts: Saudi Arabia restarted the 1200 km East-West "
     "(Petroline) pipeline, which had carried roughly 5.0 mb/d to Yanbu around the "
     "Strait, and US negotiators met an Iranian delegation for three hours at the "
     "UN General Assembly. 24 Sep tested both. The Houthis fired six ballistic "
     "missiles at Yanbu and Taif; all were intercepted, with no damage reported, "
     "and Brent spiked to $108.23 intraday on 24 Sep before settling at $106.60, up "
     "3.4%. The same day US and "
     "Iranian negotiators were reported to be exploring a phased deal - the Strait "
     "reopened, the blockade lifted - and on 25 Sep Foreign Minister Araghchi said "
     "it could open within seven days 'if certain conditions are met': four or "
     "five days for the US to take steps Iran says a June memorandum already "
     "agreed, the Strait reopening on the sixth. France pledged soldiers, radars "
     "and air defences to protect Yanbu. Brent gave back 2.14% to settle at "
     "$104.32 on 25 Sep - 4.07% below the $108.75 high of 15 Sep and +56.71% on a "
     "year earlier. None of that is a fact yet: the missiles missed, the offer is "
     "conditional, and the Strait is still closed. The pipeline is well below normal throughput - 40% "
     "within a couple of days, six to eight weeks to full - and Kpler's Yanbu loss "
     "of 2.5 to 2.7 mb/d does not close in a week. "
     "Read the disruption on VOLUME, not vessel counts. The counts run from 1 to "
     "30 a day depending on what is counted and when - IMF PortWatch 1 transit "
     "against an 85 baseline on its 20 Sep reading (8 on the 13th), Lloyd's List "
     "Intelligence 14 a day in the week to 23 Aug counting only cargo over 10000 "
     "dwt, the US government around 30 on a basis it does not state - and none of "
     "them is supply. Goldman's Gulf export reading of 15.5 mb/d against 23.0 pre-war, up "
     "from a 5.5 trough in March, is dated 2026-08-28 and predates both the "
     "pipeline strike and its restart, so it is carried as the last measurement and "
     "nothing more. The queue off berth is oscillating, not draining: 369, 357 and "
     "376 vessels on 18-20 Sep on one stated basis. Still NOT scored at the floor "
     "or near it: the stress table models full closure and Brent above $130, a "
     "strictly worse state that is not off the table while the Strait stays shut."),
]
GAUGE_10 = round(sum(w * s for _, w, s, _ in DRIVERS), 2)

# ONE-LINE SUMMARIES, shown by default; the full note sits one tap behind each.
# A check requires every number in a summary to appear in its full note, so a
# summary cannot drift from the reasoning it abbreviates.
SUMMARY = {
    "Monetary policy & liquidity": "Held at 1.75: October hike odds are 73% after a hot PMI and a hawkish Governor Barr, and on 24 Sep the 30-year hit its highest since June 2004.",
    "Inflation trajectory": "Trimmed to 2.75: core CPI eased to 2.4%, but gasoline is +27.4% y/y and PMI input costs are rising at their steepest since October 2022.",
    "Growth momentum": "Raised to 4.25: the September composite PMI hit 58.4, the strongest since July 2021, on top of +162k August payrolls.",
    "Corporate earnings": "Still the strongest pillar: Asia ex-Japan EPS of ~+52% this year, trimmed only for margins at $104.32 oil.",
    "Valuation support": "Raised to 8.25 on 23 Sep: the rate shock cheapened multiples again - the one driver the shock improves.",
    "Volatility & risk appetite": "Held at 3.0: the VIX fell back to 14.85 on 25 Sep as yields steadied - still low, and the blended curve sits just below its long-run 19.5.",
    "Geopolitics & energy": "Held at 1.5: Houthi missiles at Yanbu were intercepted and Iran offers a conditional reopening, but the Strait is still closed.",
    "US": "Near horizons cut on the rate repricing; the ten-year anchor holds at 6.5 on energy self-sufficiency and a Nasdaq still below its average forward multiple.",
    "EUROPE": "Ranked last: the ECB hiked to 2.50% into growth of just 0.7%, and Europe is the largest net energy importer facing this oil shock.",
    "ASIA": "Ranked first over ten years: 10.5x forward against ~52% EPS growth; near horizons cut for a rate shock on top of an energy one.",
    "PHILIPPINES": "Neutral across the curve: nominal carry is high and rising, but with August inflation at 6.1% the real carry is still not positive.",
}


GAUGE = to5(GAUGE_10)          # headline, 1-5
GAUGE_NEUTRAL = NEUTRAL_5

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
        "fee_feeder": 0.71, "fee_target": 0.00, "fee_note": "0.71% all-in (KIIDS: % of average daily NAV)",
        "gross_usd": None,                 # PHP asset - no FX translation
        "gross_local": 4.85,
        "gross_note": "10y average PH short-rate path. Anchored on the PH bill curve - 91d 5.43%, 182d 5.82%, 364d 6.04% at the 21 Sep auction, higher across the curve than when this assumption was set on 2 Sep - with BSP at 5.00% after a third consecutive hike, reverting toward a ~4.50% neutral policy rate by year 3-5. Held at 4.85% and flagged rather than re-fitted: the rise sits in the part of the path that reverts within a few years, which lifts a ten-year average by roughly a tenth of a point - inside this assumption's precision, but a known upward bias until it is re-fitted. CUT from 5.25% when the mandate lengthened to 10 years: the elevated front end is a 1-3 year feature, so over a decade far more of the path sits at neutral and the average falls toward it.",
        "vol_beta": 0.021, "fx_exposed": False,
        "macro_tilt": {"rates": +0.25, "energy": +0.05},
        "dd_k_adj": 0.0, "cash_like": True,
        "dd_k_why": "Not applicable - the cash sleeve is floored by a rate shock, not by the equity formula.",
    },
    {
        "id": "ATRQIAP", "name": "ATRAM Nasdaq Equity Income Feeder Fund",
        "short": "Nasdaq Equity Income", "ccy": "PHP (unhedged)", "region": "US",
        "target": "Target fund: JPMorgan Nasdaq Equity Premium Income Active UCITS ETF "
                  "(IE000U9J8HX9). Stated benchmark: 75% Nasdaq-100 Index.",
        "target_verified": True,
        "fee_feeder": 1.50, "fee_target": 0.35,
        "fee_note": "1.50% ATRAM management fee + 0.35% target-fund TER (both verified)",
        # COMPUTED (was a typed 7.2 that its own recipe did not produce). The premium
        # is the harvest at LONG-RUN implied vol: the base is a no-view return, and
        # "earned back as implied vol rises 14.3 -> 19.4" - the old wording - was the
        # same rise the volatility tilt pays for. It is counted there, once.
        "gross_usd": round((MACRO["ltcma_us_eq"] + MACRO["ndx_growth_premium"])
                           * MACRO["qiap_capture"] / 100 + MACRO["qiap_premium_lr"], 2),
        "gross_note": (f"NDX long-run total return of {MACRO['ltcma_us_eq'] + MACRO['ndx_growth_premium']:.1f}% "
                       f"(JPM LTCMA US large cap {MACRO['ltcma_us_eq']}% + {MACRO['ndx_growth_premium']}% NDX "
                       f"growth premium, valuation neutral at 22.4x vs 22.9x 10y avg), times "
                       f"~{MACRO['qiap_capture']}% covered-call upside capture, plus "
                       f"~{MACRO['qiap_premium_lr']}%/yr of option premium at long-run implied vol."),
        # NDX vol relative to the S&P (1.22, assumption) times the covered-call
        # vol factor, which is no longer a magic number: J.P. Morgan's own fact
        # sheet (31 Jul 2026) puts JEPQ since-inception annualised standard
        # deviation at 13.9% against the Nasdaq-100's 20.4%, i.e. 0.681. The 0.68
        # carried here for months happened to be right to two decimals, but it was
        # unsourced; it is now derived from two published figures.
        "vol_beta": 1.22 * (JEPQ_VOL / NDX_VOL), "fx_exposed": True,
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
        "fee_feeder": 1.18, "fee_target": 1.55,
        "fee_note": "1.17% trustee + 0.01% auditor (verified KIIDS) + ~1.55% estimated "
                    "target-fund OCF (ESTIMATE, anchored on JPMAM's published 1.50% "
                    "management fee for this Hong Kong unit trust; exact share-class OCF not "
                    "published, and trustee/admin costs may put it higher)",
        "gross_usd": round(MACRO["ltcma_em_eq"] + MACRO["asia_rerating"] - MACRO["asia_div_drag"], 2),
        "gross_note": (f"JPM LTCMA EM equity {MACRO['ltcma_em_eq']}% + ~{MACRO['asia_rerating']}% "
                       f"re-rating from a 10.5x forward multiple against ~52%/~28% EPS growth, less "
                       f"~{MACRO['asia_div_drag']}% for the dividend tilt's lower growth capture."),
        # ASSUMPTION, not a published figure: Asia Pacific ex-Japan vol at ~1.05x
        # the S&P, times ~0.92 for the dividend tilt's lower beta. Neither leg is
        # sourced to a manager document, and CLAIMS.md records it as an estimate.
        # Unlike the covered-call factor next door, no published pair was found to
        # anchor it. (Reviewed 2026-09-13.)
        "vol_beta": 1.05 * 0.92, "fx_exposed": True,
        "macro_tilt": {"rates": -0.05, "energy": -0.20},
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
        "fee_feeder": 1.15, "fee_target": 1.04,
        "fee_note": "1.15% ATRAM management fee (verified) + 1.04% target-fund OCF "
                    "(PUBLISHED by Fidelity for the W-Acc-GBP class, AMC 0.80%)",
        "gross_usd": round(MACRO["ltcma_us_eq"] + MACRO["tech_growth_premium"] - MACRO["tech_derating"], 2),
        "gross_note": (f"US large cap {MACRO['ltcma_us_eq']}% (JPM LTCMA) + {MACRO['tech_growth_premium']}% "
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
        "vol_beta": 1.30, "fx_exposed": True,
        "macro_tilt": {"rates": -0.40, "energy": -0.15},
        "dd_k_adj": +0.15, "cash_like": False,
        "dd_k_why": "Well above 1.65: concentrated long-duration growth has the fattest left tail on the sheet - the 2022 de-rating took the sector far past what 1.65 sigma predicts.",
    },
]

# MSCI ACWI IT regional decomposition, used to score the Global Tech sleeve
ACWI_IT_MIX = {"US": 0.72, "ASIA": 0.16, "EUROPE": 0.12}

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
DRIVER_NEUTRAL_10 = 5.5
TILT_CAL = {"monetary": 4.0, "geopolitics": 2.5,
            "date": "2026-09-02", "commit": "918c280"}
_DRV_NOW = {n: s for n, _, s, _ in DRIVERS}
MON_NOW = _DRV_NOW["Monetary policy & liquidity"]
GEO_NOW = _DRV_NOW["Geopolitics & energy"]
assert TILT_CAL["monetary"] != DRIVER_NEUTRAL_10 and TILT_CAL["geopolitics"] != DRIVER_NEUTRAL_10, \
    "a calibration reading at neutral carries no information about sensitivity"
RATES_SCALE = (MON_NOW - DRIVER_NEUTRAL_10) / (TILT_CAL["monetary"] - DRIVER_NEUTRAL_10)
ENERGY_SCALE = (GEO_NOW - DRIVER_NEUTRAL_10) / (TILT_CAL["geopolitics"] - DRIVER_NEUTRAL_10)

def regional_score(region_key):
    if region_key == "GLOBAL_TECH":
        return sum(REGIONS[r]["blend"] * w for r, w in ACWI_IT_MIX.items())
    return REGIONS[region_key]["blend"]

# ---- Per-fund return, volatility and drawdown -------------------------------

DD_K = 1.65      # calibrated: 1.65*sigma - 0.5*mu reproduces the observed median
DD_MU = 0.50     # rolling-5y max drawdown of the S&P 500 (~-20%) and NDX (~-33%)

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
    reg_tilt = rnd((rs - NEUTRAL) * REGIONAL_TILT_PER_PT)
    vol_tilt = rnd(VOL_RAMP * VOL_SENS[f["id"]])   # derived, not hand-set
    rates_tilt = rnd(t["rates"] * RATES_SCALE)     # derived from the Monetary driver
    energy_tilt = rnd(t["energy"] * ENERGY_SCALE)  # derived from Geopolitics & energy
    tilt_total = rnd(reg_tilt + vol_tilt + rates_tilt + energy_tilt)
    macro_net = base_net + tilt_total

    k = DD_K + f["dd_k_adj"]
    def dd(mu):
        raw = (k * sig - DD_MU * mu) * DD_HORIZON_SCALAR
        if f["cash_like"]:
            # Money market: bounded by a 100bp parallel shock on ~0.5y duration
            # less one year of carry - it cannot behave like an equity fund. This
            # floor is NOT horizon-scaled: a rate shock on a half-year duration
            # book is the same size whether you hold it 5 years or 10.
            return max(0.5, min(raw, 0.9))
        return max(raw, 0.0)

    return {
        **{q: f[q] for q in ("id", "name", "short", "ccy", "region", "target",
                             "target_verified", "fee_note", "gross_note")},
        "fee_feeder": f["fee_feeder"], "fee_target": f["fee_target"],
        "fee_total": round(fee, 2),
        "gross_php": round(gross_php, 2),
        "fx_drift": FX_DRIFT if f["fx_exposed"] else 0.0,
        "net_base": round(base_net, 2),
        "regional_score": round(rs, 2),
        "tilt_regional": round(reg_tilt, 2),
        "tilt_vol": vol_tilt, "tilt_rates": rates_tilt, "tilt_energy": energy_tilt,
        "tilt_rates_cal": t["rates"], "tilt_energy_cal": t["energy"],
        "tilt_total": round(tilt_total, 2),
        "net_macro": round(macro_net, 2),
        "vol": round(sig, 2),
        "dd_k": round(k, 2), "dd_k_why": f["dd_k_why"],
        "dd_base": round(-dd(base_net), 1),
        "dd_macro": round(-dd(macro_net), 1),
        # THE TARGET FUND ITSELF (the ETF / SICAV each feeder buys): the same
        # exposure, in pesos, net of its OWN charge only - i.e. the sleeve's
        # return with the feeder's fee added back. Derived, not a separate
        # estimate; the gap to net_macro is exactly what the feeder layer costs.
        # None for the money market, whose "target" is its own mandate.
        "target_net_macro": None if f["cash_like"] else round(macro_net + f["fee_feeder"], 2),
        "target_dd_macro": None if f["cash_like"] else round(-dd(macro_net + f["fee_feeder"]), 1),
    }

F = [build_fund(f) for f in FUNDS]

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

def port_vol(w):
    s = [w[i] * F[i]["vol"] for i in range(4)]
    v = 0.0
    for i in range(4):
        for j in range(4):
            v += s[i] * s[j] * CORR[i][j]
    return math.sqrt(v)

def port_ret(w, key):
    return sum(w[i] * F[i][key] for i in range(4))

def port_k(w):
    """Weight-averaged drawdown coefficient, ex-cash (cash contributes no equity DD)."""
    eq = sum(w[i] for i in range(4) if not FUNDS[i]["cash_like"])
    if eq <= 0:
        return DD_K
    return DD_K + sum(w[i] * FUNDS[i]["dd_k_adj"] for i in range(4)
                      if not FUNDS[i]["cash_like"]) / eq

def port_dd(w, key):
    mu = port_ret(w, key)
    return -max((port_k(w) * port_vol(w) - DD_MU * mu) * DD_HORIZON_SCALAR, 0.0)

def summarise(w, key):
    r, v, d = port_ret(w, key), port_vol(w), port_dd(w, key)
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
    d_d = round(-max((port_k(w) * v_d - DD_MU * r_d) * DD_HORIZON_SCALAR, 0.0), 1)
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

LOOKTHROUGH = {
    "ATRPHMM": {
        "dp": 3,
        "kind": "instruments",
        # Dated by the AUCTION, not by AS_OF. The 2026-09-13 fix replaced a wrong
        # "2026-08" label with AS_OF on the theory that these were the live curve;
        # they were not refreshed again, so AS_OF made a 2 Sep curve look current
        # for eleven days. A date must belong to the number it labels.
        "as_of": MACRO["ph_tbill_date"],
        "note": "A money market fund holds paper, not shares. The live PH curve "
                "is the honest look-through.",
        "rows": [["91-day T-bill", MACRO["ph_tbill_91"]],
                 ["182-day T-bill", MACRO["ph_tbill_182"]],
                 ["364-day T-bill", MACRO["ph_tbill_364"]]],
        "unit": "% yield",
        "source": "Bureau of the Treasury PH auction results",
    },
    "ATRQIAP": {
        "dp": 1,
        "kind": "stocks",
        "as_of": "2026-07-31",
        "note": "Top 10 equity positions of the JPMorgan Nasdaq Equity Premium "
                "Income strategy. Figures are from the US-listed JEPQ factsheet; "
                "ATRAM's feeder holds the UCITS sister fund (IE000U9J8HX9), which "
                "runs the same strategy on the same universe. The 31 July sheet "
                "is still the latest JPMorgan has published (checked 2026-09-24).",
        "rows": [["NVIDIA", 6.9], ["Apple", 6.4], ["Alphabet Class C", 5.3],
                 ["Microsoft", 5.0], ["Amazon", 4.3], ["Micron Technology", 4.1],
                 ["Advanced Micro Devices", 3.3], ["Meta Platforms", 2.4],
                 ["Broadcom", 2.3], ["Lam Research", 2.0]],
        "unit": "% of fund",
        "sectors": [["Information Technology", 47.7]],
        "source": "J.P. Morgan Asset Management JEPQ factsheet, 31 July 2026",
    },
    "ATRASEQ": {
        "dp": 1,
        "kind": "gap",
        "as_of": None,
        "note": "The JPMorgan Asia Equity Dividend Fund's current holdings could "
                "not be verified from a primary source. The most recent published "
                "holdings reachable were from 2023 and are too stale to show. What "
                "is verified is the mandate: at least 70% in dividend-paying Asia "
                "Pacific ex-Japan equities.",
        "rows": [],
        "unit": None,
        "source": "gap recorded rather than filled - retry at each manual review",
    },
    "ATRGTEC": {
        "dp": 2,
        "kind": "sectors",
        # Was dated "2026" - a year, which is not a date and cannot be checked for
        # staleness. This is now the RETRIEVAL date, and the note says so: Fidelity's
        # factsheet page does not expose its own snapshot date at the source
        # reachable from here, so the figures are its latest published month-end
        # rather than 13 September. Refreshed the same day; every weight had moved
        # and the residual line changed from "Managed funds" to "Cash and
        # equivalents". (Audit 2026-09-13.)
        "as_of": "2026-09-13",
        "note": "Fidelity publishes this fund's sector weights (Industry "
                "Classification Benchmark) but no current top-10 list at a source "
                "reachable from here. Dated when read: the page shows no snapshot "
                "date, so these are Fidelity's latest month-end.",
        "rows": [["Technology", 66.45], ["Consumer Discretionary", 11.99],
                 ["Industrials", 10.40], ["Telecommunications", 6.47],
                 ["Real Estate", 2.67], ["Energy", 0.95],
                 ["Cash and equivalents", 0.47]],
        "unit": "% of fund",
        "sub": [["Technology hardware & equipment", 33.28],
                ["Software & computer services", 32.02]],
        "source": "Fidelity Funds - Global Technology Fund factsheet (LU1033663649)",
    },
}

# ----------------------------------------------------------------------------
# 6. PORTFOLIOS
# ----------------------------------------------------------------------------

GRID = [x / 100 for x in range(0, 101, 5)]      # every weight ends in 5 or 0

# NO SINGLE-SLEEVE CAP - removed 2026-09-24 at the portfolio owner's instruction.
# A 50% cap applied from 2026-09-09: it was added when the Asia fee correction
# sent the optimiser to 75% in one fund, and it bound on Nasdaq Equity Income
# every day since. Removing it is a stated choice about concentration, not a
# model finding: on the model's own numbers it buys ~0.12pp of CAGR and a
# slightly shallower drawdown, and puts three-quarters of the portfolio in one
# feeder, one manager and one covered-call strategy. The page publishes what the
# 50% cap would have chosen (CAP_COUNTERFACTUAL) beside what it chooses now, so
# the trade stays visible. What remains is the 5% floor that keeps all four
# funds held (invariant 1) - which also bounds any one sleeve at 85% - and the
# drawdown budget, which is what now stops the concentration.
MIN_SLEEVE = 0.05

def enumerate_portfolios(key, min_w=MIN_SLEEVE):
    """All 5%-granular, fully-invested portfolios holding all four funds at the
    minimum weight or above."""
    out = []
    for a in GRID:
        if a < min_w: continue
        for b in GRID:
            if b < min_w: continue
            for c in GRID:
                if c < min_w: continue
                d = round(1 - a - b - c, 10)
                if d < min_w - 1e-9: continue
                if round(d * 100) % 5 != 0: continue
                w = [a, b, c, d]
                out.append((w, summarise(w, key)))
    return out

# --- Baseline: pure strategic over the mandate horizon, no macro view -------
# Horizon-appropriate growth allocation: a 20% liquidity/volatility buffer and
# the three equity engines held near-equally. This is what you would own if you
# had the mandate horizon and NO view on the cycle.
BASELINE_W = [0.20, 0.30, 0.25, 0.25]
BASE = summarise(BASELINE_W, "net_base")
BASE_UNDER_MACRO = summarise(BASELINE_W, "net_macro")

# --- Optimised: maximise macro-adjusted CAGR subject to a drawdown budget ----
# Objective: the user asked for maximum net CAGR with drawdown held to a
# minimum. A pure max-return solve just buys 90% Global Tech; a pure min-DD
# solve just buys cash. The defensible reading is: beat the baseline's return
# AND cut its drawdown. So we solve for max CAGR subject to
#   maxDD <= baseline maxDD - 2.0pp  (a hard, stated improvement)
# 2.0pp was the stated improvement at the 5-year calibration. Drawdowns are
# ~41% deeper at a 10-year horizon, so holding the budget at a flat 2.0pp would
# quietly LOOSEN the objective. It is scaled by the same factor as the drawdowns
# it constrains, so the constraint means what it meant before.
DD_BUDGET_IMPROVEMENT = round(2.0 * DD_HORIZON_SCALAR, 2)
DD_CAP = abs(BASE_UNDER_MACRO["maxdd"]) - DD_BUDGET_IMPROVEMENT

ALL = enumerate_portfolios("net_macro")
# Test the TRUE drawdown, not the rounded one the page displays. Filtering on
# round(d, 1) admitted portfolios up to 0.05pp over the stated budget - four of
# them, at the last audit - because -18.5099 displays as -18.5. The winner was
# unaffected, but a constraint that says "<= cap" must actually mean it.
# (Audit 2026-09-03.)
# BOTH ROUTES, because each alone admits a portfolio the other rejects. Testing
# only the rounded value admits one up to 0.05pp genuinely over budget (the
# 2026-09-03 finding above). Testing only the raw value admits one that PRINTS as
# over budget: [25, 30, 25, 20] came out 26.1477 raw, inside a 26.17 cap, and
# published -26.2, which a reader comparing against the printed cap reads as a
# breach. It surfaced on 2026-09-20 when the regional-blend fix moved returns a
# hundredth and broke the coincidence that had been hiding it. A portfolio is
# feasible only if it respects the cap as computed AND as shown.
FEASIBLE = [(w, s) for w, s in ALL
            if abs(port_dd(w, "net_macro")) <= DD_CAP + 1e-9
            and abs(s["maxdd"]) <= DD_CAP + 1e-9]
FEASIBLE.sort(key=lambda t: (-t[1]["cagr"], abs(t[1]["maxdd"])))
OPT_W, OPT = FEASIBLE[0]

# PORTFOLIO C - the owner's pinned variant (requested 2026-09-25): Nasdaq Equity
# Income held at exactly 50%, the other three optimised around it on the same
# inputs, the same 5% grid and floor, and the same drawdown budget. The objective
# is the owner's "maximum growth with drawdown controlled to a minimum", made
# explicit: take the best CAGR the budget allows, then, among portfolios within
# PIN_TIE_PP of it, the one with the LOWEST drawdown - a return difference smaller
# than the model's own rounding is not worth more drawdown.
PIN_FUND, PIN_W, PIN_TIE_PP = 1, 0.50, 0.05
_pin_feas = [(w, s2) for w, s2 in FEASIBLE if abs(w[PIN_FUND] - PIN_W) < 1e-9]
_pin_best = max(s2["cagr"] for _, s2 in _pin_feas)
PIN_W_ALL, PIN = min(((w, s2) for w, s2 in _pin_feas if s2["cagr"] >= _pin_best - PIN_TIE_PP - 1e-9),
                     key=lambda t: (abs(t[1]["maxdd"]), -t[1]["cagr"]))
OPT_UNDER_BASE = summarise(OPT_W, "net_base")

# What the former 50% single-sleeve cap would choose under the same objective and
# the same drawdown budget - published so the cost and benefit of removing it are
# computed, not asserted.
CAP_COUNTERFACTUAL_MAX = 0.50
_capw, _caps = next((w, s) for w, s in FEASIBLE if max(w) <= CAP_COUNTERFACTUAL_MAX + 1e-9)
CAP_COUNTERFACTUAL = {"max_sleeve": CAP_COUNTERFACTUAL_MAX,
                      "weights": [round(x * 100) for x in _capw],
                      "cagr": _caps["cagr"], "maxdd": _caps["maxdd"],
                      "ret_per_dd": _caps["ret_per_dd"]}

# WHAT WOULD CHANGE THIS VIEW - computed, not asserted. The page's list said that
# "Brent below $70 and the Fed cutting" would send Global Technology "back to a full
# weight"; re-running the optimiser showed the allocation does not move at all. Each
# counterfactual here is the SAME optimiser on an alternative return column, with
# the drawdown budget re-derived from the baseline under that column exactly as
# DD_CAP is, so the only thing that differs is the input named.
for _f in F:
    _f["net_novol"] = round(_f["net_macro"] - _f["tilt_vol"], 2)       # flat VIX curve
    _f["net_neutral"] = round(_f["net_macro"] - _f["tilt_rates"]
                              - _f["tilt_energy"], 2)                  # drags at neutral

def optimise(key):
    cap = abs(summarise(BASELINE_W, key)["maxdd"]) - DD_BUDGET_IMPROVEMENT
    feas = [(w, s) for w, s in enumerate_portfolios(key)
            if abs(port_dd(w, key)) <= cap + 1e-9 and abs(s["maxdd"]) <= cap + 1e-9]
    feas.sort(key=lambda t: (-t[1]["cagr"], abs(t[1]["maxdd"])))
    w, s = feas[0]
    return {"weights": [round(x * 100) for x in w], "cagr": s["cagr"],
            "maxdd": s["maxdd"], "dd_cap": round(cap, 2)}

# THE TWO ASSUMPTIONS THE 2026-09-25 CORRECTION LEFT CARRYING THE RESULT, tested
# the same way: the Asia base's +1.0% re-rating credit (which overlaps both the
# LTCMA's own valuation component and the Valuation driver in the regional tilt),
# and its ESTIMATED target-fund charge (a Hong Kong unit trust whose trustee and
# admin costs may put the OCF above the 1.55% carried). A result that one
# assumption can overturn is published with that assumption named.
ASIA_FEE_STRESS = 0.25
# THE 2026-09-25 CORRECTION, published as a record so the page can say what changed
# with numbers that trace. These are the values the page carried until that date.
CORRECTION = {"date": "2026-09-25", "weights_before": [15, 70, 10, 5],
              "cagr_before": 7.46, "maxdd_before": -26.9,
              "qiap_gross_usd_before": 7.2, "qiap_net_before": 8.0,
              "qiap_tilt_vol_before": 0.96, "gtec_tilt_vol_before": -0.56}
for _f in F:
    _aseq = _f["id"] == "ATRASEQ"
    _f["net_asia_norerate"] = round(_f["net_macro"] - (MACRO["asia_rerating"] if _aseq else 0.0), 2)
    _f["net_asia_fee_hi"] = round(_f["net_macro"] - (ASIA_FEE_STRESS if _aseq else 0.0), 2)
WHAT_IF = {"vol_flat": optimise("net_novol"), "drags_neutral": optimise("net_neutral"),
           "asia_no_rerating": optimise("net_asia_norerate"),
           "asia_fee_hi": optimise("net_asia_fee_hi")}
WHAT_IF["asia_fee_hi"]["stress_pp"] = ASIA_FEE_STRESS

# Best pure risk-adjusted portfolio, for reference
BEST_RATIO_W, BEST_RATIO = max(ALL, key=lambda t: t[1]["ret_per_dd"])


# ---- What the Global Technology stub actually costs --------------------------
# The report argues for keeping a 5% Global Technology position rather than
# cutting it to zero. That argument is only honest if the price of the stub is
# stated, and stated correctly: until the 2026-09-05 audit the page claimed
# "roughly 0.03pp", which was never re-derived after the tilts moved. It is now
# computed here against the SAME objective the optimiser uses - maximise CAGR
# subject to the drawdown cap - over the portfolios the enumeration excludes
# because they drop a fund entirely.
def _best_without(idx):
    best = None
    step = 5
    for a in range(0, 101, step):
        for b in range(0, 101 - a, step):
            for c in range(0, 101 - a - b, step):
                w = [a, b, c, 100 - a - b - c]
                if w[idx] != 0:
                    continue
                # Every sleeve EXCEPT the excluded one must still be held at the
                # minimum. Without this the counterfactual could drop a second
                # fund - [50, 50, 0, 0] was reachable - and the stub's "cost" would
                # be measured against a two-fund portfolio the objective forbids,
                # exactly the error the concentration-cap guard below was added to
                # prevent. It did not bite today ([15, 50, 35, 0] holds all three),
                # but nothing stopped it. (Audit 2026-09-14.)
                if any(i != idx and x < MIN_SLEEVE * 100 - 1e-9 for i, x in enumerate(w)):
                    continue
                ww = [x / 100 for x in w]
                if abs(port_dd(ww, "net_macro")) > DD_CAP + 1e-9:
                    continue
                sm = summarise(ww, "net_macro")
                if best is None or sm["cagr"] > best[1]["cagr"]:
                    best = (w, sm)
    return best

_GT_FREE_W, _GT_FREE = _best_without(3)
STUB = {
    "fund": "ATRGTEC",
    "weight": round(OPT_W[3] * 100),
    "best_without": _GT_FREE_W,
    "cagr_without": _GT_FREE["cagr"],
    "cagr_with": OPT["cagr"],
    "cost": round(_GT_FREE["cagr"] - OPT["cagr"], 2),
}

# Gap between the two US-tech sleeves' macro-adjusted net CAGR. Quoted in the
# report; derived here so it cannot drift from the funds it describes.
_Q = next(f for f in F if f["id"] == "ATRQIAP")
_G = next(f for f in F if f["id"] == "ATRGTEC")
TECH_GAP = round(_G["net_macro"] - _Q["net_macro"], 2)

# Efficient frontier: max CAGR at each 1pp drawdown bucket
# THE TRUE EFFICIENT SET, NOT WHOLE-PERCENT BUCKETS. Corrected 2026-09-25. The
# frontier was the best CAGR in each 1pp drawdown bucket, so a bucket could be won by
# a portfolio just OVER the drawdown budget - [25, 5, 65, 5] at -27.8% took the -27
# bucket from the optimum at -27.1% - and the plotted line ran above the optimum the
# page says "sits on that edge". Now: every portfolio no other beats on both CAGR and
# drawdown, thinned to ~1pp spacing for the chart, with the optimum always kept.
_pts = sorted(ALL, key=lambda t: (abs(t[1]["maxdd"]), -t[1]["cagr"]))
PARETO, _best = [], -1e9
for w, s in _pts:
    if s["cagr"] > _best + 1e-9:
        PARETO.append((w, s)); _best = s["cagr"]
FRONTIER_SPACING = 0.9
FRONTIER, _last = [], None
for w, s in PARETO:
    _is_opt = [round(x * 100) for x in w] == [round(x * 100) for x in OPT_W]
    if _is_opt or _last is None or abs(s["maxdd"]) >= _last + FRONTIER_SPACING:
        FRONTIER.append((w, s)); _last = abs(s["maxdd"])
# "maxdd" is the BUCKET (whole-percent floor); "dd" is the point's own published
# drawdown. The page plotted and labelled points at the bucket - "-28%" for a
# -28.7% portfolio, and the optimised marker (at its true -25.4) sat beside its
# own frontier point (at 25). Both are published so the chart can use the real one.
FRONTIER = [{"maxdd": abs(v[1]["maxdd"]), "dd": v[1]["maxdd"], "cagr": v[1]["cagr"],
             "weights": v[1]["weights"]} for v in FRONTIER]

# ----------------------------------------------------------------------------
# 7. SCENARIO / STRESS GRID
# ----------------------------------------------------------------------------
# Each scenario is an additive shock (pp, annualised over 5y) per fund and a
# vol multiplier, keyed to a live, named risk in the current macro picture.
SCENARIOS = [
    ("Hormuz escalation", "Already partly running since the late-August tanker strikes. "
     f"This row models the tail: full Strait closure and Brent to ${MACRO['brent_closure']:.0f}+ from "
     f"${MACRO['brent']:.0f}. Global CPI re-accelerates, the Fed is forced to hike, and "
     "multiples compress hardest at the long end.",
     {"ATRPHMM": +0.5, "ATRQIAP": -4.5, "ATRASEQ": -6.5, "ATRGTEC": -7.5}, 1.60),
    ("Hawkish repricing", "A second hike on top of the one the dot plot already has "
     f"(median {MACRO['fed_dot_2026']}% for end-2026) - {MACRO['fed_dots_two_more']} of "
     f"{MACRO['fed_dots_participants']} participants see it. The Fed hikes into a 4.1% "
     "unemployment rate; duration-heavy growth de-rates.",
     {"ATRPHMM": +0.8, "ATRQIAP": -2.5, "ATRASEQ": -2.0, "ATRGTEC": -5.0}, 1.30),
    ("AI capex digestion", "Semis order book rolls over; the 52% Asia EPS "
     "estimate is cut. Hits the AI supply chain and mega-cap tech together.",
     {"ATRPHMM": 0.0, "ATRQIAP": -3.5, "ATRASEQ": -5.5, "ATRGTEC": -8.0}, 1.45),
    ("Disinflation restart", "Oil mean-reverts to $65, headline CPI falls to 2%, "
     "Fed cuts. The bull case: multiples expand, vol collapses.",
     {"ATRPHMM": -0.9, "ATRQIAP": +2.5, "ATRASEQ": +3.5, "ATRGTEC": +4.5}, 0.80),
    ("Grind-on base case", "Vol drifts up to the 19-20 the futures curve already "
     "prices, earnings hold, no policy accident. The modelled path.",
     {"ATRPHMM": 0.0, "ATRQIAP": 0.0, "ATRASEQ": 0.0, "ATRGTEC": 0.0}, 1.00),
]

def run_scenarios(w, key):
    rows = []
    for name, desc, shock, volmul in SCENARIOS:
        r = sum(w[i] * (F[i][key] + shock[F[i]["id"]]) for i in range(4))
        s = [w[i] * F[i]["vol"] * volmul for i in range(4)]
        v = math.sqrt(sum(s[i] * s[j] * CORR[i][j] for i in range(4) for j in range(4)))
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
        d = -max((port_k(w) * v_d - DD_MU * r_d) * DD_HORIZON_SCALAR, 0.0)
        rows.append({"name": name, "desc": desc, "cagr": r_d,
                     "vol": v_d, "maxdd": round(d, 1)})
    return rows

# ----------------------------------------------------------------------------
# 8. SOURCES
# ----------------------------------------------------------------------------
SOURCES = [
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
    ("IMF", "World Economic Outlook, April 2026 - 'Global Economy in the Shadow of War'",
     "https://www.imf.org/en/publications/weo/issues/2026/04/14/world-economic-outlook-april-2026"),
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
    ("Federal Reserve", "H.15 Selected Interest Rates (Daily) - the 10-year constant-maturity yield closed 4.94% on 17 September 2026. This model had published 4.94% as the EIGHTEENTH's close",
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
    ("thetrading.tools", "VIX term structure, 11 September 2026 close - VIX 15.84, VIX3M 18.60, IVTS 0.8516. Used ONLY as an independent check on the bootstrapped curve; it is not an input to it",
     "https://www.thetrading.tools/vix-term-structure"),
    ("J.P. Morgan Asset Management", "2026 Long-Term Capital Market Assumptions - US equity 6.7%, EM equity 7.8%",
     "https://am.jpmorgan.com/us/en/asset-management/adv/about-us/media/press-releases/jp-morgan-releases-2026-long-term-capital-market-assumptions/"),
    ("J.P. Morgan Asset Management", "Nasdaq Equity Premium Income Active UCITS ETF (IE000U9J8HX9) factsheet - 0.35% TER",
     "https://am.jpmorgan.com/content/dam/jpm-am-aem/asiapacific/sg/en/literature/fact-sheet/factsheet-jpmorgan-nasdaq-equity-premium-income-active-ucits-etf.pdf"),
    ("Fidelity International", "Fidelity Funds - Global Technology Fund factsheet",
     "https://www.fidelityinternational.com/legal/documents/SG-en/hffs.SG-en.SG.G-TEC.pdf"),
    ("ATRAM Trust Corporation", "Fund pages and KIIDS - fees, target funds, benchmarks",
     "https://www.atram.com.ph/funds/selector"),
    ("UITF.com.ph (TOAP)", "Official Philippine UITF daily NAVpu portal",
     "https://www.uitf.com.ph/"),
    ("BusinessWorld", "ATRAM launches Nasdaq income feeder fund - 1.50% fee, 75% NDX benchmark",
     "https://bworldonline.com/banking-finance/2026/04/29/746186/atram-launches-nasdaq-income-feeder-fund/"),
    ("Philippine Star", "ATRAM launches Nasdaq feeder fund",
     "https://www.philstar.com/business/2026/04/29/2524247/atram-launches-nasdaq-feeder-fund"),
    ("J.P. Morgan Asset Management", "JEPQ factsheet, 30 June 2026 - top-10 holdings and sector weights used for the stock-level look-through",
     "https://am.jpmorgan.com/content/dam/jpm-am-aem/americas/us/en/literature/fact-sheet/etfs/FS-JEPQ.PDF"),
    ("Fidelity International", "Global Technology Fund W-Acc-GBP (LU1033663649) portfolio - sector composition",
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
    ("Euronews", "Saudi Arabia reports fresh Houthi attacks as France offers military "
     "support to protect Yanbu, 25 September 2026",
     "https://www.euronews.com/2026/09/25/saudi-arabia-reports-fresh-houthi-attacks-as-france-offers-military-support-to-protect-yan"),
    ("CNBC", "Stock market news for Sept. 25, 2026 - S&P 500 +0.51% to 7,743.41, Dow "
     "+478.64 (+0.93%) to 51,828.62, Nasdaq +0.5% to 27,068.72; WTI -2.33% to $92.41",
     "https://www.cnbc.com/2026/09/24/stock-market-today-live-updates.html"),
    ("BEA / BLS", "Release schedules - Personal Income and Outlays, August 2026, on "
     "30 September; Employment Situation, September 2026, on 2 October",
     "https://www.bls.gov/schedule/news_release/current_year.asp"),
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
        "correction": CORRECTION,
        "vol_channel": {"blend": round(VOL_BLEND, 2), "spot": MACRO["vix_spot"],
                        "longrun": MACRO["vix_longrun"], "ramp_ref": VOL_RAMP_REF,
                        "quote_date": VIX_QUOTE_DATE,
                        "latest": MACRO["vix_latest"],
                        "latest_date": MACRO["vix_latest_date"],
                        "latest_gap": round(MACRO["vix_latest"] - MACRO["vix_spot"], 2),
                        "ramp": round(VOL_RAMP, 2), "sens": VOL_SENS,
                        # The independent market read, and the measured cost of the
                        # strip's age. Published so the page can state the gap
                        # rather than the reader having to infer it.
                        "vix3m": MACRO["vix3m"], "vix3m_date": MACRO["vix3m_date"],
                        "vix3m_model": round(VIX3M_MODEL, 2),
                        "vix3m_resid": VIX3M_RESID,
                        "strip_age_d": (_dt.date.fromisoformat(REVIEW_DATE)
                                        - _dt.date.fromisoformat(VIX_QUOTE_DATE)).days},
        # Each driver is RESEARCHED on 1-10 (score_10) - the granularity the evidence
        # supports, and the scale every note below is written against - and REPORTED on
        # 1-5 (score) by the same endpoint-preserving rescale used for the gauge and the
        # regional rankings. Since to5() is affine and the weights sum to 1, the weighted
        # composite of the REPORTED scores is exactly the headline gauge; the check block
        # asserts that rather than assuming it.
        "drivers": [{"name": n, "weight": w,
                     "score": to5(s), "score_10": s, "note": t, "summary": SUMMARY[n]}
                    for n, w, s, t in DRIVERS],
        "driver_scale": {"research_max": 10, "reported_max": 5,
                         "neutral": NEUTRAL_5, "neutral_10": 5.5},
        "gauge": GAUGE, "gauge_10": GAUGE_10, "gauge_neutral": GAUGE_NEUTRAL,
        "funds": F, "corr": CORR, "corr_note": CORR_NOTE,
        "lookthrough": LOOKTHROUGH,
        "acwi_it_mix": ACWI_IT_MIX,
        # The covered-call sleeve's vol factor, published so it is auditable rather
        # than a constant folded into vol_beta.
        "jepq_vol": JEPQ_VOL, "ndx_vol": NDX_VOL, "jepq_beta": JEPQ_BETA,
        "cc_vol_factor": round(JEPQ_VOL / NDX_VOL, 4),
        "fx": {"drift": FX_DRIFT, "vol": FX_VOL, "corr": FX_CORR,
               "ppp_lr": round(FX_PPP_PH_LR - FX_PPP_US_LR, 2),
               "ppp_now": round(MACRO["ph_cpi_aug"] - MACRO["us_cpi_headline"], 2)},
        "vix_quote_date": VIX_QUOTE_DATE,
        "review_date": REVIEW_DATE,
        # Published so the page never has to type them: the regional tilt coefficient
        # and the peso sleeve's real yield were the last two hard-typed figures in the
        # static markup with no payload counterpart. (Audit 2026-09-11.)
        "regional_tilt_per_pt": REGIONAL_TILT_PER_PT,
        # The calibration record for the driver transmission, published so the
        # page-level and independent harnesses can re-derive every rates and energy
        # tilt from the driver scores without importing this file.
        "driver_tilt_cal": {**TILT_CAL, "neutral_10": DRIVER_NEUTRAL_10,
                            "rates_scale": round(RATES_SCALE, 6),
                            "energy_scale": round(ENERGY_SCALE, 6)},
        "real_yield": {
            "cpi": MACRO["ph_cpi_aug"],
            "t91": round(MACRO["ph_tbill_91"] - MACRO["ph_cpi_aug"], 2),
            "t364": round(MACRO["ph_tbill_364"] - MACRO["ph_cpi_aug"], 2),
        },
        "catalysts": [{"date": d, "what": w, "why": y} for d, w, y in CATALYSTS],
        "postponed": [{"what": w, "why": y} for w, y in POSTPONED],
        "dd_model": {"k": DD_K, "mu_coef": DD_MU,
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
                     "optimized_k": round(port_k(OPT_W), 5),
                     "note": "1.65 is the calibration anchor, not the coefficient every sleeve "
                             "uses. Each fund carries a declared adjustment for the shape of its "
                             "own left tail; the portfolio coefficient is the weighted average "
                             "across the equity sleeves. The whole quantity is then scaled by "
                             "sqrt(horizon / calibration window), because expected maximum "
                             "drawdown grows with the square root of the horizon - the -20% and "
                             "-33% anchors are rolling FIVE-year medians and cannot simply be "
                             "relabelled for a longer mandate."},
        "baseline": {"weights": [round(x*100) for x in BASELINE_W],
                     "base": BASE, "under_macro": BASE_UNDER_MACRO,
                     "scenarios": run_scenarios(BASELINE_W, "net_macro")},
        "optimized": {"weights": [round(x*100) for x in OPT_W],
                      "macro": OPT, "under_base": OPT_UNDER_BASE,
                      # Published at the precision it is ENFORCED at. It was
                      # round(DD_CAP, 1) = 26.0 against an enforced 25.97, so the
                      # published constraint was looser than the real one and an
                      # independent re-derivation got 370 feasible portfolios where
                      # the engine got 368. (Audit 2026-09-08.)
                      "dd_cap": round(DD_CAP, 2),
                      "scenarios": run_scenarios(OPT_W, "net_macro"),
                      "n_feasible": len(FEASIBLE), "n_total": len(ALL)},
        "pinned": {"weights": [round(x*100) for x in PIN_W_ALL], "macro": PIN,
                   "fund": FUNDS[PIN_FUND]["id"], "pin_pct": round(PIN_W * 100),
                   "tie_pp": PIN_TIE_PP, "best_cagr": _pin_best,
                   "n_feasible": len(_pin_feas),
                   "scenarios": run_scenarios(PIN_W_ALL, "net_macro"),
                   # the allocation-deciding assumption, applied to both
                   "cagr_no_rerating": summarise(PIN_W_ALL, "net_asia_norerate")["cagr"],
                   "opt_cagr_no_rerating": summarise(OPT_W, "net_asia_norerate")["cagr"]},
        "best_ratio": {"weights": [round(x*100) for x in BEST_RATIO_W], **BEST_RATIO},
        "stub": STUB, "tech_gap": TECH_GAP,
        "min_sleeve": MIN_SLEEVE,
        "cap_counterfactual": CAP_COUNTERFACTUAL,
        "what_if": WHAT_IF,
        "frontier": FRONTIER,
        "sources": [{"org": o, "what": w, "url": u} for o, w, u in SOURCES],
    }

def report():
    p = payload()
    L = []
    A = L.append
    A(f"ATRAM PORTFOLIO ENGINE - audit report  (as of {AS_OF})")
    A("=" * 78)
    A("\n[1] VOLATILITY TERM STRUCTURE (forward-variance integration of the VIX complex)")
    A(f"    spot VIX {MACRO['vix_spot']}  |  Sep fut {MACRO['vix_fut_sep']}  |  "
      f"Dec fut {MACRO['vix_fut_dec']}  |  long-run anchor {MACRO['vix_longrun']}")
    A(f"    {'H':<5}{'implied':>10}{'realised':>10}{'1sd move':>11}{'2sd move':>11}")
    for v in p["vol_ts"]:
        A(f"    {v['label']:<5}{v['implied']:>9.2f}%{v['realised']:>9.2f}%"
          f"{v['move_1sd']:>10.2f}%{v['move_2sd']:>10.2f}%")
    A("\n[2] REGIONAL MACRO-DRIVER RANKING (1-5, neutral 3.0)")
    A(f"    {'region':<14}{'3M':>6}{'6M':>6}{'12M':>6}{HZ_LABEL:>6}{'blend':>8}")
    for k, v in sorted(p["regions"].items(), key=lambda t: -t[1]["blend"]):
        A(f"    {k:<14}{v['3M']:>6}{v['6M']:>6}{v['12M']:>6}{v[HZ_LABEL]:>6}{v['blend']:>8}")
    A("\n[3] BROAD MACRO GAUGE (drivers reported 1-5, researched 1-10)")
    for d in p["drivers"]:
        A(f"    {d['name']:<30} w={d['weight']:.2f}  "
          f"score={d['score']:.2f} / 5   ({d['score_10']:.1f} / 10)")
    A(f"    {'COMPOSITE (research scale)':<30}            {p['gauge_10']} / 10")
    A(f"    {'HEADLINE GAUGE':<30}            {p['gauge']} / 5"
      f"   (neutral {p['gauge_neutral']})")
    A(f"\n[4] FUNDS - net {HZ_LABEL} CAGR after ALL fees, and expected max drawdown")
    A(f"    {'fund':<22}{'fee':>7}{'gross':>8}{'base':>8}{'tilt':>7}{'macro':>8}"
      f"{'vol':>8}{'DD base':>9}{'DD macro':>10}")
    for f in p["funds"]:
        A(f"    {f['short']:<22}{f['fee_total']:>6.2f}%{f['gross_php']:>7.2f}%"
          f"{f['net_base']:>7.2f}%{f['tilt_total']:>+7.2f}{f['net_macro']:>7.2f}%"
          f"{f['vol']:>7.2f}%{f['dd_base']:>8.1f}%{f['dd_macro']:>9.1f}%")
    A("\n[5] PORTFOLIOS   (order: MM / Nasdaq Income / Asia / Global Tech)")
    b, o = p["baseline"], p["optimized"]
    A(f"    BASELINE  weights {b['weights']}")
    A(f"      strategic view : CAGR {b['base']['cagr']}%  vol {b['base']['vol']}%  "
      f"maxDD {b['base']['maxdd']}%  ret/DD {b['base']['ret_per_dd']}")
    A(f"      macro view     : CAGR {b['under_macro']['cagr']}%  vol {b['under_macro']['vol']}%  "
      f"maxDD {b['under_macro']['maxdd']}%  ret/DD {b['under_macro']['ret_per_dd']}")
    A(f"    OPTIMIZED weights {o['weights']}   (DD cap {o['dd_cap']}%, "
      f"{o['n_feasible']}/{o['n_total']} feasible)")
    A(f"      macro view     : CAGR {o['macro']['cagr']}%  vol {o['macro']['vol']}%  "
      f"maxDD {o['macro']['maxdd']}%  ret/DD {o['macro']['ret_per_dd']}")
    A(f"      strategic view : CAGR {o['under_base']['cagr']}%  vol {o['under_base']['vol']}%  "
      f"maxDD {o['under_base']['maxdd']}%  ret/DD {o['under_base']['ret_per_dd']}")
    A(f"    DELTA (macro view): CAGR {o['macro']['cagr'] - b['under_macro']['cagr']:+.2f}pp   "
      f"maxDD {o['macro']['maxdd'] - b['under_macro']['maxdd']:+.1f}pp   "
      f"ret/DD {o['macro']['ret_per_dd'] - b['under_macro']['ret_per_dd']:+.3f}")
    A(f"    best pure ret/DD  : {p['best_ratio']['weights']}  CAGR {p['best_ratio']['cagr']}%  "
      f"maxDD {p['best_ratio']['maxdd']}%  ratio {p['best_ratio']['ret_per_dd']}")
    A("\n[6] SCENARIOS (optimized portfolio)")
    for s in o["scenarios"]:
        A(f"    {s['name']:<24} CAGR {s['cagr']:>6.2f}%   vol {s['vol']:>5.2f}%   maxDD {s['maxdd']:>6.1f}%")
    A("\n[7] SANITY CHECKS")
    checks = []
    checks.append(("baseline weights sum to 100", sum(b["weights"]) == 100))
    checks.append(("optimized weights sum to 100", sum(o["weights"]) == 100))
    checks.append(("all baseline weights end in 5 or 0", all(x % 5 == 0 for x in b["weights"])))
    checks.append(("all optimized weights end in 5 or 0", all(x % 5 == 0 for x in o["weights"])))
    checks.append(("all four funds used in baseline", all(x > 0 for x in b["weights"])))
    checks.append(("all four funds used in optimized", all(x > 0 for x in o["weights"])))
    # NOTE: horizon vol is NOT necessarily monotone in T. It converges toward the
    # long-run anchor, and when the last liquid future sits ABOVE that anchor the
    # 12M window can average above the 5Y window. The correct invariant is
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
                      p["optimized"]["scenarios"] + p["baseline"]["scenarios"])
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
    _odds = MACRO["fed_hike_odds_oct"]
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
                 MACRO["brent_closure"], MACRO["brent_session_high"]]
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
                   abs(_q["vol_beta"] / 1.22 - JEPQ_VOL / NDX_VOL) < 1e-9))
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
    _flow_loss = 1 - MACRO["hormuz_flow_now"] / MACRO["hormuz_flow_prewar"]
    checks.append(("Hormuz is quoted on oil volume, not vessel count alone",
                   "mb/d" in _geo_note and str(MACRO["hormuz_flow_now"]) in _geo_note))
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
    _vessel_loss = 1 - MACRO["hormuz_transits"] / MACRO["hormuz_baseline"]
    checks.append(("both the vessel-count and volume measures are published",
                   0.2 < _flow_loss < 0.5 and _vessel_loss > 0.8))
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
    checks.append(("every pending catalyst is dated after the as-of date",
                   all(_dt.date.fromisoformat(d) > _asof for d, _, _ in CATALYSTS)))
    checks.append(("catalysts are listed in date order",
                   [d for d, _, _ in CATALYSTS] == sorted(d for d, _, _ in CATALYSTS)))

    checks.append((f"the review date is not before the market as-of date "
                   f"({_revd:%A} {REVIEW_DATE} vs {_asof:%A} {AS_OF})",
                   _revd >= _asof))
    _q = _dt.date.fromisoformat(VIX_QUOTE_DATE)
    checks.append(("the VIX quote date is a trading weekday", _q.weekday() < 5))
    # The latest observed spot is a SEPARATE observation from the curve's spot and
    # must be newer, on a weekday, and not after the as-of date.
    _vl = _dt.date.fromisoformat(MACRO["vix_latest_date"])
    checks.append(("the latest VIX observation is a weekday", _vl.weekday() < 5))
    checks.append(("the latest VIX observation is newer than the curve quote",
                   _vl > _q))
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
    checks.append(("Brent's reported move reproduces from its own previous settle",
                   abs(MACRO["brent_prev"] * (1 + MACRO["brent_chg_reported"] / 100)
                       - MACRO["brent"])
                   <= MACRO["brent_prev"] * 0.5 * 10 ** -_bdp / 100 + 0.01))
    _bd = [d for d, _ in MACRO["brent_history"]]
    checks.append(("the Brent series is weekdays, in date order, no duplicates, "
                   "none after the as-of date",
                   _bd == sorted(set(_bd))
                   and all(_dt.date.fromisoformat(d).weekday() < 5 for d in _bd)
                   and _bd[-1] <= AS_OF))
    # A fixed year-ago base read against a moving settle stops being "year on
    # year" as the anniversary drifts; one week of drift is the bound.
    _anniv = _dt.date.fromisoformat(MACRO["brent_date"]).replace(year=_dt.date.fromisoformat(
        MACRO["brent_date"]).year - 1)
    checks.append(("Brent's year-ago base is within a week of the anniversary",
                   abs((_anniv - _dt.date.fromisoformat(MACRO["brent_yr_ago_date"])).days)
                   <= 7))
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
    checks.append(("the 30-year's session high is dated, not after the as-of date, and above the reading",
                   MACRO["ust_30y_high_date"] <= AS_OF
                   and MACRO["ust_30y_high"] > MACRO["ust_30y"]))
    checks.append(("the October FedWatch reading is dated, after its baseline, within 5 days",
                   MACRO["fed_hike_odds_oct_prev_date"] < MACRO["fed_hike_odds_oct_date"] <= AS_OF
                   and (_asof - _dt.date.fromisoformat(MACRO["fed_hike_odds_oct_date"])).days <= 5))
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
    checks.append(("no note passes a provisional 10-year point off as an official close",
                   not MACRO["ust_10y_provisional"]
                   or all("provisional" in t for t in _notes_all
                          if "official close" in t and _prov_txt in t)))
    # DAY FORMS a note may use for a dated input: "17th", "17 Sep", "17 September".
    def _dayforms(iso):
        _d = _dt.date.fromisoformat(iso)
        _sfx = "th" if 11 <= _d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(_d.day % 10, "th")
        return (f"{_d.day}{_sfx}", f"{_d.day} {_d:%b}", f"{_d.day} {_d:%B}")
    # FEDWATCH HAS TWO BASELINES and each delta must use its own. The first pass
    # printed "jumped from 50.9% to 73% in a day": the week's move as the day's.
    checks.append(("the FedWatch readings are dated in order, none after the as-of date",
                   MACRO["fed_hike_odds_oct_first_date"] <= MACRO["fed_hike_odds_oct_prev_date"]
                   < AS_OF and MACRO["fed_hike_odds_dec_date"] <= AS_OF))
    _oneday = [m for t in _notes_all
               for m in re.finditer(r"from (\d+(?:\.\d+)?)% to (\d+(?:\.\d+)?)% in a day", t)]
    checks.append(("every 'in a day' FedWatch move is quoted off the previous session",
                   all(abs(float(m.group(1)) - MACRO["fed_hike_odds_oct_prev"]) < 0.05
                       and abs(float(m.group(2)) - MACRO["fed_hike_odds_oct"]) < 0.05
                       for m in _oneday)))
    # A reading not re-found on the review date may be quoted, but only with its date.
    _decq = f"{MACRO['fed_hike_odds_dec']}%"
    checks.append(("the December odds are quoted only beside the date they were verified",
                   all(any(f in sent for f in _dayforms(MACRO["fed_hike_odds_dec_date"]))
                       for t in _notes_all for sent in re.split(r"(?<=[.;])\s", t)
                       if _decq in sent)))
    # THE DOT PLOT'S OWN INPUTS MUST REPRODUCE ITS MEDIAN: participants not in the
    # one- or two-more groups sit at today's midpoint, and each group is a whole
    # number of 25bp steps above it.
    _fmid = (MACRO["fed_funds_lower"] + MACRO["fed_funds_upper"]) / 2
    _dots = sorted([_fmid] * (MACRO["fed_dots_participants"] - MACRO["fed_dots_one_more"]
                              - MACRO["fed_dots_two_more"])
                   + [MACRO["fed_dot_one_more_level"]] * MACRO["fed_dots_one_more"]
                   + [MACRO["fed_dot_two_more_level"]] * MACRO["fed_dots_two_more"])
    _dmed = (_dots[len(_dots) // 2 - 1] + _dots[len(_dots) // 2]) / 2
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
    _uh_by_day = {_dt.date.fromisoformat(d).day: v for d, v in MACRO["ust_10y_history"]}
    _mon_run = (re.findall(r"(\d\.\d\d)% on the (\d+)(?:st|nd|rd|th)", _mon_note)
                + re.findall(r"(\d\.\d\d)% on (\d+) Sep", REGIONS["US"]["why"]))
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
    # The page's headline claim is that the curve prices MORE than spot. Say so only
    # while it is true.
    checks.append(("the December future is above the latest VIX close (the ramp the page cites)",
                   MACRO["vix_fut_dec"] > MACRO["vix_latest"]))
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
    # at the move's own precision alone, and on 2026-09-26 rejected a correct
    # print: "-5.24% to 14.85" off 15.67 is 14.849, which IS 14.85 - but 14.85 /
    # 15.67 recomputes to -5.23%. The bound is half a unit of the reported move on
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
                   abs(VIX3M_RESID) <= 10.0))
    checks.append(("the curve's spot is NOT silently replaced by the latest spot",
                   VOL_KNOTS[0][1] == MACRO["vix_spot"]
                   and MACRO["vix_spot"] != MACRO["vix_latest"]))
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
    _ppp_now = MACRO["ph_cpi_aug"] - MACRO["us_cpi_headline"]
    checks.append((f"FX drift sits between long-run PPP ({_ppp_lr:.1f}) and the "
                   f"current differential ({_ppp_now:.1f})",
                   _ppp_lr <= FX_DRIFT <= _ppp_now))

    # The zero-shock scenario is an identity, not an approximation: no shock and a
    # 1.0 volatility multiplier is the modelled path, so it must reproduce the
    # headline row of the portfolio it describes - CAGR, vol AND drawdown. Only
    # the drawdown ever disagreed, and nothing was checking it. (Audit 2026-09-09.)
    for lab, port, scens in (("baseline", p["baseline"]["under_macro"],
                              p["baseline"]["scenarios"]),
                             ("optimized", p["optimized"]["macro"],
                              p["optimized"]["scenarios"])):
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
    _pk = p["dd_model"]["optimized_k"]
    checks.append(("every scenario drawdown reproduces from its own printed row",
                   all(round(-max((_pk * x["vol"] - DD_MU * x["cagr"])
                                  * DD_HORIZON_SCALAR, 0.0), 1) == x["maxdd"]
                       for x in p["optimized"]["scenarios"])))
    # THE SAME QUESTION, asked of the four headline rows. It was only ever asked of
    # the scenarios, and the headline rows reached the reader's answer by luck: the
    # baseline under macro came out -29.0019 raw against -29.0080 by the reader's
    # route, 0.006pp from rounding to different tenths.  (Audit 2026-09-20.)
    _hd_rows = [(p["baseline"]["base"], p["dd_model"]["baseline_k"]),
                (p["baseline"]["under_macro"], p["dd_model"]["baseline_k"]),
                (p["optimized"]["under_base"], p["dd_model"]["optimized_k"]),
                (p["optimized"]["macro"], p["dd_model"]["optimized_k"])]
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
                       for h in ("3M", "6M", "12M", HZ_LABEL, "blend"))))
    # The four HORIZON scores are to5() of their research values. The BLEND is not,
    # and deliberately so since 2026-09-20: it is the horizon-weighted average of
    # the printed scores, because that is the arithmetic a reader does. Asserting
    # to5(blend_10) here would re-impose the route that printed 3.15 over a page
    # showing 3.14.
    checks.append(("every regional rescale 1-10 -> 1-5 is exact",
                   all(abs(v[h] - to5(v[h + "_10"])) < 1e-9
                       for v in p["regions"].values()
                       for h in ("3M", "6M", "12M", HZ_LABEL))))
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
                   HZ_LABEL in p["hz_weights"] and len(p["hz_weights"]) == 4))
    checks.append(("horizon blend weights sum to 1",
                   abs(sum(p["hz_weights"].values()) - 1.0) < 1e-9))
    # Asserted, not commented: a long mandate must not be run off near-term signal.
    checks.append(("the mandate-horizon bucket carries at least half the blend",
                   p["hz_weights"][HZ_LABEL] >= 0.50 - 1e-9))
    checks.append(("no single sub-year bucket outweighs the mandate horizon",
                   all(v <= p["hz_weights"][HZ_LABEL] + 1e-9
                       for k, v in p["hz_weights"].items() if k != HZ_LABEL)))
    # THE FLOOR, NOT A CAP. The single-sleeve cap was removed on 2026-09-24; the 5%
    # floor that keeps all four funds held (invariant 1) is what the enumeration
    # still enforces, and the set must be the COMPLETE grid above it - a cap left
    # behind in the loop would shrink it silently.
    _mn = p["min_sleeve"] * 100
    checks.append(("every portfolio holds all four funds at the minimum weight",
                   all(x >= _mn - 1e-9 for x in p["baseline"]["weights"]
                       + p["optimized"]["weights"])
                   and all(min(w) >= MIN_SLEEVE - 1e-9 for w, _ in ALL)))
    _units = round((1 - 4 * MIN_SLEEVE) / 0.05)
    checks.append((f"the enumeration is the complete 5% grid above the floor "
                   f"({math.comb(_units + 3, 3)} portfolios)",
                   p["optimized"]["n_total"] == math.comb(_units + 3, 3)))
    checks.append(("the stub counterfactual holds every other fund at the minimum",
                   sum(1 for x in p["stub"]["best_without"] if x == 0) == 1
                   and all(x >= _mn - 1e-9 for x in p["stub"]["best_without"] if x)))
    # Every frontier point is efficient: no enumerated portfolio has at least its
    # CAGR at no more drawdown. And the optimum is ON it, as the page says.
    _allp = [(s2["cagr"], abs(s2["maxdd"])) for _, s2 in ALL]
    checks.append(("every frontier point is efficient (no portfolio beats it on both axes)",
                   all(not any(c >= f["cagr"] + 1e-9 and d <= abs(f["dd"]) + 1e-9 for c, d in _allp)
                       for f in p["frontier"])))
    # THE REPORT'S SECTION 4 IS TYPED, so its four claims are asserted here: the
    # heading "Global Technology: the highest return, the smallest weight" and the
    # bullets "the most rate-sensitive thing you own" and "the deepest expected
    # drawdown on the sheet". Each was true when written; none was checked, and the
    # 25 Sep correction moved three of the four funds' returns underneath them.
    _gt = next(f for f in p["funds"] if f["id"] == "ATRGTEC")
    _gi = [f["id"] for f in p["funds"]].index("ATRGTEC")
    checks.append(("the Report's typed Global Technology claims still hold (highest net, "
                   "smallest weight, most rate-sensitive, deepest drawdown)",
                   all(_gt["net_macro"] >= f["net_macro"] for f in p["funds"])
                   and all(p["optimized"]["weights"][_gi] <= w for w in p["optimized"]["weights"])
                   and all(_gt["tilt_rates"] <= f["tilt_rates"] for f in p["funds"])
                   and all(_gt["dd_macro"] <= f["dd_macro"] for f in p["funds"])))
    _pn = p["pinned"]
    checks.append(("the pinned portfolio holds its fund at exactly the pin, on the grid, inside the budget",
                   _pn["weights"][PIN_FUND] == _pn["pin_pct"] and sum(_pn["weights"]) == 100
                   and all(x % 5 == 0 and x >= MIN_SLEEVE * 100 - 1e-9 for x in _pn["weights"])
                   and abs(_pn["macro"]["maxdd"]) <= DD_CAP + 1e-9))
    checks.append(("the pinned portfolio follows its stated rule (lowest drawdown within the tie band)",
                   _pn["macro"]["cagr"] >= _pn["best_cagr"] - _pn["tie_pp"] - 1e-9
                   and not any(abs(s2["maxdd"]) < abs(_pn["macro"]["maxdd"]) - 1e-9
                               and s2["cagr"] >= _pn["best_cagr"] - _pn["tie_pp"] - 1e-9
                               for w2, s2 in FEASIBLE if abs(w2[PIN_FUND] - PIN_W) < 1e-9)))
    checks.append(("the optimised portfolio is a frontier point",
                   any([float(x) for x in f["weights"]] == [float(x) for x in p["optimized"]["weights"]]
                       for f in p["frontier"])))
    # The what-if helper must BE the optimiser: on the live column it has to return
    # the published allocation, or its counterfactuals answer a different question.
    _live = optimise("net_macro")
    checks.append(("the what-if optimiser reproduces the published allocation on live inputs",
                   _live["weights"] == p["optimized"]["weights"]
                   and abs(_live["dd_cap"] - p["optimized"]["dd_cap"]) < 0.005))
    checks.append(("each what-if column differs from the live one by exactly the tilt it removes",
                   all(abs(f2["net_macro"] - f2["net_novol"] - f2["tilt_vol"]) < 0.0051
                       and abs(f2["net_macro"] - f2["net_neutral"] - f2["tilt_rates"]
                               - f2["tilt_energy"]) < 0.0051 for f2 in p["funds"])))
    # The published 50%-cap counterfactual must BE the best capped point in budget.
    _cc = p["cap_counterfactual"]
    _cbest = max((s["cagr"], [round(x * 100) for x in w]) for w, s in FEASIBLE
                 if max(w) <= _cc["max_sleeve"] + 1e-9)
    checks.append(("the published 50%-cap counterfactual is the best capped point in budget",
                   _cc["weights"] == _cbest[1] and abs(_cc["cagr"] - _cbest[0]) < 1e-9
                   and _cc["cagr"] <= p["optimized"]["macro"]["cagr"] + 1e-9))
    checks.append(("every region is scored at the mandate horizon",
                   all(HZ_LABEL in v for v in p["regions"].values())))
    checks.append(("the drawdown horizon scalar is sqrt(horizon / calibration window)",
                   abs(dm["horizon_scalar"] - math.sqrt(dm["horizon_y"] / dm["calib_y"]))
                   < 5e-5))
    checks.append(("the drawdown scalar is >1 for a horizon longer than the calibration",
                   (dm["horizon_scalar"] > 1) == (dm["horizon_y"] > dm["calib_y"])))
    checks.append(("peso terminal value compounds over the mandate horizon",
                   abs(1_000_000 * (1 + p["optimized"]["macro"]["cagr"] / 100) ** HORIZON_Y
                       - p["optimized"]["macro"]["terminal_1m"]) < 1.0))
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
    for lab, w, mm, kk in (("baseline", BASELINE_W, p["baseline"]["under_macro"],
                            p["dd_model"]["baseline_k"]),
                           ("optimized", OPT_W, p["optimized"]["macro"],
                            p["dd_model"]["optimized_k"])):
        pred = ((kk * mm["vol"] - p["dd_model"]["mu_coef"] * mm["cagr"])
                * p["dd_model"]["horizon_scalar"])
        # portfolio k is published to 3dp, so it contributes vol * 0.0005
        checks.append((f"{lab} drawdown reproduces from its published k",
                       abs(-pred - mm["maxdd"])
                       <= dd_tol(kk, p["dd_model"]["mu_coef"],
                                 k_dp=mm["vol"] * 0.0005)))
    for lab, w in (("baseline", BASELINE_W), ("optimized", OPT_W)):
        eq = [(w[i], p["funds"][i]["dd_k"]) for i in range(4)
              if not FUNDS[i]["cash_like"]]
        avg = sum(x * kx for x, kx in eq) / sum(x for x, _ in eq)
        # Bound derived from how precisely k is PUBLISHED, which changed on
        # 2026-09-14 from 3dp to 5dp. The 0.006 that stood here was set when the
        # figure printed at 3dp and was left behind by that change - against a 5dp
        # value it is roughly 1200x looser than the arithmetic warrants, so it would
        # have passed a materially wrong weighted average. A tolerance is only as
        # good as the precision it was derived from, and it must move with it.
        _k_pub = p["dd_model"][f"{lab}_k"]
        _k_dec = len(repr(float(_k_pub)).split(".")[1].rstrip("0")) if "." in repr(float(_k_pub)) else 0
        checks.append((f"{lab} portfolio k is the ex-cash weighted average of the sleeve k's",
                       abs(avg - _k_pub) <= 0.5 * 10 ** (-_k_dec) + 1e-12))
    # This check used to also assert cost > 0 - "the stub is genuinely dearer".
    # That was a contingent fact written in as an invariant, and it stopped being
    # true on 2026-09-09 when the fee corrections closed the gap: the counterfactual
    # is drawn from a DIFFERENT feasible set (no Global Tech at all), so its best
    # point can be better, equal or worse than the chosen one. The cost is an
    # arithmetic identity; its sign is a finding, not a law. (Same failure mode as
    # the "vol term structure is monotone rising" invariant, 2026-09-04.)
    checks.append(("the Global Tech stub cost is the derived difference, whatever its sign",
                   abs(p["stub"]["cost"]
                       - (p["stub"]["cagr_without"] - p["stub"]["cagr_with"])) < 0.006))
    checks.append(("the quoted tech-sleeve CAGR gap matches the two funds",
                   abs(p["tech_gap"] - (next(f["net_macro"] for f in p["funds"]
                                             if f["id"] == "ATRGTEC")
                                        - next(f["net_macro"] for f in p["funds"]
                                               if f["id"] == "ATRQIAP"))) < 0.006))
    checks.append(("every fund net CAGR is below its gross", 
                   all(f["net_base"] < f["gross_php"] for f in p["funds"])))
    checks.append(("optimized beats baseline on ret/DD",
                   o["macro"]["ret_per_dd"] > b["under_macro"]["ret_per_dd"]))
    checks.append(("optimized drawdown is smaller than baseline",
                   abs(o["macro"]["maxdd"]) < abs(b["under_macro"]["maxdd"])))
    lt = p["lookthrough"]
    checks.append(("look-through recorded for all four funds", len(lt) == 4))
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
                   all(abs(f2["tilt_vol"] - round(vc["ramp"] * vc["sens"][f2["id"]], 2)) < 1e-9
                       for f2 in p["funds"])))
    # THE DRIVERS REACH THE RETURNS. The check that was missing for three weeks
    # is not "are the tilts plausible" - constant tilts are perfectly plausible -
    # but "does a driver score MOVE them". Each tilt must reproduce from its
    # calibration anchor and the driver score as PUBLISHED in the drivers list, so
    # editing a driver without the tilts following, or reverting a tilt to a typed
    # constant, both fail here.
    _dp = {d["name"]: d["score_10"] for d in p["drivers"]}
    _rs = (_dp["Monetary policy & liquidity"] - DRIVER_NEUTRAL_10) / (TILT_CAL["monetary"] - DRIVER_NEUTRAL_10)
    _es = (_dp["Geopolitics & energy"] - DRIVER_NEUTRAL_10) / (TILT_CAL["geopolitics"] - DRIVER_NEUTRAL_10)
    checks.append(("every rates tilt is transmitted from the Monetary driver",
                   all(f2["tilt_rates"] == rnd(f2["tilt_rates_cal"] * _rs) for f2 in p["funds"])))
    checks.append(("every energy tilt is transmitted from the Geopolitics driver",
                   all(f2["tilt_energy"] == rnd(f2["tilt_energy_cal"] * _es) for f2 in p["funds"])))
    checks.append(("every fund's tilt column adds up to its published total",
                   all(rnd(f2["tilt_regional"] + f2["tilt_vol"] + f2["tilt_rates"]
                             + f2["tilt_energy"]) == f2["tilt_total"] for f2 in p["funds"])))
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
    }
    _fsrc = {f2["id"]: f2 for f2 in FUNDS}
    checks.append(("every equity gross return reproduces from its named components",
                   all(abs(_fsrc[k]["gross_usd"] - v) < 0.005 for k, (v, _) in _recipes.items())))
    checks.append(("every component of a gross return is quoted in that fund's note",
                   all(all(f"{c}%" in _fsrc[k]["gross_note"] for c in comps)
                       for k, (_, comps) in _recipes.items())))
    checks.append(("no base return credits volatility rising from spot (counted once, in the tilt)",
                   not any(re.search(r"implied vol rises|as vol rises|->\s*19", f2["gross_note"])
                           for f2 in FUNDS)))
    checks.append(("peso figures reconcile with the displayed CAGR and drawdown",
                   _ties(p["baseline"]["under_macro"]) and _ties(p["optimized"]["macro"])))
    # regression: no feasible portfolio may exceed the stated drawdown budget
    cap = p["optimized"]["dd_cap"]
    checks.append(("no chosen portfolio exceeds the drawdown budget",
                   abs(port_dd(OPT_W, "net_macro")) <= DD_CAP + 1e-9))
    # FEASIBILITY MUST MEAN THE SAME THING ON BOTH ROUTES. The constraint is tested
    # on the true drawdown, deliberately; the page prints the reader-reproducible
    # one. Nothing had been asserting that a portfolio admitted by the first is not
    # shown breaching the cap by the second. They agree today, but only because the
    # two routes happen to land the same side of every boundary - the same
    # coincidence that let the headline rows reconcile by luck.
    checks.append(("every feasible portfolio respects the cap on the PUBLISHED "
                   "drawdown too",
                   all(abs(s["maxdd"]) <= DD_CAP + 1e-9 for _, s in FEASIBLE)))
    # The published cap must BE the enforced cap. Publishing a rounded, looser
    # figure made this very check unable to bite: it read the published 26.0
    # while the optimiser enforced 25.97. (Audit 2026-09-08.)
    checks.append(("the published drawdown cap is the one actually enforced",
                   abs(cap - DD_CAP) < 5e-9))
    checks.append(("the published horizon scalar reproduces the enforced one",
                   abs(p["dd_model"]["horizon_scalar"] - DD_HORIZON_SCALAR) < 5e-9))
    checks.append(("optimum is the max-CAGR point inside the budget",
                   all(s2["cagr"] <= p["optimized"]["macro"]["cagr"] + 1e-9
                       for w2, s2 in FEASIBLE)))
    checks.append(("portfolio vol < weighted-average vol (diversification works)",
                   o["macro"]["vol"] < sum(w/100*f["vol"] for w, f in zip(o["weights"], p["funds"]))))
    for name, ok in checks:
        A(f"    [{'PASS' if ok else 'FAIL'}] {name}")
    A(f"\n    {sum(1 for _, ok in checks if ok)}/{len(checks)} checks passed")
    return "\n".join(L), all(ok for _, ok in checks)

if __name__ == "__main__":
    if "--json" in sys.argv:
        print(json.dumps(payload(), indent=1))
    else:
        txt, ok = report()
        print(txt)
        sys.exit(0 if ok else 1)
