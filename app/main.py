import os
import pandas as pd
from fastapi import FastAPI
from typing import List, Dict, Any

from .schemas import RecommendRequest, RecommendResponse, RecommendationItem, Evidence
from .rules import suitability_filter
from .market import market_preferences
from .rag import build_or_load_vectorstore, retrieve_evidence
from .agents import recommend_one, audit_one

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OPP_CSV = os.path.join(DATA_DIR, "opportunities.csv")

app = FastAPI(title="Market-aware Investment Opportunity Matching System")

# Load once at startup
vectorstore = None
opportunities: List[Dict[str, Any]] = []

@app.on_event("startup")
def startup():
    global vectorstore, opportunities
    vectorstore = build_or_load_vectorstore()
    df = pd.read_csv(OPP_CSV)
    opportunities = df.to_dict(orient="records")

def base_score(client: Dict[str, Any], product: Dict[str, Any], mweights: Dict[str, float]) -> float:
    
    score = 50.0

    
    risk_gap = client["risk_tolerance"] - int(product["risk_level"])
    score += max(0, 10 - abs(risk_gap) * 3)

    # market weights
    if mweights["prefer_low_risk"] > 0:
        score += (6 - int(product["risk_level"])) * mweights["prefer_low_risk"] * 2

    if mweights["penalize_derivatives"] > 0 and str(product.get("derivatives_exposure", "false")).lower() == "true":
        score -= 20 * mweights["penalize_derivatives"]

    if mweights["prefer_short_lockup"] > 0:
        score += max(0, 14 - int(product["lockup_days"])) * mweights["prefer_short_lockup"] * 0.4

    # fees penalty
    score -= float(product["fees"]) * 1000 
    return float(score)

@app.post("/recommend", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    client = req.client.model_dump()
    market = req.market.model_dump()

    eligible, rejected = suitability_filter(client, opportunities)
    if not eligible:
        return RecommendResponse(recommendations=[], rejected=rejected)

    mweights = market_preferences(market)

    # baseline scoring + sort
    scored = []
    for p in eligible:
        s = base_score(client, p, mweights)
        scored.append((s, p))
    scored.sort(key=lambda x: x[0], reverse=True)

    
    shortlist = scored[: max(req.top_k * 3, 6)]

    rec_items: List[RecommendationItem] = []
    for s, p in shortlist:
        query = f"Client goal={client['goal']}, horizon={client['horizon_months']} months, " \
                f"risk={client['risk_tolerance']}. Market rate={market['interest_rate_trend']}, vol={market['volatility_level']}."
        evidence = retrieve_evidence(vectorstore, query + " " + p["name"], k=4)

        draft = await recommend_one(client, market, p, evidence)
        audit = await audit_one(client, market, p, draft, evidence)

        final = audit["revised"] if not audit.get("is_ok", True) else draft

        item = RecommendationItem(
            product_id=p["product_id"],
            name=p["name"],
            score=float(s),
            why_client_fit=final["why_client_fit"],
            why_market_fit=final["why_market_fit"],
            key_risks=final["key_risks"],
            who_should_not_buy=final["who_should_not_buy"],
            evidence=[Evidence(**e) for e in evidence],
        )
        rec_items.append(item)

    # final top_k
    rec_items.sort(key=lambda x: x.score, reverse=True)
    return RecommendResponse(recommendations=rec_items[: req.top_k], rejected=rejected)

@app.get("/health")
def health():
    return {"ok": True}
