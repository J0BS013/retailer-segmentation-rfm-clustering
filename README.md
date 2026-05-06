# Retailer Segmentation — RFM + K-Means Clustering

Customer segmentation pipeline built on the UCI Online Retail II dataset (~1M transactions). Combines rule-based RFM scoring with K-Means clustering to identify behavioral segments and translate them into actionable business strategies.

---

## What is RFM?

RFM is a behavioral scoring framework used in marketing and CRM to rank customers based on their purchase history. It answers three questions:

- **Recency** — how recently did the customer buy? A customer who bought last week is more likely to buy again than one who bought two years ago.
- **Frequency** — how often do they buy? Repeat buyers have a demonstrated relationship with the brand.
- **Monetary** — how much do they spend? High spenders drive disproportionate revenue.

Each dimension is scored 1–5 using **quintile-based binning** — the top 20% of customers on a given dimension always score 5, regardless of absolute values. This makes the scoring robust to outliers and distribution shifts over time.

The combined R+F+M score determines which segment a customer belongs to. A customer with R=5, F=5, M=5 is a Champion; R=1, F=1, M=1 is Lost.

This approach is validated against K-Means clustering: if the unsupervised clusters align with the quintile-based labels, the scoring logic is sound.

---

## Key Findings

Analysis over 5,878 identified customers from 1,041,670 transactions (Dec 2009 – Dec 2011).

| Segment | Customers | % Customers | % Revenue | Avg. Spend | Avg. Recency | Avg. Orders |
|---|---|---|---|---|---|---|
| Champions | 1,345 | 22.9% | **68.8%** | £9,080 | 19 days | 16.6 |
| Loyal Customers | 1,473 | 25.1% | 16.3% | £1,960 | 65 days | 5.2 |
| At Risk | 708 | 12.0% | 8.8% | £2,209 | 360 days | 5.4 |
| Lost | 2,064 | 35.1% | 5.4% | £468 | 384 days | 1.3 |
| New Customers | 288 | 4.9% | 0.6% | £397 | 32 days | 1.2 |

**Champions (22.9% of customers) account for 68.8% of total revenue** — a classic power-law distribution that justifies differentiated treatment per segment.

Three additional findings worth noting:

- **At Risk customers spent more on average (£2,209) than Loyal Customers (£1,960)** but haven't purchased in ~360 days. They are the highest-value re-engagement target in the base.
- **Lost customers average only 1.3 orders** — most were one-time buyers who never returned, not disengaged regulars. Win-back investment is only justified for the higher-M subset.
- **Champions average 19 days since last purchase and 16.6 orders** — they are actively engaged and spending at a level 4.6× above the Loyal tier.

---

## Pipeline

```
┌─────────────────────────────────────────────────────┐
│  UCI Online Retail II (.xlsx, ~1M rows, 2 sheets)   │
└───────────────────────┬─────────────────────────────┘
                        │
                 extract.py
            • Concatenates both yearly sheets
            • Drops returns, adjustments, zero-price rows
            • Validates schema with Pandera
            • Saves to Parquet
                        │
                 transform.py
            • Removes rows without Customer ID
            • Calculates TotalPrice = Quantity × Price
            • Aggregates per customer:
                recency   → days since last purchase
                frequency → distinct invoice count
                monetary  → sum of TotalPrice
                        │
                   load.py
            • Loads Parquet into DuckDB
                        │
              sql/02_rfm_scores.sql
            • NTILE(5) window functions
              score R, F, M from 1 to 5
                        │
              sql/03_segments.sql
            • Maps score combinations to segment labels
                        │
            outputs/rfm_segments.csv + notebooks/
```

Orchestrated by `src/run_pipeline.py`, containerized with Docker.

---

## RFM Scoring — core SQL

```sql
SELECT
    "Customer ID",
    NTILE(5) OVER (ORDER BY recency DESC)  AS r_score,
    NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
    NTILE(5) OVER (ORDER BY monetary ASC)  AS m_score
FROM rfm_features
```

Score 5 is always best. Each dimension is sorted so that the worst values come first (NTILE=1) and the best come last (NTILE=5). Recency uses `DESC` because a customer inactive for 700 days should score 1, not 5.

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

K-Means applied to the normalized RFM feature space to validate the rule-based segments.

- Optimal K selected via Elbow method → **K = 5**
- Silhouette Score at K=5: **0.61** — K=5 is a local peak in the 3–10 range, confirming good cluster separation at this granularity
- Cluster profiles align strongly with the quintile-based segment labels

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

## How to Run

```bash
git clone https://github.com/J0BS013/retailer-segmentation-rfm-clustering.git
cd retailer-segmentation-rfm-clustering

# Download the dataset:
# https://archive.ics.uci.edu/dataset/502/online+retail+ii
# Place the .xlsx file in data/raw/

pip install -r requirements.txt
python src/run_pipeline.py

# For notebooks:
jupyter lab
```

**With Docker:**
```bash
docker compose up pipeline
docker compose up notebook  # → http://localhost:8888
```

---

## Dataset

UCI Online Retail II — ~500k transactions from a UK-based online retailer between December 2009 and December 2011, primarily wholesale customers.

Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

---

Joabe Santos · [LinkedIn](https://www.linkedin.com/in/joabe-santos) · [GitHub](https://github.com/J0BS013)
