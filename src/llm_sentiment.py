"""Optional LLM-based tone scoring, as a richer alternative to the keyword scorer.

Off by default -- only runs if ANTHROPIC_API_KEY is set. The keyword scorer in
sentiment.py has no external dependency and is what the rest of the pipeline
uses by default; this module exists to show the same problem solved with an
LLM call instead of a lexicon, and to compare the two.
"""
from __future__ import annotations

import json
import os

PROMPT_TEMPLATE = """You are a fixed-income analyst reading a central bank policy statement.
Score its tone on monetary policy direction from -1.0 (maximally dovish / easing bias)
to +1.0 (maximally hawkish / tightening bias), with 0.0 being neutral.

Respond with ONLY a JSON object: {{"score": <float>, "reasoning": "<one sentence>"}}

Statement:
\"\"\"{statement}\"\"\"
"""


def score_with_llm(text: str) -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. This is an optional path -- "
            "sentiment.py's keyword scorer works with no API key."
        )

    import anthropic  # deferred import so the base pipeline has no hard dependency on this

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(statement=text)}],
    )
    raw = message.content[0].text.strip()
    return json.loads(raw)


if __name__ == "__main__":
    from pathlib import Path

    samples = json.loads((Path(__file__).parent.parent / "data" / "sample_statements.json").read_text())
    for sample in samples:
        result = score_with_llm(sample["text"])
        print(f"[{sample['label']:>8}] LLM score={result['score']:+.2f}  {result['reasoning']}")
