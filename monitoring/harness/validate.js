// Page validator (rebuilt 2026-11-03, v88): loads the dashboard in Chromium at phone
// widths, opens every tab, and checks what a reader sees against the embedded payload.
//   NODE_PATH=/opt/node22/lib/node_modules node monitoring/harness/validate.js <abs path to html> [--live]
// --live: the published copy, where the host adds the viewport meta; locally it is only
// required with --live. Exit code 1 on any failure.
const { chromium } = require("playwright");
const file = process.argv[2], live = process.argv.includes("--live");
(async () => {
  const b = await chromium.launch();
  const rows = [], fail = [];
  const ck = (label, ok, detail) => { rows.push(`${ok ? "PASS" : "FAIL"}  ${label}` + (detail ? `\n      ${detail}` : "")); if (!ok) fail.push(label); };
  for (const width of [412, 360]) {
    const p = await b.newPage({ viewport: { width, height: 900 } });
    const errs = [];
    p.on("pageerror", e => errs.push(String(e)));
    p.on("console", m => { if (m.type() === "error") errs.push(m.text()); });
    await p.goto("file://" + file);
    await p.waitForTimeout(700);
    const tabs = await p.$$eval("button.tab", xs => xs.map(x => x.dataset.p));
    for (const t of tabs) { await p.click(`#t-${t}`); await p.waitForTimeout(150); }
    const info = await p.evaluate(() => {
      const D = JSON.parse(document.getElementById("D").textContent);
      const nav = document.querySelector("nav"), cs = nav ? getComputedStyle(nav) : null;
      const ids = [...document.querySelectorAll("[id]")].map(e => e.id);
      const dup = ids.filter((x, i) => ids.indexOf(x) !== i);
      const emptyNum = [...document.querySelectorAll(".num")].filter(e => !e.textContent.trim()).map(e => e.id || e.className);
      const text = document.body.innerText + " " + [...document.querySelectorAll(".panel")].map(x => x.textContent).join(" ");
      const ext = [...document.querySelectorAll("[src],[href]")].map(e => e.getAttribute("src") || e.getAttribute("href"))
        .filter(u => /^(https?:)?\/\//.test(u));
      const vs = [...document.querySelectorAll("#vswt tbody tr")].map(r => [...r.cells].map(c => c.textContent.trim()));
      return {
        D, nav: cs && cs.position === "fixed" && cs.bottom === "0px", viewport: !!document.querySelector('meta[name="viewport"]'),
        panels: document.querySelectorAll(".panel").length, dup, emptyNum,
        bad: (text.match(/\bNaN\b|\bundefined\b|Invalid Date|null%|- \+|\+-\d/g) || []).slice(0, 5),
        dashes: [...document.querySelectorAll(".num, .lede")].filter(e => e.textContent.trim() === "—").map(e => e.id).slice(0, 8),
        http: ext.filter(u => !u.startsWith("https://")),
        hscroll: document.documentElement.scrollWidth > window.innerWidth + 1,
        donuts: ["donutA", "donutB", "donutD"].map(i => !!document.querySelector(`#${i} svg`)),
        donutC: !!document.getElementById("donutC"),
        vs, shorts: D.portfolio_b.shorts,
        gaugenow: (document.getElementById("gaugenow") || {}).textContent,
        lede: (document.getElementById("pblede") || {}).textContent || "",
        dlede: (document.getElementById("dlede") || {}).textContent || "",
        donutD: !!document.querySelector("#donutD svg"),
      };
    });
    const D = info.D;
    ck(`[${width}px] no JavaScript errors after opening every tab`, errs.length === 0, errs.slice(0, 3).join(" | "));
    ck(`[${width}px] no horizontal scroll`, !info.hscroll);
    if (width !== 412) { await p.close(); continue; }
    ck("six tabs, six panels, the tab bar fixed to the bottom", tabs.length === 6 && info.panels === 6 && info.nav, `${tabs}`);
    ck("viewport meta present" + (live ? "" : " (required only on the live copy)"), info.viewport || !live);
    ck("no NaN, undefined, Invalid Date or malformed sign in any panel", info.bad.length === 0, `${info.bad}`);
    ck("no placeholder dash left in a figure or lede", info.dashes.length === 0, `${info.dashes}`);
    ck("no empty figure", info.emptyNum.length === 0, `${info.emptyNum.slice(0, 6)}`);
    ck("no duplicate element ids", info.dup.length === 0, `${info.dup.slice(0, 5)}`);
    ck("every external reference is https", info.http.length === 0, `${info.http.slice(0, 3)}`);
    ck("three donuts drawn, A, B and D, and none for the retired C", info.donuts.length === 3 && info.donuts.every(Boolean)
      && !info.donutC && !D.portfolio_c, `${info.donuts} ${info.donutC}`);
    const W = { A: D.portfolio_a.weights, B: D.portfolio_b.weights, D: D.portfolio_d.weights };
    const shown = info.vs.map(r => [r[0], r.slice(1).map(c => c === "–" ? 0 : parseInt(c))]);
    const want = info.shorts.map((s, i) => [s, [W.A[i], W.B[i], W.D[i]]]).filter(x => x[1].some(Boolean));
    ck("the A-B-D weights table is the payload's, row for row", JSON.stringify(shown) === JSON.stringify(want),
      `${JSON.stringify(shown)} vs ${JSON.stringify(want)}`);
    ck("the Report's gauge is the payload's", info.gaugenow === D.gauge.toFixed(2), `${info.gaugenow} vs ${D.gauge}`);
    const pc = x => x.toFixed(2) + "%";
    const dmix = D.portfolio_d.weights.map((w, j) => [w, j]).filter(x => x[0]).map(([w, j]) => `${w}% ${D.portfolio_b.shorts[j]}`);
    ck("Portfolio D's section draws its donut and states its mix, 3/5/10-year CAGR and drawdown",
      info.donutD && dmix.every(x => info.dlede.includes(x)) && info.dlede.includes(pc(D.portfolio_d.macro.cagr))
      && info.dlede.includes("\u2212" + Math.abs(D.portfolio_d.macro.maxdd).toFixed(1) + "%"), info.dlede.slice(0, 200));
    ck("the Portfolios lede states A's 10-year, B's and D's 3/5/10-year CAGR",
      [pc(D.portfolio_a.ten.cagr), pc(D.portfolio_b.macro.cagr), pc(D.portfolio_d.macro.cagr)].every(x => info.lede.includes(x)),
      info.lede.slice(0, 160));
    await p.close();
  }
  await b.close();
  console.log(rows.join("\n"));
  console.log(`\n${rows.length} page checks, ${fail.length} failed`);
  process.exit(fail.length ? 1 : 0);
})();
