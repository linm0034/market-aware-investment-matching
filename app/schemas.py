from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

RiskLabel = Literal["Conservative", "Balanced", "Aggressive"]
GoalLabel = Literal["Income", "Growth", "Preservation"]
VolLabel = Literal["low", "medium", "high"]
RateTrend = Literal["rising", "stable", "falling"]

class ClientProfile(BaseModel):
    client_id: str = "demo_client"
    risk_tolerance: int = Field(ge=1, le=5)
    horizon_months: int = Field(ge=1, le=600)
    goal: GoalLabel
    liquidity_need: Literal["Low", "Med", "High"]
    constraints: List[str] = []  # e.g. ["ESG-only", "No-derivatives"]

class MarketContext(BaseModel):
    interest_rate_trend: RateTrend = "stable"
    volatility_level: VolLabel = "medium"
    macro_theme: Optional[str] = None

class RecommendRequest(BaseModel):
    client: ClientProfile
    market: MarketContext = MarketContext()
    top_k: int = 3

class Evidence(BaseModel):
    doc_id: str
    snippet: str

class RecommendationItem(BaseModel):
    product_id: str
    name: str
    score: float
    why_client_fit: str
    why_market_fit: str
    key_risks: List[str]
    who_should_not_buy: List[str]
    evidence: List[Evidence]

class RecommendResponse(BaseModel):
    recommendations: List[RecommendationItem]
    rejected: List[Dict[str, Any]]  # {product_id, reason}
