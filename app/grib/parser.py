from pathlib import Path
import xarray as xr
from app.config import DOMAIN


def open_surface(path: Path) -> xr.Dataset:
    ds = xr.open_dataset(path, engine="cfgrib", backend_kwargs={"indexpath": ""})
    # ECMWF longitude is commonly 0..360. Convert to -180..180 for Morocco.
    if "longitude" in ds.coords and float(ds.longitude.max()) > 180:
        ds = ds.assign_coords(longitude=((ds.longitude + 180) % 360) - 180).sortby("longitude")
    return ds.sel(
        latitude=slice(DOMAIN["north"], DOMAIN["south"]),
        longitude=slice(DOMAIN["west"], DOMAIN["east"]),
    )


def nearest_point(ds: xr.Dataset, lat: float, lon: float) -> xr.Dataset:
    return ds.sel(latitude=lat, longitude=lon, method="nearest")
