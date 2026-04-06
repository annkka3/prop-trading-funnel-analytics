from src.analysis import create_analysis_outputs
from src.data_generation import generate_case_data, save_case_data
from src.sql_runner import build_warehouse, run_sql_queries


def main() -> None:
    data_frames = generate_case_data()
    save_case_data(data_frames)
    build_warehouse()
    run_sql_queries()
    create_analysis_outputs()


if __name__ == "__main__":
    main()
