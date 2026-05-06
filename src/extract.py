import os
import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, Check, DataFrameSchema
from pathlib import Path

os.environ["DISABLE_PANDERA_IMPORT_WARNING"] = "True"

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

# UCI dataset has ~25% missing Customer ID — nullable by design
raw_schema = DataFrameSchema(
    {
        "Invoice": Column(str, nullable=False),
        "StockCode": Column(str, nullable=False),
        "Description": Column(str, nullable=True),
        "Quantity": Column(int, Check.greater_than(0), nullable=False),
        "InvoiceDate": Column(pa.DateTime, nullable=False),
        "Price": Column(float, Check.greater_than(0), nullable=False),
        "Customer ID": Column(str, nullable=True),
        "Country": Column(str, nullable=True),
    },
    coerce=True,
)


def extract(xlsx_filename: str = "online_retail_II.xlsx") -> pd.DataFrame:
    xlsx_path = RAW_DIR / xlsx_filename
    print(f"[extract] Reading {xlsx_path} ...")

    # UCI file ships with two sheets (2009-2010 and 2010-2011)
    sheets = pd.read_excel(xlsx_path, sheet_name=None, dtype={"Customer ID": str})
    df = pd.concat(sheets.values(), ignore_index=True)

    print(f"[extract] Raw shape: {df.shape}")

    # Drop returns (C-prefix), manual adjustments, and zero-price entries
    # before validation so Pandera only sees completed positive transactions
    df = df[~df["Invoice"].astype(str).str.startswith("C")].copy()
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    print("[extract] Validating schema ...")
    df = raw_schema.validate(df, lazy=True)
    print(f"[extract] Valid. Rows after filtering: {len(df):,}")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "raw_validated.parquet"
    df.to_parquet(out_path, index=False)
    print(f"[extract] Saved to {out_path}")

    return df


if __name__ == "__main__":
    extract()
