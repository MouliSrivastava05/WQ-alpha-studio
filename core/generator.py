"""
WorldQuant Alpha Combinatorial Synthesizer & Mutation Engine.
Systematically generates diverse, mathematically sound alpha formulations
by combining fundamental, price-volume, and analyst signals with time-series
and cross-sectional operators.
"""

import random
from typing import List, Dict, Any, Optional
from core.templates import ALPHA_TEMPLATES, AlphaTemplate
from core.validator import FastExprValidator

# Canonical Signal Primitives (Clean data fields commonly available in WorldQuant Brain)
FUNDAMENTAL_RATIOS = [
    ("(sales - cogs) / (assets + 0.0001)", "Gross profitability to assets"),
    ("cfo / (assets + 0.0001)", "Operating cash flow return on assets"),
    ("ebitda / (cap + total_debt - fnd6_cash + 0.0001)", "Enterprise cash flow yield"),
    ("(net_income - cfo) / (assets + 0.0001)", "Accounting accruals (inverse)"),
    ("sales / (assets + 0.0001)", "Asset turnover efficiency"),
    ("cfo / (abs(net_income) + 0.0001)", "Cash quality of earnings"),
    ("(cfo - capex) / (cap + 0.0001)", "Free cash flow yield"),
    ("retained_earnings / (assets + 0.0001)", "Accumulated earnings quality"),
    ("working_capital / (assets + 0.0001)", "Working capital liquidity buffer"),
    ("(sales - ts_delay(sales, 252)) / (assets + 0.0001)", "Annual sales growth to assets")
]

ANALYST_SIGNALS = [
    ("(target_price - close) / (close + 0.0001)", "Target price upside discount"),
    ("ts_delta(eps_est, 20) / (abs(eps_est) + 0.0001)", "Forward EPS revision rate"),
    ("(num_upgrades - num_downgrades)", "Net recommendation revisions"),
    ("(eps - eps_est) / (ts_std_dev(eps - eps_est, 120) + 0.0001)", "Standardized unexpected earnings"),
    ("ts_delta(target_price, 20) / (target_price + 0.0001)", "Target price upward revision rate")
]

PRICE_VOLUME_SIGNALS = [
    ("(close - vwap) / (close + 0.0001)", "VWAP price displacement (reversion)"),
    ("abs(returns) / (volume * close + 0.0001)", "Amihud price impact illiquidity"),
    ("volume / (adv20 + 0.0001)", "Relative volume surge"),
    ("((close - low) - (high - close)) / ((high - low) + 0.0001)", "Intraday bar close position"),
    ("(high - low) / (close + 0.0001)", "Normalized intraday volatility range"),
    ("returns", "Daily raw return (for residual momentum or low-vol)")
]

LOOKBACK_WINDOWS = [5, 10, 20, 40, 60, 120, 252]
DECAY_PERIODS = [3, 5, 8, 10, 15]
GROUPINGS = ["subindustry", "industry", "sector"]

