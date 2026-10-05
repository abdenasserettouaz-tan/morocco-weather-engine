from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from app.config import OUTPUT_DIR, CITIES

def _city_marks(ax):
    for c in CITIES.values():
        ax.scatter(c["lon"], c["lat"], s=12)
        ax.text(c["lon"] + .15, c["lat"] + .15, c["name_ar"], fontsize=7)

def render_pressure_wind(ds, step: int, target: Path | None = None) -> Path:
    target = target or OUTPUT_DIR / f"pressure_wind_{step:03d}h.png"
    msl = ds["msl"] / 100.0
    u, v = ds["u10"], ds["v10"]
    fig, ax = plt.subplots(figsize=(11,8))
    cs=ax.contour(ds.longitude, ds.latitude, msl, levels=18)
    ax.clabel(cs, inline=True, fontsize=7, fmt="%.0f")
    skip=(slice(None,None,8),slice(None,None,8))
    ax.quiver(ds.longitude.values[::8], ds.latitude.values[::8],
              u.values[skip], v.values[skip], scale=500)
    _city_marks(ax)
    ax.set(title=f"ECMWF IFS MSLP + 10 m wind +{step}h", xlabel="Longitude", ylabel="Latitude")
    fig.tight_layout(); fig.savefig(target,dpi=170); plt.close(fig)
    return target

def render_upper_air(ds, level: int, step: int, target: Path | None = None) -> Path:
    target = target or OUTPUT_DIR / f"upper_{level}_{step:03d}h.png"
    d = ds.sel(isobaricInhPa=level) if "isobaricInhPa" in ds.coords else ds.sel(pressure=level)
    gh = d["gh"] if "gh" in d else d["z"] / 9.80665
    temp = d["t"] - 273.15
    fig, ax = plt.subplots(figsize=(11,8))
    mesh=ax.pcolormesh(d.longitude,d.latitude,temp,shading="auto")
    fig.colorbar(mesh,ax=ax,label=f"Temperature at {level} hPa (°C)")
    cs=ax.contour(d.longitude,d.latitude,gh,levels=16)
    ax.clabel(cs,inline=True,fontsize=7,fmt="%.0f")
    if "u" in d and "v" in d:
        skip=(slice(None,None,8),slice(None,None,8))
        ax.quiver(d.longitude.values[::8],d.latitude.values[::8],
                  d["u"].values[skip],d["v"].values[skip],scale=700)
    _city_marks(ax)
    ax.set(title=f"ECMWF IFS {level} hPa height / temperature / wind +{step}h",
           xlabel="Longitude",ylabel="Latitude")
    fig.tight_layout(); fig.savefig(target,dpi=170); plt.close(fig)
    return target
