from pathlib import Path
from ecmwf.opendata import Client
from app.config import DATA_DIR


def download_deterministic(step: int = 168, target: Path | None = None) -> Path:
    """Download official ECMWF IFS surface forecast fields.

    These fields provide the synoptic/base forecast. Probability is kept in a
    separate product so the UI never mistakes a deterministic value for ENS
    confidence.
    """
    target = target or DATA_DIR / f"ecmwf_ifs_{step:03d}h.grib2"
    Client(source="ecmwf").retrieve(
        stream="oper",
        type="fc",
        step=step,
        param=["msl", "2t", "10u", "10v", "tp"],
        target=str(target),
    )
    return target


def download_ens_mean_pressure(step: int = 168, target: Path | None = None) -> Path:
    """Download ECMWF ENS ensemble-mean MSL pressure (official type=em)."""
    target = target or DATA_DIR / f"ecmwf_ens_mean_{step:03d}h.grib2"
    Client(source="ecmwf").retrieve(
        stream="enfo", type="em", step=step, param=["msl"], target=str(target)
    )
    return target


def download_ens_spread_pressure(step: int = 168, target: Path | None = None) -> Path:
    """Download ECMWF ENS MSL-pressure standard deviation (official type=es)."""
    target = target or DATA_DIR / f"ecmwf_ens_spread_{step:03d}h.grib2"
    Client(source="ecmwf").retrieve(
        stream="enfo", type="es", step=step, param=["msl"], target=str(target)
    )
    return target


def download_daily_precip_probability(
    start_hour: int = 144, threshold_mm: int = 1, target: Path | None = None
) -> Path:
    """Download official ENS probability for precipitation in a 24 h window.

    ECMWF type=ep daily weather-event products use step ranges such as
    144-168 and parameters tpg1/tpg5/tpg10/tpg20/tpg25/tpg50/tpg100.
    """
    allowed = {1, 5, 10, 20, 25, 50, 100}
    if threshold_mm not in allowed:
        raise ValueError(f"threshold_mm must be one of {sorted(allowed)}")
    end_hour = start_hour + 24
    target = target or DATA_DIR / f"ecmwf_prob_tp{threshold_mm}_{start_hour:03d}-{end_hour:03d}h.grib2"
    Client(source="ecmwf").retrieve(
        stream="enfo",
        type="ep",
        step=f"{start_hour}-{end_hour}",
        param=[f"tpg{threshold_mm}"],
        target=str(target),
    )
    return target


# Backwards-compatible name used by the first prototype runner.
def download_ensemble(step: int = 168, target: Path | None = None) -> Path:
    return download_deterministic(step, target)


if __name__ == "__main__":
    print(download_deterministic())
