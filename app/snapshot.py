from __future__ import annotations

import argparse
import json
import shutil
from fastapi import HTTPException
from datetime import datetime, timezone
from pathlib import Path

from app.api.main import mobile
from app.downloader.ecmwf import download_deterministic
from app.grib.parser import open_surface
from app.maps.renderer import render_precipitation
from app.maps.synoptic import render_pressure_wind
from app.config import CITIES, OUTPUT_DIR, ROOT

DEFAULT_STEPS = [72, 192, 240, 288, 360]


def _json_default(value):
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Not JSON serializable: {type(value)!r}")


def build_snapshot(out_dir: Path, cities: list[str], steps: list[int], gefs_members: int = 3) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copy2(ROOT / "app" / "mobile" / "index.html", out_dir / "index.html")
    (out_dir / "runtime-config.js").write_text(
        'window.WEATHER_STATIC=true;\n', encoding="utf-8"
    )

    # Generate the two surface map layers that are available from the
    # deterministic surface GRIB used by the static client. Upper-air layers
    # remain explicitly unavailable until their pressure-level GRIB is ingested.
    for map_step in steps:
        surface = open_surface(download_deterministic(map_step))
        render_precipitation(surface, map_step)
        render_pressure_wind(surface, map_step)

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cities": {k: CITIES[k] for k in cities},
        "steps_hours": steps,
        "gefs_members_requested": gefs_members,
        "source": "ECMWF IFS/ENS + NOAA GEFS",
        "static_distribution": True,
    }

    for city in cities:
        city_dir = out_dir / "data" / city
        city_dir.mkdir(parents=True, exist_ok=True)
        for step in steps:
            try:
                payload = mobile(
                    city=city,
                    step=step,
                    rain_threshold=1,
                    include_gefs=True,
                    gefs_members=gefs_members,
                    include_daily=True,
                )
            except HTTPException as exc:
                # GEFS products can lag or be temporarily unavailable at long leads.
                # Keep the static forecast publishable with ECMWF instead of failing
                # the whole Pages build; the payload semantics already distinguish
                # official ECMWF probability from optional GEFS diagnostics.
                if exc.status_code != 503:
                    raise
                payload = mobile(
                    city=city,
                    step=step,
                    rain_threshold=1,
                    include_gefs=False,
                    gefs_members=0,
                    include_daily=True,
                )
                payload.setdefault("meta", {})["gefs_fallback"] = True
                payload["meta"]["gefs_fallback_reason"] = str(exc.detail)
            for layer in payload.get("maps", {}).get("layers", []):
                filename = Path(layer.get("url", "")).name
                if filename:
                    layer["url"] = "../../maps/" + filename
                    map_file = OUTPUT_DIR / filename
                    layer["available"] = map_file.is_file() and map_file.stat().st_size > 0
            (city_dir / f"{step}.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default),
                encoding="utf-8",
            )

    maps_dir = out_dir / "maps"
    maps_dir.mkdir(exist_ok=True)
    for source in OUTPUT_DIR.glob("*.png"):
        shutil.copy2(source, maps_dir / source.name)

    (out_dir / "metadata.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static weather snapshots for GitHub Pages")
    parser.add_argument("--out", default="public")
    parser.add_argument("--cities", nargs="+", default=list(CITIES))
    parser.add_argument("--steps", nargs="+", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--gefs-members", type=int, default=3)
    args = parser.parse_args()
    unknown = [c for c in args.cities if c not in CITIES]
    if unknown:
        raise SystemExit(f"Unknown cities: {', '.join(unknown)}")
    build_snapshot(Path(args.out), args.cities, args.steps, args.gefs_members)


if __name__ == "__main__":
    main()
