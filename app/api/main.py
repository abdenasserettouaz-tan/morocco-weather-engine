from fastapi import FastAPI, HTTPException, Query
from app.config import CITIES, DATA_DIR
from app.grib.parser import open_surface
from app.forecast.morocco import city_forecast, arabic_summary
from app.forecast.timeline import FORECAST_STEPS, build_timeline
from app.api.schemas import EngineMeta

app = FastAPI(
    title="Morocco Weather Engine",
    version="0.5.0",
    description="ECMWF + NOAA GEFS weather engine for Morocco and NW Africa",
)

@app.get("/health")
def health():
    return {"status": "ok", **EngineMeta().model_dump()}

@app.get("/meta")
def meta():
    return {**EngineMeta().model_dump(), "timeline_steps_hours": FORECAST_STEPS}

@app.get("/cities")
def cities():
    return CITIES

@app.get("/forecast/{city}")
def forecast(city: str, step: int = Query(168, ge=0, le=360)):
    if city not in CITIES:
        raise HTTPException(404, "Unknown city")
    path = DATA_DIR / f"ecmwf_ifs_{step:03d}h.grib2"
    if not path.exists():
        raise HTTPException(503, f"Forecast GRIB not downloaded for +{step}h")
    ds = open_surface(path)
    result = city_forecast(ds, city)
    result["model"] = "ECMWF IFS"
    result["forecast_step_hours"] = step
    result["summary_ar"] = arabic_summary(result)
    return result

@app.get("/timeline/{city}")
def timeline(
    city: str,
    start: int = Query(0, ge=0, le=360),
    end: int = Query(360, ge=0, le=360),
    include_gefs: bool = True,
):
    if city not in CITIES:
        raise HTTPException(404, "Unknown city")
    if start > end:
        raise HTTPException(400, "start must be <= end")
    steps = [s for s in FORECAST_STEPS if start <= s <= end]
    try:
        data = build_timeline(city, steps=steps, include_gefs=include_gefs)
    except Exception as exc:
        raise HTTPException(503, f"Model data unavailable: {exc}") from exc
    return {
        "city": city,
        "city_ar": CITIES[city]["name_ar"],
        "horizon_hours": end,
        "models": ["ECMWF IFS"] + (["NOAA GEFS control"] if include_gefs else []),
        "timeline": data,
        "agreement_note_ar": "درجة الاتفاق مؤشر حسابي لتقارب النموذجين وليست احتمالاً رسميًا.",
    }
