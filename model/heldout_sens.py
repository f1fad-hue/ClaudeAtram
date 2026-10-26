"""What two held-out funds would do if admitted (2026-10-22), on the engine's own basis,
and what a disputed fee on an admitted fund would do (2026-10-23).

Run: python3 model/heldout_sens.py (about 40 seconds after the engine's own build).
Its results are recorded in engine.py as useq_w_* and gbi_w_*, and in Global
Allocation's fee note; re-run it when any of those fees, or the universe, change.

Imports the engine, builds the held-out fund with build_fund() and the factor model,
re-binds the search's globals to the eleven funds plus that one, and re-runs the rule
for A (the 10-year view), B (the 5/10-year view) and C (the same, Nasdaq Equity Income at 50%). For the
disputed fee it rebuilds the admitted fund in place and re-runs the same three."""
import json, math, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

def spec_useq(trust):
    return {"id": "X_USEQ", "name": "ATRAM US Equity Opportunity Feeder Fund", "short": "US Equity Opportunity",
            "ccy": "PHP (unhedged)", "region": "US", "target": "Franklin U.S. Opportunities", "target_verified": False,
            "fee_feeder": trust, "fee_target": 0.85, "fee_note": "", "gross_usd": E.MACRO["ltcma_us_eq"] + E.MACRO["ndx_growth_premium"],
            "gross_note": "", "vol_beta": 1.15, "fx_exposed": True, "macro_tilt": {"rates": -0.30, "energy": -0.10},
            "dd_k_adj": 0.10, "cash_like": False, "dd_k_why": "", "trend_market": "ATRQIAP"}

def spec_gbi(target):
    return {"id": "X_GBI", "name": "ATRAM Global Bond Income Feeder Fund", "short": "Global Bond Income",
            "ccy": "PHP (unhedged)", "region": "GLOBAL_ALLOC", "target": "PIMCO GIS Diversified Income", "target_verified": False,
            "fee_feeder": 0.90, "fee_target": target, "fee_note": "", "gross_usd": E.MACRO["ltcma_us_ig"],
            "gross_note": "", "vol_beta": 5.0 / E.SP_VOL_LT, "fx_exposed": True, "macro_tilt": {"rates": -0.30, "energy": 0.0},
            "dd_k_adj": 0.0, "cash_like": False, "dd_k_why": "", "equity_share": 0.0, "trend_market": None}

LOAD = {"X_USEQ": {"G": 17.5, "GW": 11.0, "RG": 4.5}, "X_GBI": {"G": 1.5, "CY": 1.0, "RG": 4.0}}

def run(spec):
    E.VOL_SENS[spec["id"]] = 0.0
    E.FACTOR_LOADINGS[spec["id"]] = LOAD[spec["id"]]
    fb = E.build_fund(spec)
    specs = E.FUNDS + E.ADD_FUNDS + [spec]
    fc = E.factor_corr(specs)
    n = len(specs)
    C = [[E.CORR_U[i][j] if i < n - 1 and j < n - 1 else (1.0 if i == j else round(fc[i][j], 2)) for j in range(n)] for i in range(n)]
    assert E._chol_pd(C)
    E._UF, E._US, E._UC = E.F + E.F_ADD + [fb], specs, C
    E._UN = n; E._VOL = [f["vol"] for f in E._UF]; E._ADJ = [f["dd_k_adj"] for f in specs]
    E._CASH = [f["cash_like"] for f in specs]
    pk = {"a": E._Pick(), "b": E._Pick(), "c": E._Pick()}
    for seq, (idx, u) in enumerate(E.univ_mixes()):
        ms = E._measure(idx, u, ["net_10y", "net_macro"])
        pk["a"].add(ms[0] + (seq, idx, u)); pk["b"].add(ms[1] + (seq, idx, u))
    for seq, (idx, u) in enumerate(E.univ_mixes(pinned=True)):
        pk["c"].add(E._measure(idx, u, ["net_macro"])[0] + (seq, idx, u))
    out = {}
    for k in "abc":
        w, band, win = pk[k].result()
        out[k] = {"w": [round(x * 100) for x in w], "cagr": win[0], "dd": win[1], "new_w": round(w[-1] * 100)}
    return fb, out

def run_refee(fid, trust):
    """Re-run A, B and C with an admitted fund rebuilt at a different trust fee."""
    ix = E.UNIV_IDS.index(fid)
    spec = dict(E.UNIV[1][ix], fee_feeder=trust)
    fb = E.build_fund(spec)
    E._UF = E.UNIV[0][:ix] + [fb] + E.UNIV[0][ix + 1:]
    E._US, E._UC, E._UN = E.UNIV[1], E.UNIV[2], len(E.UNIV[1])
    E._VOL = [f["vol"] for f in E._UF]; E._ADJ = [f["dd_k_adj"] for f in E._US]
    E._CASH = [f["cash_like"] for f in E._US]
    pk = {"a": E._Pick(), "b": E._Pick(), "c": E._Pick()}
    for seq, (idx, u) in enumerate(E.univ_mixes()):
        ms = E._measure(idx, u, ["net_10y", "net_macro"])
        pk["a"].add(ms[0] + (seq, idx, u)); pk["b"].add(ms[1] + (seq, idx, u))
    for seq, (idx, u) in enumerate(E.univ_mixes(pinned=True)):
        pk["c"].add(E._measure(idx, u, ["net_macro"])[0] + (seq, idx, u))
    out = {}
    for k in "abc":
        w, band, win = pk[k].result()
        out[k] = {"w": [round(x * 100) for x in w], "cagr": win[0], "dd": win[1], "fund_w": round(w[ix] * 100)}
    E._UF = E.UNIV[0]
    return fb, out

if __name__ == "__main__":
    shorts = [f["short"] for f in E.FUNDS + E.ADD_FUNDS]
    res = {}
    for lab, sp in (("useq_listed", spec_useq(E.MACRO["useq_trust_listed"])), ("useq_peer", spec_useq(E.MACRO["useq_trust_peer"])),
                    ("gbi_inst", spec_gbi(0.69)), ("gbi_retail", spec_gbi(1.59))):
        t = time.time(); fb, out = run(sp); res[lab] = out
        print(f"{lab:12} fund net base {fb['net_base']} 10y {fb['net_10y']} macro {fb['net_macro']} vol {fb['vol']} dd {fb['dd_macro']}  ({time.time()-t:.0f}s)")
        for k, v in out.items():
            mix = ", ".join(f"{x}% {s}" for x, s in zip(v["w"], shorts + [fb["short"]]) if x)
            print(f"   {k.upper()}: {v['new_w']}% of it  | {mix}  {v['cagr']}% / {v['dd']}%")
    # Global Allocation: 1.20% on two listings, 1.50% on DragonFi (2026-10-22).
    t = time.time(); fb, out = run_refee("M_GALL", 1.50)
    print(f"gall_150     fund net base {fb['net_base']} 10y {fb['net_10y']} macro {fb['net_macro']}  ({time.time()-t:.0f}s)")
    for k, v in out.items():
        mix = ", ".join(f"{x}% {s}" for x, s in zip(v["w"], shorts) if x)
        print(f"   {k.upper()}: {v['fund_w']}% of it  | {mix}  {v['cagr']}% / {v['dd']}%")
