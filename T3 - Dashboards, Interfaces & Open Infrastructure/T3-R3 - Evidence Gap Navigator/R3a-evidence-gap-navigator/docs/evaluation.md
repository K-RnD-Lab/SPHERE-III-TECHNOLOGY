# Evaluation protocol

## Retrieval

The gold set contains realistic research questions and one or more relevant OpenAlex work IDs. Four retrieval
strategies are run against the same indexed corpus and the same top-k cutoff. The selected default is the method
with the strongest MRR@10, using nDCG@10 as a secondary signal.

## End to end

Two prompts use the same questions and retrieved contexts. A strict LLM judge receives the original question,
reference notes, numbered retrieved excerpts, and generated answer. It scores groundedness, relevance,
completeness, and citation quality from 1 to 5. The highest average is used as the default prompt.

The committed run evaluates four representative questions across evaluation frameworks, retrieval-quality
measurement, benchmarks, and production failure modes. Prompt v2 scored 2.750 overall versus 1.875 for v1,
so v2 is the default.

## Known validity limits

- The gold set is curated by one project author.
- LLM judge scores can vary between runs.
- Abstract-only evidence can omit important methodological details.
- Evaluation results should be interpreted comparatively within this corpus.
