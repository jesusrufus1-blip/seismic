"""Run the whole pipeline in one go:  python run_pipeline.py

fetch (USGS API)  ->  clean (Pandas + Regex)  ->  load (MySQL)

Options:
    python run_pipeline.py --skip-fetch     reuse data/raw/earthquakes_raw.csv
"""
import sys

import pandas as pd

from src import config
from src.clean_data import clean, report
from src.fetch_data import fetch_all
from src.load_to_mysql import load


def main():
    raw_path = config.RAW_DIR / "earthquakes_raw.csv"
    if "--skip-fetch" in sys.argv and raw_path.exists():
        print(f"[1/3] Skipping download, using {raw_path}")
        raw = pd.read_csv(raw_path, low_memory=False)
    else:
        print("[1/3] Downloading from USGS (this takes a while the first time) ...")
        raw = fetch_all()
        raw.to_csv(raw_path, index=False)

    print("\n[2/3] Cleaning ...")
    cleaned = clean(raw)
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(config.CLEAN_CSV, index=False)
    report(cleaned)

    print("\n[3/3] Loading into MySQL ...")
    rows = load(cleaned)
    print(f"Done. {rows} rows are now in MySQL table {config.DB_NAME}.earthquakes")
    print("Next:  streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    main()
