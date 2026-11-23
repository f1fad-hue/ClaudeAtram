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
        inc: [...document.querySelectorAll("#inctab tbody tr")].map(r => [...r.cells].map(c => c.textContent.trim())),
        ptabInc: [...document.querySelectorAll("#ptab tbody tr")].map(r => [...r.cells].map(c => c.textContent.trim()))
                   .filter(r => /^Payout (yield, trailing|a year on)/.test(r[0])),
        ptabPr: [...document.querySelectorAll("#ptab tbody tr")].map(r => [...r.cells].map(c => c.textContent.trim()))
                   .filter(r => /^(Payout yield, \d{4}|Change in payout)/.test(r[0])),
        pr: [...document.querySelectorAll("#prtab tbody tr")].map(r => [...r.cells].map(c => c.textContent.trim())),
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
        // v128 (owner, 23 Nov: "make the page/tabs concise"): the words each paragraph shows before its folded part
        shown: [...document.querySelectorAll(".panel p, .panel li, .panel div.note")]
          .filter(e => !e.closest("table, details:not([open]), .src, .cat") && !e.querySelector("p"))
          .map(e => { const c = e.cloneNode(true); c.querySelectorAll("details:not([open])").forEach(d => d.remove());
                      return [(c.textContent.match(/\S+/g) || []).length, (e.id ? "#" + e.id : e.tagName) + " " + c.textContent.trim().slice(0, 50)]; }),
        folds: document.querySelectorAll(".panel details.more").length,
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
    // v128 (owner, 23 Nov): concise - no paragraph shows more than 90 words before its "More"
    const longest = info.shown.reduce((a, x) => x[0] > a[0] ? x : a, [0, ""]);
    ck("every paragraph on every tab shows 90 words or fewer, the rest folded under More",
      longest[0] <= 90 && info.folds > 20, `longest ${longest[0]} words: ${longest[1]}; ${info.folds} folds`);
    // v126 (owner, 23 Nov): each portfolio's income over the trailing 12 months, in the headline table and its own card
    const INCp = ["portfolio_a", "portfolio_b", "portfolio_c", "portfolio_d"].map(k => D[k].income);
    const pz = v => "\u20b1" + v.toLocaleString("en-US");
    const tot = info.inc.find(r => r[0].startsWith("A year, at the targets")), net = info.inc.find(r => r[0].startsWith("A year, net"));
    const payF = D.portfolio_b.ids.filter(id => D.fund_payout[id].freq && INCp.some(x => x.funds.some(r => r.id === id)));
    ck("the income card and the headline table show each portfolio's trailing-12-month payout, fund by fund, at both rates",
      !!tot && !!net && INCp.every((x, k) => tot[k + 1].includes(pz(x.per_1m)) && tot[k + 1].includes(x.ttm_pct.toFixed(2) + "%")
                                   && net[k + 1].includes(pz(x.per_1m_net)) && net[k + 1].includes(x.net_pct.toFixed(2) + "%"))
      && payF.every(id => { const r = info.inc.find(c => c[0].startsWith(D.portfolio_b.shorts[D.portfolio_b.ids.indexOf(id)]));
           return r && INCp.every((x, k) => { const f = x.funds.find(q => q.id === id); return r[k + 1] === (f ? pz(f.per_1m) : "\u2013"); }); })
      && info.ptabInc.length === 2 && INCp.every((x, k) => info.ptabInc[0][k + 1] === x.ttm_pct.toFixed(2) + "%" && info.ptabInc[1][k + 1] === pz(x.per_1m)),
      JSON.stringify(tot) + " " + JSON.stringify(info.ptabInc));
    // v129 (owner, 23 Nov): the payout over the last 12 months against the year before (v127's 1-year return retired)
    const f2 = v => v == null ? "\u2013" : v.toFixed(2) + "%";
    const sg = v => v == null ? "\u2013" : (v > 0 ? "+" : v < 0 ? "\u2212" : "") + Math.abs(v).toFixed(2) + "pp";
    const prY = info.inc.find(r => r[0].startsWith("A year, at " + D.payout_prior_label));
    const payH = D.portfolio_b.ids.filter(id => D.fund_payout[id].freq && INCp.some(x => x.funds.some(r => r.id === id)));
    ck("each portfolio's payout a year earlier, and the change, and each paying fund's two years, are the payload's",
      !!prY && INCp.every((x, k) => prY[k + 1].includes(pz(x.prior_per_1m)) && prY[k + 1].includes(f2(x.prior_pct))
                                    && info.ptabPr[0][k + 1] === f2(x.prior_pct) && info.ptabPr[1][k + 1] === sg(x.change_pp))
      && info.ptabPr.length === 2 && info.pr.length === payH.length && !info.inc.some(r => /^1-year return/.test(r[0]))
      && payH.every((id, i) => info.pr[i][0].startsWith(D.portfolio_b.shorts[D.portfolio_b.ids.indexOf(id)])
                               && info.pr[i][1] === "~" + D.fund_payout[id].ttm.toFixed(1) + "%"
                               && info.pr[i][2] === (D.fund_payout[id].prior == null ? "\u2013" : "~" + D.fund_payout[id].prior.toFixed(1) + "%")),
      JSON.stringify(prY) + " " + JSON.stringify(info.ptabPr));
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
