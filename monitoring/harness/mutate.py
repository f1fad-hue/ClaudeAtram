"""Fault injection for the audit (rebuilt 2026-11-03, v88; gauge mutants v90).

Each mutant plants one error in a copy of the published payload (data.json and the page's
embedded copy); the audit must fail on it. A mutant the audit passes is a blind spot.
  python3 monitoring/harness/mutate.py [-j 4]
"""
import copy, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
D0 = json.load(open(os.path.join(ROOT, "model", "data.json")))

def _fund(d, i): return (d["funds"] + d["portfolio_b"]["funds"])[i]
def _drv(d, n): return next(x for x in d["drivers"] if x["name"].startswith(n))
def m_fee(d): f = _fund(d, 1); f["fee_total"] = round(f["fee_total"] - 0.1, 2)                 # a fee total off its parts
def m_net(d): _fund(d, 3)["net_macro"] = round(_fund(d, 3)["net_macro"] + 0.05, 2)             # a net off base + tilt
def m_tilt(d): _fund(d, 2)["tilt_trend"] = round(_fund(d, 2)["tilt_trend"] + 0.2, 2)          # a tilt part off the total
def m_fdd(d): _fund(d, 1)["dd_macro"] = round(_fund(d, 1)["dd_macro"] - 0.5, 1)               # a fund drawdown off its model
def m_wsum(d): w = d["portfolio_b"]["weights"]; w[0] += 5                                      # weights no longer 100
def m_grid(d): w = d["portfolio_a"]["weights"]; w[0] -= 2; w[1] += 2                           # off the 5% grid
def m_cap(d):                                                                                  # a fund over 35%
    w = d["portfolio_b"]["weights"]; i = max(range(1, len(w)), key=lambda k: w[k]); j = next(k for k in range(1, len(w)) if w[k] and k != i)
    w[i] += 5; w[j] -= 5
def m_cash(d): w = d["portfolio_a"]["weights"]; i = max(range(1, len(w)), key=lambda k: w[k]); w[0] -= 5; w[i] += 5   # cash under 5%
def m_cagr(d): d["portfolio_b"]["macro"]["cagr"] = round(d["portfolio_b"]["macro"]["cagr"] + 0.01, 2)   # a headline CAGR 0.01 off
def m_vol(d): d["portfolio_d"]["macro"]["vol"] = round(d["portfolio_d"]["macro"]["vol"] + 0.02, 2)
def m_dd(d): d["portfolio_a"]["ten"]["maxdd"] = round(d["portfolio_a"]["ten"]["maxdd"] + 0.1, 1)
def m_swap(d):                                                                                 # A swapped for another mix in the budget
    w = d["portfolio_a"]["weights"]; i = next(k for k in range(1, len(w)) if w[k] >= 10); j = next(k for k in range(1, len(w)) if not w[k])
    w[i] -= 5; w[j] += 5
def m_feas(d): d["portfolio_b"]["n_feasible"] += 1
def m_cback(d): d["portfolio_c"] = json.loads(json.dumps(d["portfolio_b"]))                  # the retired C back in the payload (v101)
def m_cap_k(d): d["dd_model"]["b_k"] = round(d["dd_model"]["b_k"] + 0.01, 5)
def m_gauge(d): d["gauge"] = round(d["gauge"] + 0.01, 2)
def m_dscore(d): _drv(d, "Volatility")["score"] = round(_drv(d, "Volatility")["score"] + 0.05, 2)
def m_path(d): _drv(d, "Geopolitics")["path"]["3Y"] = 6.0                                     # a path past neutral
def m_region(d): d["regions"]["ASIA"]["blend"] = round(d["regions"]["ASIA"]["blend"] + 0.02, 2)
def m_band(d): d["dd_gauge"]["value"] = 3.6                                                    # the gauge outside its band
def m_ddread(d): r = d["dd_gauge"]["parts"]["3Y"]; r["reading"] = round(r["reading"] + 0.05, 2)  # a view reading off its parts
def m_ddvol(d):                                                                                # volatility back in the reading (v90)
    g = d["dd_gauge"]; g["value"] = round(sum(g["w"][h] * (g["parts"][h]["macro"] + g["parts"][h]["trend"] + 3.0) / 3
                                              for h in g["views"]), 2)
def m_guard(d):                                                                                # a red guard shown clear
    # By state, not by name (v93): this mutant set the VIX guard clear, and went a no-op the day
    # the VIX closed under its long run. With no guard red, it shows a clear one red.
    gs = d["dd_gauge"]["guards"]; g = next((g for g in gs if not g["ok"]), gs[0]); g["ok"] = not g["ok"]
def m_vixg(d): g = next(g for g in d["dd_gauge"]["guards"] if g["name"] == "vix"); g["ok"] = not g["ok"]   # the VIX guard flipped
def m_dayref(d):                                                                               # a day-keyed move beside another day
    x = _drv(d, "Corporate"); x["note"] = x["note"].replace("on 3 Nov the KOSPI", "on 4 Nov the KOSPI", 1)
