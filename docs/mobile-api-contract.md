# Mobile API contract V0.10

The mobile client consumes `GET /mobile/{city}`.

Required top-level keys:
`meta,current,day_cards,extended_trend_8_15_days,timeline,official_probabilities,gefs_ensemble,ensemble_uncertainty,cross_model_agreement,maps,layers,analysis_ar,analysis,affected_cities`.

Semantics that must remain stable:
- ECMWF ENS `type=ep` is the only field labelled official probability.
- ECMWF ENS spread and cross-model agreement are never official probabilities.
- GEFS ensemble summaries are application-computed member statistics.
- Daily precipitation is de-accumulated from ECMWF accumulated precipitation.
- Days 8-15 are probabilistic/ensemble trend, never deterministic certainty.
- Arabic analysis is model-derived and never an official warning.
- Map metadata URLs must resolve to real PNG responses when `available=true`.

Breaking changes require an API version bump and contract-test update.
