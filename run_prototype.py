import argparse
import json
from app.downloader.ecmwf import download_ensemble
from app.grib.parser import open_surface
from app.forecast.morocco import city_forecast, arabic_summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", default="tangier")
    parser.add_argument("--step", type=int, default=168)
    args = parser.parse_args()

    path = download_ensemble(args.step)
    ds = open_surface(path)
    result = city_forecast(ds, args.city)
    result["model"] = "ECMWF ENS ensemble mean"
    result["forecast_step_hours"] = args.step
    result["summary_ar"] = arabic_summary(result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
