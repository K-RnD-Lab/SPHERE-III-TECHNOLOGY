# SPHERE-III-TECHNOLOGY

Reusable research tools, scoring systems, dashboards, and open infrastructure for K R&D Lab.

## What belongs here

- analytical engines and reusable pipelines
- reproducibility logic, confidence labels, and scoring systems
- public dashboards, registries, interfaces, and open tooling

Biology-related technology is valid in this repo when the output is a reusable method rather than a scientific claim. For example, a biomarker scoring engine belongs here; the biomarker hypothesis itself belongs in `SPHERE-I`.

## Tracks

- `T1` Research Tools, ML & Analytical Engines
  Reusable engines, models, and pipelines for scientific and analytical work.
- `T2` Reproducibility, Scoring & Method Systems
  Confidence labels, experiment-readiness scoring, and evaluation workflows.
- `T3` Dashboards, Interfaces & Open Infrastructure
  Dashboards, registries, public interfaces, and inspectable research infrastructure.

## Starter studies in this repo

- [`T1-R1a Bioinformatics Pipeline Template`](T1%20-%20Research%20Tools,%20ML%20%26%20Analytical%20Engines/T1-R1%20-%20Reusable%20Analytical%20Engines/R1a-bioinformatics-pipeline-template/README.md)
- [`T2-R1a Study Readiness Scoring`](T2%20-%20Reproducibility,%20Scoring%20%26%20Method%20Systems/T2-R1%20-%20Research%20Gap%20Scoring/R1a-study-readiness-scoring/README.md)
- [`T3-R1a Study Registry Dashboard Template`](T3%20-%20Dashboards,%20Interfaces%20%26%20Open%20Infrastructure/T3-R1%20-%20Dashboard%20Templates%20%26%20Public%20Interfaces/R1a-study-registry-dashboard-template/README.md)

## Active execution docs

- [`docs/README.md`](docs/README.md)
- [`docs/core/T1_T3_RESEARCH_EXECUTION_INDEX.md`](docs/core/T1_T3_RESEARCH_EXECUTION_INDEX.md)
- [`docs/core/TECHNOLOGY_STRUCTURE_APPROVAL_GATE.md`](docs/core/TECHNOLOGY_STRUCTURE_APPROVAL_GATE.md)
- [`docs/core/GPT_ASSISTED_TECHNOLOGY_WORKFLOW.md`](docs/core/GPT_ASSISTED_TECHNOLOGY_WORKFLOW.md)

## Cross-sphere registry scaffold

The first unified index across all three spheres lives here:

- [`dashboard/index.html`](T3%20-%20Dashboards%2C%20Interfaces%20%26%20Open%20Infrastructure/T3-R1%20-%20Dashboard%20Templates%20%26%20Public%20Interfaces/R1a-study-registry-dashboard-template/dashboard/index.html)
- [`dashboard/data/registry.json`](T3%20-%20Dashboards%2C%20Interfaces%20%26%20Open%20Infrastructure/T3-R1%20-%20Dashboard%20Templates%20%26%20Public%20Interfaces/R1a-study-registry-dashboard-template/dashboard/data/registry.json)
- [Live Study Registry Space](https://huggingface.co/spaces/K-RnD-Lab/Study-Registry_04-2026)

Registry data is now generated from repo metadata with [`tools/build_registry.py`](tools/build_registry.py), and `SPHERE-III` includes a scheduled/manual GitHub Actions workflow to rebuild the shared index.

## Example directions

- `T1`: reusable bioinformatics engines, literature mining tools, assay-support models
- `T2`: confidence labels, experiment-readiness scoring, reproducible evaluation workflows
- `T3`: public dashboards, study registries, dataset explorers, interactive lab interfaces

## Boundary rule

Use `SPHERE-III` when the output should be reused across multiple studies or domains. Keep biological conclusions in `SPHERE-I` and venture or ecosystem decisions in `SPHERE-II`.

## Primary Sphere And Hybrid Combos

`SPHERE-III` remains the home sphere for tools, methods, and infrastructure, while hybrid combo labels show who the tool is really serving:

- `T` for general-purpose tooling
- `S+T` for science-facing tools, scoring systems, or analytical engines
- `E+T` for venture, ops, or market infrastructure
- `S+E+T` for shared interfaces that connect research, decisions, and implementation

This keeps the repo structure stable without hiding interdisciplinary work.
