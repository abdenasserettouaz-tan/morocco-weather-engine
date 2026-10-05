from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from app.config import DATA_DIR, DOMAIN

BASE = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p25s.pl"


def _candidate_cycles():
    now = datetime.now(timezone.utc)
    # Operational cycles are 00/06/12/18 UTC. Try recent cycles because publication lags.
    cycle = (now.hour // 6) * 6
    anchor = now.replace(hour=cycle, minute=0, second=0, microsecond=0)
    for lag in range(0, 5):
        dt = anchor - timedelta(hours=6 * lag)
        yield dt.strftime("%Y%m%d"), dt.strftime("%H")


def _url(date: str, cycle: str, step: int, member: str) -> str:
    # GEFS atmospheric 0.25-degree products. Member examples: gec00, gep01..gep30.
    filename = f"{member}.t{cycle}z.pgrb2s.0p25.f{step:03d}"
    q = {
        "file": filename,
        "var_APCP": "on",
        "var_PRMSL": "on",
        "var_TMP": "on",
        "var_UGRD": "on",
        "var_VGRD": "on",
        "lev_surface": "on",
        "lev_mean_sea_level": "on",
        "lev_2_m_above_ground": "on",
        "lev_10_m_above_ground": "on",
        "subregion": "",
        "leftlon": DOMAIN["west"],
        "rightlon": DOMAIN["east"],
        "toplat": DOMAIN["north"],
        "bottomlat": DOMAIN["south"],
        "dir": f"/gefs.{date}/{cycle}/atmos/pgrb2sp25",
    }
    return BASE + "?" + urlencode(q)


def download_gefs_member(step: int = 72, member: str = "gec00", target: Path | None = None) -> Path:
    target = target or DATA_DIR / f"gefs_{member}_{step:03d}h.grib2"
    last_error = None
    for date, cycle in _candidate_cycles():
        try:
            with urlopen(_url(date, cycle, step, member), timeout=90) as r:
                data = r.read()
            # GRIB2 starts with GRIB; HTML errors must never be accepted as model data.
            if len(data) > 1000 and data[:4] == b"GRIB":
                target.write_bytes(data)
                return target
        except Exception as exc:
            last_error = exc
    raise RuntimeError(f"Unable to retrieve recent GEFS {member} +{step}h: {last_error}")
