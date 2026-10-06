from pathlib import Path
from app.config import OUTPUT_DIR

MAP_LAYERS = {
    "precipitation": {"label_ar": "الهطول", "filename": "precip_{step:03d}h.png", "mime": "image/png"},
    "pressure_wind": {"label_ar": "الضغط والرياح", "filename": "pressure_wind_{step:03d}h.png", "mime": "image/png"},
    "500hpa": {"label_ar": "طبقة 500 hPa", "filename": "upper_500_{step:03d}h.png", "mime": "image/png"},
    "850hpa": {"label_ar": "طبقة 850 hPa", "filename": "upper_850_{step:03d}h.png", "mime": "image/png"},
}

def map_metadata(step: int, base_url: str = "/maps") -> dict:
    layers = []
    for layer_id, cfg in MAP_LAYERS.items():
        filename = cfg["filename"].format(step=step)
        path = OUTPUT_DIR / filename
        layers.append({
            "id": layer_id,
            "label_ar": cfg["label_ar"],
            "mime": cfg["mime"],
            "forecast_step_hours": step,
            "available": path.is_file() and path.stat().st_size > 0,
            "url": f"{base_url}/{filename}",
        })
    return {"forecast_step_hours": step, "layers": layers}
