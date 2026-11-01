"""
Curated Library of Proven WorldQuant Brain Alpha Archetypes & Templates.
Covers 10 diverse quantitative strategies rooted in peer-reviewed academic finance
and professional quantitative hedge fund research.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class AlphaTemplate:
    id: str
    name: str
    category: str
    formula: str
    description: str
    rationale: str
    recommended_decay: int
    recommended_neutralization: str
    recommended_universe: str
    expected_turnover: str
    data_fields: List[str]

# 10 Core Financial Quantitative Categories
CATEGORIES = [
    "Fundamental Quality & Accruals",
    "Analyst Revisions & Consensus",
    "Microstructure & Volume Dynamics",
    "Group-Neutralized Momentum",
    "Earnings & Cash Flow Surprises",
    "Relative Value & Multi-Factor",
    "Volatility & Risk Anomalies",
    "Short Interest & Supply Squeeze",
    "Dual-Horizon & Multi-Timeframe",
    "Non-linear Interaction & Conditioning"
]

ALPHA_TEMPLATES: List[AlphaTemplate] = [
    # -------------------------------------------------------------------------
    # 1. Fundamental Quality & Accruals
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="QUAL_01_SLOAN_ACCRUALS",
        name="Sloan Balance Sheet Accruals Anomaly",
        category="Fundamental Quality & Accruals",
        formula="-rank(ts_decay_linear((net_income - cfo) / (assets + 0.0001), 10))",
        description="Firms with high accounting accruals have lower earnings persistence and underperform firms with cash-backed earnings.",
        rationale="Richard Sloan (1996) showed investors fixate on reported net income and overlook non-cash working capital accruals.",
        recommended_decay=8,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Very Low (5% - 15%)",
        data_fields=["net_income", "cfo", "assets"]
    ),
    AlphaTemplate(
        id="QUAL_02_NOVY_MARX_PROFITABILITY",
        name="Novy-Marx Gross Profitability Premium",
        category="Fundamental Quality & Accruals",
        formula="rank(ts_decay_linear((sales - cogs) / (assets + 0.0001), 20))",
        description="Gross profitability scaled by book assets identifies productive capital expenditure that outperforms classic value.",
        rationale="Novy-Marx (2013) demonstrated that profitable firms generate significantly higher returns, independent of price-to-book ratios.",
        recommended_decay=10,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (5% - 12%)",
        data_fields=["sales", "cogs", "assets"]
    ),
    AlphaTemplate(
        id="QUAL_03_CAPITAL_TURNOVER_ACCEL",
        name="Asset Turnover Acceleration",
        category="Fundamental Quality & Accruals",
        formula="rank(ts_decay_linear(ts_delta(sales / (assets + 0.0001), 60), 10))",
        description="Measures the rate of change in capital efficiency: firms speeding up revenue per dollar of assets.",
        rationale="Increasing asset utilization signals strong operational leverage prior to earnings announcements.",
        recommended_decay=8,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (10% - 20%)",
        data_fields=["sales", "assets"]
    ),
    AlphaTemplate(
        id="QUAL_04_OCF_TO_NETINCOME",
        name="Cash Quality of Earnings Divergence",
        category="Fundamental Quality & Accruals",
        formula="rank(ts_decay_linear(cfo / (abs(net_income) + 0.0001), 15))",
        description="Ranks stocks by the ratio of operating cash flow to net income.",
        rationale="Companies converting a high percentage of earnings into raw cash flow have superior solvency and resilience.",
        recommended_decay=6,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (8% - 18%)",
        data_fields=["cfo", "net_income"]
    ),
    AlphaTemplate(
        id="QUAL_05_ROIC_MOMENTUM",
        name="Return on Invested Capital Delta",
        category="Fundamental Quality & Accruals",
        formula="rank(ts_decay_linear(ts_delta(ebit / (assets - fnd6_cash + 0.0001), 60), 10))",
        description="Firms expanding economic return on invested capital over a quarterly lookback.",
        rationale="Rising ROIC attracts institutional rebalancing and signals expanding economic moats.",
        recommended_decay=6,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (12% - 22%)",
        data_fields=["ebit", "assets", "fnd6_cash"]
    ),

    # -------------------------------------------------------------------------
    # 2. Analyst Revisions & Consensus
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="ANALYST_01_TARGET_PRICE_GAP",
        name="Consensus Target Price Upside Gap",
        category="Analyst Revisions & Consensus",
        formula="rank(ts_decay_linear((target_price - close) / (close + 0.0001), 10))",
        description="Go long stocks where the Wall Street consensus price target is far above the current market price.",
        rationale="Large positive spread between analyst target price and current spot price captures underappreciated growth opportunities.",
        recommended_decay=5,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (20% - 35%)",
        data_fields=["target_price", "close"]
    ),
    AlphaTemplate(
        id="ANALYST_02_EPS_REVISION_MOMENTUM",
        name="FY1 EPS Estimate Revision Drift",
        category="Analyst Revisions & Consensus",
        formula="rank(ts_decay_linear(ts_delta(eps_est, 20) / (abs(eps_est) + 0.0001), 10))",
        description="Captures positive momentum in forward 12-month EPS consensus estimates.",
        rationale="Analysts adjust estimates incrementally due to herding behavior, creating persistent upward drift in stock prices.",
        recommended_decay=6,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low to Moderate (15% - 25%)",
        data_fields=["eps_est"]
    ),
    AlphaTemplate(
        id="ANALYST_03_UPGRADE_NET_BREADTH",
        name="Net Analyst Recommendation Upgrades",
        category="Analyst Revisions & Consensus",
        formula="rank(ts_decay_linear(num_upgrades - num_downgrades, 15))",
        description="Tracks net upgrades minus downgrades across covering sell-side analysts.",
        rationale="Brokerage upgrades generate sustained institutional buying waves that persist for weeks.",
        recommended_decay=5,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (20% - 30%)",
        data_fields=["num_upgrades", "num_downgrades"]
    ),
    AlphaTemplate(
        id="ANALYST_04_REVISION_ACCELERATION",
        name="Second Derivative of Analyst Earnings Revisions",
        category="Analyst Revisions & Consensus",
        formula="rank(ts_decay_linear(ts_delta(eps_est, 5) - ts_delta(eps_est, 20), 5))",
        description="Measures accelerating upward revisions before the broader market recognizes the inflection.",
        rationale="Accelerating revisions signal strong inflection points in quarterly corporate fundamentals.",
        recommended_decay=5,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP1000",
        expected_turnover="Moderate (25% - 40%)",
        data_fields=["eps_est"]
    ),

    # -------------------------------------------------------------------------
    # 3. Microstructure & Volume Dynamics
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="MICRO_01_AMIHUD_ILLIQUIDITY_REVERSAL",
        name="Amihud Illiquidity Premium Reversion",
        category="Microstructure & Volume Dynamics",
        formula="-rank(ts_decay_linear(ts_mean(abs(returns) / (volume * close + 0.0001), 20), 5))",
        description="Stocks experiencing temporary extreme illiquidity shocks revert as liquidity providers step in.",
        rationale="Amihud (2002) illiquidity measure captures price impact per dollar volume.",
        recommended_decay=4,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (30% - 45%)",
        data_fields=["returns", "volume", "close"]
    ),
    AlphaTemplate(
        id="MICRO_02_VWAP_MEAN_REVERSION",
        name="VWAP Stretch Mean Reversion",
        category="Microstructure & Volume Dynamics",
        formula="-rank(ts_decay_linear((close - vwap) / (close + 0.0001), 5))",
        description="Stocks closing significantly far above or below their volume-weighted average price revert toward fair value.",
        rationale="Institutional algorithmic execution executes around VWAP; extreme deviations represent temporary liquidity dislocations.",
        recommended_decay=4,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (35% - 50%)",
        data_fields=["close", "vwap"]
    ),
    AlphaTemplate(
        id="MICRO_03_VOLUME_PRICE_CORRELATION",
        name="Volume-Return Alignment Trend",
        category="Microstructure & Volume Dynamics",
        formula="rank(ts_decay_linear(ts_corr(returns, volume / (adv20 + 0.0001), 20), 10))",
        description="Stocks where high volume aligns strictly with positive returns exhibit strong accumulation.",
        rationale="Informed institutional buying expands trading volume on positive return days.",
        recommended_decay=5,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (25% - 38%)",
        data_fields=["returns", "volume", "adv20"]
    ),
    AlphaTemplate(
        id="MICRO_04_CHAIKIN_MONEY_FLOW",
        name="Chaikin Money Flow Persistence",
        category="Microstructure & Volume Dynamics",
        formula="rank(ts_decay_linear(ts_sum(((close - low) - (high - close)) / ((high - low) + 0.0001) * volume, 20) / (ts_sum(volume, 20) + 0.0001), 5))",
        description="Quantifies buying vs selling pressure based on where the close finishes relative to the day's high-low range.",
        rationale="Closing near the day's high on heavy volume signals aggressive accumulation by institutional buyers.",
        recommended_decay=5,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (28% - 42%)",
        data_fields=["close", "high", "low", "volume"]
    ),
    AlphaTemplate(
        id="MICRO_05_HIGH_LOW_SPREAD_EXPANSION",
        name="Normalized Intraday Range Expansion",
        category="Microstructure & Volume Dynamics",
        formula="rank(ts_decay_linear((high - low) / (close + 0.0001) / (ts_std_dev(returns, 20) + 0.0001), 5))",
        description="Detects anomalous range expansion scaled by historical volatility.",
        rationale="Range breakout with low historical noise flags directional institutional momentum.",
        recommended_decay=5,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (30% - 45%)",
        data_fields=["high", "low", "close", "returns"]
    ),

    # -------------------------------------------------------------------------
    # 4. Group-Neutralized Momentum
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="MOM_01_JEGADEESH_TITMAN_RESIDUAL",
        name="Subindustry-Neutral 12M-1M Momentum",
        category="Group-Neutralized Momentum",
        formula="group_neutralize(rank(ts_decay_linear(ts_delay(close, 21) / (ts_delay(close, 252) + 0.0001), 10)), subindustry)",
        description="Classic 12-month momentum skipping the most recent 1-month reversal period, strictly sector-neutralized.",
        rationale="Jegadeesh and Titman (1993) documented the 3-12 month momentum effect, enhanced by removing 1-month short-term reversal.",
        recommended_decay=8,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (12% - 25%)",
        data_fields=["close"]
    ),
    AlphaTemplate(
        id="MOM_02_BETA_RESIDUAL_MOMENTUM",
        name="Residual Idiosyncratic Momentum",
        category="Group-Neutralized Momentum",
        formula="group_neutralize(rank(ts_decay_linear(returns - ts_corr(returns, ts_mean(returns, 1), 60) * ts_mean(returns, 1), 10)), subindustry)",
        description="Momentum stripped of systematic market beta.",
        rationale="Blitz, Pang, and van Vliet (2011) showed residual momentum has twice the Sharpe ratio of total momentum.",
        recommended_decay=6,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (20% - 35%)",
        data_fields=["returns"]
    ),
    AlphaTemplate(
        id="MOM_03_PRICE_RANGE_BREAKOUT",
        name="Proximity to 52-Week High Breakout",
        category="Group-Neutralized Momentum",
        formula="rank(ts_decay_linear(close / (ts_max(high, 252) + 0.0001), 10))",
        description="George and Hwang (2004) 52-week high momentum: stocks trading near 52-week highs outperform.",
        rationale="Investors anchor to past peaks; once broken, information under-reaction drives further gains.",
        recommended_decay=8,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (10% - 22%)",
        data_fields=["close", "high"]
    ),

    # -------------------------------------------------------------------------
    # 5. Earnings & Cash Flow Surprises
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="SURPRISE_01_STANDARDIZED_UNEXPECTED_EPS",
        name="Standardized Unexpected Earnings (SUE)",
        category="Earnings & Cash Flow Surprises",
        formula="rank(ts_decay_linear((eps - eps_est) / (ts_std_dev(eps - eps_est, 120) + 0.0001), 20))",
        description="Normalized earnings surprise relative to historical forecast dispersion.",
        rationale="Post-Earnings Announcement Drift (PEAD): stocks beating consensus drift upward for 60+ trading days.",
        recommended_decay=10,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Very Low (5% - 15%)",
        data_fields=["eps", "eps_est"]
    ),
    AlphaTemplate(
        id="SURPRISE_02_FCF_YIELD_DRIFT",
        name="Free Cash Flow Yield Decayed Trend",
        category="Earnings & Cash Flow Surprises",
        formula="rank(ts_decay_linear((cfo - capex) / (cap + 0.0001), 20))",
        description="Free cash flow divided by market capitalization, smoothed with linear decay.",
        rationale="High FCF yield provides downside cushion and signals capital return capability (dividends/buybacks).",
        recommended_decay=10,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (8% - 18%)",
        data_fields=["cfo", "capex", "cap"]
    ),
    AlphaTemplate(
        id="SURPRISE_03_CASH_CONVERSION_CYCLE",
        name="Cash Conversion Cycle Shortening",
        category="Earnings & Cash Flow Surprises",
        formula="-rank(ts_decay_linear(ts_delta((accounts_receivable + inventory - accounts_payable) / (sales + 0.0001), 60), 10))",
        description="Firms reducing working capital lockup days generate superior organic liquidity.",
        rationale="A shortening cash conversion cycle reflects superior supplier bargaining power and inventory velocity.",
        recommended_decay=8,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (8% - 16%)",
        data_fields=["accounts_receivable", "inventory", "accounts_payable", "sales"]
    ),

    # -------------------------------------------------------------------------
    # 6. Relative Value & Multi-Factor
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="VAL_01_SECTOR_NEUTRAL_EBITDA_YIELD",
        name="Subindustry Relative EV/EBITDA",
        category="Relative Value & Multi-Factor",
        formula="group_neutralize(rank(ts_decay_linear(ebitda / (cap + total_debt - fnd6_cash + 0.0001), 20)), subindustry)",
        description="Enterprise Multiple (EBITDA / EV) neutralized within subindustry peer groups.",
        rationale="Enterprise value accounts for capital structure differences across companies in the same industry.",
        recommended_decay=10,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Very Low (5% - 14%)",
        data_fields=["ebitda", "cap", "total_debt", "fnd6_cash"]
    ),
    AlphaTemplate(
        id="VAL_02_BUFFETT_QUALITY_VALUE",
        name="Quality at a Reasonable Price (QARP)",
        category="Relative Value & Multi-Factor",
        formula="rank(group_rank(ts_decay_linear(ebit / (assets + 0.0001), 20), subindustry)) + rank(group_rank(ts_decay_linear(ebit / (cap + 0.0001), 20), subindustry))",
        description="Combines high Return on Capital with low price-to-earnings within subindustry.",
        rationale="Asness, Frazzini, and Pedersen (2019) demonstrated Quality-Minus-Junk yields superior Sharpe when crossed with value.",
        recommended_decay=10,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (6% - 15%)",
        data_fields=["ebit", "assets", "cap"]
    ),

    # -------------------------------------------------------------------------
    # 7. Volatility & Risk Anomalies
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="VOL_01_LOW_VOLATILITY_ANOMALY",
        name="Idiosyncratic Low Volatility Alpha",
        category="Volatility & Risk Anomalies",
        formula="-rank(ts_decay_linear(ts_std_dev(returns, 60), 10))",
        description="Baker, Bradley, and Wurgler (2011): low volatility stocks consistently generate higher risk-adjusted returns.",
        rationale="Lottery ticket preferences and leverage constraints cause retail and institutional investors to overpay for high-beta stocks.",
        recommended_decay=8,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (10% - 20%)",
        data_fields=["returns"]
    ),
    AlphaTemplate(
        id="VOL_02_DOWNSIDE_BETA_ASYMMETRY",
        name="Downside Semi-Variance Penalty",
        category="Volatility & Risk Anomalies",
        formula="-rank(ts_decay_linear(ts_mean((returns < 0 ? power(returns, 2) : 0), 60), 10))",
        description="Penalizes stocks exhibiting elevated negative semi-variance (downside tail risk).",
        rationale="Ang, Chen, and Xing (2006) showed investors demand compensation for downside crash sensitivity.",
        recommended_decay=8,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Low (12% - 22%)",
        data_fields=["returns"]
    ),

    # -------------------------------------------------------------------------
    # 8. Short Interest & Supply Squeeze
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="SHORT_01_DAYS_TO_COVER_CONTRACTION",
        name="Short Interest Cover Contraction",
        category="Short Interest & Supply Squeeze",
        formula="-rank(ts_decay_linear(ts_delta(days_to_cover, 20), 10))",
        description="Identifies decreasing days-to-cover or short unwinds.",
        rationale="Short sellers covering their positions produce persistent buying support and reduce downside overhang.",
        recommended_decay=6,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (18% - 30%)",
        data_fields=["days_to_cover"]
    ),

    # -------------------------------------------------------------------------
    # 9. Dual-Horizon & Multi-Timeframe Blends
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="BLEND_01_DUAL_HORIZON_MOMENTUM",
        name="Dual-Decay Medium-Term Trend",
        category="Dual-Horizon & Multi-Timeframe",
        formula="0.6 * rank(ts_decay_linear(ts_delta(close, 20) / (close + 0.0001), 5)) + 0.4 * rank(ts_decay_linear(ts_delta(close, 60) / (close + 0.0001), 10))",
        description="Blends 1-month and 3-month momentum with asymmetric smoothing decay.",
        rationale="Multi-timeframe blending smooths transition noise and produces higher continuous Sharpe across market regimes.",
        recommended_decay=6,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (20% - 32%)",
        data_fields=["close"]
    ),

    # -------------------------------------------------------------------------
    # 10. Non-linear Interaction & Conditioning
    # -------------------------------------------------------------------------
    AlphaTemplate(
        id="INTERACT_01_QUALITY_MOMENTUM_MULTIPLIER",
        name="Quality Multiplied by Momentum",
        category="Non-linear Interaction & Conditioning",
        formula="rank(ts_decay_linear(cfo / (net_income + 0.0001), 20)) * rank(ts_decay_linear(ts_delta(close, 60), 10))",
        description="Nonlinear interaction: momentum in stocks with superior cash flow quality yields high alpha with lower drawdowns.",
        rationale="Momentum driven by real cash flow compounding has far greater duration than speculative hype.",
        recommended_decay=6,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (18% - 30%)",
        data_fields=["cfo", "net_income", "close"]
    ),
    AlphaTemplate(
        id="INTERACT_02_ANALYST_REVISION_VOLUME_SHOCK",
        name="Analyst Upgrade on Volume Expansion",
        category="Non-linear Interaction & Conditioning",
        formula="rank(ts_decay_linear(ts_delta(eps_est, 10), 5)) * rank(ts_decay_linear(volume / (adv20 + 0.0001), 5))",
        description="Conditions analyst EPS revisions on institutional trading volume confirmation.",
        rationale="Earnings estimate upgrades backed by above-average volume signal institutional commitment rather than retail noise.",
        recommended_decay=5,
        recommended_neutralization="SUBINDUSTRY",
        recommended_universe="TOP3000",
        expected_turnover="Moderate (25% - 38%)",
        data_fields=["eps_est", "volume", "adv20"]
    )
]

def get_templates_by_category(category: Optional[str] = None) -> List[AlphaTemplate]:
    """Retrieve templates, optionally filtered by category."""
    if not category:
        return ALPHA_TEMPLATES
    return [t for t in ALPHA_TEMPLATES if t.category.lower() == category.lower()]

def get_template_by_id(alpha_id: str) -> Optional[AlphaTemplate]:
    """Lookup a specific template by its identifier."""
    for t in ALPHA_TEMPLATES:
        if t.id.lower() == alpha_id.lower():
            return t
    return None

