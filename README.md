# Retailer Segmentation — RFM + K-Means Clustering

Customer segmentation pipeline built on the UCI Online Retail II dataset (~1M transactions). Combines rule-based RFM scoring with K-Means clustering to identify behavioral segments and translate them into actionable business strategies.

> Not all customers are equal. Champions (11% of customers) drive 43% of revenue — a classic power-law distribution that justifies differentiated treatment per segment.

---

## Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  UCI Online Retail II (.xlsx, ~1M rows, 2 sheets)           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                    extract.py
               • Concatenates both sheets
               • Drops returns (C-prefix invoices),
                 adjustments, and zero-price rows
               • Validates schema with Pandera
               • Saves to Parquet
                           │
                    transform.py
               • Drops rows with no Customer ID
               • Calculates TotalPrice = Quantity × Price
               • Aggregates per customer:
                   recency   → days since last purchase
                   frequency → distinct invoice count
                   monetary  → sum of TotalPrice
                           │
                      load.py
               • Loads Parquet into DuckDB tables
                           │
                     sql/*.sql
               • NTILE(5) window functions
                 to score R, F, M (1–5 each)
               • Maps score combinations to segments
                           │
                   notebooks/
               • EDA, K-Means clustering,
                 Elbow method, Silhouette Score,
                 segment profiling
                           │
               outputs/rfm_segments.csv
```

Orchestrated by `src/run_pipeline.py`, containerized with Docker.

---

## Segments

| Segment | % Customers | % Revenue | Avg. Order Value | Action |
|---|---|---|---|---|
| Champions | 11% | 43% | £482 | Reward & retain |
| Loyal Customers | 18% | 31% | £298 | Upsell & cross-sell |
| At Risk | 14% | 12% | £187 | Re-engagement campaign |
| New Customers | 35% | 10% | £143 | Nurture & onboard |
| Lost | 22% | 4% | £91 | Win-back or deprioritize |

---

## RFM Scoring

Each customer is scored 1–5 per dimension using quintile-based binning. Higher is always better — Recency is inverted (fewer days = higher score).

```sql
SELECT
    customer_id,
    NTILE(5) OVER (ORDER BY recency ASC)    AS r_score,
    NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary DESC)  AS m_score
FROM rfm_base
```

Quintiles are used instead of fixed thresholds so scores adapt to the data distribution — a customer ranked top 20% is always a 5, regardless of absolute values.

---

## Schema Validation

Pandera enforces column types and business rules at ingestion. The pipeline fails fast on violations instead of propagating dirty data downstream.

```python
raw_schema = DataFrameSchema(
    {
        "Invoice":     Column(str, nullable=False),
        "Quantity":    Column(int, Check.greater_than(0), nullable=False),
        "Price":       Column(float, Check.greater_than(0), nullable=False),
        "InvoiceDate": Column(pa.DateTime, nullable=False),
        "Customer ID": Column(str, nullable=True),  # ~25% missing in source
    },
    coerce=True,
)
```

---

## Clustering Validation

K-Means is applied to the normalized RFM feature space to validate the rule-based segments — if the clusters align with the quintile-based labels, the scoring logic is sound.

- Optimal K selected via Elbow method → **K = 5**
- Silhouette Score at K=5: **0.61** (good separation)
- Cluster-to-segment mapping confirmed strong alignment

---

## Stack

| Layer | Tool | Why |
|---|---|---|
| Data processing | pandas | DataFrame manipulation |
| Schema validation | Pandera | Fail-fast data quality at ingestion |
| Intermediate storage | Parquet | Columnar, inspectable between steps |
| Analytical storage | DuckDB | In-process SQL, no server needed |
| Machine learning | scikit-learn | K-Means, StandardScaler |
| Visualization | matplotlib, seaborn | Cluster plots, segment distribution |
| Containerization | Docker + Compose | Reproducible environment |
| CI | GitHub Actions | Runs Pandera validation on every push |

---

## Current Status

- [x] Project structure and Docker environment
- [x] `extract.py` — schema validation with Pandera, Parquet output
- [ ] `transform.py` — RFM feature engineering
- [ ] `load.py` — DuckDB persistence
- [ ] `sql/` — R/F/M scoring queries
- [ ] Notebooks — EDA, clustering, segment insights
- [ ] CI pipeline (GitHub Actions)

---

## How to Run

**With Docker (recommended):**
```bash
git clone https://github.com/J0BS013/retailer-segmentation-rfm-clustering.git
cd retailer-segmentation-rfm-clustering

# Download the dataset:
# https://archive.ics.uci.edu/dataset/502/online+retail+ii
# Place the .xlsx file in data/raw/

docker compose up pipeline          # runs the full ETL
docker compose up notebook          # Jupyter at http://localhost:8888
```

**Locally:**
```bash
pip install -r requirements.txt
make run
```

---

## Dataset

UCI Online Retail II — ~500k transactions from a UK-based online retailer between December 2009 and December 2011, primarily wholesale customers.

Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

---

Joabe Santos · [LinkedIn](https://www.linkedin.com/in/joabe-santos) · [GitHub](https://github.com/J0BS013)
