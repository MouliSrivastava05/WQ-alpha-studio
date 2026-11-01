# WorldQuant Brain Alpha Studio
### The Complete Research Consultant Operating System & Daily Alpha Engine

Welcome to **WorldQuant Alpha Studio**, an end-to-end quantitative research toolkit engineered specifically for **WorldQuant Brain Research Consultants**. It equips you with the exact formulas, combinatorial synthesizers, syntax linters, and backtest tracking tools necessary to generate and submit high-Sharpe, high-fitness alphas consistently every day.

---

## 🚀 Quickstart: Submit Your First Alphas Today

### 1. Launch the Interactive Web Dashboard
```bash
cd /Users/moulisrivastava/.gemini/antigravity/scratch/wq-alpha-studio
python3 cli.py serve
```
Open **`http://localhost:8888`** in your browser to access the complete graphical suite:
- **Daily Quotas & Target Gauge**: Real-time progress toward your daily submission target.
- **Systematic Synthesizer**: 1-click generation of fresh candidate alphas across 10 categories.
- **Archetype Library**: Browse 80+ peer-reviewed quant alpha archetypes with citations.
- **FastExpr Linter & Sandbox**: Immediate syntax, bracket, lookahead, and turnover checking.
- **Submission Backlog**: Full SQLite journal tracking Sharpe, Turnover, Fitness, and Margin.

---

### 2. Generate Today's Batch via CLI
```bash
# Generate 10 diverse, non-correlated candidate alphas
python3 cli.py daily --count 10

# Generate specific category alphas (fundamental, analyst, microstructure, interaction)
python3 cli.py generate --theme fundamental --count 5
```

---

### 3. Run the Automated End-to-End Daily Routine
```bash
python3 examples/daily_routine.py
```
This script:
1. Synthesizes 12 diverse alpha candidates across fundamental, analyst, and microstructure signals.
2. Validates syntax and division safety.
3. Simulates backtests and measures Sharpe, Turnover, Fitness, and Drawdown.
4. Filters for alphas passing WorldQuant Brain thresholds.
5. Prints the top 3 submittable candidates ready to submit on the platform!

---

## 🏆 WorldQuant Brain Consultant Submission Criteria

To earn consultant payouts and level up on Brain, submitted alphas must satisfy:

| Metric | Minimum Required | Top Consultant Target | Why it Matters |
| :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | &ge; 1.25 | **&ge; 1.58** | Risk-adjusted return consistency |
| **Turnover** | 1% to 70% | **10% to 35%** | Low turnover preserves returns from trading costs |
| **Fitness** | &ge; 1.0 | **&ge; 1.50** | `Sharpe * sqrt(Returns / Turnover)` |
| **Sub-Universe Sharpe** | PASS | PASS | Must work on TOP1000/TOP500 liquid sub-segments |
| **Correlation** | &lt; 0.70 | **&lt; 0.50** | Must not duplicate your past alphas or platform pool |
| **Margin** | &ge; 8 bps | **&ge; 15 bps** | Return per dollar traded |

---

## 💡 The 5 Golden Rules for Brain Alphas

### Rule 1: Always Smooth High-Frequency Signals with Linear Decay
Raw price/volume signals (`returns`, `close - open`, `volume`) have 150%+ daily turnover, which **fails Brain's 70% turnover limit**.
- Always wrap in `ts_decay_linear(signal, 5)` to `ts_decay_linear(signal, 10)`.
- Or set simulation parameter `"decay": 5` or `"decay": 8`.

### Rule 2: Neutralize by Subindustry
Never submit raw un-neutralized market signals; Brain will reject them for pure factor/sector exposure:
- Either set simulation setting `"neutralization": "SUBINDUSTRY"`.
- Or explicitly wrap in `group_neutralize(rank(...), subindustry)`.

### Rule 3: Always Use Safe Division
Missing or zero fundamental denominator values cause `NaN` errors that fail simulations:
- **Unsafe**: `cfo / net_income`
- **Safe**: `cfo / (abs(net_income) + 0.0001)` or `sales / (assets + 0.0001)`

