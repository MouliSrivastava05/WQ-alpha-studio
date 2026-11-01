"""
WorldQuant FastExpr Validator and Linter.
Validates syntax, catches common pitfall bugs, prevents simulation failures,
and provides turnover and Sharpe improvement suggestions.
"""

import re
from typing import List, Dict, Any, Tuple

# Standard WorldQuant Brain operators
KNOWN_OPERATORS = {
    # Cross-sectional operators
    "rank", "zscore", "scale", "scale_down", "normalize", "quantile",
    # Group operators
    "group_neutralize", "group_rank", "group_zscore", "group_mean",
    "group_max", "group_min", "group_sum", "group_median",
    # Time-series operators
    "ts_decay_linear", "ts_decay_exp_window", "ts_mean", "ts_sum",
    "ts_std_dev", "ts_variance", "ts_zscore", "ts_rank", "ts_delta",
    "ts_delay", "ts_corr", "ts_covariance", "ts_regression",
    "ts_max", "ts_min", "ts_argmax", "ts_argmin", "ts_skewness", "ts_kurtosis",
    "ts_product", "ts_ir", "ts_percentage",
    # Math & Logic
    "log", "exp", "sqrt", "abs", "sign", "min", "max", "power", "signed_power",
    "if_else", "trade_when", "replace_nan", "is_nan", "nan_mask", "clamp",
    "filter", "density", "bucket"
}

# Standard groupings
KNOWN_GROUPS = {
    "subindustry", "industry", "sector", "market", "country", "exchange"
}

class FastExprValidator:
    """Validates WorldQuant Brain FastExpr code and provides optimization tips."""

    @staticmethod
    def check_balanced_parentheses(expr: str) -> Tuple[bool, str]:
        """Verify matching parentheses and brackets."""
        stack = []
        pairs = {')': '(', ']': '[', '}': '{'}
        
        for i, char in enumerate(expr):
            if char in "([{":
                stack.append((char, i))
            elif char in ")]}":
                if not stack:
                    return False, f"Unmatched closing bracket '{char}' at character {i}"
                top, top_idx = stack.pop()
                if pairs[char] != top:
                    return False, f"Mismatched bracket: opened '{top}' at {top_idx} but closed '{char}' at {i}"
        
        if stack:
            top, top_idx = stack[-1]
            return False, f"Unclosed opening bracket '{top}' at character {top_idx}"
        
        return True, ""

    @classmethod
    def validate(cls, expr: str, settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive validation and linting of an alpha expression."""
        if settings is None:
            settings = {}

        expr = expr.strip()
        errors: List[str] = []
        warnings: List[str] = []
        suggestions: List[str] = []

        if not expr:
            return {
                "valid": False,
                "errors": ["Expression is empty"],
                "warnings": [],
                "suggestions": []
            }

        # 1. Balanced brackets check
        balanced, b_err = cls.check_balanced_parentheses(expr)
        if not balanced:
            errors.append(b_err)

        # 2. Lookahead bias check (negative delay)
        neg_delay = re.findall(r'ts_delay\s*\([^,]+,\s*-\d+\)', expr)
        if neg_delay:
            errors.append(f"Lookahead bias detected! Negative delay found: {neg_delay[0]}")

        # 3. Unsafe division check (division by zero / negative denominator)
        # Check for patterns like / var without + eps
        division_patterns = re.findall(r'/\s*([a-zA-Z0-9_]+)(?!\s*\+)', expr)
        for denom in division_patterns:
            if denom not in ["1", "2", "10", "100", "252"]:
                warnings.append(
                    f"Potential division by zero with denominator '{denom}'. "
                    f"Safeguard with '({denom} + 0.0001)' or 'replace_nan({denom}, 1)'"
                )

        # 4. Decay and Turnover check
        has_ts_decay = "ts_decay_linear" in expr or "ts_decay_exp_window" in expr
        sim_decay = settings.get("decay", 0)
        has_high_turnover_fields = bool(re.search(r'\b(returns|volume|vwap|close\s*-\s*open)\b', expr))

        if has_high_turnover_fields and not has_ts_decay and sim_decay < 3:
            warnings.append(
                "Expression uses high-frequency price/volume fields without ts_decay_linear "
                "or simulation decay >= 3. Turnover is likely to exceed the 70% limit."
            )
            suggestions.append(
                "Wrap with ts_decay_linear(signal, 5) or set simulation decay to 5 to boost Fitness."
            )

        # 5. Cross-sectional ranking check
        if not (expr.startswith("rank(") or expr.startswith("-rank(") or 
                "group_rank(" in expr or "group_neutralize(" in expr or 
                expr.startswith("zscore(")):
            suggestions.append(
                "Top-level signal is not cross-sectionally ranked. Consider wrapping with rank(...) "
                "to normalize stock bets uniformly between 0 and 1."
            )

        # 6. Neutralization check
        setting_neutralization = settings.get("neutralization", "").upper()
        has_expr_neutralize = "group_neutralize" in expr

        if not has_expr_neutralize and setting_neutralization in ["NONE", ""]:
            warnings.append(
                "Alpha has no neutralization applied. Brain requires factor neutralization "
                "to prevent raw market/sector bias."
            )
            suggestions.append(
                "Set simulation setting 'neutralization': 'SUBINDUSTRY' or use group_neutralize(..., subindustry)."
            )

        # 7. Check for unknown function calls
        called_funcs = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', expr)
        for func in set(called_funcs):
            if func not in KNOWN_OPERATORS and func not in ["min", "max", "sum", "mean"]:
                suggestions.append(
                    f"'{func}' is treated as a function. Ensure it exists in the Brain FastExpr documentation."
                )

        # 8. Check log on negative numbers
        if re.search(r'log\s*\(\s*(close|open|returns|volume|adv20)', expr):
            if "returns" in expr:
                warnings.append("Calling log() directly on returns will produce NaN on negative return days. Use log(1 + returns) instead.")

        valid = len(errors) == 0

        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        }

