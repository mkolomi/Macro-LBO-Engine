"""Compact hawkish/dovish lexicon for monetary-policy tone scoring.

Not the full Loughran-McDonald Master Dictionary (that's licensed for
academic redistribution, not vendored here) -- this is a smaller,
policy-specific word list built the same way central-bank-watching desks
build a first-pass tone score: bucket the phrases that show up
disproportionately in hawkish vs. dovish FOMC/ECB statements.
"""

HAWKISH_TERMS = {
    "tighten", "tightening", "restrictive", "elevated inflation",
    "persistently high", "further increases", "vigilant", "upside risk",
    "overheating", "raise rates", "rate hike", "inflationary pressure",
    "firmly committed", "additional policy firming", "sustained period",
    "above target", "strong labor market", "excess demand",
}

DOVISH_TERMS = {
    "accommodative", "support the economy", "downside risk", "patient",
    "gradual", "ample time", "softening", "below target", "slack",
    "cut rates", "rate cut", "stimulus", "loosen", "loosening",
    "economic weakness", "labor market cooling", "moderating inflation",
    "pause", "on hold",
}
