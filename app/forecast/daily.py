from __future__ import annotations


def daily_from_accumulated(points: list[dict]) -> list[dict]:
    """Aggregate forecast points into day cards.

    ECMWF IFS total_precip_mm is accumulated since initialization, therefore
    daily precipitation is the positive difference between successive daily
    boundary accumulations, never the raw accumulated value.
    """
    if not points:
        return []
    by_day = {}
    for item in sorted(points, key=lambda x: x["step_hours"]):
        day = max(1, (int(item["step_hours"]) + 23) // 24)
        by_day.setdefault(day, []).append(item)

    cards = []
    previous_accum = 0.0
    for day, items in sorted(by_day.items()):
        temps = [x["ecmwf"].get("temperature_c") for x in items if x["ecmwf"].get("temperature_c") is not None]
        winds = [x["ecmwf"].get("wind_kmh") for x in items if x["ecmwf"].get("wind_kmh") is not None]
        last_accum = items[-1]["ecmwf"].get("total_precip_mm")
        daily_precip = None
        if last_accum is not None:
            daily_precip = round(max(0.0, float(last_accum) - previous_accum), 1)
            previous_accum = float(last_accum)
        cards.append({
            "day": day,
            "end_step_hours": items[-1]["step_hours"],
            "temperature_min_c": round(min(temps), 1) if temps else None,
            "temperature_max_c": round(max(temps), 1) if temps else None,
            "wind_max_kmh": round(max(winds), 1) if winds else None,
            "daily_precip_mm": daily_precip,
            "precipitation_semantics": "difference of ECMWF IFS accumulated precipitation at daily boundaries",
        })
    return cards


def extended_probabilistic_trend(
    gefs_summaries: list[dict],
    start_day: int = 8,
    end_day: int = 15,
) -> dict:
    """Summarise days 8-15 using ensemble statistics, not deterministic certainty."""
    usable = [x for x in gefs_summaries if start_day <= x.get("day", 0) <= end_day]
    temp_means = [x["temperature_c"]["mean"] for x in usable if x.get("temperature_c", {}).get("mean") is not None]
    temp_spreads = [x["temperature_c"]["spread"] for x in usable if x.get("temperature_c", {}).get("spread") is not None]
    precip_means = [x["total_precip_mm"]["mean"] for x in usable if x.get("total_precip_mm", {}).get("mean") is not None]

    return {
        "period_days": [start_day, end_day],
        "basis": "NOAA GEFS perturbed-member ensemble statistics",
        "deterministic": False,
        "official_probability": False,
        "available_steps": len(usable),
        "temperature_mean_c": round(sum(temp_means) / len(temp_means), 1) if temp_means else None,
        "temperature_mean_spread_c": round(sum(temp_spreads) / len(temp_spreads), 1) if temp_spreads else None,
        "ensemble_accumulated_precip_mean_mm": round(sum(precip_means) / len(precip_means), 1) if precip_means else None,
        "note_ar": "اتجاه الأيام 8–15 مبني على إحصاءات أعضاء GEFS ويعرض الاتجاه وعدم اليقين، وليس توقعاً حتمياً أو احتمالاً رسمياً لحدث.",
    }
