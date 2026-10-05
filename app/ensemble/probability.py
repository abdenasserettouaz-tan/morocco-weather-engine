from app.grib.parser import nearest_point


def precipitation_probability(ds, lat: float, lon: float) -> float | None:
    """Return an ECMWF probability field at a point as percent.

    ecCodes/cfgrib may expose the probability variable under its GRIB shortName;
    this function intentionally discovers the single data variable instead of
    hard-coding a cfgrib-normalized name.
    """
    p = nearest_point(ds, lat, lon)
    variables = list(p.data_vars)
    if not variables:
        return None
    value = float(p[variables[0]].values)
    # Probability GRIB products may decode as 0..1 or 0..100 depending on metadata.
    if 0.0 <= value <= 1.0:
        value *= 100.0
    return round(max(0.0, min(100.0, value)), 1)