### Rule 4: Combine Fundamental Quality with Price Momentum
WorldQuant's platform already contains millions of pure momentum alphas. To achieve low platform correlation (< 0.70), cross two distinct dimensions:
```fastexpr
rank(ts_decay_linear(cfo / (net_income + 0.0001), 20)) * rank(ts_decay_linear(ts_delta(close, 60), 10))
```

### Rule 5: Diversify Universes and Regions
Don't just submit `USA TOP3000`. Europe (`EUR TOP1200`) and Asia (`ASI TOP1000`) have far less competition and lower correlation against the global pool!

---

## 📚 10 Core Quantitative Alpha Categories Included

1. **Fundamental Quality & Accruals**: Sloan accrual anomaly, Novy-Marx gross profitability, cash quality of earnings.
2. **Analyst Revisions & Consensus**: Consensus price target upside discount, FY1 EPS revision momentum, net upgrades.
3. **Price-Volume & Microstructure**: Amihud illiquidity shock reversal, VWAP stretch mean-reversion, Chaikin money flow.
4. **Group-Neutralized Momentum**: Jegadeesh-Titman 12M-1M residual momentum, 52-week high breakout proximity.
5. **Earnings & Cash Flow Surprises**: Standardized Unexpected Earnings (SUE post-earnings announcement drift), FCF yield.
6. **Relative Value & Multi-Factor**: Subindustry enterprise multiple (EV/EBITDA), Quality at a Reasonable Price (QARP).
7. **Volatility & Risk Premia**: Idiosyncratic low-volatility anomaly, downside semi-variance asymmetry.
8. **Short Interest Dynamics**: Short days-to-cover contraction, loan utilization squeeze.
9. **Multi-Timeframe Blends**: Dual-horizon momentum blending short and intermediate horizons.
10. **Non-linear Conditioning**: Fundamental quality multipliers and volume-confirmed revision shocks.

---

## 🛠️ CLI Command Reference

| Command | Description |
| :--- | :--- |
| `python3 cli.py daily --count 10` | Synthesize today's balanced batch of candidate alphas |
| `python3 cli.py generate --theme analyst` | Generate analyst sentiment alphas |
| `python3 cli.py validate "<formula>"` | Check syntax, balanced brackets, lookahead, and division safety |
| `python3 cli.py simulate --id <alpha_id>` | Run backtest simulation and log results |
| `python3 cli.py submit --id <alpha_id>` | Mark alpha as submitted and update daily consultant quota |
| `python3 cli.py status` | View today's simulations and submissions versus target |
| `python3 cli.py archetypes` | Browse 80+ peer-reviewed alpha archetypes |
| `python3 cli.py login --user <u> --password <p>` | Connect directly to official WorldQuant Brain REST API |
| `python3 cli.py serve` | Launch the local Web UI server on port 8888 |

---

## 📂 Project Architecture

```
wq-alpha-studio/
├── README.md                      # Complete Consultant Operating Manual
├── config.py                      # Simulation settings, regional presets, and thresholds
├── cli.py                         # Interactive CLI tool
├── core/
│   ├── validator.py               # FastExpr syntax parser, lookahead checker, linter
│   ├── generator.py               # Systematic combinatorial alpha synthesizer
│   └── templates.py               # 80+ Academic & Industry Alpha Archetypes
├── api/
│   └── brain_client.py            # WorldQuant Brain REST API client
├── db/
│   └── alpha_db.py                # SQLite Alpha Journal & daily quota tracking
├── web/
│   ├── server.py                  # Lightweight HTTP & REST server (zero dependencies)
│   └── static/
│       └── index.html             # Sleek dark-mode Web Dashboard UI
└── examples/
    ├── daily_routine.py           # Automated daily generation & simulation routine
    └── curated_high_sharpe.py     # Tested high-conviction alphas across USA, EUR, ASI
```

