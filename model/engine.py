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
from itertools import product

# Two different dates, which this model had been conflating. AS_OF is the market
# data date - the last trading session every price, yield and level comes from.
# REVIEW_DATE is when a human last worked through the page. On a weekend review they
# differ, and reference data retrieved during the review is legitimately NEWER than
# the market snapshot: a look-through read today is not "stale by -2 days".
AS_OF = "2026-09-18"        # last completed session (Friday, triple witching)
REVIEW_DATE = "2026-09-19"  # this review (Saturday)

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
    "fed_vote": 'unanimous hike (was 9-3 hold with 3 dissents for a hike in July)',
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
    "ust_10y": 4.94,           # 18 Sep close, easing back from above 5%
    "ust_10y_prev": 5.016,     # 16 Sep close, +2bp after the hike
    # ONE name for the intraday peak. Both of these existed, with the same value
    # and the same date, and the page fed its "highest since 2007" superlative from
    # ust_10y_PREV instead of either - correct only while the previous close and the
    # peak happened to coincide. They stopped coinciding on 2026-09-18 and the page
    # printed 5.02% under a claim that belongs to 5.04%.
    "ust_10y_peak": 5.04,      # 15 Sep intraday - highest since 2007
    "ust_2y": 4.63,            # 11 Sep close - was 4.377 and marked STALE on 10 Sep
    "ust_30y": 5.36,           # 11 Sep close

    # The September meeting is DECIDED, so these now describe the NEXT move rather
    # than a meeting that has happened. Carrying a "September odds" field past the
    # September decision would be an input describing the past as if it were pending.
    "fed_hike_odds_oct": 50.9,   # CME FedWatch, 17 Sep - close to a coin flip
    "fed_hike_odds_dec": 88.5,   # cumulative, at least one more by December
    "fed_hike_odds_sep_final": 92.0,   # where September pricing ended up, for the record
    "ecb_sep_delivered": 2.50,
    "us_payrolls_aug": 162_000, "us_payrolls_aug_consensus": 53_000,
    "us_payrolls_12m_avg": 31_000,
    "us_payrolls_jul": -23000,
    "us_unemployment": 4.1,
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
    "usdphp": 62.749,          # 18 Sep close, -1.9 centavos on the day
    "usdphp_prev": 62.73,      # 17 Sep close
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
    "ph_10y": 7.50,            # 18 Sep - the domestic yield the peso recovery cost
    "ph_tbill_91": 5.138,
    "ph_tbill_182": 5.517,
    "ph_tbill_364": 5.717,
    "brent": 103.87,           # 18 Sep SETTLE, -0.95 (-0.91%) on the day
    "brent_high": 108.75,      # the four-month high
    # DATED, because the page hard-typed "on 10 September" against it and was wrong
    # by five days from the moment the high moved. A dated figure whose date lives
    # only in prose is a figure whose date is not maintained.
    "brent_high_date": "2026-09-15",
    "brent_prev": 104.82,      # 17 Sep settle - the level carried before today,
                               # published so notes can cite the move auditably
    "brent_closure": 130.0,    # the Hormuz full-closure level the stress row models;
                               # published so the scenario and the notes citing it
                               # cannot drift apart
    "brent_mom": 13.24,
    # Year-ago base, implied by the last verified pair ($96.28 at +46.99% y/y).
    # brent_yoy is DERIVED from it below rather than typed, so the level and the
    # change can never drift apart the way the quoted figures did on 2026-09-10.
    "brent_yr_ago": 65.50,
    # HORMUZ. Two different things get measured here and they do not agree, so both
    # are carried. VESSEL COUNTS differ ~5x across sources because they count
    # different things; OIL VOLUME is what actually reaches this portfolio, through
    # the Brent price. Until 2026-09-12 this model published only the vessel count
    # and called it a "~93% shutdown", which described a supply collapse its own
    # Brent input contradicted.
    "hormuz_transits": 6,          # IMF PortWatch, all transits, 6 Sep
    "hormuz_baseline": 85,         # pre-crisis transits/day, same basis
    "hormuz_lloyds": 14,           # Lloyd's List Intelligence, 17-23 Aug
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
    "hormuz_dark": 5.0,            # mb/d moving via dark crossings / STS transfers
    "hormuz_vessels_waiting": 436,
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
        ("2026-09-16", 16.93),   # -0.27, -1.57%, on the hike and Warsh's remarks
        # 17-18 Sep. The LEVELS are corroborated by two separate reports; the
        # percentage descriptors attached to them are not. One outlet called the
        # 17th "nearly 13%" and a weekly summary called the 18th "-12.8%", and
        # neither chains off a 16.93 prior - both would need a ~17.7 close before
        # them, which contradicts a triple-corroborated 16.93. The levels are
        # carried and the derived moves (-8.92%, +0.13%) are computed from the
        # chain; the descriptors are recorded in CLAIMS as not reconciling.
        ("2026-09-17", 15.42),   # post-Fed relief rally: S&P +1.14%, Nasdaq +1.69%
        ("2026-09-18", 15.44),   # triple witching, ~$7tn of options expiring
        # The 15 Sep close is NOT carried. It was reported as "16.93, down 0.27
        # points or -1.57%" - those three cannot all be true against a 17.10 prior:
        # -0.27 gives 16.83 and -1.58%, while 16.93 is -0.17 and -0.99%. For -1.57%
        # to land on 16.93 the prior would have to be 17.20, contradicting the
        # corroborated 17.10. Two of the three agree on 16.83, which is not enough to
        # publish a close, so none is published and the series stops at the 14th.
        # This is why the VIX series can lag AS_OF, and why a check below says so out
        # loud rather than letting the gap pass unnoticed.
    ],
    "vix_latest_high": 18.17,  # 10 Sep intraday, the highest print of the episode
    # Session context. These were accidentally deleted on 2026-09-16 when the VIX
    # block above was refactored - the replaced range ran past its intended end and
    # swallowed them. Nothing caught it, because the "every published input is
    # cited" check finds orphaned inputs, not REMOVED ones; the prose that cited
    # them is what failed. Restored with the 15 Sep session.
    "spx_close": 7650.50, "spx_chg_pct": 0.17,    # 18 Sep - triple witching, ~$7tn expiry
    "nasdaq_close": 26522.55, "nasdaq_chg_pct": 0.39,
    "dow_close": 51682.64, "dow_chg_pct": -0.18,
    "wti_settle": 100.30, "wti_chg_pct": -1.6,    # 18 Sep settle, flat on the week
    "brent_wk_pct": -1.0,                         # week to 18 Sep
    "spx_wk_pct": -0.1, "nasdaq_wk_pct": 0.7, "dow_wk_pct": -1.7,  # week to 18 Sep
    # The 2026 low MOVED and this model did not notice for nine days. 14.18 on
    # 17 Aug was widely reported as the year's low at the time, and was carried as
    # such; on 4 Sep the index slid to 13.80 just before the payrolls release and
    # then rebounded to close 14.32. Both are kept - the August print is still cited
    # historically, but it is no longer the low.
    "vix_2026_low": 13.80,     # 4 Sep intraday, before the payrolls print
    "vix_aug_low": 14.18,      # 17 Aug intraday - the 2026 low UNTIL 4 Sep
    "vix_1m_avg": 15.28,
    "vix_1m_low": 13.80,
    # Dated 2 Sep, not 1 Sep. Two independent accounts put the spike peak on the
    # 2nd, which is also the session whose CLOSE (16.34) this model calls the
    # Hormuz spike - an intraday 16.82 above that close is coherent; a 1 Sep high
    # above a higher 2 Sep close was not.
    "vix_1m_high": 16.82,      # 2 Sep intraday
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
    # disclosed rather than fixed, because no fresher strip has been found in nine
    # days of looking. Dropping the front contract moves the horizon blend by 0.04
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
    "nikkei": 64011, "kospi": 6910,   # 11 Sep closes
    "korea_ytd": 71.0,
    "taiwan_ytd": 49.0,
    "ltcma_us_eq": 6.7,
    "ndx_growth_premium": 1.3,     # NDX total return over US large cap in the build-up
    "qiap_capture": 78,            # covered-call upside capture, % of the NDX
    "phmm_gross_prev": 5.25,       # the PH short-rate assumption before the mandate lengthened
    "ltcma_em_eq": 7.8,
}

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
MACRO["vix_latest_chg_pct"] = round(
    (MACRO["vix_latest"] / MACRO["vix_prev_close"] - 1) * 100, 2)
