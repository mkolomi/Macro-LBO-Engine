"""Streamlit dashboard: paste a central bank statement, see the tone score
and how it flows through into an LBO debt schedule."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
import pandas as pd

from sentiment import score_statement
from lbo_schedule import LBOAssumptions, build_schedule, sensitivity_table, rate_adjustment_bps

st.set_page_config(page_title="Macro-LBO Engine", layout="centered")
st.title("Macro-LBO Engine")
st.caption("Central bank tone scoring -> floating-rate LBO debt schedule")

samples = json.loads((Path(__file__).parent / "data" / "sample_statements.json").read_text())
sample_labels = {s["label"]: s["text"] for s in samples}

choice = st.selectbox("Load a sample statement", ["(write your own)"] + list(sample_labels.keys()))
default_text = sample_labels.get(choice, "")
text = st.text_area("Central bank statement text", value=default_text, height=180)

st.subheader("LBO assumptions")
c1, c2, c3 = st.columns(3)
with c1:
    principal = st.number_input("Principal ($)", value=500_000_000, step=10_000_000)
with c2:
    base_rate = st.number_input("Base rate", value=0.045, format="%.4f")
    spread = st.number_input("Lender spread", value=0.035, format="%.4f")
with c3:
    term_years = st.number_input("Term (years)", value=7, min_value=1, max_value=15)
    amort_pct = st.number_input("Annual amortization %", value=0.01, format="%.4f")

if st.button("Analyze") and text.strip():
    score = score_statement(text)
    adj_bps = rate_adjustment_bps(score.hawkish_index)

    st.metric("Tone", score.label.upper(), delta=f"{adj_bps:+.0f} bps rate adjustment")
    st.write(f"Hawkish index: `{score.hawkish_index:+.4f}` "
             f"({score.hawkish_hits} hawkish hits, {score.dovish_hits} dovish hits, {score.total_words} words)")

    assumptions = LBOAssumptions(principal, base_rate, spread, int(term_years), amort_pct)
    schedule = build_schedule(assumptions, score.hawkish_index)

    st.subheader("Resulting debt schedule")
    st.dataframe(schedule, use_container_width=True)

    st.subheader("Sensitivity: total interest over term vs. tone")
    sens = sensitivity_table(assumptions, hawkish_indices=[-0.03, -0.015, 0.0, 0.015, 0.03])
    st.line_chart(sens.set_index("hawkish_index")["total_interest_over_term"])
