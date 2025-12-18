import json
import requests
from collections import Counter

API = "http://127.0.0.1:8000/recommend"

MARKETS = [
    {"interest_rate_trend": "rising", "volatility_level": "high"},
    {"interest_rate_trend": "stable", "volatility_level": "medium"},
    {"interest_rate_trend": "falling", "volatility_level": "low"}
]

clients = json.load(open("data/clients.json"))

stats = {
    "total_runs": 0,
    "with_evidence": 0,
    "total_recommendations": 0,
    "total_rejected": 0,
    "top1_changes": 0
}

top1_by_market = {}

for market in MARKETS:
    top1_by_market[str(market)] = {}

    for c in clients:
        payload = {
            "client": c,
            "market": market,
            "top_k": 3
        }
        r = requests.post(API, json=payload).json()
        stats["total_runs"] += 1

        recs = r["recommendations"]
        rej = r["rejected"]

        stats["total_recommendations"] += len(recs)
        stats["total_rejected"] += len(rej)

        if recs:
            if recs[0]["evidence"]:
                stats["with_evidence"] += 1
            top1_by_market[str(market)][c["client_id"]] = recs[0]["product_id"]

# market sensitivity
markets_keys = list(top1_by_market.keys())
for cid in clients:
    cid = cid["client_id"]
    picks = {top1_by_market[m].get(cid) for m in markets_keys}
    if len(picks) > 1:
        stats["top1_changes"] += 1

print("=== Evaluation Summary ===")
print(f"Total runs: {stats['total_runs']}")
print(f"Evidence coverage rate: {stats['with_evidence']/stats['total_runs']:.2%}")
print(f"Avg recommendations per run: {stats['total_recommendations']/stats['total_runs']:.2f}")
print(f"Avg rejected per run: {stats['total_rejected']/stats['total_runs']:.2f}")
print(f"Market-sensitive top1 ratio: {stats['top1_changes']/len(clients):.2%}")
