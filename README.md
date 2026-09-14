# Macro-LBO Engine

A two-stage pipeline: score the tone of a central bank policy statement as hawkish or dovish, then
use that score to adjust the assumed floating interest rate in a leveraged buyout (LBO) debt
schedule.

## What this is

This project connects two things that are usually analyzed separately: the language central banks
use in policy statements, and the mechanics of leveraged buyout debt. It turns the question "if a
central bank statement sounds more hawkish, what does that actually do to a highly levered deal's
economics?" into a computable pipeline, rather than leaving it as a qualitative judgment call.

It has two linked parts:

1. **A tone scorer** (`src/sentiment.py`) that reads a central bank statement and produces a single
   number — the "hawkish index" — representing the net hawkish-vs-dovish language in the text.
2. **An LBO debt schedule model** (`src/lbo_schedule.py`) that takes that hawkish index, converts it
   into a floating-rate adjustment, and builds a full year-by-year interest and amortization
   schedule for a loan under that adjusted rate.

A Streamlit app ties the two together: pick or paste in a statement and see both its tone score and
the resulting debt schedule update side by side.

## Contents

- **`src/fed_lexicon.py`** — a hand-built list of hawkish and dovish words and phrases specific to
  central bank rate-decision language (for example, "restrictive" or "elevated inflation" versus
  "accommodative" or "downside risks"). This is a narrow, purpose-built lexicon for monetary policy
  tone, not a general-purpose finance sentiment dictionary such as Loughran-McDonald.
- **`src/sentiment.py`** — scans a statement's text, counts hawkish and dovish hits against the
  lexicon, and computes `hawkish_index = (hawkish_hits - dovish_hits) / total_words`. This runs
  entirely offline with no external API calls, so every score can be traced back to the specific
  words that produced it.
- **`src/llm_sentiment.py`** — an optional second scoring method that sends the statement to an LLM
  (via the Anthropic API) and asks it to rate tone directly, as a point of comparison against the
  keyword-based score. This only runs if an `ANTHROPIC_API_KEY` environment variable is set; the
  rest of the pipeline works without it.
- **`src/lbo_schedule.py`** — takes a `hawkish_index`, maps it to a rate adjustment in basis points
  (capped at ±200bps so a single statement can't produce an unrealistic swing), and builds a
  multi-year interest and amortization schedule for a floating-rate loan at that adjusted rate. Also
  generates a sensitivity table showing how the schedule changes across a range of possible tone
  scores.
- **`data/sample_statements.json`** — four illustrative statements (hawkish, dovish, neutral, and
  mixed) written to check the scorer's behavior across different tones. These are synthetic
  examples, not real FOMC statements — for analysis against real central bank communication, source
  statements directly from
  [federalreserve.gov/newsevents/pressreleases](https://www.federalreserve.gov/newsevents/pressreleases.htm).
- **`app.py`** — a Streamlit dashboard combining both pieces: select or paste a statement, see its
  hawkish index, and see the resulting debt schedule update live.

## Running it

```bash
pip install -r requirements.txt

python src/sentiment.py       # scores the 4 sample statements
python src/lbo_schedule.py    # prints a base-case schedule + tone sensitivity table

streamlit run app.py          # interactive dashboard combining both
```

## Methodology notes

- The keyword-density approach to tone scoring is the same first-pass method used before layering on
  anything more expensive, such as LLM scoring or a human reading of the full text. Its main
  strength is that it's fully auditable — every point of the score traces back to specific words in
  the text — at the cost of missing tone conveyed through sentence structure, negation, or context
  that individual words don't capture.
- The `hawkish_index` is deliberately small in magnitude — real statements typically land in roughly
  the ±0.03 range — since it's normalized by total word count. The LBO model is built to scale and
  clamp this value rather than assume any particular range holds exactly.
- The mapping from hawkish index to a basis-point rate adjustment (`bps_per_hawkish_index_unit`,
  capped at ±200bps) is a simplifying assumption chosen to demonstrate the mechanism — tone flowing
  into a forward rate assumption flowing into interest expense — rather than a model calibrated
  against how the Fed actually sets rates.

## Limitations

- The lexicon-based scorer only recognizes tone conveyed through specific known words and phrases;
  it can miss tone conveyed more subtly and can be thrown off by unusual phrasing.
- The rate-adjustment mapping is illustrative, not empirically fit to historical Fed decisions or
  actual credit spread data.
- The sample statements are synthetic; results on real statements should be checked against the
  actual source text before being treated as meaningful.
