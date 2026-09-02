# Changelog

Newest first. Each Sunday job appends here. Every error found gets recorded
before it gets fixed.

## 2026-09-02 — Initial build

- Built `model/engine.py`: volatility term structure by forward-variance
  integration, seven-driver macro gauge, four-region ranking across
  3M/6M/12M/5Y, per-fund return build-up net of all fees, drawdown model,
  full enumeration of the 969 five-percent-granular allocations, scenario grid.
- Baseline portfolio (5-year horizon, no cycle view): **20 / 30 / 25 / 25**
  → 6.98% strategic CAGR, −20.8% expected max drawdown.
- Optimised portfolio (macro-adjusted, drawdown-budgeted): **15 / 45 / 35 / 5**
  → 7.31% CAGR, −18.6% expected max drawdown, return-per-drawdown 0.393.
- Macro gauge: **5.3 / 10**.
- All 12 engine sanity checks pass.
- Chart palette validated for colour-vision safety under `--pairs all`.
- Published to https://claude.ai/code/artifact/307440fd-2952-4b4c-b55c-51725163be31
- Registered the three Sunday routines.

### Known limitations recorded at build time

- `atram.com.ph`, `uitf.com.ph`, `fred.stlouisfed.org`, `bworldonline.com` and
  most primary-source domains are blocked by this environment's egress proxy.
  All figures were therefore verified through `WebSearch` results quoting those
  primary sources, not by direct fetch of the source documents. Job 2 should
  retry direct fetches each week.
- Two target-fund ongoing charges (JPM Asia Equity Dividend, Fidelity Global
  Technology) are estimates at 0.80% and 0.95%. Both are labelled "part est."
  on the page's fee table.
