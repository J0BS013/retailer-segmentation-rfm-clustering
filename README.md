# Retailer Segmentation — RFM + Clustering

Customer segmentation using RFM (Recency, Frequency, Monetary) analysis combined with K-Means clustering. Built on a structured ETL pipeline with schema validation, columnar storage, and SQL-based scoring.

The goal is to identify which customer segments drive revenue, which are at risk of churning, and which have growth potential — enabling targeted retention, re-engagement, and upsell strategies.

## Architecture

```
UCI Raw Data (XLSX)
    → extract.py       reads both sheets, validates schema with Pandera, saves Parquet
    → transform.py     cleans nulls, engineers RFM features per customer
    → load.py          persists processed data into DuckDB
    → sql/             calculates R/F/M scores via NTILE window functions
    → notebooks/       K-Means clustering, Elbow method, segment profiling
    → outputs/rfm_segments.csv
```

Pipeline is orchestrated by `src/run_pipeline.py` and runs inside Docker.

## Current status

- [x] Project structure and environment
- [x] `extract.py` — reads XLSX, validates with Pandera, saves to Parquet
- [ ] `transform.py` — RFM feature engineering
- [ ] `load.py` — DuckDB persistence
- [ ] SQL scoring
- [ ] Notebooks
- [ ] CI (GitHub Actions)

## Stack

| Layer | Tool |
|---|---|
| Data processing | pandas |
| Schema validation | Pandera |
| Intermediate storage | Parquet (pyarrow) |
| Analytical storage | DuckDB |
| Machine learning | scikit-learn |
| Visualization | matplotlib, seaborn |
| Containerization | Docker + Compose |
| CI | GitHub Actions |

## RFM methodology

Each customer is scored 1–5 on three dimensions using quintile-based binning:

- **Recency** — days since last purchase
- **Frequency** — number of distinct orders
- **Monetary** — total spend

The combined score drives segment assignment, validated against K-Means clusters.

## How to run

**With Docker:**
```bash
git clone https://github.com/J0BS013/retailer-segmentation-rfm-clustering.git
cd retailer-segmentation-rfm-clustering

# Download dataset from https://archive.ics.uci.edu/dataset/502/online+retail+ii
# Place the .xlsx file in data/raw/

docker compose up pipeline
docker compose up notebook  # → http://localhost:8888
```

**Locally:**
```bash
pip install -r requirements.txt
make run
```

## Dataset

UCI Online Retail II — ~500k transactions from a UK-based online retailer (Dec 2009 – Dec 2011).  
Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

## Author

Joabe Santos — Senior Data Analyst & Analytics Engineer  
[LinkedIn](https://www.linkedin.com/in/joabe-santos) · [GitHub](https://github.com/J0BS013)
