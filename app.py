
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math

import joblib
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Smart Factory Analytics",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Minimal visual theme: no charts, emojis, custom fonts, or external assets.
st.markdown(
    """
<style>
:root { color-scheme: dark; }
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background: #0d1015 !important;
    color: #ecf0f5;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] {
    max-width: 920px;
    padding-top: 2.4rem;
    padding-bottom: 3rem;
}
h1, h2, h3, p, label { color: #ecf0f5; }
h1 { font-size: clamp(1.8rem, 4vw, 2.55rem) !important; letter-spacing: -.04em; }
h3 { font-size: 1.12rem !important; }
[data-testid="stCaptionContainer"] { color: #9da8b7; }
[data-testid="stForm"] {
    background: #171c24;
    border: 1px solid #313a47;
    border-radius: 12px;
    padding: 1rem 1.25rem 1.25rem;
}
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-baseweb="select"] > div {
    background: #11161e !important;
    color: #f0f4fa !important;
    border-color: #3a4554 !important;
}
[data-testid="stFormSubmitButton"] button {
    background: #3478f6 !important;
    border: 1px solid #3478f6 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 650;
    min-height: 2.75rem;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: #4e8dff !important;
    border-color: #4e8dff !important;
}
[data-testid="stMetric"] {
    background: #171c24;
    border: 1px solid #313a47;
    border-radius: 10px;
    padding: .85rem 1rem;
}
[data-testid="stMetricLabel"] p { color: #a6b0bf !important; }
[data-testid="stMetricValue"] { color: #f3f6fb !important; }
[data-testid="stExpander"] {
    background: #151a22;
    border: 1px solid #313a47;
    border-radius: 10px;
}
.sf-eyebrow {
    color: #73a7ff;
    font-weight: 700;
    font-size: .72rem;
    letter-spacing: .16em;
    margin-bottom: .5rem;
}
.sf-subtitle { color: #a6b1bf; font-size: .94rem; margin-bottom: 1.45rem; }
.sf-result {
    border: 1px solid #344154;
    border-left: 4px solid #3478f6;
    border-radius: 10px;
    background: #171c24;
    padding: 1rem 1.15rem;
    margin-top: 1.05rem;
    margin-bottom: 1rem;
}
.sf-result-label { color: #a6b1bf; font-size: .75rem; margin-bottom: .25rem; }
.sf-result-title { color: #f5f7fc; font-size: 1.17rem; font-weight: 680; }
.sf-result-subtitle { color: #a6b1bf; font-size: .80rem; margin-top: .3rem; }
.sf-rules {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .65rem;
    margin: .8rem 0 1rem;
}
.sf-rule {
    padding: .75rem .85rem;
    border: 1px solid #343e4b;
    border-radius: 9px;
    background: #171c24;
}
.sf-rule-name { color: #abb6c4; font-size: .78rem; margin-bottom: .45rem; }
.sf-rule-status { color: #d5dce6; font-size: .9rem; font-weight: 650; }
.sf-rule.flagged { border-color: #3478f6; }
.sf-rule.flagged .sf-rule-status { color: #80b1ff; }
.sf-fineprint { color: #94a1b2; font-size: .79rem; line-height: 1.55; margin-bottom: 1.15rem; }
@media (max-width: 650px) {
    .sf-rules { grid-template-columns: 1fr; }
    [data-testid="stMainBlockContainer"] { padding-top: 1.3rem; }
    [data-testid="stForm"] { padding: .8rem; }
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_model():
    model_file = Path(__file__).resolve().parent / "machine_model.joblib"
    if not model_file.is_file():
        raise FileNotFoundError("machine_model.joblib must be in the same folder as app.py")
    saved = joblib.load(model_file)
    return saved["model"], saved["features"]


try:
    model, features = load_model()
except Exception as exc:
    st.error(f"Could not load the saved machine-learning model: {exc}")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None


def analyze(machine_id, product, air, process, speed, torque, wear):
    """Original AI4I model preparation, prediction, and simulation rules."""
    values = {
        "product_type": product,
        "air_temp_k": float(air),
        "process_temp_k": float(process),
        "speed_rpm": float(speed),
        "torque_nm": float(torque),
        "tool_wear_min": float(wear),
    }
    row = pd.get_dummies(pd.DataFrame([values]), columns=["product_type"], dtype=int)
    row = row.reindex(columns=features, fill_value=0)

    score = float(model.predict_proba(row)[0, 1])
    classification = int(model.predict(row)[0])
    power = (2 * math.pi * speed * torque) / 60
    gap = process - air
    wear_load = wear * torque
    overstrain_limit = {"L": 11000, "M": 12000, "H": 13000}[product]

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "machine_id": machine_id.strip(),
        **values,
        "score": score,
        "prediction": classification,
        "power_w": power,
        "temperature_gap_k": gap,
        "wear_load": wear_load,
        "power_alert": power < 3500 or power > 9000,
        "heat_alert": gap < 8.6 and speed < 1380,
        "overstrain_alert": wear_load > overstrain_limit,
    }


def status_box(name, triggered):
    text = "Flagged" if triggered else "Not triggered"
    flagged = " flagged" if triggered else ""
    return (
        f'<div class="sf-rule{flagged}">'
        f'<div class="sf-rule-name">{escape(name)}</div>'
        f'<div class="sf-rule-status">{text}</div>'
        "</div>"
    )


st.markdown('<div class="sf-eyebrow">SMART FACTORY ANALYTICS</div>', unsafe_allow_html=True)
st.title("Machine condition analysis")
st.markdown(
    '<div class="sf-subtitle">Assess operating measurements using a trained Random Forest '
    'and simulated engineering diagnostic rules.</div>',
    unsafe_allow_html=True,
)

with st.form("machine_form"):
    st.markdown("**Machine inputs**")
    a, b = st.columns([1.6, 1])
    with a:
        machine_id = st.text_input("Machine ID", value="DEMO-001")
    with b:
        product = st.selectbox("Product type", ["L", "M", "H"])

    c1, c2 = st.columns(2)
    with c1:
        air = st.number_input("Air temperature (K)", min_value=0.1, value=300.0, step=0.1)
        speed = st.number_input("Rotational speed (RPM)", min_value=0.0, value=1500.0, step=10.0)
        wear = st.number_input("Tool wear (min)", min_value=0.0, value=100.0, step=1.0)
    with c2:
        process = st.number_input("Process temperature (K)", min_value=0.1, value=310.0, step=0.1)
        torque = st.number_input("Torque (Nm)", min_value=0.0, value=40.0, step=1.0)

    submitted = st.form_submit_button("Analyze machine", use_container_width=True)

if submitted:
    if not machine_id.strip():
        st.error("Enter a machine ID.")
    else:
        result = analyze(machine_id, product, air, process, speed, torque, wear)
        st.session_state.last_result = result
        st.session_state.history.append(result)

result = st.session_state.last_result
if result is not None:
    st.markdown("### Analysis result")
    name = "Failure-related conditions" if result["prediction"] else "Normal operating conditions"
    st.markdown(
        '<div class="sf-result">'
        f'<div class="sf-result-label">Machine {escape(result["machine_id"])}</div>'
        f'<div class="sf-result-title">{name}</div>'
        '<div class="sf-result-subtitle">Classification from the trained Random Forest model</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.metric("Failure-class score", f'{result["score"]:.1%}')

    st.markdown("**Engineering checks**")
    st.markdown(
        '<div class="sf-rules">'
        + status_box("Power", result["power_alert"])
        + status_box("Heat dissipation", result["heat_alert"])
        + status_box("Overstrain", result["overstrain_alert"])
        + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sf-fineprint">The failure-class score is a model classification output, '
        'not a validated probability of a future breakdown. The engineering checks use '
        'rules from the synthetic AI4I dataset, not real-world operating safety limits.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Engineering measurements"):
        m1, m2, m3 = st.columns(3)
        m1.metric("Mechanical power", f'{result["power_w"]:,.0f} W')
        m2.metric("Temperature gap", f'{result["temperature_gap_k"]:.2f} K')
        m3.metric("Wear x torque", f'{result["wear_load"]:,.0f}')

if st.session_state.history:
    with st.expander(f'Session history ({len(st.session_state.history)})'):
        history = pd.DataFrame(st.session_state.history)
        table = history[["timestamp_utc", "machine_id", "score", "prediction"]].copy()
        table["score"] = (table["score"] * 100).round(1)
        table["prediction"] = table["prediction"].map({0: "Normal", 1: "Failure-related"})
        table = table.rename(columns={
            "timestamp_utc": "Time (UTC)",
            "machine_id": "Machine",
            "score": "Class score (%)",
            "prediction": "Classification",
        })
        st.dataframe(table.iloc[::-1], use_container_width=True, hide_index=True)
        st.download_button(
            "Download full history (CSV)",
            data=history.to_csv(index=False),
            file_name="smart_factory_history.csv",
            mime="text/csv",
        )
        st.caption("Session history is temporary and is not saved to the Databricks Delta table.")
