from typing import Dict, Any

def market_preferences(market: Dict[str, Any]) -> Dict[str, float]:
    
    rate = market.get("interest_rate_trend", "stable")
    vol = market.get("volatility_level", "medium")

    weights = {
        "prefer_low_risk": 0.0,
        "penalize_derivatives": 0.0,
        "prefer_short_lockup": 0.0,
    }

    if vol == "high":
        weights["prefer_low_risk"] += 0.6
        weights["penalize_derivatives"] += 0.6

    if rate == "rising":
        weights["prefer_short_lockup"] += 0.4

    return weights
