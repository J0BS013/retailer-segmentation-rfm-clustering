import logging
import duckdb
import pandas as pd

from constants import PROCESSED_DIR, DB_PATH

log = logging.getLogger(__name__)


def load(rfm: pd.DataFrame) -> None:
    log.info("Connecting to %s", DB_PATH)

    con = duckdb.connect(str(DB_PATH))
    con.execute("DROP TABLE IF EXISTS rfm_features")
    con.execute("CREATE TABLE rfm_features AS SELECT * FROM rfm")

    count = con.execute("SELECT COUNT(*) FROM rfm_features").fetchone()[0]
    log.info("rfm_features table: %s rows", f"{count:,}")

    con.close()
    log.info("Database saved to %s", DB_PATH)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    rfm = pd.read_parquet(PROCESSED_DIR / "rfm_features.parquet")
    load(rfm)
