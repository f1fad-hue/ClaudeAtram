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
import json, math, sys
from itertools import product

AS_OF = "2026-09-02"

# ----------------------------------------------------------------------------
# 1. VERIFIED INPUTS  (source-cited; see SOURCES dict at bottom)
# ----------------------------------------------------------------------------

MACRO = {
    "fed_funds_lower": 3.5,
    "fed_funds_upper": 3.75,
    "fed_vote": '9-3 hold (3 dissents for a HIKE)',
    "us_cpi_headline": 3.4,
    "us_cpi_core": 2.5,
    "us_payrolls_jul": -23000,
    "us_unemployment": 4.1,
    "ecb_depo": 2.25,
    "ecb_last_move_bp": 25,
    "ea_hicp_2026": 3.0,
    "ea_hicp_2027": 2.3,
    "ea_hicp_2028": 2.0,
    "bsp_rrp": 5.0,
    "bsp_last_move_bp": 25,
    "bsp_hikes_since_apr": 3,
    "bsp_cum_bp": 75,
    "ph_cpi_jul": 6.2,
    "ph_cpi_jun": 6.4,
    "bsp_infl_2026": 6.1,
    "bsp_infl_2027": 5.4,
    "usdphp": 62.565,
    "ph_tbill_91": 5.138,
    "ph_tbill_182": 5.517,
    "ph_tbill_364": 5.717,
    "brent": 94.86,
    "brent_mom": 13.24,
    "brent_yoy": 40.33,
    "vix_spot": 16.44,
    "vix_1m_avg": 15.28,
    "vix_1m_low": 14.13,
    "vix_1m_high": 18.43,
    "vix_fut_sep": 17.92,
    "vix_fut_dec": 20.38,
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

def fwd_vol(t):
    """Forward 30-day implied vol (annualised, %) at time t years from now."""
    v0, vs, vd = MACRO["vix_spot"], MACRO["vix_fut_sep"], MACRO["vix_fut_dec"]
    vinf = MACRO["vix_longrun"]
    T_S, T_D = 0.080, 0.330          # effective centres of the Sep / Dec futures
    if t <= 0:                 return v0
    if t <= T_S:               return v0 + (vs - v0) * (t / T_S)
    if t <= T_D:               return vs + (vd - vs) * (t - T_S) / (T_D - T_S)
    return vinf + (vd - vinf) * math.exp(-KAPPA * (t - T_D))

def horizon_vol(T, n=4000):
    """Annualised implied vol for a 0->T horizon via forward-variance integration."""
    h, acc = T / n, 0.0
    for i in range(n):
        acc += _seg_var(fwd_vol(i * h), fwd_vol((i + 1) * h), h)
    return math.sqrt(acc / T)

HORIZONS = [("3M", 0.25), ("6M", 0.50), ("12M", 1.00), ("5Y", 5.00)]
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
SP_VOL_5Y = next(v["implied"] for v in VOL_TS if v["label"] == "5Y")

# ----------------------------------------------------------------------------
# 3. REGIONAL MACRO-DRIVER SCORES  (1-10, 5.5 = neutral)
#    Each score is an evidence-weighted judgement over the seven drivers in
#    DRIVERS below; the horizon blend weights near-term signals but keeps the
#    5-year anchor dominant because the investment horizon is 5 years.
# ----------------------------------------------------------------------------

HZ_W = {"3M": 0.15, "6M": 0.25, "12M": 0.30, "5Y": 0.30}

REGIONS = {
    "US": {
        "3M": 5.0, "6M": 5.5, "12M": 6.0, "5Y": 6.5,
        "why": "Cut across the near horizons on the September bond rout: the 10-year yield is at a near-3-year high and the market now prices TWO hikes (Sep-16 and Dec), not a hold. Payrolls -23k, unemployment 4.1%. Core CPI 2.5% still contained - the one clean anchor - but headline 3.4% faces Brent +40% y/y. NDX 22.4x fwd stays BELOW its 10y (22.9x) and 5y (24.7x) averages, and the US is a net energy exporter, so the 5-year anchor holds at 6.5 while duration-sensitive growth de-rates near term.",
    },
    "EUROPE": {
        "3M": 3.0, "6M": 3.5, "12M": 4.0, "5Y": 4.5,
        "why": "Still the worst policy/growth mismatch in the world, and it got worse. The ECB hiked +25bp to 2.25% in June - first in 3 years - held on 23 July, and a further hike to 2.50% on 10 September is now close to fully priced, all into IMF growth of just 0.7% for 2026 (from 1.1%). Europe is the largest net energy importer in the world facing Brent +40% y/y, up from +32% a week ago. Offset: cheapest large market at 15.4x fwd, +9.5% YTD.",
    },
    "ASIA": {
        "3M": 5.5, "6M": 6.5, "12M": 7.0, "5Y": 7.5,
        "why": "Still the best fundamentals available, but the near horizons take the energy shock hardest: Korea, Taiwan and Japan are all large net oil importers, and on 2 Sep the KOSPI fell ~4%, the Nikkei 2.9% and MSCI Asia-Pac ex-Japan 2%. That is a macro de-rating, not an earnings event - 10.5x fwd against consensus EPS growth of ~52% (2026) and ~28% (2027) off the AI/memory/semis cycle is intact and now cheaper. The 5-year anchor stays at 7.5; JPM LTCMA still puts EM equity at 7.8%, the highest of any equity block.",
    },
    "PHILIPPINES": {
        "3M": 5.5, "6M": 5.5, "12M": 5.5, "5Y": 5.5,
        "why": "MARKED DOWN from 6.05 - the previous score rested on an error. Peso cash was scored as positive real carry against '~4% inflation'; PH inflation actually printed 6.2% in July, and BSP's own 2027 forecast was RAISED to 5.4% (from 4.5%) on El Nino and wage pressure. T-bills at 5.14% (91d) to 5.72% (364d) are therefore roughly 1pp NEGATIVE in real terms, not positive. BSP hiked to 5.00% on 27 August - a third consecutive move, 75bp cumulative - and the peso still hit a record 62.565, its fourth record low running. High nominal carry and zero duration risk are real and still worth holding; the purchasing-power gain is not. Neutral, 5.5.",
    },
}
for r in REGIONS.values():
    r["blend"] = round(sum(r[h] * w for h, w in HZ_W.items()), 2)

# ----------------------------------------------------------------------------
# 4. BROAD MACRO GAUGE (1-10) - weighted composite of seven drivers
# ----------------------------------------------------------------------------

DRIVERS = [
    ("Monetary policy & liquidity", 0.2, 3.5,
     "Tightening is no longer a bias, it is happening. BSP hiked to 5.00% on 27 Aug (third consecutive, +75bp cumulative), an ECB hike to 2.50% on 10 Sep is close to fully priced, and the market now prices TWO Fed hikes rather than the hold the July 9-3 vote delivered. The US 10-year is at a near-3-year high and global bond markets sold off hard on 2 Sep."),
    ("Inflation trajectory", 0.15, 3.5,
     "Downgraded on energy and on a Philippine print far worse than this model previously assumed. US core 2.5% remains the one clean anchor; US headline 3.4% now faces Brent +40% y/y. Euro HICP 3.0% for 2026. PH printed 6.2% in July and BSP RAISED its 2027 forecast to 5.4% from 4.5% on El Nino and wage pass-through."),
    ("Growth momentum", 0.15, 5.0,
     "IMF April WEO unchanged and still current: global 3.1% (2026) / 3.2% (2027), US resilient at 2.4%, euro area cut to 0.7%. Trimmed because a Brent move to $95 is a straight tax on every net-importing economy in Europe and Asia. Wide dispersion - a stock-picker's macro, not a beta macro."),
    ("Corporate earnings", 0.2, 7.5,
     "Still the strongest pillar, and the 2 Sep selloff was macro de-rating rather than an earnings event: Asia ex-Japan EPS ~+52% (2026) / ~+28% (2027) is intact and AI infrastructure capex is still compounding through the semis supply chain. Trimmed a half point for energy input costs and the risk that a sustained $95+ Brent forces the 52% estimate down."),
    ("Valuation support", 0.1, 7.5,
     "The one driver that IMPROVED. The selloff made everything cheaper without changing the earnings: NDX 22.4x fwd still sits BELOW both its 10y (22.9x) and 5y (24.7x) averages, Asia at 10.5x is a two-decade-wide discount and just fell another 2-4%, Europe 15.4x. No broad bubble multiple anywhere."),
    ("Volatility & risk appetite", 0.1, 4.0,
     "The complacency trade has started to break, exactly as the curve said it would. VIX printed a 2026 low of 14.13 on 28 Aug and closed 2 Sep at 16.44, +10.2% on the day, against a futures curve already in contango (Sep 17.92, Dec 20.38). Still below the 19.5 long-run anchor, so there is more room to unwind than to fall - the risk the curve priced is now arriving rather than merely implied."),
    ("Geopolitics & energy", 0.1, 1.5,
     "Sharply worse and the weakest link by a wide margin. Two Saudi supertankers were struck in the Strait of Hormuz on 31 Aug; the US hit roughly 100 Iranian targets on 1 Sep and then struck Iranian tankers for the first time on 2 Sep under a new 'tanker for tanker' policy. Brent $94.86, +13.2% in a month and +40.3% y/y, after a Q1 spike to $118. This is the Hormuz scenario beginning to run, not a hypothetical."),
]
GAUGE = round(sum(w * s for _, w, s, _ in DRIVERS), 2)

# ----------------------------------------------------------------------------
# 5. FUNDS - verified structure, fees, and the return build-up
# ----------------------------------------------------------------------------

FX_DRIFT = 2.0          # PPP-implied PHP depreciation vs USD, %/yr (PH ~3.9% infl vs US ~2.4%)
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
        "gross_local": 5.25,
        "gross_note": "5y average PH short-rate path. Anchored on the live curve (91d 5.14%, 182d 5.52%, 364d 5.72%) with BSP at 5.00% after a third consecutive hike, reverting toward a ~4.50% neutral policy rate by year 3-5 - a higher neutral than assumed in August because the inflation regime itself has shifted up (BSP 2027 forecast 5.4%).",
        "vol_beta": 0.021, "fx_exposed": False,
        "macro_tilt": {"regional": None, "vol_path": +0.10, "rates": +0.25, "energy": +0.05},
        "dd_k_adj": 0.0, "cash_like": True,
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
        "gross_note": "NDX 5y total return of 8.0% (JPM LTCMA US large cap 6.7% + 1.3% NDX growth premium, valuation neutral at 22.4x vs 22.9x 10y avg), times ~78% covered-call upside capture, plus ~0.5%/yr of option premium earned back as implied vol rises 14.1 -> 19.4.",
        "vol_beta": 1.22 * 0.68, "fx_exposed": True,
        "macro_tilt": {"regional": "US", "vol_path": +0.60, "rates": -0.10, "energy": -0.10},
        "dd_k_adj": -0.10, "cash_like": False,
    },
    {
        "id": "ATRASEQ", "name": "ATRAM Asia Equity Opportunity Feeder Fund",
        "short": "Asia Equity", "ccy": "PHP (unhedged)", "region": "ASIA",
        "target": "Target fund: JPMorgan Asia Equity Dividend Fund (Asia Pacific ex-Japan). "
                  "Feeder launched 08 Dec 2016.",
        "target_verified": True,
        "fee_feeder": 1.18, "fee_target": 0.80,
        "fee_note": "1.17% trustee + 0.01% auditor (verified KIIDS) + ~0.80% estimated "
                    "target-fund OCF (ESTIMATE - not verifiable at source)",
        "gross_usd": 8.3,
        "gross_note": "JPM LTCMA EM equity 7.8% + ~1.0% re-rating from a 10.5x forward multiple against ~52%/~28% EPS growth, less ~0.5% for the dividend tilt's lower growth capture.",
        "vol_beta": 1.05 * 0.92, "fx_exposed": True,
        "macro_tilt": {"regional": "ASIA", "vol_path": 0.00, "rates": -0.05, "energy": -0.20},
        "dd_k_adj": +0.05, "cash_like": False,
    },
    {
        "id": "ATRGTEC", "name": "ATRAM Global Technology Feeder Fund",
        "short": "Global Technology", "ccy": "PHP (unhedged)", "region": "GLOBAL_TECH",
        "target": "Target fund: Fidelity Funds - Global Technology Fund. Benchmark: "
                  "MSCI ACWI Information Technology. Target-fund 5y annualised: 15.20% "
                  "(W GBP class, to 20 Aug 2026).",
        "target_verified": True,
        "fee_feeder": 1.15, "fee_target": 0.95,
        "fee_note": "1.15% ATRAM management fee (verified) + ~0.95% estimated "
                    "target-fund OCF (ESTIMATE - not verifiable at source)",
        "gross_usd": 9.0,
        "gross_note": "US large cap 6.7% (JPM LTCMA) + 3.5% tech earnings-growth premium - 1.2% multiple de-rating drag. Deliberately well BELOW the target fund's realised 15.20% 5y, which was earned inside an AI capex boom and is not a forecast.",
        "vol_beta": 1.30, "fx_exposed": True,
        "macro_tilt": {"regional": "GLOBAL_TECH", "vol_path": -0.35, "rates": -0.40, "energy": -0.15},
        "dd_k_adj": +0.15, "cash_like": False,
    },
]

