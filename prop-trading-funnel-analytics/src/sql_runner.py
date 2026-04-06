from __future__ import annotations

import duckdb
import pandas as pd

from src.config import DATA_DIR, DB_PATH, OUTPUT_DIR, SQL_DIR


TABLE_FILES = {
    "users": DATA_DIR / "users.csv",
    "kyc_events": DATA_DIR / "kyc_events.csv",
    "challenges": DATA_DIR / "challenges.csv",
    "challenge_progress": DATA_DIR / "challenge_progress.csv",
    "payouts": DATA_DIR / "payouts.csv",
    "trader_behavior": DATA_DIR / "trader_behavior.csv",
}

QUERY_OUTPUTS = {
    "01_overall_funnel.sql": "overall_funnel.csv",
    "02_funnel_by_acquisition_channel.sql": "funnel_by_acquisition_channel.csv",
    "03_funnel_by_challenge_type.sql": "funnel_by_challenge_type.csv",
    "04_funded_payout_analysis.sql": "funded_payout_analysis.csv",
    "05_cohort_analysis_by_registration_month.sql": "cohort_analysis_by_registration_month.csv",
    "06_trader_segment_comparison.sql": "trader_segment_comparison.csv",
    "07_stage_timing.sql": "stage_timing.csv",
}


def build_warehouse() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(DB_PATH.as_posix())
    try:
        for table_name, file_path in TABLE_FILES.items():
            connection.execute(
                f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT *
                FROM read_csv_auto('{file_path.as_posix()}', HEADER = TRUE);
                """
            )
    finally:
        connection.close()


def run_sql_queries() -> dict[str, pd.DataFrame]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, pd.DataFrame] = {}
    connection = duckdb.connect(DB_PATH.as_posix(), read_only=False)
    try:
        for sql_file, output_name in QUERY_OUTPUTS.items():
            query = (SQL_DIR / sql_file).read_text()
            frame = connection.execute(query).df()
            frame.to_csv(OUTPUT_DIR / output_name, index=False)
            results[output_name] = frame
    finally:
        connection.close()

    return results


def main() -> None:
    build_warehouse()
    run_sql_queries()


if __name__ == "__main__":
    main()
