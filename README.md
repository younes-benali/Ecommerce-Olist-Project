# Olist Delivery Prediction — End-to-End ML Pipeline

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ecommerce-olist-project.streamlit.app)
[![XGBoost](https://img.shields.io/badge/XGBoost-1.7.6-orange)](https://xgboost.ai)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> Predict late deliveries on the Olist Brazilian e-commerce platform — from exploratory notebooks to a reproducible ML pipeline and an interactive Streamlit dashboard.

**[→ Launch Live Dashboard](https://ecommerce-olist-project.streamlit.app)**

<img src="https://raw.githubusercontent.com/younes-benali/Ecommerce-Olist-Project/main/app/app-image.png" alt="Dashboard Preview" width="100%">

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Approach & Pipeline](#approach--pipeline)
- [Project Structure](#project-structure)
- [Model Performance](#model-performance)
- [Live Dashboard](#live-dashboard)
- [How to Run Locally](#how-to-run-locally)
- [Technologies Used](#technologies-used)
- [Author](#author)

---

## Problem Statement

Olist connects Brazilian sellers to customers across multiple marketplaces. **Late deliveries** erode customer trust and drive up support costs — yet they can often be anticipated from order data alone.

This project trains a **binary classifier** to predict whether an order will arrive **late** (`is_late = 1`) or **on time** (`is_late = 0`), using historical data on orders, products, customers, and payments.

**Why it matters:**
- Proactively alert customers before a delay happens.
- Identify high-risk orders so logistics teams can intervene early.
- Give sellers a clear signal for improving fulfilment performance.

---

## Approach & Pipeline

The project is structured as a **production-ready ML pipeline**, not just a collection of notebooks.

### 1 — Experimentation (Notebooks)

| Notebook | Purpose |
|----------|---------|
| [`01_eda.ipynb`](notebooks/01_eda.ipynb) | Exploratory analysis, RFM segmentation, sales trends |
| [`02_data_cleaning.ipynb`](notebooks/02_data_cleaning.ipynb) | Initial cleaning logic (later refactored into `src/`) |
| [`03_feature_engineering.ipynb`](notebooks/03_feature_engineering.ipynb) | Feature creation experiments |
| [`04_models_experiment.ipynb`](notebooks/04_models_experiment%20.ipynb) | XGBoost vs. Random Forest — XGBoost won (72 % recall vs. 68 %) |

### 2 — Production Pipeline (`src/`)

All notebook logic was refactored into reusable, testable Python modules:

| Module | Responsibility |
|--------|---------------|
| [`config.py`](src/config.py) | Centralised paths via `pathlib` — no hardcoded absolute paths |
| [`data_loader.py`](src/data_loader.py) | Load raw CSVs from `olist_db/` |
| [`preprocessing.py`](src/preprocessing.py) | Clean order data (invalid dates, status fixes, null removal) |
| [`features.py`](src/features.py) | Engineer features (time-based, product aggregates, one-hot encoding) |
| [`model.py`](src/model.py) | Train XGBoost with hyperparameter tuning and imbalance handling |
| [`evaluate.py`](src/evaluate.py) | Generate metrics JSON and diagnostic plots |
| [`pipeline/run_pipeline.py`](src/pipeline/run_pipeline.py) | **Single entry point** — orchestrates every step end-to-end |
### 3 — SQL Analytics Layer (`sql/`)

PostgreSQL schema and reusable business views (`order_summary`, `customer_summary`, `product_summary`, `sales_summary`) power the EDA and BI layer. The deployed dashboard uses pre-exported CSVs, so the database is optional for local exploration.

### 4 — Interactive Dashboard (`app/`)

Built with **Streamlit**, the dashboard has three sections:

- **Business Performance** — global KPIs, sales trends, top cities, RFM customer segmentation.
- **Delivery Analysis** — late rate by month, category, and state; filterable by sidebar controls.
- **Model Performance** — confusion matrix, ROC curve, recall, precision, and false-alarm rate.

---

## Project Structure

```
Ecommerce-Olist-Project/
├── app/
│   └── streamlit_app.py          # Streamlit dashboard
├── data/
│   ├── processed/                # Feature-engineered and summary CSVs
│      ├── feature_engineered_data.csv
│      ├── order_summary_clean.csv
│      ├── sales_summary.csv
│      ├── top_cities.csv
│      └── rfm_raw.csv
│                     
├── models/
│   └── model.pkl                 # Trained XGBoost model
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_feature_engineering.ipynb
│   └── 04_models_experiment.ipynb
├── olist_db/                     # Raw CSV files (git-ignored)
├── reports/
│   ├── figures/                  # Plots from evaluate.py
│   └── metrics/                  # metrics.json
├── scripts/
│   └── save_business_data.py     # Export SQL views to CSV
├── sql/
│   ├── schema.sql
│   └── views/
├── src/
│   ├── pipeline/
│   │   └── run_pipeline.py       # Orchestration entry point
│   ├── config.py
│   ├── data_loader.py
│   ├── preprocessing.py
│   ├── features.py
│   ├── model.py
│   └── evaluate.py
└── requirements.txt
```

---

## Model Performance

**XGBoost** — 100 estimators, `max_depth=3`, `learning_rate=0.05`, `scale_pos_weight` tuned for class imbalance.

| Metric | Value |
|--------|-------|
| Recall — late deliveries caught | **72.0 %** |
| Precision — late predictions correct | 67.3 % |
| False-alarm rate — on-time flagged as late | 25.4 % |
| Overall accuracy | 73.8 % |
| ROC AUC | 0.81 |

**Confusion matrix (test set):**

|  | Predicted On Time | Predicted Late |
|--|:-:|:-:|
| **Actual On Time** | 74.6 % | 25.4 % |
| **Actual Late** | 28.0 % | **72.0 %** |

**Business interpretation:**
- ✅ 7 out of 10 real delays are caught — enough to proactively warn most affected customers.
- ⚠️ 1 in 4 warnings is a false alarm — an acceptable trade-off given the cost of a missed delay.


---

## Live Dashboard

Deployed on **Streamlit Cloud** — no setup required:

**[→ Launch Live Dashboard](https://ecommerce-olist-project.streamlit.app)**

Features at a glance:
- Global KPIs: total orders, late rate, average items per order, average freight cost.
- Sales trends: revenue, order volume, average payment value, items sold over time.
- Top 10 cities by customer count.
- RFM segmentation: pie chart breakdown and average spend per segment.
- Delivery analysis: late rate by month, product category, and state.
- Model diagnostics: confusion matrix, ROC curve, and key metrics.
- Sidebar filters (category, state, month) scoped to the delivery and model sections.

---

## How to Run Locally

**1. Clone the repository**

```bash
git clone https://github.com/younes-benali/Ecommerce-Olist-Project.git
cd Ecommerce-Olist-Project
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Add the raw data**

Download the [Olist dataset from Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and place the CSV files in `olist_db/`.

**4. Run the full pipeline**

```bash
python src/pipeline/run_pipeline.py
```

This will preprocess the data, engineer features, train the model, and save outputs to `data/processed/`, `models/`, and `reports/`.

**5. Launch the dashboard**

```bash
streamlit run app/streamlit_app.py
```

---

## Technologies Used

| Area | Tools |
|------|-------|
| Data processing | Pandas, NumPy, SQLAlchemy |
| Machine learning | Scikit-learn, XGBoost, Joblib |
| Visualisation | Plotly, Matplotlib, Seaborn |
| Dashboard | Streamlit |
| Database | PostgreSQL (optional — for analytics only) |
| Testing | Pytest |
| Version control | Git, GitHub |

---

## Author

**Younes Benali**
[GitHub](https://github.com/younes-benali) · [LinkedIn](https://www.linkedin.com/in/younes-benali-/)

---

## Acknowledgements

- [Olist Brazilian E-commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) on Kaggle.
- [Streamlit](https://streamlit.io) for making dashboard development incredibly fast.
- The [XGBoost](https://xgboost.ai) team for an outstanding gradient boosting library.
