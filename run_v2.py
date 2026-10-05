import argparse
import json
from app.config import CITIES
from app.downloader.ecmwf import download_deterministic, download_daily_precip_probability
from app.grib.parser import open_surface
from app.forecast.morocco import city_forecast, arabic_summary
from app.ensemble.probability import precipitation_probability
from app.maps.renderer import render_precipitation


def main():
    ap = argparse.ArgumentParser(description="Morocco Weather Engine ECMWF V2")
    ap.add_argument("--city", default="tangier", choices=sorted(CITIES))
    ap.add_argument("--step", type=int, default=168)
    ap.add_argument("--rain-threshold", type=int, default=1, choices=[1, 5, 10, 20, 25, 50, 100])
    args = ap.parse_args()

    deterministic_path = download_deterministic(args.step)
    ds = open_surface(deterministic_path)
    result = city_forecast(ds, args.city)
    result.update({"model": "ECMWF IFS", "forecast_step_hours": args.step})

    # Daily ENS probability window ending at the requested forecast step.
    start = args.step - 24
    if start >= 0 and start % 12 == 0:
        prob_path = download_daily_precip_probability(start, args.rain_threshold)
        prob_ds = open_surface(prob_path)
        city = CITIES[args.city]
        result["ens_precip_probability_percent"] = precipitation_probability(
            prob_ds, city["lat"], city["lon"]
        )
        result["ens_probability_window_hours"] = [start, args.step]
        result["ens_probability_threshold_mm"] = args.rain_threshold

    result["summary_ar"] = arabic_summary(result)
    result["map"] = str(render_precipitation(ds, args.step))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
