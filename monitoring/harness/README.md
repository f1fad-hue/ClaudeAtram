# Verification harnesses

Kept in the repository from v88: twice a container reset wiped them from the scratchpad.

| File | What it does | Run |
|---|---|---|
| `rebuild.sh` | Engine → `model/data.json` → the payload embedded in `dashboard.html` | `sh monitoring/harness/rebuild.sh` |
| `audit.py` | Independent re-derivation from the published payload: fund fees, nets, tilts and drawdowns; every portfolio figure; the selection rule re-run over every mix; the gauge, paths and regions; every freshness clock with its days left; chains; prose traceability; the claims register; sources; inputs nothing reads (against `BASELINE_REF`, default `HEAD`) | `python3 monitoring/harness/audit.py` |
| `validate.js` | The page in Chromium at 412px and 360px: every tab opened, no errors, no NaN or placeholder, the A-B-C table against the payload | `NODE_PATH=/opt/node22/lib/node_modules node monitoring/harness/validate.js $PWD/dashboard.html [--live]` |
| `mutate.py` | Plants one error per mutant in a copy of the payload; the audit must fail on each | `python3 monitoring/harness/mutate.py -j 4` |

The engine's own checks (`python3 model/engine.py`) run first; these test what it publishes.
