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
# v119: the macro drivers are scored on 1-5 natively. hu2 is exact half-up to 2dp (the engine's rnd);
# wavg2 an exact weighted average of 2dp scores, half-up (the engine's gauge, paths and blends).
def hu2(v): return float(Decimal(repr(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
def wavg2(pairs):
    return float(sum(Decimal(repr(w)) * Decimal(repr(v)) for w, v in pairs).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
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
for k in ("optimized",):
    ck(f"retired key '{k}' is absent", k not in D)
PAA, PBB, PCC, PDD = D["portfolio_a"], D["portfolio_b"], D["portfolio_c"], D["portfolio_d"]
# PORTFOLIO C (owner, 2026-11-23, v125): the dividend-income portfolio - the four income funds and the money
# market (the owner's three funds v111-v124); the 50%-pinned C retired on 12 Nov (v101) left held-out inputs,
# which stay gone. C is re-picked below, every what-if and budget step held to its set.
ck("Portfolio C is the income funds and the money market, in every what-if and budget step; the old C's held-out inputs stay gone",
   PCC["funds"] == ["ATRPHMM", "ATRQIAP", "ATRASEQ", "ATRGLDV", "ATRAMIP"] and "fund" not in PCC and PCC["column"] == "net_macro"
   and all("c" in v and all(x == 0 for j, x in enumerate(v["c"]["weights"]) if PCC["ids"][j] not in PCC["funds"])
           and 2 <= sum(1 for x in v["c"]["weights"] if x) <= 5 for v in D["universe"]["what_if"].values())
   and all("c" in a_ for a_ in D["dd_gauge"]["alt"].values())
   and not any(re.fullmatch(r"[a-z]+_(w|cagr)_c_[a-z]+", k) for k in D["macro"]))
ck("the 21 Oct review record stays retired (no review, match flag or outside list on A; no pa_review_*)",
   not {"review", "is_review_pick", "review_outside"} & set(PAA) and not any(k.startswith("pa_review_") for k in M))

# ---------------------------------------------------------------------------
sec("B. FUNDS: fees, nets, tilts and drawdowns")
FU = D["funds"] + PBB["funds"]
IDS = [f["id"] for f in FU]
ck("the universe is the payload's ids, in order", IDS == PBB["ids"] == PAA["ids"] == PCC["ids"] == PDD["ids"], f"{IDS}")
DM = D["dd_model"]; K0, MU, SC = DM["k"], DM["mu_coef"], DM["horizon_scalar"]
ck("the drawdown horizon scalar is sqrt(horizon / calibration)", abs(SC - math.sqrt(DM["horizon_y"] / DM["calib_y"])) < 1e-6)
CASH = {i for i, f in enumerate(FU) if f["id"] == "ATRPHMM"}
for f in FU:
    i_ = f["id"]
    ck(f"{i_}: total fee = feeder + target", abs(round(f["fee_feeder"] + f["fee_target"], 2) - f["fee_total"]) < 0.006,
       f"{f['fee_feeder']} + {f['fee_target']} vs {f['fee_total']}")
    ck(f"{i_}: net base = gross - fees", abs(round(f["gross_php"] - f["fee_total"], 2) - f["net_base"]) < 0.006)
    tt = f["tilt_regional"] + f["tilt_rates"] + f["tilt_energy"] + f["tilt_trend"] + f["tilt_valuation"]
    ck(f"{i_}: the 1/3/5/10-year tilt is the sum of its five parts - region, rates, energy, trend, valuation; no volatility tilt",
       abs(tt - f["tilt_total"]) < 0.011 and "tilt_vol" not in f, f"{tt:.3f} vs {f['tilt_total']}")
    # v107: the valuation tilt re-derived from the valuation driver's path - year 1, years 2-3 (implied),
    # years 4-5 and years 6-10 at 10/20/20/50, at the regional rate per point, on the equity share, none for cash
    _VD = next(x for x in D["drivers"] if x["name"] == "Valuation support")
    _vy1 = next(r for r in D["dd_gauge"]["drivers"] if r["name"] == "Valuation support")["y1"]
    _vy23 = round((3 * _VD["path"]["3Y"] - _vy1) / 2, 3)
    _vb = round(0.1 * _vy1 + 0.2 * hu2(_vy23) + 0.2 * _VD["path"]["5Y"] + 0.5 * _VD["path"]["10Y"], 4)
    _vt = 0.0 if f["id"] == "ATRPHMM" else (_vb - 3.0) * D["regional_tilt_per_pt"] * f["equity_share"]
    ck(f"{i_}: the valuation tilt reproduces from the valuation path, and is none at 10 years",
       abs(f["tilt_valuation"] - _vt) < 0.0051 and f["tilt_valuation_10y"] == 0.0, f"{f['tilt_valuation']} vs {_vt:.4f}")
    ck(f"{i_}: net 1/3/5/10-year = base + tilt; net 10-year = base + 10-year tilt",
       abs(f["net_base"] + f["tilt_total"] - f["net_macro"]) < 0.011 and abs(f["net_base"] + f["tilt_total_10y"] - f["net_10y"]) < 0.011)
    if f["id"] not in ("ATRPHMM",):
        for col, ddk in (("net_macro", "dd_macro"), ("net_10y", "dd_10y"), ("net_base", "dd_base")):
            dd_ = round(-max((f["dd_k"] * f["vol"] - MU * f[col]) * SC, 0.0), 1)
            ck(f"{i_}: {ddk} reproduces from k, vol and {col}", abs(dd_ - f[ddk]) <= 0.11, f"{dd_} vs {f[ddk]}")
    ck(f"{i_}: fees and volatility are positive and sane", 0 < f["fee_total"] < 5 and 0 < f["vol"] < 40)
# v107: the published valuation channel is the one re-derived above, on B and D's year split.
_VC = D["val_channel"]
ck("the valuation channel's blend is its path on the 10/20/20/50 year split", abs(_VC["blend_5"] - _vb) < 0.0006
   and _VC["w"] == D["hz_split"] == {"1Y": 0.1, "3Y": 0.2, "5Y": 0.2, "10Y": 0.5}
   and abs(sum(_VC["w"][h] * _VC["path_5"][h] for h in _VC["w"]) - _VC["blend_5"]) < 0.0006, f"{_VC['blend_5']} vs {_vb}")

# v116: THE PESO DRIFT, re-derived here (only the engine checked it until v116). Every unhedged foreign
# fund assumes the peso weakens by the same drift a year, which must sit between the long-run inflation gap
# (PH 3.9 less US 2.4) and today's month-matched gap (September: PH CPI less US CPI; October has no US
# twelve-month rate, the BLS not having collected October 2025). The money market carries none.
_fx = D["fx"]; _ppp_now = round(M["ph_cpi_sep"] - M["us_cpi_headline"], 1)
ck(f"the peso drift ({_fx['drift']}) sits between the long-run inflation gap ({_fx['ppp_lr']}) and September's ({_ppp_now}), and every foreign fund carries it",
   abs(_fx["ppp_lr"] - 1.5) < 1e-9 and abs(_fx["ppp_now"] - _ppp_now) < 1e-9 and _fx["ppp_lr"] <= _fx["drift"] <= _fx["ppp_now"]
   and all(f["fx_drift"] == (0.0 if f["id"] == "ATRPHMM" else _fx["drift"]) for f in FU), f"{_fx}")

# ---------------------------------------------------------------------------
sec("C. PORTFOLIOS: weights, limits, re-derived figures and the rule")
C = PBB["corr"]; NU = len(FU)
ck("the correlation matrix is square, symmetric, unit-diagonal", len(C) == NU and all(len(r) == NU for r in C)
   and all(abs(C[i][j] - C[j][i]) < 1e-9 for i in range(NU) for j in range(NU)) and all(C[i][i] == 1 for i in range(NU)))
# v122: THE MACRO TAB'S "CORRELATED SENTIMENT" MATRIX IS A CORRELATION MATRIX: every entry in [-1, 1] and the whole
# positive semi-definite (a Cholesky factor exists), or some mix's variance would come out negative.
def _chol_ok(M, eps=1e-10):
    n = len(M); L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s_ = M[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                if s_ < -eps: return False
                L[i][i] = math.sqrt(max(s_, 0.0))
            else:
                L[i][j] = s_ / L[j][j] if L[j][j] > eps else 0.0
    return True
_C4 = D["corr"]; _id4 = [f["id"] for f in D["funds"]]
ck("the correlation matrix's entries are in [-1, 1], it is positive semi-definite, and the four-fund copy the Funds tab quotes is its corner",
   all(-1 <= C[i][j] <= 1 for i in range(NU) for j in range(NU)) and _chol_ok(C)
   and _id4 == IDS[:len(_id4)] and all(abs(_C4[i][j] - C[i][j]) < 1e-9 for i in range(len(_C4)) for j in range(len(_C4))),
   f"{_id4} vs {IDS[:4]}")
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
for lab, P in (("A", PAA), ("B", PBB)):
    w = [int(x) for x in P["weights"]]
    ck(f"{lab}: {NU} weights on the 5% grid summing to 100", len(w) == NU and sum(w) == 100 and all(x % 5 == 0 for x in w), f"{w}")
    ck(f"{lab}: at most {LIM['max_funds']} funds, {LIM['max_w']}% in any one, {LIM['min_cash']}% cash",
       sum(1 for x in w if x) <= LIM["max_funds"] and max(w) <= LIM["max_w"] and w[0] >= LIM["min_cash"], f"{w}")
    for view, key in (("macro", "net_macro"), ("base", "net_base"), ("ten", "net_10y")):
        rd, vd, dd_, _, _ = figures(w, key)
        S = P[view]
        ck(f"{lab} {view}: CAGR / vol / drawdown re-derive ({rd} / {vd} / {dd_})",
           (rd, vd, dd_) == (S["cagr"], S["vol"], S["maxdd"]), f"vs {S['cagr']} / {S['vol']} / {S['maxdd']}")
        ck(f"{lab} {view}: return per drawdown and the 10-year peso value follow from the printed figures",
           abs(S["ret_per_dd"] - round(S["cagr"] / abs(S["maxdd"]), 3)) < 0.0011
           and abs(S["terminal_1m"] - 1e6 * (1 + S["cagr"] / 100) ** 10) < 2, f"{S['ret_per_dd']} / {S['terminal_1m']}")
    ck(f"{lab}: inside the drawdown budget on its 1/3/5/10-year view", abs(P["macro"]["maxdd"]) <= CAP + 1e-9, f"{P['macro']['maxdd']} vs {CAP}")
    own = P["ten"] if P["column"] == "net_10y" else P["macro"]
    g_ = [r_ for r_ in P["scenarios"] if r_["name"].startswith("Grind")]
    ck(f"{lab}: its grind-on stress row is its own-horizon headline", len(g_) == 1
       and (g_[0]["cagr"], g_[0]["vol"], g_[0]["maxdd"]) == (own["cagr"], own["vol"], own["maxdd"]), f"{g_[:1]} vs {own['cagr']}")
    ck(f"{lab}: its drawdown coefficient is its own mix", abs(D["dd_model"][lab.lower() + "_k"] - round(pk(w), 5)) < 1e-6)
_alt = [(c_, x, e) for c_, a_ in D["dd_gauge"]["alt"].items() for x, e in a_.items()]
ck("every budget step prints the CAGR its own search ranked on, and re-derives from its weights",
   all(e["cagr"] == e["best"] and figures(e["weights"], "net_10y" if x == "a" else "net_macro")[0] == e["cagr"] for _, x, e in _alt),
   f"{[(c_, x, e['cagr'], e['best']) for c_, x, e in _alt if e['cagr'] != e['best']][:3]}")

# The rule, re-run: maximum growth on the portfolio's own view inside the budget (raw
# drawdown), a shallower drawdown breaking exact ties - over every mix the limits allow.
def mixes():
    others = list(range(1, NU))
    slots = LIM["max_funds"] - 1
    for n in range(0, slots + 1):
        for combo in itertools.combinations(others, n):
            for ws in itertools.product(range(5, LIM["max_w"] + 1, 5), repeat=n):
                rest = 100 - sum(ws)
                if rest < LIM["min_cash"] or rest > LIM["max_w"]: continue   # cash is capped like any fund
                w = [0] * NU; w[0] = rest
                for i, x in zip(combo, ws): w[i] = x
                yield w
ALLPTS = {}   # v122: every mix's printed (CAGR, drawdown) on a view, for the frontier and best-ratio checks
def pick(key):
    """The published rule: feasible if both the raw and the printed drawdown are inside the
    budget; the best printed CAGR; within it the shallowest printed, then raw, drawdown."""
    feas, n_tot = [], 0
    pts = ALLPTS.setdefault(key, [])
    for w in mixes():
        n_tot += 1
        rd, vd, dd_, r, v = figures(w, key)
        pts.append((rd, abs(dd_)))
        ddr = max((pk(w) * v - MU * r) * SC, 0.0)
        if ddr > CAP + 1e-9 or abs(dd_) > CAP + 1e-9: continue
        feas.append((rd, abs(dd_), ddr, w))
    top = max(x[0] for x in feas)
    band = [x for x in feas if x[0] >= top - 1e-9]
    return min(band, key=lambda x: (x[1], x[2]))[3], len(feas), len(band), n_tot
for lab, P, key in (("A", PAA, "net_10y"), ("B", PBB, "net_macro")):
    w_, nf, nb, nt = pick(key)
    ck(f"{lab} is the rule's pick on its own view, re-run over all {nt} mixes ({nf} feasible, {nb} at the best CAGR)",
       w_ == [int(x) for x in P["weights"]] and nf == P["n_feasible"] and nb == P["band_n"],
       f"{w_} ({nf}, {nb}) vs {P['weights']} ({P['n_feasible']}, {P['band_n']})")
    if lab == "B": ck(f"the universe's mix count is the payload's ({nt})", nt == D["universe"]["n_total"], f"{D['universe']['n_total']}")
# v122: THE PORTFOLIOS TAB'S "FEASIBLE SET" CHART, re-derived from every mix the limits allow (only the engine checked it
# until v122). Each frontier point's figures follow from its weights; no mix has a higher CAGR at no more drawdown; B is
# on it; and the best pure ratio is the highest return per drawdown of any mix.
_FR = D["universe"]["frontier"]; _pm = ALLPTS["net_macro"]
_frd = [(figures([int(round(x)) for x in f["weights"]], "net_macro"), f) for f in _FR]
ck(f"every frontier point re-derives from its weights and is within the limits ({len(_FR)} points)",
   all((r_[0], r_[2]) == (f["cagr"], f["dd"]) and abs(f["dd"]) == f["maxdd"] and sum(f["weights"]) == 100
       and sum(1 for x in f["weights"] if x) <= LIM["max_funds"] and max(f["weights"]) <= LIM["max_w"] and f["weights"][0] >= LIM["min_cash"]
       for r_, f in _frd), f"{[(f['cagr'], f['dd'], r_[0], r_[2]) for r_, f in _frd if (r_[0], r_[2]) != (f['cagr'], f['dd'])][:3]}")
_best_by_dd = {}
for c_, d_ in _pm: _best_by_dd[d_] = max(c_, _best_by_dd.get(d_, -1e9))
_dds = sorted(_best_by_dd); _run, _cum = -1e9, {}
for d_ in _dds: _run = max(_run, _best_by_dd[d_]); _cum[d_] = _run    # the best CAGR at this drawdown or less
import bisect as _bs
def _best_at(dd):
    i = _bs.bisect_right(_dds, dd + 1e-9) - 1
    return _cum[_dds[i]] if i >= 0 else -1e9
ck("every frontier point is efficient: no mix the limits allow has a higher CAGR at no more drawdown",
   all(_best_at(abs(f["dd"])) <= f["cagr"] + 1e-9 for f in _FR),
   f"{[(f['cagr'], f['dd'], _best_at(abs(f['dd']))) for f in _FR if _best_at(abs(f['dd'])) > f['cagr'] + 1e-9][:3]}")
ck("Portfolio B is a frontier point", any([int(round(x)) for x in f["weights"]] == [int(x) for x in PBB["weights"]] for f in _FR))
_BR = D["universe"]["best_ratio"]; _brr = figures([int(round(x)) for x in _BR["weights"]], "net_macro")
ck(f"the best pure ratio ({_BR['ret_per_dd']}) re-derives from its weights and is the highest of any mix",
   (_brr[0], _brr[2]) == (_BR["cagr"], _BR["maxdd"]) and _BR["ret_per_dd"] == round(_BR["cagr"] / abs(_BR["maxdd"]), 3)
   and _BR["ret_per_dd"] == max(round(c_ / d_, 3) for c_, d_ in _pm if d_ > 0), f"{_brr[:3]} / {_BR}")
# v122: THE VOLATILITY TERM STRUCTURE (Portfolios tab, "How each drawdown is estimated"), re-derived from its own rows:
# variance adds over time, so each span's forward follows from the implied vols either side; realised is implied less
# the variance risk premium; a one-sigma move is the implied vol times the root of the years.
_VT = D["vol_ts"]; _vrp = D["vol_channel"]["vrp"]
def _fwd_ok(a, b):
    f2 = (b["implied"] ** 2 * b["years"] - a["implied"] ** 2 * a["years"]) / (b["years"] - a["years"])
    return abs(math.sqrt(max(f2, 0.0)) - b["forward"]) < 0.02
ck("the volatility term structure re-derives: forwards from the implied vols, realised = implied less the premium, moves = implied x root T",
   _VT[0]["from_years"] == 0 and abs(_VT[0]["forward"] - _VT[0]["implied"]) < 1e-9
   and all(_fwd_ok(a, b) and b["from_years"] == a["years"] for a, b in zip(_VT, _VT[1:]))
   and all(abs(v["realised"] - (v["implied"] - _vrp)) < 0.011 and abs(v["move_1sd"] - v["implied"] * math.sqrt(v["years"])) < 0.02
           and abs(v["move_2sd"] - 2 * v["move_1sd"]) < 0.02 for v in _VT)
   and abs(D["vol_channel"]["blend"] - sum(v["forward"] * D["hz_weights"][v["label"]] for v in _VT)) < 0.006,
   f"{_VT}")

# PORTFOLIO D (v96, owner 2026-11-07; re-set v99, owner 2026-11-12): Nasdaq Equity Income as the
# largest holding of two to five funds, each at least 5%, with no single-fund cap and no cash floor;
# the rule picks the number of funds. Re-checked and re-picked here from its own generator, not the
# engine's: Nasdaq's weight is the outer loop here, the fund set the engine's.
wD = [int(x) for x in PDD["weights"]]
nD = sum(1 for x in wD if x)
ck("D: 11 weights on the 5% grid summing to 100", len(wD) == NU and sum(wD) == 100 and all(x % 5 == 0 for x in wD), f"{wD}")
ck("D: Nasdaq Equity Income the largest holding of two to five funds, each at least 5%",
   PDD["fund"] == "ATRQIAP" and wD[PIN] >= 5 and 2 <= nD <= 5 == PDD["max_funds"] and PDD["min_funds"] == 2
   and nD == PDD["n_funds"] and all(x < wD[PIN] for j_, x in enumerate(wD) if j_ != PIN), f"{wD}")
for view, key in (("macro", "net_macro"), ("base", "net_base"), ("ten", "net_10y")):
    rd, vd, dd_, _, _ = figures(wD, key); S = PDD[view]
    ck(f"D {view}: CAGR / vol / drawdown re-derive ({rd} / {vd} / {dd_})",
       (rd, vd, dd_) == (S["cagr"], S["vol"], S["maxdd"]), f"vs {S['cagr']} / {S['vol']} / {S['maxdd']}")
    ck(f"D {view}: return per drawdown and the 10-year peso value follow from the printed figures",
       abs(S["ret_per_dd"] - round(S["cagr"] / abs(S["maxdd"]), 3)) < 0.0011
       and abs(S["terminal_1m"] - 1e6 * (1 + S["cagr"] / 100) ** 10) < 2, f"{S['ret_per_dd']} / {S['terminal_1m']}")
ck("D: inside the drawdown budget on its 1/3/5/10-year view", abs(PDD["macro"]["maxdd"]) <= CAP + 1e-9 and PDD["dd_cap"] == CAP,
   f"{PDD['macro']['maxdd']} vs {CAP}")
_gD = [r_ for r_ in PDD["scenarios"] if r_["name"].startswith("Grind")]
ck("D: its grind-on stress row is its own-horizon headline", len(_gD) == 1
   and (_gD[0]["cagr"], _gD[0]["vol"], _gD[0]["maxdd"]) == (PDD["macro"]["cagr"], PDD["macro"]["vol"], PDD["macro"]["maxdd"]))
ck("D: its drawdown coefficient is its own mix", abs(D["dd_model"]["d_k"] - round(pk(wD), 5)) < 1e-6)
def _splits(total, parts, lo, hi):
    if parts == 0:
        if total == 0: yield ()
        return
    for x in range(lo, min(hi, total) + 1, 5):
        for rest in _splits(total - x, parts - 1, lo, hi):
            yield (x,) + rest
def d_mixes_audit():
    others = [i for i in range(NU) if i != PIN]
    for q in range(5, 101, 5):                       # Nasdaq's weight, the largest
        for k in range(1, 5):                        # one to four other funds
            for sup in itertools.combinations(others, k):
                for sp in _splits(100 - q, k, 5, q - 5):
                    w = [0] * NU; w[PIN] = q
                    for i_, x in zip(sup, sp): w[i_] = x
                    yield w
_fD, _nD, _nDn = [], 0, {}
for w in d_mixes_audit():
    _nD += 1; n_ = sum(1 for x in w if x); _nDn[n_] = _nDn.get(n_, 0) + 1
    rd, vd, dd_, r, v = figures(w, "net_macro")
    ddr = max((pk(w) * v - MU * r) * SC, 0.0)
    if ddr > CAP + 1e-9 or abs(dd_) > CAP + 1e-9: continue
    _fD.append((rd, abs(dd_), ddr, w, n_))
def _pickD(rows):
    t_ = max(x[0] for x in rows); b_ = [x for x in rows if x[0] >= t_ - 1e-9]
    return min(b_, key=lambda x: (x[1], x[2], x[4])), b_
_winD, _bD = _pickD(_fD); _wD = _winD[3]
ck(f"D is the rule's pick on the 1/3/5/10-year view, re-run over all {_nD} of its mixes ({len(_fD)} feasible, {len(_bD)} at the best CAGR)",
   _wD == wD and len(_fD) == PDD["n_feasible"] and len(_bD) == PDD["band_n"] and _nD == PDD["n_total"],
   f"{_wD} ({len(_fD)}, {len(_bD)}, {_nD}) vs {wD} ({PDD['n_feasible']}, {PDD['band_n']}, {PDD['n_total']})")
_bcD = {b_["n"]: b_ for b_ in PDD["by_count"]}
_bc_ok, _bc_bad = sorted(_bcD) == [2, 3, 4, 5], []
for n_ in range(2, 6):
    rows_ = [x for x in _fD if x[4] == n_]
    (r_, d_, _, w_, _), _ = _pickD(rows_)
    b_ = _bcD.get(n_, {})
    if not (b_.get("weights") == w_ and b_.get("cagr") == r_ and abs(b_.get("maxdd", 0)) == d_
            and b_.get("n_feasible") == len(rows_) and b_.get("n_total") == _nDn.get(n_)):
        _bc_ok = False; _bc_bad.append(n_)
ck("D: each count's best (two to five funds) re-derives, and D's count is the best of them",
   _bc_ok and max(PDD["by_count"], key=lambda b_: (b_["cagr"], -abs(b_["maxdd"]), -b_["n"]))["n"] == nD,
   f"counts off: {_bc_bad}")

# PORTFOLIO C, THE DIVIDEND-INCOME PORTFOLIO (v125, owner 2026-11-23): two to five of the four income-paying
# funds and Peso Money Market, each at least 5%, no main fund and no single-fund cap; the one rule on the
# 1/3/5/10-year view. Re-picked here from its own generator - the fund set first, then the 5% splits - and
# its table by number of funds re-derived row by row. Its eligible set is checked against the funds' own
# payout records: every fund it may hold pays income, the money market apart, and no other fund is in it.
wC = [int(x) for x in PCC["weights"]]
nC = sum(1 for x in wC if x)
_iC = [IDS.index(f) for f in PCC["funds"]]
_payC = PCC["payout"]
ck("C: its set is the four income-paying funds and the money market, each with a payout record and its sources",
   sorted(PCC["funds"]) == sorted(["ATRPHMM", "ATRQIAP", "ATRASEQ", "ATRGLDV", "ATRAMIP"])
   and all(_payC[f]["freq"] in ("monthly", "quarterly") and _payC[f]["sources"] for f in PCC["funds"] if f != "ATRPHMM")
   and _payC["ATRPHMM"]["freq"] is None and set(_payC) == set(PCC["funds"])
   and all(h in {x["short"] for x in D["universe"]["held_out"]} for h in PCC["held_out_income"]), f"{PCC['funds']}")
ck("C: 11 weights on the 5% grid summing to 100, two to five of its funds, each at least 5%, nothing else",
   len(wC) == NU and sum(wC) == 100 and all(x % 5 == 0 for x in wC) and all(x == 0 for i, x in enumerate(wC) if i not in _iC)
   and 2 <= nC <= 5 and nC == PCC["n_funds"] and (PCC["min_funds"], PCC["max_funds"]) == (2, 5) and "fund" not in PCC, f"{wC}")
for view, key in (("macro", "net_macro"), ("base", "net_base"), ("ten", "net_10y")):
    rd, vd, dd_, _, _ = figures(wC, key); S = PCC[view]
    ck(f"C {view}: CAGR / vol / drawdown re-derive ({rd} / {vd} / {dd_})",
       (rd, vd, dd_) == (S["cagr"], S["vol"], S["maxdd"]), f"vs {S['cagr']} / {S['vol']} / {S['maxdd']}")
    ck(f"C {view}: return per drawdown and the 10-year peso value follow from the printed figures",
       abs(S["ret_per_dd"] - round(S["cagr"] / abs(S["maxdd"]), 3)) < 0.0011
       and abs(S["terminal_1m"] - 1e6 * (1 + S["cagr"] / 100) ** 10) < 2, f"{S['ret_per_dd']} / {S['terminal_1m']}")
ck("C: inside the drawdown budget on its 1/3/5/10-year view", abs(PCC["macro"]["maxdd"]) <= CAP + 1e-9 and PCC["dd_cap"] == CAP
   and PCC["in_budget"], f"{PCC['macro']['maxdd']} vs {CAP}")
_gC = [r_ for r_ in PCC["scenarios"] if r_["name"].startswith("Grind")]
ck("C: its grind-on stress row is its own-horizon headline", len(_gC) == 1
   and (_gC[0]["cagr"], _gC[0]["vol"], _gC[0]["maxdd"]) == (PCC["macro"]["cagr"], PCC["macro"]["vol"], PCC["macro"]["maxdd"]))
ck("C: its drawdown coefficient is its own mix", abs(D["dd_model"]["c_k"] - round(pk(wC), 5)) < 1e-6)
# v131 (owner 2026-11-23: "Update also portfolio C with my current age born Dec 30, 1983"; asked, "Stocks <= 110 - age"):
# the age is re-derived here from the birth date in the engine's source and the review date, and every C mix the audit
# generates keeps its stock share - each fund's equity share, the money market none - within 110 less it.
_bd = d(re.search(r'^OWNER_BIRTH = "(\d{4}-\d{2}-\d{2})"', ENGINE, re.M).group(1))
_ageA = REV.year - _bd.year - ((REV.month, REV.day) < (_bd.month, _bd.day))
_capA = 110 - _ageA
_eqA = {f["id"]: (0.0 if f["id"] == "ATRPHMM" else f.get("equity_share", 1.0)) for f in D["funds"] + PBB["funds"]}
_stk = lambda w: sum(x * _eqA[IDS[i]] for i, x in enumerate(w) if x)
ck("C: the owner's age and stock cap re-derive from the birth date and the review date, and C keeps within the cap",
   PCC["age"] == _ageA and PCC["age_rule"] == 110 and PCC["equity_cap"] == _capA and abs(PCC["stock_pct"] - _stk(wC)) < 0.006
   and _stk(wC) <= _capA + 1e-9 and d(PCC["cap_next_date"]) > REV
   and (d(PCC["cap_next_date"]).month, d(PCC["cap_next_date"]).day) == (_bd.month, _bd.day)
   and all(_stk(v["c"]["weights"]) <= _capA + 1e-9 for v in D["universe"]["what_if"].values())
   and all(_stk(a_["c"]["weights"]) <= _capA + 1e-9 for a_ in D["dd_gauge"]["alt"].values()),
   f"age {PCC['age']} vs {_ageA}, cap {PCC['equity_cap']} vs {_capA}, stocks {PCC['stock_pct']} vs {_stk(wC)}")
_fC, _nC, _nCn, _shC = [], 0, {}, {}
for k in range(2, 6):
    for sup in itertools.combinations(sorted(_iC), k):
        for sp in _splits(100, k, 5, 100):
            w = [0] * NU
            for i_, x in zip(sup, sp): w[i_] = x
            if _stk(w) > _capA + 1e-9: continue
            _nC += 1; _nCn[k] = _nCn.get(k, 0) + 1
            rd, vd, dd_, r, v = figures(w, "net_macro")
            _shC[k] = max(_shC.get(k, -1e9), dd_)
            ddr = max((pk(w) * v - MU * r) * SC, 0.0)
            if ddr > CAP + 1e-9 or abs(dd_) > CAP + 1e-9: continue
            _fC.append((rd, abs(dd_), ddr, w, k))
_winC, _bC = _pickD(_fC)
ck(f"C is the rule's pick on the 1/3/5/10-year view, re-run over all {_nC} of its mixes ({len(_fC)} feasible, {len(_bC)} at the best CAGR)",
   _winC[3] == wC and len(_fC) == PCC["n_feasible"] and len(_bC) == PCC["band_n"] and _nC == PCC["n_total"],
   f"{_winC[3]} ({len(_fC)}, {len(_bC)}, {_nC}) vs {wC} ({PCC['n_feasible']}, {PCC['band_n']}, {PCC['n_total']})")
_bcC = {b_["n"]: b_ for b_ in PCC["by_count"]}
_cc_ok, _cc_bad = sorted(_bcC) == [2, 3, 4, 5], []
for n_ in range(2, 6):
    rows_ = [x for x in _fC if x[4] == n_]; b_ = _bcC.get(n_, {})
    ok_ = b_.get("n_total") == _nCn.get(n_) and b_.get("n_feasible") == len(rows_) and b_.get("shallowest") == _shC.get(n_)
    if rows_:
        (r_, d_, _, w_, _), _ = _pickD(rows_)
        ok_ = ok_ and b_.get("weights") == w_ and b_.get("cagr") == r_ and abs(b_.get("maxdd", 0)) == d_
    else:
        ok_ = ok_ and "weights" not in b_ and abs(_shC.get(n_, 0)) > CAP + 1e-9
    if not ok_: _cc_ok = False; _cc_bad.append(n_)
ck("C: each count's best (two to five funds) re-derives, and C's count is the best of them",
   _cc_ok and max((b_ for b_ in PCC["by_count"] if b_["n_feasible"]), key=lambda b_: (b_["cagr"], -abs(b_["maxdd"]), -b_["n"]))["n"] == nC,
   f"counts off: {_cc_bad}")

# INCOME, TRAILING 12 MONTHS (v126, owner 2026-11-23: "Add each portfolio their annual dividend pay out ttm"). Every
# admitted fund has a payout record - a payer its frequency, its target's trailing-12-month yield and the sources, a
# non-payer none - and each portfolio's income is re-derived here from its weights, the records and each fund's
# trust fee: the yield at the targets' rates and net of the fee, the pesos a year on P1,000,000, the monthly and
# quarterly payments, and the share in funds that pay nothing. Whole pesos half-up, yields to two places half-up.
FPAY = D["fund_payout"]
_feeA = {f["id"]: f["fee_feeder"] for f in D["funds"] + PBB["funds"]}
_paysA = [f for f in IDS if FPAY[f]["freq"]]
ck("every admitted fund has a payout record; each payer a frequency, a trailing-12-month yield and sources, each non-payer none",
   sorted(FPAY) == sorted(IDS) and all(FPAY[f]["freq"] in ("monthly", "quarterly") and 0 < FPAY[f]["ttm"] < 20
                                       and FPAY[f]["ttm_sources"] for f in _paysA)
   and all(FPAY[f]["freq"] is None and FPAY[f]["ttm"] == 0 for f in IDS if f not in _paysA)
   and sorted(PCC["funds"]) == sorted(_paysA + ["ATRPHMM"]) and D["payout_ttm_date"] <= D["review_date"],
   f"{_paysA}")
_h0 = lambda x: int(Decimal(repr(x)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
_h2 = lambda x: float(Decimal(repr(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
_inc_bad = []
for lab_, Q in (("A", PAA), ("B", PBB), ("C", PCC), ("D", PDD)):
    g_ = n_ = mo_ = qu_ = 0.0; none_ = 0; rows_ = []
    for f, x in zip(IDS, Q["weights"]):
        if not x: continue
        if not FPAY[f]["freq"]: none_ += x; continue
        t_ = FPAY[f]["ttm"]; nt_ = _h2(max(t_ - _feeA[f], 0.0))
        rows_.append({"id": f, "w": x, "freq": FPAY[f]["freq"], "ttm": t_, "net": nt_, "per_1m": _h0(x * t_ * 100)})
        g_ += x * t_; n_ += x * nt_
        if FPAY[f]["freq"] == "monthly": mo_ += x * t_ * 100
        else: qu_ += x * t_ * 100
    want = {"ttm_pct": _h2(g_ / 100), "net_pct": _h2(n_ / 100), "per_1m": _h0(g_ * 100), "per_1m_net": _h0(n_ * 100),
            "monthly_1m": _h0(mo_ / 12), "quarterly_1m": _h0(qu_ / 4), "no_payout_w": none_, "funds": rows_}
    if {k: Q["income"].get(k) for k in want} != want: _inc_bad.append((lab_, {k: (Q["income"].get(k), v) for k, v in want.items() if Q["income"].get(k) != v}))
ck("each portfolio's trailing-12-month income re-derives from its weights, the payout records and the trust fees",
   not _inc_bad, f"{str(_inc_bad)[:220]}")
# v129 (owner 2026-11-23: "Update dividend payout 12 ttm vs dividend payout 1yr past in all 4 portfolios not the past
# 1yr return"): each portfolio's payout a year earlier re-derived from its funds' prior-year rates, with its pesos, the
# change from it and the weight whose prior year is assumed; v127's 1-year return fields are gone.
_pr_bad = []
for lab_, Q in (("A", PAA), ("B", PBB), ("C", PCC), ("D", PDD)):
    I_ = Q["income"]; miss_ = [f for f, x in zip(IDS, Q["weights"]) if x and FPAY[f]["prior"] is None]
    pg_ = None if miss_ else sum(x * FPAY[f]["prior"] for f, x in zip(IDS, Q["weights"]) if x)
    want_ = (miss_, None if pg_ is None else _h2(pg_ / 100), None if pg_ is None else _h0(pg_ * 100),
             None if pg_ is None else _h2(I_["ttm_pct"] - _h2(pg_ / 100)),
             sum(x for f, x in zip(IDS, Q["weights"]) if x and FPAY[f].get("prior_assumed")))
    got_ = (I_["prior_missing"], I_["prior_pct"], I_["prior_per_1m"], I_["change_pp"], I_["prior_assumed_w"])
    if got_ != want_ or any(k.startswith("ret_1y") for k in I_): _pr_bad.append((lab_, got_, want_))
# v130 (owner 2026-11-23: "dividend payout 12 ttm vs dividend payout 1yr forecast"; "Make it vs"): each portfolio's
# next 12 months at its funds' latest annualised rates, its pesos and the change from the last 12 months
_fw_bad = []
for lab_, Q in (("A", PAA), ("B", PBB), ("C", PCC), ("D", PDD)):
    I_ = Q["income"]; miss_ = [f for f, x in zip(IDS, Q["weights"]) if x and FPAY[f]["fwd"] is None]
    fg_ = None if miss_ else sum(x * FPAY[f]["fwd"] for f, x in zip(IDS, Q["weights"]) if x)
    want_ = (miss_, None if fg_ is None else _h2(fg_ / 100), None if fg_ is None else _h0(fg_ * 100),
             None if fg_ is None else _h2(_h2(fg_ / 100) - I_["ttm_pct"]))
    got_ = (I_["fwd_missing"], I_["fwd_pct"], I_["fwd_per_1m"], I_["fwd_change_pp"])
    if got_ != want_: _fw_bad.append((lab_, got_, want_))
ck("each portfolio's next 12 months at the latest rates re-derives from its funds, with the change from the last 12 months",
   all("fwd" in FPAY[f] and (FPAY[f]["fwd"] == 0 if not FPAY[f]["freq"] else FPAY[f]["fwd_sources"]) for f in IDS)
   and D["payout_fwd_basis"] and not _fw_bad, f"{_fw_bad[:2]}")
ck("each portfolio's payout a year earlier re-derives from its funds' prior-year rates, with the change and the assumed share",
   all("prior" in FPAY[f] and (FPAY[f]["prior"] == 0 if not FPAY[f]["freq"] else FPAY[f]["prior_sources"]) for f in IDS)
   and "fund_1y" not in D and not _pr_bad, f"{_pr_bad[:2]}")

# ---------------------------------------------------------------------------
sec("D. THE MACRO GAUGE, THE DRIVER PATHS AND THE REGIONS")
DR = D["drivers"]; HZ = D["hz_weights"]
ck("driver weights sum to 1", abs(sum(x["weight"] for x in DR) - 1) < 1e-9)
ck("horizon weights sum to 1 and are each view's share of ten years", abs(sum(HZ.values()) - 1) < 1e-9
   and HZ == {"3Y": 0.3, "5Y": 0.2, "10Y": 0.5}, f"{HZ}")
for x in DR:
    ck(f"{x['name']}: scored on 1-5 at 2dp, nothing published on the retired 1-10 scale (v119)",
       1 <= x["score"] <= 5 and round(x["score"], 2) == x["score"]
       and not any(k.endswith("_10") or k in ("path_5", "blend_5") for k in x), f"{x['score']} {sorted(x)}")
    ck(f"{x['name']}: its path runs from now toward neutral, never past it, and its blend is that path at the horizon weights",
       all(min(x["score"], 3.0) - 1e-9 <= x["path"][h] <= max(x["score"], 3.0) + 1e-9 for h in ("3Y", "5Y"))
       and x["path"]["10Y"] == 3.0 and x["blend"] == wavg2((w, x["path"][h]) for h, w in HZ.items()),
       f"{x['score']} -> {x['path']} / {x['blend']}")
g5 = wavg2((x["weight"], x["score"]) for x in DR)
ck("the gauge is the weighted driver scores, exact and half-up, and the drivers' scale is 1-5 with 3 neutral",
   D["gauge"] == g5 and not any(k.startswith("gauge") and k.endswith("_10") for k in D)
   and D["driver_scale"] == {"min": 1, "max": 5, "neutral": 3.0} and D["driver_tilt_cal"]["neutral"] == 3.0,
   f"{D['gauge']} vs {g5}")
for h in ("3Y", "5Y", "10Y"):
    gp = wavg2((x["weight"], x["path"][h]) for x in DR)
    ck(f"the {h} gauge is the weighted {h} paths", D["gauge_path"][h] == gp, f"{gp}")
for rk, r in D["regions"].items():
    ck(f"{rk}: scored on 1-5 at 2dp, nothing published on the retired 1-10 scale (v120), the blend the horizon-weighted average",
       all(1 <= r[h] <= 5 and round(r[h], 2) == r[h] for h in list(HZ) + ["1Y"]) and not any(k.endswith("_10") for k in r)
       and abs(r["blend"] - round(sum(r[h] * w for h, w in HZ.items()), 2)) < 0.006, f"{r['blend']} {sorted(r)}")
# v110: THE YEAR-1 RESEARCH IS AS NEW AS THE DATA. Its own date (y1_date), not the owner's rule date
# the engine compared until v110, is on or after the as-of date and no later than the review.
ck("the year-1 and six-month readings were researched on or after the data date, by this review",
   AS_OF <= d(D["dd_gauge"]["y1_date"]) <= REV and AS_OF <= d(D["dd_gauge"]["m6_date"]) <= REV,
   f"{D['dd_gauge']['y1_date']} / {D['dd_gauge']['m6_date']} vs {AS_OF} / {REV}")
# v110: A TRAILING RETURN IS UNDER 75 DAYS OLD, OR FLAGGED STALE WITH ITS DATE PRINTED BESIDE IT (and under
# 105 days); a flag on a fresh series is itself an error.
_tsl = D["trend"]["sleeves"]
_tage = lambda x: (AS_OF - d(x)).days
_tdl = lambda x: f"{d(x).day} {d(x):%b %Y}"
ck("every dated trailing return is under 75 days old, or flagged stale with its date shown and under 105",
   all(0 <= _tage(x) <= 75 or (v.get("trail_stale") and _tage(x) <= 105 and _tdl(x) in v["trail_source"])
       for v in _tsl.values() for x in v["trail_date"].values() if x)
   and all(not v.get("trail_stale") or any(_tage(x) > 75 for x in v["trail_date"].values() if x) for v in _tsl.values()),
   f"{[(k, v['trail_date'], v.get('trail_stale')) for k, v in _tsl.items()]}")
# v108 (owner, 16 Nov): each region reads year 1 (researched) and years 2-3 (implied by its 3-year score,
# the average of years 1-3); the path runs monotone to years 4-5, and the four printed spans at
# 10/20/20/50 give the published blend, so no year counts twice. The note states both readings.
def _sc(x):
    t = f"{x:.3f}".rstrip("0")
    return t + "0" if t.endswith(".") else t
for rk, r in D["regions"].items():
    _y23r = round((3 * r["3Y"] - r["1Y"]) / 2, 3)
    ck(f"{rk}: years 2-3 implied by the 3-year score and between year 1 and years 4-5, the four spans give the blend, the note states them",
       r["Y23"] == _y23r and min(r["1Y"], r["5Y"]) <= _y23r <= max(r["1Y"], r["5Y"])
       and r["blend"] == round(0.1 * r["1Y"] + 0.2 * r["Y23"] + 0.2 * r["5Y"] + 0.5 * r["10Y"], 2)
       and f": {_sc(r['1Y'])}, " in r["y1_why"] and f"the three-year {_sc(r['3Y'])}; years 2-3 read {_sc(_y23r)}" in r["y1_why"],
       f"{r['1Y']} / {_y23r} / {r['5Y']} -> {r['blend']}")
G = D["dd_gauge"]; band = [b for b in G["bands"] if b["lo"] <= G["value"] < b["hi"] or (b["hi"] == 5 and G["value"] == 5)]
ck("the drawdown gauge's bands tile 1-5 and its value sits in the band it reports",
   G["bands"][0]["lo"] == 1 and G["bands"][-1]["hi"] == 5 and all(a["hi"] == b["lo"] for a, b in zip(G["bands"], G["bands"][1:]))
   and len(band) == 1 and band[0] == G["band"], f"{G['value']} in {G['band']}")
# THE BAND IS THE OWNER'S (v105, 2026-11-16: "Wider the band of budget drawdown to 20-30%"; re-scaled
# v109, 2026-11-16: "Okay update it to best and recommended"): one-point steps from 20% to 30%, the 25%
# base held from 2.80 to 3.20, every inner step 0.15 wide, the end steps taking the rest of 1-5 -
# re-derived here from those facts, not read back from the engine's list.
_base = D["dd_budget"]["base"]; _nd, _nu = int(_base - 20), int(30 - _base)
_exp = ([(1.0 if i == 0 else round(2.8 - (_nd - i) * 0.15, 2), round(2.8 - (_nd - 1 - i) * 0.15, 2), 20.0 + i) for i in range(_nd)]
        + [(2.8, 3.2, _base)]
        + [(round(3.2 + i * 0.15, 2), 5.0 if i == _nu - 1 else round(3.2 + (i + 1) * 0.15, 2), _base + 1 + i) for i in range(_nu)])
ck("the budget band is the owner's 20-30%: one-point steps, the 25% base held from 2.80 to 3.20, 0.15 a step",
   [(b["lo"], b["hi"], b["cap"]) for b in G["bands"]] == _exp
   and all(b["action"].endswith(f"{b['cap']:.0f}%") for b in G["bands"])
   and sorted(float(c) for c in G["alt"]) == [float(c) for c in range(20, 31)],
   f"{[(b['lo'], b['hi'], b['cap']) for b in G['bands']]}")
# THE GAUGE RE-DERIVED (v90). Until v90 the audit checked only the bands and the budget, not
# the readings - and its budget check took the band's step as the budget, which would have
# failed falsely the first time a new band was read before two month-end reviews.
# v103 (owner, 15 Nov 2026): the gauge reads year 1, years 2-3 and years 4-5, each weighted by
# the share of the first five years it covers. Re-derived here from the drivers' own paths and
# year-1 scores and from each trend sleeve's z-scores - nothing is read back from the parts.
# v112 (owner, 17 Nov 2026): year 1 split into months 1-6 (researched) and 7-12 (implied), 10/10/40/40;
# the 10-year view shown as the anchor, neutral, and not weighted.
_sp = G["spans"]; _wv = {h: round((b - a) / 5.0, 2) for h, (a, b) in _sp.items()}
ck("the budget gauge's spans tile years 0-5 and each weighs its share of them (months 1-6 10%, 7-12 10%, years 2-3 40%, 4-5 40%)",
   G["views"] == ["6M", "12M", "3Y", "5Y"] and list(_sp) == G["views"] and _sp["6M"] == [0.0, 0.5]
   and _sp["12M"] == [0.5, 1.0] and _sp["5Y"][1] == 5
   and all(_sp[a][1] == _sp[b][0] for a, b in zip(G["views"], G["views"][1:]))
   and G["w"] == _wv == {"6M": 0.1, "12M": 0.1, "3Y": 0.4, "5Y": 0.4}, f"{_sp} {G['w']}")
_GD = {r["name"]: r for r in G["drivers"]}
ck("the year-1 table lists the seven drivers at their weights, now as the published score, years 4-5 as the 5-year path",
   [x["name"] for x in DR] == list(_GD)
   and all(_GD[x["name"]]["weight"] == x["weight"] and _GD[x["name"]]["now"] == x["score"]
           and _GD[x["name"]]["y45"] == x["path"]["5Y"] and _GD[x["name"]]["y3_avg"] == x["path"]["3Y"]
           and 1 <= _GD[x["name"]]["y1"] <= 5 and len(_GD[x["name"]]["why"]) > 60 for x in DR), f"{list(_GD)}")
_y23 = {x["name"]: round((3 * x["path"]["3Y"] - _GD[x["name"]]["y1"]) / 2, 3) for x in DR}
ck("years 2-3 are what the 3-year path leaves once year 1 is taken out, so year 1 is not counted twice",
   all(abs(_GD[n]["y23"] - v) < 1e-9 and 1 <= v <= 5 for n, v in _y23.items()), f"{ {n: (_GD[n]['y23'], v) for n, v in _y23.items()} }")
_m712 = {x["name"]: round(2 * _GD[x["name"]]["y1"] - _GD[x["name"]]["m6"], 3) for x in DR}
_tw = lambda xs: all((a - 3.0) * (b - 3.0) >= 0 and abs(b - 3.0) <= abs(a - 3.0) + 1e-9 for a, b in zip(xs, xs[1:]))
ck("months 7-12 are what year 1 leaves once months 1-6 are taken out, and every path runs from now toward neutral through them",
   all(abs(_GD[n]["m712"] - v) < 1e-9 and 1 <= _GD[n]["m6"] <= 5 and len(_GD[n]["why_m6"]) > 60
       and _tw([_GD[n]["now"], _GD[n]["m6"], v, _GD[n]["y23"], _GD[n]["y45"], 3.0]) for n, v in _m712.items()),
   f"{ {n: (_GD[n]['m6'], _GD[n]['m712'], v) for n, v in _m712.items()} }")
# v106 (owner, 16 Nov): valuation is its own part, so the macro part is the other six drivers,
# their weights scaled to one - re-derived here from the drivers' own weights and paths.
_VALN = "Valuation support"; _DR6 = [x for x in DR if x["name"] != _VALN]; _W6 = sum(x["weight"] for x in _DR6)
_xv = next(x for x in DR if x["name"] == _VALN)
_mac = {"6M": hu2(sum(x["weight"] * _GD[x["name"]]["m6"] for x in _DR6) / _W6),
        "12M": hu2(sum(x["weight"] * _m712[x["name"]] for x in _DR6) / _W6),
        "3Y": hu2(sum(x["weight"] * _y23[x["name"]] for x in _DR6) / _W6),
        "5Y": hu2(sum(x["weight"] * x["path"]["5Y"] for x in _DR6) / _W6)}
_vlp = {"6M": hu2(_GD[_VALN]["m6"]), "12M": hu2(_m712[_VALN]), "3Y": hu2(_y23[_VALN]), "5Y": hu2(_xv["path"]["5Y"])}
_mac1 = hu2(sum(x["weight"] * _GD[x["name"]]["y1"] for x in _DR6) / _W6); _vlp1 = hu2(_GD[_VALN]["y1"])
_TR = D["trend"]; _ov = lambda a, b, c, e: max(0.0, min(b, e) - max(a, c))
def _tsp(v, a, b):
    wm = _ov(a, b, *_TR["mom_years"]) / (b - a); wr = _ov(a, b, *_TR["rev_years"]) / (b - a)
    return round(min(5.0, max(1.0, 3.0 + wm * v["z"]["1Y"] - wr * _TR["reversal"] * v["z_rev"])), 2)
# v112: months 1-6 are the half-year momentum - the last two quarters compounded, as a z in the sleeve's
# own drift and volatility - and months 7-12 what year 1's momentum leaves once they are taken out.
def _z6(v):
    q = v["quarters"]; ks = list(q)[-2:]; r = 1.0
    for k in ks: r *= 1 + q[k] / 100
    r = round((r - 1) * 100, 2)
    return r, round((math.log(1 + r / 100) - 0.5 * math.log(1 + v["mu"] / 100)) / (v["sigma"] / 100 * math.sqrt(0.5)), 2)
_cl = lambda x: round(min(5.0, max(1.0, x)), 2)
_ty1 = {f: _tsp(v, 0.0, 1.0) for f, v in _TR["sleeves"].items()}
_t6 = {f: _cl(3.0 + _z6(v)[1]) for f, v in _TR["sleeves"].items()}
_ts = {"6M": _t6, "12M": {f: _cl(2 * _ty1[f] - _t6[f]) for f in _t6}}
_ts.update({h: {f: _tsp(v, *_sp[h]) for f, v in _TR["sleeves"].items()} for h in ("3Y", "5Y")})
ck("each market's trend in each span: half-year momentum for months 1-6, the rest of year 1's momentum for 7-12, reversal after; years 4-5 equal its 5-year score",
   G["trend_spans"] == _ts and G["trend_y1"] == _ty1
   and all(G["trend_6m"][f]["ret"] == _z6(v)[0] and G["trend_6m"][f]["z"] == _z6(v)[1] for f, v in _TR["sleeves"].items())
   and all(_ts["5Y"][f] == v["score"]["5Y"] for f, v in _TR["sleeves"].items()), f"{G['trend_spans']} vs {_ts}")
_trp = {h: round(sum(_ts[h].values()) / len(_ts[h]), 2) for h in _sp}
_trp["1Y"] = round(sum(_ty1.values()) / len(_ty1), 2)
# v108: THE FOUR ANALYSES, YEAR BY YEAR, re-derived cell by cell from their own inputs: the regions'
# spans, the two tilt drivers' year 1 / implied years 2-3 / paths, the five markets' trend spans and the
# valuation path; A reads the last span, B and D all four at 10/20/20/50, each the blend the forecasts use.
# v109: THE GAUGE'S REACH re-derived from each stylized case's own inputs - the six-driver macro part,
# the trend's momentum then reversal, the valuation path, each span stepped back toward neutral - and
# the band it lands in. The band is sized to it: the worst case reaches 20%, the best 29% or more, and
# a strong but expensive boom raises nothing.
def _rch(c):
    sp = []
    for i, w in enumerate((0.1, 0.1, 0.4, 0.4)):
        v = {n: x + c["back"][i] * (3.0 - x) for n, x in c["drivers"].items()}
        sp.append(w * (hu2(sum(x["weight"] * v[x["name"]] for x in _DR6) / _W6)
                       + (c["momentum"] if i < 2 else c["reversal"]) + hu2(v[_VALN])) / 3)
    return round(sum(sp), 2)
_bcap = lambda g: next(b["cap"] for b in G["bands"] if b["lo"] <= g < b["hi"] or (b["hi"] == 5 and g == 5))
_RC = {c["name"]: c for c in G["reach"]}
ck("the band fits the gauge's reach: each stylized case re-derived and banded; worst 20%, best 29%+, an expensive boom no raise",
   all(_rch(c) == c["value"] and _bcap(c["value"]) == c["cap"] and c["back"] == [0.0, 0.0, 0.6, 0.85] for c in G["reach"])
   # and where each landed on the v105-v108 steps the page quotes (hold 2.50-3.50, 0.30 a step)
   and G["hold_v105"] == [2.5, 3.5] and G["step_w_v105"] == 0.3
   and all(c["cap_v105"] == (20 + min(4, int((c["value"] - 1) / 0.3 + 1e-9)) if c["value"] < 2.5 else 25 if c["value"] < 3.5
                             else 26 + min(4, int((c["value"] - 3.5) / 0.3 + 1e-9))) for c in G["reach"])
   and _RC["Every input at its worst"]["cap"] == 20.0 and _RC["Every input at its best"]["cap"] >= 29.0
   and _RC["A strong but expensive boom, 2021-like"]["cap"] <= _base,
   f"{[(c['name'][:12], c['value'], _rch(c), c['cap']) for c in G['reach']]}")
_AB = D["analyses_by_year"]; _abw = [0.1, 0.2, 0.2, 0.5]
_DRn = {x["name"]: x for x in DR}
_drow = lambda n: [_GD[n]["y1"], hu2(_y23[n]), _DRn[n]["path"]["5Y"], _DRn[n]["path"]["10Y"]]
_abx = ([("Regional ranking", [r["1Y"], r["Y23"], r["5Y"], r["10Y"]], r["blend"]) for r in D["regions"].values()]
        + [("Macro sentiment", _drow(n), wavg2((w, _DRn[n]["path"][h]) for h, w in HZ.items()))
           for n in ("Monetary policy & liquidity", "Geopolitics & energy")]
        + [("Market trend", [_trp["1Y"], _trp["3Y"], _trp["5Y"], 3.0],
            sum(v["blend"] for v in _TR["sleeves"].values()) / len(_TR["sleeves"]))]
        + [("Market valuation", [_vlp1, _vlp["3Y"], _vlp["5Y"], _xv["path"]["10Y"]], D["val_channel"]["blend_5"])])
ck("the four analyses year by year: every cell from its inputs, A on years 6-10 alone, B and D at 10/20/20/50, each row its forecasts' blend",
   len(_AB["rows"]) == len(_abx) and _AB["w_bd"] == _abw and _AB["w_a"] == [0.0, 0.0, 0.0, 1.0]
   and all(r["analysis"] == an and r["v"] == v and r["a"] == v[-1]
           and r["bd"] == round(sum(w * x for w, x in zip(_abw, v)), 2) and abs(r["bd"] - bl) < 0.0101
           for r, (an, v, bl) in zip(_AB["rows"], _abx)),
   f"{[(r['name'], r['v'], r['bd']) for r in _AB['rows']]} vs {_abx}")
# v112 (owner, 17 Nov): the gauge reads months 1-6 and 7-12, years 2-3 and 4-5; the 10-year anchor is in
# its parts, neutral on every part, and carries no weight (v107-v111 left it out altogether)
from decimal import Decimal as _D, ROUND_HALF_UP as _HU
_q2 = lambda x: float(x.quantize(_D("0.01"), rounding=_HU))      # exact half-up, the page's convention
_rd = {h: _q2((_D(str(_mac[h])) + _D(str(_trp[h])) + _D(str(_vlp[h]))) / 3) for h in _mac}
ck("each budget-gauge view reads the mean of macro (six drivers), trend and valuation over its span - volatility not in it",
   G["reading_of"] == ["macro", "trend", "valuation"] and list(G["parts"]) == ["6M", "12M", "3Y", "5Y", "10Y"]
   and G["anchor"] == "10Y" and "10Y" not in G["w"]
   and all(G["parts"]["10Y"][k] == 3.0 for k in ("macro", "trend", "valuation", "reading"))
   and all(G["parts"][h]["macro"] == _mac[h] and G["parts"][h]["trend"] == _trp[h]
           and G["parts"][h]["valuation"] == _vlp[h]
           and G["parts"][h]["reading"] == _rd[h] and "vol" not in G["parts"][h] for h in _mac),
   f"{ {h: (G['parts'][h]['macro'], G['parts'][h]['trend'], G['parts'][h]['valuation'], G['parts'][h]['reading']) for h in G['parts']} } vs {_mac} {_trp} {_vlp} {_rd}")
_val = _q2(sum(_D(str(_rd[h])) * _D(str(_wv[h])) for h in G["views"]))
ck(f"the budget gauge is the months 1-6, 7-12, years 2-3 and 4-5 readings weighted by their share of the first five years ({_val})",
   G["value"] == _val, f"{G['value']} vs {_val}")
# v112: the halves cannot move the reading - months 7-12 are implied from year 1 - so year 1 read whole at
# 20% (the v103-v111 rule) lands within a rounding step of it.
_rd1 = _q2((_D(str(_mac1)) + _D(str(_trp["1Y"])) + _D(str(_vlp1))) / 3)
_v111 = _q2(_D(str(_rd1)) * _D("0.2") + _D(str(_rd["3Y"])) * _D("0.4") + _D(str(_rd["5Y"])) * _D("0.4"))
ck(f"splitting year 1 into months 1-6 and 7-12 leaves the gauge where year 1 whole reads it, to rounding ({_v111})",
   abs(G["value"] - _v111) <= 0.011 and G["value_v111"] == _v111, f"{G['value']} vs {_v111} / {G['value_v111']}")
# The split must not move the gauge beyond rounding: the old 3- and 5-year rule (60/40 on the
# 3-year average and years 4-5) read from the same inputs.
_old3 = _q2((_D(str(hu2(sum(x["weight"] * x["path"]["3Y"] for x in _DR6) / _W6)))
             + _D(str(round(sum(v["score"]["3Y"] for v in _TR["sleeves"].values()) / len(_TR["sleeves"]), 2)))
             + _D(str(hu2(_xv["path"]["3Y"])))) / 3)
_old = _q2(_D(str(_old3)) * _D("0.6") + _D(str(_rd["5Y"])) * _D("0.4"))
ck(f"splitting year 1 out leaves the gauge where the 3- and 5-year rule reads it, to rounding ({_old})",
   abs(G["value"] - _old) <= 0.011, f"{G['value']} vs {_old}")
_me = lambda x: (d(x) + dt.timedelta(days=1)).day == 1
ck("every month-end review on record is a month-end before the data date, read on 1-5",
   all(_me(r[0]) and d(r[0]) < AS_OF and 1 <= r[1] <= 5 for r in G["reviews"]), f"{G['reviews']}")
_bof = lambda v: next(b for b in G["bands"] if b["lo"] <= v < b["hi"] or (b["hi"] == 5 and v == 5))
_base = D["dd_budget"]["base"]; _gz = {g["name"]: g for g in G["guards"]}
_geo = next(x["score"] for x in DR if x["name"].startswith("Geopolitics"))
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
   D["dd_budget"]["cap"] == G["recommended_cap"] == _rec and all(P["dd_cap"] == CAP == _rec for P in (PAA, PBB, PCC, PDD)),
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
   (M["us_umich_latest_final"] is True or (REV - d(M["us_umich_latest_date"])).days < 14)
   and (REV - d(M["us_umich_latest_date"])).days <= 21)
# v113: a US company's results after New York's close (Nvidia's) are a US-session event too; with Asia
# rolled a day ahead of New York, they were compared with Seoul's date.
_US = re.compile(r"^(Fed decision|FOMC\b|Nvidia\b|US .*\b(GDP|PCE|CPI|PPI|payrolls|jobs report|retail sales|midterm))")
# v122: the engine read "Fed decision" alone against the US clock and the 25 Nov PCE against Asia's; this pattern
# missed "Fed decision". Each catalyst now publishes its clock, and it must be the one this pattern gives.
ck("each catalyst's clock is its own market's: US releases and the Fed against the US session, the rest against the data date",
   all(c.get("clock") == ("us" if _US.search(c["what"]) else "as_of") for c in D["catalysts"]),
   f"{[(c['what'][:24], c.get('clock')) for c in D['catalysts']]}")
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
# BRENT ON THE WEEK (v95): against the same contract's settle seven days earlier - the history's own
# when no roll falls in the week, the new contract's recorded roll prior when the week-ago day was the
# old contract's last, and nothing otherwise - read from the roll record, not the engine's calendar.
_wkd = (d(M["brent_date"]) - dt.timedelta(days=7)).isoformat()
_bhd = dict(bh); _nx = next((x for x, _ in bh if x > _wkd), None)
_rolls = [r for r in M["brent_roll_priors"] if _wkd < r <= M["brent_date"]]
_wb = (_bhd.get(_wkd) if not _rolls else M["brent_roll_priors"][_nx] if _rolls == [_nx] and _wkd in _bhd else None)
_wq = None if _wb is None else round((M["brent"] / _wb - 1) * 100, 1)
ck("Brent's weekly change is against the same contract a week earlier, and the inflation note quotes it",
   M["brent_wk_chg_pct"] == _wq and (_wq is None or f"{abs(_wq)}% " in next(x["note"] for x in DR if x["name"].startswith("Inflation"))),
   f"{M['brent_wk_chg_pct']} vs {_wq} (base {_wb})")
_ann = d(M["brent_date"]).replace(year=d(M["brent_date"]).year - 1)
# v93: past the bound the base may stand only with its own date beside every quote of the y/y,
# re-read here from the published prose (not from the engine's flag alone).
_yb = d(M["brent_yr_ago_date"]); _yg = abs((_ann - _yb).days); _ybt = f"{_yb.day} {_yb:%b} {_yb.year}"
_yq = [t for t in [x["note"] for x in DR] + [x["summary"] for x in DR]
       + [r["why"] for r in D["regions"].values()] + [r["summary"] for r in D["regions"].values()]
       if f"{M['brent_yoy_1dp']:.1f}%" in t]   # the one-decimal quote the page prints (v94)
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
# v95: THE REAL-YIELD CARD reads the newest PH CPI on record (it read September's for two days after
# October's was out) and spans all three T-bill tenors.
_MO = "jan feb mar apr may jun jul aug sep oct nov dec".split(); _am = d(D["as_of"]).month
_lk = min((k for k in M if re.fullmatch(r"ph_cpi_(" + "|".join(_MO) + ")", k)), key=lambda k: (_am - (_MO.index(k[7:]) + 1)) % 12 or 12)
_RY = D["real_yield"]; _tbs = [M["ph_tbill_91"], M["ph_tbill_182"], M["ph_tbill_364"]]
ck("the real-yield card reads the newest PH CPI on record, against every T-bill tenor",
   _RY["cpi"] == M[_lk] and _RY["month"].lower().startswith(_lk[7:]) and _RY["lo"] == min(_tbs) and _RY["hi"] == max(_tbs)
   and abs(_RY["ry_lo"] - (min(_tbs) - M[_lk])) < 0.006 and abs(_RY["ry_hi"] - (max(_tbs) - M[_lk])) < 0.006,
   f"{_RY} vs {_lk}")
# v95: an f-string split across two literals dropped the second one's f, and the monetary note printed
# "{_dday('ust_10y_peak_date')}". Every string in the payload is scanned, not only the prose above.
STRS = []
def walk_s(o, p_=""):
    if isinstance(o, str): STRS.append((p_, o))
    elif isinstance(o, dict): [walk_s(v, p_ + "." + str(k)) for k, v in o.items()]
    elif isinstance(o, list): [walk_s(v, p_) for v in o]
walk_s(D)
_br = [(p_, m.group(0)) for p_, t in STRS for m in re.finditer(r"\{[^{}\s][^{}]{0,79}\}", t)]
ck(f"no string in the payload carries an unformatted placeholder ({len(STRS)} scanned)", not _br, f"{_br[:2]}")
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
_SERIES_OF = {"brent": "brent_history", "vix_latest": "vix_history"}
_bad = []
for lab, t in TXT:
    for sent in re.split(r"(?<=[.;])\s+", t):
        if not re.search(r"\b\d{1,2} " + MON + r"|\bthe \d{1,2}(?:st|nd|rd|th)\b", sent): continue
        for k, dk in _CLOSES.items():
            # v135: a three-decimal close (the peso's 63.675) is matched as printed, not at two decimals (63.67 is
            # 17 Nov's own close), and a close is a level, so a figure followed by "%" (FedWatch's 91.4%) is not one.
            forms = {f"{M[k]:.2f}", f"{M[k]:,.2f}"} if round(M[k], 2) == M[k] else {f"{M[k]}", f"{M[k]:,}"}
            if any(re.search(r"(?<![\d.,])" + re.escape(f_) + r"(?![\d%])", sent) for f_ in forms):
                # v118: a close its own dated series also carries on another day (Brent $92.57 on 9 Nov and
                # 20 Nov) is in its place beside that day too - re-read from the series, not the engine.
                _days = {d(M[dk]).day} | ({d(x_).day for x_, y_ in M[_SERIES_OF[k]] if y_ == M[k]} if k in _SERIES_OF else set())
                if not any(re.search(rf"\b{day} {MON}|\bthe {day}(?:st|nd|rd|th)\b", sent) for day in _days):
                    _bad.append((lab, k))
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
_SNAMES = sorted(set(_SER.values()))
def _owner(snt, pos):
    """The series named nearest before `pos` in the sentence, or None if none is."""
    best = max(((snt.rfind(nm, 0, pos), nm) for nm in _SNAMES), default=(-1, None))
    return best[1] if best[0] >= 0 else None
_dk, _dq = [], 0
_LATEST = {"KOSPI": (M["kospi_latest_chg_pct"], d(M["kospi_latest_date"])),
           "Nikkei": (M["nikkei_latest_chg_pct"], d(M["nikkei_latest_date"])),
           "Nasdaq": (M["nasdaq_chg_pct"], d(M["equity_date"])), "S&P": (M["spx_chg_pct"], d(M["equity_date"])),
           "Dow": (M["dow_chg_pct"], d(M["equity_date"])), "PSEi": (M["psei_chg_pct"], d(M["psei_date"]))}
# v113: EVERY DAY A SERIES SHARES A FIGURE WITH. The KOSPI fell 3.59% on 3 Nov and again on 16 Nov, both
# now keyed days, so "3.59% on 3 Nov" was flagged as 16 Nov's figure away from its day. A figure beside any
# day of its own series that carries that value is in its place.
_KEYED = {}
for k, v in M.items():
    m_ = re.match(r"^([a-z0-9]+?)_(\d{1,2})(" + "|".join(_MO) + r")(?:_|$)", k)
    if m_ and m_.group(1) in _SER and not isinstance(v, bool) and isinstance(v, (int, float)):
        _KEYED.setdefault(_SER[m_.group(1)], []).append((abs(v), int(m_.group(2)), m_.group(3).capitalize()))
for k, v in M.items():
    m_ = re.match(r"^([a-z0-9]+?)_(\d{1,2})(" + "|".join(_MO) + r")(?:_|$)", k)
    if not m_ or m_.group(1) not in _SER or isinstance(v, bool) or not isinstance(v, (int, float)): continue
    _day, _mo = int(m_.group(2)), m_.group(3).capitalize()
    for src, t in TXT:
        for snt in re.split(r"(?<=[.])\s+(?=[A-Z(])", t):
            if _SER[m_.group(1)] not in snt: continue
            # v98: THE NUMBER MUST BELONG TO THIS SERIES. On 10 Nov the S&P fell 0.38%, the Dow's move
            # of 3 Nov, and the sentence "the S&P fell 0.38% ... and the Dow fell 0.30%" was flagged for
            # quoting the Dow's 3 Nov figure away from its day. A figure is this key's when the series
            # named nearest before it is this key's series (or none is named before it).
            for f_ in {f"{abs(v):,.2f}", f"{abs(v):.2f}"}:
                hits = [h for h in re.finditer(r"(?<![\d.,])" + re.escape(f_) + r"(?!\d)", snt)
                        if _owner(snt, h.start()) in (None, _SER[m_.group(1)])]
                if hits: break
            else: continue
            _dq += 1
            # v110: "3 Nov" is not a date inside "13 Nov" (the test matched it until v110), and a figure the
            # LATEST session shares with an older day (the KOSPI fell 3.59% on 3 Nov and on 16 Nov) is the
            # latest session's own beside its own date.
            _onday = lambda dd, mm: re.search(r"(?<!\d)" + str(dd) + " " + mm, snt) or f"the {_ordn(dd)}" in snt
            _lt = _LATEST.get(_SER[m_.group(1)])
            if _lt and abs(abs(_lt[0]) - abs(v)) < 1e-9 and _onday(_lt[1].day, f"{_lt[1]:%b}"): continue
            if any(abs(a_ - abs(v)) < 1e-9 and _onday(dd_, mm_) for a_, dd_, mm_ in _KEYED.get(_SER[m_.group(1)], [])): continue
            if not _onday(_day, _mo): _dk.append(f"{k} in {src}")
ck(f"a figure keyed to a day is quoted only beside that day ({_dq} quotes)", _dq > 0 and not _dk, "; ".join(_dk[:3]))
# v94: a move kept under its own day's key (nasdaq_5nov_chg_pct) equals the series' latest move
# while that day is the latest session - re-read from the payload, not from the engine's verdict.
_LAT = {"spx": ("equity_date", "spx_chg_pct"), "nasdaq": ("equity_date", "nasdaq_chg_pct"),
        "dow": ("equity_date", "dow_chg_pct"), "kospi": ("kospi_latest_date", "kospi_latest_chg_pct"),
        "nikkei": ("nikkei_latest_date", "nikkei_latest_chg_pct"), "psei": ("psei_date", "psei_chg_pct")}
_dd = []
for k, v in M.items():
    m_ = re.match(r"^(spx|nasdaq|dow|kospi|nikkei|psei)_(\d{1,2})(" + "|".join(_MO) + r")_chg_pct$", k)
    if not m_: continue
    _l = d(M[_LAT[m_.group(1)][0]])
    if (_l.month, _l.day) == (_MO.index(m_.group(3)) + 1, int(m_.group(2))):
        _dd.append((k, v, M[_LAT[m_.group(1)][1]]))
ck(f"a day-keyed move on the series' latest day equals the latest move ({len(_dd)} keys)",
   all(v == w for _, v, w in _dd), f"{[x for x in _dd if x[1] != x[2]]}")
# v118: the same for a day-keyed CLOSE (spx_20nov, kospi_20nov), and each week's move re-derived from its two
# day-keyed closes - so the week stays the week to its own day after the roll, and a typo in either fails.
_LATC = {"spx": "spx_close", "nasdaq": "nasdaq_close", "dow": "dow_close", "kospi": "kospi_latest",
         "nikkei": "nikkei_latest", "psei": "psei"}
_dc = []
for k, v in M.items():
    m_ = re.match(r"^(spx|nasdaq|dow|kospi|nikkei|psei)_(\d{1,2})(" + "|".join(_MO) + r")$", k)
    if not m_: continue
    _l = d(M[_LAT[m_.group(1)][0]])
    if (_l.month, _l.day) == (_MO.index(m_.group(3)) + 1, int(m_.group(2))):
        _dc.append((k, v, M[_LATC[m_.group(1)]]))
_wk = []
for k, v in M.items():
    m_ = re.match(r"^(spx|nasdaq|dow|kospi|nikkei)_wk_(\d{1,2})(" + "|".join(_MO) + r")_pct$", k)
    if not m_: continue
    _end, _beg = M.get(f"{m_.group(1)}_{m_.group(2)}{m_.group(3)}"), M.get(f"{m_.group(1)}_{int(m_.group(2)) - 7}{m_.group(3)}")
    _wk.append((k, v, None if _end is None or _beg is None else round((_end / _beg - 1) * 100, 1)))
ck(f"a day-keyed close on the series' latest day equals the latest close, and each week's move re-derives "
   f"from its own two closes ({len(_dc)} closes, {len(_wk)} weeks)",
   all(v == w for _, v, w in _dc) and _wk and all(v == w for _, v, w in _wk),
   f"{[x for x in _dc if x[1] != x[2]]} {[x for x in _wk if x[1] != x[2]]}")
# v94: Brent's y/y at one decimal is the EXACT ratio rounded half-up - re-derived from the two
# settles, not read from the payload's own rounded figure (it printed 51.0% for 51.053%).
from decimal import Decimal as _D, ROUND_HALF_UP as _HU
_yx = ((_D(str(M["brent"])) / _D(str(M["brent_yr_ago"])) - 1) * 100).quantize(_D("0.1"), rounding=_HU)
_yqs = [float(x) for _, t in TXT for x in re.findall(r"Brent \+(\d+\.\d)% ", t)]
ck(f"every one-decimal Brent y/y quote is the exact ratio rounded half-up ({float(_yx)}%, {len(_yqs)} quotes)",
   bool(_yqs) and all(abs(v - float(_yx)) < 1e-9 for v in _yqs) and M.get("brent_yoy_1dp") == float(_yx), f"{_yqs}")
# v93: every fund's target-fund check is from this review, with a known status, and a charge
# marked confirmed is the charge the forecast carries.
_TCS = {"no target", "confirmed", "partly confirmed", "estimate", "unconfirmed", "disputed", "manager change",
        "mandate change"}
_tcf = D["funds"] + [x for x in D["portfolio_b"]["funds"] if x["id"] not in {y["id"] for y in D["funds"]}]
ck(f"every fund carries a target-fund check from this review, with a known status ({len(_tcf)} funds)",
   len(_tcf) == len(D["portfolio_b"]["ids"])
   and all(f_.get("target_check", {}).get("date") == D["review_date"] and f_["target_check"]["status"] in _TCS for f_ in _tcf),
   f"{[(f_['id'], f_.get('target_check', {}).get('date')) for f_ in _tcf if f_.get('target_check', {}).get('date') != D['review_date']][:2]}")
ck("a target charge marked confirmed is quoted at the charge the forecast carries",
   all(f"{f_['fee_target']:.2f}%" in f_["target_check"]["text"] for f_ in _tcf if f_["target_check"]["status"] == "confirmed"),
   f"{[f_['id'] for f_ in _tcf if f_['target_check']['status'] == 'confirmed']}")

# v98: derived figures the notes quote, re-derived here from their inputs (the engine is not imported).
_ALLF = D["funds"] + D["portfolio_b"]["funds"]
_f1 = M["feeder_1y"]
_fx = round(((1 + _f1["ATRGLDV"] / 100) / (1 + M["gldv_feeder_usd_1y"] / 100) - 1) * 100, 2)
_tp = round(((1 + M["gtec_target_1y"] / 100) * (1 + _fx / 100) - 1) * 100, 2)
_gtec = next(f for f in _ALLF if f["id"] == "ATRGTEC")
ck("the 1-year gap test re-derives: the dollar's implied move, the target in pesos, and a gap no wider than the trust fee plus half a point",
   abs(_fx - M["fx_1y_implied_pct"]) < 1e-9 and abs(_tp - M["gtec_target_1y_php"]) < 1e-9
   and abs(round(_tp - _f1["ATRGTEC"], 2) - M["gtec_gap_1y_pp"]) < 1e-9
   and 0 <= M["gtec_gap_1y_pp"] <= _gtec["fee_feeder"] + 0.5
   and f"a gap of {M['gtec_gap_1y_pp']} points" in _gtec["target_check"]["text"],
   f"{_fx} {_tp} {M['gtec_gap_1y_pp']}")
_over = abs(M["vix_latest"] / M["vix_spot"] - 1) * 100 > D["vol_channel"]["overtaken_pct"]
_vnote = next(x for x in D["drivers"] if x["name"].startswith("Volatility"))["note"]
ck("the curve is flagged overtaken, on the page and in the volatility note, exactly when the latest close is past the flag",
   D["vol_channel"]["overtaken"] == _over and ("OVERTAKEN" in _vnote) == _over
   and ("no longer overtaken" in _vnote) == (not _over), f"{_over}")
_pids = D["portfolio_a"]["ids"]
_none = [f for f in _ALLF if "none of A, B or D holds it" in f["target_check"]["text"]]
ck("a target check that says none of A, B or D holds its fund is true of all three",
   bool(_none) and all(D[k]["weights"][_pids.index(f["id"])] == 0
                       for f in _none for k in ("portfolio_a", "portfolio_b", "portfolio_c", "portfolio_d")),
   f"{[f['id'] for f in _none]}")

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
    # v117: AS A WHOLE NUMBER, not a substring - "5.4" sat inside a stale "5.47%" and passed the 30-year row.
    _num = lambda f_, h: re.search(r"(?<![\d.,])" + re.escape(f_) + r"(?![\d])", h)
    ck(f"the register's '{lab}' headline is the payload's {v}", cell is not None and any(any(_num(f_, h) for f_ in forms) for h in head[:1]),
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
# THE PUBLISHED VOLATILITY INPUTS ARE THE ONES USED (v107 cleanup): the covered-call factor the
# Funds tab prints is JEPQ's volatility over the index's, and the tech sleeve's regional mix sums to 1.
ck("the covered-call volatility factor is the published JEPQ / Nasdaq-100 ratio",
   D["cc_vol_factor"] == round(D["jepq_vol"] / D["ndx_vol"], 4) and 0 < D["jepq_beta"] <= 1,
   f"{D['cc_vol_factor']} vs {D['jepq_vol']}/{D['ndx_vol']}")
ck("the tech sleeve's regional mix sums to 1", abs(sum(D["acwi_it_mix"].values()) - 1) < 1e-9, f"{D['acwi_it_mix']}")
# THE VERB IS THE MOVE (v95): each driver's note and summary open with HELD, RAISED or CUT, and that
# word must be what its score did against the last review's score the payload records.
_vw = lambda t: (re.match(r"(HELD|RAISED|CUT)\b", t.upper()) or [None, None])[1]
_vexp = lambda x: "HELD" if x["score"] == x["prev_score"] else "RAISED" if x["score"] > x["prev_score"] else "CUT"
_vbad = [x["name"] for x in D["drivers"] if "prev_score" not in x or _vw(x["note"]) != _vexp(x) or _vw(x["summary"]) != _vexp(x)]
ck("each driver's note and summary open with the move its score made since the last review", not _vbad, f"{_vbad}")
try:
    ref = os.environ.get("BASELINE_REF", "HEAD")
    _bfull = json.loads(subprocess.run(["git", "-C", ROOT if os.path.isdir(os.path.join(ROOT, ".git")) else os.path.dirname(__file__),
                                      "show", f"{ref}:model/data.json"], capture_output=True, text=True, check=True).stdout)
    base = _bfull["macro"]
    # When the baseline is the PREVIOUS release (its notes differ from these), its scores are the
    # "last review" scores this payload records; once this release is committed, it is skipped.
    _bd = {x["name"]: x for x in _bfull["drivers"]}
    if [x["note"] for x in D["drivers"]] != [_bd.get(x["name"], {}).get("note") for x in D["drivers"]]:
        # on 1-5 (v119): the baseline's published "score" - to v118 the 1-10 score rescaled, which is what
        # the page showed and what v119 carried across
        _pbad = [x["name"] for x in D["drivers"] if _bd.get(x["name"], {}).get("score") != x.get("prev_score")]
        ck(f"the last-review scores recorded are {ref}'s published scores", not _pbad, f"{_pbad}")
    # v116: AN INPUT ADDED SINCE THE BASELINE MUST BE READ BY NAME. used() also accepts a number whose value
    # appears in the prose, which let v113's fed_50bp_odds_dec_17nov (4.3) through because "4.3" occurs elsewhere.
    _byname = lambda k: bool(re.search(r"\b(?:m|M|macro|D\.macro)\.%s\b" % re.escape(k), _page)
                             or len(re.findall(r'MACRO\["%s"\]|\b%s\b' % (re.escape(k), re.escape(k)), ENGINE)) > 1)
    new = [k for k, v in M.items() if k not in base and not isinstance(v, (list, dict, bool)) and v is not None
           and not (_byname(k) if isinstance(v, (int, float)) else used(k, v))]
    ck(f"no input added since {ref} that nothing reads", not new, ", ".join(new))
except Exception as e:
    print(f"  [WARN] orphan check skipped: no baseline ({type(e).__name__})")

print(f"\nCHECKS: {N[0]}   FAILURES: {len(FAILS)}")
for f in FAILS: print("  FAIL:", f)
sys.exit(1 if FAILS else 0)
