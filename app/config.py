from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Analysis domain: eastern Atlantic, Iberia, Morocco and western Mediterranean.
DOMAIN = {"north": 45.0, "west": -25.0, "south": 20.0, "east": 10.0}

CITIES = {
    "tangier": {"name_ar": "طنجة", "lat": 35.7595, "lon": -5.8340},
    "tetouan": {"name_ar": "تطوان", "lat": 35.5889, "lon": -5.3626},
    "chefchaouen": {"name_ar": "شفشاون", "lat": 35.1688, "lon": -5.2636},
    "rabat": {"name_ar": "الرباط", "lat": 34.0209, "lon": -6.8416},
    "casablanca": {"name_ar": "الدار البيضاء", "lat": 33.5731, "lon": -7.5898},
    "fes": {"name_ar": "فاس", "lat": 34.0331, "lon": -5.0003},
    "marrakesh": {"name_ar": "مراكش", "lat": 31.6295, "lon": -7.9811},
}