# MSCI ACWI IT regional decomposition, used to score the Global Tech sleeve
ACWI_IT_MIX = {"US": 0.72, "ASIA": 0.16, "EUROPE": 0.12}

REGIONAL_TILT_PER_PT = 0.30     # % of 5y CAGR per point of macro score above neutral
NEUTRAL = 5.5

def regional_score(region_key):
    if region_key == "GLOBAL_TECH":
        return sum(REGIONS[r]["blend"] * w for r, w in ACWI_IT_MIX.items())
    return REGIONS[region_key]["blend"]

# ---- Per-fund return, volatility and drawdown -------------------------------

DD_K = 1.65      # calibrated: 1.65*sigma - 0.5*mu reproduces the observed median
DD_MU = 0.50     # rolling-5y max drawdown of the S&P 500 (~-20%) and NDX (~-33%)

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

    sig_asset = f["vol_beta"] * SP_VOL_5Y
    sig = sig_asset if not f["fx_exposed"] else combine_fx(sig_asset)

    # macro overlay
    t = f["macro_tilt"]
    rs = regional_score(f["region"])
    reg_tilt = (rs - NEUTRAL) * REGIONAL_TILT_PER_PT
    tilt_total = reg_tilt + t["vol_path"] + t["rates"] + t["energy"]
    macro_net = base_net + tilt_total

    k = DD_K + f["dd_k_adj"]
    def dd(mu):
        raw = k * sig - DD_MU * mu
        if f["cash_like"]:
            # money market: bounded by a 100bp parallel shock on ~0.5y duration
            # less one year of carry - it cannot behave like an equity fund
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
        "tilt_vol": t["vol_path"], "tilt_rates": t["rates"], "tilt_energy": t["energy"],
        "tilt_total": round(tilt_total, 2),
        "net_macro": round(macro_net, 2),
        "vol": round(sig, 2),
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
    return -max(port_k(w) * port_vol(w) - DD_MU * mu, 0.0)

