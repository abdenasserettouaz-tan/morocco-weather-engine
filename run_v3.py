import argparse
import json

from app.config import CITIES
from app.downloader.ecmwf import download_deterministic, download_daily_precip_probability
from app.downloader.gefs import download_gefs_member
from app.grib.parser import open_surface
from app.forecast.morocco import city_forecast, arabic_summary
from app.ensemble.probability import precipitation_probability
from app.ensemble.agreement import model_agreement
from app.maps.renderer import render_precipitation
from app.maps.synoptic import render_pressure_wind, render_upper_air
from app.downloader.upper_air import download_upper_air
from app.grib.parser import open_pressure_levels


def main():
    ap = argparse.ArgumentParser(description="Morocco Weather Engine V3: ECMWF + NOAA GEFS")
    ap.add_argument("--city", default="tangier", choices=sorted(CITIES))
    ap.add_argument("--step", type=int, default=72)
    ap.add_argument("--rain-threshold", type=int, default=1, choices=[1,5,10,20,25,50,100])
    args = ap.parse_args()

    e_path = download_deterministic(args.step)
    e_ds = open_surface(e_path)
    e = city_forecast(e_ds, args.city)
    e["model"] = "ECMWF IFS"

    start = args.step - 24
    if start >= 0 and start % 12 == 0:
        p_path = download_daily_precip_probability(start, args.rain_threshold)
        p_ds = open_surface(p_path)
        city = CITIES[args.city]
        e["ens_precip_probability_percent"] = precipitation_probability(p_ds, city["lat"], city["lon"])
        e["ens_probability_window_hours"] = [start, args.step]
        e["ens_probability_threshold_mm"] = args.rain_threshold

    g_path = download_gefs_member(args.step, "gec00")
    g_ds = open_surface(g_path)
    g = city_forecast(g_ds, args.city)
    g["model"] = "NOAA GEFS control"

    agreement = model_agreement(e, g)

    # Synoptic products: surface pressure/wind plus 500/850 hPa.
    synoptic_maps = {"pressure_wind": str(render_pressure_wind(e_ds, args.step))}
    upper_path = download_upper_air(args.step)
    upper_ds = open_pressure_levels(upper_path)
    synoptic_maps["500hpa"] = str(render_upper_air(upper_ds, 500, args.step))
    synoptic_maps["850hpa"] = str(render_upper_air(upper_ds, 850, args.step))

    prob = e.get("ens_precip_probability_percent")
    if prob is not None:
        rain_text = (
            f"احتمال تجاوز {args.rain_threshold} مم خلال نافذة 24 ساعة يبلغ {prob}% وفق ECMWF ENS. "
        )
    else:
        rain_text = ""
    confidence_note = (
        "تقارب النموذجين جيد ويزيد الثقة في الاتجاه العام، مع بقاء التفاصيل المحلية قابلة للتغير."
        if agreement["score_percent"] >= 70 else
        "يوجد اختلاف ملحوظ بين النموذجين، لذلك يجب التعامل مع التفاصيل بحذر ومتابعة التحديثات القادمة."
    )
    result = {
        "city": args.city,
        "city_ar": CITIES[args.city]["name_ar"],
        "forecast_step_hours": args.step,
        "ecmwf": e,
        "gefs": g,
        "model_agreement": agreement,
        "analysis_ar": (
            f"تحليل النماذج لمدينة {CITIES[args.city]['name_ar']} عند +{args.step} ساعة. "
            + rain_text
            + f"درجة اتفاق ECMWF وGEFS الحسابية {agreement['score_percent']}% ({agreement['label_ar']}). "
            + confidence_note
            + " درجة الاتفاق هي مؤشر تقارب بين النموذجين وليست احتمالاً رسميًا لحدوث الحالة."
        ),
        "maps": {
            "precipitation": str(render_precipitation(e_ds, args.step)),
            **synoptic_maps,
        },
    }
    e["summary_ar"] = arabic_summary(e)
    g["summary_ar"] = arabic_summary(g)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
