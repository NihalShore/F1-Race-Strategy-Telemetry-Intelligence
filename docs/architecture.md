# System architecture

## 1. Design goals

The first version should produce reproducible race-strategy comparisons from local datasets. Every prediction must be traceable to its input data, model parameters and assumptions.

The project is not intended to reproduce a Formula 1 team's proprietary timing system. Public and sample data will have gaps, different sampling rates and varying levels of detail. The ingestion layer must preserve those limitations rather than silently inventing missing measurements.

## 2. Data flow

```text
CSV / Parquet / supported data adapters
                |
                v
       Ingestion and validation
                |
                v
       Canonical race data model
                |
                v
       Telemetry and lap analysis
                |
                v
    Pace, tyre, fuel and pit-loss models
                |
                v
      Strategy generation and search
                |
                v
       Race scenario simulation
                |
                v
       API responses and dashboard
```

The canonical data model is the boundary between external data sources and the rest of the application. Source-specific column names and units should not leak into strategy code.

## 3. Main components

### Data ingestion

Responsibilities:
- Read supported local files and adapters.
- Validate required columns, types, units and session identifiers.
- Normalize timestamps, lap numbers, driver identifiers and compound names.
- Report missing, duplicated or out-of-order samples.
- Preserve source metadata and data provenance.

Initial output: validated session, lap and telemetry records. Invalid records should produce actionable errors; they should not be silently dropped.

### Telemetry processing

Responsibilities:
- Align samples to laps and sessions.
- Calculate sector and lap summaries.
- Detect gaps and suspicious values.
- Produce consistent features for the models.

Telemetry channels may be sampled at different rates. Alignment must be explicit and must not imply precision that the source data does not contain.

### Race models

Separate models keep assumptions testable:

- **Tyre model:** estimates pace change against tyre age, compound and track conditions.
- **Fuel model:** estimates fuel-related pace effect when fuel data or a documented starting-load assumption is available.
- **Pit-loss model:** estimates time lost during a stop, including pit-lane loss and stationary time when available.
- **Pace model:** combines measured pace and model adjustments while retaining uncertainty.

Start with transparent baselines. More complex fitting should only be added when there is enough suitable data to validate it.

### Strategy engine

Responsibilities:
- Generate feasible stop counts, compounds and pit laps.
- Reject strategies that violate race distance, tyre-use or configured constraints.
- Compare total expected race time and position-relative outcomes where opponent data exists.
- Report the assumptions behind each candidate.

The optimizer should not return a single unexplained answer. It should return ranked candidates with estimated time, uncertainty and the inputs that drove the ranking.

### Scenario simulator

Responsibilities:
- Simulate lap-by-lap race progression.
- Model pit stops, traffic effects and configurable neutralization scenarios.
- Run repeated trials with sampled uncertainty.
- Summarize distributions, not just a single average.

Safety-car timing and duration are scenario inputs in the initial version, not live predictions.

### C++ simulation engine

Keep the first implementation in Python until profiling identifies a real bottleneck. Move stable, CPU-heavy loops into C++ behind a narrow interface. Python remains responsible for data handling, configuration and orchestration.

The C++ library must have independent tests and deterministic test cases. Do not duplicate business rules in both languages.

### API and frontend

FastAPI exposes validated inputs and typed results. The frontend consumes those API contracts and visualizes:
- Lap and sector pace.
- Tyre-age and degradation estimates.
- Candidate pit windows.
- Strategy comparisons.
- Scenario outcome distributions.

The dashboard is a client of the analysis system, not the place where core calculations live.

## 4. Suggested repository layout

```text
backend/
  api/
  ingestion/
  telemetry/
  models/
  strategy/
  simulation/
engine/
  include/
  src/
  tests/
frontend/
data/
  samples/
  schemas/
docs/
tests/
scripts/
```

Keep modules small and introduce directories when there is code to put in them. Avoid empty scaffolding that has no tested responsibility.

## 5. Core data contracts

The first schemas should cover:

- **Session:** event identifier, session type, date, circuit and source metadata.
- **Lap:** session, driver, lap number, lap time, sector times, tyre compound and tyre age where known.
- **Telemetry sample:** session, driver, timestamp or elapsed time, lap number and named channels with units.
- **Pit stop:** session, driver, lap, pit-lane time and stationary time when available.
- **Weather sample:** session, timestamp, air temperature, track temperature, rainfall and source units.

Use explicit units in field names or schema metadata. Store unavailable values as missing, not zero.

## 6. Model validation

- Split training and evaluation by session or event, not by randomly mixing adjacent laps.
- Compare predictions with simple baselines.
- Track errors by circuit, compound and stint length where sample size permits.
- Keep model parameters and data versions with each simulation result.
- Use fixed random seeds in tests; allow configurable seeds for experiments.
- Include uncertainty intervals and flag extrapolation beyond observed data.

A model is not considered useful merely because it fits one race.

## 7. Implementation sequence

1. Define schemas, sample data and ingestion validation.
2. Build lap and telemetry summaries with tests.
3. Add baseline tyre, fuel and pit-loss models.
4. Generate and compare deterministic pit strategies.
5. Add stochastic race simulation and safety-car scenarios.
6. Expose the workflow through FastAPI.
7. Build the dashboard around stable API contracts.
8. Profile simulation workloads and move only proven bottlenecks to C++.
9. Add broader datasets, model evaluation and CI coverage.

Each stage should leave the project runnable and tested before the next one is added.

## 8. Engineering constraints

- Do not treat sample or historical data as live telemetry.
- Do not infer missing fuel loads, tyre temperatures or setup values without labelling the assumptions.
- Do not hard-code one circuit, season or driver into model logic.
- Keep external data licensing and attribution with the dataset.
- Keep secrets, local datasets and generated artifacts out of version control.
