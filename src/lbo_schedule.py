"""Map a hawkish/dovish tone score onto an LBO floating-rate debt schedule."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


# hawkish_index (see sentiment.py) is a keyword-density score: real FOMC
# statements typically land in [-0.03, +0.03], while the dense synthetic
# samples in data/sample_statements.json run higher. Scale + clamp so a
# statement that reads as strongly hawkish/dovish shifts the assumed forward
# base rate by at most MAX_ADJUSTMENT_BPS in either direction.
BPS_PER_HAWKISH_INDEX_UNIT = 5_000
MAX_ADJUSTMENT_BPS = 200


def rate_adjustment_bps(hawkish_index: float) -> float:
    raw = hawkish_index * BPS_PER_HAWKISH_INDEX_UNIT
    return max(-MAX_ADJUSTMENT_BPS, min(MAX_ADJUSTMENT_BPS, raw))


@dataclass
class LBOAssumptions:
    principal: float
    base_rate: float          # e.g. SOFR, as a decimal (0.045 = 4.5%)
    spread: float              # lender spread over base, as a decimal
    term_years: int
    amortization_pct_per_year: float = 0.0  # 0 = interest-only / bullet


def build_schedule(assumptions: LBOAssumptions, hawkish_index: float) -> pd.DataFrame:
    adj_bps = rate_adjustment_bps(hawkish_index)
    adjusted_base_rate = assumptions.base_rate + adj_bps / 10_000
    all_in_rate = adjusted_base_rate + assumptions.spread

    rows = []
    balance = assumptions.principal
    annual_amortization = assumptions.principal * assumptions.amortization_pct_per_year

    for year in range(1, assumptions.term_years + 1):
        interest_expense = balance * all_in_rate
        principal_payment = min(annual_amortization, balance)
        balance -= principal_payment
        rows.append({
            "year": year,
            "beginning_balance": round(balance + principal_payment, 2),
            "all_in_rate": round(all_in_rate, 4),
            "interest_expense": round(interest_expense, 2),
            "principal_payment": round(principal_payment, 2),
            "ending_balance": round(balance, 2),
        })

    return pd.DataFrame(rows)


def sensitivity_table(assumptions: LBOAssumptions, hawkish_indices: list[float]) -> pd.DataFrame:
    rows = []
    for hi in hawkish_indices:
        schedule = build_schedule(assumptions, hi)
        rows.append({
            "hawkish_index": hi,
            "rate_adjustment_bps": rate_adjustment_bps(hi),
            "all_in_rate": schedule["all_in_rate"].iloc[0],
            "total_interest_over_term": schedule["interest_expense"].sum(),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    assumptions = LBOAssumptions(
        principal=500_000_000,
        base_rate=0.045,
        spread=0.035,
        term_years=7,
        amortization_pct_per_year=0.01,
    )

    print("=== Base case (neutral tone) ===")
    print(build_schedule(assumptions, hawkish_index=0.0).to_string(index=False))

    print("\n=== Sensitivity to central bank tone ===")
    sens = sensitivity_table(assumptions, hawkish_indices=[-0.03, -0.015, 0.0, 0.015, 0.03])
    print(sens.to_string(index=False))
