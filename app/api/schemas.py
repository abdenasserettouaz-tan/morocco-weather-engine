from pydantic import BaseModel

class EngineMeta(BaseModel):
    engine: str = "Morocco Weather Engine"
    horizon_hours: int = 360
    horizon_days: int = 15
    models: list[str] = ["ECMWF IFS/ENS", "NOAA GEFS"]

class TimelineRequest(BaseModel):
    steps: list[int] | None = None
    include_gefs: bool = True
