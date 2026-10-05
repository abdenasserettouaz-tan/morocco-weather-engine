from pathlib import Path
from ecmwf.opendata import Client
from app.config import DATA_DIR

def download_upper_air(step: int = 72, target: Path | None = None) -> Path:
    """Official ECMWF IFS 500/850 hPa synoptic fields."""
    target = target or DATA_DIR / f"ecmwf_upper_{step:03d}h.grib2"
    Client(source="ecmwf").retrieve(
        stream="oper", type="fc", step=step,
        levelist=[500, 850], param=["gh", "t", "u", "v"],
        target=str(target),
    )
    return target
