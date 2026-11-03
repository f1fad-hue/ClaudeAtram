#!/bin/sh
# Rebuild the payload from the engine and embed it in the page (rebuilt 2026-11-03, v88).
set -e
cd "$(dirname "$0")/../.."
python3 model/engine.py --json > model/data.json
python3 - <<'PY'
import re
h = open('dashboard.html').read(); d = open('model/data.json').read().strip()
pat = re.compile(r'(<script id="D" type="application/json">)\n(.*?)\n(</script>)', re.S)
assert len(pat.findall(h)) == 1
h = pat.sub(lambda m: m.group(1) + "\n" + d + "\n" + m.group(3), h)
open('dashboard.html', 'w').write(h)
print('embedded')
PY
