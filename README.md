# Global Seismic Trends: Data-Driven Earthquake Insights

Python + Regex + SQL (MySQL) + Streamlit project.
**Flow:** USGS API → Pandas/Regex cleaning → MySQL → 30 SQL queries → Streamlit dashboard → documentation.

## 1. One-time setup (Windows, VS Code terminal)

1. Install **Python 3.10+**, **VS Code** and **MySQL Server 8.0+** (remember the root password).
2. Open this folder in VS Code (File -> Open Folder), then open a terminal (Terminal -> New Terminal):
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   `(.venv)` must appear at the start of the terminal line.
3. Run the health check. It repairs file problems, creates the `.env` file (asks for your MySQL password) and tests MySQL:
   ```
   python check_project.py
   ```

## 2. Run the project

```
python run_pipeline.py              # download (first time ~15 min) -> clean -> load MySQL
python check_project.py             # must end with ">>> ALL GOOD"
streamlit run app/streamlit_app.py  # opens the dashboard in your browser (localhost:8501)
python -m src.generate_findings     # writes docs/findings.md with your real results
```
If `run_pipeline.py` stops, run it again - finished months are saved and skipped.
Run the steps one by one if you prefer (good for the live evaluation):
```
python -m src.fetch_data      # data/raw/earthquakes_raw.csv  (each month is cached in data/raw/)
python -m src.clean_data      # data/processed/earthquakes_clean.csv
python -m src.load_to_mysql   # creates DB `seismic`, table `earthquakes`, inserts the rows
```
Then open `notebooks/eda.ipynb` for the Python exploratory analysis, and `sql/queries.sql` in MySQL Workbench to run the queries by hand.

## 3. Folder structure

```
data/raw        monthly API files + earthquakes_raw.csv      (created by fetch_data)
data/processed  earthquakes_clean.csv                        (created by clean_data)
data/external   optional impact_data.csv (casualties, loss)
check_project.py  health check + automatic repair
src/            config, fetch_data, clean_data, geo_utils, db, load_to_mysql, queries, generate_findings
sql/            create_table.sql, queries.sql (all 30 questions)
app/            streamlit_app.py
notebooks/      eda.ipynb
docs/           features.md, findings.md
tests/          automatic checks (see below)
```

## 4. Things you must know (important for the evaluation)

* **Casualties / economic loss (Q11-Q13):** USGS does not publish them. The queries are written for the columns
  `casualties` and `economic_loss_usd`. Without data the dashboard shows a clearly labelled **proxy** based on the USGS
  `sig` score. If your mentor gives you a data source, save it as `data/external/impact_data.csv` with the columns
  `id,casualties,economic_loss_usd` and run `python run_pipeline.py --skip-fetch`.
* **26 features:** 5 of them (magError, depthError, magNst, locationSource, magSource) exist only in the USGS **CSV**
  feed, so the fetch script downloads both feeds and merges them on `id`.
* **Continent** is not in the data - it comes from the lookup table in `src/geo_utils.py`.
* **"Region"** in Q24 and Q30 means country (or ocean region name).
* **Thresholds** (shallow/deep, strong magnitude, minimum magnitude downloaded) are in `src/config.py`.
* The first and last calendar year are partial, so year-over-year growth (Q23) shows `months_covered`.

## 5. Tests (no MySQL needed)

```bash
python tests/test_clean.py        # regex + cleaning checks
python tests/make_sample_data.py  # SYNTHETIC fake data, only for testing - then run python -m src.clean_data
python tests/test_sql_logic.py    # runs all queries on SQLite and compares answers with pandas
```
⚠️ `make_sample_data.py` overwrites `data/raw/earthquakes_raw.csv` with fake data. Do not use it for your final project;
run `python run_pipeline.py` again afterwards to get the real data.

## 6. Troubleshooting

| Problem | Fix |
|---|---|
| `Access denied for user` | wrong password in `.env` - delete `.env`, run `python check_project.py` and type the right one |
| `IndentationError: unexpected indent` | run `python check_project.py` - it repairs the file automatically |
| `Data too long for column` | use the `sql/create_table.sql` from this version (long text columns are TEXT) |
| `cryptography package is required` | `pip install cryptography` |
| `Can't connect to MySQL server` | start the MySQL service (Windows: Services → MySQL80) |
| Download stops / fails for a month | run it again - finished months are cached and skipped |
| Q16 error | MySQL older than 8.0.4 - the dashboard falls back to a simpler grouping |
| Dashboard shows "Cannot read the MySQL table" | run `python run_pipeline.py` first |

## 7. Grading map

| Part (weight) | Where |
|---|---|
| Data cleaning (35%) | `src/clean_data.py`, `src/geo_utils.py`, `docs/features.md`, `notebooks/eda.ipynb` |
| SQL queries (35%) | `sql/queries.sql` (Q1-Q30), `sql/create_table.sql` |
| Dashboard (10%) | `app/streamlit_app.py` |
| Documentation (10%) | `README.md`, `docs/` |
| Organization (10%) | this folder structure, `requirements.txt`, `.env.example`, tests |
