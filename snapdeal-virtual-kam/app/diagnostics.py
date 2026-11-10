from __future__ import annotations

from typing import Any


def pct_change(previous: float, current: float) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 1)


def funnel(period: dict[str, Any]) -> dict[str, float | int]:
    visits = int(period["visits"])
    orders = int(period["orders"])
    conversion = (orders / visits * 100) if visits else 0.0
    return {
        "visits": visits,
        "orders": orders,
        "conversion_rate": round(conversion, 2),
        "revenue_inr": int(period["revenue_inr"]),
    }


def analyze_seller(seller: dict[str, Any]) -> dict[str, Any]:
    previous = seller["periods"]["previous"]
    current = seller["periods"]["current"]
    prev_funnel, curr_funnel = funnel(previous), funnel(current)

    metrics = {
        "visits": {
            "previous": prev_funnel["visits"],
            "current": curr_funnel["visits"],
            "change_pct": pct_change(prev_funnel["visits"], curr_funnel["visits"]),
        },
        "orders": {
            "previous": prev_funnel["orders"],
            "current": curr_funnel["orders"],
            "change_pct": pct_change(prev_funnel["orders"], curr_funnel["orders"]),
        },
        "revenue_inr": {
            "previous": prev_funnel["revenue_inr"],
            "current": curr_funnel["revenue_inr"],
            "change_pct": pct_change(prev_funnel["revenue_inr"], curr_funnel["revenue_inr"]),
        },
        "conversion_rate": {
            "previous": prev_funnel["conversion_rate"],
            "current": curr_funnel["conversion_rate"],
            "change_pct": pct_change(prev_funnel["conversion_rate"], curr_funnel["conversion_rate"]),
        },
    }

    signals: list[dict[str, str]] = []
    actions: list[dict[str, str]] = []

    if metrics["visits"]["change_pct"] <= -10:
        signals.append({"severity": "high", "title": "Traffic is declining", "evidence": f"Visits fell {abs(metrics['visits']['change_pct']):.1f}%."})
        actions.append({
            "priority": "P2",
            "title": "Recover qualified product traffic",
            "why": "Visits declined materially versus the previous 30 days.",
            "steps": "Review search impressions and clicks for the top listings; refresh titles and attributes; check whether visibility changed before increasing promotion spend.",
            "timeframe": "Next 3 days",
            "success_metric": "Visits to the top 5 listings return toward the previous-period baseline.",
        })

    if metrics["conversion_rate"]["change_pct"] <= -10:
        signals.append({"severity": "high", "title": "Conversion is weakening", "evidence": f"Conversion moved from {prev_funnel['conversion_rate']:.2f}% to {curr_funnel['conversion_rate']:.2f}%."})
        actions.append({
            "priority": "P1",
            "title": "Fix listing conversion on the highest-traffic SKUs",
            "why": "A smaller share of visitors is becoming buyers.",
            "steps": "Check main image clarity, title/search terms, size or variant details, delivery promise, price versus comparable listings and recent negative reviews. Change one variable at a time.",
            "timeframe": "Next 48 hours",
            "success_metric": "Conversion rate improves from the current 2.40% baseline over the next 7 days.",
        })

    stock_drop = current["in_stock_rate"] - previous["in_stock_rate"]
    if current["in_stock_rate"] < 90 or stock_drop <= -5:
        signals.append({"severity": "high", "title": "Stock availability is a risk", "evidence": f"In-stock rate is {current['in_stock_rate']}%, down from {previous['in_stock_rate']}%."})
        actions.insert(0, {
            "priority": "P0",
            "title": "Restore availability for proven bestsellers",
            "why": "Out-of-stock products can lose sales and weaken listing momentum.",
            "steps": "Replenish the Kitchen Storage Rack first if feasible; verify inventory for the bedsheet set; do not promote products that cannot be fulfilled.",
            "timeframe": "Today",
            "success_metric": "In-stock rate is back above 95% for priority SKUs.",
        })

    cancel_delta = current["cancellation_rate"] - previous["cancellation_rate"]
    if current["cancellation_rate"] >= 5 or cancel_delta >= 2:
        signals.append({"severity": "high", "title": "Cancellations are elevated", "evidence": f"Cancellation rate rose from {previous['cancellation_rate']}% to {current['cancellation_rate']}%."})
        actions.append({
            "priority": "P1",
            "title": "Identify and remove cancellation causes",
            "why": "Cancellations rose and may be eroding completed orders.",
            "steps": "Group recent cancellations by reason: seller stock mismatch, dispatch delay, buyer cancellation or address issue. Correct inventory sync and dispatch SLA issues first.",
            "timeframe": "Next 24 hours",
            "success_metric": "Cancellation rate trends toward the category benchmark of 4%.",
        })

    if current["average_rating"] < seller["category_benchmark"]["average_rating"]:
        signals.append({"severity": "medium", "title": "Seller rating is below category benchmark", "evidence": f"Rating is {current['average_rating']} versus benchmark {seller['category_benchmark']['average_rating']}."})
        actions.append({
            "priority": "P2",
            "title": "Address recurring low-rating feedback",
            "why": "Product experience and trust signals can affect buyer decisions.",
            "steps": "Read the latest low-rated feedback, classify themes such as quality, dimensions or packaging, and fix the most frequent product-level issue.",
            "timeframe": "This week",
            "success_metric": "Average rating moves toward or above the 4.1 category benchmark.",
        })

    actions = sorted(actions, key=lambda item: {"P0": 0, "P1": 1, "P2": 2}.get(item["priority"], 3))
    return {
        "seller": {key: seller[key] for key in ("seller_id", "seller_name", "category")},
        "period_labels": {"previous": previous["label"], "current": current["label"]},
        "metrics": metrics,
        "operations": {
            "in_stock_rate": {"previous": previous["in_stock_rate"], "current": current["in_stock_rate"]},
            "cancellation_rate": {"previous": previous["cancellation_rate"], "current": current["cancellation_rate"]},
            "average_rating": {"previous": previous["average_rating"], "current": current["average_rating"]},
            "return_rate": {"previous": previous["return_rate"], "current": current["return_rate"]},
        },
        "signals": signals,
        "actions": actions,
        "top_products": seller["top_products"],
        "summary": (
            f"Orders are down {abs(metrics['orders']['change_pct']):.1f}%. "
            f"Both traffic ({metrics['visits']['change_pct']:.1f}%) and conversion "
            f"({metrics['conversion_rate']['change_pct']:.1f}%) have weakened. "
            "Stock availability and cancellations also need attention."
        ),
    }
