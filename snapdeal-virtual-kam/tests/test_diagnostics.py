import json
from pathlib import Path

from app.diagnostics import analyze_seller

DATA = Path(__file__).resolve().parents[1] / "data" / "seller.json"


def test_sales_funnel_and_drop_are_calculated():
    seller = json.loads(DATA.read_text(encoding="utf-8"))
    result = analyze_seller(seller)
    assert result["metrics"]["visits"]["change_pct"] == -15.0
    assert result["metrics"]["orders"]["change_pct"] == -31.9
    assert result["metrics"]["conversion_rate"]["previous"] == 3.0
    assert result["metrics"]["conversion_rate"]["current"] == 2.4


def test_operational_risks_are_prioritized():
    seller = json.loads(DATA.read_text(encoding="utf-8"))
    result = analyze_seller(seller)
    assert result["signals"]
    assert result["actions"][0]["priority"] == "P0"
    assert any("Cancellations" in signal["title"] for signal in result["signals"])
