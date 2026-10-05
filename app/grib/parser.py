from pathlib import Path
import xarray as xr
import cfgrib
from app.config import DOMAIN


def _normalise(ds: xr.Dataset) -> xr.Dataset:
    if "longitude" in ds.coords and ds.longitude.size and float(ds.longitude.max()) > 180:
        ds = ds.assign_coords(longitude=((ds.longitude + 180) % 360) - 180).sortby("longitude")
    if "latitude" not in ds.coords or "longitude" not in ds.coords:
        return ds
    lat = ds.latitude.values
    lat_slice = slice(DOMAIN["north"], DOMAIN["south"]) if lat[0] > lat[-1] else slice(DOMAIN["south"], DOMAIN["north"])
    return ds.sel(latitude=lat_slice, longitude=slice(DOMAIN["west"], DOMAIN["east"]))


def open_surface(path: Path) -> xr.Dataset:
    """Open heterogeneous surface GRIB safely.

    ECMWF/GEFS surface files mix 2 m temperature and 10 m wind messages, which
    cfgrib cannot always merge into one hypercube. Open every compatible
    hypercube and merge variables after removing scalar vertical coordinates.
    """
    datasets = cfgrib.open_datasets(str(path), backend_kwargs={"indexpath": ""})
    prepared = []
    for ds in datasets:
        ds = _normalise(ds)
        drop = [c for c in ("heightAboveGround", "surface", "meanSea") if c in ds.coords and ds[c].ndim == 0]
        if drop:
            ds = ds.drop_vars(drop)
        prepared.append(ds)
    if not prepared:
        raise ValueError(f"No GRIB datasets found in {path}")
    return xr.merge(prepared, compat="override", join="outer")


def open_isobaric(path: Path, level_hpa: int) -> xr.Dataset:
    datasets = cfgrib.open_datasets(str(path), backend_kwargs={"indexpath": ""})
    candidates = []
    for ds in datasets:
        if "isobaricInhPa" in ds.coords:
            ds = _normalise(ds)
            if "isobaricInhPa" in ds.dims:
                try:
                    ds = ds.sel(isobaricInhPa=level_hpa)
                except KeyError:
                    continue
            elif float(ds.isobaricInhPa) != level_hpa:
                continue
            candidates.append(ds)
    if not candidates:
        raise ValueError(f"Pressure level {level_hpa} hPa not found in {path}")
    return xr.merge(candidates, compat="override", join="outer")


def open_pressure_levels(path: Path) -> xr.Dataset:
    """Open all available isobaric pressure levels and merge their fields."""
    datasets = cfgrib.open_datasets(str(path), backend_kwargs={"indexpath": ""})
    candidates = []
    for ds in datasets:
        if "isobaricInhPa" not in ds.coords:
            continue
        ds = _normalise(ds)
        candidates.append(ds)
    if not candidates:
        raise ValueError(f"No isobaric pressure-level fields found in {path}")
    return xr.merge(candidates, compat="override", join="outer")


def nearest_point(ds: xr.Dataset, lat: float, lon: float) -> xr.Dataset:
    return ds.sel(latitude=lat, longitude=lon, method="nearest")
