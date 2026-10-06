# Morocco Weather Engine

Weather-analysis platform for Morocco and the surrounding North Atlantic / Iberian domain, using official ECMWF Open Data and NOAA GEFS.

## Current validated build

The backend and five-page Arabic mobile web application are now covered by live E2E and semantic contract tests. The current mobile API contract is V0.10.

### Data and forecast engine
- ECMWF IFS deterministic surface forecast through 15 days.
- ECMWF ENS official precipitation probability products.
- ECMWF ENS mean/spread uncertainty.
- NOAA GEFS control and application-computed perturbed-member summaries.
- Cross-model ECMWF/GEFS agreement score, explicitly separate from official probability.
- Daily precipitation de-accumulation and probabilistic days 8–15 trend.
- Synoptic map products: precipitation, MSLP + 10 m wind, 500 hPa and 850 hPa.
- Arabic model analysis and affected Moroccan city points.

### Mobile application
The responsive application is served at `/mobile-ui/` and contains five views:
- Home
- 15-day forecast
- Weather maps
- Model analysis
- Settings

It consumes `GET /mobile/{city}` and keeps official ECMWF probability, ensemble uncertainty and cross-model agreement semantically separate.

## Domain

45N to 20N, 25W to 10E, covering Morocco, Iberia and the eastern Atlantic so approaching Atlantic systems can be analysed upstream.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.api.main:app --reload
```

Open `/mobile-ui/` on the running server.

## Core API

- `GET /health`
- `GET /meta`
- `GET /cities`
- `GET /forecast/{city}`
- `GET /timeline/{city}`
- `GET /mobile/{city}`
- `GET /maps/...`

See `docs/mobile-api-contract.md` for the stable mobile contract.

## Validation

GitHub Actions runs both semantic regression tests and a live ECMWF + NOAA GEFS E2E workflow. The live workflow downloads real model data, generates products, exercises API/mobile contracts and verifies map/static serving.

## Scientific semantics

- Only ECMWF ENS `type=ep` is labelled official event probability.
- ECMWF ENS spread represents uncertainty, not event probability.
- Cross-model agreement is an application-defined similarity score, not official probability.
- GEFS ensemble summaries are application-computed statistics and expose the sampled member count.
- Days 8–15 are presented as probabilistic ensemble trend, never deterministic certainty.
- Arabic impact analysis is model-derived and is not an official meteorological warning.

## Next build phase

Package the validated mobile client for Android while keeping the weather engine/API server-side. Production packaging should use a configurable HTTPS API base URL rather than embedding the Python/GRIB engine inside the APK.
