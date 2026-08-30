from __future__ import annotations

import time
from dataclasses import dataclass

from groq import Groq, RateLimitError


@dataclass
class LLMOutput:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0


class GroqLLM:
    def __init__(self, api_key: str, model: str) -> None:
        if not api_key:
            raise ValueError("GROQ_API_KEY is required for LLM answers")
        self.client = Groq(api_key=api_key)
        self.model = model

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_completion_tokens: int = 360,
        json_mode: bool = False,
    ) -> LLMOutput:
        request_kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_completion_tokens": max_completion_tokens,
        }
        if self.model.startswith("openai/gpt-oss-"):
            request_kwargs["reasoning_effort"] = "low"
        elif self.model.startswith("qwen/"):
            request_kwargs["reasoning_effort"] = "none"
        if json_mode:
            request_kwargs["response_format"] = {"type": "json_object"}

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(**request_kwargs)
                break
            except RateLimitError:
                if attempt == 2:
                    raise
                time.sleep(3 * (attempt + 1))
        usage = response.usage
        return LLMOutput(
            text=response.choices[0].message.content or "",
            input_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
        )

    def rewrite_query(self, query: str) -> str:
        output = self.complete(
            "Rewrite research questions for scholarly retrieval. Return only one concise search query.",
            query,
            temperature=0.0,
            max_completion_tokens=64,
        )
        return output.text.strip().strip('"')


def extractive_preview(question: str, contexts: list[str]) -> str:
    if not contexts:
        return "No evidence was retrieved for this question."
    excerpts = "\n\n".join(f"[{index}] {context[:420]}" for index, context in enumerate(contexts, 1))
    return (
        "LLM generation is disabled because no API key is configured. "
        "The retrieved evidence below is still available for inspection.\n\n"
        f"Question: {question}\n\n{excerpts}"
    )
