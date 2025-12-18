import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(DATA_DIR, "docs")

os.makedirs(DOCS_DIR, exist_ok=True)

products = [
    # product_id, name, type, risk_level, lockup_days, fees, derivatives_exposure, esg
    ("opp_001", "Short Duration Bond Fund", "fund", 2, 7, 0.006, "false", "true"),
    ("opp_002", "Leveraged Equity Note", "structured", 5, 180, 0.012, "true", "false"),
    ("opp_003", "Money Market Fund", "fund", 1, 1, 0.002, "false", "true"),
    ("opp_004", "Investment Grade Corporate Bond Fund", "fund", 2, 30, 0.007, "false", "true"),
    ("opp_005", "High Yield Bond Fund", "fund", 4, 90, 0.010, "false", "false"),
    ("opp_006", "Global Dividend Equity Fund", "fund", 3, 30, 0.009, "false", "true"),
    ("opp_007", "Tech Growth Equity Fund", "fund", 4, 60, 0.010, "false", "false"),
    ("opp_008", "US Treasury Ladder (1-3Y)", "bond", 1, 7, 0.003, "false", "true"),
    ("opp_009", "Floating Rate Note Basket", "bond", 2, 14, 0.006, "false", "false"),
    ("opp_010", "Capital Protected Note (80% protection)", "structured", 3, 365, 0.011, "true", "false"),
    ("opp_011", "ESG Global Balanced Fund", "fund", 3, 30, 0.008, "false", "true"),
    ("opp_012", "Gold Defensive Allocation Fund", "fund", 3, 14, 0.009, "false", "true"),
    ("opp_013", "EM Local Currency Bond Fund", "fund", 4, 180, 0.011, "false", "false"),
    ("opp_014", "Private Credit Income Fund", "alternative", 4, 730, 0.014, "false", "false"),
    ("opp_015", "REITs Income Fund", "fund", 3, 60, 0.010, "false", "true"),
    ("opp_016", "Structured Range Accrual Note", "structured", 5, 365, 0.015, "true", "false"),
    ("opp_017", "Short-Term SGD Fixed Deposit Promo", "deposit", 1, 30, 0.000, "false", "true"),
    ("opp_018", "FX Hedged Global Bond Fund", "fund", 3, 90, 0.010, "true", "true"),
    ("opp_019", "Low Volatility Equity Fund", "fund", 2, 30, 0.008, "false", "true"),
    ("opp_020", "Thematic AI Innovation Equity Fund", "fund", 4, 90, 0.011, "false", "false"),
]

doc_templates = {
    "fund": """# {name}
**Type:** Fund  
**Risk Level:** {risk_level}/5  
**Liquidity/Lock-up:** Typically {lockup_days} days lock-up or settlement constraints.

## Investment Objective
Designed for clients seeking {objective} aligned with a {risk_desc} risk appetite.

## How It Works
The fund allocates across {assets}. Returns are driven by {drivers}.

## Suitable For
- Clients with goal: {goal_fit}
- Horizon: {horizon_fit}
- Risk tolerance: {risk_fit}

## Key Risks
- Market risk, NAV fluctuations
- {extra_risk}

## Not Suitable For
- Clients with {not_fit}

## Fees
Management/ongoing fees may apply (approx. {fees}).
""",
    "bond": """# {name}
**Type:** Bond / Bond Basket  
**Risk Level:** {risk_level}/5  
**Lock-up:** {lockup_days} days (liquidity constraints may apply)

## Summary
Provides exposure to {assets}. Typically suited for {goal_fit} oriented portfolios.

## Key Characteristics
- Return source: {drivers}
- Sensitivity: {rate_sens}

## Key Risks
- Interest rate risk
- Credit risk (if applicable)
- Liquidity risk

## Not Suitable For
- {not_fit}

## Fees
Estimated fees: {fees}.
""",
    "structured": """# {name}
**Type:** Structured Product  
**Risk Level:** {risk_level}/5  
**Lock-up:** {lockup_days} days  
**Complexity:** Higher (payoff may be non-linear)

## Summary
A structured opportunity linked to {assets}. Potential for enhanced payoff under certain conditions, but may involve principal loss.

## Payoff Intuition
Returns depend on {drivers}. Outcomes can vary significantly across market scenarios.

## Suitable For
- Experienced / higher risk tolerance clients (typically risk {risk_fit})
- Longer horizon clients who can tolerate illiquidity

## Key Risks
- Derivatives/complex payoff risk
- Potential loss of principal
- Liquidity/early exit risk
- Issuer/credit risk (if applicable)

## Not Suitable For
- Conservative investors or clients requiring high liquidity
- Clients who do not understand complex payoff structures

## Fees
Estimated fees/spreads: {fees}.
""",
    "alternative": """# {name}
**Type:** Alternative / Private Markets  
**Risk Level:** {risk_level}/5  
**Lock-up:** {lockup_days} days (illiquid)

## Summary
Seeks income via {assets}. Designed for longer-term investors who can tolerate illiquidity.

## Suitable For
- Long horizon clients, income-focused, higher risk tolerance
- Clients who accept limited redemption windows

## Key Risks
- Illiquidity risk
- Credit/default risk
- Valuation/pricing lag
- Concentration risk

## Not Suitable For
- Clients requiring liquidity or short horizons

## Fees
Estimated fees: {fees}.
""",
    "deposit": """# {name}
**Type:** Deposit  
**Risk Level:** {risk_level}/5  
**Tenor/Lock-up:** {lockup_days} days

## Summary
Capital preservation focused product with predictable interest accrual.

## Suitable For
- Conservative investors
- Short horizon / high liquidity need clients

## Key Risks
- Reinvestment risk
- Opportunity cost if rates rise further

## Fees
Typically none (fees: {fees}).
""",
}

