
from datetime import datetime, timezone
from pathlib import Path
import math
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Smart Factory 2.0",
    page_icon="🏭",
    layout="wide"
)

@st.cache_resource
def load_model():
    saved = joblib.load(
        Path(__file__).parent / "machine_model.joblib"
    )
    return saved["model"], saved["features"]

model, features = load_model()

if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

st.title("🏭 Smart Factory Analytics 2.0")
st.caption(
    "Educational prototype using synthetic AI4I data, "
    "not a verified breakdown forecasting system."
)

tab1, tab2, tab3 = st.tabs([
    "Machine analysis",
    "Engineering diagnostics",
    "Session history"
])

# TAB 1: MACHINE ANALYSIS
with tab1:

    with st.form("machine_form"):

        machine_id = st.text_input(
            "Machine ID", "DEMO-001"
        )

        product = st.selectbox(
            "Product type", ["L", "M", "H"]
        )

        left, right = st.columns(2)

        with left:
            air = st.number_input(
                "Air temperature (K)",
                min_value=0.1, value=300.0
            )
            speed = st.number_input(
                "Rotational speed (RPM)",
                min_value=0.0, value=1500.0
            )
            wear = st.number_input(
                "Tool wear (min)",
                min_value=0.0, value=100.0
            )

        with right:
            process = st.number_input(
                "Process temperature (K)",
                min_value=0.1, value=310.0
            )
            torque = st.number_input(
                "Torque (Nm)",
                min_value=0.0, value=40.0
            )

        submitted = st.form_submit_button(
            "Analyze machine"
        )

    if submitted:

        if not machine_id.strip():
            st.error("Enter a machine ID.")

        else:
            values = {
                "product_type": product,
                "air_temp_k": air,
                "process_temp_k": process,
                "speed_rpm": speed,
                "torque_nm": torque,
                "tool_wear_min": wear,
            }

            inputs = pd.get_dummies(
                pd.DataFrame([values]),
                columns=["product_type"],
                dtype=int
            )

            inputs = inputs.reindex(
                columns=features,
                fill_value=0
            )

            score = float(
                model.predict_proba(inputs)[0, 1]
            )

            prediction = int(
                model.predict(inputs)[0]
            )

            # Engineering calculations
            power = (2 * math.pi * speed * torque) / 60
            temp_gap = process - air
            wear_load = wear * torque

            limit = {
                "L": 11000,
                "M": 12000,
                "H": 13000
            }[product]

            result = {
                "timestamp_utc": datetime.now(
                    timezone.utc
                ).isoformat(timespec="seconds"),
                "machine_id": machine_id.strip(),
                **values,
                "score": score,
                "prediction": prediction,
                "power_w": power,
                "temperature_gap_k": temp_gap,
                "wear_load": wear_load,
                "power_alert": (
                    power < 3500 or power > 9000
                ),
                "heat_alert": (
                    temp_gap < 8.6 and speed < 1380
                ),
                "overstrain_alert": (
                    wear_load > limit
                ),
            }

            st.session_state.last_result = result
            st.session_state.history.append(result)

    result = st.session_state.last_result

    if result is not None:

        st.metric(
            "Failure-class score",
            f"{result['score']:.1%}"
        )

        if result["prediction"] == 1:
            st.warning(
                "Model classification: FAILURE-RELATED"
            )
        else:
            st.info(
                "Model classification: NORMAL"
            )

        st.caption(
            "Uses a 50% classification threshold. "
            "The score is not the probability "
            "of breakdown tomorrow."
        )

# TAB 2: ENGINEERING DIAGNOSTICS
with tab2:

    result = st.session_state.last_result

    if result is None:
        st.info(
            "First analyze a machine in the "
            "Machine analysis tab."
        )

    else:
        a, b, c = st.columns(3)

        a.metric(
            "Mechanical power",
            f"{result['power_w']:,.0f} W"
        )

        b.metric(
            "Temperature difference",
            f"{result['temperature_gap_k']:.2f} K"
        )

        c.metric(
            "Wear × torque",
            f"{result['wear_load']:,.0f} min·Nm"
        )

        checks = {
            "Power outside simulation limits":
                result["power_alert"],
            "Heat dissipation rule":
                result["heat_alert"],
            "Overstrain rule":
                result["overstrain_alert"],
        }

        for label, triggered in checks.items():

            if triggered:
                st.warning(
                    f"Rule triggered: {label}"
                )
            else:
                st.success(
                    f"Not triggered: {label}"
                )

        st.caption(
            "These are rules from the synthetic "
            "AI4I dataset, NOT real industrial "
            "safety limits."
        )

# TAB 3: SESSION HISTORY
with tab3:

    st.subheader(
        "Measurements from this session"
    )

    if st.session_state.history:

        history = pd.DataFrame(
            st.session_state.history
        )

        st.dataframe(
            history,
            use_container_width=True
        )

        st.download_button(
            "Download CSV",
            history.to_csv(index=False),
            file_name="smart_factory_history.csv",
            mime="text/csv",
        )

    else:
        st.info(
            "No measurements recorded yet."
        )

    st.caption(
        "Session history is temporary. "
        "It does not write to the Lesson 19 Delta table."
    )
