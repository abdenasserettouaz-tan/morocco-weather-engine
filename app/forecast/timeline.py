from app.config import CITIES
from app.downloader.ecmwf import download_deterministic
from app.downloader.gefs import download_gefs_member
from app.grib.parser import open_surface
from app.forecast.morocco import city_forecast
from app.ensemble.agreement import model_agreement

# 0-144 h every 6 h, then 12-hourly to day 15.
FORECAST_STEPS = list(range(0, 145, 6)) + list(range(156, 361, 12))

def build_timeline(city: str, steps=None, include_gefs: bool = True) -> list[dict]:
    if city not in CITIES:
        raise KeyError(city)
    steps = steps or FORECAST_STEPS
    timeline = []
    for step in steps:
        e_ds = open_surface(download_deterministic(step))
        e = city_forecast(e_ds, city)
        item = {"step_hours": step, "day": round(step / 24, 2), "ecmwf": e}
        if include_gefs:
            g_ds = open_surface(download_gefs_member(step, "gec00"))
            g = city_forecast(g_ds, city)
            item["gefs"] = g
            item["agreement"] = model_agreement(e, g)
        timeline.append(item)
    return timeline
