"""Score central bank statement text for hawkish/dovish tone."""
from __future__ import annotations

import re
from dataclasses import dataclass

from fed_lexicon import HAWKISH_TERMS, DOVISH_TERMS


@dataclass
class ToneScore:
    hawkish_hits: int
    dovish_hits: int
    total_words: int
    hawkish_index: float  # (hawkish - dovish) / total_words; small for real statements, larger for keyword-dense text

    @property
    def label(self) -> str:
        if self.hawkish_index > 0.005:
            return "hawkish"
        if self.hawkish_index < -0.005:
            return "dovish"
        return "neutral"


def _count_terms(text: str, terms: set[str]) -> int:
    text_lower = text.lower()
    return sum(text_lower.count(term) for term in terms)


def score_statement(text: str) -> ToneScore:
    words = re.findall(r"\w+", text)
    total_words = max(len(words), 1)
    hawkish_hits = _count_terms(text, HAWKISH_TERMS)
    dovish_hits = _count_terms(text, DOVISH_TERMS)
    hawkish_index = (hawkish_hits - dovish_hits) / total_words
    return ToneScore(hawkish_hits, dovish_hits, total_words, hawkish_index)


if __name__ == "__main__":
    from pathlib import Path
    import json

    samples = json.loads((Path(__file__).parent.parent / "data" / "sample_statements.json").read_text())
    for sample in samples:
        score = score_statement(sample["text"])
        print(f"[{sample['label']:>8}] hawkish_index={score.hawkish_index:+.4f}  "
              f"({score.hawkish_hits} hawkish / {score.dovish_hits} dovish hits, "
              f"{score.total_words} words)  -> classified as {score.label}")