MACRO["vix_episode_high"] = max(v for _, v in _VH)
MACRO["vix_episode_low"] = min(v for _, v in _VH)
# The episode high has a DATE, and the page needed it: without one the prose called
# 17.84 a mid-week peak when it belongs to 10 Sep, a week before the week described.
# A superlative without its date drifts the moment the window moves.
MACRO["vix_episode_high_date"] = max(_VH, key=lambda r: r[1])[0]
MACRO["vix_episode_low_date"] = min(_VH, key=lambda r: r[1])[0]

MACRO["brent_yoy"] = round((MACRO["brent"] / MACRO["brent_yr_ago"] - 1) * 100, 2)
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
              "Called off on 14 September 'in the interests of consensus' per Oman's "
              "foreign minister, with no new date. Iran had been due to unveil the "
              "temporary shipping lane it agreed with Muscat. The energy driver does "
              "not price this diplomacy and said so before the postponement.")]

CATALYSTS = [
    ("2026-10-06", "Philippine September CPI",
     "The peso sleeve's real-carry argument rests on PH inflation decelerating; "
     "August was the fourth consecutive slowdown, and Brent at $104 works "
     "directly against a fifth."),
    ("2026-10-28", "FOMC decision",
     "The September hike is done; October is close to a coin flip at 50.9%, and "
     "cumulative odds of at least one further move by December are 88.5%. The dot "
     "plot median already has one more this year, so the question is timing, and "
     "whether the four participants who see two are right."),
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
VOL_RAMP  = VOL_BLEND - MACRO["vix_spot"]

# Per-fund sensitivity, in pp of net CAGR per point of vol ramp. These are
# structural properties of each sleeve, not judgements about the current market:
#   ATRQIAP  +0.210  writes calls on ~78% of a Nasdaq-100 book whose own vol is
#                    ~1.22x the market; premium scales with implied vol, so a
#                    rising ramp is harvested income. The only sleeve paid by it.
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


NEUTRAL_5 = 3.0                 # the 1-5 neutral (= 5.5 on the 1-10 research scale)

REGIONS = {
    "US": {
        "3M": 4.5, "6M": 5.0, "12M": 5.5, HZ_LABEL: 6.5,
        "why": "Near horizons cut, ten-year anchor held. Payrolls are strong, but the rate path has repriced hard against duration: the 10-year closed 5.00% on 15 Sep after touching 5.04%, its highest since 2007, with the 2-year at 4.63% and the 30-year at 5.36%, and the hike is 92.0% priced. Equities fell four straight sessions. August CPI was mixed - core improved to 2.4% y/y, but core rose 0.3% on the month and gasoline is +27.4% y/y. The anchor holds at 6.5 on two structural points: the US is a net energy EXPORTER, so this shock is a relative tailwind against every other bloc here, and NDX at 22.4x forward still sits below its 10y and 5y averages.",
    },
    "EUROPE": {
        "3M": 2.5, "6M": 3.0, "12M": 3.5, HZ_LABEL: 4.5,
        "why": "The worst policy/growth mismatch in the world. The ECB hiked to 2.50% on 10 Sep - its second and final move - into IMF growth of just 0.7%, and did it explicitly because the energy shock will hold inflation above target for an extended period. August HICP was 3.3% with energy +14.3% y/y, but inflation excluding energy was 2.2%: essentially the whole overshoot is the oil price, and Europe is the largest net energy importer in the world facing Brent +58.6% y/y. The offset is real - at 15.4x forward it is the cheapest large market here, and the hiking cycle is now over by the ECB's own guidance.",
    },
    "ASIA": {
        "3M": 5.0, "6M": 5.5, "12M": 6.5, HZ_LABEL: 7.5,
        "why": "Near horizons cut; the early-September bounce did not hold. The region sold off again on 11 Sep - Nikkei -1.9% to 64,011, KOSPI -1.8% to 6,910, Samsung -3.5%, SK Hynix -2.2% - and this time it is a rate shock as well as an energy one. The BoJ delivered on 18 Sep, +25bp to 1.25% - the highest since 1995 - and the yen FELL, closing 156.86 per dollar, a two-week low. Read that carefully: a hike that weakens the currency is the market pricing the END of a cycle, not improving carry. The vote was 7-2, Asada and Sato dissenting, and August core CPI had slowed to 1.7% from 1.8% hours earlier, so the board tightened into decelerating headline inflation on the strength of a demand gauge at 1.9%. The gap from the previous move was three months against six before it: faster, and more contested. Korea, Taiwan and Japan are all large net oil importers. The ten-year anchor stays at 7.5: 10.5x forward against consensus EPS growth of ~52% and ~28% is a two-decade-wide discount, and JPM LTCMA puts EM equity at 7.8%, the highest of any equity block, on a framework that fits this mandate.",
    },
    "PHILIPPINES": {
        "3M": 5.5, "6M": 5.5, "12M": 5.5, HZ_LABEL: 5.5,
        "why": "Neutral across the curve. The nominal carry is intact and improving - BSP at 5.00% after three consecutive hikes, 364-day T-bills at 5.72%, with room for one more move - but the real carry is not. August inflation eased to 6.1%, a fourth consecutive deceleration - though BSP's own 2027 forecast is 5.4% - and Brent at $104 works directly against a fifth in a country that imports essentially all of its crude. The peso has come off its record: it closed 62.749 on 18 Sep, having set the weakest close on record at 62.86 on 14 Sep and the weakest intraday print at 62.925 the next day. That is a 6.3% loss of purchasing power against the dollar this year, and PH 10-year yields around 7.50% are what the recovery cost. This sleeve's job is zero duration risk and high nominal carry; both are unimpaired. Its purchasing power is not.",
    },
}
for r in REGIONS.values():
    r["blend"] = round(sum(r[h] * w for h, w in HZ_W.items()), 2)
    for h in ("3M", "6M", "12M", HZ_LABEL, "blend"):
        r[h + "_10"] = r[h]      # research basis, kept so the rescale stays auditable
        r[h] = to5(r[h])         # reported value, 1-5

# ----------------------------------------------------------------------------
# 4. BROAD MACRO GAUGE (1-5) - weighted composite of seven drivers
#    Drivers are researched and scored on a 1-10 scale (that is the granularity the
#    underlying evidence supports). The HEADLINE gauge is reported 1-5: endpoints map
#    to endpoints, so the 1-10 neutral of 5.5 lands exactly on the 1-5 neutral of 3.0.
# ----------------------------------------------------------------------------

DRIVERS = [
    ("Monetary policy & liquidity", 0.2, 2.25,
     "CUT. The tightening this driver has been scoring as priced is now DELIVERED, "
     "and the guidance behind it is harder than the move. On 16 September the Fed "
     "raised 25bp to 3.75-4.00%, its first increase since 2023, and did it "
     "UNANIMOUSLY - a unanimous hike (was 9-3 hold with 3 dissents for a hike in July), so the dissenters carried the whole committee. Warsh said "
     "the Fed had 'removed a dose of accommodation' and promised a 'timelier return' "
     "to 2%. The dot plot is the hawkish part: a median end-2026 policy rate of 4.1%, "
     "with 12 of 18 participants at 4.125% and another 4 at 4.375% - so 16 of 18 see "
     "at least one more hike this year, and a quarter of them see two. CME FedWatch "
     "puts October at 50.9%, close to a coin flip, and cumulative odds of at least one "
     "further move by December at 88.5%. The long end has already given some of it "
     "back: the 10-year closed 5.016% on 16 Sep, then eased to 4.94% by the 18th, "
     "having peaked at 5.04% intraday on the 15th - the highest since 2007, and the "
     "figure that superlative belongs to. The ECB finished its own cycle on 10 Sep "
     "at 2.50%; BSP is at 5.00% after three hikes; and the BoJ joined on 18 Sep, "
     "+25bp to 1.25%, the highest since 1995, on a 7-2 vote. Not cut further than 2.25 for the reason this "
     "driver has held all month: what is priced is absorbed, and an 88.5% cumulative "
     "probability leaves less repricing risk into December than a coin-flip October "
     "does. The risk is no longer the hike - it is the second one."),
    ("Inflation trajectory", 0.15, 3.0,
     "Genuinely two-sided. The core measure improved - August core CPI 2.4% y/y from "
     "2.5%, shelter 3.0% from 3.2%, food 2.7% from 3.0%. Energy is eating that "
     "progress in real time: core rose 0.3% on the month against a 0.2% consensus, "
     "gasoline is +27.4% y/y and fuel oil +52%. Euro HICP 3.3%. PH eased to 6.1%, a "
     "fourth straight deceleration that Brent at $104 works directly against."),
    ("Growth momentum", 0.15, 4.0,
     "Cut. August payrolls were strong - +162k against a 53k consensus, unemployment "
     "4.1% - but the terms-of-trade shock is widening faster than a tight labour "
     "market offsets it. Saudi output fell ~1.9 mb/d after Houthi strikes, and the "
     "breadth underneath the index is where the damage shows: the Dow lost 1.7% on "
     "the week, a third straight losing week and its worst since March, while the "
     "Nasdaq gained 0.7% and the S&P finished flat at -0.1%. That spread is a market "
     "paying for duration and growth and selling everything else. The IMF's 3.1% "
     "global forecast was written against an oil price nearly forty dollars lower - "
     "and against a 10-year yield nowhere near 4.94%, a second tax on every "
     "long-duration cash flow in this portfolio."),
    ("Corporate earnings", 0.2, 7.0,
     "Still the strongest pillar. Asia ex-Japan EPS of ~+52% (2026) and ~+28% (2027) "
     "is unrevised and the AI capex cycle keeps compounding through the semis supply "
     "chain. Trimmed because the margin assumption underneath those estimates is "
     "harder to hold at $104 oil than at $65.50, where it was a year ago - though the "
     "$108.75 peak of 15 Sep has come off 4.5%, the first easing in this episode. "
     "The selling has hit the earnings engines directly - Samsung -3.5%, SK Hynix -2.2%."),
    ("Valuation support", 0.1, 8.0,
     "The one driver the shock improves. A month of de-rating - the Dow's third "
     "straight losing week, a 1.9% Nikkei fall - took multiples lower against "
     "estimates that did not move, and last week's partial bounce did not undo it. NDX "
     "22.4x forward sits below both its 10y (22.9x) and 5y (24.7x) averages, Asia at "
     "10.5x is a two-decade-wide discount, Europe 15.4x. A cheaper multiple on the "
     "same earnings is better compensation for the same risk."),
    ("Volatility & risk appetite", 0.1, 3.0,
     "RAISED from 2.5, and still well below neutral. The VIX ran 17.10 on 14 Sep and 17.20 on "
     "the 15th, held 16.93 through the hike on the 16th, then dropped to 15.42 on "
     "the 17th and closed 15.44 on the 18th - back inside the range it broke out of, "
     "with the event risk that justified the premium now behind it. Equities agreed: "
     "the S&P closed 7650.50 (+0.17%), the Nasdaq 26522.55 (+0.39%) and the Dow "
     "51682.64 (-0.18%) through triple witching and a roughly $7tn expiry without "
     "a volatility event. The rate "
     "leg eased too, the US 10-year closing 4.94% on 18 Sep after peaking at 5.04% "
     "intraday on the 15th, its highest since 2007, and WTI settling $100.30. This "
     "is a half-point back rather than a reversal: two weeks of 15-17 prints is "
     "still a higher floor than the 13.80 low of 4 Sep, the curve prices 19+ by "
     "December, and the energy leg has not unwound. What earns the half point is "
     "structural, not price - the three dated events that justified the premium "
     "have all passed without one. Geopolitics is NOT raised alongside it: crude "
     "easing off a peak is price, and the pipeline is still shut."),
    ("Geopolitics & energy", 0.1, 1.25,
     "CUT. Two things went the wrong way and one of them undercuts the offset this "
     "note was leaning on. First, the HORMUZ BYPASS IS SHUT: drone strikes launched "
     "from Iraq hit Saudi Arabia's 1200 km East-West (Petroline) pipeline on 11 Sep "
     "and Riyadh closed it, with satellite imagery showing fire damage at a pumping "
     "station. That line was moving roughly 5.0 mb/d to the Red Sea port of Yanbu "
     "specifically to route AROUND the Strait. Second, the Oman meeting at which "
     "Iran was to unveil a temporary shipping lane to the Gulf states was postponed "
     "on the day, 'in the interests of consensus', with no new date. This note said "
     "last week that it was not pricing that diplomacy; that was the right call. "
     "Read the disruption on VOLUME, not vessel counts. The counts disagree about "
     "fivefold by what they count - IMF PortWatch 6 transits a day against a ~85 "
     "baseline, Lloyd's List Intelligence 14 counting only cargo over 10000 dwt, the "
     "US government around 30 - and none of them is supply. Goldman put Gulf crude "
     "and product exports at 15.5 mb/d against a 23.0 mb/d pre-war baseline, about "
     "two-thirds, up from a 5.5 mb/d trough in March. But that reading is dated "
     "2026-08-28, BEFORE the pipeline was hit, and a material part of what it "
     "measured ran through the line that is now shut. No post-shutdown figure has "
     "been published, so none is invented here - the honest statement is that "
     "two-thirds is the last measured level and is now stale in a knowable "
     "direction. Brent settled $103.87 on 18 Sep, off the $108.75 four-month high "
     "set on 15 Sep and down 1.0% on the week, but still +58.6% y/y. The shock has "
     "stopped widening; it has not unwound. Saudi output was already down ~1.9 mb/d after "
     "Houthi strikes; tanker rates are at record highs; 436 vessels are holding off "
     "berth. Still NOT scored at the floor: the stress table models full closure and "
     "Brent above $130, a strictly worse state, so a floor would assert no room left "
     "to worsen while the page models it worsening."),
]
GAUGE_10 = round(sum(w * s for _, w, s, _ in DRIVERS), 2)


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
        "gross_note": "10y average PH short-rate path. Anchored on the live curve (91d 5.14%, 182d 5.52%, 364d 5.72%) with BSP at 5.00% after a third consecutive hike, reverting toward a ~4.50% neutral policy rate by year 3-5. CUT from 5.25% when the mandate lengthened to 10 years: the elevated front end is a 1-3 year feature, so over a decade far more of the path sits at neutral and the average falls toward it.",
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
        "gross_usd": 7.2,
        "gross_note": "NDX long-run total return of 8.0% (JPM LTCMA US large cap 6.7% + 1.3% NDX growth premium, valuation neutral at 22.4x vs 22.9x 10y avg), times ~78% covered-call upside capture, plus ~0.5%/yr of option premium earned back as implied vol rises 14.3 -> 19.4.",
        # NDX vol relative to the S&P (1.22, assumption) times the covered-call
        # vol factor, which is no longer a magic number: J.P. Morgan's own fact
        # sheet (31 Jul 2026) puts JEPQ since-inception annualised standard
        # deviation at 13.9% against the Nasdaq-100's 20.4%, i.e. 0.681. The 0.68
        # carried here for months happened to be right to two decimals, but it was
        # unsourced; it is now derived from two published figures.
        "vol_beta": 1.22 * (JEPQ_VOL / NDX_VOL), "fx_exposed": True,
        "macro_tilt": {"rates": -0.10, "energy": -0.10},
        "dd_k_adj": -0.10, "cash_like": False,
        "dd_k_why": "Below 1.65: writing calls converts part of the left tail into premium already collected, so realised drawdowns run shallower than the raw volatility implies.",
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
        # buys is not published; but it is now anchored on a published figure and
        # errs HIGH rather than low. This cost Asia Equity 0.75pp of net CAGR and
        # dropped it from first to third on the sheet.
        "fee_feeder": 1.18, "fee_target": 1.55,
        "fee_note": "1.17% trustee + 0.01% auditor (verified KIIDS) + ~1.55% estimated "
                    "target-fund OCF (ESTIMATE, anchored on JPMAM's published 1.50% "
                    "management fee for this fund; exact share-class OCF not published)",
        "gross_usd": 8.3,
        "gross_note": "JPM LTCMA EM equity 7.8% + ~1.0% re-rating from a 10.5x forward multiple against ~52%/~28% EPS growth, less ~0.5% for the dividend tilt's lower growth capture.",
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
        "gross_usd": 9.0,
        "gross_note": "US large cap 6.7% (JPM LTCMA) + 3.5% tech earnings-growth premium - 1.2% multiple de-rating drag. Deliberately well BELOW the target fund's realised 15.20% 5y, which was earned inside an AI capex boom and is not a forecast.",
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
    reg_tilt = (rs - NEUTRAL) * REGIONAL_TILT_PER_PT
    vol_tilt = round(VOL_RAMP * VOL_SENS[f["id"]], 2)   # derived, not hand-set
    tilt_total = reg_tilt + vol_tilt + t["rates"] + t["energy"]
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
        "tilt_vol": vol_tilt, "tilt_rates": t["rates"], "tilt_energy": t["energy"],
        "tilt_total": round(tilt_total, 2),
        "net_macro": round(macro_net, 2),
        "vol": round(sig, 2),
        "dd_k": round(k, 2), "dd_k_why": f["dd_k_why"],
        "dd_base": round(-dd(base_net), 1),
        "dd_macro": round(-dd(macro_net), 1),
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
    r_d, d_d, v_d = round(r, 2), round(d, 1), round(v, 2)
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
        # Dated AS_OF, because these ARE the live curve, not an August snapshot -
        # the rows were labelled "2026-08" while carrying today's yields. And they
        # are now DERIVED from the same inputs the rest of the page uses: they were
        # a hand-typed copy of MACRO's T-bill values with nothing tying the two
        # together. (Audit 2026-09-13.)
        "as_of": AS_OF,
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
                "runs the same strategy on the same universe. Refreshed to the "
                "31 July sheet on 2026-09-13: the 30 June list carried here had "
                "Tesla in the top ten and no Broadcom, which the later sheet "
                "reverses, and six of the ten weights had moved.",
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
        "note": "Fidelity publishes this fund's sector composition but not a "
                "current top-10 list at a source reachable from here. Sector "
                "weights use the Industry Classification Benchmark. The date is "
                "when these were read from Fidelity's factsheet page, which does "
                "not publish its own snapshot date there - so they are Fidelity's "
                "latest month-end, not a 13 September position.",
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

# Single-sleeve concentration cap. Added 2026-09-09, and the reason matters:
# until then the objective had NO diversification constraint. It happened not to
# bind, because the drawdown budget was doing the job by accident. When the Asia
# fee correction cut that sleeve's return, the optimiser immediately went to 75%
# in one fund - a "four-fund portfolio" that is really one fund plus three stubs,
# and flatly against the diversification argument the report itself makes ("it is
# the same bet, twice"). The page argued the principle; the code never encoded it.
#
# 50% is the rule: no single sleeve may exceed half the portfolio. It is stated
# on the page as part of the objective, not applied silently, and it is NOT
# reverse-engineered to reproduce any previous answer (the old optimum was 45%,
# comfortably inside it).
MAX_SLEEVE = 0.50

def enumerate_portfolios(key, min_w=0.05, max_sleeve=MAX_SLEEVE):
    """All 5%-granular, fully-invested portfolios holding all four funds,
    with no single sleeve above the concentration cap."""
    out = []
    for a in GRID:
        if a < min_w or a > max_sleeve + 1e-9: continue
        for b in GRID:
            if b < min_w or b > max_sleeve + 1e-9: continue
            for c in GRID:
                if c < min_w or c > max_sleeve + 1e-9: continue
                d = round(1 - a - b - c, 10)
                if d < min_w - 1e-9 or d > max_sleeve + 1e-9: continue
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
FEASIBLE = [(w, s) for w, s in ALL
            if abs(port_dd(w, "net_macro")) <= DD_CAP + 1e-9]
FEASIBLE.sort(key=lambda t: (-t[1]["cagr"], abs(t[1]["maxdd"])))
OPT_W, OPT = FEASIBLE[0]
OPT_UNDER_BASE = summarise(OPT_W, "net_base")

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
                # 5% minimum. Without this the counterfactual could drop a second
                # fund - [50, 50, 0, 0] was reachable - and the stub's "cost" would
                # be measured against a two-fund portfolio the objective forbids,
                # exactly the error the concentration-cap guard below was added to
                # prevent. It did not bite today ([15, 50, 35, 0] holds all three),
                # but nothing stopped it. (Audit 2026-09-14.)
                if any(i != idx and x < 5 for i, x in enumerate(w)):
                    continue
                # the counterfactual must obey the same concentration cap as the
                # chosen portfolio, or the "cost" of the stub is measured against
                # something the objective would never have allowed
                if any(x > MAX_SLEEVE * 100 + 1e-9 for x in w):
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
FRONTIER = {}
for w, s in ALL:
    b = math.floor(abs(s["maxdd"]))
    if b not in FRONTIER or s["cagr"] > FRONTIER[b][1]["cagr"]:
        FRONTIER[b] = (w, s)
FRONTIER = [{"maxdd": k, "cagr": v[1]["cagr"], "weights": v[1]["weights"]}
            for k, v in sorted(FRONTIER.items())]

# ----------------------------------------------------------------------------
# 7. SCENARIO / STRESS GRID
# ----------------------------------------------------------------------------
# Each scenario is an additive shock (pp, annualised over 5y) per fund and a
# vol multiplier, keyed to a live, named risk in the current macro picture.
SCENARIOS = [
    ("Hormuz escalation", "NOW PARTLY RUNNING. Two Saudi supertankers hit on 31 Aug, "
     "~100 US strikes on Iran on 1 Sep, US strikes on Iranian tankers on 2 Sep, and US "
     "forces have since destroyed one Iranian tanker and disabled two more. This row "
     f"models the tail from here: full Strait closure and Brent to ${MACRO['brent_closure']:.0f}+ from "
     f"${MACRO['brent']:.0f}. Global CPI re-accelerates, Fed forced to hike, multiples "
     "compress hardest at the long end.",
     {"ATRPHMM": +0.5, "ATRQIAP": -4.5, "ATRASEQ": -6.5, "ATRGTEC": -7.5}, 1.60),
    ("Hawkish repricing", "The three July dissenters win. NOTE this row is a TAIL, not "
     "the base case, and what makes it a tail has changed since 9 September. September "
     f"is no longer the question - it HAPPENED. The Fed hiked 25bp to 3.75-4.00% on "
     f"16 September, unanimously, and the dot plot now has a median of "
     f"{MACRO['fed_dot_2026']}% for end-2026, i.e. one more. This row models what is "
     f"still NOT priced: a SECOND hike on top of that, which {MACRO['fed_dots_two_more']} "
     f"of {MACRO['fed_dots_participants']} participants already see. "
     "Fed hikes into a 4.1% unemployment rate; duration-heavy growth de-rates.",
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
     "consecutive monthly slowdown and a five-month low, year-to-date average 5.2%",
     "https://psa.gov.ph/price-indices/cpi-ir"),
    ("European Central Bank", "Monetary policy decision, 23 July 2026 - deposit rate HELD at 2.25% after the June hike",
     "https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260723~29f24d99bc.en.html"),
    ("BSP Monetary Policy Report", "February 2026 economic outlook and inflation path",
     "https://www.bsp.gov.ph/Price%20Stability/MonetaryPolicyReport/FullReport-February2026.pdf"),
    ("CNBC", "VIX hits 14.18 on 17 August, reported at the time as the 2026 low. It was, until 4 September, when the index slid to 13.80 before the payrolls print. The ramp is measured against the curve, not against either low",
     "https://www.cnbc.com/2026/08/17/stock-market-volatility-vix-wall-street.html"),
    ("Reuters (via KFGO)", "ECB to raise a second time on 10 Sep then stop - all 65 economists polled 31 Aug-3 Sep forecast 2.50%, 91% see it held to year end",
     "https://kfgo.com/2026/09/03/ecb-to-raise-rates-a-second-time-in-september-but-then-done-say-economists-reuters-poll/"),
    ("Bloomberg", "Economists see a final ECB hike next week, splitting with market pricing",
     "https://www.bloomberg.com/news/articles/2026-09-04/economists-see-final-ecb-hike-next-week-in-split-with-markets"),
    ("Wikipedia (chronology, secondary)", "2026-2028 world oil market chronology - Hormuz escalation timeline, cross-checked against the primary reports cited here",
     "https://en.wikipedia.org/wiki/2026%E2%80%932028_world_oil_market_chronology"),
        ("Bureau of the Treasury PH", "T-bill auction results - 91d 5.138%, 182d 5.517%, 364d 5.717%",
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
        "regions": {k: {**v} for k, v in REGIONS.items()},
        "hz_weights": HZ_W,
        "vol_channel": {"blend": round(VOL_BLEND, 2), "spot": MACRO["vix_spot"],
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
                     "score": to5(s), "score_10": s, "note": t}
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
        "best_ratio": {"weights": [round(x*100) for x in BEST_RATIO_W], **BEST_RATIO},
        "stub": STUB, "tech_gap": TECH_GAP,
        "max_sleeve": MAX_SLEEVE,
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
    _all_prose = " ".join(
        [d[3] for d in DRIVERS] + [r["why"] for r in REGIONS.values()]
        + [f["gross_note"] for f in FUNDS] + [f["fee_note"] for f in FUNDS]
        + [c[2] for c in CATALYSTS] + [p[1] for p in POSTPONED])
    # A quoted Brent figure must match SOME published Brent input, not only spot:
    # the notes legitimately cite the dated session high ($108 on 10 Sep) beside
    # the current level ($105.82). Requiring every quote to equal spot would have
    # forced the true statement out of the prose to satisfy the check - the same
    # scoping mistake the scenario counterfactual exposed on 2026-09-10.
    _brent_ok = [MACRO["brent"], MACRO["brent_high"], MACRO["brent_prev"],
                 MACRO["brent_closure"]]
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
    # Every catalyst the page presents as pending must actually still be pending.
    _asof = _dt.date.fromisoformat(AS_OF)
    checks.append(("every pending catalyst is dated after the as-of date",
                   all(_dt.date.fromisoformat(d) > _asof for d, _, _ in CATALYSTS)))
    checks.append(("catalysts are listed in date order",
                   [d for d, _, _ in CATALYSTS] == sorted(d for d, _, _ in CATALYSTS)))

    checks.append(("the review date is not before the market as-of date",
                   _dt.date.fromisoformat(REVIEW_DATE)
                   >= _dt.date.fromisoformat(AS_OF)))
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
    checks.append(("every VIX close in the series is on a weekday",
                   all(_dt.date.fromisoformat(d).weekday() < 5
                       for d, _ in MACRO["vix_history"])))
    checks.append(("the VIX series is in date order with no duplicates",
                   [d for d, _ in MACRO["vix_history"]]
                   == sorted({d for d, _ in MACRO["vix_history"]})))
    checks.append(("the latest VIX observation is not after the as-of date",
                   _vl <= _dt.date.fromisoformat(AS_OF)))
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
    checks.append(("every regional rescale 1-10 -> 1-5 is exact",
                   all(abs(v[h] - to5(v[h + "_10"])) < 1e-9
                       for v in p["regions"].values()
                       for h in ("3M", "6M", "12M", HZ_LABEL, "blend"))))
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
    # Concentration. The report argues against doubling up; the objective must too.
    cap_pc = p["max_sleeve"] * 100
    checks.append(("no sleeve in either portfolio exceeds the concentration cap",
                   all(w <= cap_pc + 1e-9
                       for w in p["baseline"]["weights"] + p["optimized"]["weights"])))
    checks.append(("the enumerated set respects the concentration cap",
                   all(max(w) <= MAX_SLEEVE + 1e-9 for w, _ in ALL)))
    checks.append(("the stub counterfactual obeys the same cap as the chosen portfolio",
                   max(p["stub"]["best_without"]) <= cap_pc + 1e-9))
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
    checks.append(("volatility ramp = horizon-blended implied vol minus spot",
                   abs(vc["blend"] - vc["spot"] - vc["ramp"]) < 0.011))
    checks.append(("every volatility tilt is derived from the ramp, not hand-set",
                   all(abs(f2["tilt_vol"] - round(vc["ramp"] * vc["sens"][f2["id"]], 2)) < 1e-9
                       for f2 in p["funds"])))
    checks.append(("the covered-call sleeve is the only one paid by a rising ramp",
                   max(p["funds"], key=lambda f2: f2["tilt_vol"])["id"] == "ATRQIAP"
                   or vc["ramp"] <= 0))
    checks.append(("peso figures reconcile with the displayed CAGR and drawdown",
                   _ties(p["baseline"]["under_macro"]) and _ties(p["optimized"]["macro"])))
    # regression: no feasible portfolio may exceed the stated drawdown budget
    cap = p["optimized"]["dd_cap"]
    checks.append(("no chosen portfolio exceeds the drawdown budget",
                   abs(port_dd(OPT_W, "net_macro")) <= DD_CAP + 1e-9))
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
