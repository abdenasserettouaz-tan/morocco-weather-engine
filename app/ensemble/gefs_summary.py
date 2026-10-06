from __future__ import annotations

from statistics import mean, pstdev

from app.forecast.morocco import city_forecast
from app.grib.parser import open_surface
from app.downloader.gefs import download_gefs_member

GEFS_PERTURBED_MEMBERS = [f"gep{i:02d}" for i in range(1, 31)]


def _stats(values: list[float]) -> dict:
    if not values:
        return {"mean": None, "spread": None, "min": None, "max": None}
    return {
        "mean": round(mean(values), 2),
        "spread": round(pstdev(values), 2) if len(values) > 1 else 0.0,
        "min": round(min(values), 2),
        "max": round(max(values), 2),
    }


def build_gefs_summary(
    city: str,
    step: int,
    members: list[str] | None = None,
    minimum_members: int = 2,
) -> dict:
    """Build a point summary from real NOAA GEFS perturbed members.

    The result is an application-computed ensemble summary, not an official
    NOAA event-probability product.
    """
    members = members or GEFS_PERTURBED_MEMBERS
    forecasts = []
    failures = []
    for member in members:
        try:
            f = city_forecast(open_surface(download_gefs_member(step, member)), city)
            f["member"] = member
            forecasts.append(f)
        except Exception as exc:
            failures.append({"member": member, "error": str(exc)})

    if len(forecasts) < minimum_members:
        raise RuntimeError(
            f"Only {len(forecasts)} GEFS members available; minimum is {minimum_members}"
        )

    def values(key):
        return [float(f[key]) for f in forecasts if f.get(key) is not None]

    return {
        "source": "NOAA/NCEP GEFS perturbed members",
        "requested_member_count": len(members),
        "available_member_count": len(forecasts),
        "members": [f["member"] for f in forecasts],
        "temperature_c": _stats(values("temperature_c")),
        "pressure_hpa": _stats(values("pressure_hpa")),
        "wind_kmh": _stats(values("wind_kmh")),
        "total_precip_mm": _stats(values("total_precip_mm")),
        "official_probability": False,
        "semantics": "application-computed ensemble mean/spread/range from NOAA GEFS members",
        "note_ar": "هذه إحصاءات محسوبة من أعضاء GEFS وليست احتمال حدث رسميًا صادرًا عن NOAA.",
        "failed_member_count": len(failures),
    }
