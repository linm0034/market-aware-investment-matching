from typing import Dict, Any, List, Tuple

def _liquidity_max_lockup(liq: str) -> int:
    
    return {"High": 14, "Med": 90, "Low": 3650}.get(liq, 90)

def suitability_filter(
    client: Dict[str, Any],
    products: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    eligible = []
    rejected = []

    max_lock = _liquidity_max_lockup(client["liquidity_need"])
    no_deriv = "No-derivatives" in client.get("constraints", [])
    esg_only = "ESG-only" in client.get("constraints", [])

    for p in products:
        reasons = []

        if int(p["risk_level"]) > int(client["risk_tolerance"]):
            reasons.append("Exceeds client's risk tolerance")

        if int(p["lockup_days"]) > max_lock:
            reasons.append("Lock-up period does not meet liquidity needs")

        if no_deriv and str(p.get("derivatives_exposure", "false")).lower() == "true":
            reasons.append("Client constraint: No-derivatives")

        if esg_only and str(p.get("esg", "false")).lower() != "true":
            reasons.append("Client constraint: ESG-only")

        if reasons:
            rejected.append({"product_id": p["product_id"], "reason": "; ".join(reasons)})
        else:
            eligible.append(p)

    return eligible, rejected