def meta_for(p):
    # simple “market-aware-ish” descriptors for variety
    rid = int(p[0].split("_")[1])
    objectives = ["income", "capital preservation", "balanced growth", "growth"]
    assets_list = [
        "short-duration investment grade bonds",
        "investment grade corporate bonds",
        "high yield credit",
        "global dividend equities",
        "low volatility equities",
        "US Treasuries ladder",
        "floating-rate notes",
        "gold and defensive assets",
        "EM bonds",
        "REITs",
        "AI/innovation equities",
        "mixed asset allocation"
    ]
    drivers_list = [
        "coupon carry and credit spreads",
        "equity dividends and quality factor",
        "rate movements and duration exposure",
        "credit spread compression/expansion",
        "macro theme performance and sector rotation",
        "structured payoff conditions and underlying index paths"
    ]
    rate_sens = ["low duration sensitivity", "moderate duration sensitivity", "higher duration sensitivity"][rid % 3]
    objective = objectives[rid % len(objectives)]
    assets = assets_list[rid % len(assets_list)]
    drivers = drivers_list[rid % len(drivers_list)]

    risk_level = int(p[3])
    risk_desc = ["very low", "low", "moderate", "high", "very high"][risk_level - 1]

    goal_fit = "Income / Preservation" if risk_level <= 2 else ("Balanced Growth" if risk_level == 3 else "Growth")
    horizon_fit = "short-to-medium term (6–24 months)" if int(p[4]) <= 30 else ("medium term (1–3 years)" if int(p[4]) <= 365 else "long term (3+ years)")
    risk_fit = f"{max(1, risk_level-1)}–{risk_level}"
    extra_risk = "credit risk and spread volatility" if risk_level >= 3 else "inflation / reinvestment risk"
    not_fit = "short horizon or low risk tolerance" if risk_level >= 4 else "seeking aggressive growth or unwilling to accept NAV fluctuations"
    return dict(
        objective=objective,
        assets=assets,
        drivers=drivers,
        rate_sens=rate_sens,
        risk_desc=risk_desc,
        goal_fit=goal_fit,
        horizon_fit=horizon_fit,
        risk_fit=risk_fit,
        extra_risk=extra_risk,
        not_fit=not_fit
    )

def main():
    # write CSV
    csv_path = os.path.join(DATA_DIR, "opportunities.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["product_id","name","type","risk_level","lockup_days","fees","derivatives_exposure","esg"])
        for p in products:
            w.writerow(p)

    # write docs
    for p in products:
        product_id, name, typ, risk_level, lockup_days, fees, deriv, esg = p
        meta = meta_for(p)
        tpl = doc_templates.get(typ, doc_templates["fund"])
        content = tpl.format(
            name=name,
            risk_level=risk_level,
            lockup_days=lockup_days,
            fees=fees,
            assets=meta["assets"],
            drivers=meta["drivers"],
            objective=meta["objective"],
            risk_desc=meta["risk_desc"],
            goal_fit=meta["goal_fit"],
            horizon_fit=meta["horizon_fit"],
            risk_fit=meta["risk_fit"],
            extra_risk=meta["extra_risk"],
            not_fit=meta["not_fit"],
            rate_sens=meta["rate_sens"],
        )
        out_path = os.path.join(DOCS_DIR, f"{product_id}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

    print("✅ Generated:")
    print(f"- {csv_path}")
    print(f"- {DOCS_DIR}/*.md  ({len(products)} files)")

if __name__ == "__main__":
    main()
