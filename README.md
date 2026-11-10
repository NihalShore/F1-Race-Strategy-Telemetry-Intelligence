# F1 Race Strategy & Telemetry Intelligence

A race engineering toolkit for analysing lap and telemetry data, estimating race pace, and comparing pit-stop strategies under uncertainty.

## Scope

The system is being built around five connected capabilities:

- Import and validate lap timing, telemetry, weather, tyre and pit-stop data.
- Estimate tyre degradation, fuel effects and expected lap pace.
- Compare pit windows, undercuts and overcuts.
- Simulate race scenarios, including safety-car periods and uncertain events.
- Explain strategy recommendations with outcome distributions and assumptions.

The first release will work with local historical or sample datasets. It will not claim to provide live team telemetry or official real-time strategy advice.

## Architecture

- **Python:** data ingestion, analysis, models, API and strategy orchestration.
- **C++:** computationally intensive simulation kernels once profiling justifies them.
- **FastAPI:** typed HTTP interface between the analysis layer and clients.
- **React + TypeScript:** interactive race and strategy views.
- **CMake / GoogleTest:** native engine build and tests.
- **pytest:** Python tests.

See [docs/architecture.md](docs/architecture.md) for the system boundaries, data flow and implementation sequence.

## Development status

The repository currently contains the project license and initial documentation. Implementation will proceed in small, testable steps, starting with data contracts and telemetry ingestion.

## Data and attribution

Use datasets only under their respective terms. Keep source attribution and licensing information with imported data. Do not commit private, licensed or personally identifying data.

## License

Apache-2.0. See [LICENSE](LICENSE).
