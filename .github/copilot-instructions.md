<!-- Copilot / AI agent guidance for dstoolkit-mlops-v2 -->
# Agent Instructions — dstoolkit-mlops-v2

Purpose: short, actionable guidance so an AI coding agent can be productive immediately in this repo.

- Quick context: this repo is a Model Factory template that uses Azure ML SDK v2. The code is split between
  - orchestration and pipeline definitions (`mlops/`)
  - model/source code (`src/` and `model/`)
  - infra as code (`infra/`)
  - global config (`config/config.yaml`) — central source of pipeline and deployment settings

Quick start (local dev)
- Copy or rename `.env.sample` → `.env` and populate `SUBSCRIPTION_ID`, `RESOURCE_GROUP_NAME`, `WORKSPACE_NAME`.
- Authenticate: `az login -t <tenant>` (DefaultAzureCredential used by runtime relies on this).
- Register data (if needed):
  - `python -m mlops.common.register_data_asset --data_config_path config/data_config.json`
- Run a local pipeline (examples):
  - `python -m mlops.london_taxi.start_local_pipeline --build_environment pr --wait_for_completion True`
  - The `mlops/<model>/start_local_pipeline.py` modules call `prepare_and_execute(...)` in the model's `src`.

Key files & patterns (examples)
- `config/config.yaml` — single canonical config; per-pipeline keys use names like `london_taxi_pr` and `london_taxi_dev`.
- `mlops/common/config_utils.py` — `MLOpsConfig` loads `config/config.yaml` and exposes `get_pipeline_config()`; prefer it for environment-specific values.
- Pipeline definition pattern: `mlops/<model>/src/mlops_pipeline.py`
  - Components are stored as YAML under `mlops/<model>/components/*.yml` and loaded via `azure.ai.ml.load_component`.
  - After loading, code sets `comp.environment = environment_name` before constructing the pipeline (see `LondonTaxi.construct_pipeline`).
- Execution helper: `mlops/common/pipeline_utils.py` contains `prepare_and_execute_pipeline()` and `execute_pipeline()` — uses `MLClient` and `DefaultAzureCredential`.
- Data handling: `mlops/common/config_utils.py::DataAssetProvider` will try to fetch a registered data asset and optionally fall back to synthetic data.
- Model packaging: `model/<model>/online` and `model/<model>/batch` contain scoring `score.py` and environment conda files for deployments.

Developer workflows & tips
- Local dev options: (a) Reopen repo in the included devcontainers under `.devcontainer/` (recommended), (b) create conda and `pip install -r .devcontainer/requirements.txt`.
- Use `az login` for credentials; the code relies on `DefaultAzureCredential` which will pick up CLI auth in dev.
- Use the debug tasks configured in `.vscode/launch.json` to run register-data and start-local-pipeline scenarios.
- Tests: tests live in `test/` (run `pytest` at repo root). The test suite is small; run quickly during changes.

Conventions and gotchas (project-specific)
- Centralized config: `MLOpsConfig` expects `pipeline_configs` and `deployment_configs` keys that append `_{environment}` (e.g. `london_taxi_pr`). Use `get_pipeline_config()` instead of indexing directly.
- Component environment naming: environment names are generated and assigned to component objects after loading; do not hardcode environment strings in component YAMLs when code intends to override them.
- Compute can be `serverless` (pipeline uses special handling). Expect `compute` to be `None` in that case.
- Synthetic data fallback: some pipelines set `allow_synthetic_fallback: true` in `config/config.yaml`; tests or local runs may create `outputs/synthetic_data`.

Integration points & external dependencies
- Azure ML SDK v2 (`azure.ai.ml`) — pipelines, components and `MLClient` usage are central.
- Authentication: `azure.identity.DefaultAzureCredential` → requires `az login` for local runs.
- CI/CD: GitHub Actions is the active CI system (see [README.md](README.md)). Azure Pipelines files remain for legacy reference.

What an agent can safely change or generate
- Add/modify pipeline components (YAMLs) under `mlops/<model>/components/` following existing examples (prep, transform, train, predict, score, register).
- Implement model logic in `src/` and `model/` directories; follow the conventions used by existing models (see `mlops/london_taxi/src/mlops_pipeline.py`).
- Update `config/config.yaml` keys but preserve the `_pr/_dev` naming pattern.

Where to look first when triaging code
- `mlops/common/` — shared utilities for config, environment and compute.
- `mlops/<model>/src/mlops_pipeline.py` — pipeline construction and orchestration pattern.
- `model/<model>/` — scoring and deployment environment examples.
- `config/config.yaml` and `.env` — runtime configuration and credentials.

If anything in this guidance is unclear or you want more specifics (examples for a particular model, CI steps, or test commands), tell me which area to expand.