class AlphaGenerator:
    """Generates and mutates alpha expressions systematically."""

    @staticmethod
    def generate_fundamental_alphas(count: int = 5) -> List[Dict[str, Any]]:
        """Generate fundamental quality and efficiency alphas."""
        alphas = []
        sampled_ratios = random.sample(FUNDAMENTAL_RATIOS, min(count, len(FUNDAMENTAL_RATIOS)))
        
        for ratio_expr, desc in sampled_ratios:
            decay = random.choice([6, 8, 10, 12])
            group = random.choice(["subindustry", "industry"])
            
            # Form variations
            # Pattern A: Group-neutralized decayed rank
            if "accruals" in desc.lower():
                # Sloan accruals is negative predictor
                formula = f"-group_neutralize(rank(ts_decay_linear({ratio_expr}, {decay})), {group})"
            else:
                formula = f"group_neutralize(rank(ts_decay_linear({ratio_expr}, {decay})), {group})"
            
            val = FastExprValidator.validate(formula, {"decay": decay, "neutralization": "SUBINDUSTRY"})
            if val["valid"]:
                alphas.append({
                    "formula": formula,
                    "name": f"Fundamental: {desc}",
                    "category": "Fundamental Quality",
                    "decay": decay,
                    "neutralization": "SUBINDUSTRY",
                    "universe": "TOP3000",
                    "description": f"Decayed {desc} neutralized by {group}."
                })
        return alphas

    @staticmethod
    def generate_analyst_alphas(count: int = 5) -> List[Dict[str, Any]]:
        """Generate analyst revision & sentiment alphas."""
        alphas = []
        sampled = random.sample(ANALYST_SIGNALS, min(count, len(ANALYST_SIGNALS)))
        
        for sig_expr, desc in sampled:
            decay = random.choice([4, 6, 8])
            formula = f"rank(ts_decay_linear({sig_expr}, {decay}))"
            
            val = FastExprValidator.validate(formula, {"decay": decay, "neutralization": "SUBINDUSTRY"})
            if val["valid"]:
                alphas.append({
                    "formula": formula,
                    "name": f"Analyst: {desc}",
                    "category": "Analyst Sentiment",
                    "decay": decay,
                    "neutralization": "SUBINDUSTRY",
                    "universe": "TOP3000",
                    "description": f"Captures market under-reaction to {desc}."
                })
        return alphas

    @staticmethod
    def generate_microstructure_alphas(count: int = 5) -> List[Dict[str, Any]]:
        """Generate price-volume and microstructure reversion/momentum alphas."""
        alphas = []
        for _ in range(count):
            window = random.choice([5, 10, 20])
            decay = random.choice([3, 5, 6])
            
            choice = random.randint(1, 4)
            if choice == 1:
                # VWAP Mean Reversion with Subindustry rank
                formula = f"-group_neutralize(rank(ts_decay_linear((close - vwap) / (close + 0.0001), {decay})), subindustry)"
                desc = "VWAP Displacement Mean Reversion"
            elif choice == 2:
                # Volume Surge confirmation on return
                formula = f"rank(ts_decay_linear(ts_corr(returns, volume / (adv20 + 0.0001), {window}), {decay}))"
                desc = f"{window}D Volume-Return Alignment"
            elif choice == 3:
                # Amihud Illiquidity Reversal
                formula = f"-rank(ts_decay_linear(ts_mean(abs(returns) / (volume * close + 0.0001), {window}), {decay}))"
                desc = f"{window}D Amihud Illiquidity Shock Reversal"
            else:
                # Chaikin Money Flow variation
                formula = f"rank(ts_decay_linear(ts_sum(((close - low) - (high - close)) / ((high - low) + 0.0001) * volume, {window}) / (ts_sum(volume, {window}) + 0.0001), {decay}))"
                desc = f"{window}D Order Flow Pressure"
                
            val = FastExprValidator.validate(formula, {"decay": decay, "neutralization": "SUBINDUSTRY"})
            if val["valid"]:
                alphas.append({
                    "formula": formula,
                    "name": f"Microstructure: {desc}",
                    "category": "Microstructure",
                    "decay": decay,
                    "neutralization": "SUBINDUSTRY",
                    "universe": "TOP3000",
                    "description": f"Microstructure alpha targeting {desc}."
                })
        return alphas

    @staticmethod
    def generate_interaction_alphas(count: int = 5) -> List[Dict[str, Any]]:
        """Combine fundamental or analyst quality with price momentum (Nonlinear interaction)."""
        alphas = []
        for _ in range(count):
            fund_expr, fund_desc = random.choice(FUNDAMENTAL_RATIOS[:5])
            mom_lookback = random.choice([20, 60, 120])
            decay = random.choice([5, 8, 10])
            
            formula = (
                f"rank(ts_decay_linear({fund_expr}, {decay})) * "
                f"rank(ts_decay_linear(ts_delta(close, {mom_lookback}) / (close + 0.0001), 5))"
            )
            
            desc = f"{fund_desc} x {mom_lookback}D Price Momentum"
            val = FastExprValidator.validate(formula, {"decay": decay, "neutralization": "SUBINDUSTRY"})
            if val["valid"]:
                alphas.append({
                    "formula": formula,
                    "name": f"Interaction: {desc}",
                    "category": "Nonlinear Interaction",
                    "decay": decay,
                    "neutralization": "SUBINDUSTRY",
                    "universe": "TOP3000",
                    "description": f"Multiplies quality ({fund_desc}) with medium-term trend to isolate resilient compounders."
                })
        return alphas

    @classmethod
    def generate_daily_batch(cls, total_alphas: int = 10) -> List[Dict[str, Any]]:
        """Generates a well-balanced daily portfolio of diverse alpha candidates ready for simulation."""
        batch = []
        per_type = max(2, total_alphas // 4)
        
        batch.extend(cls.generate_fundamental_alphas(per_type))
        batch.extend(cls.generate_analyst_alphas(per_type))
        batch.extend(cls.generate_microstructure_alphas(per_type))
        batch.extend(cls.generate_interaction_alphas(per_type))
        
        # Deduplicate by formula
        seen = set()
        unique_batch = []
        for alpha in batch:
            if alpha["formula"] not in seen:
                seen.add(alpha["formula"])
                unique_batch.append(alpha)
                
        return unique_batch[:total_alphas]

