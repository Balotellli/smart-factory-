
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import math

import joblib
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Smart Factory | Industrial Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Presentation only: no external fonts, icons, images, or extra libraries.
st.markdown(
    """
<style>
:root {
    --navy: #071624;
    --navy-card: #0d2235;
    --navy-raise: #112b41;
    --border: #234459;
    --green: #32d69b;
    --green-soft: #9ce9c6;
    --text: #eff7f8;
    --muted: #97adbc;
}
html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #071624 !important;
    color: var(--text);
}
[data-testid="stAppViewContainer"] > .main {
    background: radial-gradient(ellipse at 84% 0%, #102c3b 0%, #071624 46%);
}
[data-testid="stMainBlockContainer"] {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
    background: #0a1c2e !important;
    border-right: 1px solid #1d394d;
}
[data-testid="stSidebar"] .stRadio label {
    padding: .36rem .25rem;
    color: #d9e8eb;
}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: var(--muted) !important;
}
h1, h2, h3, h4, p, label, .stMarkdown { color: var(--text); }
h1 { letter-spacing: -.045em; }
h2, h3 { letter-spacing: -.025em; }
p, [data-testid="stCaptionContainer"] { color: #b5c5cf; }
[data-testid="stMetric"] {
    background: #0d2235;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem 1.1rem;
}
[data-testid="stMetricLabel"] p { color: var(--muted) !important; }
[data-testid="stMetricValue"] { color: var(--text) !important; }
div[data-testid="stForm"] {
    background: #0d2235;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.1rem 1.35rem 1.35rem;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-baseweb="select"] > div {
    background-color: #071b2d !important;
    color: #eef7f6 !important;
    border-color: #2c5062 !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] label p,
[data-testid="stNumberInput"] label p,
[data-testid="stSelectbox"] label p { color: #c3d5da !important; }
.stButton button[kind="primary"],
[data-testid="stFormSubmitButton"] button {
    background: #32d69b !important;
    color: #062033 !important;
    border: 1px solid #32d69b !important;
    border-radius: 9px !important;
    font-weight: 750 !important;
    min-height: 2.65rem;
}
.stButton button[kind="primary"]:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background: #7fe9c0 !important;
    border-color: #7fe9c0 !important;
}
.stButton button, [data-testid="stDownloadButton"] button {
    border-radius: 9px !important;
}
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; }
[data-testid="stAlert"] { border-radius: 12px; }
hr { border-color: #234459 !important; }
.sf-brand {
    font-size: 13px;
    font-weight: 850;
    letter-spacing: .23em;
    color: var(--green);
    margin: .5rem 0 .15rem;
}
.sf-brand-sub { font-size: 11px; letter-spacing: .13em; color: #91a9b8; }
.sf-overline {
    font-size: 11px;
    color: var(--green);
    letter-spacing: .17em;
    text-transform: uppercase;
    font-weight: 750;
    margin-bottom: 10px;
}
.sf-hero {
    padding: 1.8rem 2rem;
    border: 1px solid #244657;
    border-radius: 18px;
    background: linear-gradient(110deg, #102b40 0%, #0b2134 60%, #0b292f 100%);
    margin-bottom: 1.4rem;
    overflow: hidden;
    position: relative;
}
.sf-hero:after {
    content: "";
    position: absolute;
    right: -90px;
    top: -135px;
    width: 300px;
    height: 300px;
    border: 1px solid rgba(50,214,155,.17);
    border-radius: 50%;
    box-shadow: 0 0 0 44px rgba(50,214,155,.035), 0 0 0 90px rgba(50,214,155,.025);
    pointer-events: none;
}
.sf-hero h1 { font-size: clamp(2rem, 3.6vw, 3.1rem); line-height: 1.1; margin: 0 0 .6rem; }
.sf-hero p { max-width: 720px; color: #b9cad4; margin: 0; font-size: 14px; }
.sf-stat-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 1rem 0 1.25rem; }
.sf-stat {
    padding: 1.25rem 1.35rem;
    background: var(--navy-card);
    border: 1px solid var(--border);
    border-radius: 15px;
}
.sf-stat-label { font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: #9eb5c1; font-weight: 650; }
.sf-stat-value { font-size: 29px; color: #f1f9f9; font-weight: 740; letter-spacing: -.035em; margin: 8px 0 2px; overflow-wrap: anywhere; }
.sf-stat-note { color: #8eabb8; font-size: 12px; }
.sf-stat--accent { border-color: #2e7869; background: linear-gradient(160deg, #0d2c35, #0b2234); }
.sf-stat--accent .sf-stat-value { color: var(--green-soft); }
.sf-section { font-size: 21px; font-weight: 700; letter-spacing: -.025em; margin: 1.45rem 0 .2rem; }
.sf-muted { color: #a2b8c4; font-size: 13px; margin-bottom: .9rem; }
.sf-rule {
    padding: 1.05rem 1.2rem;
    margin: .48rem 0;
    border: 1px solid #2a4b5c;
    background: #0e2537;
    border-radius: 12px;
}
.sf-rule-title { display: flex; align-items: center; justify-content: space-between; gap: 1rem; font-weight: 700; color: #eff8f8; }
.sf-rule-desc { margin-top: .5rem; color: #a6becb; font-size: 12px; }
.sf-tag { display: inline-block; color: #aeead3; border: 1px solid #276a5c; background: #0d3439; border-radius: 99px; font-size: 10px; padding: .32rem .68rem; white-space: nowrap; }
.sf-tag--inactive { color: #b5cbd2; border-color: #315268; background: #143045; }
.sf-notice {
    background: #0b2932;
    color: #b0d8cd;
    border: 1px solid #235d54;
    border-radius: 11px;
    padding: .85rem 1.05rem;
    font-size: 12px;
    line-height: 1.6;
    margin: 1rem 0;
}
.sf-side-foot { padding-top: 1.2rem; color: #849cae; font-size: 11px; line-height: 1.65; }
@media (max-width: 740px) {
    .sf-stat-grid { grid-template-columns: 1fr; }
    .sf-hero { padding: 1.25rem; }
    .sf-stat-value { font-size: 26px; }
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource
def load_model():
    """Load the same saved Random Forest and encoded feature order."""
    file = Path(__file__).resolve().parent / "machine_model.joblib"
    if not file.is_file():
        raise FileNotFoundError("machine_model.joblib must be next to app.py")
    saved = joblib.load(file)
    return saved["model"], saved["features"]


try:
    model, features = load_model()
except Exception as exc:
    st.error(f"The saved machine-learning model could not be loaded: {exc}")
    st.stop()

if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None


def stat_card(label, value, note="", accent=False):
    tone = " sf-stat--accent" if accent else ""
    st.markdown(
        f'<div class="sf-stat{tone}">'
        f'<div class="sf-stat-label">{escape(str(label))}</div>'
        f'<div class="sf-stat-value">{escape(str(value))}</div>'
        f'<div class="sf-stat-note">{escape(str(note))}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def card_row(cards):
    html = '<div class="sf-stat-grid">'
    for label, value, note, accent in cards:
        tone = " sf-stat--accent" if accent else ""
        html += (
            f'<div class="sf-stat{tone}">'
            f'<div class="sf-stat-label">{escape(str(label))}</div>'
            f'<div class="sf-stat-value">{escape(str(value))}</div>'
            f'<div class="sf-stat-note">{escape(str(note))}</div>'
            '</div>'
        )
    st.markdown(html + '</div>', unsafe_allow_html=True)


def heading(title, subtitle=None):
    st.markdown(f'<div class="sf-section">{escape(title)}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sf-muted">{escape(subtitle)}</div>', unsafe_allow_html=True)


def score_disclaimer():
    st.markdown(
        '<div class="sf-notice">'
        '<strong>Model interpretation:</strong> The failure-class score describes how '
        'the classifier evaluates these measurements. It is not a validated '
        'probability of a breakdown in the next hour, day, or week. '
        'All engineering limits shown here come from the synthetic AI4I dataset.'
        '</div>',
        unsafe_allow_html=True,
    )


def analyze(machine_id, product, air, process, speed, torque, wear):
    """Preserve the original model feature preparation and AI4I rules."""
    values = {
        "product_type": product,
        "air_temp_k": float(air),
        "process_temp_k": float(process),
        "speed_rpm": float(speed),
        "torque_nm": float(torque),
        "tool_wear_min": float(wear),
    }
    inputs = pd.get_dummies(pd.DataFrame([values]), columns=["product_type"], dtype=int)
    inputs = inputs.reindex(columns=features, fill_value=0)

    score = float(model.predict_proba(inputs)[0, 1])
    prediction = int(model.predict(inputs)[0])

    power = (2 * math.pi * speed * torque) / 60
    temp_gap = process - air
    wear_load = wear * torque
    limit = {"L": 11000, "M": 12000, "H": 13000}[product]

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "machine_id": machine_id.strip(),
        **values,
        "score": score,
        "prediction": prediction,
        "power_w": power,
        "temperature_gap_k": temp_gap,
        "wear_load": wear_load,
        "power_alert": power < 3500 or power > 9000,
        "heat_alert": temp_gap < 8.6 and speed < 1380,
        "overstrain_alert": wear_load > limit,
    }


def rule_card(name, triggered, description):
    status = "RULE TRIGGERED" if triggered else "NOT TRIGGERED"
    cls = "" if triggered else " sf-tag--inactive"
    st.markdown(
        '<div class="sf-rule">'
        '<div class="sf-rule-title">'
        f'<span>{escape(name)}</span>'
        f'<span class="sf-tag{cls}">{status}</span>'
        '</div>'
        f'<div class="sf-rule-desc">{escape(description)}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


# ---- Persistent page shell -------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sf-brand">SMART FACTORY</div>', unsafe_allow_html=True)
    st.markdown('<div class="sf-brand-sub">ANALYTICS CONSOLE / 2.0</div>', unsafe_allow_html=True)
    st.divider()
    page = st.radio(
        "Navigation",
        ["Machine Analysis", "Engineering Diagnostics", "Session History"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("SESSION SUMMARY")
    st.metric("Measurements analyzed", len(st.session_state.history))
    last = st.session_state.last_result
    if last is not None:
        st.metric("Latest class score", f"{last['score']:.1%}")
        st.caption(f"Latest machine: {last['machine_id']}")
    st.markdown(
        '<div class="sf-side-foot">'
        'AI4I 2020 synthetic data<br>'
        'Random Forest classification<br>'
        'Engineering rule diagnostics<br><br>'
        'Educational engineering prototype'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="sf-hero">'
    '<div class="sf-overline">Industrial intelligence / monitoring console</div>'
    '<h1>Smart Factory Analytics</h1>'
    '<p>Machine condition classification, engineering diagnostics, and session-based '
    'measurement monitoring in one analytical workspace.</p>'
    '</div>',
    unsafe_allow_html=True,
)


# ---- Machine Analysis ------------------------------------------------------
if page == "Machine Analysis":
    heading("Machine Analysis", "Evaluate one set of simulated industrial operating measurements.")
    with st.form("machine_form"):
        id_col, type_col = st.columns([2, 1])
        with id_col:
            machine_id = st.text_input("Machine ID", value="DEMO-001")
        with type_col:
            product = st.selectbox("Product type", ["L", "M", "H"])

        st.markdown("**Sensor measurements**")
        c1, c2, c3 = st.columns(3)
        with c1:
            air = st.number_input("Air temperature (K)", min_value=0.1, value=300.0, step=0.1)
            process = st.number_input("Process temperature (K)", min_value=0.1, value=310.0, step=0.1)
        with c2:
            speed = st.number_input("Rotational speed (RPM)", min_value=0.0, value=1500.0, step=10.0)
            torque = st.number_input("Torque (Nm)", min_value=0.0, value=40.0, step=1.0)
        with c3:
            wear = st.number_input("Tool wear (min)", min_value=0.0, value=100.0, step=1.0)
        submitted = st.form_submit_button("Run Machine Analysis", use_container_width=True)

    if submitted:
        if not machine_id.strip():
            st.error("Machine ID cannot be empty.")
        else:
            result = analyze(machine_id, product, air, process, speed, torque, wear)
            st.session_state.last_result = result
            st.session_state.history.append(result)

    result = st.session_state.last_result
    if result is None:
        heading("Analysis Results")
        st.info("No machine has been analyzed in this session yet.")
    else:
        heading("Analysis Results", f"Latest reading: {result['machine_id']} | {result['timestamp_utc']} UTC")
        triggered_count = sum(result[k] for k in ("power_alert", "heat_alert", "overstrain_alert"))
        card_row([
            ("Failure-class score", f"{result['score']:.1%}", "Random Forest output", True),
            ("Model classification", "Failure-related" if result["prediction"] else "Normal", "Fixed 50% classification threshold", False),
            ("Diagnostic rules triggered", f"{triggered_count} / 3", "AI4I simulation rules", False),
        ])
        score_disclaimer()
        heading("Latest Operating Profile", "Temperature values and key mechanical readings from the latest submission.")
        chart_col, measure_col = st.columns([1.15, 1])
        with chart_col:
            st.markdown("**Temperature comparison (K)**")
            temp_df = pd.DataFrame({
                "Measurement": ["Air", "Process"],
                "Temperature (K)": [result["air_temp_k"], result["process_temp_k"]],
            }).set_index("Measurement")
            st.bar_chart(temp_df, color="#32d69b", height=245)
        with measure_col:
            st.markdown("**Mechanical readings**")
            a, b = st.columns(2)
            a.metric("Rotational speed", f"{result['speed_rpm']:,.0f} RPM")
            b.metric("Torque", f"{result['torque_nm']:,.1f} Nm")
            st.metric("Accumulated tool wear", f"{result['tool_wear_min']:,.0f} min")


# ---- Engineering Diagnostics ----------------------------------------------
elif page == "Engineering Diagnostics":
    heading("Engineering Diagnostics", "Explain operating conditions using the AI4I simulation's physical rules.")
    result = st.session_state.last_result
    if result is None:
        st.info("Analyze a machine to populate its engineering diagnostics.")
    else:
        st.markdown(f"**Machine:** {escape(result['machine_id'])}")
        card_row([
            ("Mechanical power", f"{result['power_w']:,.0f} W", "Derived from RPM and torque", True),
            ("Temperature difference", f"{result['temperature_gap_k']:.2f} K", "Process minus ambient", False),
            ("Wear-load index", f"{result['wear_load']:,.0f}", "Tool wear multiplied by torque", False),
        ])
        heading("Rule Evaluation", "These thresholds reproduce the failure-generation conditions of the synthetic dataset.")
        rule_card(
            "Mechanical power",
            result["power_alert"],
            f"Observed: {result['power_w']:,.0f} W. Rule: below 3,500 W or above 9,000 W.",
        )
        rule_card(
            "Heat dissipation",
            result["heat_alert"],
            f"Temperature gap: {result['temperature_gap_k']:.2f} K; speed: {result['speed_rpm']:,.0f} RPM. "
            "Rule: gap below 8.6 K AND speed below 1,380 RPM.",
        )
        limit = {"L": 11000, "M": 12000, "H": 13000}[result["product_type"]]
        rule_card(
            "Mechanical overstrain",
            result["overstrain_alert"],
            f"Wear-load index: {result['wear_load']:,.0f}. Rule: exceeds {limit:,} for product type {result['product_type']}.",
        )
        triggered = [name for name, flag in (
            ("power condition", result["power_alert"]),
            ("heat dissipation condition", result["heat_alert"]),
            ("overstrain condition", result["overstrain_alert"]),
        ) if flag]
        if triggered:
            st.markdown(
                "**Diagnostic summary:** The current reading triggered "
                + ", ".join(triggered)
                + ". Review the associated measurements in the context of this simulation."
            )
        else:
            st.markdown("**Diagnostic summary:** None of the three simulated engineering rules was triggered for this reading.")
        score_disclaimer()


# ---- Session History -------------------------------------------------------
else:
    heading("Session History", "Review analyses performed during the current browser session.")
    history = st.session_state.history
    if not history:
        st.info("No measurements are recorded in this session yet.")
    else:
        df = pd.DataFrame(history)
        unique_machines = df["machine_id"].nunique()
        card_row([
            ("Recorded analyses", len(df), "Current session only", True),
            ("Machine identifiers", unique_machines, "Unique IDs analyzed", False),
            ("Failure-related classes", int(df["prediction"].sum()), "Model classifications", False),
        ])
        machine_options = ["All machines"] + sorted(df["machine_id"].unique().tolist())
        selected_machine = st.selectbox("Filter by machine", machine_options)
        shown = df if selected_machine == "All machines" else df[df["machine_id"] == selected_machine]

        heading("Score Trend", "Scores are shown in submission order, not as future failure probabilities.")
        score_chart = pd.DataFrame({
            "Observation": range(1, len(shown) + 1),
            "Failure-class score (%)": (shown["score"].to_numpy() * 100).round(2),
        }).set_index("Observation")
        st.line_chart(score_chart, color="#32d69b", height=280)

        heading("Temperature Trend")
        temps = shown[["air_temp_k", "process_temp_k"]].copy()
        temps.index = range(1, len(temps) + 1)
        temps.index.name = "Observation"
        temps.columns = ["Air temperature (K)", "Process temperature (K)"]
        st.line_chart(temps, color=["#32d69b", "#74b4c8"], height=250)

        heading("Measurement Log")
        table_columns = [
            "timestamp_utc", "machine_id", "product_type", "air_temp_k",
            "process_temp_k", "speed_rpm", "torque_nm", "tool_wear_min",
            "score", "prediction", "power_w", "temperature_gap_k", "wear_load",
            "power_alert", "heat_alert", "overstrain_alert",
        ]
        display_df = shown[table_columns].copy()
        display_df["score"] = (display_df["score"] * 100).round(1)
        display_df = display_df.rename(columns={
            "timestamp_utc": "Time (UTC)", "machine_id": "Machine",
            "product_type": "Type", "score": "Class score (%)",
            "prediction": "Class (0/1)",
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        download_col, clear_col = st.columns([2, 1])
        with download_col:
            st.download_button(
                "Download Session CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="smart_factory_session_history.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with clear_col:
            if st.button("Clear Session History", use_container_width=True):
                st.session_state.history = []
                st.session_state.last_result = None
                st.rerun()
    st.markdown(
        '<div class="sf-notice">Session history is stored temporarily in the current app session. '
        'It is not connected to the Databricks Delta monitoring table and may disappear '
        'after a reload or session reset.</div>',
        unsafe_allow_html=True,
    )

st.divider()
st.caption(
    "Smart Factory Analytics 2.0 | AI4I 2020 synthetic dataset | "
    "Machine condition classification and engineering diagnostics | Educational prototype"
)
