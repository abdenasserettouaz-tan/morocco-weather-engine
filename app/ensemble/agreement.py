def model_agreement(ecmwf: dict, gefs: dict) -> dict:
    """Transparent V1 cross-model agreement score.

    This is an engineering score, not an official meteorological probability.
    It compares common surface variables and reports the components so the UI
    never presents it as an ECMWF/NOAA-issued confidence value.
    """
    components = {}

    def closeness(name, a, b, tolerance):
        if a is None or b is None:
            return
        delta = abs(a - b)
        components[name] = {
            "difference": round(delta, 2),
            "score": round(max(0.0, 1.0 - delta / tolerance) * 100, 1),
        }

    closeness("temperature", ecmwf.get("temperature_c"), gefs.get("temperature_c"), 8.0)
    closeness("pressure", ecmwf.get("pressure_hpa"), gefs.get("pressure_hpa"), 12.0)
    closeness("wind", ecmwf.get("wind_kmh"), gefs.get("wind_kmh"), 35.0)
    closeness("precipitation", ecmwf.get("total_precip_mm"), gefs.get("total_precip_mm"), 25.0)

    scores = [v["score"] for v in components.values()]
    score = round(sum(scores) / len(scores), 1) if scores else None
    label = None
    if score is not None:
        label = "مرتفع" if score >= 75 else "متوسط" if score >= 50 else "منخفض"
    return {"score_percent": score, "label_ar": label, "components": components,
            "method": "cross-model similarity; not an official forecast probability"}
