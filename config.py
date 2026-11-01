"""
WorldQuant Brain Alpha Studio - Configuration
Defines default settings, Brain simulation parameters, targets, and regions.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, List

# Base URL for WorldQuant Brain API
BRAIN_API_BASE_URL = "https://api.worldquantbrain.com"

# Default Submission Quality Thresholds (Brain Consultant Standards)
MIN_SHARPE = 1.25            # Minimum acceptable Sharpe ratio for submission (ideally > 1.58)
PREFERRED_SHARPE = 1.58      # Gold standard for top-tier consultant compensation
MIN_FITNESS = 1.0            # Minimum Fitness = Sharpe * sqrt(abs(Returns) / max(Turnover, 0.125))
PREFERRED_FITNESS = 1.5      # Preferred fitness
MIN_TURNOVER = 0.01          # 1% minimum turnover (to avoid static non-trading portfolios)
MAX_TURNOVER = 0.70          # 70% maximum turnover (Brain cutoff; best is 5% - 35%)
PREFERRED_MAX_TURNOVER = 0.35# 35% target max turnover to prevent high execution costs
MIN_MARGIN_BPS = 8.0         # Minimum margin in basis points (returns / volume traded)
MAX_DRAWDOWN = 0.20          # Max acceptable historical drawdown (20%)
MAX_SELF_CORRELATION = 0.70  # Max correlation against your own submitted alphas

# Common Simulation Settings Presets
DEFAULT_SIMULATION_SETTINGS: Dict[str, Any] = {
    "instrumentType": "EQUITY",
    "region": "USA",
    "universe": "TOP3000",
    "delay": 1,              # Delay 1: standard for daily trading (no lookahead bias)
    "decay": 5,              # Linear decay reduces turnover significantly
    "neutralization": "SUBINDUSTRY",  # SUBINDUSTRY is Brain gold standard
    "truncation": 0.08,      # Maximum weight per stock (8%)
    "pasteurization": "ON",  # Outlier smoothing
    "unitHandling": "VERIFY",
    "nanHandling": "OFF",
    "language": "FASTEXPR",
    "visualization": False
}

# Regional Universes supported by Brain
REGIONS_AND_UNIVERSES: Dict[str, List[str]] = {
    "USA": ["TOP3000", "TOP1000", "TOP500", "MINVOL1M", "SP500"],
    "EUR": ["TOP1200", "TOP600", "TOP400"],
    "ASI": ["TOP1000", "TOP500"],
    "CHN": ["TOP2000", "TOP1000"],
    "GLB": ["TOP3000", "TOP2000"]
}

# Supported Neutralizations
NEUTRALIZATIONS = [
    "SUBINDUSTRY",
    "INDUSTRY",
    "SECTOR",
    "MARKET",
    "NONE"
]

# Credentials storage path
CREDENTIALS_PATH = os.path.expanduser("~/.brain_credentials.json")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "alphas.sqlite")

