import logging
import sys
import duckdb
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from constants import DB_PATH, SQL_DIR, OUTPUT_DIR
from extract import extract
from transform import transform
from load import load

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

log = logging.getLogger(__name__)


def run_sql(con: duckdb.DuckDBPyConnection, filename: str) -> None:
    sql = (SQL_DIR / filename).read_text()
    con.execute(sql)
    log.info("Executed %s", filename)


def pipeline() -> None:
    log.info("=== STEP 1 — Extract ===")
    df = extract()

    log.info("=== STEP 2 — Transform ===")
    rfm = transform(df)

    log.info("=== STEP 3 — Load ===")
    load(rfm)

    log.info("=== STEP 4 — SQL Scoring ===")
    con = duckdb.connect(str(DB_PATH))
    run_sql(con, "02_rfm_scores.sql")
    run_sql(con, "03_segments.sql")

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / "rfm_segments.csv"
    segments = con.execute("SELECT * FROM rfm_segments").df()
    segments.to_csv(out_path, index=False)
    con.close()

    log.info("Output saved to %s", out_path)
    log.info("Total customers: %s", f"{len(segments):,}")

    dist = (
        segments.groupby("segment")
        .size()
        .reset_index(name="customers")
        .assign(pct=lambda x: (x["customers"] / len(segments) * 100).round(1))
        .sort_values("customers", ascending=False)
    )
    log.info("Segment distribution:\n%s", dist.to_string(index=False))


if __name__ == "__main__":
    pipeline()
