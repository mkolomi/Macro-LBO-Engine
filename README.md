# Macro-LBO Engine

Scores central bank statements for hawkish/dovish tone, then flows that score through
into a floating-rate LBO debt schedule — the two halves of a question that shows up
constantly in credit/macro interviews: "rates move, what happens to the deal?"

## Why this exists

Two linked pieces, deliberately kept simple enough to defend line-by-line in an interview:

1. A **tone scorer** for central bank statements (`src/sentiment.py`) — no external API
   required, runs offline, and is auditable: you can point at any hit and explain why it
   counted.
2. An **LBO debt schedule** (`src/lbo_schedule.py`) that takes that tone score and adjusts
   the assumed floating base rate, showing how a more hawkish statement raises total
   interest expense over the life of the loan.

## Contents

- `src/fed_lexicon.py` — a compact, hand-built hawkish/dovish phrase list for monetary
  policy language (not the full Loughran-McDonald Master Dictionary — this is scoped
  specifically to rate-decision tone, not general finance sentiment).
- `src/sentiment.py` — counts hawkish/dovish hits per statement and computes a
  `hawkish_index = (hawkish_hits - dovish_hits) / total_words`.
- `src/llm_sentiment.py` — **optional** alternative scorer using the Anthropic API
  instead of keyword counting, for comparison. Only runs if `ANTHROPIC_API_KEY` is set;
  the rest of the pipeline has no dependency on it.
- `src/lbo_schedule.py` — takes a `hawkish_index`, converts it to a rate adjustment in
  bps (clamped to ±200bps), and builds a year-by-year interest/amortization schedule.
  Also produces a sensitivity table across a range of tones.
- `data/sample_statements.json` — four **synthetic, illustrative** statements (hawkish /
  dovish / neutral / mixed) used to sanity-check the scorer. Not real FOMC text — for
  real analysis, pull actual statements from
  [federalreserve.gov/newsevents/pressreleases](https://www.federalreserve.gov/newsevents/pressreleases.htm).
- `app.py` — Streamlit dashboard: pick or paste a statement, see the tone score and the
  resulting debt schedule live.

## Running it

```bash
pip install -r requirements.txt

python src/sentiment.py       # scores the 4 sample statements
python src/lbo_schedule.py    # prints a base-case schedule + tone sensitivity table

streamlit run app.py          # interactive dashboard
```

## Methodology notes

- The tone scorer is keyword-density based, the same first-pass approach research desks
  use before layering on anything more expensive (LLM scoring, human read) — it's
  auditable and has zero external dependency, which matters more for a demo than
  marginal accuracy.
- `hawkish_index` is deliberately small in magnitude (real statements typically fall in
  roughly ±0.03) since it's normalized by total word count; the LBO model scales and
  clamps it rather than assuming any specific range holds exactly.
- The rate-adjustment mapping (`bps_per_hawkish_index_unit`, capped at ±200bps) is a
  simplifying assumption, not a calibrated forecast — the point is to demonstrate the
  mechanism (tone -> forward rate assumption -> interest expense), not to predict actual
  Fed moves.
