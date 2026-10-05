from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from app.config import OUTPUT_DIR, CITIES


def render_precipitation(ds, step: int, target: Path | None = None) -> Path:
    """Render the first V1 precipitation map over the configured domain."""
    target = target or OUTPUT_DIR / f"precip_{step:03d}h.png"
    if "tp" not in ds:
        raise KeyError("tp field is not present in dataset")
    rain = np.maximum(ds["tp"].values * 1000.0, 0.0)
    lon = ds.longitude.values
    lat = ds.latitude.values
    fig, ax = plt.subplots(figsize=(10, 8))
    mesh = ax.pcolormesh(lon, lat, rain, shading="auto")
    fig.colorbar(mesh, ax=ax, label="Total precipitation (mm)")
    for city in CITIES.values():
        ax.scatter(city["lon"], city["lat"], s=16)
    ax.set(title=f"ECMWF IFS total precipitation +{step}h", xlabel="Longitude", ylabel="Latitude")
    fig.tight_layout()
    fig.savefig(target, dpi=160)
    plt.close(fig)
    return target
