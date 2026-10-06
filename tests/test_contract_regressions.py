from app.analysis.arabic import build_arabic_analysis
from app.forecast.daily import daily_from_accumulated, extended_probabilistic_trend


def test_daily_precipitation_is_deaccumulated():
    points = [
        {"step_hours": 24, "ecmwf": {"temperature_c": 12, "wind_kmh": 20, "total_precip_mm": 4}},
        {"step_hours": 48, "ecmwf": {"temperature_c": 15, "wind_kmh": 25, "total_precip_mm": 11}},
    ]
    cards = daily_from_accumulated(points)
    assert [x["daily_precip_mm"] for x in cards] == [4.0, 7.0]


def test_extended_trend_never_claims_official_probability():
    trend = extended_probabilistic_trend([
        {"day": 8, "temperature_c": {"mean": 18, "spread": 3}, "total_precip_mm": {"mean": 5}}
    ])
    assert trend["deterministic"] is False
    assert trend["official_probability"] is False


def test_arabic_analysis_never_claims_official_warning():
    forecast = {"city_ar": "طنجة", "temperature_c": 20, "pressure_hpa": 1005, "wind_kmh": 80, "total_precip_mm": 30}
    analysis = build_arabic_analysis(forecast, [])
    assert analysis["warning"] is False
    assert "ليس نشرة إنذار رسمية" in analysis["warning_note_ar"]
    assert analysis["impact_score"] >= 2
