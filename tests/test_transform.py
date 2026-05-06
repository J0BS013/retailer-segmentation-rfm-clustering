import pandas as pd
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transform import transform


@pytest.fixture
def raw_df():
    return pd.DataFrame(
        {
            "Invoice": ["INV001", "INV001", "INV002", "INV003", "INV004"],
            "StockCode": ["A", "B", "A", "C", "D"],
            "Quantity": [2, 3, 1, 5, 2],
            "Price": [10.0, 5.0, 20.0, 8.0, 15.0],
            "InvoiceDate": pd.to_datetime(
                ["2011-12-01", "2011-12-01", "2011-12-05", "2011-12-09", "2011-12-09"]
            ),
            "Customer ID": ["C001", "C001", "C001", "C002", None],
            "Country": ["UK", "UK", "UK", "UK", "UK"],
        }
    )


def test_output_columns(raw_df):
    rfm = transform(raw_df)
    assert set(rfm.columns) == {"Customer ID", "frequency", "monetary", "recency"}


def test_null_customer_id_dropped(raw_df):
    rfm = transform(raw_df)
    assert rfm["Customer ID"].notna().all()
    assert len(rfm) == 2


def test_recency_is_non_negative(raw_df):
    rfm = transform(raw_df)
    assert (rfm["recency"] >= 0).all()


def test_frequency_counts_unique_invoices(raw_df):
    rfm = transform(raw_df)
    c001 = rfm[rfm["Customer ID"] == "C001"].iloc[0]
    # C001 has INV001 and INV002 — 2 distinct invoices
    assert c001["frequency"] == 2


def test_monetary_is_sum_of_total_price(raw_df):
    rfm = transform(raw_df)
    c001 = rfm[rfm["Customer ID"] == "C001"].iloc[0]
    # INV001: 2*10 + 3*5 = 35, INV002: 1*20 = 20 → total 55
    assert c001["monetary"] == pytest.approx(55.0)


def test_recency_uses_max_date_as_snapshot(raw_df):
    rfm = transform(raw_df)
    c001 = rfm[rfm["Customer ID"] == "C001"].iloc[0]
    # snapshot = 2011-12-09, last purchase C001 = 2011-12-05 → 4 days
    assert c001["recency"] == 4
