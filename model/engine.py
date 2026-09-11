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

AS_OF = "2026-09-11"

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
    "fed_funds_lower": 3.5,
    "fed_funds_upper": 3.75,
    "fed_vote": '9-3 hold (3 dissents for a HIKE)',
    "us_cpi_headline": 3.4,
    "us_cpi_core": 2.4,        # Aug CPI, released 11 Sep (was 2.5 in July)
    "us_cpi_core_mom": 0.3,    # 0.1pp above consensus
    "us_cpi_headline_mom": 0.4,
    "us_cpi_shelter": 3.0,     # eased from 3.2
    "us_cpi_gasoline_yoy": 27.4,
    "us_pce_12m": 3.7, "us_pce_6m": 4.1,
    "ust_10y": 4.92,           # 10 Sep - a ten-year high
    "ust_10y_wk_high": 4.93,   # 10 Sep intraday
    "ust_2y": 4.377,           # highest since January 2025
    "ust_30y": 5.233,

    "fed_hike_odds_sep": 85.6,   # CME FedWatch, 11 Sep, after August CPI
    "fed_hike_odds_prev": 70.0,  # 10 Sep, after PPI
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
    "ea_hicp_2027": 2.3,
    "ea_hicp_2028": 2.0,
    "bsp_rrp": 5.0,
    "bsp_last_move_bp": 25,
    "bsp_hikes_since_apr": 3,
    "bsp_cum_bp": 75,
    "ph_cpi_aug": 6.1, "ph_cpi_ytd_avg": 5.2,
    "ph_cpi_jul": 6.2, "ph_core_jul": 4.2,
    "ph_cpi_jun": 6.4,
    "bsp_infl_2026": 6.1,
    "bsp_infl_2027": 5.4,
    # 8 Sep close (Tue), reported 9 Sep. Prior session closed 62.586 - not a record;
    # the record it broke is 62.59 from 4 Sep. Trade date checked against publication
    # date, because a wire story dated the 9th reports the 8th's close.
    "usdphp": 62.68,           # 11 Sep close - another record low
    "usdphp_records_2026": 23,
    "usdphp_prev_record": 62.625,  # 8 Sep
    "usdphp_intraday_low": 62.775, # 11 Sep
    "ph_tbill_91": 5.138,
    "ph_tbill_182": 5.517,
    "ph_tbill_364": 5.717,
    "brent": 105.82,           # 11 Sep 09:15 ET; Brent benchmark
    "brent_high": 108.0,       # 10 Sep session - highest since 19 May 2026
    "brent_prev": 96.28,       # 7 Sep - the level this model carried a week ago,
                               # published so notes can cite the move auditably
    "brent_wk": 9.3,
    "brent_mom": 13.24,
    # Year-ago base, implied by the last verified pair ($96.28 at +46.99% y/y).
    # brent_yoy is DERIVED from it below rather than typed, so the level and the
    # change can never drift apart the way the quoted figures did on 2026-09-10.
    "brent_yr_ago": 65.50,
    "hormuz_transits": 6,      # PortWatch, 6 Sep (latest published day found)
    "hormuz_baseline": 85,     # pre-crisis transits/day - the honest comparator
    "hormuz_vessels_waiting": 436,
    # The VIX spiked to 16.34 on 2 Sep on the Hormuz strikes and has since fallen
    # BACK toward the 2026 low. The calm did not break - it re-asserted itself,
    # which widens rather than closes the gap to the futures curve.
    # 5 Sep 2026 was a SATURDAY. One aggregator reported a "5 Sep close of 14.53";
    # there is no such close, and it was discarded. Friday 4 Sep is the last print.
    # THE CURVE'S t=0. This is the spot that belongs to VIX_QUOTE_DATE, and it must
    # stay paired with the futures strip below: the bootstrap integrates forward
    # variance from spot through the strip, so a spot from one date and a strip
    # from another is not a term structure, it is two half-curves glued together.
    "vix_spot": 14.32,         # 4 Sep close (Friday) - the curve's own spot
    # THE LATEST OBSERVED SPOT, which is NOT on the curve. On 10 Sep the VIX closed
    # 17.84, +8.38%, breaking a 28-session range of 14-17 after US WTI crossed $100
    # and August CPI landed. The strip has not been re-quoted since 4 Sep and every
    # source found on 11 Sep still echoes the 4 Sep levels alongside a spot of
    # ~14.9, which is proof those quotes are stale rather than confirmation they
    # are current. So the curve is NOT re-anchored on a spot it does not match;
    # this figure drives the volatility DRIVER SCORE and the page's narrative, and
    # the gap between the two is published rather than hidden.
    "vix_latest": 17.84,       # 10 Sep close (Thursday)
    "vix_latest_date": "2026-09-10",
    "vix_latest_chg_pct": 8.38,
    "vix_latest_high": 18.17,  # 10 Sep intraday
    "vix_prev_close": 16.46,   # 9 Sep close, implied by the +8.38% move
    "vix_prev": 15.20,         # 3 Sep close, after the -6.98% unwind
    "vix_spike": 16.34,        # 2 Sep close, the Hormuz spike
    "vix_2026_low": 14.18,     # 17 Aug intraday, the 2026 low
    "vix_1m_avg": 15.28,
    "vix_1m_low": 14.18,
    "vix_1m_high": 16.80,      # 1 Sep intraday
    # VIX futures strip. Effective centre = expiry + 15 days, because a VIX future
    # settles on 30-day forward implied vol; that centre is the t at which the
    # contract's level is the forward vol, and it is what the bootstrap interpolates
    # between. Four contracts are observable, so the curve no longer has to guess
    # across a five-month gap between Sep and Dec.
    # Levels only. The MATURITIES are derived below from the contract settlement
    # rule and VIX_QUOTE_DATE - see the note there for why they are no longer typed.
    "vix_futs_levels": [("Sep", 2026, 9, 16.57), ("Oct", 2026, 10, 18.41),
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
    "korea_ytd": 71.0,
    "taiwan_ytd": 49.0,
    "ltcma_us_eq": 6.7,
    "ltcma_em_eq": 7.8,
    "ltcma_6040plus": 6.9,
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

MACRO["brent_yoy"] = round((MACRO["brent"] / MACRO["brent_yr_ago"] - 1) * 100, 2)

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

CATALYSTS = [
    ("2026-09-16", "FOMC decision",
     "A 25bp hike is priced at 85.6% after August CPI, up from 70% before it and "
     "58% a week ago. The monetary driver is scored on tightening that has "
     "already happened; this would be the first US move of the cycle."),
    ("2026-09-17", "Bank of Japan decision",
     "Asian markets are now pricing BoJ tightening alongside the Fed, which is "
     "part of why the Nikkei fell 1.9% on 11 September."),
    ("2026-10-06", "Philippine September CPI",
     "The peso sleeve's real-carry argument rests on PH inflation decelerating; "
     "August was the fourth consecutive slowdown, and Brent at $106 works "
     "directly against a fifth."),
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

def horizon_vol(T, n=4000):
    """Annualised implied vol for a 0->T horizon via forward-variance integration."""
    h, acc = T / n, 0.0
    for i in range(n):
        acc += _seg_var(fwd_vol(i * h), fwd_vol((i + 1) * h), h)
    return math.sqrt(acc / T)

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
        "why": "Near horizons cut, ten-year anchor held. Payrolls are strong, but the rate path has repriced hard against duration: the 10-year closed 4.92%, a ten-year high, and the 16 Sep hike is 85.6% priced. Equities fell four straight sessions. August CPI was mixed - core improved to 2.4% y/y, but core rose 0.3% on the month and gasoline is +27.4% y/y. The anchor holds at 6.5 on two structural points: the US is a net energy EXPORTER, so this shock is a relative tailwind against every other bloc here, and NDX at 22.4x forward still sits below its 10y and 5y averages.",
    },
    "EUROPE": {
        "3M": 2.5, "6M": 3.0, "12M": 3.5, HZ_LABEL: 4.5,
        "why": "The worst policy/growth mismatch in the world. The ECB hiked to 2.50% on 10 Sep - its second and final move - into IMF growth of just 0.7%, and did it explicitly because the energy shock will hold inflation above target for an extended period. August HICP was 3.3% with energy +14.3% y/y, but inflation excluding energy was 2.2%: essentially the whole overshoot is the oil price, and Europe is the largest net energy importer in the world facing Brent +61.6% y/y. The offset is real - at 15.4x forward it is the cheapest large market here, and the hiking cycle is now over by the ECB's own guidance.",
    },
    "ASIA": {
        "3M": 5.0, "6M": 5.5, "12M": 6.5, HZ_LABEL: 7.5,
        "why": "Near horizons cut; the early-September bounce did not hold. The region sold off again on 11 Sep - Nikkei -1.9% to 64,011, KOSPI -1.8% to 6,910, Samsung -3.5%, SK Hynix -2.2% - and this time it is a rate shock as well as an energy one, with the BoJ now expected to tighten alongside the Fed. Korea, Taiwan and Japan are all large net oil importers. The ten-year anchor stays at 7.5: 10.5x forward against consensus EPS growth of ~52% and ~28% is a two-decade-wide discount, and JPM LTCMA puts EM equity at 7.8%, the highest of any equity block, on a framework that fits this mandate.",
    },
    "PHILIPPINES": {
        "3M": 5.5, "6M": 5.5, "12M": 5.5, HZ_LABEL: 5.5,
        "why": "Neutral across the curve. The nominal carry is intact and improving - BSP at 5.00% after three consecutive hikes, 364-day T-bills at 5.72%, with room for one more move - but the real carry is not. August inflation eased to 6.1%, a fourth consecutive deceleration, and Brent at $106 works directly against a fifth in a country that imports essentially all of its crude. The peso closed at another record low of 62.68. This sleeve's job is zero duration risk and high nominal carry; both are unimpaired. Its purchasing power is not.",
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
    ("Monetary policy & liquidity", 0.2, 2.5,
     "Tightening is now delivered rather than forecast. The ECB hiked 25bp to 2.50% "
     "on 10 Sep, its second and final move; CME FedWatch puts a US hike on 16 Sep at "
     "85.6%, from 58% a week ago; the 10-year closed 4.92%, a ten-year high. BSP is "
     "at 5.00% after three consecutive hikes. Not scored lower because a hike priced "
     "at 85.6% is one the market has already largely absorbed."),
    ("Inflation trajectory", 0.15, 3.0,
     "Genuinely two-sided. The core measure improved - August core CPI 2.4% y/y from "
     "2.5%, shelter 3.0% from 3.2%, food 2.7% from 3.0%. Energy is eating that "
     "progress in real time: core rose 0.3% on the month against a 0.2% consensus, "
     "gasoline is +27.4% y/y and fuel oil +52%. Euro HICP 3.3%. PH eased to 6.1%, a "
     "fourth straight deceleration that Brent at $106 works directly against."),
    ("Growth momentum", 0.15, 4.5,
     "Cut. August payrolls were strong - +162k against a 53k consensus, unemployment "
     "4.1% - but the terms-of-trade shock is widening faster than a tight labour "
     "market offsets it. Saudi output fell ~1.9 mb/d after Houthi strikes, US "
     "equities fell four straight sessions and Asia followed. The IMF's 3.1% global "
     "forecast was written against an oil price forty dollars lower."),
    ("Corporate earnings", 0.2, 7.0,
     "Still the strongest pillar. Asia ex-Japan EPS of ~+52% (2026) and ~+28% (2027) "
     "is unrevised and the AI capex cycle keeps compounding through the semis supply "
     "chain. Trimmed because the margin assumption underneath those estimates is "
     "harder to hold at $106 oil than at $96, and the selling hit the earnings "
     "engines directly - Samsung -3.5%, SK Hynix -2.2%."),
    ("Valuation support", 0.1, 8.0,
     "The one driver the shock improves. Four down sessions in the US and a 1.9% "
     "Nikkei fall took multiples lower against estimates that did not move. NDX "
     "22.4x forward sits below both its 10y (22.9x) and 5y (24.7x) averages, Asia at "
     "10.5x is a two-decade-wide discount, Europe 15.4x. A cheaper multiple on the "
     "same earnings is better compensation for the same risk."),
    ("Volatility & risk appetite", 0.1, 3.0,
     "The calm broke. The VIX closed 17.84 on 10 Sep, +8.38%, after touching 18.17 - "
     "ending a 28-session range of 14 to 17 that had held since mid-August. The "
     "trigger was WTI through $100 and a CPI print that made the September hike "
     "near-certain. The futures curve has priced this for weeks; it is now arriving "
     "in spot."),
    ("Geopolitics & energy", 0.1, 1.0,
     "At the floor of the scale. Brent passed $108 on 10 Sep, its highest since "
     "19 May, with Brent +61.6% y/y against +47% a week ago. US Central Command "
     "confirmed five Iranian tankers destroyed; Houthi strikes on Saudi energy sites "
     "cut output ~1.9 mb/d; tanker rates are at record highs. Hormuz transits are 6 "
     "a day against a ~85 pre-crisis baseline, a ~93% shutdown, and the conflict has "
     "widened to the Bab al-Mandab. A floor score says this driver has no room left "
     "to worsen within its scale, not that catastrophe is forecast."),
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
        "vol_beta": 1.22 * 0.68, "fx_exposed": True,
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
        "as_of": "2026-08",
        "note": "A money market fund holds paper, not shares. The live PH curve "
                "is the honest look-through.",
        "rows": [["91-day T-bill", 5.138], ["182-day T-bill", 5.517],
                 ["364-day T-bill", 5.717]],
        "unit": "% yield",
        "source": "Bureau of the Treasury PH auction results",
    },
    "ATRQIAP": {
        "dp": 1,
        "kind": "stocks",
        "as_of": "2026-06-30",
        "note": "Top 10 equity positions of the JPMorgan Nasdaq Equity Premium "
                "Income strategy. Figures are from the US-listed JEPQ factsheet; "
                "ATRAM's feeder holds the UCITS sister fund (IE000U9J8HX9), which "
                "runs the same strategy on the same universe.",
        "rows": [["NVIDIA", 6.7], ["Apple", 5.8], ["Micron Technology", 5.6],
                 ["Alphabet Class C", 5.0], ["Microsoft", 3.9],
                 ["Advanced Micro Devices", 3.9], ["Amazon", 3.7],
                 ["Lam Research", 2.9], ["Tesla", 2.4], ["Meta Platforms", 2.4]],
        "unit": "% of fund",
        "sectors": [["Information Technology", 50.9],
                    ["Communication Services", 10.2],
                    ["Consumer Discretionary", 9.2]],
        "source": "J.P. Morgan Asset Management JEPQ factsheet, 30 June 2026",
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
        "as_of": "2026",
        "note": "Fidelity publishes this fund's sector composition but not a "
                "current top-10 list at a source reachable from here. Sector "
                "weights use the Industry Classification Benchmark and sum to "
                "100.2% on the manager's own rounding.",
        "rows": [["Technology", 65.30], ["Consumer Discretionary", 11.73],
                 ["Industrials", 10.74], ["Telecommunications", 7.33],
                 ["Real Estate", 2.73], ["Energy", 1.43], ["Managed funds", 0.94]],
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
                if any(x != 0 and x < 5 for x in w):
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
     f"models the tail from here: full Strait closure and Brent to $130+ from "
     f"${MACRO['brent']:.0f}. Global CPI re-accelerates, Fed forced to hike, multiples "
     "compress hardest at the long end.",
     {"ATRPHMM": +0.5, "ATRQIAP": -4.5, "ATRASEQ": -6.5, "ATRGTEC": -7.5}, 1.60),
    ("Hawkish repricing", "The three July dissenters win. NOTE this row is a TAIL, not "
     "the base case, and what makes it a tail has changed since 9 September. September "
     f"is no longer the question: a 25bp hike is priced at {MACRO['fed_hike_odds_sep']:.1f}% "
     "for 16 Sep, so the move is effectively in the market and largely in the price. "
     "This row models what is NOT priced - a SECOND hike returning to the 2026 strip "
     "behind it, after the December move had already slipped to January 2027. "
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
        d = -max((port_k(w) * v - DD_MU * r) * DD_HORIZON_SCALAR, 0.0)
        rows.append({"name": name, "desc": desc, "cagr": round(r, 2),
                     "vol": round(v, 2), "maxdd": round(d, 1)})
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
    ("CNBC", "VIX hits its 2026 low of 14.18 on 17 August - the complacency baseline this model measures the ramp against",
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
    ("BusinessWorld", "Philippine peso falls to a new all-time low of P62.565 per dollar, 2 September 2026 - a fourth consecutive record low. The peso has since printed a FIFTH record of P62.59 on 4 September, which is the figure this model uses",
     "https://bworldonline.com/editors-picks/2026/09/03/774273/philippine-peso-falls-to-new-all-time-low-p62-565-vs-dollar/"),
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
                        "ramp": round(VOL_RAMP, 2), "sens": VOL_SENS},
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
        "fx": {"drift": FX_DRIFT, "vol": FX_VOL, "corr": FX_CORR,
               "ppp_lr": round(FX_PPP_PH_LR - FX_PPP_US_LR, 2),
               "ppp_now": round(MACRO["ph_cpi_aug"] - MACRO["us_cpi_headline"], 2)},
        "vix_quote_date": VIX_QUOTE_DATE,
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
        "dd_model": {"k": DD_K, "mu_coef": DD_MU,
                     "horizon_y": HORIZON_Y, "calib_y": DD_CALIB_Y,
                     # 4dp left a 2.5e-04 error in every drawdown - enough to
                     # flip portfolios sitting on the budget boundary.
                     "horizon_scalar": round(DD_HORIZON_SCALAR, 9),
                     "baseline_k": round(port_k(BASELINE_W), 3),
                     "optimized_k": round(port_k(OPT_W), 3),
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
    _odds = MACRO["fed_hike_odds_sep"]
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
    _all_prose = " ".join(
        [d[3] for d in DRIVERS] + [r["why"] for r in REGIONS.values()]
        + [f["gross_note"] for f in FUNDS] + [f["fee_note"] for f in FUNDS])
    # A quoted Brent figure must match SOME published Brent input, not only spot:
    # the notes legitimately cite the dated session high ($108 on 10 Sep) beside
    # the current level ($105.82). Requiring every quote to equal spot would have
    # forced the true statement out of the prose to satisfy the check - the same
    # scoping mistake the scenario counterfactual exposed on 2026-09-10.
    _brent_ok = [MACRO["brent"], MACRO["brent_high"], MACRO["brent_prev"]]
    _quoted = [
        (r"Brent[^.]{0,20}?\$(\d+(?:\.\d+)?)", _brent_ok, 1.0, "Brent level"),
        (r"Brent \+(\d+(?:\.\d+)?)%", [MACRO["brent_yoy"]], 1.0, "Brent y/y"),
    ]
    for pat, wants, tol, lab in _quoted:
        found = [float(x) for x in re.findall(pat, _all_prose)]
        checks.append((f"every {lab} quoted in prose matches a published input",
                       bool(found) and all(any(abs(v - w) <= tol for w in wants)
                                           for v in found)))

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

    _q = _dt.date.fromisoformat(VIX_QUOTE_DATE)
    checks.append(("the VIX quote date is a trading weekday", _q.weekday() < 5))
    # The latest observed spot is a SEPARATE observation from the curve's spot and
    # must be newer, on a weekday, and not after the as-of date.
    _vl = _dt.date.fromisoformat(MACRO["vix_latest_date"])
    checks.append(("the latest VIX observation is a weekday", _vl.weekday() < 5))
    checks.append(("the latest VIX observation is newer than the curve quote",
                   _vl > _q))
    checks.append(("the latest VIX observation is not after the as-of date",
                   _vl <= _dt.date.fromisoformat(AS_OF)))
    checks.append(("the latest VIX move reproduces from its own prior close",
                   abs(MACRO["vix_prev_close"] * (1 + MACRO["vix_latest_chg_pct"] / 100)
                       - MACRO["vix_latest"]) < 0.02))
    checks.append(("the curve's spot is NOT silently replaced by the latest spot",
                   VOL_KNOTS[0][1] == MACRO["vix_spot"]
                   and MACRO["vix_spot"] != MACRO["vix_latest"]))
    checks.append(("the VIX quote date is not after the model as-of date",
                   _q <= _dt.date.fromisoformat(AS_OF)))
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
    checks.append(("scenario drawdowns are on the same horizon scaling as the page",
                   all(abs(x["maxdd"]
                               + max((port_k(OPT_W) * x["vol"] - DD_MU * x["cagr"])
                                     * DD_HORIZON_SCALAR, 0.0)) < 0.06
                       for x in p["optimized"]["scenarios"])))
    checks.append(("every driver score is reported in 1-5",
                   all(1 <= d["score"] <= 5 for d in p["drivers"])))
    checks.append(("every driver rescale 1-10 -> 1-5 is exact",
                   all(abs(d["score"] - to5(d["score_10"])) < 1e-9 for d in p["drivers"])))
    checks.append(("the weighted composite of the reported driver scores is the gauge",
                   abs(sum(d["weight"] * d["score"] for d in p["drivers"]) - p["gauge"])
                   <= 0.006))
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
        checks.append((f"{lab} portfolio k is the ex-cash weighted average of the sleeve k's",
                       abs(avg - p["dd_model"][f"{lab}_k"]) < 0.006))
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
