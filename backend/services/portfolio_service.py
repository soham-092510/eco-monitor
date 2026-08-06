# =====================================================================
# ECO MONITOR — PORTFOLIO_SERVICE.PY (SERVICE)
# Purpose: Compiles sustainability scorecards and runs the portfolio
#          rebalancing optimization algorithm balancing risk, returns, and ESG targets.
# =====================================================================

# Import Session from SQLAlchemy ORM
from sqlalchemy.orm import Session

# Import CarbonRecord and CarbonCredit models
from backend.models.carbon_record import CarbonRecord
from backend.models.carbon_credit import CarbonCredit
from backend.models.account import Account

# Import DB query helper
from sqlalchemy import func

# Import typing utilities
from typing import Dict, List


def get_user_portfolio_summary(db: Session, user_id: str) -> Dict:
    # Compile portfolio statistics
    # WHY:
    # - Summarizes carbon footprint, credits owned, net position, and sustainability index
    
    # 1. Calculate total emissions logged by user
    emissions_sum = db.query(func.sum(CarbonRecord.amount)).filter(
        CarbonRecord.user_id == user_id
    ).scalar() or 0.0
    
    # 2. Calculate total active carbon credits owned by user
    credits_sum = db.query(func.sum(CarbonCredit.amount)).filter(
        CarbonCredit.user_id == user_id,
        CarbonCredit.status == "active"
    ).scalar() or 0.0
    
    # 3. Compute net balance position
    net_balance = credits_sum - emissions_sum
    
    # 4. Compute sustainability score (0-100 index)
    # WHY:
    # - Dynamic formula: Base 50, increases/decreases based on net balance relative to emissions
    if emissions_sum == 0:
        sustainability_score = 100 if credits_sum > 0 else 50
    else:
        ratio = credits_sum / emissions_sum
        sustainability_score = min(100, max(0, int(ratio * 50)))
        
    return {
        "total_emissions": float(emissions_sum),
        "total_credits": float(credits_sum),
        "net_balance": float(net_balance),
        "sustainability_score": int(sustainability_score)
    }


def rebalance_portfolio_optimization(
    db: Session,
    user_id: str,
    target_esg: int,  # Target ESG score (0 to 10 scale)
    risk_level: str   # Risk Level: "low", "medium", "high"
) -> Dict:
    # Portfolio rebalancing optimization engine
    # WHY:
    # - Implements a mathematical model determining target allocations across asset types
    # - Suggests execution orders if drift exceeds 5%
    
    # Define asset class characteristics
    # - Wind: Low risk, Medium ESG (8/10), Medium Return
    # - Solar: Medium risk, High ESG (9/10), High Return
    # - Forestry: High risk, Ultra ESG (10/10), Variable Return
    asset_types = ["wind", "solar", "forestry"]
    
    # 1. Retrieve current carbon credits holdings grouped by type
    credits = db.query(CarbonCredit).filter(
        CarbonCredit.user_id == user_id,
        CarbonCredit.status == "active"
    ).all()
    
    total_holdings = sum(c.amount for c in credits)
    
    current_allocation = {t: 0.0 for t in asset_types}
    if total_holdings > 0:
        for c in credits:
            if c.credit_type.lower() in current_allocation:
                current_allocation[c.credit_type.lower()] += c.amount
                
        # Normalize to percentages (0.0 to 1.0)
        for t in current_allocation:
            current_allocation[t] /= total_holdings
            
    # 2. Determine target allocations based on user input parameters
    # WHY:
    # - Solves allocation targets using simple optimization heuristics
    targets = {"wind": 0.33, "solar": 0.33, "forestry": 0.34}  # Default equal weights
    
    if risk_level == "low":
        # Prioritize wind (low risk)
        targets = {"wind": 0.60, "solar": 0.30, "forestry": 0.10}
    elif risk_level == "medium":
        # Balanced
        targets = {"wind": 0.30, "solar": 0.50, "forestry": 0.20}
    elif risk_level == "high":
        # Aggressive yield
        targets = {"wind": 0.10, "solar": 0.40, "forestry": 0.50}
        
    # Adjust targets dynamically towards higher ESG types if target_esg is high
    if target_esg >= 9:
        # Increase forestry (ESG = 10) and solar (ESG = 9) allocation
        targets["forestry"] = min(0.70, targets["forestry"] + 0.15)
        targets["solar"] = min(0.70, targets["solar"] + 0.05)
        # Reduce wind to balance total sum = 1.0
        targets["wind"] = max(0.05, 1.0 - targets["forestry"] - targets["solar"])
        
    # 3. Calculate portfolio drift & generate orders list
    # WHY:
    # - Compares target allocation vs. current holdings. If diff > 5%, creates trade order recommendations
    orders = []
    
    # If user has no assets, suggest initial purchase targets
    if total_holdings == 0:
        for asset, weight in targets.items():
            orders.append({
                "action": "buy",
                "asset_type": asset,
                "percentage": round(weight * 100, 1),
                "suggested_amount": round(weight * 100.0, 2),  # Target base metric
                "reason": f"Initial portfolio purchase for {asset} to meet targets"
            })
    else:
        for asset in asset_types:
            drift = current_allocation[asset] - targets[asset]
            # If drift is substantial (e.g. > 5%), generate recommended order
            if abs(drift) > 0.05:
                action = "sell" if drift > 0 else "buy"
                order_percent = abs(drift)
                orders.append({
                    "action": action,
                    "asset_type": asset,
                    "percentage": round(order_percent * 100, 1),
                    "suggested_amount": round(order_percent * total_holdings, 2),
                    "reason": f"Portfolio rebalancing due to {asset} drift of {round(drift * 100, 1)}%"
                })
                
    return {
        "current_allocation_pct": {k: round(v * 100, 1) for k, v in current_allocation.items()},
        "target_allocation_pct": {k: round(v * 100, 1) for k, v in targets.items()},
        "rebalance_required": len(orders) > 0,
        "recommended_orders": orders
    }