def summarise(w, key):
    r, v, d = port_ret(w, key), port_vol(w), port_dd(w, key)
    # The peso illustration is computed from the ROUNDED figures the page shows,
    # not the raw ones, so a reader who multiplies out the displayed CAGR gets
    # exactly the peso number printed beside it. Using the raw values instead
    # left a ~P235 gap that nobody could reconcile. (Audit 2026-09-03.)
    r_d, d_d = round(r, 2), round(d, 1)
    return {
        "weights": [round(x * 100, 1) for x in w],
        "cagr": r_d, "vol": round(v, 2), "maxdd": d_d,
        "ret_per_dd": round(r / abs(d), 3) if d else None,
        "sharpe_like": round((r - MACRO["ph_tbill_364"]) / v, 3),
        "terminal_1m": round(1_000_000 * (1 + r_d / 100) ** 5),
        "trough_1m": round(1_000_000 * (1 + d_d / 100)),
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
        "source": "gap recorded rather than filled - Sunday job 2 retries weekly",
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

def enumerate_portfolios(key, min_w=0.05, max_eq=0.90):
    """All 5%-granular, fully-invested portfolios holding all four funds."""
    out = []
    for a in GRID:
        if a < min_w: continue
        for b in GRID:
            if b < min_w: continue
            for c in GRID:
                if c < min_w: continue
                d = round(1 - a - b - c, 10)
                if d < min_w - 1e-9 or d > 1: continue
                if round(d * 100) % 5 != 0: continue
                w = [a, b, c, d]
                out.append((w, summarise(w, key)))
    return out

# --- Baseline: pure 5-year strategic, no macro view -------------------------
# Horizon-appropriate growth allocation: a 20% liquidity/volatility buffer and
# the three equity engines held near-equally. This is what you would own if you
# had a 5-year horizon and NO view on the cycle.
BASELINE_W = [0.20, 0.30, 0.25, 0.25]
BASE = summarise(BASELINE_W, "net_base")
BASE_UNDER_MACRO = summarise(BASELINE_W, "net_macro")

# --- Optimised: maximise macro-adjusted CAGR subject to a drawdown budget ----
# Objective: the user asked for maximum 5y net CAGR with drawdown held to a
# minimum. A pure max-return solve just buys 90% Global Tech; a pure min-DD
# solve just buys cash. The defensible reading is: beat the baseline's return
# AND cut its drawdown. So we solve for max CAGR subject to
#   maxDD <= baseline maxDD - 2.0pp  (a hard, stated improvement)
DD_BUDGET_IMPROVEMENT = 2.0
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
     "~100 US strikes on Iran on 1 Sep, US strikes on Iranian tankers on 2 Sep. This row "
     "models the tail from here: full Strait closure and Brent to $130+ from $95. Global "
     "CPI re-accelerates, Fed forced to hike, multiples compress hardest at the long end.",
     {"ATRPHMM": +0.5, "ATRQIAP": -4.5, "ATRASEQ": -6.5, "ATRGTEC": -7.5}, 1.60),
    ("Hawkish repricing", "The 3 July dissents win and the market is already there - "
     "two hikes are priced for Sep-16 and Dec, with the 10-year at a near-3-year high. "
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
        d = -max(port_k(w) * v - DD_MU * r, 0.0)
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
    ("Philippine Statistics Authority", "Consumer Price Index - headline inflation 6.2% y/y in July 2026, eased from 6.4% in June",
     "https://psa.gov.ph/price-indices/cpi-ir"),
    ("European Central Bank", "Monetary policy decision, 23 July 2026 - deposit rate HELD at 2.25% after the June hike",
     "https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260723~29f24d99bc.en.html"),
    ("BSP Monetary Policy Report", "February 2026 economic outlook and inflation path",
     "https://www.bsp.gov.ph/Price%20Stability/MonetaryPolicyReport/FullReport-February2026.pdf"),
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
    ("BusinessWorld", "Philippine peso falls to a new all-time low of P62.565 per dollar, 2 September 2026 - a fourth consecutive record low",
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
        "sp_vol_5y": SP_VOL_5Y,
        "regions": {k: {**v} for k, v in REGIONS.items()},
        "hz_weights": HZ_W,
        "drivers": [{"name": n, "weight": w, "score": s, "note": t} for n, w, s, t in DRIVERS],
        "gauge": GAUGE,
        "funds": F, "corr": CORR, "corr_note": CORR_NOTE,
        "lookthrough": LOOKTHROUGH,
        "acwi_it_mix": ACWI_IT_MIX,
        "fx": {"drift": FX_DRIFT, "vol": FX_VOL, "corr": FX_CORR},
        "dd_model": {"k": DD_K, "mu_coef": DD_MU},
        "baseline": {"weights": [round(x*100) for x in BASELINE_W],
                     "base": BASE, "under_macro": BASE_UNDER_MACRO,
                     "scenarios": run_scenarios(BASELINE_W, "net_macro")},
        "optimized": {"weights": [round(x*100) for x in OPT_W],
                      "macro": OPT, "under_base": OPT_UNDER_BASE,
                      "dd_cap": round(DD_CAP, 1),
                      "scenarios": run_scenarios(OPT_W, "net_macro"),
                      "n_feasible": len(FEASIBLE), "n_total": len(ALL)},
        "best_ratio": {"weights": [round(x*100) for x in BEST_RATIO_W], **BEST_RATIO},
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
    A("\n[2] REGIONAL MACRO-DRIVER RANKING (1-10)")
    A(f"    {'region':<14}{'3M':>6}{'6M':>6}{'12M':>6}{'5Y':>6}{'blend':>8}")
    for k, v in sorted(p["regions"].items(), key=lambda t: -t[1]["blend"]):
        A(f"    {k:<14}{v['3M']:>6}{v['6M']:>6}{v['12M']:>6}{v['5Y']:>6}{v['blend']:>8}")
    A("\n[3] BROAD MACRO GAUGE")
    for d in p["drivers"]:
        A(f"    {d['name']:<30} w={d['weight']:.2f}  score={d['score']:.1f}")
    A(f"    {'COMPOSITE':<30}            GAUGE = {p['gauge']} / 10")
    A("\n[4] FUNDS - net 5y CAGR after ALL fees, and expected max drawdown")
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
    checks.append(("gauge within 1-10", 1 <= p["gauge"] <= 10))
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
        return (abs(1_000_000 * (1 + m["cagr"] / 100) ** 5 - m["terminal_1m"]) < 1.0
                and abs(1_000_000 * (1 + m["maxdd"] / 100) - m["trough_1m"]) < 1.0)
    checks.append(("peso figures reconcile with the displayed CAGR and drawdown",
                   _ties(p["baseline"]["under_macro"]) and _ties(p["optimized"]["macro"])))
    # regression: no feasible portfolio may exceed the stated drawdown budget
    cap = p["optimized"]["dd_cap"]
    checks.append(("no chosen portfolio exceeds the drawdown budget",
                   abs(port_dd(OPT_W, "net_macro")) <= cap + 1e-9))
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
