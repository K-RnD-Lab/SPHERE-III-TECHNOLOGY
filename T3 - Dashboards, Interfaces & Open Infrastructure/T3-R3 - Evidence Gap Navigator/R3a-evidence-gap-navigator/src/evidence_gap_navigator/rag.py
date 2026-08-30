from __future__ import annotations

import time

from evidence_gap_navigator.config import Settings
from evidence_gap_navigator.llm import GroqLLM, extractive_preview
from evidence_gap_navigator.models import RAGResponse
from evidence_gap_navigator.retrieval import EvidenceSearchEngine

SYSTEM_PROMPT_V1 = """You are an evidence navigator for AI engineering researchers.
Answer only from the supplied scholarly evidence. Cite claims with [1], [2], etc.
Separate established findings, limitations, and open evidence gaps. If the evidence
does not support a claim, say so. Do not invent paper details or citations."""

SYSTEM_PROMPT_V2 = """You are a rigorous research synthesis assistant for RAG evaluation and monitoring.
Use only the numbered evidence excerpts. Structure the answer as:
1. Evidence-backed synthesis
2. Methodological caveats
3. Research gaps / next experiments
Every substantive claim must have a bracket citation such as [1]. Explicitly state
when retrieved studies disagree or when evidence is insufficient."""


class RAGService:
    def __init__(self, settings: Settings, search_engine: EvidenceSearchEngine) -> None:
        self.settings = settings
        self.search_engine = search_engine

    def answer(
        self,
        question: str,
        retrieval_method: str = "hybrid_rerank",
        top_k: int = 6,
        prompt_version: str = "v2",
        rewrite_query: bool = False,
        max_completion_tokens: int | None = None,
    ) -> RAGResponse:
        started = time.perf_counter()
        llm = None
        effective_query = question
        if self.settings.groq_api_key:
            llm = GroqLLM(self.settings.groq_api_key, self.settings.llm_model)
            if rewrite_query:
                effective_query = llm.rewrite_query(question)

        sources = self.search_engine.search(effective_query, method=retrieval_method, top_k=top_k)
        contexts = [result.document.text for result in sources]
        metadata = {"input_tokens": 0, "output_tokens": 0, "prompt_version": prompt_version}

        if llm:
            evidence = "\n\n".join(
                f"[{index}] {result.document.title}\n"
                f"Excerpt: {result.document.text[:900]}\nURL: {result.document.url}"
                for index, result in enumerate(sources, start=1)
            )
            user_prompt = f"Question: {question}\n\nEvidence:\n{evidence}"
            output = llm.complete(
                SYSTEM_PROMPT_V2 if prompt_version == "v2" else SYSTEM_PROMPT_V1,
                user_prompt,
                max_completion_tokens=max_completion_tokens or 360,
            )
            answer = output.text
            metadata.update(input_tokens=output.input_tokens, output_tokens=output.output_tokens)
            provider = self.settings.llm_provider
            model = self.settings.llm_model
        else:
            answer = extractive_preview(question, contexts)
            provider = "retrieval-only-preview"
            model = "none"

        return RAGResponse(
            question=question,
            answer=answer,
            sources=sources,
            retrieval_method=retrieval_method,
            latency_ms=(time.perf_counter() - started) * 1000,
            provider=provider,
            model=model,
            rewritten_query=effective_query if effective_query != question else None,
            metadata=metadata,
        )
