from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from app.config import CITIES, DATA_DIR
from app.grib.parser import open_surface
from app.forecast.morocco import city_forecast, arabic_summary
from app.forecast.timeline import FORECAST_STEPS, build_timeline
from app.api.schemas import EngineMeta
from app.maps.metadata import map_metadata

app = FastAPI(
    title="Morocco Weather Engine",
    version="0.10.0",
    description="ECMWF + NOAA GEFS weather engine for Morocco and NW Africa",
)

# Generated weather maps are served read-only to mobile/web clients.
app.mount("/maps", StaticFiles(directory=str(DATA_DIR.parent / "output")), name="maps")

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


@app.get("/mobile/{city}")
def mobile(
    city: str,
    step: int = Query(72, ge=0, le=360),
    rain_threshold: int = Query(1),
    include_gefs: bool = True,
    gefs_members: int = Query(5, ge=2, le=30),
    include_daily: bool = True,
):
    """Unified payload contract for the mobile client.

    V1 intentionally reads/downloads only the requested forecast step. The
    complete 15-day timeline remains a separate endpoint until ingestion/cache
    precomputes it, avoiding dozens of network downloads per mobile request.
    """
    if city not in CITIES:
        raise HTTPException(404, "Unknown city")
    if rain_threshold not in {1, 5, 10, 20, 25, 50, 100}:
        raise HTTPException(400, "Unsupported precipitation threshold")

    from app.downloader.ecmwf import download_deterministic, download_daily_precip_probability
    from app.downloader.gefs import download_gefs_member
    from app.ensemble.agreement import model_agreement
    from app.ensemble.probability import precipitation_probability
    from app.ensemble.uncertainty import pressure_uncertainty
    from app.downloader.ecmwf import download_ens_mean_pressure, download_ens_spread_pressure
    from app.ensemble.gefs_summary import build_gefs_summary, GEFS_PERTURBED_MEMBERS
    from app.forecast.daily import daily_from_accumulated, extended_probabilistic_trend
    from app.analysis.arabic import affected_cities, build_arabic_analysis

    try:
        e = city_forecast(open_surface(download_deterministic(step)), city)
        e["model"] = "ECMWF IFS"
        e["forecast_step_hours"] = step

        g = None
        agreement = None
        if include_gefs:
            g = city_forecast(open_surface(download_gefs_member(step, "gec00")), city)
            g["model"] = "NOAA GEFS control"
            g["forecast_step_hours"] = step
            agreement = model_agreement(e, g)

        gefs_ensemble = None
        if include_gefs:
            try:
                gefs_ensemble = build_gefs_summary(
                    city, step, members=GEFS_PERTURBED_MEMBERS[:gefs_members]
                )
            except Exception:
                gefs_ensemble = None

        # Daily cards use 24 h boundaries so precipitation can be de-accumulated.
        # Limit this to the requested day; full 15-day ingestion/cache is a separate job.
        daily_points = []
        if include_daily:
            day_end = max(24, min(360, ((step + 23) // 24) * 24))
            for daily_step in range(24, day_end + 1, 24):
                d = city_forecast(open_surface(download_deterministic(daily_step)), city)
                daily_points.append({"step_hours": daily_step, "ecmwf": d})
        daily_cards = daily_from_accumulated(daily_points)

        # Expose an 8-15 day ensemble trend only when the requested step is in
        # the extended range. This avoids pretending a single deterministic
        # value is a long-range probabilistic forecast.
        extended_inputs = []
        if include_gefs and step >= 192:
            try:
                extended = build_gefs_summary(
                    city, step, members=GEFS_PERTURBED_MEMBERS[:gefs_members]
                )
                extended["day"] = round(step / 24, 2)
                extended_inputs.append(extended)
            except Exception:
                pass
        extended_trend = extended_probabilistic_trend(extended_inputs)

        city_cfg = CITIES[city]
        uncertainty = None
        try:
            mean_ds = open_surface(download_ens_mean_pressure(step))
            spread_ds = open_surface(download_ens_spread_pressure(step))
            uncertainty = pressure_uncertainty(
                mean_ds, spread_ds, city_cfg["lat"], city_cfg["lon"]
            )
        except Exception:
            # ENS mean/spread is additive metadata; keep the base forecast usable
            # if a specific ENS product is temporarily unavailable.
            uncertainty = None

        official_probability = None
        if step >= 24:
            start_hour = step - 24
            try:
                prob_ds = open_surface(
                    download_daily_precip_probability(start_hour, rain_threshold)
                )
                probability = precipitation_probability(
                    prob_ds, city_cfg["lat"], city_cfg["lon"]
                )
                official_probability = {
                    "probability_percent": probability,
                    "threshold_mm": rain_threshold,
                    "window_start_hour": start_hour,
                    "window_end_hour": step,
                    "source": "ECMWF ENS type=ep",
                    "official_probability": True,
                }
            except Exception:
                # Probability is optional in this contract: deterministic/model
                # data remains usable when the requested EP window is unavailable.
                official_probability = None
    except Exception as exc:
        raise HTTPException(503, f"Model data unavailable: {exc}") from exc

    affected = affected_cities(open_surface(download_deterministic(step)))
    analysis = build_arabic_analysis(e, affected, uncertainty, agreement)

    return {
        "meta": {
            **EngineMeta().model_dump(),
            "api_version": "0.10.0",
            "city": city,
            "city_ar": CITIES[city]["name_ar"],
            "forecast_step_hours": step,
        },
        "current": e,
        "day_cards": daily_cards,
        "extended_trend_8_15_days": extended_trend,
        "timeline": [
            {
                "step_hours": step,
                "day": round(step / 24, 2),
                "ecmwf": e,
                **({"gefs": g} if g is not None else {}),
            }
        ],
        "official_probabilities": {
            "ecmwf_ens_precipitation": official_probability,
            "note_ar": "هذا الاحتمال رسمي من منتج ECMWF ENS probability عندما تكون البيانات متاحة.",
        },
        "gefs_ensemble": gefs_ensemble or {
            "source": "NOAA/NCEP GEFS perturbed members",
            "requested_member_count": gefs_members if include_gefs else 0,
            "available_member_count": 0,
            "official_probability": False,
            "semantics": "application-computed ensemble mean/spread/range from NOAA GEFS members",
            "note_ar": "ملخص أعضاء GEFS غير متاح لهذه الخطوة حالياً؛ لم يتم اختلاق قيم بديلة.",
        },
        "ensemble_uncertainty": uncertainty or {
            "ecmwf_ens_mean_pressure_hpa": None,
            "ecmwf_ens_pressure_spread_hpa": None,
            "uncertainty_label_ar": None,
            "source_mean": "ECMWF ENS type=em",
            "source_spread": "ECMWF ENS type=es",
            "official_probability": False,
            "note_ar": "بيانات ENS mean/spread غير متاحة لهذه الخطوة حالياً؛ لم يتم اختلاق قيمة بديلة.",
        },
        "cross_model_agreement": {
            **(agreement or {"score_percent": None, "label_ar": None, "components": {}}),
            "official_probability": False,
            "note_ar": "درجة الاتفاق مؤشر حسابي لتقارب ECMWF وGEFS وليست احتمالاً رسميًا لحدوث الحالة.",
        },
        "maps": {
            **map_metadata(step),
            "available_layers": ["precipitation", "pressure_wind", "500hpa", "850hpa"],
        },
        "layers": [
            {"id": "precipitation", "label_ar": "الهطول"},
            {"id": "pressure_wind", "label_ar": "الضغط والرياح"},
            {"id": "500hpa", "label_ar": "طبقة 500 hPa"},
            {"id": "850hpa", "label_ar": "طبقة 850 hPa"},
        ],
        "analysis_ar": analysis["headline_ar"] + " " + analysis["regional_ar"] + " " + analysis["confidence_ar"],
        "analysis": analysis,
        "affected_cities": affected,
    }
