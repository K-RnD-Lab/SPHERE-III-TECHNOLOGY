# R3a Evidence Gap Navigator

Evidence Gap Navigator is a retrieval-evaluated RAG interface for researchers studying RAG evaluation
and monitoring. It turns a public OpenAlex corpus into inspectable evidence, compares retrieval and prompt
strategies, and records interaction and feedback signals for later quality monitoring.

## Registry Metadata

```yaml
primary_sphere: technology
secondary_spheres: [science]
combo: S+T
artifact_type: research_tool
delivery_layers: [GitHub]
validation_stage: prototype
```

## Delivery

- [Standalone project repository](https://github.com/K-RnD-Lab/evidence-gap-navigator)
- Streamlit interface with citation-grounded synthesis and retrieval inspection
- Automated OpenAlex ingestion through `dlt`, plus reproducible retrieval and LLM evaluation artifacts

## Why it belongs in T3

The result is reusable research infrastructure rather than a claim about a specific scientific domain. The
current corpus focuses on retrieval-augmented generation methods, but the ingestion, hybrid retrieval,
evaluation, and monitoring architecture can be adapted to other evidence domains.
