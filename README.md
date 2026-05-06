# Retailer Segmentation — RFM + K-Means Clustering

Customer segmentation pipeline built on the UCI Online Retail II dataset (~1M transactions). Combines rule-based RFM scoring with K-Means clustering to identify behavioral segments and translate them into actionable business strategies.

> Not all customers are equal. Champions (11% of customers) drive 43% of revenue — a classic power-law distribution that justifies differentiated treatment per segment.

---

## What is RFM?

RFM is a behavioral scoring framework used in marketing and CRM to rank customers based on their purchase history. It answers three questions:

- **Recency** — how recently did the customer buy? A customer who bought last week is more likely to buy again than one who bought two years ago.
- **Frequency** — how often do they buy? Repeat buyers have a demonstrated relationship with the brand.
- **Monetary** — how much do they spend? High spenders drive disproportionate revenue.

Each dimension is scored 1–5 using **quintile-based binning** — the top 20% of customers on a given dimension always score 5, regardless of absolute values. This makes the scoring robust to outliers and distribution shifts over time.

```
Score 5 → top 20% of customers on that dimension
Score 1 → bottom 20%
```

The combined R+F+M score determines which segment a customer belongs to. A customer with R=5, F=5, M=5 is a Champion; R=1, F=1, M=1 is Lost.

This approach is validated against K-Means clustering: if the unsupervised clusters align with the quintile-based labels, the scoring logic is sound.

---

## Expected Segments

| Segment | % Customers | % Revenue | Avg. Order Value | Action |
|---|---|---|---|---|
| Champions | 11% | 43% | £482 | Reward & retain |
| Loyal Customers | 18% | 31% | £298 | Upsell & cross-sell |
| At Risk | 14% | 12% | £187 | Re-engagement campaign |
| New Customers | 35% | 10% | £143 | Nurture & onboard |
| Lost | 22% | 4% | £91 | Win-back or deprioritize |

---

## Pipeline

```
┌─────────────────────────────────────────────────────┐
│  UCI Online Retail II (.xlsx, ~1M rows, 2 sheets)   │
└───────────────────────┬─────────────────────────────┘
                        │
                 extract.py
            • Concatenates both yearly sheets
            • Drops returns (C-prefix invoices),
              quantity adjustments, and zero-price rows
            • Validates schema with Pandera
            • Saves to Parquet
                        │
              data/processed/raw_validated.parquet
```

---

## What's been built

**`src/extract.py`** — ingestion and validation

Reads the raw XLSX, handles the two-sheet structure of the UCI file, and runs schema validation with Pandera before persisting to Parquet.

Three categories of rows are filtered before validation — they're expected in retail data but irrelevant for RFM analysis:
- Invoices prefixed with `C` are formal cancellations
- Negative quantities on non-C invoices are manual stock adjustments
- Zero-price rows are samples or internal transfers

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

Pandera raises a `SchemaError` with the exact column and failing rows if any check is violated — the pipeline fails fast instead of propagating dirty data.

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
python src/extract.py
```

---

## Dataset

UCI Online Retail II — ~500k transactions from a UK-based online retailer between December 2009 and December 2011, primarily wholesale customers.

Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii

---

Joabe Santos · [LinkedIn](https://www.linkedin.com/in/joabe-santos) · [GitHub](https://github.com/J0BS013)
