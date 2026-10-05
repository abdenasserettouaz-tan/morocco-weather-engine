from fastapi import FastAPI, HTTPException
from app.config import CITIES, DATA_DIR
from app.grib.parser import open_surface
from app.forecast.morocco import city_forecast, arabic_summary

app = FastAPI(title="Morocco Weather Engine", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "engine": "Morocco Weather Engine V1"}


@app.get("/cities")
def cities():
    return CITIES


@app.get("/forecast/{city}")
def forecast(city: str, step: int = 168):
    if city not in CITIES:
        raise HTTPException(404, "Unknown city")
    path = DATA_DIR / f"ecmwf_ens_{step:03d}h.grib2"
    if not path.exists():
        raise HTTPException(503, f"Forecast GRIB not downloaded for +{step}h")
    ds = open_surface(path)
    result = city_forecast(ds, city)
    result["model"] = "ECMWF ENS ensemble mean"
    result["forecast_step_hours"] = step
    result["summary_ar"] = arabic_summary(result)
    return result
