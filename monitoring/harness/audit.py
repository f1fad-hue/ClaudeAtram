"""Independent audit of the published dashboard (rebuilt 2026-11-03, v88).

Reads the payload (model/data.json and the copy embedded in dashboard.html), the
claims register and the README, and re-derives what the page states from the
published inputs. It never imports the engine: a check that shares the engine's
code shares its bugs. Exit code 1 if any check fails.

  python3 monitoring/harness/audit.py            # the working tree
  ATRAM_ROOT=/path/to/copy python3 .../audit.py  # a copy (the mutation runner)
  BASELINE_REF=<git ref>                         # the release new inputs are compared with
"""
import datetime as dt, itertools, json, math, os, re, subprocess, sys
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.environ.get("ATRAM_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = json.load(open(os.path.join(ROOT, "model", "data.json")))
HTML = open(os.path.join(ROOT, "dashboard.html")).read()
CLAIMS = open(os.path.join(ROOT, "monitoring", "CLAIMS.md")).read()
README = open(os.path.join(ROOT, "README.md")).read()
ENGINE = open(os.path.join(ROOT, "model", "engine.py")).read()
M = D["macro"]
def d(iso): return dt.date.fromisoformat(iso)
AS_OF, REV = d(D["as_of"]), d(D["review_date"])
FAILS, N = [], [0]

def sec(t): print(f"\n== {t}")
def ck(label, ok, detail=""):
    N[0] += 1
    if not ok: FAILS.append(label)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"   {detail}" if detail and not ok else ""))

# ---------------------------------------------------------------------------
sec("A. THE PAYLOAD")
m_ = re.search(r'<script id="D" type="application/json">\s*(.*?)\s*</script>', HTML, re.S)
ck("the page embeds exactly one payload", m_ is not None and HTML.count('<script id="D"') == 1)
ck("the embedded payload is model/data.json", m_ is not None and json.loads(m_.group(1)) == D)
ck("the review date is on or after the data date", REV >= AS_OF, f"{REV} vs {AS_OF}")
ck("the data date is a weekday", AS_OF.weekday() < 5, f"{AS_OF:%A}")
for k in ("optimized", "portfolio_d"):
    ck(f"retired key '{k}' is absent", k not in D)
PAA, PBB, PCC = D["portfolio_a"], D["portfolio_b"], D["portfolio_c"]
ck("the 21 Oct review record stays retired (no review, match flag or outside list on A; no pa_review_*)",
   not {"review", "is_review_pick", "review_outside"} & set(PAA) and not any(k.startswith("pa_review_") for k in M))

# ---------------------------------------------------------------------------
sec("B. FUNDS: fees, nets, tilts and drawdowns")
FU = D["funds"] + PBB["funds"]
IDS = [f["id"] for f in FU]
ck("the universe is the payload's ids, in order", IDS == PBB["ids"] == PAA["ids"] == PCC["ids"], f"{IDS}")
DM = D["dd_model"]; K0, MU, SC = DM["k"], DM["mu_coef"], DM["horizon_scalar"]
ck("the drawdown horizon scalar is sqrt(horizon / calibration)", abs(SC - math.sqrt(DM["horizon_y"] / DM["calib_y"])) < 1e-6)
CASH = {i for i, f in enumerate(FU) if f["id"] == "ATRPHMM"}
for f in FU:
    i_ = f["id"]
    ck(f"{i_}: total fee = feeder + target", abs(round(f["fee_feeder"] + f["fee_target"], 2) - f["fee_total"]) < 0.006,
       f"{f['fee_feeder']} + {f['fee_target']} vs {f['fee_total']}")
    ck(f"{i_}: net base = gross - fees", abs(round(f["gross_php"] - f["fee_total"], 2) - f["net_base"]) < 0.006)
    tt = f["tilt_regional"] + f["tilt_vol"] + f["tilt_rates"] + f["tilt_energy"] + f["tilt_trend"]
    ck(f"{i_}: the 3/5/10-year tilt is the sum of its five parts", abs(tt - f["tilt_total"]) < 0.011, f"{tt:.3f} vs {f['tilt_total']}")
    ck(f"{i_}: net 3/5/10-year = base + tilt; net 10-year = base + 10-year tilt",
       abs(f["net_base"] + f["tilt_total"] - f["net_macro"]) < 0.011 and abs(f["net_base"] + f["tilt_total_10y"] - f["net_10y"]) < 0.011)
    if f["id"] not in ("ATRPHMM",):
        for col, ddk in (("net_macro", "dd_macro"), ("net_10y", "dd_10y"), ("net_base", "dd_base")):
            dd_ = round(-max((f["dd_k"] * f["vol"] - MU * f[col]) * SC, 0.0), 1)
            ck(f"{i_}: {ddk} reproduces from k, vol and {col}", abs(dd_ - f[ddk]) <= 0.11, f"{dd_} vs {f[ddk]}")
    ck(f"{i_}: fees and volatility are positive and sane", 0 < f["fee_total"] < 5 and 0 < f["vol"] < 40)

