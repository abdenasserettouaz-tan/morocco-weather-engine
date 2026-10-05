from pathlib import Path
from ecmwf.opendata import Client
from app.config import DATA_DIR


def download_ensemble(step: int = 168, target: Path | None = None) -> Path:
    """Download selected ECMWF ENS surface fields for a forecast step.

    V1 deliberately downloads only the fields needed by the prototype.
    GRIB spatial subsetting is performed after download; later versions can
    introduce cached/ranged retrieval as the data pipeline matures.
    """
    target = target or DATA_DIR / f"ecmwf_ens_{step:03d}h.grib2"
    client = Client(source="ecmwf")
    client.retrieve(
        stream="enfo",
        type="em",
        step=step,
        param=["msl", "2t", "10u", "10v", "tp"],
        target=str(target),
    )
    return target


if __name__ == "__main__":
    print(download_ensemble())
