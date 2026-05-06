import logging
import pandas as pd

from constants import PROCESSED_DIR

log = logging.getLogger(__name__)


def transform(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Input shape: %s", df.shape)

    # Rows without Customer ID cannot be attributed to anyone
    df = df.dropna(subset=["Customer ID"]).copy()
    log.info("After dropping null Customer ID: %s rows", f"{len(df):,}")

    df["TotalPrice"] = df["Quantity"] * df["Price"]

    # Use the dataset's max date as a fixed reference point so Recency
    # is reproducible regardless of when the pipeline runs
    snapshot_date = df["InvoiceDate"].max()
    log.info("Snapshot date: %s", snapshot_date.date())

    rfm = (
        df.groupby("Customer ID")
        .agg(
            last_purchase=("InvoiceDate", "max"),
            frequency=("Invoice", "nunique"),
            monetary=("TotalPrice", "sum"),
        )
        .reset_index()
    )

    rfm["recency"] = (snapshot_date - rfm["last_purchase"]).dt.days
    rfm = rfm.drop(columns=["last_purchase"])

    log.info("RFM table: %s customers", f"{len(rfm):,}")
    log.info("RFM stats:\n%s", rfm.describe().round(2).to_string())

    out_path = PROCESSED_DIR / "rfm_features.parquet"
    rfm.to_parquet(out_path, index=False)
    log.info("Saved to %s", out_path)

    return rfm


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    df = pd.read_parquet(PROCESSED_DIR / "raw_validated.parquet")
    transform(df)
