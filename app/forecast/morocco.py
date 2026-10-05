import math
from app.config import CITIES
from app.grib.parser import nearest_point


def _value(point, names):
    for name in names:
        if name in point:
            return float(point[name].values)
    return None


def city_forecast(ds, city_key: str) -> dict:
    city = CITIES[city_key]
    p = nearest_point(ds, city["lat"], city["lon"])
    t = _value(p, ["t2m", "2t"])
    msl = _value(p, ["msl", "prmsl"])
    u = _value(p, ["u10", "10u"])
    v = _value(p, ["v10", "10v"])
    tp = _value(p, ["tp"])
    wind_ms = math.hypot(u, v) if u is not None and v is not None else None
    return {
        "city": city_key,
        "city_ar": city["name_ar"],
        "latitude": city["lat"],
        "longitude": city["lon"],
        "temperature_c": round(t - 273.15, 1) if t is not None else None,
        "pressure_hpa": round(msl / 100, 1) if msl is not None else None,
        "wind_kmh": round(wind_ms * 3.6, 1) if wind_ms is not None else None,
        "total_precip_mm": round(tp * 1000, 1) if tp is not None else None,
    }


def arabic_summary(f: dict) -> str:
    pieces = [f"التوقع لمدينة {f['city_ar']}."]
    if f["temperature_c"] is not None:
        pieces.append(f"درجة الحرارة المتوقعة نحو {f['temperature_c']}°م.")
    if f["pressure_hpa"] is not None:
        pieces.append(f"الضغط عند سطح البحر {f['pressure_hpa']} hPa.")
    if f["wind_kmh"] is not None:
        pieces.append(f"سرعة الرياح نحو {f['wind_kmh']} كم/س.")
    if f["total_precip_mm"] is not None:
        pieces.append(f"إجمالي الهطول في الحقل المتاح {f['total_precip_mm']} مم.")
    return " ".join(pieces)
