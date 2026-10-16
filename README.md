[README (5).md](https://github.com/user-attachments/files/33544216/README.5.md)
# Smart Factory Analytics 2.0

**Industrial machine-condition monitoring with Databricks, machine learning, and engineering diagnostics**

[**Live application**](https://59gnmdhqpguufrdhxv5zl7.streamlit.app/) · [**Source code**](https://github.com/Balotellli/smart-factory-) · [**Dataset (UCI)**](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)

## Overview

Smart Factory Analytics is an interactive industrial condition-monitoring prototype. It combines a **Random Forest classification model** with **engineering-based diagnostic rules** to analyze machine operating measurements and help users investigate conditions associated with equipment failure.

I developed the data-processing and analysis workflow in **Databricks** using **PySpark, SQL, Delta tables, and Python**, then built a **Streamlit** interface that allows users to enter measurements, receive model results, inspect diagnostic warnings, and compare entries from their session.

The project uses the **AI4I 2020 Predictive Maintenance Dataset**, containing **10,000 synthetic operating observations**. It demonstrates condition monitoring and failure classification; it is **not** a validated predictor of when a real machine will break down.

## Features

### 1. Machine analysis

Enter six operating inputs:

- Product category: **L, M, or H**
- Air temperature (**K**) and process temperature (**K**)
- Rotational speed (**RPM**)
- Torque (**Nm**)
- Tool wear (**minutes**)

The model returns a **failure-class score** and a **normal/failure-related classification**, currently using a 50% decision threshold. The score describes the model's assessment of the current observation, **not** a calibrated probability of a future breakdown.

### 2. Engineering diagnostics

The application calculates additional indicators from the same measurements:

| Indicator | Calculation | Application |
|---|---|---|
| Mechanical power | `2 × π × RPM × torque / 60` | Flags values outside the dataset's simulated power range |
| Temperature difference | `process temperature − air temperature` | Checks the simulated heat-dissipation rule together with RPM |
| Wear–load index | `tool wear × torque` | Checks product-category-specific simulated overstrain limits |

The rules help explain **which measured conditions trigger a warning**, independently of the machine-learning classification. Their thresholds are defined by the synthetic dataset, **not real industrial safety specifications**.

### 3. Session history

The app records each analysis in the current Streamlit session, including the entered measurements, timestamp, model output, and engineering checks. Users can review the entries and **download a CSV**.

The Databricks notebook also implements a separate **Delta measurement log** for manually submitted test readings. The public Streamlit application's history is session-based and **is not connected to that persistent Delta table**.

## Results

### Dataset analysis

| Result | Value |
|---|---:|
| Total synthetic operating observations | **10,000** |
| Observations labeled normal | **9,661 (96.61%)** |
| Observations labeled machine failure | **339 (3.39%)** |

The imbalance matters: a model that almost always predicts “normal” could appear accurate while missing many failures. For this reason, the notebook evaluates **precision, recall, F1-score, a confusion matrix, and average precision** on a held-out test split, rather than relying on accuracy alone.

### Engineering-rule checks

I reproduced three of the dataset's defined failure mechanisms from the operating measurements and compared the calculated flags with their original labels:

| Failure mechanism | Recorded labels | Correct matches | False alarms | Missed labels |
|---|---:|---:|---:|---:|
| Power failure | 95 | 95 | 0 | 0 |
| Heat-dissipation failure | 115 | 115 | 0 | 0 |
| Overstrain failure | 98 | 98 | 0 | 0 |

**Interpretation:** These are exact matches because the diagnostic calculations reproduce the mathematical rules used to generate those synthetic labels. This is a **rule-implementation consistency check**, **not 100% machine-learning accuracy** or evidence of successful real-world failure forecasting. Failure types can overlap in an observation.

### Example model behavior

Keeping **product type L**, **air temperature 300 K**, **process temperature 310 K**, **speed 1,500 RPM**, and **torque 40 Nm** constant:

| Tool wear | Model failure-class score | Classification at 50% threshold |
|---|---:|---|
| 100 minutes | **0.0%** | Normal |
| 230 minutes | **17.3%** | Normal |

Increasing tool wear changed the model's failure-class score. This illustrates its sensitivity to operating inputs; **17.3% does not mean a verified 17.3% probability of breaking down tomorrow**.

### Model and evaluation setup

- **Model:** `RandomForestClassifier` with 100 trees, balanced class weighting, and a minimum of two samples per leaf.
- **Inputs:** Six original operating features (the product category is one-hot encoded).
- **Target:** `Machine failure` (`0` / `1`).
- **Evaluation:** Stratified **80/20 train/test split**, with a fixed random seed in the notebook.
- **Threshold analysis:** Compares alert thresholds of **10%, 20%, and 50%** in terms of detected failures, false alarms, missed failures, precision, and recall.
- **Leakage control:** Failure-type labels (TWF, HDF, PWF, OSF, RNF) are **not used as model input features**.

The notebook computes the quantitative evaluation metrics; this README focuses on results that are available and verifiable from the saved project outputs.

## How the system works

```text
AI4I synthetic dataset
        |
        v
Databricks + PySpark (data cleaning and exploration)
        |
        v
Delta table + SQL analysis
        |
        v
Random Forest training and evaluation
        |
        v
Saved machine_model.joblib
        |
        v
Streamlit web app
        |-- Machine analysis
        |-- Engineering-rule diagnostics
        `-- Session history / CSV export
```

## Technologies

**Databricks · PySpark · SQL · Delta Lake · Python · pandas · scikit-learn · Streamlit · joblib**

## Run the application locally

Clone the repository and install its dependencies:

```bash
git clone https://github.com/Balotellli/smart-factory-.git
cd smart-factory-
pip install -r requirements.txt
streamlit run app.py
```

The app loads the included `machine_model.joblib`. The repository pins the scikit-learn version used to serialize that model. Only load serialized model files from sources you trust.

## Project limitations and next steps

- The dataset is **synthetic** and its rows are operating observations, **not histories of individually tracked factory machines**.
- The model classifies the **current observation**; it cannot estimate remaining useful life or reliably predict failure within a future time window.
- Model scores have **not been demonstrated to be calibrated future-failure probabilities**.
- The engineering thresholds replicate dataset simulation rules, not real-machine operating limits.
- The public app accepts **manual inputs**, rather than live sensor streams, and its session history is temporary.

Future development could introduce real sensor time series, timestamps and machine identifiers, maintenance/failure-event records, time-based validation, probability calibration, and persistent application logging.

## Dataset attribution

**AI4I 2020 Predictive Maintenance Dataset** (2020), *UCI Machine Learning Repository*. [DOI: 10.24432/C5HS5C](https://doi.org/10.24432/C5HS5C). Licensed under **CC BY 4.0**. The original dataset and its simulated failure rules are credited to the dataset authors and repository.

---

**Project focus:** Demonstrating the integration of industrial engineering concepts, data engineering, machine learning, and a usable web interface for interpretable machine-condition analysis.