def m_yoy1(d): d["macro"]["brent_yoy_1dp"] = round(d["macro"]["brent_yoy_1dp"] - 0.1, 1)      # the y/y a rounding of a rounding (v94)
def m_daydup(d):                                                                               # a day-keyed copy off the latest (v94)
    # By state (v95): it moved nasdaq_5nov, and went blind the day New York rolled to 6 Nov. It now
    # moves whichever day-keyed copy sits on its series' latest day.
    M = d["macro"]; mon = "jan feb mar apr may jun jul aug sep oct nov dec".split()
    lat = {"spx": "equity_date", "nasdaq": "equity_date", "dow": "equity_date", "kospi": "kospi_latest_date",
           "nikkei": "nikkei_latest_date", "psei": "psei_date"}
    def on_latest(k):
        g = re.match(r"^(spx|nasdaq|dow|kospi|nikkei|psei)_(\d{1,2})([a-z]{3})_chg_pct$", k)
        return bool(g) and M[lat[g.group(1)]][5:] == f"{mon.index(g.group(3)) + 1:02d}-{int(g.group(2)):02d}"
    ks = [k for k in M if on_latest(k)]
    if ks: M[ks[0]] = round(M[ks[0]] + 0.02, 2)
    else:
        # v98: no day-keyed copy sat on any series' latest day (every copy was a session behind), and
        # the mutant crashed the run instead of testing anything. With none to move, it plants one
        # that disagrees with the latest move - the same defect, made rather than found.
        e = M["equity_date"]; M[f"spx_{int(e[8:])}{mon[int(e[5:7]) - 1]}_chg_pct"] = round(M["spx_chg_pct"] + 0.02, 2)
def m_tcheck(d): _fund(d, 1)["target_check"]["date"] = "2026-10-20"                            # a target-fund check from an old review
def m_stale(d): d["macro"]["equity_date"] = "2026-10-20"                                       # a close a week behind
def m_lt(d): d["lookthrough"]["ATRQIAP"]["as_of"] = "2026-08-31"                               # holdings past 60 days
def m_imf(d): d["macro"]["imf_weo_vintage"] = "2026-07-08"                                     # last edition back after the next
def m_umich(d): d["macro"]["us_umich_oct_final"] = False; d["macro"]["us_umich_oct_date"] = "2026-10-09"
def m_chain(d): d["macro"]["spx_chg_pts"] = round(d["macro"]["spx_chg_pts"] - 0.05, 2)         # a move 0.05 off its prior
def m_vix(d): d["macro"]["vix_latest"] = d["macro"]["vix_history"][-2][1]                      # the VIX a session behind
def m_brent(d): d["macro"]["brent_yoy"] = round(d["macro"]["brent_yoy"] + 0.5, 2)
def m_base(d): d["macro"]["brent_yr_ago_date"] = "2025-10-15"                                  # a year-ago base far off the anniversary
def m_peso(d): d["macro"]["usdphp_chg"] = round(d["macro"]["usdphp_chg"] - 0.01, 3)
def m_note(d):                                                                                 # a number in a note no input carries
    # Planted by position, not by wording (v94): it replaced "HELD at" in the Growth note, and went a
    # no-op the day Growth was RAISED. Every note has a first sentence.
    # v98: the planted "13.37" became a real input (a target fund's 1-year return) and the mutant
    # went quiet - the audit cannot flag a number an input carries. The number is now chosen by
    # state: the first of a run of candidates that appears nowhere in the payload.
    def nums(o):
        if isinstance(o, bool): return
        if isinstance(o, (int, float)): yield round(float(o), 2)
        elif isinstance(o, dict):
            for v in o.values(): yield from nums(v)
        elif isinstance(o, (list, tuple)):
            for v in o: yield from nums(v)
        elif isinstance(o, str):
            for t in re.findall(r"\d+(?:\.\d+)?", o): yield round(float(t), 2)
    have = set(nums(d))
    c = next(v for v in (round(913.37 + 101.01 * i, 2) for i in range(200)) if v not in have)
    x = _drv(d, "Growth"); x["note"] = x["note"].replace(". ", f". It moved {c} points. ", 1)
def m_summ(d): x = _drv(d, "Inflation"); x["summary"] = x["summary"].rstrip(".") + ", 4.44% above target."
def m_brhigh(d):
    x = _drv(d, "Inflation"); x["note"] = re.sub(r"(Brent settled at \$[\d.]+ on [^,]+,)", lambda m: m.group(1) + f" below the ${d['macro']['brent']:.2f} of the 23rd,", x["note"], count=1)
def m_src(d): d["sources"].append(dict(d["sources"][0]))                                       # a source listed twice
def m_http(d): d["sources"][1]["url"] = d["sources"][1]["url"].replace("https://", "http://", 1)
def m_nan(d): _drv(d, "Valuation")["note"] += " NaN"
def m_retired(d): d["portfolio_a"]["is_review_pick"] = True                                    # the retired review flag back
def m_opt(d): d["optimized"] = d["portfolio_b"]                                                # the retired optimiser key back
def m_cat(d): d["catalysts"].append({"date": "2026-10-01", "what": "Old event", "why": "past"})
def m_step(d):                                                                                 # a budget step printing a CAGR its search did not rank on
    e = next(iter(d["dd_gauge"]["alt"].values()))["b"]; e["cagr"] = round(e["cagr"] - 0.01, 2)