# ---------------------------------------------------------------------------
sec("C. PORTFOLIOS: weights, limits, re-derived figures and the rule")
C = PBB["corr"]; NU = len(FU)
ck("the correlation matrix is square, symmetric, unit-diagonal", len(C) == NU and all(len(r) == NU for r in C)
   and all(abs(C[i][j] - C[j][i]) < 1e-9 for i in range(NU) for j in range(NU)) and all(C[i][i] == 1 for i in range(NU)))
LIM = D["universe"]["limits"]; CAP = D["dd_budget"]["cap"]
def pk(w):
    eq = sum(w[i] for i in range(NU) if i not in CASH)
    return K0 if eq <= 0 else K0 + sum(w[i] * (FU[i]["dd_k"] - K0) for i in range(NU) if i not in CASH) / eq
N100 = {}
def figures(w, key):
    """The printed figures by the reader's route: the CAGR as the EXACT decimal sum of
    weight x net rounded half-up (weights on the 5% grid, nets at 2dp), the volatility
    from the correlation matrix, the drawdown from the two printed figures."""
    if key not in N100: N100[key] = [round(f[key] * 100) for f in FU]
    s_ = sum(w[i] * N100[key][i] for i in range(NU))             # in units of 0.0001%
    rd = float((Decimal(s_) / 10000).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    r = math.fsum(w[i] / 100 * FU[i][key] for i in range(NU))
    v = math.sqrt(math.fsum(w[i] / 100 * w[j] / 100 * FU[i]["vol"] * FU[j]["vol"] * C[i][j] for i in range(NU) for j in range(NU)))
    vd = round(v, 2)
    return rd, vd, round(-max((pk(w) * vd - MU * rd) * SC, 0.0), 1), r, v
PIN = IDS.index("ATRQIAP")
for lab, P in (("A", PAA), ("B", PBB), ("C", PCC)):
    w = [int(x) for x in P["weights"]]
    ck(f"{lab}: {NU} weights on the 5% grid summing to 100", len(w) == NU and sum(w) == 100 and all(x % 5 == 0 for x in w), f"{w}")
    caps = [x for i, x in enumerate(w) if not (lab == "C" and i == PIN)]
    ck(f"{lab}: at most {LIM['max_funds']} funds, {LIM['max_w']}% in any one, {LIM['min_cash']}% cash"
       + (" (C's pin excepted from the cap)" if lab == "C" else ""),
       sum(1 for x in w if x) <= LIM["max_funds"] and max(caps) <= LIM["max_w"] and w[0] >= LIM["min_cash"], f"{w}")
    for view, key in (("macro", "net_macro"), ("base", "net_base"), ("ten", "net_10y")):
        rd, vd, dd_, _, _ = figures(w, key)
        S = P[view]
        ck(f"{lab} {view}: CAGR / vol / drawdown re-derive ({rd} / {vd} / {dd_})",
           (rd, vd, dd_) == (S["cagr"], S["vol"], S["maxdd"]), f"vs {S['cagr']} / {S['vol']} / {S['maxdd']}")
        ck(f"{lab} {view}: return per drawdown and the 10-year peso value follow from the printed figures",
           abs(S["ret_per_dd"] - round(S["cagr"] / abs(S["maxdd"]), 3)) < 0.0011
           and abs(S["terminal_1m"] - 1e6 * (1 + S["cagr"] / 100) ** 10) < 2, f"{S['ret_per_dd']} / {S['terminal_1m']}")
    ck(f"{lab}: inside the drawdown budget on its 3/5/10-year view", abs(P["macro"]["maxdd"]) <= CAP + 1e-9, f"{P['macro']['maxdd']} vs {CAP}")
    own = P["ten"] if P["column"] == "net_10y" else P["macro"]
    g_ = [r_ for r_ in P["scenarios"] if r_["name"].startswith("Grind")]
    ck(f"{lab}: its grind-on stress row is its own-horizon headline", len(g_) == 1
       and (g_[0]["cagr"], g_[0]["vol"], g_[0]["maxdd"]) == (own["cagr"], own["vol"], own["maxdd"]), f"{g_[:1]} vs {own['cagr']}")
    ck(f"{lab}: its drawdown coefficient is its own mix", abs(D["dd_model"][lab.lower() + "_k"] - round(pk(w), 5)) < 1e-6)
ck("C holds Nasdaq Equity Income at its pin", PCC["weights"][PIN] == PCC["pin_pct"] == 50, f"{PCC['weights'][PIN]}")
_alt = [(c_, x, e) for c_, a_ in D["dd_gauge"]["alt"].items() for x, e in a_.items()]
ck("every budget step prints the CAGR its own search ranked on, and re-derives from its weights",
   all(e["cagr"] == e["best"] and figures(e["weights"], "net_10y" if x == "a" else "net_macro")[0] == e["cagr"] for _, x, e in _alt),
   f"{[(c_, x, e['cagr'], e['best']) for c_, x, e in _alt if e['cagr'] != e['best']][:3]}")

# The rule, re-run: maximum growth on the portfolio's own view inside the budget (raw
# drawdown), a shallower drawdown breaking exact ties - over every mix the limits allow.
def mixes(pin=None):
    others = [i for i in range(1, NU) if i != pin]
    slots = LIM["max_funds"] - 1 - (1 if pin is not None else 0)
    for n in range(0, slots + 1):
        for combo in itertools.combinations(others, n):
            for ws in itertools.product(range(5, LIM["max_w"] + 1, 5), repeat=n):
                rest = 100 - sum(ws) - (PCC["pin_pct"] if pin is not None else 0)
                if rest < LIM["min_cash"] or rest > LIM["max_w"]: continue   # cash is capped like any fund
                w = [0] * NU; w[0] = rest
                if pin is not None: w[pin] = PCC["pin_pct"]
                for i, x in zip(combo, ws): w[i] = x
                yield w
def pick(key, pin=None):
    """The published rule: feasible if both the raw and the printed drawdown are inside the
    budget; the best printed CAGR; within it the shallowest printed, then raw, drawdown."""
    feas, n_tot = [], 0
    for w in mixes(pin):
        n_tot += 1
        rd, vd, dd_, r, v = figures(w, key)
        ddr = max((pk(w) * v - MU * r) * SC, 0.0)
        if ddr > CAP + 1e-9 or abs(dd_) > CAP + 1e-9: continue
        feas.append((rd, abs(dd_), ddr, w))
    top = max(x[0] for x in feas)
    band = [x for x in feas if x[0] >= top - 1e-9]
    return min(band, key=lambda x: (x[1], x[2]))[3], len(feas), len(band), n_tot
for lab, P, key, pin in (("A", PAA, "net_10y", None), ("B", PBB, "net_macro", None), ("C", PCC, "net_macro", PIN)):
    w_, nf, nb, nt = pick(key, pin)
    ck(f"{lab} is the rule's pick on its own view, re-run over all {nt} mixes ({nf} feasible, {nb} at the best CAGR)",
       w_ == [int(x) for x in P["weights"]] and nf == P["n_feasible"] and nb == P["band_n"],
       f"{w_} ({nf}, {nb}) vs {P['weights']} ({P['n_feasible']}, {P['band_n']})")
    if lab == "B": ck(f"the universe's mix count is the payload's ({nt})", nt == D["universe"]["n_total"], f"{D['universe']['n_total']}")
    if lab == "C": ck(f"C's pinned mix count is the payload's ({nt})", nt == PCC["n_total"], f"{PCC['n_total']}")

# ---------------------------------------------------------------------------
sec("D. THE MACRO GAUGE, THE DRIVER PATHS AND THE REGIONS")
def to5(v): return round(1 + (v - 1) * 4 / 9, 2)
DR = D["drivers"]; HZ = D["hz_weights"]
ck("driver weights sum to 1", abs(sum(x["weight"] for x in DR) - 1) < 1e-9)
ck("horizon weights sum to 1 and are each view's share of ten years", abs(sum(HZ.values()) - 1) < 1e-9
   and HZ == {"3Y": 0.3, "5Y": 0.2, "10Y": 0.5}, f"{HZ}")
for x in DR:
    ck(f"{x['name']}: the 1-5 score is the 1-10 research score rescaled", x["score"] == to5(x["score_10"]), f"{x['score']} vs {to5(x['score_10'])}")
    ck(f"{x['name']}: its path runs from now toward neutral, never past it",
       all(min(x["score_10"], 5.5) - 1e-9 <= x["path"][h] <= max(x["score_10"], 5.5) + 1e-9 for h in ("3Y", "5Y"))
       and x["path"]["10Y"] == 5.5, f"{x['score_10']} -> {x['path']}")
g10 = round(sum(x["weight"] * x["score_10"] for x in DR), 2)
ck("the gauge is the weighted drivers, rescaled", D["gauge_10"] == g10 and D["gauge"] == to5(g10), f"{g10} / {to5(g10)}")
for h in ("3Y", "5Y", "10Y"):
    gp = round(sum(x["weight"] * x["path"][h] for x in DR), 2)
    ck(f"the {h} gauge is the weighted {h} paths", D["gauge_path_10"][h] == gp and D["gauge_path"][h] == to5(gp), f"{gp}")
for rk, r in D["regions"].items():
    ok = all(r[h] == to5(r[h + "_10"]) for h in HZ)
    ck(f"{rk}: each horizon's 1-5 score is its research score rescaled, the blend the horizon-weighted average",
       ok and abs(r["blend"] - round(sum(r[h] * w for h, w in HZ.items()), 2)) < 0.006
       and abs(r["blend_10"] - round(sum(r[h + "_10"] * w for h, w in HZ.items()), 2)) < 0.006, f"{r['blend']}")
G = D["dd_gauge"]; band = [b for b in G["bands"] if b["lo"] <= G["value"] < b["hi"] or (b["hi"] == 5 and G["value"] == 5)]
ck("the drawdown gauge's bands tile 1-5 and its value sits in the band it reports",
   G["bands"][0]["lo"] == 1 and G["bands"][-1]["hi"] == 5 and all(a["hi"] == b["lo"] for a, b in zip(G["bands"], G["bands"][1:]))
   and len(band) == 1 and band[0] == G["band"], f"{G['value']} in {G['band']}")
# THE GAUGE RE-DERIVED (v90). Until v90 the audit checked only the bands and the budget, not
# the readings - and its budget check took the band's step as the budget, which would have
# failed falsely the first time a new band was read before two month-end reviews.
_w3 = HZ["3Y"] / (HZ["3Y"] + HZ["5Y"]); _wv = {"3Y": round(_w3, 2), "5Y": round(1 - _w3, 2)}
_trp = {h: round(sum(v["score"][h] for v in D["trend"]["sleeves"].values()) / len(D["trend"]["sleeves"]), 2) for h in ("3Y", "5Y", "10Y")}
from decimal import Decimal as _D, ROUND_HALF_UP as _HU
_q2 = lambda x: float(x.quantize(_D("0.01"), rounding=_HU))      # exact half-up, the page's convention
_rd = {h: _q2((_D(str(D["gauge_path"][h])) + _D(str(_trp[h]))) / 2) for h in ("3Y", "5Y", "10Y")}
ck("each budget-gauge view reads the mean of the driver gauge and the trend score at that horizon - volatility not in it",
   G["reading_of"] == ["macro", "trend"]
   and all(G["parts"][h]["macro"] == D["gauge_path"][h] and G["parts"][h]["trend"] == _trp[h]
           and G["parts"][h]["reading"] == _rd[h] and "vol" not in G["parts"][h] for h in ("3Y", "5Y", "10Y")),
   f"{ {h: (G['parts'][h]['macro'], G['parts'][h]['trend'], G['parts'][h]['reading']) for h in G['parts']} } vs {_rd}")
_val = _q2(sum(_D(str(_rd[h])) * _D(str(_wv[h])) for h in ("3Y", "5Y")))
ck(f"the budget gauge is the 3- and 5-year readings weighted by their share of the first five years ({_val})",
   G["views"] == ["3Y", "5Y"] and G["w"] == _wv and G["value"] == _val, f"{G['value']} vs {_val}")
_me = lambda x: (d(x) + dt.timedelta(days=1)).day == 1
ck("every month-end review on record is a month-end before the data date, read on 1-5",
   all(_me(r[0]) and d(r[0]) < AS_OF and 1 <= r[1] <= 5 for r in G["reviews"]), f"{G['reviews']}")
_bof = lambda v: next(b for b in G["bands"] if b["lo"] <= v < b["hi"] or (b["hi"] == 5 and v == 5))
_base = D["dd_budget"]["base"]; _gz = {g["name"]: g for g in G["guards"]}
_geo = next(x["score_10"] for x in DR if x["name"].startswith("Geopolitics"))
_ok = {"persistence": len(G["reviews"]) >= _gz["persistence"]["needed"]
                      and all(_bof(r[1]) == G["band"] for r in G["reviews"][-_gz["persistence"]["needed"]:]),
       "geopolitics": _geo > _gz["geopolitics"]["floor"],
       "vix": M["vix_latest"] <= M["vix_longrun"]}
_raise = G["band"]["cap"] > _base
_step = all(_ok[n] for n, g in _gz.items() if g["applies_to"] == "any step" or (_raise and g["applies_to"] == "raise"))
_rec = G["band"]["cap"] if G["band"]["cap"] != _base and _step else _base
ck("each guard reads what it guards: two month-end reviews in the band, geopolitics above its floor, the VIX at or under its long run",
   all(_gz[n]["ok"] == _ok[n] for n in _ok) and _gz["vix"]["reading"] == M["vix_latest"] and _gz["geopolitics"]["reading"] == _geo,
   f"{ {n: (_gz[n]['ok'], _ok[n]) for n in _ok} }")
ck(f"the budget in force is the band's step only when every guard that applies is clear ({_rec:.0f}%), and the picks ran at it",
   D["dd_budget"]["cap"] == G["recommended_cap"] == _rec and all(P["dd_cap"] == CAP == _rec for P in (PAA, PBB, PCC)),
   f"{D['dd_budget']['cap']} / {G['recommended_cap']} vs {_rec}")

# ---------------------------------------------------------------------------
sec("E. FRESHNESS (every clock, with its days left)")
for key, lim in (("equity_date", 5), ("brent_date", 5), ("wti_date", 5), ("usdphp_date", 5), ("psei_date", 5),
                 ("nikkei_latest_date", 5), ("kospi_latest_date", 5), ("ust_2y_date", 5), ("ust_30y_date", 5),
                 ("ust_10y_date", 5), ("fed_hike_odds_dec_date", 5)):
    lag = (AS_OF - d(M[key])).days
    ck(f"{key} within {lim}d of the data date ({lag}d, {lim - lag}d left)", 0 <= lag <= lim)
for lab, ser in (("VIX", M["vix_history"]), ("Brent", M["brent_history"]), ("10-year", M["ust_10y_history"])):
    lag = (AS_OF - d(ser[-1][0])).days
    ck(f"the {lab} series within 5d of the data date ({lag}d)", 0 <= lag <= 5)
    ck(f"the {lab} series is in date order with no repeats and nothing after the data date",
       [x[0] for x in ser] == sorted({x[0] for x in ser}) and d(ser[-1][0]) <= AS_OF)
for key, lim in (("ph_tbill_date", 14), ("hormuz_transits_date", 14)):
    age = (REV - d(M[key])).days
    ck(f"{key} within {lim}d of the review ({age}d, {lim - age}d left)", 0 <= age <= lim)
for k, v in D["lookthrough"].items():
    if v.get("as_of"):
        age = (REV - d(v["as_of"])).days
        ck(f"{k} holdings within 60d of the review ({age}d, {60 - age}d left)", 0 <= age <= 60)
age = (REV - d(D["vix_quote_date"])).days
ck(f"the VIX futures strip is younger than one 30-day roll window ({age}d)", 0 <= age < 30)
_due = max(dt.date(y, m, 1) for y in (REV.year - 1, REV.year)
           for m, last in ((1, 31), (4, 25), (7, 31), (10, 25)) if dt.date(y, m, last) <= REV)
ck("the IMF edition carried is the newest whose release window has closed", _due <= d(M["imf_weo_vintage"]) <= REV,
   f"{M['imf_weo_vintage']} vs due {_due}")
ck("Michigan sentiment is the final reading, or its first read is under two weeks old",
   M["us_umich_oct_final"] is True or (REV - d(M["us_umich_oct_date"])).days < 14)
_US = re.compile(r"^(FOMC\b|US .*\b(GDP|PCE|CPI|PPI|payrolls|jobs report|retail sales|midterm))")
ck("every catalyst is after the last session of its own market carried (US events against the US session)",
   all(d(c["date"]) > (d(M["equity_date"]) if _US.search(c["what"]) else AS_OF) for c in D["catalysts"]),
   f"{[(c['date'], c['what']) for c in D['catalysts']]}")

# ---------------------------------------------------------------------------
sec("F. CHAINS: every move reproduces from its own prior")
for lab, c_, p_, pts, pct in (("S&P", "spx_close", "spx_prev", "spx_chg_pts", "spx_chg_pct"),
                              ("Nasdaq", "nasdaq_close", "nasdaq_prev", "nasdaq_chg_pts", "nasdaq_chg_pct"),
                              ("Dow", "dow_close", "dow_prev", "dow_chg_pts", "dow_chg_pct"),
                              ("Nikkei", "nikkei_latest", "nikkei_latest_prev", "nikkei_latest_chg_pts", "nikkei_latest_chg_pct"),
                              ("KOSPI", "kospi_latest", "kospi_latest_prev", "kospi_latest_chg_pts", "kospi_latest_chg_pct"),
                              ("PSEi", "psei", "psei_prev", "psei_chg_pts", "psei_chg_pct")):
    ck(f"the {lab}'s close = prior + points, and its percentage = points / prior",
       abs(M[p_] + M[pts] - M[c_]) < 0.006 and abs(M[pts] / M[p_] * 100 - M[pct]) <= 0.0051, f"{M[p_]} {M[pts]:+} = {M[c_]}; {M[pct]}%")
vh = M["vix_history"]
ck("the VIX's latest and prior are the series' last two", M["vix_latest"] == vh[-1][1] and M["vix_prev_close"] == vh[-2][1]
   and M["vix_latest_date"] == vh[-1][0])
_vr = M["vix_reported_moves"][M["vix_latest_date"]]; _dp = len(repr(_vr).split(".")[1]) if "." in repr(_vr) else 0
ck("the VIX's reported move reproduces from the series", abs((vh[-1][1] / vh[-2][1] - 1) * 100 - _vr) <= 0.5 * 10 ** -_dp + 0.06)
bh = M["brent_history"]
ck("Brent's latest is the series' last", M["brent"] == bh[-1][1] and M["brent_date"] == bh[-1][0])
_bp = M["brent_roll_priors"].get(M["brent_date"], bh[-2][1])
ck("Brent's prior is the previous settle, or the new contract's own prior on a roll day", M["brent_prev"] == _bp, f"{M['brent_prev']} vs {_bp}")
ck("Brent's move and year-on-year change follow from its levels",
   abs(round(M["brent"] - M["brent_prev"], 2) - M["brent_chg_pts"]) < 0.006
   and abs(round((M["brent"] / M["brent_yr_ago"] - 1) * 100, 2) - M["brent_yoy"]) < 0.006)
_ann = d(M["brent_date"]).replace(year=d(M["brent_date"]).year - 1)
# v93: past the bound the base may stand only with its own date beside every quote of the y/y,
# re-read here from the published prose (not from the engine's flag alone).
_yb = d(M["brent_yr_ago_date"]); _yg = abs((_ann - _yb).days); _ybt = f"{_yb.day} {_yb:%b} {_yb.year}"
_yq = [t for t in [x["note"] for x in DR] + [x["summary"] for x in DR]
       + [r["why"] for r in D["regions"].values()] + [r["summary"] for r in D["regions"].values()]
       if f"{M['brent_yoy']:.1f}%" in t]
ck(f"Brent's year-ago base is within three days of the anniversary, or past it with its own date beside every y/y quote ({_yg}d)",
   _yg <= 3 or (M.get("brent_yr_ago_stale") is True and bool(_yq) and all(_ybt in t for t in _yq)
                and not any("of a year earlier" in t for t in _yq)), f"{len(_yq)} quotes")
ck("Brent's high is at or above every settle since its date, and the latest is not above it",
   all(v <= M["brent_high"] + 1e-9 for x, v in bh if x >= M["brent_high_date"]) and M["brent"] <= M["brent_high"] + 1e-9)
ck("WTI's move reproduces from its prior", abs((M["wti_settle"] / M["wti_prev"] - 1) * 100 - M["wti_chg_pct"]) <= 0.006
   and M["wti_prev_date"] < M["wti_date"])
ck("the peso's move and year-to-date loss follow from its levels",
   abs(M["usdphp"] - M["usdphp_prev"] - M["usdphp_chg"]) < 0.0006 and M["usdphp_prev_date"] < M["usdphp_date"]
   and abs(round((1 - M["usdphp_2025_close"] / M["usdphp"]) * 100, 2) - M["usdphp_ytd_pct"]) < 0.006)
uh = M["ust_10y_history"]
ck("the 10-year is the series' last official close", (M["ust_10y_date"], M["ust_10y"]) == tuple(uh[-1]))
ck("the 10-year's peak is above every close and older than the data date",
   all(v <= M["ust_10y_peak"] for _, v in uh) and d(M["ust_10y_peak_date"]) <= AS_OF)

# ---------------------------------------------------------------------------
sec("G. PROSE: numbers trace to inputs, summaries to notes, closes to their own days")
TXT = []
for x in DR:
    TXT += [("driver:" + x["name"], x["note"]), ("summary:" + x["name"], x["summary"]), ("path:" + x["name"], x["path_why"])]
for rk, r in D["regions"].items():
    TXT += [("region:" + rk, r["why"]), ("summary:" + rk, r["summary"])]
for c in D["catalysts"]: TXT.append(("catalyst:" + c["what"], c["why"]))
for k, v in D["lookthrough"].items(): TXT.append(("lookthrough:" + k, v.get("note", "")))
# v93: each fund's target-fund check is prose on the page, so its numbers must trace too.
for f_ in D["funds"] + [x for x in D["portfolio_b"]["funds"] if x["id"] not in {y["id"] for y in D["funds"]}]:
    if f_.get("target_check"): TXT.append(("target_check:" + f_["id"], f_["target_check"]["text"]))
TXT.append(("corr_note", D["corr_note"]))
NUMS = []
def walk(o):
    if isinstance(o, bool): return
    if isinstance(o, (int, float)): NUMS.append(float(o))
    elif isinstance(o, dict): [walk(v) for k, v in o.items() if k != "sources"]
    elif isinstance(o, list): [walk(v) for v in o]
walk(D)
NUMSET = sorted({abs(x) for x in NUMS})
NUM = re.compile(r"(?<![\w.])[-+]?\$?\d[\d,]*(?:\.\d+)?")
MON = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*"
untraced = []
for lab, t in TXT:
    clean = re.sub(r"\b\d{1,2} " + MON + r"\b", " ", t)
    clean = re.sub(r"\b\d+(?:st|nd|rd|th)\b", " ", clean)
    clean = re.sub(r"\b" + MON + r" (?:19|20)\d\d\b", " ", clean)
    for mm in NUM.finditer(clean):
        s_ = mm.group(0).lstrip("+$").replace(",", "").lstrip("-")
        if re.fullmatch(r"(19|20)\d\d", s_): continue
        tail = clean[mm.end():mm.end() + 7]
        if re.match(r"-(?:day|year|month|week|session)|d\b|y\b", tail): continue
        v = float(s_) * (1000 if tail.startswith("k") else 1)
        if v in (0.0, 1.0, 2.0, 3.0) and "." not in s_: continue
        prec = len(s_.split(".")[1]) if "." in s_ else 0
        tol = 0.5 * 10 ** -prec + 1e-9
        if not any(abs(w - v) <= tol for w in NUMSET): untraced.append((lab, mm.group(0)))
ck("every number in the notes traces to an input", not untraced, f"{untraced[:6]}")
def tokens(t): return {m.group(0).lstrip("+$").replace(",", "") for m in NUM.finditer(re.sub(r"\b\d{1,2} " + MON, " ", t))}
for x in DR:
    ck(f"the {x['name']} summary states nothing its note does not", tokens(x["summary"]) <= tokens(x["note"]) | tokens(x["summary"]) & tokens(x["note"]),
       f"{tokens(x['summary']) - tokens(x['note'])}")
for rk, r in D["regions"].items():
    ck(f"the {rk} summary states nothing its note does not", tokens(r["summary"]) <= tokens(r["why"]), f"{tokens(r['summary']) - tokens(r['why'])}")
_CLOSES = {"spx_close": "equity_date", "nasdaq_close": "equity_date", "dow_close": "equity_date",
           "nikkei_latest": "nikkei_latest_date", "kospi_latest": "kospi_latest_date", "psei": "psei_date",
           "usdphp": "usdphp_date", "brent": "brent_date", "wti_settle": "wti_date", "vix_latest": "vix_latest_date"}
_bad = []
for lab, t in TXT:
    for sent in re.split(r"(?<=[.;])\s+", t):
        if not re.search(r"\b\d{1,2} " + MON + r"|\bthe \d{1,2}(?:st|nd|rd|th)\b", sent): continue
        for k, dk in _CLOSES.items():
            forms = {f"{M[k]:.2f}", f"{M[k]:,.2f}"}
            if any(re.search(r"(?<![\d.,])" + re.escape(f_) + r"(?![\d])", sent) for f_ in forms):
                day = d(M[dk]).day
                if not re.search(rf"\b{day} {MON}|\bthe {day}(?:st|nd|rd|th)\b", sent): _bad.append((lab, k))
ck("every daily close quoted beside a date is quoted beside its own", not _bad, f"{_bad[:4]}")
_bel = [(lab, m.group(0)[:60]) for lab, t in TXT for m in re.finditer(
    r"Brent settled at \$(\d+(?:\.\d+)?)(?:[^.;]|\.(?=\d))*?below the \$(\d+(?:\.\d+)?)", t) if float(m.group(2)) <= float(m.group(1))]
ck("no note puts Brent below a high it has reached", not _bel, f"{_bel[:2]}")
_all = json.dumps(D)
ck("no NaN, undefined or malformed sign anywhere in the payload",
   not re.search(r"\bNaN\b|\bundefined\b|Infinity", _all) and "- +" not in _all and "+-" not in _all.replace("+-0", ""))

# ---------------------------------------------------------------------------
# v93: a figure keyed to a day (kospi_3nov_chg_pct) is quoted only in a sentence that names that
# day. The earnings note read the KOSPI's latest move beside "on the same fear" and Apple's 3 Nov
# fall as "the same day": true when written, false after each roll.
_MO = "jan feb mar apr may jun jul aug sep oct nov dec".split()
_SER = {"kospi": "KOSPI", "nikkei": "Nikkei", "nasdaq": "Nasdaq", "spx": "S&P", "dow": "Dow", "brent": "Brent",
        "wti": "WTI", "psei": "PSEi", "vix": "VIX", "usdphp": "peso"}
_ordn = lambda n: f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
_dk, _dq = [], 0
for k, v in M.items():
    m_ = re.match(r"^([a-z0-9]+?)_(\d{1,2})(" + "|".join(_MO) + r")(?:_|$)", k)
    if not m_ or m_.group(1) not in _SER or isinstance(v, bool) or not isinstance(v, (int, float)): continue
    _day, _mo = int(m_.group(2)), m_.group(3).capitalize()
    for src, t in TXT:
        for snt in re.split(r"(?<=[.])\s+(?=[A-Z(])", t):
            if _SER[m_.group(1)] in snt and any(re.search(r"(?<![\d.,])" + re.escape(f_) + r"(?!\d)", snt)
                                                for f_ in {f"{abs(v):,.2f}", f"{abs(v):.2f}"}):
                _dq += 1
                if f"{_day} {_mo}" not in snt and f"the {_ordn(_day)}" not in snt: _dk.append(f"{k} in {src}")
ck(f"a figure keyed to a day is quoted only beside that day ({_dq} quotes)", _dq > 0 and not _dk, "; ".join(_dk[:3]))
# v93: every fund's target-fund check is from this review, with a known status, and a charge
# marked confirmed is the charge the forecast carries.
_TCS = {"no target", "confirmed", "partly confirmed", "estimate", "unconfirmed", "disputed", "manager change"}
_tcf = D["funds"] + [x for x in D["portfolio_b"]["funds"] if x["id"] not in {y["id"] for y in D["funds"]}]
ck(f"every fund carries a target-fund check from this review, with a known status ({len(_tcf)} funds)",
   len(_tcf) == len(D["portfolio_b"]["ids"])
   and all(f_.get("target_check", {}).get("date") == D["review_date"] and f_["target_check"]["status"] in _TCS for f_ in _tcf),
   f"{[(f_['id'], f_.get('target_check', {}).get('date')) for f_ in _tcf if f_.get('target_check', {}).get('date') != D['review_date']][:2]}")
ck("a target charge marked confirmed is quoted at the charge the forecast carries",
   all(f"{f_['fee_target']:.2f}%" in f_["target_check"]["text"] for f_ in _tcf if f_["target_check"]["status"] == "confirmed"),
   f"{[f_['id'] for f_ in _tcf if f_['target_check']['status'] == 'confirmed']}")

sec("H. THE CLAIMS REGISTER")
_rows = [l for l in CLAIMS.splitlines() if l.startswith("|")]
_bad = []
hdr = None
for l in CLAIMS.splitlines():
    if l.startswith("| Claim |") or l.startswith("| Item |"): hdr = l.count("|"); continue
    if l.startswith("|") and not l.startswith("|---") and hdr is not None:
        cells = l.count("|") - l.count("\\|")
        if cells != hdr: _bad.append(l[:50])
    if not l.startswith("|"): hdr = None if not l.strip() else hdr
ck("every register row has as many cells as its table's header", not _bad, f"{_bad[:3]}")
def row(label):
    for l in _rows:
        cells = [c.strip() for c in l.split("|")]
        if len(cells) > 2 and cells[1].strip("* ") == label: return cells[2]
    return None
REG = [("Brent crude", M["brent"]), ("Brent y/y change", M["brent_yoy"]), ("USD/PHP", M["usdphp"]),
       ("US 2-year Treasury yield", M["ust_2y"]), ("US 10-year Treasury yield", M["ust_10y"]),
       ("VIX latest close", M["vix_latest"]), ("PSEi", M["psei"]), ("WTI crude", M["wti_settle"]),
       ("Nikkei 225", M["nikkei_latest"]), ("KOSPI", M["kospi_latest"]), ("USD/PHP YTD loss of purchasing power", M["usdphp_ytd_pct"]),
       ("US 30-year Treasury yield", M["ust_30y"])]
for lab, v in REG:
    cell = row(lab)
    head = re.findall(r"\*\*(.*?)\*\*", cell or "")
    forms = {f"{v:.2f}", f"{v:,.2f}", f"{v:g}"}
    ck(f"the register's '{lab}' headline is the payload's {v}", cell is not None and any(any(f_ in h for f_ in forms) for h in head[:1]),
       f"{head[:1]}")
ck("the register's gauge row reads the payload's drawdown gauge", f"{G['value']:.2f} of 5" in CLAIMS)
ck("the README dates the data the payload's way", f"Market data as of {AS_OF.day} {AS_OF:%b} {AS_OF.year}" in README)

# ---------------------------------------------------------------------------
sec("I. SOURCES AND INPUTS")
urls = [s["url"] for s in D["sources"]]
ck(f"no duplicate source URLs ({len(urls)} sources)", len(urls) == len(set(urls)), f"{[u for u in urls if urls.count(u) > 1][:2]}")
ck("every source is https", all(u.startswith("https://") for u in urls), f"{[u for u in urls if not u.startswith('https://')][:2]}")
_page = re.sub(r'<script id="D" type="application/json">.*?</script>', "", HTML, flags=re.S)
_prose = " ".join(t for _, t in TXT)
def used(k, v):
    if re.search(r"\b(?:m|M|macro|D\.macro)\.%s\b" % re.escape(k), _page): return True
    if len(re.findall(r'MACRO\["%s"\]|\b%s\b' % (re.escape(k), re.escape(k)), ENGINE)) > 1: return True
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return any(re.search(r"(?<![\d.])%s(?![\d])" % re.escape(f_), _prose.replace(",", "")) for f_ in {"%g" % v, "%g" % abs(v)})
    return False
try:
    ref = os.environ.get("BASELINE_REF", "HEAD")
    base = json.loads(subprocess.run(["git", "-C", ROOT if os.path.isdir(os.path.join(ROOT, ".git")) else os.path.dirname(__file__),
                                      "show", f"{ref}:model/data.json"], capture_output=True, text=True, check=True).stdout)["macro"]
    new = [k for k, v in M.items() if k not in base and not isinstance(v, (list, dict, bool)) and v is not None and not used(k, v)]
    ck(f"no input added since {ref} that nothing reads", not new, ", ".join(new))
except Exception as e:
    print(f"  [WARN] orphan check skipped: no baseline ({type(e).__name__})")

print(f"\nCHECKS: {N[0]}   FAILURES: {len(FAILS)}")
for f in FAILS: print("  FAIL:", f)
sys.exit(1 if FAILS else 0)
