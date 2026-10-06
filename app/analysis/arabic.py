from __future__ import annotations

from app.config import CITIES
from app.forecast.morocco import city_forecast


def _severity(f: dict) -> tuple[int, list[str]]:
    score = 0
    reasons = []
    rain = f.get("total_precip_mm")
    wind = f.get("wind_kmh")
    temp = f.get("temperature_c")
    pressure = f.get("pressure_hpa")
    if rain is not None:
        if rain >= 50: score += 4; reasons.append("أمطار غزيرة جداً")
        elif rain >= 20: score += 3; reasons.append("أمطار غزيرة")
        elif rain >= 5: score += 1; reasons.append("أمطار")
    if wind is not None:
        if wind >= 70: score += 4; reasons.append("رياح قوية جداً")
        elif wind >= 45: score += 2; reasons.append("رياح قوية")
    if temp is not None:
        if temp >= 40: score += 3; reasons.append("حرارة شديدة")
        elif temp >= 35: score += 1; reasons.append("حرارة مرتفعة")
        elif temp <= 0: score += 3; reasons.append("برودة شديدة")
        elif temp <= 5: score += 1; reasons.append("برودة")
    if pressure is not None and pressure <= 995:
        score += 1; reasons.append("ضغط جوي منخفض")
    return score, reasons


def affected_cities(ds, minimum_score: int = 1) -> list[dict]:
    affected = []
    for key in CITIES:
        f = city_forecast(ds, key)
        score, reasons = _severity(f)
        if score >= minimum_score:
            affected.append({
                "city": key, "city_ar": f["city_ar"], "impact_score": score,
                "reasons_ar": reasons, "temperature_c": f.get("temperature_c"),
                "wind_kmh": f.get("wind_kmh"), "total_precip_mm": f.get("total_precip_mm"),
            })
    return sorted(affected, key=lambda x: x["impact_score"], reverse=True)


def build_arabic_analysis(forecast: dict, affected: list[dict], uncertainty: dict | None = None,
                          agreement: dict | None = None) -> dict:
    score, reasons = _severity(forecast)
    level = "مرتفع" if score >= 5 else "متوسط" if score >= 2 else "منخفض"
    city_names = [x["city_ar"] for x in affected[:5]]
    if reasons:
        headline = f"أبرز الظواهر المتوقعة قرب {forecast['city_ar']}: " + "، ".join(reasons) + "."
    else:
        headline = f"لا تظهر مؤشرات جوية بارزة قرب {forecast['city_ar']} في هذه الخطوة."
    regional = ("المدن الأكثر تأثراً ضمن نقاط الرصد الحالية: " + "، ".join(city_names) + ".") if city_names else "لا توجد مدن تتجاوز عتبة التأثير الحالية."
    confidence = []
    if uncertainty and uncertainty.get("uncertainty_label_ar"):
        confidence.append(f"تشتت ECMWF ENS {uncertainty['uncertainty_label_ar']}.")
    if agreement and agreement.get("label_ar"):
        confidence.append(f"اتفاق ECMWF وGEFS {agreement['label_ar']}، وهو مؤشر تقارب وليس احتمالاً رسمياً.")
    return {
        "headline_ar": headline,
        "regional_ar": regional,
        "impact_level_ar": level,
        "impact_score": score,
        "signals_ar": reasons,
        "affected_cities": affected,
        "confidence_ar": " ".join(confidence) if confidence else "بيانات الثقة الإضافية غير متاحة.",
        "method": "rule-based analysis of model fields at configured Moroccan city points",
        "warning": False,
        "warning_note_ar": "هذا تحليل آلي للنماذج وليس نشرة إنذار رسمية.",
    }
