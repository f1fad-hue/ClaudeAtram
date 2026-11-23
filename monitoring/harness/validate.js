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
        // v114: the tabs fill the bar edge to edge in equal widths (a stale six-column grid left a gap)
        tabfit: (() => { const bar = document.querySelector(".navin"), ts = [...document.querySelectorAll("button.tab")];
          if (!bar || !ts.length) return false; const r = bar.getBoundingClientRect(), w = ts.map(t => t.getBoundingClientRect());
          return Math.abs(w[0].left - r.left) < 1.5 && Math.abs(w[w.length - 1].right - r.right) < 1.5
            && w.every(x => Math.abs(x.width - r.width / ts.length) < 1.5); })(),
        donuts: ["donutA", "donutB", "donutC", "donutD"].map(i => !!document.querySelector(`#${i} svg`)),
        vs, shorts: D.portfolio_b.shorts,
        gaugenow: (document.getElementById("gaugenow") || {}).textContent,
        lede: (document.getElementById("pblede") || {}).textContent || "",
        dlede: (document.getElementById("dlede") || {}).textContent || "",
        clede: (document.getElementById("clede") || {}).textContent || "",
        ccount: [...document.querySelectorAll("#ccount tbody tr")].map(r => r.textContent.trim()),
        cpay: [...document.querySelectorAll("#cpay tbody tr")].map(r => r.textContent.trim()),
        ddh: [...document.querySelectorAll("#ddtab thead th")].map(c => c.textContent.trim()),
        ddnote: (document.querySelector("#ddbarnote") || {}).textContent || "",
        ddw: [...document.querySelectorAll("#ddtab tbody tr")].map(r => [...r.cells].map(c => c.textContent.trim()))
               .find(r => r[0].startsWith("Weight")) || [],
        donutD: !!document.querySelector("#donutD svg"),
        // v119: every surface that shows a macro driver, for the retired 1-10 scale; v120: and every regional one
        drvtxt: ["#drivers", "#dptab", "#dpnote", "#ddy1", "#ddy1note", "#ddy1why", "#ddval", "#ddvalnote", "#ddguards",
                 "#rtab", "#rwhy", "#abytab"]
          .map(q => (document.querySelector(q) || {}).textContent || "").join(" ")
          + " " + (((document.getElementById("dvgeo") || {}).parentElement || {}).textContent || ""),
        drvh: [...document.querySelectorAll("h3")].map(h => h.textContent).filter(t => /Macro drivers|Market valuation/.test(t)),
        // v122: every section on every tab, after each tab has been opened: its text, and any element in it left empty
        secs: [...document.querySelectorAll(".panel section")].map(s => ({
          tab: s.closest(".panel").id, eb: ((s.querySelector(".eyebrow") || {}).textContent || "").trim().slice(0, 40),
          n: s.textContent.trim().length,
          empty: [...s.querySelectorAll("[id]")].filter(x => !x.textContent.trim() && !x.querySelector("svg,canvas")).map(x => x.id) })),
      };
    });
    const D = info.D;
    ck(`[${width}px] no JavaScript errors after opening every tab`, errs.length === 0, errs.slice(0, 3).join(" | "));
    ck(`[${width}px] no horizontal scroll`, !info.hscroll);
    ck(`[${width}px] the tabs fill the bottom bar in equal widths, edge to edge`, info.tabfit);
    if (width !== 412) { await p.close(); continue; }
    // v107 (owner, 16 Nov): the Volatility tab retired - five tabs, its drawdown model on the Portfolios tab
    ck("five tabs, five panels, no Volatility tab, the tab bar fixed to the bottom",
      tabs.length === 5 && info.panels === 5 && info.nav && !tabs.includes("vol"), `${tabs}`);
    ck("viewport meta present" + (live ? "" : " (required only on the live copy)"), info.viewport || !live);
    ck("no NaN, undefined, Invalid Date or malformed sign in any panel", info.bad.length === 0, `${info.bad}`);
    ck("no placeholder dash left in a figure or lede", info.dashes.length === 0, `${info.dashes}`);
    ck("no empty figure", info.emptyNum.length === 0, `${info.emptyNum.slice(0, 6)}`);
    ck("no duplicate element ids", info.dup.length === 0, `${info.dup.slice(0, 5)}`);
    ck("every external reference is https", info.http.length === 0, `${info.http.slice(0, 3)}`);
    // v125 (owner, 23 Nov): C is the dividend-income portfolio - two to five of the income funds and the money market
    ck("four donuts drawn, A, B, C and D", info.donuts.length === 4 && info.donuts.every(Boolean), `${info.donuts}`);
    const W = { A: D.portfolio_a.weights, B: D.portfolio_b.weights, C: D.portfolio_c.weights, D: D.portfolio_d.weights };
    const shown = info.vs.map(r => [r[0], r.slice(1).map(c => c === "–" ? 0 : parseInt(c))]);
    const want = info.shorts.map((s, i) => [s, [W.A[i], W.B[i], W.C[i], W.D[i]]]).filter(x => x[1].some(Boolean));
    ck("the A-B-C-D weights table is the payload's, row for row", JSON.stringify(shown) === JSON.stringify(want),
      `${JSON.stringify(shown)} vs ${JSON.stringify(want)}`);
    ck("the Report's gauge is the payload's", info.gaugenow === D.gauge.toFixed(2), `${info.gaugenow} vs ${D.gauge}`);
    const pc = x => x.toFixed(2) + "%";
    const dmix = D.portfolio_d.weights.map((w, j) => [w, j]).filter(x => x[0]).map(([w, j]) => `${w}% ${D.portfolio_b.shorts[j]}`);
    ck("Portfolio D's section draws its donut and states its mix, 1/3/5/10-year CAGR and drawdown",
      info.donutD && dmix.every(x => info.dlede.includes(x)) && info.dlede.includes(pc(D.portfolio_d.macro.cagr))
      && info.dlede.includes("\u2212" + Math.abs(D.portfolio_d.macro.maxdd).toFixed(1) + "%"), info.dlede.slice(0, 200));
    const cmix = D.portfolio_c.weights.map((w, j) => [w, j]).filter(x => x[0]).map(([w, j]) => `${w}% ${D.portfolio_b.shorts[j]}`);
    const cbc = D.portfolio_c.by_count, cpy = D.portfolio_c.payout, cf = D.portfolio_c.funds;
    const cpRows = info.cpay.filter((_, i) => i % 2 === 0), cpSub = info.cpay.filter((_, i) => i % 2 === 1);
    ck("Portfolio C's section states its mix, 1/3/5/10-year CAGR and drawdown, a row per fund count with C's marked, and what each of its funds pays",
      cmix.length === D.portfolio_c.n_funds && cmix.every(x => info.clede.includes(x)) && info.clede.includes(pc(D.portfolio_c.macro.cagr))
      && info.clede.includes("\u2212" + Math.abs(D.portfolio_c.macro.maxdd).toFixed(1) + "%")
      && info.ccount.length === 2 * cbc.length && info.ccount.filter(t => t.includes("\u2190 C")).length === 1
      && info.ccount.findIndex(t => t.includes("\u2190 C")) === 2 * cbc.findIndex(b => b.n === D.portfolio_c.n_funds)
      && info.cpay.length === 2 * cf.length
      && cf.every(id => { const k = cpRows.findIndex(t => t.startsWith(D.portfolio_b.shorts[D.portfolio_b.ids.indexOf(id)]));
           const w = D.portfolio_c.weights[D.portfolio_b.ids.indexOf(id)];
           return k >= 0 && cpRows[k].includes(cpy[id].freq ? cpy[id].freq.replace(/^./, c => c.toUpperCase()) : "No payout")
             && cpRows[k].endsWith(w ? w + "%" : "\u2013") && cpSub[k].includes(cpy[id].sources); }),
      info.clede.slice(0, 200));
    // v112 (owner, 17 Nov): the gauge reads months 1-6 and 7-12, years 2-3 and 4-5 at 10/10/40/40, the 10-year anchor beside them
    const G = D.dd_gauge;
    ck("the Budget tab's gauge table shows months 1-6, 7-12, years 2-3, 4-5 at their weights and the 10-year anchor unweighted",
      info.ddh.length === 6 && info.ddw.slice(1).join() === G.views.map(h => (G.w[h] * 100).toFixed(0) + "%").concat(["anchor"]).join()
      && G.views.join() === "6M,12M,3Y,5Y", `${info.ddh} | ${info.ddw}`);
    // v117: the band sentence read the width of the LOWEST band (1.00-2.20, so "each 1.20 below 2.80") as the step down.
    const sw = G.step_w.toFixed(2), nt = info.ddnote.replace(/\s+/g, " ");
    ck("the Budget tab's band sentence states the payload's step width both ways",
      nt.includes(`each ${sw} below`) && nt.includes(`each ${sw} above`), nt.slice(0, 220));
    // v119 (owner, 21 Nov: "Macroeconomics drivers update it 1-5 guauge. No more 1-10."): no driver surface prints
    // the retired 1-10 scale, its 5.5 neutral or a "research scale" label, and the tables are headed 1-5.
    // v120 ("Regional driver update them to 1-5 gauge"): nor does the regional ranking or the year-by-year table.
    const old10 = info.drvtxt.match(/\b1[–-]10\b|\/ 10\b|research scale|5\.5 neutral/g) || [];
    ck("no macro driver or regional surface shows the retired 1-10 scale; the driver and valuation tables are headed 1-5, 3 neutral",
      old10.length === 0 && info.drvh.length === 2 && info.drvh.every(t => t.includes("1–5 (3 neutral)")),
      `${old10.slice(0, 3)} | ${info.drvh}`);
    // v122: the review covers every tab, so the check does too - each section renders, none is a stub, and no element in
    // it is left empty (the postponed list only while the payload has nothing postponed)
    const tabsSeen = new Set(info.secs.map(x => x.tab));
    const stubs = info.secs.filter(x => x.n < 150 || x.empty.some(id => !(id === "postponed" && !(D.postponed || []).length)));
    ck(`every section on all ${tabsSeen.size} tabs renders (${info.secs.length} sections), none a stub and nothing in it left empty`,
      tabsSeen.size === 5 && info.secs.length >= 30 && stubs.length === 0,
      stubs.map(x => `${x.tab}/${x.eb || "?"}: ${x.n} chars, empty ${x.empty}`).slice(0, 3).join(" | "));
    ck("the Portfolios lede states A's 10-year, B's, C's and D's 1/3/5/10-year CAGR",
      [pc(D.portfolio_a.ten.cagr), pc(D.portfolio_b.macro.cagr), pc(D.portfolio_c.macro.cagr), pc(D.portfolio_d.macro.cagr)].every(x => info.lede.includes(x)),
      info.lede.slice(0, 160));
    await p.close();
  }
  await b.close();
  console.log(rows.join("\n"));
  console.log(`\n${rows.length} page checks, ${fail.length} failed`);
  process.exit(fail.length ? 1 : 0);
})();
