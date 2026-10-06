from app.grib.parser import nearest_point


def _first_value(ds, lat: float, lon: float) -> float | None:
    point = nearest_point(ds, lat, lon)
    variables = list(point.data_vars)
    if not variables:
        return None
    return float(point[variables[0]].values)


def pressure_uncertainty(mean_ds, spread_ds, lat: float, lon: float) -> dict:
    """Describe official ECMWF ENS MSL-pressure mean/spread at a point.

    The spread is ensemble standard deviation, not an event probability.
    The qualitative band is an application interpretation exposed transparently.
    """
    mean_pa = _first_value(mean_ds, lat, lon)
    spread_pa = _first_value(spread_ds, lat, lon)
    mean_hpa = round(mean_pa / 100.0, 1) if mean_pa is not None else None
    spread_hpa = round(abs(spread_pa) / 100.0, 2) if spread_pa is not None else None

    label = None
    if spread_hpa is not None:
        label = "منخفض" if spread_hpa < 2.5 else "متوسط" if spread_hpa < 5.0 else "مرتفع"

    return {
        "ecmwf_ens_mean_pressure_hpa": mean_hpa,
        "ecmwf_ens_pressure_spread_hpa": spread_hpa,
        "uncertainty_label_ar": label,
        "source_mean": "ECMWF ENS type=em",
        "source_spread": "ECMWF ENS type=es",
        "spread_semantics": "ensemble standard deviation of mean sea-level pressure",
        "official_probability": False,
        "interpretation_method": "app qualitative band: <2.5 hPa low; 2.5-<5 hPa medium; >=5 hPa high",
        "note_ar": "الـ spread هو تشتت أعضاء ECMWF ENS حول المتوسط وليس احتمالاً رسميًا لحدوث حالة جوية.",
    }
