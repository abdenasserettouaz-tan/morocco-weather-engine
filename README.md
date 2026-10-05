# Morocco Weather Engine

Prototype V1 for a Morocco/North Africa weather-analysis application.

## V1 goal

Use official ECMWF Open Data to download selected ECMWF ENS fields, decode GRIB2, subset the eastern Atlantic / Iberia / Morocco domain, extract city forecasts, and expose the result as JSON with an Arabic machine-generated summary.

## Current data fields

- Mean sea-level pressure
- 2 m temperature
- 10 m U/V wind
- Total precipitation
- ECMWF ENS ensemble-mean product

## Domain

45N to 20N, 25W to 10E. This deliberately includes the eastern Atlantic and Iberian Peninsula so approaching Atlantic systems can be analysed before reaching Morocco.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python run_prototype.py --city tangier --step 168
```

The command downloads the required official ECMWF Open Data GRIB2 file and prints a JSON forecast for Tangier at +168 hours.

## API

```bash
uvicorn app.api.main:app --reload
```

Endpoints:

- `GET /health`
- `GET /cities`
- `GET /forecast/tangier?step=168`

The forecast endpoint expects the corresponding GRIB file to have been downloaded first by the prototype runner.

## Next milestones

1. Validate live ECMWF GRIB retrieval and field decoding on a runtime with ecCodes.
2. Add precipitation/pressure map renderer.
3. Retrieve ENS members and calculate probability + spread instead of treating the ensemble mean as probability.
4. Add NOAA GEFS ingestion.
5. Add ECMWF-vs-GEFS agreement score.
6. Add synoptic-pattern analysis and richer Arabic explanations.
7. Connect the engine to the Android UI.

## Scientific caution

Long-range deterministic-looking values must not be presented as certainty. V1 keeps ensemble mean separate from probability. Probability/confidence will only be exposed after member-level calculations are implemented and validated.
