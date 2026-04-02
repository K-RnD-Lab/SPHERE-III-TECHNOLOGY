# R1a Study Registry Dashboard Template

## Question

What is the minimal reusable dashboard or registry pattern that can make K R&D Lab studies easier to browse, compare, and audit across spheres?

## Scope

This starter study is about interface and infrastructure design, not about any one domain finding.

## Registry Metadata

```yaml
primary_sphere: technology
secondary_spheres:
  - science
  - entrepreneurship
combo: S+E+T
artifact_type: dashboard
delivery_layers:
  - GitHub
  - Hugging Face
validation_stage: live prototype
```

## Method

1. Identify the core metadata each study should expose.
2. Design a consistent card, table, and filter pattern for multi-study browsing.
3. Separate public-facing browsing needs from internal audit or reproducibility needs.
4. Define a reusable template that can be adapted across science, entrepreneurship, and technology repos.

## Candidate dashboard blocks

- study cards with lane, status, and evidence labels
- registry filters by sphere, track, and maturity
- links to `README`, `report`, data, and live demos
- simple indicators for reproducibility or readiness status

## Current scaffold files

- [`dashboard/index.html`](dashboard/index.html)
- [`dashboard/styles.css`](dashboard/styles.css)
- [`dashboard/app.js`](dashboard/app.js)
- [`dashboard/data/registry.json`](dashboard/data/registry.json)
- [`../../../tools/build_registry.py`](../../../tools/build_registry.py)

## Status

Starter scaffold for a reusable public-interface pattern. Registry data can now be regenerated automatically from repository metadata instead of being hand-edited.
