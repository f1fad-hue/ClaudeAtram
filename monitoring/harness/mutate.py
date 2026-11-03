"""Fault injection for the audit (rebuilt 2026-11-03, v88).

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
def m_vol(d): d["portfolio_c"]["macro"]["vol"] = round(d["portfolio_c"]["macro"]["vol"] + 0.02, 2)
def m_dd(d): d["portfolio_a"]["ten"]["maxdd"] = round(d["portfolio_a"]["ten"]["maxdd"] + 0.1, 1)
def m_swap(d):                                                                                 # A swapped for another mix in the budget
    w = d["portfolio_a"]["weights"]; i = next(k for k in range(1, len(w)) if w[k] >= 10); j = next(k for k in range(1, len(w)) if not w[k])
    w[i] -= 5; w[j] += 5
def m_feas(d): d["portfolio_b"]["n_feasible"] += 1
def m_pin(d): w = d["portfolio_c"]["weights"]; w[1] -= 5; w[0] += 5                           # C off its 50% pin
def m_cap_k(d): d["dd_model"]["b_k"] = round(d["dd_model"]["b_k"] + 0.01, 5)
def m_gauge(d): d["gauge"] = round(d["gauge"] + 0.01, 2)
def m_dscore(d): _drv(d, "Volatility")["score"] = round(_drv(d, "Volatility")["score"] + 0.05, 2)
def m_path(d): _drv(d, "Geopolitics")["path"]["3Y"] = 6.0                                     # a path past neutral
def m_region(d): d["regions"]["ASIA"]["blend"] = round(d["regions"]["ASIA"]["blend"] + 0.02, 2)
def m_band(d): d["dd_gauge"]["value"] = 3.6                                                    # the gauge outside its band
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
    x = _drv(d, "Growth"); x["note"] = x["note"].replace("HELD at", "HELD, after 13.37 points, at", 1)
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