def m_verb(d):                                                                                 # a note announcing a move not made (v95)
    x = _drv(d, "Growth"); w = x["note"].split(" ", 1)
    x["note"] = {"HELD": "RAISED", "RAISED": "HELD", "CUT": "HELD"}[w[0]] + " " + w[1]
def m_brace(d): x = _drv(d, "Monetary"); x["note"] = x["note"].replace(". ", ". The {_dday('x')} high. ", 1)   # an f lost (v95)
def m_rycpi(d): d["real_yield"]["cpi"] = d["macro"]["ph_cpi_sep"]; d["real_yield"]["month"] = "September"   # the stale month (v95)
def m_dshift(d):                                                                               # D moved 5% off its pick (v96)
    w = d["portfolio_d"]["weights"]; i = w.index(max(w)); j = next(k for k in range(len(w)) if w[k] and k != i)
    w[i] -= 5; w[j] += 5
def m_dextra(d):                                                                               # D holding one fund more than its pick (v96; v99)
    w = d["portfolio_d"]["weights"]; i = w.index(max(w)); j = next(k for k in range(len(w)) if not w[k])
    w[i] -= 5; w[j] += 5
def m_dlead(d):                                                                                # D's main fund no longer the largest (v99)
    w = d["portfolio_d"]["weights"]; i = w.index(max(w)); j = max((k for k in range(len(w)) if k != i), key=lambda k: w[k])
    g = (w[i] - w[j]) // 10 * 5 + (5 if (w[i] - w[j]) % 10 else 0); w[i] -= g; w[j] += g
def m_dcount(d): b = d["portfolio_d"]["by_count"][0]; b["cagr"] = round(b["cagr"] + 0.01, 2)   # a count's best off its re-run (v99)
def m_gap(d): d["macro"]["gtec_gap_1y_pp"] = round(d["macro"]["gtec_gap_1y_pp"] + 0.5, 2)      # a 1-year gap off its inputs (v98)
def m_over(d): d["vol_channel"]["overtaken"] = not d["vol_channel"]["overtaken"]              # the overtaken flag flipped (v98)
def m_retr(d): d["macro"]["vix_spike_retraced_pct"] += 5                                       # the retrace off the series (v98)
def m_holds(d):                                                                                # "none holds it" said of a fund A and B hold (v98)
    f = next(f for f in d["funds"] if f["id"] == "ATRGTEC"); f["target_check"]["text"] += " And none of A, B or D holds it."
def m_grind(d):
    r = next(r for r in d["portfolio_b"]["scenarios"] if r["name"].startswith("Grind")); r["cagr"] = round(r["cagr"] + 0.01, 2)

MUTS = [(n, f) for n, f in sorted(globals().items()) if n.startswith("m_") and callable(f)]

def run(name, fn):
    tmp = tempfile.mkdtemp(prefix="mut_")
    try:
        for sub in ("model", "monitoring"): os.makedirs(os.path.join(tmp, sub))
        for f_ in ("model/engine.py", "monitoring/CLAIMS.md", "README.md", "dashboard.html"):
            shutil.copy(os.path.join(ROOT, f_), os.path.join(tmp, f_))
        d = copy.deepcopy(D0); fn(d)
        if d == D0: return name, "NO-OP", ""
        raw = json.dumps(d, indent=1)
        open(os.path.join(tmp, "model/data.json"), "w").write(raw + "\n")
        h = open(os.path.join(tmp, "dashboard.html")).read()
        h = re.sub(r'(<script id="D" type="application/json">)\n.*?\n(</script>)', lambda m: m.group(1) + "\n" + raw + "\n" + m.group(2), h, flags=re.S)
        open(os.path.join(tmp, "dashboard.html"), "w").write(h)
        res = subprocess.run([sys.executable, os.path.join(HERE, "audit.py")], capture_output=True, text=True,
                             env={**os.environ, "ATRAM_ROOT": tmp, "BASELINE_REF": os.environ.get("BASELINE_REF", "HEAD")}, cwd=ROOT)
        fails = [l.strip() for l in res.stdout.splitlines() if l.strip().startswith("[FAIL]") and "embedded payload" not in l]
        if not fails and res.returncode != 0 and "Traceback" in res.stderr:
            return name, "CRASH", res.stderr.strip().splitlines()[-1][:100]
        return name, "CAUGHT" if fails else "MISSED", (fails[0][:110] if fails else "")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    j = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 4
    print(f"{len(MUTS)} mutants")
    with ThreadPoolExecutor(j) as ex:
        out = list(ex.map(lambda nf: run(*nf), MUTS))
    for name, st, why in out: print(f"{name:<12} {st:<7} {why}")
    bad = [o for o in out if o[1] in ("MISSED", "NO-OP")]
    print(f"\n{len(out) - len(bad)}/{len(out)} caught" + (f"; not caught: {[b[0] for b in bad]}" if bad else ""))
    sys.exit(1 if bad else 0)
